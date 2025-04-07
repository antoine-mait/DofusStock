import pyautogui
import random
import time
import numpy as np
import os
import re
import win32api
import win32con
import pytesseract as tess
import ctypes
import cv2
import pandas as pd
import pytesseract
from PIL import Image
from tmp.correction import correction_dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

load_dotenv()
main_folder= os.environ.get("MAIN_IMG_FOLDER")
tmp_folder= os.environ.get("folder_dir_tmp")

def read_image():

    def extract_items_data(image_path):
    # Read the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get clearer text
        _, img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Use pytesseract to extract text
        custom_config = r'--oem 3 --psm 4 -l fra'
        text = tess.image_to_string(img, config=custom_config)
        
        # Process the text to extract items and values
        lines = text.strip().split('\n')
        
        items_data = []
        
        for line in lines:
            if not line.strip():
                continue
                
            # Split each line into item name and value
            parts = line.strip().split('  ')
            parts = [p for p in parts if p.strip()]
            
            if len(parts) >= 2:
                item_name = parts[0].strip()
                value = parts[-1].strip()
                items_data.append({'Item': item_name, 'Value': value})
            elif len(parts) == 1 and parts[0].strip():
                # Handle cases where there might be only one part
                item_name = parts[0].strip()
                value = ""
                items_data.append({'Item': item_name, 'Value': value})
        
        # Convert to DataFrame
        df = pd.DataFrame(items_data)

        return df

    def main():
        path = os.path.join(r"HDV_CONSUMABLE", r"HDV_CONSUMABLE_PRICE_IMG", r"BLACKOUT_PRICE", r"BLACKOUT_HDV_CONSUMABLE_1.png")
        path_format = path.replace("\\", "\\\\")
        image_path = os.path.join( main_folder , path_format)
        items_df = extract_items_data(image_path)
        dir_path = os.path.join("tmp","HDV_Price.csv")
        items_df.to_csv(dir_path, index=False)
        print("Data has been saved to 'extracted_items_data.csv'")
        
    main()