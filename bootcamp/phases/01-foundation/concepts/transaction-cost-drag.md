# Concept: transaction cost drag  (EXEMPLAR)

WHEN I LEARNED IT: 2025-01-17 — while S01's net Sharpe (0.19) refused to diverge
from its gross Sharpe (0.21), and I could not tell whether that gap was real or a
bug in my cost model.

DEFINITION (2 sentences):
Cost drag is the expected return consumed per year by trading, equal to the
fraction of the portfolio traded per year multiplied by the round-trip cost per
unit traded. It turns a gross forecast into a net one and scales linearly with
turnover, which is why high-frequency signals need proportionally bigger edges.

FORMULA:
```
annual_drag = turnover_per_bar x periods_per_year x (fee_bps + slippage_bps) / 10_000
break-even  : your gross edge must exceed annual_drag
```

CODE (3–5 lines):
```python
from metrics import turnover
t = turnover(res.position)          # S01: 0.0274 per bar
print(t * 252 * 6 / 10_000)         # 0.00414 -> 0.41% per year
```

WHERE IT LIES / LIMITS:
Assumes linear price impact — true when you are a small fraction of ADV, false
once you move the book, where impact is roughly proportional to
sqrt(size/ADV). It also assumes you can transact at the close every day and
ignores the bid-ask bounce baked into your price data, which makes measured
returns from a strategy that trades at the bid and marks at the mid look better
than they are. It says nothing about taxes or borrow availability.

HOW I'D SPOT IT WRONG IN SOMEONE ELSE'S CODE:
Missing `abs()` on the position delta. Then sells produce NEGATIVE cost, the
strategy's P&L improves every time it trades more, and net Sharpe comes out
ABOVE gross Sharpe. That single symptom — net > gross — is the tell. I check for
it in every tear sheet now.

APPLIED TO:
- **S01** (MA 10/50): turnover 0.0274/bar → 0.41%/yr → 4.14% over the 10-year
  sample. The backtester's `total cost paid` was 4.14%. The model and my
  arithmetic agreed, which is how I knew the cost model was wired correctly.
- **S03** (RSI-2): turnover 0.47/bar → 118 trades/yr → 7.1%/yr of drag. Its gross
  Sharpe was +0.94 and net was −0.21. This is the number that killed it.
- **S05** (Donchian): turnover 0.087/bar → 22 trades/yr → 1.3%/yr. Cheap enough to
  survive; that is part of why it shipped.

DONE WHEN self-check:
- [x] I can code it from scratch in <5 min without looking
- [x] I can explain it in 2 sentences to a non-finance programmer
- [x] I can spot it wrong: net Sharpe > gross Sharpe means a missing abs()
