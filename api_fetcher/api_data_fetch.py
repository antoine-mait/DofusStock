import os
import re
import sys
import time
import logging
import requests
import unicodedata
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Django setup
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dofustock_project.settings')
django.setup()

# Import your models
from dofustock_site.models import Item, Effect, Recipe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dofus_api_fetch.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DOFUS_API = os.environ.get("DOFUS_API")

class DofusItemFetcher:
    def __init__(self, base_url):
        logger.info(f"Initializing DofusItemFetcher with base URL: {base_url}")

        # API Session Setup
        self.base_url = base_url
        self.session = requests.Session()
        retry_strategy = Retry(
            total=10,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=50)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_item(self, categorie, item_type, level_min, level_max):
        """Fetch items from Dofus API"""
        logger.info(f"Fetching items for category: {categorie}, type: {item_type}, levels: {level_min}-{level_max}")
        
        params = {
            "sort[level]": "asc",
            "filter[min_level]": level_min,
            "filter[max_level]": level_max,
        }   
        if categorie in ["equipment"]:
            params["filter[type_enum]"] = item_type
        
        url = (f"{self.base_url}/dofus3/v1/fr/{categorie}/all" 
               if categorie == "mounts" 
               else f"{self.base_url}/dofus3/v1/fr/items/{categorie}/all")
        
        try:
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request Params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            if categorie == "mounts":
                all_mounts = response.json().get("mounts", [])
                # Filter mounts by family name if a specific type was requested
                if item_type in ["Dragodinde", "Muldo", "Volkorne"]:
                    items = [mount for mount in all_mounts if mount.get('family', {}).get('name') == item_type]
                else:
                    items = all_mounts
            else: 
                items = response.json().get("items", [])
            
            logger.info(f"Retrieved {len(items)} items for {categorie} - {item_type}")
            return items
        
        except requests.RequestException as e:
            logger.error(f"Error fetching items of type {item_type}: {e}")
            return None

    def download_image(self, item, categorie):
        """
        Download item image and save it in the specified folder structure
        Folder structure: media/IMG/category/item_type/image_file
        """
        try:
            # Sanitize filename to remove invalid characters
            def sanitize_filename(filename):
                # Normalize Unicode characters (decompose accented characters)
                normalized = unicodedata.normalize('NFKD', filename)
                
                # Remove accent marks
                ascii_filename = normalized.encode('ascii', 'ignore').decode('ascii')
                
                # Remove invalid characters and replace spaces with underscores
                sanitized = re.sub(r'[<>:"/\\|?*\']', '', ascii_filename).replace(' ', '_')
                
                return sanitized

            # Determine base media directory
            base_media_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'dofustock_site', 'media', 'IMG'
            )

            # Create base media directory if it doesn't exist
            os.makedirs(base_media_dir, exist_ok=True)

            # Determine item type
            item_type = (item['type']['name'] if categorie != 'mounts' 
                        else item.get('family', {}).get('name', 'unknown'))

            # Create category and type folders
            category_folder = os.path.join(base_media_dir, categorie)
            item_type_folder = os.path.join(category_folder, item_type)
            
            # Create folders
            os.makedirs(item_type_folder, exist_ok=True)

            # Construct image path and filename
            image_url = item['image_urls']['sd']
            image_name = f"{item['ankama_id']}-{sanitize_filename(item['name'])}.png"
            image_path = os.path.join(item_type_folder, image_name)
            
            # Skip if image already exists
            if os.path.exists(image_path):
                logger.info(f"Image for {item['name']} already exists.")
                # Return relative path for database storage
                relative_path = os.path.join('IMG', categorie, item_type, image_name)
                return relative_path

            # Download the image
            logger.info(f"Downloading image from {image_url}")
            response = self.session.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logger.info(f"Image for {item['name']} saved at {image_path}")
                # Return relative path for database storage
                relative_path = os.path.join('IMG', categorie, item_type, image_name)
                return relative_path
            else:
                logger.error(f"Failed to download image for {item['name']} (Status: {response.status_code})")
                return None
        
        except Exception as e:
            logger.error(f"Error downloading image for {item.get('name', 'Unknown')}: {e}")
            return None

    def insert_item_to_database(self, categorie, items, item_type):
        """Insert items into Django database"""
        if not items:
            logger.warning(f"No items found for {categorie} type '{item_type}'. Skipping...")
            return

        logger.info(f"Inserting {len(items)} items for {categorie} - {item_type}")
        
        for item in items:
            try:
                # Download image and get the image path
                image_path = self.download_image(item, categorie)
                image_url = item['image_urls']['sd'] if image_path is None else image_path

                # Insert or update item using Django's ORM
                item_obj, created = Item.objects.update_or_create(
                    ankama_id=item['ankama_id'],
                    defaults={
                        'name': item['name'],
                        'category': categorie,
                        'item_type': item['type']['name'] if categorie != 'mounts' else item.get('family', {}).get('name', ''),
                        'level': item.get('level', 0),
                        'description': item.get('description', ''),
                        'image_url': image_url,
                        'is_weapon': item.get('is_weapon', False) if categorie != 'mounts' else False
                    }
                )
                
                # Insert Effects - first delete existing ones
                if 'effects' in item and item['effects']:
                    # Delete existing effects for this item
                    Effect.objects.filter(item=item_obj).delete()
                    
                    # Create new effects
                    effects_to_create = [
                        Effect(
                            item=item_obj,
                            description=effect['formatted']
                        )
                        for effect in item['effects']
                    ]
                    Effect.objects.bulk_create(effects_to_create)
                    logger.info(f"Inserted {len(effects_to_create)} effects for {item['name']}")

                # Insert Recipes - first delete existing ones
                if categorie != 'mounts' and 'recipe' in item and item['recipe']:
                    # Delete existing recipes for this item
                    Recipe.objects.filter(item=item_obj).delete()
                    
                    # Create new recipes
                    recipes_to_create = []
                    for recipe in item['recipe']:
                        resource_name = ''
                        try:
                            # Try to find the resource name from existing items
                            resource = Item.objects.filter(ankama_id=recipe['item_ankama_id']).first()
                            if resource:
                                resource_name = resource.name
                        except Exception:
                            pass
                            
                        recipes_to_create.append(
                            Recipe(
                                item=item_obj,
                                resource_id=recipe['item_ankama_id'],
                                resource_name=resource_name,
                                quantity=recipe['quantity']
                            )
                        )
                    
                    Recipe.objects.bulk_create(recipes_to_create)
                    logger.info(f"Inserted {len(recipes_to_create)} recipe items for {item['name']}")

            except Exception as e:
                logger.error(f"Error inserting item {item['name']}: {e}")
                import traceback
                logger.error(traceback.format_exc())

