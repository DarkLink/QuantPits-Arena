# Methodology & Statistical Axioms

**Empirical Quantitative Standards**

The testing architecture, null benchmark suite, execution constraints, and statistical interpretation rules of **QuantPits Arena**.

---

## ⚖️ 1. Core Axiom: Historical Biography ≠ Arena Record

Traditional quantitative presentations often blur together historical backtests, development-period performance, and later live results.

QuantPits Arena does not.

Every contestant has two strictly separated records:

### Historical Biography & Context

Historical material may include:

* original research thesis,
* architecture and feature set,
* training period,
* historical backtest statistics,
* former production role,
* promotion / replacement history,
* and the reason the model was eventually retired.

These records exist only as biography.

**They contribute zero weight to Arena rankings.**

A former production champion receives no starting advantage.
A historically disastrous model receives no penalty.

### Arena Out-of-Sample Record

Every eligible artifact enters the common Arena at the same anchor:

* **Arena anchor:** 2026-07-03
* **Initial NAV:** 1.0000
* **Initial capital:** CNY 500,000

All Arena metrics are calculated from this common starting point.

The model artifacts themselves had no access to Arena-period market data during training. Therefore Arena returns are **out-of-sample with respect to the frozen artifacts**.

However, the distinction between model-OOS and researcher-OOS is preserved:

* Jul–Aug 2026 replay is retrospective to the researchers, although OOS to the artifacts.
* Subsequent shadow observation is prospective only while the artifact and its inference definition remain frozen.

**Historical reputation is biography. Arena performance starts from zero.**

---

## 🐒 2. High-Resolution Parametric Monkey Null Benchmark

Absolute return alone says very little about signal quality.

A strategy can earn money because its universe rises.
It can lose money during a market drawdown while still selecting unusually well.
A highly concentrated random portfolio can occasionally generate spectacular returns purely by chance.

QuantPits Arena therefore maintains a large empirical **random-ranking null benchmark**.

### Monkey Construction

For each distinct **TOPK / DROPN parameter specification**, an independent colony of:

**1,000 deterministic pseudo-random ranking paths**

is evaluated.

Current benchmark suite:

* **11 parameter groups**
* **11,000 monkey portfolios in total**

Each monkey uses:

* the same eligible stock universe,
* the same market observations,
* the same CNY 500,000 initial capital,
* the same 100-share trading-lot constraint,
* the same affordability rules,
* the same TOPK / DROPN specification,
* and the same transaction-cost assumptions,

but receives **no model signal**.

Its stock ranking is pseudo-random.

### Monkeys Do Not Imitate the Animals

The monkey colony is a **no-signal reference**, not a behavioral sympathy program.

Monkeys are parameterized by the underlying TOPK / DROPN portfolio specification.

They do **not** reproduce animal-specific behavioral choices such as:

* sleeping for several weeks,
* delaying rebalances,
* intentionally inverting the model,
* or otherwise modifying a perfectly usable signal.

If a Sloth sleeps through a useful signal, that is the Sloth's problem.

---

### Empirical Upper-Tail p-value

For return-based upper-tail testing:

$$
p_{\text{upper}}
=
\frac{
\#\{\text{Monkey Return} \ge \text{Candidate Return}\}+1
}{
N+1
}
$$

where:

* \(N=1000\) for the standard colony,
* and the `+1` correction prevents impossible claims of `p = 0`.

With 1,000 monkeys, the minimum reportable plus-one empirical p-value is approximately:

$$
1/1001 \approx 0.001
$$

The 1,000-monkey colony therefore provides approximately **0.1 percentage-point empirical rank resolution**.

This is a resolution of the empirical grid — **not a claim that the true tail probability is estimated with ±0.1% uncertainty**.

### Statistical Label

A candidate may be marked as exhibiting:

> **Statistically significant upper-tail outperformance versus its random-ranking null**

when:

$$
p_{\text{upper}} < 0.05
$$

This corresponds approximately to placement above the 95th percentile of the matched monkey distribution.

The Arena deliberately does **not** automatically translate this label into:

> "Alpha confirmed."

