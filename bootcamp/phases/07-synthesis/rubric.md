# Phase 07 Rubric — Synthesis (Week 13, final gate)

**Gate:** ≥80/100 AND the repo is public AND `pytest -q` passes from a clean
clone.

| # | Criterion | Weight | Check | Score |
|---|---|---|---|---|
| 1 | **Writeup quality** | 30 | every claim traceable; all 5 required sections; no hedging | /30 |
| 2 | **Repo legibility** | 20 | quick start works from clean clone; README complete | /20 |
| 3 | **Notes vault** | 20 | `NOTES.md` indexed, ≥100 notes, counts by type | /20 |
| 4 | **Self-grade** | 15 | all 6 components scored with evidence paths | /15 |
| 5 | **Graveyard + journal** | 10 | ≥10 rows, 13 weekly entries, final feedback loop | /10 |
| 6 | **Honesty** | 5 | shortfalls recorded rather than papered over | /5 |

**Pass: ≥80/100 AND the repo is public AND the test suite passes.**

---

## Detailed checks

### 1. Writeup quality (30)
- [ ] What I built — concrete, with counts
- [ ] What died and why — with mechanisms, not "market conditions"
- [ ] What survived and by how much — with numbers and confidence intervals
- [ ] What I would do differently — specific, actionable
- [ ] What I still do not know — genuine, not false modesty
- [ ] every number traceable to a file in the repo

### 2. Repo legibility (20)
- [ ] `git clone` + `pip install -r requirements.txt` + `pytest -q` works
- [ ] at least one strategy runs from the README's instructions
- [ ] no secrets in history
- [ ] structure matches the scaffold

### 3. Notes vault (20)
- [ ] `NOTES.md` exists with an index by type and by week
- [ ] ≥100 notes (≥140 for full marks), counted and reported
- [ ] links resolve

### 4. Self-grade (15)
- [ ] all 6 components of `grading.md` scored
- [ ] each score has ≥1 evidence path
- [ ] the total is stated and justified

### 5. Graveyard + journal (10)
- [ ] graveyard has ≥10 rows, each with a concept-level root cause
- [ ] 13 weekly journal entries
- [ ] final feedback-loop answers reference the graveyard

### 6. Honesty (5)
- [ ] `reports/final-audit.md` lists shortfalls
- [ ] no backfilled notes presented as contemporaneous
- [ ] no claim in the writeup unsupported by an artifact

---

## Calibration

**Pass (85):** writeup complete and traceable; repo clones and runs; notes
indexed; self-grade has evidence. Some shortfalls recorded.

**Pass (100):** all of the above, plus: the writeup's "what I still do not know"
section is specific and technical; the graveyard includes a self-kill (a strategy
you killed on live data, or a belief about trading that your own data killed);
the notes vault exceeds 140 with all four criteria met per note; and the
self-grade is harsher than any external grader would be.

**Fail (70):** writeup has unsupported claims; or the repo does not clone-and-run;
or notes below 100 with no shortfall recorded.

**Fail (<60):** no writeup; or the repo is not public; or the test suite fails.

---

## The single question that decides the grade

> If a competent, skeptical quant read only your `capstone/writeup.md` and your
> `graveyard/graveyard.md`, would they believe you ran the loop, or would they
> believe you tuned until something looked good?

Everything in this course was designed to make the honest answer to that question
"they ran the loop". If your artifacts support the other answer, the course did
not work — and the writeup should say so.

## Self-grade

| Criterion | Score | Evidence |
|---|---|---|
| Writeup quality | /30 | |
| Repo legibility | /20 | |
| Notes vault | /20 | |
| Self-grade | /15 | |
| Graveyard + journal | /10 | |
| Honesty | /5 | |
| **Total** | **/100** | |

**FINAL GATE: PASS / FAIL** — date:
