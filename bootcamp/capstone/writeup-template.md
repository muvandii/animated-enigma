# <Your name> — 13-Week Quant Trading Bootcamp: Capstone

**Repo:** <url>
**Dates:** <start> → <end>
**Hours:** <total>
**Strategies shipped:** <N of 16>
**Strategies killed:** <N>
**Notes:** <N>

> Everything below is traceable to a file in this repository. Where I say a
> number, the file that produced it is named. Where I do not know something, I
> say so.

---

## 1. What I built

**The engine** (`engine/`) — <one paragraph: event-driven or vectorized, how many
tests, what it models and what it deliberately does not.>

**The strategies** (`strategies/`) — <table: one row per shipped strategy.>

| ID | Name | Mechanism | Universe | Trades/yr | Net Sharpe | OOS Sharpe | Verdict |
|---|---|---|---|---|---|---|---|
| S01 | MA(10/50) | trend | AAPL | 7 | +0.19 | +0.08 | KILL |
| ... | | | | | | | |

**The replications** (`papers/replications/`) — <one row per paper.>

| Paper | Their Sharpe | My Sharpe | Ratio | Dominant cause of gap |
|---|---|---|---|---|
| TSMOM (MOP 2012) | 0.95 | | | |
| Vol-managed momentum | | | | |
| Distance pairs (GGR 2006) | | | | |

**The portfolio** (`strategies/P01_combined_portfolio/`) — <what you combined,
how you weighted it, and whether it beat the best single strategy.>

**Live** (`live/`) — <30 days, what you ran, realized slippage vs assumed.>

---

## 2. What died, and why

**Kill count: <N> of <M>.** The full list is in `graveyard/graveyard.md`.

The mechanisms, ranked by how many strategies each killed:

1. **<mechanism>** — killed <N> strategies. Example: <ID>. Explanation: <why, in
   2 sentences, with the number that decided it.>
2. **<mechanism>** — killed <N>. Example: <ID>. <explanation>
3. **<mechanism>** — killed <N>. Example: <ID>. <explanation>

The one I was most wrong about:

> <A strategy you believed in, what you predicted, what actually happened, and
> the concept that explained the difference. Cite the failure note.>

---

## 3. What survived, and by how much

**Survivors: <N>.**

| ID | Net Sharpe | 95% CI | OOS/IS | Trades | Break-even bps | Would I trade it? |
|---|---|---|---|---|---|---|
| | | | | | | |

For each survivor, the honest caveat:

- **<ID>:** <what would make it stop working, and what I would watch.>
- **<ID>:** <...>

**Did the portfolio beat the best single strategy?** <yes/no, with the numbers.>
If no, say why you still built it.

**What live trading changed:** <realized vs assumed slippage, and whether any
verdict had to be restated.>

---

## 4. What I would do differently

Not "I would work harder". Specific, mechanical changes:

1. **<change>** — because <specific thing that went wrong, with the week>.
2. **<change>** — because <...>.
3. **<change>** — because <...>.

---

## 5. What I still do not know

The honest list. This is the most valuable section and the one most people skip.

1. **<question>** — why it matters: <...>. What would answer it: <the experiment.>
2. **<question>** — <...>
3. **<question>** — <...>

---

## 6. The numbers that define the course for me

| Metric | Value |
|---|---|
| Strategies shipped | |
| Strategies killed | |
| Kill rate | % |
| Notes written | |
| Tests written | |
| Median turnover of shipped strategies | /yr |
| Median gross-to-net Sharpe gap | |
| Best net Sharpe (deflated) | |
| Realized slippage / assumed slippage | x |
| Days of live paper trading | |

---

## 7. The one-sentence summary

> <What you now believe about systematic trading that you did not believe 13
> weeks ago, stated so that it could be falsified.>

---

## Appendix — traceability

| Claim in this writeup | File that supports it |
|---|---|
| | |
| | |

## Self-grade

See `SELF-GRADE.md`. Total: <score>/100.

---

*All results are from backtests on historical data and 30 days of paper trading.
No real money was used. Nothing here is investment advice.*
