// static/js/01-frontend/image-dominant-bg.js

document.addEventListener('DOMContentLoaded', function () {
    // Target both carousel images and current_images.html images
    const images = document.querySelectorAll(
        '.media-carousel__image, .current-images__container img'
    );
    if (!images.length) return;

    images.forEach(function (img) {
        if (img.complete && img.naturalWidth) {
            applyDominantBg(img);
        } else {
            img.addEventListener('load', function () {
                applyDominantBg(img);
            });
        }
    });

    function applyDominantBg(img) {
        // Only same-origin images will work due to canvas security
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            const size = 40; // small thumbnail size
            canvas.width = size;
            canvas.height = size;

            ctx.drawImage(img, 0, 0, size, size);
            const imageData = ctx.getImageData(0, 0, size, size).data;

            let r = 0, g = 0, b = 0, count = 0;

            for (let i = 0; i < imageData.length; i += 4) {
                const alpha = imageData[i + 3];
                if (alpha < 128) continue; // skip transparent-ish pixels

                r += imageData[i];
                g += imageData[i + 1];
                b += imageData[i + 2];
                count++;
            }

            if (!count) return;

            r = Math.round(r / count);
            g = Math.round(g / count);
            b = Math.round(b / count);

            const parent =
                img.closest('.media-carousel__item') ||
                img.closest('.current-images__container') ||
                img.parentElement;

            if (parent) {
                parent.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
            }
        } catch (e) {
            // Likely a cross-origin issue; just skip silently
            console.warn('Could not compute dominant color for image:', img.src, e);
        }
    }
});