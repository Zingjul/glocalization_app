/* ================================================
   Smart Overflow Handler
   Detects actual overflow and applies solutions
   ================================================ */

window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class SmartOverflowHandler {
    constructor() {
      this.config = {
        checkInterval: 500,      // How often to check for overflow (ms)
        marqueeSpeed: 30,        // Pixels per second for marquee
        marqueeDelay: 2000,      // Delay before marquee starts (ms)
        marqueePause: 3000       // Pause between marquee loops (ms)
      };
      
      this.init();
    }

    init() {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.startMonitoring());
      } else {
        this.startMonitoring();
      }

      // Re-check on window resize
      window.addEventListener('resize', this.debounce(() => {
        this.checkAllElements();
      }, 250));
    }

    startMonitoring() {
      // Initial check
      this.checkAllElements();
      
      // Monitor for dynamic content changes
      this.observeChanges();
    }

    checkAllElements() {
      // Find all elements that might overflow
      const elementsToCheck = document.querySelectorAll(`
        .feed-card-name,
        .feed-card-title,
        .feed-card-text,
        .feed-card-time,
        .sidebar-user-details h5,
        .sidebar-user-details p,
        .widget-item span,
        [data-overflow-check]
      `);

      elementsToCheck.forEach(element => {
        this.checkAndHandleOverflow(element);
      });
    }

    checkAndHandleOverflow(element) {
      // Skip if already processed
      if (element.dataset.overflowProcessed === 'true') return;

      // Get actual dimensions
      const isOverflowing = this.isElementOverflowing(element);
      
      if (isOverflowing) {
        // Check if marquee is requested
        const shouldMarquee = element.hasAttribute('data-marquee') || 
                            element.classList.contains('marquee-on-overflow');
        
        if (shouldMarquee) {
          this.applyMarquee(element);
        } else {
          this.applyEllipsis(element);
        }
      } else {
        // Remove any overflow handling if not needed
        this.removeOverflowHandling(element);
      }

      // Mark as processed
      element.dataset.overflowProcessed = 'true';
    }

    isElementOverflowing(element) {
      // Store original styles
      const originalStyles = {
        overflow: element.style.overflow,
        whiteSpace: element.style.whiteSpace,
        textOverflow: element.style.textOverflow
      };

      // Temporarily set styles to check real dimensions
      element.style.overflow = 'visible';
      element.style.whiteSpace = 'nowrap';
      element.style.textOverflow = 'initial';

      // Check if content is wider than container
      const isOverflowing = element.scrollWidth > element.clientWidth || 
                          element.scrollHeight > element.clientHeight;

      // Restore original styles
      Object.assign(element.style, originalStyles);

      return isOverflowing;
    }

    applyEllipsis(element) {
      // Simple CSS ellipsis
      element.classList.add('text-overflow-ellipsis');
      element.setAttribute('title', element.textContent); // Show full text on hover
    }

    applyMarquee(element) {
      // Don't re-apply if already has marquee
      if (element.classList.contains('marquee-active')) return;

      const text = element.textContent;
      const wrapper = document.createElement('div');
      wrapper.className = 'marquee-wrapper';
      
      const content = document.createElement('span');
      content.className = 'marquee-content';
      content.textContent = text;
      
      // Create duplicate for seamless loop
      const duplicate = document.createElement('span');
      duplicate.className = 'marquee-content';
      duplicate.textContent = text;
      
      // Clear element and add marquee structure
      element.textContent = '';
      wrapper.appendChild(content);
      wrapper.appendChild(duplicate);
      element.appendChild(wrapper);
      
      // Mark as marquee active
      element.classList.add('marquee-active');
   }}} )
      // Calculate animation duration based on text length