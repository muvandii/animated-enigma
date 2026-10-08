# Failure: <short name>

DATE: <YYYY-MM-DD>
STRATEGY: <ID + name>

WHAT BROKE:
<The observable symptom, with the number. "Net Sharpe went from +0.9 to -0.2
when I added 20 bps of slippage." Not "it didn't work".>

ROOT CAUSE:
<The mechanism. Keep asking "why" until you hit something you could have
predicted in advance. "It was overfit" is not a root cause — overfit to WHAT?>

CONCEPT THAT EXPLAINS IT:
<The named concept. If you cannot name it, you have not diagnosed it; go write a
concept note first, then come back.>

FIX ATTEMPTED:
<What you changed, exactly. Files and parameter values.>

DID FIX WORK: <YES / NO / PARTIALLY — with the new number>

LESSON:
<One sentence, phrased as a rule you will actually follow next time. "Compute
turnover before backtesting, and abandon any signal whose annual cost exceeds
half the expected edge.">

---
Graveyard row added? ☐   (graveyard/graveyard.md)
