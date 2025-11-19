// autofill_user_fields_location_editpage.js
// Prefill cascading selects (continent -> country -> state -> town).
// Priority: window.savedPost* (edit) -> window.user* (profile defaults).
// Works with location_dropdown.js (window.locationSelects.fetchList / fillOptions).

document.addEventListener("DOMContentLoaded", () => {
  if (!window.locationSelects) return;

  const {
    continentSelect,
    countrySelect,
    stateSelect,
    townSelect,
    fetchList,
    fillOptions
  } = window.locationSelects;

  // Prefer saved post values (edit), fallback to user profile values (create).
  function pickValue(saved, user) {
    // Treat empty string / null / undefined as "not present".
    if (saved !== undefined && saved !== null && String(saved).trim() !== "") {
      // Keep "0" as valid (Unspecified) if it's intentionally stored.
      return String(saved).trim();
    }
    if (user !== undefined && user !== null && String(user).trim() !== "") {
      return String(user).trim();
    }
    return "";
  }

  const desiredContinent = pickValue(window.savedPostContinent, window.userContinent);
  const desiredCountry   = pickValue(window.savedPostCountry,   window.userCountry);
  const desiredState     = pickValue(window.savedPostState,     window.userState);
  const desiredTown      = pickValue(window.savedPostTown,      window.userTown);

  // If nothing at all to prefill, nothing to do.
  if (!desiredContinent && !desiredCountry && !desiredState && !desiredTown) {
    return;
  }

  // Find option by exact value
  function findOption(select, value) {
    if (!select || value === "" || value == null) return null;
    const v = String(value);
    for (let i = 0; i < select.options.length; i++) {
      if (String(select.options[i].value) === v) return select.options[i];
    }
    return null;
  }

  // Wait for an option to appear in the select (useful when options are populated async).
  function waitForOption(select, value, timeout = 3000) {
    return new Promise((resolve) => {
      if (!select || value === "" || value == null) return resolve(false);
      if (findOption(select, value)) return resolve(true);

      let timer;
      const obs = new MutationObserver(() => {
        if (findOption(select, value)) {
          try { obs.disconnect(); } catch (e) {}
          if (timer) clearTimeout(timer);
          resolve(true);
        }
      });

      obs.observe(select, { childList: true });

      timer = setTimeout(() => {
        try { obs.disconnect(); } catch (e) {}
        resolve(false);
      }, timeout);
    });
  }

  // Attempt to set select to value if option exists or appears. Dispatch change event when set.
  async function applySelectionIfAvailable(select, value, wait = true) {
    if (!select || value === "" || value == null) return false;

    if (findOption(select, value)) {
      select.value = String(value);
      try { select.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
      return true;
    }

    if (wait) {
      const ok = await waitForOption(select, value, 3000);
      if (ok) {
        select.value = String(value);
        try { select.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
        return true;
      }
    }
    return false;
  }

  // Main prefill flow (runs once)
  (async () => {
    // small delay to let other scripts (wiring / observers) initialize
    await new Promise(res => setTimeout(res, 25));

    // --------- CONTINENT ----------
    if (desiredContinent) {
      await applySelectionIfAvailable(continentSelect, desiredContinent, true);
    }

    // --------- COUNTRIES ----------
    // Compute parent id to fetch countries for: prefer actual selected continent, else desiredContinent
    const continentUsed = (continentSelect && continentSelect.value) || desiredContinent || "";
    if (continentUsed) {
      try {
        const countries = await fetchList("country", continentUsed) || [];
        fillOptions(countrySelect, countries);
      } catch (e) {
        console.error("fetchList(country) failed:", e);
      }

      if (desiredCountry) {
        await applySelectionIfAvailable(countrySelect, desiredCountry, true);
      }
    } else {
      // No continent parent known: try to set desired country directly if present in existing options
      if (desiredCountry) {
        await applySelectionIfAvailable(countrySelect, desiredCountry, true);
      }
    }

    // --------- STATES ----------
    const countryUsed = (countrySelect && countrySelect.value) || desiredCountry || "";
    if (countryUsed) {
      try {
        const states = await fetchList("state", countryUsed) || [];
        fillOptions(stateSelect, states);
      } catch (e) {
        console.error("fetchList(state) failed:", e);
      }

      if (desiredState) {
        await applySelectionIfAvailable(stateSelect, desiredState, true);
      }
    } else {
      if (desiredState) {
        await applySelectionIfAvailable(stateSelect, desiredState, true);
      }
    }

    // --------- TOWNS ----------
    const stateUsed = (stateSelect && stateSelect.value) || desiredState || "";
    if (stateUsed) {
      try {
        const towns = await fetchList("town", stateUsed) || [];
        fillOptions(townSelect, towns);
      } catch (e) {
        console.error("fetchList(town) failed:", e);
      }

      if (desiredTown) {
        await applySelectionIfAvailable(townSelect, desiredTown, true);
      }
    } else {
      if (desiredTown) {
        await applySelectionIfAvailable(townSelect, desiredTown, true);
      }
    }

    // Final fallback: if selects are still empty but have options, pick the first option (graceful)
    [continentSelect, countrySelect, stateSelect, townSelect].forEach(s => {
      if (!s) return;
      try {
        if (!s.value && s.options && s.options.length > 0) {
          s.selectedIndex = 0;
          try { s.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
        }
      } catch (e) { /* ignore */ }
    });

    // debug
    console.log("Location prefill complete:", {
      continent: continentSelect?.value,
      country:   countrySelect?.value,
      state:     stateSelect?.value,
      town:      townSelect?.value,
    });
  })();
});
