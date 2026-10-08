"""fetcher.py — minimal, dependency-light market data fetcher for the bootcamp.

Purpose: get ONE symbol of daily OHLCV onto disk as parquet, with a deterministic
offline generator so every test and every example runs with zero network access.

Supported sources
    stooq    : free CSV endpoint, no API key, no rate limit drama (default)
    yfinance : optional, only if you `pip install yfinance`
    synthetic: deterministic pseudo-random walk used by the test suite and by
               examples when the network is unavailable (sandbox, airplane, CI)

Usage
    python fetcher.py AAPL                       # stooq -> data/aapl.parquet
    python fetcher.py AAPL --source synthetic    # offline, deterministic
    python fetcher.py AAPL --source yfinance --start 2015-01-01

Contract
    Every fetch_* returns a DataFrame indexed by `date` (datetime64[ns], sorted,
    unique) with columns: open, high, low, close, volume, adj_close  (floats).
    Everything downstream (metrics.py, backtester.py) assumes exactly this.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "COLUMNS",
    "normalize",
    "fetch_stooq",
    "fetch_yfinance",
    "fetch_synthetic",
    "fetch",
    "save_parquet",
    "load_parquet",
]

COLUMNS = ["open", "high", "low", "close", "volume", "adj_close"]

_STOOQ_URL = "https://stooq.com/q/d/l/?s={ticker}&i=d"


# --------------------------------------------------------------------------- #
# normalization
# --------------------------------------------------------------------------- #
def normalize(df: pd.DataFrame, ticker: str | None = None) -> pd.DataFrame:
    """Force any raw frame into the bootcamp contract: sorted date index + COLUMNS.

    - lowercases/renames common vendor column names (Date, Close/Last, Adj Close)
    - drops rows with a missing close (holidays, vendor junk)
    - fills adj_close with close when the vendor does not supply one
    """
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    renames = {
        "date": "date",
        "datetime": "date",
        "timestamp": "date",
        "closelast": "close",
        "adj_close": "adj_close",
        "adjclose": "adj_close",
        "adj._close": "adj_close",
    }
    df = df.rename(columns={k: v for k, v in renames.items() if k in df.columns})

    if "date" not in df.columns and isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index().rename(columns={df.index.name or "index": "date"})

    if "date" not in df.columns:
        raise ValueError(f"no date column found; got {list(df.columns)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "close"])

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["adj_close"].isna().all():
        df["adj_close"] = df["close"]
    for col in ("open", "high", "low"):
        if df[col].isna().all():
            df[col] = df["close"]

    if df["volume"].isna().all():
        df["volume"] = 0.0

    df = df[["date"] + COLUMNS]
    df = df.groupby("date", as_index=False).last().sort_values("date")
    df = df.set_index("date")
    df.index.name = "date"
    if ticker:
        df.attrs["ticker"] = ticker
    return df


# --------------------------------------------------------------------------- #
# sources
# --------------------------------------------------------------------------- #
def fetch_stooq(symbol: str, timeout: int = 15) -> pd.DataFrame:
    """Free daily OHLCV from stooq.com. US tickers need the `.us` suffix."""
    import urllib.request  # local import: keeps CLI start fast, no new dep

    ticker = symbol.lower()
    if "." not in ticker:
        ticker += ".us"
    url = _STOOQ_URL.format(ticker=ticker)
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    if not raw or raw.lower().startswith("exceeded") or "<html" in raw.lower():
        raise RuntimeError(f"stooq refused/errored for {symbol}: {raw[:120]!r}")
    df = pd.read_csv(io.StringIO(raw))
    return normalize(df, ticker=symbol.upper())


def fetch_yfinance(symbol: str, start: str = "2010-01-01", end: str | None = None) -> pd.DataFrame:
    """Optional path. Requires `pip install yfinance` (not in requirements.txt)."""
    try:
        import yfinance as yf  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("yfinance not installed: pip install yfinance") from exc
    df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)
    if df.empty:
        raise RuntimeError(f"yfinance returned no rows for {symbol}")
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return normalize(df, ticker=symbol.upper())


def _trading_days(start: str, periods: int) -> pd.DatetimeIndex:
    """Business days minus US federal holidays -> ~252 bars per calendar year.

    Why not plain bdate_range: bdate_range yields ~261 bars/year, which does not
    match the 252 bars/year that metrics.py annualises with. The mismatch makes
    every tear sheet report ~3.6% more elapsed years than the calendar really
    contains, which is exactly the kind of quiet error that makes a mediocre
    CAGR look slightly better than it is. Synthetic data should not lie
    differently than real data.
    """
    from pandas.tseries.holiday import USFederalHolidayCalendar  # local: slow import

    start_ts = pd.Timestamp(start)
    end_ts = start_ts + pd.DateOffset(days=int(periods * 365.25 / 252) + 45)
    cal = USFederalHolidayCalendar()
    days = pd.bdate_range(start=start_ts, end=end_ts).difference(
        cal.holidays(start=start_ts, end=end_ts)
    )
    if len(days) < periods:
        # should not happen with the buffer above, but never silently return short
        raise ValueError(f"could not build {periods} trading days from {start}")
    return days[:periods]


def fetch_synthetic(
    symbol: str = "SYNTH",
    start: str = "2015-01-01",
    periods: int = 2520,
    seed: int = 7,
    mu: float = 0.06,
    sigma: float = 0.22,
    start_price: float = 100.0,
) -> pd.DataFrame:
    """Deterministic geometric-Brownian walk. Same seed => same data, always.

    This is the offline spine of the course: every example and test can run on a
    plane. It is deliberately NOT trend-free (mu>0) so naive strategies do not
    accidentally look like genius.
    """
    rng = np.random.default_rng(seed)
    dates = pd.DatetimeIndex(_trading_days(start, periods), name="date")
    dt = 1 / 252
    shocks = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), size=periods)
    close = start_price * np.exp(np.cumsum(shocks))
    open_ = np.concatenate([[start_price], close[:-1]]) * (1 + rng.normal(0, 0.002, periods))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, periods)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, periods)))
    volume = rng.integers(1_000_000, 40_000_000, periods).astype(float)
    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=dates,
    )
    df["adj_close"] = df["close"]
    df.index.name = "date"
    df.attrs["ticker"] = symbol.upper()
    return df[COLUMNS]


def fetch(symbol: str, source: str = "auto", start: str = "2010-01-01", **kw) -> pd.DataFrame:
    """One entry point. `auto` tries stooq, then yfinance, then synthetic."""
    if source == "synthetic":
        return fetch_synthetic(symbol, start=start, **kw)
    if source == "stooq":
        return fetch_stooq(symbol, **kw)
    if source == "yfinance":
        return fetch_yfinance(symbol, start=start, **kw)
    if source == "auto":
        for fn in (fetch_stooq, fetch_yfinance):
            try:
                return fn(symbol, **kw) if fn is fetch_stooq else fn(symbol, start=start)
            except Exception:
                continue
        print(f"[fetcher] network unavailable — falling back to synthetic data for {symbol}",
              file=sys.stderr)
        return fetch_synthetic(symbol, start=start, **kw)
    raise ValueError(f"unknown source: {source}")


# --------------------------------------------------------------------------- #
# io
# --------------------------------------------------------------------------- #
def save_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return path


def load_parquet(path: str | Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df.sort_index()


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fetch one symbol to parquet.")
    p.add_argument("symbol", help="e.g. AAPL")
    p.add_argument("--source", default="auto", choices=["auto", "stooq", "yfinance", "synthetic"])
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--out", default=None, help="default: data/<symbol>.parquet")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args(argv)

    kw = {}
    if args.source in ("auto", "synthetic"):
        kw["seed"] = args.seed
    df = fetch(args.symbol, source=args.source, start=args.start, **kw)
    out = Path(args.out) if args.out else Path("data") / f"{args.symbol.lower()}.parquet"
    save_parquet(df, out)
    print(f"wrote {out}  rows={len(df)}  {df.index.min().date()} -> {df.index.max().date()}")
    print(df.tail(3).to_string())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
