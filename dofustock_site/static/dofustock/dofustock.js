document.addEventListener('DOMContentLoaded', () => {
    const categoryButtons = document.querySelectorAll('.category-button');
    const itemTypeContainer = document.getElementById('item-type-container');
    const itemContainer = document.getElementById('item-container');
    const searchInput = document.getElementById('item-search');
    const urlForm = document.getElementById('url-form');
    const buildUrl = document.getElementById('build-url');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsTitle = document.getElementById('results-title');
    const itemsList = document.getElementById('items-list');

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
                const itemElement = document.createElement('a');
                itemElement.href = `/item/${item.ankama_id}/`;
                itemElement.classList.add('item-card');
                
                // Attempt to construct image path
                // Note: This might need adjustment based on your actual image storage
                const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${sanitizeFilename(item.name)}.png`;
                
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
            .replace(/[<>:"/\\|?*'°œ]/g, '')   // Remove invalid characters
            .replace(/\s+/g, '_');           // Replace spaces with underscores
    }

    // Search input event listener
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            // Clear any existing timeout
            clearTimeout(searchTimeout);
        
        // Set a new timeout to prevent too many requests
        searchTimeout = setTimeout(performGlobalSearch, 300);
       });
    }
    // Add click event to category buttons to reset search
    if (categoryButtons) {
        categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            searchInput.value = ''; // Clear search input
            fetchItemTypes(category);
            });
        });
    }

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
                const itemElement = document.createElement('a');
                itemElement.href = `/item/${item.ankama_id}/`;
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
                        src="${imagePath} " 
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

    if (urlForm) {
        urlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = buildUrl.value.trim();
            if (!url || !url.startsWith('https://d-bk.net/fr/d/')) {
                alert('Please enter a valid Dofus Build URL (https://d-bk.net/fr/d/...)');
                return;
            }
            
            // Show loading indicator
            loading.classList.remove('d-none');
            resultsTitle.classList.add('d-none');
            itemsList.innerHTML = '';
            
            try {
                // Call your Django view to scrape the URL
                const response = await fetch(`/scrape-build/?url=${encodeURIComponent(url)}`);
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const items = await response.json();
                
                // Hide loading indicator
                loading.classList.add('d-none');
                
                // Display the results
                if (items.length > 0) {
                    resultsTitle.classList.remove('d-none');
                    
                    // Process each item to search for it in the database and get its image
                    for (const itemName of items) {
                        try {
                            // Search for the item by name
                            const searchResponse = await fetch(`/search-items/?search=${encodeURIComponent(itemName)}`);
                            const searchResults = await searchResponse.json();
                            
                            const itemElement = document.createElement('div');
                            itemElement.classList.add('item-entry', 'd-flex', 'align-items-center', 'mb-2');
                            
                            // If we found a matching item, display its image
                            if (searchResults.length > 0) {
                                const item = searchResults[0]; // Use the first matching item
                                const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${sanitizeFilename(item.name)}.png`;
                                
                                itemElement.innerHTML = `
                                    <img 
                                        src="${imagePath}" 
                                        alt="${item.name}"
                                        onerror="this.src='${FALLBACK_IMAGE}'; this.onerror=null;"
                                        style="width: 40px; height: 40px; margin-right: 10px;"
                                    >
                                    <a href="/item/${item.ankama_id}/" class="item-link">${itemName}</a>
                                `;
                            } else {
                                // No matching item found, just display the name with fallback image
                                itemElement.innerHTML = `
                                    <img 
                                        src="${FALLBACK_IMAGE}" 
                                        alt="${itemName}"
                                        style="width: 40px; height: 40px; margin-right: 10px;"
                                    >
                                    <span>${itemName}</span>
                                `;
                            }
                            
                            itemsList.appendChild(itemElement);
                        } catch (searchError) {
                            console.error('Error searching for item:', searchError);
                            
                            // Display item without image on error
                            const itemElement = document.createElement('p');
                            itemElement.textContent = itemName;
                            itemElement.classList.add('item-entry');
                            itemsList.appendChild(itemElement);
                        }
                    }
                } else {
                    resultsTitle.classList.remove('d-none');
                    const noItems = document.createElement('p');
                    noItems.textContent = 'No items found in this build.';
                    itemsList.appendChild(noItems);
                }
                
            } catch (error) {
                console.error('Error:', error);
                loading.classList.add('d-none');
                
                const errorMessage = document.createElement('p');
                errorMessage.textContent = 'An error occurred while extracting items. Please try again.';
                errorMessage.classList.add('text-danger');
                itemsList.appendChild(errorMessage);
            }
        });
    }
});
