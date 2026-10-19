window.MethodologyView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const adapter = window.arenaAdapter;
    const meta = adapter.getCurrentSeasonMeta();
    const n = meta.monkeys_per_random_spec || 100000;
    const participation = adapter.getGlobalKPIs();
    const animals = adapter.getAllAnimals();
    const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
    const groups = [
      {icon:'🤖', name:'Robot', category:'Baseline', match:a => a.id === 'robot',
        description:'The reference policy: target 22 holdings and replace up to 3 positions at a scheduled rebalance. It provides a common starting point for studying execution behavior.'},
      {icon:'🦥', name:'Sloth', category:'Signal delay · cash start', match:a => a.id.startsWith('sloth-'),
        description:'Waits in cash for 1–4 weeks before its first entry, then rebalances using rankings delayed by that many weekly cycles. Tests signal latency together with the initial cash-exposure gap.'},
      {icon:'🐌', name:'Snail', category:'Signal delay · invested start', match:a => a.id.startsWith('snail-'),
        description:'Enters immediately using the initial ranking, reuses that ranking during the transition, then follows rankings delayed by 1–4 weekly cycles. Studies signal latency without Sloth’s initial cash-only period.'},
      {icon:'🐢 🐇', name:'Turtle & Rabbit', category:'Turnover stress', match:a => a.id === 'turtle' || a.id.startsWith('rabbit-'),
        description:'Targets 22 holdings with replacement budgets of 1, 11 or 22 positions per rebalance. Compares slower rotation with half-portfolio and full-portfolio replacement under the same trading costs.'},
      {icon:'🐨', name:'Koala', category:'Ranking inversion', match:a => a.id === 'koala',
        description:'Selects from the bottom of the ranking. This directional sanity check asks whether reversing the signal changes its behavior; it does not establish why a ranking succeeds or fails.'},
      {icon:'🦡', name:'Meerkat', category:'Ranking slices', match:a => a.id.startsWith('meerkat-'),
        description:'Targets 22 holdings around ranking percentiles from 10% through 90%. Compares different parts of the ranking to explore whether performance changes consistently across score regions.'},
      {icon:'🦅', name:'Eagle', category:'Concentration spectrum', match:a => a.id.startsWith('eagle-'),
        description:'Targets 5, 11, 44, 66 or 88 holdings with corresponding replacement budgets. Studies concentration and breadth; the highest return need not carry the strongest statistical evidence.'},
      {icon:'🐋', name:'Whale Shark', category:'Broad portfolio', match:a => a.id === 'whale-shark',
        description:'Targets 123 holdings with a replacement budget of 17 in every pool. That is half of the 246-stock subset, but a smaller share of expanded pools. Actual holdings remain subject to execution constraints.'}
    ];
    el.innerHTML = `<div class="doc-page-container methodology-page">
      <header class="view-header methodology-hero">
        <span class="badge badge-primary">${escape(meta.short_title || meta.season_title)} · Research field guide</span>
        <h1 class="view-title">Methodology &amp; Statistical Interpretation</h1>
        <p class="view-subtitle">One signal, many animal policies. Understand what each experiment tests, which benchmark answers the question, and how to read the evidence.</p>
        <div class="methodology-summary">
          <div><strong>${participation.totalPaths}</strong><span>Participant paths in this pool</span></div>
          <div><strong>${animals.length}</strong><span>Animal execution policies</span></div>
          <div><strong>${n.toLocaleString()}</strong><span>Random paths per specification</span></div>
          <div><strong>840</strong><span>Original five-pool test family</span></div>
        </div>
      </header>

      <div class="methodology-sections">
        <section class="card methodology-section methodology-section--amber">
          <div class="methodology-section-heading"><span aria-hidden="true">⚖️</span><h2>Participation and test coverage</h2></div>
          <p>This pool contains ${participation.totalPaths} participant paths across ${participation.contestantCount} contestants: ${participation.fullSeasonPaths} full-season paths and ${participation.observationPaths} observation paths. The ${participation.referencePaths} benchmark reference paths are counted separately.</p>
          <div class="methodology-grid">
            <div class="methodology-panel"><h3>Each participant keeps its own history</h3><p>Original contestants retain the full season. A later entrant starts at its own entry date with NAV 1.0000. Retrained participants have their own records; their parents' earlier performance is not inherited.</p></div>
            <div class="methodology-panel"><h3>Compare over a shared period</h3><p>For a parent and its retrained branch, use the same animal and the common observation window. <a href="#decision-audit">Compare Participants →</a> aligns available dates and rebases both paths to NAV 1.0000.</p></div>
          </div>
          <p class="methodology-callout">The original full-season test family remains unchanged when a new observation participant joins. Observation paths receive no inherited random-control p value. Historical reputation contributes no weight to Arena rankings.</p>
        </section>

        <section class="card methodology-section methodology-section--cyan">
          <div class="methodology-section-heading"><span aria-hidden="true">🦁</span><h2>The ${animals.length}-Animal Execution Zoo</h2><a href="#animals" class="btn btn-sm btn-outline">Explore the Zoo →</a></div>
          <p>A contestant produces a ranking. The animals apply different portfolio policies to the same signal, testing entry timing, holding inertia, turnover, inversion, ranking geometry and concentration. TopK is the target holding count; DropN is the scheduled replacement budget, not a guarantee of completed trades.</p>
          <div class="methodology-grid methodology-animal-grid">
            ${groups.map(group => `<article class="methodology-panel methodology-animal-card">
              <div class="methodology-animal-heading"><span class="methodology-animal-icon" aria-hidden="true">${group.icon}</span><div><span class="methodology-eyebrow">${group.category}</span><h3>${group.name}</h3></div></div>
              <p>${group.description}</p>
              <div class="methodology-animal-links">${animals.filter(group.match).map(animal => `<a class="methodology-animal-link" href="#animals/${escape(animal.id)}" title="${escape(animal.name)} · TopK ${animal.topk} / DropN ${animal.n_drop}">${escape(animal.name.split(' (')[0])}<span>${animal.topk}/${animal.n_drop}</span></a>`).join('')}</div>
            </article>`).join('')}
          </div>
          <p class="methodology-note">Taotie and Ghost Taotie are portfolio benchmarks, separate from these ${animals.length} animal policies. Random controls are grouped by TopK/DropN; they do not imitate every animal behavior.</p>
        </section>

        <section class="card methodology-section methodology-section--purple">
          <div class="methodology-section-heading"><span aria-hidden="true">🧭</span><h2>Different benchmarks, different questions</h2></div>
          <div class="methodology-grid">
            <div class="methodology-panel"><span class="methodology-eyebrow">Market context</span><h3>${escape(adapter.getMarketBenchmarkName())}</h3><p>How did the external market perform over the same dates? Beating the index describes market-relative performance; it does not by itself isolate ranking skill.</p></div>
            <div class="methodology-panel"><span class="methodology-eyebrow">Executable universe</span><h3>🐉 Taotie</h3><p>A full-universe portfolio under the standard account's capital, allocation policy, costs and round lots. Realized weights reflect affordability, residual cash and trading frictions.</p></div>
            ${adapter.hasGhostTaotie() ? `<div class="methodology-panel"><span class="methodology-eyebrow">Capital-granularity scenario</span><h3>👻 Ghost Taotie</h3><p>A separate capital-granularity scenario that retains costs and round lots. It does not reset every holding to equal weight each week and is not an unconstrained equal-weight index.</p></div>` : ''}
            <div class="methodology-panel"><span class="methodology-eyebrow">Random-ranking null</span><h3>🐒 Matched monkeys</h3><p>How unusual is the result relative to random ranking under the matched TopK/DropN specification? This is the reference for the published random-control p values.</p></div>
          </div>
        </section>

        <section class="card methodology-section methodology-section--green">
          <div class="methodology-section-heading"><span aria-hidden="true">⏱️</span><h2>Decision and execution</h2></div>
          <div class="methodology-grid methodology-timeline">
            <div class="methodology-panel"><span class="methodology-eyebrow">01 · Decision close</span><h3>Freeze the intent</h3><p>Each animal freezes its ranking and policy at the decision close.</p></div>
            <div class="methodology-panel"><span class="methodology-eyebrow">02 · Trading Monday</span><h3>Evaluate the orders</h3><p>Opening prices, direction status, affordability and execution are evaluated on the trading Monday. A closed Monday skips the rebalance.</p></div>
            <div class="methodology-panel"><span class="methodology-eyebrow">03 · Daily valuation</span><h3>Carry the portfolio forward</h3><p>Missing or invalid execution quotes cannot liquidate a position. Daily marks may use the last valid close and are counted as stale.</p></div>
          </div>
          <p>Standard accounts and Taotie share the same capital and allocation policy, costs and round lots. Holiday reopening does not imply a makeup rebalance. Turnover is gross buys plus gross sells divided by starting assets.</p>
        </section>

        <section class="card methodology-section methodology-section--purple">
          <div class="methodology-section-heading"><span aria-hidden="true">🐒</span><h2>Random controls</h2></div>
          <p>Ten random TopK/DropN specifications each contain ${n.toLocaleString()} paths per pool. P_ALL_0 is one deterministic passive reference, with no random-control p value. Delay, cold/warm starts, inversion and percentile selection remain properties of the animal; they do not create extra monkey species. The same random-score prefix is shared across specifications, so these controls are not independent across groups.</p>
          <div class="methodology-formula"><span class="methodology-eyebrow">Empirical upper-tail probability</span><code>p = (k + 1) / (N + 1)</code><p>k counts random returns greater than or equal to the contestant return. Each path uses its matched specification; controls are not pooled across specifications to increase N.</p></div>
          <p>At N = ${n.toLocaleString()}, the minimum p is ${(1/(n+1)).toExponential(5)}. A zero exceedance count is not p = 0. Finite percentile = 100 × count(null &lt; actual)/(N+1); decisions use full-precision p.</p>
        </section>

        <section class="card methodology-section methodology-section--amber">
          <div class="methodology-section-heading"><span aria-hidden="true">🔬</span><h2>Declared comparison family</h2></div>
          <div class="methodology-formula"><span class="methodology-eyebrow">Original cumulative cutoff family</span><code>5 pools × 6 contestants × 28 animals = 840 comparisons</code></div>
          <p>Bonferroni uses adjusted p = min(840p, 1), with strict significance at adjusted p &lt; 0.05. The raw threshold is ${(0.05/840).toExponential(5)}. Holm, BH and BY are also reported; BH/BY target false discovery rate. The visible family does not account for hidden earlier research selection.</p>
          <p>At N = 100,000, Bonferroni can pass with at most 4 exceedances. Monte Carlo intervals describe uncertainty in the simulated tail, not uncertainty from additional market history. Monthly and repeated weekly reviews remain descriptive monitoring; they are not additional predeclared confirmatory tests.</p>
          <p class="methodology-callout">An unusual result under a specified random-ranking null does not establish persistent future alpha, causal superiority or freedom from earlier research selection.</p>
        </section>

        <section class="card methodology-section methodology-section--cyan">
          <div class="methodology-section-heading"><span aria-hidden="true">📈</span><h2>Charts and return interpretation</h2></div>
          <p>All curves start at NAV 1.0000. Period returns divide ending NAV by the prior reporting anchor. Differences between percentage returns are percentage points. The same monkeys retain cash and positions across weeks and are valued every trading day; only scheduled rebalances draw new random rankings.</p>
          <p>Monkey curves show observed daily P05, median and P95, including days without a rebalance. These are pointwise null distribution ranges, not confidence bands for future returns. Daily cutoff reviews are descriptive monitoring; the correction does not jointly cover every inspected date.</p>
        </section>

        <section class="card methodology-section methodology-section--amber">
          <div class="methodology-section-heading"><span aria-hidden="true">📋</span><h2>Evaluation provenance &amp; research limits</h2></div>
          <div class="methodology-grid">
            <div class="methodology-panel"><h3>Evaluation provenance</h3><p>Published curves are a retrospective repair replay through ${escape(meta.cutoff || '2026-10-09')}, using the actual raw weekly signals preserved in legacy checkpoints. Current daily-bar market snapshots are frozen separately. Historical dispatches do not establish a pre-market commitment.</p></div>
            <div class="methodology-panel"><h3>Daily-bar research limits</h3><p>This release uses a retrospective full-day volume proxy for tradability. Verified corporate-action coverage, opening direction limits and executable capacity are incomplete. Factors alone are not treated as cash-dividend records. The strict execution profile fails its data preflight when required coverage is absent.</p></div>
          </div>
        </section>
      </div>
    </div>`;
  }
};
