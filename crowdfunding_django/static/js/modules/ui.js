/**
 * UI Components Module
 * Handles interactive UI components like modals, tooltips, alerts, etc.
 */

import { debounce, throttle } from "../utils/helpers.js";

/**
 * Modal Component
 */
class Modal {
  constructor(element, options = {}) {
    this.element =
      typeof element === "string" ? document.querySelector(element) : element;
    this.options = {
      backdrop: true,
      keyboard: true,
      focus: true,
      ...options,
    };
    this.isShown = false;
    this.init();
  }

  init() {
    if (!this.element) return;

    this.backdrop = null;
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Close button
    const closeButtons = this.element.querySelectorAll(
      '[data-dismiss="modal"]'
    );
    closeButtons.forEach((button) => {
      button.addEventListener("click", () => this.hide());
    });

    // Keyboard events
    if (this.options.keyboard) {
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && this.isShown) {
          this.hide();
        }
      });
    }
  }

  show() {
    if (this.isShown) return;

    this.isShown = true;
    this.element.style.display = "block";
    this.element.classList.add("show");

    if (this.options.backdrop) {
      this.showBackdrop();
    }

    if (this.options.focus) {
      this.element.focus();
    }

    // Trigger event
    this.element.dispatchEvent(new CustomEvent("modal.show"));

    // Lock body scroll
    document.body.classList.add("modal-open");
  }

  hide() {
    if (!this.isShown) return;

    this.isShown = false;
    this.element.classList.remove("show");

    setTimeout(() => {
      this.element.style.display = "none";
    }, 300);

    this.hideBackdrop();

    // Trigger event
    this.element.dispatchEvent(new CustomEvent("modal.hide"));

    // Unlock body scroll
    document.body.classList.remove("modal-open");
  }

  showBackdrop() {
    this.backdrop = document.createElement("div");
    this.backdrop.className = "modal-backdrop";
    document.body.appendChild(this.backdrop);

    setTimeout(() => {
      this.backdrop.classList.add("show");
    }, 10);

    // Close on backdrop click
    this.backdrop.addEventListener("click", () => {
      if (this.options.backdrop !== "static") {
        this.hide();
      }
    });
  }

  hideBackdrop() {
    if (this.backdrop) {
      this.backdrop.classList.remove("show");
      setTimeout(() => {
        if (this.backdrop && this.backdrop.parentNode) {
          this.backdrop.parentNode.removeChild(this.backdrop);
        }
        this.backdrop = null;
      }, 300);
    }
  }

  toggle() {
    this.isShown ? this.hide() : this.show();
  }
}

/**
 * Alert Component
 */
class Alert {
  constructor(element) {
    this.element =
      typeof element === "string" ? document.querySelector(element) : element;
    this.init();
  }

  init() {
    if (!this.element) return;

    const closeButton = this.element.querySelector('[data-dismiss="alert"]');
    if (closeButton) {
      closeButton.addEventListener("click", () => this.close());
    }
  }

  close() {
    this.element.classList.add("fade", "out");

    setTimeout(() => {
      this.element.remove();
    }, 300);

    // Trigger event
    this.element.dispatchEvent(new CustomEvent("alert.close"));
  }

