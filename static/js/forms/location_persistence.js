document.addEventListener("DOMContentLoaded", () => {
    const $ = id => document.getElementById(id);

    const scopeSelect      = $("id_availability_scope");
    const continentSelect  = $("id_post_continent");
    const countrySelect    = $("id_post_country");
    const stateSelect      = $("id_post_state");
    const townSelect       = $("id_post_town");

    if (!scopeSelect || !continentSelect || !countrySelect || !stateSelect || !townSelect) {
        console.warn("⚠️ Some location dropdowns or scope field not found. Skipping location persistence setup.");
        return;
    }

    const STORAGE_KEYS = {
        scope: "user_scope",
        continent: "user_continent",
        country: "user_country",
        state: "user_state",
        town: "user_town"
    };

    // --- Save selection changes persistently ---
    function saveSelection(key, value) {
        if (value !== undefined && value !== null) {
            localStorage.setItem(key, value);
        }
    }

    // --- Load selection from localStorage ---
    function getSelection(key) {
        return localStorage.getItem(key) || "0"; // "0" = Unspecified
    }

    // --- Clear all stored selections (optional reset) ---
    function clearSelections() {
        Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
    }

    // --- Restore saved selections on load ---
    async function restoreSelections() {
        const savedScope      = getSelection(STORAGE_KEYS.scope);
        const savedContinent  = getSelection(STORAGE_KEYS.continent);
        const savedCountry    = getSelection(STORAGE_KEYS.country);
        const savedState      = getSelection(STORAGE_KEYS.state);
        const savedTown       = getSelection(STORAGE_KEYS.town);

        // Restore scope first
        if (scopeSelect && savedScope !== "0") {
            scopeSelect.value = savedScope;
            scopeSelect.dispatchEvent(new Event("change"));
        }

        // Helper that waits until select has an option matching value
        function waitForOption(select, value, timeout = 5000) {
            return new Promise((resolve) => {
                const start = Date.now();
                const interval = setInterval(() => {
                    const ready = Array.from(select.options).some(opt => opt.value === value);
                    if (ready || Date.now() - start > timeout) {
                        clearInterval(interval);
                        resolve(ready);
                    }
                }, 150);
            });
        }

        // Restore continent
        if (continentSelect && savedContinent !== "0") {
            continentSelect.value = savedContinent;
            continentSelect.dispatchEvent(new Event("change"));
            await waitForOption(countrySelect, savedCountry);
        }

        // Restore country
        if (countrySelect && savedCountry !== "0") {
            countrySelect.value = savedCountry;
            countrySelect.dispatchEvent(new Event("change"));
            await waitForOption(stateSelect, savedState);
        }

        // Restore state
        if (stateSelect && savedState !== "0") {
            stateSelect.value = savedState;
            stateSelect.dispatchEvent(new Event("change"));
            await waitForOption(townSelect, savedTown);
        }

        // Restore town
        if (townSelect && savedTown !== "0") {
            townSelect.value = savedTown;
            townSelect.dispatchEvent(new Event("change"));
        }
    }

    // --- Handle changes and persist them ---
    scopeSelect.addEventListener("change", () => {
        const scopeVal = scopeSelect.value || "0";
        saveSelection(STORAGE_KEYS.scope, scopeVal);

        // Handle visibility-dependent resets
        // Any hidden field = reset to "Unspecified" (0)
        [continentSelect, countrySelect, stateSelect, townSelect].forEach(select => {
            if (select.offsetParent === null) { // hidden by CSS or visibility logic
                select.value = "0";
                saveSelection(STORAGE_KEYS[select.id.replace("id_post_", "")], "0");
            }
        });
    });

    continentSelect.addEventListener("change", () => {
        saveSelection(STORAGE_KEYS.continent, continentSelect.value || "0");
        // Reset lower levels
        saveSelection(STORAGE_KEYS.country, "0");
        saveSelection(STORAGE_KEYS.state, "0");
        saveSelection(STORAGE_KEYS.town, "0");
    });

    countrySelect.addEventListener("change", () => {
        saveSelection(STORAGE_KEYS.country, countrySelect.value || "0");
        saveSelection(STORAGE_KEYS.state, "0");
        saveSelection(STORAGE_KEYS.town, "0");
    });

    stateSelect.addEventListener("change", () => {
        saveSelection(STORAGE_KEYS.state, stateSelect.value || "0");
        saveSelection(STORAGE_KEYS.town, "0");
    });

    townSelect.addEventListener("change", () => {
        saveSelection(STORAGE_KEYS.town, townSelect.value || "0");
    });

    // --- Initialize restore on load ---
    restoreSelections();
});
