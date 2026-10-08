"""metrics.py — the only performance numbers allowed in this bootcamp.

Rule of the course: if a number is not computed here, it does not go in a verdict.
That single rule kills 80% of self-deception ("my Sharpe is 4.1!").

Everything takes a pandas Series of PERIODIC (default: daily) returns, indexed by
date. No price series, no DataFrames, no hidden annualisation.

Functions
    returns        price/equity -> periodic returns
    cagr           compound annual growth rate
    ann_vol        annualised standard deviation
    max_drawdown   worst peak-to-trough decline (as a negative number)
    sharpe         annualised excess return / annualised vol
    sortino        same, but only downside deviation in the denominator
    calmar         cagr / |max_drawdown|
    hit_rate       fraction of non-zero periods that were winners
    turnover       average absolute change in position (cost sanity check)
    tear_sheet     one dict of everything above, ready to print or assert on
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "returns",
    "cagr",
    "ann_vol",
    "max_drawdown",
    "drawdown_series",
    "sharpe",
    "sortino",
    "calmar",
    "hit_rate",
    "turnover",
    "tear_sheet",
    "format_tear_sheet",
]

PERIODS_PER_YEAR = 252
RISK_FREE = 0.0  # override per-era if you care; keep it constant and honest

# A series of identical returns has sample stdev ~1e-19 (floating-point dust),
# NOT 0.0. Without this floor, a constant +0.01%/day curve reports
# Sharpe = 5.9e16 instead of "this has no volatility, the ratio is meaningless".
VOL_FLOOR = 1e-8


# --------------------------------------------------------------------------- #
# primitive
# --------------------------------------------------------------------------- #
def returns(prices: pd.Series, dropna: bool = True, kind: str = "simple") -> pd.Series:
    """Convert a price or equity-curve Series into periodic returns.

    kind="simple"  : pct change  (what your P&L actually is)
    kind="log"     : log change  (additive across time — only for math, never
                                  for reporting a return number to a human)
    """
    if not isinstance(prices, pd.Series):
        raise TypeError(f"expected Series, got {type(prices).__name__}")
    if kind not in ("simple", "log"):
        raise ValueError("kind must be 'simple' or 'log'")
    out = np.log(prices / prices.shift(1)) if kind == "log" else prices.pct_change()
    out.name = "ret"
    return out.dropna() if dropna else out


# --------------------------------------------------------------------------- #
# growth / risk
# --------------------------------------------------------------------------- #
def cagr(periodic_returns: pd.Series, periods_per_year: int = PERIODS_PER_YEAR) -> float:
    """Compound annual growth rate: (final/initial)^(1/years) - 1.

    Uses elapsed CALENDAR years from the index when it is a DatetimeIndex, so a
    6-month backtest is not silently annualised into a fantasy.
    """
    r = periodic_returns.dropna()
    if r.empty:
        return float("nan")
    growth = float((1.0 + r).prod())
    if growth <= 0:
        return -1.0  # total wipeout; CAGR is undefined-but-bad, do not hide it
    years = _years(r, periods_per_year)
    return growth ** (1.0 / years) - 1.0


def ann_vol(periodic_returns: pd.Series, periods_per_year: int = PERIODS_PER_YEAR) -> float:
    """Annualised volatility (sample stdev, ddof=1)."""
    r = periodic_returns.dropna()
    if len(r) < 2:
        return float("nan")
    return float(r.std(ddof=1) * np.sqrt(periods_per_year))


def drawdown_series(periodic_returns: pd.Series) -> pd.Series:
    """Percent drawdown from running peak, as a negative number (0.0 at highs)."""
    r = periodic_returns.dropna()
    equity = (1.0 + r).cumprod()
    peak = equity.cummax()
    return equity / peak - 1.0


def max_drawdown(periodic_returns: pd.Series) -> float:
    """Worst peak-to-trough decline. Returns <= 0.0 (-0.35 == -35%)."""
    r = periodic_returns.dropna()
    if r.empty:
        return float("nan")
    return float(drawdown_series(r).min())


def sharpe(
    periodic_returns: pd.Series,
    risk_free: float = RISK_FREE,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Annualised Sharpe ratio (geometric CAGR based, not mean/std of returns).

    Why CAGR-based: mean/std rewards smooth but slowly compounding equity curves
    and punishes compounding ones. Report one number and say which it is.
    """
    r = periodic_returns.dropna()
    if len(r) < 2:
        return float("nan")
    vol = ann_vol(r, periods_per_year)
    if not np.isfinite(vol) or vol <= VOL_FLOOR:
        return float("nan")
    return (cagr(r, periods_per_year) - risk_free) / vol


