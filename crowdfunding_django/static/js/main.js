// Custom JavaScript for CrowdFunding Platform

document.addEventListener("DOMContentLoaded", function () {
  // Mobile Navigation Toggle
  const navToggle = document.getElementById("navToggle");
  const navMenu = document.getElementById("navMenu");

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      navMenu.classList.toggle("show");

      // Animate hamburger menu
      navToggle.classList.toggle("active");
    });

    // Close mobile menu when clicking outside
    document.addEventListener("click", function (e) {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove("show");
        navToggle.classList.remove("active");
      }
    });
  }

  // User Dropdown Toggle
  const userDropdown = document.getElementById("userDropdown");
  const userDropdownMenu = document.getElementById("userDropdownMenu");

  if (userDropdown && userDropdownMenu) {
    userDropdown.addEventListener("click", function (e) {
      e.preventDefault();
      userDropdownMenu.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (!userDropdown.contains(e.target)) {
        userDropdownMenu.classList.remove("show");
      }
    });
  }

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = "0";
      alert.style.transform = "translateX(100%)";
      setTimeout(function () {
        alert.remove();
      }, 300);
    }, 5000);
  });

  // Search functionality with AJAX
  const searchInput = document.querySelector('input[name="search_query"]');
  if (searchInput) {
    let searchTimeout;

    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      const query = this.value.trim();

      if (query.length > 2) {
        searchTimeout = setTimeout(function () {
          performSearch(query);
        }, 300);
      }
    });
  }

  // Project search by date
  const dateSearchInput = document.querySelector('input[name="date_search"]');
  if (dateSearchInput) {
    dateSearchInput.addEventListener("change", function () {
      const date = this.value;
      if (date) {
        searchByDate(date);
      }
    });
  }

  // Progress bar animations
  const progressBars = document.querySelectorAll(".progress-bar");
  progressBars.forEach(function (bar) {
    const percentage = bar.dataset.percentage || bar.style.width;
    if (percentage) {
      bar.style.width = "0%";
      setTimeout(function () {
        bar.style.width = percentage;
      }, 500);
    }
  });

  // Form validation
  const forms = document.querySelectorAll("form");
  forms.forEach(function (form) {
    // Allow forms to opt out of client-side validation by setting
    // data-client-validate="false" on the <form> element (default: true)
    const clientValidate = form.getAttribute("data-client-validate");
    if (clientValidate && clientValidate.toLowerCase() === "false") {
      return; // skip adding validation handlers for this form
    }

    form.addEventListener("submit", function (e) {
      if (!validateForm(form)) {
        e.preventDefault();
      }
    });

    // Real-time validation
    const inputs = form.querySelectorAll("input, textarea, select");
    inputs.forEach(function (input) {
      input.addEventListener("blur", function () {
        validateField(input);
      });
    });
  });

  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Loading states for buttons
  const submitButtons = document.querySelectorAll(
    'button[type="submit"], input[type="submit"]'
  );
  submitButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      if (this.form && this.form.checkValidity()) {
        showLoading(this);
      }
    });
  });

  // Auto-resize textareas
  const textareas = document.querySelectorAll("textarea");
  textareas.forEach(function (textarea) {
    textarea.addEventListener("input", function () {
      this.style.height = "auto";
      this.style.height = this.scrollHeight + "px";
    });
  });

  // Image preview for file inputs
  const fileInputs = document.querySelectorAll(
    'input[type="file"][accept*="image"]'
  );
  fileInputs.forEach(function (input) {
    input.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        previewImage(file, input);
      }
    });
  });

  // Project stats real-time updates
  const projectStatsElements = document.querySelectorAll("[data-project-id]");
  projectStatsElements.forEach(function (element) {
    const projectId = element.dataset.projectId;
    if (projectId) {
      updateProjectStats(projectId);
      // Update every 30 seconds
      setInterval(function () {
        updateProjectStats(projectId);
      }, 30000);
    }
  });
});

// Search functions
function performSearch(query) {
  if (typeof searchProjectsAjax === "function") {
    searchProjectsAjax(query);
  }
}

function searchByDate(date) {
  // AJAX disabled in simplified build. Fall back to a full page load with the
  // date as a query parameter so the server can handle filtering.
  try {
    const params = new URLSearchParams(window.location.search);
    params.set("date", date);
    // preserve other params
    window.location.search = params.toString();
  } catch (err) {
    console.warn("searchByDate fallback failed, performing full reload");
    window.location.href = `${
      window.location.pathname
    }?date=${encodeURIComponent(date)}`;
  }
}

