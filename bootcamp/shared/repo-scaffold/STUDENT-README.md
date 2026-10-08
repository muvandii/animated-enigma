# quant-bootcamp — <your name>

Public, shareable record of a 13-week project-driven quant trading bootcamp.
16 strategies shipped, each with costs, out-of-sample results, and a written
verdict. Own backtester. 3 paper replications. 30 days of live paper trading.

**Everything here is research and paper trading. No real money was used.**

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                       # all tests must pass
python fetcher.py AAPL --out data/clean/aapl.parquet
python strategies/S01_ma_crossover/strategy.py
```

## Repo conventions

These are not style preferences. They are what make the repo auditable.

| Convention | Rule |
|---|---|
| Data | Never commit parquet. Fetch it. `data/raw/` is gitignored. |
| Costs | No backtest result is valid at zero cost. Default: 1 bp fee + 5 bp slippage. |
| Look-ahead | Signals are shifted by 1 bar. `tests/test_backtester.py` enforces it. |
| Sharpe > 5 | Requires a written investigation before you believe it. Usually look-ahead. |
| Secrets | Never committed. The live harness reads env vars and refuses to run in live mode. |
| Verdicts | Every strategy folder has a `verdict.md`. No verdict = not shipped. |

## Layout

```
data/          raw + cleaned parquet (gitignored)
strategies/    one folder per strategy: strategy.py, config.yaml, tearsheet.txt, verdict.md
engine/        your backtester, from Week 3
notes/         daily/ concepts/ strategies/ failures/   <- graded
papers/        dossiers/ replications/
live/          paper-trading log, reconciliation notebook, incidents
reports/       parameter sweeps, portfolio analysis
graveyard/     graveyard.md — required, structured, graded
journal/       lessons.md — appended at the end of every week
tests/         all *_test.py / test_*.py
```

Root-level modules: `fetcher.py`, `metrics.py`, `backtester.py` (+ tests in
`tests/`). These three are the only files you did not write yourself.

## Status

| Phase | Weeks | Status | Strategies |
|---|---|---|---|
| 01 Foundation | 1–2 | ☐ | 5 |
| 02 Engine | 3–4 | ☐ | 0 (re-verify 5) |
| 03 Strategy factory | 5–7 | ☐ | 8 |
| 04 Paper replication | 8–9 | ☐ | 3 |
| 05 Risk & portfolio | 10–11 | ☐ | portfolio |
| 06 Live paper | 12 | ☐ | 2–3 live |
| 07 Synthesis | 13 | ☐ | — |

Last updated: <!-- fill in -->
