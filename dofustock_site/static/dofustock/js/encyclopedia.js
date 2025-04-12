// encyclopedia.js - Item search and browsing
function initEncyclopedia() {
    // Get search input element directly when function is called
    window.searchInput = document.getElementById('item-search');
    window.itemTypeContainer = document.getElementById('item-type-container');
    window.itemContainer = document.getElementById('item-container');
    
    // Only add event listener if search input exists
    if (window.searchInput) {
        console.log("Search input found, adding event listener");
        
        // Search input event listener
        let searchTimeout;
        window.searchInput.addEventListener('input', () => {
            // Clear any existing timeout
            clearTimeout(searchTimeout);
            
            // Set a new timeout to prevent too many requests
            searchTimeout = setTimeout(performGlobalSearch, 300);
        });
    } else {
        console.error("Search input element not found");
    }
    
    // Add click event to category buttons
    window.categoryButtons = document.querySelectorAll('.category-button');
    if (window.categoryButtons) {
        window.categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                if (window.searchInput) {
                    window.searchInput.value = ''; // Clear search input
                }
                fetchItemTypes(category);
            });
        });
    }
}

// Global search function
async function performGlobalSearch() {
    const searchInput = document.getElementById('item-search');
    if (!searchInput) {
        console.error("Search input not found");
        return;
    }
    
    const searchTerm = searchInput.value.trim();
    const itemContainer = document.getElementById('item-container');
    const itemTypeContainer = document.getElementById('item-type-container');
    
    // Clear previous content
    if (itemTypeContainer) itemTypeContainer.innerHTML = '';
    if (itemContainer) itemContainer.innerHTML = '';

    if (searchTerm.length < 2) {
        return; // Minimum 2 characters to search
    }

    console.log("Searching for:", searchTerm);

    try {
        const response = await fetch(`/search-items/?search=${encodeURIComponent(searchTerm)}`);
        const items = await response.json();
        
        console.log("Found items:", items.length);

        // Display search results
        items.forEach(item => {
            const itemElement = document.createElement('a');
            itemElement.href = `/item/${item.ankama_id}/`;
            itemElement.classList.add('item-card');
            
            // Attempt to construct image path
            const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${window.sanitizeFilename(item.name)}.png`;
            
            itemElement.innerHTML = `
                <h3>${item.name}</h3>
                <p>Category: ${item.category}</p>
                <p>Type: ${item.item_type}</p>
                <p>Level: ${item.level}</p>
                <p>Price: ${formatPriceDisplay(item.price)}</p>
                <p>Craft Cost: ${formatPriceDisplay(item.craft_cost)}</p>
                <img 
                    src="${imagePath}" 
                    alt="${item.name}"
                    onerror="this.src='${window.FALLBACK_IMAGE || '/media/IMG/equipment/Outil/489-Loupe.png'}'; this.onerror=null;"
                >
            `;
            if (itemContainer) itemContainer.appendChild(itemElement);
        });
    } catch (error) {
        console.error('Error performing global search:', error);
    }
}

// Function to fetch item types
async function fetchItemTypes(category) {
    try {
        const response = await fetch(`/get-item-types/?category=${category}`);
        const itemTypes = await response.json();
        
        // Clear previous item types
        window.itemTypeContainer.innerHTML = '';
        window.itemContainer.innerHTML = '';
        
        // Create buttons for each item type
        itemTypes.forEach(itemType => {
            const button = document.createElement('button');
            button.textContent = itemType;
            button.classList.add('item-type-button');
            button.addEventListener('click', () => filterItems(category, itemType));
            window.itemTypeContainer.appendChild(button);
        });
    } catch (error) {
        console.error('Error fetching item types:', error);
    }
}

// Function to filter items by category and type
async function filterItems(category, itemType) {
    try {
        const response = await fetch(`/get-items/?category=${category}&item_type=${itemType}`);
        const items = await response.json();
        
        // Clear previous items
        window.itemContainer.innerHTML = '';
        
        // Create item elements
        items.forEach(item => {
            const itemElement = document.createElement('a');
            itemElement.href = `/item/${item.ankama_id}/`;
            itemElement.classList.add('item-card');
            
            const imagePath = `/media/IMG/${category}/${itemType}/${item.ankama_id}-${window.sanitizeFilename(item.name)}.png`;
            
            itemElement.innerHTML = `
                <h3>${item.name}</h3>
                <p>Level: ${item.level}</p>
                <p>Price: ${formatPriceDisplay(item.price)}</p>
                <p>Craft Price: ${formatPriceDisplay(item.craft_cost)}</p>
                <img 
                    src="${imagePath}" 
                    alt="${item.name}"
                    onerror="this.src='${window.FALLBACK_IMAGE}'; this.onerror=null;"
                >
            `;
            window.itemContainer.appendChild(itemElement);
        });
    } catch (error) {
        console.error('Error fetching items:', error);
    }
}

// Helper function to format price values for display
function formatPriceDisplay(price) {
    // Special case handling
    if (price === 0 || price === "0") return 'No Item in HDV';
    if (!price || price === "N/A") return 'No data';
    if (price === "Incomplete") return 'Incomplete';
    
    // If already a string and not a valid number, return as is
    if (typeof price === 'string') {
        // Check if it's already properly formatted (contains spaces)
        if (price.includes(' ')) return price;
        
        // Check if it's a numeric string without formatting
        if (!isNaN(price.replace(/[\s,]/g, ''))) {
            // Parse the string as a number, removing any existing formatting
            const numValue = parseInt(price.replace(/[\s,]/g, ''), 10);
            if (!isNaN(numValue)) {
                // Format with spaces as thousand separators
                return numValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
            }
        }
        
        // If we can't parse it as a number, return the original string
        return price;
    }
    
    // If it's a number, format it with spaces
    if (typeof price === 'number') {
        return Math.floor(price).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
    
    // Default fallback
    return String(price);
}

// Expose necessary functions to other modules
window.performGlobalSearch = performGlobalSearch;
window.fetchItemTypes = fetchItemTypes;
window.filterItems = filterItems;