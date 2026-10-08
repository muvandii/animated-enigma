# Phase 05 — Risk & portfolio (Weeks 10–11)

Two weeks, no new signals. Everything here is about the difference between a
strategy with good statistics and an account that survives long enough to collect
them.

**The uncomfortable premise:** of ~16 strategies you shipped, several survived.
But "survived a backtest" is not the same as "should be traded at size", and the
gap between those two statements is this entire phase.

## Files

| File | What |
|---|---|
| `week-10.md` | sizing: Kelly, vol targeting, circuit breakers, correlation limits |
| `week-11.md` | portfolio construction: 5 weighting schemes + the correlation-regime test |
| `rubric.md` | Phase 5 gate |

## The five things this phase must produce

1. `engine/risk.py` — 4 sizing/risk functions, ≥10 tests
2. `reports/sizing-comparison.md` — 5 strategies × 4 sizing methods, Sharpe AND max DD
3. `reports/selection-rationale.md` — a mechanical, pre-written in/out rule
4. `reports/portfolio-construction.md` — 5 weighting schemes, choice made on the validation window
5. `strategies/P01_combined_portfolio/` — the portfolio, shipped like any other strategy

## Two rules that are easy to break and expensive to break

**Rule 1: choose on validation, report on test.** The moment you pick the
weighting scheme by looking at test-window results, the test window is validation
and you have no honest number left. Write the choice down before you look.

**Rule 2: a covariance matrix is a look-ahead machine.** Minimum-variance and
risk-parity weighting estimated on a full-sample covariance matrix will produce
beautiful backtests that fail. Rolling windows only. There is a test for this.

## The number most people never compute

Average pairwise correlation in the **worst 5% of months**, versus in normal
months. If it goes from 0.2 to 0.8, your 5 strategies are 4 independent bets most
of the time and 1.4 bets exactly when you need diversification. Nothing you do in
this phase fixes that; you can only size for it.

## Start Week 12's clock now

The live-paper requirement is **30 calendar days**. Set up the paper broker
account on Sunday of Week 11, not on Monday of Week 12 — some brokers take days
to approve, and the clock is calendar time, not study time.
