/**
 * web/js/views/contestant_detail.js
 * =================================
 * Contestant Profile View:
 * Separates Historical Biography & Retrospective Context from Arena OOS Record.
 * Evaluates 5 Behavioral Fingerprints across 28 execution containers:
 *   1. Delay Sensitivity (Sloth vs. Snail)
 *   2. Turnover Sensitivity (Turtle vs. Robot vs. Rabbit)
 *   3. Breadth & Capacity (Eagle spectrum -> Whale Shark -> Taotie)
 *   4. Direction Sanity (Robot vs. Koala Reverse)
 *   5. Meerkat Percentile Slices (10% to 90%)
 * Plus: Multi-Animal Execution NAV Trajectories Chart.
 */

window.ContestantDetailView = {
  activeContestantId: "CONTESTANT_A",
  activeAnimalCluster: "rep",

  getClusterPaths(paths, clusterKey) {
    switch (clusterKey) {
      case "sloth":
        return paths.filter(p => p.animal_id.startsWith("sloth") || p.animal_id === "robot");
      case "snail":
        return paths.filter(p => p.animal_id.startsWith("snail") || p.animal_id === "robot");
      case "turnover":
        return paths.filter(p => ["turtle", "robot", "rabbit-1", "rabbit-2"].includes(p.animal_id));
      case "capacity":
        return paths.filter(p => p.animal_id.startsWith("eagle") || p.animal_id === "whale-shark" || p.animal_id === "robot");
      case "meerkats":
        return paths.filter(p => p.animal_id.startsWith("meerkat") || p.animal_id === "robot");
      case "all":
        return paths;
      case "rep":
      default: {
        const repAnimalIds = ["robot", "sloth-2", "snail-2", "turtle", "rabbit-1", "koala", "eagle-11-2", "whale-shark"];
        return repAnimalIds.map(aid => paths.find(p => p.animal_id === aid)).filter(Boolean);
      }
    }
  },

  render(containerId, contestantId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
      if (contestantId) {
        if (typeof contestantId === "object") {
          this.activeContestantId = contestantId.contestantId || contestantId.id || "CONTESTANT_A";
        } else {
          this.activeContestantId = String(contestantId);
        }
      }

      const contestants = window.arenaAdapter.getAllContestants();
      const contestant = window.arenaAdapter.getContestant(this.activeContestantId) || contestants[0];
      if (!contestant) {
        container.innerHTML = `<div class="card" style="text-align:center; padding:3rem;">No contestant found.</div>`;
        return;
      }
      this.activeContestantId = contestant.id || contestant.contestant_id;

      // Extract fingerprints and paths
      const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
      const fingerprints = window.arenaAdapter.getContestantFingerprints(this.activeContestantId);
      const paths = window.arenaAdapter.getFilteredPaths({ contestantId: this.activeContestantId });

      // Calculate stats
      const returns = paths.map(p => p.total_return_pct);
      const maxRet = returns.length ? Math.max(...returns) : 0;
      const minRet = returns.length ? Math.min(...returns) : 0;
      const robotPath = paths.find(p => p.animal_id === "robot");
      const robotRet = robotPath ? robotPath.total_return_pct : 0;
      const beatMonkeys = paths.filter(p => (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0)) >= 95).length;
      const avgMonkeyPct = (paths.reduce((s, p) => s + (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0)), 0) / Math.max(1, paths.length)).toFixed(1);

      container.innerHTML = `
        <div class="view-header">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
              <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <h1 class="view-title">${contestant.anonymous_name || contestant.display_name || contestant.contestant_id}</h1>
                <span class="badge ${contestant.status === 'RETIRED' ? 'badge-danger' : 'badge-primary'}">${contestant.status || 'BENCHMARKED'}</span>
                <span class="badge badge-neutral">${contestant.family || 'Alpha Family'}</span>
              </div>
              <p class="view-subtitle">Detailed model architecture profile, historical lineage, and 28-animal execution stress tests</p>
            </div>

            <!-- Model Switcher Chips -->
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span style="font-size: 12px; color: var(--text-secondary); font-weight: 600;">Select Model:</span>
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                ${contestants.map(c => {
                  const cid = c.id || c.contestant_id;
                  const isActive = cid === this.activeContestantId;
                  const familyTag = c.family || c.lineage || 'Alpha';
                  return `
                    <button class="btn ${isActive ? 'btn-primary' : 'btn-secondary'} contestant-switch-btn" 
                            data-cid="${cid}" style="padding: 4px 10px; font-size: 11px; font-weight: 600;">
                      ${c.display_name || c.anonymous_name || cid} <span style="font-size: 10px; opacity: 0.75; margin-left: 2px;">[${familyTag}]</span>
                    </button>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>

        <!-- Two Pillars: Historical Context vs Arena OOS Performance -->
        <div class="grid-2col" style="margin-bottom: 24px;">
          <!-- 1. Historical Biography: Context Prior to Arena -->
          <div class="card" style="border-left: 4px solid var(--accent-amber);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
              <h3 style="font-size: 15px; font-weight: 700; color: var(--accent-amber); display: flex; align-items: center; gap: 8px; margin: 0;">
                Historical Biography (Legacy Production Pool Archive)
              </h3>
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span class="badge badge-warning" style="font-size: 10px;">Prior to Arena Cutoff</span>
                <span class="badge" style="font-size: 10px; background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3);">Non-Comparable Cross-Pool</span>
              </div>
            </div>

            <!-- Prominent Universe Incomparability Warning -->
            <div class="callout-box" style="margin-bottom: 12px; padding: 10px 12px; background: rgba(245, 158, 11, 0.08); border-left: 3px solid var(--accent-amber); border-radius: 4px; font-size: 11.5px; line-height: 1.55;">
              <strong style="color: var(--accent-amber); display: block; margin-bottom: 3px;">
                ⚠️ Cross-Universe Incomparability Notice:
              </strong>
              <span style="color: var(--text-secondary);">
                The historical production metrics below (annualized return, Sharpe ratio, maximum drawdown) were evaluated under each model's historical production universe and liquidity filter regime (e.g., legacy CSI 300 / dedicated high-liquidity stock pool). Different constituent universes diverge fundamentally in stock count, market capitalization, idiosyncratic volatility, and alpha capacity. <strong>These legacy metrics must not be compared across different asset pools</strong> (such as against the current <strong>${seasonMeta.title || 'CSI 1000'}</strong> 1,000-stock small-cap testbed) or between models from different eras, and are preserved solely as archival baseline reference at retirement.
              </span>
            </div>

            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.6;">
              ${contestant.bio || contestant.historical_role || 'Historical quantitative production alpha candidate.'}
            </p>

            <!-- Headline Metric: Annualized System Return at Burial -->
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
              <div>
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Burial Annualized Return (Legacy Selection Pool Only)</div>
                <div style="font-size: 22px; font-weight: 800; color: var(--accent-positive); font-family: monospace; margin-top: 2px;">
                  +${(contestant.historical_sys_ann_return_pct || 10.0).toFixed(1)}% <span style="font-size: 13px; font-weight: 500; color: var(--text-secondary);">p.a.</span>
                </div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; color: var(--text-muted);">Cumulative Return &amp; MDD</div>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">
                  +${(contestant.historical_is_return_pct || 20.0).toFixed(1)}% <span style="color: var(--accent-negative); font-size: 12px;">(-${(contestant.historical_is_mdd_pct || 8.0).toFixed(2)}% MDD)</span>
                </div>
                <div style="font-size: 11px; color: var(--text-muted);">Historical Sharpe: <b>${(contestant.historical_is_sharpe || 1.85).toFixed(2)}</b></div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 12px; background: rgba(0,0,0,0.2); padding: 12px; border-radius: var(--radius-sm);">
              <div><span style="color: var(--text-muted);">Architecture:</span> <strong style="color: var(--text-primary);">${contestant.architecture_type || contestant.training_mode || 'Multi-Factor Ensemble'}</strong></div>
              <div><span style="color: var(--text-muted);">Family:</span> <strong style="color: var(--text-primary);">${contestant.lineage || contestant.family || 'Alpha Family'}</strong></div>
              <div><span style="color: var(--text-muted);">Historical Stock Pool:</span> <strong style="color: #fbbf24;">Legacy Production Pool</strong></div>
              <div><span style="color: var(--text-muted);">Current Arena Pool:</span> <strong style="color: var(--brand-cyan);">${seasonMeta.universe_name || (seasonMeta.id === 'season_csi1000' ? 'CSI 1000 (~1,000 Stocks)' : 'Season 1 (246 Stocks)')}</strong></div>
              <div><span style="color: var(--text-muted);">Training Cutoff:</span> <span style="color: var(--text-secondary); font-family: monospace;">${contestant.train_cutoff || '2026-06-26'}</span></div>
              <div><span style="color: var(--text-muted);">Burial Date:</span> <span style="color: var(--text-secondary); font-family: monospace;">${contestant.burial_date || contestant.retire_date || '2026-06-28'}</span></div>
              <div style="grid-column: span 2;"><span style="color: var(--text-muted);">Retirement Context:</span> <span style="color: var(--text-secondary);">${contestant.retire_reason || contestant.historical_role || 'Regular cycle retirement to evaluate out-of-sample decay.'}</span></div>
              <div style="grid-column: span 2; font-size: 11px; color: var(--text-muted); line-height: 1.5; margin-top: 4px; padding-top: 6px; border-top: 1px dashed var(--border-subtle);">
                * Evaluated from production logs (<code>daily_amount_log_full.csv</code>) using cashflow-adjusted time-weighted return formula from weekly inception (2024-10-21) to model retirement. Due to differences in constituent universe breadth, liquidity hurdles, and macro market regimes, historical production performance is non-comparable across distinct asset pools or with out-of-sample arena horizons.
              </div>
              ${contestant.known_issues && contestant.known_issues.length > 0 ? `
                <div style="grid-column: span 2; font-size: 11px; color: var(--accent-warning);">
                  <b>Known Caveat:</b> ${contestant.known_issues[0]}
                </div>
              ` : ''}
            </div>
          </div>

          <!-- 2. Arena OOS Performance -->
          <div class="card" style="border-left: 4px solid var(--accent-cyan);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
              <h3 style="font-size: 15px; font-weight: 700; color: var(--accent-cyan); display: flex; align-items: center; gap: 8px; margin: 0;">
                Arena OOS Reality (${seasonMeta.short_title || "Current Season"})
              </h3>
              <span class="badge badge-info" style="font-size: 10px;">${seasonMeta.universe_name || (seasonMeta.id === 'season_csi1000' ? 'CSI 1000 Universe' : 'Season Universe')}</span>
            </div>
            <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
              <div class="kpi-card" style="padding: 12px;">
                <div class="kpi-title">Baseline Handler (Robot)</div>
                <div class="kpi-value ${robotRet >= 0 ? 'text-up' : 'text-down'}" style="font-size: 20px;">
                  ${robotRet >= 0 ? '+' : ''}${robotRet.toFixed(2)}%
                </div>
                <div class="kpi-hint">Canonical 22/3 Policy</div>
              </div>
              <div class="kpi-card" style="padding: 12px;">
                <div class="kpi-title">Zoo Return Spread</div>
                <div class="kpi-value" style="font-size: 20px; color: var(--accent-purple);">
                  ${minRet.toFixed(1)}% ~ ${maxRet.toFixed(1)}%
                </div>
                <div class="kpi-hint">Across 28 Handlers</div>
              </div>
              <div class="kpi-card" style="padding: 12px;">
                <div class="kpi-title">Paths p &lt; 0.05 vs Null</div>
                <div class="kpi-value text-gold" style="font-size: 20px;">
                  ${beatMonkeys} / 28
                </div>
                <div class="kpi-hint">Mean Rank: ${window.formatPercentile ? window.formatPercentile(avgMonkeyPct) : avgMonkeyPct + '%'}</div>
              </div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: var(--radius-sm); line-height: 1.5;">
              Evaluated across the <strong>${seasonMeta.universe_name || (seasonMeta.id === 'season_csi1000' ? 'CSI 1000 Universe (~1,000 Stocks)' : 'Season 1 Constituent Universe (246 Stocks)')}</strong> starting from zero on ${seasonMeta.anchor_date || "2026-07-03"} under ${seasonMeta.methodology?.capital_spec || "identical market conditions, CNY 500,000 cash, and 100-share trading lots"}.
            </div>
          </div>
        </div>

        <!-- Multi-Animal Execution Trajectories Chart with Toolbar -->
        <div class="card" style="margin-bottom: 24px;">
          <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
              <h3 class="card-title">Cross-Animal Execution Trajectories</h3>
              <div class="card-subtitle">Comparing key execution handlers of ${contestant.display_name || contestant.anonymous_name} against Taotie and ${window.arenaAdapter.getMarketBenchmarkName()} benchmarks</div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <div class="chart-metric-btn-group" id="contestant-metric-btn-group">
                <button class="chart-metric-btn active" data-metric="nav">Cumulative NAV</button>
                <button class="chart-metric-btn" data-metric="drawdown">Underwater Drawdown</button>
                <button class="chart-metric-btn" data-metric="excess_csi300">Excess vs. ${window.arenaAdapter.getMarketBenchmarkName()}</button>
              </div>

              <!-- Benchmark Standards Independent Controls -->
              <div class="benchmark-pill-group" id="contestant-benchmark-pill-group">
                <span class="benchmark-pill-label">Benchmarks:</span>
                ${window.arenaAdapter.hasGhostTaotie() ? `
                <button type="button" class="benchmark-pill ghost-taotie is-active" data-benchmark="ghost" title="Toggle Ghost Taotie (100M)">
                  <span class="bm-line-badge"></span> Ghost (100M)
                </button>` : ''}
                <button type="button" class="benchmark-pill taotie is-active" data-benchmark="taotie" title="Toggle Taotie (500k)">
                  <span class="bm-line-badge"></span> Taotie (500k)
                </button>
                <button type="button" class="benchmark-pill csi300 is-active" data-benchmark="csi300" title="Toggle ${window.arenaAdapter.getMarketBenchmarkName()}">
                  <span class="bm-line-badge"></span> ${window.arenaAdapter.getMarketBenchmarkName()}
                </button>
              </div>
            </div>
          </div>

          <!-- Animal Family Cluster Toolbar -->
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 10px 16px; background: rgba(0,0,0,0.15); border-bottom: 1px solid var(--border-subtle);">
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
              <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-right: 4px;">Animal Family:</span>
              <div class="chart-metric-btn-group" id="contestant-cluster-btn-group">
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'rep' ? 'active' : ''}" data-cluster="rep">Representative (8)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'sloth' ? 'active' : ''}" data-cluster="sloth">Sloths (Lag 1-4)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'snail' ? 'active' : ''}" data-cluster="snail">Snails (Delay 1-4)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'turnover' ? 'active' : ''}" data-cluster="turnover">Turnover (Friction)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'capacity' ? 'active' : ''}" data-cluster="capacity">Capacity (Eagles &amp; Whale)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'meerkats' ? 'active' : ''}" data-cluster="meerkats">Deciles (Meerkats)</button>
                <button class="chart-metric-btn ${this.activeAnimalCluster === 'all' ? 'active' : ''}" data-cluster="all">All Animals (28)</button>
              </div>
            </div>
            <div id="contestant-cluster-count" style="font-size: 11px; color: var(--text-muted);">
              Showing ${this.getClusterPaths(paths, this.activeAnimalCluster).length} animal trajectories
            </div>
          </div>

          <div id="chart-contestant-multi-curves" style="height: 380px; width: 100%;"></div>
        </div>

        <!-- 5 Behavioral Fingerprint Tests -->
        <div style="margin-bottom: 24px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <h2 style="font-size: 18px; font-weight: 700; color: var(--text-primary);">
              🧬 Five Behavioral Fingerprint Stress Tests
            </h2>
            <span style="font-size: 12px; color: var(--text-muted);">Testing signal behavior under execution lag, turnover friction, capacity expansion, and polarity inversion</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 16px;">
            <!-- 1. Delay Sensitivity -->
            <div class="chart-card">
              <div class="chart-card-header">
                <div class="chart-card-title">1. Delay Sensitivity (Execution Lag)</div>
                <span class="badge badge-neutral">Sloth (Cash) vs Snail (Holding)</span>
              </div>
              <div id="chart-fingerprint-delay" style="height: 240px; width: 100%;"></div>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                Steep downward slope indicates rapid alpha decay requiring prompt order execution.
              </div>
            </div>

            <!-- 2. Turnover Sensitivity -->
            <div class="chart-card">
              <div class="chart-card-header">
                <div class="chart-card-title">2. Turnover Sensitivity (Friction Stress)</div>
                <span class="badge badge-neutral">Turtle vs Robot vs Rabbit 1~2</span>
              </div>
              <div id="chart-fingerprint-turnover" style="height: 240px; width: 100%;"></div>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                Tests resilience from minimum turnover (Turtle) to complete weekly portfolio liquidation (Rabbit-2).
              </div>
            </div>

            <!-- 3. Capacity & Breadth -->
            <div class="chart-card">
              <div class="chart-card-header">
                <div class="chart-card-title">3. Capacity & Breadth Expansion</div>
                <span class="badge badge-neutral">Eagle 5~88 → Whale Shark → Taotie</span>
              </div>
              <div id="chart-fingerprint-breadth" style="height: 240px; width: 100%;"></div>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                Portfolio size expands from 5 stocks to full universe (246 stocks). Evaluates concentration vs generalizability.
              </div>
            </div>

            <!-- 4. Direction Sanity -->
            <div class="chart-card">
              <div class="chart-card-header">
                <div class="chart-card-title">4. Polarity & Direction Sanity</div>
                <span class="badge badge-neutral">Robot (Top) vs Koala (Bottom)</span>
              </div>
              <div id="chart-fingerprint-direction" style="height: 240px; width: 100%;"></div>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                Koala serves as a directional sanity check. A viable model should produce meaningful positive separation from its inverted selection; a negative or near-zero spread warns of sign convention issues or noise.
              </div>
            </div>
          </div>

          <!-- 5. Meerkat Percentile Slices -->
          <div class="chart-card">
            <div class="chart-card-header">
              <div class="chart-card-title">5. Meerkat Percentile Slices (10% ~ 90% Decile Slices)</div>
              <span class="badge badge-neutral">Rank Geometry Test</span>
            </div>
            <div id="chart-fingerprint-meerkat" style="height: 220px; width: 100%;"></div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
              Meerkats examine cross-sectional rank geometry to evaluate whether information decays monotonically across deciles or concentrates only in narrow extreme slices.
            </div>
          </div>
        </div>

        <!-- 28 Execution Containers Table -->
        <div class="card" style="margin-bottom: 24px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
            <h3 style="font-size: 16px; font-weight: 700;">All 28 Execution Containers for ${contestant.display_name || contestant.anonymous_name}</h3>
            <span style="font-size: 12px; color: var(--text-secondary);">Click any row to drill down to its dedicated path dossier</span>
          </div>
          <div class="table-responsive">
            <table class="table" style="font-size: 12px;">
              <thead>
                <tr>
                  <th>Execution Handler</th>
                  <th>Category</th>
                  <th style="text-align: right;">Total Return</th>
                  <th style="text-align: right;">Max Drawdown</th>
                  <th style="text-align: right;">Sharpe Ratio</th>
                  <th style="text-align: right;">Monkey Percentile</th>
                  <th style="text-align: right;">Empirical p-value</th>
                  <th style="text-align: right;">1-Lot Skips</th>
                  <th style="text-align: right;">Mean Cash Ratio</th>
                  <th style="text-align: center;">Action</th>
                </tr>
              </thead>
              <tbody>
                ${paths.map(p => {
                  const retColor = p.total_return_pct >= 0 ? "text-up" : "text-down";
                  const pRank = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0);
                  const isSig = pRank >= 95;
                  const pVal = p.empirical_p_value !== undefined ? p.empirical_p_value : (p.p_value !== undefined ? p.p_value : 1.0);
                  return `
                    <tr style="cursor: pointer;" onclick="window.appRouter.navigate('path-detail', { pathId: '${p.path_id}' })">
                      <td>
                        <div style="font-weight: 600; color: var(--text-primary);">${p.animal_name || p.animal_id}</div>
                        <div style="font-size: 10px; color: var(--text-muted);">${p.animal_id}</div>
                      </td>
                      <td><span class="badge badge-neutral">${p.animal_category}</span></td>
                      <td style="text-align: right; font-weight: 700;" class="${retColor}">
                        ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%
                      </td>
                      <td style="text-align: right; color: var(--accent-rose);">${p.max_drawdown_pct ? p.max_drawdown_pct.toFixed(2) : '0.00'}%</td>
                      <td style="text-align: right; font-weight: 600;">${p.sharpe_ratio !== undefined ? p.sharpe_ratio.toFixed(2) : '-'}</td>
                      <td style="text-align: right;">
                        <span class="badge ${isSig ? 'badge-success' : 'badge-neutral'}" style="font-weight: 700;">
                          ${window.formatPercentile ? window.formatPercentile(pRank) : pRank.toFixed(1) + '%'}
                        </span>
                      </td>
                      <td style="text-align: right; font-family: monospace; color: ${isSig ? 'var(--accent-cyan)' : 'var(--text-muted)'};">
                        ${window.formatPValue ? window.formatPValue(pVal) : pVal.toFixed(4)}
                      </td>
                      <td style="text-align: right; color: ${p.unaffordable_buy_count > 0 ? 'var(--accent-amber)' : 'var(--text-muted)'};">
                        ${p.unaffordable_buy_count ?? 0}
                      </td>
                      <td style="text-align: right; color: var(--text-secondary);">
                        ${p.mean_cash_ratio_pct ? p.mean_cash_ratio_pct.toFixed(2) + '%' : '-'}
                      </td>
                      <td style="text-align: center;">
                        <button class="btn btn-secondary" style="padding: 2px 8px; font-size: 11px;">
                          Details →
                        </button>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;

      // Bind contestant switcher buttons
      container.querySelectorAll(".contestant-switch-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const cid = btn.getAttribute("data-cid");
          window.appRouter.navigate("contestants", { contestantId: cid });
        });
      });

      // Render fingerprint charts & multi-curve chart
      setTimeout(() => {
        this.renderCharts(fingerprints, paths);
      }, 50);

    } catch (err) {
      console.error("Error rendering ContestantDetailView:", err);
      container.innerHTML = `
        <div class="card" style="padding: 2rem; text-align: center; color: var(--accent-rose);">
          <h3>Error Loading Contestant Profile</h3>
          <p style="font-size: 13px; color: var(--text-secondary); margin-top: 8px;">${err.message}</p>
          <button class="btn btn-primary" onclick="window.appRouter.navigate('contestants', { contestantId: 'CONTESTANT_A' })" style="margin-top: 12px;">
            Reset to Default Model
          </button>
        </div>
      `;
    }
  },

  renderCharts(fingerprints, paths) {
    let currentMetric = "nav";
    const dates = window.arenaAdapter.getNavDates();
    const taotieCurve = window.arenaAdapter.getBenchmarkTaotieCurve();
    const csi300Curve = window.arenaAdapter.getBenchmarkCsi300Curve();

    const drawMultiCurves = () => {
      const currentPaths = this.getClusterPaths(paths, this.activeAnimalCluster);
      window.ArenaCharts.renderMultiAnimalCurves(
        "chart-contestant-multi-curves",
        dates,
        currentPaths,
        taotieCurve,
        csi300Curve,
        currentMetric
      );

      // Maintain benchmark pill selection state
      document.querySelectorAll("#contestant-benchmark-pill-group .benchmark-pill").forEach(pill => {
        const bmKey = pill.getAttribute("data-benchmark");
        window.ArenaCharts.toggleBenchmark("chart-contestant-multi-curves", bmKey, pill.classList.contains("is-active"));
      });

      const countEl = document.getElementById("contestant-cluster-count");
      if (countEl) {
        countEl.textContent = `Showing ${currentPaths.length} animal trajectories`;
      }
    };

    // 1. Initial render of multi-animal curves
    drawMultiCurves();

    // Bind animal cluster buttons
    const clusterGroup = document.getElementById("contestant-cluster-btn-group");
    if (clusterGroup) {
      clusterGroup.querySelectorAll(".chart-metric-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
          clusterGroup.querySelectorAll(".chart-metric-btn").forEach(b => b.classList.remove("active"));
          e.currentTarget.classList.add("active");
          this.activeAnimalCluster = e.currentTarget.getAttribute("data-cluster");
          drawMultiCurves();
        });
      });
    }

    // Bind metric buttons
    const btnGroup = document.getElementById("contestant-metric-btn-group");
    if (btnGroup) {
      btnGroup.querySelectorAll(".chart-metric-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
          btnGroup.querySelectorAll(".chart-metric-btn").forEach(b => b.classList.remove("active"));
          e.currentTarget.classList.add("active");
          currentMetric = e.currentTarget.getAttribute("data-metric");
          drawMultiCurves();
        });
      });
    }

    // Bind benchmark pills
    const contestantBmPills = document.querySelectorAll("#contestant-benchmark-pill-group .benchmark-pill");
    contestantBmPills.forEach(pill => {
      pill.addEventListener("click", () => {
        const isActive = pill.classList.toggle("is-active");
        const bmKey = pill.getAttribute("data-benchmark");
        window.ArenaCharts.toggleBenchmark("chart-contestant-multi-curves", bmKey, isActive);
      });
    });

    // 2. Render 4 fingerprint charts
    window.ArenaCharts.renderFingerprintGroup(
      "chart-fingerprint-delay",
      "chart-fingerprint-turnover",
      "chart-fingerprint-breadth",
      "chart-fingerprint-direction",
      fingerprints
    );

    // 3. Render Meerkat decile bars
    const domMeerkat = document.getElementById("chart-fingerprint-meerkat");
    if (domMeerkat) {
      const chart = echarts.getInstanceByDom(domMeerkat) || echarts.init(domMeerkat);
      const tc = window.ArenaCharts.getThemeColors();
      const labels = fingerprints.meerkatData.map(d => `Meerkat ${d.percentile}`);
      const vals = fingerprints.meerkatData.map(d => d.return);

      chart.setOption({
        backgroundColor: tc.bg,
        tooltip: { trigger: "axis" },
        grid: { left: "6%", right: "4%", top: "15%", bottom: "20%" },
        xAxis: { type: "category", data: labels, axisLabel: { color: tc.textSecondary, fontSize: 11 } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{
          type: "bar",
          data: vals.map(v => ({
            value: v,
            itemStyle: { color: v >= 0 ? "#10b981" : "#f43f5e" }
          })),
          markLine: {
            data: [{ type: "average", name: "Mean" }],
            lineStyle: { color: "#f59e0b", type: "dashed" }
          }
        }]
      }, true);
      window.addEventListener("resize", () => chart.resize());
    }
  }
};
