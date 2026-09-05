/**
 * web/js/views/leaderboard_view.js
 * ================================
 * Leaderboard & Heatmap Matrix View Component (English Edition)
 */

window.LeaderboardView = {
  activeTab: "table", // "table" or "matrix"
  sortField: "total_return_pct",
  sortAsc: false,
  matrixMetric: "total_return_pct",

  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

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
        <div class="card">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th onclick="window.LeaderboardView.handleSort('path_id')">Path ID</th>
                  <th onclick="window.LeaderboardView.handleSort('contestant_id')">Model</th>
                  <th onclick="window.LeaderboardView.handleSort('animal_id')">Execution Handler</th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('total_return_pct')">Return (%)</th>
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
            <span style="color:var(--text-muted); font-weight:600;">External Benchmark Reference Standards:</span>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
              <span>Taotie Baseline (Full-Pool Passive): <b style="color:var(--accent-positive);">+2.32%</b></span>
              <span>CSI 300 Index (SH000300): <b style="color:var(--accent-negative);">-4.81%</b></span>
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

    const sorted = [...filtered].sort((a, b) => {
      let vA = a[this.sortField];
      let vB = b[this.sortField];
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
      const pct = (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0));
      const isSig = pct >= 95.0;
      const pVal = (p.empirical_p_value !== undefined ? p.empirical_p_value : (p.p_value || 1.0));

      return `
        <tr class="clickable-row" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
          <td><b>${p.path_id}</b></td>
          <td><span class="badge badge-cyan">${p.contestant_id}</span></td>
          <td><span class="badge badge-purple">${p.animal_id}</span></td>
          <td class="numeric ${isPositive ? 'positive' : 'negative'}">
            <b>${isPositive ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b>
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
