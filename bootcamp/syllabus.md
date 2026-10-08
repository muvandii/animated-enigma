# Syllabus — 13 Weeks

**Who this is for:** you know pandas (groupby, resample, merge, datetime index),
you have never shipped a trading strategy, and you want a portfolio of real
artifacts rather than a folder of notebooks.

**Time:** 10–20 hrs/week. 13 weeks. ~180 hrs total. Self-paced: the gates are
artifact-based, not calendar-based. If a week takes you three weeks, it takes
three weeks — but you do not start Week 5 until Week 4's gate passes.

**The rule that makes this work:** you may not advance on a failed gate. Ever.
Reading ahead is fine; shipping ahead is not.

---

## Phase map

| # | Phase | Weeks | Milestone (the gate artifact) | Strategies shipped | Cumulative |
|---|---|---|---|---|---|
| 01 | Foundation | 1–2 | 5 strategies with verdicts, on a borrowed backtester | 5 | 5 |
| 02 | Engine | 3–4 | your own event-driven backtester, unit-tested, documented | 0 (re-verify 5) | 5 |
| 03 | Strategy factory | 5–7 | 8 config-driven strategies + parameter sweep discipline | 8 | 13 |
| 04 | Paper replication | 8–9 | 3 published papers reproduced from scratch | 3 | 16 |
| 05 | Risk & portfolio | 10–11 | risk-managed portfolio of survivors | portfolio | 16 |
| 06 | Live paper | 12 | 30 days live paper + daily reconciliation | 2–3 live | 16 |
| 07 | Synthesis | 13 | public repo + capstone writeup | — | 16 |

**16 strategies.** The bar is 15. The 16th is insurance against one dying in
live paper.

---

## Week 1 — Ship one strategy, kill it properly

- **Objective:** ship S01 (MA crossover) through the full loop: thesis → code →
  gross backtest → costs → out-of-sample → verdict.
- **Concepts injected:** simple vs log returns; why a cost model is not optional.
- **Deliverables:** `strategies/S01_ma_crossover/{strategy.py,verdict.md}`,
  `notes/strategies/S01.md`, 7 daily notes, graveyard seeded.
- **Expected outcome:** it dies. Week 1 is designed so your first strategy gets
  killed by its own numbers. That is a pass.
- **Hours:** 12–16.

## Week 2 — Three more, faster

- **Objective:** ship S03 RSI-2 mean reversion, S04 Bollinger reversion,
  S05 Donchian breakout. Same loop, one day each.
- **Concepts injected:** stationarity / why mean reversion needs a bounded
  distribution; multiple-comparisons (you just tested 3 things).
- **Deliverables:** 3 strategy folders, 3 strategy notes, 3 verdicts, 7 daily
  notes, 3 graveyard entries (probably).
- **Hours:** 14–18.

## Week 3 — Build the engine (part 1)

- **Objective:** replace the vectorized toy with an event-driven backtester that
  supports multiple symbols, a portfolio, and an explicit order lifecycle.
- **Concepts injected:** event loop vs vectorization; the order lifecycle
  (signal → order → fill → position → P&L).
- **Deliverables:** `engine/engine.py` + `engine/README.md` + 10 unit tests;
  all 5 Phase-01 strategies re-run and reconciled (±2% of old numbers).
- **Hours:** 16–20. This is the hardest week.

## Week 4 — Engine hardening: costs, OOS, look-ahead

- **Objective:** add a real cost model, walk-forward splitter, purge/embargo,
  and a look-ahead test suite. Prove the engine cannot cheat.
- **Concepts injected:** slippage models; purge & embargo; survivorship bias.
- **Deliverables:** `engine/costs.py`, `engine/splits.py`,
  `engine/tests/test_lookahead.py` (12+ tests), tear-sheet generator.
- **Hours:** 14–18.

## Week 5 — Momentum

- **Objective:** S06 time-series momentum, S07 cross-sectional momentum,
  S08 distance pairs.
