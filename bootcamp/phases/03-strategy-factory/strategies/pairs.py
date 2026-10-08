"""S08/S16 — Distance pairs (Gatev-Goetzmann-Rouwenhorst style).

THESIS: two assets with the same economic exposure have prices that are
cointegrated; the spread between them is stationary and reverts. Trade the
spread: short the outperformer, long the underperformer, unwind at convergence.

THREE-STAGE RULE (this is GGR, not a generic "correlation" trade):
  1. FORMATION (12 months): find pairs by minimum sum of squared deviations
     between normalized prices. Pick the top N pairs.
  2. TRADING (6 months): open when |spread| > entry_z, close when it reverts
     (|spread| < exit_z) or at a stop / time limit.
  3. OUT-OF-SAMPLE: the next 6 months, using pairs chosen in the prior formation
     window. Never re-select pairs using the trading period's data.

The most common error: forming pairs over the WHOLE sample including the trading
period. That is look-ahead and it is why so many published pairs results do not
replicate.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class PairsConfig(StrategyConfig):
    formation_months: int = 12
    trading_months: int = 6
    n_pairs: int = 5
    entry_z: float = 2.0
    exit_z: float = 0.5
    stop_z: float = 4.0
    max_hold: int = 60


def _z(x: pd.Series, window: int) -> pd.Series:
    mu = x.rolling(window, min_periods=max(window // 3, 5)).mean()
    sd = x.rolling(window, min_periods=max(window // 3, 5)).std(ddof=1)
    return (x - mu) / sd.replace(0, np.nan)


def _select_pairs(px: pd.DataFrame, n_pairs: int) -> list[tuple[str, str]]:
    """Minimum sum of squared deviations between NORMALIZED prices, computed on
    the FORMATION window only."""
    norm = px / px.iloc[0]
    scores = {}
    for a, b in combinations(px.columns, 2):
        scores[(a, b)] = float(((norm[a] - norm[b]) ** 2).sum())
    return sorted(scores, key=scores.get)[:n_pairs]


def signal(data: DataBundle, cfg: PairsConfig) -> pd.DataFrame:
    px = data.close
    pos = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    formation = cfg.formation_months * 21
    trading = cfg.trading_months * 21
    start = formation
    while start + trading <= len(px):
        form_end = start
        trade_end = min(start + trading, len(px))
        # pairs selected on data ending BEFORE the trading window opens
        pairs = _select_pairs(px.iloc[start - formation: form_end], cfg.n_pairs)
        window = px.iloc[:trade_end]
        for a, b in pairs:
            spread = np.log(window[a]) - np.log(window[b])
            z = _z(spread, formation)
            state = 0
            hold = 0
            for i in range(form_end, trade_end):
                zi = z.iloc[i]
                if not np.isfinite(zi):
                    continue
                if state == 0:
                    if zi > cfg.entry_z:
                        state, hold = -1, 0
                    elif zi < -cfg.entry_z:
                        state, hold = 1, 0
                else:
                    hold += 1
                    if abs(zi) < cfg.exit_z or abs(zi) > cfg.stop_z or hold > cfg.max_hold:
                        state = 0
                pos.iloc[i, px.columns.get_loc(a)] += 0.5 * state
                pos.iloc[i, px.columns.get_loc(b)] -= 0.5 * state
        start += trading
    return pos


if __name__ == "__main__":
    cfg = PairsConfig(name="S08_distance_pairs",
                      symbols=["AAPL", "MSFT", "SPY", "IWM", "QQQ", "XLK", "XLF", "XLE"],
                      lookahead_bars=1, warmup_bars=252,
                      params={"formation_months": 12, "trading_months": 6})
    print(run_strategy(signal, cfg).summary("DISTANCE PAIRS"))
