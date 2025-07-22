console.log("Town dropdown:", document.querySelector("select[name='post_town']"));
console.log("Town input:", document.querySelector("input[name='post_town_input']"));

document.addEventListener("DOMContentLoaded", () => {
  const locationOrder = ["continent", "country", "state", "town"];

  const dropdowns = {
    continent: document.querySelector("select[name='post_continent']"),
    country: document.querySelector("select[name='post_country']"),
    state: document.querySelector("select[name='post_state']"),
    town: document.querySelector("select[name='post_town']")
  };

  const typedInputs = {
    continent: document.querySelector("input[name='post_continent_input']"),
    country: document.querySelector("input[name='post_country_input']"),
    state: document.querySelector("input[name='post_state_input']"),
    town: document.querySelector("input[name='post_town_input']")
  };

  function isFilled(name) {
    const dropdown = dropdowns[name];
    const input = typedInputs[name];
    return (
      (dropdown && dropdown.value && dropdown.value !== "None") ||
      (input && input.value.trim() !== "")
    );
  }

  function setEnabled(name, enabled) {
    const dropdown = dropdowns[name];
    const input = typedInputs[name];

    if (dropdown) {
      dropdown.disabled = !enabled;
      if (enabled) dropdown.removeAttribute("disabled");
    }

    if (input) {
      input.disabled = !enabled;
      if (enabled) input.removeAttribute("disabled");
    }
  }

  function updateFieldAvailability() {
    // Start by enabling continent
    setEnabled("continent", true);

    for (let i = 1; i < locationOrder.length; i++) {
      const prevField = locationOrder[i - 1];
      const currentField = locationOrder[i];
      const canEnable = isFilled(prevField);
      setEnabled(currentField, canEnable);
    }
  }

  locationOrder.forEach(name => {
    if (dropdowns[name]) {
      dropdowns[name].addEventListener("change", updateFieldAvailability);
    }
    if (typedInputs[name]) {
      typedInputs[name].addEventListener("input", updateFieldAvailability);
    }
  });

  // Run once on page load
  updateFieldAvailability();
});
