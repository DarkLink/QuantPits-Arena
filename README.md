# QuantPits Arena | Empirical Strategy Testbed & Benchmark Zoo

> **An empirical research testbed, execution zoo, and parametric null benchmark for quantitative alpha models.**
> Reviving historical model artifacts at an identical prospective starting line under standardized finite-capital execution constraints.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Live Arena](https://img.shields.io/badge/Live%20Arena-arena.quantpits.com-success.svg)](https://arena.quantpits.com/)
[![Status: Research Testbed](https://img.shields.io/badge/Status-Research%20Testbed-purple.svg)](#disclaimer)

---

## 🧭 Repository Scope & System Architecture

QuantPits Arena is an **empirical evaluation framework, benchmark zoo, and interactive visualization testbed**.

### 1. Interactive Research Testbed
- **Live Platform**: Access the hosted arena directly at **[arena.quantpits.com](https://arena.quantpits.com/)**.
- **100% Offline Ready**: The web research platform (`web/`) is completely self-contained and pre-packaged with complete tournament simulation data:
  - Zero external package dependencies (native Python standard library server).
  - Complete coverage of **168 contestant-animal execution paths**, **11,000 parametric monkey null simulations**, **cross-model trajectory curves**, **counterfactual decision audits**, and **behavioral fingerprints**.

```bash
# Clone the repository
git clone https://github.com/QuantPits/QuantPits-Arena.git
cd QuantPits-Arena

# Launch local exploration server
python3 -m http.server 8080 --directory web

# Open in your browser
# http://localhost:8080
```

### 2. Operational Scope & Running Custom Tournaments
- **Visual Exploration vs. Raw Execution**:
  - **Offline Analytics (Out-of-the-Box)**: The web testbed comes with pre-compiled tournament datasets, allowing immediate visual exploration and cross-model comparison without any training or inference setup.
  - **Running Custom Evaluations**: If you wish to run the evaluation pipeline from scratch or benchmark your own custom models through the Zoo:
    1. **User-Provided Models**: Model weights are not bundled in this repository. Users must supply their own local model artifacts or checkpoints (conforming to the configuration manifests in `manifests/public/`).
    2. **User-Provided Market Data**: Historical market quote feeds and feature matrices for your target stock universe and evaluation dates must be provided locally.
    3. **Included Components**: This repository supplies the 28 animal execution policies, finite-capital transaction and portfolio accounting engine, parametric monkey null generators, and report export tooling.
- **Not a Live Trading Engine**: The repository is an empirical evaluation testbed; it does not provide real-time order routing, brokerage gateway connectivity, or continuous live execution infrastructure.
- **Declarative Manifests**: Strategy models are specified as reproducible configuration manifests (`manifests/public/`) documenting architectural parameters, feature groupings, and standardized inference adapters.

---

## 🏛️ Core Research Axioms

QuantPits Arena is built on six foundational methodological principles:

1. **Historical Biography ≠ Arena Record**: Past in-sample backtests, former production roles, and historical accolades exist only as biography. They contribute **zero weight** to Arena standings. Every model enters the common Arena at the same anchor date (2026-07-03) with a normalized base NAV of 1.0000 and CNY 500,000 initial capital.
2. **High-Resolution Parametric Monkey Null Benchmark**: Absolute return alone says very little about signal quality. For each of the 11 portfolio execution policies, an independent colony of **1,000 deterministic pseudo-random monkey portfolios** (11,000 total) is evaluated under identical capital and lot constraints.
3. **Statistical Interpretation Nuance**: A nominal $p_{\text{upper}} < 0.05$ indicates the result is difficult to reproduce with the random-ranking null. **The Arena deliberately does NOT translate this into "Alpha confirmed."**
4. **The 28-Animal Execution Zoo**: The same underlying model signal is deployed through 28 distinct portfolio behaviors to isolate signal decay, holding inertia, turnover friction, capacity scalability, and directional polarity.
5. **Real Trading & Finite-Capital Constraints**: Fixed initial capital (CNY 500,000), 100-share trading-lot roundings, unaffordable order skipping (preserving real cash drag), and standard transaction costs.
6. **External Simplicity Reference (The Rock)**: The Permanent Portfolio is displayed alongside the arena as a simplicity benchmark: *"Four buckets. No ranking. No ensemble. No retraining. No comment. Complexity is not free."*

---

## 🦁 The 28-Animal Zoo Taxonomy

| Family | Animals | Specification | Research Hypothesis Tested |
| :--- | :--- | :--- | :--- |
| **Baseline Control** | 🤖 **Robot** | TopK=22, DropN=3, Weekly | Canonical production baseline policy. |
| **Cash Lag** | 🦥 **Sloth 1–4** | 1, 2, 3, 4 Weeks Delay | Delays execution while holding cash; measures signal timing decay. |
| **Holding Inertia** | 🐌 **Snail 1–4** | 1, 2, 3, 4 Weeks Lag | Delays rebalances while holding stale positions; measures inertia friction. |
| **Turnover Extremes** | 🐢 **Turtle**<br>🐇 **Rabbit 1–2** | DropN=1 (Low)<br>DropN=11 / 22 (High) | Tests whether aggressive deployment extracts alpha or ingests noise. |
| **Polarity Inversion** | 🐨 **Koala** | Bottom-22 Worst Stocks | Directional sanity check: inverted ranking should underperform baseline. |
| **Rank Geometry** | 🦡 **Meerkat 10%–90%** | 9 Decile Slices (P10–P90) | Tests cross-sectional monotonicity and signal depth across deciles. |
| **Concentration** | 🦅 **Eagle Suite** | 5/1, 11/2, 44/6, 66/9, 88/12 | Evaluates concentration risk vs. diversification capacity. |
| **Market Breadth** | 🐋 **Whale Shark**<br>🐉 **Taotie** | 50% Universe (123 stocks)<br>100% Full Universe (246) | Tests survival of signal under broad diversification up to the passive limit. |

### External Reference Standards
- **Parametric Monkey Null ($N = 1,000$ per spec, 11,000 total)**: Strict random-ranking null reference distributions.
- **CSI 300 Index (SH000300)**: Broad mainland China equity market benchmark.
- **Taotie Baseline**: Equal-weight, capital-constrained passive reference tracking the full eligible universe.
- **The Rock (Permanent Portfolio)**: External 4-bucket simplicity anchor (Equity, Gold, Bonds, Cash).

---

## 🖥️ Interactive Web Application Architecture

The frontend application (`web/`) is an institutional, dependency-free single-page research dashboard:

```
web/
├── index.html                  # Single-page application shell
├── css/
│   ├── variables.css           # Institutional color palettes & design tokens
│   ├── main.css                # Typography & layout fundamentals
│   ├── components.css          # Tables, cards, compact filter bars, buttons
│   └── views.css               # Specific view layouts
└── js/
    ├── data/
    │   └── arena_data.js       # Pre-compiled offline tournament payload (168 paths, 11k monkeys)
    ├── adapter.js              # In-memory query engine & statistical aggregator
    ├── components/
    │   ├── charts.js           # Apache ECharts wrapper (trajectories, heatmaps, regret curves)
    │   └── filters.js          # Single-row compact filter toolbar
    ├── views/
    │   ├── landing.js          # Platform Exhibition & tournament introduction (/#intro)
    │   ├── overview.js         # KPI metrics, scatter distributions & standings (/#overview)
    │   ├── leaderboard_view.js # Sortable leaderboard & Model × Animal heatmap matrix (/#leaderboard)
    │   ├── animals_view.js     # 28 Animal containers, dual-scope telemetry & curves (/#animals)
    │   ├── contestant_detail.js# Model biography, burial annualized returns & fingerprints (/#contestants)
    │   ├── decision_audit.js   # Counterfactual decision archaeology & regret analysis (/#decision-audit)
    │   ├── methodology.js      # Statistical axioms & experimental standards (/#methodology)
    │   └── disclaimer.js       # Full 8-section legal and research disclosures (/#disclaimer)
    └── app.js                  # Client-side hash router & lifecycle controller
```

---

## 🔧 Repository Verification

To audit repository integrity and data formatting consistency:

```bash
python3 scripts/audit_privacy.py
```

---

## 🛡️ Disclaimer

> **For research, educational, and informational purposes only.**  
> Nothing contained herein constitutes investment advice, a recommendation, endorsement, or solicitation to buy or sell any security or financial product.  
> Results may include live, delayed, simulated, backtested, counterfactual, or shadow-trading performance and are not indicative of future performance. Data are published with an approximately one-week delay. Investing involves risk, including the possible loss of principal.  
> 
> *“QuantPits Arena is a research testbed. It studies models, portfolio policies, historical decisions, failures, and occasionally monkeys. **It does not tell you what to buy.**”*  
>
> For full disclosures, visit the [Research & Legal Disclaimer](https://arena.quantpits.com/#disclaimer).

---

## 📜 License

MIT License. Copyright (c) QuantPits Research.
