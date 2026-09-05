/**
 * QuantPits-Arena: Path Detail View
 * Deep-dive analysis for a single execution path:
 * - Cumulative NAV with Monkey 90% Confidence Envelope, Underwater Drawdown, Excess Return vs CSI 300
 * - Parametric monkey null distribution boxplot & empirical p-value
 * - Finite-capital constraint diagnostics (CNY 500k, 100-share minimum lots)
 */

window.PathDetailView = {
  activeMetric: "nav",

  render(containerId, pathId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const path = window.arenaAdapter.getPath(pathId);
    if (!path) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 4rem 2rem;">
          <h2>Path Not Found</h2>
          <p style="color: var(--text-tertiary); margin: 1rem 0;">Path ID "${pathId}" does not exist in this tournament run.</p>
          <button class="btn btn-primary" onclick="window.appRouter.navigate('leaderboard')">
            Back to Leaderboard
          </button>
        </div>
      `;
      return;
    }

    const contestant = window.arenaAdapter.getContestant(path.contestant_id);
    const dates = window.arenaAdapter.getNavDates();
    const taotieCurve = window.arenaAdapter.getBenchmarkTaotieCurve();
    const csi300Curve = window.arenaAdapter.getBenchmarkCsi300Curve();
    const monkeyDist = window.arenaAdapter.getMonkeyDistribution(path.strategy_spec);

    const isSig = path.is_statistically_significant || (path.empirical_p_value !== undefined && path.empirical_p_value < 0.05);
    const pVal = path.empirical_p_value !== undefined ? path.empirical_p_value : 1.0;
    const pRank = path.monkey_percentile !== undefined ? path.monkey_percentile : 50.0;
    const retColor = path.total_return_pct >= 0 ? "var(--accent-positive)" : "var(--accent-negative)";

    this.activeMetric = "nav";

    container.innerHTML = `
      <!-- Top Action Bar -->
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem; flex-wrap:wrap; gap:1rem;">
        <button class="btn btn-secondary" onclick="window.appRouter.navigate('leaderboard')">
          ← Back to Leaderboard
        </button>
        <div style="display:flex; gap:0.75rem;">
          <button class="btn btn-secondary" onclick="window.appRouter.navigate('contestants', { contestantId: '${path.contestant_id}' })">
            Model Profile (${contestant?.display_name || path.contestant_id})
          </button>
          <button class="btn btn-secondary" onclick="navigator.clipboard.writeText(window.location.href); alert('Path URL copied to clipboard!')">
            Share Path
          </button>
        </div>
      </div>

      <!-- Path Hero Header Card -->
      <div class="path-hero-card" style="margin-bottom: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
          <div>
            <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem; flex-wrap:wrap;">
              <span class="badge badge-cyan" style="font-size:0.85rem; padding:0.25rem 0.75rem;">
                ${contestant?.display_name || path.contestant_id}
              </span>
              <span class="badge badge-purple" style="font-size:0.85rem; padding:0.25rem 0.75rem;">
                ${path.animal_name || path.animal_id}
              </span>
              <span style="font-size:0.85rem; color:var(--text-tertiary);">
                Specification: <b>${path.strategy_spec}</b> (${path.animal_category})
              </span>
            </div>
            <h1 style="font-size:2rem; font-weight:800; color:var(--text-primary); margin:0 0 6px 0;">
              ${path.path_id}
            </h1>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
              ${(path.badges || []).map(b => `<span class="badge badge-neutral">${b}</span>`).join('')}
            </div>
          </div>

          <!-- Return & Percentile Highlights -->
          <div style="display:flex; gap:1.25rem; align-items:center;">
            <div style="text-align:right;">
              <div style="font-size:0.75rem; color:var(--text-tertiary); text-transform:uppercase;">OOS Total Return</div>
              <div style="font-size:2.2rem; font-weight:800; color:${retColor};">
                ${path.total_return_pct >= 0 ? '+' : ''}${path.total_return_pct.toFixed(2)}%
              </div>
              <div style="font-size:0.75rem; color:var(--text-tertiary);">
                Excess vs Taotie: <b>${(path.total_return_pct - 2.32) >= 0 ? '+' : ''}${(path.total_return_pct - 2.32).toFixed(2)}%</b>
              </div>
            </div>
            <div style="text-align:right; border-left:1px solid var(--border-subtle); padding-left:1.25rem;">
              <div style="font-size:0.75rem; color:var(--text-tertiary); text-transform:uppercase;">Monkey Percentile</div>
              <div style="font-size:2.2rem; font-weight:800; color:${isSig ? 'var(--accent-positive)' : 'var(--accent-warning)'};">
                ${window.formatPercentile ? window.formatPercentile(pRank) : pRank.toFixed(1) + '%'}
              </div>
              <div style="font-size:0.75rem; color:var(--text-tertiary);">
                Empirical p-value: <b>${window.formatPValue ? window.formatPValue(pVal) : pVal.toFixed(4)}</b>
              </div>
            </div>
          </div>
        </div>

        <!-- 4 Sub-Metrics Grid -->
        <div class="kpi-grid" style="margin-top:1.5rem; grid-template-columns:repeat(4, 1fr);">
          <div class="kpi-card">
            <div class="kpi-label">Final NAV</div>
            <div class="kpi-value">${path.final_nav.toFixed(4)}</div>
            <div class="kpi-subtext">Base 1.0000 on 2026-07-03</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Max Drawdown</div>
            <div class="kpi-value" style="color:var(--accent-negative);">${path.max_drawdown_pct.toFixed(2)}%</div>
            <div class="kpi-subtext">Peak-to-trough drop</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Sharpe Ratio</div>
            <div class="kpi-value" style="color:var(--accent-positive);">${path.sharpe_ratio || '-'}</div>
            <div class="kpi-subtext">Annualized risk-adjusted return</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Holdings Breadth</div>
            <div class="kpi-value" style="color:var(--accent-cyan);">${path.actual_holdings_mean.toFixed(1)} / ${path.target_holdings_mean.toFixed(0)}</div>
            <div class="kpi-subtext">Mean actual vs target stocks</div>
          </div>
        </div>
      </div>

      <!-- Main Visualizations Grid -->
      <div class="path-detail-grid">
        <!-- 1. Equity Curves vs Benchmarks & Monkey Envelope -->
        <div class="card">
          <div class="card-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
              <h3 class="card-title">Trajectory & Risk Visualizer</h3>
              <div class="card-subtitle">Examine daily performance dynamics across cumulative return, drawdown, and excess spread</div>
            </div>
            <div class="chart-metric-btn-group" id="path-metric-btn-group">
              <button class="chart-metric-btn active" data-metric="nav">Cumulative NAV</button>
              <button class="chart-metric-btn" data-metric="drawdown">Underwater Drawdown</button>
              <button class="chart-metric-btn" data-metric="excess_csi300">Excess vs. CSI 300</button>
            </div>
          </div>
          <div id="chart-path-equity-curves" class="chart-container tall"></div>
        </div>

        <!-- 2. Monkey Null Distribution Analysis -->
        <div class="card">
          <div class="card-header">
            <div>
              <h3 class="card-title">Null Distribution & Statistical Significance</h3>
              <div class="card-subtitle">Benchmarked against 1,000 random monkeys with identical portfolio parameters (${path.strategy_spec})</div>
            </div>
          </div>
          <div id="chart-path-monkey-dist" class="chart-container" style="height:260px;"></div>

          <!-- Finite Capital Diagnostics & Metadata -->
          <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid var(--border-subtle);">
            <h4 style="font-size:0.95rem; margin-bottom:0.75rem;">Finite Capital Execution Diagnostics (CNY 500k Constraint)</h4>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.85rem;">
              <div style="background:var(--bg-surface-elevated); padding:0.65rem 0.85rem; border-radius:var(--radius-sm);">
                <span style="color:var(--text-tertiary);">Unaffordable 1-Lot Skips:</span>
                <b style="float:right; color:${path.unaffordable_buy_count > 0 ? 'var(--accent-warning)' : 'var(--text-primary)'};">
                  ${path.unaffordable_buy_count} orders
                </b>
              </div>
              <div style="background:var(--bg-surface-elevated); padding:0.65rem 0.85rem; border-radius:var(--radius-sm);">
                <span style="color:var(--text-tertiary);">Mean Uninvested Cash Drag:</span>
                <b style="float:right;">${(path.mean_cash_ratio_pct || 0).toFixed(2)}%</b>
              </div>
            </div>

            <div style="margin-top:1rem; font-size:0.8rem; color:var(--text-tertiary); line-height:1.5;">
              <b>Model Metadata:</b> Family: <i>${contestant?.family || 'Alpha Family'}</i> | Architecture: <i>${contestant?.training_mode || 'Multi-Factor Ensemble'}</i> | Cutoff: <i>${contestant?.train_cutoff || '2026-06-26'}</i>
            </div>
          </div>
        </div>
      </div>
    `;

    const renderChart = (metric) => {
      window.ArenaCharts.renderEquityCurves(
        "chart-path-equity-curves",
        dates,
        path,
        taotieCurve,
        csi300Curve,
        monkeyDist,
        metric
      );
    };

    // Render initial charts
    setTimeout(() => {
      renderChart(this.activeMetric);

      if (monkeyDist) {
        window.ArenaCharts.renderMonkeyDistribution(
          "chart-path-monkey-dist",
          monkeyDist,
          path.total_return_pct,
          pRank,
          pVal
        );
      }

      // Bind metric switcher buttons
      const btnGroup = document.getElementById("path-metric-btn-group");
      if (btnGroup) {
        btnGroup.querySelectorAll(".chart-metric-btn").forEach(btn => {
          btn.addEventListener("click", (e) => {
            btnGroup.querySelectorAll(".chart-metric-btn").forEach(b => b.classList.remove("active"));
            e.currentTarget.classList.add("active");
            const metric = e.currentTarget.getAttribute("data-metric");
            this.activeMetric = metric;
            renderChart(metric);
          });
        });
      }
    }, 50);
  }
};
