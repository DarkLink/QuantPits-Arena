/**
 * QuantPits-Arena: Main Application Controller & Hash Router
 * Manages SPA routing, theme toggling, global filter synchronization, and view lifecycle.
 */

window.ArenaApp = {
  currentRoute: "overview",
  routeParams: {},

  init() {
    console.log("Initializing QuantPits-Arena Web App...");

    // 0. Initialize Local Preview Watermark (if preview data present)
    this.initPreviewBanner();

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

    // 6. Initialize Proof of Timeliness notice from commitments.json
    this.initTimelinessNotice();
  },

  async initTimelinessNotice() {
    try {
      const bannerSpan = document.getElementById("timeliness-proof-text");
      if (!bannerSpan) return;
      const res = await fetch("js/data/commitments.json?v=3.0");
      if (!res.ok) return;
      const data = await res.json();
      const list = data.commitments || [];
      const latest = list.length > 0 ? list[list.length - 1] : null;
      if (!latest) return;

      const hashShort = (latest.sha256_digests?.daily_nav_curves_csv || "").slice(0, 8);
      const commitDate = (latest.committed_at || "").split("T")[0];
      bannerSpan.innerHTML = `🔐 <strong style="color: var(--text-secondary);">Proof of Timeliness:</strong> Next cycle (through ${latest.cutoff_date}) cryptographically committed on ${commitDate} (<code style="font-size: 10px; color: var(--brand-cyan);">SHA-256: ${hashShort}...</code>). Public reveal embargoed until ${latest.embargo_until}.`;
    } catch (e) {
      // Graceful fallback to static HTML
    }
  },

  initPreviewBanner() {
    const isPreview = window._ARENA_IS_PREVIEW || (window.arenaAdapter && window.arenaAdapter.isPreviewMode && window.arenaAdapter.isPreviewMode());
    if (!isPreview) return;

    if (document.getElementById("arena-preview-watermark-bar")) return;

    const banner = document.createElement("div");
    banner.id = "arena-preview-watermark-bar";
    banner.style.cssText = `
      background: linear-gradient(90deg, #d97706, #b45309);
      color: #ffffff;
      font-weight: 600;
      font-size: 12px;
      padding: 7px 16px;
      text-align: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      position: sticky;
      top: 0;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 10px;
      letter-spacing: 0.02em;
    `;

    const embargoDate = window.arenaAdapter ? window.arenaAdapter.getEmbargoDate() : "2026-09-11";
    const periodLabel = window.arenaAdapter ? window.arenaAdapter.getPeriodLabel() : "extended through 2026-09-04";

    banner.innerHTML = `
      <span>⚡ <strong style="text-transform: uppercase; letter-spacing: 0.05em; background: rgba(0,0,0,0.25); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">Local Preview Mode</strong>
      ${periodLabel} &bull; Public production release embargoed until <strong>${embargoDate}</strong></span>
      <span style="font-size: 11px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-weight: 700; border: 1px solid rgba(255,255,255,0.4);">CONFIDENTIAL / UNRELEASED</span>
    `;

    document.body.prepend(banner);
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

        // Synchronize Giscus comments theme
        if (window.DiscussionView && window.DiscussionView.isGiscusLoaded) {
          window.DiscussionView.syncTheme();
        }
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

    // Update active nav highlights (segmented desktop nav, secondary nav, mobile drawer, and mobile subnav)
    document.querySelectorAll(".nav-link, .nav-link-secondary, .mobile-nav-link, .mobile-subnav-link").forEach(link => {
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
      "view-methodology",
      "view-disclaimer",
      "view-discussion"
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

      case "disclaimer":
        this.showView("view-disclaimer");
        window.DisclaimerView.render("view-disclaimer");
        break;

      case "discussion":
      case "comments":
        this.showView("view-discussion");
        window.DiscussionView.render("view-discussion");
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
    const drawer = document.getElementById("mobile-nav-drawer");
    if (mobileBtn && drawer) {
      mobileBtn.addEventListener("click", () => {
        const isOpen = drawer.classList.toggle("open");
        mobileBtn.classList.toggle("active", isOpen);
        mobileBtn.innerHTML = isOpen ? "<span>✕</span>" : "<span>☰</span>";
      });
    }

    // Auto-close drawer on navigation click
    document.querySelectorAll(".mobile-nav-link, .mobile-subnav-link").forEach(link => {
      link.addEventListener("click", () => {
        if (drawer) {
          drawer.classList.remove("open");
          if (mobileBtn) {
            mobileBtn.classList.remove("active");
            mobileBtn.innerHTML = "<span>☰</span>";
          }
        }
      });
    });
  }
};

// Global routing and filter aliases
window.appRouter = window.ArenaApp;
window.appFilter = window.ArenaFilters;

// Start app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.ArenaApp.init();
});
