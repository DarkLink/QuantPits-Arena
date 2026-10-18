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
    window.ArenaCharts.beginViewRender(el);
    this.updateFilterVisibility();

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
              🐾 Alpha vs Taotie (${taotieRet >= 0 ? '+' : ''}${window.formatNumber(taotieRet, 2, '%')})
            </button>
            ${hasGhost ? `
              <button class="btn btn-sm ${this.viewMode === 'vs_ghost' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('vs_ghost')">
                👻 Alpha vs Ghost (${ghostRet >= 0 ? '+' : ''}${window.formatNumber(ghostRet, 2, '%')})
              </button>
            ` : ''}
            <button class="btn btn-sm ${this.viewMode === 'vs_csi300' ? 'btn-primary' : 'btn-secondary'}" onclick="window.LeaderboardView.switchViewMode('vs_csi300')">
              🏛️ Alpha vs ${window.arenaAdapter.getMarketBenchmarkName()} (${csiRet >= 0 ? '+' : ''}${window.formatNumber(csiRet, 2, '%')})
            </button>
          </div>
          <div style="font-size: 11px; color: var(--text-tertiary); font-family: monospace;">
            Full-season paths and separately labeled observations
          </div>
        </div>

        <div class="card">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th onclick="window.LeaderboardView.handleSort('path_id')">Path ID</th>
                  <th onclick="window.LeaderboardView.handleSort('contestant_id')">
                    <span class="arena-glossary-term" data-tooltip-term="CONTESTANT_A">Model</span>
                  </th>
                  <th onclick="window.LeaderboardView.handleSort('animal_id')">
                    <span class="arena-glossary-term" data-tooltip-term="robot">Execution Handler</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('total_return_pct')">
                    <span class="arena-glossary-term" data-tooltip-term="total_return_pct">${this.getReturnColumnHeader()}</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('excess_over_monkey_pct')">
                    <span class="arena-glossary-term" data-tooltip-term="monkeys">Excess vs Monkey (pp)</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('percentile_rank')">
                    <span class="arena-glossary-term" data-tooltip-term="monkey_percentile">Monkey %ile</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('empirical_p_value')">
                    <span class="arena-glossary-term" data-tooltip-term="empirical_p_value">p-value</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('max_drawdown_pct')">
                    <span class="arena-glossary-term" data-tooltip-term="max_drawdown_pct">MDD (%)</span>
                  </th>
                  <th class="numeric" onclick="window.LeaderboardView.handleSort('sharpe_ratio')">
                    <span class="arena-glossary-term" data-tooltip-term="sharpe_ratio">Sharpe</span>
                  </th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody id="leaderboard-tbody">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
          <div style="font-size: 11px; color: var(--text-tertiary); padding: 12px 16px 4px 16px; border-top: 1px solid var(--border-subtle);">
            * Full-season paths cover <strong>${window.arenaAdapter.getPeriodLabel()}</strong>. Later entrants use their labeled observation windows and have no full-season rank. Missing statistics are N/A; use Compare Participants for a common-window comparison.
          </div>
        </div>
      </div>

      <!-- Tab Content 2: Matrix View -->
      <div id="tab-content-matrix" style="display: ${this.activeTab === 'matrix' ? 'block' : 'none'};">
        <div class="card">
          <div class="card-header" style="flex-wrap:wrap; gap:10px;">
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <h3 class="card-title">🗺️ Participant Performance Matrix</h3>
                <button class="chart-spec-pill" onclick="window.ArenaSpecDrawer && window.ArenaSpecDrawer.open('Zoo Animals')">
                  <span>🦁 Zoo Specs</span>
                </button>
              </div>
              <div class="card-subtitle">Each participant retains its own observation period. Full-season paths: ${window.arenaAdapter.getNavDates()[0]} → ${window.arenaAdapter.getNavDates().at(-1)}; later entry dates are labeled on the rows. Unavailable statistics are N/A. Use <a href="#decision-audit">Compare Participants</a> for a common-window comparison.</div>
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
            <span style="color:var(--text-muted); font-weight:600;">Full-season Benchmark References:</span>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
              <span><span class="arena-glossary-term" data-tooltip-term="taotie">Taotie (Executable Universe Benchmark)</span>: <b style="color:var(--accent-positive);">${taotieRet >= 0 ? '+' : ''}${window.formatNumber(taotieRet, 2, '%')}</b></span>
              ${hasGhost ? `
              <span><span class="arena-glossary-term" data-tooltip-term="ghost_taotie">Ghost Taotie (Theoretical Equal-Weight)</span>: <b style="color:#00f0ff;">${ghostRet >= 0 ? '+' : ''}${window.formatNumber(ghostRet, 2, '%')}</b></span>
              ` : ''}
              <span><span class="arena-glossary-term" data-tooltip-term="market">${window.arenaAdapter.getMarketBenchmarkName()} (External Market Anchor)</span>: <b style="color:var(--accent-negative);">${csiRet >= 0 ? '+' : ''}${window.formatNumber(csiRet, 2, '%')}</b></span>
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
    if (this.viewMode === "vs_taotie") return "Alpha vs Taotie (pp)";
    if (this.viewMode === "vs_ghost") return "Alpha vs Ghost (pp)";
    if (this.viewMode === "vs_csi300") return `Alpha vs ${window.arenaAdapter.getMarketBenchmarkName()} (pp)`;
    return "Return (%)";
  },

  switchViewMode(mode) {
    this.viewMode = mode;
    this.render(this.containerId);
  },

  switchTab(tab) {
    this.activeTab = tab;
    this.updateFilterVisibility();
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

  updateFilterVisibility() {
    const container = document.getElementById('global-filters-container');
    if (container) container.style.display = this.activeTab === 'table' ? 'block' : 'none';
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
    const referenceId = {vs_taotie:'BENCHMARK_taotie', vs_ghost:'BENCHMARK_ghost_taotie', vs_csi300:'BENCHMARK_csi300'}[this.viewMode];
    const excess = (path, reference) => {
      const benchmark = window.arenaAdapter.getBenchmarkReturnForPath(path, reference);
      return Number.isFinite(benchmark) && Number.isFinite(path.total_return_pct) ? path.total_return_pct - benchmark : null;
    };
    const formatSpread = (value, digits = 2) => Number.isFinite(value)
      ? `${value >= 0 ? '+' : ''}${value.toFixed(digits)} pp` : 'N/A';

    const sorted = [...filtered].sort((a, b) => {
      if (a.full_season_eligible !== b.full_season_eligible) return a.full_season_eligible === false ? 1 : -1;
      if (a.observation_start && b.observation_start && a.observation_start !== b.observation_start) return a.observation_start.localeCompare(b.observation_start);
      let vA = a[this.sortField];
      let vB = b[this.sortField];

      if (this.sortField === "total_return_pct" && referenceId) {
        vA = excess(a, referenceId);
        vB = excess(b, referenceId);
      }

      if (typeof vA === "string") {
        return this.sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
      }
      const missingA = !Number.isFinite(vA), missingB = !Number.isFinite(vB);
      if (missingA || missingB) return missingA === missingB ? 0 : missingA ? 1 : -1;
      return this.sortAsc ? vA - vB : vB - vA;
    });

    if (sorted.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:2rem; color:var(--text-tertiary);">No paths match the selected filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = sorted.map(p => {
      const isPositive = p.total_return_pct >= 0;
      const pct = p.percentile_rank ?? p.monkey_percentile ?? p.monkey_percentile_rank ?? null;
      const isSig = p.empirical_p_value != null && p.empirical_p_value < 0.05;
      const pVal = p.empirical_p_value ?? p.p_value ?? null;

      const alphaTao = excess(p, 'BENCHMARK_taotie');
      const alphaGhost = excess(p, 'BENCHMARK_ghost_taotie');
      const alphaCsi = excess(p, 'BENCHMARK_csi300');

      let returnCellHtml = "";
      if (this.viewMode === "vs_taotie") {
        const isAlphaPos = alphaTao >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? 'var(--accent-positive)' : 'var(--accent-negative)'}; font-family: monospace;">
              ${formatSpread(alphaTao)}
            </b>
            <span style="font-size: 10px; color: var(--text-tertiary);">Abs: ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</span>
          </div>
        `;
      } else if (this.viewMode === "vs_ghost") {
        const isAlphaPos = alphaGhost >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? '#00f0ff' : 'var(--accent-negative)'}; font-family: monospace;">
              ${formatSpread(alphaGhost)}
            </b>
            <span style="font-size: 10px; color: var(--text-tertiary);">Abs: ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</span>
          </div>
        `;
      } else if (this.viewMode === "vs_csi300") {
        const isAlphaPos = alphaCsi >= 0;
        returnCellHtml = `
          <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <b style="color: ${isAlphaPos ? 'var(--accent-positive)' : 'var(--accent-negative)'}; font-family: monospace;">
              ${formatSpread(alphaCsi)}
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
              α_Tao: ${formatSpread(alphaTao, 1)}
            </span>
          </div>
        `;
      }

      if (p.observation_start) {
        returnCellHtml += `<small style="display:block">Own observation window</small>`;
      }

      return `
        <tr class="clickable-row" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
          <td><b>${p.path_id}</b></td>
          <td><span class="badge badge-cyan">${p.contestant_id}</span>${p.observation_start ? `<small style="display:block">Observation since ${p.observation_start} · full-season rank N/A</small>` : ''}</td>
          <td><span class="badge badge-purple">${p.animal_id}</span></td>
          <td class="numeric">
            ${returnCellHtml}
          </td>
          <td class="numeric ${p.excess_over_monkey_pct >= 0 ? 'positive' : 'negative'}">
            ${p.excess_over_monkey_pct == null ? 'N/A' : (p.excess_over_monkey_pct >= 0 ? '+' : '')+p.excess_over_monkey_pct.toFixed(2)+' pp'}
          </td>
          <td class="numeric">
            <span class="badge ${isSig ? 'badge-green' : 'badge-neutral'}">
              ${window.formatPercentile ? window.formatPercentile(pct, p.monkey_count) : window.formatNumber(pct, 1, '%')}
            </span>
          </td>
          <td class="numeric" style="font-family:monospace; color:${isSig ? 'var(--accent-positive)' : 'var(--text-tertiary)'};">
            ${window.formatPValue ? window.formatPValue(pVal) : window.formatNumber(pVal, 4)}
          </td>
          <td class="numeric" style="color:var(--accent-negative);">
            ${window.formatNumber(p.max_drawdown_pct, 2, '%')}
          </td>
          <td class="numeric">${window.formatNumber(p.sharpe_ratio)}</td>
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
    const isCurrent = window.ArenaCharts.beginViewRender(document.getElementById('chart-leaderboard-matrix'));
    setTimeout(() => {
      if (!isCurrent()) return;
      window.ArenaCharts.renderHeatmap("chart-leaderboard-matrix", matrixData, this.matrixMetric, path => {
        window.appRouter.navigate("path-detail", { pathId: path.path_id });
      });
    }, 50);
  }
};
