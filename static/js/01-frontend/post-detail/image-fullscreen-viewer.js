// static/js/01-frontend/post-detail/image-fullscreen-viewer.js
document.addEventListener('DOMContentLoaded', function () {
    if (!document.body.classList.contains('post-detail-page')) return;

    const overlay = document.getElementById('postImageOverlay');
    if (!overlay) return;

    const imgEl = overlay.querySelector('.post-fullscreen-image');
    const videoEl = overlay.querySelector('.post-fullscreen-video');
    const videoSourceEl = videoEl ? videoEl.querySelector('source') : null;

    const btnPrev = overlay.querySelector('.post-fullscreen-nav--prev');
    const btnNext = overlay.querySelector('.post-fullscreen-nav--next');
    const btnClose = overlay.querySelector('.post-fullscreen-close');
    const counterEl = document.getElementById('postFullscreenCounter');

    // Collect both images and videos from the main carousel
    const mediaEls = Array.from(
        document.querySelectorAll(
            '.platform-feed .media-carousel__image, .platform-feed .media-carousel__video'
        )
    );
    if (!mediaEls.length) return;

    // Normalize into a media queue
    const galleryMedia = mediaEls.map(function (el) {
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

    let currentIndex = 0;

    function updateViewer() {
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
            counterEl.textContent =
                (currentIndex + 1) + ' / ' + galleryMedia.length;
        }
    }

    function openFullscreen(index) {
        if (index < 0 || index >= galleryMedia.length) return;
        currentIndex = index;
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
        currentIndex = (currentIndex - 1 + galleryMedia.length) % galleryMedia.length;
        updateViewer();
    }

    function showNext() {
        currentIndex = (currentIndex + 1) % galleryMedia.length;
        updateViewer();
    }

    // Attach click to all media (images + videos)
    mediaEls.forEach(function (el, index) {
        el.style.cursor = 'zoom-in';
        el.addEventListener('click', function () {
            openFullscreen(index);
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

    // Prev/Next buttons
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

    // Keyboard navigation
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