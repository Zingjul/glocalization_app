// static/js/back_button.js
document.addEventListener('DOMContentLoaded', function () {
    const links = document.querySelectorAll('.js-back-link');
    if (!links.length) return;

    links.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();

            // If there's browsing history, go back one step
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // Fallback: go to the href (e.g. homepage or post list)
                window.location.href = link.getAttribute('href');
            }
        });
    });
});