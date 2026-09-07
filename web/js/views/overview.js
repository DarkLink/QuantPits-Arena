/**
 * web/js/views/overview.js
 * ========================
 * Arena Overview View:
 * 6 KPI Cards + Interactive Scatter Plot (Return vs. Monkey Percentile) + Outperformers & Laggards.
 */

window.OverviewView = {
  activeFilterGroup: "top5",
  activeFocusModel: "all",
  activeMetricMode: "nav",

  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const kpis = window.arenaAdapter.getGlobalKPIs();
    const allPaths = window.arenaAdapter.getAllPaths().filter(p => p.contestant_id !== "BENCHMARK");

    // Top 5 and Bottom 5 paths
    const sorted = [...allPaths].sort((a, b) => b.total_return_pct - a.total_return_pct);
    const top5 = sorted.slice(0, 5);
    const bottom5 = sorted.slice(-5).reverse();

    const seasonMeta = window.arenaAdapter.getCurrentSeasonMeta();
    const banner = seasonMeta.dispatches_banner || {
      tag: "🎙️ Tournament Dispatches",
      title: "Tournament Dispatches & Market Climate active.",
      link: "#dispatches",
      link_text: "Read Dispatches &rarr;"
    };

    el.innerHTML = `
      <!-- Tournament Dispatches & Climate Alert Banner -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-subtle); border-left: 4px solid var(--brand-cyan); border-radius: 6px; padding: 10px 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
          <span>${banner.tag.split(" ")[0] || "🎙️"}</span>
          <span>${banner.title}</span>
        </div>
        <a href="${banner.link}" class="btn btn-xs btn-primary" style="font-size: 11px; padding: 4px 10px; text-decoration: none;">
          ${banner.link_text}
        </a>
      </div>

      <!-- Candidate Strategy Highlights (Clean 4-column Grid) -->
      <div class="kpi-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 14px;">
        <div class="kpi-card">
          <div class="kpi-label">Active Strategy Paths</div>
          <div class="kpi-value">${kpis.totalPaths}</div>
          <div class="kpi-subtext">6 Model Candidates × 28 Zoo Handlers</div>
        </div>
        <div class="kpi-card positive">
          <div class="kpi-label">Upper Tail vs Null (p &lt; 0.05)</div>
          <div class="kpi-value positive">${kpis.statSignificantCount}</div>
          <div class="kpi-subtext">${kpis.statSignificantPct} exceed 95th %ile of matched nulls</div>
        </div>
        <div class="kpi-card positive">
          <div class="kpi-label">Peak OOS Return</div>
          <div class="kpi-value positive">+${kpis.topReturn.toFixed(2)}%</div>
          <div class="kpi-subtext">Top performer across ${window.arenaAdapter.getTradingDays()} trading days</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Median OOS Return</div>
          <div class="kpi-value" style="color:#38bdf8;">+${kpis.medianReturn.toFixed(2)}%</div>
          <div class="kpi-subtext">Cross-path median performance</div>
        </div>
      </div>

      <!-- Benchmark Baseline Reference Standards Strip (Dedicated Full-Width Row) -->
      <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 12px 18px; margin-bottom: 22px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 11px; font-weight: 700; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em;">
            Benchmark Reference Standards:
          </span>
        </div>
        <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 8px;" title="Executable baseline: CNY 500k capital, 100-share trading lot friction">
            <span class="bm-line-badge" style="border-top-color: #c084fc; width: 14px;"></span>
            <span style="font-size: 12px; color: var(--text-secondary);">Taotie (Physical Baseline 500k):</span>
            <b style="font-size: 13px; font-family: monospace; color: #c084fc;">+${kpis.taotieReturn.toFixed(2)}%</b>
          </div>
          ${window.arenaAdapter.hasGhostTaotie() ? `
          <div style="display: flex; align-items: center; gap: 8px;" title="Theoretical equal-weight baseline: CNY 100M institutional capital, zero lot friction">
            <span class="bm-line-badge" style="border-top-color: #00f0ff; width: 14px;"></span>
            <span style="font-size: 12px; color: var(--text-secondary);">Ghost Taotie (Theoretical Equal-Weight 100M):</span>
            <b style="font-size: 13px; font-family: monospace; color: #00f0ff;">+${window.arenaAdapter.getGhostTaotieReturn().toFixed(2)}%</b>
          </div>
          ` : ''}
          <div style="display: flex; align-items: center; gap: 8px;" title="External broad market equity anchor (SH000300)">
            <span class="bm-line-badge" style="border-top-color: #f59e0b; width: 14px;"></span>
            <span style="font-size: 12px; color: var(--text-secondary);">CSI 300 (Market Benchmark):</span>
            <b style="font-size: 13px; font-family: monospace; color: #f59e0b;">${kpis.csi300Return.toFixed(2)}%</b>
          </div>
        </div>
        <div style="font-size: 11px; color: var(--text-tertiary);">
          * Evaluated over <strong>${window.arenaAdapter.getPeriodLabel()}</strong>
        </div>
      </div>

      <!-- Arena Horizon & Benchmark Zoo Trajectories (Macro Panorama) -->
      <div class="card" style="margin-bottom: 24px; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 16px;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.25rem;">🌐</span>
              <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">
                Arena Horizon &amp; Benchmark Zoo Trajectories
              </h3>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
              Multi-line trajectory panorama comparing model strategies against Taotie (500k), ${window.arenaAdapter.hasGhostTaotie() ? 'Ghost Taotie (100M), ' : ''}and CSI 300
            </div>
          </div>

          <!-- Controls: Metric Mode, Model Focus & Filter Group -->
          <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <!-- Model Focus Filter -->
            <div class="filter-group" style="display: flex; align-items: center; gap: 6px;">
              <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Model Focus:</span>
              <select id="panorama-model-focus-select" class="form-control" style="font-size: 11px; padding: 3px 8px; width: auto; background: rgba(15,23,42,0.8); border: 1px solid var(--border-subtle); color: var(--text-primary); border-radius: 4px;">
                <option value="all" ${this.activeFocusModel === 'all' ? 'selected' : ''}>All Contestant Models</option>
                ${window.arenaAdapter.getAllContestants().map(c => `
                  <option value="${c.id}" ${this.activeFocusModel === c.id ? 'selected' : ''}>${c.display_name || c.id}</option>
                `).join('')}
              </select>
            </div>

            <!-- Cohort Preset Filter Select -->
            <div class="filter-group" style="display: flex; align-items: center; gap: 6px;">
              <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Cohort:</span>
              <div class="chart-metric-btn-group" id="panorama-cohort-btn-group">
                <button class="chart-metric-btn ${this.activeFilterGroup === 'top5' ? 'active' : ''}" data-cohort="top5">Top Leaders</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'robot' ? 'active' : ''}" data-cohort="robot">Robots (22/3)</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'sloth' ? 'active' : ''}" data-cohort="sloth">Sloths (Lag)</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'snail' ? 'active' : ''}" data-cohort="snail">Snails (Delay)</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'eagle' ? 'active' : ''}" data-cohort="eagle">Eagles (TopK)</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'turnover' ? 'active' : ''}" data-cohort="turnover">Turnover (Friction)</button>
                <button class="chart-metric-btn ${this.activeFilterGroup === 'koala' ? 'active' : ''}" data-cohort="koala">Inversion (Koala)</button>
              </div>
            </div>

            <!-- Metric Mode Toggle -->
            <div class="filter-group" style="display: flex; align-items: center; gap: 6px;">
              <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">View:</span>
              <div class="chart-metric-btn-group" id="panorama-metric-btn-group">
                <button class="chart-metric-btn ${this.activeMetricMode === 'nav' ? 'active' : ''}" data-metric="nav">📈 NAV</button>
                <button class="chart-metric-btn ${this.activeMetricMode === 'excess_taotie' ? 'active' : ''}" data-metric="excess_taotie">🐾 vs Taotie</button>
                ${window.arenaAdapter.hasGhostTaotie() ? `
                <button class="chart-metric-btn ${this.activeMetricMode === 'excess_ghost' ? 'active' : ''}" data-metric="excess_ghost">👻 vs Ghost (100M)</button>
                ` : ''}
                <button class="chart-metric-btn ${this.activeMetricMode === 'excess_csi300' ? 'active' : ''}" data-metric="excess_csi300">🏛️ vs CSI 300</button>
                <button class="chart-metric-btn ${this.activeMetricMode === 'drawdown' ? 'active' : ''}" data-metric="drawdown">🌊 Drawdown</button>
              </div>
            </div>

            <!-- Benchmark Standards Independent Toggle Controls -->
            <div class="benchmark-pill-group" id="panorama-benchmark-pill-group">
              <span class="benchmark-pill-label">Benchmarks:</span>
              ${window.arenaAdapter.hasGhostTaotie() ? `
              <button type="button" class="benchmark-pill ghost-taotie is-active" data-benchmark="ghost" title="Toggle Ghost Taotie (100M)">
                <span class="bm-line-badge"></span> Ghost (100M)
              </button>` : ''}
              <button type="button" class="benchmark-pill taotie is-active" data-benchmark="taotie" title="Toggle Taotie (500k)">
                <span class="bm-line-badge"></span> Taotie (500k)
              </button>
              <button type="button" class="benchmark-pill csi300 is-active" data-benchmark="csi300" title="Toggle CSI 300">
                <span class="bm-line-badge"></span> CSI 300
              </button>
            </div>
          </div>
        </div>

        <div id="chart-arena-panorama" style="height: 420px; width: 100%;"></div>
      </div>

      <!-- Main Overview Layout: Scatter Plot + Top Performers -->
      <div class="overview-grid">
        <!-- Main Scatter Chart -->
        <div class="card">
          <div class="card-header">
            <div>
              <h3 class="card-title">🎯 Return vs. Monkey Percentile Significance</h3>
              <div class="card-subtitle">
                X-axis: 1,000-Monkey Null Percentile | Y-axis: OOS Total Return (%) | Bubble Size: Sharpe Ratio
              </div>
            </div>
            <div style="font-size:0.8rem; color:var(--text-tertiary);">
              Green Line: 95% Confidence (p = 0.05)
            </div>
          </div>
          <div id="chart-overview-scatter" class="chart-container tall"></div>
        </div>

        <!-- Top / Bottom Performers Sidebar -->
        <div style="display:flex; flex-direction:column; gap:1.5rem;">
          <!-- Top Performers -->
          <div class="card">
            <div class="card-header">
              <h4 class="card-title">🔥 Top Outperformers</h4>
            </div>
            <div class="top-paths-list">
              ${top5.map((p, idx) => `
                <div class="path-mini-row" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
                  <div>
                    <div style="font-weight:600; font-size:0.88rem; color:var(--text-primary);">
                      #${idx + 1} ${p.path_id}
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-tertiary);">
                      Monkey Pct: <b style="color:#a855f7;">${window.formatPercentile ? window.formatPercentile(p.percentile_rank ?? p.monkey_percentile) : (p.percentile_rank || 0).toFixed(1) + '%'}</b> | ${(() => {
                        const rawP = p.empirical_p_value !== undefined ? p.empirical_p_value : p.p_value;
                        const pVal = window.formatPValue ? window.formatPValue(rawP) : '1.0000';
                        return pVal.startsWith('<') ? `p ${pVal}` : `p=${pVal}`;
                      })()}
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-weight:700; color:var(--accent-positive); font-size:0.95rem;">
                      +${p.total_return_pct.toFixed(2)}%
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-tertiary);">
                      MDD: ${p.max_drawdown_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>

          <!-- Bottom Laggards -->
          <div class="card">
            <div class="card-header">
              <h4 class="card-title">❄️ Tail Laggards & Inversions</h4>
            </div>
            <div class="top-paths-list">
              ${bottom5.map((p, idx) => `
                <div class="path-mini-row" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
                  <div>
                    <div style="font-weight:600; font-size:0.88rem; color:var(--text-primary);">
                      ${p.path_id}
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-tertiary);">
                      ${p.animal_id === 'koala' ? '⚡ Inverted Polarity Test' : 'Monkey Pct: ' + (window.formatPercentile ? window.formatPercentile(p.percentile_rank ?? p.monkey_percentile) : (p.percentile_rank || 0).toFixed(1) + '%')}
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-weight:700; color:var(--accent-negative); font-size:0.95rem;">
                      ${p.total_return_pct.toFixed(2)}%
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-tertiary);">
                      MDD: ${p.max_drawdown_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      </div>
    `;

    // Bind model focus select
    const modelFocusSelect = el.querySelector("#panorama-model-focus-select");
    if (modelFocusSelect) {
      modelFocusSelect.addEventListener("change", (e) => {
        this.activeFocusModel = e.target.value;
        this.updatePanoramaChart();
      });
    }

    // Bind cohort group buttons
    const cohortBtns = el.querySelectorAll("#panorama-cohort-btn-group button");
    cohortBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        cohortBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeFilterGroup = btn.getAttribute("data-cohort");
        this.updatePanoramaChart();
      });
    });

    // Bind metric mode buttons
    const metricBtns = el.querySelectorAll("#panorama-metric-btn-group button");
    metricBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        metricBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeMetricMode = btn.getAttribute("data-metric");
        this.updatePanoramaChart();
      });
    });

    // Bind benchmark pill toggles
    const bmPills = el.querySelectorAll("#panorama-benchmark-pill-group .benchmark-pill");
    bmPills.forEach(pill => {
      pill.addEventListener("click", () => {
        const isActive = pill.classList.toggle("is-active");
        const bmKey = pill.getAttribute("data-benchmark");
        window.ArenaCharts.toggleBenchmark("chart-arena-panorama", bmKey, isActive);
      });
    });

    // Render charts
    setTimeout(() => {
      this.updatePanoramaChart();
      window.ArenaCharts.renderScatter("chart-overview-scatter", allPaths, path => {
        window.appRouter.navigate("path-detail", { pathId: path.path_id });
      });
    }, 50);
  },

  updatePanoramaChart() {
    if (!window.arenaAdapter || !window.ArenaCharts) return;
    const data = window.arenaAdapter.getMacroPanoramaData(this.activeMetricMode, this.activeFilterGroup, this.activeFocusModel);
    window.ArenaCharts.renderMacroPanorama("chart-arena-panorama", data);

    // Maintain benchmark pill selection state
    const bmPills = document.querySelectorAll("#panorama-benchmark-pill-group .benchmark-pill");
    bmPills.forEach(pill => {
      const bmKey = pill.getAttribute("data-benchmark");
      window.ArenaCharts.toggleBenchmark("chart-arena-panorama", bmKey, pill.classList.contains("is-active"));
    });
  }
};

