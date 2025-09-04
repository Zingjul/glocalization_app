document.addEventListener("DOMContentLoaded", () => {
    const $ = id => document.getElementById(id);

    const continentSelect = $("id_post_continent");
    const countrySelect = $("id_post_country");
    const stateSelect = $("id_post_state");
    const townSelect = $("id_post_town");

    if (!continentSelect || !countrySelect || !stateSelect || !townSelect) {
        return;
    }

    // --- Helper functions ---

    /**
     * Resets a select element completely, clearing all its options.
     * @param {HTMLSelectElement} select The select element to clear.
     */
    function clearSelect(select) {
        select.innerHTML = "";
    }

    /**
     * Fills a select element with options from an array of items.
     * @param {HTMLSelectElement} select The select element to fill.
     * @param {Array<Object>} items The array of items, each with an 'id' and 'name' property.
     */
    function fillOptions(select, items) {
        clearSelect(select);
        const frag = document.createDocumentFragment();
        items.forEach(({ id, name }) => {
            const opt = document.createElement("option");
            opt.value = String(id);
            opt.textContent = name;
            frag.appendChild(opt);
        });
        select.appendChild(frag);
    }

    // Abort controllers to avoid race conditions and ensure only the latest request is processed.
    const ctrls = {
        country: new AbortController(),
        state: new AbortController(),
        town: new AbortController(),
    };

    /**
     * Fetches a list of locations from the API based on the parent ID.
     * @param {string} level The level to fetch ('country', 'state', or 'town').
     * @param {string|number} parentId The ID of the parent location.
     * @returns {Promise<Array<Object>>} A promise that resolves to an array of location objects.
     */
    async function fetchList(level, parentId) {
        const urls = {
            country: `/api/countries/?continent_id=${encodeURIComponent(parentId)}`,
            state: `/api/states/?country_id=${encodeURIComponent(parentId)}`,
            town: `/api/towns/?state_id=${encodeURIComponent(parentId)}`
        };

        ctrls[level].abort(); // Abort any previous fetch for this level
        ctrls[level] = new AbortController();

        try {
            console.log(`📡 Fetching [${level}]: ${urls[level]}`);
            const res = await fetch(urls[level], { signal: ctrls[level].signal });
            if (!res.ok) {
                throw new Error(`${res.status} ${res.statusText}`);
            }
            return await res.json();
        } catch (e) {
            if (e.name !== "AbortError") {
                console.error(`[${level}] fetch failed:`, e);
            }
            return [];
        }
    }

    // --- Event Handlers ---

    continentSelect.addEventListener("change", async function() {
        const continentId = this.value;
        fillOptions(countrySelect, []); // Reset subsequent dropdowns
        fillOptions(stateSelect, []);
        fillOptions(townSelect, []);
        if (!continentId) return;

        const countries = await fetchList("country", continentId);
        fillOptions(countrySelect, countries);
    });

    countrySelect.addEventListener("change", async function() {
        const countryId = this.value;
        fillOptions(stateSelect, []); // Reset subsequent dropdowns
        fillOptions(townSelect, []);
        if (!countryId) return;

        const states = await fetchList("state", countryId);
        fillOptions(stateSelect, states);
    });

    stateSelect.addEventListener("change", async function() {
        const stateId = this.value;
        fillOptions(townSelect, []); // Reset subsequent dropdown
        if (!stateId) return;

        const towns = await fetchList("town", stateId);
        fillOptions(townSelect, towns);
    });

    // --- Initial setup on page load ---

    // Ensure selects keep the value rendered by Django or fall back to the first option.
    [continentSelect, countrySelect, stateSelect, townSelect].forEach(s => {
        if (!s.value && s.options.length > 0) {
            s.selectedIndex = 0;
        }
    });
});