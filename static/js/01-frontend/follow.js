/**
 * Follow Button Handler
 * Handles AJAX follow/unfollow functionality with optimistic UI updates
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    selectors: {
      form: '.follow-form',
      button: '.follow-btn',
      wrapper: '.follow-button-wrapper',
      count: '.follow-count',
      countNumber: '.follow-count__number',
    },
    classes: {
      loading: 'is-loading',
      following: 'is-following',
    },
    animationDuration: 200,
  };

  /**
   * Get CSRF token from cookies
   */
  function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  /**
   * Update button state
   */
  function updateButtonState(button, isFollowing) {
    const followIcon = button.querySelector('.follow-btn__icon--follow');
    const followingIcon = button.querySelector('.follow-btn__icon--following');
    const followText = button.querySelector('.follow-btn__text--follow');
    const followingText = button.querySelector('.follow-btn__text--following');

    if (isFollowing) {
      button.classList.add(CONFIG.classes.following);
      button.setAttribute('data-following', 'true');
      button.setAttribute('aria-pressed', 'true');
      button.setAttribute('aria-label', button.getAttribute('aria-label').replace('Follow', 'Unfollow'));
      
      if (followIcon) followIcon.style.display = 'none';
      if (followingIcon) followingIcon.style.display = 'inline-flex';
      if (followText) followText.style.display = 'none';
      if (followingText) followingText.style.display = 'inline-block';
    } else {
      button.classList.remove(CONFIG.classes.following);
      button.setAttribute('data-following', 'false');
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', button.getAttribute('aria-label').replace('Unfollow', 'Follow'));
      
      if (followIcon) followIcon.style.display = 'inline-flex';
      if (followingIcon) followingIcon.style.display = 'none';
      if (followText) followText.style.display = 'inline-block';
      if (followingText) followingText.style.display = 'none';
    }
  }

  /**
   * Update follower count display
   */
  function updateFollowerCount(userId, count) {
    const countElements = document.querySelectorAll(
      `${CONFIG.selectors.count}[data-user-id="${userId}"] ${CONFIG.selectors.countNumber}`
    );
    
    countElements.forEach(el => {
      el.textContent = count;
      
      // Update label (follower vs followers)
      const label = el.nextElementSibling;
      if (label && label.classList.contains('follow-count__label')) {
        label.textContent = count === 1 ? 'follower' : 'followers';
      }
    });
  }

  /**
   * Show loading state
   */
  function setLoading(button, isLoading) {
    if (isLoading) {
      button.classList.add(CONFIG.classes.loading);
      button.disabled = true;
    } else {
      button.classList.remove(CONFIG.classes.loading);
      button.disabled = false;
    }
  }

  /**
   * Handle follow form submission
   */
  async function handleFollowSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const button = form.querySelector(CONFIG.selectors.button);
    const userId = form.getAttribute('data-user-id');
    const actionUrl = form.getAttribute('action');
    const currentlyFollowing = button.getAttribute('data-following') === 'true';

    // Optimistic UI update
    setLoading(button, true);
    
    try {
      const response = await fetch(actionUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Update button state
        updateButtonState(button, data.is_following);
        
        // Update follower count
        if (data.follower_count !== undefined) {
          updateFollowerCount(userId, data.follower_count);
        }
        
        // Update all buttons for the same user on the page
        updateAllButtonsForUser(userId, data.is_following);
        
        // Dispatch custom event for other components to listen to
        document.dispatchEvent(new CustomEvent('followStateChanged', {
          detail: {
            userId: userId,
            isFollowing: data.is_following,
            followerCount: data.follower_count,
            action: data.action,
          }
        }));
        
        // Show success feedback (optional toast notification)
        showToast(data.is_following ? 'Followed successfully' : 'Unfollowed successfully', 'success');
        
      } else {
        // Revert optimistic update on error
        console.error('Follow action failed:', data.error);
        showToast(data.error || 'Something went wrong', 'error');
      }
      
    } catch (error) {
      console.error('Network error:', error);
      showToast('Network error. Please try again.', 'error');
    } finally {
      setLoading(button, false);
    }
  }

  /**
   * Update all follow buttons for the same user
   * (In case there are multiple on the same page)
   */
  function updateAllButtonsForUser(userId, isFollowing) {
    const allButtons = document.querySelectorAll(
      `${CONFIG.selectors.button}[data-user-id="${userId}"]`
    );
    
    allButtons.forEach(button => {
      updateButtonState(button, isFollowing);
    });
  }

  /**
   * Simple toast notification (optional)
   */
  function showToast(message, type = 'info') {
    // Check if a toast container exists
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 8px;
        pointer-events: none;
      `;
      document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.style.cssText = `
      background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.3s ease;
      pointer-events: auto;
    `;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    });
    
    // Remove after delay
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-20px)';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  /**
   * Initialize follow buttons
   */
  function init() {
    // Attach event listeners to all follow forms
    document.querySelectorAll(CONFIG.selectors.form).forEach(form => {
      form.addEventListener('submit', handleFollowSubmit);
    });
    
    // Handle dynamically added forms (e.g., infinite scroll)
    document.addEventListener('DOMContentLoaded', () => {
      // Use event delegation for dynamically added content
      document.body.addEventListener('submit', (event) => {
        if (event.target.matches(CONFIG.selectors.form)) {
          handleFollowSubmit(event);
        }
      });
    });
    
    console.log('Follow button handler initialized');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for external use
  window.FollowHandler = {
    updateButtonState,
    updateFollowerCount,
    updateAllButtonsForUser,
  };

})();