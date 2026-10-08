# Look-ahead bias — the eight tests your engine must have

Look-ahead is the #1 killer of backtests and the #1 reason a beautiful backtest
becomes a losing strategy. It is invisible in code review because the code looks
fine. These tests make it visible.

**Philosophy:** you cannot test for the absence of look-ahead directly. You test
for its *consequences*, and you build detectors that you have first proven work
by deliberately cheating and watching them fire.

---

## The taxonomy

| Type | What it looks like | Detector |
|---|---|---|
| **Execution lag** | signal from bar t traded at bar t | Test 2 |
| **Future in feature** | `.shift(-1)`, `.iloc[i+1]`, forward returns in the signal | Test 1, 3 |
| **Global statistic** | `df.mean()`, `.max()`, z-score over the whole sample | Test 4 |
| **Backward fill** | `fillna(method="bfill")`, `interpolate()` | Test 5 |
| **Label overlap** | 20-day forward return label crossing the train/test boundary | Test 6 |
| **Ordering** | fills applied before mark-to-market | Test 7 |
| **Survivorship** | universe chosen using end-of-sample knowledge | Test 8 |
| **Data vintage** | using restated/as-of-today fundamentals | Test 8 |

---

## Test 1 — Rewriting the future must not change the past

```python
def test_rewriting_the_future_does_not_change_the_past(engine, px):
    a = run(engine, px, signal)
    px2 = px.copy()
    px2.iloc[-100:] *= 3.0                      # rewrite the last 100 bars
    b = run(engine, px2, signal)
    n = len(px) - 100
    pd.testing.assert_series_equal(a.returns.iloc[:n - 1], b.returns.iloc[:n - 1])
```

**This is the single highest-value test in the suite.** It catches every form of
"my signal peeks", regardless of mechanism.

## Test 2 — Position at bar t depends only on data ≤ t−1

```python
def test_position_lags_signal(engine, px):
    sig = pd.Series(0.0, index=px.index)
    sig.iloc[500:] = 1.0
    res = run(engine, px, sig)
    assert res.position.iloc[500] == 0.0        # decided at 500...
    assert res.position.iloc[501] == 1.0        # ...held from 501
```

## Test 3 — A peeking signal must produce an absurd result

```python
def test_peeking_signal_is_detected(engine, px):
    """PROVE the detector works. If this ever passes without a huge Sharpe,
    your engine is silently allowing look-ahead."""
    peek = np.sign(px.pct_change().shift(-1)).fillna(0.0)
    res = run(engine, px, peek)
    assert res.tear_sheet()["sharpe"] > 10
    assert res.equity.iloc[-1] > buy_and_hold(px).equity.iloc[-1] * 100
```

⚠️ Notice: the backtester's `shift(1)` guard does **not** catch this. The peek is
inside the signal function. The only reliable detector is the magnitude of the
result. **Adopt the rule: any daily-bar Sharpe above 5 is look-ahead until
proven otherwise.**

## Test 4 — Global statistics are rejected

```python
def test_signal_using_full_sample_mean_is_rejected(engine, px):
    """A z-score computed over the WHOLE sample leaks the future into bar 0."""
    bad = (px - px.mean()) / px.std()           # uses data from 2030 to trade in 2015
    res_bad = run(engine, px, np.sign(bad))
    rolling = (px - px.rolling(60).mean()) / px.rolling(60).std()
    res_ok = run(engine, px, np.sign(rolling))
    assert res_bad.tear_sheet()["sharpe"] != res_ok.tear_sheet()["sharpe"]
    # and flag it explicitly:
    with pytest.raises(LookAheadError):
        engine.validate_signal(bad)             # if you implement a validator
```

## Test 5 — No backward fill

```python
def test_backward_fill_is_detected(engine):
    px = pd.Series([100, np.nan, np.nan, 104], index=pd.bdate_range("2020-01-01", periods=4))
    with pytest.raises((ValueError, LookAheadError)):
        engine.validate_prices(px.bfill())      # 101 -> filled using tomorrow's 104
    engine.validate_prices(px.ffill())          # forward fill is fine
```

## Test 6 — Embargo catches label overlap

```python
def test_embargo_removes_label_overlap():
    idx = pd.bdate_range("2015-01-01", periods=2000)
    label_lookahead = 20
    splits = walk_forward_splits(idx, n_splits=5, train_frac=0.6, embargo=label_lookahead)
    for train, test in splits:
        gap = idx.get_loc(test[0]) - idx.get_loc(train[-1])
        assert gap >= label_lookahead + 1, "labels overlap the boundary"

def test_without_embargo_sharpe_is_inflated():
    """Deliberate demonstration: turn the embargo off, watch OOS Sharpe rise."""
    idx = pd.bdate_range("2015-01-01", periods=2000)
    with_e = walk_forward_splits(idx, n_splits=5, embargo=20)
    no_e   = walk_forward_splits(idx, n_splits=5, embargo=0)
    assert len(with_e[0][0]) < len(no_e[0][0])      # embargo drops training rows
```

## Test 7 — Ordering: mark-to-market before fills

```python
def test_fills_are_applied_after_mark_to_market(engine, px):
    res = run(engine, px, alternating_signal(px.index))
    # equity at bar t must equal (equity at t-1) * (1 + return on existing holdings)
    # plus the effect of fills at t -- never the reverse
    for t in range(2, 50):
        held = res.position.iloc[t - 1]
        expected = res.equity.iloc[t - 1] * (1 + held * px.pct_change().iloc[t])
        assert abs(res.equity.iloc[t] - expected) < res.equity.iloc[t - 1] * 0.01
```

## Test 8 — Survivorship

```python
def test_universe_is_not_chosen_with_hindsight(engine):
    """The S&P 500 membership you have TODAY is not the membership of 2015."""
    with pytest.raises(SurvivorshipError):
        engine.set_universe(today_sp500_members, start="2015-01-01")
    # correct: point-in-time membership
    engine.set_universe(pit_membership_series, start="2015-01-01")

def test_delisting_bias_is_visible():
    """Universe of only currently-listed tickers overstates returns."""
    survivors = run(engine, current_members_only)
    with_delisted = run(engine, pit_universe_including_delisted)
    assert survivors.tear_sheet()["cagr"] > with_delisted.tear_sheet()["cagr"]
```

---

## The magnitude rule (put this in your README)

> **Sharpe > 5 on daily bars is look-ahead until proven otherwise.**
>
> Rough calibration: the best real-world systematic strategies run 1–3. A
> long-only equity index runs 0.3–0.5. A single-name momentum strategy in a
> 10-year backtest might print 0.8–1.2. If you see 5, 10, or 40, you are not a
> genius, you have met the future.

## How to hunt it when the rule fires

1. Run Test 1. If it fails, bisect the signal: comment out half the features, re-run.
2. Grep your strategy file for: `shift(-`, `iloc[i +`, `bfill`, `.mean()`,
   `.max()`, `.min()`, `.std()` without `.rolling`, `iloc[-1]`.
3. Check whether any feature is computed on a *different* (larger) date range
   than the signal.
4. Check the label: is the thing you predict computed with forward data, and did
   it cross a split boundary?
5. Check the data vintage: are you using today's restated fundamentals?
