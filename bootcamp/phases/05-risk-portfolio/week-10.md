# Week 10 — Position sizing and risk

> **Phase 05 · Risk & portfolio** · Hours: 14–18 · Strategies: none new
>
> The only week with no new strategy. Everything you have shipped so far assumed
> 100% of capital per position. That assumption is a leverage decision you never
> made explicitly.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Build the risk layer: Kelly/fractional-Kelly sizing, vol targeting, drawdown circuit breakers, and correlation-aware limits, then re-run 5 survivors through it
WHY:          The difference between a strategy that works and an account that survives is sizing. Every strategy you shipped is a return series; sizing determines whether you live to collect it.
INPUT:        5+ surviving strategies, engine/
OUTPUT:       engine/risk.py (kelly_fraction, vol_target_scale, drawdown_breaker, correlation_limit)
              engine/tests/test_risk.py (>=10 tests)
              reports/sizing-comparison.md (5 strategies x 4 sizing methods)
              notes/daily/week-10/*.md (7)
              notes/concepts/{kelly-criterion,ruin-probability}.md
PROOF:        reports/sizing-comparison.md shows, for each strategy, the Sharpe and max drawdown under fixed-fractional, vol-target, half-Kelly, and drawdown-breaker sizing
TIME:         840–1080 min
BLOCKER IF:   any sizing method produces a drawdown deeper than the strategy's un-sized drawdown (that is a bug, not a feature)
```

---

## Daily objectives

### Monday — Measure what you have

```text
🎯 OBJECTIVE:   Compute the realized Sharpe, vol, and max DD of every shipped strategy and rank them by drawdown-adjusted return
WHY:          You cannot size a portfolio of strategies you have not measured uniformly. One table, same metrics module, no exceptions.
INPUT:        strategies/S01..S16 verdicts
OUTPUT:       reports/survivor-metrics.md (one row per surviving strategy: net Sharpe, ann vol, max DD, Calmar, turnover, trades)
              notes/daily/week-10/mon.md
PROOF:        every number comes from metrics.py; no hand-computed values
TIME:         120 min
BLOCKER IF:   any surviving strategy has fewer than 30 trades (it cannot be sized meaningfully)
```

### Tuesday — Kelly and why you will not use full Kelly

```text
🎯 OBJECTIVE:   Implement kelly_fraction() and run the full-Kelly experiment on your best strategy
WHY:          Full Kelly maximizes long-run growth and is unusable in practice because you never know the true edge. You need to have watched it blow up in a backtest before you internalize that.
INPUT:        reports/survivor-metrics.md
OUTPUT:       engine/risk.py::kelly_fraction, engine/tests/test_risk.py
              reports/kelly-experiment.md (full Kelly vs half vs quarter vs fixed, on your best strategy)
              notes/concepts/kelly-criterion.md
              notes/daily/week-10/tue.md
PROOF:        the report shows full Kelly's max drawdown and the growth rate at each fraction; you state which fraction you would use and why
TIME:         150 min
BLOCKER IF:   you implement Kelly using a Sharpe estimated on fewer than 30 trades
```

### Wednesday — Vol targeting at the portfolio level

```text
🎯 OBJECTIVE:   Implement vol_target_scale() and re-run 5 survivors at a 12% portfolio vol target
WHY:          S09 targeted vol per instrument. Portfolio-level targeting is different: it uses the covariances and it changes when the strategies' correlation changes.
INPUT:        strategies (5 survivors), engine/risk.py
OUTPUT:       engine/risk.py::vol_target_scale
              reports/sizing-comparison.md (first two columns: un-sized vs vol-targeted)
              notes/daily/week-10/wed.md
PROOF:        realized vol of the vol-targeted portfolio is within 20% of the 12% target
TIME:         150 min
BLOCKER IF:   realized vol misses the target by more than 20% — the estimator is wrong or the rebalance is too slow
```

### Thursday — Drawdown circuit breakers

```text
🎯 OBJECTIVE:   Implement drawdown_breaker() and test whether de-risking after a drawdown helps or hurts
WHY:          Every fund has one. Most backtests show it hurts long-run return while improving drawdown. You need to know which regime you are in before you decide.
INPUT:        engine/risk.py, 5 survivors
OUTPUT:       engine/risk.py::drawdown_breaker
              reports/circuit-breaker.md (Sharpe and max DD with breakers at -10%, -15%, -20%, and re-entry rules)
              notes/daily/week-10/thu.md
PROOF:        the report states the re-entry rule explicitly (a breaker without a re-entry rule is just a stop-out)
TIME:         150 min
BLOCKER IF:   you test a breaker without specifying when it turns back on
```

### Friday — Correlation-aware limits

```text
🎯 OBJECTIVE:   Implement correlation_limit() and measure how much of your portfolio's risk is one bet
WHY:          Your 5 survivors may be 5 expressions of the same exposure. The correlation matrix from Week 5 told you; now you act on it.
INPUT:        reports/week5-comparison.md, reports/week6-comparison.md, strategies
OUTPUT:       engine/risk.py::correlation_limit
              reports/correlation-risk.md (effective number of independent bets, now and during the worst month)
              notes/daily/week-10/fri.md
PROOF:        the report computes the effective number of bets (via the diversification ratio) and compares it to the nominal count, in normal times AND in the worst month
TIME:         150 min
BLOCKER IF:   you report only the full-sample correlation and not the worst-month correlation
```

**The number that matters:** if 5 strategies have an average pairwise correlation
of 0.2 normally and 0.8 in the worst month, you have 5 strategies in calm markets
and 1.2 strategies when you need them. Compute it.

### Saturday — Re-run survivors through the risk layer

```text
🎯 OBJECTIVE:   Apply your chosen sizing stack to all 5 survivors and produce the before/after table
WHY:          The risk layer is only real if it changes the numbers. Saturday is where you find out whether it was worth a week.
INPUT:        engine/risk.py (complete), 5 survivors
OUTPUT:       reports/sizing-comparison.md (complete, 5 strategies x 4 sizing methods)
              notes/daily/week-10/sat.md
PROOF:        the table shows Sharpe AND max drawdown for every combination; you name the stack you would actually use
TIME:         150 min
BLOCKER IF:   the table reports only Sharpe (max drawdown is half the point of risk management)
```

### Sunday — Journal + concept note

```text
🎯 OBJECTIVE:   Write notes/concepts/ruin-probability.md and append the Week 10 journal entry
WHY:          Ruin is the risk that actually ends careers, and it is not visible in a Sharpe ratio.
INPUT:        reports/sizing-comparison.md
OUTPUT:       notes/concepts/ruin-probability.md
              journal/lessons.md (Week 10 entry)
              notes/daily/week-10/sun.md
PROOF:        the concept note computes the probability of a 50% drawdown at your chosen sizing, and states whether that is acceptable to you personally
TIME:         90 min
BLOCKER IF:   the note does not state a personal answer to "what drawdown would make you quit"
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Kelly criterion

```text
📐 CONCEPT: Kelly criterion and fractional Kelly
WHY NOW:   Tuesday's blocker: you have five strategies and no principled way to size them.
FORMULA:   For a bet with edge mu and variance sigma^2 (continuous, Gaussian):
           f* = mu / sigma^2                      [full Kelly, = Sharpe / sigma]
           growth rate g(f) = f*mu - 0.5*f^2*sigma^2, maximized at f*
           g(f*/2) = 0.75 * g(f*)                  half Kelly gives 3/4 the growth, 1/2 the vol
           g(f) = 0 at f = 2*f*                    beyond 2x Kelly, growth is NEGATIVE
