# DofuStock - Dofus Market Tracker

## Project Purpose and Personal Statement

I created DofuStock to solve a problem faced by players of the MMORPG Dofus: optimizing the in-game economy to make informed crafting and trading decisions. I noticed that players spent significant time manually calculating crafting costs and comparing market prices, often with outdated information. DofuStock automates this entire process, providing real-time market data and sophisticated crafting analysis.

Building this project allowed me to combine my passion for game optimization with advanced programming techniques. I particularly focused on integrating computer vision and OCR technology to extract data directly from the game client - a technical challenge that required implementing custom image processing algorithms and fuzzy matching strategies to handle recognition errors. This automation component distinguishes my project significantly from standard web applications that rely solely on user input or API data.

Throughout development, I leveraged knowledge obtained from both CS50 and CS50W, going well beyond just web development fundamentals. The project's scale - handling more than a thousand items from the API and real-time data - made it substantially more complex than previous exercises. I gained valuable experience in:
- Implementing complex recursive algorithms for crafting calculations
- Designing systems that integrate external data sources with advanced error handling
- Building a responsive frontend that visualizes complex economic relationships
- Solving real-world OCR challenges with computer vision techniques

This project represents a comprehensive full-stack solution that bridges gameplay mechanics with economic optimization through advanced technologies.

##  Table of Contents

