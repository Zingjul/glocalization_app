function postFormHandler() {
    return {
        category: "",

        handleCategoryChange(event) {
            const categoryField = event.target.name === "category" ? event.target : document.querySelector('[name="category"]');
            if (categoryField) {
                this.category = categoryField.value;
            }
        },

        init() {
            const categoryField = document.querySelector('[name="category"]');
            if (categoryField) {
                this.category = categoryField.value;
            }
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
  const previewContainer = document.getElementById("imagePreviewContainer");

  for (let i = 1; i <= 6; i++) {
    const input = document.querySelector(`input[name="image${i}"]`);
    if (input) {
      input.addEventListener("change", (event) => {
        const file = event.target.files[0];
        const previewId = `preview-image${i}`;

        const existing = document.getElementById(previewId);
        if (existing) existing.remove();

        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            const img = document.createElement("img");
            img.id = previewId;
            img.src = e.target.result;
            img.className = "w-28 h-28 object-cover rounded shadow border";
            previewContainer.appendChild(img);
          };
          reader.readAsDataURL(file);
        }
      });
    }
  }

 // 🌍 Scope-aware location field toggling
  const scopeField = document.querySelector('[name="availability_scope"]');

  const townFields = [
    document.querySelector('[name="post_town"]'),
    document.querySelector('[name="post_town_input"]')
  ];
  const stateFields = [
    document.querySelector('[name="post_state"]'),
    document.querySelector('[name="post_state_input"]')
  ];
  const countryFields = [
    document.querySelector('[name="post_country"]'),
    document.querySelector('[name="post_country_input"]')
  ];
  const continentFields = [
    document.querySelector('[name="post_continent"]'),
    document.querySelector('[name="post_continent_input"]')
  ];

  const setFieldState = (fields, enabled) => {
    fields.forEach(field => {
      if (field) {
        field.disabled = !enabled;
        const wrapper = field.closest(".field-wrapper") || field.closest("div");
        if (wrapper) {
          wrapper.style.display = enabled ? "block" : "none";
        }
      }
    });
  };

  const updateLocationFields = () => {
    const scope = scopeField?.value;
    if (!scope) return;

    const showTown = scope === "town";
    const showState = scope === "town" || scope === "state";
    const showCountry = ["town", "state", "country"].includes(scope);
    const showContinent = ["town", "state", "country", "continent"].includes(scope);

    setFieldState(townFields, showTown);
    setFieldState(stateFields, showState);
    setFieldState(countryFields, showCountry);
    setFieldState(continentFields, showContinent);
  };
  if (scopeField) {
    scopeField.addEventListener("change", updateLocationFields);
    updateLocationFields(); // initial run
  }
});