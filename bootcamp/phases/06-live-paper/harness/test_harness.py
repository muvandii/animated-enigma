"""Tests for harness.py — these are SAFETY tests, not feature tests.

If one of these fails, the harness may be about to trade real money. Do not
skip them to make a build green.

Run: pytest test_harness.py -v
"""

from __future__ import annotations

import json
import os

import pandas as pd
import pytest

from harness import (
    HarnessConfig,
    LiveTradingRefused,
    apply_limits,
    assert_paper,
    build_orders,
    compute_targets,
    load_config,
    reconcile,
    submit,
)


# --------------------------------------------------------------------------- #
# THE paper-mode guard
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("endpoint", [
    "https://paper-api.alpaca.markets",
    "https://testnet.binance.vision",
    "https://sandbox.example.com",
    "https://demo-api.broker.io",
])
def test_paper_endpoints_accepted(endpoint):
    assert_paper(endpoint)  # must not raise


@pytest.mark.parametrize("endpoint", [
    "https://api.alpaca.markets",          # live Alpaca
    "https://api.binance.com",             # live Binance
    "https://live-api.broker.io",
    "",                                    # empty -> refuse, never guess
])
def test_live_endpoints_refused(endpoint):
    with pytest.raises(LiveTradingRefused):
        assert_paper(endpoint)


def test_submit_refuses_live_endpoint_even_when_confirmed(monkeypatch, tmp_path):
    """This is the test that matters. Even with --execute AND I_UNDERSTAND=1,
    a live endpoint gets refused. There is no path from config to real money."""
    monkeypatch.setenv("I_UNDERSTAND", "1")
    cfg = HarnessConfig(endpoint="https://api.alpaca.markets", dry_run=False,
                        log_path=str(tmp_path / "orders.log"))
    orders = pd.DataFrame([{"symbol": "SPY", "side": "buy", "qty": 1.0,
                            "notional": 100.0, "price": 100.0, "weight": 0.1}])
    with pytest.raises(LiveTradingRefused):
        submit(orders, cfg)


def test_submit_requires_both_execute_and_confirmation(tmp_path):
    cfg = HarnessConfig(dry_run=False, log_path=str(tmp_path / "orders.log"))
    orders = pd.DataFrame([{"symbol": "SPY", "side": "buy", "qty": 1.0,
                            "notional": 100.0, "price": 100.0, "weight": 0.1}])
    if "I_UNDERSTAND" in os.environ:
        os.environ.pop("I_UNDERSTAND")
    result = submit(orders, cfg)
    assert result["submitted"] == 0
    assert result.get("refused") == "no_confirmation"


def test_dry_run_submits_nothing_and_still_logs(tmp_path):
    cfg = HarnessConfig(dry_run=True, log_path=str(tmp_path / "orders.log"))
    orders = pd.DataFrame([{"symbol": "SPY", "side": "buy", "qty": 1.0,
                            "notional": 100.0, "price": 100.0, "weight": 0.1}])
    result = submit(orders, cfg)
    assert result["submitted"] == 0 and result["logged"] == 1
    log = (tmp_path / "orders.log").read_text().strip().split("\n")
    assert len(log) == 1
    assert json.loads(log[0])["mode"] == "dry_run"


# --------------------------------------------------------------------------- #
# limits
# --------------------------------------------------------------------------- #


def test_leverage_is_capped_by_apply_limits():
    cfg = HarnessConfig(max_gross_leverage=1.0, max_position_weight=0.4)
    targets = pd.Series({"A": 1.5, "B": 1.5, "C": -1.5})
    out = apply_limits(targets, cfg)
    assert out.abs().sum() <= 1.0 + 1e-9
    assert out.abs().max() <= cfg.max_position_weight + 1e-9


def test_position_weight_cap_enforced():
    cfg = HarnessConfig(max_position_weight=0.25)
    out = apply_limits(pd.Series({"A": 0.9}), cfg)
    assert abs(out["A"]) <= 0.25 + 1e-9


