# Dossier 02 — Volatility-managed momentum

**Papers:**
- Barroso, P. & Santa-Clara, P. (2015), "Momentum Has Its Moments", *Journal of
  Financial Economics* 116(1), 111–120.
- Moreira, A. & Muir, T. (2017), "Volatility-Managed Portfolios", *Journal of
  Finance* 72(4), 1611–1644.

**One-line thesis:** momentum's terrible crashes are predictable — they happen
when momentum's own realized volatility is high — so scaling the strategy by
inverse recent volatility roughly doubles its Sharpe and nearly eliminates its
crash risk.

---

## Method summary

| Element | Paper's choice | Your implementation |
|---|---|---|
| Base strategy | WML (winner-minus-loser, cross-sectional momentum, 12-1) | your S07 |
| Scaling | `w_t = (target_vol / σ_{t-1}) × w_base_t`, σ from DAILY returns over the prior month (Barroso) or 6 months (Moreira-Muir) | pick one, state it, test both |
| Target vol | 12% annualised (Barroso) | keep 12% for comparability, and report 15% as a sensitivity |
| Rebalance | monthly | monthly (scaling updated daily in Moreira-Muir — note the turnover consequence) |
| Universe | CRSP NYSE/AMEX/NASDAQ, 1926–2011 | your ETF universe, 2010–2025 |
| Costs | Barroso reports that the strategy survives plausible transaction costs | you must test this; scaling ADDS turnover |

**Headline numbers to reproduce:**
- WML raw: Sharpe ≈ **0.55**, with a **-73%** drawdown in 1932 and **-52%** in 2009
- WML vol-managed: Sharpe ≈ **1.04**, max drawdown ≈ **-19%**
- Moreira-Muir: vol management improves Sharpe for **most** of 12 anomaly
  portfolios and the market factor itself

## The trap in this replication

Vol scaling improves Sharpe **partly because it is market timing** — it reduces
exposure after vol rises. There are therefore three competing explanations for
any improvement you find:

1. **Genuine predictability of momentum's own risk** (the paper's claim)
2. **Generic vol targeting** (works on any strategy, including a random one)
3. **Look-ahead in the vol estimate** (a centered window, or a window that
   includes the rebalance date's own return)

**You must separate them.** Minimum work:
- Apply the same vol scaling to a *random* long-short portfolio. If it also
  improves, explanation 2 is live.
- Re-run with the vol window shifted one more bar back. If the improvement
  vanishes, you had look-ahead.

If you find the improvement but cannot rule out explanations 2 and 3, say so in
the delta table. That is a legitimate, honest replication outcome.

## Where you will not reproduce it

- Your universe is ETFs, not 1,000s of individual stocks, so cross-sectional
  dispersion is much lower and WML is weaker.
- Your sample (2010–2025) contains few of the momentum crashes that the scaling
  is designed to avoid. The mechanism has less to do.
- Daily-updated scaling (Moreira-Muir) generates real turnover; on ETFs at 5 bps
  this can consume a meaningful part of the improvement.

## Pre-registered kill criteria

- FAIL if: vol-managed Sharpe is not higher than raw Sharpe net of costs, OR the
  improvement disappears when you shift the vol window back one bar, OR vol
  scaling also improves a random portfolio by a comparable amount.
- The third criterion is the one people skip. Do not skip it.

## Prompts

1. Is the vol-scaling result evidence about momentum specifically, or about
   volatility generally? What experiment distinguishes them?
2. Barroso's sample starts in 1926. What in your 2010–2025 sample is missing that
   his had?
3. If vol-managed momentum doubles the Sharpe, why is not everyone doing it?
   Give a capacity/risk answer, not a "people are irrational" answer.
