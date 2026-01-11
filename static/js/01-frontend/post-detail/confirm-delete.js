// Delete Request Page Enhancements
document.addEventListener("DOMContentLoaded", () => {
  const deleteBtn = document.querySelector(".js-confirm-delete");

  if (deleteBtn) {
    deleteBtn.addEventListener("click", (e) => {
      const confirmed = confirm("⚠️ Are you absolutely sure? This action cannot be undone.");
      if (!confirmed) {
        e.preventDefault();
      }
    });
  }
});
