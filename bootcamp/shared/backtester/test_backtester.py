"""Tests for backtester.py.

These tests are the ENGINE GATE for Phase 2, pre-written. Most of them are
look-ahead and cost-honesty tests: they exist so that when your backtester gets
fancier in Weeks 3-4, it cannot quietly start cheating.

Run: pytest test_backtester.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "metrics-module"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data-fetcher"))

from backtester import (  # noqa: E402
    CostModel,
    backtest,
    buy_and_hold,
    purge_and_embargo,
    walk_forward_splits,
)
from fetcher import fetch_synthetic  # noqa: E402


@pytest.fixture
def px():
    return fetch_synthetic("TEST", periods=1000, seed=7)["close"]


@pytest.fixture
def alternating_signal(px):
    """Trades every other day -- maximum turnover, maximum cost pain."""
    return pd.Series(np.where(np.arange(len(px)) % 2 == 0, 1.0, -1.0), index=px.index)


# --------------------------------------------------------------------------- #
# look-ahead: the hill the whole course dies on
# --------------------------------------------------------------------------- #
def test_position_is_shifted_by_one_bar(px):
    sig = pd.Series(1.0, index=px.index)
    sig.iloc[:500] = 0.0
    res = backtest(px, sig)
    # target flips at bar 500; position must flip at bar 501
    assert res.position.iloc[500] == 0.0
    assert res.position.iloc[501] == 1.0


def test_peeking_signal_is_caught_by_an_absurd_sharpe(px):
    """THE test that matters. A signal built from tomorrow's return slips past
    the shift guard (the peek is inside the signal, not the shift), so the only
    reliable detector is the RESULT: Sharpe > 10 and 100x buy & hold.

    Course rule: any shipped strategy with Sharpe > 5 gets a failure note
    explaining where the future leaked, or it does not ship.
    """
    peek = np.sign(px.pct_change().shift(-1)).fillna(0.0)
    res = backtest(px, peek)
    ts = res.tear_sheet()
    assert ts["sharpe"] > 10, "peeking signal should print an impossible Sharpe"
    assert res.equity.iloc[-1] > buy_and_hold(px).equity.iloc[-1] * 100
    assert res.trades > len(px) * 0.3   # flips on roughly half of all bars


def test_legitimate_signal_stays_in_human_range(px):
    """Mirror image of the test above: a signal using only PAST data must not
    print an absurd Sharpe on the same data."""
    sig = (px.rolling(50).mean() > px.rolling(200).mean()).astype(float)
    assert backtest(px, sig).tear_sheet()["sharpe"] < 5


def test_shift_guard_is_not_a_noop(px):
    """allow_lookahead=True must change the answer -- otherwise the guard is
    decorative and every number it protects is unprotected."""
    sig = (px.rolling(20).mean() > px.rolling(100).mean()).astype(float)
    a = backtest(px, sig).net_returns
    b = backtest(px, sig, allow_lookahead=True).net_returns
    diff = (a - b).abs().sum()
    assert diff > 0.0, "shift guard had no effect"
    assert diff < 10.0, "a 1-bar shift should matter, but not by an order of magnitude"


def test_future_data_cannot_leak_into_past_returns(px):
    """Changing the FUTURE half of the price series must not change returns in
    the PAST half."""
    sig = pd.Series(1.0, index=px.index)
    a = backtest(px, sig)
    px2 = px.copy()
    px2.iloc[800:] *= 3.0            # rewrite the last 200 bars
    b = backtest(px2, sig)
    pd.testing.assert_series_equal(a.net_returns.iloc[:799], b.net_returns.iloc[:799])


# --------------------------------------------------------------------------- #
# costs
# --------------------------------------------------------------------------- #
def test_flat_position_earns_zero_and_costs_nothing(px):
    res = backtest(px, pd.Series(0.0, index=px.index))
    assert res.net_returns.abs().sum() == pytest.approx(0.0)
    assert res.equity.iloc[-1] == pytest.approx(res.equity.iloc[0])
    assert res.trades == 0


def test_costs_reduce_returns_monotonically(px, alternating_signal):
    zero = backtest(px, alternating_signal, cost_model=CostModel(0, 0, 0))
    low = backtest(px, alternating_signal, cost_model=CostModel(1, 1, 0))
    high = backtest(px, alternating_signal, cost_model=CostModel(10, 50, 0))
    assert zero.equity.iloc[-1] > low.equity.iloc[-1] > high.equity.iloc[-1]


def test_high_turnover_strategy_dies_on_costs(px, alternating_signal):
    """1000 bars of flipping every day at 10+50bps must be a catastrophic loss.
    If this passes with a profit, your cost model is decorative."""
    res = backtest(px, alternating_signal, cost_model=CostModel(10, 50, 0))
    assert res.equity.iloc[-1] < res.equity.iloc[0]
    assert res.tear_sheet()["total_cost_paid"] > 0.5   # >50% of capital burned


def test_costs_are_charged_when_position_changes_only(px):
    sig = pd.Series(0.0, index=px.index)
    res = backtest(px, sig, cost_model=CostModel(fee_bps=100, slippage_bps=100))
    assert res.data["cost"].abs().sum() == pytest.approx(0.0)


def test_short_pays_borrow_carry(px):
    long_ = backtest(px, pd.Series(1.0, index=px.index), cost_model=CostModel(0, 0, 0))
    short_ = backtest(px, pd.Series(-1.0, index=px.index), cost_model=CostModel(0, 0, 0))
    long_borrow = backtest(px, pd.Series(1.0, index=px.index), cost_model=CostModel(0, 0, 500))
    short_borrow = backtest(px, pd.Series(-1.0, index=px.index), cost_model=CostModel(0, 0, 500))
    assert long_.equity.iloc[-1] == pytest.approx(long_borrow.equity.iloc[-1])
    assert short_borrow.equity.iloc[-1] < short_.equity.iloc[-1]


# --------------------------------------------------------------------------- #
# mechanics
# --------------------------------------------------------------------------- #
def test_buy_and_hold_equity_matches_price_ratio(px):
    res = buy_and_hold(px, cost_model=CostModel(0, 0, 0))
    expected = 10_000.0 * (px.iloc[-1] / px.iloc[0])
    assert res.equity.iloc[-1] == pytest.approx(expected)


def test_inverse_position_approximately_inverts_return(px):
    up = backtest(px, pd.Series(1.0, index=px.index), cost_model=CostModel(0, 0, 0))
    dn = backtest(px, pd.Series(-1.0, index=px.index), cost_model=CostModel(0, 0, 0))
    # (1+r_long)(1+r_short) ~= 1 up to compounding; check the sign of total drift
    assert (up.gross_returns.sum() > 0) == (px.iloc[-1] > px.iloc[0])
    assert up.gross_returns.sum() * dn.gross_returns.sum() < 0


def test_rejects_non_series():
    with pytest.raises(TypeError):
        backtest([1, 2, 3], pd.Series([1.0, 1.0, 1.0]))


def test_result_has_tear_sheet_and_summary(px):
    res = buy_and_hold(px)
    ts = res.tear_sheet()
    for key in ("cagr", "sharpe", "max_drawdown", "trades", "gross_sharpe", "cost_model"):
        assert key in ts
    txt = res.summary("MA CROSSOVER")
    assert "MA CROSSOVER" in txt and "Sharpe" in txt and "cost model" in txt
    assert len(txt.split("\n")) > 12


# --------------------------------------------------------------------------- #
# walk-forward
# --------------------------------------------------------------------------- #
def test_walk_forward_splits_are_ordered_and_disjoint(px):
    splits = walk_forward_splits(px.index, n_splits=5, train_frac=0.6, embargo=5)
    assert len(splits) >= 3
    prev_test_end = None
    for train, test in splits:
        assert train[-1] < test[0], "embargo violated: train touches test"
        assert len(train) > 10
        if prev_test_end is not None:
            assert test[0] >= prev_test_end
        prev_test_end = test[-1]


def test_walk_forward_covers_the_tail(px):
    splits = walk_forward_splits(px.index, n_splits=4, train_frac=0.5)
    assert splits[-1][1][-1] == px.index[-1]


def test_walk_forward_rejects_bad_args(px):
    with pytest.raises(ValueError):
        walk_forward_splits(px.index, train_frac=1.5)
    with pytest.raises(ValueError):
        walk_forward_splits(px.index, n_splits=0)


def test_purge_and_embargo_removes_the_boundary(px):
    idx = px.index
    test_start, test_end = idx[500], idx[600]
    kept = purge_and_embargo(idx, test_start, test_end, embargo=10)
    assert test_start not in kept and test_end not in kept
    assert idx[490] not in kept and idx[610] not in kept   # embargoed neighbours
    assert idx[489] in kept and idx[611] in kept           # just outside the embargo
    assert idx[400] in kept and idx[800] in kept
    assert len(kept) == len(idx) - 121                     # 101 test + 2*10 embargo


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
