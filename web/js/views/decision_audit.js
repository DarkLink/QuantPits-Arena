/**
 * web/js/views/decision_audit.js
 * ==============================
 * Decision Archaeology View:
 * Evaluates historical model selection decisions (Counterfactual Branch Audit):
 *   - Fork 1: Architecture Selection (Candidate-B vs. Candidate-A)
 *   - Fork 2: Feature Dimensionality (Candidate-F vs. Candidate-E)
 * Features:
 *   - Counterfactual Decision Regret Curve (NAV_rejected - NAV_chosen)
 *   - Execution Handler Selector (allows switching across all 28 animal variants)
 *   - 28-Animal Robustness Matrix
 */

window.DecisionAuditView = {
  activeForkId: "fork_model_selection_20260626",
  activeAnimalId: "robot",

  render(containerId, forkId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (forkId) {
      if (typeof forkId === "object") {
        this.activeForkId = forkId.forkId || "fork_model_selection_20260626";
      } else {
        this.activeForkId = String(forkId);
      }
    }

    const forks = window.arenaAdapter.getDecisionForks();
    const fork = forks.find(f => f.id === this.activeForkId || f.fork_id === this.activeForkId) || forks[0];
    if (!fork) return;
    this.activeForkId = fork.id || fork.fork_id;

    const chosenCid = fork.chosen_contestant_id || fork.chosen_id;
    const rejectedCid = fork.rejected_contestant_id || fork.rejected_id;
    const chosenContestant = window.arenaAdapter.getContestant(chosenCid);
    const rejectedContestant = window.arenaAdapter.getContestant(rejectedCid);

    // Get paths for the selected animal
    const chosenPath = window.arenaAdapter.getPath(`${chosenCid}_${this.activeAnimalId}`) || window.arenaAdapter.getPath(`${chosenCid}_robot`);
    const rejectedPath = window.arenaAdapter.getPath(`${rejectedCid}_${this.activeAnimalId}`) || window.arenaAdapter.getPath(`${rejectedCid}_robot`);

    const chosenRet = chosenPath ? chosenPath.total_return_pct : 0;
    const rejectedRet = rejectedPath ? rejectedPath.total_return_pct : 0;
    const diffRet = chosenRet - rejectedRet;
    const isChosenBetter = diffRet >= 0;

    // Cross-animal comparison
    const chosenPaths = window.arenaAdapter.getFilteredPaths({ contestantId: chosenCid });
    const rejectedPaths = window.arenaAdapter.getFilteredPaths({ contestantId: rejectedCid });
    let chosenWinCount = 0;
    const animalComparisons = [];

    chosenPaths.forEach(cp => {
      const rp = rejectedPaths.find(p => p.animal_id === cp.animal_id);
      if (rp) {
        const spread = cp.total_return_pct - rp.total_return_pct;
        if (spread > 0) chosenWinCount++;
        animalComparisons.push({
          animalId: cp.animal_id,
          animalName: cp.animal_name || cp.animal_id,
          category: cp.animal_category,
          chosenRet: cp.total_return_pct,
          rejectedRet: rp.total_return_pct,
          spread: spread
        });
      }
    });

    // Available animals for dropdown
    const availableAnimals = [
      { id: "robot", name: "Robot 22/3 (Baseline)" },
      { id: "sloth-1", name: "Sloth-1 (1W Lag)" },
      { id: "sloth-2", name: "Sloth-2 (2W Lag)" },
      { id: "snail-1", name: "Snail-1 (1W Holding)" },
      { id: "turtle", name: "Turtle (Low Turnover)" },
      { id: "rabbit-1", name: "Rabbit-1 (High Turnover)" },
      { id: "koala", name: "Koala (Inverted Selection)" },
      { id: "eagle-11-2", name: "Eagle 11/2 (Concentrated)" },
      { id: "eagle-44-6", name: "Eagle 44/6 (Broad)" },
      { id: "whale-shark", name: "Whale Shark (50% Pool)" }
    ];

    container.innerHTML = `
      <div class="view-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
          <div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
              <h1 class="view-title">Decision Archaeology</h1>
              <span class="badge badge-warning">Counterfactual Audit</span>
            </div>
            <p class="view-subtitle">Revisiting historical model selection forks to evaluate whether rejected architectures outperform in real out-of-sample arena</p>
          </div>

          <!-- Decision Fork Buttons -->
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            ${forks.map(f => {
              const fid = f.id || f.fork_id;
              return `
                <button class="btn ${fid === this.activeForkId ? 'btn-primary' : 'btn-secondary'} fork-btn" data-fork="${fid}">
                  ${f.title}
                </button>
              `;
            }).join('')}
          </div>
        </div>
      </div>

      <!-- Fork Banner & Verdict -->
      <div class="card" style="margin-bottom: 24px; border-left: 4px solid ${isChosenBetter ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 12px;">
          <div>
            <h2 style="font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">
              ${fork.title}
            </h2>
            <span style="font-size: 12px; color: var(--text-muted); font-family: monospace;">Decision Date: ${fork.decision_date || fork.date}</span>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Out-of-Sample Verdict (${this.activeAnimalId.toUpperCase()}):</div>
            <span class="badge ${isChosenBetter ? 'badge-success' : 'badge-danger'}" style="font-size: 13px; font-weight: 700; padding: 4px 12px;">
              ${isChosenBetter ? '✅ Decision Validated (Chosen Outperformed)' : '⚠️ Regret Observed (Rejected Outperformed)'}
            </span>
          </div>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0;">
          ${fork.historical_context || fork.description}
        </p>
      </div>

      <!-- Side-by-Side Model Cards -->
      <div class="grid-2col" style="margin-bottom: 24px;">
        <!-- Chosen Model Card -->
        <div class="card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">🏆</span>
              <h3 style="font-size: 15px; font-weight: 700; color: #10b981;">
                Chosen Candidate: ${chosenContestant?.display_name || chosenCid}
              </h3>
            </div>
            <span class="badge badge-success">CHOSEN</span>
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.5;">
            <strong>Selection Rationale:</strong> Higher cross-validation stability and lower expected generalization error.
          </div>
          <div class="kpi-grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">${this.activeAnimalId.toUpperCase()} Return</div>
              <div class="kpi-value ${chosenRet >= 0 ? 'text-up' : 'text-down'}" style="font-size: 18px;">
                ${chosenRet >= 0 ? '+' : ''}${chosenRet.toFixed(2)}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">Max Drawdown</div>
              <div class="kpi-value" style="font-size: 18px; color: var(--accent-rose);">
                ${chosenPath ? chosenPath.max_drawdown_pct.toFixed(2) : '0'}%
              </div>
            </div>
          </div>
        </div>

        <!-- Rejected Model Card -->
        <div class="card" style="border: 1px solid rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">🚫</span>
              <h3 style="font-size: 15px; font-weight: 700; color: #f43f5e;">
                Rejected Candidate: ${rejectedContestant?.display_name || rejectedCid}
              </h3>
            </div>
            <span class="badge badge-danger">REJECTED</span>
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.5;">
            <strong>Rejection Reason:</strong> Deemed higher risk of in-sample overfitting or marginal incremental factor value.
          </div>
          <div class="kpi-grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">${this.activeAnimalId.toUpperCase()} Return</div>
              <div class="kpi-value ${rejectedRet >= 0 ? 'text-up' : 'text-down'}" style="font-size: 18px;">
                ${rejectedRet >= 0 ? '+' : ''}${rejectedRet.toFixed(2)}%
              </div>
            </div>
            <div class="kpi-card" style="padding: 10px;">
              <div class="kpi-title">Max Drawdown</div>
              <div class="kpi-value" style="font-size: 18px; color: var(--accent-rose);">
                ${rejectedPath ? rejectedPath.max_drawdown_pct.toFixed(2) : '0'}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Decision Regret Chart with Animal Handler Selector -->
      <div class="chart-card" style="margin-bottom: 24px;">
        <div class="chart-card-header" style="flex-wrap: wrap; gap: 12px;">
          <div>
            <div class="chart-card-title">Counterfactual Regret Curve (NAV_rejected - NAV_chosen)</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
              Lower panel displays cumulative decision regret. Regret &gt; 0 indicates the rejected candidate outperformed.
            </div>
          </div>

          <!-- Animal Selector -->
          <div style="display: flex; align-items: center; gap: 8px;">
            <label style="font-size: 12px; color: var(--text-secondary); font-weight: 600;">Execution Handler:</label>
            <select id="regret-animal-select" class="filter-select" style="min-width: 170px;">
              ${availableAnimals.map(a => `
                <option value="${a.id}" ${a.id === this.activeAnimalId ? 'selected' : ''}>${a.name}</option>
              `).join('')}
            </select>
          </div>
        </div>
        <div id="chart-decision-regret" style="height: 440px; width: 100%;"></div>
      </div>

      <!-- 28-Animal Robustness Matrix -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
          <div>
            <h3 style="font-size: 16px; font-weight: 700;">
              28-Animal Cross-Handler Robustness Matrix
            </h3>
            <span style="font-size: 12px; color: var(--text-muted);">
              Chosen candidate won <strong>${chosenWinCount} / ${animalComparisons.length}</strong> execution variations (${((chosenWinCount/Math.max(1, animalComparisons.length))*100).toFixed(0)}% win rate)
            </span>
          </div>
        </div>
        <div class="table-responsive">
          <table class="table" style="font-size: 12px;">
            <thead>
              <tr>
                <th>Execution Handler</th>
                <th>Category</th>
                <th style="text-align: right;">${chosenContestant?.display_name || chosenCid} (Chosen)</th>
                <th style="text-align: right;">${rejectedContestant?.display_name || rejectedCid} (Rejected)</th>
                <th style="text-align: right;">Spread</th>
                <th style="text-align: center;">Verdict</th>
              </tr>
            </thead>
            <tbody>
              ${animalComparisons.map(ac => {
                const isChosenWin = ac.spread >= 0;
                return `
                  <tr>
                    <td>
                      <span style="font-weight: 600; color: var(--text-primary);">${ac.animalName}</span>
                      <span style="font-size: 10px; color: var(--text-muted); margin-left: 4px;">(${ac.animalId})</span>
                    </td>
                    <td><span class="badge badge-neutral">${ac.category}</span></td>
                    <td style="text-align: right; font-weight: 600;" class="${ac.chosenRet >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.chosenRet >= 0 ? '+' : ''}${ac.chosenRet.toFixed(2)}%
                    </td>
                    <td style="text-align: right; font-weight: 600;" class="${ac.rejectedRet >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.rejectedRet >= 0 ? '+' : ''}${ac.rejectedRet.toFixed(2)}%
                    </td>
                    <td style="text-align: right; font-weight: 700; font-family: monospace;" class="${ac.spread >= 0 ? 'text-up' : 'text-down'}">
                      ${ac.spread >= 0 ? '+' : ''}${ac.spread.toFixed(2)}%
                    </td>
                    <td style="text-align: center;">
                      <span class="badge ${isChosenWin ? 'badge-success' : 'badge-danger'}">
                        ${isChosenWin ? 'Chosen Outperformed' : 'Regret'}
                      </span>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Bind fork switch buttons
    container.querySelectorAll(".fork-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const fid = btn.getAttribute("data-fork");
        window.appRouter.navigate("decision-audit", { forkId: fid });
      });
    });

    // Bind animal selector
    const animalSelect = document.getElementById("regret-animal-select");
    if (animalSelect) {
      animalSelect.addEventListener("change", (e) => {
        this.activeAnimalId = e.target.value;
        this.render(containerId, this.activeForkId);
      });
    }

    // Render chart
    const dates = window.arenaAdapter.getNavDates();
    const chosenCurve = window.arenaAdapter.getNavCurve(chosenPath ? chosenPath.path_id : `${chosenCid}_${this.activeAnimalId}`);
    const rejectedCurve = window.arenaAdapter.getNavCurve(rejectedPath ? rejectedPath.path_id : `${rejectedCid}_${this.activeAnimalId}`);

    if (dates && dates.length > 0 && chosenCurve && rejectedCurve) {
      setTimeout(() => {
        window.ArenaCharts.renderDecisionRegret(
          "chart-decision-regret",
          dates,
          chosenCurve,
          rejectedCurve,
          chosenContestant ? (chosenContestant.display_name || chosenContestant.anonymous_name) : "Chosen",
          rejectedContestant ? (rejectedContestant.display_name || rejectedContestant.anonymous_name) : "Rejected",
          this.activeAnimalId.toUpperCase()
        );
      }, 50);
    }
  }
};
