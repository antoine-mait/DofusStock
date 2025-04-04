import pyautogui
import random
import time
import cv2
import easyocr
import numpy as np
import os
import re
import win32api
import win32con
import pytesseract as tess
import ctypes
from ctypes import wintypes
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

# from .correction import correction_dict
from dotenv import load_dotenv


load_dotenv()
main_folder= os.environ.get("MAIN_IMG_FOLDER")
tmp_folder= os.environ.get("folder_dir_tmp")

# Define required structures and constants
LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(DWORD)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", DWORD),
        ("union", INPUT_UNION)
    ]

# Mouse event flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
INPUT_MOUSE = 0

def HDV_Reader():
    """
    Processes images of market prices for items in the game Dofus.

    This function reads images from specified directories, optionally applies a blackout effect to 
    obscure certain areas, and extracts text using Tesseract (Tess) for Optical Character Recognition (OCR). 
    The extracted text is corrected based on a predefined dictionary and saved to a text file.

    The process is divided into several internal functions:
    - `process_image`: Applies blackout to images and extracts text using Tesseract OCR.
    - `screenshot_reader`: Reads images from directories, processes them in parallel, 
      and compiles the results into a text file.
    - `blackout`: Obscures specific regions of the image.
    - `main_screenshot_reader`: Initiates the screenshot reading process based on user input (Optionnal).
    """
    def process_image(IMAGE1, user_input, blackout_folder):
        """Process a single image: blackout if needed, extract text."""
        if user_input == "y":
            blackout_img = blackout(IMAGE1, blackout_folder)
            img = Image.open(blackout_img)
            if img is None:
                print(f"Failed to load image: {blackout_img}")
                return None
        else:
            check_blackout_img = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
            img = Image.open(check_blackout_img)
        
        # Instance Text Detector
        img = img.convert('L')  # Convert to grayscale
        img = img.point(lambda x: 0 if x < 128 else 255, '1') 
        custom_config = r'--oem 3 --psm 6 -l fra'
        text = tess.image_to_string(img, config=custom_config)
        
        results = []
        words = text.splitlines()
        for line in words:
            for wrong, correct in correction_dict.items():
                line = line.replace(wrong, correct)
            # Find all letters and numbers
            letters = re.findall(r'[^\d]+', line)  # Extract all non-digit characters
            numbers = re.findall(r'\d+', line)  # Extract all digit sequences

            # Join letters and numbers into a formatted string
            letter_part = ''.join(letters).strip()
            number_part = ' '.join(numbers).replace(" ", "")

            if letter_part and number_part:  # Only print if both parts exist
                results.append(f"{letter_part}, {number_part}")
        
        return results

    def screenshot_reader(user_input):
        """Read images and extract text using multithreading."""
        all_results = []

        for directory in ["HDV_CONSUMABLE", "HDV_ITEM", "HDV_RESOURCES", "HDV_RUNES"]:
            print(f"Processing img in {directory} folder")
            path = os.path.join(main_folder, f"{directory}", f"{directory}_PRICE_IMG")  # Construct the full path

            image_files = [f for f in os.listdir(path) if f.endswith('.png')]
            IMAGES_Path = path
            blackout_folder = os.path.join(IMAGES_Path, "BLACKOUT_PRICE")

            with ThreadPoolExecutor() as executor:
                future_to_image = {}
                future_to_image = ({executor.submit(process_image, 
                                                    os.path.join(IMAGES_Path, f"{directory}_{i}.png"), 
                                                    user_input, blackout_folder):
                                                      i for i in range(1, len(image_files) + 1)})
                for future in as_completed(future_to_image):
                    try:
                        results = future.result()
                        if results:
                            all_results.extend(results)
                    except Exception as e:
                        print(f"Error processing image: {e}")

        # Print all results after processing
        dir_path = os.path.join("tmp","HDV_Price.txt")
        with open(dir_path, "w" , encoding="utf-8") as file:
            for results in all_results : 
                file.write(f"{results}\n")

        print(f"All price written on {dir_path}")

    def blackout(IMAGE1, blackout_folder):
        """Blackout specific regions of the image."""
        region1 = (350, 0, 610, 1000)
        region2 = (775, 0, 825, 1000)

        try:
            img = Image.open(IMAGE1)
            
            # Convert image to an array for faster pixel manipulation
            img_array = np.array(img)

            # Apply blackouts using numpy slicing
            img_array[region1[1]:region1[3], region1[0]:region1[2]] = 0  # Blackout first region
            img_array[region2[1]:region2[3], region2[0]:region2[2]] = 0  # Blackout second region

            os.makedirs(blackout_folder, exist_ok=True)
            blackout_path = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
            
            # Convert back to an Image object and save
            Image.fromarray(img_array).save(blackout_path)
            print(f"Image saved to {blackout_path}")
            return blackout_path

        except KeyboardInterrupt:
            print("\nScript stopped with Ctrl + C.")
        except Exception as e:
            print(f"Error processing image: {e}")

    def main_screenshot_reader():
        user_input = "y" #input("Do you want to Blackout the screenshot ? (y/n)")
        screenshot_reader(user_input)

    main_screenshot_reader()

