# Week 7 — Dual momentum, baskets, and the parameter-discipline week

> **Phase 03 · Strategy factory** · Hours: 14–18 · Strategies: S12, S13
>
> Two more strategies, and then the week's real deliverable:
> `reports/parameter-sweep.md` — an honest account of how many of your "winners"
> were luck.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Ship S12 (dual momentum) and S13 (mean-reversion basket), then run a full parameter sweep with a deflated verdict
WHY:          You have now shipped 13 strategies. The probability that some of them look good by chance is near 1. This week produces the single document that separates what you found from what you fitted.
INPUT:        strategies/, configs/, all prior verdicts, strategy-ledger.md
OUTPUT:       strategies/S12_dual_momentum/{strategy.py,config.json,tearsheet.txt,verdict.md}
              strategies/S13_mr_basket/{...}
              reports/parameter-sweep.md  <-- THE deliverable
              sweeps/<date>-S12-*/{manifest.json,000..0NN.json,results.csv}
              notes/strategies/{S12,S13}.md, notes/daily/week-07/*.md (7)
              notes/concepts/deflated-sharpe.md
PROOF:        reports/parameter-sweep.md reports the number of configs tested (N), the best net Sharpe, the deflated Sharpe, and the share of configs that beat the benchmark
TIME:         840–1080 min
BLOCKER IF:   the sweep reports only the winning config
```

---

## Daily objectives

### Monday — S12 thesis + build

```text
🎯 OBJECTIVE:   Write S12's thesis and build dual momentum (absolute + relative) via the factory
WHY:          Dual momentum is the first strategy you have built that can be in CASH by design. That makes its benchmark comparison genuinely interesting rather than a formality.
INPUT:        strategies/momentum.py (reuse the ranking), configs/
OUTPUT:       notes/strategies/S12.md (pre-registration), strategies/S12_dual_momentum/{strategy.py,config.json}
              notes/daily/week-07/mon.md
PROOF:        S12 has an explicit cash/bond state and the tear sheet reports the fraction of time in each
TIME:         150 min
BLOCKER IF:   S12 has no out-of-market state — then it is just cross-sectional momentum with a new name
```

### Tuesday — S13 build; break S12

```text
🎯 OBJECTIVE:   Build S13 (mean-reversion basket) and break S12 with costs + OOS
WHY:          S13 tests whether z-scored mean reversion works better as a basket than as pairs — the basket diversifies idiosyncratic risk, but it also diversifies away the dislocations that made pairs work.
INPUT:        strategies/pairs.py (reuse the z-score), strategies/S12_dual_momentum/
OUTPUT:       strategies/S13_mr_basket/{strategy.py,config.json}
              strategies/S12_dual_momentum/tearsheet.txt
              notes/daily/week-07/tue.md
PROOF:        S12's tear sheet reports time-in-cash, time-in-assets, and the Sharpe of each state separately
TIME:         150 min
BLOCKER IF:   S13 ranks fewer than 5 assets per rebalance
```

### Wednesday — S12 verdict; break S13

```text
🎯 OBJECTIVE:   Ship S12's verdict, then break S13 (costs, OOS, and the "is it just short vol?" test)
WHY:          Mean-reversion baskets are structurally short volatility: they sell winners and buy losers, which is exactly the payoff of a short straddle. You need to know whether you are being paid for reversion or for bearing crash risk.
INPUT:        strategies/S13_mr_basket/
OUTPUT:       strategies/S12_dual_momentum/verdict.md
              notes/strategies/S12.md (results)
              strategies/S13_mr_basket/tearsheet.txt (with the worst-month analysis)
              notes/daily/week-07/wed.md
PROOF:        S13's tear sheet reports its return in the worst month of the universe and compares it to the universe's return that month
TIME:         150 min
BLOCKER IF:   you report S13 without stating its behavior in the worst drawdown month
```

### Thursday — S13 verdict + start the sweep

```text
🎯 OBJECTIVE:   Ship S13's verdict and build the parameter sweep harness
WHY:          Thursday is the earliest you can start the sweep and still have Friday and Saturday to interpret it. The harness is code; the interpretation is the deliverable.
INPUT:        strategies/, run_strategy.py
OUTPUT:       strategies/S13_mr_basket/verdict.md
              notes/strategies/S13.md (results)
              sweeps/<date>-S12-dual-momentum/manifest.json + N config files
              notes/daily/week-07/thu.md
PROOF:        >= 24 configs generated programmatically from a grid; manifest.json records the grid
TIME:         150 min
BLOCKER IF:   fewer than 24 configs, or any config was hand-written rather than generated
```

### Friday — Run the sweep; write the deflated-Sharpe concept note

```text
🎯 OBJECTIVE:   Run all sweep configs, produce results.csv, and write notes/concepts/deflated-sharpe.md
WHY:          The sweep produces the numbers; the concept note is what lets you interpret them. Without the note, you will look at the best Sharpe and believe it.
INPUT:        sweeps/<date>-S12-*/
OUTPUT:       sweeps/<date>-S12-*/results.csv
              notes/concepts/deflated-sharpe.md
              notes/daily/week-07/fri.md
