/* ================================================
   Main Platform Controller - Enhanced Version
   Works alongside existing backend JS without conflicts
   ================================================ */

// Namespace to avoid conflicts with existing code
window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class MainController {
    constructor() {
      // Only initialize if we're on the platform page
      if (!document.body.classList.contains('platform-page')) return;
      
      this.init();
      this.preserveExistingFunctionality();
    }

    init() {
      // Wait for DOM and existing scripts to load
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.onReady());
      } else {
        this.onReady();
      }
    }

    onReady() {
      console.log('🚀 Platform Enhanced: Initializing...');
      
      // Add smooth enhancements without breaking existing code
      this.enhanceNavigation();
      this.enhanceCards();
      this.addKeyboardShortcuts();
      this.improveAccessibility();
      this.initializeAnimations();
    }

    preserveExistingFunctionality() {
      // Ensure existing scope filters still work
      const existingScripts = ['post_scope_filter', 'seekers_scope_filter'];
      existingScripts.forEach(script => {
        if (window[script]) {
          console.log(`✅ Existing script preserved: ${script}`);
        }
      });
    }

    enhanceNavigation() {
      // Smooth scroll for navigation links
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
          const target = document.querySelector(this.getAttribute('href'));
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      });

      // Enhanced mobile menu (works with existing menu)
      const mobileToggle = document.querySelector('.mobile-menu-toggle');
      const mobileMenu = document.querySelector('.mobile-menu');
      
      if (mobileToggle && mobileMenu) {
        // Add swipe gestures for mobile menu
        let touchStartX = 0;
        
        document.addEventListener('touchstart', (e) => {
          touchStartX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', (e) => {
          const touchEndX = e.changedTouches[0].screenX;
          const swipeDistance = touchEndX - touchStartX;
          
          if (swipeDistance > 100 && mobileMenu.classList.contains('active')) {
            mobileMenu.classList.remove('active');
          }
        });
      }
    }

    enhanceCards() {
      // Add hover effects and lazy loading to feed cards
      const cards = document.querySelectorAll('.feed-card');
      
      if (!cards.length) return;

      // Intersection Observer for lazy loading and animations
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            // Lazy load images in the card
            const images = entry.target.querySelectorAll('img[data-src]');
            images.forEach(img => {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            });
            
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '50px' });

      cards.forEach(card => {
        // Don't interfere with existing click handlers
        observer.observe(card);
        
        // Add subtle animation class
        card.classList.add('enhanced-card');
      });
    }

    addKeyboardShortcuts() {
      // Professional keyboard navigation
      document.addEventListener('keydown', (e) => {
        // Don't interfere when typing
        if (e.target.matches('input, textarea, select')) return;
        
        switch(e.key) {
          case '/':
            e.preventDefault();
            document.querySelector('.feed-search input')?.focus();
            break;
          case 'Escape':
            document.querySelector('.mobile-menu')?.classList.remove('active');
            break;
          case 'n':
            if (e.ctrlKey || e.metaKey) {
              e.preventDefault();
              window.location.href = '/post_create/';
            }
            break;
        }
      });
    }

    improveAccessibility() {
      // Add ARIA labels dynamically
      document.querySelectorAll('.feed-card').forEach((card, index) => {
        card.setAttribute('role', 'article');
        card.setAttribute('aria-label', `Post ${index + 1}`);
      });

      // Add focus indicators
      document.querySelectorAll('a, button, input, select, textarea').forEach(el => {
        if (!el.classList.contains('focus-visible')) {
          el.classList.add('focus-visible');
        }
      });
    }

    initializeAnimations() {
      // Add page transition effects
      const animateElements = document.querySelectorAll('[data-animate]');
      
      animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
          el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
        }, 100);
      });
    }
  }

  // Initialize and expose to global scope
  PE.MainController = MainController;
  PE.main = new MainController();

})(window.PlatformEnhanced);