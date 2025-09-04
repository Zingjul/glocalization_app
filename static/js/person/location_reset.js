document.addEventListener("DOMContentLoaded", function () {
    const selects = [
        document.getElementById("id_continent"),
        document.getElementById("id_country"),
        document.getElementById("id_state"),
        document.getElementById("id_town")
    ];

    selects.forEach(select => {
        if (select) {
            select.value = "0"; // just reset to "Unspecified", don’t hide it
        }
    });
});
