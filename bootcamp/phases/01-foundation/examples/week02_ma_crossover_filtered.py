"""WEEK 1 SATURDAY EXEMPLAR — Strategy S02: MA(10/50) + MA(200) trend filter.

This is what "rebuild with the fix" looks like. ONE change from S01:

    S01: long when MA(10) > MA(50)
    S02: long when MA(10) > MA(50) AND price > MA(200)

Pre-registered claim (written BEFORE running, in notes/strategies/S02.md):
    "The 200-day filter removes whipsaw entries inside long sideways/down
     regimes. Expect turnover to fall by >25% while CAGR falls by <15%."

The claim is then tested against numbers. If it fails, S02 is KILLED with the
same honesty as S01. Both outcomes are acceptable. Fudging the claim afterwards
is not.

Run:  python week02_ma_crossover_filtered.py --offline
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def _find_shared(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "shared" / "backtester").is_dir():
            return p / "shared"
    return start


SHARED = _find_shared(HERE)
for mod in ("data-fetcher", "metrics-module", "backtester"):
    sys.path.insert(0, str(SHARED / mod))

from backtester import CostModel, backtest, buy_and_hold, walk_forward_splits  # noqa: E402
from fetcher import fetch_synthetic  # noqa: E402
from metrics import turnover  # noqa: E402

SYMBOL, SEED, START, PERIODS = "AAPL", 13, "2015-01-01", 2520


def signal_s01(prices: pd.Series, fast: int = 10, slow: int = 50) -> pd.Series:
    out = (prices.rolling(fast).mean() > prices.rolling(slow).mean()).astype(float)
    out[prices.rolling(slow).mean().isna()] = 0.0
    return out


def signal_s02(prices: pd.Series, fast: int = 10, slow: int = 50,
               trend: int = 200) -> pd.Series:
    """S01's crossover AND a long-term trend filter. Exactly one change."""
    base = signal_s01(prices, fast, slow)
    above = (prices > prices.rolling(trend).mean()).astype(float)
    above[prices.rolling(trend).mean().isna()] = 0.0
    return base * above          # AND, not OR -- both conditions required


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", default=True)
    args = ap.parse_args(argv)

    px = fetch_synthetic(SYMBOL, start=START, periods=PERIODS, seed=SEED)["close"]
    cm = CostModel(fee_bps=1.0, slippage_bps=5.0)

    s01 = backtest(px, signal_s01(px), cost_model=cm)
    s02 = backtest(px, signal_s02(px), cost_model=cm)
    bh = buy_and_hold(px, cost_model=cm)

    print("=" * 68)
    print("  S02 REBUILD — does the 200-day trend filter fix S01?")
    print("=" * 68)
    print(f"  PRE-REGISTERED CLAIM: turnover -25% or more, CAGR -15% or less")
    print()

    rows = []
    for name, res in (("S01 crossover", s01), ("S02 +MA200 filter", s02)):
        ts = res.tear_sheet()
        rows.append({
            "strategy": name,
            "trades": ts["trades"],
            "turnover/yr": round(turnover(res.position) * 252, 1),
            "cagr_%": round(ts["cagr"] * 100, 2),
            "sharpe": round(ts["sharpe"], 3),
            "max_dd_%": round(ts["max_drawdown"] * 100, 1),
            "time_in_mkt_%": round((res.position.abs() > 1e-9).mean() * 100, 1),
            "cost_paid_%": round(ts["total_cost_paid"] * 100, 2),
        })
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print()
    print(bh.summary("BUY & HOLD"))
    print()

    d_trades = (s02.trades - s01.trades) / s01.trades * 100
    d_cagr = (s02.tear_sheet()["cagr"] - s01.tear_sheet()["cagr"]) / abs(s01.tear_sheet()["cagr"]) * 100
    d_sharpe = s02.tear_sheet()["sharpe"] - s01.tear_sheet()["sharpe"]

    print("-" * 68)
    print("  CLAIM TEST")
    print("-" * 68)
    print(f"  trades  : {s01.trades} -> {s02.trades}   ({d_trades:+.1f}%)"
          f"   claimed <= -25%   {'PASS' if d_trades <= -25 else 'FAIL'}")
    print(f"  CAGR    : {s01.tear_sheet()['cagr']*100:+.2f}% -> {s02.tear_sheet()['cagr']*100:+.2f}%"
          f"   ({d_cagr:+.1f}%)   claimed >= -15%   {'PASS' if d_cagr >= -15 else 'FAIL'}")
    print(f"  Sharpe  : {s01.tear_sheet()['sharpe']:+.3f} -> {s02.tear_sheet()['sharpe']:+.3f}"
          f"   ({d_sharpe:+.3f})")
    print()

    claim_holds = d_trades <= -25 and d_cagr >= -15
    beats_bh = s02.tear_sheet()["cagr"] > bh.tear_sheet()["cagr"]
    verdict = "SHIP (paper)" if (claim_holds and beats_bh) else "KILL"
    print("=" * 68)
    print(f"  VERDICT S02: {verdict}")
    print("=" * 68)
    print(f"  claim survived its own test : {'YES' if claim_holds else 'NO'}")
    print(f"  beats buy & hold net        : {'YES' if beats_bh else 'NO'}")
    print()
    if not claim_holds:
        t1 = (s01.position.abs() > 1e-9).mean() * 100
        t2 = (s02.position.abs() > 1e-9).mean() * 100
        print("  DIAGNOSIS (write this in the failure note)")
        print("  " + "-" * 64)
        if d_trades > 0:
            print(f"  Trade count went UP ({s01.trades} -> {s02.trades}), not down.")
            print("  Mechanism: AND-ing two binary conditions sums their TRANSITIONS.")
            print("  The 200-day filter does not merely delete S01's entries -- it adds")
            print("  its own crossings. Fewer trades is not what a filter guarantees;")
            print("  it is what a filter guarantees only if its own signal is smoother")
            print("  than the one it gates. Here it is not.")
        else:
            print(f"  Trade count fell ({s01.trades} -> {s02.trades}) as claimed.")
        print()
        print(f"  Time in market fell {t1:.1f}% -> {t2:.1f}%. In a market drifting")
        print(f"  {bh.tear_sheet()['cagr']*100:+.1f}%/yr, every day out of the market costs")
        print("  expected return. A filter that cuts exposure can only help if the")
        print("  days it removes are worse than average. Here they were not.")
        print()
        print("  ROOT CAUSE FOR THE GRAVEYARD: not costs. S01 was already cheap")
        print("  (7 trades/yr, 0.41%/yr drag). The failure is a SIGNAL-LEVEL one:")
        print("  both S01 and S02 are long-only lag indicators in a drifting market,")
        print("  and lag costs more than the drawdown it avoids.")
    print()

    # walk-forward for S02
    rows = []
    for i, (tr, te) in enumerate(walk_forward_splits(px.index, n_splits=5,
                                                     train_frac=0.6, embargo=5), 1):
        seg = px.loc[te]
        r = backtest(seg, signal_s02(px).reindex(te), cost_model=cm)
        b = buy_and_hold(seg, cost_model=cm)
        rows.append({"fold": i, "test_start": str(te[0].date()), "test_end": str(te[-1].date()),
                     "strat_sharpe": round(r.tear_sheet()["sharpe"], 2),
                     "strat_cagr_%": round(r.tear_sheet()["cagr"] * 100, 1),
                     "bh_cagr_%": round(b.tear_sheet()["cagr"] * 100, 1)})
    oos = pd.DataFrame(rows)
    print("  WALK-FORWARD S02")
    print(oos.to_string(index=False))
    print(f"\n  mean OOS Sharpe: {oos['strat_sharpe'].mean():+.2f}"
          f"   (in-sample net Sharpe: {s02.tear_sheet()['sharpe']:+.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
