# Config schema

Every strategy is a config file + a signal function. Nothing else. That means the
parameter sweep in Week 7 is "loop over JSON files", not "edit six scripts".

Format: **JSON** (no PyYAML dependency). If you prefer YAML, it is a two-line
change in `strategies/base.py::from_json`, and `PyYAML` becomes your problem.

## Shared fields (required in every config)

| Field | Type | Meaning |
|---|---|---|
| `name` | string | matches the strategy folder name, e.g. `S06_ts_momentum` |
| `symbols` | list[str] | universe. **Membership must be knowable at `start`.** |
| `start` | ISO date | sample start |
| `periods` | int | bars (2520 ≈ 10 years) |
| `seed` | int | synthetic-data seed; ignored when real data is available |
| `fee_bps` | float | commission per unit traded |
| `slippage_bps` | float | half-spread + impact per unit traded |
| `borrow_bps` | float | ANNUALISED cost of short inventory |
| `lookahead_bars` | int | **longest forward window any feature uses.** Drives the walk-forward embargo. Understating it is a form of cheating. |
| `warmup_bars` | int | bars before the signal may trade |
| `params` | object | strategy-specific parameters (see below) |

## Per-strategy `params`

### ma_crossover
`fast` (int), `slow` (int), `trend_filter` (int|null), `allow_short` (bool)

### rsi_reversal
`period` (int), `entry` (float), `exit_thr` (float), `regime_filter` (int|null)

### bollinger_reversion
`window` (int), `num_std` (float), `exit_mode` ("mid"|"fixed"), `hold_days` (int)

### donchian_breakout
`entry_window` (int), `exit_window` (int), `allow_short` (bool)

### momentum
`mode` ("timeseries"|"crosssectional"), `lookback` (int), `skip` (int),
`vol_window` (int), `target_vol` (float), `rebalance` (pandas offset alias),
`long_frac` (float), `dollar_neutral` (bool)

### pairs
`formation_months` (int), `trading_months` (int), `n_pairs` (int),
`entry_z` (float), `exit_z` (float), `stop_z` (float), `max_hold` (int)

## Rules

1. **Never commit a config you tuned after seeing results without a note.** The
   config is part of the evidence. Commit the sweep, not just the winner.
2. **`lookahead_bars` is audited.** Week 7's `reports/parameter-sweep.md` checks
   that every config's embargo ≥ `lookahead_bars`.
3. **One config = one experiment.** If you want to compare two parameter sets,
   that is two config files and two rows in the ledger, not one file you edit in
   place.

## Sweep convention

A sweep is a directory of configs plus a manifest:

```
sweeps/2025-02-15-S06-momentum/
├── manifest.json      {"strategy": "momentum", "grid": {"lookback": [126,252,504], "skip": [0,21]}, "n_configs": 6}
├── 000.json ... 005.json
└── results.csv        one row per config: net Sharpe, OOS Sharpe, turnover, trades
```

The `results.csv` is what gets the deflated-Sharpe treatment in Week 7.
