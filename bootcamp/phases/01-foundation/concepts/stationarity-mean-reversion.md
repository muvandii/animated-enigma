# Concept: stationarity / mean-reverting vs trending processes  (EXEMPLAR)

WHEN I LEARNED IT: 2025-01-22 — after S03 (RSI-2) came back with a negative net
Sharpe and I needed to know whether the *mechanism* was wrong or only the
*costs*.

DEFINITION (2 sentences):
A stationary (mean-reverting) process is pulled back toward a level, so a move
away from that level carries information about the next move. A random walk is
not, so a move away from a level tells you nothing about what happens next — and
any rule that bets on reversion is then just paying costs to flip a coin.

FORMULA:
```
AR(1):   x_t = phi * x_{t-1} + e_t
         |phi| < 1  -> stationary;  half-life = -ln(2) / ln(phi)
         phi ~= 1   -> random walk (unit root); no predictable reversion
Variance ratio:  VR(q) = Var(x_t - x_{t-q}) / (q * Var(x_t - x_{t-1}))
         VR < 1  -> mean reversion;   VR > 1  -> trending
```

CODE (3–5 lines):
```python
x = np.diff(np.log(px.to_numpy()))
phi = np.polyfit(x[:-1], x[1:], 1)[0]              # lag-1 autocorrelation
hl = -np.log(2) / np.log(phi) if 0 < phi < 1 else np.nan
print(f"phi={phi:+.3f}  half_life={hl:.2f} periods")
```

WHERE IT LIES / LIMITS:
`phi` estimated on price LEVELS is always ≈0.99 and tells you nothing — it must
be estimated on returns or on the residual of the process you are trading.
Stationarity is also regime-dependent: a series can revert for a decade and trend
for the next one, and a full-sample `phi` averages those into a meaningless
number. Estimate it rolling. And a statistically significant `phi` is not
necessarily an economically exploitable one once you subtract costs.

HOW I'D SPOT IT WRONG IN SOMEONE ELSE'S CODE:
Autocorrelation computed on levels instead of returns; a "mean reversion"
strategy that uses a moving average for the mean (a moving average is not a
constant — it is a trend-following level, so the rule is trend-following in
disguise); or a half-life quoted in days when the signal holds for weeks.

APPLIED TO:
- **S03 (RSI-2)**: SPY daily log returns gave phi ≈ −0.05 → half-life under one
  day. RSI-2 holds for ~2 days on average, i.e. *past* the reversion horizon.
  That is a concrete, testable prediction I got wrong: I expected the edge to be
  in days 2–5; it was entirely in day 1, and day 1 is the day you pay the spread.
- **S08 (pairs, Week 5)**: the same tool decides whether a spread is tradable at
  all.

DONE WHEN self-check:
- [x] I can estimate phi and a half-life in 3 lines
- [x] I can explain in 2 sentences why a trending series makes mean-reversion
      rules lose money
- [x] I can spot autocorrelation computed on price levels (the ~0.99 tell)
