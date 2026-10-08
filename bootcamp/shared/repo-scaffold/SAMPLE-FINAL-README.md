# quant-bootcamp — A. Student

> This is the **sample final README** — what your repo's front door should look
> like in Week 13. The one `bootstrap.sh` writes on Day 1 is deliberately
> plainer; replace it with something like this once you have results.

**13 weeks · 16 strategies shipped · 11 killed · 30 days live paper trading**
**All results are backtests and paper trading. No real money was used.**

---

## TL;DR

I built a backtester, shipped 16 strategies with costs and out-of-sample testing,
replicated 3 published papers, and ran the survivors in paper mode for 30 days.
**11 of 16 strategies died.** The dominant killer was transaction costs
interacting with turnover: strategies with a gross Sharpe above 0.9 produced a
*negative* net Sharpe purely because they traded 100+ times a year.

The most useful thing I learned was not about markets. It was that my gross
Sharpe and my net Sharpe are different random variables, and only one of them
exists in reality.

- **Full writeup:** [`capstone/writeup.md`](../../capstone/writeup-template.md)
- **Graveyard (11 entries):** [`graveyard/graveyard.md`](../../shared/repo-scaffold/graveyard.md)
- **Notes vault (147 notes):** `NOTES.md`

---

## Run it

```bash
git clone <this-repo> && cd quant-bootcamp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pytest -q                                  # 63 tests, all green
python fetcher.py SPY --out data/clean/spy.parquet   # fetch data (or use --source synthetic)
python strategies/S05_donchian_breakout/strategy.py  # run a surviving strategy
python run_strategy.py configs/ts_momentum.json      # or run any config
```

Everything runs offline: if the network is unavailable, `fetcher.py` falls back
to a deterministic synthetic twin so every example and test still works.

## Layout

```
data/           raw + cleaned parquet (gitignored — fetch, don't commit)
strategies/     16 folders: strategy.py, config.json, tearsheet.txt, verdict.md
engine/         my event-driven backtester: 63 tests, 8 look-ahead detectors
notes/          daily/ concepts/ strategies/ failures/  — 147 notes
papers/         dossiers/ + replications/ with delta tables
live/           30-day paper log, reconciliation.csv, incidents.md
reports/        parameter sweeps, cost break-evens, portfolio construction
graveyard/      11 killed strategies, each with a root cause
journal/        13 weekly entries
```

## Results

### The scoreboard (abridged — full table in the writeup)

| ID | Strategy | Trades/yr | Gross SR | Net SR | OOS SR | Verdict |
|---|---|---|---|---|---|---|
| S01 | MA(10/50) | 7 | +0.21 | +0.19 | +0.08 | KILL |
| S02 | MA + MA200 filter | 10 | +0.07 | +0.05 | −0.17 | KILL |
| S03 | RSI(2) reversal | 118 | +0.94 | −0.21 | −0.34 | KILL |
| S04 | Bollinger reversion | 64 | +0.55 | +0.22 | +0.11 | KILL |
| S05 | Donchian 20/10 | 22 | +0.61 | +0.48 | +0.41 | **SHIP** |
| ... | | | | | | |

**Best net Sharpe: 0.48. Deflated for 16 strategies tested: 0.30.**
**95% CI on that estimate: ±0.35.** I do not claim it is different from zero.

### What killed the most strategies

1. **Costs × turnover (5 kills).** S03 had the best gross Sharpe of the entire
   course (+0.94) and the worst net (−0.21). The gap is 1.15 of Sharpe, entirely
   explained by 118 trades/yr at 6 bps.
2. **No out-of-sample stability (3 kills).** OOS/IS ratios of 0.4, 0.5, 0.4.
3. **Wrong mechanism (3 kills).** I predicted costs would kill S01; costs were
   0.03 of Sharpe. The signal simply had no edge. Writing that failure note
   changed how I diagnose everything after it.

### Replications

| Paper | Their SR | My SR | Ratio | Dominant cause |
|---|---|---|---|---|
| TSMOM (MOP 2012) | 0.95 | 0.09 | 0.10 | Universe: 10 correlated ETFs vs 58 instruments across 4 asset classes |
| Vol-managed momentum | 1.04 | 0.61 | 0.59 | Sample has fewer momentum crashes to avoid |
| Distance pairs (GGR 2006) | ~1.10 | 0.22 | 0.20 | Candidate pool: 28 pairs vs ~500,000 |

None reproduced in magnitude. All reproduced in sign. I explain every gap > 20%
in `papers/replications/*/delta-table.md`.

### Live paper (30 days)

- Realized slippage **14 bps** vs the **5 bps** my backtests assumed (2.8×).
- Consequence: I restated 4 verdicts. Two survivors became marginal.
- Unexplained reconciliation gaps: **0**.
- Incidents: 6, all with root causes and a control added for each.

## What I would tell someone starting this

Compute turnover **before** you backtest. It takes two minutes, and it would have
saved me five dead strategies and about thirty hours.

## Disclaimer

Educational project. Paper trading only. Nothing here is investment advice, and
every number in this repository is a backtest or a paper fill — neither of which
is a promise about the future.
