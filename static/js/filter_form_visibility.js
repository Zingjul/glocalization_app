document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("postFilterForm");
  const scopeSelect = document.getElementById("scopeSelect");
  const queryInput = document.querySelector("input[name='query']");
  const submitButton = form?.querySelector("button[type='submit']");

  const fields = {
    continent: document.getElementById("continentField"),
    country: document.getElementById("countryField"),
    state: document.getElementById("stateField"),
    town: document.getElementById("townField"),
  };

  const dropdowns = {
    continent: document.querySelector("select[name='continent']"),
    country: document.querySelector("select[name='country']"),
    state: document.querySelector("select[name='state']"),
    town: document.querySelector("select[name='town']")
  };

  const typedInputs = {
    continent: document.querySelector("input[name='continent_text']"),
    country: document.querySelector("input[name='country_text']"),
    state: document.querySelector("input[name='state_text']"),
    town: document.querySelector("input[name='town_text']")
  };

  function isFilled(name) {
    const select = dropdowns[name];
    const typed = typedInputs[name];
    return (
      (select && select.value && select.value !== "None") ||
      (typed && typed.value.trim() !== "")
    );
  }

  function updateVisibleFields(scope) {
    Object.values(fields).forEach(div => div.style.display = "none");

    if (scope !== "global" && scope !== "") {
      fields.continent.style.display = "block";
    }
    if (scope === "country") {
      fields.country.style.display = "block";
    }
    if (scope === "state") {
      fields.country.style.display = "block";
      fields.state.style.display = "block";
    }
    if (scope === "town") {
      fields.country.style.display = "block";
      fields.state.style.display = "block";
      fields.town.style.display = "block";
    }
  }

  function updateDependencies() {
    const continentFilled = isFilled("continent");
    const countryFilled = isFilled("country");
    const stateFilled = isFilled("state");

    dropdowns.country.disabled = typedInputs.country.disabled = !continentFilled;
    dropdowns.state.disabled = typedInputs.state.disabled = !countryFilled;
    dropdowns.town.disabled = typedInputs.town.disabled = !stateFilled;
  }

  function toggleSubmitButton() {
    if (queryInput?.value.trim() === "") {
      submitButton.disabled = true;
      submitButton.classList.add("opacity-50", "cursor-not-allowed");
    } else {
      submitButton.disabled = false;
      submitButton.classList.remove("opacity-50", "cursor-not-allowed");
    }
  }

  function resetFormFieldsAfterSearch() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has("scope") || urlParams.has("query")) {
      form.reset();
      scopeSelect.value = "global";
      updateVisibleFields("global");
      updateDependencies();
      toggleSubmitButton();
    }
  }

  if (scopeSelect) {
    updateVisibleFields(scopeSelect.value);
    scopeSelect.addEventListener("change", e => {
      updateVisibleFields(e.target.value);
      updateDependencies(); // Update rules when changing scope
    });
  }

  if (form && queryInput && submitButton) {
    toggleSubmitButton();
    queryInput.addEventListener("input", toggleSubmitButton);
  }

  ["continent", "country", "state"].forEach(field => {
    const select = dropdowns[field];
    const typed = typedInputs[field];
    if (select) select.addEventListener("change", updateDependencies);
    if (typed) typed.addEventListener("input", updateDependencies);
  });

  updateDependencies();
  resetFormFieldsAfterSearch();
});
