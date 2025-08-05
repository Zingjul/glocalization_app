// document.addEventListener("DOMContentLoaded", () => {
document.addEventListener("change", () => {
  const locationOrder = ["continent", "country", "state", "town"];

  const dropdowns = {
    continent: document.getElementById("id_post_continent"),
    country: document.getElementById("id_post_country"),
    state: document.getElementById("id_post_state"),
    town: document.getElementById("id_post_town")
  };

  const typedInputs = {
    continent: null,
    country: null,
    state: null,
    town: document.getElementById("id_post_town_input")
  };

  // function isFilled(name) {
  //   const dropdown = dropdowns[name];
  //   const input = typedInputs[name];

  //   const dropdownFilled =
  //     dropdown && dropdown.value && dropdown.value.trim() !== "" && dropdown.value !== "None";
  //   const inputFilled =
  //     input && input.value.trim() !== "";

  //   return dropdownFilled || inputFilled;
  // }

  function isFilled(name) {
    const dropdown = dropdowns[name];
    const input = typedInputs[name];

    const dropdownFilled = dropdown && dropdown.value && dropdown.value.trim() !== "" && dropdown.value !== "None";
    const inputFilled = input ? input.value.trim() !== "" : false;

    return dropdownFilled || inputFilled;
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
    setEnabled("continent", true); // always enable first field
    for (let i = 1; i < locationOrder.length; i++) {
      const prev = locationOrder[i - 1];
      const current = locationOrder[i];
      const unlock = isFilled(prev);
      setEnabled(current, unlock);
    }
  }

  locationOrder.forEach(name => {
    const dropdown = dropdowns[name];
    const input = typedInputs[name];
    // console.log(`🧩 ${name} filled:`, isFilled(name));
    if (dropdown) dropdown.addEventListener("change", updateFieldAvailability);
    if (input) input.addEventListener("change", updateFieldAvailability);
  });

  // Run on load
  updateFieldAvailability();
});
