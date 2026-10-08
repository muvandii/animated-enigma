# Week 3 — Build the engine (part 1): the loop, the portfolio, the broker

> **Phase 02 · Engine** · Hours: 16–20 · Hardest week of the course
>
> You stop borrowing `backtester.py` and write your own. The deliverable is not
> "a better backtester" — it is a backtester you can *prove* is honest, because
> you wrote the tests.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Build engine/{data,portfolio,broker,engine}.py as an event-driven loop that re-runs S01–S05 and reconciles within ±2%
WHY:          Weeks 5–11 need cross-sectional ranking, portfolio risk limits, and path-dependent fills. The vectorized toy cannot express any of them, and bolting them on later would mean rewriting everything in Week 11.
INPUT:        phases/02-engine/README.md (the spec), shared/backtester/backtester.py (reference behavior), strategies/S01–S05
OUTPUT:       engine/{__init__,data,portfolio,broker,engine,costs,signals,splits,reporting}.py
              engine/README.md (conventions + assumptions + limitations)
              engine/tests/{test_engine,test_portfolio,test_costs,test_lookahead}.py  (>=20 tests)
              reports/engine-reconciliation.md (S01–S05 old vs new, every gap explained)
              notes/daily/week-03/{mon..sun}.md, notes/concepts/event-loop-vs-vectorized.md
PROOF:        `python -m pytest -q` green with >=20 tests, AND `python engine/run_reconciliation.py` prints a 5-row table with every |Δ| < 2%
TIME:         960–1200 min
BLOCKER IF:   a reconciliation gap exceeds 2% and you cannot name the assumption that causes it — stop and find it, do not tune until it matches
```

---

## Daily objectives

### Monday — Write the spec before the code

```text
🎯 OBJECTIVE:   Write engine/README.md documenting the 9 conventions from phases/02-engine/README.md §2
WHY:          Every unexplained reconciliation gap you will hit on Saturday traces back to a convention you did not decide today.
INPUT:        phases/02-engine/README.md
OUTPUT:       engine/README.md (position convention, execution price, signal lag, cost model, fractional shares, shorting, corporate actions, warm-up, missing data)
              notes/daily/week-03/mon.md
