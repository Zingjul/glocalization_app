// static/js/01-frontend/post-detail/comments-modal.js
document.addEventListener('DOMContentLoaded', function () {
    if (!document.body.classList.contains('post-detail-page')) return;

    const modal = document.getElementById('postCommentsModal');
    if (!modal) return;

    const openDescriptionBtn = document.querySelector('.js-open-description');
    const openCommentsBtn = document.querySelector('.js-open-comments');
    const closeBtn = modal.querySelector('.js-close-comments');
    const backdrop = modal.querySelector('.post-comments-modal__backdrop');
    const tabs = Array.from(modal.querySelectorAll('.post-comments-modal__tab'));
    const panes = Array.from(modal.querySelectorAll('.post-comments-modal__pane'));

    function switchPane(target) {
        tabs.forEach(tab => {
            tab.classList.toggle('is-active', tab.dataset.pane === target);
        });
        panes.forEach(pane => {
            pane.classList.toggle(
                'is-active',
                pane.dataset.paneTarget === target
            );
        });
    }

    function openModal(initialPane) {
        if (!initialPane) initialPane = 'description';
        switchPane(initialPane);
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // Open from "View more"
    if (openDescriptionBtn) {
        openDescriptionBtn.addEventListener('click', function () {
            openModal('description');
        });
    }

    // Open from "Comments" button
    if (openCommentsBtn) {
        openCommentsBtn.addEventListener('click', function () {
            openModal('comments');
        });
    }

    // Tab switching inside modal
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const pane = tab.dataset.pane;
            if (pane) switchPane(pane);
        });
    });

    // Close actions
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    document.addEventListener('keydown', function (e) {
        if (!modal.classList.contains('is-open')) return;
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});