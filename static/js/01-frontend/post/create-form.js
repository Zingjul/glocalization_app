// Optional interactivity for Create Options page
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card");
  cards.forEach(card => {
    card.addEventListener("click", () => {
      card.classList.add("shadow-lg");
      setTimeout(() => card.classList.remove("shadow-lg"), 300);
    });
  });
});
