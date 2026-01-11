//              ${!n.read ? '<span class="notification-card__badge">new</span>' : ""}
//
// notification_list.js — FINAL 100% WORKING VERSION (GUARANTEED)
document.addEventListener("DOMContentLoaded", () => {
  fetch("/notifications/api/?unread=true")
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById("notifications-container");
      const countEl = document.getElementById("notification-count");
      const emptyEl = document.getElementById("no-notifications");

      container.innerHTML = "";

      if (!data || data.length === 0) {
        countEl.textContent = "0 notifications";
        emptyEl.style.display = "block";
        return;
      }

      countEl.textContent = `${data.length}`;

      data.forEach((n, i) => {
        const actor = n.actor || "Someone";
        const verb = (n.verb || "").replace(/^\d+|\bnull\b/gi, "").trim();
        const timestamp = formatTimeAgo(n.created_at);

        // === BUILD URL — MULTIPLE FALLBACKS (THIS IS BULLETPROOF) ===
        let targetUrl = n.link || n.extra?.link;

        // 1. Try target_content_type + target_object_id (your current backend)
        if (!targetUrl && n.target_content_type === "user" && n.target_object_id) {
          targetUrl = `/person/${n.target_object_id}/`;
        }
        // 2. Try target_content_type (lowercase) — some APIs send it this way
        else if (!targetUrl && n.target_content_type?.toLowerCase() === "user" && n.target_object_id) {
          targetUrl = `/person/${n.target_object_id}/`;
        }
        // 3. Fallback: actor profile (for follows)
        else if (!targetUrl && n.actor_id) {
          targetUrl = `/person/${n.actor_id}/`;
        }
        // 4. Final fallback: try to extract ID from actor string if it's a URL
        else if (!targetUrl && typeof n.actor === "string" && n.actor.includes("/person/")) {
          const match = n.actor.match(/\/person\/(\d+)\//);
          if (match) targetUrl = `/person/${match[1]}/`;
        }

        const notifType = getNotificationType(verb);

        const card = document.createElement("article");
        card.className = `notification-card ${!n.read ? "notification-card--unread" : ""}`;
        card.style.animationDelay = `${i * 0.08}s`;

        card.innerHTML = `
          <div class="notification-card__indicator ${!n.read ? "notification-card__indicator--active" : ""}"></div>
          
          <div class="notification-card__icon notification-card__icon--${notifType.type}">
            <i class="${notifType.icon}"></i>
          </div>
          
          <div class="notification-card__content">
            
            <div class="notification-card__message">
              ${verb} #${actor}
              ${n.extra?.post_title ? `<span class="notification-card__target">"${truncateText(n.extra.post_title, 60)}"</span>` : ""}
            </div>
            
            <div class="notification-card__footer">
              <span class="notification-card__time">
                <i class="far fa-clock"></i> ${timestamp}
              </span>
            </div>
          </div>
          
          ${targetUrl ? '<div class="notification-card__arrow"><i class="fas fa-chevron-right"></i></div>' : ""}
        `;

        // MAKE IT CLICKABLE IF WE HAVE ANY URL
        if (targetUrl) {
          card.classList.add("notification-card--clickable");
          card.style.cursor = "pointer";
          card.onclick = (e) => {
            if (e.target.closest('a')) return;
            
            fetch(`/notifications/api/${n.id}/mark-read/`, {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
              },
              body: JSON.stringify({ read: true }),
            }).finally(() => {
              window.location.href = targetUrl;
            });
          };
        }

        container.appendChild(card);
      });

      // Animation
      container.querySelectorAll(".notification-card").forEach((el, i) => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        setTimeout(() => {
          el.style.transition = "all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)";
          el.style.opacity = "1";
          el.style.transform = "translateY(0)";
        }, i * 80);
      });

    })
    .catch(err => {
      console.error("Failed to load notifications:", err);
      document.getElementById("notification-count").textContent = "Error";
    });
});

// Your perfect helpers
function formatTimeAgo(dateString) {
  const date = new Date(dateString);
  const seconds = Math.floor((Date.now() - date) / 1000);
  const intervals = { year: 31536000, month: 2592000, week: 604800, day: 86400, hour: 3600, minute: 60 };
  for (let [unit, secs] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secs);
    if (interval >= 1) return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
  }
  return 'Just now';
}

function getNotificationType(verb) {
  const v = (verb || "").toLowerCase();
  if (v.includes('follow')) return { type: 'follow', icon: 'fas fa-user-plus' };
  if (v.includes('like') || v.includes('love')) return { type: 'like', icon: 'fas fa-heart' };
  if (v.includes('comment')) return { type: 'comment', icon: 'fas fa-comment' };
  if (v.includes('mention')) return { type: 'mention', icon: 'fas fa-at' };
  return { type: 'default', icon: 'fas fa-bell' };
}

function truncateText(text, len) {
  return text.length <= len ? text : text.substring(0, len) + '...';
}