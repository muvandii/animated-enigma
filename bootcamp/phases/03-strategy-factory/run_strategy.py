"""run_strategy.py — execute any strategy from any config, identically.

    python run_strategy.py configs/ma_crossover.json
    python run_strategy.py configs/ts_momentum.json --compare-bh
    python run_strategy.py configs/donchian_breakout.json --folds 5

One runner for all six skeletons is the point: identical cost handling, identical
look-ahead guard, identical reporting, so the Week 7 comparison table is
mechanical rather than hand-assembled.

It also enforces the embargo rule: the walk-forward embargo can never be smaller
than the config's declared `lookahead_bars`.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "strategies"))

from base import StrategyConfig, load_data, run_strategy, to_positions  # noqa: E402


def _shared() -> Path:
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / "shared" / "backtester").is_dir():
            return p / "shared"
    return Path(__file__).resolve()


for _m in ("data-fetcher", "metrics-module", "backtester"):
    sys.path.insert(0, str(_shared() / _m))


# Map config `name` -> (module, config class). Add yours here.
REGISTRY = {
    "ma_crossover": ("ma_crossover", "MACrossoverConfig"),
    "rsi_reversal": ("rsi_reversal", "RSIConfig"),
    "bollinger_reversion": ("bollinger_reversion", "BollingerConfig"),
    "donchian_breakout": ("donchian_breakout", "DonchianConfig"),
    "momentum": ("momentum", "MomentumConfig"),
    "pairs": ("pairs", "PairsConfig"),
}


def resolve_strategy(name: str):
    """Find the strategy module from a config name like S06_ts_momentum."""
    for key, (mod, cls) in REGISTRY.items():
        if key in name:
            module = importlib.import_module(mod)
            return getattr(module, "signal"), getattr(module, cls)
    raise KeyError(f"no strategy registered for {name!r}; known: {list(REGISTRY)}")


def fold_table(signal_fn, cfg, cm_factory, n_splits=5, train_frac=0.6) -> pd.DataFrame:
    """Walk-forward with the embargo FLOORED at the config's lookahead_bars."""
    from backtester import backtest  # noqa: PLC0415
    from metrics import tear_sheet  # noqa: PLC0415

    data = load_data(cfg)
    px = data.close
    sig = to_positions(signal_fn(data, cfg)).reindex(columns=px.columns).fillna(0.0)
    embargo = max(5, cfg.lookahead_bars)
    rows = []
    sys.path.insert(0, str(_shared() / "backtester"))
    from backtester import walk_forward_splits  # noqa: PLC0415

    for i, (tr, te) in enumerate(walk_forward_splits(px.index, n_splits=n_splits,
                                                     train_frac=train_frac,
                                                     embargo=embargo), 1):
        seg = px.loc[te]
        s = sig.loc[te]
        ret = seg.pct_change().fillna(0.0)
        pos = s.shift(1).fillna(0.0)
        gross = (pos * ret).sum(axis=1) / max(len(px.columns), 1)
        delta = pos.diff().fillna(pos)
        cost = (delta.abs() * (cfg.fee_bps + cfg.slippage_bps) / 1e4).sum(axis=1) / max(len(px.columns), 1)
        net = gross - cost
        ts = tear_sheet(net)
        bh = (ret.sum(axis=1) / max(len(px.columns), 1))
        bh_ts = tear_sheet(bh)
        rows.append({"fold": i, "start": str(te[0].date()), "end": str(te[-1].date()),
                     "strat_sharpe": round(ts["sharpe"], 2),
                     "strat_cagr_%": round(ts["cagr"] * 100, 1),
                     "bh_cagr_%": round(bh_ts["cagr"] * 100, 1),
                     "max_dd_%": round(ts["max_drawdown"] * 100, 1)})
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run one strategy from one config.")
    ap.add_argument("config")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--no-folds", action="store_true")
    ap.add_argument("--offline", action="store_true", default=True)
    args = ap.parse_args(argv)

    cfg = StrategyConfig.from_json(args.config)
    signal_fn, cfg_cls = resolve_strategy(cfg.name)
    # re-parse into the strategy-specific dataclass so `params` become attributes
    raw = cfg.params
    typed = cfg_cls.from_json(args.config)
    typed.params = raw

    res = run_strategy(signal_fn, typed, offline=args.offline)
    print(res.summary(cfg.name.upper()))

    if not args.no_folds:
        folds = fold_table(signal_fn, typed, None, n_splits=args.folds)
        print()
        print(f"  WALK-FORWARD (embargo = max(5, lookahead_bars={typed.lookahead_bars}))")
        print(folds.to_string(index=False))
        ts = res.tear_sheet()
        oos = folds["strat_sharpe"].mean()
        if not np.isfinite(ts["sharpe"]) or abs(ts["sharpe"]) < 0.1:
            print(f"\n  mean OOS Sharpe {oos:+.2f}  vs IS net {ts['sharpe']:+.2f}"
                  f"   ratio n/a (IS Sharpe too close to zero for a ratio)")
        else:
            ratio = oos / ts["sharpe"]
            print(f"\n  mean OOS Sharpe {oos:+.2f}  vs IS net {ts['sharpe']:+.2f}   ratio {ratio:.2f}")
            if ratio < 0.5:
                print("  !! OOS/IS < 0.5: the in-sample result is not real. Log it.")
        if ts["sharpe"] > 5:
            print("  !! Sharpe > 5: assume look-ahead until proven otherwise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
