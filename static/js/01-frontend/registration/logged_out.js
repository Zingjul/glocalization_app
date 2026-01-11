// Enhancements for Logout Successfully page
document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector(".animate-fade-in");

  if (card) {
    // Add a slight delay before fade-in
    card.style.opacity = 0;
    setTimeout(() => {
      card.style.opacity = 1;
    }, 150);
  }

  // Optional: auto-redirect after 5 seconds
  setTimeout(() => {
    window.location.href = "/"; // Homepage URL
  }, 500);
});
