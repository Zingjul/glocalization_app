//post_scope_filter.js
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll("#postContainer [data-scope]");

  // These globals should be set server-side in your template:
  // currentUserApprovalStatus, currentUserContinent, currentUserCountry, currentUserState, currentUserTown

  // 1️⃣ If user has no profile or is not approved → show all approved posts
  if (
    typeof currentUserApprovalStatus === "undefined" ||
    !currentUserApprovalStatus ||
    currentUserApprovalStatus.toLowerCase() !== "approved"
  ) {
    cards.forEach(card => (card.style.display = "block"));
    return;
  }

  // 2️⃣ Otherwise, enforce location-based visibility
  cards.forEach(card => {
    const scope = card.dataset.scope;
    const continent = card.dataset.continent?.trim().toLowerCase();
    const country = card.dataset.country?.trim().toLowerCase();
    const state = card.dataset.state?.trim().toLowerCase();
    const town = card.dataset.town?.trim().toLowerCase();

    const userContinent = currentUserContinent?.trim().toLowerCase();
    const userCountry = currentUserCountry?.trim().toLowerCase();
    const userState = currentUserState?.trim().toLowerCase();
    const userTown = currentUserTown?.trim().toLowerCase();

    let shouldShow = false;

    switch (scope) {
      case "global":
        shouldShow = true;
        break;

      case "continent":
        shouldShow = continent === userContinent;
        break;

      case "country":
        shouldShow =
          continent === userContinent && country === userCountry;
        break;

      case "state":
        shouldShow =
          continent === userContinent &&
          country === userCountry &&
          state === userState;
        break;

      case "town":
        shouldShow =
          continent === userContinent &&
          country === userCountry &&
          state === userState &&
          town === userTown;
        break;
    }

    card.style.display = shouldShow ? "block" : "none";
  });
});
