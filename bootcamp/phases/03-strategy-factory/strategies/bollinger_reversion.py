"""S04 — Bollinger band mean reversion.

THESIS: price oscillates around a locally-estimated mean, and excursions beyond
~2 sigma are mean-reverting because they are usually liquidity events, not
information events.

RULES: enter long when close < lower band; exit when close >= middle band
(stateful). Optional: exit after a fixed `hold_days` window instead — ALWAYS test
both, because if the result depends on the exit rule, the exit rule is the
strategy and you should admit that in the verdict.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class BollingerConfig(StrategyConfig):
    window: int = 20
    num_std: float = 2.0
    exit_mode: str = "mid"          # "mid" (stateful) | "fixed" (hold_days)
    hold_days: int = 5


def signal(data: DataBundle, cfg: BollingerConfig) -> pd.DataFrame:
    if cfg.exit_mode not in ("mid", "fixed"):
        raise ValueError("exit_mode must be 'mid' or 'fixed'")
    out = {}
    for sym in data.symbols:
        px = data.close[sym]
        mid = px.rolling(cfg.window).mean()
        sd = px.rolling(cfg.window).std(ddof=1)
        lower = mid - cfg.num_std * sd
        valid = sd.notna() & (sd > 0)

        if cfg.exit_mode == "fixed":
            sig = pd.Series(0.0, index=px.index)
            fired = (px < lower) & valid
            held = 0
            for i in range(1, len(px)):
                if held > 0:
                    held -= 1
                    sig.iloc[i] = 1.0
                elif fired.iloc[i - 1]:
                    held = cfg.hold_days
                    sig.iloc[i] = 1.0
            out[sym] = sig
        else:
            pos = pd.Series(0.0, index=px.index)
            long = False
            for i in range(1, len(px)):
                if not long and valid.iloc[i - 1] and px.iloc[i - 1] < lower.iloc[i - 1]:
                    long = True
                elif long and px.iloc[i - 1] >= mid.iloc[i - 1]:
                    long = False
                pos.iloc[i] = 1.0 if long else 0.0
            out[sym] = pos
    return pd.DataFrame(out, index=data.close.index)


if __name__ == "__main__":
    for mode in ("mid", "fixed"):
        cfg = BollingerConfig(name=f"S04_bollinger_{mode}",
                              symbols=["AAPL", "SPY", "IWM"],
                              lookahead_bars=1, warmup_bars=20,
                              params={"window": 20, "num_std": 2.0, "exit_mode": mode})
        print(run_strategy(signal, cfg).summary(f"BOLLINGER exit={mode}"))
        print()
