document.addEventListener('DOMContentLoaded', function() {
    // Add scroll effect to header
    let lastScroll = 0;
    const feedNav = document.querySelector('.feed-nav');
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 10) {
            feedNav?.classList.add('scrolled');
        } else {
            feedNav?.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
    
    // Add click animation to nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// Toggle search function
function toggleSearch() {
    const searchForm = document.querySelector('.feed-search');
    if (searchForm) {
        searchForm.style.display = searchForm.style.display === 'none' ? 'flex' : 'none';
    }
}