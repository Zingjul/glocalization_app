document.addEventListener("DOMContentLoaded", () => {
  if (typeof currentUserTown === "undefined") return;

  const cards = document.querySelectorAll(".post-card");
  cards.forEach(card => {
    const scope = card.dataset.scope;
    const town = card.dataset.town?.trim().toLowerCase();

    const shouldShow =
      scope === "global" ||
      (scope === "town" && town === currentUserTown);

    card.style.display = shouldShow ? "block" : "none";
  });
});
