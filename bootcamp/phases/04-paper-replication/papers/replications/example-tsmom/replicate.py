"""REPLICATION — Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum".

Fully worked example of what a replication looks like in this course:
    spec -> implementation -> results -> DELTA TABLE vs the paper

Run:  python replicate.py             # offline, seeded synthetic ETF universe
      python replicate.py --live      # tries to fetch real ETF data

The point is NOT to hit the paper's number. The point is to produce a number and
an honest explanation of the gap.

DELTA RULE: every gap bigger than 20% between your number and the paper's gets a
written cause. A replication that "matches" suspiciously well is a red flag.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _shared() -> Path:
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / "shared" / "backtester").is_dir():
            return p / "shared"
    return Path(__file__).resolve()


SHARED = _shared()
for _m in ("data-fetcher", "metrics-module", "backtester"):
    sys.path.insert(0, str(SHARED / _m))

from backtester import CostModel  # noqa: E402
from fetcher import fetch, fetch_synthetic  # noqa: E402
from metrics import tear_sheet, turnover  # noqa: E402

# --- Paper's parameters (spec.md) ------------------------------------------- #
LOOKBACK = 252          # 12 months
SKIP = 21               # skip most recent month (12-1)
TARGET_VOL = 0.40       # paper scales to 40% annualised vol per instrument
VOL_WINDOW = 126        # 6-month EWMA in the paper; we use a rolling window
REBALANCE = "ME"        # monthly
FEE_BPS, SLIP_BPS = 1.0, 5.0

# --- Paper's headline numbers (Table 2, TSMOM(12,1), equal-weight) ---------- #
PAPER = {
    "ann_return": 0.105,
    "sharpe": 0.95,
    "universe_size": 58,
    "asset_classes": 4,
    "sample": "1965-2009",
}

UNIVERSE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "LQD", "HYG", "GLD"]


# --------------------------------------------------------------------------- #
def load_universe(live: bool, periods: int = 2520, seed: int = 13):
    cols, src = {}, "synthetic"
    if live:
        try:
            for sym in UNIVERSE:
                cols[sym] = fetch(sym, source="stooq")["adj_close"]
            src = "stooq"
            px = pd.DataFrame(cols).dropna(how="all")
            return px.sort_index(), src
        except Exception as exc:
            print(f"[data] live fetch failed ({exc.__class__.__name__}); using synthetic")
    for i, sym in enumerate(UNIVERSE):
        # different vol/drift per symbol so the cross-section is not degenerate
        cols[sym] = fetch_synthetic(
            sym, start="2015-01-01", periods=periods, seed=seed + i,
            sigma=0.14 + 0.03 * (i % 5), mu=0.05 + 0.02 * (i % 3),
        )["close"]
    return pd.DataFrame(cols), src


def tsmom_signal(px: pd.DataFrame) -> pd.DataFrame:
    """w_t = sign(r_{t-12m .. t-1m}) x (target_vol / sigma_t), held one month.

    Look-ahead audit:
      - px.shift(21) / px.shift(252) - 1  uses data up to t-21 at the latest
      - sigma is a TRAILING rolling window (never centered)
      - the signal is shifted one more bar by the backtester before trading
      - positions are held constant between monthly rebalances
    """
    mom = px.shift(SKIP) / px.shift(LOOKBACK) - 1.0
    ret = px.pct_change()
    vol = ret.rolling(VOL_WINDOW, min_periods=40).std(ddof=1) * np.sqrt(252)
    raw = np.sign(mom) * (TARGET_VOL / vol.replace(0, np.nan))
    raw = raw.clip(-3.0, 3.0).fillna(0.0)
    # hold between month-end rebalances
    monthly = raw.resample(REBALANCE).last()
    return monthly.reindex(px.index).ffill().fillna(0.0)


def run(px: pd.DataFrame) -> dict:
    sig = tsmom_signal(px).reindex(columns=px.columns).fillna(0.0)
    pos = sig.shift(1).fillna(0.0)                       # THE guard
    ret = px.pct_change().fillna(0.0)
    n = len(px.columns)

    gross = (pos * ret).sum(axis=1) / n
    delta = pos.diff().fillna(pos)
    cost = (delta.abs() * (FEE_BPS + SLIP_BPS) / 1e4).sum(axis=1) / n
    net = gross - cost
    equity = 10_000 * (1 + net).cumprod()

    ts_net = tear_sheet(net, positions=delta.abs().sum(axis=1) / n)
    ts_gross = tear_sheet(gross)
    bh = tear_sheet(ret.sum(axis=1) / n)
    return {
        "gross": ts_gross, "net": ts_net, "bh": bh,
        "turnover": turnover(delta.abs().sum(axis=1) / n),
        "equity": equity, "net_ret": net,
        "n_symbols": n,
        "trades": int((delta.abs().sum(axis=1) > 1e-12).sum()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--periods", type=int, default=2520)
    args = ap.parse_args(argv)

    px, src = load_universe(args.live, periods=args.periods)
    r = run(px)

    print("=" * 66)
    print("  REPLICATION — Moskowitz/Ooi/Pedersen 'Time Series Momentum'")
    print("=" * 66)
    print(f"  data source        : {src}")
    print(f"  universe           : {r['n_symbols']} instruments")
    print(f"  sample             : {px.index[0].date()} -> {px.index[-1].date()}"
          f"  ({r['net']['years']:.1f} yrs)")
    print(f"  parameters         : lookback={LOOKBACK} skip={SKIP} "
          f"target_vol={TARGET_VOL} rebal={REBALANCE}")
    print(f"  costs              : {FEE_BPS} bps fee + {SLIP_BPS} bps slippage")
    print()
    print("-" * 66)
    print("  RESULTS")
    print("-" * 66)
    print(f"  gross annualised return : {r['gross']['cagr']*100:8.2f}%")
    print(f"  net   annualised return : {r['net']['cagr']*100:8.2f}%")
    print(f"  gross Sharpe            : {r['gross']['sharpe']:8.2f}")
    print(f"  net   Sharpe            : {r['net']['sharpe']:8.2f}")
    print(f"  max drawdown (net)      : {r['net']['max_drawdown']*100:8.2f}%")
    print(f"  annualised vol (net)    : {r['net']['ann_vol']*100:8.2f}%")
    print(f"  turnover/day            : {r['turnover']:8.4f}"
          f"   ({r['turnover']*252:.0f}/yr)")
    print(f"  rebalance events        : {r['trades']:8d}")
    print(f"  cost drag               : "
          f"{(r['gross']['cagr'] - r['net']['cagr'])*100:7.2f}%/yr")
    print()
    print("-" * 66)
    print("  DELTA TABLE vs the paper")
    print("-" * 66)
    rows = [
        ("annualised return", f"{PAPER['ann_return']*100:.1f}%",
         f"{r['gross']['cagr']*100:.1f}% (gross)", r['gross']['cagr'] / PAPER['ann_return']),
        ("Sharpe", f"{PAPER['sharpe']:.2f}", f"{r['gross']['sharpe']:.2f} (gross)",
         r['gross']['sharpe'] / PAPER['sharpe']),
        ("universe size", str(PAPER['universe_size']), str(r['n_symbols']),
         r['n_symbols'] / PAPER['universe_size']),
        ("asset classes", str(PAPER['asset_classes']), "1 (US-listed ETFs)",
         1 / PAPER['asset_classes']),
    ]
    print(f"  {'metric':<20}{'paper':>12}{'mine':>22}{'ratio':>10}  flag")
    for name, paper, mine, ratio in rows:
        flag = "" if 0.8 <= ratio <= 1.2 else "  <-- EXPLAIN (>20% gap)"
        print(f"  {name:<20}{paper:>12}{mine:>22}{ratio:>10.2f}{flag}")
    print()
    print("=" * 66)
    print("  VERDICT")
    print("=" * 66)
    reproduced = r['gross']['sharpe'] > 0
    print(f"  sign of the effect reproduced : {'YES' if reproduced else 'NO'}")
    print(f"  magnitude reproduced          : "
          f"{'NO' if abs(r['gross']['sharpe']/PAPER['sharpe'] - 1) > 0.2 else 'YES'}")
    print(f"  net of costs still positive   : {'YES' if r['net']['sharpe'] > 0 else 'NO'}")
    print()
    print("  This is a SUCCESSFUL replication if the sign reproduces and every")
    print("  magnitude gap has a written cause below. It is a FAILED replication")
    print("  if you changed the paper's rules to close the gap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
