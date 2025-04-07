import cv2
import pytesseract as tess
import pytesseract
import pandas as pd
import os
import re
import unicodedata
from dotenv import load_dotenv
from tmp.correction import correction_dict

load_dotenv()
main_folder= os.environ.get("MAIN_IMG_FOLDER")
tmp_folder= os.environ.get("folder_dir_tmp")

def sanitize_filename(filename):
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFD', filename)
    
    # Remove accent marks
    no_accents = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    # Remove invalid characters and replace spaces
    sanitized = re.sub(r'[<>:"/\\|?*\'°œ]', '', no_accents)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    return sanitized

def extract_items_data(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
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
    
    # Sort by vertical position (top)
    lines_data.sort(key=lambda x: x['top'])
    
    # Identify rows based on vertical position
    rows = []
    current_row = []
    last_top = -1
    vertical_threshold = 20  # Adjust this based on your image
    
    for line in lines_data:
        if last_top == -1 or abs(line['top'] - last_top) < vertical_threshold:
            current_row.append(line)
        else:
            # New row
            if current_row:
                rows.append(current_row)
            current_row = [line]
        last_top = line['top']
    
    # Add the last row
    if current_row:
        rows.append(current_row)
    
    # Identify items and prices from each row
    items_data = []
    
    # Determine the boundary between item and price columns
    img_width = img.shape[1]
    column_boundary = img_width * 0.6  # Adjust this threshold based on your image layout
    
    for i, row in enumerate(rows):
        # Sort each row by horizontal position
        row.sort(key=lambda x: x['top'])
        
        left_side_text = []
        right_side_text = []
        
        for item in row:
            if item['left'] < column_boundary:
                left_side_text.append(item['text'])
            else:
                right_side_text.append(item['text'])
        
        item_text = " ".join(left_side_text).strip()

        price_text = " ".join(right_side_text).strip()
        
        # Clean up price text - keep only numbers and separators
        if price_text:
            # Remove any non-numeric characters except spaces and common separators
            price_text = re.sub(r'[^0-9\s.,]', '', price_text).strip()

        if item_text or price_text:
            items_data.append({'Item': sanitize_filename(item_text), 'Price': price_text})
    
    # Convert to DataFrame
    df = pd.DataFrame(items_data)

    return df

def extract_text_regions(image_path, output_folder):
    """Extract text regions from the image and save them to a folder,
    avoiding duplicate text content and close rows"""
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Read the image
    img = cv2.imread(image_path)
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
            print(f"Skipping row at y={y_start} as it's too close to a previously processed row")
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
    
    print(f"Extracted {len(saved_regions)} text regions to {output_folder}")
    return saved_regions

def main():
    # Use main_folder in all path constructions
    path = os.path.join(main_folder, "HDV_CONSUMABLE", "HDV_CONSUMABLE_PRICE_IMG", "BLACKOUT_PRICE", "BLACKOUT_HDV_CONSUMABLE_1.png")
    
    region_path = os.path.join(main_folder, "HDV_CONSUMABLE", "HDV_CONSUMABLE_PRICE_IMG", "ITEM_PRICE")
        
    # extract_text_regions(path, region_path)
    
    items_df = None

    for img in os.listdir(region_path):
        img_path = os.path.join(region_path, img)
        
        # For the first image, create the dataframe
        if items_df is None:
            items_df = extract_items_data(img_path)
        else:
            # For subsequent images, append to the dataframe
            items_df = pd.concat([items_df, extract_items_data(img_path)], ignore_index=True)
    

    dir_path = os.path.join("tmp", "HDV_Price_test.csv")
    df = pd.read_csv(dir_path)

    df['Item'] = df['Item'].apply(
    lambda item: next((item.replace(wrong, correct) for wrong, correct in correction_dict.items() if wrong in item), item))

    output_path = os.path.join("tmp", "HDV_Price_test.csv")
    df.to_csv(output_path, index=False)
    
if __name__ == "__main__":
    main()