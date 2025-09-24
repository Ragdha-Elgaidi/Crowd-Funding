/**
 * Form Validation Module
 * Handles client-side form validation and user feedback
 */

import { validateEgyptianPhone, debounce } from "../utils/helpers.js";

class FormValidator {
  constructor(form, options = {}) {
    this.form = typeof form === "string" ? document.querySelector(form) : form;
    this.options = {
      validateOnInput: true,
      validateOnBlur: true,
      showErrors: true,
      errorClass: "is-invalid",
      successClass: "is-valid",
      errorSelector: ".invalid-feedback",
      ...options,
    };

    this.validators = new Map();
    this.errors = new Map();

    if (this.form) {
      this.init();
    }
  }

  /**
   * Initialize form validation
   */
  init() {
    this.setupDefaultValidators();
    this.setupEventListeners();
    this.setupFormSubmission();
  }

  /**
   * Setup default validators
   */
  setupDefaultValidators() {
    // Required field validator
    this.addValidator(
      "required",
      (value, element) => {
        if (element.type === "checkbox" || element.type === "radio") {
          return element.checked;
        }
        return value && value.trim().length > 0;
      },
      "This field is required."
    );

    // Email validator
    this.addValidator(
      "email",
      (value) => {
        if (!value) return true; // Allow empty if not required
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
      },
      "Please enter a valid email address."
    );

    // Phone validator (Egyptian format)
    this.addValidator(
      "phone",
      (value) => {
        if (!value) return true; // Allow empty if not required
        return validateEgyptianPhone(value);
      },
      "Please enter a valid Egyptian phone number."
    );

    // Min length validator
    this.addValidator(
      "minlength",
      (value, element) => {
        if (!value) return true; // Allow empty if not required
        const minLength = parseInt(
          element.getAttribute("data-minlength") || element.minLength
        );
        return value.length >= minLength;
      },
      (element) => {
        const minLength = parseInt(
          element.getAttribute("data-minlength") || element.minLength
        );
        return `This field must be at least ${minLength} characters long.`;
      }
    );

    // Max length validator
    this.addValidator(
      "maxlength",
      (value, element) => {
        if (!value) return true; // Allow empty if not required
        const maxLength = parseInt(
          element.getAttribute("data-maxlength") || element.maxLength
        );
        return value.length <= maxLength;
      },
      (element) => {
        const maxLength = parseInt(
          element.getAttribute("data-maxlength") || element.maxLength
        );
        return `This field must not exceed ${maxLength} characters.`;
      }
    );

    // Pattern validator
    this.addValidator(
      "pattern",
      (value, element) => {
        if (!value) return true; // Allow empty if not required
        const pattern = element.getAttribute("pattern");
        if (!pattern) return true;
        const regex = new RegExp(pattern);
        return regex.test(value);
      },
      "Please match the requested format."
    );

    // Password strength validator
    this.addValidator(
      "password-strength",
      (value) => {
        if (!value) return true; // Allow empty if not required
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        const strongPasswordRegex =
          /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
        return strongPasswordRegex.test(value);
      },
      "Password must be at least 8 characters long and contain uppercase, lowercase, and number."
    );

    // Confirm password validator
    this.addValidator(
      "confirm-password",
      (value, element) => {
        const passwordField = this.form.querySelector("[data-password-field]");
        return passwordField ? value === passwordField.value : true;
      },
      "Passwords do not match."
    );

    // URL validator
    this.addValidator(
      "url",
      (value) => {
        if (!value) return true; // Allow empty if not required
        try {
          new URL(value);
          return true;
        } catch {
          return false;
        }
      },
      "Please enter a valid URL."
    );

    // Number validators
    this.addValidator(
      "number",
      (value) => {
        if (!value) return true; // Allow empty if not required
        return !isNaN(value) && !isNaN(parseFloat(value));
      },
      "Please enter a valid number."
    );

    this.addValidator(
      "min",
      (value, element) => {
        if (!value) return true; // Allow empty if not required
        const min = parseFloat(element.min);
        return isNaN(min) || parseFloat(value) >= min;
      },
      (element) => `Value must be at least ${element.min}.`
    );

    this.addValidator(
      "max",
      (value, element) => {
        if (!value) return true; // Allow empty if not required
        const max = parseFloat(element.max);
        return isNaN(max) || parseFloat(value) <= max;
      },
      (element) => `Value must not exceed ${element.max}.`
    );

    // Date validator
    this.addValidator(
      "date",
      (value) => {
        if (!value) return true; // Allow empty if not required
        const date = new Date(value);
        return !isNaN(date.getTime());
      },
      "Please enter a valid date."
    );

    // Future date validator
    this.addValidator(
      "future-date",
      (value) => {
        if (!value) return true; // Allow empty if not required
        const date = new Date(value);
        const now = new Date();
        return date > now;
      },
      "Date must be in the future."
    );

    // Past date validator
    this.addValidator(
      "past-date",
      (value) => {
        if (!value) return true; // Allow empty if not required
        const date = new Date(value);
        const now = new Date();
        return date < now;
      },
      "Date must be in the past."
    );
  }

