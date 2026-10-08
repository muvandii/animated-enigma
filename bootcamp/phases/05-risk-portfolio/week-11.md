# Week 11 — The portfolio of survivors

> **Phase 05 · Risk & portfolio** · Hours: 14–18 · Deliverable: the portfolio
>
> You have ~16 strategies, of which some survived. This week you combine them
> into the single portfolio you will paper-trade in Week 12.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Build the portfolio of survivors with 4 weighting schemes, choose one, and prove it beats the best single strategy on a risk-adjusted basis
WHY:          A portfolio is the deliverable. Also, the honest answer is often that it does NOT beat the best single strategy, and finding that out now rather than in Week 12 is worth the week.
INPUT:        survivors, engine/risk.py, correlation matrices from Weeks 5–6
OUTPUT:       engine/portfolio_weights.py (equal, inverse-vol, risk-parity, min-variance, signal-weighted)
              engine/tests/test_portfolio_weights.py (>=8 tests)
              reports/portfolio-construction.md (5 weighting schemes x metrics, with OOS)
              strategies/P01_combined_portfolio/{strategy.py,config.json,tearsheet.txt,verdict.md}
              notes/daily/week-11/*.md (7)
              notes/concepts/{risk-parity,correlation-regimes}.md
PROOF:        reports/portfolio-construction.md compares all 5 schemes on NET OOS Sharpe and max DD, and states which one you chose and why
TIME:         840–1080 min
BLOCKER IF:   the chosen scheme was selected on the test window (use the validation window to choose, test window to report)
```

---

## Daily objectives

### Monday — Decide who is in

```text
🎯 OBJECTIVE:   Write reports/selection-rationale.md naming which strategies are IN, which are OUT, and the rule that decided it
WHY:          Selection is where most portfolios are quietly curve-fit. Write the rule first, then apply it, then do not change it.
INPUT:        strategy-ledger.md, reports/survivor-metrics.md
OUTPUT:       reports/selection-rationale.md
              notes/daily/week-11/mon.md
PROOF:        the rule is stated as numbers (e.g. "net Sharpe > 0.3 AND OOS/IS > 0.6 AND trades > 50") and every strategy is classified by it mechanically
TIME:         120 min
BLOCKER IF:   any strategy is included or excluded for a reason not in the rule
```

### Tuesday — Equal weight baseline + inverse vol

```text
🎯 OBJECTIVE:   Implement equal-weight and inverse-vol weighting and compare them
WHY:          Equal weight is the benchmark every other scheme must beat. Inverse-vol is the simplest improvement. If inverse-vol does not help, nothing fancier will.
INPUT:        engine/risk.py, survivors
OUTPUT:       engine/portfolio_weights.py (2 schemes), reports/portfolio-construction.md (first 2 rows)
              notes/daily/week-11/tue.md
PROOF:        equal-weight results are reported as the baseline row, and every other scheme is compared to it
TIME:         150 min
BLOCKER IF:   the equal-weight baseline is missing or was computed on a different sample
```

### Wednesday — Risk parity and minimum variance

```text
🎯 OBJECTIVE:   Implement risk-parity and minimum-variance weighting, with covariance estimated on a rolling (never full-sample) window
WHY:          These are the two schemes that can go badly wrong with a full-sample covariance. Rolling windows are slower and correct.
INPUT:        engine/portfolio_weights.py
OUTPUT:       risk-parity + min-variance implementations
              notes/concepts/risk-parity.md
              notes/daily/week-11/wed.md
PROOF:        the covariance matrix is estimated with a rolling window, and the test suite asserts it never uses data after the rebalance date
TIME:         180 min
BLOCKER IF:   the covariance estimate uses the full sample (that is look-ahead, and it will make min-variance look amazing and then fail)
```

### Thursday — Signal-weighted + the correlation regime test

```text
🎯 OBJECTIVE:   Implement signal-weighted combination and run the correlation-regime analysis
WHY:          Weighting by recent performance is the most intuitive scheme and the most dangerous (it chases). And the correlation-regime test tells you whether diversification survives when you need it.
INPUT:        engine/portfolio_weights.py, survivors' return series
OUTPUT:       signal-weighted scheme
              reports/correlation-regimes.md
              notes/concepts/correlation-regimes.md
              notes/daily/week-11/thu.md
PROOF:        correlation-regimes.md reports average pairwise correlation in: calm months, the worst 5% of months, and the worst single month
TIME:         150 min
BLOCKER IF:   you report only the full-sample correlation
```

### Friday — Choose, on the validation window only

```text
🎯 OBJECTIVE:   Choose the weighting scheme using the validation window, and lock it
WHY:          Choosing on the test window makes the test window meaningless. Lock the choice now, in writing, before you look.
INPUT:        reports/portfolio-construction.md (partial)
OUTPUT:       reports/portfolio-construction.md (choice row filled, with the validation-window numbers that justified it)
              notes/daily/week-11/fri.md
PROOF:        the choice is justified by validation-window numbers and the test window is untouched
TIME:         120 min
BLOCKER IF:   the justification cites test-window results
```

### Saturday — Ship P01

```text
🎯 OBJECTIVE:   Ship strategies/P01_combined_portfolio/ with a full verdict, including the OOS test-window result
WHY:          The portfolio is a strategy. It gets a folder, a tear sheet, a verdict, and a ledger row.
INPUT:        everything
OUTPUT:       strategies/P01_combined_portfolio/{strategy.py,config.json,tearsheet.txt,verdict.md}
              reports/portfolio-construction.md (complete: 5 schemes x metrics)
              notes/daily/week-11/sat.md
PROOF:        the verdict compares the portfolio to the best single strategy, on net OOS Sharpe AND max DD
TIME:         180 min
BLOCKER IF:   the verdict does not say whether the portfolio beat the best single strategy
```

### Sunday — Journal, ledger, Phase 5 gate

```text
🎯 OBJECTIVE:   Append the Week 11 journal entry, add the P01 ledger row, and self-grade Phase 5
WHY:          Phase 5 ends today. Also: start your Week 12 paper-trading account setup TODAY, because the 30-day clock is calendar time, not study time.
INPUT:        all Phase 5 artifacts
OUTPUT:       journal/lessons.md (Week 11 + Phase 5 feedback-loop answers)
              strategy-ledger.md (P01 row)
              phases/06-live-paper/ account setup checklist started
              notes/daily/week-11/sun.md
PROOF:        Phase 5 rubric self-graded; broker paper account created (or explicitly scheduled)
TIME:         90 min
BLOCKER IF:   you reach Week 12 without a paper account and then discover the 30-day clock
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Risk parity

```text
📐 CONCEPT: Risk parity / equal risk contribution
WHY NOW:   Wednesday's blocker: you are implementing it and need to know what "parity" means and
           why it is not the same as inverse-vol.
FORMULA:   portfolio vol: sigma_p = sqrt(w' Sigma w)
           risk contribution of asset i: RC_i = w_i * (Sigma w)_i / sigma_p
           risk parity: find w such that RC_i = RC_j for all i,j  (and sum(w) = 1)
           inverse-vol (1/sigma_i) is the SPECIAL CASE where all correlations are equal.
CODE:      def risk_parity(Sigma, iters=100):
               w = 1 / np.sqrt(np.diag(Sigma)); w /= w.sum()
               for _ in range(iters):
                   rc = w * (Sigma @ w); rc /= rc.sum()
                   w = w * (1/len(w) / rc) ** 0.5; w /= w.sum()
               return w
EXAMPLE:   With two assets at vol 10% and 30% and correlation 0, inverse-vol gives 75%/25%.
           Risk parity also gives 75%/25% (because corr=0). With correlation 0.8, inverse-vol
           still says 75%/25% but risk parity shifts to roughly 65%/35%, because the high-vol
           asset now contributes more risk than its own vol suggests.
TIME:      20 min
NOTE:      write notes/concepts/risk-parity.md
DONE WHEN: you can implement the iterative solver in 5 lines, explain in 2 sentences the difference
           from inverse-vol, and spot a covariance matrix estimated on the FULL sample
```

### 📐 CONCEPT — Correlation regimes

```text
📐 CONCEPT: Correlation is regime-dependent and rises toward 1 in crises
WHY NOW:   Thursday's blocker: your diversification math from Week 10 assumed a constant
           correlation. It is not constant, and it moves against you.
FORMULA:   diversification ratio DR = (sum_i w_i sigma_i) / sigma_p     [DR=1 means no benefit]
           effective number of bets  N_eff = DR^2   (approximately, for equal risk weights)
           crisis behavior: rho -> 1  =>  DR -> 1  =>  N_eff -> 1
CODE:      worst = ret.mean(axis=1).nsmallest(int(len(ret)*0.05)).index
           print("calm  rho:", ret.corr().where(~np.eye(len(c), dtype=bool)).stack().mean())
           print("worst rho:", ret.loc[worst].corr().where(~np.eye(len(c), dtype=bool)).stack().mean())
EXAMPLE:   Your 5 survivors: average pairwise correlation 0.18 normally (N_eff ~ 4.1) but 0.74 in
           the worst 5% of months (N_eff ~ 1.4). So the portfolio genuinely holds 4 independent
           bets 95% of the time and 1.4 bets exactly when diversification would pay. That is
           not a bug in your strategies; it is a property of markets, and your position sizing
           must assume it.
TIME:      15 min
NOTE:      write notes/concepts/correlation-regimes.md
DONE WHEN: you can compute conditional correlation in 3 lines, explain in 2 sentences why N_eff
           collapses in a crisis, and spot a portfolio backtest that reports the full-sample
           diversification benefit as if it applied in drawdowns
```

---

## ✅ CHECKPOINT RUBRIC — Week 11 gate (Phase 5 gate)

- [ ] `reports/selection-rationale.md`: mechanical rule, applied to all strategies
- [ ] `engine/portfolio_weights.py`: 5 schemes, ≥8 tests, rolling covariance only
- [ ] `reports/portfolio-construction.md`: 5 schemes × metrics, choice made on the validation window
- [ ] `reports/correlation-regimes.md`: calm vs worst-month correlation and N_eff
- [ ] P01 shipped with a verdict comparing it to the best single strategy
- [ ] 7 daily notes, 2 concept notes
- [ ] Week 12 paper account setup started

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **Min-variance attack:** estimate the covariance on the full sample. Record
>    the Sharpe. Compare it to the rolling-window version. The difference is the
>    value of the look-ahead you are not allowed to use.
> 2. **Chasing attack:** weight by trailing 3-month performance instead of
>    12-month. Record how much worse it is. That is the cost of chasing.
> 3. **Diversification attack:** build the portfolio from the 3 most correlated
>    survivors. Record the Sharpe and max DD. Compare to the diversified version.
>    If they are similar, your diversification was never real.

## Next

Phase 6 (`../06-live-paper/`): 30 days of live paper trading. Start the clock.