def api_to_django():
    """Main function to fetch API data and insert into Django database"""
    logger.info("Starting API to Django data fetch")
    
    base_url = DOFUS_API
    logger.info(f"Dofus API URL: {base_url}")

    if not base_url:
        logger.error("DOFUS_API environment variable not set!")
        sys.exit(1)

    try:
        # Initialize the fetcher
        fetcher = DofusItemFetcher(base_url)

        for categorie in ["resources", "equipment", "consumables", "mounts"]:
            logger.info(f"Processing category: {categorie}")
            level_min = 1
            level_max = 200

            # Set up the Item Type
            if categorie == "equipment":
                types = [
                    "Amulet", "Ring", "Boots", "Shield", 
                    "Cloak", "Belt", "Hat", "Dofus", 
                    "Trophy", "Prysmaradite", "Pet", "Petsmount"
                ]
            elif categorie == "mounts":
                types = ["Dragodinde", "Muldo", "Volkorne"]
            elif categorie == "consumables":
                types = ["consumables"]
            elif categorie == "resources":
                types = ["resources"]
            else:
                continue

            # Process items sequentially to avoid race conditions
            for item_type in types:
                items = fetcher.get_item(categorie, item_type, level_min, level_max)
                if items:
                    if categorie == 'mounts':
                        for item in items:
                            if 'recipe' in item:
                                del item['recipe']
                    fetcher.insert_item_to_database(categorie, items, item_type)
                time.sleep(1)

    except KeyboardInterrupt:
        logger.warning("Script stopped with Ctrl + C.")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        api_to_django()
    except KeyboardInterrupt:
        logger.warning("Script stopped with Ctrl + C.")