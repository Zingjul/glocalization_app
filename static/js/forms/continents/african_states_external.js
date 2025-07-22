// Map country names to their external fetch functions
const AfricanStateFetchers = {
    "Nigeria": function (stateSelectId = "id_post_state") {
        const stateSelect = document.getElementById(stateSelectId);
        if (!stateSelect) return;

        stateSelect.innerHTML = '<option value="">Loading Nigerian states...</option>';

        fetch("https://nga-states-lga.onrender.com/fetch")
            .then(res => res.json())
            .then(states => {
                stateSelect.innerHTML = '<option value="">Select a state</option>';
                states.forEach(state => {
                    const opt = document.createElement("option");
                    opt.value = state;
                    opt.textContent = state;
                    stateSelect.appendChild(opt);
                });
            })
            .catch(err => {
                console.error("Failed to load Nigerian states", err);
                stateSelect.innerHTML = '<option value="">Failed to load states</option>';
            });
    },

    // 🔜 Add more countries here
    // "Kenya": function (stateSelectId) { ... }
};
