import cv2
import pytesseract as tess
import pytesseract
import pandas as pd
import os
import re
import unicodedata
from dotenv import load_dotenv
from tmp.correction import correction_dict
from concurrent.futures import ThreadPoolExecutor
import glob
import time

load_dotenv()
main_folder = os.environ.get("MAIN_IMG_FOLDER")
tmp_folder = os.environ.get("folder_dir_tmp")


def sanitize_filename(filename):
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFD', filename)
    
    # Remove accent marks
    no_accents = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    # Remove invalid characters and replace spaces
    sanitized = re.sub(r'[<>:"/\\|?*\'°œ]', '', no_accents)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    return sanitized

def extract_text_regions(image_path, output_folder):
    """Extract text regions from the image and save them to a folder,
    avoiding duplicate text content and close rows"""
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to read image: {image_path}")
        return []
        
    height, width = img.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get clearer text
    _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Use Tesseract to detect text and their bounding boxes
    custom_config = r'--oem 3 --psm 11'
    data = pytesseract.image_to_data(threshold, lang='fra', config=custom_config, output_type=pytesseract.Output.DICT)
    
    # Group boxes by their y-coordinates to identify rows
    rows = {}
    for i, text in enumerate(data['text']):
        if int(data['conf'][i]) < 40 or not text.strip():  # Skip low confidence or empty text
            continue
            
        y = data['top'][i]
        h = data['height'][i]
        
        # Find or create row group (with 15px tolerance)
        row_key = None
        for existing_y in rows.keys():
            if abs(existing_y - y) < 15:
                row_key = existing_y
                break
                
        if row_key is None:
            row_key = y
            rows[row_key] = {'min_y': y, 'max_y': y + h, 'text': [text]}
        else:
            rows[row_key]['min_y'] = min(rows[row_key]['min_y'], y)
            rows[row_key]['max_y'] = max(rows[row_key]['max_y'], y + h)
            rows[row_key]['text'].append(text)
    
    # Process rows
    sorted_rows = sorted(rows.items(), key=lambda x: x[0])  # Sort by y-coordinate
    
    # Extract and save each row
    saved_regions = []
    saved_texts = set()  # Keep track of saved text content to avoid duplicates
    processed_y_positions = []  # Keep track of already processed y positions
    min_y_distance = 25  # Minimum vertical distance between regions in pixels
    
    for i, (y_key, row) in enumerate(sorted_rows):
        y_start = max(0, row['min_y'] - 10)  # Add small padding
        y_end = min(height, row['max_y'] + 15)
        
        # Skip if row is too thin
        if y_end - y_start < 15:
            continue
        
        # Generate combined text for this row
        row_text = ' '.join(row['text']).strip().lower()
        
        # Skip if similar text content already saved
        if row_text in saved_texts:
            continue
        
        # Skip if too close to a previously processed region
        too_close = False
        for prev_y in processed_y_positions:
            if abs(y_start - prev_y) < min_y_distance:
                too_close = True
                break
        
        if too_close:
            continue
        
        # Extract full width of the row
        row_image = img[y_start:y_end, 0:width]
        
        # Generate filename from text if possible
        name = f"row_{i}.png"
        if row['text']:
            # Use first few words of text as filename (sanitized)
            text_name = '_'.join(row['text'][:3])
            text_name = ''.join(c if c.isalnum() else '_' for c in text_name)
            if text_name:
                name = f"{text_name[:30]}_{i}.png"
                filename = sanitize_filename(name)
        
        # Save the region
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, row_image)
        saved_regions.append({'y': y_start, 'filename': output_path, 'height': y_end - y_start, 'text': row_text})
        
        # Add this text to the saved texts set
        saved_texts.add(row_text)
        processed_y_positions.append(y_start)
    
    return saved_regions