CODE:      sr, vol = 0.5, 0.15
           f_star = sr / vol                       # 3.33 (i.e. 333% leverage!)
           print(f"full Kelly {f_star:.2f}x  half {f_star/2:.2f}x  quarter {f_star/4:.2f}x")
EXAMPLE:   Your best survivor: Sharpe 0.48, vol 12%. Full Kelly = 0.48/0.12 = 4.0x leverage.
           At 4x, a 25% drawdown in the strategy wipes you out. Half Kelly (2x) still gives a
           50% wipeout on the same move. This is why you use quarter Kelly or vol targeting, and
           why "Kelly optimal" and "Kelly sane" are different numbers.
TIME:      20 min
NOTE:      write notes/concepts/kelly-criterion.md
DONE WHEN: you can compute f* in 3 lines, explain in 2 sentences why full Kelly is unusable when
           the edge is estimated, and spot a Kelly calculation that uses the Sharpe as the edge
           without dividing by volatility (that gives a number in the wrong units)
```

### 📐 CONCEPT — Ruin probability and the drawdown you would actually quit at

```text
📐 CONCEPT: Risk of ruin, and personal drawdown tolerance
WHY NOW:   Sunday's blocker. Every risk number you have computed is a statistic about a return
           series; ruin is a statement about whether you keep trading.
