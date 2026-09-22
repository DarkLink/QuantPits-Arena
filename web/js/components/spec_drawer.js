/**
 * web/js/components/spec_drawer.js
 * ================================
 * Picture-in-Picture Specification Drawer (Sidebar Panel)
 * Designed for uninterrupted reading and cross-referencing:
 *   - Non-modal slide-out side panel (desktop readers can scroll & inspect simultaneously)
 *   - Categorized filter tabs (All, Contestants, Zoo Animals, Benchmarks, Metrics)
 *   - Real-time instant search input
 *   - Deep-linking with smooth scroll and pulse highlight (openTerm)
 *   - Automatic refresh on season change
 */

window.ArenaSpecDrawer = {
  isOpen: false,
  activeCategory: "All",
  searchQuery: "",
  drawerEl: null,
  fabEl: null,

  init() {
    this.createFab();
    this.createDrawer();
  },

  createFab() {
    if (document.getElementById("arena-spec-drawer-fab")) return;
    const fab = document.createElement("button");
    fab.id = "arena-spec-drawer-fab";
    fab.className = "arena-drawer-fab";
    fab.setAttribute("aria-label", "Toggle Arena Field Guide & Spec Drawer");
    fab.setAttribute("title", "Open Season Specification Guide (Picture-in-Picture)");
    fab.innerHTML = `
      <span class="fab-icon">📖</span>
      <span class="fab-label">Field Guide</span>
    `;
    fab.addEventListener("click", () => this.toggle());
    document.body.appendChild(fab);
    this.fabEl = fab;
  },

  createDrawer() {
    if (document.getElementById("arena-spec-drawer")) return;
    const drawer = document.createElement("aside");
    drawer.id = "arena-spec-drawer";
    drawer.className = "arena-spec-drawer";
    drawer.setAttribute("aria-label", "Arena Tournament Specification Panel");
    drawer.innerHTML = `
      <div class="drawer-header">
        <div class="drawer-title-row">
          <div class="drawer-title-wrap">
            <span class="drawer-icon">📖</span>
            <h3 class="drawer-title">Arena Field Guide</h3>
          </div>
          <div class="drawer-actions">
            <button class="drawer-close-btn" id="arena-spec-drawer-close" aria-label="Close Drawer" title="Close Panel (Esc)">&times;</button>
          </div>
        </div>
        <div class="drawer-season-badge" id="arena-drawer-season-indicator">
          Season Specs Active
        </div>
        <!-- Search Input -->
        <div class="drawer-search-wrap">
          <input type="text" id="arena-drawer-search" class="drawer-search-input" placeholder="Search models, animals, benchmarks, metrics..." autocomplete="off">
        </div>
        <!-- Category Tabs -->
        <div class="drawer-tabs" id="arena-drawer-tabs">
          <button class="drawer-tab active" data-cat="All">All</button>
          <button class="drawer-tab" data-cat="Contestants">🧬 Models</button>
          <button class="drawer-tab" data-cat="Zoo Animals">🦁 Zoo</button>
          <button class="drawer-tab" data-cat="Benchmarks">⚖️ Benchmarks</button>
          <button class="drawer-tab" data-cat="Metrics">📐 Metrics</button>
        </div>
      </div>
      <!-- Scrollable Content Body -->
      <div class="drawer-body" id="arena-drawer-content">
        <!-- Rendered dynamically -->
      </div>
    `;

    document.body.appendChild(drawer);
    this.drawerEl = drawer;

    // Attach listeners
    drawer.querySelector("#arena-spec-drawer-close").addEventListener("click", () => this.close());
    
    const searchInput = drawer.querySelector("#arena-drawer-search");
    searchInput.addEventListener("input", (e) => {
      this.searchQuery = e.target.value.toLowerCase().trim();
      this.renderContent();
    });

    const tabs = drawer.querySelectorAll(".drawer-tab");
    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        this.activeCategory = tab.getAttribute("data-cat");
        this.renderContent();
      });
    });

    // Close on Escape key
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isOpen) {
        this.close();
      }
    });
  },

  open(category = null) {
    if (category) {
      this.activeCategory = category;
      const tabs = this.drawerEl.querySelectorAll(".drawer-tab");
      tabs.forEach(t => {
        if (t.getAttribute("data-cat") === category) t.classList.add("active");
        else t.classList.remove("active");
      });
    }

    this.isOpen = true;
    this.drawerEl.classList.add("open");
    this.fabEl?.classList.add("active");
    this.updateSeasonIndicator();
    this.renderContent();
  },

  close() {
    this.isOpen = false;
    this.drawerEl.classList.remove("open");
    this.fabEl?.classList.remove("active");
  },

  toggle() {
    if (this.isOpen) this.close();
    else this.open();
  },

  updateSeasonIndicator() {
    const el = document.getElementById("arena-drawer-season-indicator");
    if (!el) return;
    const adapter = window.arenaAdapter;
    const seasonMeta = adapter ? adapter.getCurrentSeasonMeta() : {};
    el.innerHTML = `
      <span class="pulse-dot"></span>
      <span>${seasonMeta.title || "Season Baseline"} Specs</span>
    `;
  },

  openTerm(termKey) {
    if (!termKey) return;
    this.open();

    const termData = window.ArenaGlossaryService ? window.ArenaGlossaryService.lookup(termKey) : null;
    if (termData && termData.category) {
      // Switch to category tab
      const catName = termData.category;
      this.activeCategory = catName === "Zoo Mechanics" ? "Zoo Animals" : catName;
      const tabs = this.drawerEl.querySelectorAll(".drawer-tab");
      tabs.forEach(t => {
        if (t.getAttribute("data-cat") === this.activeCategory || (this.activeCategory === "Zoo Animals" && t.getAttribute("data-cat") === "Zoo Animals")) {
          t.classList.add("active");
        } else {
          t.classList.remove("active");
        }
      });
      // Clear search to make sure item is visible
      this.searchQuery = "";
      const searchInput = this.drawerEl.querySelector("#arena-drawer-search");
      if (searchInput) searchInput.value = "";
      this.renderContent();
    }

    // Scroll and pulse highlight target card
    setTimeout(() => {
      const card = document.getElementById(`spec-card-${termData?.id || termKey}`);
      if (card) {
        card.scrollIntoView({ behavior: "smooth", block: "center" });
        card.classList.add("spec-card-highlight");
        setTimeout(() => {
          card.classList.remove("spec-card-highlight");
        }, 2200);
      }
    }, 120);
  },

  renderContent() {
    const contentEl = document.getElementById("arena-drawer-content");
    if (!contentEl) return;

    const dict = window.ArenaGlossaryService ? window.ArenaGlossaryService.getDictionary() : null;
    if (!dict) {
      contentEl.innerHTML = `<div class="drawer-empty">Specification dictionary not loaded.</div>`;
      return;
    }

    let items = [];
    const pushCategory = (catKey, catLabel) => {
      if (this.activeCategory !== "All" && this.activeCategory !== catLabel) return;
      for (const [k, item] of Object.entries(dict[catKey] || {})) {
        items.push({ ...item, displayCategory: catLabel });
      }
    };

    pushCategory("contestants", "Contestants");
    pushCategory("animals", "Zoo Animals");
    pushCategory("benchmarks", "Benchmarks");
    pushCategory("metrics", "Metrics");

    // Filter by search query
    if (this.searchQuery) {
      items = items.filter(it => {
        return (it.name && it.name.toLowerCase().includes(this.searchQuery)) ||
               (it.term && it.term.toLowerCase().includes(this.searchQuery)) ||
               (it.tagline && it.tagline.toLowerCase().includes(this.searchQuery)) ||
               (it.tooltip && it.tooltip.toLowerCase().includes(this.searchQuery)) ||
               (it.details && it.details.toLowerCase().includes(this.searchQuery));
      });
    }

    if (items.length === 0) {
      contentEl.innerHTML = `
        <div class="drawer-empty">
          <div style="font-size: 2rem; margin-bottom: 8px;">🔍</div>
          <div>No matching specifications found for "${this.searchQuery}".</div>
        </div>
      `;
      return;
    }

    const categoryBadgeColors = {
      "Contestants": "var(--brand-cyan)",
      "Zoo Animals": "var(--accent-purple)",
      "Benchmarks": "#fbbf24",
      "Metrics": "#34d399",
      "Zoo Mechanics": "#f472b6"
    };

    contentEl.innerHTML = items.map(item => {
      const badgeColor = categoryBadgeColors[item.category] || "var(--brand-cyan)";
      return `
        <div class="spec-card" id="spec-card-${item.id || item.term}">
          <div class="spec-card-header">
            <span class="spec-card-badge" style="color:${badgeColor}; border-color:${badgeColor}40; background:${badgeColor}15;">
              ${item.displayCategory || item.category}
            </span>
            ${item.tagline ? `<span class="spec-card-tagline">${item.tagline}</span>` : ''}
          </div>
          <h4 class="spec-card-title">${item.name || item.term}</h4>
          <p class="spec-card-summary">${item.tooltip || ''}</p>
          ${item.details ? `<div class="spec-card-details">${item.details}</div>` : ''}
        </div>
      `;
    }).join("");
  },

  // Called when active tournament season changes
  onSeasonChange() {
    this.updateSeasonIndicator();
    if (this.isOpen) {
      this.renderContent();
    }
  }
};