- [DofuStock - Dofus Market Tracker](#dofustock---dofus-market-tracker)
  - [Project Purpose and Personal Statement](#project-purpose-and-personal-statement)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Distinctiveness and Complexity](#distinctiveness-and-complexity)
    - [Distinctiveness](#distinctiveness)
      - [Comparison with Project 1 (Wiki)](#comparison-with-project-1-wiki)
      - [Comparison with Project 2 (Commerce)](#comparison-with-project-2-commerce)
      - [Comparison with Project 3 (Mail)](#comparison-with-project-3-mail)
      - [Comparison with Project 4 (Network)](#comparison-with-project-4-network)
    - [Complexity](#complexity)
  - [Files and Structure](#files-and-structure)
    - [Django Backend Files](#django-backend-files)
      - [`models.py`](#modelspy)
      - [`views.py`](#viewspy)
      - [`import_price.py`](#import_pricepy)
    - [JavaScript Files](#javascript-files)
      - [`base.js`](#basejs)
      - [`encyclopedia.js`](#encyclopediajs)
      - [`craft_list.js`](#craft_listjs)
      - [`extract_url_data.js`](#extract_url_datajs)
    - [HTML Template Files](#html-template-files)
      - [`layout.html`](#layouthtml)
      - [`encyclopedie.html`](#encyclopediehtml)
      - [`item.html`](#itemhtml)
      - [`craft_list.html`](#craft_listhtml)
      - [`login.html` and `register.html`](#loginhtml-and-registerhtml)
    - [CSS Files](#css-files)
      - [`main.css`](#maincss)
      - [`encyclopedia.css`](#encyclopediacss)
      - [`item-detail.css`](#item-detailcss)
      - [`craft-list.css`](#craft-listcss)
    - [Data Collection System Files](#data-collection-system-files)
      - [`In_game_price_scrapper.py`](#in_game_price_scrapperpy)
      - [`read_ingame_price.py`](#read_ingame_pricepy)
  - [Mobile Responsiveness](#mobile-responsiveness)
  - [How to Run the Application](#how-to-run-the-application)
  - [Additional Information](#additional-information)
    - [Requirements](#requirements)
    - [Environmental Variables](#environmental-variables)
    - [Technical Challenges and Solutions](#technical-challenges-and-solutions)
    - [Ethical Considerations](#ethical-considerations)
    - [Future Development](#future-development)

---

## Overview

**DofuStock** is a comprehensive Django web application designed to track items, prices, and crafting opportunities in the MMORPG *Dofus*. It serves as an **economic analysis tool**, helping players make informed decisions by providing:

- Up-to-date market data
- Crafting cost calculations
- Build optimization
- Integrated OCR and computer vision support for in-game data capture

## Distinctiveness and Complexity

### Distinctiveness

My project DofuStock is distinctively different from all previous CS50W projects. It's not just another social network, e-commerce site, wiki, or email client - it's a specialized data analytics platform focused on game economics with automated data acquisition capabilities. What makes my project unique is that it bridges real-time in-game data with economic analysis through advanced technologies like computer vision and OCR. This creates a fundamentally different application category focused on data harvesting, processing, and algorithmic calculation rather than simple content management or user interactions.

The application uses Django's models in sophisticated ways, creating complex relationships between items, recipes, effects, and prices. The JavaScript components go far beyond simple DOM manipulation to implement real-time calculations, dynamic filtering, and interactive data visualization. My database schema handles thousands of items with multiple relationships, historical price data, and crafting dependencies - a level of data complexity not present in any of the previous projects.

#### Comparison with Project 1 (Wiki)

1. **Implements real-time data processing** of market prices and crafting opportunities rather than static content management
2. **Uses computer vision and OCR technology** to extract game data, going far beyond Wiki's simple file operations
3. **Features complex database models** with relationships between items, recipes, and prices, while Wiki had no database models
4. **Performs algorithmic calculations** for crafting optimization and profit analysis rather than just displaying content
5. **Creates a dynamic user experience** with real-time data updates and interactive components instead of static page rendering

#### Comparison with Project 2 (Commerce)

1. **Implements real-time data acquisition** through computer vision and OCR technology to extract game data, while Commerce relies only on manual user input for listings.
2. **Features complex algorithmic processing** for crafting calculations with recursive dependency trees, compared to Commerce's simple bidding logic.
3. **Integrates multiple external data sources** including in-game screenshots, APIs, and web scraping, whereas Commerce is entirely self-contained.
4. **Uses advanced image processing** with OpenCV and Tesseract for text extraction, while Commerce has no image processing capabilities.
5. **Implements concurrent processing** for performance optimization, compared to Commerce's standard sequential processing.

#### Comparison with Project 3 (Mail)

1. **Features an automated data collection system** using computer vision and OCR for extracting game information, whereas Mail simply stores and displays user-submitted content.
2. **Implements complex algorithmic calculations** for multi-level crafting costs and profit analysis, while Mail focuses on basic CRUD operations for email messages.
3. **Integrates with external systems** including game clients and third-party APIs, compared to Mail's entirely self-contained architecture with no external interactions.
4. **Provides sophisticated data analysis** with price tracking, trend detection, and optimization algorithms, whereas Mail only implements basic message filtering and organization.
5. **Utilizes advanced technologies** including OpenCV for image processing and multi-threading for performance, while Mail relies on standard web technologies and a simple RESTful API.


#### Comparison with Project 4 (Network)

1. **Implements Automated Data Collection System**
   - **Network**: Simply stores and displays user-submitted posts with basic CRUD operations.
   - **DofuStock**: Uses computer vision and OCR technology to automatically extract game data, with preprocessing filters and error correction algorithms.

2. **Features Complex Calculation Algorithms**  
   - **Network**: Has simple algorithms for following users and displaying posts.
   - **DofuStock**: Implements recursive crafting calculations with dependency detection, cost optimization, and profit analysis using caching techniques.

3. **Integrates with External Systems**
   - **Network**: Is entirely self-contained with no external data sources.
   - **DofuStock**: Integrates with game client screen capture, external APIs, and web scraping with data reconciliation.

4. **Utilizes Advanced Technologies**
   - **Network**: Uses basic Django and JavaScript for AJAX page loading.
   - **DofuStock**: Leverages computer vision (OpenCV), OCR (Pytesseract), multi-threading, and fuzzy matching algorithms.

5. **Implements Sophisticated Data Models**
   - **Network**: Has simple models for User, Post, Follow, and Like.
   - **DofuStock**: Features complex models with multi-level relationships and specialized business logic for items, recipes, effects, and price tracking.

### Complexity

The complexity of DofuStock far exceeds the requirements of CS50W projects in several substantial ways:

1. **Advanced Data Collection Pipeline**: The application implements a four-stage automated data collection system that handles:
   - Automated in-game navigation and screenshot capture using programmatic input simulation with pyautogui and win32api for precise mouse control
   - Image preprocessing using computer vision techniques (OpenCV) for enhanced OCR accuracy, including custom filtering and region detection
   - OCR text extraction with error correction algorithms (Pytesseract) to handle game font peculiarities and imprecisions
   - Database integration with multiple fuzzy matching strategies to handle OCR imperfections and character recognition errors

2. **Integration of Multiple External Systems**:
   - DofusDude API integration for comprehensive item data with custom caching mechanisms to minimize API calls
   - Automated in-game data collection through screen capture with coordinate mapping and pixel-perfect mouse movement
   - Web scraping of external Dofusbook websites for build data using custom parsers with error recovery mechanisms
   - Complex synchronization between these different data sources with reconciliation of inconsistencies

3. **Complex Algorithmic Processing**:
   - Multi-level crafting cost calculations that recurse through crafting trees with circular dependency detection to prevent infinite loops
   - Price comparison algorithms between market buying vs. crafting with profit margin analysis and opportunity cost calculations
   - Resource optimization across multiple crafting projects with shared dependencies and priority-based allocation
   - Custom caching and memoization techniques to optimize performance for computationally expensive operations

4. **Advanced Front-End Functionality**:
   - Dynamic content loading with AJAX for seamless user experience and reduced page reloads
   - Complex JavaScript-powered search and filtering system with debounce implementation for performance optimization
   - Mobile-responsive design with advanced CSS techniques including grid layouts and media queries
   - Interactive data visualization with dynamic updates based on price fluctuations and market trends

5. **Advanced Django Usage**:
   - Complex database models with multiple relationships and custom managers for specialized queries
   - Custom Django annotations and queries for efficient data retrieval with optimization techniques
   - Integration of external libraries within the Django framework with middleware customization for session management
   - Custom authentication and permission systems for different user roles and access levels

The technical implementation involves significant complexity beyond basic CRUD operations or simple data display:

- **Computer Vision and OCR Integration**: Using OpenCV and Pytesseract for extracting text from screenshots, with custom preprocessing filters to improve text recognition accuracy for the game's unique font, including adaptive thresholding, noise reduction, and region detection algorithms.
- **Multi-threading and Multi-processing**: For performance-critical operations, using Python's concurrent processing libraries to parallelize data processing across multiple CPU cores.
- **Web Automation**: Using Playwright for external website data extraction with custom navigation logic, timing controls, and error recovery mechanisms.
- **Complex Database Queries**: Including annotations, custom sorting, and multiple relationship traversals with optimization techniques such as select_related and prefetch_related for performance.

## Files and Structure

### Django Backend Files

#### `models.py`
Contains all database models for the application with complex relationships and business logic:

- `User`: Extended Django user model with additional preferences and settings for customization
  - Includes profile picture handling, notification preferences, and custom validation
  - Implements custom authentication methods and permission checks

- `Item`: Core model for game items with properties like ID, name, category, type, and level
  - Implements complex ORM relationships to other models
  - Contains custom manager methods for specialized queries
  - Includes methods for price history analysis and trend detection

- `Effect`: Represents special effects or properties of items with strength values
  - Handles complex effect calculations and comparisons
  - Implements normalization of different effect types for comparison

- `Recipe`: Defines crafting requirements for items (resources and quantities)
  - Uses many-to-many relationships with through tables
  - Implements custom methods for cost calculations and resource optimization
  - Handles circular dependencies in crafting trees

- `Craftlist`: Links users to collections of items they're interested in crafting
  - Tracks user preferences for crafting and resource collection
  - Implements custom prioritization algorithms for resource allocation
  - Provides interfaces for batch operations on multiple craft items

- `Price`: Historical price records for items with timestamps and market analysis fields
  - Implements time-based queries and trend analysis
  - Provides data extraction methods for visualization
  - Includes statistical methods for price fluctuation analysis

This file demonstrates advanced Django model usage including:
- Complex relationships between models (many-to-many with through tables)
- Custom model methods and properties for business logic
- Advanced query optimization techniques
- Custom model managers for specialized data access

#### `views.py`
Contains all view functions that handle user requests and render templates:

- Authentication views (`login_view`, `logout_view`, `register`) with custom validation logic
  - Implements security features like rate limiting and CSRF protection
  - Handles custom user model integration and permissions

- Item encyclopedia views (`encyclopedie`, `item_detail`) with advanced querying
  - Optimizes database queries for performance with select_related and prefetch_related
  - Implements caching strategies for frequently accessed data
  - Provides complex filtering and sorting mechanisms

- API-like endpoints for dynamic content (`get_item_types`, `get_items`, `search_items`)
  - Returns properly formatted JSON responses with appropriate status codes
  - Implements error handling and input validation
  - Supports pagination and result limiting for performance

- Web scraping functionality (`scrape_build`, `scrape_dofus_build_items`)
  - Integrates with Playwright for external data extraction
  - Implements error handling and retry mechanisms
  - Processes and normalizes extracted data for database integration

- Craft list management (`craft_list`, `toggle_craftlist`)
  - Handles complex user interactions and state management
  - Implements AJAX endpoints for dynamic updates
  - Provides calculations for resource requirements and costs

- Complex crafting calculations with recursive algorithms and caching mechanisms
  - Implements dependency traversal with cycle detection
  - Uses memoization for performance optimization
  - Provides detailed breakdown of costs and requirements

This file demonstrates advanced Django view patterns including:
- Class-based views for complex functionality
- API endpoints with proper REST conventions
- Integration with external services
- Optimized database access patterns

#### `import_price.py`
Integrates extracted price data with the database with sophisticated data processing:

- Uses multiprocessing for efficient data processing
  - Implements thread pools with the `concurrent.futures` module
  - Optimizes workload distribution across CPU cores
  - Implements thread synchronization for shared resources

- Implements multiple name matching strategies
  - Exact matching for reliable identifications
  - Sanitized name comparison with normalization algorithms
  - Fuzzy matching with Levenshtein distance for OCR errors
  - Hierarchical matching strategy with fallbacks

- Updates price records with custom sanitization and validation
  - Implements data cleaning for OCR errors
  - Validates price ranges against historical data
  - Detects and handles outliers in price data

- Generates reports of matched and missing items
  - Creates detailed logs of the import process
  - Provides statistics on match success rates
  - Identifies problematic items for manual review

This file demonstrates complex data processing techniques including:
- Concurrent processing for performance optimization
- Advanced string matching algorithms
- Database transaction management
- Error handling and reporting

### JavaScript Files

#### `base.js`
Core JavaScript functionality used across the application:

- Theme switching for light/dark mode
  - Uses localStorage for persistence across sessions
  - Implements smooth transitions between themes
  - Detects system preferences for initial setting

- Utility functions for UI interactions
  - Implements debounce and throttle for performance
  - Provides common formatting functions
  - Handles cross-browser compatibility issues

- Global event handlers and DOM initialization
  - Sets up event listeners for common interactions
  - Implements custom event delegation
  - Provides initialization hooks for other modules

- Sets up shared references to DOM elements
  - Creates a centralized registry of UI elements
  - Implements lazy loading for performance
  - Provides access control for DOM manipulation

This file provides the foundation for the application's frontend functionality with a focus on performance optimization and code organization.

#### `encyclopedia.js`
Implements dynamic content loading for the item encyclopedia:

- AJAX-powered search functionality
  - Implements debounce for performance optimization
  - Handles error states and loading indicators
  - Processes and renders search results dynamically

- Category and type filtering with UI feedback
  - Implements complex filter combinations
  - Maintains filter state across page navigation
  - Provides visual feedback on active filters

- Responsive grid layout management
  - Adapts to screen size changes dynamically
  - Implements optimal item display for different devices
  - Uses modern CSS Grid techniques for layout

- Price formatting and display logic
  - Handles currency formatting with localization
  - Implements price comparison visualization
  - Highlights price changes and trends

This file showcases advanced frontend techniques including asynchronous data loading, complex UI state management, and responsive design principles.

#### `craft_list.js`
Manages the user's craft list interface:

- Adding/removing items to craft lists
  - Implements optimistic UI updates with fallbacks
  - Handles complex validation of craft combinations
  - Provides undo functionality for actions

- Dynamic updating of totals when items change
  - Recalculates resource requirements in real-time
  - Updates cost estimates based on current prices
  - Visualizes resource allocation across items

- UI component generation for craft list items
  - Creates dynamic DOM elements for list items
  - Implements drag-and-drop for prioritization
  - Provides detailed tooltips with craft information

- CSRF token management for secure requests
  - Implements token refresh mechanisms
  - Handles authentication failures gracefully
  - Secures all AJAX communications

This file implements complex UI interactions with a focus on user experience and data integrity, demonstrating advanced JavaScript techniques for dynamic application state management.

#### `extract_url_data.js`
Handles the Dofusbook URL scraping feature:

- Extracts build data from external websites
  - Parses URL parameters for processing
  - Validates input before submission
  - Handles various URL formats and versions

- Processes results into usable format
  - Normalizes data structure for consistency
  - Handles error cases and edge conditions
  - Implements retry logic for transient failures

- Updates the interface with extracted item lists
  - Dynamically generates UI components for results
  - Provides grouping and categorization options
  - Implements batch operations on extracted items

- Implements local storage for saving extracted data
  - Creates persistent cache of frequent builds
  - Implements versioning for cache invalidation
  - Manages storage limits and cleanup

This file demonstrates integration with external data sources with robust error handling and user feedback mechanisms.

### HTML Template Files

#### `layout.html`
The main layout template that serves as the foundation for all pages:

- Implements a responsive navigation system
  - Provides consistent UI elements across the application
  - Implements conditional rendering based on authentication status
  - Contains theme selection controls with dynamic styling

- Includes essential metadata
  - Sets up proper document structure with language and viewport settings
  - Loads all required JavaScript and CSS resources with proper dependencies
  - Configures CSRF token access for JavaScript components

- Implements theme selector
  - Provides multiple visual themes inspired by in-game aesthetics
  - Contains user interface controls for theme selection
  - Implements persistence of theme preferences

This template provides the structural backbone for all pages with a focus on consistent navigation, responsive design, and theme management.

#### `encyclopedie.html`
The main encyclopedia page for browsing items:

- Implements a category-based filtering system
  - Dynamically generates filter buttons based on available categories
  - Provides visual feedback for active filters
  - Implements event handlers for filter interactions

- Features responsive search functionality
  - Implements real-time search with AJAX integration
  - Provides accessible input controls with proper ARIA labels
  - Shows search results with visual formatting for easy scanning

- Contains a dynamic item grid layout
  - Implements responsive grid using modern CSS techniques
  - Handles variable content sizes with consistent spacing
  - Provides optimal display for different screen sizes

This template serves as the main entry point for item discovery with advanced filtering and search capabilities, demonstrating effective use of Django template inheritance and dynamic content rendering.

#### `item.html`
The detailed view for individual items:

- Implements a comprehensive item display
  - Shows item images, stats, and metadata with proper formatting
  - Implements conditional rendering for different item categories
  - Provides interactive elements for item management

- Features craftlist integration
  - Implements toggle buttons for adding/removing items from craft lists
  - Shows current status with visual indicators
  - Processes form submissions with CSRF protection

- Displays crafting recipes with cost analysis
  - Shows detailed breakdown of crafting requirements
  - Implements price comparisons between market and crafting costs
  - Provides visual highlighting for optimal crafting decisions

- Implements effect styling system
  - Uses conditional CSS classes based on effect types
  - Provides consistent color coding for different effect categories
  - Implements accessibility features for visual information

This template showcases detailed item information with sophisticated formatting, interactive elements, and comprehensive data presentation techniques.

#### `craft_list.html`
The user's crafting management interface:

- Implements build URL extraction feature
  - Provides input form for external build URLs
  - Shows loading states with spinners and messages
  - Dynamically displays extraction results

- Features detailed item cards
  - Shows comprehensive item information in structured cards
  - Implements resource requirement calculations
  - Provides interactive elements for item management

- Shows aggregated resource requirements
  - Calculates and displays total resources needed
  - Implements cost summaries with price information
  - Shows comparison between market and crafting costs

- Implements removal functionality
  - Provides interactive buttons for item removal
  - Implements client-side item removal with AJAX
  - Updates totals dynamically when items are modified

This template demonstrates complex data presentation with interactive elements, aggregated calculations, and dynamic content updates.

#### `login.html` and `register.html`
Authentication templates with consistent styling:

- Implement security best practices
  - Use CSRF protection for all form submissions
  - Implement proper password handling
  - Show validation messages for input errors

- Feature responsive form layouts
  - Implement accessible form controls with proper labeling
  - Show clear error messages for validation issues
  - Provide navigation between authentication pages

These templates provide a secure and user-friendly authentication experience with consistent styling and proper validation.

### CSS Files

#### `main.css`
The core stylesheet that defines application-wide styling:

- Implements theme system
  - Defines CSS variables for theme colors and dimensions
  - Provides dark/light mode variants with smooth transitions
  - Implements multiple game-inspired themes (Dofusbook, Emeraude, etc.)

- Defines responsive layout foundation
  - Implements mobile-first responsive design principles
  - Uses flexible grid systems and media queries
  - Ensures consistent spacing and typography across devices

- Standardizes UI components
  - Defines button styles with hover and active states
  - Implements form controls with consistent appearance
  - Provides utility classes for common styling needs

This stylesheet establishes the visual foundation for the entire application with a focus on consistency, theming, and responsiveness.

#### `encyclopedia.css`
Styles specific to the encyclopedia page:

- Implements item grid system
  - Uses CSS Grid for responsive item layouts
  - Implements card-based design for item display
  - Provides hover effects and visual feedback

- Styles category filters
  - Implements toggle button appearance
  - Shows active state for selected filters
  - Provides accessible color contrast for all states

- Defines search input styling
  - Implements consistent input appearance
  - Provides visual feedback for focus and input states
  - Ensures proper sizing and spacing for different screens

This stylesheet focuses on the specialized components of the encyclopedia interface with emphasis on filtering, searching, and grid-based item display.

#### `item-detail.css`
Styles for the item detail page:

- Implements two-column layout
  - Uses flexible width distribution for responsive design
  - Implements proper spacing between content sections
  - Provides mobile adaptations for single-column layout

- Styles item header
  - Shows item image with proper sizing and alignment
  - Implements title typography with emphasis
  - Provides action button styling for craft list integration

- Defines effect styling system
  - Implements color-coded effect display
  - Uses specialized classes for different effect types
  - Ensures proper spacing and typography for effect lists

- Styles recipe tables
  - Implements consistent table formatting for recipes
  - Shows resource information with proper alignment
  - Highlights price comparisons with color coding

This stylesheet provides specialized styling for detailed item information with a focus on readability and visual organization.

#### `craft-list.css`
Styles for the crafting management interface:

- Implements card-based layout
  - Defines consistent card styling for items
  - Implements proper spacing and typography
  - Provides visual hierarchy through color and sizing

- Styles resource tables
  - Implements compact table layouts for resources
  - Shows quantities and prices with proper alignment
  - Highlights total calculations with emphasis

- Defines action button styling
  - Implements interactive button appearance
  - Shows hover and active states with visual feedback
  - Provides icon integration for clearer actions

- Styles form elements
  - Implements consistent styling for URL input
  - Shows loading states with proper animations
  - Provides feedback for form submission

This stylesheet focuses on the craft list management interface with emphasis on clear data presentation, interactive elements, and resource visualization.

### Data Collection System Files

#### `In_game_price_scrapper.py`
Implements automated navigation and screenshot capture:

- Simulates mouse movements and clicks with natural motion
  - Implements jitter and variable speed for humanlike movement
  - Uses win32api for precise control at the pixel level
  - Implements safety checks and abort mechanisms

- Takes strategic screenshots of the game interface
  - Calculates optimal regions for capture
  - Implements timing controls for menu transitions
  - Handles resolution independence through relative positioning

- Navigates game menus automatically
  - Maps game coordinate system for reliable navigation
  - Implements state machine for menu traversal
  - Handles error recovery for missed clicks or lag

- Manages multi-stage data collection pipeline
  - Coordinates screenshot capture across multiple game areas
  - Implements proper file naming and organization
  - Provides progress reporting and statistics

This file demonstrates advanced automation techniques with a focus on reliability and error handling in an unpredictable environment.

#### `read_ingame_price.py`
Processes captured screenshots with OCR technology:

- Preprocesses images for optimal text recognition
  - Implements adaptive thresholding for contrast enhancement
  - Uses region detection to isolate text areas
  - Applies noise reduction for cleaner text extraction

- Extracts text with Tesseract OCR
  - Configures OCR parameters for game font specifics
  - Implements language-specific processing
  - Handles multi-line text and formatting

- Post-processes extracted text
  - Applies correction dictionaries for common errors
  - Implements string sanitization for database compatibility
  - Groups related text by spatial positioning

- Integrates extracted data with the database
  - Implements parallel processing for efficiency
  - Handles duplicate detection and resolution
  - Provides detailed logging of extraction results

This file demonstrates advanced image processing and OCR techniques with sophisticated text analysis algorithms.

## Mobile Responsiveness

The application is fully mobile-responsive with:

- Flexible grid layouts that adapt to screen size
  - Uses CSS Grid and Flexbox for modern layouts
  - Implements breakpoints for different device categories
  - Maintains content hierarchy across screen sizes

- Media queries for different device sizes
  - Targets standard breakpoints for consistent experience
  - Implements device-specific optimizations
  - Handles orientation changes gracefully

- Touch-friendly UI elements
  - Implements larger touch targets for mobile
  - Provides touch gestures for common actions
  - Ensures adequate spacing between interactive elements

- Responsive navigation menu
  - Collapses into hamburger menu on small screens
  - Implements smooth transitions between states
  - Provides context-aware navigation options

- Optimized content display
  - Adjusts text size and spacing for readability
  - Prioritizes critical content on small screens
  - Implements progressive disclosure for complex information

The JavaScript components are designed for mobile with event handling that supports both mouse and touch interactions, with special attention to performance optimization for mobile devices.

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

4. Create Django base settings.py in dofustock_project folder and add the installed apps:
   ```python
   INSTALLED_APPS = [
      "dofustock_project",
      "api_fetcher",
      "ingame_price",
      "dofustock_site",
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      'dofustock',
   ]
   ```

5. Create urls.py in the same folder.
      ```python
   from django.contrib import admin
   from django.urls import path
   from django.conf import settings
   from django.conf.urls.static import static
   from dofustock_site import views

   urlpatterns = [
      path("admin/", admin.site.urls),
      path("", views.encyclopedie, name="encyclopedie"),
      path("login", views.login_view, name="login"),
      path("logout", views.logout_view, name="logout"),
      path("register", views.register, name="register"),

      path("encyclopedie", views.encyclopedie, name="encyclopedie"),
      
      path('get-item-types/', views.get_item_types, name='get_item_types'),
      path('get-items/', views.get_items, name='get_items'),
      path('get-items-recipe/<int:ankama_id>/', views.get_items_recipe, name='get_items_recipe'),
      path('item/<int:ankama_id>/', views.item_detail, name='item_detail'),
      path('search-items/', views.search_items, name='search_items'),

      path("craft_list", views.craft_list, name="craft_list"),
      path('scrape-build/', views.scrape_build, name='scrape_build'),
      path("toggle-craftlist/<int:ankama_id>/", views.toggle_craftlist, name="toggle_craftlist"),  
   ] 

   if settings.DEBUG:
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

6. Set up the database:
   ```bash
   python manage.py migrate
   ```

7. Create the website.sqlite3 in the main folder.

8. Populate the database with the API:
   ```bash
   python api_data_fetch.py 
   ```

9. To capture in-game prices (optional):
   - Open the Dofus game client at 2K resolution
   - Position your character at HDV Creature in Brakmar city
   - Run the scraping process:
     ```bash
     python main.py 
     ```

10. Create a superuser account:
    ```bash
    python manage.py createsuperuser
    ```

11. Run the development server:
    ```bash
    python manage.py runserver
    ```

12. Access the application at http://127.0.0.1:8000/

## Additional Information

### Requirements
All required Python packages are listed in requirements.txt, including:
- Django==4.2.7
- Playwright==1.40.0
- OpenCV-Python==4.8.1.78
- pytesseract==0.3.10
- Requests==2.31.0
- Pillow==10.1.0
- NumPy==1.26.2
- python-dotenv==1.0.0
- django-crispy-forms==2.1
- crispy-bootstrap5==0.7
- fuzzywuzzy==0.18.0
- python-Levenshtein==0.21.1

### Environmental Variables
Create a `.env` file with the following settings:
```
DATABASE_URL=your_database_url
DOFUS_API=dofus_api_endpoint
TESSERACT_PATH=path_to_tesseract_executable
SCREENSHOT_DIR=path_to_save_screenshots
MAIN_IMG_FOLDER=path_to_item_images
folder_dir_tmp=path_to_temporary_files
```

### Technical Challenges and Solutions

One of the most significant technical challenges was developing an accurate OCR system that could reliably extract item names and prices from in-game screenshots. The game's custom font and UI layout presented particular difficulties. To overcome this:

1. I implemented custom image preprocessing filters using OpenCV to enhance text clarity before OCR
   - Used adaptive thresholding to handle variable lighting conditions
   - Applied region-based contrast enhancement for better text/background separation
   - Implemented custom noise reduction filters to clean up artifacts

2. Developed a multi-stage text cleaning process to handle common OCR errors
   - Created a specialized correction dictionary for game-specific terms
   - Implemented regular expression patterns to identify and fix common error patterns
   - Built a context-aware correction system that uses item categories to improve matching

3. Created a sophisticated name matching algorithm that could handle partial matches and common OCR mistakes
   - Implemented a hierarchical matching strategy that tries exact matches first
   - Used normalized string comparisons with accent and special character handling
   - Applied Levenshtein distance algorithms for fuzzy matching with configurable thresholds

Another challenge was efficiently calculating crafting costs for items with deep dependency trees. Some items require crafting components that themselves require crafted components, creating complex recursive relationships. I solved this by:

1. Implementing a memoization system to cache intermediate calculations
   - Used a multi-level cache with configurable expiration
   - Implemented cache invalidation strategies for price updates
   - Optimized memory usage with smart reference management

2. Detecting circular dependencies to prevent infinite recursion
   - Built a path tracking system to detect cycles in the dependency graph
   - Implemented alternative calculation paths when cycles were detected
   - Created a visualization system to help understand complex dependencies

3. Building a priority queue system to optimize the calculation order
   - Implemented a topological sort of the dependency graph
   - Used heuristics to prioritize high-impact calculations
   - Created a chunking system to handle very large crafting operations efficiently

### Ethical Considerations
The in-game scraping method takes approximately 20 minutes and should be used responsibly. This project is for educational purposes only and demonstrates technical integration with game systems. Be aware that automated scraping may be against the game's terms of service in some cases.

### Future Development
Planned enhancements include:
- Multi-server support for tracking prices across different game servers
- Enhanced data visualization with historical price charts
- User-configurable alerts for price thresholds
- Improved OCR accuracy through machine learning with TensorFlow
- Alternative data collection methods compliant with game policies
- Community contribution system for price reporting
- API integration for third-party tools and extensions
- Mobile application version with push notifications
