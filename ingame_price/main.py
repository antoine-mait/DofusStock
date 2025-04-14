from In_game_price_scrapper import HDV_Screenshot , IMG_Blackout
from read_ingame_price import main as main_read
from import_price import main as main_import
import time
import os
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("DofusHDVPriceScraper")

"""
DOFUS HDV PRICE SCRAPER
======================

This system automates the collection, extraction, and importation of in-game market prices 
from the Dofus game's HDV (Auction House). The pipeline consists of four main stages:

1. HDV_Screenshot: Automates in-game navigation and captures screenshots
2. IMG_Blackout: Processes images to prepare them for OCR
3. main_read: Extracts text data from images using OCR
4. main_import: Updates database with extracted price data

REQUIREMENTS:
- Dofus game client running at 2K resolution
- Game positioned at HDV Creature in Brakmar city
- Python environment with dependencies (cv2, pytesseract, etc.)
- Properly configured .env file with path settings

"""

def run_pipeline():
    """Execute the complete HDV price scraping pipeline."""
    start_time = time.time()
    logger.info("Starting HDV price scraping pipeline")
    
    try:
        """
        STAGE 1: CAPTURE IN-GAME SCREENSHOTS
        ===================================
        
        The HDV_Screenshot function controls the game client to:
        - Navigate through the Brakmar city's various auction houses (HDVs)
        - Capture screenshots of item listings with their prices
        - Handle map transitions between different HDV types
        
        The function uses a combination of mouse movements, clicks, and keyboard inputs
        to interact with the game client. It follows a predefined path through:
        - HDV_CREATURE
        - HDV_RUNES
        - HDV_ITEM  
        - HDV_RESOURCES
        - HDV_CONSUMABLE
        
        Screenshots are saved into category-specific folders for the next stage.
        """
        logger.info("Stage 1/4: Capturing in-game HDV screenshots")
        HDV_Screenshot()
        logger.info("Screenshot capture completed")
        
        """
        STAGE 2: IMAGE PREPROCESSING
        ==========================
        
        The IMG_Blackout function processes the raw screenshots to:
        - Remove irrelevant visual elements (item images, category markers, level indicators)
        - Detect and blackout "Panoplie" icons that could interfere with text recognition
        - Prepare clean images focused only on item names and prices
        
        This preprocessing improves OCR accuracy by eliminating visual noise and
        focusing only on the text data we need to extract.
        
        Processed images are saved into "BLACKOUT_PRICE" subfolders for each HDV category.
        """
        logger.info("Stage 2/4: Processing images for OCR")
        IMG_Blackout()
        logger.info("Image processing completed")
        
        """
        STAGE 3: TEXT EXTRACTION WITH OCR
        ===============================
        
        The main_read function processes the blackout images to extract structured data:
        - Uses multithreading to process multiple images concurrently
        - For each image:
          - Detects text regions and extracts them as separate images
          - Uses pytesseract to recognize text in these regions
          - Identifies item names and prices based on their position
          - Sanitizes extracted text to normalize formatting
        - Organizes results into CSV files with item names and prices
        
        The function uses advanced region detection algorithms to handle
        multi-line item names and avoid duplicate entries.
        """
        logger.info("Stage 3/4: Extracting text with OCR")
        main_read()
        logger.info("Text extraction completed")
        
        """
        STAGE 4: DATABASE INTEGRATION
        ===========================
        
        The main_import function integrates the extracted data with your database:
        - Uses multiprocessing to efficiently process large datasets
        - Normalizes item names between the CSV data and database records
        - Employs multiple matching strategies:
          - Exact name matching
          - Sanitized name matching
          - Fuzzy matching for close matches
        - Updates price records for matched items
        - Creates reports of successfully imported and missing items
        
        This stage ensures the price data is properly linked to the correct items
        in your database, handling edge cases like similar names or OCR errors.
        """
        logger.info("Stage 4/4: Importing prices to database")
        main_import()
        logger.info("Price import completed")
        
        # Calculate and display execution time
        execution_time = time.time() - start_time
        logger.info(f"Complete pipeline executed in {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    run_pipeline()