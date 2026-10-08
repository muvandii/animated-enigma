"""Tests for fetcher.py.

Design rule: the suite must pass in <30s with NO network access.
The two network tests are skipped unless BOOTCAMP_NET=1 is set.
Run:  pytest test_fetcher.py -v      (or: python -m pytest -q)
"""

from __future__ import annotations

import os
import socket

import numpy as np
import pandas as pd
import pytest

from fetcher import (
    COLUMNS,
    fetch_synthetic,
    fetch,
    load_parquet,
    normalize,
    save_parquet,
)

RUN_NET = os.environ.get("BOOTCAMP_NET") == "1"


def _has_net(host="stooq.com", port=443, timeout=2.0) -> bool:
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------- #
# offline tests (always run)
# --------------------------------------------------------------------------- #
def test_synthetic_is_deterministic():
    a = fetch_synthetic("TEST", periods=200, seed=42)
    b = fetch_synthetic("TEST", periods=200, seed=42)
    pd.testing.assert_frame_equal(a, b)


def test_synthetic_matches_contract():
    df = fetch_synthetic("TEST", periods=300, seed=1)
    assert list(df.columns) == COLUMNS
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert not df[["open", "high", "low", "close"]].isna().any().any()
    assert (df["close"] > 0).all()
    # high >= max(o,c) and low <= min(o,c) by construction
    assert (df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all()


def test_synthetic_calendar_matches_the_252_convention():
    """If synthetic bars arrive at 261/yr (raw bdate_range) but metrics.py
    annualises at 252/yr, every tear sheet overstates elapsed time. Guard the
    density so synthetic data behaves like a real US trading calendar."""
    df = fetch_synthetic("CAL", periods=2520, seed=5)
    years = (df.index[-1] - df.index[0]).days / 365.25
    bars_per_year = len(df) / years
    assert 245 <= bars_per_year <= 256, f"got {bars_per_year:.1f} bars/yr"
    assert df.index.dayofweek.max() < 5          # no weekends
    assert df.index.is_unique and df.index.is_monotonic_increasing


def test_synthetic_periods_is_exact():
    for n in (10, 253, 1000):
        assert len(fetch_synthetic("N", periods=n, seed=1)) == n


def test_normalize_renames_vendor_columns_and_sorts():
    raw = pd.DataFrame(
        {
            "Date": ["2020-01-03", "2020-01-02", "2020-01-02"],
            "Open": [1, 1, 1],
            "High": [2, 2, 2],
            "Low": [0.5, 0.5, 0.5],
            "Close": [1.5, 1.4, 1.45],
            "Volume": [10, 11, 12],
        }
    )
    out = normalize(raw, ticker="X")
    assert list(out.columns) == COLUMNS
    assert out.index.is_monotonic_increasing and out.index.is_unique
    # duplicate date collapses to the LAST row
    assert out.loc["2020-01-02", "close"] == 1.45
    assert out["adj_close"].equals(out["close"])  # backfilled when absent


def test_normalize_drops_bad_rows():
    raw = pd.DataFrame(
        {"Date": ["2020-01-02", "2020-01-03"], "Close": [np.nan, 5.0], "Volume": [1, 2]}
    )
    out = normalize(raw)
    assert len(out) == 1
    assert float(out["close"].iloc[0]) == 5.0


def test_parquet_roundtrip(tmp_path):
    df = fetch_synthetic("RT", periods=120, seed=3)
    path = save_parquet(df, tmp_path / "nested" / "rt.parquet")
    back = load_parquet(path)
    assert list(back.columns) == COLUMNS
    assert back.index.equals(df.index)
    np.testing.assert_allclose(back["close"].to_numpy(), df["close"].to_numpy())


def test_auto_falls_back_to_synthetic_offline(monkeypatch):
    """In a sandbox (no DNS) `auto` must degrade, not crash."""
    if _has_net():
        pytest.skip("machine has network; fallback path not exercised")
    df = fetch("AAPL", source="auto", start="2016-01-01", periods=400, seed=7)
    assert len(df) == 400
    assert df.attrs.get("ticker") == "AAPL"


def test_unknown_source_raises():
    with pytest.raises(ValueError):
        fetch("AAPL", source="bloomberg-terminal")


# --------------------------------------------------------------------------- #
# network tests (opt-in)
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not RUN_NET, reason="set BOOTCAMP_NET=1 to hit the live endpoint")
def test_stooq_live():
    df = fetch_stooq("AAPL")
    assert len(df) > 1000
    assert df.index.max() > pd.Timestamp("2020-01-01")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
