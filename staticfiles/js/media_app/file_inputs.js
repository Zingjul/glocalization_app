// file:///c%3A/Users/jshot/Desktop/folders/shepherd/tradesapp/glocalization_app/static/js/media_app/file_inputs.js
// file_inputs.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("fileinput working!");

  const container = document.getElementById("fileInputsContainer");
  const addMoreBtn = document.getElementById("addMoreBtn");
  const previewContainer = document.getElementById("newImagePreviewContainer");

  const firstInput = container.querySelector("#firstFileInput");

  // Always make sure the name is media_files[]
  firstInput.name = "media_files[]";

  // Attach preview listener to first input
  attachPreviewListener(firstInput, previewContainer);

  // Show "Add More" button after the first file input exists
  addMoreBtn.classList.remove("hidden");

  // Add new input on button click
  addMoreBtn.addEventListener("click", () => {
    const newInput = document.createElement("input");
    newInput.type = "file";
    newInput.name = "media_files[]"; // 🔑 all inputs use same array name
    newInput.multiple = true;
    newInput.accept = "image/*,video/*";
    newInput.className = "file-input mt-2";

    container.appendChild(newInput);
    attachPreviewListener(newInput, previewContainer);
  });
});

/**
 * Preview helper
 */
function attachPreviewListener(input, previewContainer) {
  input.addEventListener("change", () => {
    Array.from(input.files).forEach(file => {
      const reader = new FileReader();
      reader.onload = e => {
        let preview;
        if (file.type.startsWith("image/")) {
          preview = document.createElement("img");
          preview.src = e.target.result;
          preview.className = "w-24 h-24 object-cover rounded shadow";
        } else if (file.type.startsWith("video/")) {
          preview = document.createElement("video");
          preview.src = e.target.result;
          preview.controls = true;
          preview.className = "w-24 h-24 rounded shadow";
        }
        if (preview) previewContainer.appendChild(preview);
      };
      reader.readAsDataURL(file);
    });
  });
}
