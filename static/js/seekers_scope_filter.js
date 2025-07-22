document.addEventListener("DOMContentLoaded", () => {
  if (typeof currentUserTown === "undefined") return;

  const cards = document.querySelectorAll("#seekerContainer [data-scope]");
  cards.forEach(card => {
    const scope = card.dataset.scope;
    const town = card.dataset.town?.trim().toLowerCase();

    // Match current user's town against seeker post's declared scope
    const shouldShow =
      scope === "global" ||
      scope === "continent" ||
      scope === "country" ||
      scope === "state" ||
      (scope === "town" && town === currentUserTown);

    card.style.display = shouldShow ? "block" : "none";
  });
});
