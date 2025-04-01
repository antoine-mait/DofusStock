// extract_url_data.js - URL extraction and item processing
function initUrlExtractor() {
    // Check for stored URL and items in localStorage
    const storedUrl = localStorage.getItem('dofusBuildUrl');
    const storedItems = localStorage.getItem('dofusBuildItems');
    
    // Restore the URL if available
    if (window.buildUrl && storedUrl) {
        window.buildUrl.value = storedUrl;
    }
    
    // Restore the items list if available
    if (window.itemsList && storedItems) {
        try {
            const items = JSON.parse(storedItems);
            displayExtractedItems(items);
        } catch (e) {
            console.error('Error restoring stored items:', e);
        }
    }

    // Set up form submission handler
    if (window.urlForm) {
        window.urlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = window.buildUrl.value.trim();
            if (!url || !url.startsWith('https://d-bk.net/fr/d/')) {
                alert('Please enter a valid Dofus Build URL (https://d-bk.net/fr/d/...)');
                return;
            }
            
            // Store the URL in localStorage
            localStorage.setItem('dofusBuildUrl', url);
            
            // Show loading indicator
            window.loading.classList.remove('d-none');
            window.resultsTitle.classList.add('d-none');
            window.itemsList.innerHTML = '';
            
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
                window.loading.classList.add('d-none');
                
                // Display the results
                displayExtractedItems(items);
                
            } catch (error) {
                console.error('Error:', error);
                window.loading.classList.add('d-none');
                
                const errorMessage = document.createElement('p');
                errorMessage.textContent = 'An error occurred while extracting items. Please try again.';
                errorMessage.classList.add('text-danger');
                window.itemsList.appendChild(errorMessage);
            }
        });
        
        // Add a clear button to reset stored data
        const clearButton = document.createElement('button');
        clearButton.textContent = 'Clear';
        clearButton.classList.add('btn', 'btn-secondary', 'ml-2');
        clearButton.type = 'button';
        clearButton.addEventListener('click', () => {
            localStorage.removeItem('dofusBuildUrl');
            localStorage.removeItem('dofusBuildItems');
            if (window.buildUrl) window.buildUrl.value = '';
            window.resultsTitle.classList.add('d-none');
            window.itemsList.innerHTML = '';
        });
        
        // Append to the button group
        const inputGroup = window.urlForm.querySelector('.input-group-append');
        if (inputGroup) {
            inputGroup.appendChild(clearButton);
        }
    }
}

// Function to display extracted items
async function displayExtractedItems(items) {
    // Show results title
    window.resultsTitle.classList.remove('d-none');
    window.itemsList.innerHTML = '';
    
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
                    const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${window.sanitizeFilename(item.name)}.png`;
                    
                    // Check if item is already in craft list
                    const isInCraftList = document.getElementById(`craft-item-${item.ankama_id}`) !== null;
                    
                    itemElement.innerHTML = `
                        <div class="item-container" style="display: flex; align-items: center;">
                            <img 
                                src="${imagePath}" 
                                alt="${item.name}"
                                onerror="this.src='${window.FALLBACK_IMAGE}'; this.onerror=null;"
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
                
                window.itemsList.appendChild(itemElement);
            } catch (searchError) {
                console.error('Error searching for item:', searchError);
                
                // Display item without image on error
                const itemElement = document.createElement('p');
                itemElement.textContent = itemName;
                itemElement.classList.add('item-entry');
                window.itemsList.appendChild(itemElement);
            }
        }
        
        // Add event listeners to the new buttons
        document.querySelectorAll('.add-to-craftlist-btn').forEach(button => {
            button.addEventListener('click', async function() {
                const itemId = this.getAttribute('data-item-id');
                const itemData = JSON.parse(decodeURIComponent(this.getAttribute('data-item-data')));
                
                const result = await window.toggleCraftlistItem(itemId);
                if (result.status === 'added') {
                    // Update button state
                    this.textContent = "Added to craft list";
                    this.disabled = true;
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    
                    // Update craft list UI
                    window.addItemToCraftListUI(itemData);
                }
            });
        });
    } else {
        const noItems = document.createElement('p');
        noItems.textContent = 'No items found in this build.';
        window.itemsList.appendChild(noItems);
    }
}

// Expose necessary functions to other modules
window.displayExtractedItems = displayExtractedItems;