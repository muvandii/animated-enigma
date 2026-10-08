# Week 5 — Momentum and pairs

> **Phase 03 · Strategy factory** · Hours: 16–20 · Strategies: S06, S07, S08
>
> Three new mechanisms, all ported through the factory. The skeletons are in
> `strategies/` — your job is to run them, break them, and write verdicts, not to
> write them from scratch.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Ship S06 (time-series momentum), S07 (cross-sectional momentum), and S08 (distance pairs) via the config-driven factory
WHY:          These three are the workhorses of the published literature. Everything you replicate in Weeks 8–9 is a variant of one of them, so shipping them now makes the replications deltas rather than cold starts.
INPUT:        phases/03-strategy-factory/strategies/{momentum,pairs}.py, configs/*.json, engine/ (Week 4)
OUTPUT:       strategies/S06_ts_momentum/{strategy.py,config.json,tearsheet.txt,verdict.md}
              strategies/S07_xs_momentum/{...}
              strategies/S08_distance_pairs/{...}
              notes/strategies/{S06,S07,S08}.md, notes/daily/week-05/*.md (7)
              notes/concepts/{time-series-vs-cross-sectional-momentum,cointegration-vs-correlation}.md
              graveyard/graveyard.md (+rows for anything killed)
PROOF:        `python run_strategy.py configs/<name>.json` prints a tear sheet with costs, >=3 walk-forward folds, and embargo >= lookahead_bars, for all three
TIME:         960–1200 min
BLOCKER IF:   any config's lookahead_bars is understated (S06/S07 use trailing data only, so 1 is correct; if you add a forward-return label, it is not)
```

---

## Daily objectives

### Monday — Read the skeletons, then form pairs

```text
🎯 OBJECTIVE:   Read strategies/{momentum,pairs}.py line by line and write the three theses with pre-registered kill criteria
WHY:          You cannot break code you have not read. And S08's formation/trading split is the single easiest place in the course to accidentally introduce look-ahead.
INPUT:        strategies/{momentum,pairs}.py
OUTPUT:       notes/strategies/{S06,S07,S08}.md (thesis + kill criteria + expected turnover)
              notes/daily/week-05/mon.md
PROOF:        each note explains, in your own words, WHY the formation window must end before the trading window begins
TIME:         120 min
BLOCKER IF:   you cannot state S08's lookahead window without looking
```

### Tuesday — S06 time-series momentum through the factory

```text
🎯 OBJECTIVE:   Run S06 and break it: costs, OOS, and the vol-scaling question
WHY:          TSMOM's defining feature is that it scales by inverse volatility. That scaling is also a turnover generator, so the gross/net gap will be larger than you expect.
INPUT:        configs/ts_momentum.json, run_strategy.py
OUTPUT:       strategies/S06_ts_momentum/{config.json,tearsheet.txt}
              notes/daily/week-05/tue.md
PROOF:        tear sheet shows turnover, and you have computed whether the vol-scaling (not the signal) is what generates it
TIME:         150 min
BLOCKER IF:   you cannot separate signal turnover from vol-targeting turnover
```

Test this specifically: run S06 twice — once with `target_vol` scaling on, once
with a constant 1.0 position. If the turnover differs by more than 3×, the vol
scaler is your cost driver, and the verdict must say so.

### Wednesday — S06 verdict, S07 build

```text
🎯 OBJECTIVE:   Ship S06's verdict and run S07 (cross-sectional momentum) through the factory
WHY:          S06 and S07 are routinely conflated in blog posts. Running them a day apart, on the same universe, makes the difference concrete in your own numbers.
INPUT:        strategies/S06_ts_momentum/, configs/
OUTPUT:       strategies/S06_ts_momentum/verdict.md
              notes/strategies/S06.md (results)
              strategies/S07_xs_momentum/{config.json,tearsheet.txt}
              graveyard/graveyard.md (S06 row if KILL)
              notes/daily/week-05/wed.md
PROOF:        S06 verdict compares against buy & hold AND states whether results are level-driven or vol-scaling-driven
TIME:         150 min
BLOCKER IF:   S07's universe has fewer than 5 symbols — cross-sectional ranking needs a cross-section
```

### Thursday — Break S07; build S08

```text
🎯 OBJECTIVE:   Break S07 (costs + OOS + the "is it just beta?" test) and run S08 (distance pairs)
WHY:          A dollar-neutral cross-sectional strategy's first question is whether it is short volatility rather than long skill. Answer it before you ship.
INPUT:        strategies/S07_xs_momentum/, strategies/pairs.py
OUTPUT:       strategies/S07_xs_momentum/tearsheet.txt (with the beta test)
              strategies/S08_distance_pairs/{config.json,tearsheet.txt}
              notes/daily/week-05/thu.md
PROOF:        S07's tear sheet reports correlation of its returns to the equal-weight universe return; if |beta| > 0.3 it is not dollar-neutral in practice
TIME:         150 min
BLOCKER IF:   S08's pairs are selected over the whole sample instead of per-formation-window — that is look-ahead, fix it now
```

### Friday — S07 verdict; break S08

```text
🎯 OBJECTIVE:   Ship S07's verdict, then attack S08 with the three pairs-specific kills
WHY:          Pairs trading dies in three specific ways, and all three are testable: the spread is not stationary, the pair selection is look-ahead, and the convergence takes longer than your capital can wait.
INPUT:        strategies/S08_distance_pairs/
OUTPUT:       strategies/S07_xs_momentum/verdict.md
              notes/strategies/S07.md (results)
              strategies/S08_distance_pairs/tearsheet.txt (with the stationarity test)
              notes/concepts/cointegration-vs-correlation.md
              notes/daily/week-05/fri.md
PROOF:        for each of the top 5 pairs, an ADF or half-life estimate on the log spread is reported
TIME:         150 min
BLOCKER IF:   you report a pairs result without testing whether the spread mean-reverts
```

### Saturday — S08 verdict; write the momentum-vs-pairs comparison

```text
🎯 OBJECTIVE:   Ship S08's verdict and write reports/week5-comparison.md
WHY:          Three mechanisms, one table. This is where you find out whether your universe can support more than one kind of edge at all.
INPUT:        strategies/S06,S07,S08
OUTPUT:       strategies/S08_distance_pairs/verdict.md
              notes/strategies/S08.md (results)
              reports/week5-comparison.md (3 rows + correlation matrix of their returns)
              notes/daily/week-05/sat.md
PROOF:        the correlation matrix is reported; any pair of strategies with |rho| > 0.7 is flagged as redundant
TIME:         120 min
BLOCKER IF:   the correlation matrix is missing
```

### Sunday — Journal + ledger

```text
🎯 OBJECTIVE:   Append the Week 5 journal entry and update strategy-ledger.md with S06–S08
WHY:          The ledger is the evidence you ran the loop. Three more rows this week.
INPUT:        strategies/S06..S08 verdicts
OUTPUT:       journal/lessons.md (Week 5 entry), strategy-ledger.md (3 rows)
              notes/daily/week-05/sun.md
PROOF:        ledger rows have gross Sharpe, net Sharpe, OOS Sharpe, turnover, verdict, and killed-by
TIME:         60 min
BLOCKER IF:   any ledger row has a blank cell
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Time-series vs cross-sectional momentum

```text
📐 CONCEPT: Time-series (absolute) vs cross-sectional (relative) momentum
WHY NOW:   Wednesday's S06 verdict and Thursday's S07 build sit one day apart and you will be
           tempted to describe both as "momentum". They have different risk exposures and
           different failure modes, and conflating them will corrupt your Week 9 replication.
FORMULA:   TS:  w_i,t = sign(r_i,t-12m..t-1m) x (target_vol / sigma_i,t)     [vs its own history]
           XS:  w_i,t = (rank_i,t - mean_rank_t) / sum|rank - mean_rank|      [vs its peers]
           XS is ~dollar-neutral by construction; TS is not and can be net short in a bear market.
CODE:      ts = np.sign(px.shift(21) / px.shift(252) - 1)                     # one asset
           xs = mom.rank(axis=1, pct=True).sub(0.5).mul(2).div(mom.notna().sum(1) - 1, axis=0)
EXAMPLE:   On your 5-symbol universe, TS momentum was in cash ~35% of the time; XS momentum was
           ~100% invested, half long half short, and its return correlation with the equal-weight
           universe was <0.1. Those are two completely different bets with the same name.
TIME:      20 min
NOTE:      write notes/concepts/time-series-vs-cross-sectional-momentum.md
DONE WHEN: you can compute both rankings in 3 lines, explain in 2 sentences why XS is exposed to
           dispersion rather than level, and spot the "cross-sectional" strategy that ranks
           against a universe of 2 assets (that is not a cross-section, it is one pair)
```

### 📐 CONCEPT — Cointegration vs correlation

```text
📐 CONCEPT: Cointegration, correlation, and why pairs need the former
WHY NOW:   Friday's S08 tear sheet is blocked until you can test whether each spread actually
           mean-reverts. Correlation is not the test. Two assets can be 0.95 correlated and
           their spread can wander forever.
FORMULA:   spread_t = log(P_A,t) - beta * log(P_B,t),  beta from OLS on the FORMATION window
           ADF test: d(spread)_t = phi * spread_{t-1} + e_t ;  phi < 0 and significant => reverting
           half-life = -ln(2) / ln(1 + phi)
           Correlation measures co-MOVEMENT of returns; cointegration means the LEVELS cannot
           drift arbitrarily far apart.
CODE:      import statsmodels.api as sm                      # or: np.polyfit for beta
           beta = np.polyfit(np.log(pb), np.log(pa), 1)[0]
           sp = np.log(pa) - beta * np.log(pb)
           phi = np.polyfit(sp[:-1].values, np.diff(sp.values), 1)[0]
           print(phi, -np.log(2)/np.log(1+phi) if phi < 0 else "no reversion")
EXAMPLE:   Run it on your top pair. If half-life > your max_hold (60 bars), the trade cannot
           converge inside your risk limit -- that pair is untradeable at your settings
           regardless of how good the backtest looked.
TIME:      20 min
NOTE:      write notes/concepts/cointegration-vs-correlation.md
DONE WHEN: you can estimate beta and a half-life in 3 lines, explain in 2 sentences why high
           correlation does not imply a tradable spread, and spot pairs selected by minimum
           price-distance over the FULL sample (look-ahead: formation must precede trading)
```

---

## ✅ CHECKPOINT RUBRIC — Week 5 gate

- [ ] 3 strategy folders, each with `config.json`, `tearsheet.txt`, `verdict.md`
- [ ] every config declares `lookahead_bars`, and the embargo respects it
- [ ] costs + OOS in all three verdicts, with dates
- [ ] S08's pairs are formed on a window that ENDS before the trading window starts
- [ ] S07's beta to the equal-weight universe is reported
- [ ] `reports/week5-comparison.md` has the 3-row table and the correlation matrix
- [ ] 7 daily notes, 2 concept notes, 3 strategy notes
- [ ] `strategy-ledger.md` has 3 new complete rows

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **S06:** remove the vol scaling. If the Sharpe rises, your vol targeting is
>    costing more than it saves at this turnover, and you should say so.
> 2. **S07:** run it on a universe of 2 symbols. Watch the "cross-sectional"
>    strategy degenerate into a single pair, and log it.
> 3. **S08:** select pairs using the WHOLE sample instead of per-window. Record
>    the Sharpe difference — that number is the value of the look-ahead you are
>    not allowed to use.

## Next

Week 6: volatility and calendar effects (S09, S10, S11).
