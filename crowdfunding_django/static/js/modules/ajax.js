/**
 * AJAX Module
 * Handles AJAX requests and responses with proper error handling
 */

import {
  request,
  showLoading,
  hideLoading,
  setupCSRF,
} from "../utils/helpers.js";

class AjaxManager {
  constructor() {
    this.pendingRequests = new Map();
    this.defaultConfig = {
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      showLoading: true,
      showErrors: true,
    };

    this.init();
  }

  /**
   * Initialize AJAX manager
   */
  init() {
    setupCSRF();
    this.setupGlobalErrorHandling();
    this.setupFormHandlers();
    this.setupSearchHandlers();
  }

  /**
   * Setup global error handling
   */
  setupGlobalErrorHandling() {
    window.addEventListener("unhandledrejection", (event) => {
      console.error("Unhandled promise rejection:", event.reason);
      this.showError("An unexpected error occurred. Please try again.");
    });
  }

  /**
   * Setup automatic form AJAX handlers
   */
  setupFormHandlers() {
    document.addEventListener("submit", (e) => {
      const form = e.target;
      if (form.hasAttribute("data-ajax")) {
        e.preventDefault();
        this.submitForm(form);
      }
    });
  }

  /**
   * Setup search handlers
   */
  setupSearchHandlers() {
    const searchForms = document.querySelectorAll("[data-search]");
    searchForms.forEach((form) => {
      const input = form.querySelector('input[type="text"]');
      if (input) {
        let debounceTimer;
        input.addEventListener("input", (e) => {
          clearTimeout(debounceTimer);
          debounceTimer = setTimeout(() => {
            this.handleSearch(form, e.target.value);
          }, 300);
        });
      }
    });
  }

  /**
   * Make AJAX request
   * @param {string} url - Request URL
   * @param {Object} options - Request options
   * @returns {Promise} Request promise
   */
  async makeRequest(url, options = {}) {
    const config = { ...this.defaultConfig, ...options };
    const requestId = this.generateRequestId();

    try {
      // Cancel any pending request to the same URL
      if (config.cancelPending !== false) {
        this.cancelPendingRequest(url);
      }

      // Setup request options
      const requestOptions = {
        method: config.method || "GET",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          ...config.headers,
        },
      };

      // Add request body for POST/PUT/PATCH
      if (
        config.data &&
        ["POST", "PUT", "PATCH"].includes(requestOptions.method)
      ) {
        if (config.data instanceof FormData) {
          // Remove Content-Type header for FormData (browser sets it)
          delete requestOptions.headers["Content-Type"];
          requestOptions.body = config.data;
        } else {
          requestOptions.body = JSON.stringify(config.data);
        }
      }

      // Setup loading indicator
      let loadingElement = null;
      if (config.showLoading && config.loadingElement) {
        loadingElement =
          typeof config.loadingElement === "string"
            ? document.querySelector(config.loadingElement)
            : config.loadingElement;

        if (loadingElement) {
          showLoading(loadingElement, config.loadingText);
        }
      }

      // Create AbortController for request cancellation
      const controller = new AbortController();
      requestOptions.signal = controller.signal;

      // Set timeout
      const timeoutId = setTimeout(() => controller.abort(), config.timeout);

      // Store request for potential cancellation
      this.pendingRequests.set(requestId, {
        controller,
        url,
        timeoutId,
        loadingElement,
      });

      // Make the request
      const response = await request(url, requestOptions);

      // Clear timeout
      clearTimeout(timeoutId);

      // Remove from pending requests
      this.pendingRequests.delete(requestId);

      // Hide loading indicator
      if (loadingElement) {
        hideLoading(loadingElement);
      }

      // Parse response
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      // Handle different response status codes
      if (response.ok) {
        if (config.successCallback) {
          config.successCallback(data, response);
        }
        return { success: true, data, response };
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      // Clear timeout if it exists
      const pendingRequest = this.pendingRequests.get(requestId);
      if (pendingRequest) {
        clearTimeout(pendingRequest.timeoutId);
        if (pendingRequest.loadingElement) {
          hideLoading(pendingRequest.loadingElement);
        }
        this.pendingRequests.delete(requestId);
      }

      // Handle different types of errors
      if (error.name === "AbortError") {
        console.log("Request was aborted");
        return { success: false, error: "Request cancelled" };
      }

      // Retry logic
      if (config.retries > 0 && !error.message.includes("4")) {
        console.log(`Retrying request. Attempts left: ${config.retries - 1}`);
        await this.delay(config.retryDelay);
        return this.makeRequest(url, {
          ...config,
          retries: config.retries - 1,
        });
      }

      // Show error message
      if (config.showErrors) {
        this.showError(error.message);
      }

      if (config.errorCallback) {
        config.errorCallback(error);
      }

      return { success: false, error: error.message };
    }
  }

  /**
   * Submit form via AJAX
   * @param {Element} form - Form element
   * @param {Object} options - Submission options
   */
  async submitForm(form, options = {}) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('[type="submit"]');

    const config = {
      method: form.method || "POST",
      data: formData,
      loadingElement: submitButton,
      loadingText: "Submitting...",
      ...options,
    };

    // Get form action URL
    const url = options.url || form.action || window.location.href;

    // Add form validation if needed
    if (form.hasAttribute("data-validate")) {
      const isValid = this.validateForm(form);
      if (!isValid) {
        return { success: false, error: "Form validation failed" };
      }
    }

    const result = await this.makeRequest(url, config);

