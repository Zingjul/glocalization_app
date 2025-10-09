// static/js/location/auto_phone_code.js
document.addEventListener("DOMContentLoaded", function () {
  const countrySelect = document.querySelector("#id_country, #id_post_country");
  const phoneInput = document.querySelector("#id_phone_number, #id_author_phone_number");

  if (!countrySelect || !phoneInput) return;

  countrySelect.addEventListener("change", function () {
    const iso2 = this.value;
    if (!iso2) return;

    fetch(`/get-phone-code/?country_code=${iso2}`)
      .then((response) => response.json())
      .then((data) => {
        const code = data.phone_code || "";
        if (code && !phoneInput.value.startsWith(code)) {
          phoneInput.value = code + " ";
        }
      })
      .catch((err) => console.error("Error fetching phone code:", err));
  });
});
