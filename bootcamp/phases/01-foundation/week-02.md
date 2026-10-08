# Week 2 — Three strategies, one per day, same loop

> **Phase 01 · Foundation** · Hours: 14–18 · Strategies: S03, S04, S05
>
> Last week you spent seven days on one strategy. This week you spend one day
> per strategy. The loop is identical; only the clock changes. If the loop feels
> slow, you did not internalize it last week — go back and read `week-01.md`
> before you speed up.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Ship S03 (RSI-2 reversal), S04 (Bollinger reversion), and S05 (Donchian breakout) through the full loop, each in one day
WHY:          Three independent mechanisms in three days proves the loop is a tool, not a ritual. It also produces the first real sample for the question "what pattern kills strategies?"
INPUT:        data/clean/*.parquet (≥3 symbols; add SPY, QQQ, IWM), strategies/S01_*/verdict.md, notes/failures/ from Week 1
OUTPUT:       strategies/S03_rsi2_reversal/{strategy.py,tearsheet.txt,verdict.md}
              strategies/S04_bollinger_reversion/{strategy.py,tearsheet.txt,verdict.md}
              strategies/S05_donchian_breakout/{strategy.py,tearsheet.txt,verdict.md}
              notes/strategies/{S03,S04,S05}.md
              notes/daily/week-02/{mon,tue,wed,thu,fri,sat,sun}.md
              notes/concepts/{stationarity-mean-reversion,multiple-comparisons}.md
              notes/failures/<date>-S0{3,4,5}-*.md  (>=2)
              graveyard/graveyard.md (+3 rows)
              journal/lessons.md (Week 2 entry, WITH Phase 1 feedback-loop answers)
PROOF:        three verdict.md files, each with a cost model in bps + OOS dates + a WHY section; `python -m pytest -q` green
TIME:         840–1080 min
BLOCKER IF:   you run out of week before all three are shipped — ship two properly rather than three badly, and take the gate failure honestly
```

**Multi-symbol rule (new this week):** S03 and S04 run on a **3-symbol
universe** (AAPL, SPY, IWM). S05 runs on a **5-symbol universe**. A strategy
that only works on one ticker is a story about one ticker.

---

## The daily loop

| Day | S03 RSI-2 | S04 Bollinger | S05 Donchian |
|---|---|---|---|
| Mon | thesis + universe fetch | | |
| Tue | build + gross backtest | | |
| Wed | break it (costs, OOS) | thesis + build | |
| Thu | verdict + note | break it | thesis + build |
| Fri | | verdict + note | break it |
| Sat | | | verdict + note |
| Sun | journal, graveyard, Phase 1 feedback loop | | |

Offset deliberately: while one strategy is in the "break it" phase, the next is
being built. This is the rhythm from Week 5 onward.

---

### Monday — S03 thesis + fetch the universe

```text
🎯 OBJECTIVE:   Write the S03 thesis with pre-registered kill criteria, and fetch a 3-symbol universe
WHY:          RSI-2 is a mean-reversion bet, and mean reversion has a specific precondition (bounded/mean-reverting price process) that you must state before you can test it.
INPUT:        phases/01-foundation/templates/strategy-note-template.md
OUTPUT:       notes/strategies/S03.md (pre-registration block filled)
              data/clean/{aapl,spy,iwm}.parquet
              notes/daily/week-02/mon.md
PROOF:        `python fetcher.py SPY --out data/clean/spy.parquet` succeeds; all three parquet files have aligned, duplicate-free date indexes
TIME:         90 min
BLOCKER IF:   the three symbols have different date ranges — align on the intersection and record how many bars you lost
```

### Tuesday — Build S03 + gross backtest

```text
🎯 OBJECTIVE:   Build strategies/S03_rsi2_reversal/strategy.py and print the gross tear sheet for all 3 symbols
WHY:          RSI-2 is the highest-turnover signal you will build. Its gross number tells you nothing and its net number tells you everything, so you need both on paper before Thursday.
INPUT:        data/clean/{aapl,spy,iwm}.parquet
OUTPUT:       strategies/S03_rsi2_reversal/strategy.py
              strategies/S03_rsi2_reversal/tearsheet.txt (gross, 3 symbols)
              notes/daily/week-02/tue.md