def HDV_Screenshot():
    """
    Captures screenshots of items from the HDV (Auction House) in the game Dofus,
    and interacts with the game's user interface to find and click specific images.
    
    This function is designed to:
    1. Navigate the Auction House based on coordinates.
    2. Take screenshots of items within the Auction House based on the type of items being traded.
    3. Locate and click images representing various items types in the Auction House.
    4. Manage mouse movements with jitter for more natural interactions.
    
    Nested Functions:
    - move_with_jitter: Smoothly moves the mouse with slight random variations.
    - find_and_click_image: Searches for a given image on the screen and clicks it.
    - screen_shot_items: Captures and saves screenshots of items.
    - scroll: Performs scrolling action to navigate through item lists.
    - item_type: Determines the type of items based on the current map and clicks on them.
    - map: Coordinates the entire process of taking screenshots and interacting with the Auction House.
    - coordinate: Checks the player's current map and validates it against expected coordinates.
    - start_map: Initializes the starting map for navigation.
    - map_switch: Handles the transition between different Auction House types and their corresponding actions.
    - click_right: Clicks on the right side of the screen with a jitter effect.
    - click_left: Clicks on the left side of the screen with a jitter effect.
    - click_top: Clicks on the top area of the screen with a jitter effect.
    - click_bottom: Clicks on the bottom area of the screen with a jitter effect.
    - loop_main: Repeatedly invokes the main navigation and interaction process.
    - main_bot: Main entry point to start the Auction House interaction process.
    """
    def move_with_jitter(start_pos, end_pos, steps=5):
        """
        Moves the mouse from the start position to the end position with a jitter effect.

        Parameters:
        - start_pos (tuple): The starting (x, y) position of the mouse.
        - end_pos (tuple): The ending (x, y) position to move the mouse to.
        - steps (int): The number of intermediate steps for the movement.
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos

        for i in range(steps + 1):
            # Calculate the position in a straight line
            x = start_x + (end_x - start_x) * (i / steps)
            y = start_y + (end_y - start_y) * (i / steps)

            # Add jitter to the mouse movement
            jitter_x = random.uniform(-10, 10)
            jitter_y = random.uniform(-10, 10)

            pyautogui.moveTo(x + jitter_x, y + jitter_y, duration=0.01)

    def screen_shot_items(folder_dir, HDV_name):
        """
        Takes screenshots of items from the HDV and saves them to a folder.

        Parameters:
        - img_stop (str): Path to the STOP image.
        - folder_dir (str): Directory to save the screenshots.
        - HDV_name (str): Name of the HDV category being processed.
        
        Returns:
        - bool: True if the last screenshot was captured, else False.
        """
        Folder_name = f"{HDV_name}_PRICE_IMG"
        save_path = os.path.join(rf"{folder_dir}", Folder_name)
        os.makedirs(save_path, exist_ok=True)# Create directory if it doesn't exist
        nb_loop_mapping = {
            "HDV_RESOURCES": 225, #225
            "HDV_CONSUMABLE": 218, #218
            "HDV_ITEM": 304, #304
            "HDV_RUNES": 19, #19
        }
        nb_loop = nb_loop_mapping.get(HDV_name)

        for i in range(1000):
            i += 1
            if i == 1:
                pyautogui.moveTo(1240, 460, duration=random.uniform(0.1, 0.2))   # Initial mouse position
            screenshot = pyautogui.screenshot(region=(850, 455, 670, 600))      # Screenshot region
            screenshot.save(os.path.join(save_path, f"{HDV_name}_{i}.png"))     # Save screenshot

            if i <= nb_loop:
                print(f"Screenshot {HDV_name}_{i}")
                scroll()# Scroll to the next items
            else:
                print(f"Screenshot {HDV_name}_{i}")
                scroll()# Scroll and check for STOP image
                stopscreenshot = True
                if stopscreenshot:
                    print(f"Last Screenshot for {HDV_name}")
                    left_click(1980,332)
                    return True

    def scroll():
        """
        Scrolls down in the HDV to navigate through the items.
        """
        for _ in range(7):
            pyautogui.scroll(-250)# Scroll down

        return True

    def item_type(map_name, main_folder_dir):
        """
        Determines the type of items based on the current map name and performs clicking actions.

        Parameters:
        - map_name (str): The name of the current map.
        - main_folder_dir (str): Main directory path for images and folders.
        """

        if map_name == "HDV_RUNES":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (870, 250)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(870, 250)
            
            time.sleep(random.uniform(1, 2))
            print("active options")
            
            # Define Y positions to click (all with the same X coordinate of 670)
            y_positions = [575, 600, 625, 650, 680, 705]
            
            # Click all positions with random delay
            for y in y_positions:
                left_click(670, y)
                time.sleep(random.uniform(0.7, 1.2))
            
            # Set directory variables
            folder_dir = f"{main_folder_dir}HDV_RUNES\\"
            HDV_name = "HDV_RUNES"

        if map_name == "HDV_ITEM":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (840, 830)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(840, 830)
            
            time.sleep(random.uniform(1, 2))
            print("active options")
            
            # Define all click positions in a grid
            click_positions = [
                # First row - Y=580
                (600, 580), (645, 580), (690, 580), (735, 580), (780, 580),
                # Second row - Y=625
                (600, 625), (645, 625), (690, 625), (735, 625), (780, 625),
                # Third row - just one click
                (600, 670)
            ]
            
            # Click all positions with random delay
            for x, y in click_positions:
                left_click(x, y)
                time.sleep(random.uniform(0.7, 1.2))
            
            # Set directory variables
            folder_dir = f"{main_folder_dir}HDV_ITEM\\"
            HDV_name = "HDV_ITEM"

        if map_name == "HDV_CONSUMABLE":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (1890, 550)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1890, 550)
            time.sleep(random.uniform(1, 2))

            # Define all the Y ranges to click (with same X coordinate)
            click_ranges = [
                # First range
                range(865, 1040 + 25, 25),
                
                # After first scroll
                range(505, 630 + 25, 25),
                
                # Individual clicks (converted to a list for consistency)
                [675, 700, 730, 770],
                
                # After second scroll
                range(710, 960 + 25, 25),

                [1000, 1040],
            ]
            
            # Function to perform clicks for a range of positions
            def click_range(positions):
                for y in positions:
                    left_click(645, y)
                    time.sleep(random.uniform(0.7, 1.2))
            
            # Process the first range
            click_range(click_ranges[0])
            
            # Scroll and process second range
            scroll()
            click_range(click_ranges[1])
            
            # Process individual clicks
            click_range(click_ranges[2])
            
            # Scroll and process final range
            scroll()
            click_range(click_ranges[3])

            click_range(click_ranges[4])


            folder_dir = f"{main_folder_dir}HDV_CONSUMABLE\\"
            HDV_name = "HDV_CONSUMABLE"

        if map_name == "HDV_RESOURCES":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (730, 715)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(730, 715)
            time.sleep(random.uniform(1, 2))

            # Define all the Y ranges to click (with same X coordinate)
            click_ranges = [
                # First range
                range(575, 875 + 25, 25),

                # After first scroll
                range(605, 1040 + 25, 25),
                
                # After second scroll
                range(525, 990 + 25, 25),

                # After second scroll
                range(885, 1040 + 25, 25),

                [710]
            ]
            
            # Function to perform clicks for a range of positions
            def click_range(positions):
                for y in positions:
                    left_click(630, y)
                    time.sleep(random.uniform(0.7, 1.2))

            click_range(click_ranges[0])
            
            for _ in range(4):
                pyautogui.scroll(-250)

            click_range(click_ranges[1])

            scroll()
            click_range(click_ranges[2])

            scroll()
            click_range(click_ranges[3])

            click_range(click_ranges[4])

            folder_dir = f"{main_folder_dir}HDV_RESOURCES\\"
            HDV_name = "HDV_RESOURCES"

        time.sleep(random.uniform(0.1, 0.2))
        all_item = screen_shot_items(folder_dir, HDV_name)

        if all_item:
            return True


    def map(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map=None):
        """
        Manages the navigation and interaction based on the current map.

        Parameters:
        - current_map (str): The name of the current map being processed.
        """
        map_names = [
            "HDV_RUNES",
            "HDV_ITEM",
            "HDV_CONSUMABLE",
            "HDV_RESOURCES",
        ]

        # Start from the beginning or from a specific map
        if starting_map in map_names:
            start_index = map_names.index(starting_map)
        else:
            start_index = 0
            starting_map = map_names[0]  # Set starting_map to first map if not provided
        
        # Process each map in sequence
        for i in range(start_index, len(map_names)):
            current_map = map_names[i]
            print(f"Proceed for the map : {current_map}")
            
            # Process the current map
            HDV_done = item_type(current_map, main_folder_dir)
            
            if HDV_done:
                print(f"{current_map} done, proceed to next HDV")
                
                # Check if there's a next map to process
                if i < len(map_names) - 1:
                    next_map = map_names[i + 1]
                    # Navigate to the next map
                    map_switch(current_map, next_map)
                else:
                    # All maps have been processed
                    print("All HDV processing complete")
                    print("All 4 HDV screenshot")

                    print("Return to HDV runes")

                    click_top()
                    print("click top")
                    time.sleep(random.uniform(3, 3))

                    for _ in range(4):
                        print("click left")
                        click_left()
                        time.sleep(random.uniform(5, 8))

                    
                    # Record end time and calculate duration
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    print(f"HDV Screenshot completed in {duration:.2f} seconds ({duration/60:.2f} minutes)")


                    # HDV_Reader()

                    break


    def map_switch(current_map, next_map):
        """
        Switches between different HDV types based on the current state.
        """
        print(f"Switching from {current_map} to {next_map}")
        time.sleep(random.uniform(1, 2))
        
        print(f"Navigating from {current_map} to {next_map}")
    
        # Navigation from HDV_RUNES to HDV_ITEM
        if current_map == "HDV_RUNES" and next_map == "HDV_ITEM":
            print("Moving from RUNES to ITEM")
            time.sleep(random.uniform(1, 2))
            click_right()
            time.sleep(random.uniform(1, 2))
            click_right()
            time.sleep(random.uniform(5, 8))
        
        # Navigation from HDV_ITEM to HDV_CONSUMABLE
        elif current_map == "HDV_ITEM" and next_map == "HDV_CONSUMABLE":
            print("Moving from ITEM to CONSUMABLE")
            time.sleep(random.uniform(1, 2))
            click_right()
            time.sleep(random.uniform(5, 8))
            click_right()
            time.sleep(random.uniform(5, 8))
        
        # Navigation from HDV_CONSUMABLE to HDV_RESOURCES
        elif current_map == "HDV_CONSUMABLE" and next_map == "HDV_RESOURCES":
            print("Moving from CONSUMABLE to RESOURCES")
            time.sleep(random.uniform(1, 2))
            click_bottom()
            time.sleep(random.uniform(5, 8))

    def left_click(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def click_right():
        start_pos = pyautogui.position()
        end_pos = (2145, random.uniform(70, 1300))
        move_with_jitter(start_pos, end_pos)
        current_pos = pyautogui.position()
        left_click(current_pos.x, current_pos.y)

    def click_left():
        start_pos = pyautogui.position()
        end_pos = (450, random.uniform(40, 1100))
        move_with_jitter(start_pos, end_pos)
        current_pos = pyautogui.position()
        left_click(current_pos.x, current_pos.y)

    def click_top():
        start_pos = pyautogui.position()
        end_pos = (random.uniform(480, 2060), 30)
        move_with_jitter(start_pos, end_pos)
        current_pos = pyautogui.position()
        left_click(current_pos.x, current_pos.y)

    def click_bottom():
        start_pos = pyautogui.position()
        end_pos = (random.uniform(800, 1200), 1215)
        move_with_jitter(start_pos, end_pos)
        current_pos = pyautogui.position()
        left_click(current_pos.x, current_pos.y)

    def real_click(x, y):
       # Move cursor with SetCursorPos
        ctypes.windll.user32.SetCursorPos(x, y)
        
        # Add a small random delay to simulate human behavior
        time.sleep(random.uniform(0.05, 0.15))
        
        # Create a pointer for dwExtraInfo (0)
        extra_info = DWORD(0)
        p_extra_info = ctypes.pointer(extra_info)
        
        # Create input structure for mouse down
        mouse_down = INPUT()
        mouse_down.type = INPUT_MOUSE
        mouse_down.union.mi.dx = 0
        mouse_down.union.mi.dy = 0
        mouse_down.union.mi.mouseData = 0
        mouse_down.union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
        mouse_down.union.mi.time = 0
        mouse_down.union.mi.dwExtraInfo = p_extra_info
        
        # Create input structure for mouse up
        mouse_up = INPUT()
        mouse_up.type = INPUT_MOUSE
        mouse_up.union.mi.dx = 0
        mouse_up.union.mi.dy = 0
        mouse_up.union.mi.mouseData = 0
        mouse_up.union.mi.dwFlags = MOUSEEVENTF_LEFTUP
        mouse_up.union.mi.time = 0
        mouse_up.union.mi.dwExtraInfo = p_extra_info
        
        # Send mouse down event
        ctypes.windll.user32.SendInput(1, ctypes.byref(mouse_down), ctypes.sizeof(INPUT))
        
        # Add a small delay between down and up events
        time.sleep(random.uniform(0.05, 0.15))
        
        # Send mouse up event
        ctypes.windll.user32.SendInput(1, ctypes.byref(mouse_up), ctypes.sizeof(INPUT))

    def main_bot():
        """
        Main entry point to start the HDV screenshot and interaction process.
        """
        main_folder_dir = main_folder
        folder_dir_tmp = tmp_folder
        map_name_tmp = "coordinate_tmp"
        map(main_folder_dir, folder_dir_tmp, map_name_tmp)

    # Record start time
    start_time = time.time()
    main_bot()
    


if __name__ == "__main__":
    try:

        # Execute screenshot function
        HDV_Screenshot()

        #HDV_Reader()
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")
