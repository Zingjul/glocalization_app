// static/js/back_button.js
(function() {
    'use strict';
    
    const STORAGE_KEY = 'siteNavStack';
    const MAX_STACK_SIZE = 20;
    
    // Pages to ignore (action URLs that redirect immediately)
    const IGNORE_PATTERNS = [
        '/upload',
        '/delete/',
        '/caption/',
        '/visibility/',
        '/toggle_business_name',
    ];
    
    // Get navigation stack from sessionStorage
    function getNavStack() {
        try {
            const data = sessionStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.warn('Failed to read nav stack:', e);
            return [];
        }
    }
    
    // Save navigation stack to sessionStorage
    function saveNavStack(stack) {
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stack));
        } catch (e) {
            console.warn('Failed to save nav stack:', e);
        }
    }
    
    // Check if URL should be ignored
    function shouldIgnoreUrl(url) {
        return IGNORE_PATTERNS.some(pattern => url.includes(pattern));
    }
    
    // Add current page to navigation stack
    function trackCurrentPage() {
        const currentPath = window.location.pathname;
        const currentUrl = window.location.href;
        
        // Don't track action pages
        if (shouldIgnoreUrl(currentPath)) {
            return;
        }
        
        const stack = getNavStack();
        
        // Don't add if it's the same as the last page
        if (stack.length > 0 && stack[stack.length - 1] === currentUrl) {
            return;
        }
        
        // Remove current URL if it exists elsewhere in stack (user navigated back then forward)
        const existingIndex = stack.indexOf(currentUrl);
        if (existingIndex !== -1) {
            // Trim stack to that point (user went back in history)
            stack.length = existingIndex + 1;
        } else {
            // Add new page
            stack.push(currentUrl);
        }
        
        // Keep stack size manageable
        while (stack.length > MAX_STACK_SIZE) {
            stack.shift();
        }
        
        saveNavStack(stack);
    }
    
    // Get the previous page URL
    function getPreviousPageUrl(fallbackUrl) {
        const stack = getNavStack();
        const currentUrl = window.location.href;
        
        // Find current page in stack and get the one before it
        for (let i = stack.length - 1; i >= 0; i--) {
            if (stack[i] === currentUrl) {
                // Return the page before this one
                if (i > 0) {
                    return stack[i - 1];
                }
                break;
            }
        }
        
        // If current page not in stack, return last item that isn't current
        for (let i = stack.length - 1; i >= 0; i--) {
            if (stack[i] !== currentUrl) {
                return stack[i];
            }
        }
        
        // Fallback
        return fallbackUrl;
    }
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        // Track current page
        trackCurrentPage();
        
        // Handle back button clicks
        const backLinks = document.querySelectorAll('.js-back-link');
        
        backLinks.forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                
                const fallbackUrl = link.getAttribute('href') || '/';
                const previousUrl = getPreviousPageUrl(fallbackUrl);
                
                // Remove current page from stack before navigating
                const stack = getNavStack();
                const currentUrl = window.location.href;
                const currentIndex = stack.lastIndexOf(currentUrl);
                if (currentIndex !== -1) {
                    stack.splice(currentIndex, 1);
                    saveNavStack(stack);
                }
                
                window.location.href = previousUrl;
            });
        });
    });
    
    // Also track when using browser back/forward buttons
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was loaded from cache (back/forward navigation)
            trackCurrentPage();
        }
    });
})();