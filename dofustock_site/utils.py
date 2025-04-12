import unicodedata
import re

def sanitize_filename(filename):
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFD', filename)
    
    # Remove accent marks
    no_accents = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    # Remove invalid characters and replace spaces
    sanitized = re.sub(r'[<>:"/\\|?*\'°œ]', '', no_accents)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    return sanitized

def calculate_craft_cost(item):
    """
    Calculate the total craft cost for an item based on its recipe.
    Returns a tuple (cost, all_prices_available) where:
    - cost is the numeric total cost (or None if not all prices are available)
    - all_prices_available is a boolean indicating if all resource prices were available
    """
    total_craft_cost = 0
    all_prices_available = True
    
    # If item has no recipes, return early
    if not hasattr(item, 'recipes') or not item.recipes.exists():
        return None, False
    
    for recipe in item.recipes.all():
        try:
            resource_item = item.__class__.objects.get(ankama_id=recipe.resource_id)
            resource_price = resource_item.prices.latest('date_updated')
            
            if resource_price.price is not None and resource_price.price != 0:
                total_craft_cost += int(resource_price.price) * recipe.quantity
            else:
                all_prices_available = False
        except Exception:
            all_prices_available = False
    
    return total_craft_cost, all_prices_available

def format_craft_cost(total_craft_cost, all_prices_available):
    """
    Format the craft cost for display.
    """
    if all_prices_available:
        return f"{total_craft_cost:,}".replace(',', ' ')
    else:
        return "Incomplete"