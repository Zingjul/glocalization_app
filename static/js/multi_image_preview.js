document.addEventListener("DOMContentLoaded", () => {
  for (let i = 1; i <= 6; i++) {
    console.log("multiimgpreviewer is working alright");
    const input = document.querySelector(`input[name="image${i}"]`);
    if (input) {
      input.addEventListener("change", (event) => {
        const file = event.target.files[0];
        const previewContainer = document.getElementById("newImagePreviewContainer");
        const previewId = `preview-image${i}`;

        const existingPreview = document.getElementById(previewId);
        if (existingPreview) {
          existingPreview.remove(); // Remove only that preview
        }

        if (file && previewContainer) {
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