    if (result.success) {
      // Handle successful form submission
      if (result.data.redirect) {
        window.location.href = result.data.redirect;
      } else if (result.data.message) {
        this.showSuccess(result.data.message);
      }

      // Reset form if specified
      if (options.resetForm !== false) {
        form.reset();
      }

      // Trigger custom event
      form.dispatchEvent(
        new CustomEvent("ajaxSuccess", {
          detail: { data: result.data, response: result.response },
        })
      );
    } else {
      // Trigger custom event for errors
      form.dispatchEvent(
        new CustomEvent("ajaxError", {
          detail: { error: result.error },
        })
      );
    }

    return result;
  }

  /**
   * Handle search functionality
   * @param {Element} form - Search form element
   * @param {string} query - Search query
   */
  async handleSearch(form, query) {
    const url = form.action || form.getAttribute("data-search-url");
    const resultContainer = document.querySelector(
      form.getAttribute("data-result-container")
    );

    if (!url || !resultContainer) return;

    // Clear results if query is empty
    if (!query.trim()) {
      resultContainer.innerHTML = "";
      return;
    }

    const config = {
      method: "GET",
      showLoading: false,
      showErrors: false,
    };

    // Add query parameter
    const searchUrl = new URL(url, window.location.origin);
    searchUrl.searchParams.set("q", query);

    const result = await this.makeRequest(searchUrl.toString(), config);

    if (result.success) {
      if (typeof result.data === "string") {
        resultContainer.innerHTML = result.data;
      } else if (result.data.html) {
        resultContainer.innerHTML = result.data.html;
      } else if (result.data.results) {
        this.renderSearchResults(resultContainer, result.data.results);
      }

      // Trigger custom event
      form.dispatchEvent(
        new CustomEvent("searchComplete", {
          detail: { query, results: result.data },
        })
      );
    }
  }

  /**
   * Render search results
   * @param {Element} container - Results container
   * @param {Array} results - Search results
   */
  renderSearchResults(container, results) {
    if (results.length === 0) {
      container.innerHTML =
        '<div class="alert alert-info">No results found.</div>';
      return;
    }

    const resultsHtml = results
      .map(
        (result) => `
            <div class="search-result">
                <h5><a href="${result.url || "#"}">${result.title}</a></h5>
                ${result.description ? `<p>${result.description}</p>` : ""}
                ${
                  result.meta
                    ? `<small class="text-muted">${result.meta}</small>`
                    : ""
                }
            </div>
        `
      )
      .join("");

    container.innerHTML = resultsHtml;
  }

  /**
   * Load content dynamically
   * @param {string} url - URL to load content from
   * @param {string|Element} target - Target element selector or element
   * @param {Object} options - Load options
   */
  async loadContent(url, target, options = {}) {
    const targetElement =
      typeof target === "string" ? document.querySelector(target) : target;

    if (!targetElement) {
      console.error("Target element not found");
      return { success: false, error: "Target element not found" };
    }

    const config = {
      loadingElement: targetElement,
      loadingText: "Loading...",
      ...options,
    };

    const result = await this.makeRequest(url, config);

    if (result.success) {
      if (typeof result.data === "string") {
        targetElement.innerHTML = result.data;
      } else if (result.data.html) {
        targetElement.innerHTML = result.data.html;
      }

      // Trigger custom event
      targetElement.dispatchEvent(
        new CustomEvent("contentLoaded", {
          detail: { url, data: result.data },
        })
      );
    }

    return result;
  }

  /**
   * Cancel pending request
   * @param {string} url - URL or request ID to cancel
   */
  cancelPendingRequest(url) {
    for (const [requestId, request] of this.pendingRequests) {
      if (request.url === url || requestId === url) {
        request.controller.abort();
        clearTimeout(request.timeoutId);
        if (request.loadingElement) {
          hideLoading(request.loadingElement);
        }
        this.pendingRequests.delete(requestId);
      }
    }
  }

  /**
   * Cancel all pending requests
   */
  cancelAllRequests() {
    for (const [requestId, request] of this.pendingRequests) {
      request.controller.abort();
      clearTimeout(request.timeoutId);
      if (request.loadingElement) {
        hideLoading(request.loadingElement);
      }
    }
    this.pendingRequests.clear();
  }

  /**
   * Show success message
   * @param {string} message - Success message
   */
  showSuccess(message) {
    this.showNotification(message, "success");
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    this.showNotification(message, "danger");
  }

  /**
   * Show notification
   * @param {string} message - Notification message
   * @param {string} type - Notification type
   */
  showNotification(message, type = "info") {
    // Try to use existing message system
    const messageContainer = document.querySelector(".messages");
    if (messageContainer) {
      const alert = document.createElement("div");
      alert.className = `alert alert-${type} alert-dismissible fade show`;
      alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
      messageContainer.appendChild(alert);

      // Auto-remove after 5 seconds
      setTimeout(() => {
        alert.remove();
      }, 5000);
    } else {
      // Fallback to console or alert
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  /**
   * Validate form before submission
   * @param {Element} form - Form to validate
   * @returns {boolean} Whether form is valid
   */
  validateForm(form) {
    // Basic HTML5 validation
    if (!form.checkValidity()) {
      form.reportValidity();
      return false;
    }

    // Custom validation can be added here
    return true;
  }

  /**
   * Generate unique request ID
   * @returns {string} Unique request ID
   */
  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Delay utility for retries
   * @param {number} ms - Milliseconds to delay
   * @returns {Promise} Delay promise
   */
  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Destroy AJAX manager
   */
  destroy() {
    this.cancelAllRequests();
  }
}

// Initialize AJAX manager
export default function initAjaxManager() {
  return new AjaxManager();
}

// Auto-initialize
if (typeof window !== "undefined" && !window.ajaxManager) {
  document.addEventListener("DOMContentLoaded", () => {
    window.ajaxManager = initAjaxManager();
  });
}
