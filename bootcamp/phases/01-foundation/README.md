# Phase 01 — Foundation (Weeks 1–2)

**Goal:** ship 5 strategies by borrowing a backtester, so that when you build
your own engine in Phase 2 you already know what it has to do.

**Deliberately absent from this phase:** no event-driven engine, no portfolio, no
parameter optimization, no live trading. You get one asset (or a handful), a
vectorized backtester someone else wrote, and the loop.

## Files

| File | What it is |
|---|---|
| `week-01.md` | **fully authored** — 7 daily objectives, 2 concepts, rubric, graveyard, worked example |
| `week-02.md` | fully authored — 3 strategies in 3 days, 2 concepts, Phase 1 gate |
| `rubric.md` | Phase 1 gate rubric + calibration examples |
| `concepts/` | 4 **filled** concept notes (exemplars — read after you write yours) |
| `templates/` | verdict template, viral-strategy debunk worksheet, starter notebook |
| `examples/` | runnable S01 and S02, with their real outputs and verdicts |
| `graveyard/` | filled example graveyard + failure-note samples |

## Start here

```bash
cd phases/01-foundation/examples
python week01_ma_crossover.py --offline      # read the output before writing code
```

Then open `week-01.md` and do Monday.

## What "done" means

5 strategies. Every one with costs, out-of-sample, and a verdict. A graveyard
with at least 4 bodies. 14 daily notes, 4 concept notes, 5 strategy notes, 3+
failure notes. All of it honest — including, especially, the parts where you were
wrong.
