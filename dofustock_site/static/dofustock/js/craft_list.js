// craft_list.js - Craft list management functionality
// Update initCraftList function
function initCraftList() {
    // Set container reference to the new structure
    window.craftListContainer = document.querySelector('.item-detail-container');
    
    if (window.craftListContainer) {
        // Find all existing remove buttons and attach event listeners
        document.querySelectorAll('.remove-from-craft-list').forEach(button => {
            button.addEventListener('click', async function() {
                const itemId = this.getAttribute('data-item-id');
                console.log('Remove button clicked for item:', itemId);
                await toggleCraftlistItem(itemId, true);
            });
        });
        
        // Event delegation for the new structure
        window.craftListContainer.addEventListener('click', async event => {
            // Using closest to handle clicks on the button or its child image
            const button = event.target.closest('.remove-from-craft-list');
            if (button) {
                const itemId = button.getAttribute('data-item-id');
                console.log('Remove button clicked through delegation for item:', itemId);
                await toggleCraftlistItem(itemId, true);
            }
        });
    }
}

// Update the function to match the new card structure
function createCraftListItemCard(item) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'row mb-3';
    cardDiv.id = `craft-item-${item.ankama_id}`;
    
    const sanitizedName = window.sanitizeFilename(item.name);
    const imagePath = `/media/IMG/${item.category}/${item.item_type}/${item.ankama_id}-${sanitizedName}.png`;
    
    // Match the new structure
    cardDiv.innerHTML = `
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="item-image mr-3">
                            <img src="${imagePath}" 
                                alt="${item.name}" class="item_img"
                                onerror="this.src='/media/IMG/equipment/Outil/489-Loupe.png'; this.onerror=null;">
                        </div>
                        <h5 class="card-title mb-0 flex-grow-1">
                            <a href="/item/${item.ankama_id}/" class="item-link"> ${itemName}</a>
                        </h5>
                        <div class="button-actions d-flex">
                            <button type="button" 
                                    class="btn btn-sm remove-from-craft-list" 
                                    data-item-id="${item.ankama_id}">
                                <img class="trash icon-small" src="/media/Icon/trash.png" alt="delete">
                            </button>
                            
                        </div>
                    </div>
                    
                    <div class="item-metadata mb-3">
                        <div class="row">
                            <div class="col-md-4">
                                <p class="card-text"><span>${item.item_type} - Level:</span> ${item.level}</p>
                            </div>
                            <div class="col-md-4">
                                <p class="card-text"><strong>Price:</strong> ${item.price}</p>
                            </div>
                            <div class="col-md-4">
                                <p class="card-text"><strong>Craft Cost:</strong> ${item.craft_cost}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return cardDiv;
}

// Function to add item to craft list UI
async function addItemToCraftListUI(item) {
    // Check if craftListContainer exists
    if (!window.craftListContainer) return;
    
    // Check if we already have a row for cards
    let rowDiv = window.craftListContainer.querySelector('.row');
    if (!rowDiv) {
        // Create a header first if empty
        if (window.craftListContainer.querySelector('.alert-info')) {
            window.craftListContainer.innerHTML = '<h3>Your Craft List</h3>';
        }
        
        rowDiv = document.createElement('div');
        rowDiv.className = 'row';
        window.craftListContainer.appendChild(rowDiv);
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
    window.location.href = window.location.href;
}

// Function to toggle craftlist item via AJAX
async function toggleCraftlistItem(itemId, isRemove = false) {
    try {
        // Get the CSRF token from the page
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
                    window.location.href = window.location.href;
                    // If craft list is now empty, show empty message
                    const craftListRow = document.querySelector('.craft-list-container .row');
                    if (craftListRow && craftListRow.children.length === 0) {
                        window.craftListContainer.innerHTML = `
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

// Expose necessary functions to other modules
window.createCraftListItemCard = createCraftListItemCard;
window.addItemToCraftListUI = addItemToCraftListUI;
window.toggleCraftlistItem = toggleCraftlistItem;