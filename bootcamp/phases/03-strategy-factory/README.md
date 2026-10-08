# Phase 03 — Strategy factory (Weeks 5–7)

Eight strategies in three weeks, all run through one config-driven runner.

**The point of the factory:** identical cost handling, identical look-ahead guard,
identical reporting for every strategy. When the reporting is mechanical, the
Week 7 comparison table is trustworthy; when it is hand-made per strategy, it is
not.

## Run any strategy

```bash
python run_strategy.py configs/ma_crossover.json
python run_strategy.py configs/ts_momentum.json --folds 5
python run_strategy.py configs/distance_pairs.json --no-folds
```

Every run prints: gross/net tear sheet, turnover, total cost paid, walk-forward
folds (with embargo floored at the config's `lookahead_bars`), and two automatic
warnings — `OOS/IS < 0.5` and `Sharpe > 5`.

## Files

| Path | What |
|---|---|
| `strategies/base.py` | the contract: `DataBundle`, `StrategyConfig`, `run_strategy()` |
| `strategies/ma_crossover.py` | S01/S02 — trend following |
| `strategies/rsi_reversal.py` | S03 — stateful mean reversion |
| `strategies/bollinger_reversion.py` | S04 — band reversion, two exit modes |
| `strategies/donchian_breakout.py` | S05 — turtle breakout |
| `strategies/momentum.py` | S06/S07 — time-series and cross-sectional |
| `strategies/pairs.py` | S08/S16 — distance pairs, formation/trading split |
| `configs/` | one JSON per strategy + `config-schema.md` |
| `run_strategy.py` | one runner for all of them |

## Adding a strategy

1. Copy `strategies/ma_crossover.py`, rename.
2. Subclass `StrategyConfig` with your parameters.
3. Write `signal(data, cfg) -> DataFrame` using **only** data at or before each bar.
4. Add a config JSON.
5. Register it in `run_strategy.py::REGISTRY`.
6. Run the look-ahead audit from `templates/starter-notebook.ipynb` cell 3 on it.

## The rule that makes this phase work

**One config = one experiment.** Comparing two parameter sets means two config
files and two ledger rows, never one file edited in place. The Week 7 sweep
depends on this: if you have been overwriting configs, you do not know your N,
and if you do not know your N you cannot deflate your Sharpe.
