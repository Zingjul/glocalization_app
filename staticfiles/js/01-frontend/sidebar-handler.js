document.addEventListener('DOMContentLoaded', () => {
    console.log('sidebar-handler.js loaded');
    const sidebarNotificationToggleHide = document.getElementById('sidebarNotificationToggleHide');
    const sidebarNotificationToggleShow = document.getElementById('sidebarNotificationToggleShow');
    const platformSidebar = document.getElementById('platformSidebar');
    let isSidebarVisible = true;

    function hideSideBar(){
        console.log('hideSideBar function initialized');
            if (isSidebarVisible) {
                platformSidebar.style.display = 'none';
                isSidebarVisible = false;
            }
    }
    function showSideBar(){
        console.log('showSideBar function initialized');
            if (!isSidebarVisible) {
                platformSidebar.style.display = 'block';
                isSidebarVisible = true;
            }

    }});

  