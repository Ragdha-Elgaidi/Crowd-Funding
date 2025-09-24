/**
 * Navigation Module
 * Handles navigation functionality including mobile menu and dropdowns
 */

import { debounce } from "../utils/helpers.js";

class Navigation {
  constructor() {
    this.navbar = document.querySelector(".navbar");
    this.navbarToggle = document.querySelector(".navbar-toggle");
    this.navbarNav = document.querySelector(".navbar-nav");
    this.dropdowns = document.querySelectorAll(".dropdown");
    this.searchForm = document.querySelector(".navbar-search form");

    this.init();
  }

  /**
   * Initialize navigation functionality
   */
  init() {
    this.setupMobileToggle();
    this.setupDropdowns();
    this.setupScrollBehavior();
    this.setupKeyboardNavigation();
    this.setupSearchForm();
  }

  /**
   * Setup mobile navigation toggle
   */
  setupMobileToggle() {
    if (!this.navbarToggle || !this.navbarNav) return;

    this.navbarToggle.addEventListener("click", (e) => {
      e.preventDefault();
      this.toggleMobileMenu();
    });

    // Close mobile menu when clicking outside
    document.addEventListener("click", (e) => {
      if (
        !this.navbar.contains(e.target) &&
        this.navbarNav.classList.contains("show")
      ) {
        this.closeMobileMenu();
      }
    });

    // Close mobile menu on window resize
    window.addEventListener(
      "resize",
      debounce(() => {
        if (
          window.innerWidth > 768 &&
          this.navbarNav.classList.contains("show")
        ) {
          this.closeMobileMenu();
        }
      }, 250)
    );
  }

  /**
   * Toggle mobile menu visibility
   */
  toggleMobileMenu() {
    this.navbarNav.classList.toggle("show");
    this.navbarToggle.setAttribute(
      "aria-expanded",
      this.navbarNav.classList.contains("show")
    );

    // Close any open dropdowns when toggling mobile menu
    this.closeAllDropdowns();
  }

  /**
   * Close mobile menu
   */
  closeMobileMenu() {
    this.navbarNav.classList.remove("show");
    this.navbarToggle.setAttribute("aria-expanded", "false");
    this.closeAllDropdowns();
  }

