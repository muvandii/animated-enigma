# Concept: multiple comparisons / the winner's curse  (EXEMPLAR)

WHEN I LEARNED IT: 2025-01-24 — when I caught myself writing "S05: Sharpe 0.48"
in the Phase 1 summary without mentioning that it was the best of five tries.

DEFINITION (2 sentences):
When you test N variants and report the best one, the expected value of that best
result rises with N even if every variant is worthless, so the reported number is
biased upward. The more things you tried, the higher the bar a single result has
to clear before it means anything.

FORMULA:
```
P(at least one of N independent trials clears threshold p) = 1 - (1 - p)^N
Expected max of N standard normals ~ sqrt(2 ln N)
Deflated Sharpe (simplified):
    SR_adj ~= SR_obs - sqrt(2 ln N) / sqrt(T_years)     [N = trials, T = years]
```

CODE (3–5 lines):
```python
import numpy as np
N, T = 5, 10                                       # 5 strategies, 10 years
adj = np.sqrt(2 * np.log(N)) / np.sqrt(T)
print(f"subtract ~{adj:.2f} before believing the best Sharpe")   # 0.18
```

WHERE IT LIES / LIMITS:
The formula assumes INDEPENDENT trials. Correlated strategies (five momentum
variants on the same universe) are effectively fewer than five trials, so the
correction is too harsh — but not zero. It also ignores that your N is bigger
than you think: every parameter you eyeballed, every start date you nudged, every
"let me just try one more thing" is a trial. Honest N is always larger than the N
you would report.

HOW I'D SPOT IT WRONG IN SOMEONE ELSE'S CODE:
A parameter sweep that reports only the best cell; a paper that says "we tested
3,000 signals" in the appendix and reports the top one in the abstract as if it
were a single hypothesis; any backtest whose sample start date is suspiciously
round-adjacent to a regime change.

APPLIED TO:
- **Phase 1**: best net Sharpe across S01–S05 was 0.19 (S01) / 0.48 (S05). With
  N=5, T=10 → subtract ≈0.18. S05's honest estimate is ≈0.30, and the 95% CI on
  10 years of a 22-trades/yr strategy is roughly ±0.4. So "S05 works" should have
  read "S05 is not yet distinguishable from zero, but it is the least-bad of
  five." I wrote that in the summary instead.
- **Week 7**: this becomes the backbone of `reports/parameter-sweep.md`.

DONE WHEN self-check:
- [x] I can compute the adjustment in 3 lines
- [x] I can explain why testing MORE strategies RAISES the bar
- [x] I can spot "best of 40 parameter sets" presented as one result
