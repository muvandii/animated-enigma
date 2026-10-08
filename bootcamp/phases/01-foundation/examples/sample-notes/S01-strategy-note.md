# Strategy: S01 MA(10/50) crossover on AAPL

SOURCE: my own head, from the first chapter of basically every TA book. I picked
it because it is the cheapest possible expression of "trend persistence", so if
it fails I learn that trend persistence at this frequency is not exploitable, not
that my implementation was fancy-but-wrong.

THESIS:
Trends in large-cap equities persist for weeks because capital moves slowly:
index rebalancing, fund flows, and analyst-revision cascades all play out over
weeks, and traders anchored to recent prices under-react at first. A fast/slow
moving-average crossover is the cheapest way to express "be long when the
short-term trend is up". The bet: the middle of big moves is worth more than the
whipsaw in sideways markets costs.

RULES:
- entry: go long 1.0 at the close when MA(10) > MA(50)
- exit: go flat at the close when MA(10) <= MA(50)
- position sizing: 100% of a fixed $10,000 notional, no leverage, no compounding
- universe: AAPL only
- rebalance: evaluated daily at the close, executed next close

DATA + TIMEFRAME:
- symbols: AAPL
- source: stooq via fetcher.py (fallback: synthetic, seed=13)
- range: 2015-01-02 → 2025-01-23 (2520 bars, 10.0 yrs)
- frequency: daily

NAIVE RESULT (gross, no costs, in-sample):
- CAGR: +3.46%
- Sharpe: +0.21
- max DD: -31.31%
- trades: 69

AFTER COSTS + OOS:
- cost model: fee 1.0 bps + slippage 5.0 bps, borrow 50 bps/yr (unused, long-flat)
- turnover/yr: 6.9
- total cost paid: 4.14% of capital
- net Sharpe: +0.19
- OOS Sharpe (walk-forward, 5 folds): +0.08
- OOS vs IS ratio: 0.42  (< 0.5: the in-sample result was not real)

VERDICT: KILL

WHY:
It made +3.0%/yr while simply holding the asset made +8.0%/yr, so the strategy's
only achievement was cutting volatility from 22.0% to 16.3%, and it paid 5 points
of annual return for that. Costs were NOT the cause — they took only 0.03 of
Sharpe at 7 trades a year — the signal itself arrives too late, after roughly
15% of each move, so in a drifting market being out 48% of the time costs more
than the drawdowns avoided. Out-of-sample Sharpe (0.08) is 42% of in-sample
(0.19), and individual folds swing from -1.74 to +1.90, which with 69 total
trades means I cannot distinguish this from zero.

WHAT I'D TRY NEXT (max 2, each a NEW testable claim):
1. 200-day trend filter — claim: removes whipsaw entries in sideways regimes,
   cutting turnover >25% for <15% CAGR. → TESTED AS S02: FAILED (trades +38%,
   CAGR -77%). Claim dead, do not retry.
2. 5-symbol universe — claim: if trend persistence is real it shows up on more
   than one asset. Test in Week 2 alongside S05.

---
PRE-REGISTRATION (filled 2025-01-13, BEFORE the first backtest):
- kill criteria: net Sharpe < 0.5 OR OOS Sharpe < 50% of IS OR total cost paid
  > 50% of gross return OR fewer than 30 trades in sample
- expected turnover: 7/yr, estimated from the MA10/50 crossing frequency on
  monthly data (roughly 8-10 crossings/yr, minus those that revert within a day)
