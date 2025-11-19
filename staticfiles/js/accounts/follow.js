// document.addEventListener("DOMContentLoaded", () => {
//     document.querySelectorAll(".follow-btn").forEach(button => {
//         button.addEventListener("click", function () {
//             const userId = this.dataset.userId;

//             fetch(`/accounts/follow/${userId}/`, {
//                 method: "POST",
//                 headers: {
//                     "X-CSRFToken": getCookie("csrftoken"),
//                     "X-Requested-With": "XMLHttpRequest",
//                 },
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.error) {
//                     alert(data.error);
//                     return;
//                 }

//                 // Update button text
//                 this.textContent = (data.action === "followed") ? "Unfollow" : "Follow";

//                 // Update follower count
//                 const countSpan = document.getElementById(`followers-${userId}`);
//                 if (countSpan) {
//                     countSpan.textContent = data.follower_count;
//                 }
//             })
//             .catch(err => console.error("Error:", err));
//         });
//     });
// });

// // ✅ Helper to get CSRF token
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== "") {
//         const cookies = document.cookie.split(";");
//         for (let cookie of cookies) {
//             cookie = cookie.trim();
//             if (cookie.startsWith(name + "=")) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
