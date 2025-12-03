document.addEventListener("DOMContentLoaded", () => {
  fetch("/notifications/api/?unread=true")
    .then((response) => response.json())
    .then((data) => {
      const list = document.getElementById("notifications-list");
      list.innerHTML = "";

      if (!data || data.length === 0) {
        const empty = document.createElement("li");
        empty.className = "list-group-item text-muted";
        empty.textContent = "No new notifications";
        list.appendChild(empty);
        return;
      }

      data.forEach((n) => {
        const li = document.createElement("li");
        li.className = `list-group-item ${n.read ? "" : "fw-bold"}`;

        // Clean actor and verb
        const actor =
          n.actor && typeof n.actor === "string" && n.actor !== "null"
            ? n.actor
            : "";
        const verb =
          n.verb && typeof n.verb === "string"
            ? n.verb.replace(/^\d+|\bnull\b/gi, "").trim()
            : "";

        // Optional target title
        const target = n.extra?.post_title || n.target_content_type || "";

        // Optional timestamp
        const timestamp = n.created_at
          ? new Date(n.created_at).toLocaleString()
          : "";

        // Determine link (prefer `link`, fallback to `extra.link`)
        const targetUrl =
          (n.link && typeof n.link === "string" && n.link.trim()) ||
          (n.extra?.link && typeof n.extra.link === "string"
            ? n.extra.link.trim()
            : null);

        const content = `
          <div>
            <strong>${actor}</strong> ${verb}
            ${target ? `<span class="text-secondary">(${target})</span>` : ""}
            <div class="small text-muted">${timestamp}</div>
          </div>
        `;

        if (targetUrl) {
          const a = document.createElement("a");
          a.href = targetUrl;
          a.className = "text-decoration-none text-dark d-block";
          a.innerHTML = content;

          a.addEventListener("click", (event) => {
            event.preventDefault();

            // Mark notification as read before redirecting
            fetch(`/notifications/api/${n.id}/mark-read/`, {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
              },
              body: JSON.stringify({ read: true }),
            })
              .catch((err) =>
                console.warn(`Failed to mark notification ${n.id} as read:`, err)
              )
              .finally(() => {
                // Redirect after marking as read
                window.location.href = targetUrl;
              });
          });

          li.appendChild(a);
        } else {
          li.innerHTML = content;
        }

        list.appendChild(li);
      });
    })
    .catch((err) => {
      console.error("Error loading notifications:", err);
      const list = document.getElementById("notifications-list");
      list.innerHTML =
        '<li class="list-group-item text-danger">Failed to load notifications</li>';
    });
});
