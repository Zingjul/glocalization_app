document.addEventListener("DOMContentLoaded", () => {
  // Show all seeker posts if currentUserTown is missing, empty, or "undefined"
  if (
    typeof currentUserTown === "undefined" ||
    !currentUserTown ||
    currentUserTown === "undefined"
  ) {
    document.querySelectorAll("#seekerContainer [data-scope]").forEach(card => {
      card.style.display = "block";
    });
    return;
  }

  const cards = document.querySelectorAll("#seekerContainer [data-scope]");
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