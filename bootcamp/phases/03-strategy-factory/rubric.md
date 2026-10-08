# Phase 03 Rubric — Strategy factory (Weeks 5–7)

**Gate:** ≥80/100 AND all 8 strategies shipped (S06–S13).

| # | Criterion | Weight | Check | Score |
|---|---|---|---|---|
| 1 | **8 strategies shipped** | 25 | 8 folders with code + config + tear sheet + verdict | /25 |
| 2 | **Config discipline** | 15 | every config has `lookahead_bars`; embargo respected; no in-place edits | /15 |
| 3 | **Parameter sweep** | 20 | ≥24 configs, manifest, results.csv, plateau-vs-spike | /20 |
| 4 | **Honesty of the sweep report** | 15 | N stated, deflated Sharpe computed, share-vs-benchmark stated | /15 |
| 5 | **Cross-strategy analysis** | 10 | correlation matrices in week5/week6 comparisons | /10 |
| 6 | **Notes + ledger** | 15 | 21 daily, 6 concept, 8 strategy notes; 8 ledger rows | /15 |

**Pass: ≥80/100 AND criterion 1 is perfect.**

---

## Detailed checks

### 1. Eight strategies (25)
- [ ] S06 ts-momentum, S07 xs-momentum, S08 distance pairs
- [ ] S09 vol-target overlay, S10 turn-of-month, S11 gap fade
- [ ] S12 dual momentum, S13 mean-reversion basket
- [ ] each: `strategy.py`, `config.json`, `tearsheet.txt`, `verdict.md`
- [ ] each: costs in bps, OOS with dates, benchmark comparison

### 2. Config discipline (15)
- [ ] `lookahead_bars` declared and correct on every config
- [ ] walk-forward embargo ≥ `lookahead_bars`
- [ ] S08 pairs formed on a window ending before the trading window
- [ ] no config was edited in place after results were seen (check git history)

### 3. Parameter sweep (20)
- [ ] ≥24 configs generated programmatically
- [ ] `manifest.json` records the grid
- [ ] `results.csv`: one row per config, failures recorded not dropped
- [ ] robustness ratio or equivalent plateau-vs-spike diagnostic

### 4. Sweep report honesty (15)
- [ ] N stated explicitly
- [ ] best, median, and deflated Sharpe all reported
- [ ] share of configs beating the benchmark reported
- [ ] at least one parameter shown to be a spike (or an explicit argument for why not)

### 5. Cross-strategy analysis (10)
- [ ] `reports/week5-comparison.md` and `reports/week6-comparison.md` exist
- [ ] correlation matrices included; |rho| > 0.7 pairs flagged as redundant
- [ ] S09 compared like-for-like against the unscaled underlying

### 6. Notes + ledger (15)
- [ ] 21 daily notes, 6 concept notes, 8 strategy notes
- [ ] 8 complete ledger rows (S06–S13)
- [ ] Phase 3 feedback loop answered, citing the sweep

---

## Calibration

**Pass (85):** 8 strategies shipped, configs disciplined, sweep run with 24+
configs, report includes the deflated Sharpe. Correlation matrices present but
thin commentary.

**Pass (100):** all of the above, plus: the sweep report includes the plateau-vs-
spike diagnostic for every swept parameter; at least one *winning* config was
honestly killed in the graveyard; the ledger shows a visible relationship between
turnover and gross-vs-net Sharpe gap that you discuss in the journal; and at
least two strategies were flagged as redundant via correlation.

**Fail (70):** 7 strategies; or configs edited in place; or sweep reports only the
winner; or the sweep has < 24 configs.

**Fail (<60):** fewer than 7 strategies; or no sweep; or the sweep report quotes
the best Sharpe with no adjustment and no N.

---

## The Phase 3 failure mode

**Reporting the winner instead of the distribution.** You will find a config with
a good Sharpe and every instinct will push you to write about that config. The
deliverable is the *distribution* over all configs, and the winner is just one
draw from it. If your Week 7 report reads like an advertisement for one
parameter set, you have failed this phase even if the strategies all shipped.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| 8 strategies shipped | /25 | |
| Config discipline | /15 | |
| Parameter sweep | /20 | |
| Sweep report honesty | /15 | |
| Cross-strategy analysis | /10 | |
| Notes + ledger | /15 | |
| **Total** | **/100** | |

**GATE: PASS / FAIL** — date:
