document.addEventListener("DOMContentLoaded", () => {
  const previewContainer = document.getElementById("imagePreviewContainer");

  for (let i = 1; i <= 6; i++) {
    const input = document.getElementById(`id_image${i}`);
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
});
