// static/js/01-frontend/post-detail/post-detail-viewer.js
document.addEventListener('DOMContentLoaded', function () {
    const viewer = document.getElementById('postViewer');
    const overlay = document.getElementById('postOverlay');
    if (!viewer || !overlay) return;

    const IDLE_DELAY = 2500; // ms
    let idleTimer = null;

    function showOverlay() {
        overlay.classList.add('post-detail-overlay--visible');
    }

    function hideOverlay() {
        if (overlay.matches(':hover') || overlay.contains(document.activeElement)) {
            return;
        }
        overlay.classList.remove('post-detail-overlay--visible');
    }

    function handleActivity() {
        showOverlay();
        if (idleTimer) clearTimeout(idleTimer);
        idleTimer = setTimeout(hideOverlay, IDLE_DELAY);
    }

    // Initial state: show briefly, then hide
    showOverlay();
    idleTimer = setTimeout(hideOverlay, IDLE_DELAY);

    viewer.addEventListener('mousemove', handleActivity);
    viewer.addEventListener('click', handleActivity);
    viewer.addEventListener('touchstart', handleActivity, { passive: true });
});