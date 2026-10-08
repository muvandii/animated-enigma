"""S05 — Donchian channel breakout (the classic turtle rule).

THESIS: new 20-day highs attract trend-following capital and predict continuation
over weeks. Exit on the opposite 10-day extreme, which is deliberately tighter
than the entry so winners are given room and losers are cut.

FRAGILITY WARNING: breakout strategies concentrate their P&L in a handful of
months. Before shipping: remove the single best month and the single worst month
from the sample and report the Sharpe both ways. If removing one month kills it,
you do not have a strategy, you have a month.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class DonchianConfig(StrategyConfig):
    entry_window: int = 20
    exit_window: int = 10
    allow_short: bool = False


def signal(data: DataBundle, cfg: DonchianConfig) -> pd.DataFrame:
    out = {}
    for sym in data.symbols:
        px = data.close[sym]
        # shift(1) so the channel EXCLUDES today: today's high cannot set today's
        # breakout level, or you would trigger on yourself.
        upper = px.rolling(cfg.entry_window).max().shift(1)
        lower = px.rolling(cfg.exit_window).min().shift(1)
        pos = pd.Series(0.0, index=px.index)
        state = 0
        for i in range(1, len(px)):
            u, l, p = upper.iloc[i], lower.iloc[i], px.iloc[i]
            if pd.isna(u) or pd.isna(l):
                continue
            if state == 0 and p > u:
                state = 1
            elif state == 1 and p < l:
                state = 0
            pos.iloc[i] = float(state)
        if not cfg.allow_short:
            pos = pos.clip(lower=0.0)
        out[sym] = pos
    return pd.DataFrame(out, index=data.close.index)


if __name__ == "__main__":
    cfg = DonchianConfig(name="S05_donchian_breakout",
                         symbols=["AAPL", "SPY", "IWM", "QQQ", "XLK"],
                         lookahead_bars=1, warmup_bars=21,
                         params={"entry_window": 20, "exit_window": 10})
    print(run_strategy(signal, cfg).summary("DONCHIAN 20/10"))
