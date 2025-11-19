/* ================================================
   Responsive Handler - Works with existing layout
   ================================================ */

window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class ResponsiveHandler {
    constructor() {
      this.breakpoints = {
        mobile: 576,
        tablet: 768,
        desktop: 1024,
        wide: 1440
      };
      
      this.currentBreakpoint = this.getBreakpoint();
      this.init();
    }

    init() {
      // Smart resize handling
      let resizeTimer;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => this.handleResize(), 250);
      });

      // Initial setup
      this.applyBreakpointClass();
      this.handleSpecialRange();
    }

    getBreakpoint() {
      const width = window.innerWidth;
      
      if (width < this.breakpoints.mobile) return 'mobile';
      if (width < this.breakpoints.tablet) return 'tablet';
      if (width < this.breakpoints.desktop) return 'desktop';
      return 'wide';
    }

    handleResize() {
      const newBreakpoint = this.getBreakpoint();
      
      if (newBreakpoint !== this.currentBreakpoint) {
        this.currentBreakpoint = newBreakpoint;
        this.applyBreakpointClass();
        
        // Emit custom event for other components
        window.dispatchEvent(new CustomEvent('breakpointChange', {
          detail: { 
            breakpoint: newBreakpoint,
            width: window.innerWidth
          }
        }));
      }
      
      this.handleSpecialRange();
    }

    applyBreakpointClass() {
      const body = document.body;
      
      // Remove all breakpoint classes
      body.classList.remove('is-mobile', 'is-tablet', 'is-desktop', 'is-wide');
      
      // Add current breakpoint class
      body.classList.add(`is-${this.currentBreakpoint}`);
    }

    handleSpecialRange() {
      // Fix for 560-770px range
      const width = window.innerWidth;
      const feedCards = document.querySelectorAll('.feed-card');
      const platformFeed = document.querySelector('.platform-feed');
      
      if (width >= 560 && width <= 770) {
        // Add special class for this range
        document.body.classList.add('is-tablet-special');
        
        // Ensure text doesn't overflow
        feedCards.forEach(card => {
          const textElements = card.querySelectorAll('.feed-card-title, .feed-card-text');
          textElements.forEach(el => {
            el.style.wordBreak = 'break-word';
            el.style.overflowWrap = 'break-word';
          });
        });
        
        // Ensure feed takes full width
        if (platformFeed) {
          platformFeed.style.maxWidth = '100%';
          platformFeed.style.width = '100%';
        }
      } else {
        document.body.classList.remove('is-tablet-special');
      }
    }
  }

  // Initialize
  PE.ResponsiveHandler = ResponsiveHandler;
  PE.responsive = new ResponsiveHandler();

})(window.PlatformEnhanced);