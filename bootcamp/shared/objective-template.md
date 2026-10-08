# The Guided Objective Contract (copy-paste template)

Every objective in this course — weekly and daily — uses exactly this structure.
No exceptions. If an objective cannot be written in this format, it is not an
objective; it is a wish.

```text
🎯 OBJECTIVE:   <Verb> <the artifact> — one line, starts with a verb
WHY:          <the reason this exists / what it proves / what it unblocks>
INPUT:        <files, data, or prior artifacts you start from>
OUTPUT:       <exact file paths that must exist when you are done>
PROOF:        <the command you run, or the artifact you open, that proves it>
TIME:         <realistic minutes, not aspirational>
BLOCKER IF:   <the specific condition under which you must stop and ask/fix>
```

## The verb rule

OBJECTIVE must begin with a **verb**: Build, Test, Compare, Ship, Write,
Replicate, Break, Diagnose, Rebuild, Log.

Banned openings, because they produce no artifact:

- ~~"Understand Sharpe ratios"~~
- ~~"Learn about look-ahead bias"~~
- ~~"Get familiar with the backtester"~~

Rewrite them until they name an artifact and a proof:

- ✅ "Build `notes/concepts/sharpe-ratio.md` from the Concept Note Template after
  measuring your own strategy's Sharpe three ways"
- ✅ "Break S01 by adding 25 bps of slippage and log the Sharpe delta in
  `notes/failures/2025-01-16-S01-costs.md`"

## Field rules

- **OUTPUT names real files.** "understand costs" is not an output.
  `notes/failures/2025-01-16-S01-costs.md` is.
- **PROOF is executable or openable.** A command (`python -m pytest -q`), a file
  you can open, a number you can compare. If the proof is a feeling, it is not a
  proof.
- **TIME is honest.** Objectives that take 4 hours get `TIME: 240 min`. Better to
  plan a long block than to blow the week.
- **BLOCKER IF is a stop condition, not a mood.** "if the test suite is red",
  "if you cannot fetch AAPL", "if |net Sharpe - gross Sharpe| > 1.0 and you
  cannot explain why". Its purpose is to make you surface problems on the day
  they happen instead of on Sunday.

## Worked example

```text
🎯 OBJECTIVE:   Build the S01 MA(10/50) crossover signal as strategies/S01_ma_crossover/strategy.py
WHY:          Nothing else this week can start until a signal exists that runs on real data.
INPUT:        data/clean/aapl.parquet (from `python fetcher.py AAPL`)
OUTPUT:       strategies/S01_ma_crossover/strategy.py, notes/daily/week-01/tue.md
PROOF:        `python strategies/S01_ma_crossover/strategy.py` prints a tear sheet with n_periods > 1000
TIME:         90 min
BLOCKER IF:   the parquet has < 1000 rows, or the signal is 1.0 for every bar
```

## Daily note is part of every objective

Every daily objective's OUTPUT includes `notes/daily/week-NN/<day>.md`. No daily
note = the day did not happen. Do not backfill on Sunday; backfilled notes are
fiction and the rubric treats them as missing.
