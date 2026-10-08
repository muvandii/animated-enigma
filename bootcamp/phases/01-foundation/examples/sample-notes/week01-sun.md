# 2025-01-19 — Week 1 · Sun

BUILT:
- strategies/S01_ma_crossover/{tearsheet.txt, verdict.md}
- strategies/S02_ma_crossover_filtered/{tearsheet.txt, verdict.md}
- graveyard/graveyard.md (2 rows)
- journal/lessons.md (Week 1 entry)
- notes/strategies/S01.md + S02.md (results sections)

BROKE:
- Both strategies died. S01 loses to buy & hold (+3.0% vs +8.0%). S02 is worse
  (+0.69%).
- My pre-registered hypothesis for S01 was WRONG: I predicted cost drag would be
  the killer; it was 0.03 of Sharpe. The signal has no edge, full stop.
- My S02 prediction was wrong in the opposite direction: I assumed a filter
  reduces trades. It increased them 38%.

LEARNED:
Two different wrongs, and the second one taught me more. A filter is itself a
signal and brings its own transitions; AND-ing two binary signals sums their
crossing counts. I had been treating filters as free.

QUESTION I STILL HAVE:
With 69 trades, what is the standard error on Sharpe 0.19? If it is ~0.24, then
"KILL" is really "unmeasurable", and I should be reporting confidence intervals
on every verdict from here on. That changes how I read Week 2.

TOMORROW'S FIRST MOVE:
Look up the standard error of the Sharpe ratio estimator (sqrt((1+SR²/2)/T)),
then add a `sharpe_ci()` function to metrics.py with a test.

Time spent: 14.5 hrs   Notes written today: none new (2 verdicts, 2 graveyard rows)
