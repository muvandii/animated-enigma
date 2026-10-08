# Phase 04 — Paper replication (Weeks 8–9)

Three published papers, reproduced from their own rules, with delta tables.

**The rule that makes this phase honest:** a delta table with a written cause for
every gap > 20% is worth more than a replication that "matches". If your numbers
match the paper's to within 5%, be suspicious before you are pleased.

## Files

| Path | What |
|---|---|
| `papers/dossiers/01-tsmom-moskowitz-ooi-pedersen.md` | method summary, headline numbers, what you cannot reproduce |
| `papers/dossiers/02-vol-managed-momentum.md` | Barroso / Moreira-Muir, with the three-explanations trap |
| `papers/dossiers/03-distance-pairs-gatev.md` | GGR pairs, formation/trading discipline |
| `papers/replications/example-tsmom/` | **fully executed example**: spec, runnable code, results, delta table |
| `week-08.md`, `week-09.md` | daily objectives, concepts, rubrics, graveyard prompts |
| `rubric.md` | Phase 4 gate |

## Run the worked example

```bash
cd papers/replications/example-tsmom
python replicate.py
```

It prints the results and a delta table with a ratio column and flags every gap
bigger than 20%. On the seeded offline universe it produces:

| Metric | Paper | Example run | Ratio |
|---|---|---|---|
| Gross Sharpe | 0.95 | 0.09 | 0.10 (explained in `delta-table.md`) |
| Universe size | 58 | 10 | 0.17 |
| Asset classes | 4 | 1 | 0.25 |

Read `delta-table.md` — the decomposition of *why* the gap is 10× is the most
instructive part of the phase, and it is not "my implementation is worse".

## The three questions every replication must answer

1. Did the **sign** of the effect reproduce? (yes/no)
2. Did the **magnitude** reproduce? (ratio + cause for every gap > 20%)
3. Would you **trade** this, given what you now know? (this becomes the S-verdict)
