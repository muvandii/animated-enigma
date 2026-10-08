# Week 1 — Ship one strategy, then kill it with its own numbers

> **Phase 01 · Foundation** · Hours: 12–16 · Strategies: S01, S02
>
> You will spend this week on one strategy. It will probably die. That is the
> designed outcome: Week 1's job is to produce a KILL with a *reason*, not a SHIP
> with a *hope*. Everything after this week is the same loop, run faster.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Ship S01 (MA 10/50 crossover on AAPL) through the full loop and ship S02 (rebuilt) on Saturday
WHY:          Prove to yourself that the loop works end-to-end before you run it 15 more times. The loop, not the strategy, is the deliverable this week.
INPUT:        data/clean/aapl.parquet (from `python fetcher.py AAPL --out data/clean/aapl.parquet`)
OUTPUT:       strategies/S01_ma_crossover/{strategy.py, tearsheet.txt, verdict.md}
              strategies/S02_ma_crossover_filtered/{strategy.py, tearsheet.txt, verdict.md}
              notes/strategies/S01.md, notes/strategies/S02.md
              notes/daily/week-01/{mon,tue,wed,thu,fri,sat,sun}.md
              notes/concepts/{simple-vs-log-returns,transaction-cost-drag}.md
              notes/failures/<date>-S01-costs.md
              graveyard/graveyard.md (row for the killed one)
              journal/lessons.md (Week 1 entry)
PROOF:        `python -m pytest -q` green AND both verdict.md files exist AND both name a cost model in bps AND both report OOS numbers
TIME:         720–960 min across the week
BLOCKER IF:   you cannot fetch ≥1000 bars of AAPL (switch to `python fetcher.py AAPL --source synthetic`), or your net Sharpe exceeds gross Sharpe (that is a bug, stop and find it)
```

**Deliverable of the week, in one sentence:** two strategy folders, each holding
a strategy that runs, a tear sheet with costs and out-of-sample numbers, and a
verdict — plus a graveyard entry with a root cause.

---

## The daily loop

Every day ends with `notes/daily/week-01/<day>.md`, written **that day**, from
`shared/notes-templates/daily-note-template.md`. Backfilled notes do not count.

---

### Monday — Pick it. Write the thesis before the code.

```text
🎯 OBJECTIVE:   Write the S01 thesis and pre-register its kill criteria in notes/strategies/S01.md
WHY:          A strategy whose success criteria are written after the results is not a test, it is a rescue mission. Writing them first is the whole point.
INPUT:        phases/01-foundation/templates/strategy-note-template.md, shared/strategy-ledger.md
OUTPUT:       notes/strategies/S01.md (THESIS, RULES, kill criteria, expected turnover filled; results left blank)
              notes/daily/week-01/mon.md
PROOF:        notes/strategies/S01.md contains a THESIS paragraph naming a causal mechanism, and 4 numeric kill criteria
TIME:         90 min
BLOCKER IF:   your thesis is "it backtested well" — you do not have a thesis yet, go read the thesis() function in examples/week01_ma_crossover.py and try again
```

Do:
1. `python fetcher.py AAPL --out data/clean/aapl.parquet` (fallback: `--source synthetic`).
2. Print 5 rows. Check the date range and that there are no duplicate dates.
3. Write the thesis: *who is on the other side of this trade, and why are they
   willing to lose?*
4. Pre-register kill criteria and **expected turnover** — estimate it from the
   signal's half-life *before* you backtest. A 10/50 crossover on daily bars
   flips roughly 7 times a year; write that down.

---

### Tuesday — Build v0. Ugly, but it runs.

```text
🎯 OBJECTIVE:   Build strategies/S01_ma_crossover/strategy.py that prints a gross tear sheet
WHY:          You cannot diagnose a strategy that does not exist. Gross-only is allowed today and only today.
INPUT:        data/clean/aapl.parquet, backtester.py, metrics.py
OUTPUT:       strategies/S01_ma_crossover/strategy.py
              notes/daily/week-01/tue.md
PROOF:        `python strategies/S01_ma_crossover/strategy.py` prints a tear sheet with n_periods > 1000 and no exception
TIME:         120 min
BLOCKER IF:   the signal is 1.0 (or 0.0) for every bar — your MA warm-up is leaking NaN into a comparison
```

The whole strategy is 6 lines. Resist adding features:

```python
import pandas as pd
from backtester import backtest, CostModel

