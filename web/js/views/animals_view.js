/**
 * web/js/views/animals_view.js
 * ============================
 * The Zoo: Execution Containers View
 * Deep-dive analysis for all 28 animal execution policies.
 * Enables:
 *   - Single Container Profile: deep dive into 1 animal across 6 contestant models
 *   - Uncapped Multi-Animal Comparison: freely select and compare any number of animal containers
 *     with optional Model Focus filter and benchmark overlays.
 */

window.AnimalsView = {
  activeAnimalId: "robot",
  activeCategory: "All",
  activeMetric: "nav",
  telemetryScope: "container", // "container" or "category"
  comparisonMode: "single", // "single" or "multi"
  selectedAnimalIds: ["robot", "sloth-2", "snail-2", "turtle", "rabbit-1", "koala", "eagle-11-2", "whale-shark"],
  activeFocusModel: "all", // "all" or specific contestant_id

  render(containerId, params) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
      if (params) {
        if (typeof params === "object") {
          if (params.mode) this.comparisonMode = params.mode;
          if (params.animalId || params.id) this.activeAnimalId = params.animalId || params.id;
          if (params.modelFocus) this.activeFocusModel = params.modelFocus;
        } else if (typeof params === "string") {
          this.activeAnimalId = params;
        }
      }

      const allAnimals = window.arenaAdapter.getAllAnimals();
      let activeAnimal = allAnimals.find(a => a.id === this.activeAnimalId);
      if (!activeAnimal) {
        activeAnimal = allAnimals[0];
        this.activeAnimalId = activeAnimal.id;
      }

      const categories = [
        "All",
        "Baseline",
        "Execution Lag",
        "Stale Holding",
        "Turnover Friction",
        "Polarity Inversion",
        "Capacity & Breadth",
        "Percentile Deciles"
      ];

      const filteredAnimals = this.activeCategory === "All"
        ? allAnimals
        : allAnimals.filter(a => a.category === this.activeCategory);

      // Paths determination based on single vs multi comparison mode
      let chartPaths = [];
      if (this.comparisonMode === "single") {
        chartPaths = window.arenaAdapter.getAnimalPaths(this.activeAnimalId);
      } else {
        if (this.activeFocusModel === "all") {
          chartPaths = window.arenaAdapter.getAllPaths().filter(p => 
            p.contestant_id !== "BENCHMARK" && this.selectedAnimalIds.includes(p.animal_id)
          );
        } else {
          chartPaths = window.arenaAdapter.getAllPaths().filter(p => 
            p.contestant_id === this.activeFocusModel && this.selectedAnimalIds.includes(p.animal_id)
          );
        }
        if (chartPaths.length === 0 && this.selectedAnimalIds.length === 0) {
          this.selectedAnimalIds = ["robot"];
          chartPaths = window.arenaAdapter.getAnimalPaths("robot");
        }
      }

      // Benchmark metrics for reference
      const csi300Ret = window.arenaAdapter.getCsi300Return();
      const taotieRet = window.arenaAdapter.getTaotieReturn();
      const allContestants = window.arenaAdapter.getAllContestants();

      // Compute statistics
      const returns = chartPaths.map(p => p.total_return_pct);
      const drawdowns = chartPaths.map(p => p.max_drawdown_pct);
      const bestPath = chartPaths.length > 0 ? [...chartPaths].sort((a, b) => b.total_return_pct - a.total_return_pct)[0] : null;
      const medianReturn = returns.length > 0
        ? [...returns].sort((a, b) => a - b)[Math.floor(returns.length / 2)]
        : 0;
      const avgDrawdown = drawdowns.length > 0
        ? drawdowns.reduce((s, v) => s + v, 0) / drawdowns.length
        : 0;
      const sigCount = chartPaths.filter(p => {
        const pct = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.monkey_percentile_rank || 0));
        return pct >= 95;
      }).length;
      const sigPct = chartPaths.length > 0
        ? ((sigCount / chartPaths.length) * 100).toFixed(0)
        : 0;

      container.innerHTML = `
        <div class="view-header">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
              <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <h1 class="view-title">The Zoo | Execution Handlers</h1>
                <span class="badge badge-primary">28 Containers</span>
                <span class="badge badge-neutral">Execution Stress Suite</span>
              </div>
              <p class="view-subtitle">Explore operational execution containers testing latency, exit inertia, turnover constraints, portfolio capacity, and polarity sanity across all contestant models.</p>
            </div>

            <!-- Single vs Multi-Animal Mode Switcher -->
            <div style="display: flex; gap: 6px; background: rgba(0,0,0,0.25); padding: 4px; border-radius: 8px; border: 1px solid var(--border-subtle);">
              <button class="btn btn-sm ${this.comparisonMode === 'single' ? 'btn-primary' : 'btn-outline'} zoo-mode-btn" data-mode="single" style="font-size: 11px; padding: 5px 12px; font-weight: 600;">
                Single Container Profile
              </button>
              <button class="btn btn-sm ${this.comparisonMode === 'multi' ? 'btn-primary' : 'btn-outline'} zoo-mode-btn" data-mode="multi" style="font-size: 11px; padding: 5px 12px; font-weight: 600;">
                ⚡ Multi-Animal Comparison (${this.selectedAnimalIds.length})
              </button>
            </div>
          </div>

          <!-- Category Filter Pills + Quick Dropdown Selector -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-top: 18px; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
              <span style="font-size: 11px; color: var(--text-secondary); font-weight: 600; margin-right: 4px;">Category:</span>
              ${categories.map(cat => {
                const count = cat === "All" ? allAnimals.length : allAnimals.filter(a => a.category === cat).length;
                const isActive = this.activeCategory === cat;
                return `
                  <button class="btn btn-sm ${isActive ? 'btn-primary' : 'btn-outline'} animal-cat-btn" data-cat="${cat}" style="font-size: 11px; padding: 4px 9px;">
                    ${cat} <span style="opacity: 0.75; font-size: 10px;">(${count})</span>
                  </button>
                `;
              }).join("")}
            </div>

            <!-- Direct Container Dropdown Selector (Single Mode) or Multi Quick Action Toolbar -->
            ${this.comparisonMode === 'single' ? `
            <div style="display: flex; align-items: center; gap: 8px;">
              <label for="zoo-animal-dropdown" style="font-size: 11px; color: var(--text-secondary); font-weight: 600; white-space: nowrap;">
                Quick Select:
              </label>
              <select id="zoo-animal-dropdown" class="form-control" style="font-size: 11px; padding: 4px 10px; min-width: 220px; background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary); border-radius: var(--radius-sm);">
                ${filteredAnimals.map(a => `
                  <option value="${a.id}" ${a.id === this.activeAnimalId ? 'selected' : ''}>
                    ${a.name} (${a.spec || a.category})
                  </option>
                `).join("")}
              </select>
            </div>
            ` : `
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
              <button class="btn btn-sm btn-outline zoo-multi-action-btn" data-action="rep" style="font-size: 10px; padding: 3px 8px;" title="Select 8 canonical representative handlers">
                Representative (8)
              </button>
              <button class="btn btn-sm btn-outline zoo-multi-action-btn" data-action="all_cat" style="font-size: 10px; padding: 3px 8px;" title="Select all containers in the active category">
                Select All in Category
              </button>
              <button class="btn btn-sm btn-outline zoo-multi-action-btn" data-action="clear" style="font-size: 10px; padding: 3px 8px;" title="Reset selection">
                Reset Selection
              </button>
              <span class="badge badge-neutral" style="font-size: 10px; padding: 3px 7px;">
                ${this.selectedAnimalIds.length} Selected (Uncapped)
              </span>
            </div>
            `}
          </div>

          <!-- Wrapping Animal Selector Chips -->
          <div style="display: flex; flex-wrap: wrap; gap: 6px; padding: 10px 0 6px 0;" id="animal-chip-bar">
            ${filteredAnimals.map(a => {
              const isSelected = this.comparisonMode === 'single'
                ? a.id === this.activeAnimalId
                : this.selectedAnimalIds.includes(a.id);
              return `
                <button class="btn btn-sm ${isSelected ? 'btn-primary' : 'btn-outline'} animal-chip-btn" data-animal-id="${a.id}" style="font-size: 11px; padding: 4px 10px; display: inline-flex; align-items: center; gap: 6px; border-radius: 16px;">
                  <span>${a.name.split(' (')[0]}</span>
                  <span class="badge ${isSelected ? 'badge-neutral' : 'badge-primary'}" style="font-size: 9px; padding: 1px 5px;">${a.badge || a.category}</span>
                </button>
              `;
            }).join("")}
          </div>
        </div>

        <!-- Animal Container Profile & Key Performance Card -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-bottom: 24px;">
          <!-- Left: Animal Container Specifications / Sandbox Summary -->
          <div class="card" style="padding: 20px;">
            ${this.comparisonMode === 'single' ? `
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                  <span class="badge badge-primary" style="margin-bottom: 6px;">${activeAnimal.category}</span>
                  <h3 style="font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0;">${activeAnimal.name}</h3>
                </div>
                <span class="badge badge-neutral" style="font-family: monospace; font-size: 11px;">Target: ${activeAnimal.spec || `P_${activeAnimal.topk}_${activeAnimal.n_drop}`}</span>
              </div>
              <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px;">
                ${activeAnimal.description}
              </p>
              <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; background: var(--surface-hover); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div>
                  <div style="font-size: 11px; color: var(--text-muted);">Portfolio Holdings (topk)</div>
                  <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); font-family: monospace;">${activeAnimal.topk} stocks</div>
                </div>
                <div>
                  <div style="font-size: 11px; color: var(--text-muted);">Rebalance Churn (n_drop)</div>
                  <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); font-family: monospace;">${activeAnimal.n_drop} stocks/wk</div>
                </div>
              </div>
            ` : `
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                  <span class="badge badge-success" style="margin-bottom: 6px;">Uncapped Comparison Sandbox</span>
                  <h3 style="font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0;">Multi-Animal Sandbox</h3>
                </div>
                <span class="badge badge-neutral" style="font-family: monospace; font-size: 11px;">${this.selectedAnimalIds.length} Animals Active</span>
              </div>
              <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px;">
                Simultaneously comparing execution paths across selected animal policies. Toggle chips to add or remove any containers without restrictions.
              </p>
              <div style="background: var(--surface-hover); padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-subtle); font-size: 12px;">
                <div style="color: var(--text-muted); font-size: 11px; margin-bottom: 4px;">Active Selection (${this.selectedAnimalIds.length}):</div>
                <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                  ${this.selectedAnimalIds.map(aid => {
                    const an = allAnimals.find(a => a.id === aid);
                    return `<span class="badge badge-primary" style="font-size: 10px;">${an ? an.name.split(' (')[0] : aid}</span>`;
                  }).join('')}
                </div>
              </div>
            `}
          </div>

          <!-- Right: Execution Stress Telemetry Card -->
          <div class="card" style="padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
              <div>
                <h4 style="font-size: 13px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.5px; margin: 0;">
                  Execution Stress Telemetry
                </h4>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 3px;">
                  ${this.comparisonMode === 'single'
                    ? `Testing alpha durability across all 6 contestant models under <b>${activeAnimal.name}</b>`
                    : `Telemetry across ${chartPaths.length} evaluated path${chartPaths.length > 1 ? 's' : ''} in comparison scope`}
                </div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
              <div style="background: var(--surface-hover); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-muted);">Top Return in Scope</div>
                <div style="font-size: 18px; font-weight: 700; color: ${bestPath && bestPath.total_return_pct >= 0 ? 'var(--color-success)' : 'var(--color-danger)'};">
                  ${bestPath ? (bestPath.total_return_pct >= 0 ? '+' : '') + bestPath.total_return_pct.toFixed(2) + '%' : 'N/A'}
                </div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">
                  Leader: <b>${bestPath ? `${bestPath.contestant_id} (${bestPath.animal_id})` : 'N/A'}</b>
                </div>
              </div>

              <div style="background: var(--surface-hover); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-muted);">Median Return</div>
                <div style="font-size: 18px; font-weight: 700; color: ${medianReturn >= 0 ? 'var(--color-success)' : 'var(--color-danger)'};">
                  ${medianReturn >= 0 ? '+' : ''}${medianReturn.toFixed(2)}%
                </div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">
                  Active spread: <b>${(medianReturn - csi300Ret >= 0 ? '+' : '') + (medianReturn - csi300Ret).toFixed(2)}% vs ${window.arenaAdapter.getMarketBenchmarkName()}</b>
                </div>
              </div>

              <div style="background: var(--surface-hover); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-muted);">Average Max Drawdown</div>
                <div style="font-size: 18px; font-weight: 700; color: var(--color-danger);">
                  -${avgDrawdown.toFixed(2)}%
                </div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">
                  Across ${chartPaths.length} path${chartPaths.length > 1 ? 's' : ''}
                </div>
              </div>

              <div style="background: var(--surface-hover); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-muted);">Upper-Tail Rate (p &lt; 0.05)</div>
                <div style="font-size: 18px; font-weight: 700; color: var(--color-accent);">
                  ${sigPct}%
                </div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">
                  <b>${sigCount}/${chartPaths.length}</b> beat null 95th %ile
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Trajectory Chart Card -->
        <div class="card" style="margin-bottom: 24px;">
          <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid var(--border-subtle); padding: 16px 20px;">
            <div>
              <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0;">
                ${this.comparisonMode === 'single'
                  ? `Cross-Model Execution Curves: ${activeAnimal.name}`
                  : `Multi-Animal Comparison Curves (${this.selectedAnimalIds.length} Containers)`}
              </h3>
              <p style="font-size: 12px; color: var(--text-secondary); margin: 2px 0 0 0;">
                ${this.comparisonMode === 'single'
                  ? `Comparing performance trajectories of all 6 contestant models under <b>${activeAnimal.name}</b> vs. benchmarks`
                  : `Overlaying trajectories for ${this.selectedAnimalIds.length} animal containers (Model Focus: <b>${this.activeFocusModel === 'all' ? 'All Models' : this.activeFocusModel}</b>)`}
              </p>
            </div>

            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <!-- Model Focus Filter (Multi-Animal Mode) -->
              ${this.comparisonMode === 'multi' ? `
              <div class="filter-group" style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Model Focus:</span>
                <select id="zoo-focus-model-select" class="form-control" style="font-size: 11px; padding: 3px 8px; width: auto; background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary); border-radius: 4px;">
                  <option value="all" ${this.activeFocusModel === 'all' ? 'selected' : ''}>All Models</option>
                  ${allContestants.map(c => `
                    <option value="${c.id}" ${this.activeFocusModel === c.id ? 'selected' : ''}>${c.display_name || c.id}</option>
                  `).join('')}
                </select>
              </div>
              ` : ''}

              <!-- Metric Switcher Buttons -->
              <div class="chart-metric-btn-group" style="display: flex; gap: 4px; background: var(--surface-hover); padding: 3px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <button class="btn btn-sm ${this.activeMetric === 'nav' ? 'btn-primary' : 'btn-outline'} animal-metric-btn" data-metric="nav" style="font-size: 11px; padding: 4px 10px;">
                  Cumulative NAV
                </button>
                <button class="btn btn-sm ${this.activeMetric === 'drawdown' ? 'btn-primary' : 'btn-outline'} animal-metric-btn" data-metric="drawdown" style="font-size: 11px; padding: 4px 10px;">
                  Underwater Drawdown
                </button>
                <button class="btn btn-sm ${this.activeMetric === 'excess_csi300' ? 'btn-primary' : 'btn-outline'} animal-metric-btn" data-metric="excess_csi300" style="font-size: 11px; padding: 4px 10px;">
                  Excess vs. ${window.arenaAdapter.getMarketBenchmarkName()}
                </button>
              </div>

              <!-- Benchmark Standards Independent Controls -->
              <div class="benchmark-pill-group" id="animal-benchmarks-pill-group">
                <span class="benchmark-pill-label">Benchmarks:</span>
                ${window.arenaAdapter.hasGhostTaotie() ? `
                <button type="button" class="benchmark-pill ghost-taotie is-active" data-benchmark="ghost" title="Toggle Ghost Taotie (100M)">
                  <span class="bm-line-badge"></span> Ghost (100M)
                </button>` : ''}
                <button type="button" class="benchmark-pill taotie is-active" data-benchmark="taotie" title="Toggle ${window.arenaAdapter.getTaotieDisplayName()}">
                  <span class="bm-line-badge"></span> ${window.arenaAdapter.getTaotieShortName()}
                </button>
                <button type="button" class="benchmark-pill csi300 is-active" data-benchmark="csi300" title="Toggle ${window.arenaAdapter.getMarketBenchmarkName()}">
                  <span class="bm-line-badge"></span> ${window.arenaAdapter.getMarketBenchmarkName()}
                </button>
              </div>
            </div>
          </div>

          <div class="card-body" style="padding: 16px 20px;">
            <div id="animal-cross-model-chart" style="width: 100%; height: 380px;"></div>
          </div>
        </div>

        <!-- Standings Table -->
        <div class="card">
          <div class="card-header" style="border-bottom: 1px solid var(--border-subtle); padding: 16px 20px;">
            <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0;">
              ${this.comparisonMode === 'single'
                ? `Contestant Standings under ${activeAnimal.name}`
                : `Multi-Animal Comparison Matrix (${chartPaths.length} Paths)`}
            </h3>
            <p style="font-size: 12px; color: var(--text-secondary); margin: 2px 0 0 0;">
              Ranked by Out-of-Sample Return. Compare empirical significance against the 1,000-monkey null benchmark.
            </p>
          </div>

          <div class="card-body" style="padding: 0; overflow-x: auto;">
            <table class="table" style="width: 100%; font-size: 12px; border-collapse: collapse;">
              <thead>
                <tr style="border-bottom: 1px solid var(--border-subtle); background: var(--surface-hover); text-align: left;">
                  <th style="padding: 10px 16px; width: 48px;">Rank</th>
                  <th style="padding: 10px 16px;">Contestant Model</th>
                  <th style="padding: 10px 16px;">Animal Container</th>
                  <th style="padding: 10px 16px;">Path Identifier</th>
                  <th style="padding: 10px 16px; text-align: right;">Total Return</th>
                  <th style="padding: 10px 16px; text-align: right;">Max Drawdown</th>
                  <th style="padding: 10px 16px; text-align: right;">Sharpe</th>
                  <th style="padding: 10px 16px; text-align: right;">Monkey Null %</th>
                  <th style="padding: 10px 16px; text-align: center;">Significance</th>
                  <th style="padding: 10px 16px; text-align: right;">vs. ${window.arenaAdapter.getMarketBenchmarkName()}</th>
                  <th style="padding: 10px 16px; text-align: right;">vs. Taotie</th>
                  <th style="padding: 10px 16px; text-align: center;">Action</th>
                </tr>
              </thead>
              <tbody>
                ${[...chartPaths].sort((a, b) => b.total_return_pct - a.total_return_pct).map((p, idx) => {
                  const rawPct = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.monkey_percentile_rank || 0));
                  const pct = window.formatPercentile ? window.formatPercentile(rawPct) : rawPct.toFixed(1) + "%";
                  const rawP = p.empirical_p_value !== undefined ? p.empirical_p_value : (p.p_value !== undefined ? p.p_value : 1.0);
                  const pVal = window.formatPValue ? window.formatPValue(rawP) : rawP.toFixed(4);
                  const isSig = (typeof rawPct === "number" ? rawPct : parseFloat(pct)) >= 95;
                  const spreadCsi = p.total_return_pct - csi300Ret;
                  const spreadTaotie = p.total_return_pct - taotieRet;

                  return `
                    <tr style="border-bottom: 1px solid var(--border-subtle); hover:background var(--surface-hover);">
                      <td style="padding: 12px 16px; font-weight: 700; color: var(--text-muted);">#${idx + 1}</td>
                      <td style="padding: 12px 16px;">
                        <a href="#contestants/${p.contestant_id}" style="font-weight: 600; color: var(--color-accent); text-decoration: none;">
                          ${p.contestant_id}
                        </a>
                      </td>
                      <td style="padding: 12px 16px;">
                        <span class="badge badge-neutral">${p.animal_name || p.animal_id}</span>
                      </td>
                      <td style="padding: 12px 16px; font-family: monospace; color: var(--text-secondary);">
                        ${p.path_id}
                      </td>
                      <td style="padding: 12px 16px; text-align: right; font-weight: 700; color: ${p.total_return_pct >= 0 ? 'var(--color-success)' : 'var(--color-danger)'};">
                        ${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%
                      </td>
                      <td style="padding: 12px 16px; text-align: right; color: var(--color-danger); font-family: monospace;">
                        -${p.max_drawdown_pct.toFixed(2)}%
                      </td>
                      <td style="padding: 12px 16px; text-align: right; font-family: monospace; font-weight: 600;">
                        ${p.sharpe_ratio !== undefined ? p.sharpe_ratio.toFixed(2) : 'N/A'}
                      </td>
                      <td style="padding: 12px 16px; text-align: right; font-family: monospace;">
                        <span style="font-weight: 600; color: ${isSig ? 'var(--color-success)' : 'var(--text-primary)'};">${pct}</span>
                        <div style="font-size: 10px; color: var(--text-muted);">${pVal.startsWith('<') ? 'p ' + pVal : 'p = ' + pVal}</div>
                      </td>
                      <td style="padding: 12px 16px; text-align: center;">
                        <span class="badge ${isSig ? 'badge-success' : 'badge-neutral'}" style="font-size: 10px;">
                          ${isSig ? 'P < 0.05' : 'Null Range'}
                        </span>
                      </td>
                      <td style="padding: 12px 16px; text-align: right; font-weight: 600; color: ${spreadCsi >= 0 ? 'var(--color-success)' : 'var(--color-danger)'};">
                        ${spreadCsi >= 0 ? '+' : ''}${spreadCsi.toFixed(2)}%
                      </td>
                      <td style="padding: 12px 16px; text-align: right; font-weight: 600; color: ${spreadTaotie >= 0 ? 'var(--color-success)' : 'var(--color-danger)'};">
                        ${spreadTaotie >= 0 ? '+' : ''}${spreadTaotie.toFixed(2)}%
                      </td>
                      <td style="padding: 12px 16px; text-align: center;">
                        <a href="#path/${p.path_id}" class="btn btn-sm btn-outline" style="font-size: 11px; padding: 3px 8px; text-decoration: none;">
                          Inspect
                        </a>
                      </td>
                    </tr>
                  `;
                }).join("")}
              </tbody>
            </table>
          </div>
        </div>
      `;

      // Attach event listeners
      this.attachEvents(containerId, chartPaths);

      // Render cross-model chart
      setTimeout(() => {
        this.updateChart(chartPaths);
      }, 50);

    } catch (err) {
      console.error("Error rendering AnimalsView:", err);
      container.innerHTML = `<div class="card" style="text-align:center; padding:2rem; color:var(--color-danger);">Failed to render Animals View: ${err.message}</div>`;
    }
  },

  updateChart(paths) {
    const dates = window.arenaAdapter.getNavDates();
    const taotieCurve = window.arenaAdapter.getBenchmarkTaotieCurve();
    const csi300Curve = window.arenaAdapter.getBenchmarkCsi300Curve();
    window.ArenaCharts.renderCrossModelAnimalCurves(
      "animal-cross-model-chart",
      dates,
      paths,
      taotieCurve,
      csi300Curve,
      this.activeMetric
    );

    // Maintain benchmark pill selection state
    document.querySelectorAll("#animal-benchmarks-pill-group .benchmark-pill").forEach(pill => {
      const bmKey = pill.getAttribute("data-benchmark");
      window.ArenaCharts.toggleBenchmark("animal-cross-model-chart", bmKey, pill.classList.contains("is-active"));
    });
  },

  attachEvents(containerId, currentPaths) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Zoo Mode Switcher (Single vs Multi)
    container.querySelectorAll(".zoo-mode-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const mode = e.currentTarget.getAttribute("data-mode");
        this.comparisonMode = mode;
        this.render(containerId);
      });
    });

    // Model Focus select (Multi-Animal Mode)
    const modelFocusSelect = container.querySelector("#zoo-focus-model-select");
    if (modelFocusSelect) {
      modelFocusSelect.addEventListener("change", (e) => {
        this.activeFocusModel = e.target.value;
        this.render(containerId);
      });
    }

    // Multi-Action Buttons (Representative, All in Category, Clear)
    container.querySelectorAll(".zoo-multi-action-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const action = e.currentTarget.getAttribute("data-action");
        const allAnimals = window.arenaAdapter.getAllAnimals();
        const filteredAnimals = this.activeCategory === "All"
          ? allAnimals
          : allAnimals.filter(a => a.category === this.activeCategory);

        if (action === "rep") {
          this.selectedAnimalIds = ["robot", "sloth-2", "snail-2", "turtle", "rabbit-1", "koala", "eagle-11-2", "whale-shark"];
        } else if (action === "all_cat") {
          const idsToAdd = filteredAnimals.map(a => a.id);
          this.selectedAnimalIds = Array.from(new Set([...this.selectedAnimalIds, ...idsToAdd]));
        } else if (action === "clear") {
          this.selectedAnimalIds = ["robot"];
        }
        this.render(containerId);
      });
    });

    // Category button clicks
    container.querySelectorAll(".animal-cat-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const cat = e.currentTarget.getAttribute("data-cat");
        this.activeCategory = cat;
        if (cat !== "All") {
          const matching = window.arenaAdapter.getAllAnimals().filter(a => a.category === cat);
          if (matching.length > 0 && !matching.some(a => a.id === this.activeAnimalId)) {
            this.activeAnimalId = matching[0].id;
          }
        }
        this.render(containerId);
      });
    });

    // Dropdown selection change (Single mode)
    const animalDropdown = container.querySelector("#zoo-animal-dropdown");
    if (animalDropdown) {
      animalDropdown.addEventListener("change", (e) => {
        const aId = e.target.value;
        this.activeAnimalId = aId;
        window.location.hash = `#animals/${aId}`;
        this.render(containerId);
      });
    }

    // Animal chip button clicks
    container.querySelectorAll(".animal-chip-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const aId = e.currentTarget.getAttribute("data-animal-id");
        if (this.comparisonMode === "single") {
          this.activeAnimalId = aId;
          window.location.hash = `#animals/${aId}`;
          this.render(containerId);
        } else {
          // Uncapped multi-toggle!
          if (this.selectedAnimalIds.includes(aId)) {
            if (this.selectedAnimalIds.length > 1) {
              this.selectedAnimalIds = this.selectedAnimalIds.filter(id => id !== aId);
            }
          } else {
            this.selectedAnimalIds.push(aId);
          }
          this.render(containerId);
        }
      });
    });

    // Metric button clicks
    container.querySelectorAll(".animal-metric-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const metric = e.currentTarget.getAttribute("data-metric");
        this.activeMetric = metric;
        container.querySelectorAll(".animal-metric-btn").forEach(b => {
          b.classList.remove("btn-primary");
          b.classList.add("btn-outline");
        });
        e.currentTarget.classList.add("btn-primary");
        e.currentTarget.classList.remove("btn-outline");

        this.updateChart(currentPaths);
      });
    });

    // Benchmark pill clicks
    container.querySelectorAll("#animal-benchmarks-pill-group .benchmark-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const isActive = pill.classList.toggle("is-active");
        const bmKey = pill.getAttribute("data-benchmark");
        window.ArenaCharts.toggleBenchmark("animal-cross-model-chart", bmKey, isActive);
      });
    });
  }
};
