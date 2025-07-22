document.addEventListener("DOMContentLoaded", () => {
  const scopeField = document.getElementById("id_availability_scope");

  function setFieldVisibilityAndReset(wrapperId, shouldShow) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    wrapper.style.display = shouldShow ? "block" : "none";

    if (!shouldShow) {
      // 👇 Find all form elements inside the wrapper and reset them
      const selects = wrapper.querySelectorAll("select");
      const inputs = wrapper.querySelectorAll("input");

      selects.forEach(select => {
        select.selectedIndex = 0; // Reset to first option
        select.value = ""; // Also reset value
        select.disabled = false; // Optional: re-enable in case it was locked
      });

      inputs.forEach(input => {
        input.value = "";
        input.disabled = false; // Optional: re-enable as well
      });
    }
  }

  function updateLocationFields() {
    const scope = scopeField?.value;
    if (!scope) return;

    const showTown = scope === "town";
    const showState = scope === "town" || scope === "state";
    const showCountry = ["town", "state", "country"].includes(scope);
    const showContinent = ["town", "state", "country", "continent"].includes(scope);

    setFieldVisibilityAndReset("location_field_continent", showContinent);
    setFieldVisibilityAndReset("location_field_country", showCountry);
    setFieldVisibilityAndReset("location_field_state", showState);
    setFieldVisibilityAndReset("location_field_town", showTown);
  }

  if (scopeField) {
    scopeField.addEventListener("change", updateLocationFields);
    updateLocationFields();
  }
});
