// postfinder_filter.js
document.addEventListener("DOMContentLoaded", function () {
  const continentField = document.querySelector("#id_post_continent");
  const countryField   = document.querySelector("#id_post_country");
  const stateField     = document.querySelector("#id_post_state");
  const townField      = document.querySelector("#id_post_town");
  const applyBtn       = document.getElementById("applyFilters");
  const posts          = document.querySelectorAll(".post-item");

  // Normalize values: treat "0" or "" as empty
  function normalize(val) {
    return (val && val !== "0") ? val : null;
  }

  function applyFiltersFn() {
    const selectedContinent = normalize(continentField.value);
    const selectedCountry   = normalize(countryField.value);
    const selectedState     = normalize(stateField.value);
    const selectedTown      = normalize(townField.value);

    posts.forEach(post => {
      const matches =
        (!selectedContinent || post.dataset.continent === selectedContinent) &&
        (!selectedCountry   || post.dataset.country   === selectedCountry) &&
        (!selectedState     || post.dataset.state     === selectedState) &&
        (!selectedTown      || post.dataset.town      === selectedTown);

      post.style.display = matches ? "" : "none";
    });
  }

  if (applyBtn) {
    applyBtn.addEventListener("click", applyFiltersFn);
  }
});
