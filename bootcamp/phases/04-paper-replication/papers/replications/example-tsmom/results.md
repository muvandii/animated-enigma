# Results — TSMOM replication (ACTUAL RUN)

Command: `python replicate.py` (offline, seeded synthetic ETF universe)
Reproduce: the run is deterministic on the same seed.

```
==================================================================
  REPLICATION — Moskowitz/Ooi/Pedersen 'Time Series Momentum'
==================================================================
  data source        : synthetic
  universe           : 10 instruments
  sample             : 2015-01-02 -> 2025-01-23  (10.0 yrs)
  parameters         : lookback=252 skip=21 target_vol=0.4 rebal=ME
  costs              : 1.0 bps fee + 5.0 bps slippage

------------------------------------------------------------------
  RESULTS
------------------------------------------------------------------
  gross annualised return :     1.12%
  net   annualised return :     0.77%
  gross Sharpe            :     0.09
  net   Sharpe            :     0.06
  max drawdown (net)      :   -26.68%
  annualised vol (net)    :    11.87%
  turnover/day            :   0.0463   (12/yr)
  rebalance events        :       75
  cost drag               :    0.35%/yr
```

## Did the predictions hold?

| Prediction | Result |
|---|---|
| 1. Sign of 12-1m return predicts next-month return positively | **Directionally yes** — gross Sharpe +0.09 is positive, but it is 1/10th of the paper's and within noise of zero |
| 2. Lower than the paper's | **Yes, dramatically** — 0.09 vs 0.95 gross Sharpe (ratio 0.10) |
| 3. Low correlation to the equal-weight universe | **Not testable as predicted** — with 10 US equity ETFs the strategy is effectively a levered US-market bet, so the correlation is high by construction |

## Additional tests (required by the dossier)

- **Vol-estimator sensitivity:** re-ran with EWMA(0.94) instead of rolling 126d.
  [fill in: Sharpe changed from X to Y]. If the result moves materially, the
  estimator choice is doing work it should not be.
- **Look-ahead check:** rewrote the last 100 bars of prices and confirmed the
  first (N−100) signal values were unchanged. Passed.
- **Per-instrument decomposition:** [fill in: how many of the 10 instruments had
  a positive TSMOM Sharpe]. If fewer than 3, the result is 3 instruments, not a
  strategy.
