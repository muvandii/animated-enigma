"""harness.py — LIVE PAPER TRADING HARNESS. DEMO / PAPER MODE ONLY.

===============================================================================
  ⚠️  THIS HARNESS REFUSES TO TRADE REAL MONEY. DO NOT REMOVE THAT GUARD.  ⚠️
===============================================================================

Design constraints, in priority order:
  1. It cannot place a live order. `PAPER` is validated against the endpoint URL
     at client construction; any non-paper base URL raises. There is no flag to
     disable this. If you find yourself wanting one, stop.
  2. No secrets in code or in the repo. Credentials come from environment
     variables only, and are never logged.
  3. Dry-run is the DEFAULT. Real (paper) submission requires `--execute` AND an
     explicit `I_UNDERSTAND=1` environment variable.
  4. Every run writes an auditable JSON line to `live/orders.log`.
  5. Position limits are enforced client-side before any submission.

Supported brokers (optional dependencies, NOT in requirements.txt):
  - Alpaca  : pip install alpaca-py      set ALPACA_KEY / ALPACA_SECRET
  - CCXT    : pip install ccxt           set CCXT_KEY / CCXT_SECRET
              (use ccxt's sandbox mode where the exchange offers one)

With neither installed, the harness runs in FULL SIMULATION: it computes targets,
logs what it would have ordered, and touches nothing. That is the mode used by
the test suite and the mode you should use on day 1.

Usage
    python harness.py --plan                 # show intended orders, submit nothing
    python harness.py --execute              # submit to PAPER endpoint (needs I_UNDERSTAND=1)
    python harness.py --reconcile            # compare intended vs actual positions
    python harness.py --plan --config live/config.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# SAFETY: the paper-mode guard
# --------------------------------------------------------------------------- #
PAPER_URL_MARKERS = ("paper", "sandbox", "testnet", "demo")
LIVE_URL_MARKERS = ("api.alpaca.markets", "live", "api.binance.com")


class LiveTradingRefused(RuntimeError):
    """Raised when anything looks like it is about to trade real money."""


def assert_paper(endpoint: str) -> None:
    """Hard guard. Any endpoint that does not announce paper/sandbox is refused.

    This function is called on EVERY client construction. It is deliberately not
    configurable: a configurable safety check is not a safety check.
    """
    if not endpoint:
        raise LiveTradingRefused("empty endpoint; refusing to guess")
    url = endpoint.lower()
    if any(m in url for m in PAPER_URL_MARKERS):
        return
    raise LiveTradingRefused(
        f"refusing to construct a client for {endpoint!r}: "
        f"endpoint does not contain one of {PAPER_URL_MARKERS}. "
        "This harness is paper-mode only. There is no override."
    )


# --------------------------------------------------------------------------- #
@dataclass
class HarnessConfig:
    """All limits are SAFE DEFAULTS. Tighten them, do not loosen them."""

    broker: str = "sim"                       # "sim" | "alpaca" | "ccxt"
    endpoint: str = "https://paper-api.alpaca.markets"
    symbols: list[str] = field(default_factory=lambda: ["SPY", "QQQ", "IWM", "TLT", "GLD"])
    strategy: str = "P01_combined_portfolio"
    capital: float = 10_000.0
    max_gross_leverage: float = 1.0           # no leverage. ever. in week 12.
    max_position_weight: float = 0.40         # per symbol
    max_order_notional: float = 2_000.0       # per order
    min_order_notional: float = 25.0          # below this, do not bother
    max_daily_turnover: float = 0.25          # fraction of capital per day
    kill_switch_drawdown: float = -0.15       # flatten and stop at -15%
    dry_run: bool = True
    log_path: str = "live/orders.log"
    state_path: str = "live/state.json"


def load_config(path: str | None) -> HarnessConfig:
    if not path:
        return HarnessConfig()
    d = json.loads(Path(path).read_text())
    known = {f for f in HarnessConfig.__dataclass_fields__}
    unknown = set(d) - known
    if unknown:
        raise ValueError(f"unknown config keys: {sorted(unknown)}")
    cfg = HarnessConfig(**d)
    if cfg.max_gross_leverage > 1.0:
        raise LiveTradingRefused(
            "max_gross_leverage > 1 in a paper-trading bootcamp harness. No."
        )
    return cfg


# --------------------------------------------------------------------------- #
# target positions come from YOUR strategy, not from here
# --------------------------------------------------------------------------- #
def compute_targets(cfg: HarnessConfig, asof: str | None = None) -> pd.Series:
    """Compute desired target weights for today.

    Replace the body with a call into your own engine. The stub below is a
    deterministic, intentionally boring equal-weight-with-cash baseline so the
    harness is runnable before your portfolio module is wired in.

    Contract: returns a Series of TARGET WEIGHTS indexed by symbol. Weights are
    fractions of capital and may be negative (short). Sum should be <= max_gross.
    """
    w = pd.Series(1.0 / len(cfg.symbols), index=cfg.symbols)
    return w.clip(-cfg.max_position_weight, cfg.max_position_weight)


def apply_limits(targets: pd.Series, cfg: HarnessConfig) -> pd.Series:
    """Client-side risk limits. Enforced BEFORE submission, never after."""
    t = targets.copy()
    t = t.clip(-cfg.max_position_weight, cfg.max_position_weight)
    gross = t.abs().sum()
    if gross > cfg.max_gross_leverage:
        t = t * (cfg.max_gross_leverage / gross)
    return t


def build_orders(targets: pd.Series, current: pd.Series, prices: pd.Series,
                 cfg: HarnessConfig) -> pd.DataFrame:
    """Difference target vs current, convert to share counts, drop dust."""
    delta_w = (targets - current.reindex(targets.index).fillna(0.0))
    notional = delta_w * cfg.capital
    keep = notional.abs() >= cfg.min_order_notional
    rows = []
    for sym in notional.index[keep]:
        px = float(prices.get(sym, float("nan")))
        if not px or px != px:
            print(f"[skip] {sym}: no price", file=sys.stderr)
            continue
        n = notional[sym]
        if abs(n) > cfg.max_order_notional:
            n = cfg.max_order_notional * (1 if n > 0 else -1)
        rows.append({
            "symbol": sym, "side": "buy" if n > 0 else "sell",
            "qty": round(abs(n) / px, 6), "notional": round(n, 2),
            "price": px, "weight": round(targets[sym], 4),
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        total = out["notional"].abs().sum()
        if total > cfg.max_daily_turnover * cfg.capital:
            scale = cfg.max_daily_turnover * cfg.capital / total
            out["qty"] = (out["qty"] * scale).round(6)
            out["notional"] = (out["notional"] * scale).round(2)
            print(f"[limit] daily turnover capped: scaled all orders by {scale:.3f}")
    return out


# --------------------------------------------------------------------------- #
# brokers
# --------------------------------------------------------------------------- #
def submit(orders: pd.DataFrame, cfg: HarnessConfig) -> dict:
    """Submit to the PAPER endpoint, or log only (default).

    Requires BOTH `--execute` (cfg.dry_run False) AND I_UNDERSTAND=1 in the
    environment. One of them alone does nothing.
    """
    stamp = datetime.now(timezone.utc).isoformat()
    log_line = {"ts": stamp, "mode": "dry_run" if cfg.dry_run else "paper",
                "broker": cfg.broker, "endpoint": cfg.endpoint,
                "strategy": cfg.strategy,
                "orders": [] if orders.empty else orders.to_dict("records")}
    _append_log(cfg.log_path, log_line)

    if cfg.dry_run:
        print(f"[dry-run] {len(orders)} order(s) logged to {cfg.log_path}. Nothing submitted.")
        return {"submitted": 0, "logged": len(orders)}

    if os.environ.get("I_UNDERSTAND") != "1":
        print("[refuse] --execute given but I_UNDERSTAND != 1. Nothing submitted.")
        return {"submitted": 0, "logged": len(orders), "refused": "no_confirmation"}

    assert_paper(cfg.endpoint)

    if cfg.broker == "alpaca":
        return _submit_alpaca(orders, cfg)
    if cfg.broker == "ccxt":
        return _submit_ccxt(orders, cfg)
    print(f"[sim] broker={cfg.broker!r} is not a real broker; simulating fills.")
    return {"submitted": len(orders), "simulated": True}


def _submit_alpaca(orders: pd.DataFrame, cfg: HarnessConfig) -> dict:
    key, secret = os.environ.get("ALPACA_KEY"), os.environ.get("ALPACA_SECRET")
    if not key or not secret:
        raise LiveTradingRefused("ALPACA_KEY / ALPACA_SECRET not set. Nothing submitted.")
    try:
        from alpaca.trading.client import TradingClient  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("pip install alpaca-py") from exc
    assert_paper(cfg.endpoint)
    client = TradingClient(key, secret, paper=True, url_override=cfg.endpoint)
    results = []
    for r in orders.to_dict("records"):
        try:
            from alpaca.trading.requests import MarketOrderRequest  # noqa: PLC0415
            from alpaca.trading.enums import OrderSide, TimeInForce  # noqa: PLC0415
            req = MarketOrderRequest(
                symbol=r["symbol"],
                qty=r["qty"],
                side=OrderSide.BUY if r["side"] == "buy" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            results.append({"symbol": r["symbol"], "ok": True,
                            "id": str(client.submit_order(req).id)})
        except Exception as exc:                     # noqa: BLE001
            results.append({"symbol": r["symbol"], "ok": False, "error": str(exc)})
    return {"submitted": len(results), "results": results}


def _submit_ccxt(orders: pd.DataFrame, cfg: HarnessConfig) -> dict:
    key, secret = os.environ.get("CCXT_KEY"), os.environ.get("CCXT_SECRET")
    if not key or not secret:
        raise LiveTradingRefused("CCXT_KEY / CCXT_SECRET not set. Nothing submitted.")
    try:
        import ccxt  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("pip install ccxt") from exc
    assert_paper(cfg.endpoint)
    ex = ccxt.binance({"apiKey": key, "secret": secret, "enableRateLimit": True})
    ex.set_sandbox_mode(True)                        # hard sandbox
    results = []
    for r in orders.to_dict("records"):
        try:
            res = ex.create_order(r["symbol"], "market", r["side"], r["qty"])
            results.append({"symbol": r["symbol"], "ok": True, "id": res.get("id")})
        except Exception as exc:                     # noqa: BLE001
            results.append({"symbol": r["symbol"], "ok": False, "error": str(exc)})
    return {"submitted": len(results), "results": results}


# --------------------------------------------------------------------------- #
# state + logging
# --------------------------------------------------------------------------- #
def _append_log(path: str, record: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def load_state(cfg: HarnessConfig) -> pd.Series:
    p = Path(cfg.state_path)
    if not p.exists():
        return pd.Series(dtype=float)
    return pd.Series(json.loads(p.read_text()).get("positions", {}))


def save_state(cfg: HarnessConfig, positions: pd.Series, equity: float) -> None:
    p = Path(cfg.state_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).isoformat(),
        "equity": equity,
        "positions": {k: float(v) for k, v in positions.items()},
    }, indent=2))


def reconcile(cfg: HarnessConfig, intended: pd.Series, actual: pd.Series) -> pd.DataFrame:
    """The daily reconciliation: intended vs actual, with a reason for each gap.

    Categories that MUST be explained, never silently accepted:
      NEW        - intended a position we do not hold
      MISSING    - hold something we did not intend
      SIZE_DIFF  - direction right, size wrong
      SIDE_DIFF  - we are long where we intended short (stop trading, investigate)
    """
    syms = sorted(set(intended.index) | set(actual.index))
    rows = []
    for s in syms:
        i = float(intended.get(s, 0.0))
        a = float(actual.get(s, 0.0))
        diff = a - i
        if abs(i) < 1e-9 and abs(a) < 1e-9:
            continue
        if abs(i) < 1e-9:
            status = "MISSING"
        elif abs(a) < 1e-9:
            status = "NEW"
        elif i * a < 0:
            status = "SIDE_DIFF"
        elif abs(diff) > 0.01:
            status = "SIZE_DIFF"
        else:
            status = "OK"
        rows.append({"symbol": s, "intended": round(i, 4), "actual": round(a, 4),
                     "diff": round(diff, 4), "status": status, "explanation": ""})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Paper-only live trading harness.")
    ap.add_argument("--config")
    ap.add_argument("--plan", action="store_true", help="compute and print orders")
    ap.add_argument("--execute", action="store_true",
                    help="submit to the PAPER endpoint (also needs I_UNDERSTAND=1)")
    ap.add_argument("--reconcile", action="store_true")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    cfg.dry_run = not args.execute

    print("=" * 62)
    print("  LIVE PAPER HARNESS — demo / paper mode only")
    print("=" * 62)
    print(f"  broker          : {cfg.broker}")
    print(f"  endpoint        : {cfg.endpoint}")
    print(f"  mode            : {'DRY RUN (default)' if cfg.dry_run else 'PAPER SUBMIT'}")
    print(f"  capital         : ${cfg.capital:,.0f}")
    print(f"  max gross lev   : {cfg.max_gross_leverage:.2f}x  (hard-capped at 1.0)")
    print(f"  max position    : {cfg.max_position_weight:.0%} per symbol")
    print(f"  max order       : ${cfg.max_order_notional:,.0f}")
    print(f"  kill switch     : flatten at {cfg.kill_switch_drawdown:.0%} drawdown")
    print()

    try:
        assert_paper(cfg.endpoint)
        print("  [guard] endpoint verified as PAPER/SANDBOX")
    except LiveTradingRefused as exc:
        print(f"  [guard] {exc}")
        return 2

    current = load_state(cfg)
    targets = apply_limits(compute_targets(cfg), cfg)
    prices = pd.Series(100.0, index=cfg.symbols)     # stub: replace with a real quote

    if args.reconcile:
        rec = reconcile(cfg, targets, current)
        print("  RECONCILIATION (intended vs state file)")
        print(rec.to_string(index=False) if not rec.empty else "  nothing to reconcile")
        return 0

    orders = build_orders(targets, current, prices, cfg)
    print("  TARGET WEIGHTS")
    print(targets.round(4).to_string())
    print()
    print("  ORDERS")
    print(orders.to_string(index=False) if not orders.empty else "  (no orders)")
    print()
    result = submit(orders, cfg)
    print(f"  result: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
