"""Tests for metrics.py. Offline, deterministic, <30s.

The point of these tests is not coverage — it is to pin down the DEFINITIONS so
you cannot quietly change a metric to make a dead strategy look alive.
Run: pytest test_metrics.py -v
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from metrics import (
    ann_vol,
    cagr,
    calmar,
    drawdown_series,
    format_tear_sheet,
    hit_rate,
    max_drawdown,
    returns,
    sharpe,
    sortino,
    tear_sheet,
    turnover,
)


@pytest.fixture
def idx():
    return pd.bdate_range("2018-01-01", periods=504)  # ~2 calendar years


@pytest.fixture
def flat(idx):
    return pd.Series(0.0, index=idx, name="ret")


# --------------------------------------------------------------------------- #
def test_returns_simple_and_log():
    p = pd.Series([100.0, 110.0, 99.0], index=pd.bdate_range("2020-01-01", periods=3))
    s = returns(p)
    assert len(s) == 2
    np.testing.assert_allclose(s.iloc[0], 0.10)
    np.testing.assert_allclose(s.iloc[1], -0.10)
    lg = returns(p, kind="log")
    np.testing.assert_allclose(lg.iloc[0], np.log(1.10))
    # log returns add up across time; simple returns do not
    np.testing.assert_allclose(lg.sum(), np.log(99 / 100), rtol=1e-12)


def test_returns_rejects_non_series():
    with pytest.raises(TypeError):
        returns([1, 2, 3])


def test_cagr_recovers_a_known_annual_rate(idx):
    """504 obs == 2.0 years by the 252/yr convention; compounding daily at
    (1.10)^(1/252)-1 must return exactly 10%/yr back."""
    daily = 1.10 ** (1 / 252) - 1
    r = pd.Series(daily, index=idx)
    assert cagr(r) == pytest.approx(0.10, abs=1e-9)


def test_cagr_short_sample_is_annualised_but_years_are_reported():
    """126 obs == 0.5 years. The annualised number is huge -- that is the point:
    the tear sheet prints BOTH total_return and years so you cannot fool yourself
    into thinking a 6-month sample is a 6-year track record."""
    half = pd.bdate_range("2020-01-01", periods=126)
    r = pd.Series(0.01, index=half)
    expected = (1.01 ** 126) ** (1 / 0.5) - 1
    assert cagr(r) == pytest.approx(expected, rel=1e-9)
    ts = tear_sheet(r)
    assert ts["years"] == pytest.approx(0.5)
    assert ts["total_return"] == pytest.approx(1.01 ** 126 - 1, rel=1e-9)


def test_cagr_total_wipeout_returns_minus_one():
    r = pd.Series([-1.0, 0.1], index=pd.bdate_range("2020-01-01", periods=2))
    assert cagr(r) == -1.0


def test_ann_vol_scales_with_sqrt_time(idx):
    daily_sd = 0.01
    r = pd.Series(daily_sd, index=idx)  # constant => sample sd = 0
    assert ann_vol(r) == pytest.approx(0.0)
    rng = np.random.default_rng(1)
    r2 = pd.Series(rng.normal(0, daily_sd, len(idx)), index=idx)
    assert ann_vol(r2) == pytest.approx(daily_sd * np.sqrt(252), rel=0.10)


def test_max_drawdown_sign_and_value():
    r = pd.Series([0.10, 0.10, -0.20, -0.10, 0.05],
                  index=pd.bdate_range("2020-01-01", periods=5))
    mdd = max_drawdown(r)
    assert mdd < 0
    # peak 1.21 -> trough 0.8712  => -28%
    assert mdd == pytest.approx(-0.28, abs=1e-6)


def test_drawdown_series_starts_at_zero_and_returns_to_zero():
    # equity: 0.90 -> 0.81 -> 1.053   peak: 0.90 -> 0.90 -> 1.053
    r = pd.Series([-0.10, -0.10, 0.30], index=pd.bdate_range("2020-01-01", periods=3))
    dd = drawdown_series(r)
    np.testing.assert_allclose(dd.iloc[0], 0.0, atol=1e-12)
    np.testing.assert_allclose(dd.iloc[1], -0.10, atol=1e-12)
    np.testing.assert_allclose(dd.iloc[-1], 0.0, atol=1e-12)  # new high
    assert dd.max() <= 0.0


def test_sharpe_zero_vol_is_nan_not_infinity(idx):
    assert np.isnan(sharpe(pd.Series(0.0001, index=idx)))


def test_sharpe_uses_cagr_over_vol_not_mean_over_std():
    """Pin the DEFINITION. Two conventions exist in the wild; this course uses
    (CAGR - rf) / ann_vol. This test fails loudly if anyone 'simplifies' it to
    mean/std and silently rewrites every historical verdict number."""
    idx = pd.bdate_range("2018-01-01", periods=504)
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0.0006, 0.013, len(idx)), index=idx)
    assert sharpe(r) == pytest.approx((cagr(r) - 0.0) / ann_vol(r), rel=1e-12)
    naive = r.mean() / r.std(ddof=1) * np.sqrt(252)
    assert sharpe(r) != pytest.approx(naive)  # they are genuinely different


def test_sharpe_penalises_volatility():
    idx = pd.bdate_range("2018-01-01", periods=504)
    # near-smooth 10%/yr compounding vs same drift with 2%/day noise
    smooth = pd.Series(1.10 ** (1 / 252) - 1 + 1e-6 * np.sin(np.arange(504)), index=idx)
    rng = np.random.default_rng(3)
    choppy = pd.Series(rng.normal(1.10 ** (1 / 252) - 1, 0.02, len(idx)), index=idx)
    assert sharpe(smooth) > sharpe(choppy)
    assert ann_vol(choppy) > 10 * ann_vol(smooth)  # the only thing that differs


def test_sortino_ignores_upside_vol():
    """Profitable but lopsided: +2% half the time, -1.9% half the time.
    Upside dispersion is not risk, so Sortino must beat Sharpe."""
    idx = pd.bdate_range("2020-01-01", periods=252)
    r = pd.Series([0.02] * 126 + [-0.019] * 126, index=idx)
    assert cagr(r) > 0            # guard: ratios only compare cleanly when > 0
    assert sortino(r) > sharpe(r) > 0


def test_calmar_relationship():
    idx = pd.bdate_range("2018-01-01", periods=504)
    rng = np.random.default_rng(11)
    r = pd.Series(rng.normal(0.0006, 0.012, len(idx)), index=idx)
    assert max_drawdown(r) < 0                      # guard: needs a real drawdown
    assert calmar(r) == pytest.approx(cagr(r) / abs(max_drawdown(r)), rel=1e-9)


def test_calmar_is_nan_when_never_in_drawdown():
    """A monotone money-printing curve has no drawdown. Calmar must say n/a --
    not infinity -- so a fantasy backtest cannot post Calmar = 99."""
    idx = pd.bdate_range("2018-01-01", periods=504)
    r = pd.Series(0.0005, index=idx)
    assert np.isnan(calmar(r))


def test_hit_rate_ignores_flat_days():
    r = pd.Series([0.0, 0.0, 0.0, 0.01, -0.01, 0.02])
    assert hit_rate(r) == pytest.approx(2 / 3)


def test_turnover():
    pos = pd.Series([0.0, 1.0, 1.0, -1.0, -1.0])
    # diffs: 1, 0, 2, 0 -> mean = 0.75
    assert turnover(pos) == pytest.approx(0.75)


def test_tear_sheet_keys_and_optional_turnover(idx):
    rng = np.random.default_rng(5)
    r = pd.Series(rng.normal(0.0003, 0.011, len(idx)), index=idx)
    ts = tear_sheet(r)
    for key in ("cagr", "ann_vol", "sharpe", "sortino", "max_drawdown",
                "calmar", "hit_rate", "total_return", "n_periods", "years"):
        assert key in ts
    assert "turnover" not in ts
    ts2 = tear_sheet(r, positions=pd.Series(1.0, index=idx))
    assert "turnover" in ts2


def test_tear_sheet_survives_empty_input():
    ts = tear_sheet(pd.Series(dtype=float))
    assert np.isnan(ts["sharpe"]) and ts["n_periods"] == 0
    assert isinstance(format_tear_sheet(ts, "EMPTY"), str)


def test_format_tear_sheet_prints_nan_as_na():
    txt = format_tear_sheet(tear_sheet(pd.Series(dtype=float)), "EMPTY")
    assert "n/a" in txt


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
