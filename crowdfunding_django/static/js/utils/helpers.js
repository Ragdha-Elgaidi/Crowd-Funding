/**
 * Utility Functions Module
 * Common utility functions used across the application
 */

/**
 * Get CSRF token from DOM
 * @returns {string} CSRF token
 */
export function getCSRFToken() {
  const token = document.querySelector("[name=csrfmiddlewaretoken]");
  return token ? token.value : "";
}

/**
 * Get CSRF token from cookies
 * @returns {string} CSRF token from cookies
 */
export function getCSRFTokenFromCookie() {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
  return cookieValue || "";
}

/**
 * Set up CSRF token for AJAX requests
 */
export function setupCSRF() {
  const token = getCSRFToken() || getCSRFTokenFromCookie();

  if (window.jQuery) {
    // Setup jQuery AJAX defaults
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (
          !(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))
        ) {
          xhr.setRequestHeader("X-CSRFToken", token);
        }
      },
    });
  }

  return token;
}

/**
 * Debounce function to limit function execution frequency
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - Execute immediately on first call
 * @returns {Function} Debounced function
 */
export function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * Throttle function to limit function execution frequency
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Check if element is in viewport
 * @param {Element} element - DOM element to check
 * @returns {boolean} Whether element is in viewport
 */
export function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <=
      (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

/**
 * Smooth scroll to element
 * @param {string|Element} target - CSS selector or DOM element
 * @param {number} offset - Offset from top in pixels
 */
export function scrollToElement(target, offset = 0) {
  const element =
    typeof target === "string" ? document.querySelector(target) : target;
  if (element) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth",
    });
  }
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: EGP)
 * @param {string} locale - Locale (default: ar-EG)
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currency = "EGP", locale = "ar-EG") {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format date
 * @param {Date|string} date - Date to format
 * @param {string} locale - Locale (default: ar-EG)
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(date, locale = "ar-EG", options = {}) {
  const defaultOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  const dateObj = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat(locale, {
    ...defaultOptions,
    ...options,
  }).format(dateObj);
}

/**
 * Generate unique ID
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
export function generateId(prefix = "id") {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      textArea.style.top = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand("copy");
      textArea.remove();
      return result;
    }
  } catch (error) {
    console.error("Failed to copy text: ", error);
    return false;
  }
}

/**
 * Local storage wrapper with error handling
 */
export const storage = {
  /**
   * Get item from localStorage
   * @param {string} key - Storage key
   * @param {*} defaultValue - Default value if key doesn't exist
   * @returns {*} Stored value or default
   */
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      return defaultValue;
    }
  },

  /**
   * Set item in localStorage
   * @param {string} key - Storage key
   * @param {*} value - Value to store
   * @returns {boolean} Success status
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error("Error writing to localStorage:", error);
      return false;
    }
  },

  /**
   * Remove item from localStorage
   * @param {string} key - Storage key
   * @returns {boolean} Success status
   */
  remove(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error("Error removing from localStorage:", error);
      return false;
    }
  },

  /**
   * Clear all localStorage
   * @returns {boolean} Success status
   */
  clear() {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error("Error clearing localStorage:", error);
      return false;
    }
  },
};

/**
 * HTTP request wrapper
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @returns {Promise<Response>} Fetch response
 */
export async function request(url, options = {}) {
  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken() || getCSRFTokenFromCookie(),
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error("Request failed:", error);
    throw error;
  }
}

/**
 * Show loading state on element
 * @param {Element} element - Target element
 * @param {string} text - Loading text
 */
export function showLoading(element, text = "Loading...") {
  element.disabled = true;
  element.classList.add("btn-loading");
  element.dataset.originalText = element.textContent;
  element.textContent = text;
}

/**
 * Hide loading state on element
 * @param {Element} element - Target element
 */
export function hideLoading(element) {
  element.disabled = false;
  element.classList.remove("btn-loading");
  if (element.dataset.originalText) {
    element.textContent = element.dataset.originalText;
    delete element.dataset.originalText;
  }
}

/**
 * Validate Egyptian phone number
 * @param {string} phone - Phone number to validate
 * @returns {boolean} Whether phone number is valid
 */
export function validateEgyptianPhone(phone) {
  const phoneRegex = /^(\+201|01|1)[0-9]{9}$/;
  return phoneRegex.test(phone);
}

/**
 * Format Egyptian phone number
 * @param {string} phone - Phone number to format
 * @returns {string} Formatted phone number
 */
export function formatEgyptianPhone(phone) {
  // Remove any non-digit characters
  const cleaned = phone.replace(/\D/g, "");

  // Add country code if missing
  if (cleaned.length === 10 && cleaned.startsWith("1")) {
    return `+20${cleaned}`;
  } else if (cleaned.length === 11 && cleaned.startsWith("01")) {
    return `+20${cleaned.substring(1)}`;
  } else if (cleaned.length === 13 && cleaned.startsWith("201")) {
    return `+${cleaned}`;
  }

  return phone; // Return original if can't format
}
