document.addEventListener('DOMContentLoaded', () => {
    const categoryButtons = document.querySelectorAll('.category-button');
    const itemTypeContainer = document.getElementById('item-type-container');
    const itemContainer = document.getElementById('item-container');
    const searchInput = document.getElementById('item-search');


    // Default fallback image
    const FALLBACK_IMAGE = '/media/IMG/equipment/Outil/489-Loupe.png';
    
    // Global search function
    async function performGlobalSearch() {
        const searchTerm = searchInput.value.trim();
        
        // Clear previous content
        itemTypeContainer.innerHTML = '';
        itemContainer.innerHTML = '';

        if (searchTerm.length < 2) {
            return; // Minimum 2 characters to search
        }

        try {
            const response = await fetch(`/search-items/?search=${encodeURIComponent(searchTerm)}`);
            const items = await response.json();

            // Display search results
            items.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.classList.add('item-card');
                
                // Attempt to construct image path
                // Note: This might need adjustment based on your actual image storage
                const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${sanitizeFilename(item.name)}.png`;
                
                itemElement.innerHTML = `
                    <h3>${item.name}</h3>
                    <p>Category: ${item.category}</p>
                    <p>Type: ${item.item_type}</p>
                    <p>Level: ${item.level}</p>
                    <img 
                        src="${imagePath}" 
                        alt="${item.name}"
                        onerror="this.src='/media/IMG/equipment/Outil/489-Loupe.png'; this.onerror=null;"
                    >
                `;
                itemContainer.appendChild(itemElement);
            });
        } catch (error) {
            console.error('Error performing global search:', error);
        }
    }

    // Helper function to sanitize filename
    function sanitizeFilename(filename) {
        return filename
            .normalize('NFD')  // Normalize Unicode characters
            .replace(/[\u0300-\u036f]/g, '') // Remove accent marks
            .replace(/[<>:"/\\|?*'°]/g, '')   // Remove invalid characters
            .replace(/\s+/g, '_');           // Replace spaces with underscores
    }

    // Search input event listener
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        // Clear any existing timeout
        clearTimeout(searchTimeout);
        
        // Set a new timeout to prevent too many requests
        searchTimeout = setTimeout(performGlobalSearch, 300);
    });

    // Add click event to category buttons to reset search
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            searchInput.value = ''; // Clear search input
            fetchItemTypes(category);
        });
    });

    // Original function to fetch item types (kept for category navigation)
    async function fetchItemTypes(category) {
        try {
            const response = await fetch(`/get-item-types/?category=${category}`);
            const itemTypes = await response.json();
            
            // Clear previous item types
            itemTypeContainer.innerHTML = '';
            itemContainer.innerHTML = '';
            
            // Create buttons for each item type
            itemTypes.forEach(itemType => {
                const button = document.createElement('button');
                button.textContent = itemType;
                button.classList.add('item-type-button');
                button.addEventListener('click', () => filterItems(category, itemType));
                itemTypeContainer.appendChild(button);
            });
        } catch (error) {
            console.error('Error fetching item types:', error);
        }
    }

    // Original function to filter items by category and type (kept for type navigation)
    async function filterItems(category, itemType) {
        try {
            const response = await fetch(`/get-items/?category=${category}&item_type=${itemType}`);
            const items = await response.json();
            
            // Clear previous items
            itemContainer.innerHTML = '';
            
            // Create item elements
            items.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.classList.add('item-card');
                
                const imagePath = `/media/IMG/${category}/${itemType}/${item.ankama_id}-${sanitizeFilename(item.name)}.png`;
                
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
                        src="${imagePath}" 
                        alt="${item.name}"
                        onerror="this.src='/media/IMG/equipment/Outil/489-Loupe.png'; this.onerror=null;"
                    >
                `;
                itemContainer.appendChild(itemElement);
            });
        } catch (error) {
            console.error('Error fetching items:', error);
        }
    }
});