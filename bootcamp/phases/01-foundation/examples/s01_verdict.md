# VERDICT — S01 MA(10/50) crossover on AAPL

DATE:        (fill in)
STATUS:      KILL
SHIPPED BY:  (your name)

## Thesis
Trends in large-cap equities persist for weeks because of slow capital flows (index rebalancing, fund allocations) and because traders anchor to recent prices. A fast/slow moving-average crossover is the cheapest possible way to express 'be long when the short-term trend is up'. Expectation: it captures the middle of big moves, gets chopped in sideways markets, and should beat buy-and-hold on a risk-adjusted basis by cutting exposure during drawdowns -- IF the whipsaw cost is smaller than the drawdown it avoids. That is the bet.

## Rules
- Long 1.0 when MA(10) > MA(50), else flat 0.0
- Signal computed on today's close, executed at tomorrow's close (backtester shift)
- No leverage, no shorting, no stops

## Costs modeled
- fee 1.0 bps + slippage 5.0 bps per unit traded
- borrow 50 bps/yr on short notional (unused here: long-flat only)

## Results (net of costs, 10.0 yrs)
| metric | strategy | buy & hold |
|---|---|---|
| CAGR | +3.04% | +8.05% |
| Sharpe | +0.19 | +0.37 |
| Sortino | +0.14 | +0.37 |
| max DD | -31.72% | -41.94% |
| Calmar | +0.10 | +0.19 |
| ann. vol | 16.26% | 22.01% |
| hit rate | 48.8% | 51.0% |

- gross Sharpe (zero costs): +0.21  ->  net: +0.19
- costs removed 0.03 of Sharpe
- total cost paid: 4.1% of capital over 69 trades

## Out-of-sample (walk-forward, 5 folds)
| fold | test_start | test_end | strat_sharpe | strat_cagr | bh_cagr | max_dd | trades |
|---|---|---|---|---|---|---|---|
| 1 | 2021-01-15 | 2021-11-02 | -1.74 | -24.0 | -16.5 | -19.7 | 8 |
| 2 | 2021-11-03 | 2022-08-23 | 1.9 | 37.6 | 36.7 | -7.5 | 3 |
| 3 | 2022-08-24 | 2023-06-13 | 0.18 | 3.2 | 21.9 | -17.9 | 9 |
| 4 | 2023-06-14 | 2024-04-03 | -0.52 | -8.6 | -2.4 | -16.9 | 5 |
| 5 | 2024-04-04 | 2025-01-23 | 0.58 | 9.9 | 36.8 | -24.2 | 7 |

- mean OOS Sharpe: +0.08  vs in-sample net Sharpe +0.19

## Decision
- Beats buy & hold net of costs? **NO**
- Meets the viability bar (Sharpe > 0.5 and CAGR > 0)? **NO**
- VERDICT: **KILL**

## Why (3 sentences, no hedging)
The crossover cut volatility versus buy & hold but gave up most of the return,
so net of costs it lost to simply holding the asset.
Costs removed 0.03 of Sharpe across
69 trades, and the out-of-sample folds
degraded versus in-sample,
which means the edge (if any) is
fragile to period choice.

## What I'd try next (max 2, each must be a new testable claim)
1. Add a trend filter (only take long signals above the 200-day MA) -- claim:
   it removes the whipsaw trades in sideways regimes.
2. Test on a 5-symbol universe -- claim: if this is a real trend effect it
   should show up on more than one asset.

## Graveyard
- If KILL: create `notes/failures/YYYY-MM-DD-S01-ma-crossover.md` using the
  Failure Note Template and add a row to `graveyard/graveyard.md`.
