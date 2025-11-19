document.addEventListener('DOMContentLoaded', () => {
  // Remove or comment out console.logs for production
  // console.log('Sidebar initiated');

  const sidebar = document.getElementById('platformSidebar') || document.querySelector('.platform-sidebar');
  const hideBtn = document.getElementById('hideSideBar');
  const showBtn = document.getElementById('showSideBar');

  if (!sidebar) {
    // console.warn('platformSidebar not found on this page.');
    return;
  }

  if (showBtn) {
    // console.log('showSideBar function initialized');
    showBtn.addEventListener('click', () => {
      sidebar.classList.add('is-open');
      // console.log('tried show');
    });
  }

  if (hideBtn) {
    // console.log('hideSideBar function initialized');
    hideBtn.addEventListener('click', () => {
      sidebar.classList.remove('is-open');
      // console.log('tried hide');
    });
  }
});