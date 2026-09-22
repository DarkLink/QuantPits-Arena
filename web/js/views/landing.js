/**
 * web/js/views/landing.js
 * =======================
 * Landing View Component (Season 1: Summer 2026 Tournament)
 */

window.LandingView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
    const hasGhost = window.arenaAdapter ? window.arenaAdapter.hasGhostTaotie() : false;

    el.innerHTML = `
      <section class="landing-hero">
        <div class="hero-tag">
          <span>🏛️ QuantPits Arena · ${seasonMeta.title || "Season 1: Summer 2026"}</span>
        </div>
        <h1 class="hero-title">Where Quantitative Strategies Face the Execution Zoo</h1>
        <p class="hero-description">
          An empirical laboratory for stress-testing quantitative alpha models. We revive historical model candidates at an identical prospective starting line, subject them to 28 distinct execution handlers, and rigorously benchmark their performance against 11,000 parametric random monkeys.
        </p>
        <div class="hero-actions">
          <button class="btn btn-primary" onclick="window.appRouter.navigate('overview')">
            <span>🚀 Enter Arena Overview</span>
          </button>
          <button class="btn btn-secondary" onclick="window.appRouter.navigate('leaderboard')">
            <span>🏆 Full Leaderboard</span>
          </button>
          <button class="btn btn-secondary" onclick="window.appRouter.navigate('contestants')">
            <span>🧬 Explore Models</span>
          </button>
          <button class="btn btn-secondary" onclick="window.appRouter.navigate('decision-audit')">
            <span>⚖️ Decision Archaeology</span>
          </button>
          <button class="btn btn-secondary" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.toggle();">
            <span>📖 Field Guide Specs</span>
          </button>
        </div>
      </section>

      <!-- QuantPits Ecosystem Bridge Banner -->
      <div class="ecosystem-bridge-banner">
        <div class="bridge-content">
          <div class="bridge-badge">
            <span>🌐</span> QuantPits Ecosystem Integration
          </div>
          <p class="bridge-text">
            Arena is the empirical tournament &amp; benchmark laboratory of the <strong>QuantPits</strong> production quantitative trading engine.
          </p>
        </div>
        <a href="https://quantpits.com/" target="_blank" rel="noopener" class="bridge-link-btn">
          <span>Visit QuantPits Main Platform</span>
          <span class="bridge-arrow">&rarr;</span>
        </a>
      </div>

      <!-- Key Methodology Card: Historical Context vs Arena Record -->
      <div class="disclaimer-banner" style="border-left: 4px solid var(--accent-cyan); background: rgba(56, 189, 248, 0.05);">
        <div class="disclaimer-icon">⚖️</div>
        <div>
          <h4 style="color:var(--accent-cyan); margin-bottom:4px;">Core Scientific Boundary: Historical Biography ≠ Arena Record</h4>
          <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.6; margin:0;">
            Every strategy model in this tournament carries historical context (e.g. why it was accepted or superseded in production, historical training metrics). <b>In the Arena, all models start strictly from zero (NAV = 1.0000) on ${seasonMeta.anchor_date || "2026-07-03"} under ${seasonMeta.methodology?.capital_spec || "identical capital constraints"}</b>. Historical biography provides qualitative context, not arena advantage.
          </p>
        </div>
      </div>

      <!-- 4 Pillars Concept Grid -->
      <div class="concept-grid">
        <div class="concept-card">
          <div class="concept-icon">🏺</div>
          <h3>The Models</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            Production ensemble snapshots and neural architectures. Each model artifact represents a milestone in the quantitative evolutionary lineage.
          </p>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
            <a href="#contestants" style="font-size:0.84rem; font-weight:600; color:var(--accent-cyan);">Explore Profiles →</a>
            <button class="chart-spec-pill" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.openCategory('contestants');">Specs</button>
          </div>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🐾</div>
          <h3>The Animal Zoo</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            28 execution handlers stress-testing each model across multiple real-world axes: signal lag (<span data-tooltip-term="sloth-22-3">Sloth</span>/<span data-tooltip-term="snail-22-3">Snail</span>), turnover (<span data-tooltip-term="rabbit-22-3">Rabbit</span>/<span data-tooltip-term="turtle-22-3">Turtle</span>), breadth (<span data-tooltip-term="eagle-6">Eagle</span>/<span data-tooltip-term="whale_shark">WhaleShark</span>), and polarity (<span data-tooltip-term="koala">Koala</span>).
          </p>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
            <a href="#animals" style="font-size:0.84rem; font-weight:600; color:var(--accent-cyan);">Inspect Zoo Handlers →</a>
            <button class="chart-spec-pill" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.openCategory('animals');">Specs</button>
          </div>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🐒</div>
          <h3>Parametric Monkeys</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            A high-resolution null model suite: 11 distinct portfolio execution policies, each benchmarked by 1,000 deterministic pseudo-random monkeys (11,000 monkeys total) under identical 100-share trading lot constraints.
          </p>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
            <a href="#methodology" style="font-size:0.84rem; font-weight:600; color:var(--accent-cyan);">Read Null Methodology →</a>
            <button class="chart-spec-pill" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.openTerm('metric_monkey_percentile');">Specs</button>
          </div>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🏛️</div>
          <h3>${(() => {
            const mBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "Market Benchmark";
            return hasGhost ? `Taotie, Ghost &amp; ${mBmName}` : `Taotie &amp; ${mBmName}`;
          })()}</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            ${(() => {
              const mBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "Market Benchmark";
              return hasGhost ? `Triple reference standards: <span data-tooltip-term="taotie">Executable Taotie</span> (CNY 500k), <span data-tooltip-term="ghost_taotie">Theoretical Ghost Taotie</span> (CNY 100M unconstrained), and <span data-tooltip-term="market_benchmark">${mBmName}</span> (external broad market anchor).` : `Dual reference standards: <span data-tooltip-term="taotie">Taotie</span> (executable universe benchmark under capital &amp; lot frictions) and <span data-tooltip-term="market_benchmark">${mBmName}</span> (external broad market anchor).`;
            })()}
          </p>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
            <a href="#overview" style="font-size:0.84rem; font-weight:600; color:var(--accent-cyan);">Compare Benchmarks &rarr;</a>
            <button class="chart-spec-pill" onclick="if(window.ArenaSpecDrawer) window.ArenaSpecDrawer.openCategory('benchmarks');">Specs</button>
          </div>
        </div>
      </div>

      <!-- Institutional Research & Legal Disclaimer -->
      <div class="card" style="margin-top: 36px; border-left: 4px solid var(--accent-amber); background: rgba(245, 158, 11, 0.03); padding: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
          <h2 style="font-size: 17px; font-weight: 700; color: var(--accent-amber); margin: 0; display: flex; align-items: center; gap: 8px;">
            <span>🛡️</span> Disclaimer
          </h2>
          <a href="#disclaimer" class="btn btn-sm btn-outline" style="font-size: 11px; padding: 4px 10px; text-decoration: none;">
            Full Legal Notice &rarr;
          </a>
        </div>
        <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.75; display: flex; flex-direction: column; gap: 12px;">
          <p style="margin: 0; color: var(--text-primary); font-weight: 500;">
            This website is provided solely for research, educational, and informational purposes. It does not constitute investment advice, a recommendation, solicitation, or offer to buy or sell any security or financial product.
          </p>
          <p style="margin: 0;">
            Results shown may include live, delayed, simulated, backtested, counterfactual, or shadow-trading performance and should be interpreted only within the methodology stated for each experiment. Historical and simulated results are not indicative of future performance.
          </p>
          <p style="margin: 0;">
            Market and portfolio data are published with a delay of approximately one week and are not intended for real-time trading or investment decision-making.
          </p>
          <p style="margin: 0;">
            All models, strategies, benchmarks, and experimental variants are presented as research subjects. Their inclusion, ranking, or historical performance does not imply endorsement, expected profitability, or statistical validity beyond the stated experiment.
          </p>
          <p style="margin: 0; font-weight: 600; color: var(--text-primary);">
            Investing involves risk, including the possible loss of principal.
          </p>
          <div style="margin-top: 6px; padding-top: 12px; border-top: 1px dashed var(--border-subtle); font-style: italic; color: var(--text-muted); font-size: 12px;">
            “QuantPits Arena is a research testbed. It studies models, portfolio policies, historical decisions, failures, and occasionally monkeys. <b style="color: var(--accent-rose);">It does not tell you what to buy.</b>”
          </div>
        </div>
      </div>

      <!-- Community Discussion & Peer Review Invitation Card -->
      <div class="card" style="margin-top: 24px; border-left: 4px solid var(--brand-purple); background: rgba(167, 139, 250, 0.04); padding: 22px 26px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
          <div style="max-width: 720px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span style="font-size: 1.25rem;">💬</span>
              <h3 style="margin: 0; font-size: 1.1rem; color: var(--brand-purple); font-weight: 700;">
                Community Discussion &amp; Peer Review
              </h3>
            </div>
            <p style="margin: 0; font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6;">
              Have questions regarding model decay, methodology nuances, or want to suggest new animal execution handlers? Join the open peer review powered by GitHub Discussions (Thread #2).
            </p>
          </div>
          <button class="btn btn-secondary" style="border-color: rgba(167, 139, 250, 0.4); color: var(--brand-purple);" onclick="window.appRouter.navigate('discussion')">
            <span>Open Discussion &rarr;</span>
          </button>
        </div>
      </div>
    `;
  }
};
