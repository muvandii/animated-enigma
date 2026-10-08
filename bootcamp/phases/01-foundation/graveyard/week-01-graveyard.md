# Graveyard — Week 1 (SAMPLE, completed)

Copy this table into `graveyard/graveyard.md` in your own repo. This is what a
complete Week 1 looks like **when both strategies die** — which is the expected
outcome.

| ID | NAME | DATE KILLED | KILLED BY | ROOT CAUSE (concept) | NOTE | LESSON CARRIED FORWARD |
|---|---|---|---|---|---|---|
| S01 | MA(10/50) crossover | 2025-01-19 | loses to buy & hold net of costs | signal lag in a drifting market | `notes/failures/2025-01-16-S01-costs.md` | always print buy & hold beside the strategy; volatility reduction is not alpha |
| S02 | MA + MA200 filter | 2025-01-19 | filter added trades and cut CAGR 77% | AND-ing binary signals sums their transitions; opportunity cost of time out of market | `notes/failures/2025-01-18-S02-filter.md` | a filter trades too — measure its turnover before adding it |

## Sample failure note — S02 (the rebuild that failed)

```markdown
# Failure: S02 trend filter made S01 worse

DATE: 2025-01-18
STRATEGY: S02 MA(10/50) + MA(200) filter

WHAT BROKE:
Trades went 69 -> 95 (+38%) when I predicted -25%. CAGR went +3.04% -> +0.69%
(-77%). Sharpe +0.19 -> +0.05. Both pre-registered claims failed.

ROOT CAUSE:
Two mechanisms, both of which I predicted backwards.
(1) Turnover: I assumed a filter only removes trades. Wrong. Combining two binary
conditions with AND sums their TRANSITION counts — the MA200 crossing adds its own
entries and exits to the MA10/50 ones. A filter reduces trades only if it is
SMOOTHER than the signal it gates; a 200-day MA on daily bars is not smooth
enough relative to a 10/50 cross to achieve that.
(2) Return: time in market fell 52.0% -> 36.1%. In a sample where buy & hold
earned +8.0%/yr, the days the filter removed had positive expected return. A
filter that cuts exposure only helps if the removed days are worse than average,
and here they were better.

CONCEPT THAT EXPLAINS IT:
Transition-count arithmetic on combined signals + opportunity cost of time out
of market (NOT cost drag — S01 was already cheap at 0.41%/yr).

FIX ATTEMPTED:
None. The claim failed on both axes; there is nothing to rescue. I am not going
to search for a trend-window length that works, because that would be fitting.

DID FIX WORK: NO

LESSON:
A "filter" is a signal, and every signal trades. Before adding one, count the
transitions it introduces, not the ones it removes.
```

## Look-ahead attack log (Week 1 graveyard prompt, attack 3)

```markdown
# Failure: S01 with .shift(-1) prints Sharpe 14.2

DATE: 2025-01-19
STRATEGY: S01 (deliberately corrupted)

WHAT BROKE:
Adding .shift(-1) to the signal (using tomorrow's close to decide today's
position) produced Sharpe 14.2 and CAGR 340%. The honest version prints 0.19.

ROOT CAUSE:
The signal was computed from data that did not exist at the decision time.
The backtester's shift(1) guard cannot catch this — the peek is INSIDE the signal
function, not in the execution lag.

CONCEPT THAT EXPLAINS IT:
Look-ahead bias. The detector is not the guard, it is the MAGNITUDE of the
result: any Sharpe above ~5 on daily data is look-ahead until proven otherwise.

FIX ATTEMPTED:
Removed the shift(-1). Result returned to Sharpe 0.19.

DID FIX WORK: YES

LESSON:
Memorize the number 5. If a daily-bar strategy prints Sharpe > 5, I do not
celebrate; I go hunting for the future. And I now run the "rewrite the last 100
bars and check the first N" test on every signal I write (see
templates/starter-notebook.ipynb, cell 3).
```
