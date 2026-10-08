# Capstone Rubric — the final artifact

The capstone is the whole package: repo + writeup + notes vault + portfolio page.
This rubric grades it as a single artifact, complementing the six weighted
components in `../grading.md`.

```text
🎯 OBJECTIVE:   Ship a public repo where a stranger can audit every claim in the writeup
WHY:          A portfolio of backtests is not evidence of skill; a portfolio of backtests with
              a graveyard, a notes vault, and traceable claims is.
INPUT:        13 weeks of artifacts
OUTPUT:       public repo + capstone/writeup.md + capstone/portfolio.md + NOTES.md + SELF-GRADE.md
PROOF:        clean-clone `pytest -q` passes; every number in the writeup resolves to a file
TIME:         840–1080 min (Week 13)
BLOCKER IF:   any claim in the writeup has no supporting artifact
```

---

## The six questions a grader asks

Score each 0–10. Total /60. Add the `grading.md` weighted score for the final
result.

### 1. Can I run it? (0–10)
- 10: clone → `pip install -r requirements.txt` → `pytest -q` → one strategy, all
  from the README, on a clean machine.
- 5: it runs, but the README is incomplete or a step is undocumented.
- 0: it does not run.

### 2. Is the evidence complete? (0–10)
- 10: 16 strategies with costs + OOS + verdicts; engine with 40+ tests; 3
  replications with delta tables; 30 live days; graveyard; journal.
- 5: most of it, with documented shortfalls.
- 0: major components missing and undocumented.

### 3. Is it honest? (0–10)
- 10: kill rate reported; deflated Sharpe computed; the writeup's "what I still
  do not know" section is technical and specific; a self-kill is present.
- 5: honest but thin — no self-kill, vague uncertainties.
- 0: claims unsupported by artifacts, or notes backfilled.

### 4. Is the graveyard real? (0–10)
- 10: ≥10 rows, every root cause names a concept, failure notes are dated to the
  day of the failure.
- 5: ≥5 rows with concept-level causes.
- 0: <5 rows, or causes like "needs more tuning".

### 5. Can I follow the reasoning? (0–10)
- 10: every number in the writeup traces to a file; the traceability appendix is
  complete; the argument is easy to follow.
- 5: mostly traceable, a few unattributed numbers.
- 0: claims without artifacts.

### 6. Did they learn anything measurable? (0–10)
- 10: a specific belief is identified, tested, and killed by their own data; the
  journal shows the evolution; at least one concept changed the code.
- 5: general reflections without numbers.
- 0: no evidence of change.

---

## Bands

| Total | Band |
|---|---|
| 55–60 | Exceptional. Publish it, write about it, put it in front of people. |
| 45–54 | Strong. Real evidence of the loop being run, honestly reported. |
| 35–44 | Pass. The loop ran; the reporting is thin somewhere. |
| 25–34 | Marginal. Artifacts exist but the argument does not hold together. |
| <25 | Fail. |

## Automatic failures

- Real money was traded.
- Secrets in the repository history.
- Fewer than 15 strategies shipped.
- Fewer than 30 live paper days.
- Notes backfilled and presented as contemporaneous.
- A writeup whose central claim is contradicted by an artifact in the same repo.

## The last check

Open `capstone/writeup.md`. For every sentence that contains a number, find the
file that produced it. If you cannot, either find the file or cut the sentence.
What remains is the capstone.
