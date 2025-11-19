//location_dropdown.js
document.addEventListener("DOMContentLoaded", () => {
    const $ = id => document.getElementById(id);

    const continentSelect = $("id_post_continent");
    const countrySelect   = $("id_post_country");
    const stateSelect     = $("id_post_state");
    const townSelect      = $("id_post_town");

    if (!continentSelect || !countrySelect || !stateSelect || !townSelect) {
        return;
    }

    // --- Helper functions ---
    function clearSelect(select) {
        select.innerHTML = "";
    }

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

    const ctrls = {
        country: new AbortController(),
        state: new AbortController(),
        town: new AbortController(),
    };

    async function fetchList(level, parentId) {
        const urls = {
            country: `/api/countries/?continent_id=${encodeURIComponent(parentId)}`,
            state: `/api/states/?country_id=${encodeURIComponent(parentId)}`,
            town: `/api/towns/?state_id=${encodeURIComponent(parentId)}`
        };

        ctrls[level].abort();
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
        fillOptions(countrySelect, []);
        fillOptions(stateSelect, []);
        fillOptions(townSelect, []);
        if (!continentId) return;

        const countries = await fetchList("country", continentId);
        fillOptions(countrySelect, countries);
    });

    countrySelect.addEventListener("change", async function() {
        const countryId = this.value;
        fillOptions(stateSelect, []);
        fillOptions(townSelect, []);
        if (!countryId) return;

        const states = await fetchList("state", countryId);
        fillOptions(stateSelect, states);
    });

    stateSelect.addEventListener("change", async function() {
        const stateId = this.value;
        fillOptions(townSelect, []);
        if (!stateId) return;

        const towns = await fetchList("town", stateId);
        fillOptions(townSelect, towns);
    });

    // --- NEW: Auto-populate from profile values ---
    async function autoPopulateFromProfile() {
        const continentId = window.userContinent || "";
        const countryId   = window.userCountry   || "";
        const stateId     = window.userState     || "";
        const townId      = window.userTown      || "";

        if (continentId) {
            continentSelect.value = continentId;

            const countries = await fetchList("country", continentId);
            fillOptions(countrySelect, countries);
            if (countryId) countrySelect.value = countryId;

            if (countryId) {
                const states = await fetchList("state", countryId);
                fillOptions(stateSelect, states);
                if (stateId) stateSelect.value = stateId;

                if (stateId) {
                    const towns = await fetchList("town", stateId);
                    fillOptions(townSelect, towns);
                    if (townId) townSelect.value = townId;
                }
            }
        }
    }

    // --- Initial setup on page load ---
    autoPopulateFromProfile().then(() => {
        [continentSelect, countrySelect, stateSelect, townSelect].forEach(s => {
            if (!s.value && s.options.length > 0) {
                s.selectedIndex = 0;
            }
        });
    });
});
