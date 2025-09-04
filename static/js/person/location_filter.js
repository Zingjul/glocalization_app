document.addEventListener("DOMContentLoaded", function () {
    const continentSelect = document.getElementById("id_continent");
    const countrySelect   = document.getElementById("id_country");
    const stateSelect     = document.getElementById("id_state");
    const townSelect      = document.getElementById("id_town");

    // Backup all options on load
    const countryOptions = [...countrySelect.options];
    const stateOptions   = [...stateSelect.options];
    const townOptions    = [...townSelect.options];

    function filterOptions(select, options, parentField, parentValue) {
        // Always preserve the "Unspecified" option first
        const unspecified = options.find(opt => opt.value === "0");

        select.innerHTML = ""; // clear all
        if (unspecified) {
            select.appendChild(unspecified.cloneNode(true));
        }

        options.forEach(opt => {
            if (opt.value !== "0" && opt.dataset[parentField] === parentValue) {
                select.appendChild(opt.cloneNode(true));
            }
        });

        // Default back to Unspecified
        select.value = "0";
    }

    continentSelect.addEventListener("change", function () {
        filterOptions(countrySelect, countryOptions, "continent", this.value);
        filterOptions(stateSelect, stateOptions, "country", "0");
        filterOptions(townSelect, townOptions, "state", "0");
    });

    countrySelect.addEventListener("change", function () {
        filterOptions(stateSelect, stateOptions, "country", this.value);
        filterOptions(townSelect, townOptions, "state", "0");
    });

    stateSelect.addEventListener("change", function () {
        filterOptions(townSelect, townOptions, "state", this.value);
    });
});
