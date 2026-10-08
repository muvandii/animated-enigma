# Concept: simple vs log returns  (EXEMPLAR)

WHEN I LEARNED IT: 2025-01-16 — while splitting S01's 10-year sample into five
walk-forward folds and noticing that summing each fold's total return did not
equal the total return of the whole sample.

DEFINITION (2 sentences):
A simple return is the actual fractional change in your capital
(`P_t/P_{t-1} - 1`), so it compounds multiplicatively across time. A log return
is `ln(P_t/P_{t-1})`, and it adds across time, which makes it the right object
for any math that aggregates periods — and the wrong object to show a human.

FORMULA:
```
simple:  r_t = P_t / P_{t-1} - 1
log:     l_t = ln(P_t / P_{t-1}) = ln(1 + r_t)
total over T periods:  prod(1 + r_t) - 1  ==  exp(sum l_t) - 1
sum of simple returns != total return   (it is always an overstatement when vol > 0)
```

CODE (3–5 lines):
```python
p = px.iloc[:4]                                  # 102.58, 98.31, 99.64, 99.75
s = p.pct_change().dropna(); l = np.log(p / p.shift(1)).dropna()
print(s.sum(), np.expm1(l.sum()), p.iloc[-1] / p.iloc[0] - 1)
# -0.027011  -0.027605  -0.027605     <- sum(simple) is wrong; expm1(sum(log)) is right
```

WHERE IT LIES / LIMITS:
Log returns are only additive if you never rebalance and never go flat — for a
strategy that is in cash half the time, the log return of the *equity curve* is
still additive, but the log return of the *asset* is not the strategy's return.
Also, log returns understate gains in a way that looks small (a +50% move is
0.405 in log space) and is psychologically misleading in a verdict. Report simple
returns, always. Use log only for aggregation math.

HOW I'D SPOT IT WRONG IN SOMEONE ELSE'S CODE:
Averaging simple returns across assets to get a portfolio return. If AAPL is
+50% and IWM is −50%, the average simple return is 0%, but you actually lost
13.4%. The correct cross-sectional aggregation for a *buy-and-hold* basket is to
average the log returns, or better, compound the actual weights. Also: any code
that does `returns.sum()` and calls it "total return".

APPLIED TO:
- **S01 walk-forward**: the five folds' simple returns did not sum to the
  full-sample return (−2.7% discrepancy); summing log returns did. Now I always
  aggregate folds with `expm1(sum(log))`.
- **metrics.py**: `returns(kind="log")` exists for math, `kind="simple"` for
  reporting. My verdicts only ever quote simple.

DONE WHEN self-check:
- [x] I can convert between them in 3 lines
- [x] I can explain why log returns add but simple returns do not
- [x] I can spot the "average the simple returns" portfolio bug
