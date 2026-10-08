"""base.py — the contract every strategy in the factory obeys.

Why a contract: once all six skeletons expose the same `signal()` signature and
the same config object, ONE runner (`run_strategy.py`) can execute any of them,
which means the tear sheets are identical and the comparison table in Week 7 is
mechanical instead of hand-made.

The contract
------------
A strategy module defines:

    CONFIG : a dataclass of parameters (defaults are the "textbook" values)
    signal(data: DataBundle, cfg: CONFIG) -> pd.Series | pd.DataFrame

`signal()` returns DESIRED POSITIONS, decided at each bar's close, in units of
capital (-1.0 .. 1.0). The runner shifts by 1 before trading. `signal()` must
use only data available at or before each bar.

DataBundle is a dict-like with:
    close   : DataFrame (date x symbol)
    open    : DataFrame
    high    : DataFrame
    low     : DataFrame
    volume  : DataFrame
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Protocol

import pandas as pd


def _shared() -> Path:
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / "shared" / "backtester").is_dir():
            return p / "shared"
    return Path(__file__).resolve()


SHARED = _shared()
for _mod in ("data-fetcher", "metrics-module", "backtester"):
    sys.path.insert(0, str(SHARED / _mod))


# --------------------------------------------------------------------------- #
@dataclass
class DataBundle:
    """Everything a signal is allowed to see. No more, ever."""

    close: pd.DataFrame
    open: pd.DataFrame | None = None
    high: pd.DataFrame | None = None
    low: pd.DataFrame | None = None
    volume: pd.DataFrame | None = None

    @property
    def symbols(self) -> list[str]:
        return list(self.close.columns)

    def single(self) -> pd.Series:
        """Convenience for single-asset strategies."""
        if self.close.shape[1] != 1:
            raise ValueError(f"expected 1 symbol, got {self.close.shape[1]}")
        return self.close.iloc[:, 0]


@dataclass
class StrategyConfig:
    """Shared fields for every strategy. Subclass and add your own.

    `lookahead_bars` is NOT optional metadata: the runner uses it to set the
    walk-forward embargo. Understate it and your OOS number is a lie.
    """

    name: str
    symbols: list[str] = field(default_factory=lambda: ["AAPL"])
    start: str = "2015-01-01"
    periods: int = 2520
    seed: int = 13
    fee_bps: float = 1.0
    slippage_bps: float = 5.0
    borrow_bps: float = 50.0
    lookahead_bars: int = 1        # longest FORWARD window used by any feature
    warmup_bars: int = 0           # bars before the signal is allowed to trade
    params: dict[str, Any] = field(default_factory=dict)

    # ---- io ------------------------------------------------------------- #
    @classmethod
    def from_json(cls, path: str | Path) -> "StrategyConfig":
        d = json.loads(Path(path).read_text())
        params = d.pop("params", {})
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        return cls(params=params, **d)

    def to_json(self, path: str | Path) -> None:
        d = asdict(self)
        Path(path).write_text(json.dumps(d, indent=2) + "\n")


class Strategy(Protocol):
    def __call__(self, data: DataBundle, cfg: StrategyConfig) -> pd.Series | pd.DataFrame: ...


# --------------------------------------------------------------------------- #
def load_data(cfg: StrategyConfig, offline: bool = True) -> DataBundle:
    """Fetch (or synthesize) the configured universe.

    Uses the synthetic generator when offline so every skeleton is runnable on a
    plane and in CI. Each symbol gets a DIFFERENT seed so cross-sectional
    strategies see genuinely different series.
    """
    from fetcher import fetch_synthetic  # noqa: PLC0415

    cols = {}
    for i, sym in enumerate(cfg.symbols):
        px = fetch_synthetic(sym, start=cfg.start, periods=cfg.periods, seed=cfg.seed + i)
        cols[sym] = px["close"]
    close = pd.DataFrame(cols)
    close.index.name = "date"
    return DataBundle(close=close)


def to_positions(sig: pd.Series | pd.DataFrame) -> pd.DataFrame:
    """Normalize a signal into a (date x symbol) position frame, clipped to ±1."""
    if isinstance(sig, pd.Series):
        sig = sig.to_frame()
    return sig.clip(-1.0, 1.0).fillna(0.0)


def run_strategy(strategy: Strategy, cfg: StrategyConfig, offline: bool = True):
    """Execute one strategy on its config and return the BacktestResult.

    Multi-symbol: equal-weight across symbols, rebalanced to the target each bar.
    Costs are charged per symbol on that symbol's position change.
    """
    from backtester import CostModel, backtest  # noqa: PLC0415

    data = load_data(cfg, offline=offline)
    sig = to_positions(strategy(data, cfg))
    sig = sig.reindex(columns=data.symbols).fillna(0.0)

    cm = CostModel(fee_bps=cfg.fee_bps, slippage_bps=cfg.slippage_bps,
                   borrow_bps=cfg.borrow_bps)
    ret = data.close.pct_change().fillna(0.0)
    pos = sig.shift(1).fillna(0.0)                       # THE look-ahead guard
    gross = (pos * ret).sum(axis=1) / max(len(data.symbols), 1)
    delta = pos.diff().fillna(pos)
    cost = (delta.abs() * (cm.fee_bps + cm.slippage_bps) / 1e4).sum(axis=1) / max(len(data.symbols), 1)
    carry = (pos.clip(upper=0).abs() * cm.borrow_bps / 1e4 / 252).sum(axis=1) / max(len(data.symbols), 1)
    net = gross - cost - carry
    equity = 10_000 * (1 + net).cumprod()

    out = pd.DataFrame({"gross_ret": gross, "cost": cost + carry, "net_ret": net,
                        "equity": equity})

    class _Res:  # minimal shim so `summary()` works for both single & multi
        def __init__(self, df, cm, pos):
            self.data = df
            self.cost_model = cm
            self._pos = pos

        @property
        def position(self):
            return self._pos.abs().sum(axis=1)

        @property
        def net_returns(self):
            return self.data["net_ret"]

        @property
        def gross_returns(self):
            return self.data["gross_ret"]

        @property
        def equity(self):
            return self.data["equity"]

        @property
        def trades(self):
            return int((self._pos.diff().abs().sum(axis=1) > 1e-12).sum())

        def tear_sheet(self):
            from metrics import tear_sheet, sharpe, turnover  # noqa: PLC0415
            ts = tear_sheet(self.net_returns, positions=self.position)
            ts["trades"] = self.trades
            ts["total_cost_paid"] = float(self.data["cost"].sum())
            ts["gross_sharpe"] = float(sharpe(self.gross_returns))
            ts["cost_model"] = f"{self.cost_model.fee_bps}+{self.cost_model.slippage_bps} bps"
            ts["turnover"] = turnover(self.position)
            return ts

        def summary(self, title="STRATEGY"):
            from metrics import format_tear_sheet  # noqa: PLC0415
            ts = self.tear_sheet()
            body = format_tear_sheet(ts, title).split("\n")
            extra = [f"  trades            {ts['trades']:>8d}",
                     f"  total cost paid   {ts['total_cost_paid'] * 100:8.2f}%",
                     f"  gross Sharpe      {ts['gross_sharpe']:8.2f}",
                     f"  cost model        {ts['cost_model']:>8s}",
                     "=" * 46]
            return "\n".join(body[:-1] + extra)

    return _Res(out, cm, pos)