px = pd.read_parquet("data/clean/aapl.parquet")["adj_close"]
sig = (px.rolling(10).mean() > px.rolling(50).mean()).astype(float)
sig[px.rolling(50).mean().isna()] = 0.0        # warm-up: flat, not "long by accident"
res = backtest(px, sig, cost_model=CostModel(0, 0, 0))   # GROSS, today only
print(res.summary("S01 GROSS"))
```

---

### Wednesday — Backtest it. No filters, no excuses.

```text
🎯 OBJECTIVE:   Run the full-sample gross backtest and write strategies/S01_ma_crossover/tearsheet.txt
WHY:          You need the unvarnished in-sample number on paper so that Thursday's costs have something to destroy.
INPUT:        strategies/S01_ma_crossover/strategy.py, metrics.py
OUTPUT:       strategies/S01_ma_crossover/tearsheet.txt (gross + buy & hold side by side)
              notes/daily/week-01/wed.md
PROOF:        tearsheet.txt contains CAGR, Sharpe, max DD, and the buy & hold comparison, all from metrics.py
TIME:         90 min
BLOCKER IF:   your Sharpe is above 5. Stop. That is look-ahead until proven otherwise — see shared/backtester/test_backtester.py::test_peeking_signal_is_caught_by_an_absurd_sharpe
```

Always print buy & hold next to it. A strategy that makes 4% while the asset
makes 8% is not a strategy, it is a way to underperform with extra steps.

---

### Thursday — Break it.

```text
🎯 OBJECTIVE:   Break S01 with a real cost model and a walk-forward split, and log the damage
WHY:          Gross results are a fantasy. Thursday is the day the fantasy dies, and the failure note is the artifact that proves you were honest about it.
INPUT:        strategies/S01_ma_crossover/strategy.py, backtester.CostModel, backtester.walk_forward_splits
OUTPUT:       strategies/S01_ma_crossover/tearsheet.txt (gross + net + walk-forward table)
              notes/failures/<YYYY-MM-DD>-S01-costs.md
              notes/daily/week-01/thu.md
PROOF:        tearsheet.txt shows gross Sharpe, net Sharpe, total cost paid, and ≥3 walk-forward folds with dates; the failure note names a number
TIME:         120 min
BLOCKER IF:   net Sharpe > gross Sharpe — impossible. You have a sign error in the cost model.
```

Three attacks, in order:
1. **Costs.** `CostModel(fee_bps=1, slippage_bps=5)`. Then re-run at
   `slippage_bps=25` (small-cap) and report where it breaks even.
2. **Out-of-sample.** `walk_forward_splits(px.index, n_splits=5, train_frac=0.6, embargo=5)`.
3. **Turnover.** Print `turnover(res.position) * 252`. If the strategy trades
   more than ~50×/year, at 6 bps round trip it needs to earn 3%/yr *just to pay
   for itself*.

---

### Friday — Diagnose, then learn the concept that explains it.

```text
🎯 OBJECTIVE:   Write notes/concepts/transaction-cost-drag.md and compute S01's break-even edge
WHY:          You now have a number you cannot interpret: gross 0.21 vs net 0.19. Until you can compute the cost drag yourself, you cannot say whether S01 survived or whether the gap is noise.
INPUT:        strategies/S01_ma_crossover/tearsheet.txt, shared/notes-templates/concept-note-template.md
OUTPUT:       notes/concepts/transaction-cost-drag.md
              notes/daily/week-01/fri.md
PROOF:        the note's CODE block runs and reproduces S01's observed cost drag within 10%
TIME:         60 min (20 for the concept, 40 for the note)
BLOCKER IF:   your computed drag and the backtester's `total cost paid` differ by >20% — you have mis-derived the formula; do not write the note yet
```

See 📐 CONCEPT 1 below. Write the note **today**, not on Sunday.

---

### Saturday — Rebuild with the fix. This is S02.

```text
🎯 OBJECTIVE:   Ship S02 by rebuilding S01 with one pre-registered improvement, then run the same three attacks
WHY:          The loop is only real if a diagnosis changes the code. S02 is the measurable proof that Friday's concept mattered.
INPUT:        notes/failures/<date>-S01-costs.md, strategies/S01_ma_crossover/strategy.py
OUTPUT:       strategies/S02_ma_crossover_filtered/{strategy.py, tearsheet.txt, verdict.md}
              notes/strategies/S02.md
              notes/daily/week-01/sat.md
