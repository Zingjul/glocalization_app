/* ================================================
   Interaction Enhancements - Smooth UX
   ================================================ */

window.PlatformEnhanced = window.PlatformEnhanced || {};

(function(PE) {
  'use strict';

  class InteractionHandler {
    constructor() {
      this.init();
    }

    init() {
      this.enhanceButtons();
      this.addRippleEffect();
      this.improveFormFeedback();
      this.addLoadingStates();
    }

    enhanceButtons() {
      // Add micro-interactions to buttons
      document.querySelectorAll('.btn, button').forEach(btn => {
        // Don't interfere with existing handlers
        btn.addEventListener('mouseenter', function() {
          this.style.transform = 'translateY(-1px)';
        });

        btn.addEventListener('mouseleave', function() {
          this.style.transform = 'translateY(0)';
        });
      });
    }

    addRippleEffect() {
      // Material Design-style ripple effect
      document.querySelectorAll('.feed-action, .btn').forEach(element => {
        element.style.position = 'relative';
        element.style.overflow = 'hidden';

        element.addEventListener('click', function(e) {
          const ripple = document.createElement('span');
          ripple.className = 'ripple-effect';
          
          const rect = this.getBoundingClientRect();
          const size = Math.max(rect.width, rect.height);
          const x = e.clientX - rect.left - size / 2;
          const y = e.clientY - rect.top - size / 2;
          
          ripple.style.width = ripple.style.height = size + 'px';
          ripple.style.left = x + 'px';
          ripple.style.top = y + 'px';
          
          this.appendChild(ripple);
          
          setTimeout(() => ripple.remove(), 600);
        });
      });
    }

    improveFormFeedback() {
      // Real-time form validation feedback
      const inputs = document.querySelectorAll('input:not([type="file"]), textarea');
      
      inputs.forEach(input => {
        // Visual feedback on focus
        input.addEventListener('focus', function() {
          this.parentElement?.classList.add('input-focused');
        });

        input.addEventListener('blur', function() {
          this.parentElement?.classList.remove('input-focused');
          
          // Validate on blur
          if (this.value.trim()) {
            this.classList.add('has-value');
          } else {
            this.classList.remove('has-value');
          }
        });
      });
    }

    addLoadingStates() {
      // Add loading states to async operations
      document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
          const submitBtn = this.querySelector('[type="submit"]');
          if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
          }
        });
      });
    }
  }

  // Initialize
  PE.InteractionHandler = InteractionHandler;
  PE.interactions = new InteractionHandler();

})(window.PlatformEnhanced);