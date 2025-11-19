/* ================================================
   Performance Monitor & Optimizer
   ================================================ */

window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class PerformanceOptimizer {
    constructor() {
      this.init();
    }

    init() {
      this.optimizeImages();
      this.deferNonCriticalCSS();
      this.enableResourceHints();
      this.monitorMetrics();
    }

    optimizeImages() {
      // Convert images to lazy load
      const images = document.querySelectorAll('img:not([loading])');
      
      images.forEach(img => {
        // Skip critical images (logo, avatars)
        if (!img.classList.contains('critical')) {
          img.setAttribute('loading', 'lazy');
        }
      });

      // Use Intersection Observer for better control
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
              imageObserver.unobserve(img);
            }
          }
        });
      }, { rootMargin: '50px' });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }

    deferNonCriticalCSS() {
      // Move non-critical CSS to load after page render
      const nonCriticalStyles = document.querySelectorAll('link[data-defer]');
      
      nonCriticalStyles.forEach(link => {
        link.setAttribute('media', 'print');
        link.addEventListener('load', function() {
          this.media = 'all';
        });
      });
    }

    enableResourceHints() {
      // Add preconnect for external resources
      const preconnects = [
        'https://cdn.jsdelivr.net',
        'https://cdnjs.cloudflare.com'
      ];

      preconnects.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = url;
        document.head.appendChild(link);
      });
    }

    monitorMetrics() {
      // Track performance metrics
      if ('performance' in window && 'PerformanceObserver' in window) {
        // Largest Contentful Paint
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            console.log('FID:', entry.processingStart - entry.startTime);
          });
        }).observe({ entryTypes: ['first-input'] });
      }
    }
  }

  // Initialize
  PE.PerformanceOptimizer = PerformanceOptimizer;
  PE.performance = new PerformanceOptimizer();

})(window.PlatformEnhanced);