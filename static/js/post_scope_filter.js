document.addEventListener("DOMContentLoaded", () => {
  if (typeof currentUserTown === "undefined") return;

  const cards = document.querySelectorAll("#postContainer [data-scope]");
  cards.forEach(card => {
    const scope = card.dataset.scope;
    const town = card.dataset.town?.trim().toLowerCase();

    const shouldShow =
      scope === "global" ||
      scope === "continent" ||
      scope === "country" ||
      scope === "state" ||
      (scope === "town" && town === currentUserTown);

    card.style.display = shouldShow ? "block" : "none";
  });
});