def extract_items_data(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to read image: {image_path}")
        return pd.DataFrame(columns=['Item', 'Price'])
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get clearer text
    _, img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Use pytesseract to get bounding boxes of text with coordinates
    custom_config = r'--oem 3 --psm 6 -l fra'
    boxes = tess.image_to_data(img, config=custom_config, output_type=tess.Output.DICT)
    
    # Prepare data structure to hold text by position
    lines_data = []
    
    # Process text with position information
    for i in range(len(boxes['text'])):
        if boxes['text'][i].strip():
            lines_data.append({
                'text': boxes['text'][i],
                'left': boxes['left'][i],
                'top': boxes['top'][i],
                'width': boxes['width'][i],
                'height': boxes['height'][i],
                'conf': boxes['conf'][i]
            })
    
    # Get image dimensions for setting column boundaries
    img_height, img_width = img.shape
    
    # Define price column boundary (adjust as needed)
    price_boundary = img_width * 0.6
    
    # Collect item names and prices
    item_texts = []
    price_texts = []
    
    for block in lines_data:
        # If the text starts in the right side of the image, treat as price
        if block['left'] > price_boundary:
            price_texts.append(block['text'])
        else:
            item_texts.append(block['text'])
    
    # Combine text blocks to form item name and price
    item_name = " ".join(item_texts).strip()
    price_text = " ".join(price_texts).strip()
    
    # Create DataFrame
    items_data = [{'Item': sanitize_filename(item_name), 'Price': price_text}]
    df = pd.DataFrame(items_data)
    
    return df

def process_directory(directory , user_input_slice , user_input_all):
    """Process all images in a directory"""
    start_time = time.time()
    print(f"Starting processing of {directory}...")
    
    # Construct paths
    input_path = os.path.join(main_folder, directory, "BLACKOUT_PRICE")
    output_base = os.path.join(main_folder, directory, "ITEM_PRICE")

    mono_img = os.path.join(main_folder, directory, "ITEM_PRICE" , "Aileron_de_Requin_7.png")
    # mono_img = os.path.join(main_folder, directory, "ITEM_PRICE" , "Gravure_d_Eboulement_4_3.png")
    
    # Ensure the output directory exists
    os.makedirs(output_base, exist_ok=True)
    
    # Get all PNG images in the directory
    image_files = glob.glob(os.path.join(input_path, "*.png"))
    
    if not image_files:
        return None
    
    # Process each image to extract text regions
    if user_input_slice == "y" : 
        with ThreadPoolExecutor(max_workers=min(len(image_files), 8)) as executor:
            for img_path in image_files:
                executor.submit(extract_text_regions, img_path, output_base)
        
    # Extract item data from all regions
    region_files = glob.glob(os.path.join(output_base, "*.png"))
    item_dfs = []
    
    # Use ThreadPoolExecutor to process images in parallel
    if user_input_all == "y":
        with ThreadPoolExecutor(max_workers=min(len(region_files), 16)) as executor:
            # Submit all tasks and get futures
            futures = [executor.submit(extract_items_data, img_path) for img_path in region_files]
            
            # Process results as they complete
            for future in futures:
                df = future.result()
                if not df.empty:
                    item_dfs.append(df)

    else : 
        df = extract_items_data(mono_img)
        if not df.empty:
            item_dfs.append(df)
        
    # Combine all dataframes
    if item_dfs:
        combined_df = pd.concat(item_dfs, ignore_index=True)
        
        # Apply correction dictionary to Item column
        if 'Item' in combined_df.columns:
            combined_df['Item'] = combined_df['Item'].apply(
                lambda item: next((item.replace(wrong, correct) for wrong, correct in correction_dict.items() if wrong in item), item) if isinstance(item, str) else item)
        
        # Save results
        if user_input_all == "y":
            output_path = os.path.join(tmp_folder, f"{directory}_Price.csv")
        else:
            output_path = os.path.join(tmp_folder, f"test_Price.csv")

        combined_df.to_csv(output_path, index=False)

        print(f"Directory {directory} processing completed in {time.time() - start_time:.2f} seconds")
        return combined_df
    else:
        print(f"No valid data extracted from {directory}")
        return None

def main():
    """Main function to process all directories in parallel"""
    overall_start = time.time()
    
    user_input_slice = "n" #input("Slice image ? y or n")
    user_input_all = "y" #input("all image ? y or n")

    directories = ["HDV_CONSUMABLE", "HDV_ITEM", "HDV_RESOURCES", "HDV_RUNES"]
    # directories = ["HDV_RUNES"]
    # if user_input_all == "n":
        #  directories = ["HDV_CONSUMABLE"]

    all_dataframes = []
    
    # Process each directory in parallel
    with ThreadPoolExecutor(max_workers=len(directories)) as executor:
        # Submit all tasks and get futures
        futures = {executor.submit(process_directory, directory , user_input_slice, user_input_all): directory for directory in directories}
        
        # Process results as they complete
        for future in futures:
            directory = futures[future]
            try:
                df = future.result()
                if df is not None and not df.empty:
                    all_dataframes.append(df)
            except Exception as e:
                print(f"Error processing directory {directory}: {e}")

    # Combine all results into a single CSV if needed
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Remove duplicates
        final_df.drop_duplicates(subset=['Item'], keep='first', inplace=True)
        
        # Save combined results
        final_output_path = os.path.join(tmp_folder, "ALL_HDV_Prices.csv")
        final_df.to_csv(final_output_path, index=False)
        print(f"Saved combined results with {len(final_df)} items to {final_output_path}")
    
    print(f"Total processing time: {time.time() - overall_start:.2f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")