  /**
   * Add custom validator
   * @param {string} name - Validator name
   * @param {Function} validator - Validator function
   * @param {string|Function} message - Error message or function returning message
   */
  addValidator(name, validator, message) {
    this.validators.set(name, { validator, message });
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    const inputs = this.form.querySelectorAll("input, textarea, select");

    inputs.forEach((input) => {
      if (this.options.validateOnInput) {
        const debouncedValidate = debounce(
          () => this.validateField(input),
          300
        );
        input.addEventListener("input", debouncedValidate);
      }

      if (this.options.validateOnBlur) {
        input.addEventListener("blur", () => this.validateField(input));
      }

      // Real-time password strength indicator
      if (
        input.type === "password" &&
        input.hasAttribute("data-show-strength")
      ) {
        input.addEventListener("input", () => this.showPasswordStrength(input));
      }

      // Confirm password real-time validation
      if (input.hasAttribute("data-confirm-password")) {
        const passwordField = this.form.querySelector("[data-password-field]");
        if (passwordField) {
          passwordField.addEventListener("input", () =>
            this.validateField(input)
          );
        }
      }
    });
  }

  /**
   * Setup form submission handling
   */
  setupFormSubmission() {
    this.form.addEventListener("submit", (e) => {
      const isValid = this.validateForm();

      if (!isValid) {
        e.preventDefault();
        this.focusFirstError();
      }
    });
  }

  /**
   * Validate entire form
   * @returns {boolean} Whether form is valid
   */
  validateForm() {
    const inputs = this.form.querySelectorAll("input, textarea, select");
    let isValid = true;

    this.errors.clear();

    inputs.forEach((input) => {
      if (!this.validateField(input, false)) {
        isValid = false;
      }
    });

    return isValid;
  }

  /**
   * Validate single field
   * @param {Element} field - Form field element
   * @param {boolean} showFeedback - Whether to show visual feedback
   * @returns {boolean} Whether field is valid
   */
  validateField(field, showFeedback = true) {
    const value = field.value;
    const validatorNames = this.getFieldValidators(field);

    this.clearFieldError(field);

    for (const validatorName of validatorNames) {
      const validator = this.validators.get(validatorName);
      if (!validator) continue;

      const isValid = validator.validator(value, field);

      if (!isValid) {
        const message =
          typeof validator.message === "function"
            ? validator.message(field)
            : validator.message;

        this.setFieldError(field, message);

        if (showFeedback && this.options.showErrors) {
          this.showFieldError(field, message);
        }

        return false;
      }
    }

    if (showFeedback && this.options.showErrors) {
      this.showFieldSuccess(field);
    }

    return true;
  }

  /**
   * Get validators for a field
   * @param {Element} field - Form field element
   * @returns {Array} Array of validator names
   */
  getFieldValidators(field) {
    const validators = [];

    // Check HTML5 validation attributes
    if (field.required) validators.push("required");
    if (field.type === "email") validators.push("email");
    if (field.type === "url") validators.push("url");
    if (field.type === "number") validators.push("number");
    if (field.type === "date") validators.push("date");
    if (field.minLength) validators.push("minlength");
    if (field.maxLength) validators.push("maxlength");
    if (field.min) validators.push("min");
    if (field.max) validators.push("max");
    if (field.pattern) validators.push("pattern");

    // Check custom data attributes
    if (field.hasAttribute("data-phone")) validators.push("phone");
    if (field.hasAttribute("data-password-strength"))
      validators.push("password-strength");
    if (field.hasAttribute("data-confirm-password"))
      validators.push("confirm-password");
    if (field.hasAttribute("data-future-date")) validators.push("future-date");
    if (field.hasAttribute("data-past-date")) validators.push("past-date");

    // Check data-validators attribute for custom validators
    const customValidators = field.getAttribute("data-validators");
    if (customValidators) {
      validators.push(...customValidators.split(",").map((v) => v.trim()));
    }

    return validators;
  }

