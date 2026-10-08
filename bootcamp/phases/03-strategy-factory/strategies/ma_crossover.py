"""S01/S02 — Moving-average crossover.

THESIS: trends persist for weeks because capital reallocates slowly (index
rebalancing, fund flows, analyst cascades). A fast/slow MA cross is the cheapest
expression of "be long when the short-term trend is up".

FALSIFIABLE CLAIM: the edge comes from the MIDDLE of sustained moves. Prediction:
removing the largest 5% of daily moves should destroy most of the excess return
(if instead it helps, the "edge" is tail-catching, not trend-following).

LOOK-AHEAD AUDIT: rolling(N).mean() at bar t uses bars t-N+1..t only. No global
statistics, no bfill, no shift(-1).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class MACrossoverConfig(StrategyConfig):
    fast: int = 10
    slow: int = 50
    trend_filter: int | None = None      # e.g. 200 -> require close > MA(200)
    allow_short: bool = False


def signal(data: DataBundle, cfg: MACrossoverConfig) -> pd.DataFrame:
    out = {}
    for sym in data.symbols:
        px = data.close[sym]
        fast_ma = px.rolling(cfg.fast).mean()
        slow_ma = px.rolling(cfg.slow).mean()
        sig = (fast_ma > slow_ma).astype(float)
        sig[slow_ma.isna()] = 0.0
        if cfg.trend_filter:
            tma = px.rolling(cfg.trend_filter).mean()
            sig = sig * (px > tma).astype(float)
            sig[tma.isna()] = 0.0
        if not cfg.allow_short:
            sig = sig.clip(lower=0.0)
        out[sym] = sig
    return pd.DataFrame(out, index=data.close.index)


if __name__ == "__main__":
    cfg = MACrossoverConfig(name="S01_ma_crossover", symbols=["AAPL"],
                            lookahead_bars=1, warmup_bars=50,
                            params={"fast": 10, "slow": 50})
    res = run_strategy(signal, cfg)
    print(res.summary(f"MA({cfg.fast}/{cfg.slow}) crossover"))
