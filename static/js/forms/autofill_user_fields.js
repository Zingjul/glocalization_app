// autofill_user_fields.js
document.addEventListener("DOMContentLoaded", () => {
    // Values will be injected by Django template context
    const userPhone = window.userPhone || "";
    const userEmail = window.userEmail || "";

    const phoneField = document.querySelector("#id_author_phone_number");
    const emailField = document.querySelector("#id_author_email");

    if (phoneField && !phoneField.value && userPhone) {
        phoneField.value = userPhone;
    }

    if (emailField && !emailField.value && userEmail) {
        emailField.value = userEmail;
    }
});
