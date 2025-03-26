import os
import re
import sys
import time
import sqlite3
import logging
import requests
import unicodedata
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

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
    def __init__(self, base_url, db_path):
        logger.info(f"Initializing DofusItemFetcher with base URL: {base_url}")
        logger.info(f"Database path: {db_path}")

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

        # Database Setup
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        """Create database tables if they don't exist"""
        logger.info("Creating database tables if they don't exist")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Items table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ankama_id INTEGER UNIQUE,
                        name TEXT,
                        category TEXT,
                        item_type TEXT,
                        level INTEGER,
                        description TEXT,
                        image_url TEXT,
                        is_weapon BOOLEAN
                    )
                ''')

                # Effects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS effects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER,
                        description TEXT,
                        FOREIGN KEY(item_id) REFERENCES items(id)
                    )
                ''')

                # Recipes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS recipes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER,
                        resource_id INTEGER,
                        resource_name TEXT,
                        quantity INTEGER,
                        FOREIGN KEY(item_id) REFERENCES items(id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_item(self, categorie, item_type, level_min, level_max):
        """Fetch items from Dofus API"""
        logger.info(f"Fetching items for category: {categorie}, type: {item_type}, levels: {level_min}-{level_max}")
        
        params = {
            "sort[level]": "asc",
            "filter[min_level]": level_min,
            "filter[max_level]": level_max,
        }   
        if categorie in ["equipment", "mounts"]:
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
                items = response.json().get("mounts", [])
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
                        else item.get('family_name', 'unknown'))

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
                return image_path

            # Download the image
            logger.info(f"Downloading image from {image_url}")
            response = self.session.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logger.info(f"Image for {item['name']} saved at {image_path}")
                return image_path
            else:
                logger.error(f"Failed to download image for {item['name']} (Status: {response.status_code})")
                return None
        
        except Exception as e:
            logger.error(f"Error downloading image for {item.get('name', 'Unknown')}: {e}")
            return None

    def insert_item_to_database(self, categorie, items, item_type):
        """Insert items into the SQLite database"""
        if not items:
            logger.warning(f"No items found for {categorie} type '{item_type}'. Skipping...")
            return

        logger.info(f"Inserting {len(items)} items for {categorie} - {item_type}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for item in items:
                try:
                    # Download image and get the image path
                    image_path = self.download_image(item, categorie)
                    image_url = item['image_urls']['sd'] if image_path is None else image_path

                    # Insert Item
                    cursor.execute('''
                        INSERT OR REPLACE INTO items 
                        (ankama_id, name, category, item_type, level, description, image_url, is_weapon) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['ankama_id'],
                        item['name'],
                        categorie,
                        item['type']['name'] if categorie != 'mounts' else item['family_name'],
                        item.get('level', 0),
                        item.get('description', ''),
                        image_url,
                        item.get('is_weapon', False) if categorie != 'mounts' else False
                    ))
                    
                    # Get the ID of the inserted/updated item
                    item_db_id = cursor.lastrowid
                    
                    # Insert Effects
                    if 'effects' in item and item['effects']:
                        effects_data = [
                            (item_db_id, effect['formatted']) 
                            for effect in item['effects']
                        ]
                        cursor.executemany('''
                            INSERT INTO effects (item_id, description) 
                            VALUES (?, ?)
                        ''', effects_data)
                        logger.info(f"Inserted {len(effects_data)} effects for {item['name']}")

                    # Insert Recipes
                    if categorie != 'mounts' and 'recipe' in item and item['recipe']:
                        recipes_data = [
                            (
                                item_db_id, 
                                recipe['item_ankama_id'], 
                                self.find_resource_name(recipe['item_ankama_id'], conn) or '',
                                recipe['quantity']
                            ) 
                            for recipe in item['recipe']
                        ]
                        cursor.executemany('''
                            INSERT INTO recipes (item_id, resource_id, resource_name, quantity) 
                            VALUES (?, ?, ?, ?)
                        ''', recipes_data)
                        logger.info(f"Inserted {len(recipes_data)} recipe items for {item['name']}")

                except sqlite3.Error as e:
                    logger.error(f"Error inserting item {item['name']}: {e}")

            # Commit the transaction
            conn.commit()
            logger.info(f"Successfully inserted {len(items)} items for {categorie} - {item_type}")

    def find_resource_name(self, recipe_id, conn):
        """Find resource name by ID"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name FROM items 
                WHERE ankama_id = ?
            ''', (recipe_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error:
            return None

def api_to_sqlite():
    """Main function to fetch API data and insert into SQLite database"""
    logger.info("Starting API to SQLite data fetch")
    
    base_url = DOFUS_API
    logger.info(f"Dofus API URL: {base_url}")

    if not base_url:
        logger.error("DOFUS_API environment variable not set!")
        sys.exit(1)

    try:
        # Get the parent directory of the current script's directory
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create database path in the parent directory
        db_path = os.path.join(parent_dir, 'dofus_items.sqlite3')

        # Initialize the fetcher with a specific database path
        fetcher = DofusItemFetcher(base_url, db_path)

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

            # Multithreaded fetching and inserting
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(fetch_and_insert, categorie, item_type, level_min, level_max, fetcher)
                    for item_type in types
                ]
                
                # Wait for all threads to complete
                concurrent.futures.wait(futures)
            
            # Slowdown between categories
            time.sleep(2)

    except KeyboardInterrupt:
        logger.warning("Script stopped with Ctrl + C.")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())

def fetch_and_insert(categorie, item_type, level_min, level_max, fetcher):
    """Helper function for fetching and inserting items"""
    items = fetcher.get_item(categorie, item_type, level_min, level_max)
    if items:
        fetcher.insert_item_to_database(categorie, items, item_type)
    time.sleep(1)

if __name__ == "__main__":
    try:
        api_to_sqlite()
    except KeyboardInterrupt:
        logger.warning("Script stopped with Ctrl + C.")