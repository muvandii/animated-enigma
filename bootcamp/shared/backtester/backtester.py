"""backtester.py — the smallest backtester that cannot lie to you.

Design constraints (do not violate these as you extend it):
  1. VECTORIZED, not event-driven. ~40 lines. You cannot hide a bug in 40 lines.
  2. LOOK-AHEAD IS IMPOSSIBLE: positions are `target.shift(1)`, enforced in one
     place, covered by test_backtester.py::test_no_lookahead_*.
  3. COSTS ARE NOT OPTIONAL. fee_bps and slippage_bps default to nonzero.
     A backtest with costs=0 is a fantasy and is not a valid artifact.
  4. No partial fills, no borrow costs, no market impact. Those live in Phase 2
     (02-engine). Ship the simple one first, then earn the complexity.

Position convention
    target: Series of desired exposure in "units of capital", e.g.
        0.0  = flat
        1.0  = fully long
       -1.0  = fully short
        0.5  = half-size long
    Leverage >1 is allowed by the math but forbidden by the course gate until
    Week 10. If |target| > 1 you must say so in the verdict.

Usage
    from backtester import backtest
    res = backtest(px, signal, fee_bps=1.0, slippage_bps=5.0)
    print(res.summary())
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

__all__ = [
    "CostModel",
    "BacktestResult",
    "backtest",
    "buy_and_hold",
    "walk_forward_splits",
    "purge_and_embargo",
]

BPS = 1.0 / 10_000.0


# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CostModel:
    """Round-trip costs, in basis points of traded notional.

    fee_bps      : commission + exchange fees. US equities ~0 on retail brokers,
                   but NOT zero in reality (spread/reg fees). Never set 0.
    slippage_bps : you cross the spread and you move small-cap books. 5 bps is a
                   sane default for liquid US large-caps, 10-20 for small-caps,
                   20-50 for crypto alts.
    borrow_bps   : annualised cost of short inventory, charged per day held short.
    """

    fee_bps: float = 1.0
    slippage_bps: float = 5.0
    borrow_bps: float = 50.0

    def per_trade_cost(self, dollar_traded: float) -> float:
        return abs(dollar_traded) * (self.fee_bps + self.slippage_bps) * BPS

    def carry_cost(self, short_notional: float, periods: int = 1) -> float:
        return abs(short_notional) * self.borrow_bps * BPS * periods / 252.0


@dataclass
class BacktestResult:
    """Everything needed to grade a strategy. Nothing else."""

    data: pd.DataFrame                      # position, gross_ret, cost, net_ret, equity
    cost_model: CostModel
    meta: dict = field(default_factory=dict)

    # ---- series views ---------------------------------------------------- #
    @property
    def position(self) -> pd.Series:
        return self.data["position"]

    @property
    def net_returns(self) -> pd.Series:
        return self.data["net_ret"]

    @property
    def gross_returns(self) -> pd.Series:
        return self.data["gross_ret"]

    @property
    def equity(self) -> pd.Series:
        return self.data["equity"]

    @property
    def trades(self) -> int:
        return int((self.data["position"].diff().abs() > 1e-12).sum())

    # ---- reporting ------------------------------------------------------- #
    def tear_sheet(self) -> dict:
        from metrics import tear_sheet  # sibling module; keep the import local

        ts = tear_sheet(self.net_returns, positions=self.position)
        ts["trades"] = self.trades
        # positive number = fraction of initial capital burned by costs
        ts["total_cost_paid"] = float(self.data["cost"].sum())
        ts["gross_sharpe"] = float(
            __import__("metrics").sharpe(self.gross_returns)
        )
        ts["cost_model"] = f"{self.cost_model.fee_bps}+{self.cost_model.slippage_bps} bps"
        ts.update(self.meta)
        return ts

    def summary(self, title: str = "BACKTEST") -> str:
        from metrics import format_tear_sheet

        ts = self.tear_sheet()
        body = format_tear_sheet(ts, title).split("\n")
        extra = [
            f"  trades            {ts['trades']:>8d}",
            f"  total cost paid   {ts['total_cost_paid'] * 100:8.2f}%",
            f"  gross Sharpe      {ts['gross_sharpe']:8.2f}",
            f"  cost model        {ts['cost_model']:>8s}",
            "=" * 46,
        ]
        return "\n".join(body[:-1] + extra)


# --------------------------------------------------------------------------- #
def backtest(
    prices: pd.Series,
    target: pd.Series,
    cost_model: CostModel | None = None,
    initial_cash: float = 10_000.0,
    allow_lookahead: bool = False,
) -> BacktestResult:
    """Run a long/short vectorized backtest.

    Parameters
    ----------
    prices : close (or adjusted close) Series, datetime-indexed.
    target : DESIRED position for each bar, decided at that bar's close.
             It is executed on the NEXT bar. This is the whole point.
    cost_model : CostModel; defaults to 1bp fee + 5bp slippage.
    allow_lookahead : NEVER pass True outside test_no_lookahead_makes_it_look_good.
                      It exists so the test suite can PROVE the guard matters.

    Notes
    -----
    Return on bar t   = position_decided_on_t_minus_1 * pct_change[t]
    Cost charged on t = |position[t] - position[t-1]| * (fee + slippage)
                        + borrow carry on any short notional held overnight
    """
    if not isinstance(prices, pd.Series) or not isinstance(target, pd.Series):
        raise TypeError("prices and target must be pandas Series")
    cm = cost_model or CostModel()

    px = prices.astype(float).sort_index()
    tgt = target.astype(float).reindex(px.index)

    # ---- THE look-ahead guard. One line. Do not touch. ------------------- #
    position = tgt if allow_lookahead else tgt.shift(1)
    position = position.fillna(0.0)

    asset_ret = px.pct_change().fillna(0.0)
    gross_ret = position * asset_ret

    # costs: trade cost on the bar the position changes + borrow on short book
    delta = position.diff().fillna(position)
    trade_cost = delta.abs() * (cm.fee_bps + cm.slippage_bps) * BPS
    short_notional = position.clip(upper=0).abs()
    carry = short_notional * cm.borrow_bps * BPS / 252.0
    cost = trade_cost + carry

    net_ret = gross_ret - cost
    equity = initial_cash * (1.0 + net_ret).cumprod()

    data = pd.DataFrame(
        {
            "price": px,
            "target": tgt,
            "position": position,
            "asset_ret": asset_ret,
            "gross_ret": gross_ret,
            "cost": cost,
            "net_ret": net_ret,
            "equity": equity,
        }
    )
    return BacktestResult(data=data, cost_model=cm,
                          meta={"initial_cash": initial_cash})


def buy_and_hold(prices: pd.Series, **kw) -> BacktestResult:
    """The only benchmark you need in Week 1. If you cannot beat this net of
    costs, the strategy is dead. Print it next to every tear sheet."""
    return backtest(prices, pd.Series(1.0, index=prices.index), **kw)


# --------------------------------------------------------------------------- #
# out-of-sample machinery
# --------------------------------------------------------------------------- #
def walk_forward_splits(
    index: pd.Index,
    n_splits: int = 5,
    train_frac: float = 0.6,
    embargo: int = 5,
) -> list[tuple[pd.Index, pd.Index]]:
    """Anchored walk-forward splits: (train, test) index pairs.

    Anchored = the train window always starts at index[0] and grows; the test
    window walks forward. That mirrors how you would actually have traded.

    embargo : bars dropped between train end and test start. Without it, a
              signal using t-1..t-20 leaks across the boundary (labels at the
              end of train peek at returns at the start of test).
    """
    if not 0 < train_frac < 1:
        raise ValueError("train_frac must be in (0, 1)")
    n = len(index)
    if n_splits < 1 or n < 10:
        raise ValueError("need n_splits >= 1 and at least 10 observations")

    splits: list[tuple[pd.Index, pd.Index]] = []
    test_size = max(int((n * (1 - train_frac)) / n_splits), 1)
    for k in range(n_splits):
        test_end = n - (n_splits - 1 - k) * test_size
        test_start = test_end - test_size
        train_end = test_start - embargo
        if train_end <= 10 or test_start < 0:
            continue  # not enough history for this fold; skip rather than lie
        splits.append((index[:train_end], index[test_start:test_end]))
    return splits


def purge_and_embargo(index: pd.Index, test_start, test_end, embargo: int = 5) -> pd.Index:
    """Drop [test_start - embargo, test_end + embargo] from a training index.
    Call this on ANY train set that will touch a labelled/overnight-return
    feature, or your 'out-of-sample' Sharpe is a lie you told yourself."""
    pos = pd.Series(np.arange(len(index)), index=index)
    lo = pos.index.searchsorted(test_start)
    hi = pos.index.searchsorted(test_end, side="right")
    drop = set(range(max(lo - embargo, 0), min(hi + embargo, len(index))))
    keep = [i for i in range(len(index)) if i not in drop]
    return index[keep]


# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-fetcher"))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "metrics-module"))
    from fetcher import fetch_synthetic

    px = fetch_synthetic("DEMO", periods=1500, seed=7)["close"]
    fast, slow = px.rolling(20).mean(), px.rolling(100).mean()
    sig = (fast > slow).astype(float)
    print(backtest(px, sig).summary("MA 20/100 CROSSOVER"))
    print(buy_and_hold(px).summary("BUY & HOLD"))
