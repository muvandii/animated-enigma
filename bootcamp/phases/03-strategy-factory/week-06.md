# Week 6 — Volatility and the calendar

> **Phase 03 · Strategy factory** · Hours: 14–18 · Strategies: S09, S10, S11
>
> Three strategies whose edges, if they exist, are structural rather than
> directional. These are the ones most likely to be eaten by costs, so the
> break-even table matters more than the Sharpe.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Ship S09 (vol-target overlay), S10 (turn of month), S11 (overnight gap fade) with verdicts
WHY:          S09 is a risk overlay that changes how every later strategy is sized; S10 and S11 are the two calendar/structure effects most likely to be real and most likely to be arbed away. Testing both tells you whether structural effects survive in your universe and era.
INPUT:        strategies/, engine/ (week 4), data/clean/*.parquet (>=5 symbols, incl. IWM for small caps)
OUTPUT:       strategies/S09_vol_target_overlay/{strategy.py,config.json,tearsheet.txt,verdict.md}
              strategies/S10_turn_of_month/{...}
              strategies/S11_gap_fade/{...}
              notes/strategies/{S09,S10,S11}.md, notes/daily/week-06/*.md (7)
              notes/concepts/{volatility-estimation,calendar-effects-and-decay}.md
              reports/week6-comparison.md
PROOF:        all three verdicts state a break-even bps number; S09 is compared against the SAME underlying strategy unscaled
TIME:         840–1080 min
BLOCKER IF:   S09 is reported without a like-for-like unscaled comparison (otherwise you are reporting the vol target's effect, not the strategy's)
```

---

## Daily objectives

### Monday — Theses + S09 build

```text
🎯 OBJECTIVE:   Write all three theses, then build S09 (vol-target overlay on top of S06)
WHY:          S09 is not a standalone strategy, it is a sizing layer. You must be able to show its effect on an EXISTING strategy, so build it as an overlay on S06, not in isolation.
INPUT:        strategies/momentum.py, configs/ts_momentum.json
OUTPUT:       notes/strategies/{S09,S10,S11}.md (pre-registration)
              strategies/S09_vol_target_overlay/{strategy.py,config.json}
              notes/daily/week-06/mon.md
PROOF:        S09 runs S06 twice — scaled and unscaled — and prints both tear sheets side by side
TIME:         150 min
BLOCKER IF:   S09's scaled and unscaled runs use different underlying signals
```

### Tuesday — Break S09; build S10

```text
🎯 OBJECTIVE:   Break S09 (costs of the scaler, vol-of-vol, drawdown during vol spikes) and build S10 (turn of month)
WHY:          Vol targeting sells AFTER volatility rises, i.e. after the drawdown. That is a real, mechanical cost and you need to measure it rather than assert it.
INPUT:        strategies/S09_vol_target_overlay/
OUTPUT:       strategies/S09_vol_target_overlay/tearsheet.txt (scaled vs unscaled vs the vol-scaler's own cost)
              strategies/S10_turn_of_month/{strategy.py,config.json}
              notes/daily/week-06/tue.md
PROOF:        the tear sheet reports the number of trades the SCALER added versus the unscaled S06, and the Sharpe cost of those trades
TIME:         150 min
BLOCKER IF:   you report S09 without isolating the scaler's turnover
```

### Wednesday — S09 verdict; break S10; build S11

```text
🎯 OBJECTIVE:   Ship S09's verdict, break S10, and build S11 (overnight gap fade)
WHY:          Three strategies in three states again. By now this rhythm should be automatic.
INPUT:        strategies/S09_vol_target_overlay/, strategies/S10_turn_of_month/
OUTPUT:       strategies/S09_vol_target_overlay/verdict.md
              notes/strategies/S09.md (results)
              strategies/S10_turn_of_month/tearsheet.txt
              strategies/S11_gap_fade/{strategy.py,config.json}
              notes/daily/week-06/wed.md
PROOF:        S09's verdict states whether the overlay helped, hurt, or was neutral, with the Sharpe delta
TIME:         150 min
BLOCKER IF:   S09's verdict says "improved risk-adjusted returns" without giving the delta
```

### Thursday — S10 verdict; break S11

```text
🎯 OBJECTIVE:   Ship S10's verdict, then attack S11 with the overnight-vs-intraday decomposition
WHY:          Gap-fade strategies live entirely in the overnight return. If you cannot decompose total return into overnight and intraday components, you cannot tell whether your result is the gap effect or just beta.
INPUT:        strategies/S11_gap_fade/
OUTPUT:       strategies/S10_turn_of_month/verdict.md
              notes/strategies/S10.md (results)
              strategies/S11_gap_fade/tearsheet.txt (with the decomposition)
              notes/daily/week-06/thu.md
PROOF:        the decomposition is reported: what fraction of the strategy's return comes from overnight bars
TIME:         150 min
BLOCKER IF:   S11 is run without open prices — a gap strategy needs open AND close
```

### Friday — S11 verdict; the decay test

```text
🎯 OBJECTIVE:   Ship S11's verdict and run the decade-by-decade decay test on S10 and S11
WHY:          Calendar effects are the most arbitraged effects in existence. If they worked in 1995 and not in 2020, that is the finding — and it is a finding worth shipping.
INPUT:        strategies/S10,S11
OUTPUT:       strategies/S11_gap_fade/verdict.md
              notes/strategies/S11.md (results)
              reports/calendar-decay.md (Sharpe by year and by 3-year block for both)
              notes/concepts/calendar-effects-and-decay.md
              notes/daily/week-06/fri.md
PROOF:        Sharpe is reported per 3-year block, and any monotonic decline is stated plainly
TIME:         150 min
BLOCKER IF:   you report a full-sample Sharpe for a calendar effect without the sub-period breakdown
```

### Saturday — Comparison + concept note

```text
🎯 OBJECTIVE:   Write reports/week6-comparison.md and notes/concepts/volatility-estimation.md
WHY:          S09 taught you that the vol estimate drives turnover. That is a general lesson for every later strategy that scales by risk.
INPUT:        strategies/S09,S10,S11
OUTPUT:       reports/week6-comparison.md (3 rows + correlation matrix vs S06/S07)
              notes/concepts/volatility-estimation.md
              notes/daily/week-06/sat.md
PROOF:        the concept note compares close-to-close vs EWMA vs Parkinson vol estimators and states which one S09 uses and why
TIME:         120 min
BLOCKER IF:   the concept note does not state which estimator you chose
```

### Sunday — Journal + ledger

```text
🎯 OBJECTIVE:   Append the Week 6 journal entry and add 3 ledger rows
WHY:          Rows 9, 10, 11. You are two-thirds through the ledger.
INPUT:        strategies/S09..S11 verdicts
OUTPUT:       journal/lessons.md (Week 6 entry), strategy-ledger.md (3 rows)
              notes/daily/week-06/sun.md
PROOF:        3 complete ledger rows; journal entry names which of the three had the best gross-to-net survival
TIME:         60 min
BLOCKER IF:   any ledger row has a blank cell
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Volatility estimation

```text
📐 CONCEPT: Volatility estimators (close-to-close, EWMA, Parkinson, Garman-Klass)
WHY NOW:   S09's turnover is driven entirely by how jumpy your vol estimate is. Your tear sheet
           shows the scaler adding trades, and you cannot fix or evaluate it without knowing which
           estimator is causing the jitter.
FORMULA:   close-to-close: sigma = std(r, ddof=1) * sqrt(252)
           EWMA:           sigma2_t = lambda * sigma2_{t-1} + (1-lambda) * r_t^2,  lambda ~ 0.94
           Parkinson:      sigma = sqrt( (1/(4 ln2)) * mean(ln(H/L)^2) * 252 )
           Garman-Klass:   sigma^2 = 0.5*ln(H/L)^2 - (2ln2 - 1)*ln(C/O)^2
CODE:      cc = r.rolling(63).std(ddof=1) * np.sqrt(252)
           ew = r.ewm(span=63).std() * np.sqrt(252)
           park = np.sqrt((np.log(h/l)**2).rolling(63).mean() / (4*np.log(2)) * 252)
EXAMPLE:   Measure the daily absolute change of each estimator: mean(|d sigma|). The one with the
           highest value generates the most turnover in S09. On your data, close-to-close (63d)
           jumps ~3x more per day than EWMA(0.94) -- which is why S09's turnover is 4x the
           unscaled strategy's. Switching to EWMA should cut the scaler's trades substantially.
TIME:      20 min
NOTE:      write notes/concepts/volatility-estimation.md
DONE WHEN: you can compute all three in 3 lines, explain in 2 sentences why a range-based estimator
           is statistically more efficient than close-to-close, and spot a "volatility" calculated
           with a centered rolling window (look-ahead: it uses tomorrow)
```

### 📐 CONCEPT — Calendar effects and their decay

```text
📐 CONCEPT: Calendar anomalies, publication decay, and capacity
WHY NOW:   Friday's decay test. A calendar effect that worked for 30 years and stopped is not a
           strategy you can trade; it is a historical fact.
FORMULA:   decay test: regress rolling 3-year Sharpe on time; slope < 0 and significant => decaying
           capacity: max_AUM ~ risk_budget / (turnover x impact)
           publication effect: post-publication Sharpe typically ~50% of pre-publication
CODE:      blocks = ret.groupby(ret.index.year // 3 * 3).apply(lambda r: sharpe(r))
           slope = np.polyfit(blocks.index, blocks.values, 1)[0]
           print(f"Sharpe trend per block: {slope:+.3f}")
EXAMPLE:   Turn-of-month on your sample: full-sample Sharpe +0.4, but by 3-year block it is
           +0.9, +0.7, +0.2, -0.1. The full-sample number is an average of an effect that has
           already gone. Report the slope, not the average.
TIME:      15 min
NOTE:      write notes/concepts/calendar-effects-and-decay.md
DONE WHEN: you can compute a rolling-block Sharpe in 3 lines, explain in 2 sentences why a decaying
           effect can still show a positive full-sample Sharpe, and spot a calendar study whose
           sample ends before the effect was published
```

---

## ✅ CHECKPOINT RUBRIC — Week 6 gate

- [ ] 3 strategy folders complete (code, config, tear sheet, verdict)
- [ ] S09 compared against the unscaled underlying, with the scaler's turnover isolated
- [ ] S11 uses open AND close prices, with an overnight/intraday decomposition
- [ ] break-even bps stated for all three
- [ ] `reports/calendar-decay.md` has a sub-period breakdown for S10 and S11
- [ ] `reports/week6-comparison.md` has 3 rows + correlation matrix
- [ ] 7 daily notes, 2 concept notes, 3 strategy notes
- [ ] 3 new complete ledger rows

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **S09:** set the vol estimator to a 5-day close-to-close window. Watch the
>    scaler trade constantly and the costs eat the Sharpe. Log the turnover.
> 2. **S10:** shift the entry by one day (buy on the 1st instead of the last
>    trading day). If the effect vanishes, it was a one-day microstructure
>    artifact, not a month-turn effect.
> 3. **S11:** run it with cost assumptions appropriate to a market-on-open order
>    (wider spread than a close order). Log the break-even.

## Next

Week 7: S12, S13, and the parameter-discipline week — the most important
document of the course.
