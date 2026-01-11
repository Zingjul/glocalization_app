// Logout Page Enhancements
document.addEventListener("DOMContentLoaded", function () {
  const alertBox = document.querySelector(".alert-success");

  if (alertBox) {
    // Add a fade-in effect
    alertBox.style.opacity = 0;
    setTimeout(() => {
      alertBox.style.transition = "opacity 1s ease-in-out";
      alertBox.style.opacity = 1;
    }, 200);
  }
});
