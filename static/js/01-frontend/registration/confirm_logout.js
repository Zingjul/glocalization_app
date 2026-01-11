// Confirm Logout Page Enhancements
document.addEventListener("DOMContentLoaded", function () {
  const confirmCard = document.querySelector(".confirm-card");

  if (confirmCard) {
    // Add a subtle fade-in effect
    confirmCard.style.opacity = 0;
    setTimeout(() => {
      confirmCard.style.transition = "opacity 0.8s ease-in-out";
      confirmCard.style.opacity = 1;
    }, 150);
  }
});
