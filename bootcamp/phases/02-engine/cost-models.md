# Cost models — worked examples

Copy these into `engine/costs.py`. Every one has a test you should write.

## 0. Why this file exists

The single most common way to lie to yourself in a backtest is `costs = 0`.
The second is `costs = 1 bp` because that is the commission your broker shows
you, while forgetting the spread you cross every time.

**Your round-trip cost is at minimum half the spread plus impact.** For a
liquid US large-cap with a 1-cent spread at $100, that is 5 bps before fees.

---

## 1. Flat bps (the default)

```python
def flat_cost(delta_notional: float, bps: float) -> float:
    return abs(delta_notional) * bps / 10_000.0

# 1 bp fee + 5 bps slippage on a $10,000 position change:
#   10_000 * 6 / 10_000 = $6.00
```

**When it lies:** any time your order is a meaningful fraction of ADV. A
$10,000 order in AAPL is nothing; a $10,000 order in a $2m-ADV small-cap is 0.5%
of the day's volume and will move the price.

## 2. Spread crossing

```python
def spread_cost(shares: float, bid: float, ask: float) -> float:
    return abs(shares) * (ask - bid) / 2.0
```

**Better than flat bps** because the spread widens exactly when you most want to
trade (volatile, illiquid, stressed). If you only have closes, approximate the
spread from the high-low range:

```python
# Corwin-Schultz (2012) high-low spread estimator, simplified
def hl_spread(high, low):
    beta = np.log((high / low) ** 2).rolling(2).sum()
    gamma = np.log(high.rolling(2).max() / low.rolling(2).min()) ** 2
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / (3 - 2 * np.sqrt(2)) - np.sqrt(gamma / (3 - 2 * np.sqrt(2)))
    return 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))      # can go negative; clip at 0
```

## 3. Square-root market impact

```python
def impact_cost(shares: float, adv: float, sigma: float, eta: float = 0.1) -> float:
    """Fraction of price moved, then converted to a dollar cost."""
    if adv <= 0:
        return 0.0
    frac = abs(shares) / adv
    return eta * sigma * np.sqrt(frac) * abs(shares)      # bps ~ eta*sigma*sqrt(participation)
```

**Sanity check:** trading 1% of ADV with 20% annual vol and η=0.1 moves the price
by roughly `0.1 × 0.20 × sqrt(0.01)` = 0.2% — i.e. ~20 bps. That is 4× your flat
slippage assumption, and it is why size limits exist.

## 4. Borrow (short book)

```python
def borrow_cost(short_notional: float, borrow_bps: float, days: int = 1) -> float:
    return abs(short_notional) * borrow_bps / 10_000.0 * days / 252.0
```

**When it lies:** hard-to-borrow names. Real borrow on a small-cap squeeze is
100%+ annualized, not 50 bps. If your strategy shorts, check whether the name is
on a borrow-restricted list before you trust 50 bps.

## 5. Financing on leverage

```python
def financing_cost(gross_exposure: float, notional_capital: float, rate: float, days: int = 1) -> float:
    borrowed = max(gross_exposure - notional_capital, 0.0)
    return borrowed * rate * days / 252.0
```

A 2× levered strategy does not earn 2× the returns. It earns 2× minus the
financing rate. Model it or you will ship a strategy whose entire edge is
leverage, which is theWeek 10 failure mode.

---

## 6. The break-even table (print this for every strategy)

```python
def breakeven_table(turnover_yr: float, gross_cagr: float) -> pd.DataFrame:
    rows = []
    for bps in (0, 2, 5, 10, 25, 50, 100):
        drag = turnover_yr * bps / 10_000.0
        rows.append({"slippage_bps": bps, "annual_drag_%": round(drag * 100, 2),
                     "net_cagr_%": round((gross_cagr - drag) * 100, 2),
                     "survives": (gross_cagr - drag) > 0})
    return pd.DataFrame(rows)
```

Example — S03 (RSI-2), turnover 118/yr, gross CAGR 9.4%:

| slippage_bps | annual_drag_% | net_cagr_% | survives |
|---|---|---|---|
| 0 | 0.00 | 9.40 | True |
| 2 | 2.36 | 7.04 | True |
| 5 | 5.90 | 3.50 | True |
| 10 | 11.80 | **-2.40** | **False** |
| 25 | 29.50 | -20.10 | False |

**This one table killed S03.** Read across the row where `survives` flips: at
~8 bps the strategy is dead. 8 bps round-trip is *optimistic* for a retail
equity order. That is the whole argument, in one table, and no amount of
parameter tuning changes it.

## 7. Cost model self-test (put this in `tests/test_costs.py`)

```python
def test_costs_are_monotonic_in_bps(): ...
def test_cost_is_always_non_negative(): ...      # catches the missing abs()
def test_no_cost_when_position_unchanged(): ...
def test_high_turnover_strategy_dies_at_realistic_bps(): ...
def test_borrow_only_charged_on_shorts(): ...
def test_impact_grows_superlinearly_in_size(): ...
```
