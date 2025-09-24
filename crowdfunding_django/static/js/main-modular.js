/**
 * Main JavaScript Entry Point - Modular Version
 * Imports and initializes all modules for the CrowdFunding platform
 */

// Import utility functions
import {
  setupCSRF,
  debounce,
  formatCurrency,
  formatDate,
} from "./utils/helpers.js";

// Import modules
import initNavigation from "./modules/navigation.js";
import initFormValidation from "./modules/forms.js";
import initAjaxManager from "./modules/ajax.js";
import { initUIComponents, Alert } from "./modules/ui.js";

/**
 * Main Application Class
 */
class CrowdFundingApp {
  constructor() {
    this.modules = {};
    this.config = {
      debug: false,
      currency: "EGP",
      locale: "ar-EG",
    };

    this.init();
  }

  /**
   * Initialize the application
   */
  init() {
    // Wait for DOM to be ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () =>
        this.initializeModules()
      );
    } else {
      this.initializeModules();
    }
  }

  /**
   * Initialize all modules
   */
  initializeModules() {
    try {
      // Setup CSRF protection
      setupCSRF();

      // Initialize core modules
      this.modules.navigation = initNavigation();
      this.modules.ajax = initAjaxManager();
      this.modules.ui = initUIComponents();

      // Initialize form validation for all forms with data-validate
      document.querySelectorAll("[data-validate]").forEach((form) => {
        this.modules.formValidators = this.modules.formValidators || [];
        this.modules.formValidators.push(initFormValidation(form));
      });

      // Initialize project-specific functionality
      this.initProjectFunctionality();
      this.initSearchFunctionality();
      this.initContributionFunctionality();
      this.initUserProfile();

      // Setup global event handlers
      this.setupGlobalEventHandlers();

      // Setup performance monitoring
      this.setupPerformanceMonitoring();

      console.log("CrowdFunding App initialized successfully");
    } catch (error) {
      console.error("Error initializing CrowdFunding App:", error);
      this.showError(
        "Application initialization failed. Please refresh the page."
      );
    }
  }

  /**
   * Initialize project-specific functionality
   */
  initProjectFunctionality() {
    // Project card interactions
    this.initProjectCards();

    // Project creation/editing
    this.initProjectForms();

    // Project progress tracking
    this.initProjectProgress();
  }

  /**
   * Initialize project cards
   */
  initProjectCards() {
    const projectCards = document.querySelectorAll(".project-card");

    projectCards.forEach((card) => {
      // Add hover effects
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-4px)";
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0)";
      });

      // Handle favorite button
      const favoriteBtn = card.querySelector(".btn-favorite");
      if (favoriteBtn) {
        favoriteBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.toggleProjectFavorite(favoriteBtn);
        });
      }

      // Handle share button
      const shareBtn = card.querySelector(".btn-share");
      if (shareBtn) {
        shareBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.shareProject(shareBtn);
        });
      }
    });
  }

  /**
   * Initialize project forms
   */
  initProjectForms() {
    const projectForm = document.querySelector("#project-form");
    if (!projectForm) return;

    // Dynamic form fields
    this.setupDynamicFormFields(projectForm);

    // Image upload preview
    this.setupImageUploadPreview(projectForm);

    // Real-time goal validation
    this.setupGoalValidation(projectForm);
  }

  /**
   * Setup dynamic form fields
   */
  setupDynamicFormFields(form) {
    // Category change handler
    const categoryField = form.querySelector("#id_category");
    if (categoryField) {
      categoryField.addEventListener("change", () => {
        this.updateCategorySpecificFields(categoryField.value);
      });
    }

    // Duration calculation
    const startDateField = form.querySelector("#id_start_date");
    const endDateField = form.querySelector("#id_end_date");

    if (startDateField && endDateField) {
      [startDateField, endDateField].forEach((field) => {
        field.addEventListener("change", () => {
          this.calculateProjectDuration(
            startDateField.value,
            endDateField.value
          );
        });
      });
    }
  }

  /**
   * Setup image upload preview
   */
  setupImageUploadPreview(form) {
    const imageInput = form.querySelector("#id_image");
    if (!imageInput) return;

    imageInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith("image/")) {
        Alert.show("Please select a valid image file.", "danger");
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        Alert.show("Image size must be less than 5MB.", "danger");
        return;
      }

      // Show preview
      const reader = new FileReader();
      reader.onload = (e) => {
        this.showImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    });
  }

  /**
   * Show image preview
   */
  showImagePreview(src) {
    let preview = document.querySelector("#image-preview");
    if (!preview) {
      preview = document.createElement("div");
      preview.id = "image-preview";
      preview.className = "mt-3";
      document.querySelector("#id_image").parentNode.appendChild(preview);
    }

    preview.innerHTML = `
            <img src="${src}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <button type="button" class="btn btn-sm btn-danger ml-2" onclick="this.parentNode.remove()">
                <i class="fas fa-times"></i> Remove
            </button>
        `;
  }

  /**
   * Setup goal validation
   */
  setupGoalValidation(form) {
    const goalField = form.querySelector("#id_goal_amount");
    if (!goalField) return;

    goalField.addEventListener(
      "input",
      debounce((e) => {
        const amount = parseFloat(e.target.value);
        if (amount) {
          this.validateGoalAmount(amount);
        }
      }, 500)
    );
  }

  /**
   * Validate goal amount
   */
  validateGoalAmount(amount) {
    const minGoal = 1000; // Minimum goal in EGP
    const maxGoal = 1000000; // Maximum goal in EGP

    let message = "";
    let isValid = true;

    if (amount < minGoal) {
      message = `Minimum goal amount is ${formatCurrency(minGoal)}`;
      isValid = false;
    } else if (amount > maxGoal) {
      message = `Maximum goal amount is ${formatCurrency(maxGoal)}`;
      isValid = false;
    } else {
      message = `Goal amount: ${formatCurrency(amount)}`;
    }

    this.showGoalFeedback(message, isValid);
  }

  /**
   * Show goal feedback
   */
  showGoalFeedback(message, isValid) {
    let feedback = document.querySelector("#goal-feedback");
    if (!feedback) {
      feedback = document.createElement("div");
      feedback.id = "goal-feedback";
      feedback.className = "form-text";
      document
        .querySelector("#id_goal_amount")
        .parentNode.appendChild(feedback);
    }

    feedback.textContent = message;
    feedback.className = `form-text ${
      isValid ? "text-success" : "text-danger"
    }`;
  }

  /**
   * Initialize search functionality
   */
  initSearchFunctionality() {
    const searchForm = document.querySelector(".search-form");
    if (!searchForm) return;

    const searchInput = searchForm.querySelector('input[type="text"]');
    const searchResults = document.querySelector("#search-results");

    if (searchInput && searchResults) {
      // Real-time search
      const debouncedSearch = debounce((query) => {
        if (query.length >= 2) {
          this.performSearch(query, searchResults);
        } else {
          searchResults.innerHTML = "";
        }
      }, 300);

      searchInput.addEventListener("input", (e) => {
        debouncedSearch(e.target.value);
      });

      // Search filters
      this.setupSearchFilters(searchForm);
    }
  }

  /**
   * Perform search
   */
  async performSearch(query, resultsContainer) {
    try {
      const url = new URL("/projects/search/", window.location.origin);
      url.searchParams.set("q", query);

      const response = await this.modules.ajax.makeRequest(url.toString(), {
        showLoading: false,
      });

      if (response.success) {
        this.renderSearchResults(response.data, resultsContainer);
      }
    } catch (error) {
      console.error("Search error:", error);
    }
  }

  /**
   * Render search results
   */
  renderSearchResults(data, container) {
    if (!data.projects || data.projects.length === 0) {
      container.innerHTML =
        '<div class="alert alert-info">No projects found.</div>';
      return;
    }

    const resultsHtml = data.projects
      .map(
        (project) => `
            <div class="search-result-item">
                <div class="row">
                    <div class="col-md-3">
                        <img src="${
                          project.image || "/static/img/placeholder.jpg"
                        }" 
                             alt="${project.title}" class="img-fluid rounded">
                    </div>
                    <div class="col-md-9">
                        <h5><a href="/projects/${project.id}/">${
          project.title
        }</a></h5>
                        <p class="text-muted">${project.description.substring(
                          0,
                          150
                        )}...</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-primary">${
                              project.category
                            }</span>
                            <span class="text-success">${formatCurrency(
                              project.current_amount
                            )} / ${formatCurrency(project.goal_amount)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");

    container.innerHTML = resultsHtml;
  }

  /**
   * Setup search filters
   */
  setupSearchFilters(form) {
    const filterInputs = form.querySelectorAll(
      'input[type="checkbox"], select'
    );

    filterInputs.forEach((input) => {
      input.addEventListener("change", () => {
        this.applySearchFilters(form);
      });
    });
  }

  /**
   * Initialize contribution functionality
   */
  initContributionFunctionality() {
    const contributeBtn = document.querySelector("#contribute-btn");
    const contributeModal = document.querySelector("#contribute-modal");

    if (contributeBtn && contributeModal) {
      this.setupContributionModal(contributeBtn, contributeModal);
    }

    // Contribution amount buttons
    this.setupContributionAmountButtons();
  }

  /**
   * Setup contribution modal
   */
  setupContributionModal(btn, modal) {
    const form = modal.querySelector("#contribution-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await this.processContribution(form);
    });
  }

  /**
   * Setup contribution amount buttons
   */
  setupContributionAmountButtons() {
    const amountButtons = document.querySelectorAll(".amount-btn");
    const amountInput = document.querySelector("#id_amount");

    if (!amountInput) return;

    amountButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const amount = btn.dataset.amount;
        amountInput.value = amount;

        // Update active state
        amountButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });

    // Custom amount handling
    amountInput.addEventListener("input", () => {
      amountButtons.forEach((btn) => btn.classList.remove("active"));
    });
  }

  /**
   * Process contribution
   */
  async processContribution(form) {
    try {
      const result = await this.modules.ajax.submitForm(form, {
        loadingText: "Processing contribution...",
      });

      if (result.success) {
        Alert.show(
          "Contribution successful! Thank you for your support.",
          "success"
        );
        // Update project progress
        this.updateProjectProgress(result.data);
        // Close modal
        const modal = form.closest(".modal");
        if (modal) {
          // Assuming Modal class is available
          modal.style.display = "none";
        }
      }
    } catch (error) {
      console.error("Contribution error:", error);
      Alert.show("Contribution failed. Please try again.", "danger");
    }
  }

  /**
   * Initialize project progress tracking
   */
  initProjectProgress() {
    const progressBars = document.querySelectorAll(
      ".progress-bar[data-project-id]"
    );

    progressBars.forEach((bar) => {
      this.animateProgressBar(bar);
    });
  }

  /**
   * Animate progress bar
   */
  animateProgressBar(bar) {
    const targetWidth =
      bar.style.width || bar.getAttribute("data-progress") + "%";
    bar.style.width = "0%";

    setTimeout(() => {
      bar.style.transition = "width 1s ease-in-out";
      bar.style.width = targetWidth;
    }, 100);
  }

  /**
   * Update project progress
   */
  updateProjectProgress(data) {
    if (!data.project_id) return;

    const progressBar = document.querySelector(
      `[data-project-id="${data.project_id}"] .progress-bar`
    );
    const currentAmount = document.querySelector(
      `[data-project-id="${data.project_id}"] .current-amount`
    );
    const contributorsCount = document.querySelector(
      `[data-project-id="${data.project_id}"] .contributors-count`
    );

    if (progressBar) {
      const percentage = (data.current_amount / data.goal_amount) * 100;
      progressBar.style.width = `${Math.min(percentage, 100)}%`;
    }

    if (currentAmount) {
      currentAmount.textContent = formatCurrency(data.current_amount);
    }

    if (contributorsCount) {
      contributorsCount.textContent = data.contributors_count;
    }
  }

  /**
   * Initialize user profile functionality
   */
  initUserProfile() {
    // Profile image upload
    this.setupProfileImageUpload();

    // Profile settings
    this.setupProfileSettings();
  }

  /**
   * Setup global event handlers
   */
  setupGlobalEventHandlers() {
    // Handle back to top button
    this.setupBackToTop();

    // Handle external links
    this.setupExternalLinks();

    // Handle print functionality
    this.setupPrintHandlers();
  }

  /**
   * Setup back to top button
   */
  setupBackToTop() {
    const backToTopBtn = document.querySelector(".back-to-top");
    if (!backToTopBtn) return;

    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        backToTopBtn.style.display = "block";
      } else {
        backToTopBtn.style.display = "none";
      }
    };

    window.addEventListener("scroll", debounce(toggleVisibility, 100));

    backToTopBtn.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /**
   * Setup external links
   */
  setupExternalLinks() {
    const externalLinks = document.querySelectorAll(
      'a[href^="http"]:not([href*="' + window.location.hostname + '"])'
    );

    externalLinks.forEach((link) => {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    });
  }

  /**
   * Setup performance monitoring
   */
  setupPerformanceMonitoring() {
    if (this.config.debug) {
      // Monitor page load time
      window.addEventListener("load", () => {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
      });

      // Monitor AJAX requests
      const originalFetch = window.fetch;
      window.fetch = async (...args) => {
        const start = performance.now();
        const response = await originalFetch(...args);
        const end = performance.now();
        console.log(
          `AJAX request to ${args[0]} took ${(end - start).toFixed(2)}ms`
        );
        return response;
      };
    }
  }

  /**
   * Toggle project favorite
   */
  async toggleProjectFavorite(btn) {
    const projectId = btn.dataset.projectId;
    if (!projectId) return;

    try {
      const result = await this.modules.ajax.makeRequest(
        `/projects/${projectId}/favorite/`,
        {
          method: "POST",
          loadingElement: btn,
        }
      );

      if (result.success) {
        btn.classList.toggle("favorited");
        const icon = btn.querySelector("i");
        if (icon) {
          icon.classList.toggle("fas");
          icon.classList.toggle("far");
        }
      }
    } catch (error) {
      console.error("Favorite error:", error);
    }
  }

  /**
   * Share project
   */
  shareProject(btn) {
    const projectUrl = btn.dataset.url || window.location.href;
    const projectTitle = btn.dataset.title || document.title;

    if (navigator.share) {
      navigator.share({
        title: projectTitle,
        url: projectUrl,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(projectUrl).then(() => {
        Alert.show("Project link copied to clipboard!", "success");
      });
    }
  }

  /**
   * Show error message
   */
  showError(message) {
    Alert.show(message, "danger");
  }

  /**
   * Show success message
   */
  showSuccess(message) {
    Alert.show(message, "success");
  }

  /**
   * Destroy application
   */
  destroy() {
    Object.values(this.modules).forEach((module) => {
      if (module && typeof module.destroy === "function") {
        module.destroy();
      }
    });
  }
}

// Initialize application
const app = new CrowdFundingApp();

// Export for global access
window.CrowdFundingApp = app;

export default app;