PROOF:        results.csv has one row per config with net Sharpe, OOS Sharpe, turnover, trades, and all parameter values
TIME:         150 min
BLOCKER IF:   results.csv has fewer rows than configs (a failed run must be recorded as a row with an error, not dropped)
```

### Saturday — Write reports/parameter-sweep.md

```text
🎯 OBJECTIVE:   Write reports/parameter-sweep.md — the honest account
WHY:          This document is the highest-value artifact in the entire course. It is the one you will re-read in Week 13 when you are tempted to believe a good number.
INPUT:        sweeps/*/results.csv, notes/concepts/deflated-sharpe.md
OUTPUT:       reports/parameter-sweep.md
              notes/daily/week-07/sat.md
PROOF:        the report states N, best Sharpe, median Sharpe, deflated Sharpe, share of configs beating the benchmark, and the Sharpe surface (is the optimum a plateau or a spike?)
TIME:         150 min
BLOCKER IF:   the report does not distinguish a plateau from a spike
```

**The plateau test.** Plot Sharpe against each parameter. If the best region is a
broad plateau, the parameter is doing real work. If it is a single spike
surrounded by bad values, you fitted noise. This is more informative than any
single statistic, and it is why you must report the surface, not the maximum.

### Sunday — Journal, ledger, Phase 3 gate

```text
🎯 OBJECTIVE:   Append the Week 7 journal entry, add 2 ledger rows, and self-grade Phase 3
WHY:          Phase 3 ends today: 8 strategies shipped, and a document that says how many of them were real.
INPUT:        all Phase 3 artifacts
OUTPUT:       journal/lessons.md (Week 7 + Phase 3 feedback-loop answers)
              strategy-ledger.md (2 rows)
              notes/daily/week-07/sun.md
PROOF:        Phase 3 rubric self-graded; all three feedback-loop questions answered with numbers from the sweep
TIME:         90 min
BLOCKER IF:   the Phase 3 feedback-loop answer to "what am I still fooling myself about" does not cite the sweep
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Deflated Sharpe ratio

```text
📐 CONCEPT: Deflated Sharpe ratio (Bailey & Lopez de Prado)
WHY NOW:   Saturday's report is blocked: you have a best-of-24 Sharpe and no idea what it means.
FORMULA:   SR* = expected max Sharpe across N trials under the null of zero skill
           SR_adj ~ SR_obs - sqrt(V) * ( (1-gamma)*Z^-1(1 - 1/N) + gamma*Z^-1(1 - 1/(N*e)) )
           simplified: SR_adj ~ SR_obs - sqrt(2 ln N) / sqrt(T_years)
           V = variance of the Sharpe estimates across trials (use it; it is usually > 1)
CODE:      import numpy as np
           N, T, V = 24, 10, 1.5                       # 24 configs, 10 yrs, observed variance
           adj = np.sqrt(V) * np.sqrt(2*np.log(N)) / np.sqrt(T)
           print(f"deflate the best Sharpe by ~{adj:.2f}")   # ~0.53
EXAMPLE:   Your S12 sweep's best net Sharpe is 0.71 across 24 configs over 10 years. Deflated:
           0.71 - 0.53 = 0.18. The median config was 0.05. So the "best" strategy is ~0.2, and
           the gap between best and median (0.66) is mostly selection, not skill.
TIME:      20 min
NOTE:      write notes/concepts/deflated-sharpe.md
DONE WHEN: you can compute the deflation in 3 lines, explain in 2 sentences why the MAXIMUM of many
           trials overstates skill, and spot a sweep report that quotes only the top row
```

### 📐 CONCEPT — Parameter plateaus vs spikes

```text
📐 CONCEPT: Parameter surface shape (plateau vs spike)
WHY NOW:   Same blocker as above, different diagnostic. The deflated Sharpe tells you the expected
           size of the bias; the surface shape tells you whether THIS result is a bias.
FORMULA:   For parameter p, look at SR(p) over the grid.
           plateau: |SR(p_best) - SR(p_neighbour)| is small over a wide range -> robust
           spike:   SR(p_best) >> SR(p_best +/- 1 step) -> fitted to noise
           robustness ratio = median(SR over top quartile of configs) / SR_best
CODE:      top = results.nlargest(max(1, len(results)//4), "net_sharpe")
           ratio = top["net_sharpe"].median() / results["net_sharpe"].max()
           print(f"robustness ratio {ratio:.2f}  (>0.7 = plateau, <0.4 = spike)")
EXAMPLE:   S12's lookback grid [63, 126, 252, 504]: Sharpe 0.21, 0.58, 0.71, 0.19. The optimum at
           252 is a spike -- one step away in either direction loses most of the edge. That is
           what fitting looks like, and it means 252 is not "the right lookback", it is the one
           that got lucky in this sample.
TIME:      15 min
NOTE:      write notes/concepts/parameter-plateaus.md
DONE WHEN: you can compute a robustness ratio in 3 lines, explain in 2 sentences why a spike is
           evidence of fitting, and spot a parameter grid so coarse that a spike looks like a plateau
```

---

## ✅ CHECKPOINT RUBRIC — Week 7 gate (Phase 3 gate)

- [ ] S12 and S13 folders complete
- [ ] Sweep: ≥24 configs, generated programmatically, manifest recorded
- [ ] `results.csv` has one row per config (failures recorded, not dropped)
- [ ] `reports/parameter-sweep.md` states N, best, median, deflated Sharpe, share beating benchmark, plateau-vs-spike
- [ ] 7 daily notes, 2 concept notes, 2 strategy notes
- [ ] Phase 3 feedback loop answered, citing the sweep
- [ ] `strategy-ledger.md` complete through S13 (13 rows)

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> Kill the winner. Take the best config from your sweep and:
> 1. Re-run it on the 5 years you did NOT sweep over, if any exist. If you swept
>    the whole sample, re-run on a different universe.
> 2. Nudge each parameter one grid step and record the Sharpe.
> 3. Report how much of the best Sharpe survives both.
>
> Then write the graveyard row **for the winning config**, not for a loser. This
> is the hardest graveyard entry you will write and the most valuable.

## Next

Phase 4 (`../04-paper-replication/`): reproduce three published papers.
