document.addEventListener("DOMContentLoaded", function () {
    const continentSelect = document.getElementById("id_post_continent");
    const countrySelect = document.getElementById("id_post_country");
    const stateSelect = document.getElementById("id_post_state");
    const townSelect = document.getElementById("id_post_town");

    function clearDropdown(select) {
        select.innerHTML = '<option value="">Select an option</option>';
    }

    function fetchLocations(level, parentId) {
        const endpoints = {
            country: `/api/countries/?continent_id=${parentId}`,
            state: `/api/states/?country_id=${parentId}`,
            town: `/api/towns/?state_id=${parentId}`,
        };
        console.log("📡 Fetching:", endpoints[level]);
        return fetch(endpoints[level])
            .then(res => res.json())
            .catch(err => {
                console.error("Fetch failed:", err);
                return [];
            });
    }



    continentSelect?.addEventListener("change", function () {
        clearDropdown(countrySelect);
        clearDropdown(stateSelect);
        clearDropdown(townSelect);

        const continentId = this.value;
        if (continentId) {
            fetchLocations("country", continentId).then(countries => {
                countries.forEach(country => {
                    const opt = document.createElement("option");
                    opt.value = country.id;
                    opt.textContent = country.name;
                    countrySelect.appendChild(opt);
                });
            });
        }
    });

    countrySelect?.addEventListener("change", function () {
        clearDropdown(stateSelect);
        clearDropdown(townSelect);

        const countryId = this.value;
        console.log("this is console, country id: ", countryId)
        const selectedCountryName = this.options[this.selectedIndex].text;

        if (AfricanStateFetchers[selectedCountryName]) {
            AfricanStateFetchers[selectedCountryName](); // external source
        } else if (countryId) {
            fetchLocations("state", countryId).then(states => {
                states.forEach(state => {
                    const opt = document.createElement("option");
                    opt.value = state.id;
                    opt.textContent = state.name;
                    stateSelect.appendChild(opt);
                });
            });
        }
    });
    
    stateSelect?.addEventListener("change", function () {
        clearDropdown(townSelect);

        const stateId = this.value;
        if (stateId) {
            fetchLocations("town", stateId).then(towns => {
                towns.forEach(town => {
                    const opt = document.createElement("option");
                    opt.value = town.id;
                    opt.textContent = town.name;
                    townSelect.appendChild(opt);
                });
            });
        }
    });
});
