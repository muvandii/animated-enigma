# Phase 02 — The Engine (Weeks 3–4)

You have been running `backtester.py`, which is ~150 lines of vectorized pandas.
It is honest, and it is not enough. This phase you build your own.

**Do not build a general-purpose backtesting framework.** Build the smallest
thing that can express the strategies you already shipped, with a test suite that
proves it cannot cheat. Every feature you add beyond that is a feature you have to
test, document, and defend in Week 13.

---

## 1. Why event-driven at all

| | Vectorized (what you have) | Event-driven (what you build) |
|---|---|---|
| Speed | 100× faster | slower |
| Multi-asset portfolio | awkward | natural |
| Position-level logic (stops, scaling, risk limits) | very awkward | natural |
| Path-dependent costs (impact, partial fills) | impossible | possible |
| Look-ahead bugs | easy to introduce, hard to see | harder to introduce |
| Lines of code | ~150 | ~400 |

**Decision rule:** if your strategies are "compute a signal column, shift it,
multiply by returns", stay vectorized and spend the week on tests instead. Go
event-driven if you need **cross-sectional ranking, portfolio-level risk limits,
or path-dependent fills** — you will need all three by Week 11.

The course default: **event-driven core, vectorized signal computation.** Signals
are computed with pandas (fast, no loop); the portfolio loop consumes them bar by
bar.

---

## 2. Architecture — the five objects

```
engine/
├── engine.py        # Backtester: the loop
├── portfolio.py     # Portfolio: cash, positions, NAV, margin
├── broker.py        # Broker: orders -> fills, applies the cost model
├── costs.py         # CostModel: fee, slippage, borrow, impact
├── data.py          # DataFeed: bar-by-bar iteration, the ONLY source of truth
├── signals.py       # your strategies' signal functions (pure, vectorized)
├── splits.py        # walk_forward_splits, purge_and_embargo
├── reporting.py     # tear_sheet, plots
├── README.md        # YOU WRITE THIS — conventions, assumptions, limitations
└── tests/
    ├── test_engine.py
    ├── test_costs.py
    ├── test_portfolio.py
    └── test_lookahead.py     # >= 8 tests, non-negotiable
```

### The loop (the whole thing)

```python
class Backtester:
    def __init__(self, data: DataFeed, broker: Broker, portfolio: Portfolio):
        self.data, self.broker, self.portfolio = data, broker, portfolio

    def run(self, strategy) -> pd.DataFrame:
        for bar in self.data:                    # bar = one timestamp, ALL symbols
            self.portfolio.mark_to_market(bar)   # 1. value what we hold
            targets = strategy.on_bar(bar, self.portfolio.history)  # 2. decide
            orders = self.portfolio.to_orders(targets)              # 3. size
            fills = self.broker.execute(orders, bar)                # 4. fill + cost
            self.portfolio.apply(fills)                             # 5. settle
            self.portfolio.snapshot(bar)         # 6. record
        return self.portfolio.equity_curve()
```

**The one rule that makes this safe:** `strategy.on_bar()` receives a
`history` object that is *structurally incapable of returning data after `bar`*.
Not "I promise not to look" — cannot look. Implement it by slicing:

```python
class DataFeed:
    def __iter__(self):
        for i in range(len(self.index)):
            yield self.index[i], self.frame.iloc[: i + 1]   # up to AND INCLUDING bar i
```

Everything through bar `i` is fair game (you know today's close when you trade at
today's close). Nothing after. If your strategy code cannot even express
`frame.iloc[i + 1]`, you cannot write look-ahead.

### Conventions you must document in `engine/README.md`

| Question | Your answer (write it down) |
|---|---|
| Position convention | units? weight? notional? signed? |
| Execution price | close? next open? VWAP? |
| When is a signal from bar t executed? | bar t+1 close (default) |
| Cost model | fee bps, slippage bps, borrow bps, impact function |
| Fractional shares? | yes/no |
| Shorting allowed? borrowing cost? | |
| Corporate actions | adjusted close only? dividend handling? |
| Warm-up | how many bars before a strategy is allowed to trade |
| Missing data | skip bar? forward-fill? halt trading? |

Ambiguity here is where bugs live. Write it down before you write the code.

---

## 3. Cost models — with numbers

See `cost-models.md` in this folder for the full worked examples. Summary:

| Model | Formula | Use when |
|---|---|---|
| Flat bps | `\|Δnotional\| × bps/1e4` | liquid US equities, small size |
| Spread-crossing | `\|Δshares\| × (ask−bid)/2` | when you have quotes |
| Square-root impact | `σ × sqrt(\|Δshares\| / ADV)` | size > 0.1% of ADV |
| Borrow | `\|short notional\| × borrow_bps/1e4 × days/252` | any short book |
| Slippage by order type | market: half-spread + impact; limit: 0 if filled | when you model order types |

**Default for this course:** 1 bp fee + 5 bps slippage on US large-caps,
10–20 bps on small-caps, 20–50 bps on crypto alts, 50 bps/yr borrow.

---

## 4. Walk-forward, purge, embargo

`engine/splits.py` — see `walk-forward.md` for the full treatment.

The part everyone gets wrong: **the embargo must be at least as long as the
longest forward-looking window in your features.** If your label is a 20-day
forward return, and you split train|test at a date boundary, the last 20 days of
training have seen the first 20 days of test. Your "out-of-sample" Sharpe is then
partly in-sample.

```python
embargo >= max_lookahead_in_features      # e.g. 20 bars for a 20-day label
```

---

## 5. The look-ahead test suite (≥8 tests, non-negotiable)

See `look-ahead-tests.md`. The eight you must have:

1. Rewriting the future does not change the past.
2. Position at bar t depends only on data at t−1 and earlier.
3. A deliberately-peeking signal produces an absurd Sharpe (proves your detector
   works).
4. A signal using a global statistic (mean/max/std over the whole series) is
   rejected or produces a degraded result.
5. `fillna(method="bfill")` / backward-filled prices are detected.
6. Label overlap across the train/test boundary is caught by the embargo.
7. Ordering: fills for bar t are never applied before bar t's mark-to-market.
8. Survivorship: a universe chosen at the end of the sample is rejected.

---

## 6. Tear-sheet generator

`engine/reporting.py` must produce, from a returns Series:
- the full `metrics.tear_sheet()` table
- gross vs net side by side
- benchmark comparison
- walk-forward fold table
- monthly returns heatmap (optional, matplotlib)
- equity + drawdown + position plots
- a `README`-able text block and a CSV of the equity curve

Stub: `tearsheet_stub.py` in this folder.

---

## 7. The reconciliation requirement (this is the gate)

Your new engine must reproduce your old numbers. For each of S01–S05:

| ID | `backtester.py` net CAGR | `engine/` net CAGR | Δ | Explained? |
|---|---|---|---|---|
| S01 | | | | |
| ... | | | | |

**Tolerance: ±2%.** Any gap larger must be explained in writing, and the
explanation must name which assumption differs (execution price, cost timing,
position convention, warm-up handling). Most gaps are warm-up handling or
cost-timing; both are legitimate differences, but you have to know which one you
have.

If you cannot explain a gap, your engine has a bug and you must not advance.
A bug here propagates into 11 more strategies and you will find it in Week 11,
three weeks too late.
