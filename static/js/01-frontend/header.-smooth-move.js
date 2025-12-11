<script>
document.addEventListener('DOMContentLoaded', function () {
    const header = document.getElementById('mainHeader');
    const bottomNav = document.querySelector('.bottom-nav');
    const SCROLL_THRESHOLD = 20;   // px

    function updateNavStates() {
        const scrolled = window.scrollY > SCROLL_THRESHOLD;

        if (header) {
            header.classList.toggle('site-header--scrolled', scrolled);
        }
        if (bottomNav) {
            bottomNav.classList.toggle('bottom-nav--scrolled', scrolled);
        }
    }

    // Initial state (if page loads scrolled)
    updateNavStates();

    window.addEventListener('scroll', updateNavStates, { passive: true });
});
</script>