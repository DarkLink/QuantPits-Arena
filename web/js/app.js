/**
 * QuantPits-Arena: Main Application Controller & Hash Router
 * Manages SPA routing, theme toggling, global filter synchronization, and view lifecycle.
 */

window.ArenaApp = {
  currentRoute: "overview",
  routeParams: {},

  init() {
    console.log("Initializing QuantPits-Arena Web App...");

    // 1. Initialize Theme
    this.initTheme();

    // 2. Initialize Global Filters
    window.ArenaFilters.render("global-filters-container");
    window.ArenaFilters.subscribe((filters) => {
      this.onFilterChange(filters);
    });

    // 3. Listen for Route Changes
    window.addEventListener("hashchange", () => this.handleRouting());

    // 4. Handle Initial Route
    this.handleRouting();

    // 5. Bind Navigation Events
    this.bindNavEvents();
  },

  initTheme() {
    const savedTheme = localStorage.getItem("arena_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    this.updateThemeButton(savedTheme);

    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    if (themeToggleBtn) {
      themeToggleBtn.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("arena_theme", newTheme);
        this.updateThemeButton(newTheme);

        // Re-render active view to refresh theme colors
        this.handleRouting();
      });
    }
  },

  updateThemeButton(theme) {
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    if (themeToggleBtn) {
      themeToggleBtn.innerHTML = theme === "dark" ? "<span>☀️</span>" : "<span>🌙</span>";
      themeToggleBtn.setAttribute("title", `Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`);
    }
  },

  parseHash() {
    const rawHash = window.location.hash.replace(/^#/, "").trim();
    if (!rawHash) {
      return { route: "overview", params: {} };
    }

    const [routePart, queryPart] = rawHash.split("?");
    const params = {};

    if (queryPart) {
      const searchParams = new URLSearchParams(queryPart);
      for (const [k, v] of searchParams.entries()) {
        params[k] = v;
      }
    }

    // Support slash-based pathing like #contestants/CONTESTANT_A, #animals/robot, #path/CONTESTANT_A_robot
    const slashParts = routePart.split("/");
    const primaryRoute = slashParts[0] || "overview";

    if (slashParts.length > 1) {
      const subId = decodeURIComponent(slashParts.slice(1).join("/"));
      if (primaryRoute === "contestants") {
        params.contestantId = subId;
      } else if (primaryRoute === "animals" || primaryRoute === "zoo") {
        params.animalId = subId;
      } else if (primaryRoute === "path" || primaryRoute === "path-detail") {
        params.pathId = subId;
      } else if (primaryRoute === "decision-audit" || primaryRoute === "archaeology") {
        params.forkId = subId;
      }
    }

    let normalizedRoute = primaryRoute;
    if (normalizedRoute === "zoo") normalizedRoute = "animals";
    if (normalizedRoute === "path") normalizedRoute = "path-detail";
    if (normalizedRoute === "archaeology") normalizedRoute = "decision-audit";

    return { route: normalizedRoute, params };
  },

  handleRouting() {
    const { route, params } = this.parseHash();
    this.currentRoute = route;
    this.routeParams = params;

    // Update active nav highlights (both segmented primary nav and secondary docs links)
    document.querySelectorAll(".nav-link, .nav-link-secondary").forEach(link => {
      const linkRoute = link.getAttribute("data-route");
      if (linkRoute === route || (route === "path-detail" && linkRoute === "leaderboard")) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Control visibility of global filter container (active ONLY in Leaderboard)
    const filterContainer = document.getElementById("global-filters-container");
    if (filterContainer) {
      if (route === "leaderboard") {
        filterContainer.style.display = "block";
      } else {
        filterContainer.style.display = "none";
      }
    }

    // Hide all views
    const viewIds = [
      "view-landing",
      "view-overview",
      "view-leaderboard",
      "view-animals",
      "view-path-detail",
      "view-contestant-detail",
      "view-decision-audit",
      "view-methodology"
    ];
    viewIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = "none";
    });

    // Render active view
    switch (route) {
      case "intro":
        this.showView("view-landing");
        window.LandingView.render("view-landing");
        break;

      case "overview":
        this.showView("view-overview");
        window.OverviewView.render("view-overview", window.ArenaFilters.currentFilters);
        break;

      case "leaderboard":
        this.showView("view-leaderboard");
        window.LeaderboardView.render("view-leaderboard", window.ArenaFilters.currentFilters);
        break;

      case "animals":
        this.showView("view-animals");
        const animalId = params.animalId || params.id || "robot";
        window.AnimalsView.render("view-animals", animalId);
        break;

      case "path-detail":
        this.showView("view-path-detail");
        const pathId = params.pathId || "CONTESTANT_B_robot";
        window.PathDetailView.render("view-path-detail", pathId);
        break;

      case "contestants":
        this.showView("view-contestant-detail");
        const contestantId = params.contestantId || "CONTESTANT_A";
        window.ContestantDetailView.render("view-contestant-detail", contestantId);
        break;

      case "decision-audit":
        this.showView("view-decision-audit");
        const forkId = params.forkId || "fork_model_selection_20260626";
        window.DecisionAuditView.render("view-decision-audit", forkId);
        break;

      case "methodology":
        this.showView("view-methodology");
        window.MethodologyView.render("view-methodology");
        break;

      default:
        this.showView("view-overview");
        window.OverviewView.render("view-overview", window.ArenaFilters.currentFilters);
        break;
    }

    // Smooth scroll to top on navigation
    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  navigate(route, params = {}) {
    let hash = `#${route}`;
    const keys = Object.keys(params);
    if (keys.length > 0) {
      const qs = keys.map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`).join("&");
      hash += `?${qs}`;
    }
    window.location.hash = hash;
  },

  showView(viewId) {
    const el = document.getElementById(viewId);
    if (el) el.style.display = "block";
  },

  onFilterChange(filters) {
    if (this.currentRoute === "leaderboard") {
      window.LeaderboardView.render("view-leaderboard", filters);
    }
  },

  bindNavEvents() {
    const mobileBtn = document.getElementById("mobile-menu-toggle");
    const navMenu = document.getElementById("nav-menu");
    if (mobileBtn && navMenu) {
      mobileBtn.addEventListener("click", () => {
        navMenu.classList.toggle("open");
      });
    }
  }
};

// Global routing and filter aliases
window.appRouter = window.ArenaApp;
window.appFilter = window.ArenaFilters;

// Start app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.ArenaApp.init();
});
