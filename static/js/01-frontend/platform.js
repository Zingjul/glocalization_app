/**
 * Platform JavaScript Module
 * Professional architecture with ES6+ features
 * @version 2.0.0
 */

class PlatformController {
    constructor() {
        this.config = {
            breakpoints: {
                mobile: 576,
                tablet: 768,
                desktop: 1024,
                wide: 1440
            },
            animation: {
                duration: 300,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
            },
            api: {
                timeout: 5000,
                retries: 3
            }
        };
        
        this.state = {
            sidebar: 'expanded',
            theme: 'light',
            breakpoint: null,
            isOnline: navigator.onLine
        };
        
        this.init();
    }
    
    /**
     * Initialize all platform features
     */
    async init() {
        try {
            await this.domReady();
            
            // Core initialization
            this.setupEventListeners();
            this.initializeComponents();
            this.handleResponsive();
            this.setupAccessibility();
            this.initializePerformance();
            
            // Optional enhancements
            this.setupPWA();
            this.initializeAnalytics();
            
            console.log('✅ Platform initialized successfully');
        } catch (error) {
            console.error('❌ Platform initialization failed:', error);
            this.handleInitError(error);
        }
    }
    
    /**
     * Wait for DOM to be ready
     */
    domReady() {
        return new Promise(resolve => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }
    
    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Optimized resize handler with debouncing
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => this.handleResize(), 250);
        });
        
        // Network status monitoring
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Visibility change handling
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
        
        // Global error handling
        window.addEventListener('error', (e) => this.handleGlobalError(e));
        window.addEventListener('unhandledrejection', (e) => this.handleUnhandledRejection(e));
    }
    
    /**
     * Initialize UI components
     */
    initializeComponents() {
        // Sidebar
        this.initSidebar();
        
        // Navigation
        this.initNavigation();
        
        // Cards
        this.initCards();
        
        // Forms
        this.initForms();
        
        // Modals
        this.initModals();
        
        // Tooltips
        this.initTooltips();
    }
    
    /**
     * Sidebar functionality
     */
    initSidebar() {
        const sidebar = document.querySelector('.platform__sidebar');
        const toggleBtn = document.querySelector('.sidebar-toggle');
        
        if (!sidebar || !toggleBtn) return;
        
        toggleBtn.addEventListener('click', () => {
            const isCollapsed = sidebar.classList.contains('platform__sidebar--collapsed');
            
            if (isCollapsed) {
                this.expandSidebar(sidebar);
            } else {
                this.collapseSidebar(sidebar);
            }
            
            // Save preference
            localStorage.setItem('sidebarState', isCollapsed ? 'expanded' : 'collapsed');
        });
        
        // Restore saved state
        const savedState = localStorage.getItem('sidebarState');
        if (savedState === 'collapsed') {
            this.collapseSidebar(sidebar);
        }
    }
    
    /**
     * Collapse sidebar with animation
     */
    collapseSidebar(sidebar) {
        sidebar.classList.add('platform__sidebar--collapsed');
        this.state.sidebar = 'collapsed';
        
        // Animate text fade
        const textElements = sidebar.querySelectorAll('.sidebar-text');
        textElements.forEach(el => {
            el.style.opacity = '0';
            el.style.visibility = 'hidden';
        });
        
        // Emit event
        this.emit('sidebar:collapsed');
    }
    
    /**
     * Expand sidebar with animation
     */
    expandSidebar(sidebar) {
        sidebar.classList.remove('platform__sidebar--collapsed');
        this.state.sidebar = 'expanded';
        
        // Animate text fade
        const textElements = sidebar.querySelectorAll('.sidebar-text');
        textElements.forEach(el => {
            el.style.opacity = '1';
            el.style.visibility = 'visible';
        });
        
        // Emit event
        this.emit('sidebar:expanded');
    }
    
    /**
     * Initialize navigation enhancements
     */
    initNavigation() {
        // Mobile menu
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        if (mobileToggle && mobileMenu) {
            mobileToggle.addEventListener('click', () => {
                const isOpen = mobileMenu.classList.contains('mobile-menu--open');
                
                if (isOpen) {
                    this.closeMobileMenu(mobileMenu, mobileToggle);
                } else {
                    this.openMobileMenu(mobileMenu, mobileToggle);
                }
            });
            
            // Close on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && mobileMenu.classList.contains('mobile-menu--open')) {
                    this.closeMobileMenu(mobileMenu, mobileToggle);
                }
            });
            
            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!mobileMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
                    this.closeMobileMenu(mobileMenu, mobileToggle);
                }
            });
        }
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    /**
     * Open mobile menu
     */
    openMobileMenu(menu, toggle) {
        menu.classList.add('mobile-menu--open');
        toggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close mobile menu
     */
    closeMobileMenu(menu, toggle) {
        menu.classList.remove('mobile-menu--open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }
    
    /**
     * Initialize card interactions
     */
    initCards() {
        const cards = document.querySelectorAll('.card');
        
        if (!cards.length) return;
        
        // Intersection Observer for lazy loading and animations
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCard(entry.target);
                        this.lazyLoadMedia(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                root: null,
                rootMargin: '50px',
                threshold: 0.1
            }
        );
        
        cards.forEach(card => {
            observer.observe(card);
            
            // Add hover effects
            card.addEventListener('mouseenter', () => this.handleCardHover(card, true));
            card.addEventListener('mouseleave', () => this.handleCardHover(card, false));
            
            // Handle click
            card.addEventListener('click', (e) => this.handleCardClick(e, card));
        });
    }
    
    /**
     * Animate card on scroll
     */
    animateCard(card) {
        card.classList.add('card--visible');
        card.style.animation = `fadeInUp ${this.config.animation.duration}ms ${this.config.animation.easing}`;
    }
    
    /**
     * Lazy load media in card
     */
    lazyLoadMedia(card) {
        const images = card.querySelectorAll('img[data-src]');
        const videos = card.querySelectorAll('video[data-src]');
        
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            img.addEventListener('load', () => img.classList.add('loaded'));
        });
        
        videos.forEach(video => {
            video.src = video.dataset.src;
            video.removeAttribute('data-src');
        });
    }
    
    /**
     * Handle card hover
     */
    handleCardHover(card, isHovering) {
        if (isHovering) {
            card.classList.add('card--hover');
        } else {
            card.classList.remove('card--hover');
        }
    }
    
    /**
     * Handle card click
     */
    handleCardClick(event, card) {
        // Don't navigate if clicking on action buttons
        if (event.target.closest('.card__actions')) {
            return;
        }
        
        const url = card.dataset.url;
        if (url) {
            window.location.href = url;
        }
    }
    
    /**
     * Initialize form enhancements
     */
    initForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateInput(input));
                input.addEventListener('input', () => this.clearInputError(input));
            });
            
            // Handle submission
            form.addEventListener('submit', (e) => this.handleFormSubmit(e, form));
        });
    }
    
    /**
     * Validate input field
     */
    validateInput(input) {
        const value = input.value.trim();
        const isRequired = input.hasAttribute('required');
        const type = input.type;
        
        // Clear previous errors
        this.clearInputError(input);
        
        // Check if empty and required
        if (isRequired && !value) {
            this.showInputError(input, 'This field is required');
            return false;
        }
        
        // Type-specific validation
        switch (type) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    this.showInputError(input, 'Please enter a valid email');
                    return false;
                }
                break;
                
            case 'tel':
                if (value && !this.isValidPhone(value)) {
                    this.showInputError(input, 'Please enter a valid phone number');
                    return false;
                }
                break;
                
            case 'url':
                if (value && !this.isValidURL(value)) {
                    this.showInputError(input, 'Please enter a valid URL');
                    return false;
                }
                break;
        }
        
        return true;
    }
    
    /**
     * Show input error
     */
    showInputError(input, message) {
        const formGroup = input.closest('.form-group');
        if (!formGroup) return;
        
        input.classList.add('is-invalid');
        
        let errorEl = formGroup.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            formGroup.appendChild(errorEl);
        }
        
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    /**
     * Clear input error
     */
    clearInputError(input) {
        const formGroup = input.closest('.form-group');
        if (!formGroup) return;
        
        input.classList.remove('is-invalid');
        
        const errorEl = formGroup.querySelector('.form-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }
    
    /**
     * Handle form submission
     */
    async handleFormSubmit(event, form) {
        event.preventDefault();
        
        // Validate all inputs
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            this.showNotification('Please fix the errors in the form', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
        
        try {
            // Submit form
            const formData = new FormData(form);
            const response = await this.submitForm(form.action, formData);
            
            if (response.ok) {
                this.showNotification('Form submitted successfully', 'success');
                form.reset();
                
                // Handle redirect if needed
                const data = await response.json();
                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                }
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            this.showNotification('An error occurred. Please try again.', 'error');
            console.error('Form submission error:', error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
    
    /**
     * Submit form via fetch
     */
    async submitForm(url, formData) {
        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCookie('csrftoken')
            }
        });
    }
    
    /**
     * Initialize modal functionality
     */
    initModals() {
        // Custom modal implementation if needed
        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modalTrigger;
                this.openModal(modalId);
            });
        });
        
        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                const modal = closeBtn.closest('.modal');
                if (modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }
    
    /**
     * Open modal
     */
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.add('modal--open');
        document.body.style.overflow = 'hidden';
        
        // Focus management
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length) {
            focusableElements[0].focus();
        }
    }
    
    /**
     * Close modal
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.remove('modal--open');
        document.body.style.overflow = '';
    }
    
    /**
     * Initialize tooltips
     */
    initTooltips() {
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
        
        tooltipTriggers.forEach(trigger => {
            const tooltipText = trigger.dataset.tooltip;
            let tooltipEl = null;
            
            trigger.addEventListener('mouseenter', () => {
                tooltipEl = this.showTooltip(trigger, tooltipText);
            });
            
            trigger.addEventListener('mouseleave', () => {
                if (tooltipEl) {
                    this.hideTooltip(tooltipEl);
                }
            });
        });
    }
    
    /**
     * Show tooltip
     */
    showTooltip(trigger, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = trigger.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 10}px`;
        
        // Animate in
        requestAnimationFrame(() => {
            tooltip.classList.add('tooltip--visible');
        });
        
        return tooltip;
    }
    
    /**
     * Hide tooltip
     */
    hideTooltip(tooltip) {
        tooltip.classList.remove('tooltip--visible');
        setTimeout(() => {
            tooltip.remove();
        }, 200);
    }
    
    /**
     * Handle responsive behavior
     */
    handleResponsive() {
        this.updateBreakpoint();
        
        // Apply responsive classes
        document.body.classList.remove('is-mobile', 'is-tablet', 'is-desktop', 'is-wide');
        document.body.classList.add(`is-${this.state.breakpoint}`);
    }
    
    /**
     * Update current breakpoint
     */
    updateBreakpoint() {
        const width = window.innerWidth;
        const { breakpoints } = this.config;
        
        if (width < breakpoints.mobile) {
            this.state.breakpoint = 'mobile';
        } else if (width < breakpoints.tablet) {
            this.state.breakpoint = 'tablet';
        } else if (width < breakpoints.desktop) {
            this.state.breakpoint = 'desktop';
        } else {
            this.state.breakpoint = 'wide';
        }
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        const oldBreakpoint = this.state.breakpoint;
        this.updateBreakpoint();
        
        if (oldBreakpoint !== this.state.breakpoint) {
            this.handleResponsive();
            this.emit('breakpoint:change', this.state.breakpoint);
        }
    }
    
    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        // Skip links
        const skipLinks = document.querySelectorAll('.skip-link');
        skipLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Skip if in input
            if (e.target.matches('input, textarea, select')) return;
            
            switch (e.key) {
                case '/':
                    e.preventDefault();
                    const searchInput = document.querySelector('.search-input');
                    if (searchInput) searchInput.focus();
                    break;
                    
                case 'g':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    }
                    break;
            }
        });
        
        // ARIA live regions
        this.setupLiveRegions();
    }
    
    /**
     * Setup ARIA live regions for dynamic content
     */
    setupLiveRegions() {
        // Create notification live region
        if (!document.getElementById('live-notifications')) {
            const liveRegion = document.createElement('div');
            liveRegion.id = 'live-notifications';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.className = 'visually-hidden';
            document.body.appendChild(liveRegion);
        }
    }
    
    /**
     * Initialize performance optimizations
     */
    initializePerformance() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Debounce scroll events
        this.optimizeScrollEvents();
        
        // Prefetch links on hover
        this.setupPrefetch();
        
        // Web Workers for heavy operations
        this.setupWebWorkers();
    }
    
    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.dataset.src;
                            img.classList.add('loaded');
                            imageObserver.unobserve(img);
                        }
                    });
                },
                {
                    rootMargin: '100px'
                }
            );
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
    
    /**
     * Optimize scroll events
     */
    optimizeScrollEvents() {
        let scrollTimer;
        let lastScrollTop = 0;
        
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            
            scrollTimer = setTimeout(() => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const direction = scrollTop > lastScrollTop ? 'down' : 'up';
                
                this.emit('scroll:end', { scrollTop, direction });
                
                lastScrollTop = scrollTop;
            }, 150);
        }, { passive: true });
    }
    
    /**
     * Setup link prefetching
     */
    setupPrefetch() {
        if ('requestIdleCallback' in window) {
            document.querySelectorAll('a[href^="/"]').forEach(link => {
                link.addEventListener('mouseenter', () => {
                    requestIdleCallback(() => {
                        const prefetchLink = document.createElement('link');
                        prefetchLink.rel = 'prefetch';
                        prefetchLink.href = link.href;
                        document.head.appendChild(prefetchLink);
                    });
                }, { once: true });
            });
        }
    }
    
    /**
     * Setup Web Workers
     */
    setupWebWorkers() {
        if ('Worker' in window) {
            // Create worker for heavy computations
            this.worker = new Worker('/static/js/worker.js');
            
            this.worker.addEventListener('message', (e) => {
                this.handleWorkerMessage(e.data);
            });
        }
    }
    
    /**
     * Setup PWA features
     */
    setupPWA() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('ServiceWorker registered:', registration);
                })
                .catch(error => {
                    console.log('ServiceWorker registration failed:', error);
                });
        }
        
        // Install prompt
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            const installBtn = document.querySelector('.install-btn');
            if (installBtn) {
                installBtn.style.display = 'block';
                installBtn.addEventListener('click', () => {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(choiceResult => {
                        deferredPrompt = null;
                    });
                });
            }
        });
    }
    
    /**
     * Initialize analytics
     */
    initializeAnalytics() {
        // Track page views
        this.trackPageView();
        
        // Track events
        document.addEventListener('click', (e) => {
            const trackable = e.target.closest('[data-track]');
            if (trackable) {
                this.trackEvent(
                    'click',
                    trackable.dataset.trackCategory || 'interaction',
                    trackable.dataset.trackLabel || trackable.textContent
                );
            }
        });
    }
    
    /**
     * Track page view
     */
    trackPageView() {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', {
                page_path: window.location.pathname
            });
        }
    }
    
    /**
     * Track custom event
     */
    trackEvent(action, category, label, value) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label,
                value: value
            });
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.textContent = message;
        notification.setAttribute('role', 'alert');
        
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('notification--visible');
        });
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }
        
        // Update live region
        const liveRegion = document.getElementById('live-notifications');
        if (liveRegion) {
            liveRegion.textContent = message;
        }
        
        return notification;
    }
    
    /**
     * Hide notification
     */
    hideNotification(notification) {
        notification.classList.remove('notification--visible');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
    
    /**
     * Handle online status
     */
    handleOnline() {
        this.state.isOnline = true;
        this.showNotification('Connection restored', 'success');
        this.emit('network:online');
    }
    
    /**
     * Handle offline status
     */
    handleOffline() {
        this.state.isOnline = false;
        this.showNotification('Connection lost. Some features may be unavailable.', 'warning', 0);
        this.emit('network:offline');
    }
    
    /**
     * Handle visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.emit('page:hidden');
        } else {
            this.emit('page:visible');
        }
    }
    
    /**
     * Handle global errors
     */
    handleGlobalError(error) {
        console.error('Global error:', error);
        
        // Log to server
        this.logError(error);
    }
    
    /**
     * Handle unhandled promise rejections
     */
    handleUnhandledRejection(event) {
        console.error('Unhandled promise rejection:', event.reason);
        
        // Log to server
        this.logError(event.reason);
    }
    
    /**
     * Handle initialization errors
     */
    handleInitError(error) {
        console.error('Initialization error:', error);
        
        // Show user-friendly error
        const errorContainer = document.createElement('div');
        errorContainer.className = 'init-error';
        errorContainer.innerHTML = `
            <h2>Something went wrong</h2>
            <p>We're having trouble loading the page. Please try refreshing.</p>
            <button onclick="location.reload()">Refresh Page</button>
        `;
        
        document.body.appendChild(errorContainer);
    }
    
    /**
     * Log error to server
     */
    async logError(error) {
        try {
            await fetch('/api/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: error.message || error,
                    stack: error.stack,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });
        } catch (logError) {
            console.error('Failed to log error:', logError);
        }
    }
    
    /**
     * Event emitter
     */
    emit(eventName, data = {}) {
        const event = new CustomEvent(`platform:${eventName}`, {
            detail: data,
            bubbles: true
        });
        
        document.dispatchEvent(event);
    }
    
    /**
     * Validation helpers
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    isValidPhone(phone) {
        const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        return re.test(phone);
    }
    
    isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Get cookie value
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.platform = new PlatformController();
    });
} else {
    window.platform = new PlatformController();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlatformController;
}