  static show(message, type = "info", container = null) {
    const alertElement = document.createElement("div");
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-dismiss="alert" aria-label="Close"></button>
        `;

    const targetContainer =
      container || document.querySelector(".messages") || document.body;
    targetContainer.appendChild(alertElement);

    // Initialize alert component
    new Alert(alertElement);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alertElement.parentNode) {
        new Alert(alertElement).close();
      }
    }, 5000);

    return alertElement;
  }
}

/**
 * Tooltip Component
 */
class Tooltip {
  constructor(element, options = {}) {
    this.element =
      typeof element === "string" ? document.querySelector(element) : element;
    this.options = {
      placement: "top",
      trigger: "hover",
      delay: 0,
      ...options,
    };
    this.tooltip = null;
    this.isShown = false;
    this.init();
  }

  init() {
    if (!this.element) return;

    this.title =
      this.element.getAttribute("title") ||
      this.element.getAttribute("data-title");
    if (!this.title) return;

    // Remove title attribute to prevent default tooltip
    this.element.removeAttribute("title");

    this.setupEventListeners();
  }

  setupEventListeners() {
    if (this.options.trigger === "hover") {
      this.element.addEventListener("mouseenter", () => this.show());
      this.element.addEventListener("mouseleave", () => this.hide());
    } else if (this.options.trigger === "click") {
      this.element.addEventListener("click", () => this.toggle());
    } else if (this.options.trigger === "focus") {
      this.element.addEventListener("focus", () => this.show());
      this.element.addEventListener("blur", () => this.hide());
    }
  }

  show() {
    if (this.isShown) return;

    const delay =
      typeof this.options.delay === "number"
        ? this.options.delay
        : this.options.delay.show || 0;

    setTimeout(() => {
      if (!this.isShown) {
        this.createTooltip();
        this.positionTooltip();
        this.isShown = true;
      }
    }, delay);
  }

  hide() {
    if (!this.isShown) return;

    const delay =
      typeof this.options.delay === "number"
        ? this.options.delay
        : this.options.delay.hide || 0;

    setTimeout(() => {
      if (this.tooltip) {
        this.tooltip.remove();
        this.tooltip = null;
        this.isShown = false;
      }
    }, delay);
  }

  createTooltip() {
    this.tooltip = document.createElement("div");
    this.tooltip.className = `tooltip tooltip-${this.options.placement}`;
    this.tooltip.innerHTML = `
            <div class="tooltip-arrow"></div>
            <div class="tooltip-content">${this.title}</div>
        `;
    document.body.appendChild(this.tooltip);
  }

  positionTooltip() {
    if (!this.tooltip) return;

    const elementRect = this.element.getBoundingClientRect();
    const tooltipRect = this.tooltip.getBoundingClientRect();

    let top, left;

    switch (this.options.placement) {
      case "top":
        top = elementRect.top - tooltipRect.height - 10;
        left = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
        break;
      case "bottom":
        top = elementRect.bottom + 10;
        left = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
        break;
      case "left":
        top = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
        left = elementRect.left - tooltipRect.width - 10;
        break;
      case "right":
        top = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
        left = elementRect.right + 10;
        break;
    }

    this.tooltip.style.top = `${top + window.scrollY}px`;
    this.tooltip.style.left = `${left + window.scrollX}px`;
  }

  toggle() {
    this.isShown ? this.hide() : this.show();
  }
}

/**
 * Collapse Component
 */
class Collapse {
  constructor(element, options = {}) {
    this.element =
      typeof element === "string" ? document.querySelector(element) : element;
    this.options = {
      duration: 300,
      easing: "ease",
      ...options,
    };
    this.isShown = false;
    this.init();
  }

  init() {
    if (!this.element) return;

    this.isShown = !this.element.classList.contains("collapsed");
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Find toggle buttons
    const toggles = document.querySelectorAll(
      `[data-toggle="collapse"][data-target="#${this.element.id}"]`
    );
    toggles.forEach((toggle) => {
      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        this.toggle();
      });
    });
  }

  show() {
    if (this.isShown) return;

    this.element.style.height = "0px";
    this.element.style.overflow = "hidden";
    this.element.classList.remove("collapsed");

    // Get the full height
    const fullHeight = this.element.scrollHeight;

    // Animate to full height
    this.element.style.transition = `height ${this.options.duration}ms ${this.options.easing}`;
    this.element.style.height = `${fullHeight}px`;

    setTimeout(() => {
      this.element.style.height = "auto";
      this.element.style.overflow = "visible";
      this.element.style.transition = "";
      this.isShown = true;

      // Trigger event
      this.element.dispatchEvent(new CustomEvent("collapse.show"));
    }, this.options.duration);
  }

  hide() {
    if (!this.isShown) return;

    const currentHeight = this.element.offsetHeight;
    this.element.style.height = `${currentHeight}px`;
    this.element.style.overflow = "hidden";

    // Force reflow
    this.element.offsetHeight;

    // Animate to 0 height
    this.element.style.transition = `height ${this.options.duration}ms ${this.options.easing}`;
    this.element.style.height = "0px";

    setTimeout(() => {
      this.element.classList.add("collapsed");
      this.element.style.transition = "";
      this.isShown = false;

      // Trigger event
      this.element.dispatchEvent(new CustomEvent("collapse.hide"));
    }, this.options.duration);
  }

  toggle() {
    this.isShown ? this.hide() : this.show();
  }
}

/**
 * Tab Component
 */
class Tabs {
  constructor(element, options = {}) {
    this.element =
      typeof element === "string" ? document.querySelector(element) : element;
    this.options = {
      activeClass: "active",
      ...options,
    };
    this.init();
  }

  init() {
    if (!this.element) return;

    this.tabLinks = this.element.querySelectorAll('[data-toggle="tab"]');
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.tabLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        this.showTab(link);
      });

      // Keyboard navigation
      link.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
          e.preventDefault();
          this.navigateTab(e.key === "ArrowRight" ? 1 : -1);
        }
      });
    });
  }

  showTab(tabLink) {
    const targetId =
      tabLink.getAttribute("data-target") || tabLink.getAttribute("href");
    const targetPane = document.querySelector(targetId);

    if (!targetPane) return;

    // Remove active class from all tabs and panes
    this.tabLinks.forEach((link) => {
      link.classList.remove(this.options.activeClass);
      link.setAttribute("aria-selected", "false");
    });

    document.querySelectorAll(".tab-pane").forEach((pane) => {
      pane.classList.remove(this.options.activeClass);
    });

    // Add active class to current tab and pane
    tabLink.classList.add(this.options.activeClass);
    tabLink.setAttribute("aria-selected", "true");
    targetPane.classList.add(this.options.activeClass);

    // Trigger event
    targetPane.dispatchEvent(
      new CustomEvent("tab.show", {
        detail: { relatedTarget: tabLink },
      })
    );
  }

  navigateTab(direction) {
    const activeTab = this.element.querySelector(
      `.${this.options.activeClass}`
    );
    const tabs = Array.from(this.tabLinks);
    const currentIndex = tabs.indexOf(activeTab);
    const newIndex = (currentIndex + direction + tabs.length) % tabs.length;

    tabs[newIndex].focus();
    this.showTab(tabs[newIndex]);
  }
}

/**
 * Initialize all UI components
 */
function initUIComponents() {
  // Initialize modals
  document.querySelectorAll(".modal").forEach((modal) => {
    new Modal(modal);
  });

  // Initialize modal triggers
  document.querySelectorAll('[data-toggle="modal"]').forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute("data-target");
      const modal = new Modal(targetId);
      modal.show();
    });
  });

  // Initialize alerts
  document.querySelectorAll(".alert").forEach((alert) => {
    new Alert(alert);
  });

  // Initialize tooltips
  document.querySelectorAll('[data-toggle="tooltip"]').forEach((element) => {
    new Tooltip(element);
  });

  // Initialize collapses
  document.querySelectorAll(".collapse").forEach((collapse) => {
    new Collapse(collapse);
  });

  // Initialize tabs
  document.querySelectorAll(".nav-tabs, .nav-pills").forEach((tabContainer) => {
    new Tabs(tabContainer);
  });
}

// Export components and initializer
export { Modal, Alert, Tooltip, Collapse, Tabs, initUIComponents };

// Auto-initialize
if (typeof window !== "undefined") {
  document.addEventListener("DOMContentLoaded", initUIComponents);
}