  /**
   * Set field error
   * @param {Element} field - Form field element
   * @param {string} message - Error message
   */
  setFieldError(field, message) {
    this.errors.set(field.name || field.id, message);
  }

  /**
   * Clear field error
   * @param {Element} field - Form field element
   */
  clearFieldError(field) {
    this.errors.delete(field.name || field.id);
  }

  /**
   * Show field error visually
   * @param {Element} field - Form field element
   * @param {string} message - Error message
   */
  showFieldError(field, message) {
    field.classList.remove(this.options.successClass);
    field.classList.add(this.options.errorClass);

    const errorElement = this.getOrCreateErrorElement(field);
    errorElement.textContent = message;
    errorElement.style.display = "block";
  }

  /**
   * Show field success visually
   * @param {Element} field - Form field element
   */
  showFieldSuccess(field) {
    field.classList.remove(this.options.errorClass);
    field.classList.add(this.options.successClass);

    const errorElement = field.parentNode.querySelector(
      this.options.errorSelector
    );
    if (errorElement) {
      errorElement.style.display = "none";
    }
  }

  /**
   * Get or create error element for field
   * @param {Element} field - Form field element
   * @returns {Element} Error element
   */
  getOrCreateErrorElement(field) {
    let errorElement = field.parentNode.querySelector(
      this.options.errorSelector
    );

    if (!errorElement) {
      errorElement = document.createElement("div");
      errorElement.className = this.options.errorSelector.replace(".", "");
      field.parentNode.appendChild(errorElement);
    }

    return errorElement;
  }

  /**
   * Show password strength indicator
   * @param {Element} passwordField - Password input element
   */
  showPasswordStrength(passwordField) {
    const password = passwordField.value;
    let strength = 0;
    let message = "";

    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&]/.test(password)) strength++;

    const strengthLabels = ["Very Weak", "Weak", "Fair", "Good", "Strong"];
    const strengthColors = [
      "#ef4444",
      "#f59e0b",
      "#f59e0b",
      "#10b981",
      "#059669",
    ];

    message = strengthLabels[Math.min(strength - 1, 4)] || "Very Weak";

    let strengthElement =
      passwordField.parentNode.querySelector(".password-strength");
    if (!strengthElement) {
      strengthElement = document.createElement("div");
      strengthElement.className = "password-strength";
      strengthElement.innerHTML = `
                <div class="strength-bar">
                    <div class="strength-fill"></div>
                </div>
                <div class="strength-text"></div>
            `;
      passwordField.parentNode.appendChild(strengthElement);
    }

    const strengthFill = strengthElement.querySelector(".strength-fill");
    const strengthText = strengthElement.querySelector(".strength-text");

    strengthFill.style.width = `${(strength / 5) * 100}%`;
    strengthFill.style.backgroundColor =
      strengthColors[Math.min(strength - 1, 4)] || strengthColors[0];
    strengthText.textContent = message;
    strengthText.style.color =
      strengthColors[Math.min(strength - 1, 4)] || strengthColors[0];
  }

  /**
   * Focus first field with error
   */
  focusFirstError() {
    const firstErrorField = this.form.querySelector(
      `.${this.options.errorClass}`
    );
    if (firstErrorField) {
      firstErrorField.focus();
    }
  }

  /**
   * Get form errors
   * @returns {Map} Map of field errors
   */
  getErrors() {
    return new Map(this.errors);
  }

  /**
   * Clear all form validation states
   */
  clearValidation() {
    this.errors.clear();

    const fields = this.form.querySelectorAll("input, textarea, select");
    fields.forEach((field) => {
      field.classList.remove(
        this.options.errorClass,
        this.options.successClass
      );

      const errorElement = field.parentNode.querySelector(
        this.options.errorSelector
      );
      if (errorElement) {
        errorElement.style.display = "none";
      }
    });
  }

  /**
   * Destroy validator instance
   */
  destroy() {
    const inputs = this.form.querySelectorAll("input, textarea, select");
    inputs.forEach((input) => {
      input.removeEventListener("input", this.validateField);
      input.removeEventListener("blur", this.validateField);
    });

    this.form.removeEventListener("submit", this.validateForm);
  }
}

/**
 * Initialize form validation
 * @param {string|Element} form - Form selector or element
 * @param {Object} options - Validation options
 * @returns {FormValidator} Validator instance
 */
export default function initFormValidation(form, options = {}) {
  return new FormValidator(form, options);
}

// Auto-initialize forms with data-validate attribute
if (typeof window !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("[data-validate]");
    forms.forEach((form) => {
      new FormValidator(form);
    });
  });
}