PROOF:        strategy.py prints three gross tear sheets; turnover/yr is reported per symbol BEFORE costs
TIME:         120 min
BLOCKER IF:   turnover/yr is under 20 — you built RSI-2 wrong; a 2-period RSI flips constantly
```

```python
def rsi(close, n=2):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def signal_s03(close, n=2, entry=10, exit_thr=50):
    r = rsi(close, n)
    pos = pd.Series(0.0, index=close.index)
    long = False
    for i in range(1, len(close)):                 # loop: stateful exit rule
        if not long and r.iloc[i-1] < entry:
            long = True
        elif long and r.iloc[i-1] > exit_thr:
            long = False
        pos.iloc[i] = 1.0 if long else 0.0
    return pos
```

> The `for` loop is deliberate: RSI-2's exit is **stateful** (hold until RSI
> recovers to 50), which a vectorized `.where()` expresses badly. Ugly and
> correct beats elegant and wrong. Keep the loop.

### Wednesday — Break S03; thesis and build S04

```text
🎯 OBJECTIVE:   Add costs and walk-forward to S03, and build S04 (Bollinger reversion) v0
WHY:          S03 is the strategy most likely to be destroyed by costs (turnover 100+/yr), so it is the cleanest demonstration of the cost-drag concept you learned Friday.
INPUT:        strategies/S03_rsi2_reversal/strategy.py, backtester.CostModel
OUTPUT:       strategies/S03_rsi2_reversal/tearsheet.txt (net + OOS added)
              notes/failures/<date>-S03-costs.md
              strategies/S04_bollinger_reversion/strategy.py
              notes/strategies/S04.md (pre-registration filled)
              notes/daily/week-02/wed.md
PROOF:        S03's tear sheet shows net Sharpe below gross Sharpe; the failure note states the bps level at which net CAGR crosses zero
TIME:         150 min
BLOCKER IF:   S03's net Sharpe is within 0.05 of its gross Sharpe while turnover > 100/yr — the cost model is not being applied
```

### Thursday — S03 verdict; break S04; thesis and build S05

```text
🎯 OBJECTIVE:   Ship S03's verdict, break S04 with costs and OOS, and build S05 (Donchian breakout) v0
WHY:          Three strategies in three states at once is the steady-state rhythm of this course. Learn to hold it now, at low stakes.
INPUT:        strategies/S03_rsi2_reversal/tearsheet.txt, strategies/S04_bollinger_reversion/strategy.py
OUTPUT:       strategies/S03_rsi2_reversal/verdict.md
              notes/strategies/S03.md (results filled)
              graveyard/graveyard.md (S03 row if KILL)
              strategies/S04_bollinger_reversion/tearsheet.txt (net + OOS)
              strategies/S05_donchian_breakout/strategy.py
              notes/strategies/S05.md (pre-registration filled)
              notes/daily/week-02/thu.md
PROOF:        S03 has a verdict; S04 has net + OOS numbers; S05 has a thesis written before code
TIME:         150 min
BLOCKER IF:   you write S05's thesis after seeing its results
```

### Friday — S04 verdict; break S05; write the multiple-comparisons concept note

```text
🎯 OBJECTIVE:   Ship S04's verdict, break S05, and write notes/concepts/multiple-comparisons.md
WHY:          You have now tested 5 strategies. The probability that at least one looks good by chance is no longer small, and you cannot interpret a single verdict without accounting for it.
INPUT:        strategies/S04_bollinger_reversion/tearsheet.txt, strategies/S05_donchian_breakout/strategy.py, shared/notes-templates/concept-note-template.md
OUTPUT:       strategies/S04_bollinger_reversion/verdict.md
              notes/strategies/S04.md (results filled)
              graveyard/graveyard.md (S04 row)
              strategies/S05_donchian_breakout/tearsheet.txt (net + OOS)
              notes/concepts/multiple-comparisons.md
              notes/daily/week-02/fri.md
PROOF:        the concept note computes the expected max Sharpe across N independent trials and states the adjusted bar for N=5
TIME:         150 min
BLOCKER IF:   you report a single strategy's Sharpe without stating how many strategies you tested to find it
```

### Saturday — S05 verdict; reconcile all five

```text
🎯 OBJECTIVE:   Ship S05's verdict and build reports/phase1-summary.md comparing S01–S05 in one table
WHY:          Five verdicts in five files is not knowledge. One table with all five is where the pattern becomes visible.
INPUT:        strategies/S0{1..5}_*/verdict.md, strategy-ledger.md
OUTPUT:       strategies/S05_donchian_breakout/verdict.md
              notes/strategies/S05.md (results filled)
              graveyard/graveyard.md (S05 row)
              reports/phase1-summary.md (one table: gross Sharpe, net Sharpe, OOS Sharpe, turnover, verdict, killed-by)
              notes/daily/week-02/sat.md
