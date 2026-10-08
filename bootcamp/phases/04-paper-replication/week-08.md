# Week 8 — Replicate a paper, properly

> **Phase 04 · Paper replication** · Hours: 16–20 · Strategies: S14
>
> You stop inventing strategies and start reproducing someone else's. This is
> harder in a different way: the rules are fixed, so you cannot tune your way out
> of a bad result.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Replicate Moskowitz-Ooi-Pedersen "Time Series Momentum" end to end and write an honest delta table
WHY:          Replication is the only way to find out whether your machinery agrees with the published literature. If your engine cannot reproduce a known result's DIRECTION, every number you have shipped is suspect.
INPUT:        papers/dossiers/01-tsmom-moskowitz-ooi-pedersen.md, papers/replications/example-tsmom/ (worked example — read it AFTER you write your spec)
OUTPUT:       papers/replications/tsmom/{spec.md,replicate.py,results.md,delta-table.md}
              strategies/S14_tsmom_paper/{strategy.py,config.json,tearsheet.txt,verdict.md}
              notes/strategies/S14.md, notes/daily/week-08/*.md (7)
              notes/concepts/reading-a-paper-as-a-spec.md
              graveyard/graveyard.md (row if the effect does not reproduce)
PROOF:        delta-table.md has one row per headline metric with a ratio column, and a written cause for every ratio outside [0.8, 1.2]
TIME:         960–1200 min
BLOCKER IF:   you changed the paper's parameters to improve your result — that is a new strategy (S14.5), not a replication
```

---

## Daily objectives

### Monday — Read the paper. Write spec.md. Do not code.

```text
🎯 OBJECTIVE:   Read the paper and extract its rules into papers/replications/tsmom/spec.md
WHY:          Coding before you can state the rules is how you accidentally implement a different strategy and then "replicate" it successfully.
INPUT:        papers/dossiers/01-tsmom-moskowitz-ooi-pedersen.md, the paper itself
OUTPUT:       papers/replications/tsmom/spec.md (parameter table with paper-vs-mine columns and a Deviates? flag on every row)
              notes/daily/week-08/mon.md
PROOF:        every parameter row cites the section of the paper it came from
TIME:         150 min
BLOCKER IF:   any row says "I chose X because it seemed reasonable" without flagging it as a deviation
```

### Tuesday — Build the universe

```text
🎯 OBJECTIVE:   Fetch a multi-asset universe (>=10 instruments across >=3 asset classes) and reconcile it against the paper's Table 1
WHY:          The universe IS most of the result (see the delta table's cause #1). Getting a genuinely multi-asset universe is the highest-leverage work of the week.
INPUT:        fetcher.py
OUTPUT:       data/clean/ (multi-asset parquet), papers/replications/tsmom/universe.md (what you got vs the paper's, and what you could not get)
              notes/daily/week-08/tue.md
PROOF:        >=10 instruments spanning >=3 asset classes; a written statement of what the paper had that you do not
TIME:         150 min
BLOCKER IF:   fewer than 3 asset classes — you cannot test the paper's diversification claim with one
```

Minimum viable multi-asset universe on free data: SPY/QQQ/IWM (equities),
TLT/IEF/LQD (bonds), GLD/DBC (commodities), UUP/FXE (currencies), VNQ (real
estate). That is 4 asset classes for $0.

### Wednesday — Implement from the spec

```text
🎯 OBJECTIVE:   Write papers/replications/tsmom/replicate.py implementing spec.md exactly
WHY:          From the spec, not from anyone else's GitHub. If you read someone's implementation first you will reproduce their bugs and learn nothing.
INPUT:        papers/replications/tsmom/spec.md
OUTPUT:       papers/replications/tsmom/replicate.py
              notes/daily/week-08/wed.md
PROOF:        every function has a comment citing the spec row it implements; the look-ahead audit passes
TIME:         180 min
BLOCKER IF:   the vol estimator uses a centered window
```

### Thursday — Run it. Write down whatever comes out.

```text
🎯 OBJECTIVE:   Run the replication and write results.md WITHOUT editing the implementation to improve the number
WHY:          Thursday's result is the data. You do not get to negotiate with it.
INPUT:        papers/replications/tsmom/replicate.py
OUTPUT:       papers/replications/tsmom/results.md (gross + net + turnover + decomposition)
              notes/daily/week-08/thu.md
PROOF:        results.md reports gross AND net, plus the per-instrument decomposition and the vol-estimator sensitivity
TIME:         150 min
BLOCKER IF:   results.md reports only the number that looks best
```

### Friday — The delta table

```text
🎯 OBJECTIVE:   Write papers/replications/tsmom/delta-table.md with a cause for every gap > 20%
WHY:          The delta table is the deliverable. The code was just how you produced the numbers in it.
INPUT:        results.md, the dossier
OUTPUT:       papers/replications/tsmom/delta-table.md
              notes/concepts/reading-a-paper-as-a-spec.md
              notes/daily/week-08/fri.md
PROOF:        every flagged row has a cause that is a MECHANISM (universe/sample/instrument/estimation), not "my implementation is worse"
TIME:         150 min
BLOCKER IF:   any flagged row's cause is "implementation error" without you having found and fixed the error
```

### Saturday — Ship S14 as a strategy

```text
🎯 OBJECTIVE:   Promote the replication to strategies/S14_tsmom_paper/ with a normal verdict
WHY:          Every replication is also a strategy. It gets a folder, a ledger row, and a verdict, or it does not count toward the 16.
INPUT:        papers/replications/tsmom/
OUTPUT:       strategies/S14_tsmom_paper/{strategy.py,config.json,tearsheet.txt,verdict.md}
              notes/strategies/S14.md
              notes/daily/week-08/sat.md
PROOF:        the S14 verdict cites the delta table and states whether you would trade this
TIME:         120 min
BLOCKER IF:   S14's verdict omits the comparison to the published result
```

### Sunday — Journal + ledger

```text
🎯 OBJECTIVE:   Append the Week 8 journal entry and add the S14 ledger row
WHY:          Row 14. Three to go.
INPUT:        strategies/S14_tsmom_paper/
OUTPUT:       journal/lessons.md (Week 8), strategy-ledger.md (S14 row)
              notes/daily/week-08/sun.md
PROOF:        the journal entry names what surprised you most about the gap
TIME:         60 min
BLOCKER IF:   the journal entry says only "could not reproduce due to data limits"
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Reading a paper as a specification

```text
📐 CONCEPT: Extracting an implementable spec from an academic paper
WHY NOW:   Monday's blocker: you have a 40-page PDF and need a parameter table. Papers are written
           to persuade, not to be implemented, so the information you need is scattered and the
           choices that matter most are often in a footnote.
FORMULA:   spec = {universe, formation window, skip, holding period, sizing, costs, sample, rebalance}
           For each: (a) what did they do, (b) WHY (economic reason or convention?),
           (c) what will I do, (d) does the difference matter?
           Convention vs economics test: if the paper gives no reason for a parameter, it is a
           convention, and you are free to deviate as long as you flag it.
CODE:      # the extraction template, one row per parameter
           {"param": "lookback", "paper": 252, "why": "12m momentum anomaly (economic)",
            "mine": 252, "deviates": False}
EXAMPLE:   MOP's 40% vol target is ECONOMIC (they want equal risk across instruments). Their choice
           of month-end rebalancing is CONVENTION (someone had to pick a date). So: keep the vol
           target exactly, and feel free to test weekly rebalancing as a sensitivity. But document
           both in spec.md before you run anything.
TIME:      20 min
NOTE:      write notes/concepts/reading-a-paper-as-a-spec.md
DONE WHEN: you can fill the 8-field spec from a paper in under an hour, explain in 2 sentences the
           difference between an economic parameter and a conventional one, and spot the replication
           that silently changed an economic parameter and called itself a replication
```

### 📐 CONCEPT — Why replication gaps are usually not about the signal

```text
📐 CONCEPT: Decomposing a replication gap (universe, sample, instrument, estimation)
WHY NOW:   Friday's delta table is blocked until you can attribute the gap rather than just measure it.
FORMULA:   Sharpe_portfolio ~ Sharpe_single * sqrt(N / (1 + (N-1) * rho))
           Use it to separate "the effect is weaker" from "the diversification is worse".
CODE:      import numpy as np
           def sharpe_mult(N, rho): return np.sqrt(N / (1 + (N - 1) * rho))
           print(sharpe_mult(58, 0.05), sharpe_mult(10, 0.70))    # 3.9x  vs  1.17x
EXAMPLE:   My gross Sharpe was 0.09 vs the paper's 0.95 (ratio 0.10). The diversification formula
           says the paper's 58 instruments at rho=0.05 get a 3.9x multiplier while my 10 correlated
           ETFs get 1.17x -- a 3.3x difference from DIVERSIFICATION ALONE. That is most of the
           gap, and it is not a statement about the signal at all. This is the single most useful
           thing I learned in Week 8.
TIME:      15 min
NOTE:      write notes/concepts/replication-gap-decomposition.md
DONE WHEN: you can apply the diversification multiplier in 3 lines, explain in 2 sentences why a
           small correlated universe cannot reproduce a large diversified one, and spot a delta
           table that blames "different market conditions" without quantifying anything
```

---

## ✅ CHECKPOINT RUBRIC — Week 8 gate

- [ ] `spec.md` complete: 8+ parameters, each with paper value, section citation, my value, deviation flag
- [ ] Universe: ≥10 instruments across ≥3 asset classes, with `universe.md` naming what you lack
- [ ] `replicate.py` implements the spec, with look-ahead audit passing
- [ ] `results.md` reports gross AND net, per-instrument decomposition, vol-estimator sensitivity
- [ ] `delta-table.md`: ratio column + written cause for every ratio outside [0.8, 1.2]
- [ ] S14 shipped as a strategy with a verdict citing the delta table
- [ ] 7 daily notes, 2 concept notes, 1 strategy note
- [ ] S14 ledger row complete

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> Kill the replication three ways:
> 1. **Universe attack:** re-run using only the 3 instruments that performed
>    best. Record the Sharpe. Then throw that away — it is selection bias, and
>    you are logging it so you recognise it later.
> 2. **Estimator attack:** switch the vol estimator to a 5-day window. Record the
>    turnover and the Sharpe.
> 3. **Period attack:** re-run on the first half and second half separately. If
>    the sign flips, log it — the effect is not stable in your sample.

## Next

Week 9: two more replications (vol-managed momentum, distance pairs).
