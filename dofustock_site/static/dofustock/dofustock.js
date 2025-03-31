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
    const craftListContainer = document.querySelector('.craft-list-container');

    // Default fallback image
    const FALLBACK_IMAGE = '/media/IMG/equipment/Outil/489-Loupe.png';
    
    // Check for stored URL and items in localStorage
    const storedUrl = localStorage.getItem('dofusBuildUrl');
    const storedItems = localStorage.getItem('dofusBuildItems');
    
    // Restore the URL if available
    if (buildUrl && storedUrl) {
        buildUrl.value = storedUrl;
    }
    
    // Restore the items list if available
    if (itemsList && storedItems) {
        try {
            const items = JSON.parse(storedItems);
            displayExtractedItems(items);
        } catch (e) {
            console.error('Error restoring stored items:', e);
        }
    }
    
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

    // Function to create a craft list item card
    function createCraftListItemCard(item) {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'col-md-4 mb-3';
        cardDiv.id = `craft-item-${item.ankama_id}`;
        
        const sanitizedName = sanitizeFilename(item.name);
        const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${sanitizedName}.png`;
        
        cardDiv.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${item.name}</h5>
                    <img src="${imagePath}" 
                        alt="${item.name}"
                        onerror="this.src='/media/IMG/equipment/Outil/489-Loupe.png'; this.onerror=null;">
                    <p class="card-text">Level: ${item.level}</p>
                    <p class="card-text">Category: ${item.category}</p>
                    <a href="/item/${item.ankama_id}/" class="btn btn-primary btn-sm">View Details</a>
                    <button type="button" class="btn btn-danger btn-sm remove-from-craft-list" data-item-id="${item.ankama_id}">Remove</button>
                </div>
            </div>
        `;
        
        return cardDiv;
    }

    // Function to add item to craft list UI
    async function addItemToCraftListUI(item) {
        // Check if craftListContainer exists
        if (!craftListContainer) return;
        
        // Check if we already have a row for cards
        let rowDiv = craftListContainer.querySelector('.row');
        if (!rowDiv) {
            // Create a header first if empty
            if (craftListContainer.querySelector('.alert-info')) {
                craftListContainer.innerHTML = '<h3>Your Craft List</h3>';
            }
            
            rowDiv = document.createElement('div');
            rowDiv.className = 'row';
            craftListContainer.appendChild(rowDiv);
        }
        
        // Create and add the card
        const cardDiv = createCraftListItemCard(item);
        rowDiv.appendChild(cardDiv);
        
        // Add event listener to the remove button
        const removeBtn = cardDiv.querySelector('.remove-from-craft-list');
        if (removeBtn) {
            removeBtn.addEventListener('click', async function() {
                const itemId = this.getAttribute('data-item-id');
                await toggleCraftlistItem(itemId, true);
            });
        }
    }

    // Function to display extracted items
    async function displayExtractedItems(items) {
        // Show results title
        resultsTitle.classList.remove('d-none');
        itemsList.innerHTML = '';
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (items.length > 0) {
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
                        
                        // Check if item is already in craft list
                        const isInCraftList = document.getElementById(`craft-item-${item.ankama_id}`) !== null;
                        
                        itemElement.innerHTML = `
                            <div class="item-container" style="display: flex; align-items: center;">
                                <img 
                                    src="${imagePath}" 
                                    alt="${item.name}"
                                    onerror="this.src='${FALLBACK_IMAGE}'; this.onerror=null;"
                                    style="width: 40px; height: 40px; margin-right: 10px;"
                                >
                                <a href="/item/${item.ankama_id}/" class="item-link">${itemName}</a>
                                <button 
                                    type="button" 
                                    class="add-to-craftlist-btn btn ${isInCraftList ? 'btn-success' : 'btn-primary'}" 
                                    data-item-id="${item.ankama_id}" 
                                    data-item-data="${encodeURIComponent(JSON.stringify(item))}"
                                    data-csrf="${csrfToken}"
                                    style="margin-left: 10px;"
                                    ${isInCraftList ? 'disabled' : ''}
                                >
                                    ${isInCraftList ? 'Added to craft list' : 'Add to craft list'}
                                </button>
                            </div>
                        `;
                    } else {
                        itemElement.textContent = itemName + " (Not found in database)";
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
            
            // Add event listeners to the new buttons
            document.querySelectorAll('.add-to-craftlist-btn').forEach(button => {
                button.addEventListener('click', async function() {
                    const itemId = this.getAttribute('data-item-id');
                    const itemData = JSON.parse(decodeURIComponent(this.getAttribute('data-item-data')));
                    
                    const result = await toggleCraftlistItem(itemId);
                    if (result.status === 'added') {
                        // Update button state
                        this.textContent = "Added to craft list";
                        this.disabled = true;
                        this.classList.remove('btn-primary');
                        this.classList.add('btn-success');
                        
                        // Update craft list UI
                        addItemToCraftListUI(itemData);
                    }
                });
            });
        } else {
            const noItems = document.createElement('p');
            noItems.textContent = 'No items found in this build.';
            itemsList.appendChild(noItems);
        }
    }

    // Function to toggle craftlist item via AJAX
    async function toggleCraftlistItem(itemId, isRemove = false) {
        try {
            // Get the CSRF token from the page
            // Make sure to look for it in META tag if it's not in a form
            let csrfToken = '';
            const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (tokenInput) {
                csrfToken = tokenInput.value;
            } else {
                // Try to get it from the meta tag
                const metaToken = document.querySelector('meta[name="csrf-token"]');
                if (metaToken) {
                    csrfToken = metaToken.getAttribute('content');
                }
            }
            
            if (!csrfToken) {
                console.error('CSRF token not found. Cannot proceed with AJAX request.');
                return { status: 'error', message: 'CSRF token not found' };
            }
            
            // Send AJAX request to toggle craftlist
            const response = await fetch(`/toggle-craftlist/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Toggle result:', result);
                
                // If removing from craft list
                if (isRemove && result.status === 'removed') {
                    const itemCard = document.getElementById(`craft-item-${itemId}`);
                    if (itemCard) {
                        itemCard.remove();
                        
                        // Update any matching add buttons
                        const addBtn = document.querySelector(`.add-to-craftlist-btn[data-item-id="${itemId}"]`);
                        if (addBtn) {
                            addBtn.textContent = "Add to craft list";
                            addBtn.disabled = false;
                            addBtn.classList.remove('btn-success');
                            addBtn.classList.add('btn-primary');
                        }
                        
                        // If craft list is now empty, show empty message
                        const craftListRow = document.querySelector('.craft-list-container .row');
                        if (craftListRow && craftListRow.children.length === 0) {
                            craftListContainer.innerHTML = `
                                <div class="alert alert-info">
                                    Your craft list is currently empty. Add items from the item detail pages.
                                </div>
                            `;
                        }
                    }
                }
                
                return result;
            } else {
                console.error('Server responded with an error:', response.status);
                return { status: 'error', message: `Server responded with ${response.status}` };
            }
            
        } catch (error) {
            console.error('Error toggling craftlist:', error);
            return { status: 'error', message: error.toString() };
        }
    }

    // Set up event listeners for ALL remove buttons in craft list at load time
    if (craftListContainer) {
        // Find all existing remove buttons and attach event listeners
        document.querySelectorAll('.remove-from-craft-list').forEach(button => {
            button.addEventListener('click', async function() {
                const itemId = this.getAttribute('data-item-id');
                console.log('Remove button clicked for item:', itemId);
                await toggleCraftlistItem(itemId, true);
            });
        });
        
        // Also set up event delegation for dynamically added buttons
        craftListContainer.addEventListener('click', async event => {
            if (event.target.classList.contains('remove-from-craft-list')) {
                const itemId = event.target.getAttribute('data-item-id');
                console.log('Remove button clicked through delegation for item:', itemId);
                await toggleCraftlistItem(itemId, true);
            }
        });
    }

    if (urlForm) {
        urlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = buildUrl.value.trim();
            if (!url || !url.startsWith('https://d-bk.net/fr/d/')) {
                alert('Please enter a valid Dofus Build URL (https://d-bk.net/fr/d/...)');
                return;
            }
            
            // Store the URL in localStorage
            localStorage.setItem('dofusBuildUrl', url);
            
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
                
                // Store the items in localStorage
                localStorage.setItem('dofusBuildItems', JSON.stringify(items));
                
                // Hide loading indicator
                loading.classList.add('d-none');
                
                // Display the results
                displayExtractedItems(items);
                
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
    
    // Add a clear button to reset stored data
    if (urlForm) {
        const clearButton = document.createElement('button');
        clearButton.textContent = 'Clear';
        clearButton.classList.add('btn', 'btn-secondary', 'ml-2');
        clearButton.type = 'button';
        clearButton.addEventListener('click', () => {
            localStorage.removeItem('dofusBuildUrl');
            localStorage.removeItem('dofusBuildItems');
            if (buildUrl) buildUrl.value = '';
            resultsTitle.classList.add('d-none');
            itemsList.innerHTML = '';
        });
        
        // Append to the button group
        const inputGroup = urlForm.querySelector('.input-group-append');
        if (inputGroup) {
            inputGroup.appendChild(clearButton);
        }
    }
});