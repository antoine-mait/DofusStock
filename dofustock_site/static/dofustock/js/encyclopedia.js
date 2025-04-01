// encyclopedia.js - Item search and browsing
function initEncyclopedia() {
    // Search input event listener
    let searchTimeout;
    if (window.searchInput) {
        window.searchInput.addEventListener('input', () => {
            // Clear any existing timeout
            clearTimeout(searchTimeout);
        
            // Set a new timeout to prevent too many requests
            searchTimeout = setTimeout(performGlobalSearch, 300);
        });
    }
    
    // Add click event to category buttons to reset search
    if (window.categoryButtons) {
        window.categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                window.searchInput.value = ''; // Clear search input
                fetchItemTypes(category);
            });
        });
    }
}

// Global search function
async function performGlobalSearch() {
    const searchTerm = window.searchInput.value.trim();
    
    // Clear previous content
    window.itemTypeContainer.innerHTML = '';
    window.itemContainer.innerHTML = '';

    if (searchTerm.length < 2) {
        return; // Minimum 2 characters to search
    }

    try {
        const response = await fetch(`/search-items/?search=${encodeURIComponent(searchTerm)}`);
        const items = await response.json();

        // Display search results
        items.forEach(item => {
            const itemElement = document.createElement('a');
            itemElement.href = `/item/${item.ankama_id}/`;
            itemElement.classList.add('item-card');
            
            // Attempt to construct image path
            const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${window.sanitizeFilename(item.name)}.png`;
            
            // Conditional rendering of craft information
            const priceSection = item.category !== 'resources' 
                ? `<p>Price: ${item.price || 'N/A'}</p>
                <p>Craft: ${item.craft_price || 'N/A'}</p>` 
                : `<p>Price: ${item.price || 'N/A'}</p>`;
        
            itemElement.innerHTML = `
                <h3>${item.name}</h3>
                <p>Category: ${item.category}</p>
                <p>Type: ${item.item_type}</p>
                <p>Level: ${item.level}</p>
                ${priceSection}
                <img 
                    src="${imagePath}" 
                    alt="${item.name}"
                    onerror="this.src='${window.FALLBACK_IMAGE}'; this.onerror=null;"
                >
            `;
            window.itemContainer.appendChild(itemElement);
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
            
            // Conditional rendering of craft information
            const priceSection = category !== 'resources' 
                ? `<p>Price: ${item.price || 'N/A'}</p>
                <p>Craft: ${item.craft_price || 'N/A'}</p>` 
                : `<p>Price: ${item.price || 'N/A'}</p>`;
            
            itemElement.innerHTML = `
                <h3>${item.name}</h3>
                <p>Level: ${item.level}</p>
                ${priceSection}
                <img 
                    src="${imagePath} " 
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

// Expose necessary functions to other modules
window.performGlobalSearch = performGlobalSearch;
window.fetchItemTypes = fetchItemTypes;
window.filterItems = filterItems;