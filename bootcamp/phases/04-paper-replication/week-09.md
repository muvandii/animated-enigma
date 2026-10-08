# Week 9 — Two more replications, then the pattern

> **Phase 04 · Paper replication** · Hours: 16–20 · Strategies: S15, S16
>
> Two papers, five days. Then the Phase 4 gate, whose real question is: across
> three replications, what did you learn about the gap between published results
> and reproducible ones?

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Replicate vol-managed momentum (Barroso/Moreira-Muir) and distance pairs (Gatev et al.), and write reports/replication-synthesis.md across all three
WHY:          One replication teaches you the mechanics. Three teach you the pattern — and the pattern is that published magnitudes do not survive contact with free data and post-publication samples.
INPUT:        papers/dossiers/02-*.md and 03-*.md, strategies/S07_xs_momentum/, strategies/pairs.py
OUTPUT:       papers/replications/vol-managed-momentum/{spec.md,replicate.py,results.md,delta-table.md}
              papers/replications/ggR-pairs/{spec.md,replicate.py,results.md,delta-table.md}
              strategies/S15_vol_managed_momentum/{...}, strategies/S16_ggR_pairs/{...}
              reports/replication-synthesis.md  <-- the Phase 4 deliverable
              notes/strategies/{S15,S16}.md, notes/daily/week-09/*.md (7)
PROOF:        both delta tables have ratio columns with written causes; reports/replication-synthesis.md compares the three gaps and ranks the causes
TIME:         960–1200 min
BLOCKER IF:   either replication changed the paper's economic parameters to improve the result
```

---

## Daily objectives

### Monday — Vol-managed momentum: spec

```text
🎯 OBJECTIVE:   Write papers/replications/vol-managed-momentum/spec.md, including the three-competing-explanations test design
WHY:          This replication has a specific trap (is it momentum-specific, generic vol targeting, or look-ahead?). The test design must be written before the code, or you will not run it.
INPUT:        papers/dossiers/02-vol-managed-momentum.md
OUTPUT:       spec.md, notes/strategies/S15.md (pre-registration)
              notes/daily/week-09/mon.md
PROOF:        spec.md specifies three runs: (a) WML vol-managed, (b) RANDOM long-short vol-managed, (c) WML vol-managed with the vol window shifted one more bar back
TIME:         150 min
BLOCKER IF:   the random-portfolio control is missing — without it you cannot distinguish explanation 1 from explanation 2
```

### Tuesday — Implement and run all three

```text
🎯 OBJECTIVE:   Implement vol-managed momentum and run all three specifications
WHY:          The control runs are the experiment. The headline run alone tells you nothing.
INPUT:        spec.md, strategies/S07_xs_momentum/
OUTPUT:       papers/replications/vol-managed-momentum/replicate.py
              results.md (all three specifications side by side)
              notes/daily/week-09/tue.md
PROOF:        results.md reports: raw WML Sharpe, vol-managed WML Sharpe, vol-managed RANDOM Sharpe, and vol-managed-with-lagged-vol Sharpe
TIME:         180 min
BLOCKER IF:   the lagged-vol run is missing
```

**Interpretation guide:** if the improvement survives the lagged-vol run but the
random portfolio improves by a similar amount, the finding is "vol targeting
works generically", which is real but is NOT the paper's specific claim. Write
exactly that.

### Wednesday — Vol-managed delta table; pairs spec

```text
🎯 OBJECTIVE:   Write the vol-managed delta table, then write the pairs spec
WHY:          Two papers, offset by a day, keeps the rhythm you learned in Week 5.
INPUT:        results.md, papers/dossiers/03-distance-pairs-gatev.md
OUTPUT:       papers/replications/vol-managed-momentum/delta-table.md
              papers/replications/ggR-pairs/spec.md
              notes/daily/week-09/wed.md
PROOF:        the delta table states whether the improvement is momentum-specific or generic, with numbers
TIME:         150 min
BLOCKER IF:   the delta table does not answer the specificity question
```

### Thursday — Implement pairs

```text
🎯 OBJECTIVE:   Implement distance pairs with a strict non-overlapping formation/trading walk, and count your trades
WHY:          The number of trades is the number of independent observations. Under 50, the confidence interval on your Sharpe is wider than your Sharpe, and you must say so.
INPUT:        papers/replications/ggR-pairs/spec.md, strategies/pairs.py
OUTPUT:       papers/replications/ggR-pairs/replicate.py, results.md
              notes/daily/week-09/thu.md
PROOF:        results.md reports the number of trades, the number of formation windows, and the Sharpe with the two best pairs removed
TIME:         180 min
BLOCKER IF:   pairs are re-selected using any data from the trading window
```

### Friday — Pairs delta table; ship S15

```text
🎯 OBJECTIVE:   Write the pairs delta table and ship S15 (vol-managed momentum) as a strategy
WHY:          Every replication becomes a strategy with a verdict. Two more ledger rows this week.
INPUT:        results.md, spec.md
OUTPUT:       papers/replications/ggR-pairs/delta-table.md
              strategies/S15_vol_managed_momentum/{strategy.py,config.json,tearsheet.txt,verdict.md}
              notes/strategies/S15.md (results)
              notes/daily/week-09/fri.md
PROOF:        S15's verdict cites the specificity test result
TIME:         150 min
BLOCKER IF:   S15's verdict claims the paper's result was confirmed without the control runs
```

### Saturday — Ship S16; write reports/replication-synthesis.md

```text
🎯 OBJECTIVE:   Ship S16 (GGR pairs) and write the three-replication synthesis
WHY:          This is the Phase 4 deliverable: the pattern across three papers, ranked by cause.
INPUT:        all three replications
OUTPUT:       strategies/S16_ggR_pairs/{...}
              notes/strategies/S16.md
              reports/replication-synthesis.md
              notes/daily/week-09/sat.md
PROOF:        the synthesis has a table with one row per paper (paper Sharpe, your Sharpe, ratio, dominant cause) and a ranked list of gap causes
TIME:         180 min
BLOCKER IF:   the synthesis does not rank the causes
```

### Sunday — Journal, ledger, Phase 4 gate

```text
🎯 OBJECTIVE:   Append the Week 9 journal entry, add 2 ledger rows, self-grade Phase 4
WHY:          Phase 4 ends today. 16 strategies should now be shipped.
INPUT:        all Phase 4 artifacts, strategy-ledger.md
OUTPUT:       journal/lessons.md (Week 9 + Phase 4 feedback-loop answers)
              strategy-ledger.md (S15, S16 rows)
              notes/daily/week-09/sun.md
PROOF:        ledger has 16 rows; Phase 4 rubric self-graded; all three feedback-loop questions answered
TIME:         90 min
BLOCKER IF:   fewer than 16 ledger rows
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — The control experiment in replication

```text
📐 CONCEPT: Control runs that separate a specific claim from a generic effect
WHY NOW:   Monday/Tuesday's blocker. You will find that vol-managed momentum beats raw momentum in
           your sample, and that finding has three possible explanations. Without controls it is
           unfalsifiable, and unfalsifiable findings are worth nothing.
FORMULA:   claim:      SR(vol-managed WML) > SR(WML)
           control 1:  SR(vol-managed RANDOM) vs SR(RANDOM)    -> isolates generic vol targeting
           control 2:  SR(vol-managed-lagged WML) vs SR(WML)   -> isolates look-ahead in the vol est.
           specific effect survives ONLY if the claim holds AND control 1's improvement is
           materially smaller AND control 2's improvement is ~equal to the claim's.
CODE:      rng = np.random.default_rng(0)
           random_ls = pd.DataFrame(rng.choice([-1.0, 1.0], size=px.shape),
                                    index=px.index, columns=px.columns)
           # then apply the SAME vol scaler to random_ls and to WML, compare Sharpe deltas
EXAMPLE:   If WML goes 0.42 -> 0.68 (+0.26) and RANDOM goes 0.01 -> 0.23 (+0.22), then ~85% of the
           improvement is generic vol timing, not momentum-specific. The honest headline is
           "vol targeting added +0.22 to +0.26 of Sharpe regardless of the underlying signal".
TIME:      20 min
NOTE:      write notes/concepts/control-experiments-in-replication.md
DONE WHEN: you can design both controls in 3 lines, explain in 2 sentences why a single run cannot
           distinguish a specific from a generic effect, and spot the replication that reports the
           headline improvement with no control
```

### 📐 CONCEPT — Effective sample size and the number of trades

```text
📐 CONCEPT: Effective sample size (N_eff) for a trading strategy
WHY NOW:   Thursday's blocker: your pairs backtest has 2,520 daily bars but maybe 40 trades. Which
           number governs the confidence interval on your Sharpe?
FORMULA:   SE(SR) ~ sqrt((1 + SR^2/2) / N_eff)
           N_eff = number of INDEPENDENT observations ~ number of trades (or number of
                   non-overlapping holding periods), NOT number of bars
           With overlapping monthly positions over 10 years: N_eff ~ 120 months, not 2520 days.
CODE:      import numpy as np
           SR, N = 0.4, 40
           se = np.sqrt((1 + SR**2 / 2) / N)
           print(f"Sharpe {SR:.2f} +/- {1.96*se:.2f} (95% CI)")     # +/- 0.31
EXAMPLE:   Your GGR pairs result: Sharpe 0.38 on 46 trades. 95% CI is +/- 0.29, i.e. [0.09, 0.67].
           It is positive, but the interval is nearly as wide as the estimate. Reporting "Sharpe
           0.38" without the interval overstates what you know by a lot.
TIME:      15 min
NOTE:      write notes/concepts/effective-sample-size.md
DONE WHEN: you can compute the CI in 3 lines, explain in 2 sentences why 2,520 daily bars of a
           monthly strategy is 120 observations and not 2,520, and spot a Sharpe quoted to two
           decimal places on a 20-trade backtest
```

---

## ✅ CHECKPOINT RUBRIC — Week 9 gate (Phase 4 gate)

- [ ] Both replications have spec / replicate / results / delta-table
- [ ] Vol-managed momentum: all three runs (claim + 2 controls) reported
- [ ] Pairs: formation/trading non-overlapping; trade count reported; two-best-pairs-removed test
- [ ] Both delta tables have ratio columns and written causes for > 20% gaps
- [ ] `reports/replication-synthesis.md`: one row per paper + ranked cause list
- [ ] S15 and S16 shipped with verdicts
- [ ] 7 daily notes, 2 concept notes, 2 strategy notes
- [ ] Ledger has 16 rows

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **Pairs universe attack:** run the identical code on a universe of 5
>    instruments instead of 20. Record how the Sharpe changes — that is the value
>    of candidate-pool size, quantified.
> 2. **Pairs look-ahead attack:** select pairs over the whole sample. Record the
>    Sharpe. The difference between that and your honest number is the size of the
>    single most common error in published pairs research.
> 3. **Vol-managed look-ahead attack:** use a centered 21-day vol window. Record
>    the Sharpe. Compare it to your lagged-vol control.

## Next

Phase 5 (`../05-risk-portfolio/`): sizing, risk, and the portfolio of survivors.
