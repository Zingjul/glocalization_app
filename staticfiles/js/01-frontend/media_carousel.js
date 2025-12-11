// media-carousel.js - Professional Media Carousel Handler

class MediaCarousel {
    constructor() {
        this.carousels = new Map();
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.init();
    }
    
    init() {
        // Initialize all carousels on page load
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeCarousels();
            this.setupKeyboardNavigation();
            this.setupTouchSupport();
        });
        
        // Reinitialize when new content is loaded (for infinite scroll)
        // Note: 'contentLoaded' should be a custom event fired by your infinite scroll logic.
        document.addEventListener('contentLoaded', () => {
            this.initializeCarousels();
        });
    }

    /**
     * Detects image aspect ratio robustly, even if the image is already cached.
     * It ensures the promise resolves either on load, if already complete, or on error.
     */
    detectImageAspectRatio(img) {
        return new Promise((resolve) => {
            
            const calculateRatio = () => {
                // Return 0 if natural dimensions are not available (e.g., broken image)
                if (img.naturalWidth === 0 || img.naturalHeight === 0) {
                    return 0;
                }
                return img.naturalWidth / img.naturalHeight;
            };

            let handled = false; 

            const handleLoad = () => {
                if (!handled) {
                    handled = true;
                    resolve(calculateRatio());
                }
            };

            const handleError = () => {
                if (!handled) {
                    handled = true;
                    console.error("Image failed to load:", img.src);
                    resolve(0); // Resolve with 0 ratio on error to ensure .loaded class is applied
                }
            };

            // 1. Check if the image is already complete (handles cached images)
            if (img.complete) {
                // Note: We use setTimeout to ensure a clean exit from the synchronous flow
                // and give the browser a chance to render the existing image structure.
                setTimeout(handleLoad, 0); 
            } else {
                // 2. Attach standard event listeners
                img.onload = handleLoad;
                img.onerror = handleError;
                
                // 3. Re-check complete status immediately after attaching listeners 
                //    (Handles the race condition where the image loaded in-between)
                if (img.complete) {
                    handleLoad();
                }
            }
        });
    }

    async initializeCarousels() {
        const carousels = document.querySelectorAll('.media-carousel');
        
        carousels.forEach(async (carousel) => {
            const postId = carousel.dataset.postId;

            // Only initialize carousels we haven't processed yet
            if (!this.carousels.has(postId)) {
                this.carousels.set(postId, {
                    element: carousel,
                    currentIndex: 0,
                    totalItems: carousel.querySelectorAll('.media-carousel__item').length,
                    isPlaying: false
                });
                
                // Process images for aspect ratio and apply the critical .loaded class
                const images = carousel.querySelectorAll('.media-carousel__image');
                images.forEach(async (img) => {
                    let ratio = 0;
                    try {
                        ratio = await this.detectImageAspectRatio(img);
                        
                        // Add aspect ratio class
                        const item = img.closest('.media-carousel__item');
                        
                        if (ratio > 1.5) {
                            item.dataset.aspect = 'landscape';
                        } else if (ratio < 0.8 && ratio > 0) {
                            item.dataset.aspect = 'portrait';
                            if (ratio < 0.5) {
                                img.classList.add('very-tall');
                            }
                        } else {
                            item.dataset.aspect = 'square';
                        }
                    } catch (error) {
                        console.error("Error processing image for carousel:", error);
                    } finally {
                        // CRITICAL: Always mark image as loaded to trigger visibility in CSS (opacity: 1)
                        img.classList.add('loaded');
                    }
                });
                
                // Initial visibility check: if no active class is set, set the first item as active
                const items = carousel.querySelectorAll('.media-carousel__item');
                if (items.length > 0 && !carousel.querySelector('.media-carousel__item.active')) {
                    items[0].classList.add('active');
                }
            }
        });
    }
    
    navigateMedia(button, direction) {
        const carouselEl = button.closest('.media-carousel');
        if (!carouselEl) return;
        const postId = carouselEl.dataset.postId;

        const carousel = this.carousels.get(postId);
        
        if (!carousel) return;
        
        const { currentIndex, totalItems } = carousel;
        let newIndex;
        
        if (direction === 'prev') {
            newIndex = currentIndex > 0 ? currentIndex - 1 : totalItems - 1;
        } else {
            newIndex = currentIndex < totalItems - 1 ? currentIndex + 1 : 0;
        }
        
        this.goToMedia(postId, newIndex);
    }
    
    goToMedia(postId, index) {
        const carousel = this.carousels.get(String(postId));
        
        if (!carousel) return;
        
        const { element } = carousel;
        const items = element.querySelectorAll('.media-carousel__item');
        const indicators = element.querySelectorAll('.media-carousel__indicator');
        
        // Pause any playing videos
        const currentVideo = items[carousel.currentIndex]?.querySelector('video');
        if (currentVideo) {
            currentVideo.pause();
        }
        
        // Update active states
        items.forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });
        
        indicators.forEach((indicator, i) => {
            indicator.classList.toggle('active', i === index);
        });
        
        // Update carousel state
        carousel.currentIndex = index;
        
        // Autoplay video if it's a video
        const newVideo = items[index]?.querySelector('video');
        if (newVideo) {
            newVideo.load(); // Ensure video is ready to play
            newVideo.play().catch(e => console.log("Video autoplay blocked or failed:", e));
        }
        
        // Preload next image (remains the same)
        this.preloadNext(carousel, index);
    }
    
    preloadNext(carousel, currentIndex) {
        const { element, totalItems } = carousel;
        const nextIndex = (currentIndex + 1) % totalItems;
        const nextImage = element.querySelectorAll('.media-carousel__item')[nextIndex]?.querySelector('img');
        
        if (nextImage && !nextImage.complete) {
            // Note: The new Image() object is purely for browser pre-fetching
            const img = new Image();
            img.src = nextImage.src;
        }
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            const activeCarousel = document.querySelector('.media-carousel:hover, .media-carousel:focus-within'); // Improved focus check
            if (!activeCarousel) return;
            
            const postId = activeCarousel.dataset.postId;
            
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.navigateToPrev(postId);
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.navigateToNext(postId);
            }
        });
    }
    
    setupTouchSupport() {
        document.querySelectorAll('.media-carousel__container').forEach(container => {
            // Touch events
            container.addEventListener('touchstart', (e) => {
                this.touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });
            
            container.addEventListener('touchend', (e) => {
                this.touchEndX = e.changedTouches[0].screenX;
                this.handleSwipe(container);
            }, { passive: true });
            
            // Mouse events for desktop drag/swipe
            let mouseDown = false;
            let startX = 0;
            
            container.addEventListener('mousedown', (e) => {
                mouseDown = true;
                startX = e.clientX;
                container.style.cursor = 'grabbing';
            });
            
            // Handle mouse move to prevent accidental text selection during drag
            container.addEventListener('mousemove', (e) => {
                 if (mouseDown) e.preventDefault();
            });

            container.addEventListener('mouseup', (e) => {
                if (mouseDown) {
                    const endX = e.clientX;
                    const diff = startX - endX;
                    
                    if (Math.abs(diff) > 50) {
                        const postId = container.closest('.media-carousel').dataset.postId;
                        if (diff > 0) {
                            this.navigateToNext(postId);
                        } else {
                            this.navigateToPrev(postId);
                        }
                    }
                }
                mouseDown = false;
                container.style.cursor = 'grab';
            });
            
            container.addEventListener('mouseleave', () => {
                mouseDown = false;
                container.style.cursor = 'grab';
            });
        });
    }
    
    handleSwipe(container) {
        const diff = this.touchStartX - this.touchEndX;
        const minSwipeDistance = 50;
        
        if (Math.abs(diff) > minSwipeDistance) {
            const postId = container.closest('.media-carousel').dataset.postId;
            
            if (diff > 0) {
                // Swiped left - next
                this.navigateToNext(postId);
            } else {
                // Swiped right - previous
                this.navigateToPrev(postId);
            }
        }
    }
    
    navigateToNext(postId) {
        const carousel = this.carousels.get(String(postId));
        if (!carousel) return;
        
        const { currentIndex, totalItems } = carousel;
        const newIndex = currentIndex < totalItems - 1 ? currentIndex + 1 : 0;
        this.goToMedia(postId, newIndex);
    }
    
    navigateToPrev(postId) {
        const carousel = this.carousels.get(String(postId));
        if (!carousel) return;
        
        const { currentIndex, totalItems } = carousel;
        const newIndex = currentIndex > 0 ? currentIndex - 1 : totalItems - 1;
        this.goToMedia(postId, newIndex);
    }
}

// Initialize carousel
const mediaCarousel = new MediaCarousel();

// Global functions for onclick handlers
function navigateMedia(button, direction) {
    mediaCarousel.navigateMedia(button, direction);
}

function goToMedia(postId, index) {
    mediaCarousel.goToMedia(postId, index);
}

// Auto-advance carousel (optional feature)
function enableAutoAdvance(postId, interval = 5000) {
    const carousel = mediaCarousel.carousels.get(String(postId));
    if (!carousel) return;
    
    // Use a unique ID for the interval to allow stopping/restarting if needed
    carousel.intervalId = setInterval(() => {
        if (!carousel.element.matches(':hover, :focus-within')) {
            mediaCarousel.navigateToNext(postId);
        }
    }, interval);
}