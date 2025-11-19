/* ================================================
   Live Search Feature - search-engine.js
   Real-time search with debouncing
   ================================================ */

class SearchEngine {
  constructor() {
    this.searchInput = document.querySelector('.feed-search input');
    this.searchResults = document.querySelector('.feed-content');
    this.searchTimeout = null;
    this.cache = new Map(); // Cache results for performance
    
    this.init();
  }

  init() {
    if (!this.searchInput) return;

    // Advanced input handling with debouncing
    this.searchInput.addEventListener('input', (e) => {
      clearTimeout(this.searchTimeout);
      const query = e.target.value.trim();
      
      // Show loading state
      this.showLoadingState();
      
      // Debounce search (wait 300ms after user stops typing)
      this.searchTimeout = setTimeout(() => {
        this.performSearch(query);
      }, 300);
    });

    // Add search suggestions
    this.initSearchSuggestions();
  }

  async performSearch(query) {
    // Check cache first
    if (this.cache.has(query)) {
      this.displayResults(this.cache.get(query));
      return;
    }

    try {
      // Professional error handling
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      
      // Cache the results
      this.cache.set(query, data);
      
      // Display with animation
      this.displayResults(data);
      
    } catch (error) {
      console.error('Search error:', error);
      this.showErrorState();
    }
  }

  displayResults(data) {
    // Smooth transition between results
    this.searchResults.style.opacity = '0';
    
    setTimeout(() => {
      this.searchResults.innerHTML = this.renderResults(data);
      this.searchResults.style.opacity = '1';
    }, 200);
  }
}