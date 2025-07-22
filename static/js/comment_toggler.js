// comment-toggle.js

function toggleReplyForm(commentId) {
  const el = document.getElementById(`reply-form-${commentId}`);
  if (el) {
    el.classList.toggle("hidden");
  }
}
