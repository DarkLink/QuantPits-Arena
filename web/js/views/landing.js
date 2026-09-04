/**
 * web/js/views/landing.js
 * =======================
 * Landing View Component (Season 1: Summer 2026 Tournament)
 */

window.LandingView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    el.innerHTML = `
      <section class="landing-hero">
        <div class="hero-tag">
          <span>🏛️ QuantPits Arena · Season 1 (Summer 2026)</span>
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
        </div>
      </section>

      <!-- Key Methodology Card: Historical Context vs Arena Record -->
      <div class="disclaimer-banner" style="border-left: 4px solid var(--accent-cyan); background: rgba(56, 189, 248, 0.05);">
        <div class="disclaimer-icon">⚖️</div>
        <div>
          <h4 style="color:var(--accent-cyan); margin-bottom:4px;">Core Scientific Boundary: Historical Biography ≠ Arena Record</h4>
          <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.6; margin:0;">
            Every strategy model in this tournament carries historical context (e.g. why it was accepted or superseded in production, historical training metrics). <b>In the Arena, all models start strictly from zero (NAV = 1.0000) on 2026-07-03 under identical capital constraints</b>. Historical biography provides qualitative context, not arena advantage.
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
          <a href="#contestants" style="font-size:0.84rem; font-weight:600; margin-top:auto; color:var(--accent-cyan);">Explore Profiles →</a>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🐾</div>
          <h3>The Animal Zoo</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            28 execution handlers stress-testing each model across multiple real-world axes: signal lag (Sloth/Snail), high/low turnover (Rabbit/Turtle), portfolio breadth (Eagle/WhaleShark), and polarity sanity (Koala).
          </p>
          <a href="#leaderboard" style="font-size:0.84rem; font-weight:600; margin-top:auto; color:var(--accent-cyan);">Inspect Zoo Handlers →</a>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🐒</div>
          <h3>Parametric Monkeys</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            A high-resolution null model suite: 11 distinct portfolio execution policies, each benchmarked by 1,000 deterministic pseudo-random monkeys (11,000 monkeys total) under identical 100-share trading lot constraints.
          </p>
          <a href="#methodology" style="font-size:0.84rem; font-weight:600; margin-top:auto; color:var(--accent-cyan);">Read Null Methodology →</a>
        </div>

        <div class="concept-card">
          <div class="concept-icon">🏛️</div>
          <h3>Taotie & CSI 300</h3>
          <p style="font-size:0.88rem; color:var(--text-secondary);">
            Two primary reference benchmarks: Taotie (a capital-constrained, full-universe passive executable portfolio) and CSI 300 (SH000300 A-share broad market index).
          </p>
          <a href="#overview" style="font-size:0.84rem; font-weight:600; margin-top:auto; color:var(--accent-cyan);">Compare Benchmarks →</a>
        </div>
      </div>
    `;
  }
};
