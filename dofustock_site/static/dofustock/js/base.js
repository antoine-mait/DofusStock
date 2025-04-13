// base.js - Core initialization and shared utilities
document.addEventListener('DOMContentLoaded', () => {
    // Initialize global DOM elements
    window.categoryButtons = document.querySelectorAll('.category-button');
    window.itemTypeContainer = document.getElementById('item-type-container');
    window.itemContainer = document.getElementById('item-container');
    window.searchInput = document.getElementById('item-search');
    window.urlForm = document.getElementById('url-form');
    window.buildUrl = document.getElementById('build-url');
    window.loading = document.getElementById('loading');
    window.results = document.getElementById('results');
    window.resultsTitle = document.getElementById('results-title');
    window.itemsList = document.getElementById('items-list');
    window.craftListContainer = document.querySelector('.craft-list-container');
    
    // Default fallback image
    window.FALLBACK_IMAGE = '/media/IMG/equipment/Outil/489-Loupe.png';
    
    // Initialize modules
    initEncyclopedia();
    initCraftList();
    initUrlExtractor();
});

// Theme switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeSelect = document.getElementById('theme-select');
    
    // Check for saved theme preference or use default
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeSelect.value = savedTheme;
    
    // Add event listener for theme change
    themeSelect.addEventListener('change', function() {
      const selectedTheme = this.value;
      document.documentElement.setAttribute('data-theme', selectedTheme);
      localStorage.setItem('theme', selectedTheme);
    });
  });
  
// Helper function to sanitize filename
window.sanitizeFilename = function(filename) {
    return filename
        .normalize('NFD')  // Normalize Unicode characters
        .replace(/[\u0300-\u036f]/g, '') // Remove accent marks
        .replace(/[<>:"/\\|?*'°œ]/g, '')   // Remove invalid characters
        .replace(/\s+/g, '_');           // Replace spaces with underscores
};