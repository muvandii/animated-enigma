"""S06/S07 — Time-series momentum and cross-sectional momentum.

S06 TIME-SERIES MOMENTUM (Moskowitz-Ooi-Pedersen style):
    sign of the trailing 12-1 month return sets the direction; size scales with
    the inverse of recent volatility. Each asset is judged against its OWN
    history.

S07 CROSS-SECTIONAL MOMENTUM:
    rank assets against EACH OTHER each rebalance date; long the top quintile,
    short the bottom. Direction is always relative; a market-wide crash is not a
    signal.

The critical difference: S06 can be flat in a bear market; S07 is always
invested (dollar-neutral if you short), so it is exposed to the *dispersion* of
returns, not their level. Report them separately. Never conflate them.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from base import DataBundle, StrategyConfig, run_strategy


@dataclass
class MomentumConfig(StrategyConfig):
    mode: str = "timeseries"        # "timeseries" | "crosssectional"
    lookback: int = 252             # 12 months
    skip: int = 21                  # skip the most recent month (1-1 avoidance)
    vol_window: int = 63            # vol estimate for scaling
    target_vol: float = 0.15        # annualised vol target
    rebalance: str = "ME"           # month-end
    long_frac: float = 0.2          # cross-sectional: top/bottom quantile
    dollar_neutral: bool = True


def _momentum_score(px: pd.DataFrame, lookback: int, skip: int) -> pd.DataFrame:
    """Total return over [t-lookback, t-skip]. The `skip` avoids the 1-month
    reversal effect and avoids trading on last month's microstructure."""
    return px.shift(skip) / px.shift(lookback) - 1.0


def _zscore(df: pd.DataFrame, window: int) -> pd.DataFrame:
    mu = df.rolling(window, min_periods=max(window // 2, 5)).mean()
    sd = df.rolling(window, min_periods=max(window // 2, 5)).std(ddof=1)
    return (df - mu) / sd.replace(0, np.nan)


def signal(data: DataBundle, cfg: MomentumConfig) -> pd.DataFrame:
    if cfg.mode not in ("timeseries", "crosssectional"):
        raise ValueError("mode must be 'timeseries' or 'crosssectional'")
    px = data.close
    ret = px.pct_change()
    vol = ret.rolling(cfg.vol_window, min_periods=20).std(ddof=1) * np.sqrt(252)
    mom = _momentum_score(px, cfg.lookback, cfg.skip)

    if cfg.mode == "timeseries":
        direction = np.sign(mom)
        raw = direction * (cfg.target_vol / vol.replace(0, np.nan))
        return raw.clip(-1.0, 1.0).fillna(0.0)

    # cross-sectional: rank within each row, then hold until the next rebalance
    raw = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    idx = pd.Series(px.index, index=px.index)
    period = idx.groupby(px.index.to_period(cfg.rebalance)).transform("first") \
        if cfg.rebalance else px.index
    for _, group in px.groupby(period):
        end = group.index[-1]
        scores = mom.loc[end]
        scores = _zscore(mom.loc[:end], cfg.vol_window).loc[end] if cfg.vol_window else scores
        if scores.notna().sum() < 2:
            continue
        n = max(int(len(scores.dropna()) * cfg.long_frac), 1)
        ranked = scores.dropna().sort_values()
        longs, shorts = ranked.index[-n:], ranked.index[:n]
        w = pd.Series(0.0, index=px.columns)
        w[longs] = 1.0 / n
        if cfg.dollar_neutral:
            w[shorts] = -1.0 / n
        raw.loc[group.index[0]:] = w  # hold until the next rebalance
    # vectorize the "hold through period" step cleanly
    raw = raw.where(raw != 0).ffill().fillna(0.0)
    vol_scale = (cfg.target_vol / vol.replace(0, np.nan)).clip(upper=1.0)
    return (raw * vol_scale).clip(-1.0, 1.0).fillna(0.0)


if __name__ == "__main__":
    syms = ["AAPL", "SPY", "IWM", "QQQ", "XLK"]
    for mode in ("timeseries", "crosssectional"):
        cfg = MomentumConfig(name=f"S0{'6' if mode == 'timeseries' else '7'}_{mode}_momentum",
                             symbols=syms, lookahead_bars=1, warmup_bars=252,
                             params={"mode": mode})
        print(run_strategy(signal, cfg).summary(f"MOMENTUM {mode}"))
        print()
