# QuantPits Graveyard Arena (Zoo)

> **A reproducible, historical alpha benchmark and execution arena.**
> Recovering frozen model artifacts in a unified prospective timeline under standardized execution and portfolio policies.

---

## Overview

**QuantPits Graveyard Arena** is an independent benchmark and research framework designed to evaluate machine learning alpha models across time. Rather than retraining or fine-tuning, the Arena revives historical, frozen model artifacts and evaluates them through standardized **execution animals (handlers)** in an out-of-sample weekly cycle.

### Core Objectives

1. **Signal Decay Profiling**: Measure how rapidly alpha degrades under execution delays (Sloth handlers).
2. **Turnover & Capacity Sensitivity**: Compare high-bandwidth vs. low-turnover policies (Rabbit vs. Turtle handlers).
3. **Hypothesis Testing vs. Random Controls**: Rigorously contrast every model path against a 1,000-member **Monkey Colony** null distribution.
4. **Historical Decision Auditing**: Statistically evaluate historical model retirement/promotion decisions (e.g. Static vs. Cross-Validated variants).

---

## Architectural Principles

```
  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
  │   Contestant    │       │     Animal      │       │    Portfolio    │
  │    (Signal)     │ ────▶ │    (Policy)     │ ────▶ │    (Engine)     │
  └─────────────────┘       └─────────────────┘       └─────────────────┘
     Raw Prediction            Transformed              NAV & Trades
        Score                     Score
```

- **Contestant**: Pure prediction layer. Generates cross-sectional stock rankings for each time step. Does not control execution or turnover.
- **Animal**: Execution handler. Transforms signal timing, bandwidth, or direction according to deterministic, pre-registered rules.
- **Portfolio Engine**: Canonical portfolio construction and transaction accounting with explicit trading cost models.

---

## The Zoo (Animal Taxonomy)

| Animal | Family | Policy Specification | Research Purpose |
|---|---|---|---|
| **Robot** | Benchmark | Canonical Top-22, Drop-3, weekly rebalance | Standard execution benchmark |
| **Sloth-1** | Latency | 1-week signal delay | Measure 1-week signal latency decay |
| **Sloth-2** | Latency | 2-week signal delay | Measure 2-week signal latency decay |
| **Sloth-3** | Latency | 3-week signal delay | Measure 3-week signal latency decay |
| **Sloth-4** | Latency | 4-week signal delay | Measure 4-week signal latency decay |
| **Snail-1** | Latency-Warm | Day 1 match Robot, then 1-week signal delay | Decouple latency decay from cold-start exposure truncation |
| **Snail-2** | Latency-Warm | Day 1 match Robot, then 2-week signal delay | Decouple latency decay from cold-start exposure truncation |
| **Snail-3** | Latency-Warm | Day 1 match Robot, then 3-week signal delay | Decouple latency decay from cold-start exposure truncation |
| **Snail-4** | Latency-Warm | Day 1 match Robot, then 4-week signal delay | Decouple latency decay from cold-start exposure truncation |
| **Rabbit-1** | Bandwidth | Half-turnover: Drop-11 (50% of Top-22) | Test aggressive opinion deployment |
| **Rabbit-2** | Bandwidth | Full-turnover: Drop-22 (complete replacement) | Measure maximum turnover performance |
| **Turtle** | Low Turnover | Drop-1 minimal turnover | Test extreme turnover minimization |
| **Koala** | Inversion | Cross-sectional rank reversal (`1.0 - rank_norm`) | Anti-alpha & signal symmetry check (100% percentile) |
| **Meerkat-10% ~ 90%** | Percentile | 9 percentile slices ($P \in [10\%, 90\%]$), Top-22, Drop-3 | Test cross-sectional signal linearity & alpha depth |
| **Eagle-5/1 ~ 88/12** | Capacity | (5/1, 11/2, 44/6, 66/9, 88/12) TopK/DropN matrix | Stress-test portfolio capacity, concentration & cost boundary |
| **WhaleShark-50%** | Broad-Market | TopK=50% of Universe (123), DropN~13.8% (17) | Broad-market half-pool capacity benchmark |
| **Taotie-All** | All-Market | TopK=100% of Universe, DropN=0 (Pure Passive) | Full-market index tracking with passive exit/entry rebalancing |

### Controls

- **Monkey Colony ($N=1000$)**: Matched null distribution sharing the identical canonical portfolio policy, testing whether alpha outperforms random stock selection.
- **Rock (Permanent Portfolio)**: Multi-asset benchmark providing market baseline context.

---

## Weekly Synchronous Cycle Runner

Execution is anchored to real market calendar dates rather than bulk historical simulation:

```
  anchor_date (Fri) ──▶ PREDICT(data ≤ anchor) ──▶ ORDER(first_trade_date)
                              │
  first_trade (Mon) ──▶ EXECUTE_FULL_POSITION (TopK Full Entry)
                              │
  settle_day (Fri)  ──▶ SETTLE(NAV & Return) ──▶ PREDICT(data ≤ settle_day) ──▶ ORDER(next_monday)
                              │
  rebalance (Mon)   ──▶ REBALANCE(per Animal DropN) ──▶ [LOOP]
```

1. **Information Cutoff**: Predictions are generated after Friday market close using strictly past data ($t \le \text{Friday}$).
2. **First Week Full Entry**: On Week 1 ($T+1$ Monday), all models enter full positions up to TopK.
3. **Subsequent Rebalances**: On subsequent Mondays, portfolios adjust positions based on respective Animal policies (`n_drop`).
4. **Weekly Settlement**: Every Friday close, weekly performance, NAV, and execution statistics are settled.

---

## Privacy & Anonymization Architecture

This repository is engineered for open publication under strict privacy standards:

- **Model Weight Isolation**: Binary weights (`*.pkl`, `trained_model`) remain strictly in local private directories and are barred from version control.
- **Contestant Anonymization**: Public metadata uses standardized anonymous IDs (`CONTESTANT_A` through `CONTESTANT_F`).
- **Zero Raw Capital/Position Fingerprints**: All reported NAV time series are strictly normalized (Initial NAV $\equiv 1.0000$). Individual stock codes in public reports are securely masked.
- **Automated Privacy Auditor**: Includes `scripts/audit_privacy.py` enforcing zero-leakage reporting.

---

## Repository Structure

```
QuantPits-Arena/
├── manifests/
│   ├── public/              # Anonymized contestant definitions (Git tracked)
│   └── private/             # Local private contestant manifests & mappings (Git ignored)
├── scripts/
│   ├── audit_privacy.py     # Local zero-leakage privacy & compliance scanner
│   └── anonymize_manifests.py # Deterministic public manifest generator
├── AGENTS.md                # AI agent operating guidelines & security rules
└── .gitignore               # Strict exclusion rules
```

---

## Compliance Audit

To audit the repository before any commit or release:

```bash
python3 scripts/audit_privacy.py
```