function displaySearchResults(results) {
  // Implementation depends on the specific page layout
  console.log("Search results:", results);
}

// Form validation
function validateForm(form) {
  let isValid = true;
  const inputs = form.querySelectorAll(
    "input[required], textarea[required], select[required]"
  );

  inputs.forEach(function (input) {
    if (!validateField(input)) {
      isValid = false;
    }
  });

  return isValid;
}

function validateField(field) {
  const value = field.value.trim();
  let isValid = true;
  let message = "";

  // Remove existing error states
  field.classList.remove("is-invalid");
  const existingFeedback = field.parentNode.querySelector(".invalid-feedback");
  if (existingFeedback) {
    existingFeedback.remove();
  }

  // Required field validation
  if (field.hasAttribute("required") && !value) {
    isValid = false;
    message = "This field is required.";
  }

  // Email validation
  if (field.type === "email" && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      isValid = false;
      message = "Please enter a valid email address.";
    }
  }

  // Phone validation (Egyptian numbers)
  if (field.name === "phone_number" && value) {
    const phoneRegex = /^(\+201|01|1)[0125][0-9]{8}$/;
    if (!phoneRegex.test(value.replace(/[\s-]/g, ""))) {
      isValid = false;
      message = "Please enter a valid Egyptian mobile number.";
    }
  }

  // Password validation
  if (field.type === "password" && value) {
    if (value.length < 8) {
      isValid = false;
      message = "Password must be at least 8 characters long.";
    } else if (!/[A-Za-z]/.test(value) || !/[0-9]/.test(value)) {
      isValid = false;
      message = "Password must contain both letters and numbers.";
    }
  }

  // Password confirmation
  if (field.name === "password2") {
    const password1 = field.form.querySelector('input[name="password1"]');
    if (password1 && value !== password1.value) {
      isValid = false;
      message = "Passwords do not match.";
    }
  }

  // Number validation
  if (field.type === "number" && value) {
    const num = parseFloat(value);
    const min = field.getAttribute("min");
    const max = field.getAttribute("max");

    if (min && num < parseFloat(min)) {
      isValid = false;
      message = `Value must be at least ${min}.`;
    } else if (max && num > parseFloat(max)) {
      isValid = false;
      message = `Value cannot exceed ${max}.`;
    }
  }

  // Date validation
  if (field.type === "date" && value) {
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (field.name === "start_date" && date < today) {
      isValid = false;
      message = "Start date cannot be in the past.";
    }

    if (field.name === "end_date") {
      const startDateField = field.form.querySelector(
        'input[name="start_date"]'
      );
      if (startDateField && date <= new Date(startDateField.value)) {
        isValid = false;
        message = "End date must be after start date.";
      }
    }
  }

  // Show error if invalid
  if (!isValid) {
    field.classList.add("is-invalid");
    const feedback = document.createElement("div");
    feedback.className = "invalid-feedback";
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
  }

  return isValid;
}

// UI helpers
function showLoading(button) {
  const originalText = button.innerHTML;
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
  button.disabled = true;

  // Restore after 3 seconds if no form submission
  setTimeout(function () {
    if (button.disabled) {
      button.innerHTML = originalText;
      button.disabled = false;
    }
  }, 3000);
}

function previewImage(file, input) {
  const reader = new FileReader();
  reader.onload = function (e) {
    let preview = input.parentNode.querySelector(".image-preview");
    if (!preview) {
      preview = document.createElement("img");
      preview.className = "image-preview";
      preview.style.maxWidth = "200px";
      preview.style.marginTop = "10px";
      preview.style.borderRadius = "8px";
      input.parentNode.appendChild(preview);
    }
    preview.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function updateProjectStats(projectId) {
  // AJAX polling disabled in simplified build. Leave project stats static or
  // let the server render fresh values on page refresh.
  console.warn(
    "updateProjectStats: AJAX disabled; skipping live update for",
    projectId
  );
}

// Utility functions
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-EG", {
    style: "currency",
    currency: "EGP",
  }).format(amount);
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Custom form helper for Django CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Setup CSRF token for AJAX requests
const csrftoken = getCookie("csrftoken");
if (csrftoken) {
  // Setup jQuery AJAX defaults if jQuery is available
  if (typeof $ !== "undefined") {
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      },
    });
  }
}