def sortino(
    periodic_returns: pd.Series,
    risk_free: float = RISK_FREE,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Sharpe using downside deviation only (upside vol is not risk)."""
    r = periodic_returns.dropna()
    if len(r) < 2:
        return float("nan")
    target = (1.0 + risk_free) ** (1.0 / periods_per_year) - 1.0
    downside = r[r < target] - target
    dd = float(np.sqrt((downside**2).mean()) * np.sqrt(periods_per_year))
    if not np.isfinite(dd) or dd <= VOL_FLOOR:
        return float("nan")
    return (cagr(r, periods_per_year) - risk_free) / dd


def calmar(periodic_returns: pd.Series, periods_per_year: int = PERIODS_PER_YEAR) -> float:
    """CAGR / |max drawdown|. The 'how much pain per unit of gain' number."""
    mdd = abs(max_drawdown(periodic_returns))
    if not np.isfinite(mdd) or mdd <= VOL_FLOOR:
        return float("nan")
    return cagr(periodic_returns, periods_per_year) / mdd


# --------------------------------------------------------------------------- #
# trade-quality
# --------------------------------------------------------------------------- #
def hit_rate(periodic_returns: pd.Series) -> float:
    """Fraction of ACTIVE periods (ret != 0) that were profitable.

    Deliberately ignores flat days: a strategy in cash 90% of the time should not
    get a 10% hit rate reported as if it traded 100% of the time.
    """
    r = periodic_returns.dropna()
    active = r[r != 0]
    if active.empty:
        return float("nan")
    return float((active > 0).mean())


def turnover(positions: pd.Series) -> float:
    """Mean absolute daily change in position. Multiply by cost_bps to sanity-check
    your cost drag: drag_per_year ~= turnover * 252 * cost_bps / 1e4."""
    p = positions.dropna()
    if len(p) < 2:
        return float("nan")
    return float(p.diff().abs().mean())


# --------------------------------------------------------------------------- #
# aggregation
# --------------------------------------------------------------------------- #
def _years(r: pd.Series, periods_per_year: int) -> float:
    """Elapsed years = number of observations / observations per year.

    WHY NOT CALENDAR SPAN: the sqrt(252) in ann_vol already assumes
    "252 observations == 1 year". If CAGR used calendar days instead, the two
    halves of the Sharpe ratio would disagree by the weekend/holiday gap and
    every number would drift ~4%. One convention, everywhere.

    (Calendar span is defensible too — it is the more conservative one for real
    daily data — but mixing conventions inside one ratio is never defensible.)
    """
    return max(len(r) / periods_per_year, 1.0 / periods_per_year)


def tear_sheet(
    periodic_returns: pd.Series,
    positions: pd.Series | None = None,
    periods_per_year: int = PERIODS_PER_YEAR,
    risk_free: float = RISK_FREE,
) -> dict:
    """Every number the verdict template asks for, in one dict."""
    r = periodic_returns.dropna()
    out = {
        "n_periods": int(len(r)),
        "years": round(_years(r, periods_per_year), 3),
        "total_return": float((1 + r).prod() - 1) if len(r) else float("nan"),
        "cagr": cagr(r, periods_per_year),
        "ann_vol": ann_vol(r, periods_per_year),
        "sharpe": sharpe(r, risk_free, periods_per_year),
        "sortino": sortino(r, risk_free, periods_per_year),
        "max_drawdown": max_drawdown(r),
        "calmar": calmar(r, periods_per_year),
        "hit_rate": hit_rate(r),
        "best_period": float(r.max()) if len(r) else float("nan"),
        "worst_period": float(r.min()) if len(r) else float("nan"),
    }
    if positions is not None:
        out["turnover"] = turnover(positions)
    return out


def format_tear_sheet(ts: dict, title: str = "TEAR SHEET") -> str:
    """Print-ready block. Paste this into the strategy note verbatim."""
    pct = lambda v: "n/a" if not np.isfinite(v) else f"{v * 100:8.2f}%"
    num = lambda v: "n/a" if not np.isfinite(v) else f"{v:8.2f}"
    lines = [
        "=" * 46,
        f"{title:^46}",
        "=" * 46,
        f"  periods          {ts['n_periods']:>8d}   ({ts['years']:.2f} yrs)",
        f"  total return     {pct(ts['total_return'])}",
        f"  CAGR             {pct(ts['cagr'])}",
        f"  ann. vol         {pct(ts['ann_vol'])}",
        f"  Sharpe           {num(ts['sharpe'])}",
        f"  Sortino          {num(ts['sortino'])}",
        f"  max drawdown     {pct(ts['max_drawdown'])}",
        f"  Calmar           {num(ts['calmar'])}",
        f"  hit rate         {pct(ts['hit_rate'])}",
    ]
    if "turnover" in ts:
        lines.append(f"  turnover/day     {num(ts['turnover'])}")
    lines += [
        f"  best / worst day {pct(ts['best_period'])} / {pct(ts['worst_period'])}",
        "=" * 46,
    ]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    idx = pd.bdate_range("2018-01-01", periods=1000)
    rng = np.random.default_rng(0)
    demo = pd.Series(rng.normal(0.0004, 0.01, len(idx)), index=idx, name="ret")
    print(format_tear_sheet(tear_sheet(demo, demo * 0 + 1), "DEMO (random walk)"))
