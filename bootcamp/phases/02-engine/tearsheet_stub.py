"""tearsheet_stub.py — extend this into engine/reporting.py.

Contract: every strategy's `tearsheet.txt` is produced by this module, so every
tear sheet in the course has the same shape and can be compared mechanically.

Run:  python tearsheet_stub.py            # prints a demo tear sheet
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _shared():
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / "shared" / "backtester").is_dir():
            return p / "shared"
    return Path(__file__).resolve()


SHARED = _shared()
for mod in ("data-fetcher", "metrics-module", "backtester"):
    sys.path.insert(0, str(SHARED / mod))

from backtester import CostModel, backtest, buy_and_hold, walk_forward_splits  # noqa: E402
from fetcher import fetch_synthetic  # noqa: E402
from metrics import format_tear_sheet, tear_sheet, turnover  # noqa: E402


# --------------------------------------------------------------------------- #
def breakeven_table(turnover_yr: float, gross_cagr: float,
                    bps_grid=(0, 2, 5, 10, 25, 50, 100)) -> pd.DataFrame:
    """At what cost level does this strategy stop making money?"""
    rows = []
    for bps in bps_grid:
        drag = turnover_yr * bps / 10_000.0
        rows.append({
            "slippage_bps": bps,
            "annual_drag_%": round(drag * 100, 2),
            "net_cagr_%": round((gross_cagr - drag) * 100, 2),
            "survives": bool(gross_cagr - drag > 0),
        })
    return pd.DataFrame(rows)


def fold_table(prices, signal_fn, cost_model, n_splits=5,
               train_frac=0.6, embargo=5) -> pd.DataFrame:
    """Walk-forward results, one row per fold."""
    rows = []
    for i, (tr, te) in enumerate(walk_forward_splits(prices.index, n_splits=n_splits,
                                                     train_frac=train_frac,
                                                     embargo=embargo), 1):
        seg = prices.loc[te]
        res = backtest(seg, signal_fn(prices).reindex(te), cost_model=cost_model)
        bh = buy_and_hold(seg, cost_model=cost_model)
        ts = res.tear_sheet()
        rows.append({
            "fold": i,
            "start": str(te[0].date()),
            "end": str(te[-1].date()),
            "strat_sharpe": round(ts["sharpe"], 2),
            "strat_cagr_%": round(ts["cagr"] * 100, 1),
            "bh_cagr_%": round(bh.tear_sheet()["cagr"] * 100, 1),
            "max_dd_%": round(ts["max_drawdown"] * 100, 1),
            "trades": ts["trades"],
        })
    return pd.DataFrame(rows)


def monthly_table(returns: pd.Series) -> pd.DataFrame:
    """Year x month return grid. Read it for clustering: if all the return is in
    three months, the strategy is three months."""
    m = (1 + returns).resample("ME").prod() - 1
    grid = m.groupby([m.index.year, m.index.month]).sum().unstack()
    grid.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][: len(grid.columns)]
    return grid.round(4)


def full_tear_sheet(prices: pd.Series, signal_fn, name: str,
                    cost_model: CostModel | None = None,
                    n_splits: int = 5) -> str:
    """The one function every strategy calls. Returns a printable string."""
    cm = cost_model or CostModel()
    gross = backtest(prices, signal_fn(prices), cost_model=CostModel(0, 0, 0))
    net = backtest(prices, signal_fn(prices), cost_model=cm)
    bh = buy_and_hold(prices, cost_model=cm)
    folds = fold_table(prices, signal_fn, cm, n_splits=n_splits)
    to_yr = turnover(net.position) * 252
    g_ts, n_ts, b_ts = gross.tear_sheet(), net.tear_sheet(), bh.tear_sheet()

    L = []
    L.append(gross.summary(f"{name} — GROSS"))
    L.append("")
    L.append(net.summary(f"{name} — NET"))
    L.append("")
    L.append(bh.summary("BENCHMARK — BUY & HOLD"))
    L.append("")
    L.append(f"  turnover/yr            {to_yr:8.1f}")
    L.append(f"  cost drag/yr           {to_yr * (cm.fee_bps + cm.slippage_bps) / 1e4 * 100:8.2f}%")
    L.append(f"  Sharpe lost to costs   {g_ts['sharpe'] - n_ts['sharpe']:8.3f}")
    L.append("")
    L.append("  WALK-FORWARD")
    L.append(folds.to_string(index=False))
    L.append("")
    L.append(f"  mean OOS Sharpe        {folds['strat_sharpe'].mean():8.2f}"
             f"    (IS net {n_ts['sharpe']:+.2f}, ratio "
             f"{folds['strat_sharpe'].mean() / n_ts['sharpe'] if n_ts['sharpe'] else float('nan'):.2f})")
    L.append(f"  folds profitable       {int((folds['strat_sharpe'] > 0).sum())}/{len(folds)}")
    L.append("")
    L.append("  COST BREAK-EVEN (gross CAGR vs slippage)")
    L.append(breakeven_table(to_yr, g_ts["cagr"]).to_string(index=False))
    L.append("")
    L.append("  MONTHLY RETURNS")
    L.append(monthly_table(net.net_returns).to_string())
    return "\n".join(L)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    px = fetch_synthetic("DEMO", periods=2520, seed=13)["close"]
    sig = lambda p: (p.rolling(10).mean() > p.rolling(50).mean()).astype(float)
    print(full_tear_sheet(px, sig, "DEMO MA(10/50)", CostModel(1, 5, 50)))
