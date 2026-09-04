/**
 * web/js/components/filters.js
 * =============================
 * Global Filter Toolbar Component (English Edition)
 */

window.ArenaFilters = {
  currentFilters: {
    contestantId: "ALL",
    animalCategory: "ALL",
    significance: "ALL",
    returnFilter: "ALL",
    search: ""
  },

  listeners: [],

  getFilteredPaths() {
    return window.arenaAdapter.getFilteredPaths(this.currentFilters);
  },

  subscribe(listener) {
    this.listeners.push(listener);
  },

  notify() {
    this.listeners.forEach(fn => fn(this.currentFilters));
  },

  render(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const contestants = window.arenaAdapter.getAllContestants();
    const categories = window.arenaAdapter.getAnimalCategories();

    container.innerHTML = `
      <div class="filters-card-compact">
        <div class="filter-item">
          <label class="filter-label">Model:</label>
          <select id="filter-contestant" class="filter-select">
            <option value="ALL">All Models</option>
            ${contestants.map(c => `
              <option value="${c.id || c.contestant_id}" ${this.currentFilters.contestantId === (c.id || c.contestant_id) ? 'selected' : ''}>
                ${c.display_name || c.anonymous_name || c.contestant_id}
              </option>
            `).join('')}
          </select>
        </div>

        <div class="filter-item">
          <label class="filter-label">Category:</label>
          <select id="filter-category" class="filter-select">
            <option value="ALL">All Categories</option>
            ${categories.map(cat => `
              <option value="${cat}" ${this.currentFilters.animalCategory === cat ? 'selected' : ''}>
                ${cat}
              </option>
            `).join('')}
          </select>
        </div>

        <div class="filter-item">
          <label class="filter-label">Null Test:</label>
          <select id="filter-significance" class="filter-select">
            <option value="ALL" ${this.currentFilters.significance === 'ALL' ? 'selected' : ''}>All Paths</option>
            <option value="SIG" ${this.currentFilters.significance === 'SIG' ? 'selected' : ''}>Upper Tail (p &lt; 0.05)</option>
            <option value="NOT_SIG" ${this.currentFilters.significance === 'NOT_SIG' ? 'selected' : ''}>Within Null</option>
          </select>
        </div>

        <div class="filter-item">
          <label class="filter-label">Return:</label>
          <select id="filter-return" class="filter-select">
            <option value="ALL" ${this.currentFilters.returnFilter === 'ALL' ? 'selected' : ''}>All Returns</option>
            <option value="POSITIVE" ${this.currentFilters.returnFilter === 'POSITIVE' ? 'selected' : ''}>Positive (&gt; 0%)</option>
          </select>
        </div>

        <div class="filter-item" style="flex: 1; min-width: 170px;">
          <input type="text" id="filter-search" class="filter-input" style="width: 100%;" placeholder="Search path, model, animal..." value="${this.currentFilters.search}">
        </div>

        <button id="filter-reset-btn" class="btn btn-sm btn-outline" style="font-size: 11px; padding: 4px 10px; white-space: nowrap;">
          Reset
        </button>
      </div>
    `;

    this.bindEvents();
  },

  bindEvents() {
    const selContestant = document.getElementById("filter-contestant");
    const selCategory = document.getElementById("filter-category");
    const selSig = document.getElementById("filter-significance");
    const selReturn = document.getElementById("filter-return");
    const inpSearch = document.getElementById("filter-search");
    const btnReset = document.getElementById("filter-reset-btn");

    if (selContestant) {
      selContestant.addEventListener("change", (e) => {
        this.currentFilters.contestantId = e.target.value;
        this.notify();
      });
    }

    if (selCategory) {
      selCategory.addEventListener("change", (e) => {
        this.currentFilters.animalCategory = e.target.value;
        this.notify();
      });
    }

    if (selSig) {
      selSig.addEventListener("change", (e) => {
        this.currentFilters.significance = e.target.value;
        this.notify();
      });
    }

    if (selReturn) {
      selReturn.addEventListener("change", (e) => {
        this.currentFilters.returnFilter = e.target.value;
        this.notify();
      });
    }

    if (inpSearch) {
      let debounceTimer = null;
      inpSearch.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          this.currentFilters.search = e.target.value.trim();
          this.notify();
        }, 200);
      });
    }

    if (btnReset) {
      btnReset.addEventListener("click", () => {
        this.reset();
      });
    }
  },

  reset() {
    this.currentFilters = {
      contestantId: "ALL",
      animalCategory: "ALL",
      significance: "ALL",
      returnFilter: "ALL",
      search: ""
    };
    const c = document.getElementById("filter-contestant");
    const cat = document.getElementById("filter-category");
    const s = document.getElementById("filter-significance");
    const r = document.getElementById("filter-return");
    const q = document.getElementById("filter-search");
    if (c) c.value = "ALL";
    if (cat) cat.value = "ALL";
    if (s) s.value = "ALL";
    if (r) r.value = "ALL";
    if (q) q.value = "";
    this.notify();
  }
};
