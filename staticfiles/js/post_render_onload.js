//post_render_onload.js
window.addEventListener("load", () => {
  const postContainer = document.getElementById("postContainer");
  if (postContainer) {
    postContainer.style.display = "block";
  }
});
