# Dossier 03 — Pairs trading: distance method

**Paper:** Gatev, E., Goetzmann, W. N., Rouwenhorst, K. G. (2006), "Pairs Trading:
Performance of a Relative Value Arbitrage Rule", *Review of Financial Studies*
19(3), 797–827.

**One-line thesis:** pairs of stocks whose normalized prices have historically
moved together (minimum sum of squared deviations) tend to reconverge; trading
the spread when it exceeds two historical standard deviations earns ~11% annualized
with low exposure to the market.

---

## Method summary

| Element | Paper's choice | Your implementation |
|---|---|---|
| Formation period | 12 months, **non-overlapping** with the trading period | 252 bars, must end before trading begins |
| Pair selection | top 5–20 pairs by minimum sum of squared deviations of normalized prices | your `pairs.py::_select_pairs` |
| Trading period | the following 6 months | 126 bars |
| Open rule | spread moves more than **2 historical standard deviations** from its formation-period mean | `entry_z = 2.0` |
| Close rule | spread crosses (reverts), or end of the trading period | `exit_z` + `max_hold` |
| Sizing | $1 long / $1 short per pair, equal-weighted across pairs | ±0.5 per leg |
| Universe | CRSP, 1962–2002, ~cheapest-to-trade subset | your ETF/sector universe |
| Costs | the paper's central analysis is **both** with and without costs,
  and costs cut returns substantially | you must model them; this is where the
  strategy usually dies |

**Headline numbers to reproduce:**
- Average annualized excess return ≈ **11%** (self-financing, before costs)
- Returns are **larger for the cheapest-to-trade** (lowest bid-ask) decile
- The strategy is nearly **market-neutral** (low beta)
- **Crucially:** returns decline over the sample period, and the paper's own
  discussion of transaction costs suggests much of the excess return is
  compensation for liquidity provision that would be arbed away

## The three ways this replication fails — and what each means

1. **Your universe is too small.** With 8 ETFs you have 28 candidate pairs; with
   1,000 stocks you have ~500,000. The minimum-distance criterion is far more
   powerful with a big candidate pool, and "the best 5 of 28" is mostly noise.
   *Expect this and quantify it.*
2. **Pairs do not reconverge.** Many published pairs results come from
   look-ahead in pair selection. With a clean formation/trading split, the effect
   is much smaller.
3. **Costs.** The paper's own cost analysis is the most important part. If your
   net result is negative while gross is positive, that is the finding, and it is
   consistent with the literature's post-publication experience.

## The specific discipline this paper demands

**Formation and trading windows must not overlap, and must not be re-selected.**
Implement the walk as:

```
[form 0:252][trade 252:378][form 378:630][trade 630:756] ...
```

The tempting shortcut — find the best pairs over the whole sample, then trade
them — inflates results enormously and is the single most common error in
published and amateur pairs backtests. Your `pairs.py` skeleton does it
correctly; do not "optimize" it into incorrectness.

## Pre-registered kill criteria

- FAIL if: net Sharpe < 0 after costs, OR fewer than 50 trades in the sample,
  OR the result is driven by a single pair, OR removing the two best pairs kills
  the strategy.
- REPORT: the number of trades. If it is under 50, the confidence interval on
  your Sharpe is wider than your Sharpe.

## Prompts

1. The paper selects pairs by *price distance*, not by cointegration. What does
   that miss, and does it matter?
2. If pairs trading is liquidity provision, who is paying you and why do they
   stop?
3. Why does the effect decline over the paper's own sample, and what does that
   predict about your 2015–2025 sample?
