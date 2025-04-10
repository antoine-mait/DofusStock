import csv
import os
import sys
import django
import re
import unicodedata
import time

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dofustock_project.settings')
django.setup()

from dofustock_site.models import Item, Price  # Adjust the import path as needed
from dotenv import load_dotenv

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

def import_prices_from_csv(csv_file_path):
    # Prepare CSV for missing items
    missing_items_path = os.path.join(tmp_folder, 'missing_items.csv')

    imported_items_path = os.path.join(tmp_folder, 'imported_items.csv')

    with open(missing_items_path, 'w', newline='') as missing_file, \
         open(imported_items_path, 'w', newline='') as imported_file:
        missing_writer = csv.writer(missing_file)
        missing_writer.writerow(['Item', 'Price'])

        imported_writer = csv.writer(imported_file)
        imported_writer.writerow(['Item', 'Price', 'Item ID'])
        
        # Process main CSV
        with open(csv_file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            # Track stats
            total_rows = 0
            matched_items = 0
            missing_items = 0
            
            for row in reader:
                total_rows += 1
                item_name = row['Item']
                price_value = row['Price']

                csv_item_normalized = sanitize_filename(item_name)
                
                # Clean the price value for proper decimal format
                cleaned_price = clean_price_value(price_value)
                
                # For display in imported items and logs
                display_price = "N/A" if cleaned_price == "0" else cleaned_price
                
                # Try to find matching item by name
                item_found = False
                try:
                    # Try to get the item, but catch the MultipleObjectsReturned exception
                    try:
                        item = Item.objects.get(name=csv_item_normalized)
                        item_found = True
                    
                    except Item.MultipleObjectsReturned:
                        # Handle multiple items with the same name
                        print(f"Multiple items found with name: {csv_item_normalized}")
                        # Get all items with this name and choose the first one
                        items = Item.objects.filter(name=csv_item_normalized)
                        item = items.first()  # Take the first matching item
                        item_found = True
                        print(f"Selected item ID: {item.id} from multiple matches")
                        
                except Item.DoesNotExist:
                    try:
                        # Try to find items by sanitizing the database names for comparison
                        all_items = Item.objects.all()
                        matched_item = None
                        
                        for db_item in all_items:
                            sanitized_db_name = sanitize_filename(db_item.name)
                            if sanitized_db_name == csv_item_normalized:
                                matched_item = db_item
                                break
                        
                        if matched_item:
                            item = matched_item
                            item_found = True

                        else:
                            # If no exact sanitized match, fall back to your existing fuzzy match logic
                            potential_items = Item.objects.filter(name__icontains=csv_item_normalized.split('_')[0] if '_' in csv_item_normalized else csv_item_normalized)
                            
                            if potential_items.exists():
                                # Find the best match by comparing sanitized database names
                                best_match = None
                                best_score = 0
                                
                                for potential_item in potential_items:
                                    sanitized_db_name = sanitize_filename(potential_item.name)
                                    # Compare the CSV name with the sanitized DB name
                                    similarity = sum(c1 == c2 for c1, c2 in zip(csv_item_normalized, sanitized_db_name))
                                    if similarity > best_score:
                                        best_score = similarity
                                        best_match = potential_item
                                
                                if best_match:
                                    item = best_match
                                    item_found = True
                                else:
                                    # No good match found
                                    item_found = False
                            else:
                                # No potential items found
                                item_found = False
                                
                    except Exception as e:
                        print(f"Error finding item {csv_item_normalized}: {str(e)}")
                        item_found = False
                
                # If item wasn't found, add to missing items and continue
                if not item_found:
                    print(f"Item not found: {item_name}")
                    missing_writer.writerow([csv_item_normalized, price_value])
                    missing_items += 1
                    continue
                
                # Create or update price
                try:
                    price, created = Price.objects.update_or_create(
                        item=item,
                        defaults={'price': cleaned_price}
                    )
                    
                    matched_items += 1
                    # print(f"Updated price for {item.name}: {display_price}")
                    imported_writer.writerow([item.name, display_price, item.id])

                except Exception as e:
                    print(f"Error updating price for {csv_item_normalized}: {str(e)}")
            
            print(f"Import completed. Processed {total_rows} rows, matched {matched_items} items, {missing_items} missing items.")

if __name__ == "__main__":

    overall_start = time.time()

    csv_file_path = os.path.join(tmp_folder, 'ALL_HDV_Prices.csv')
    import_prices_from_csv(csv_file_path)

    print(f"Total processing time: {time.time() - overall_start:.2f} seconds")