  /**
   * Setup dropdown functionality
   */
  setupDropdowns() {
    this.dropdowns.forEach((dropdown) => {
      const toggle = dropdown.querySelector(".dropdown-toggle");
      const menu = dropdown.querySelector(".dropdown-menu");

      if (!toggle || !menu) return;

      // Click toggle
      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggleDropdown(dropdown);
      });

      // Keyboard navigation
      toggle.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          this.toggleDropdown(dropdown);
        } else if (e.key === "ArrowDown") {
          e.preventDefault();
          this.openDropdown(dropdown);
          this.focusFirstMenuItem(dropdown);
        }
      });

      // Menu item keyboard navigation
      const menuItems = menu.querySelectorAll(".dropdown-item");
      menuItems.forEach((item, index) => {
        item.addEventListener("keydown", (e) => {
          this.handleMenuItemKeydown(e, dropdown, index);
        });
      });
    });

    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
      this.closeAllDropdowns();
    });
  }

  /**
   * Toggle dropdown visibility
   * @param {Element} dropdown - Dropdown element
   */
  toggleDropdown(dropdown) {
    const isOpen = dropdown.classList.contains("show");

    // Close all other dropdowns
    this.closeAllDropdowns();

    if (!isOpen) {
      this.openDropdown(dropdown);
    }
  }

  /**
   * Open dropdown
   * @param {Element} dropdown - Dropdown element
   */
  openDropdown(dropdown) {
    dropdown.classList.add("show");
    const toggle = dropdown.querySelector(".dropdown-toggle");
    toggle.setAttribute("aria-expanded", "true");
  }

  /**
   * Close dropdown
   * @param {Element} dropdown - Dropdown element
   */
  closeDropdown(dropdown) {
    dropdown.classList.remove("show");
    const toggle = dropdown.querySelector(".dropdown-toggle");
    toggle.setAttribute("aria-expanded", "false");
  }

  /**
   * Close all dropdowns
   */
  closeAllDropdowns() {
    this.dropdowns.forEach((dropdown) => {
      this.closeDropdown(dropdown);
    });
  }

  /**
   * Focus first menu item in dropdown
   * @param {Element} dropdown - Dropdown element
   */
  focusFirstMenuItem(dropdown) {
    const firstItem = dropdown.querySelector(".dropdown-item");
    if (firstItem) {
      firstItem.focus();
    }
  }

  /**
   * Handle keyboard navigation in dropdown menu
   * @param {KeyboardEvent} e - Keyboard event
   * @param {Element} dropdown - Dropdown element
   * @param {number} currentIndex - Current item index
   */
  handleMenuItemKeydown(e, dropdown, currentIndex) {
    const menuItems = Array.from(dropdown.querySelectorAll(".dropdown-item"));

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % menuItems.length;
        menuItems[nextIndex].focus();
        break;

      case "ArrowUp":
        e.preventDefault();
        const prevIndex =
          currentIndex === 0 ? menuItems.length - 1 : currentIndex - 1;
        menuItems[prevIndex].focus();
        break;

      case "Escape":
        e.preventDefault();
        this.closeDropdown(dropdown);
        dropdown.querySelector(".dropdown-toggle").focus();
        break;

      case "Tab":
        this.closeDropdown(dropdown);
        break;
    }
  }

  /**
   * Setup navbar scroll behavior
   */
  setupScrollBehavior() {
    let lastScrollTop = 0;
    let ticking = false;

    const handleScroll = () => {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;

      // Add/remove scrolled class for styling
      if (scrollTop > 50) {
        this.navbar.classList.add("navbar-scrolled");
      } else {
        this.navbar.classList.remove("navbar-scrolled");
      }

      // Hide/show navbar on scroll (optional)
      if (Math.abs(lastScrollTop - scrollTop) <= 5) return;

      if (scrollTop > lastScrollTop && scrollTop > 100) {
        // Scrolling down
        this.navbar.classList.add("navbar-hidden");
      } else {
        // Scrolling up
        this.navbar.classList.remove("navbar-hidden");
      }

      lastScrollTop = scrollTop;
      ticking = false;
    };

    window.addEventListener("scroll", () => {
      if (!ticking) {
        requestAnimationFrame(handleScroll);
        ticking = true;
      }
    });
  }

  /**
   * Setup keyboard navigation for accessibility
   */
  setupKeyboardNavigation() {
    // Skip to content link
    const skipLink = document.querySelector(".skip-to-content");
    if (skipLink) {
      skipLink.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.querySelector(skipLink.getAttribute("href"));
        if (target) {
          target.focus();
          target.scrollIntoView({ behavior: "smooth" });
        }
      });
    }

    // Handle escape key to close mobile menu and dropdowns
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeMobileMenu();
        this.closeAllDropdowns();
      }
    });
  }

  /**
   * Setup search form in navigation
   */
  setupSearchForm() {
    if (!this.searchForm) return;

    const searchInput = this.searchForm.querySelector('input[type="text"]');
    const searchButton = this.searchForm.querySelector('button[type="submit"]');

    if (searchInput) {
      // Add search icon toggle for mobile
      searchInput.addEventListener("focus", () => {
        this.searchForm.classList.add("search-focused");
      });

      searchInput.addEventListener("blur", () => {
        if (!searchInput.value.trim()) {
          this.searchForm.classList.remove("search-focused");
        }
      });

      // Handle keyboard shortcuts
      document.addEventListener("keydown", (e) => {
        // Focus search on Ctrl+K or Cmd+K
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
          e.preventDefault();
          searchInput.focus();
        }
      });
    }
  }

  /**
   * Add navigation item programmatically
   * @param {Object} item - Navigation item configuration
   */
  addNavItem(item) {
    if (!this.navbarNav) return;

    const navItem = document.createElement("li");
    navItem.className = "nav-item";

    const navLink = document.createElement("a");
    navLink.className = "nav-link";
    navLink.href = item.href || "#";
    navLink.textContent = item.text;

    if (item.active) {
      navLink.classList.add("active");
    }

    if (item.external) {
      navLink.target = "_blank";
      navLink.rel = "noopener noreferrer";
    }

    navItem.appendChild(navLink);
    this.navbarNav.appendChild(navItem);
  }

  /**
   * Update active navigation item
   * @param {string} href - URL or href to mark as active
   */
  setActiveNavItem(href) {
    const navLinks = this.navbarNav.querySelectorAll(".nav-link");

    navLinks.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === href) {
        link.classList.add("active");
      }
    });
  }

  /**
   * Show notification badge on navigation item
   * @param {string} selector - CSS selector for navigation item
   * @param {number} count - Notification count
   */
  showNotificationBadge(selector, count) {
    const navItem = this.navbarNav.querySelector(selector);
    if (!navItem) return;

    let badge = navItem.querySelector(".notification-badge");
    if (!badge) {
      badge = document.createElement("span");
      badge.className = "notification-badge";
      navItem.style.position = "relative";
      navItem.appendChild(badge);
    }

    if (count > 0) {
      badge.textContent = count > 99 ? "99+" : count.toString();
      badge.style.display = "inline-block";
    } else {
      badge.style.display = "none";
    }
  }

  /**
   * Destroy navigation instance
   */
  destroy() {
    // Remove event listeners
    if (this.navbarToggle) {
      this.navbarToggle.removeEventListener("click", this.toggleMobileMenu);
    }

    this.dropdowns.forEach((dropdown) => {
      const toggle = dropdown.querySelector(".dropdown-toggle");
      if (toggle) {
        toggle.removeEventListener("click", this.toggleDropdown);
      }
    });
  }
}

// Initialize navigation when DOM is loaded
export default function initNavigation() {
  return new Navigation();
}

// Auto-initialize if not using modules
if (typeof window !== "undefined" && !window.navigationModule) {
  document.addEventListener("DOMContentLoaded", () => {
    window.navigationModule = initNavigation();
  });
}
