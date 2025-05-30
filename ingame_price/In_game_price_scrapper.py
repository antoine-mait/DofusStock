import pyautogui
import random
import time
import numpy as np
import os
import win32api
import win32con
import ctypes
import concurrent.futures
import cv2
import keyboard
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
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


def IMG_Blackout():

    def detect_and_blackout_panoplie_icons(img_array, template_path):
        """Detect panoplie icons using template matching and blackout them."""
        try:
            # Convert template to numpy array
            template = np.array(Image.open(template_path))
            
            # Get image dimensions to ensure we don't go out of bounds
            img_height, img_width = img_array.shape[:2]
            
            # Define the specific region to search (x, y, width, height)
            # Adjusted to look at the right side of the item names
            search_region = (230, 0, 50, min(1000, img_height))
            
            # Extract the region to search
            region_to_search = img_array[search_region[1]:search_region[1]+search_region[3], 
                                         search_region[0]:search_region[0]+search_region[2]]
            
            # Convert both images to grayscale for template matching
            region_gray = cv2.cvtColor(region_to_search, cv2.COLOR_RGB2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(region_gray, template_gray, cv2.TM_CCOEFF_NORMED)

            # Set threshold for matches
            threshold = 0.35
            loc = np.where(result >= threshold)
            
            # Get template dimensions
            h, w = template_gray.shape
            
             # Blackout all matches within the region
            for pt in zip(*loc[::-1]):
                # Calculate coordinates in the original image
                original_x = pt[0] + search_region[0]
                original_y = pt[1] + search_region[1]
                
                # Blackout the detected area in the original image
                img_array[original_y:original_y + h, original_x:original_x + w] = 0

            return img_array
            
        except Exception as e:
            print(f"Error detecting panoplie icons: {e}")
            return img_array

    def blackout(IMAGE1, blackout_folder, template_path, directory):
        
        """Blackout specific regions of the image."""
        region1 = (250, 0, 450, 1000)
        region2 = (0, 0, 40, 1000)
        region3 = (610, 0, 670, 1000)

        try:
            img = Image.open(IMAGE1)
            
            # Convert image to an array for faster pixel manipulation
            img_array = np.array(img)

            # Apply blackouts using numpy slicing
            img_array[region1[1]:region1[3], region1[0]:region1[2]] = 0  # Blackout first region
            img_array[region2[1]:region2[3], region2[0]:region2[2]] = 0  # Blackout second region
            img_array[region3[1]:region3[3], region3[0]:region3[2]] = 0  # Blackout third region

            if directory == "HDV_ITEM":
                img_array = detect_and_blackout_panoplie_icons(img_array, template_path) #icon pos

            os.makedirs(blackout_folder, exist_ok=True)
            blackout_path = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
            
            # Convert back to an Image object and save
            Image.fromarray(img_array).save(blackout_path)

            return blackout_path

        except KeyboardInterrupt:
            print("\nScript stopped with Ctrl + C.")
        except Exception as e:
            print(f"Error processing image: {e}")

    def main():
        """Blackout region to help OCR reading later."""
        user_input = "y" #input("Do you want to Blackout the screenshot ? (y/n)")
        all_results = []

        template_path = os.path.join(tmp_folder, 'panoplie_icon.jpg')

        # Check if template exists
        if not os.path.exists(template_path):
            print(f"Warning: Template file not found at {template_path}")
            template_path = None  # Skip template matching if file doesn't exist

        if user_input == "y":
            for directory in ["HDV_CONSUMABLE", "HDV_ITEM", "HDV_RESOURCES", "HDV_RUNES" , "HDV_CREATURE"]:
                print(f"Processing img in {directory} folder")
                path = os.path.join(main_folder, f"{directory}", f"{directory}_PRICE_IMG")

                blackout_folder = os.path.join(main_folder, f"{directory}", "BLACKOUT_PRICE")

                image_files = [os.path.join(path, f) for f in os.listdir(path) 
                              if os.path.isfile(os.path.join(path, f))]
                
                # Create a thread pool and process all images
                with ThreadPoolExecutor() as executor:
                    # Submit each image to the thread pool
                    futures = [executor.submit(blackout, img_path, blackout_folder, template_path , directory) for img_path in image_files]

                    # Wait for all tasks to complete and collect results
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()
                            if result:  # Only add non-None results
                                all_results.append(result)
                        except Exception as e:
                            print(f"Task generated an exception: {e}")
                
                print(f"Completed processing {len(image_files)} images in {directory}")
            
            print(f"Total processed images: {len(all_results)}")
    
    main()

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
            "HDV_CREATURE": 65, #65
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

        if map_name == "HDV_CREATURE":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (1300, 400)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1300, 400)
            
            time.sleep(random.uniform(1, 2))
            print("active options")
            
            # Define Y positions to click (all with the same X coordinate of 670)
            y_positions = [715, 785, 890, 575, 600, 625, 650, 680, 750, 825, 850, 925, 950, 975]
            
            # Click all positions with random delay
            for y in y_positions:
                left_click(670, y)
                time.sleep(random.uniform(1, 1.2))
            
            # Set directory variables
            folder_dir = f"{main_folder_dir}HDV_CREATURE\\"
            HDV_name = "HDV_CREATURE"

        if map_name == "HDV_RUNES":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (1250, 550)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1250, 550)
            
            time.sleep(random.uniform(1, 2))
            print("active options")
            
            # Define Y positions to click (all with the same X coordinate of 670)
            y_positions = [575, 600, 625, 650, 680, 705]
            
            # Click all positions with random delay
            for y in y_positions:
                left_click(670, y)
                time.sleep(random.uniform(1, 1.2))
            
            # Set directory variables
            folder_dir = f"{main_folder_dir}HDV_RUNES\\"
            HDV_name = "HDV_RUNES"

        if map_name == "HDV_ITEM":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (1500, 870)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1500, 870)
            
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
                time.sleep(random.uniform(1, 1.2))
            
            # Set directory variables
            folder_dir = f"{main_folder_dir}HDV_ITEM\\"
            HDV_name = "HDV_ITEM"

        if map_name == "HDV_CONSUMABLE":
            print("click on hdv")
            # Move to HDV position
            start_pos = pyautogui.position()
            end_pos = (1650, 770)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1650, 770)
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
                    time.sleep(random.uniform(1, 1.2))
            
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
            end_pos = (1660, 400)
            move_with_jitter(start_pos, end_pos)
            time.sleep(random.uniform(1, 2))
            real_click(1660, 400)
            time.sleep(random.uniform(1, 2))

            # Define all the Y ranges to click (with same X coordinate)
            y_increment = 26
            click_ranges = [
                # First range
                range(575, 875 + y_increment, y_increment),

                # After first scroll
                range(605, 1040 + y_increment, y_increment),
                
                # After second scroll
                range(500, 990 + y_increment, y_increment),

                # After second scroll
                range(885, 1040 + y_increment, y_increment),

            ]
            
            # Function to perform clicks for a range of positions
            def click_range(positions):
                for y in positions:
                    left_click(630, y)
                    time.sleep(random.uniform(1, 1.2))

            click_range(click_ranges[0])
            
            for _ in range(4):
                pyautogui.scroll(-250)

            click_range(click_ranges[1])

            scroll()
            click_range(click_ranges[2])

            scroll()
            click_range(click_ranges[3])

            folder_dir = f"{main_folder_dir}HDV_RESOURCES\\"
            HDV_name = "HDV_RESOURCES"

        time.sleep(random.uniform(0.1, 0.2))
        all_item = screen_shot_items(folder_dir, HDV_name)

        if all_item:
            return True


    def map(main_folder_dir, starting_map=None):
        """
        Manages the navigation and interaction based on the current map.

        Parameters:
        - current_map (str): The name of the current map being processed.
        """
        map_names = [
            "HDV_CREATURE",
            "HDV_RUNES",
            "HDV_ITEM",
            "HDV_RESOURCES",
            "HDV_CONSUMABLE",
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

                    print("Return to HDV Creature")
                    time.sleep(random.uniform(1,1.2))

                    real_click(1980 , 335)
                    time.sleep(random.uniform(1,1.2))

                    real_click(350 , 1385)
                    travel = "/travel -25,38"
                    for char in travel:
                        keyboard.write(char, delay=0.05)
                    keyboard.press_and_release('enter')
                    time.sleep(random.uniform(0.5,1))
                    keyboard.press_and_release('enter')
                    time.sleep(random.uniform(25,28))

                    
                    # Record end time and calculate duration
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    print(f"HDV Screenshot completed in {duration:.2f} seconds ({duration/60:.2f} minutes)")

                    break

    def map_switch(current_map, next_map):
        """
        Switches between different HDV types based on the current state.
        """
        print(f"Switching from {current_map} to {next_map}")
        time.sleep(random.uniform(1, 2))
        
        print(f"Navigating from {current_map} to {next_map}")
    
        # Navigation from HDV_CREATURE to HDV_RUNES
        if current_map == "HDV_CREATURE" and next_map == "HDV_RUNES":
            print("Moving from CREATURE to RUNE")
            time.sleep(random.uniform(1, 2))
            click_left()
            time.sleep(random.uniform(8, 10))

        # Navigation from HDV_RUNES to HDV_ITEM
        if current_map == "HDV_RUNES" and next_map == "HDV_ITEM":
            print("Moving from RUNES to ITEM")
            real_click(350 , 1385)
            travel = "/travel -28,35"
            for char in travel:
                keyboard.write(char, delay=0.05)
            keyboard.press_and_release('enter')
            time.sleep(random.uniform(0.5,1))
            keyboard.press_and_release('enter')
            time.sleep(random.uniform(25,28))

        # Navigation from HDV_ITEM to HDV_RESOURCES
        elif current_map == "HDV_ITEM" and next_map == "HDV_RESOURCES":
            print("Moving from ITEM to RESSOURCES")
            time.sleep(random.uniform(1, 2))
            print("click right")
            click_right()
            time.sleep(random.uniform(8,10))
            print("click top")
            real_click(1950, 120)
            time.sleep(random.uniform(8, 10))

    
        # Navigation from HDV_RESOURCES to HDV_CONSUMABLE
        elif current_map == "HDV_RESOURCES" and next_map == "HDV_CONSUMABLE":
            print("Moving from RESOURCES to CONSUMABLE")
            time.sleep(random.uniform(1, 2))
            print("click bot")
            click_bottom()
            time.sleep(random.uniform(8,10))
            click_right()
            time.sleep(random.uniform(8,10))
            click_right()
            time.sleep(random.uniform(8,10))
            click_bottom()
            time.sleep(random.uniform(8,10))

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
        end_pos = (random.uniform(500, 2060), 36)
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
        map(main_folder_dir)

    # Record start time
    start_time = time.time()
    main_bot()
    
if __name__ == "__main__":
    try:

        # Execute screenshot function
        # HDV_Screenshot()

        IMG_Blackout()

    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")
