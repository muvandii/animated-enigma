# Phase 02 Rubric — The Engine (Weeks 3–4)

**Gate:** you do not start Week 5 until this passes at ≥80/100 AND the
reconciliation table is complete.

| # | Criterion | Weight | How to check | Score |
|---|---|---|---|---|
| 1 | **Test coverage** | 25 | ≥40 tests, all passing | /25 |
| 2 | **Look-ahead suite** | 20 | 8 named tests present; `test_peeking_signal_is_detected` FIRES | /20 |
| 3 | **Reconciliation** | 20 | 5 rows, all \|Δ\| < 2%, every residual explained in writing | /20 |
| 4 | **Cost modeling** | 15 | fee + slippage + impact + borrow + financing; break-even table per strategy | /15 |
| 5 | **OOS discipline** | 10 | embargo ≥ lookahead for every strategy; embargo audit written | /10 |
| 6 | **Documentation** | 10 | `engine/README.md`: 9 conventions + limitations | /10 |

**Pass: ≥80/100 AND criteria 2 and 3 both ≥ 80% of their weight.**

---

## Detailed checks

### 1. Test coverage (25)
- [ ] ≥40 tests
- [ ] tests exist for: data feed, portfolio, broker, costs, splits, reporting, engine, look-ahead
- [ ] tests run in < 60s (no network)
- [ ] `python -m pytest -q` from a clean checkout is green

### 2. Look-ahead suite (20)
- [ ] rewriting the future does not change the past
- [ ] position at bar t depends only on data ≤ t−1
- [ ] peeking signal produces Sharpe > 10 (detector proven to fire)
- [ ] global-statistic signal is rejected or flagged
- [ ] backward-filled prices rejected
- [ ] embargo catches label overlap
- [ ] fills applied after mark-to-market
- [ ] survivorship / point-in-time universe enforced
- [ ] **each test has a comment naming the bug it prevents**

### 3. Reconciliation (20)
- [ ] all 5 strategies re-run through the new engine
- [ ] every |Δ| < 2%
- [ ] a written cause for every residual (warm-up / cost timing / position convention / execution price)
- [ ] at least one verdict changed, and the change is logged

### 4. Cost modeling (15)
- [ ] flat bps, spread, sqrt-impact, borrow, financing all implemented
- [ ] cost can never be negative (test exists)
- [ ] `reports/cost-breakeven.md` gives a break-even bps number per strategy
- [ ] the bps assumptions are justified in writing (asset class, size, order type)

### 5. OOS discipline (10)
- [ ] `purge_and_embargo` implemented and tested
- [ ] embargo ≥ the strategy's forward-looking window, per strategy
- [ ] fold tables in every tear sheet, with dates

### 6. Documentation (10)
- [ ] the 9 conventions answered
- [ ] a "limitations" section naming what the engine does NOT model
- [ ] a worked 3-bar example in the README

---

## Calibration

**Pass (85):** engine works, 42 tests, reconciliation within 2% with causes
named, break-even tables present, embargo audit done. README covers the
conventions but the limitations section is thin.

**Pass (100):** all of the above, plus: the look-ahead suite has extra tests
beyond the 8 required; the engine is fast enough (< 60s for all 5 strategies);
at least one Phase 1 "SHIP" was honestly re-killed; and the README's limitations
section names at least three things the engine cannot model (e.g. partial fills,
borrow availability, intraday path dependency).

**Fail (72):** 30 tests; or reconciliation gaps explained as "close enough"; or
the peeking test does not fire; or tear sheets lack fold tables.

**Fail (<60):** no look-ahead suite; or reconciliation not attempted; or the
engine cannot run all 5 Phase 1 strategies.

---

## The Phase 2 failure mode to watch

**Tuning the engine until it matches.** When your reconciliation gap is 5%, the
temptation is to adjust a convention until the numbers line up. Do not. Find the
*cause* of the gap, state it, and move on. An engine tuned to reproduce
`backtester.py` inherits `backtester.py`'s bugs and calls them agreement.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| Test coverage | /25 | |
| Look-ahead suite | /20 | |
| Reconciliation | /20 | |
| Cost modeling | /15 | |
| OOS discipline | /10 | |
| Documentation | /10 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
