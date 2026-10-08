# Strategy: <ID> <name>

SOURCE: <where the idea came from: paper, blog, book, my own head — be specific>

THESIS:
<1 paragraph. The CAUSAL claim: why should this work? Who is on the other side
and why are they willing to lose? If your thesis is "it backtested well" you do
not have a thesis.>

RULES:
- entry:
- exit:
- position sizing:
- universe:
- <be precise enough that someone else could reimplement it from this note alone>

DATA + TIMEFRAME:
- symbols:
- source:
- range: <start> → <end> (<N> bars, <M> yrs)
- frequency:

NAIVE RESULT (gross, no costs, in-sample):
- CAGR: 
- Sharpe: 
- max DD: 
- trades: 

AFTER COSTS + OOS:
- cost model: <fee> bps + <slippage> bps, borrow <x> bps/yr
- turnover/yr: 
- total cost paid: <% of capital>
- net Sharpe: 
- OOS Sharpe (walk-forward): 
- OOS vs IS ratio: <OOS/IS — if < 0.5, say so plainly>

VERDICT: <SHIP (paper) | KILL>

WHY:
<3 sentences, no hedging. Name the single number that decided it. If KILL, name
the mechanism — not "needs more tuning".>

WHAT I'D TRY NEXT (max 2, each a NEW testable claim):
1. <change> — claim: <what should happen and why> — test: <how, with dates>
2. <change> — claim: <...> — test: <...>

---
PRE-REGISTRATION (filled in BEFORE the first backtest — do not edit after):
- kill criteria: <numbers>
- expected turnover: <computed from the signal, not from the backtest>
