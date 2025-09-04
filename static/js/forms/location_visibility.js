document.addEventListener("DOMContentLoaded", () => {
  const scopeField = document.getElementById("id_availability_scope");

  const SELECT_QUERIES = [
    "#location_field_continent select",
    "#location_field_country select",
    "#location_field_state select",
    "#location_field_town select",
  ];

  const getAllLocationSelects = () =>
    document.querySelectorAll(SELECT_QUERIES.join(", "));

  function resetToUnspecified(select) {
    // Just reset to DB's Unspecified (id=0)
    select.value = "0";
  }

  function setFieldVisibilityAndReset(wrapperId, shouldShow) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    wrapper.style.display = shouldShow ? "block" : "none";

    const selects = wrapper.querySelectorAll("select");
    const inputs = wrapper.querySelectorAll("input");

    if (!shouldShow) {
      // When hiding, force back to "Unspecified"
      selects.forEach(resetToUnspecified);
      inputs.forEach(input => { input.value = ""; });
      return;
    }

    // When showing, if nothing selected (or invalid), force "Unspecified"
    selects.forEach(select => {
      const hasCurrent =
        select.value &&
        select.querySelector(`option[value="${CSS.escape(select.value)}"]`);
      if (!hasCurrent) {
        select.value = "0";
      }
    });
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

  function initializeDefaults() {
    // On page load, force all location selects to "Unspecified"
    getAllLocationSelects().forEach(resetToUnspecified);

    // If options are populated later (via fetch), keep enforcing "Unspecified" if invalid
    getAllLocationSelects().forEach(select => {
      const observer = new MutationObserver(() => {
        if (
          !select.value ||
          !select.querySelector(`option[value="${CSS.escape(select.value)}"]`)
        ) {
          select.value = "0";
        }
      });
      observer.observe(select, { childList: true });
    });
  }

  if (scopeField) {
    initializeDefaults();   // ensure defaults at page load
    scopeField.addEventListener("change", updateLocationFields);
    updateLocationFields(); // ensure correct visibility & defaults on first render
  }
});
