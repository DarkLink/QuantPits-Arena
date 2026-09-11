/**
 * web/js/views/leaderboard_view.js
 * ================================
 * Leaderboard & Heatmap Matrix View Component:
 * Features multi-benchmark alpha perspective toggles, visual spread bars,
 * and cross-sectional robustness heatmaps.
 */

window.LeaderboardView = {
  activeTab: "table", // "table" or "matrix"
  sortField: "total_return_pct",
  sortAsc: false,
  viewMode: "return", // "return", "vs_taotie", "vs_ghost", "vs_csi300"
  matrixMetric: "total_return_pct",

  render(containerId) {
    this.containerId = containerId || this.containerId || "view-leaderboard";
    const el = document.getElementById(this.containerId);
    if (!el) return;

    const taotieRet = window.arenaAdapter.getTaotieReturn();
    const hasGhost = window.arenaAdapter.hasGhostTaotie();
    const ghostRet = hasGhost ? window.arenaAdapter.getGhostTaotieReturn() : null;
    const csiRet = window.arenaAdapter.getCsi300Return();

    el.innerHTML = `
      <!-- View Sub-Navigation Tabs -->
      <div class="tabs-container" style="margin-bottom: 20px;">
        <button class="tab-btn ${this.activeTab === 'table' ? 'active' : ''}" onclick="window.LeaderboardView.switchTab('table')">
          <span>📊 Full Leaderboard Table</span>
        </button>
        <button class="tab-btn ${this.activeTab === 'matrix' ? 'active' : ''}" onclick="window.LeaderboardView.switchTab('matrix')">
          <span>🗺️ Model × Animal Heatmap Matrix</span>
        </button>
      </div>

      <!-- Tab Content 1: Table View -->
      <div id="tab-content-table" style="display: ${this.activeTab === 'table' ? 'block' : 'none'};">
        <!-- Benchmark Alpha Perspective Switcher -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; padding: 10px 14px; background: rgba(30, 41, 59, 0.4); border-radius: 8px; border: 1px solid var(--border-color);">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Benchmark Perspective:</span>
            <button class="btn btn-sm ${this.viewMode === 'return' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('return')">
              📊 Absolute Return
            </button>
            <button class="btn btn-sm ${this.viewMode === 'vs_taotie' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('vs_taotie')">
              🐾 Alpha vs Taotie (${taotieRet >= 0 ? '+' : ''}${taotieRet.toFixed(2)}%)
            </button>
            ${hasGhost ? `
              <button class="btn btn-sm ${this.viewMode === 'vs_ghost' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('vs_ghost')">
                👻 Alpha vs Ghost (${ghostRet >= 0 ? '+' : ''}${ghostRet.toFixed(2)}%)
              </button>
            ` : ''}
            <button class="btn btn-sm ${this.viewMode === 'vs_csi300' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('vs_csi300')">
              🏛️ Alpha vs ${window.arenaAdapter.getMarketBenchmarkName()} (${csiRet >= 0 ? '+' : ''}${csiRet.toFixed(2)}%)
            </button>
          </div>
          <div style="font-size: 11px; color: var(--text-tertiary); font-family: monospace;">
            Showing 168 Execution Paths
          </div>
        </div>

        <div class="card">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th onclick="window.LeaderboardView.handleSort('path_id')">Path ID</th>
                  <th onclick="window.LeaderboardView.handleSort('contestant_id')">Model</th>
                  <th onclick="window.LeaderboardView.handleSort('animal_id')">Execution Handler</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('total_return_pct')">
                    ${this.getReturnColumnHeader()}
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('excess_over_monkey_pct')">Excess vs Monkey</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('percentile_rank')">Monkey Pct (%)</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('empirical_p_value')">p-value</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('max_drawdown_pct')">MDD (%)</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('sharpe_ratio')">Sharpe</th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody id="leaderboard-tbody">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
          <div style="font-size: 11px; color: var(--text-tertiary); padding: 12px 16px 4px 16px; border-top: 1px solid var(--border-subtle);">
            * Note: Return, Sharpe Ratio, and MDD are computed over <strong>${window.arenaAdapter.getPeriodLabel()}</strong>. All path statistics update dynamically across incremental evaluation cycles.
          </div>
        </div>
      </div>

      <!-- Tab Content 2: Matrix View -->
      <div id="tab-content-matrix" style="display: ${this.activeTab === 'matrix' ? 'block' : 'none'};">
        <div class="card">
          <div class="card-header" style="flex-wrap:wrap; gap:10px;">
            <div>
              <h3 class="card-title">🗺️ Cross-Sectional Performance Matrix (6 Models × 28 Handlers)</h3>
              <div class="card-subtitle">Examine structural sensitivity across models and execution variations</div>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span style="font-size:0.82rem; color:var(--text-tertiary);">Display Metric:</span>
              <select class="form-control" style="width:auto; font-size:0.82rem; padding:0.25rem 0.5rem;" onchange="window.LeaderboardView.changeMatrixMetric(this.value)">
                <option value="total_return_pct" ${this.matrixMetric === 'total_return_pct' ? 'selected' : ''}>Total Return (%)</option>
                <option value="percentile_rank" ${this.matrixMetric === 'percentile_rank' ? 'selected' : ''}>Monkey Percentile (%)</option>
                <option value="max_drawdown_pct" ${this.matrixMetric === 'max_drawdown_pct' ? 'selected' : ''}>Max Drawdown (%)</option>
                <option value="sharpe_ratio" ${this.matrixMetric === 'sharpe_ratio' ? 'selected' : ''}>Sharpe Ratio</option>
              </select>
            </div>
          </div>
          <div id="chart-leaderboard-matrix" class="chart-container" style="height: 520px;"></div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding:10px 16px; background:var(--bg-surface-elevated); border-radius:var(--radius-sm); font-size:0.8rem; border:1px solid var(--border-subtle); flex-wrap:wrap; gap:10px;">
            <span style="color:var(--text-muted); font-weight:600;">Benchmark Reference Standards:</span>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
              <span title="A capital-constrained, round-lot-constrained full-universe portfolio designed to approximate broad exposure with minimal active selection">Taotie (Executable Universe Benchmark): <b style="color:var(--accent-positive);">${taotieRet >= 0 ? '+' : ''}${taotieRet.toFixed(2)}%</b></span>
              ${hasGhost ? `
              <span title="Theoretical unconstrained equal-weight universe benchmark under CNY 100M capital">Ghost Taotie (Theoretical Equal-Weight): <b style="color:#00f0ff;">${ghostRet >= 0 ? '+' : ''}${ghostRet.toFixed(2)}%</b></span>
              ` : ''}
              <span title="External broad market index context (${window.arenaAdapter.getMarketBenchmarkCode()})">${window.arenaAdapter.getMarketBenchmarkName()} (External Market Anchor): <b style="color:var(--accent-negative);">${csiRet >= 0 ? '+' : ''}${csiRet.toFixed(2)}%</b></span>
            </div>
          </div>
        </div>
      </div>
    `;

    if (this.activeTab === "table") {
      this.renderTableBody();
    } else {
      this.renderMatrixChart();
    }
  },

  getReturnColumnHeader() {
    if (this.viewMode === "vs_taotie") return "Alpha vs Taotie (%)";
    if (this.viewMode === "vs_ghost") return "Alpha vs Ghost (%)";
    if (this.viewMode === "vs_csi300") return `Alpha vs ${window.arenaAdapter.getMarketBenchmarkName()} (%)`;
    return "Return (%)";
  },

  switchViewMode(mode) {
    this.viewMode = mode;
    this.render(this.containerId);
  },

  switchTab(tab) {
    this.activeTab = tab;
    const tabTable = document.getElementById("tab-content-table");
    const tabMatrix = document.getElementById("tab-content-matrix");
    if (tabTable) tabTable.style.display = tab === "table" ? "block" : "none";
    if (tabMatrix) tabMatrix.style.display = tab === "matrix" ? "block" : "none";

    document.querySelectorAll(".tabs-container .tab-btn").forEach((btn, idx) => {
      if ((idx === 0 && tab === "table") || (idx === 1 && tab === "matrix")) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    if (tab === "table") {
      this.renderTableBody();
    } else {
      this.renderMatrixChart();
    }
  },

  handleSort(field) {
    if (this.sortField === field) {
      this.sortAsc = !this.sortAsc;
    } else {
      this.sortField = field;
      this.sortAsc = false;
    }
    this.renderTableBody();
  },

  changeMatrixMetric(metric) {
    this.matrixMetric = metric;
    this.renderMatrixChart();
  },

  renderTableBody() {
    const tbody = document.getElementById("leaderboard-tbody");
    if (!tbody) return;

    const filtered = window.arenaAdapter.getFilteredPaths(window.ArenaFilters ? window.ArenaFilters.currentFilters : {});
    const taotieRet = window.arenaAdapter.getTaotieReturn();
    const hasGhost = window.arenaAdapter.hasGhostTaotie();
    const ghostRet = hasGhost ? window.arenaAdapter.getGhostTaotieReturn() : 0;
    const csiRet = window.arenaAdapter.getCsi300Return();

    const sorted = [...filtered].sort((a, b) => {
      let vA = a[this.sortField];
      let vB = b[this.sortField];

      if (this.sortField === "total_return_pct") {
        if (this.viewMode === "vs_taotie") {
          vA = a.total_return_pct - taotieRet;
          vB = b.total_return_pct - taotieRet;
        } else if (this.viewMode === "vs_ghost") {
          vA = a.total_return_pct - ghostRet;
          vB = b.total_return_pct - ghostRet;
        } else if (this.viewMode === "vs_csi300") {
          vA = a.total_return_pct - csiRet;
          vB = b.total_return_pct - csiRet;
        }
      }

      if (typeof vA === "string") {
        return this.sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      return this.sortAsc ? vA - vB : vB - vA;
    });

    if (sorted.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:2rem; color:var(--text-tertiary);">No paths match the selected filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = sorted.map(p => {
      const isPositive = p.total_return_pct >= 0;
      const pct = (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.monkey_percentile_rank || 0)));
      const isSig = pct >= 95.0;
      const pVal = (p.empirical_p_value !== undefined ? p.empirical_p_value : (p.p_value !== undefined ? p.p_value : 1.0));

      const alphaTao = p.total_return_pct - taotieRet;
      const alphaGhost = p.total_return_pct - ghostRet;
      const alphaCsi = p.total_return_pct - csiRet;

      let returnCellHtml = "";
      if (this.viewMode === "vs_taotie") {
        const isAlphaPos = alphaTao >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? 'var(--accent-positive)' : 'var(--accent-negative)'}; font-family: monospace;">
              ${isAlphaPos ? '+' : ''}${alphaTao.toFixed(2)}%
            </b>
            <span style="font-size: 10px; color: var(--text-tertiary);">Abs: ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</span>
          </div>
        `;
      } else if (this.viewMode === "vs_ghost") {
        const isAlphaPos = alphaGhost >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? '#00f0ff' : 'var(--accent-negative)'}; font-family: monospace;">
              ${isAlphaPos ? '+' : ''}${alphaGhost.toFixed(2)}%
            </b>
            <span style="font-size: 10px; color: var(--text-tertiary);">Abs: ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</span>
          </div>
        `;
      } else if (this.viewMode === "vs_csi300") {
        const isAlphaPos = alphaCsi >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? 'var(--accent-positive)' : 'var(--accent-negative)'}; font-family: monospace;">
              ${isAlphaPos ? '+' : ''}${alphaCsi.toFixed(2)}%
            </b>
            <span style="font-size: 10px; color: var(--text-tertiary);">Abs: ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</span>
          </div>
        `;
      } else {
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b class="${isPositive ? 'positive' : 'negative'}">
              ${isPositive ? '+' : ''}${p.total_return_pct.toFixed(2)}%
            </b>
            <span style="font-size: 10px; color: var(--text-muted); font-family: monospace;">
              α_Tao: ${alphaTao >= 0 ? '+' : ''}${alphaTao.toFixed(1)}%
            </span>
          </div>
        `;
      }

      return `
        <tr class="clickable-row" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
          <td><b>${p.path_id}</b></td>
          <td><span class="badge badge-cyan">${p.contestant_id}</span></td>
          <td><span class="badge badge-purple">${p.animal_id}</span></td>
          <td class="numeric">
            ${returnCellHtml}
          </td>
          <td class="numeric ${p.excess_over_monkey_pct >= 0 ? 'positive' : 'negative'}">
            ${p.excess_over_monkey_pct >= 0 ? '+' : ''}${p.excess_over_monkey_pct.toFixed(2)}%
          </td>
          <td class="numeric">
            <span class="badge ${isSig ? 'badge-green' : 'badge-neutral'}">
              ${window.formatPercentile ? window.formatPercentile(pct) : pct.toFixed(1) + '%'}
            </span>
          </td>
          <td class="numeric" style="font-family:monospace; color:${isSig ? 'var(--accent-positive)' : 'var(--text-tertiary)'};">
            ${window.formatPValue ? window.formatPValue(pVal) : pVal.toFixed(4)}
          </td>
          <td class="numeric" style="color:var(--accent-negative);">
            ${p.max_drawdown_pct.toFixed(2)}%
          </td>
          <td class="numeric">${p.sharpe_ratio || '-'}</td>
          <td>
            <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
              ${(p.badges || []).map(b => `<span class="badge badge-neutral" style="font-size:0.65rem;">${b}</span>`).join("")}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  renderMatrixChart() {
    const matrixData = window.arenaAdapter.matrix;
    setTimeout(() => {
      window.ArenaCharts.renderHeatmap("chart-leaderboard-matrix", matrixData, this.matrixMetric, path => {
        window.appRouter.navigate("path-detail", { pathId: path.path_id });
      });
    }, 50);
  }
};
