# Portfolio — <Your name>

**One page. A skim-reader should get the whole picture in 60 seconds.**

---

## At a glance

| | |
|---|---|
| Period | <start> → <end> (13 weeks, <N> hours) |
| Strategies shipped | **<N>** of 16 |
| Strategies killed | **<N>** (<kill rate>%) |
| Survivors | **<N>** |
| Best net Sharpe (deflated) | **<n>** |
| Live paper days | **30** |
| Notes written | **<N>** |
| Tests written | **<N>** |

## What I built

- **A backtester** (`engine/`) — event-driven, <N> unit tests, look-ahead suite
  with 8+ detectors, documented conventions and limitations.
- **<N> strategies** (`strategies/`) — each with costs, out-of-sample results, a
  break-even analysis, and a written verdict.
- **<N> paper replications** (`papers/replications/`) — with delta tables
  explaining every gap > 20% from the published results.
- **A portfolio** (`strategies/P01_combined_portfolio/`) — <weighting scheme>,
  <N> strategies combined.
- **30 days of live paper trading** (`live/`) — daily reconciliation, <N>
  unexplained gaps, realized slippage <n> bps vs <n> assumed.

## The scoreboard

| ID | Strategy | Mechanism | Trades/yr | Gross SR | Net SR | OOS SR | Verdict |
|---|---|---|---|---|---|---|---|
| S01 | MA(10/50) | trend | 7 | +0.21 | +0.19 | +0.08 | KILL |
| | | | | | | | |
| **Survivors** | | | | | | | |
| | | | | | | | |

## What killed the most strategies

1. **<mechanism>** — <N> strategies. <one sentence>
2. **<mechanism>** — <N> strategies. <one sentence>
3. **<mechanism>** — <N> strategies. <one sentence>

## Honest summary

> <3 sentences. What you set out to do, what actually happened, and the single
> most useful thing you learned. No hedging.>

**What I would tell someone starting this tomorrow:** <one sentence.>

---

## Links

- Full writeup: [`writeup.md`](./writeup.md)
- Graveyard: [`../graveyard/graveyard.md`](../graveyard/graveyard.md)
- Notes vault: [`../NOTES.md`](../NOTES.md)
- Self-grade: [`../SELF-GRADE.md`](../SELF-GRADE.md)
- Quick start: [`../README.md`](../README.md)

*All results are from backtests on historical data and 30 days of paper trading.
No real money was used. Nothing here is investment advice.*
