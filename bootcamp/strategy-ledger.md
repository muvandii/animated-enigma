# Strategy Ledger — 16 slots

The bar is 15 shipped. Ship 16 so one can die in live paper and you still pass.

**"Shipped" means all six columns are filled and `verdict.md` exists.** A strategy
that is still being tuned is not shipped; it is a hobby.

Fill this in as you go. Order is fixed — do not reorder to hide the messy part.

| ID | Name | Week | Turnover/yr | Gross Sharpe | Net Sharpe | OOS Sharpe | Verdict | Killed by |
|---|---|---|---|---|---|---|---|---|
| S01 | MA(10/50) crossover | 1 | ~7 | +0.21 | +0.19 | +0.08 | KILL | underperforms buy & hold net of costs |
| S02 | MA + 200d trend filter | 1 | | | | | | |
| S03 | RSI(2) mean reversion | 2 | | | | | | |
| S04 | Bollinger reversion | 2 | | | | | | |
| S05 | Donchian breakout | 2 | | | | | | |
| S06 | Time-series momentum | 5 | | | | | | |
| S07 | Cross-sectional momentum | 5 | | | | | | |
| S08 | Distance pairs | 5 | | | | | | |
| S09 | Vol-target overlay | 6 | | | | | | |
| S10 | Turn of month | 6 | | | | | | |
| S11 | Overnight gap fade | 6 | | | | | | |
| S12 | Dual momentum | 7 | | | | | | |
| S13 | Mean-reversion basket | 7 | | | | | | |
| S14 | TSMOM (paper: Moskowitz–Ooi–Pedersen) | 8 | | | | | | |
| S15 | Vol-managed momentum (paper) | 9 | | | | | | |
| S16 | Distance pairs (paper: Gatev et al.) | 9 | | | | | | |

## Rules of the ledger

1. **Turnover is computed before the backtest, from the signal.** If you do not
   know it until after, you built the strategy to fit the cost model.
2. **Gross vs net Sharpe gap is the single most informative number in this
   table.** A gap > 0.5 means your edge is a cost-structure bet, not a
   forecasting bet. Say so in the verdict.
3. **OOS < 50% of IS = dead, regardless of how good IS looked.** Log it.
4. **You may not delete a row.** Killed strategies stay. The ledger is the
   evidence that you ran the loop 16 times.

## Pre-registration (do this on Monday, every week)

Before you write code, add a row to `notes/strategies/<ID>.md` with:

- **THESIS** (1 paragraph — the causal claim, not the indicator)
- **KILL CRITERIA** (numbers, decided now):
  - net Sharpe < 0.5 on the full sample, **or**
  - OOS Sharpe < 50% of IS Sharpe, **or**
  - total cost paid > 50% of gross return, **or**
  - fewer than 30 independent trades in the sample
- **EXPECTED TURNOVER** (from the signal's half-life, before backtesting)

If you change the kill criteria after seeing results, the strategy is
disqualified and must be re-run with new pre-registered criteria and a new ID.
