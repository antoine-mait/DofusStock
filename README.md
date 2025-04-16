# DofuStock - Dofus Market Tracker

DofuStock is a Django web application for tracking items, prices, and crafting opportunities in the MMORPG Dofus. The application helps players make informed economic decisions by providing up-to-date market data and crafting cost calculations.

## Distinctiveness and Complexity

This project is distinct from other course projects in several ways:

1. **External API Integration**: DofuStock connects to a Dofus API to fetch comprehensive item data, including equipment, consumables, resources, and mounts, along with their properties, effects, and crafting recipes.

2. **Integration with External Game Data**: Unlike traditional web applications, DofuStock connects directly to the Dofus game through automated scraping. It captures, processes, and analyzes in-game market data using computer vision techniques (OpenCV) and OCR (Pytesseract).

3. **Multi-stage Data Processing Pipeline**: The application implements a sophisticated pipeline that handles screenshot capture, image preprocessing, text extraction, and database integration. This demonstrates complex system design beyond basic CRUD operations.

4. **Real-time Economic Analysis**: The app calculates optimal crafting decisions by comparing market prices against crafting costs, requiring complex algorithms to determine resource requirements and total expenses.

5. **External Web Scraping**: The application can extract item information from the popular Dofusbook websites using Playwright, providing a unique integration with the game's ecosystem.

6. **Asynchronous Processing**: The application uses multithreading and multiprocessing for performance-critical operations, enabling efficient processing of large datasets.

The complexity is evident in:
- Advanced JavaScript for dynamic content loading and UI interactions
- Complex database queries with annotations and custom sorting
- Integration of multiple external libraries (Playwright, OpenCV, Pytesseract)
- Custom algorithms for price calculation and resource optimization

## File Contents

### Django Models and Views
- `models.py`: Defines database models for User, Item, Effect, Recipe, Craftlist, and Price.
- `views.py`: Contains views for user authentication, item encyclopedia, detail pages, API endpoints for searching/filtering, and the build URL scraper.

### JavaScript Files
- `base.js`: Core initialization and shared utilities, including theme switching and filename sanitization.
- `encyclopedia.js`: Implements item search, category filtering, and dynamic content loading.
- `craft_list.js`: Manages user craft lists, including adding/removing items and UI updates.
- `extract_url_data.js`: Handles URL extraction from Dofusbook websites and processes results. 
    - ( test link : https://d-bk.net/fr/d/1K4FD)

### Data Collection Systems
- `api-fetcher folder`
  - `api_data_fetch.py`: Connects to the DofusDude API to fetch comprehensive item data, downloads item images, and populates the database with items, effects, and recipes.

- `ingame-price folder`
  - `main.py`: Coordinates the complete HDV price scraping pipeline.
    - `In_game_price_scrapper.py`: Controls the game client to capture screenshots.
    - `read_ingame_price.py`: Extracts text data from images using OCR.
    - `import_price.py`: Updates the database with extracted price data.

## How to Run the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dofustock.git
   cd dofustock
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create Django base settings.py in dofustock_project folder and add the installed_apps.

5. Create urls.py in the same folder and link the views to a path. 

6. Set up the database:
   ```bash
   python manage.py migrate
   ```

7.  Create the website.sqlite3 in the main folder

8. Populate the database with the Api:
   ```bash
   python api_data_fetch.py 
   ```

9. Open the game on the correct game map and start the scraping process:
   ```bash
   python main.py 
   ```

10. Create a superuser account:
   ```bash
   python manage.py createsuperuser
   ```

11.  Run the development server:
   ```bash
   python manage.py runserver
   ```

12. Access the application at http://127.0.0.1:8000/

## Additional Information

- **API Data Fetch**: To populate the database with items from the Dofus API, run:
  ```bash
  python api_data_fetch.py
  ```
  You'll need to set the `DOFUS_API` environment variable in your `.env` file with the appropriate API endpoint.

- **Image Directory Structure**: The application automatically organizes item images in a specific directory structure under `/media/IMG/[category]/[item_type]/`.

- **Price Scraping Setup**: For the automatic price scraper to work, the Dofus client must be running at 2K resolution with the character positioned at HDV Creature in Brakmar city.

- **Environmental Variables**: Create a `.env` file with the following settings:
  ```
  DATABASE_URL=your_database_url
  DOFUS_API=dofus_api_endpoint
  TESSERACT_PATH=path_to_tesseract_executable
  SCREENSHOT_DIR=path_to_save_screenshots
  ```

- **Browser Requirements**: The Playwright-based scraping requires a Chromium-based browser.

- **Ingame scrapping**: The ingame scrapping method take 20 minutes. This project is a learning project and shouldn't be commercialise as this automated scrapping method is not allowed by the game policie.

## Requirements

See `requirements.txt` for the complete list of Python packages needed to run this application.

# Future Improvements

## Multi-Server Support
- Implement server selection functionality to allow users to choose which game server's market data they want to visualize
- Create database structure to link items with server-specific price data
- Modify the scraping pipeline to collect prices from multiple servers
- Add server filtering in the UI to let users switch between different server economies
- Incorporate server comparison features to highlight arbitrage opportunities between different servers

## Data Visualization Enhancements
- Add historical price charts to track item value over time
- Implement price trend indicators (rising, falling, stable)
- Create market volatility metrics for each item category

## User Experience Improvements
- Develop a more user-friendly setup for the scraping process with different resolution options
- Add customizable alerts for price thresholds
- Implement a watchlist feature for tracking specific items of interest

# Troubleshooting

## OCR Text Recognition Issues
- Multiple name corrections needed in the `correction.py` file for OCR mistakes
- Common character confusion: 'o', 'a', 'e', 't', 'f', etc. causing item names to not match correctly
- Solution: Manually check "missing.csv" , compare with ingame item name , and add the wrong name with his correction ,
  in the correction.py : 
  ```bash
  correction_dict = {"ostrale":"astrale"} 
      # This is an example, more than 300 correction were needed on my side
  ```

## Resolution and Display Problems
- The screen capture functionality is currently optimized for 2K resolution
- If using a different resolution, text positions, and ingame scrapping won't work
- Solution: Adjust all coordinate values in `In_game_price_scrapper.py` to match your screen resolution

## Game Client Positioning
- The character must be positioned at HDV Creature in Brakmar city
- If positioned incorrectly, the scraper will not find the expected UI elements
- Solution: Ensure your character is at the correct location before starting the scraping process

## API Connection Failures
- If the DofusDude API is unavailable or returns errors, item data may not populate correctly
- Solution: Check your API key and endpoint in the `.env` file, and verify the API status
