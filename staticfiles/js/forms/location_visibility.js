// location_visibility.js
// Works with location_persistence.js and ensures that when
// fields are re-shown after a scope reset, they properly restore
// previous saved/user values or fall back to "Unspecified" (id=0).

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
    try {
      select.value = "0"; // DB Unspecified
    } catch (e) {}
  }

  function getLevelFromSelect(select) {
    const id = (select.id || "").toLowerCase();
    const name = (select.name || "").toLowerCase();
    if (id.includes("continent") || name.includes("continent")) return "continent";
    if (id.includes("country") || name.includes("country")) return "country";
    if (id.includes("state") || name.includes("state")) return "state";
    if (id.includes("town") || name.includes("town")) return "town";
    return null;
  }

  function getDesiredValueForLevel(level) {
    switch (level) {
      case "continent": return (window.savedPostContinent || window.userContinent || "") + "";
      case "country":   return (window.savedPostCountry || window.userCountry || "") + "";
      case "state":     return (window.savedPostState || window.userState || "") + "";
      case "town":      return (window.savedPostTown || window.userTown || "") + "";
      default:          return "";
    }
  }

  function ensureSelectHasDesired(select) {
    const level = getLevelFromSelect(select);
    if (!level) return false;
    const desired = getDesiredValueForLevel(level);
    if (!desired) return false;

    try {
      const opt = select.querySelector(`option[value="${CSS.escape(desired)}"]`);
      if (opt) {
        select.value = desired;
        return true;
      }
    } catch (e) {
      const fallback = Array.from(select.options).find(o => String(o.value) === String(desired));
      if (fallback) {
        select.value = fallback.value;
        return true;
      }
    }
    return false;
  }

  function setFieldVisibilityAndReset(wrapperId, shouldShow) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    wrapper.style.display = shouldShow ? "block" : "none";

    const selects = wrapper.querySelectorAll("select");
    const inputs = wrapper.querySelectorAll("input");

    if (!shouldShow) {
      selects.forEach(resetToUnspecified);
      inputs.forEach(input => { input.value = ""; });
      return;
    }

    // When showing again:
    selects.forEach(select => {
      const applied = ensureSelectHasDesired(select);
      if (applied) return;

      const currentValue = select.value;
      const hasCurrent = currentValue && Boolean(
        select.querySelector(`option[value="${CSS.escape(currentValue)}"]`)
      );

      if (!hasCurrent) {
        const level = getLevelFromSelect(select);
        const desired = level ? getDesiredValueForLevel(level) : "";
        if (!desired) select.value = "0";
      }
    });
  }

  function updateLocationFields() {
    const scope = scopeField?.value;
    if (!scope) return;

    const showTown = scope === "town";
    const showState = ["town", "state"].includes(scope);
    const showCountry = ["town", "state", "country"].includes(scope);
    const showContinent = ["town", "state", "country", "continent"].includes(scope);

    setFieldVisibilityAndReset("location_field_continent", showContinent);
    setFieldVisibilityAndReset("location_field_country", showCountry);
    setFieldVisibilityAndReset("location_field_state", showState);
    setFieldVisibilityAndReset("location_field_town", showTown);
  }

  function initializeDefaults() {
    const hasSavedOrUserValues = Boolean(
      window.savedPostContinent || window.savedPostCountry || window.savedPostState || window.savedPostTown ||
      window.userContinent || window.userCountry || window.userState || window.userTown
    );

    if (hasSavedOrUserValues) {
      getAllLocationSelects().forEach(select => {
        ensureSelectHasDesired(select);
        const observer = new MutationObserver(() => {
          const applied = ensureSelectHasDesired(select);
          if (applied) return;
          const level = getLevelFromSelect(select);
          const desired = level ? getDesiredValueForLevel(level) : "";
          if (!desired) {
            const curr = select.value;
            const currHas = curr && Boolean(select.querySelector(`option[value="${CSS.escape(curr)}"]`));
            if (!currHas) select.value = "0";
          }
        });
        observer.observe(select, { childList: true });
      });
      return;
    }

    // No saved values: default all to "0"
    getAllLocationSelects().forEach(resetToUnspecified);

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
    initializeDefaults();
    scopeField.addEventListener("change", updateLocationFields);
    updateLocationFields();
  }
});