PROOF:        reports/phase1-summary.md has 5 rows and the gross-vs-net Sharpe gap computed for each
TIME:         120 min
BLOCKER IF:   any row is missing a number — fill it or mark it N/A with a reason, never leave it blank
```

### Sunday — Journal, graveyard, Phase 1 gate

```text
🎯 OBJECTIVE:   Answer the three feedback-loop questions in journal/lessons.md and self-grade against phases/01-foundation/rubric.md
WHY:          Phase 1 ends today. The gate is not "did you build 5 strategies" — it is "can you say what killed them, mechanically, and what you will do differently."
INPUT:        reports/phase1-summary.md, graveyard/graveyard.md, notes/**
OUTPUT:       journal/lessons.md (Week 2 entry + Phase 1 feedback-loop answers)
              graveyard/graveyard.md (complete, >=4 rows)
              notes/daily/week-02/sun.md
PROOF:        all three feedback-loop questions answered in prose with numbers cited; Phase 1 rubric self-graded
TIME:         120 min
BLOCKER IF:   fewer than 4 graveyard rows — if 4 of 5 strategies did not die, you did not break them hard enough
```

---

## Deliverables — exact file names

| Artifact | Path |
|---|---|
| S03 | `strategies/S03_rsi2_reversal/{strategy.py, tearsheet.txt, verdict.md}` |
| S04 | `strategies/S04_bollinger_reversion/{strategy.py, tearsheet.txt, verdict.md}` |
| S05 | `strategies/S05_donchian_breakout/{strategy.py, tearsheet.txt, verdict.md}` |
| Strategy notes | `notes/strategies/{S03,S04,S05}.md` |
| Daily notes (7) | `notes/daily/week-02/{mon,tue,wed,thu,fri,sat,sun}.md` |
| Concept notes (2) | `notes/concepts/stationarity-mean-reversion.md`, `notes/concepts/multiple-comparisons.md` |
| Failure notes (≥2) | `notes/failures/<date>-S03-costs.md`, `<date>-S04-*.md`, … |
| Phase summary | `reports/phase1-summary.md` |
| Graveyard | `graveyard/graveyard.md` |
| Journal | `journal/lessons.md` |

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT 1 — Stationarity and why mean reversion needs it

```text
📐 CONCEPT: Stationarity / mean-reverting vs trending processes
WHY NOW:   S03 and S04 both bet that price returns to a level. That bet is only coherent if the
           process actually reverts. You are about to measure whether it does; without this
           concept you will read the result as "RSI-2 works/doesn't work" instead of "this
           instrument reverts on a 2-day horizon in this regime".
FORMULA:   AR(1): x_t = phi * x_{t-1} + e_t
           |phi| < 1  -> mean-reverting (stationary); half-life = -ln(2)/ln(phi)
           phi ~= 1   -> random walk (no predictable reversion)
           Variance ratio: VR(q) = Var(x_t - x_{t-q}) / (q * Var(x_t - x_{t-1}));  VR < 1 = reversion
CODE:      import numpy as np
           x = np.diff(np.log(px.to_numpy()))
           phi = np.polyfit(x[:-1], x[1:], 1)[0]              # lag-1 autocorrelation
           print(phi, -np.log(2)/np.log(phi) if 0 < phi < 1 else "no reversion")
EXAMPLE:   Run it on SPY daily returns: phi ~ -0.05, i.e. mild reversion with a half-life under a
           day -- which means RSI-2's 2-day holding period is ALREADY past the reversion
           horizon. That is a prediction you can test on Thursday: if phi < 0, RSI-2's edge
           should be concentrated in the first day after entry, not days 2-5.
TIME:      20 min
NOTE:      write notes/concepts/stationarity-mean-reversion.md using Concept Note Template
DONE WHEN: you can estimate phi and a half-life in 3 lines, explain in 2 sentences why a
           trending series makes mean-reversion rules lose money, and spot the bug where someone
           computes autocorrelation on PRICE levels (always returns ~0.99, tells you nothing)
```

### 📐 CONCEPT 2 — Multiple comparisons

```text
📐 CONCEPT: Multiple comparisons / the winner's curse
WHY NOW:   You have now tested 5 strategies. If you report the best Sharpe among 5 independent
           tries as if it were the result of one try, you are reporting a biased number upward.
           The bar for "this looks real" rises with the number of things you tried.
FORMULA:   P(at least one of N independent trials beats threshold by chance) = 1 - (1 - p)^N
           Expected max Sharpe across N trials grows ~ sqrt(2 ln N) above the single-trial mean.
           Deflated Sharpe (simplified): SR_adj ~= SR_obs - sqrt(2 ln N) / sqrt(T/252)
CODE:      import numpy as np
           N, T = 5, 2520                                    # 5 strategies, 10 yrs
           adj = np.sqrt(2*np.log(N)) / np.sqrt(T/252)
           print(f"subtract ~{adj:.2f} from your best Sharpe before believing it")
EXAMPLE:   Best net Sharpe across S01-S05 = 0.19. N=5, T=2520 -> subtract ~0.18.
           Adjusted: 0.01. Your best strategy is statistically indistinguishable from zero.
           This is the honest headline for reports/phase1-summary.md.
TIME:      20 min
NOTE:      write notes/concepts/multiple-comparisons.md using Concept Note Template
DONE WHEN: you can compute the adjustment in 3 lines, explain in 2 sentences why testing more
           strategies RAISES the bar rather than lowering it, and spot the report that quotes the
           best of 40 parameter sets as "the strategy's Sharpe"
```

---

## Note prompts

| Note | Template | Due | Prompt |
|---|---|---|---|
| `notes/daily/week-02/*.md` (7) | daily-note-template | same day | Same four fields. Be specific. |
| `notes/concepts/stationarity-mean-reversion.md` | concept-note-template | Wed | Estimate phi for each of your 3 symbols. Do they differ? |
| `notes/concepts/multiple-comparisons.md` | concept-note-template | Fri | Compute the adjusted Sharpe for your best strategy. |
| `notes/strategies/{S03,S04,S05}.md` | strategy-note-template | before code | Pre-registration first, results after. |
| `notes/failures/<date>-S03-costs.md` | failure-note-template | Wed | At what bps does net CAGR cross zero? |
| `notes/failures/<date>-S0{4,5}-*.md` | failure-note-template | as found | Root cause must name a concept. |

---

## ✅ CHECKPOINT RUBRIC — Week 2 gate (also the Phase 1 gate)

**Artifacts**
- [ ] 3 strategy folders, each with `strategy.py`, `tearsheet.txt`, `verdict.md`
- [ ] S03 + S04 run on ≥3 symbols; S05 runs on ≥5 symbols
- [ ] `reports/phase1-summary.md` with all 5 strategies in one table
- [ ] Every verdict has costs **and** OOS dates **and** a WHY section

**Strategy content (all three)**
- [ ] runs on real (or seeded-synthetic) data
- [ ] fees **and** slippage in bps, stated in the verdict
- [ ] out-of-sample results with explicit date ranges
- [ ] turnover reported per strategy

**Notes**
- [ ] 7 daily notes
- [ ] 2 concept notes passing DONE WHEN
- [ ] 3 strategy notes, pre-registration filled before results
- [ ] ≥2 failure notes, same-day
- [ ] `journal/lessons.md` Week 2 entry + Phase 1 feedback-loop answers

**Graveyard**
- [ ] ≥4 rows total across Phase 1
- [ ] Root causes name concepts, not feelings

**Multi-symbol honesty**
- [ ] For any strategy that worked on one symbol, you report the other symbols too
- [ ] No strategy is reported only on its best symbol

**GATE: PASS / FAIL**

---

## ⚰️ GRAVEYARD PROMPT — Week 2

> **Find the cheapest way to kill each strategy.**
>
> 1. **S03 (RSI-2):** sweep slippage 0 → 10 → 25 → 50 bps. Plot is optional; the
>    number you want is the break-even bps. Then compute the same strategy's
>    Sharpe on SPY and IWM. If it only works on AAPL, say so out loud.
> 2. **S04 (Bollinger):** the entry is `price < lower_band`. Break it by holding
>    for a fixed 5 days instead of until reversion to the mid-band. If the
>    result changes sign, your exit rule was doing all the work.
> 3. **S05 (Donchian):** breakout strategies live or die on ONE month in a
>    decade. Find the single best and single worst month in your sample, remove
>    each in turn, and report the Sharpe both ways. If removing one month kills
>    it, the strategy is one month.
>
> Log all three. Rows in `graveyard/graveyard.md`, failure notes dated the day.

---

## ▶️ SAMPLE OUTPUT — what the Phase 1 summary table looks like

Fill yours in with real numbers. Structure is what matters:

| ID | Strategy | Universe | Trades/yr | Gross SR | Net SR | OOS SR | Turnover cost/yr | Verdict | Killed by |
|---|---|---|---|---|---|---|---|---|---|
| S01 | MA(10/50) | AAPL | 7 | +0.21 | +0.19 | +0.08 | 0.41% | KILL | lags a drifting market; loses to buy & hold |
| S02 | MA + MA200 | AAPL | 10 | +0.07 | +0.05 | −0.17 | 0.57% | KILL | filter added trades; time out of market cost return |
| S03 | RSI-2 reversal | AAPL/SPY/IWM | 118 | +0.94 | −0.21 | −0.34 | 7.1% | KILL | costs: needs ~60bps/trade to break even |
| S04 | Bollinger reversion | AAPL/SPY/IWM | 64 | +0.55 | +0.22 | +0.11 | 3.8% | KILL | exit rule did all the work; OOS halves |
| S05 | Donchian(20/10) | 5 symbols | 22 | +0.61 | +0.48 | +0.41 | 1.3% | **SHIP (paper)** | — |

**The lesson this table teaches** (yours will differ; the shape usually does not):

- S03 has the best gross Sharpe in the phase and the worst net Sharpe. Gross
  Sharpe is not evidence.
- The **gross-vs-net gap** correlates almost perfectly with turnover. Sort your
  table by `Trades/yr` and the gap column will be monotonic.
- Of 5 strategies, 1 survived. At N=5, expect about that by chance alone. That
  is not cynicism, it is the multiple-comparisons math you wrote a note about on
  Friday.

### Sample graveyard rows

| ID | NAME | DATE KILLED | KILLED BY | ROOT CAUSE (concept) | LESSON CARRIED FORWARD |
|---|---|---|---|---|---|
| S01 | MA(10/50) | 2025-01-19 | underperforms buy & hold | signal lag in a drifting market | always print B&H beside the strategy |
| S02 | MA + MA200 | 2025-01-19 | filter added trades, cut return | AND-ing signals sums their transitions | a filter trades too; measure its turnover |
| S03 | RSI-2 | 2025-01-22 | net CAGR negative at 6bps | cost drag ∝ turnover | compute turnover BEFORE backtesting |
| S04 | Bollinger | 2025-01-24 | OOS Sharpe 50% of IS; exit-dependent | overfitting the exit rule | hold for a fixed window as the null test |

### Sample Phase 1 journal entry (feedback loop)

```markdown
## Week 2 — Foundation

Hours: 17.  Shipped: S03, S04, S05.  Killed: S01, S02, S03, S04.

**1. What pattern killed most strategies?**
Turnover, and my blindness to it until after the fact. S03 had the best gross
Sharpe of the phase (+0.94) and the worst net (-0.21). The gap is 1.15 of
Sharpe, entirely explained by 118 trades/yr at 6bps = 7.1%/yr of drag. I built
a signal with a 2-day half-life and costed it like a signal with a 30-day
half-life. Every strategy I built has the same flaw in miniature: I choose the
lookback for signal quality and never check what it does to turnover.

**2. Which concept made the biggest difference?**
Cost drag as turnover × cost, computed BEFORE the backtest. It changed my
process: I now estimate turnover from the signal's half-life on Monday and
abandon anything whose annual cost exceeds half the expected edge. That single
rule would have saved me S03 and S04.

**3. What am I still fooling myself about?**
That S05 "works." It has a net Sharpe of 0.48 on 22 trades/yr across 5 symbols,
but I tested 5 strategies and picked the best, so the multiple-comparisons
adjustment is ~0.18 and my honest estimate is 0.30 with a wide interval. I am
also fooling myself that 5 symbols is a universe — that is one correlated bet on
US equity beta.
```

---

## Next

Phase 2 (`../02-engine/`): stop borrowing the backtester. Build your own.
Do not start Week 3 until the Phase 1 gate passes.
