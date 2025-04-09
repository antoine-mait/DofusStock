import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dofustock_project.settings')
django.setup()

# Now you can import your models
from dofustock_site.models import Item, Price  

def check_prices():
    # Count total items
    total_items = Item.objects.count()
    print(f"Total items in database: {total_items}")
    
    # Count items with prices
    items_with_prices_count = Item.objects.filter(prices__isnull=False).distinct().count()
    print(f"Items with at least one price entry: {items_with_prices_count}")
    
    # Get the actual items with prices as a queryset for iteration
    items_with_prices = Item.objects.filter(prices__isnull=False).distinct()
    for item in items_with_prices:
        # Use date_updated instead of date
        latest_price = item.prices.order_by('-date_updated').first()
        price_value = latest_price.price if latest_price else "No price"
        print(f"  - {item.name} (ID: {item.ankama_id}) - {price_value}")
    
    # Sample of items without prices
    items_without_prices = Item.objects.filter(prices__isnull=True)[:5]
    print(f"Sample of items without prices:")
    for item in items_without_prices:
        print(f"  - {item.name} (ID: {item.ankama_id})")
    
    # Check total price entries
    total_prices = Price.objects.count()
    print(f"Total price entries: {total_prices}")
    
if __name__ == "__main__":
    check_prices()