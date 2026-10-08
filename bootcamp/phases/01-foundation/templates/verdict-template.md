# VERDICT — <ID> <strategy name>

DATE:        <YYYY-MM-DD>
STATUS:      <SHIP (paper) | KILL>
SHIPPED BY:  <your name>
UNIVERSE:    <symbols, count>
SAMPLE:      <start> → <end>  (<N> bars, <M> yrs)

## Thesis
<1 paragraph. Copy it verbatim from notes/strategies/<ID>.md. If you are tempted
to edit it now that you have seen the results, STOP — that is the whole failure
mode this template exists to prevent.>

## Rules
- entry:
- exit:
- position sizing:
- universe & rebalance frequency:
- <precise enough that a stranger could reimplement it>

## Costs modeled
- fee: <n> bps   slippage: <n> bps   borrow: <n> bps/yr on shorts
- **rationale for these numbers:** <e.g. "US large-cap, market orders, <1% of ADV">
- turnover/yr: <n>   (computed from the SIGNAL before backtesting: <method>)
- total cost paid over sample: <n>% of capital

## Results
| metric | strategy | benchmark (buy & hold) |
|---|---|---|
| total return | | |
| CAGR | | |
| ann. vol | | |
| Sharpe | | |
| Sortino | | |
| max drawdown | | |
| Calmar | | |
| hit rate | | |
| trades | | |

- gross Sharpe (zero costs): <n>   ->   net Sharpe: <n>   (gap: <n>)
- **Is the gross-vs-net gap explained by turnover x cost? <show the arithmetic>**

## Out-of-sample
Method: <walk-forward N folds, train_frac, embargo> OR <held-out period with dates>

| fold | period | strategy Sharpe | strategy CAGR | benchmark CAGR | max DD | trades |
|---|---|---|---|---|---|---|

- mean OOS Sharpe: <n>   in-sample net Sharpe: <n>   ratio: <n>
- **If OOS/IS < 0.5: state plainly that the in-sample result was not real.**

## Decision
- Beats benchmark net of costs? **<YES/NO>**
- Meets the pre-registered kill criteria? **<YES/NO — list each criterion>**
- Sharpe < 5 (i.e. you checked for look-ahead)? **<YES/NO>**
- VERDICT: **<SHIP (paper) | KILL>**

## Why (3 sentences, no hedging)
<Name the single number that decided it. No "maybes", no "could be tuned".
If KILL: name the MECHANISM (costs / no OOS stability / look-ahead / survivorship
/ leverage artifact / too few trades), not "needs more work".>

## What I'd try next (max 2, each a NEW testable claim)
1. <change> — claim: <what should happen and why> — test: <how, with dates>
2. <change> — claim: <...> — test: <...>

## Graveyard
- If KILL: graveyard row added? ☐   failure note at `notes/failures/<date>-<ID>-<cause>.md`? ☐
- If SHIP (paper): what is the specific condition that would make you kill it later?
