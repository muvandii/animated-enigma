"""S03 — RSI(2) mean reversion.

THESIS: short-term oversold moves in liquid names revert within days because
liquidity provision is rewarded and panic selling exhausts itself. RSI(2) is a
cheap detector of a 2-day oversold condition.

ENTRY: RSI(2) < entry (default 10) -> long.
EXIT:  STATEFUL — hold until RSI(2) recovers above exit_thr (default 50).
The exit is stateful, so this is one of the few signals that needs a loop.
Ugly-and-correct beats elegant-and-wrong.

WARNING: expect turnover > 100/yr. Compute the break-even bps before you believe
any gross result.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class RSIConfig(StrategyConfig):
    period: int = 2
    entry: float = 10.0
    exit_thr: float = 50.0
    regime_filter: int | None = 200      # only take longs above MA(200), or None


def rsi(close: pd.Series, n: int = 2) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def signal(data: DataBundle, cfg: RSIConfig) -> pd.DataFrame:
    out = {}
    for sym in data.symbols:
        px = data.close[sym]
        r = rsi(px, cfg.period)
        above = pd.Series(True, index=px.index)
        if cfg.regime_filter:
            above = px > px.rolling(cfg.regime_filter).mean()
        pos = pd.Series(0.0, index=px.index)
        long = False
        for i in range(1, len(px)):
            if not long and r.iloc[i - 1] < cfg.entry and above.iloc[i - 1]:
                long = True
            elif long and r.iloc[i - 1] > cfg.exit_thr:
                long = False
            pos.iloc[i] = 1.0 if long else 0.0
        out[sym] = pos
    return pd.DataFrame(out, index=data.close.index)


if __name__ == "__main__":
    cfg = RSIConfig(name="S03_rsi2_reversal", symbols=["AAPL", "SPY", "IWM"],
                    lookahead_bars=1, warmup_bars=200,
                    params={"period": 2, "entry": 10, "exit_thr": 50})
    res = run_strategy(signal, cfg)
    print(res.summary("RSI(2) REVERSAL"))
