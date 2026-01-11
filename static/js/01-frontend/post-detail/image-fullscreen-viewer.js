// static/js/01-frontend/post-detail/image-fullscreen-viewer.js
document.addEventListener('DOMContentLoaded', function () {
    // Run on both detail and list pages
    const isDetail = document.body.classList.contains('post-detail-page');
    const isPostList = document.body.classList.contains('post-list-page');
    const isSeekerList = document.body.classList.contains('seeker-list-page');

    if (!isDetail && !isPostList && !isSeekerList) return;

    const overlay = document.getElementById('postImageOverlay');
    if (!overlay) return;

    const imgEl = overlay.querySelector('.post-fullscreen-image');
    const videoEl = overlay.querySelector('.post-fullscreen-video');
    const videoSourceEl = videoEl ? videoEl.querySelector('source') : null;

    const btnPrev = overlay.querySelector('.post-fullscreen-nav--prev');
    const btnNext = overlay.querySelector('.post-fullscreen-nav--next');
    const btnClose = overlay.querySelector('.post-fullscreen-close');
    const counterEl = document.getElementById('postFullscreenCounter');

    // Current gallery for the *clicked* post only
    let galleryMedia = [];   // [{type: 'image'|'video', src: '...'}, ...]
    let currentIndex = 0;

    function buildGalleryFromCarousel(carouselEl, clickedEl) {
        const mediaEls = Array.from(
            carouselEl.querySelectorAll('.media-carousel__image, .media-carousel__video')
        );
        galleryMedia = mediaEls.map(function (el) {
            const isVideo = el.tagName.toLowerCase() === 'video';
            let src = '';

            if (isVideo) {
                const s = el.querySelector('source');
                src = s ? s.src : (el.currentSrc || el.src || '');
            } else {
                src = el.currentSrc || el.src || '';
            }

            return {
                type: isVideo ? 'video' : 'image',
                src: src
            };
        });

        currentIndex = mediaEls.indexOf(clickedEl);
        if (currentIndex < 0) currentIndex = 0;
    }

    function updateViewer() {
        if (!galleryMedia.length) return;

        const item = galleryMedia[currentIndex];

        if (item.type === 'image') {
            if (videoEl) {
                videoEl.pause();
                videoEl.style.display = 'none';
            }
            if (imgEl) {
                imgEl.src = item.src;
                imgEl.style.display = 'block';
            }
        } else {
            if (imgEl) {
                imgEl.style.display = 'none';
            }
            if (videoEl) {
                if (videoSourceEl) {
                    videoSourceEl.src = item.src;
                    videoEl.load();
                } else {
                    videoEl.src = item.src;
                }
                videoEl.style.display = 'block';
            }
        }

        if (counterEl) {
            counterEl.textContent = (currentIndex + 1) + ' / ' + galleryMedia.length;
        }
    }

    function openFullscreenFromElement(clickedEl) {
        const carousel = clickedEl.closest('.media-carousel');
        if (!carousel) return;

        buildGalleryFromCarousel(carousel, clickedEl);
        if (!galleryMedia.length) return;

        updateViewer();
        overlay.classList.add('is-open');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeFullscreen() {
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (videoEl) videoEl.pause();
    }

    function showPrev() {
        if (!galleryMedia.length) return;
        currentIndex = (currentIndex - 1 + galleryMedia.length) % galleryMedia.length;
        updateViewer();
    }

    function showNext() {
        if (!galleryMedia.length) return;
        currentIndex = (currentIndex + 1) % galleryMedia.length;
        updateViewer();
    }

    // Attach click handlers to all media in all carousels
    const allMediaEls = document.querySelectorAll('.media-carousel__image, .media-carousel__video');
    allMediaEls.forEach(function (el) {
        el.style.cursor = 'zoom-in';
        el.addEventListener('click', function () {
            openFullscreenFromElement(el);
        });
    });

    // Close button
    if (btnClose) {
        btnClose.addEventListener('click', function (e) {
            e.stopPropagation();
            closeFullscreen();
        });
    }

    // Click backdrop to close
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
            closeFullscreen();
        }
    });

    // Navigation
    if (btnPrev) {
        btnPrev.addEventListener('click', function (e) {
            e.stopPropagation();
            showPrev();
        });
    }
    if (btnNext) {
        btnNext.addEventListener('click', function (e) {
            e.stopPropagation();
            showNext();
        });
    }

    // Keyboard support
    document.addEventListener('keydown', function (e) {
        if (!overlay.classList.contains('is-open')) return;

        if (e.key === 'Escape') {
            closeFullscreen();
        } else if (e.key === 'ArrowLeft') {
            showPrev();
        } else if (e.key === 'ArrowRight') {
            showNext();
        }
    });
});