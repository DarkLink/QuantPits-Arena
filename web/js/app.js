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

    // 0. Initialize Season Switcher & Multi-Season state
    this.initSeasonSelector();

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

  currentSeasonId: "season_01",

  initSeasonSelector() {
    const container = document.getElementById("season-switcher");
    const btn = document.getElementById("season-switcher-btn");
    const label = document.getElementById("current-season-label");
    const dropdown = document.getElementById("season-dropdown");
    if (!container || !btn || !dropdown) return;

    // Detect initial season from query or hash
    const urlParams = new URLSearchParams(window.location.search);
    const hashParams = this.parseHash().params;
    const requestedSeason = urlParams.get("season") || hashParams.season;
    if (requestedSeason) {
      this.currentSeasonId = requestedSeason;
    }

    const seasons = window.ARENA_SEASONS_INDEX || [
      { id: "season_01", title: "Season 1: Graveyard Arena", short_title: "Season 1", status: "ACTIVE" }
    ];

    // Render dropdown items
    dropdown.innerHTML = `
      <div class="season-dropdown-header">Select Arena Season</div>
      ${seasons.map(s => {
        const isSelected = s.id === this.currentSeasonId;
        const isDraft = s.status === "DRAFT";
        const badgeClass = isDraft ? "badge-draft" : "badge-active";
        return `
          <div class="season-dropdown-item ${isSelected ? 'is-selected' : ''}" data-season-id="${s.id}">
            <div class="season-item-header">
              <span class="season-item-title">${s.title}</span>
              <span class="season-item-badge ${badgeClass}">${s.status}</span>
            </div>
            <div class="season-item-desc">${s.description || ''}</div>
            <div class="season-item-meta">
              <span>📅 ${s.period}</span>
              <span>•</span>
              <span>🐾 ${s.animals_count || 29} Animals</span>
            </div>
          </div>
        `;
      }).join("")}
    `;

    // Update button text and style
    this.updateSeasonButtonUI();

    // Bind dropdown toggle
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      container.classList.toggle("is-open");
    });

    // Bind item click
    dropdown.querySelectorAll(".season-dropdown-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.stopPropagation();
        const sid = item.getAttribute("data-season-id");
        this.switchSeason(sid);
        container.classList.remove("is-open");
      });
    });

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (!container.contains(e.target)) {
        container.classList.remove("is-open");
      }
    });

    // If initial requested season differs from default, trigger switch
    if (this.currentSeasonId !== "season_01" && window.ARENA_SEASONS_DATA && window.ARENA_SEASONS_DATA[this.currentSeasonId]) {
      this.switchSeason(this.currentSeasonId, false);
    }
  },

  updateSeasonButtonUI() {
    const btn = document.getElementById("season-switcher-btn");
    const label = document.getElementById("current-season-label");
    if (!btn || !label) return;

    const seasons = window.ARENA_SEASONS_INDEX || [];
    const current = seasons.find(s => s.id === this.currentSeasonId);
    const shortTitle = current ? current.short_title : this.currentSeasonId;
    label.textContent = shortTitle;

    if (current && current.status === "DRAFT") {
      btn.classList.add("is-draft");
    } else {
      btn.classList.remove("is-draft");
    }

    // Update dropdown item selected states
    const items = document.querySelectorAll(".season-dropdown-item");
    items.forEach(it => {
      if (it.getAttribute("data-season-id") === this.currentSeasonId) {
        it.classList.add("is-selected");
      } else {
        it.classList.remove("is-selected");
      }
    });
  },

  switchSeason(seasonId, updateHistory = true) {
    if (!seasonId) return;
    this.currentSeasonId = seasonId;

    const seasonData = window.ARENA_SEASONS_DATA ? window.ARENA_SEASONS_DATA[seasonId] : null;
    if (seasonData) {
      console.log(`[ArenaApp] Switching to ${seasonId}...`);
      window.arenaAdapter = new ArenaDataAdapter(seasonData);
    } else {
      console.warn(`[ArenaApp] No data found for ${seasonId}, retaining active adapter.`);
    }

    this.updateSeasonButtonUI();
    this.updatePreviewBanner();
    this.updateTimelinessNotice();

    // Synchronize URL query parameter
    if (updateHistory) {
      try {
        const url = new URL(window.location.href);
        url.searchParams.set("season", seasonId);
        window.history.replaceState({}, "", url.toString());
      } catch (e) {
        // Fallback for older browsers
      }
    }

    // Re-render the active view with the new season data
    this.handleRouting();
  },

  async initTimelinessNotice() {
    this.updateTimelinessNotice();
  },

  updateTimelinessNotice() {
    const bannerSpan = document.getElementById("timeliness-proof-text");
    if (!bannerSpan) return;

    const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
    if (seasonMeta.timeliness_proof) {
      bannerSpan.innerHTML = seasonMeta.timeliness_proof;
      return;
    }
    const title = seasonMeta.short_title || seasonMeta.title || "Arena";
    const univ = seasonMeta.universe_name || "Universe";
    const windowLabel = seasonMeta.window_label || seasonMeta.period_label || "Active Window";
    bannerSpan.innerHTML = `🔬 <strong style="color: var(--text-secondary);">${title} Proof:</strong> ${univ} verified over ${windowLabel}. Unfalsifiable empirical null resolution.`;
  },

  initPreviewBanner() {
    this.updatePreviewBanner();
  },

  updatePreviewBanner() {
    const banner = document.getElementById("arena-preview-watermark-bar");
    const isPreview = window._ARENA_IS_PREVIEW || (window.arenaAdapter && window.arenaAdapter.isPreviewMode && window.arenaAdapter.isPreviewMode());
    const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
    const isS2Draft = seasonMeta.status === "DRAFT";

    if (!isPreview && !isS2Draft) {
      if (banner) banner.remove();
      return;
    }

    const target = banner || document.createElement("div");
    target.id = "arena-preview-watermark-bar";
    target.style.cssText = `
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

    if (isS2Draft) {
      target.innerHTML = `
        <span>⚡ <strong style="text-transform: uppercase; letter-spacing: 0.05em; background: rgba(0,0,0,0.25); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">Season 2 Calibration Preview</strong>
        Two-Phase State Machine &amp; Ghost Taotie (100M) Active &bull; Horizon: <strong>${seasonMeta.period || "2026.09 - 2026.10"}</strong></span>
        <span style="font-size: 11px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-weight: 700; border: 1px solid rgba(255,255,255,0.4);">DEVELOPMENT DRAFT</span>
      `;
    } else {
      const embargoDate = window.arenaAdapter ? window.arenaAdapter.getEmbargoDate() : "2026-09-11";
      const periodLabel = window.arenaAdapter ? window.arenaAdapter.getPeriodLabel() : "extended through 2026-09-04";
      target.innerHTML = `
        <span>⚡ <strong style="text-transform: uppercase; letter-spacing: 0.05em; background: rgba(0,0,0,0.25); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">Local Preview Mode</strong>
        ${periodLabel} &bull; Public production release embargoed until <strong>${embargoDate}</strong></span>
        <span style="font-size: 11px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-weight: 700; border: 1px solid rgba(255,255,255,0.4);">CONFIDENTIAL / UNRELEASED</span>
      `;
    }

    if (!banner) {
      document.body.prepend(target);
    }
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
    if (normalizedRoute === "contestant-detail") normalizedRoute = "contestants";

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
      "view-dispatches",
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

    // Scroll to top upon route transition
    window.scrollTo({ top: 0, behavior: "instant" });

    // Render corresponding view component
    switch (route) {
      case "landing":
        this.showView("view-landing");
        window.LandingView.render("view-landing");
        break;

      case "dispatches":
        this.showView("view-dispatches");
        window.DispatchesView.render("view-dispatches");
        break;

      case "overview":
        this.showView("view-overview");
        window.OverviewView.render("view-overview");
        break;

      case "leaderboard":
        this.showView("view-leaderboard");
        window.LeaderboardView.render("view-leaderboard");
        break;

      case "animals":
        this.showView("view-animals");
        const animalId = params.animalId || params.id || "robot";
        window.AnimalsView.render("view-animals", animalId);
        break;

      case "path-detail":
        this.showView("view-path-detail");
        const pathId = params.pathId || params.id || "CONTESTANT_B_robot";
        window.PathDetailView.render("view-path-detail", pathId);
        break;

      case "contestants":
        this.showView("view-contestant-detail");
        const contestantId = params.contestantId || params.id || "CONTESTANT_A";
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

      case "dispatches":
      case "chronicles":
      case "episodes":
        this.showView("view-dispatches");
        window.DispatchesView.render("view-dispatches", params);
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
