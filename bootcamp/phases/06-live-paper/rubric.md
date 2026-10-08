# Phase 06 Rubric — Live paper trading (Week 12)

**Gate:** ≥80/100 AND 30 complete daily entries AND zero unexplained gaps.

| # | Criterion | Weight | Check | Score |
|---|---|---|---|---|
| 1 | **30 daily entries** | 30 | `live/live-log.md`, 30 consecutive dated entries | /30 |
| 2 | **Zero unexplained gaps** | 25 | every `status != OK` row has an explanation | /25 |
| 3 | **Reconciliation notebook** | 15 | all 6 panels filled | /15 |
| 4 | **Incidents** | 15 | every error logged with root cause AND prevention | /15 |
| 5 | **Cost measurement** | 10 | realized vs assumed slippage; live vs backtest turnover | /10 |
| 6 | **Safety + notes** | 5 | paper mode proven, no secrets, 7 daily notes + 1 concept note | /5 |

**Pass: ≥80/100 AND criteria 1 and 2 are both perfect.**
Fewer than 30 entries or any unexplained gap is a course fail, not a phase fail.

---

## Detailed checks

### 1. Thirty daily entries (30)
- [ ] 30 consecutive trading days, dated
- [ ] each entry has intended positions, actual positions, differences, and a lesson
- [ ] gaps in the sequence are explained (market holidays are fine; missing days are not)

### 2. Zero unexplained gaps (25)
- [ ] `live/reconciliation.csv` has one row per day per symbol
- [ ] every row with `status != OK` has a non-empty `explanation`
- [ ] the notebook's panel-2 assertion passes
- [ ] explanations name mechanisms ("partial fill due to the $2,000 order cap"),
      not symptoms ("didn't fill")

### 3. Reconciliation notebook (15)
- [ ] daily status counts
- [ ] cumulative unexplained gap (must be 0.000)
- [ ] slippage distribution vs the assumed 5 bps
- [ ] intended vs actual equity, with the execution gap quantified
- [ ] fill rate
- [ ] live vs backtest turnover

### 4. Incidents (15)
- [ ] every error, rejection, and anomaly has an entry
- [ ] each entry has a root cause
- [ ] each entry has a prevention (a control you added, ideally with a test)
- [ ] no `SIDE_DIFF` is left unresolved

### 5. Cost measurement (10)
- [ ] realized slippage: mean, median, p95, and the ratio to the assumed value
- [ ] live vs backtest turnover, with any ratio > 1.5 explained
- [ ] affected verdicts restated if realized costs differ materially from assumed

### 6. Safety + notes (5)
- [ ] paper/testnet mode proven (screenshot or statement)
- [ ] `git log -p | grep -iE "key|secret|token"` returns nothing
- [ ] `pytest harness/test_harness.py -q` green
- [ ] 7 daily notes + `notes/concepts/operational-risk.md`

---

## Calibration

**Pass (85):** 30 entries, clean reconciliation, notebook filled, incidents logged
with causes. Slippage measured but the verdict restatement is thin.

**Pass (100):** all of the above, plus: realized slippage materially differed from
the assumption and you RESTATED the affected verdicts (this is the highest-value
outcome of the whole phase); at least one strategy was killed based on live data
rather than backtest data; every incident has a prevention that was added as a
test; and the notebook's "what live trading exposed that backtesting cannot"
section is specific.

**Fail (70):** 25–29 entries; or a handful of unexplained gaps; or incidents
logged without root causes.

**Fail (<60):** fewer than 25 entries; or systematic unexplained gaps; or any
evidence of live (non-paper) trading; or secrets committed to the repo.

---

## Automatic failures (no partial credit)

- Any real-money order, ever.
- Any credential in the repository history.
- Fewer than 30 daily entries.
- An unresolved `SIDE_DIFF`.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| 30 daily entries | /30 | |
| Zero unexplained gaps | /25 | |
| Reconciliation notebook | /15 | |
| Incidents | /15 | |
| Cost measurement | /10 | |
| Safety + notes | /5 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
