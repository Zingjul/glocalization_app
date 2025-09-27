document.addEventListener("DOMContentLoaded", () => {
    fetch("/notifications/api/?unread=true")
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById("notifications-list");
            list.innerHTML = "";

            data.forEach(notification => {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.textContent = `${notification.actor} - ${notification.verb}`;
                list.appendChild(li);
            });
        })
        .catch(err => console.error("Error loading notifications:", err));
});
