document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');

  if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
      const confirmed = confirm('Are you sure you want to log out?');

      if (!confirmed) {
        // Redirect back to homepage or any other page
        window.location.href = '/';
        return;
      }

      fetch('/accounts/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
      })
      .then(response => {
        if (response.redirected) {
          window.location.href = response.url;
        } else {
          alert('Logout failed.');
        }
      })
      .catch(err => {
        console.error('Logout error:', err);
      });
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