A low empirical p-value means the observed result is difficult to reproduce with the specified random-ranking null.

It does not, by itself, establish:

* persistent future alpha,
* causal model superiority,
* independence from all factor exposures,
* or immunity from multiple-comparison effects.

For inverted strategies such as Koala, the corresponding **lower-tail** distribution may also be examined as a directional sanity check.

---

## 🦁 3. The 28-Animal Execution Zoo Framework

[**Explore In The Zoo →**](http://localhost:8080/#animals)

A prediction model produces a ranking.

What happens after that ranking exists is a separate research question.

QuantPits Zoo therefore applies deliberately different portfolio behaviors to the **same underlying model signal** in order to study timing, persistence, turnover, ranking geometry, and concentration.

---

### 🤖 Robot — Baseline

**TOPK=22 / DROPN=3**

Weekly immediate execution.

Robot represents the baseline production-style portfolio policy and serves as the primary control animal.

---

### 🦥 Sloth 1–4 — Cash Lag

Sloth delays signal execution by:

* 1 week,
* 2 weeks,
* 3 weeks,
* or 4 weeks.

The delay applies from initial portfolio construction onward.

Before delayed purchases are executed, the corresponding capital remains uninvested.

Sloth primarily measures:

> **signal timing decay and delayed-entry robustness.**

If a model remains useful after Sloth has slept for several weeks, its signal is probably not purely instantaneous.

---

### 🐌 Snail 1–4 — Holding Lag

Snail constructs its initial portfolio normally.

Subsequent rebalance actions are delayed by:

* 1 week,
* 2 weeks,
* 3 weeks,
* or 4 weeks,

while existing positions remain in place.

Snail therefore measures:

> **the cost or benefit of holding inertia after the initial signal has already entered the portfolio.**

Sloth delays getting into the position.

Snail is already inside and simply refuses to move quickly.

---

### 🐢 Turtle & 🐇 Rabbit — Turnover Extremes

These animals test how aggressively new model information should be written into the portfolio.

**Turtle**

* TOPK=22
* DROPN=1
* ultra-low update bandwidth

**Rabbit — Half Rebalance**

Approximately half of the target portfolio may be replaced per cycle.

**Rabbit — Full Rebalance**

The portfolio may be completely refreshed each cycle.

Together with Robot, these animals form a turnover spectrum:

> Turtle → Robot → Rabbit

They test whether model information benefits from rapid deployment or whether high turnover simply accelerates the ingestion of noisy predictions.

---

### 🐨 Koala — Inverted Polarity

Koala deliberately interprets the ranking backwards.

Instead of buying the model's preferred stocks, it selects from the bottom of the ranking under an otherwise comparable long-only portfolio construction.

Koala is a directional sanity check.

A useful ranking should generally produce a meaningful separation between:

> preferred stocks
> and
> deliberately inverted selections.

If Koala consistently beats Robot, checking the sign convention is recommended.

---

### 🦡 Meerkat 10%–90% — Rank Slices

Meerkats stand at different locations along the ranked cross-section.

Rank regions from approximately:

**10% → 90%**

are sampled systematically.

The resulting performance profile examines:

* rank monotonicity,
* where predictive information is concentrated,
* whether only the extreme top ranks contain useful signal,
* and whether lower-ranked regions behave consistently with the model's ordering.

Meerkats study the **geometry of the ranking**, rather than only its TopK output.

---

### 🦅 Eagle Suite — Concentration Spectrum

Eagles operate at progressively different portfolio concentrations:

* TOPK 5 / DROPN 1
* TOPK 11 / DROPN 2
* TOPK 44 / DROPN 6
* TOPK 66 / DROPN 9
* TOPK 88 / DROPN 12

Together with the Robot's 22/3 specification, the Eagle family measures:

> **signal concentration versus diversification.**

A highly concentrated Eagle may achieve very large returns while also possessing an extremely wide random-null distribution.

Therefore:

> highest return
> and
> strongest statistical evidence

are not necessarily the same thing.

---

### 🐋 Whale Shark — Broad Selection

Whale Shark holds approximately half of the eligible universe:

* approximately 123 stocks under the current universe size,
* with DROPN scaled proportionally.

It examines how much signal survives when portfolio selection becomes broad and highly diversified.

This is a test of:

> **signal breadth and concentration sensitivity**

rather than market-capacity scaling.

---

### 🐉 Taotie — Full Universe

Taotie wants everything.

It attempts to hold the entire eligible universe and changes primarily as securities enter or leave that universe.

Conceptually, Taotie approaches the limit:

> **selection intensity → zero**

and therefore acts as the Zoo's full-universe structural reference.

Because actual execution remains subject to finite capital and 100-share trading lots, realized weights are **executable approximations of equal weighting**, not mathematically perfect fractional-share equal weights.

---

## 💰 4. Real Trading & Finite-Capital Constraints

Arena portfolios are simulated as finite-capital executable portfolios rather than frictionless continuous-weight portfolios.

### Fixed Initial Capital

Every portfolio begins with exactly:

**CNY 500,000**

No contestant receives capital proportional to its number of holdings.

---

### Minimum Trading Lot

Mainland-equity transactions obey:

**1 lot = 100 shares**

Fractional-share purchases are not permitted.

---

### Unaffordable Order Skipping

If the capital allocated to a target security cannot purchase one complete 100-share lot:

> **the order is skipped.**

The engine does not:

* round upward,
* borrow additional cash,
* or redistribute the unused allocation across other target positions.

This intentionally preserves finite-capital cash drag.

---

### Transaction Costs

All contestants and monkey portfolios use the same predefined transaction-cost model.

The exact one-way cost assumption used by the current Arena run must be reported alongside published results.

No strategy receives a frictionless execution exemption.

This is particularly important for high-turnover animals such as Rabbit and for full-rebalance monkey specifications.

---

### Universe Exit Priority

Securities no longer belonging to the eligible universe receive exit priority.

Under the current portfolio rules, forced universe exits interact with the applicable DROPN budget according to the engine's predefined execution logic.

This rule is applied consistently across contestants.

Because this choice can affect portfolios during large universe changes, the exact forced-exit implementation is treated as part of the portfolio specification rather than an incidental implementation detail.

---

## 🔬 5. Statistical Interpretation & Multiple Comparisons

QuantPits Arena contains:

* multiple historical artifacts,
* multiple animal policies,
* multiple concentration levels,
* and multiple exploratory comparisons.

Therefore the Arena is not interpreted as a collection of independent confirmatory hypothesis tests.

A nominal:

> `p < 0.05`

for one contestant means only that its observed Arena return lies unusually high relative to the specified random-ranking null.

It does **not** mean that searching across the entire Graveyard and Zoo carries a family-wise false-positive probability of 5%.

### Confirmatory vs Exploratory Comparisons

Where a historical decision pair was specified in advance — for example a surviving accepted/rejected artifact pair — it may be treated as a focused historical decision trial.

The broad Zoo and Graveyard leaderboards remain exploratory.

Arena statistics are therefore used primarily to answer:

1. Is this model/policy behaving unusually relative to random ranking?
2. How sensitive is the signal to timing, turnover, concentration, or inversion?
3. Do historical artifacts retain useful predictive structure in a common future environment?
4. Did a specific historical replacement decision appear beneficial or regrettable in subsequent OOS data?

They are **not** used to manufacture a single post-hoc "winning model" and retroactively declare it proven.

---

## 🪨 6. External Simplicity Reference

The Permanent Portfolio is displayed separately from the stock-selection Arena.

It is not a random-ranking null and does not participate in monkey significance testing.

It exists as an external simplicity benchmark:

> Four buckets.
> No ranking.
> No ensemble.
> No retraining.
> No comment.

Its purpose is not to answer whether QuantPits has stock-selection alpha.

Its purpose is to remind the Arena that complexity is not free.

---

## Final Axiom

> **Absolute return determines who wins the race.**
> **Monkey percentile determines how surprised we should be.**
> **The Zoo explains what the model's signal survives.**
> **The Rock asks whether any of this complexity was worth it.**
