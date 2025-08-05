document.addEventListener("DOMContentLoaded", function() {
    $(".location-input").on("keyup", function () {
        let inputField = $(this);
        let searchTerm = inputField.val();
        let fieldName = inputField.attr("name").replace("_text", "");  // Extract field name

        $.get(`/search/autocomplete/?field=${fieldName}&query=${searchTerm}`, function (data) {
            let suggestions = data.suggestions;
            inputField.autocomplete({ source: suggestions });
        });
    });
});
