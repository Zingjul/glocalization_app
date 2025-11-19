/* ================================================
   Text Length Handler - Conditional Overflow/Marquee
   Checks actual text length and applies effects accordingly
   ================================================ */

window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class TextLengthHandler {
    constructor() {
      // Configuration for different elements
      this.config = {
        // Element selector: max characters before overflow handling
        '.sidebar-user-details h5': 15,    // Business name
        '.sidebar-user-details p': 20,      // Email
        '.feed-card-name': 12,              // Author name
        '.feed-card-time': 15,              // Time text
        '.feed-card-title': 50,             // Post title
        '.feed-card-text': 17,             // Post description
        '.widget-item span:first-child': 18 // Widget labels
      };
      
      this.init();
    }

    init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
            this.forceSingleLine(); // Add this line
            this.processAllElements();
            });
        } else {
            this.forceSingleLine(); // Add this line
            this.processAllElements();
        }

        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.updateBasedOnWidth();
            this.forceSingleLine();
        }, 250));

        // Watch for dynamic content
        this.observeNewContent();
    }

    // Add this method to force single-line on all target elements
    forceSingleLine() {
        const selectors = Object.keys(this.config);
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                element.style.whiteSpace = 'nowrap';
                element.style.overflow = 'hidden';
                element.style.textOverflow = 'ellipsis';
                element.style.display = 'block';
                element.style.maxWidth = '100%';
            });
        });
    }
    processAllElements() {
      // Check each configured element
      Object.entries(this.config).forEach(([selector, maxLength]) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          this.checkAndHandleText(element, maxLength);
        });
      });
    }

    checkAndHandleText(element, baseMaxLength) {
      // Skip if already processed
      if (element.dataset.textHandled === 'true') return;

      // Get current window width
      const width = window.innerWidth;
      
      // Adjust max length based on screen width
      let maxLength = this.getAdjustedMaxLength(baseMaxLength, width);
      
      // Get the actual text
      const originalText = element.textContent.trim();
      
      // Store original text for later use
      element.dataset.originalText = originalText;
      
      // Check if text exceeds limit
      if (originalText.length > maxLength) {
        // Determine which method to use
        if (this.shouldUseMarquee(element)) {
          this.applyMarquee(element, originalText, maxLength);
        } else {
          this.applyEllipsis(element, originalText, maxLength);
        }
      }
      
      // Mark as handled
      element.dataset.textHandled = 'true';
    }

    getAdjustedMaxLength(baseLength, width) {
      // Adjust character limit based on screen width
      if (width <= 400) {
        return Math.floor(baseLength * 0.6);  // 60% for very small screens
      } else if (width <= 576) {
        return Math.floor(baseLength * 0.7);  // 70% for phones
      } else if (width <= 770) {
        return Math.floor(baseLength * 0.85); // 85% for problem range
      } else {
        return baseLength;                     // Full length for desktop
      }
    }

    shouldUseMarquee(element) {
      // Decide which elements get marquee vs ellipsis
      const marqueeElements = [
        '.feed-card-name',
        '.sidebar-user-details h5'
      ];
      
      return marqueeElements.some(selector => element.matches(selector));
    }

    applyEllipsis(element, text, maxLength) {
      // Simple ellipsis
      const truncated = text.substring(0, maxLength - 3) + '...';
      element.textContent = truncated;
      element.title = text; // Show full text on hover
      element.style.cssText = `
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: block;
        max-width: 100%;
      `;
    }

    applyMarquee(element, text, maxLength) {
      // Create marquee structure
      const truncated = text.substring(0, maxLength - 3) + '...';
      
      element.innerHTML = `
        <span class="text-marquee-container">
          <span class="text-visible">${truncated}</span>
          <span class="text-full">${text}</span>
        </span>
      `;
      
      element.classList.add('marquee-enabled');
      
      // Add CSS for marquee
      this.injectMarqueeStyles();
      
      // Add hover listener
      element.addEventListener('mouseenter', () => {
        element.classList.add('marquee-active');
      });
      
      element.addEventListener('mouseleave', () => {
        element.classList.remove('marquee-active');
      });
    }

    updateBasedOnWidth() {
      // Re-process all elements when window resizes
      const elements = document.querySelectorAll('[data-text-handled="true"]');
      
      elements.forEach(element => {
        const originalText = element.dataset.originalText;
        if (originalText) {
          // Reset element
          element.textContent = originalText;
          element.dataset.textHandled = 'false';
          element.classList.remove('marquee-enabled', 'marquee-active');
          
          // Find the appropriate max length from config
          const selector = Object.keys(this.config).find(sel => element.matches(sel));
          if (selector) {
            const baseMaxLength = this.config[selector];
            this.checkAndHandleText(element, baseMaxLength);
          }
        }
      });
    }

    injectMarqueeStyles() {
      // Only inject once
      if (document.getElementById('text-marquee-styles')) return;
      
      const style = document.createElement('style');
      style.id = 'text-marquee-styles';
      style.innerHTML = `
        .marquee-enabled {
          cursor: pointer;
          position: relative;
          overflow: hidden;
        }
        
        .text-marquee-container {
          display: inline-block;
          position: relative;
          width: 100%;
        }
        
        .text-visible {
          display: inline-block;
        }
        
        .text-full {
          position: absolute;
          left: 0;
          top: 0;
          white-space: nowrap;
          opacity: 0;
          transition: opacity 0.3s ease;
        }
        
        .marquee-active .text-visible {
          opacity: 0;
        }
        
        .marquee-active .text-full {
          opacity: 1;
          animation: marquee-scroll 5s linear infinite;
        }
        
        @keyframes marquee-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        
        /* Specific width adjustments */
        @media (min-width: 560px) and (max-width: 770px) {
          .feed-card-name {
            max-width: 120px !important;
          }
          
          .feed-card-title {
            max-width: 100% !important;
          }
        }
      `;
      
      document.head.appendChild(style);
    }

    observeNewContent() {
      // Watch for dynamically added content
      const observer = new MutationObserver(this.debounce(() => {
        this.processAllElements();
      }, 500));

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }

    // Public method to manually check an element
    checkElement(element, maxLength = 20) {
      element.dataset.textHandled = 'false';
      this.checkAndHandleText(element, maxLength);
    }
  }

  // Initialize
  PE.TextLengthHandler = TextLengthHandler;
  PE.textLength = new TextLengthHandler();

  // Expose global function for manual use
  window.checkTextLength = (element, maxLength) => PE.textLength.checkElement(element, maxLength);

})(window.PlatformEnhanced);