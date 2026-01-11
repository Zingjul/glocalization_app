// header-smooth-move.js
const header = document.querySelector('.site-header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
        header.classList.add('site-header--scrolled');
    } else {
        header.classList.remove('site-header--scrolled');
    }
    
    lastScroll = currentScroll;
});