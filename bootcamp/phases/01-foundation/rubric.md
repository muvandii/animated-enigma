# Phase 01 Rubric — Foundation (Weeks 1–2)

**Gate:** you do not open `../02-engine/` until this passes.

| # | Criterion | Weight | How to check | Score |
|---|---|---|---|---|
| 1 | **5 strategies shipped** (S01–S05) | 30 | 5 `strategies/*/verdict.md` exist | /30 |
| 2 | **Costs modeled everywhere** | 15 | every tear sheet states fee+slippage in bps | /15 |
| 3 | **Out-of-sample everywhere** | 15 | every verdict has OOS numbers with DATES | /15 |
| 4 | **Notes complete** | 20 | 14 daily + 4 concept + 5 strategy + ≥3 failure | /20 |
| 5 | **Graveyard honest** | 10 | ≥4 rows, each root cause naming a concept | /10 |
| 6 | **Phase summary** | 10 | `reports/phase1-summary.md`, all 5 rows, gross-vs-net gap computed | /10 |

**Pass: ≥80/100 AND criterion 1 is perfect (5/5 strategies).**

---

## Per-strategy checklist (repeat 5×)

- [ ] `strategy.py` runs end to end on real (or seeded-synthetic) data
- [ ] fee **and** slippage modeled, stated in bps, with a one-line rationale
- [ ] turnover reported, and computed from the signal before backtesting
- [ ] out-of-sample: walk-forward folds OR a held-out period, with dates
- [ ] `verdict.md` complete, including the WHY section in 3 plain sentences
- [ ] `notes/strategies/<ID>.md` with PRE-REGISTRATION filled before results
- [ ] benchmark (buy & hold) printed alongside
- [ ] net Sharpe ≤ gross Sharpe (if not, you have a bug)
- [ ] no Sharpe > 5 anywhere (if yes, investigate look-ahead first)
- [ ] if KILL: graveyard row + same-day failure note

## What a pass looks like (calibration)

**Pass (85):** 5 strategies shipped, 4 killed with concept-level root causes, all
tear sheets have costs and OOS, notes complete and same-day, phase summary shows
the gross-vs-net gap sorted by turnover. Best strategy reported with the
multiple-comparisons adjustment applied.

**Pass (100):** all of the above, PLUS: at least one strategy run on a
multi-symbol universe with per-symbol results reported (not just the best one);
at least one pre-registered claim that FAILED and was logged as a failure; and
the viral-strategy debunk worksheet completed and applied to the student's own
S01.

**Fail (70):** 4 strategies shipped; or costs modeled on only some; or OOS
reported without dates; or notes backfilled on Sunday.

**Fail (<60):** fewer than 4 strategies; or any strategy reported gross-only; or
a graveyard with fewer than 3 rows; or failure notes whose root cause is
"needs more tuning" / "market conditions changed".

---

## The three failure modes of Phase 1

1. **Gross-only shipping.** The most common. Guard: a verdict without a cost
   model in basis points is not a verdict.
2. **Backfilled notes.** You will be tempted, on Sunday, to write seven daily
   notes from memory. They will be vague, and they will be the least useful
   notes you ever write. The rubric treats a backfilled note as a missing note.
3. **"Needs more tuning" as a root cause.** It is not a root cause. Ask "tuning
   what, and why would that change the mechanism?" until you reach a concept you
   could have stated in advance.

## Self-grade

| Criterion | Score | Evidence (file paths) |
|---|---|---|
| 5 strategies shipped | /30 | |
| Costs modeled | /15 | |
| Out-of-sample | /15 | |
| Notes complete | /20 | |
| Graveyard honest | /10 | |
| Phase summary | /10 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
