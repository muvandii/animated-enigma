# Spec — extracted from the paper BEFORE writing any code

**Rule:** you write this file by reading the paper, not by reading someone else's
GitHub. If you cannot fill in a row, go back to the paper.

## The rule, as the paper states it

> "We form time-series momentum portfolios by taking a long position in an
> instrument if its excess return over the past 12 months is positive and a short
> position if negative... we scale positions by the inverse of the instrument's
> ex-ante volatility, targeting 40% annualised volatility." (paraphrased from
> MOP 2012, §2)

## Parameter table

| Parameter | Paper's value | Where in the paper | My value | Deviates? |
|---|---|---|---|---|
| Formation / lookback | 12 months | §2, "past 12 months" | 252 bars | no |
| Skip (12-1) | 1 month | §2, excludes most recent month | 21 bars | no |
| Holding period | 1 month | §2 | 1 month (ME rebalance) | no |
| Vol target | 40% annualised | §2.2 | 0.40 | no |
| Vol estimator | EWMA of daily returns, 6-month | §2.2 | rolling 126-day stdev | **yes** (see note) |
| Universe | 58 instruments, 4 asset classes | §3, Table 1 | 10 US-listed ETFs | **yes** (unavoidable) |
| Sample | 1965–2009 (varies) | §3 | 2015–2025 | **yes** (unavoidable) |
| Costs | not in the headline numbers; separate section | §5 | 1 bp + 5 bps | **yes** (the paper omits them; I must not) |
| Rebalance | monthly | §2 | monthly | no |
| Sizing | equal risk across instruments | §2.2 | equal weight across instruments | no |

**Note on the vol estimator:** the paper uses an EWMA on daily returns; I use a
126-day rolling standard deviation. This is a deliberate, documented deviation —
a rolling window is easier to audit for look-ahead, and EWMA vs rolling is a
second-order effect compared to the universe and sample differences. I test the
sensitivity by re-running with EWMA: [result goes in results.md].

## Falsifiable predictions (written before running)

1. The sign of the 12-1 month return predicts next-month return **positively**.
   If the slope is ≤ 0, the effect is absent in my sample.
2. TSMOM's return should be **lower** in my sample than the paper's, because:
   - one asset class instead of four (less diversification, lower Sharpe)
   - post-publication period (decay)
   - ETFs instead of futures (no roll yield, different microstructure)
3. TSMOM should have **low correlation** with the equal-weight universe return
   (it is directional per asset, not a market bet) — though with 10 US equity
   ETFs, that correlation will be higher than the paper's.

## What I am NOT allowed to do to close the gap

- Change the lookback to something that works better in my sample.
- Add a filter, trend condition, or vol regime switch.
- Switch to cross-sectional momentum.
- Choose the universe by looking at which instruments worked.
- Report gross as if it were net (the paper's headline is gross; I report both).

Any of these turns a replication into strategy S14.5, and I would have to
pre-register it as a new strategy with a new ID.
