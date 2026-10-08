# Phase 05 Rubric — Risk & portfolio (Weeks 10–11)

**Gate:** ≥80/100 AND the P01 portfolio is shipped.

| # | Criterion | Weight | Check | Score |
|---|---|---|---|---|
| 1 | **Risk layer** | 25 | `engine/risk.py`, 4 functions, ≥10 tests | /25 |
| 2 | **Sizing comparison** | 20 | 5 strategies × 4 methods, Sharpe AND max DD | /20 |
| 3 | **Selection rule** | 15 | mechanical, written before application | /15 |
| 4 | **Portfolio construction** | 20 | 5 weighting schemes, choice on validation window | /20 |
| 5 | **Correlation regimes** | 10 | calm vs worst-month correlation + N_eff | /10 |
| 6 | **Notes** | 10 | 14 daily, 4 concept notes | /10 |

**Pass: ≥80/100 AND P01 shipped.**

---

## Detailed checks

### 1. Risk layer (25)
- [ ] `kelly_fraction` — and the report shows full/half/quarter Kelly
- [ ] `vol_target_scale` — realized vol within 20% of target
- [ ] `drawdown_breaker` — with an explicit re-entry rule
- [ ] `correlation_limit` — effective number of bets
- [ ] ≥10 tests, including "no sizing method increases max drawdown" sanity checks

### 2. Sizing comparison (20)
- [ ] 5 survivors × 4 methods
- [ ] both Sharpe and max drawdown reported per cell
- [ ] a stack is named as the one you would use, with reasoning

### 3. Selection rule (15)
- [ ] numeric rule (e.g. net Sharpe > 0.3 AND OOS/IS > 0.6 AND trades > 50)
- [ ] applied mechanically to every strategy
- [ ] no strategy included or excluded for a reason outside the rule

### 4. Portfolio construction (20)
- [ ] 5 schemes: equal, inverse-vol, risk-parity, min-variance, signal-weighted
- [ ] covariance estimated on a ROLLING window (test asserts this)
- [ ] choice made on the validation window, test window untouched
- [ ] P01 shipped with tear sheet + verdict

### 5. Correlation regimes (10)
- [ ] average pairwise correlation in calm months and in the worst 5% of months
- [ ] effective number of bets computed for both regimes
- [ ] the verdict states the implication for sizing

### 6. Notes (10)
- [ ] 14 daily notes, 4 concept notes (Kelly, ruin, risk parity, correlation regimes)

---

## Calibration

**Pass (85):** risk layer implemented and tested; sizing table complete; portfolio
built with 5 schemes; correlation regimes computed. The selection rule exists but
is applied a little loosely.

**Pass (100):** all of the above, plus: the Kelly experiment shows full Kelly's
drawdown and you state a personal fraction; the circuit-breaker has a re-entry
rule and you measured what it costs; the correlation-regime result changed your
sizing decision (and you can say how); and P01's verdict honestly compares the
portfolio to the best single strategy even if the portfolio loses.

**Fail (70):** 3 of 4 risk functions; or the sizing table reports only Sharpe; or
the portfolio used a full-sample covariance; or the choice cites test-window
numbers.

**Fail (<60):** no risk layer; or no portfolio; or the covariance look-ahead is
present and untested.

---

## The Phase 5 failure mode

**Minimum-variance with a full-sample covariance matrix.** It produces the best
backtest you will see all course, and it is entirely an artefact. The test you
must have:

```python
def test_covariance_never_uses_future():
    w = min_variance_weights(returns, asof=DATE)
    w_later = min_variance_weights(returns_truncated_at_DATE, asof=DATE)
    np.testing.assert_allclose(w, w_later)     # future data must not change today's weights
```

If that test fails, every portfolio number you report is fiction.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| Risk layer | /25 | |
| Sizing comparison | /20 | |
| Selection rule | /15 | |
| Portfolio construction | /20 | |
| Correlation regimes | /10 | |
| Notes | /10 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
