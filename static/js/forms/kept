// location_visibility.js (updated)
// - Preserves original behavior for blank/create forms (force "Unspecified" = "0").
// - Does NOT clobber saved post / user profile values on edit pages.
// - Listens for option mutations and applies saved/user values when options arrive.

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
    try {
      select.value = "0";
    } catch (e) {
      // defensive
    }
  }

  // Determine logical level of a select element: 'continent'|'country'|'state'|'town' or null.
  function getLevelFromSelect(select) {
    const id = (select.id || "").toLowerCase();
    const name = (select.name || "").toLowerCase();

    if (id.includes("continent") || name.includes("continent")) return "continent";
    if (id.includes("country") || name.includes("country")) return "country";
    if (id.includes("state") || name.includes("state")) return "state";
    if (id.includes("town") || name.includes("town")) return "town";
    return null;
  }

  // Return the desired saved/user value for a logical level.
  function getDesiredValueForLevel(level) {
    switch (level) {
      case "continent":
        return (window.savedPostContinent || window.userContinent || "") + "";
      case "country":
        return (window.savedPostCountry || window.userCountry || "") + "";
      case "state":
        return (window.savedPostState || window.userState || "") + "";
      case "town":
        return (window.savedPostTown || window.userTown || "") + "";
      default:
        return "";
    }
  }

  // Try to apply the desired value for a select if the matching option exists.
  // Returns true if applied.
  function ensureSelectHasDesired(select) {
    const level = getLevelFromSelect(select);
    if (!level) return false;
    const desired = getDesiredValueForLevel(level);
    if (!desired) return false;

    // If option exists, set it.
    try {
      const opt = select.querySelector(`option[value="${CSS.escape(desired)}"]`);
      if (opt) {
        select.value = desired;
        return true;
      }
    } catch (e) {
      // If CSS.escape not supported or other error, fall back to safer search:
      const fallback = Array.from(select.options).find(o => String(o.value) === String(desired));
      if (fallback) {
        select.value = fallback.value;
        return true;
      }
    }
    return false;
  }

  // Show/hide wrapper and handle resets in a friendly way:
  function setFieldVisibilityAndReset(wrapperId, shouldShow) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    wrapper.style.display = shouldShow ? "block" : "none";

    const selects = wrapper.querySelectorAll("select");
    const inputs = wrapper.querySelectorAll("input");

    if (!shouldShow) {
      // When hiding, force back to "Unspecified" and clear typed inputs.
      selects.forEach(resetToUnspecified);
      inputs.forEach(input => { input.value = ""; });
      return;
    }

    // When showing, prefer applying any saved/user desired value if present.
    selects.forEach(select => {
      const applied = ensureSelectHasDesired(select);
      if (applied) return;

      // If no desired value OR desired option not yet present,
      // then only force "0" if the select has no valid current option.
      const currentValue = select.value;
      const currentHasOption =
        currentValue &&
        Boolean(select.querySelector(`option[value="${CSS.escape(currentValue)}"]`));

      if (!currentHasOption) {
        // Only force to "0" if there's no desired value for this level
        const level = getLevelFromSelect(select);
        const desired = level ? getDesiredValueForLevel(level) : "";
        if (!desired) {
          select.value = "0";
        }
        // If desired exists but option not yet present, leave it alone;
        // a MutationObserver (registered below) will apply desired when options arrive.
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
    // Detect if this page already has saved post values (edit) or profile defaults (create-fallback).
    const hasSavedOrUserValues = Boolean(
      window.savedPostContinent || window.savedPostCountry || window.savedPostState || window.savedPostTown ||
      window.userContinent || window.userCountry || window.userState || window.userTown
    );

    if (hasSavedOrUserValues) {
      // Do NOT forcibly reset selects to "0" — allow prefill logic to set desired values.
      // But attach MutationObservers so when options are added/changed we can:
      //  - apply the desired saved/user option if it appears, or
      //  - if there is no desired value, ensure select value is valid else set to "0".
      getAllLocationSelects().forEach(select => {
        // Try immediate apply if option already exists
        ensureSelectHasDesired(select);

        const observer = new MutationObserver((mutations) => {
          // On changes to options, try to apply desired value (if there is one)
          const applied = ensureSelectHasDesired(select);
          if (applied) return;

          // If no desired value for this level, make sure current value is valid; otherwise default to "0"
          const level = getLevelFromSelect(select);
          const desired = level ? getDesiredValueForLevel(level) : "";
          if (!desired) {
            const curr = select.value;
            const currHas = curr && Boolean(select.querySelector(`option[value="${CSS.escape(curr)}"]`));
            if (!currHas) {
              select.value = "0";
            }
          }
          // If desired exists but its option is still not present, do nothing — we wait for the desired option to appear.
        });

        observer.observe(select, { childList: true });
      });

      // Done — allow other code (prefill scripts) to run and set values.
      return;
    }

    // No saved/user values -> legacy behavior: force all selects to "Unspecified" now
    getAllLocationSelects().forEach(resetToUnspecified);

    // And attach observers to keep selects valid when options are populated later
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
    initializeDefaults();   // ensure defaults / observers on page load
    scopeField.addEventListener("change", updateLocationFields);
    updateLocationFields(); // ensure correct visibility & defaults on first render
  }
});
