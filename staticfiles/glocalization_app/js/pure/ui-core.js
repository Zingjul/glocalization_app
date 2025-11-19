/**
 * UI Core - Pure Vanilla JavaScript
 * Handles all UI interactions for the Apple-inspired, X-refined design
 */

(function() {
    'use strict';

    // DOM Ready
    document.addEventListener('DOMContentLoaded', function() {
        initMobileMenu();
        initAlerts();
        initScrollEffects();
        initRevealAnimations();
        initFormEnhancements();
    });

    /**
     * Mobile Menu Toggle
     */
    function initMobileMenu() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const nav = document.querySelector('.header-nav');
        
        if (!toggle || !nav) return;
        
        toggle.addEventListener('click', function() {
            toggle.classList.toggle('active');
            nav.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                toggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && nav.classList.contains('active')) {
                toggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    /**
     * Alert Dismissal
     */
    function initAlerts() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.alert-close');
            
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    // Fade out animation
                    alert.style.animation = 'fadeOut 0.3s ease forwards';
                    
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                });
            }
            
            // Auto-dismiss after 5 seconds (except for page-level alerts)
            if (!alert.classList.contains('alert--page')) {
                setTimeout(() => {
                    if (alert && alert.parentNode) {
                        alert.style.animation = 'fadeOut 0.3s ease forwards';
                        setTimeout(() => {
                            if (alert.parentNode) {
                                alert.remove();
                            }
                        }, 300);
                    }
                }, 5000);
            }
        });
    }

    /**
     * Scroll Effects
     */
    function initScrollEffects() {
        const header = document.querySelector('.site-header');
        let lastScroll = 0;
        
        if (!header) return;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            // Add scrolled class when scrolled down
            if (currentScroll > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }

    /**
     * Reveal Animations on Scroll
     */
    function initRevealAnimations() {
        const reveals = document.querySelectorAll('.reveal');
        const revealStagger = document.querySelectorAll('.reveal-stagger');
        
        if (!reveals.length && !revealStagger.length) return;
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        reveals.forEach(el => observer.observe(el));
        revealStagger.forEach(el => observer.observe(el));
    }

    /**
     * Form Enhancements
     */
    function initFormEnhancements() {
        // Character counter for textareas
        const textareas = document.querySelectorAll('textarea[data-max-length]');
        
        textareas.forEach(textarea => {
            const maxLength = parseInt(textarea.dataset.maxLength);
            const counter = document.createElement('div');
            counter.className = 'form-counter';
            textarea.parentNode.insertBefore(counter, textarea.nextSibling);
            
            function updateCounter() {
                const length = textarea.value.length;
                const remaining = maxLength - length;
                
                counter.textContent = `${remaining} characters remaining`;
                
                if (remaining < 20) {
                    counter.classList.add('form-counter--warning');
                } else {
                    counter.classList.remove('form-counter--warning');
                }
                
                if (remaining < 0) {
                    counter.classList.add('form-counter--danger');
                } else {
                    counter.classList.remove('form-counter--danger');
                }
            }
            
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
        
        // File input preview
        const fileInputs = document.querySelectorAll('.form-file-input');
        
        fileInputs.forEach(input => {
            const label = input.nextElementSibling;
            const originalText = label.innerHTML;
            
            input.addEventListener('change', function() {
                const files = Array.from(this.files);
                
                if (files.length > 0) {
                    const fileNames = files.map(f => f.name).join(', ');
                    label.innerHTML = `<i class="fas fa-check"></i> ${files.length} file(s) selected`;
                    label.title = fileNames;
                } else {
                    label.innerHTML = originalText;
                    label.title = '';
                }
            });
        });
        
        // Form validation feedback
        const forms = document.querySelectorAll('.form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                let isValid = true;
                const requiredFields = form.querySelectorAll('[required]');
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        field.classList.add('form-input--error');
                        
                        // Remove error class on input
                        field.addEventListener('input', function() {
                            this.classList.remove('form-input--error');
                        }, { once: true });
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    
                    // Show error message
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'alert alert--error alert--page';
                    errorMsg.innerHTML = `
                        <span>Please fill in all required fields.</span>
                        <button class="alert-close" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    form.insertBefore(errorMsg, form.firstChild);
                    initAlerts(); // Re-initialize alerts for the new one
                    
                    // Scroll to top of form
                    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    /**
     * Utility: Show Toast Notification
     */
    window.showToast = function(message, type = 'info', duration = 3000) {
        const container = document.querySelector('.alerts-container') || createAlertsContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert--${type}`;
        alert.innerHTML = `
            <span>${message}</span>
            <button class="alert-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(alert);
        
        // Initialize close button
        const closeBtn = alert.querySelector('.alert-close');
        closeBtn.addEventListener('click', function() {
            alert.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => alert.remove(), 300);
        });
        
        // Auto-dismiss
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, duration);
    };
    
    function createAlertsContainer() {
        const container = document.createElement('div');
        container.className = 'alerts-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Utility: Lazy Load Images
     */
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px'
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }

})();