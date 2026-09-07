/**
 * web/js/views/dispatches.js
 * ==========================
 * Tournament Dispatches & Market Climate View
 * Decoupled into Executive Status (README Layer) & Episodic Narrative (Reader Layer).
 */

window.DispatchesView = {
  currentEpisode: null,

  render(containerId, params = {}) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
    const dispatches = window.arenaAdapter ? window.arenaAdapter.getDispatchesData() : null;

    // Fallback if no dispatches object exists
    const exec = dispatches?.executive || {
      tag: "🏆 Official Released Standing",
      badge: "Active",
      title: "Tournament Standing & Baseline",
      window_label: seasonMeta.period || "Current Season Window",
      nature_label: "Empirical strategy evaluation under execution constraints.",
      leader_summary: "Evaluation active across all animal variants."
    };

    const climate = dispatches?.climate || {
      tag: "🌪️ Market Climate Report",
      status_badge: "Active",
      title: "Cross-Market Volatility & Execution Dynamics",
      summary: "Tracking market liquidity, factor dispersion, and execution friction.",
      bullets: [
        "Active monitoring of cross-sectional return dispersion.",
        "Zero alpha leakage under cryptographic verification."
      ],
      decrypt_label: "Standard Weekly Cycle"
    };

    const episodes = dispatches?.episodes || [
      {
        id: "ep08",
        tab_label: "📜 Ep 01–08: The Forty-One Day King",
        badge: "Released",
        title: "Episodes 01–08: The 41-Day Baseline & The Eagle King",
        content_type: "ep08_baseline"
      },
      {
        id: "ep09",
        tab_label: "🔒 Ep 09: Sep 02 Breadth Shock",
        badge: "Embargoed",
        title: "Episode 09: The September 02 Breadth Shock",
        content_type: "ep09_embargoed"
      }
    ];

    // Ensure valid current episode
    if (params.episode && episodes.some(e => e.id === params.episode)) {
      this.currentEpisode = params.episode;
    } else if (!this.currentEpisode || !episodes.some(e => e.id === this.currentEpisode)) {
      this.currentEpisode = episodes[0]?.id || "ep08";
    }

    const firstEpId = episodes[0]?.id || "ep08";

    el.innerHTML = `
      <div class="doc-page-container">
        <!-- View Header -->
        <div class="view-header" style="text-align: center; margin-bottom: 2rem;">
          <div class="hero-tag" style="margin-bottom: 0.75rem;">
            <span>📜 ${seasonMeta.title || "QuantPits Arena"} Dispatches &amp; Market Climate</span>
          </div>
          <h1 class="view-title" style="font-size: 2.2rem; margin-bottom: 0.5rem;">Arena Dispatches</h1>
          <p class="view-subtitle" style="max-width: 720px; margin: 0 auto; font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;">
            Empirical chronicles of quantitative alpha models facing execution zoo frictions, regime shifts, and the Monte Carlo Null Court.
          </p>
        </div>

        <!-- Layer 1: Executive Status & Market Climate (The README Layer) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.25rem; margin-bottom: 2rem;">
          
          <!-- Card 1: Official Baseline Status -->
          <div class="card" style="border-left: 4px solid var(--brand-cyan); background: rgba(15, 23, 42, 0.55); padding: 1.25rem 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand-cyan); font-weight: 700;">
                ${exec.tag || "🏆 Official Baseline"}
              </span>
              <span class="badge" style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 0.75rem;">
                ${exec.badge || "Active"}
              </span>
            </div>
            <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
              ${exec.title}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.75rem;">
              <strong>Window:</strong> ${exec.window_label}<br>
              <strong>Nature:</strong> ${exec.nature_label}<br>
              <strong>Status:</strong> ${exec.leader_summary}
            </p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-sm btn-primary" onclick="window.DispatchesView.selectEpisode('${firstEpId}')" style="font-size: 0.8rem; padding: 4px 10px;">
                <span>📖 Read Latest Dispatch &rarr;</span>
              </button>
              <a href="#leaderboard" class="btn btn-sm btn-secondary" style="font-size: 0.8rem; padding: 4px 10px; text-decoration: none;">
                <span>🏆 View Leaderboard</span>
              </a>
            </div>
          </div>

          <!-- Card 2: Weekly Market Climate Report (Public facts, zero alpha leak) -->
          <div class="card" style="border-left: 4px solid var(--accent-amber); background: rgba(15, 23, 42, 0.55); padding: 1.25rem 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-amber); font-weight: 700;">
                ${climate.tag || "🌪️ Market Climate"}
              </span>
              <span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.75rem;">
                ${climate.status_badge || "Active"}
              </span>
            </div>
            <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
              ${climate.title}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.75rem;">
              <em>${climate.summary}</em>
            </p>
            <ul style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin: 0 0 0.75rem 1.25rem; padding: 0;">
              ${(climate.bullets || []).map(b => `<li>${b}</li>`).join("")}
            </ul>
            <div style="font-size: 0.78rem; color: var(--accent-amber); display: flex; align-items: center; gap: 6px;">
              <span>⏳</span> <strong>${climate.decrypt_label || "Continuous Monitoring"}</strong>
            </div>
          </div>
        </div>

        <!-- Layer 2: Episodic Reader Container -->
        <div class="card" style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border-subtle); padding: 1.75rem; border-radius: var(--radius-md);">
          
          <!-- Dispatch Navigation Tabs -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1rem; margin-bottom: 1.5rem;">
            
            <!-- Episode Tabs -->
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;" id="dispatch-tabs-container">
              ${episodes.map(ep => `
                <button id="tab-btn-${ep.id}" class="btn btn-sm ${this.currentEpisode === ep.id ? 'btn-primary' : 'btn-secondary'}" onclick="window.DispatchesView.selectEpisode('${ep.id}')">
                  <span>${ep.tab_label}</span>
                  ${ep.badge ? `<span style="font-size: 10px; opacity: 0.8; margin-left: 4px;">(${ep.badge})</span>` : ''}
                </button>
              `).join("")}
            </div>

            <div style="font-size: 0.8rem; color: var(--text-tertiary);">
              Official Tournament Log · ${seasonMeta.short_title || "Arena"}
            </div>
          </div>

          <!-- Dynamic Episode Content Area -->
          <div id="dispatch-article-body">
            ${this.renderArticleContent()}
          </div>

        </div>
      </div>
    `;
  },

  selectEpisode(epId) {
    this.currentEpisode = epId;
    const bodyEl = document.getElementById("dispatch-article-body");
    if (bodyEl) {
      bodyEl.innerHTML = this.renderArticleContent();
    }
    
    // Update button states dynamically
    const container = document.getElementById("dispatch-tabs-container");
    if (container) {
      const btns = container.querySelectorAll("button");
      btns.forEach(btn => {
        if (btn.id === `tab-btn-${epId}`) {
          btn.className = "btn btn-sm btn-primary";
        } else {
          btn.className = "btn btn-sm btn-secondary";
        }
      });
    }
  },

  renderArticleContent() {
    const dispatches = window.arenaAdapter ? window.arenaAdapter.getDispatchesData() : null;
    const episodes = dispatches?.episodes || [];
    const activeEp = episodes.find(e => e.id === this.currentEpisode);

    if (activeEp) {
      if (activeEp.content_html) {
        return `
          <article class="prose" style="max-width: 820px; margin: 0 auto; color: var(--text-secondary); line-height: 1.75; font-size: 0.95rem;">
            <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
              <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem;">
                <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--brand-cyan); border: 1px solid rgba(56, 189, 248, 0.3);">
                  ${activeEp.badge || "Dispatch"}
                </span>
                <span style="font-size: 0.8rem; color: var(--text-tertiary);">
                  Date: ${activeEp.date || "2026"} · ${activeEp.read_time || "4 min read"}
                </span>
              </div>
              <h2 style="font-size: 1.9rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
                ${activeEp.title}
              </h2>
              ${activeEp.summary ? `
                <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 0.5rem; font-style: italic;">
                  ${activeEp.summary}
                </p>
              ` : ''}
            </div>
            ${activeEp.content_html}
            <div style="margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle); text-align: center; font-size: 0.85rem; color: var(--text-tertiary);">
              🏛️ <em>QuantPits Arena Official Tournament Log</em>
            </div>
          </article>
        `;
      }
      if (activeEp.content_type === "ep09_embargoed") {
        return this.renderEp09Embargoed();
      }
    }

    if (this.currentEpisode === "ep09") {
      return this.renderEp09Embargoed();
    }
    return this.renderEp08En();
  },

  renderEp08En() {
    return `
      <article class="prose" style="max-width: 820px; margin: 0 auto; color: var(--text-secondary); line-height: 1.75; font-size: 0.95rem;">
        
        <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem;">
            <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--brand-cyan); border: 1px solid rgba(56, 189, 248, 0.3);">
              Retrospective Backtest Baseline
            </span>
            <span style="font-size: 0.8rem; color: var(--text-tertiary);">
              Window: 2026-07-03 ~ 2026-08-28 · 41 Trading Days
            </span>
          </div>
          <h2 style="font-size: 1.9rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
            Episodes 01–08: The 41-Day Baseline &amp; The Eagle King
          </h2>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0;">
            Executable Universe Benchmark: Taotie <code>1.0000 &rarr; 1.0232 (+2.32%)</code>
          </p>
        </div>

        <!-- Section I -->
        <h3 style="color: var(--text-primary); font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.75rem;">
          I. Nature of the Evaluation: Retrospective Backtest
        </h3>
        <p>
          This 41-day baseline covers the opening 8 weeks of the tournament calendar (Episodes 01–08):
        </p>
        <ul style="margin-left: 1.25rem; margin-bottom: 1.25rem;">
          <li><strong>Retrospective Execution</strong>: The simulation for these 41 trading days was conducted after July and August market data was already known. Model weights were frozen prior to June 30, 2026, but contestant selection and simulation execution were performed retrospectively with full knowledge of the market environment during this period.</li>
          <li><strong>Purpose</strong>: This phase serves as a backtest baseline to establish initial contestant positions, cash drag, and execution fingerprints before forward tracking begins.</li>
          <li><strong>Prospective Forward Tracking &amp; Provenance</strong>: From the August 28 close onward, the evaluation transitions to prospective forward tracking (beginning with Episode 09). Evaluation results packages are sealed under SHA-256 cryptographic digests upon cycle completion for institutional anti-tampering embargo periods prior to public unlock (which proves zero modification during the embargo window, rather than serving as a pre-market prediction digest).</li>
        </ul>

        <!-- Section II -->
        <h3 style="color: var(--text-primary); font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.75rem;">
          II. Standings: High Selection Intensity Dominance
        </h3>
        <p>
          Across the 41-day baseline, the executable universe benchmark (<strong>Taotie</strong>) gained <strong>+2.32%</strong> (NAV <code>1.0232</code>) under finite-capital and round-lot constraints. Strategies with elevated selection intensity achieved substantial upside:
        </p>
        <div style="background: rgba(0, 0, 0, 0.35); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 14px 18px; font-family: monospace; font-size: 0.88rem; margin-bottom: 1.25rem; color: var(--text-primary);">
          [Top 5 Cumulative Standings as of August 28, 2026 (41 Trading Days)]<br>
          1. CONTESTANT_B_eagle-5-1  : NAV 1.1971 (+19.71%, +17.39pp vs executable Taotie benchmark)<br>
          2. CONTESTANT_A_eagle-11-2 : NAV 1.1468 (+14.68%, +12.36pp vs executable Taotie benchmark)<br>
          3. CONTESTANT_B_sloth-1    : NAV 1.1438 (+14.38%, +12.06pp vs executable Taotie benchmark)<br>
          4. CONTESTANT_A_rabbit-1   : NAV 1.1313 (+13.13%, +10.81pp vs executable Taotie benchmark)<br>
          5. CONTESTANT_D_rabbit-1   : NAV 1.1247 (+12.47%, +10.15pp vs executable Taotie benchmark)
        </div>
        <p>
          <strong>CONTESTANT_B_eagle-5-1</strong> led all 168 variants with a cumulative return of <strong>+19.71%</strong> (NAV <code>1.1971</code>), posting an annualized Sharpe ratio of <code>2.64</code> and a maximum drawdown of <code>-2.41%</code> during this backtest window.
        </p>

        <!-- Section III -->
        <h3 style="color: var(--text-primary); font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.75rem;">
          III. Execution Zoo Autopsy: Summer Tailwind Regimes
        </h3>
        <p>
          <strong>1. The Eagles (High Selection Intensity)</strong>: <code>eagle-5-1</code> concentrates capital into the top 5 predicted assets (Top 5 quantile, Drop 1), exerting the highest selection intensity in the tournament. In a persistent trending market, concentrating capital into top 5 positions amplifies both exposure to the model signal and idiosyncratic concentration risk (magnifying both genuine signal and concentrated luck).
        </p>
        <p>
          <strong>2. The Sloths (Signal Delay Stress-Testing)</strong>: <code>sloth-1</code> deliberately delays the incoming model prediction signal by one full rebalance cycle before executing, yet still delivered an NAV of <code>1.1438</code> (Rank 3 overall). This observation is consistent with relatively slow signal decay over this window; a one-cycle delayed ranking retained substantial economic value. Note that Sloth mechanics combine signal delay with portfolio-path inertia and cash drag (Sloth variants hold substantial uninvested cash during delay windows). A rigorous claim of an extended pure prediction half-life would require cross-sectional verification across the full Sloth-1/2/3/4 lag gradient.
        </p>
        <div style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid var(--brand-cyan); padding: 10px 14px; margin: 1rem 0; font-size: 0.9rem;">
          <strong>Tactical Takeaway:</strong> When market trends persist and signal decay is slow, elevating selection intensity (Eagle) and harvesting delayed alpha (Sloth) both captured significant upside during this period.
        </div>

        <!-- Section IV -->
        <h3 style="color: var(--text-primary); font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.75rem;">
          IV. The Null Court: Matched Monte Carlo &amp; Multiple Testing Sensitivity
        </h3>
        <p>
          To test whether this outperformance was distinguishable from random selection, <code>CONTESTANT_B_eagle-5-1</code> was tested against its <strong>matched null colony of 1,000 deterministic pseudo-random monkey portfolios</strong> (identical TopK=5, DropN=1 rules, lot constraints, and capital frictions, with zero ranking signal):
        </p>
        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem; background: rgba(56, 189, 248, 0.05); padding: 8px 12px; border-radius: 4px;">
          <em>Note on Monkey Architecture:</em> Arena simulates 11,000 total monkeys across 11 unique matched portfolio-rule specifications (1,000 monkeys each). Because pseudo-random ranking completely strips out model identity, contestants sharing identical portfolio mechanics share the same matched null colony.
        </div>
        <ul style="margin-left: 1.25rem; margin-bottom: 1.25rem;">
          <li>Across 1,000 matched random simulations, <strong>0 monkeys outperformed eagle-5-1</strong>.</li>
          <li>Under standard finite-sample plus-one correction:
            <code style="color: var(--brand-cyan);">p = (0 + 1) / (1000 + 1) &approx; 0.000999 &approx; 0.001</code>.
          </li>
          <li>The strategy ranks in the <strong>&gt;99.9% empirical percentile</strong> of its matched null colony.</li>
        </ul>

        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 12px 16px; margin-bottom: 1.5rem;">
          <h4 style="color: var(--accent-amber); margin: 0 0 6px 0; font-size: 0.95rem;">Multiple Testing Sensitivity &amp; Resolution Limits</h4>
          <p style="font-size: 0.88rem; margin: 0 0 8px 0; line-height: 1.6;">
            Because <code>eagle-5-1</code> was selected as the best among 168 living tournament variants, its raw <em>p</em>-value cannot be interpreted as an unselected discovery.
            Conducting a limited sensitivity analysis applying a distribution-free <strong>Bonferroni upper bound</strong> across the 168 explicitly enumerated execution paths:
            <br>
            <code style="font-size: 0.9rem; color: var(--accent-amber);">168 &times; 0.000999 &approx; 0.168 &gt; 0.05</code>
          </p>
          <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
            <strong>1. The Bonferroni-adjusted p-value exceeds 0.05.</strong><br>
            <strong>2. Monte Carlo Resolution Limitation:</strong> With <code>N = 1,000</code> matched monkeys, the minimum finite-sample p-value is <code>1 / 1001 &approx; 0.001</code>. Under a 168-way Bonferroni test, this simulation scale itself cannot mathematically reach a family-wise 0.05 significance threshold. This represents a known resolution limit of finite matched simulation rather than a requirement to arbitrarily inflate monkey counts.<br>
            <strong>3. Unadjusted Researcher Degrees of Freedom:</strong> Crucially, this 168-path calculation is only a narrow sensitivity check bounded to the actively tracked paths on the leaderboard. It does <em>not</em> account for broader retrospective researcher degrees of freedom—such as prior model candidate screening, Zoo animal taxonomy design, or parameter grid formulation.
          </div>
        </div>

        <!-- Section V -->
        <h3 style="color: var(--text-primary); font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.75rem;">
          V. Transition to Forward Tracking
        </h3>
        <p>
          As of Friday, August 28, 2026, the baseline standings are locked:
          <br>
          <em style="color: var(--text-primary);">"41 Trading Days: Cumulative +19.71% (+17.39pp vs Benchmark); 0 / 1,000 matched monkeys exceeded it (p &approx; 0.001)."</em>
        </p>
        <p>
          With Episodes 01–08 establishing the initial baseline, prospective forward tracking begins with Episode 09 (covering the forward trading window of August 31 to September 04, 2026).
        </p>

        <div style="margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle); text-align: center; font-size: 0.85rem; color: var(--text-tertiary);">
          🏛️ <em>QuantPits Arena Official Tournament Log</em>
        </div>

      </article>
    `;
  },

  renderEp09Embargoed() {
    return `
      <div style="text-align: center; padding: 3rem 1.5rem; max-width: 680px; margin: 0 auto;">
        
        <div style="width: 72px; height: 72px; border-radius: 50%; background: rgba(245, 158, 11, 0.1); border: 2px solid rgba(245, 158, 11, 0.4); display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 1.5rem auto;">
          🔒
        </div>

        <div class="hero-tag" style="margin-bottom: 0.75rem; background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); color: #fbbf24;">
          <span>Institutional Embargo Active · Evaluation Cycle Unlocking</span>
        </div>

        <h2 style="font-size: 1.8rem; color: var(--text-primary); margin-bottom: 0.75rem;">
          Episode 09: The September 02 Breadth Shock (Arena Designation: "Black Wednesday")
        </h2>

        <p style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.7; margin-bottom: 1.5rem;">
          The forward trading window from <strong>August 31 to September 04, 2026</strong> (anchored at the August 28 close) has concluded. The completed performance evaluation package was sealed under an SHA-256 cryptographic digest on Saturday, September 05, 2026 for institutional anti-tampering embargo until public reveal on September 11.
        </p>

        <!-- Public Market Climate Summary Box -->
        <div class="card" style="background: rgba(0,0,0,0.4); border: 1px solid var(--border-subtle); padding: 1.25rem; text-align: left; margin-bottom: 1.75rem; font-size: 0.88rem; line-height: 1.6;">
          <strong style="color: var(--accent-amber); display: block; margin-bottom: 6px;">
            🌪️ Public Market Climate Overview (Aug 31 – Sep 04, 2026):
          </strong>
          During this 5-day cycle, the broader market experienced what the Arena designates as its "Black Wednesday" intraday breadth shock on September 2. Turnover contracted, and growth-heavy and previously strong segments experienced sharp localized drawdowns.
          <br><br>
          <em>Individual model trajectories and animal handler performance remain cryptographically sealed under institutional embargo.</em>
        </div>

        <div style="background: rgba(56, 189, 248, 0.08); border: 1px dashed var(--brand-cyan); padding: 12px 18px; border-radius: 6px; font-size: 0.85rem; color: var(--brand-cyan); margin-bottom: 1.5rem;">
          ⏳ <strong>Official Public Decryption Date:</strong> Friday, September 11, 2026 at 18:00 UTC+8
        </div>

        <div style="margin-top: 2rem;">
          <button class="btn btn-secondary" onclick="window.DispatchesView.selectEpisode('ep08')">
            <span>&larr; Return to Episodes 01–08 Baseline Dispatch</span>
          </button>
        </div>

      </div>
    `;
  }
};
