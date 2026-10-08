# Phase 04 Rubric — Paper replication (Weeks 8–9)

**Gate:** ≥80/100 AND all three replications complete with delta tables.

| # | Criterion | Weight | Check | Score |
|---|---|---|---|---|
| 1 | **Three replications complete** | 30 | spec + code + results + delta table, ×3 | /30 |
| 2 | **Spec fidelity** | 20 | parameter table per paper; every deviation flagged; economic vs conventional distinguished | /20 |
| 3 | **Delta tables** | 20 | ratio column + written mechanistic cause for every >20% gap | /20 |
| 4 | **Control experiments** | 15 | vol-managed: 2 controls run; pairs: formation/trading non-overlap + trade count | /15 |
| 5 | **Synthesis** | 10 | `reports/replication-synthesis.md`, causes ranked | /10 |
| 6 | **Notes** | 5 | 14 daily, 4 concept, 3 strategy notes | /5 |

**Pass: ≥80/100 AND criterion 1 is perfect.**

---

## Detailed checks

### 1. Three replications (30)
- [ ] TSMOM (MOP 2012), vol-managed momentum (Barroso / Moreira-Muir), distance pairs (GGR 2006)
- [ ] each has `spec.md`, `replicate.py`, `results.md`, `delta-table.md`
- [ ] each promoted to a strategy folder (S14, S15, S16) with a verdict

### 2. Spec fidelity (20)
- [ ] ≥8 parameters per paper, each citing the source section
- [ ] every deviation from the paper flagged with a reason
- [ ] economic parameters (vol target, formation window) preserved exactly
- [ ] conventional parameters (rebalance date) may deviate IF documented

### 3. Delta tables (20)
- [ ] ratio column present
- [ ] every ratio outside [0.8, 1.2] has a cause
- [ ] causes are mechanisms (universe / sample / instrument / estimation), not "implementation error" or "different market"
- [ ] the diversification multiplier (or equivalent) is used to quantify the universe gap

### 4. Controls (15)
- [ ] vol-managed momentum: raw WML, vol-managed WML, vol-managed RANDOM, vol-managed with lagged vol
- [ ] pairs: non-overlapping formation/trading windows, trade count reported, two-best-pairs-removed test
- [ ] look-ahead audit run on all three replications

### 5. Synthesis (10)
- [ ] one row per paper: paper Sharpe, your Sharpe, ratio, dominant cause
- [ ] causes ranked by how much gap they explain
- [ ] an explicit statement of what you would need to close the gap

### 6. Notes (5)
- [ ] 14 daily notes, 4 concept notes, 3 strategy notes

---

## Calibration

**Pass (85):** three replications done honestly; delta tables have causes; the
vol-managed controls were run; the synthesis ranks causes. Some causes are
hand-wavy ("different market regime") rather than quantified.

**Pass (100):** all of the above, plus: the diversification multiplier is used to
*quantify* the universe gap for all three papers; every replication reports gross
AND net with the cost drag separated; the synthesis identifies at least one cause
that is fixable and states the experiment that would fix it; and at least one
replication honestly concludes "the effect did not reproduce in my sample" with a
mechanistic explanation.

**Fail (70):** two replications; or a delta table with unwritten causes; or the
vol-managed controls were skipped; or a paper's economic parameters were changed
to improve results.

**Fail (<60):** fewer than two replications; or any replication that copies an
existing implementation instead of working from the paper; or a replication
reported gross-only as if it were the paper's number.

---

## The Phase 4 failure mode

**Closing the gap by changing the rules.** You will find your number is 0.1× the
paper's and every instinct will say "my universe is too small, let me add a
filter / change the lookback / drop the worst assets". Every one of those turns a
replication into a new strategy. If you want to do that, fine — pre-register it
as S17 and say clearly that it is no longer a replication. What you may not do is
report it *as* the replication.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| Three replications | /30 | |
| Spec fidelity | /20 | |
| Delta tables | /20 | |
| Control experiments | /15 | |
| Synthesis | /10 | |
| Notes | /5 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