PROOF:        a stranger could read engine/README.md and predict what the engine does on a 3-bar example
TIME:         90 min
BLOCKER IF:   any of the 9 conventions says "TBD"
```

### Tuesday — DataFeed and the look-ahead-proof iterator

```text
🎯 OBJECTIVE:   Build engine/data.py with an iterator that structurally cannot return future bars
WHY:          This is the single design decision that prevents most look-ahead. If strategy code cannot express "tomorrow's price", most bugs become impossible.
INPUT:        data/clean/*.parquet
OUTPUT:       engine/data.py, engine/tests/test_data.py (>=4 tests)
              notes/daily/week-03/tue.md
PROOF:        test_data.py::test_iterator_never_exposes_future_bars passes; a strategy that tries frame.iloc[i+1] raises IndexError
TIME:         120 min
BLOCKER IF:   you can access a bar after the current one from inside on_bar()
```

### Wednesday — Portfolio and Broker

```text
🎯 OBJECTIVE:   Build engine/portfolio.py (cash, positions, NAV, mark-to-market) and engine/broker.py (orders -> fills -> cost)
WHY:          Separating "what we hold" from "how we trade" is what lets you add risk limits in Week 10 without touching the strategy code.
INPUT:        engine/data.py, phases/02-engine/cost-models.md
OUTPUT:       engine/portfolio.py, engine/broker.py, engine/costs.py
              engine/tests/test_portfolio.py, engine/tests/test_costs.py (>=8 tests)
              notes/daily/week-03/wed.md
PROOF:        cash + sum(positions x price) == NAV at every bar (test it); no fill can be applied before mark-to-market
TIME:         180 min
BLOCKER IF:   NAV does not reconcile to cash + positions after any fill
```

### Thursday — The loop, plus S01 through it

```text
🎯 OBJECTIVE:   Build engine/engine.py and run S01 through it end to end
WHY:          One strategy through the whole loop is worth more than five half-wired modules. Get S01 green before generalizing.
INPUT:        engine/{data,portfolio,broker}.py, strategies/S01_ma_crossover/strategy.py
OUTPUT:       engine/engine.py, engine/signals.py, engine/tests/test_engine.py (>=5 tests)
              reports/engine-reconciliation.md (S01 row)
              notes/daily/week-03/thu.md
PROOF:        S01's engine net CAGR is within 2% of backtester.py's 3.04%
TIME:         180 min
BLOCKER IF:   |Δ| > 2% on S01 — the most common causes are warm-up handling and cost timing; check both before anything else
```

### Friday — The look-ahead suite

```text
🎯 OBJECTIVE:   Write engine/tests/test_lookahead.py with all 8 tests from phases/02-engine/look-ahead-tests.md
WHY:          These are the tests that will save Weeks 5–11. Writing them now, before you have 13 strategies depending on the engine, is the cheapest they will ever be.
INPUT:        phases/02-engine/look-ahead-tests.md
OUTPUT:       engine/tests/test_lookahead.py (8 tests, all passing)
              notes/concepts/event-loop-vs-vectorized.md
              notes/daily/week-03/fri.md
PROOF:        test_peeking_signal_is_detected passes (i.e. your detector FIRES on a deliberately cheated signal)
TIME:         150 min
BLOCKER IF:   the peeking test does not produce Sharpe > 10 — your engine is letting look-ahead through silently
```

### Saturday — Reconcile S02–S05

```text
🎯 OBJECTIVE:   Run S02–S05 through the engine and complete reports/engine-reconciliation.md
WHY:          This is the gate. A gap you cannot explain is a bug that will contaminate 8 more strategies.
INPUT:        strategies/S02–S05, engine/
OUTPUT:       reports/engine-reconciliation.md (5 rows, every |Δ| explained in writing)
              notes/daily/week-03/sat.md
PROOF:        all 5 rows within ±2%, each with a one-sentence cause for the residual difference
TIME:         150 min
BLOCKER IF:   any |Δ| > 2% is unexplained
```

### Sunday — Journal + Phase check

```text
🎯 OBJECTIVE:   Append the Week 3 journal entry and count your tests
WHY:          Half of Phase 2's gate is test coverage. Count them now so Saturday of Week 4 is not a surprise.
INPUT:        engine/tests/, reports/engine-reconciliation.md
OUTPUT:       journal/lessons.md (Week 3 entry)
              notes/daily/week-03/sun.md
PROOF:        >=20 tests passing; journal entry names at least one assumption that turned out to matter
TIME:         60 min
BLOCKER IF:   fewer than 20 tests
```

---

## Deliverables

| Artifact | Path |
|---|---|
| Engine modules | `engine/{data,portfolio,broker,engine,costs,signals,splits,reporting}.py` |
| Engine docs | `engine/README.md` |
| Tests | `engine/tests/test_{engine,portfolio,costs,data,lookahead}.py` (≥20) |
| Reconciliation | `reports/engine-reconciliation.md` |
| Notes | `notes/daily/week-03/*.md` × 7, `notes/concepts/event-loop-vs-vectorized.md` |

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — The order lifecycle (signal → order → fill → position → P&L)

```text
📐 CONCEPT: Order lifecycle
WHY NOW:   Your NAV does not reconcile after a fill (Wednesday's blocker). You are conflating
           "what I decided" with "what I got".
FORMULA:   target_weight[t] -> (x NAV) -> target_shares -> - current_shares -> order
           -> fill(price, size, cost) -> position[t] -> P&L[t] = position[t-1] * ret[t] - cost[t]
CODE:      target_sh = int(target_w * nav / price)
           order = target_sh - held
           fill_px = price * (1 + np.sign(order) * slip_bps/1e4)
           cash -= order * fill_px + abs(order * fill_px) * fee_bps/1e4
EXAMPLE:   NAV $10,000, target 1.0, price $100 -> 100 shares. Holding 40 -> order 60.
           Fill at 100.05 (5bps) = $6,003 + $0.60 fee. Cash is now $3,996.40 with 100 shares
           worth $10,000 at the close -> NAV $13,996.40? No: NAV = cash + 100*100 = $13,996.40
           and the $6.60 you spent is gone from NAV. That $6.60 is the cost. Print it.
TIME:      20 min
NOTE:      write notes/concepts/order-lifecycle.md using Concept Note Template
DONE WHEN: you can trace one trade through all five stages without looking, explain in 2 sentences
           why the fill price differs from the decision price, and spot a broker that charges
           cost on the target instead of on the DELTA (symptom: cost is charged even when position
           does not change)
```

### 📐 CONCEPT — Event loop vs vectorization

```text
📐 CONCEPT: Event-driven loop vs vectorized computation
WHY NOW:   You just rewrote a 150-line vectorized backtester as a 400-line loop and it is 100x
           slower. You need to be able to justify that trade to yourself, and to know which parts
           should NOT be event-driven.
FORMULA:   vectorized:  result[t] = f(frame[0..t])   for all t at once  (numpy/pandas)
           event loop:  for bar in feed: state = update(state, bar)     (python objects)
           Hybrid (recommended): compute SIGNALS vectorized, run the PORTFOLIO as a loop.
CODE:      sig = (px.rolling(10).mean() > px.rolling(50).mean()).astype(float)  # vectorized
           for ts, hist in feed:                                                # loop
               port.rebalance_to(sig.loc[ts], price=px.loc[ts])
EXAMPLE:   Your engine computes signals once, up front, over the whole frame (fast, and the
           rolling() semantics are obviously backward-looking), then walks bars to apply
           portfolio logic. Costs ~40 lines instead of ~400 and keeps 90% of the speed.
TIME:      15 min
NOTE:      write notes/concepts/event-loop-vs-vectorized.md using Concept Note Template
DONE WHEN: you can state in 2 sentences when a loop is worth the cost, can write both versions of
           a 3-line strategy, and can spot the vectorized "portfolio" that silently assumes you
           can always rebalance at the close with infinite liquidity
```

---

## ✅ CHECKPOINT RUBRIC — Week 3 gate

- [ ] `engine/` has data, portfolio, broker, engine, costs, signals, splits, reporting
- [ ] `engine/README.md` answers all 9 conventions
- [ ] ≥20 tests, all passing
- [ ] `test_lookahead.py` has 8 tests, and `test_peeking_signal_is_detected` FIRES
- [ ] S01 runs through the engine
- [ ] No Sharpe above 5 anywhere in the engine's output

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> **Kill your own engine, three ways, and log each.**
> 1. Remove the `shift(1)` on the signal (or its event-loop equivalent). Record
>    the Sharpe. That number is what look-ahead looks like in YOUR engine.
> 2. Charge cost on `target` instead of on `delta`. Record how much NAV inflates.
> 3. Let the strategy see `hist.iloc[-1]` as "tomorrow" by accidentally including
>    the current bar in the *prior* bar's history. Record the Sharpe.
>
> Each becomes a row in `graveyard/graveyard.md` with type `engine-bug` and a
> test in `test_lookahead.py` that now prevents it.

## Next

Week 4: costs, walk-forward, purge/embargo, tear-sheet generator. Then the Phase
2 gate.
