/**
 * web/js/views/decision_audit.js
 * ==============================
 * Decision Archaeology & Comparative Sandbox View:
 * Evaluates historical model selection decisions (Counterfactual Branch Audit)
 * and provides an interactive multi-subject comparator sandbox.
 * 
 * Organization:
 *   - Quick-Select Curated Presets bar (Case 1: Architecture, Case 2: Feature Pruning, Custom Sandbox)
 *   - 3-Slot Comparator (Slot A vs Slot B vs optional Slot C / Benchmark)
 *   - 28-Animal Execution Handler Selector
 *   - Side-by-side Null Court / Arbiter scorecards
 *   - Synchronized Dual-Grid NAV & Spread/Regret Trajectory Chart
 *   - 28-Animal Cross-Handler Robustness Matrix
 */

window.DecisionAuditView = {
  activePreset: "fork_model_selection_20260626",
  slotA: "CONTESTANT_B",
  slotB: "CONTESTANT_A",
  slotC: "BENCHMARK_taotie",
  activeAnimalId: "robot",

  render(containerId, params) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const forks = window.arenaAdapter.getDecisionForks() || [];
    const allSubjects = window.arenaAdapter.getAllContestantsAndBenchmarks() || [];
    const allAnimals = window.arenaAdapter.getAllAnimals() || [];

    // Parse params if navigated from link/route
    if (params) {
      if (typeof params === "object") {
        if (params.forkId) this.applyPreset(params.forkId, forks);
        if (params.animalId) this.activeAnimalId = params.animalId;
      } else if (typeof params === "string") {
        this.applyPreset(params, forks);
      }
    }

    // Validate slots against available subjects
    const validIds = allSubjects.map(s => s.id);
    if (!validIds.includes(this.slotA)) {
      this.slotA = validIds[0] || "CONTESTANT_B";
    }
    if (!validIds.includes(this.slotB)) {
      this.slotB = validIds[1] || "CONTESTANT_A";
    }
    if (this.slotC && !validIds.includes(this.slotC)) {
      this.slotC = "";
    }

    // Retrieve full profiles for Slot A, B, and C
    const profA = window.arenaAdapter.getSubjectProfile(this.slotA, this.activeAnimalId);
    const profB = window.arenaAdapter.getSubjectProfile(this.slotB, this.activeAnimalId);
    const profC = this.slotC ? window.arenaAdapter.getSubjectProfile(this.slotC, this.activeAnimalId) : null;

    if (!profA || !profB) return;

    // Active animal object
    const currentAnimal = allAnimals.find(a => a.id === this.activeAnimalId) || allAnimals[0] || { id: "robot", name: "Robot 22/3" };

    // Active preset / fork object if applicable
    const activeFork = forks.find(f => (f.id === this.activePreset || f.fork_id === this.activePreset));

    // Calculate Head-to-Head delta on active animal
    const deltaRetAB = Number((profA.totalReturnPct - profB.totalReturnPct).toFixed(2));
    const isABetter = deltaRetAB >= 0;

    // Cross-Animal Win Count & Comparisons
    let winCountA = 0;
    let winCountB = 0;
    const animalComparisons = [];

    allAnimals.forEach(animal => {
      const aPath = window.arenaAdapter.getPath(`${this.slotA}_${animal.id}`);
      const bPath = window.arenaAdapter.getPath(`${this.slotB}_${animal.id}`);
      const cPath = this.slotC ? window.arenaAdapter.getPath(`${this.slotC}_${animal.id}`) : null;

      // Returns for this animal
      const retA = aPath ? aPath.total_return_pct : profA.totalReturnPct;
      const retB = bPath ? bPath.total_return_pct : profB.totalReturnPct;
      const retC = cPath ? cPath.total_return_pct : (profC ? profC.totalReturnPct : null);

      const spread = Number((retA - retB).toFixed(2));
      if (spread > 0) winCountA++;
      else if (spread < 0) winCountB++;

      animalComparisons.push({
        animalId: animal.id,
        animalName: animal.name || animal.id,
        category: animal.category || "Execution",
        retA: retA,
        retB: retB,
        retC: retC,
        spread: spread
      });
    });

    const totalAnimals = animalComparisons.length || 28;
    const winRatePctA = Number(((winCountA / totalAnimals) * 100).toFixed(0));

    // Render Main Layout
    container.innerHTML = `
      <div class="view-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
          <div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
              <h1 class="view-title">Decision Archaeology & Sandbox</h1>
              <span class="badge badge-warning">Counterfactual Audit</span>
              <span class="badge badge-neutral" style="font-family: monospace;">Multi-Subject Engine</span>
            </div>
            <p class="view-subtitle">Interactive counterfactual evaluation across historical model selection forks, physical/theoretical benchmarks, and 28 execution containers</p>
          </div>
          <button class="chart-spec-pill" style="align-self: center;" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.toggle();">
            📖 Field Guide Specs
          </button>
        </div>
      </div>

      <!-- Workbench Control Center (Unified Presets + 3 Comparator Slots) -->
      <div class="card" style="margin-bottom: 24px; padding: 18px 20px; background: rgba(30, 41, 59, 0.4); border: 1px solid var(--border-color); box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06);">
          <!-- Curated Presets Pills -->
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-right: 4px;">
              🏛️ Presets:
            </span>
            ${forks.map(f => {
              const fid = f.id || f.fork_id;
              const isSelected = this.activePreset === fid;
              return `
                <button class="btn btn-sm ${isSelected ? 'btn-primary' : 'btn-secondary'} preset-btn" data-preset="${fid}">
                  ${f.title}
                </button>
              `;
            }).join('')}
            <button class="btn btn-sm ${this.activePreset === 'custom' ? 'btn-primary' : 'btn-secondary'} preset-btn" data-preset="custom">
              🧪 Custom Sandbox
            </button>
          </div>

          <!-- Animal Selector -->
          <div style="display: flex; align-items: center; gap: 8px;">
            <label style="font-size: 12px; color: var(--text-secondary); font-weight: 600;">🐾 Execution Handler:</label>
            <select id="archaeology-animal-select" class="filter-select" style="min-width: 190px;">
              ${allAnimals.map(a => `
                <option value="${a.id}" ${a.id === this.activeAnimalId ? 'selected' : ''}>
                  ${a.name}
                </option>
              `).join('')}
            </select>
          </div>
        </div>

        <!-- 3 Comparator Selection Slots -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px;">
          <!-- Slot A -->
          <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 10px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 11px; font-weight: 700; color: #10b981; letter-spacing: 0.05em;">● SUBJECT A (Baseline / Chosen)</span>
              <span class="badge badge-success" style="font-size: 10px; padding: 2px 6px;">Slot A</span>
            </div>
            <select id="slot-a-select" class="filter-select" style="width: 100%; font-weight: 600;">
              ${this.renderSubjectOptions(allSubjects, this.slotA)}
            </select>
          </div>

          <!-- Slot B -->
          <div style="background: rgba(244, 63, 94, 0.06); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 8px; padding: 10px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 11px; font-weight: 700; color: #f43f5e; letter-spacing: 0.05em;">● SUBJECT B (Challenger / Rejected)</span>
              <span class="badge badge-danger" style="font-size: 10px; padding: 2px 6px;">Slot B</span>
            </div>
            <select id="slot-b-select" class="filter-select" style="width: 100%; font-weight: 600;">
              ${this.renderSubjectOptions(allSubjects, this.slotB)}
            </select>
          </div>

          <!-- Slot C -->
          <div style="background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px; padding: 10px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 0.05em;">● SUBJECT C (Reference / Benchmark)</span>
              <span class="badge badge-neutral" style="font-size: 10px; padding: 2px 6px;">Optional</span>
            </div>
            <select id="slot-c-select" class="filter-select" style="width: 100%;">
              <option value="">-- None (2-way comparison) --</option>
              ${this.renderSubjectOptions(allSubjects, this.slotC)}
            </select>
          </div>
        </div>
      </div>

      <!-- Historical Context or Sandbox Intelligence Banner -->
      <div class="card" style="margin-bottom: 24px; border-left: 4px solid ${isABetter ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 12px;">
          <div>
            <h2 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">
              ${activeFork ? activeFork.title : `Comparative Sandbox: ${profA.shortName} vs ${profB.shortName}${profC ? ` vs ${profC.shortName}` : ''}`}
            </h2>
            <span style="font-size: 12px; color: var(--text-muted); font-family: monospace;">
              ${activeFork ? `Decision Date: ${activeFork.decision_date || activeFork.date || 'Historical Fork'}` : `Custom Counterfactual Session • Active Handler: ${currentAnimal.name}`}
            </span>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">Spread (A − B on ${currentAnimal.name}):</div>
            <span class="badge ${isABetter ? 'badge-success' : 'badge-danger'}" style="font-size: 13px; font-weight: 700; padding: 4px 12px;">
              ${isABetter ? '✅' : '⚠️'} ${deltaRetAB >= 0 ? '+' : ''}${deltaRetAB}% (${isABetter ? 'A Outperformed' : 'B Outperformed'})
            </span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0;">
          ${activeFork 
            ? (activeFork.historical_context || activeFork.description) 
            : `Evaluating relative alpha and stability between <strong>${profA.name}</strong> and <strong>${profB.name}</strong> across all market friction regimes. Subject A holds a <strong>${winRatePctA}%</strong> win rate across the 28 animal containers.`}
        </p>
      </div>

      <!-- Side-by-Side Subject Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-bottom: 24px;">
        <!-- Subject A Card -->
        <div class="card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">🏆</span>
              <div>
                <h3 style="font-size: 15px; font-weight: 700; color: #10b981; margin: 0;">
                  ${profA.name}
                </h3>
                <span style="font-size: 11px; color: var(--text-muted);">${profA.tag}</span>
              </div>
            </div>
            <span class="badge badge-success">SLOT A</span>
          </div>
          <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px;">
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">${currentAnimal.name.split(' ')[0]} Return</div>
              <div class="kpi-value ${profA.totalReturnPct >= 0 ? 'text-up' : 'text-down'}" style="font-size: 16px;">
                ${profA.totalReturnPct >= 0 ? '+' : ''}${profA.totalReturnPct.toFixed(2)}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title" data-tooltip-term="mdd">Max DD</div>
              <div class="kpi-value" style="font-size: 16px; color: var(--accent-rose);">
                ${profA.maxDrawdownPct ? profA.maxDrawdownPct.toFixed(2) : '0'}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title" data-tooltip-term="null_court">Null Court</div>
              <div class="kpi-value" style="font-size: 13px; color: var(--accent-emerald);">
                ${profA.nullCourt || 'Pass'}
              </div>
            </div>
          </div>
        </div>

        <!-- Subject B Card -->
        <div class="card" style="border: 1px solid rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">⚔️</span>
              <div>
                <h3 style="font-size: 15px; font-weight: 700; color: #f43f5e; margin: 0;">
                  ${profB.name}
                </h3>
                <span style="font-size: 11px; color: var(--text-muted);">${profB.tag}</span>
              </div>
            </div>
            <span class="badge badge-danger">SLOT B</span>
          </div>
          <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px;">
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">${currentAnimal.name.split(' ')[0]} Return</div>
              <div class="kpi-value ${profB.totalReturnPct >= 0 ? 'text-up' : 'text-down'}" style="font-size: 16px;">
                ${profB.totalReturnPct >= 0 ? '+' : ''}${profB.totalReturnPct.toFixed(2)}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title" data-tooltip-term="mdd">Max DD</div>
              <div class="kpi-value" style="font-size: 16px; color: var(--accent-rose);">
                ${profB.maxDrawdownPct ? profB.maxDrawdownPct.toFixed(2) : '0'}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title" data-tooltip-term="null_court">Null Court</div>
              <div class="kpi-value" style="font-size: 13px; color: var(--accent-emerald);">
                ${profB.nullCourt || 'Pass'}
              </div>
            </div>
          </div>
        </div>

        <!-- Subject C Card (Conditional) -->
        ${profC ? `
          <div class="card" style="border: 1px solid rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">🏛️</span>
                <div>
                  <h3 style="font-size: 15px; font-weight: 700; color: #38bdf8; margin: 0;">
                    ${profC.name}
                  </h3>
                  <span style="font-size: 11px; color: var(--text-muted);">${profC.tag}</span>
                </div>
              </div>
              <span class="badge badge-info">SLOT C</span>
            </div>
            <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px;">
              <div class="kpi-card" style="padding: 10px;">
                <div class="kpi-title">${currentAnimal.name.split(' ')[0]} Return</div>
                <div class="kpi-value ${profC.totalReturnPct >= 0 ? 'text-up' : 'text-down'}" style="font-size: 16px;">
                  ${profC.totalReturnPct >= 0 ? '+' : ''}${profC.totalReturnPct.toFixed(2)}%
                </div>
              </div>
              <div class="kpi-card" style="padding: 10px;">
                <div class="kpi-title">Max DD</div>
                <div class="kpi-value" style="font-size: 16px; color: var(--accent-rose);">
                  ${profC.maxDrawdownPct ? profC.maxDrawdownPct.toFixed(2) : '0'}%
                </div>
              </div>
              <div class="kpi-card" style="padding: 10px;">
                <div class="kpi-title">Role</div>
                <div class="kpi-value" style="font-size: 13px; color: var(--text-secondary);">
                  ${profC.nullCourt || 'Benchmark'}
                </div>
              </div>
            </div>
          </div>
        ` : ''}
      </div>

      <!-- Synchronized Trajectory & Spread Chart -->
      <div class="chart-card" style="margin-bottom: 24px;">
        <div class="chart-card-header" style="flex-wrap: wrap; gap: 12px;">
          <div>
            <div class="chart-card-title">Synchronized Trajectory & Counterfactual Spread / Regret</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
              Upper panel: Out-of-sample NAV trajectories. Lower panel: Relative spread (A − B). Positive values indicate Slot A outperformance.
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 12px; font-family: monospace; color: var(--accent-cyan);">
              Active Execution Container: <strong>${currentAnimal.name}</strong>
            </div>
            <button class="chart-spec-pill" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.openCategory('animals');">
              🐾 Handler Specs
            </button>
          </div>
        </div>
        <div id="chart-archaeology-trajectory" style="height: 480px; width: 100%;"></div>
      </div>

      <!-- 28-Animal Robustness Matrix -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div>
            <h3 style="font-size: 16px; font-weight: 700; margin: 0 0 4px 0;">
              28-Animal Cross-Handler Robustness Matrix
            </h3>
            <span style="font-size: 12px; color: var(--text-muted);">
              <strong>${profA.shortName}</strong> out-alpha'd <strong>${profB.shortName}</strong> in <strong>${winCountA} / ${totalAnimals}</strong> execution policies (${winRatePctA}% win rate).
            </span>
          </div>
          <div style="display: flex; gap: 8px;">
            <span class="badge badge-success">A Wins: ${winCountA}</span>
            <span class="badge badge-danger">B Wins: ${winCountB}</span>
            <span class="badge badge-neutral">Ties: ${totalAnimals - winCountA - winCountB}</span>
          </div>
        </div>
        <div class="table-responsive">
          <table class="table" style="font-size: 12px;">
            <thead>
              <tr>
                <th data-tooltip-term="execution_handler">Execution Handler</th>
                <th>Category</th>
                <th style="text-align: right;">${profA.shortName} (A)</th>
                <th style="text-align: right;">${profB.shortName} (B)</th>
                ${profC ? `<th style="text-align: right;">${profC.shortName} (C)</th>` : ''}
                <th style="text-align: right;">Spread (A − B)</th>
                <th style="text-align: center;">Verdict</th>
              </tr>
            </thead>
            <tbody>
              ${animalComparisons.map(ac => {
                const isWinA = ac.spread > 0;
                const isTie = ac.spread === 0;
                return `
                  <tr style="${ac.animalId === this.activeAnimalId ? 'background: rgba(56, 189, 248, 0.08); font-weight: 600;' : ''}">
                    <td>
                      <span style="font-weight: 600; color: var(--text-primary);">${ac.animalName}</span>
                      <span style="font-size: 10px; color: var(--text-muted); margin-left: 4px;">(${ac.animalId})</span>
                    </td>
                    <td><span class="badge badge-neutral">${ac.category}</span></td>
                    <td style="text-align: right; font-weight: 600;" class="${ac.retA >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.retA >= 0 ? '+' : ''}${ac.retA.toFixed(2)}%
                    </td>
                    <td style="text-align: right; font-weight: 600;" class="${ac.retB >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.retB >= 0 ? '+' : ''}${ac.retB.toFixed(2)}%
                    </td>
                    ${profC ? `
                      <td style="text-align: right; font-weight: 600; color: #38bdf8;">
                        ${ac.retC !== null ? `${ac.retC >= 0 ? '+' : ''}${ac.retC.toFixed(2)}%` : '—'}
                      </td>
                    ` : ''}
                    <td style="text-align: right; font-weight: 700; font-family: monospace;" class="${ac.spread >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.spread >= 0 ? '+' : ''}${ac.spread.toFixed(2)}%
                    </td>
                    <td style="text-align: center;">
                      ${isTie 
                        ? '<span class="badge badge-neutral">Flat</span>' 
                        : `<span class="badge ${isWinA ? 'badge-success' : 'badge-danger'}">${isWinA ? 'A Won' : 'B Won'}</span>`}
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Bind Event Listeners
    this.bindEvents(container, containerId, forks);

    // Render Dual-Grid Chart
    const dates = window.arenaAdapter.getNavDates();
    const modelsData = [
      {
        name: profA.shortName,
        curve: profA.curve,
        color: "#10b981",
        isBenchmark: profA.isBenchmark
      },
      {
        name: profB.shortName,
        curve: profB.curve,
        color: "#f43f5e",
        isBenchmark: profB.isBenchmark
      }
    ];

    if (profC && profC.curve && profC.curve.length > 0) {
      modelsData.push({
        name: profC.shortName,
        curve: profC.curve,
        color: "#38bdf8",
        isBenchmark: profC.isBenchmark
      });
    }

    if (dates && dates.length > 0) {
      setTimeout(() => {
        window.ArenaCharts.renderCustomArchaeology(
          "chart-archaeology-trajectory",
          dates,
          modelsData,
          currentAnimal.name
        );
      }, 50);
    }
  },

  applyPreset(presetId, forks) {
    this.activePreset = presetId;
    if (presetId === "custom") {
      return;
    }

    const fork = forks.find(f => (f.id === presetId || f.fork_id === presetId));
    if (fork) {
      this.slotA = fork.chosen_contestant_id || fork.chosen_id || "CONTESTANT_B";
      this.slotB = fork.rejected_contestant_id || fork.rejected_id || "CONTESTANT_A";
      this.slotC = "BENCHMARK_taotie";
    }
  },

  renderSubjectOptions(allSubjects, currentSelectedId) {
    const models = allSubjects.filter(s => !s.isBenchmark);
    const benchmarks = allSubjects.filter(s => s.isBenchmark);

    let html = "";
    if (models.length > 0) {
      html += `<optgroup label="Model Candidates">`;
      models.forEach(m => {
        html += `<option value="${m.id}" ${m.id === currentSelectedId ? 'selected' : ''}>${m.name}</option>`;
      });
      html += `</optgroup>`;
    }
    if (benchmarks.length > 0) {
      html += `<optgroup label="Arena Benchmarks">`;
      benchmarks.forEach(b => {
        html += `<option value="${b.id}" ${b.id === currentSelectedId ? 'selected' : ''}>${b.name}</option>`;
      });
      html += `</optgroup>`;
    }
    return html;
  },

  bindEvents(container, containerId, forks) {
    // Preset buttons
    container.querySelectorAll(".preset-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const pid = btn.getAttribute("data-preset");
        this.applyPreset(pid, forks);
        this.render(containerId);
      });
    });

    // Animal selector
    const animalSelect = container.querySelector("#archaeology-animal-select");
    if (animalSelect) {
      animalSelect.addEventListener("change", (e) => {
        this.activeAnimalId = e.target.value;
        this.render(containerId);
      });
    }

    // Slot A selector
    const slotASelect = container.querySelector("#slot-a-select");
    if (slotASelect) {
      slotASelect.addEventListener("change", (e) => {
        this.slotA = e.target.value;
        this.activePreset = "custom";
        this.render(containerId);
      });
    }

    // Slot B selector
    const slotBSelect = container.querySelector("#slot-b-select");
    if (slotBSelect) {
      slotBSelect.addEventListener("change", (e) => {
        this.slotB = e.target.value;
        this.activePreset = "custom";
        this.render(containerId);
      });
    }

    // Slot C selector
    const slotCSelect = container.querySelector("#slot-c-select");
    if (slotCSelect) {
      slotCSelect.addEventListener("change", (e) => {
        this.slotC = e.target.value;
        this.activePreset = "custom";
        this.render(containerId);
      });
    }
  }
};
