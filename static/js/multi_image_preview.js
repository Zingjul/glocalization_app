// preview_handler.js
function attachPreviewListener(input, previewContainer) {
  input.addEventListener("change", (event) => {
    const files = Array.from(event.target.files);

    files.forEach((file, index) => {
      if (!(file.type.startsWith("image/") || file.type.startsWith("video/"))) {
        alert(`File "${file.name}" is not an image or video and will be ignored.`);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        // Wrapper for preview + delete button
        const wrapper = document.createElement("div");
        wrapper.className = "relative inline-block";

        let previewElement;
        if (file.type.startsWith("image/")) {
          previewElement = document.createElement("img");
          previewElement.src = e.target.result;
          previewElement.className = "w-28 h-28 object-cover rounded shadow border";
        } else {
          previewElement = document.createElement("video");
          previewElement.src = e.target.result;
          previewElement.className = "w-28 h-28 rounded shadow border";
          previewElement.controls = true;
        }

        // ❌ Delete button
        const deleteBtn = document.createElement("button");
        deleteBtn.innerHTML = "❌";
        deleteBtn.className =
          "absolute top-0 right-0 bg-red-600 text-white rounded-full px-1 text-xs";
        deleteBtn.type = "button";

        deleteBtn.addEventListener("click", () => {
          wrapper.remove();

          // Remove the file from the input
          const dataTransfer = new DataTransfer();
          Array.from(input.files)
            .filter((_, fileIndex) => fileIndex !== index)
            .forEach((f) => dataTransfer.items.add(f));
          input.files = dataTransfer.files;
        });

        wrapper.appendChild(previewElement);
        wrapper.appendChild(deleteBtn);
        previewContainer.appendChild(wrapper);
      };
      reader.readAsDataURL(file);
    });
  });
}