PROOF:        S02's tear sheet shows a different turnover than S01, and the change is traced to one specific rule from the failure note
TIME:         120 min
BLOCKER IF:   S02 differs from S01 in more than one rule — you will not know which change caused the difference, so you learned nothing
```

One change only. The exemplar change: **add a 200-day trend filter** — only take
long signals when price > MA(200). Pre-registered claim: *it removes whipsaw
entries in sideways regimes, cutting turnover by >25% without cutting CAGR by
more than 15%.* Test it. If the claim fails, S02 dies and you say so.

---

### Sunday — Verdict, journal, graveyard, strategy note.

```text
🎯 OBJECTIVE:   Ship both verdicts, bury the dead one, and append the Week 1 journal entry
WHY:          An unwritten verdict is a strategy you will quietly re-litigate for the next 12 weeks. Burial prevents that.
INPUT:        phases/01-foundation/templates/verdict-template.md, shared/journal-template.md, graveyard/graveyard.md
OUTPUT:       strategies/S01_ma_crossover/verdict.md
              strategies/S02_ma_crossover_filtered/verdict.md
              notes/strategies/S01.md + S02.md (results sections filled)
              graveyard/graveyard.md (one row per KILL)
              journal/lessons.md (Week 1 entry, 3 feedback-loop questions answered)
              notes/daily/week-01/sun.md
PROOF:        every KILL has: a verdict.md, a graveyard row with a concept-level root cause, and a failure note dated this week
TIME:         120 min
BLOCKER IF:   a KILL lacks a graveyard row — an unb killed strategy will come back to haunt you in Week 11
```

---

## Deliverables — exact file names

| Artifact | Path |
|---|---|
| S01 strategy | `strategies/S01_ma_crossover/strategy.py` |
| S01 tear sheet | `strategies/S01_ma_crossover/tearsheet.txt` |
| S01 verdict | `strategies/S01_ma_crossover/verdict.md` |
| S02 strategy | `strategies/S02_ma_crossover_filtered/strategy.py` |
| S02 worked example | `examples/week02_ma_crossover_filtered.py` (runs the claim test) |
| S02 tear sheet | `strategies/S02_ma_crossover_filtered/tearsheet.txt` |
| S02 verdict | `strategies/S02_ma_crossover_filtered/verdict.md` |
| Strategy notes | `notes/strategies/S01.md`, `notes/strategies/S02.md` |
| Daily notes (7) | `notes/daily/week-01/{mon,tue,wed,thu,fri,sat,sun}.md` |
| Concept notes (2) | `notes/concepts/transaction-cost-drag.md`, `notes/concepts/simple-vs-log-returns.md` |
| Failure note (≥1) | `notes/failures/<YYYY-MM-DD>-S01-costs.md` |
| Graveyard | `graveyard/graveyard.md` (row per KILL) |
| Journal | `journal/lessons.md` (Week 1 entry) |

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT 1 — Transaction cost drag

```text
📐 CONCEPT: Transaction cost drag
WHY NOW:   strategies/S01_ma_crossover/tearsheet.txt shows gross Sharpe +0.21 and net Sharpe +0.19.
           You cannot say whether S01 survived until you can compute that gap yourself.
FORMULA:   annual_cost_drag = turnover_per_bar × periods_per_year × (fee_bps + slippage_bps) / 10_000
           break-even gross edge = annual_cost_drag
CODE:      from metrics import turnover
           t = turnover(res.position)                       # S01: 0.0274 per bar
           drag = t * 252 * (1 + 5) / 10_000               # 0.00414 -> 0.41%/yr
           print(f"{drag*100:.2f}%/yr, {drag*10*100:.1f}% over 10 years")
EXAMPLE:   S01's turnover is 0.0274/bar => 0.0274 × 252 × 6/10_000 = 0.414%/yr ≈ 4.14% over the
           10-year sample. The backtester's `total cost paid` is 4.14%. They agree, which means
           your cost model is wired correctly. At 25 bps slippage (small-caps) the same turnover
           costs 1.9%/yr — 19% of capital, which is more than S01's entire 3.0% CAGR.
