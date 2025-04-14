import csv
import os
import sys
import django
import re
import unicodedata
import time
import concurrent.futures
from functools import partial

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dofustock_project.settings')
django.setup()

from dofustock_site.models import Item, Price  # Adjust the import path as needed
from dotenv import load_dotenv
from django.db import connection

load_dotenv()
main_folder = os.environ.get("MAIN_IMG_FOLDER")
tmp_folder = os.environ.get("folder_dir_tmp")

def sanitize_filename(name):
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFD', name)
    
    # Remove accent marks
    no_accents = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    # Convert to lowercase for case-insensitive comparison
    lowercase = no_accents.lower()
    
    # Remove apostrophes, spaces, and other common special characters
    cleaned = re.sub(r'[<>:"/\\|?*\'°œ\-]', '', lowercase)
    
    # Replace spaces with underscores
    final = re.sub(r'\s+', '_', cleaned)

    return final

def clean_price_value(price_str):
    # Check if price_str is None, empty, or just contains a hyphen or whitespace
    if price_str is None or not price_str.strip() or price_str.strip() == "-":
        return "0"  

    # Remove any spaces and replace commas with dots for decimal
    cleaned = price_str.replace(' ', '').replace(',', '.')
    
    # Remove any remaining non-numeric characters (except decimal point)
    cleaned = re.sub(r'[^\d.]', '', cleaned)
    
    # Check if there are any digits left after cleaning
    if not cleaned or not any(c.isdigit() for c in cleaned):
        return "0"  
    
    return cleaned

def process_item(row, all_items_dict, missing_writer, imported_writer, lock):
    """Process a single item from the CSV"""
    item_name = row['Item']
    price_value = row['Price']
    
    csv_item_normalized = sanitize_filename(item_name)
    cleaned_price = clean_price_value(price_value)
    display_price = "N/A" if cleaned_price == "0" else cleaned_price
    
    # Close old connections to prevent connection leaks
    connection.close()
    
    # Try to find matching item by normalized name
    item_found = False
    item = None
    
    # First try exact match
    try:
        item = Item.objects.get(name=csv_item_normalized)
        item_found = True
    except Item.MultipleObjectsReturned:
        # Handle multiple items with the same name
        items = Item.objects.filter(name=csv_item_normalized)
        item = items.first()
        item_found = True
    except Item.DoesNotExist:
        # Try to find by sanitized name comparison
        for db_item_id, db_item_name in all_items_dict.items():
            sanitized_db_name = sanitize_filename(db_item_name)
            if sanitized_db_name == csv_item_normalized:
                item = Item.objects.get(id=db_item_id)
                item_found = True
                break
        
        # If still not found, try fuzzy matching
        if not item_found:
            first_part = csv_item_normalized.split('_')[0] if '_' in csv_item_normalized else csv_item_normalized
            potential_items = []
            
            for db_item_id, db_item_name in all_items_dict.items():
                sanitized_db_name = sanitize_filename(db_item_name)
                if first_part in sanitized_db_name:
                    potential_items.append((db_item_id, db_item_name, sanitized_db_name))
            
            if potential_items:
                # Find best match
                best_match = None
                best_score = 0
                
                for pot_id, pot_name, pot_sanitized in potential_items:
                    similarity = sum(c1 == c2 for c1, c2 in zip(csv_item_normalized, pot_sanitized))
                    if similarity > best_score:
                        best_score = similarity
                        best_match = pot_id
                
                if best_match:
                    item = Item.objects.get(id=best_match)
                    item_found = True
    
    # Write results with thread safety
    with lock:
        if not item_found:
            print(f"Item not found: {item_name}")  # Keep this print statement for missing items
            missing_writer.writerow([csv_item_normalized, price_value])
            return {'status': 'missing', 'name': item_name}
        
        try:
            # Create or update price
            price, created = Price.objects.update_or_create(
                item=item,
                defaults={'price': cleaned_price}
            )
            
            imported_writer.writerow([item.name, display_price, item.id])
            return {'status': 'updated', 'name': item.name, 'price': display_price}
        except Exception as e:
            return {'status': 'error', 'name': item_name, 'error': str(e)}

def import_prices_from_csv(csv_file_path, num_workers=4):
    missing_items_path = os.path.join(tmp_folder, 'missing_items.csv')
    imported_items_path = os.path.join(tmp_folder, 'imported_items.csv')
    
    # Preload all items into memory for faster lookups
    print("Preloading items from database...")
    all_items_dict = {item.id: item.name for item in Item.objects.all()}
    print(f"Loaded {len(all_items_dict)} items")
    
    with open(missing_items_path, 'w', newline='') as missing_file, \
         open(imported_items_path, 'w', newline='') as imported_file, \
         open(csv_file_path, 'r', encoding='utf-8', errors='replace') as f:
        
        missing_writer = csv.writer(missing_file)
        missing_writer.writerow(['Item', 'Price'])
        
        imported_writer = csv.writer(imported_file)
        imported_writer.writerow(['Item', 'Price', 'Item ID'])
        
        reader = csv.DictReader(f)
        rows = list(reader)
        total_rows = len(rows)
        
        print(f"Processing {total_rows} items with {num_workers} workers...")
        
        # Setup counters
        matched_items = 0
        missing_items = 0
        error_items = 0
        
        # Create a lock for thread-safe file writing
        from threading import Lock
        lock = Lock()
        
        # Create a partial function with shared resources
        process_func = partial(
            process_item, 
            all_items_dict=all_items_dict,
            missing_writer=missing_writer,
            imported_writer=imported_writer,
            lock=lock
        )
        
        batch_size = 100
        total_batches = (total_rows + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_rows)
            batch_rows = rows[start_idx:end_idx]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                results = list(executor.map(process_func, batch_rows))
            
            # Process batch results
            for result in results:
                if result['status'] == 'updated':
                    matched_items += 1
                elif result['status'] == 'missing':
                    missing_items += 1
                else:
                    error_items += 1
            
            # Print progress
            progress_pct = (batch_idx + 1) / total_batches * 100
            print(f"Progress: {progress_pct:.1f}% - Batch {batch_idx+1}/{total_batches} processed")
    
    print(f"Import completed. Processed {total_rows} rows, matched {matched_items} items, {missing_items} missing items, {error_items} errors.")

def main():
    overall_start = time.time()
    
    csv_file_path = os.path.join(tmp_folder, 'ALL_HDV_Prices.csv')
    
    # Detect optimal number of workers based on CPU cores (default to 4)
    import multiprocessing
    num_cores = multiprocessing.cpu_count()
    # Use a few less threads than cores to avoid overloading the system
    recommended_workers = max(32, num_cores * 2)  
    
    import_prices_from_csv(csv_file_path, num_workers=recommended_workers)
    
    print(f"Total processing time: {time.time() - overall_start:.2f} seconds")

if __name__ == "__main__":
    main()