# Dossier 01 — "Time Series Momentum"

**Paper:** Moskowitz, T. J., Ooi, Y. H., Pedersen, L. H. (2012), *Journal of
Financial Economics* 104(2), 228–250.

**One-line thesis:** the sign of an asset's own trailing 12-month return predicts
its next-month return, for 58 diverse instruments across equities, bonds,
currencies and commodities, over 25+ years.

---

## Method summary (the spec you implement against)

| Element | Paper's choice | Your implementation |
|---|---|---|
| Signal | sign of the trailing 12-month excess return | `sign(px.shift(21)/px.shift(252) - 1)` |
| Hold period | 1 month | monthly rebalance, held through the month |
| Position size | `w_t = sign(r_12m) × (0.4 / σ_t)` | target 40% annualised vol per instrument |
| Vol estimate | exponentially weighted daily returns, 6-month window | EWMA on daily returns |
| Universe | 58 instruments: 24 commodity futures, 12 cross-rates (fwd),
  9 developed equity indices (futures), 13 government bond (10y) futures | **you cannot get 58 futures for free.** Substitute: liquid US equity ETFs + a handful of sector ETFs. Say so. |
| Sample | 1965–2009 (varies by asset) | 2010–2025, whatever you can fetch |
| Costs | the paper reports gross; it also reports a transaction-cost
  sensitivity section using futures turnover | you must model costs; the paper does not hand you a number |

**Headline numbers to reproduce (from the paper):**
- TSMOM(12,1) average annualised return ≈ **10.5%** (equal-weight across assets,
  Table 2), gross of costs
- Sharpe ≈ **0.95** for the diversified TSMOM portfolio
- The effect is negative at the 1-month horizon (short-term reversal) and
  positive from ~3 to 12 months
- TSMOM is **negatively correlated** with the S&P in market crashes (it is the
  hedge, not the risk)

## Why this paper is a good first replication

1. The rule is six lines of pandas. All the difficulty is in the *rigor*, not the
   code.
2. It has a strong, specific, falsifiable claim (10.5% annualised, across 58
   asset classes) so you can actually fail.
3. It forces you to confront the gap between "58 futures" and "what I can fetch
   for free" — which is the central practical lesson of replication.

## Where you will not be able to reproduce it

- **Universe:** you have ~10 ETFs, not 58 futures across 4 asset classes. Your
  diversification is 1 asset class. Expect a materially lower Sharpe.
- **Sample:** you have 2010–2025; they have 1965–2009. The effect has been
  publicly known since 2012. Expect decay.
- **Data source:** continuous futures vs ETF total returns are different
  instruments with different roll costs.
- **Result:** expect a Sharpe in the 0.3–0.6 range, not 0.95. **That is not a
  failed replication; it is a replication with a documented delta.** A claim that
  you reproduced 0.95 on 10 US equity ETFs from 2015 is the suspicious outcome.

## Pre-registered kill criteria (write these before you code)

- FAIL to reproduce if: sign of the 12-month excess return does not predict
  next-month return in your sample (slope ≤ 0 in a univariate regression), OR
  net Sharpe < 0 after costs, OR the result is driven by fewer than 3 of your
  instruments.
- DO NOT: add filters, tweak the vol target, or change the holding period to get
  closer to 10.5%. If you do, you are no longer replicating; you are building
  S14.5.

## Prompts for your dossier notes

1. What exactly does the paper claim, and what is the strongest alternative
   explanation for it (risk premium? liquidity provision? data snooping)?
2. Which of the paper's choices are *economic* (motivated by a mechanism) and
   which are *conventional* (someone had to pick 12 months)?
3. What would a critic say is the single weakest link in the chain from the
   paper's claim to your implementation?
