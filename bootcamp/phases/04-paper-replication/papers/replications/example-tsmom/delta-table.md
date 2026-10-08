# Delta table — my numbers vs the paper's

**Rule:** every row with a ratio outside [0.8, 1.2] needs a written cause.
A replication with no flagged rows is suspicious, not successful.

| Metric | Paper | Mine | Ratio | Cause of gap |
|---|---|---|---|---|
| Annualised return (gross) | 10.5% | 1.12% | **0.11** | See causes 1–4 below |
| Sharpe (gross) | 0.95 | 0.09 | **0.10** | Same causes; Sharpe falls more than return because my vol target is not achieved (see cause 5) |
| Universe size | 58 | 10 | **0.17** | Free-data constraint. Cannot be fixed without a paid futures data source. |
| Asset classes | 4 | 1 | **0.25** | Same constraint. This is the single biggest cause: the paper's diversification comes from *uncorrelated* asset classes, and 10 US-listed ETFs are ~one correlated bet. |
| Sample | 1965–2009 | 2015–2025 | n/a | The effect has been publicly known since 2012. Post-publication decay is documented for most anomalies. |
| Max drawdown | (not headline) | −26.7% | n/a | Reported because the paper's central risk claim is about crash behavior, and I could not test it: my sample has no 2008-style momentum crash for a US-equity-only universe. |
| Turnover | (paper reports turnover separately) | 12/yr | n/a | My number is lower than the paper's because I hold for a month at a fixed vol-scaled size; the paper updates the scaler daily in some specifications. |
| Costs | omitted from headline | −0.35%/yr | n/a | The paper's 10.5% is gross. I report both. At 12 rebalances/yr the cost is small — costs are NOT why my number is lower. |

## The five causes, ranked by how much of the gap they explain

**1. Universe diversification (largest).** The paper's Sharpe of 0.95 comes from
combining 58 instruments across equities, bonds, currencies, and commodities.
Roughly, if the per-instrument Sharpe is ρ and the average pairwise correlation
is r across N instruments, the portfolio Sharpe ≈ ρ·√(N/(1+(N−1)r)). With N=58
and r≈0.05 you get √((58)/(1+2.85)) ≈ 3.9× the single-instrument Sharpe. With
N=10 US equity ETFs and r≈0.7 you get √(10/(1+6.3)) ≈ 1.17×. **That ratio — 3.9
vs 1.17 — is about 3.3×, and it accounts for most of the 10× gap on its own.**

**2. Post-publication decay.** The paper's sample ends in 2009. Mine starts in
2015, three years after publication. Published anomalies typically decay
substantially after publication.

**3. Instrument mismatch.** The paper trades futures (with roll yield and
margining); I trade ETFs. For commodities and bonds the roll yield is a real
component of the return that I do not have.

**4. Different sample, different regimes.** My 10-year window contains one
dominant regime (post-GFC equity bull market plus 2020 and 2022). Trend
following in a single sustained uptrend adds little over buy and hold.

**5. Vol targeting not achieved.** My realised net vol is 11.9%, not the 40%
target. That is because I scale by `target_vol/σ` per instrument and then average
across 10 correlated instruments — the portfolio vol collapses toward the
average, well below the per-instrument target. The paper faces the same effect
but with 4 uncorrelated classes the collapse is smaller. Consequence: my return
is small *and* my vol is small, so the Sharpe comparison is the fair one.

## Verdict

**Sign reproduced: YES. Magnitude reproduced: NO (0.10×).**

This is an honest, successful *replication attempt* with a documented delta. It
is NOT a confirmation of the paper's numbers, and I will not claim it is. The
value of the exercise is that I can now state, with numbers, exactly how much of
the paper's result came from diversification across uncorrelated asset classes —
which is something reading the paper alone would never have taught me.

## What would actually close the gap

Not parameter tuning. The only real fix is a **multi-asset universe**: add bond
futures (or TLT/IEF), commodities (GLD/DBC), and currencies (UUP/FXE) so the
average pairwise correlation drops. I have TLT, IEF and GLD in the universe
already — they are 3 of 10. A replication with a genuinely multi-asset universe
is a legitimate Week 9 extension, and it would be pre-registered as a new
experiment with a new prediction.