TIME:      20 min
NOTE:      write notes/concepts/transaction-cost-drag.md using Concept Note Template
DONE WHEN: you can code the drag from turnover without looking, explain in 2 sentences why a
           3-day-half-life signal needs a bigger edge than a 30-day one, and spot a cost model
           that forgot abs() (symptom: the strategy's P&L IMPROVES when it trades more)
```

### 📐 CONCEPT 2 — Simple vs log returns

```text
📐 CONCEPT: Simple vs log returns
WHY NOW:   You are about to split S01's 10-year sample into 5 walk-forward folds and compare their
           returns. Summing simple returns across folds gives the wrong total; summing log returns
           gives the right one. This breaks the comparison you are making on Thursday.
FORMULA:   simple: r_t = P_t / P_{t-1} - 1        (compound multiplicatively)
           log:    r_t = ln(P_t / P_{t-1})        (add across time)
           total simple return = Π(1 + r_t) - 1 ≠ Σ r_t
           total log return    = Σ r_t  ;  convert back with exp(Σ) - 1
CODE:      p = px.iloc[:4]                                  # 102.58, 98.31, 99.64, 99.75
           s = p.pct_change().dropna(); l = np.log(p/p.shift(1)).dropna()
           print(s.sum(), np.expm1(l.sum()), p.iloc[-1]/p.iloc[0]-1)
EXAMPLE:   For AAPL's first three steps: Σ simple = -2.7011%, but the true move is -2.7605%.
           Σ log = -2.7993%, and expm1(-2.7993%) = -2.7605% — exactly right.
           Report simple returns to humans. Use log returns only for math, never in a verdict.
TIME:      15 min
NOTE:      write notes/concepts/simple-vs-log-returns.md using Concept Note Template
DONE WHEN: you can convert between them in 3 lines, explain in 2 sentences why log returns add but
           simple returns do not, and spot the bug where someone computes a portfolio return by
           averaging simple returns across assets (correct: average the log returns, or compound)
```

---

## Note prompts

Write these **the day they are listed**. The note is the assessment; the code is
just how you earn the right to write it.

| Note | Template | Due | Prompt |
|---|---|---|---|
| `notes/daily/week-01/*.md` (7) | daily-note-template | same day | What did you build, what broke, what's tomorrow's first move? |
| `notes/concepts/transaction-cost-drag.md` | concept-note-template | Fri | Derive the drag formula, then check it against S01's 4.14%. |
| `notes/concepts/simple-vs-log-returns.md` | concept-note-template | Fri | Why does `sum()` lie for one and not the other? |
| `notes/strategies/S01.md` | strategy-note-template | Mon (thesis) + Sun (results) | Fill PRE-REGISTRATION on Monday. Do not edit it after Tuesday. |
| `notes/strategies/S02.md` | strategy-note-template | Sat | Name the single change from S01 and the pre-registered claim. |
| `notes/failures/<date>-S01-costs.md` | failure-note-template | Thu | Root cause must name a concept, not a feeling. |

Every note must pass the 4 criteria: **specific, same-day, self-contained, has a
forward action.**

---

## ✅ CHECKPOINT RUBRIC — Week 1 gate

Pass/fail. Every box or the week does not count.

**Artifacts**
- [ ] `strategies/S01_ma_crossover/strategy.py` runs end to end on ≥1000 bars
- [ ] `strategies/S01_ma_crossover/tearsheet.txt` has gross, net, AND buy & hold
- [ ] `strategies/S02_ma_crossover_filtered/` has all three artifacts
- [ ] S02's change from S01 is traced to ONE pre-registered claim, tested against numbers
- [ ] Both `verdict.md` files filled **including the WHY section in sentences**

**Mandatory strategy content (all three, both strategies)**
- [ ] runs on real (or seeded-synthetic) data
- [ ] fees **and** slippage modeled, stated in bps
- [ ] out-of-sample results with **explicit date ranges**

**Notes**
- [ ] 7 daily notes in `notes/daily/week-01/`
- [ ] 2 concept notes, each passing the DONE WHEN three-part test
- [ ] 2 strategy notes with the PRE-REGISTRATION block filled *before* results
- [ ] ≥1 failure note, dated the day of the failure
- [ ] `journal/lessons.md` Week 1 entry with all three feedback-loop questions

**Graveyard**
- [ ] Every KILL has a row in `graveyard/graveyard.md`
- [ ] Root cause names a **concept** (costs / no OOS stability / look-ahead /
      survivorship / leverage artifact) — not "needs more tuning"

**Proof of learning (at least one, measurable)**
- [ ] You can recompute one number from your tear sheet by hand and match the
      backtester within 10% (e.g. cost drag from turnover)
- [ ] OR you caught a bug in your own code this week and can point to the commit
- [ ] OR your OOS result changed a decision you had already made

**Sanity**
- [ ] `python -m pytest -q` is green
- [ ] No Sharpe above 5 anywhere in your artifacts

**GATE: PASS / FAIL** — if FAIL, name the missing boxes and fix them before
opening `week-02.md`. Do not carry a failed gate forward; it compounds.

---

## ⚰️ GRAVEYARD PROMPT — Week 1

The graveyard is required and structured. This week's prompt:

> **Break S01 on purpose, three ways, and log each one.**
>
> 1. **Cost attack.** Re-run S01 at 0, 5, 25, and 100 bps of slippage. At what
>    level does net CAGR cross zero? Log the number.
> 2. **Regime attack.** Split the sample at the median date. Report Sharpe in
>    each half. If the halves disagree in sign, the "edge" is period-dependent.
> 3. **Look-ahead attack.** Add `.shift(-1)` to the signal (i.e. peek at
>    tomorrow) and re-run. Record the Sharpe you get. That number is what
>    self-deception looks like; memorize its magnitude so you recognize it later.
>
> For each attack: a row in `graveyard/graveyard.md` (or a note if the strategy
> died), a failure note if it produced a real diagnosis, and the number in
> `tearsheet.txt`.

Expectation: attack 3 will produce a Sharpe above 10. When it does, you have
learned the single most valuable lesson of this course for the price of one
afternoon.

> **Worked S02 outcome (so you know what a failed rebuild looks like):**
> the trend filter *increased* trades from 69 to 95 and cut CAGR from +3.04% to
> +0.69%. Both pre-registered claims failed. S02 is KILLED. This is a pass —
> the artifact is the diagnosis, not a better Sharpe.

---

## ▶️ COMPLETED EXAMPLE — S01 run end to end

This is a real run. `python phases/01-foundation/examples/week01_ma_crossover.py --offline`
reproduces it exactly (seeded synthetic twin of AAPL; your live AAPL numbers will
differ — that is fine, the *shape* of the argument is what you are copying).

### The strategy (6 lines that matter)

```python
def signal(prices, fast=10, slow=50):
    ma_fast = prices.rolling(fast).mean()
    ma_slow = prices.rolling(slow).mean()
    out = (ma_fast > ma_slow).astype(float)
    out[ma_slow.isna()] = 0.0        # warm-up: flat, not "long by accident"
    return out

res = backtest(px, signal(px), cost_model=CostModel(fee_bps=1.0, slippage_bps=5.0))
```

### Output (abridged; full file: `examples/s01_tearsheet.txt`)

```
==============================================
         GROSS  (no costs)  MA 10/50
==============================================
  periods              2520   (10.00 yrs)
  total return        40.57%
  CAGR                 3.46%
  ann. vol            16.26%
  Sharpe               0.21
  Sortino              0.16
  max drawdown       -31.31%
  Calmar               0.11
  hit rate            50.15%
  turnover/day         0.03
  best / worst day     5.13% /    -4.44%
  trades                  69
  total cost paid      0.00%
  gross Sharpe          0.21
  cost model            0+0 bps
==============================================

==============================================
           NET (1+5 bps)  MA 10/50
==============================================
  periods              2520   (10.00 yrs)
  total return        34.87%
  CAGR                 3.04%
  ann. vol            16.26%
  Sharpe               0.19
  Sortino              0.14
  max drawdown       -31.72%
  Calmar               0.10
  hit rate            48.81%
  turnover/day         0.03
  trades                  69
  total cost paid      4.14%
  gross Sharpe          0.21
  cost model        1.0+5.0 bps
==============================================

==============================================
            BENCHMARK  buy & hold
==============================================
  total return       116.86%
  CAGR                 8.05%
  ann. vol            22.01%
  Sharpe               0.37
  max drawdown       -41.94%
  trades                   1
==============================================

  WALK-FORWARD  (5 folds, 60% train, 5-bar embargo)
 fold test_start   test_end  strat_sharpe  strat_cagr  bh_cagr  max_dd  trades
    1 2021-01-15 2021-11-02         -1.74       -24.0    -16.5   -19.7       8
    2 2021-11-03 2022-08-23          1.90        37.6     36.7    -7.5       3
    3 2022-08-24 2023-06-13          0.18         3.2     21.9   -17.9       9
    4 2023-06-14 2024-04-03         -0.52        -8.6     -2.4   -16.9       5
    5 2024-04-04 2025-01-23          0.58         9.9     36.8   -24.2       7

  folds where strategy beat buy & hold (CAGR): 1/5
  mean out-of-sample Sharpe: +0.08   (in-sample net Sharpe: +0.19)

  VERDICT: KILL
  beats buy & hold net of costs : NO   (+3.0% vs +8.0% CAGR)
  survives costs                : Sharpe +0.21 gross -> +0.19 net
  out-of-sample Sharpe          : +0.08 vs +0.19 in-sample
  total cost paid               : 4.1% of capital over 69 trades
```

### Reading this output correctly

Three facts, in order of importance:

1. **It lost to doing nothing.** +3.0% vs +8.0% CAGR. The strategy's *only*
   achievement was cutting volatility from 22.0% to 16.3% — and it was paid for
   with 5 points of annual return.
2. **Costs were NOT the killer** (0.21 → 0.19). This matters: the correct
   diagnosis is *the signal does not have an edge*, not *the signal is too
   expensive*. Do not write the wrong failure note.
3. **Out-of-sample is worse than in-sample** (0.08 vs 0.19), and the fold
   results swing from -1.74 to +1.90. That spread is the real finding: with ~7
   trades/year, you have 69 observations total. The 95% CI on that Sharpe is
   roughly ±0.24 — wider than the entire point estimate.

### The verdict file (abridged; full: `examples/s01_verdict.md`)

```markdown
# VERDICT — S01 MA(10/50) crossover on AAPL

STATUS:      KILL

## Results (net of costs, 10.0 yrs)
| metric | strategy | buy & hold |
|---|---|---|
| CAGR | +3.04% | +8.05% |
| Sharpe | +0.19 | +0.37 |
| max DD | -31.72% | -41.94% |
| ann. vol | 16.26% | 22.01% |

- gross Sharpe (zero costs): +0.21  ->  net: +0.19
- total cost paid: 4.1% of capital over 69 trades

## Decision
- Beats buy & hold net of costs? **NO**
- Meets the viability bar (Sharpe > 0.5 and CAGR > 0)? **NO**
- VERDICT: **KILL**

## Why (3 sentences, no hedging)
The crossover cut volatility versus buy & hold but gave up most of the return,
so net of costs it lost to simply holding the asset. Costs removed 0.03 of
Sharpe across 69 trades, and the out-of-sample folds degraded versus in-sample,
which means the edge (if any) is fragile to period choice.

## What I'd try next (max 2, each must be a new testable claim)
1. Add a trend filter (only take long signals above the 200-day MA) -- claim:
   it removes the whipsaw trades in sideways regimes.
2. Test on a 5-symbol universe -- claim: if this is a real trend effect it
   should show up on more than one asset.
```

### Sample notes this run produces

**`notes/daily/week-01/thu.md`**
```markdown
# 2025-01-16 — Week 1 · Thu

BUILT:
- strategies/S01_ma_crossover/strategy.py (added CostModel + walk_forward_splits)
- strategies/S01_ma_crossover/tearsheet.txt (gross + net + 5 folds)

BROKE:
- S01 net CAGR 3.04% vs buy & hold 8.05%. It loses.
- Fold 1 Sharpe -1.74, fold 2 Sharpe +1.90. Same strategy, same params, 4 months apart.

LEARNED:
Costs were only 0.03 of Sharpe. My pre-registered guess was that costs would
kill it, and I was wrong — the signal simply has no edge. Turnover is 7/yr,
which is far too low for costs to matter.

QUESTION I STILL HAVE:
With 69 trades, what is the confidence interval on Sharpe 0.19? If it is
±0.24 then I cannot distinguish this from zero, and "KILL" should really read
"unmeasurable".

TOMORROW'S FIRST MOVE:
python -c "import numpy as np; print(np.sqrt((1+0.19**2/2)/69))"  # SE of Sharpe
```

**`notes/failures/2025-01-16-S01-costs.md`**
```markdown
# Failure: S01 loses to buy & hold net of costs

DATE: 2025-01-16
STRATEGY: S01 MA(10/50) crossover

WHAT BROKE:
Net CAGR 3.04% vs buy & hold 8.05%. Net Sharpe 0.19 vs 0.37. It lost.

ROOT CAUSE:
Wrong hypothesis. I predicted cost drag would kill it; costs only removed 0.03
of Sharpe. The actual mechanism: MA crossovers are always late. The 10/50 cross
fires after ~15% of the move has already happened, so the strategy buys high and
sells low relative to a buy-and-hold holder, and in a market with a +8% drift
being out of the market 40% of the time costs more than the drawdowns avoid.
Volatility fell (22.0% -> 16.3%) but so did return, roughly proportionally.

CONCEPT THAT EXPLAINS IT:
Signal lag in a drifting market + opportunity cost of time out of market.
A trend filter does not remove it; it increases it.

FIX ATTEMPTED:
S02: added a 200-day trend filter (price > MA200 required to go long).
Pre-registered claim: trades -25% or more, CAGR -15% or less.
See examples/week02_ma_crossover_filtered.py (run it; it prints the claim test).

DID FIX WORK: NO — and it failed in a way I did not predict.
  trades : 69 -> 95   (+38%)        claimed <= -25%   FAIL
  CAGR   : +3.04% -> +0.69%  (-77%) claimed >= -15%   FAIL
  Sharpe : +0.19 -> +0.05
  time in market: 52.0% -> 36.1%
Trade count went UP, not down. AND-ing two binary conditions sums their
TRANSITIONS: the 200-day filter adds its own crossings instead of only
deleting S01's entries. And the exposure it removed was in a market
drifting +8%/yr, so the days out were better than average, not worse.

LESSON:
Before blaming costs, print turnover. Under 20 trades a year, costs are not
your problem — the signal is. And a "filter" is not free: it trades too.
```

**`notes/concepts/transaction-cost-drag.md`**
```markdown
# Concept: transaction cost drag

WHEN I LEARNED IT: 2025-01-17 — while S01's net Sharpe (0.19) refused to
diverge from its gross Sharpe (0.21) and I needed to know if that gap was real.

DEFINITION (2 sentences):
Cost drag is the expected annual return consumed by trading, equal to the
fraction of the portfolio you trade per year multiplied by the round-trip cost
per unit traded. It converts a gross forecast into a net one, and it scales
linearly with turnover — so high-frequency signals need proportionally larger
edges.

FORMULA:
annual_drag = turnover_per_bar × periods_per_year × (fee_bps + slippage_bps) / 10_000

CODE (3-5 lines):
from metrics import turnover
t = turnover(res.position)                    # S01: 0.0274
print(t * 252 * 6 / 10_000)                   # 0.00414 -> 0.41%/yr

WHERE IT LIES / LIMITS:
It assumes linear impact (true for small size, false once you move the book),
ignores the bid-ask bounce in your price data, and assumes you can always trade
at the close. For large positions the real cost is market impact, which is
superlinear in size and invisible in a backtest.

HOW I'D SPOT IT WRONG IN SOMEONE ELSE'S CODE:
No abs() on the position delta — then sells generate negative cost and the
strategy's P&L IMPROVES as it trades more. Symptom: net Sharpe > gross Sharpe.

APPLIED TO:
- S01: turnover 0.0274/bar → 0.41%/yr → 4.14% over 10 years. Backtester's
  `total cost paid` = 4.14%. Model verified.
- S02: turnover 0.019/bar → 0.29%/yr.
```

---

## Next

Week 2: three strategies, one per day, same loop. `week-02.md`.
Do not open it until Week 1's gate passes.
