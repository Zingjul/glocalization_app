/* ================================================
   Form Controller - forms.js
   Professional form validation and UX
   ================================================ */

class FormController {
  constructor(formElement) {
    this.form = formElement;
    this.validators = new Map();
    this.init();
  }

  init() {
    if (!this.form) return;

    // Real-time validation
    this.form.addEventListener('input', (e) => {
      if (e.target.matches('input, textarea, select')) {
        this.validateField(e.target);
      }
    });

    // Submit handler
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (this.validateAll()) {
        this.submitForm();
      }
    });

    // Auto-save draft feature
    this.initAutoSave();
  }

  validateField(field) {
    const rules = field.dataset.validate?.split(' ') || [];
    let isValid = true;
    let errorMessage = '';

    rules.forEach(rule => {
      switch(rule) {
        case 'required':
          if (!field.value.trim()) {
            isValid = false;
            errorMessage = 'This field is required';
          }
          break;
        case 'email':
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email';
          }
          break;
        // Add more validators
      }
    });

    this.showFieldFeedback(field, isValid, errorMessage);
    return isValid;
  }

  showFieldFeedback(field, isValid, message) {
    // Remove existing feedback
    const existing = field.parentElement.querySelector('.field-feedback');
    if (existing) existing.remove();

    if (!isValid) {
      const feedback = document.createElement('div');
      feedback.className = 'field-feedback error animate-in';
      feedback.textContent = message;
      field.parentElement.appendChild(feedback);
      field.classList.add('error');
    } else {
      field.classList.remove('error');
      field.classList.add('success');
    }
  }

  async submitForm() {
    // Show loading state
    const submitBtn = this.form.querySelector('[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Processing...';

    try {
      const formData = new FormData(this.form);
      const response = await fetch(this.form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      const data = await response.json();
      
      if (data.success) {
        this.showSuccessMessage(data.message);
        this.form.reset();
      } else {
        this.showErrorMessage(data.error);
      }
    } catch (error) {
      this.showErrorMessage('An error occurred. Please try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  }

  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }
}