- **Concepts injected:** cross-sectional ranking & z-scores; cointegration
  (only when the pairs trade fails without it).
- **Hours:** 16–20.

## Week 6 — Volatility and calendar

- **Objective:** S09 vol-targeting overlay, S10 turn-of-month, S11 overnight gap
  fade.
- **Concepts injected:** volatility estimation (EWMA vs close-to-close), the
  variance-drag / vol-targeting math, calendar effects and why they decay.
- **Hours:** 14–18.

## Week 7 — Parameter discipline

- **Objective:** S12 dual momentum, S13 mean-reversion basket. Then run a
  **parameter sweep with a deflated verdict** and record how many "winners" were
  luck.
- **Concepts injected:** overfitting, the deflated Sharpe ratio, multiple testing.
- **Deliverable:** `reports/parameter-sweep.md` — the single most important
  document you will write about self-deception.
- **Hours:** 14–18.

## Week 8 — Replicate a paper (1 of 3)

- **Objective:** reproduce Moskowitz–Ooi–Pedersen "Time Series Momentum" end to
  end, from the paper's own rules, on data you fetch yourself.
- **Concepts injected:** reading a paper as a spec; survivorship-free universes.
- **Hours:** 16–20.

## Week 9 — Replicate two more papers

- **Objective:** S15 vol-managed momentum (Moreira–Muir / Barroso–Santa-Clara),
  S16 distance pairs (Gatev–Goetzmann–Rouwenhorst).
- **Deliverable:** a delta table: your numbers vs the paper's numbers, with a
  written explanation for every gap > 20%.
- **Hours:** 16–20.

## Week 10 — Position sizing and risk

- **Objective:** build the risk layer: Kelly/fractional-Kelly, vol targeting,
  max drawdown circuit breakers, correlation-aware limits.
- **Concepts injected:** Kelly criterion and why full Kelly is insane; ruin
  probability; drawdown-constrained sizing.
- **Hours:** 14–18.

## Week 11 — Portfolio of survivors

- **Objective:** combine the surviving strategies into one portfolio with
  risk-parity / inverse-vol weights. Compare to equal weight and to each
  standalone strategy.
- **Concepts injected:** correlation regimes, diversification ratio, why
  correlations go to 1 in a crash.
- **Hours:** 14–18.

## Week 12 — Live paper trading

- **Objective:** run 2–3 survivors live in **paper mode** for 30 days. Daily
  reconciliation: intended vs actual positions, and every difference explained.
- **Concepts injected:** operational risk; the gap between backtest fills and
  real fills; slippage measurement.
- **Deliverables:** `live/live-log.md` (30 entries), `live/reconciliation.ipynb`
  filled, `live/incidents.md`.
- **Hours:** 10–14 (plus 30 calendar days — **start the clock in Week 6** by
  setting up the harness, even if you go live later).

## Week 13 — Synthesis and public ship

- **Objective:** write the capstone, publish the repo, produce the portfolio page.
- **Deliverables:** `capstone/writeup.md`, public README, notes vault exported,
  `graveyard/graveyard.md` complete, self-grade against `capstone/rubric.md`.
- **Hours:** 14–18.

---

## Total artifacts you will have at the end

- 16 strategy folders, each with: strategy code, config, tear sheet, verdict,
  strategy note.
- 1 backtester you wrote, ~40 tests, documented.
- 3 paper replications with delta tables.
- 30 days of live paper log + reconciliation.
- ~140 notes (daily × 91, concept × 20, strategy × 16, failure × 15+).
- A graveyard with 10+ entries, each with a root cause.
- A public, shareable repo + a capstone writeup.

## Reading ahead is allowed; shipping ahead is not

You may read Weeks 5–13 tonight. You may not start Week 5's strategies until
Week 3–4's engine gate passes. The gate exists because every shortcut you take
in Weeks 3–4 becomes a silent bug in Weeks 5–11 that you will spend three weeks
finding.