FORMULA:   P(ever hitting a drawdown of depth D) rises toward 1 as time grows, for ANY strategy
           with positive vol. Approx for a Brownian motion with drift mu, vol sigma:
           P(hit -D) ~ exp(-2*mu*D/sigma^2)   (mu > 0, in log terms)
           Time to recover from a drawdown D at annual return r: t = D / r (roughly; a 50%
           drawdown needs +100% to recover, so recovery time is superlinear in depth)
CODE:      mu, sig, D = 0.06, 0.12, 0.5
           print(f"P(50% drawdown) ~ {np.exp(-2*mu*D/sig**2):.2f}")
           print(f"years to recover at 6%/yr: {np.log(1/(1-D))/np.log(1.06):.1f}")
EXAMPLE:   Sharpe 0.5 at 12% vol = 6% drift. P(50% drawdown) ~ exp(-2*0.06*0.5/0.0144) = 12%.
           Over a 30-year career that is not a tail event, it is a scheduled one. And recovering
           from -50% at 6%/yr takes ~12 years. Decide NOW what depth you would stop at, write it
           down, and make the circuit breaker enforce it.
TIME:      15 min
NOTE:      write notes/concepts/ruin-probability.md
DONE WHEN: you can compute an approximate ruin probability in 3 lines, explain in 2 sentences why
           recovery time is superlinear in drawdown depth, and spot a "max drawdown" reported
           without the date range it occurred over
```

---

## ✅ CHECKPOINT RUBRIC — Week 10 gate

- [ ] `engine/risk.py` with 4 functions, ≥10 tests
- [ ] `reports/survivor-metrics.md`: uniform metrics for every survivor
- [ ] `reports/kelly-experiment.md`: fractions compared, a fraction chosen, with reasoning
- [ ] `reports/circuit-breaker.md`: breakers with explicit re-entry rules
- [ ] `reports/correlation-risk.md`: effective number of bets, normal vs worst month
- [ ] `reports/sizing-comparison.md`: 5 × 4 grid, Sharpe AND max DD
- [ ] 7 daily notes, 2 concept notes

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **Kelly attack:** run full Kelly on your best strategy. Record the max
>    drawdown. Then run it on your WORST survivor and record the same. If full
>    Kelly looks good on the best one, you have not run it long enough.
> 2. **Correlation attack:** compute the average pairwise correlation in the worst
>    month of your sample. If it exceeds 0.7, log "N strategies = 1.3 bets" as a
>    failure of diversification, not of the strategies.
> 3. **Breaker attack:** run the circuit breaker without a re-entry rule. Record
>    how much return it costs. That number is the price of the rule you forgot.

## Next

Week 11: combine the survivors into one portfolio.
