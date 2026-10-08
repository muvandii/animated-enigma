# Grading — self-assessed, artifact-evidenced

You grade yourself. The grade is only meaningful if every checkbox points at a
file that exists. **No file, no credit — including for things you genuinely
learned.** Understanding that produced no artifact is indistinguishable from not
understanding.

## Weights

| # | Component | Weight | Evidence required |
|---|---|---|---|
| 1 | **Strategy verdicts** | 25% | 16 `strategies/*/verdict.md`, each with costs + OOS + verdict. Gate: <15 shipped = 0 for this component. |
| 2 | **Backtester quality** | 15% | `engine/` yours, ≥40 tests passing, `engine/README.md`, look-ahead suite present. |
| 3 | **Paper replications** | 15% | 3 `papers/replications/*/`, each with a delta table vs the paper. |
| 4 | **Live paper log** | 15% | 30 daily entries, reconciliation notebook filled, incidents logged. |
| 5 | **Journal + graveyard** | 15% | `journal/lessons.md` appended 13×, `graveyard/graveyard.md` with ≥10 entries. |
| 6 | **Notes vault** | 15% | ~140 notes, each meeting the 4 criteria below. |

Cutoffs: **<15 strategies = fail.** **<30 live days = fail.** **<100 notes =
fail.** A missing component is a zero, not a partial.

---

## Component 1 — Strategy verdicts (25%)

Per strategy, 4 checks. All 4 or it does not count as shipped.

- [ ] `strategy.py` runs end-to-end on real (or seeded-synthetic) data
- [ ] costs modeled: fee **and** slippage, stated in bps, in the verdict
- [ ] out-of-sample results: walk-forward or a held-out period, with dates
- [ ] `verdict.md` filled, including the **WHY** section in plain sentences
- [ ] `notes/strategies/<ID>.md` exists using the Strategy Note Template
- [ ] if KILL: graveyard row + failure note

Scoring: 16/16 shipped = 25 pts. 15/16 = 22. 13–14 = 18. <13 = 8. <15 = 0.

**Honesty multiplier:** any strategy whose verdict you cannot defend in a
5-minute oral exam ("where did the future leak?") reduces this component by 50%.

## Component 2 — Backtester quality (15%)

- [ ] `engine/` written by you (the borrowed `backtester.py` does not count)
- [ ] event-driven or clearly-documented vectorized core
- [ ] ≥40 unit tests, all passing
- [ ] `engine/README.md` documents the position convention, cost model, and fill
      assumptions
- [ ] look-ahead test suite (≥8 tests) present and passing
- [ ] all Phase-01 strategies re-run and reconciled within 2% of their
      `backtester.py` numbers

## Component 3 — Paper replications (15%)

Per replication:
- [ ] read the paper first; rules extracted into a `spec.md` before coding
- [ ] your implementation, from the spec, not from someone else's GitHub
- [ ] delta table: your number vs paper's number, with a written reason for every
      gap > 20%
- [ ] an honest "did not reproduce" is worth full credit **if** the delta is
      explained. Faking agreement is an automatic zero for the component.

## Component 4 — Live paper log (15%)

- [ ] 30 consecutive daily entries in `live/live-log.md`
- [ ] each entry: intended positions, actual positions, difference, explanation
- [ ] `live/reconciliation.ipynb` filled with the 30-day series
- [ ] `live/incidents.md`: every error, missed order, API failure — with root cause
- [ ] **paper mode only**, proven by a screenshot of the broker's paper badge

## Component 5 — Journal + graveyard (15%)

- [ ] `journal/lessons.md` has 13 weekly entries
- [ ] each weekly entry answers the three feedback-loop questions (below)
- [ ] `graveyard/graveyard.md` has ≥10 rows, each with a concept-level root cause
- [ ] ≥8 failure notes, written the same day the failure happened

## Component 6 — Notes vault (15%)

~140 notes: 91 daily + ~20 concept + 16 strategy + ~15 failure.

Every note must meet **4 criteria**. A note failing any one does not count:

1. **Specific** — names a file, a number, or a line of code. Not "learned about
   Sharpe."
2. **Dated / same-day** — written the day it happened. Backfilled notes are
   fiction and you know it.
3. **Self-contained** — readable in 6 months with zero other context.
4. **Has a forward action** — a next move, a question, or a claim to test.

Scoring: ≥140 = 15. 120–139 = 12. 100–119 = 8. <100 = 0 (course fail).

---

## The feedback loop — end of every phase (Weeks 2, 4, 7, 9, 11, 12, 13)

Answer all three, in `journal/lessons.md`, in prose, no bullet fragments.
These are graded under Component 5.

### 1. What pattern killed most strategies?

Not "the market is efficient." Name the mechanical pattern: costs ate the edge at
N trades/year; the effect existed in-sample only; the signal was look-ahead; the
universe was survivorship-biased; the result was one outlier month.

**Sample answer (Week 2):**
> Costs, and specifically the interaction between turnover and signal decay.
> Three of five strategies had a positive gross Sharpe and a negative net Sharpe.
> The two that survived net of costs both traded under 20 times a year. My RSI-2
> version traded 180 times a year and needed a 60 bp per-trade edge just to break
> even after 6 bps round-trip. The pattern: I keep building signals with a
> half-life of ~3 days and a cost basis sized for signals with a half-life of
> ~30 days. Fix: from Week 5, I compute expected turnover BEFORE I backtest, and
> if turnover × cost > 50% of the gross edge, I do not build it.

### 2. Which concept made the biggest difference?

One concept. Explain what changed in your code because of it.

**Sample answer (Week 4):**
> Purge and embargo. I had been splitting my data at a date boundary and calling
> the second half "out-of-sample," but my labels were 20-day forward returns, so
> the last 20 days of training had seen the first 20 days of test. Adding a
> 20-bar embargo dropped S06's OOS Sharpe from 0.9 to 0.4. That one change
> reclassified a strategy I had already mentally shipped. It also retroactively
> explains the Week 2 result I could not account for.

### 3. What am I still fooling myself about?

The most valuable question. Answer it honestly or the whole course is theater.

**Sample answer (Week 7):**
> That my parameter sweeps are searches and not tests. I ran 400 parameter
> combinations for S12, took the best, and reported it as one result. The
> deflated Sharpe math says my expected out-of-sample Sharpe is roughly 0.1, not
> the 1.4 I printed. I am also fooling myself that a 10-year sample means I have
> 10 years of evidence — with 69 trades I have 69 observations of the thing that
> actually matters, and the bootstrap CI on my Sharpe is ±0.35.

---

## Gate escalation

If you fail a gate twice, do not re-run the gate. Go back one week, re-read that
week's concept injections, and rewrite the artifact from the template. Failing a
gate three times means the prerequisites are missing, not that the gate is wrong.

## Self-grade worksheet

| Component | Weight | Your evidence files | Score |
|---|---|---|---|
| Strategy verdicts | 25 | | /25 |
| Backtester | 15 | | /15 |
| Paper replications | 15 | | /15 |
| Live paper log | 15 | | /15 |
| Journal + graveyard | 15 | | /15 |
| Notes vault | 15 | | /15 |
| **Total** | **100** | | |