def test_orders_below_min_notional_are_dropped():
    """$1 of drift should not generate an order; $100 should."""
    cfg = HarnessConfig(capital=10_000.0, min_order_notional=100.0)
    targets = pd.Series({"A": 0.5100, "B": 0.5001})   # +$100 and +$1 of drift
    current = pd.Series({"A": 0.5000, "B": 0.5000})
    prices = pd.Series({"A": 100.0, "B": 100.0})
    orders = build_orders(targets, current, prices, cfg)
    assert set(orders["symbol"]) == {"A"}       # $1 of drift is dust, not an order
    assert orders.iloc[0]["notional"] == pytest.approx(100.0)


def test_daily_turnover_is_capped():
    cfg = HarnessConfig(capital=10_000.0, max_daily_turnover=0.10,
                        min_order_notional=1.0)
    targets = pd.Series({"A": 1.0, "B": 0.0})
    current = pd.Series({"A": 0.0, "B": 1.0})
    prices = pd.Series({"A": 100.0, "B": 100.0})
    orders = build_orders(targets, current, prices, cfg)
    assert orders["notional"].abs().sum() <= 0.10 * cfg.capital + 1.0


def test_order_direction_matches_target():
    cfg = HarnessConfig(min_order_notional=1.0, max_daily_turnover=1.0)
    targets = pd.Series({"A": 0.5, "B": -0.5})
    orders = build_orders(targets, pd.Series(dtype=float),
                          pd.Series({"A": 100.0, "B": 100.0}), cfg)
    sides = dict(zip(orders["symbol"], orders["side"]))
    assert sides["A"] == "buy" and sides["B"] == "sell"


def test_missing_price_is_skipped_not_guessed():
    cfg = HarnessConfig(min_order_notional=1.0)
    targets = pd.Series({"A": 0.5})
    orders = build_orders(targets, pd.Series(dtype=float),
                          pd.Series({"A": float("nan")}), cfg)
    assert orders.empty


# --------------------------------------------------------------------------- #
# reconciliation
# --------------------------------------------------------------------------- #
def test_reconcile_classifies_every_gap():
    intended = pd.Series({"A": 0.2, "B": 0.0, "C": 0.3, "D": 0.1, "E": 0.0})
    actual = pd.Series({"A": 0.2, "B": 0.1, "C": 0.4, "D": 0.0, "E": 0.0})
    rec = reconcile(HarnessConfig(), intended, actual).set_index("symbol")
    assert rec.loc["A", "status"] == "OK"
    assert rec.loc["B", "status"] == "MISSING"     # hold, did not intend
    assert rec.loc["C", "status"] == "SIZE_DIFF"
    assert rec.loc["D", "status"] == "NEW"         # intended, do not hold
    assert "E" not in rec.index                    # both flat -> not a row


def test_reconcile_flags_side_mismatch():
    intended = pd.Series({"A": 0.2})
    actual = pd.Series({"A": -0.2})
    rec = reconcile(HarnessConfig(), intended, actual)
    assert rec.iloc[0]["status"] == "SIDE_DIFF"


def test_reconcile_has_an_explanation_column():
    rec = reconcile(HarnessConfig(), pd.Series({"A": 0.2}), pd.Series({"A": 0.4}))
    assert "explanation" in rec.columns
    assert (rec["explanation"] == "").all()   # blank == you have not done the work


# --------------------------------------------------------------------------- #
def test_defaults_are_safe():
    cfg = HarnessConfig()
    assert cfg.dry_run is True
    assert cfg.max_gross_leverage <= 1.0
    assert cfg.broker == "sim"


def test_compute_targets_respects_limits():
    cfg = HarnessConfig(symbols=["A", "B", "C", "D"], max_position_weight=0.4)
    t = compute_targets(cfg)
    assert len(t) == 4
    assert t.abs().max() <= 0.4 + 1e-9


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
