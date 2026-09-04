/**
 * web/js/views/overview.js
 * ========================
 * Arena Overview View:
 * 6 KPI Cards + Interactive Scatter Plot (Return vs. Monkey Percentile) + Outperformers & Laggards.
 */

window.OverviewView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const kpis = window.arenaAdapter.getGlobalKPIs();
    const allPaths = window.arenaAdapter.getAllPaths().filter(p => p.contestant_id !== "BENCHMARK");

    // Top 5 and Bottom 5 paths
    const sorted = [...allPaths].sort((a, b) => b.total_return_pct - a.total_return_pct);
    const top5 = sorted.slice(0, 5);
    const bottom5 = sorted.slice(-5).reverse();

    el.innerHTML = `
      <!-- Top KPI Metric Cards -->
      <div class="kpi-grid" style="margin-bottom: 24px;">
        <div class="kpi-card">
          <div class="kpi-label">Active Strategy Paths</div>
          <div class="kpi-value">${kpis.totalPaths}</div>
          <div class="kpi-subtext">6 Model Candidates × 28 Zoo Handlers</div>
        </div>
        <div class="kpi-card positive">
          <div class="kpi-label">Statistically Alpha (p &lt; 0.05)</div>
          <div class="kpi-value positive">${kpis.statSignificantCount}</div>
          <div class="kpi-subtext">${kpis.statSignificantPct} beats 95% of monkey colony</div>
        </div>
        <div class="kpi-card positive">
          <div class="kpi-label">Peak OOS Return</div>
          <div class="kpi-value positive">+${kpis.topReturn.toFixed(2)}%</div>
          <div class="kpi-subtext">Top performer across 40 trading days</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Median OOS Return</div>
          <div class="kpi-value" style="color:#38bdf8;">+${kpis.medianReturn.toFixed(2)}%</div>
          <div class="kpi-subtext">Cross-path median performance</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-label">Taotie Baseline (Full Universe)</div>
          <div class="kpi-value" style="color:#c084fc;">+${kpis.taotieReturn.toFixed(2)}%</div>
          <div class="kpi-subtext">CNY 500k capital-constrained full pool</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">CSI 300 Index (SH000300)</div>
          <div class="kpi-value" style="color:#f59e0b;">${kpis.csi300Return.toFixed(2)}%</div>
          <div class="kpi-subtext">A-share broad market benchmark</div>
        </div>
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
                      Monkey Pct: <b style="color:#a855f7;">${(p.percentile_rank || p.monkey_percentile || 0).toFixed(1)}%</b> | p=${(p.empirical_p_value || p.p_value || 1.0).toFixed(4)}
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
                      ${p.animal_id === 'koala' ? '⚡ Inverted Polarity Test' : 'Monkey Pct: ' + (p.percentile_rank || p.monkey_percentile || 0).toFixed(1) + '%'}
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

    // Render scatter chart
    setTimeout(() => {
      window.ArenaCharts.renderScatter("chart-overview-scatter", allPaths, path => {
        window.appRouter.navigate("path-detail", { pathId: path.path_id });
      });
    }, 50);
  }
};
