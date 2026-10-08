# Week 13 — Synthesis, writeup, public ship

> **Phase 07 · Synthesis** · Hours: 14–18 · Deliverable: a public repo
>
> Everything exists. This week you make it legible to a stranger, and you are
> graded on whether the artifacts support the claims you make.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Publish the repo, write capstone/writeup.md, and self-grade against capstone/rubric.md
WHY:          Work that nobody can audit is indistinguishable from work that did not happen. The writeup is where you find out whether your 13 weeks hold together as an argument.
INPUT:        everything: strategies/, engine/, papers/, live/, notes/, graveyard/, journal/, reports/
OUTPUT:       capstone/writeup.md (complete, from the template)
              capstone/portfolio.md (from the portfolio template)
              README.md (repo root, rewritten as a public document)
              NOTES.md (the notes vault, exported and indexed)
              graveyard/graveyard.md (complete)
              SELF-GRADE.md (every rubric self-graded, with totals)
              notes/daily/week-13/*.md (7)
PROOF:        a stranger can clone the repo, run `pytest -q` and one strategy, and understand what you did, what died, and what you concluded
TIME:         840–1080 min
BLOCKER IF:   the writeup claims a result whose supporting artifact does not exist in the repo
```

---

## Daily objectives

### Monday — The audit

```text
🎯 OBJECTIVE:   Run a completeness audit: every deliverable vs every rubric, and list what is missing
WHY:          You will discover gaps. Monday is when there is still time to fill them.
INPUT:        all phase rubrics, grading.md
OUTPUT:       reports/final-audit.md (one line per requirement: present / missing / weak)
              notes/daily/week-13/mon.md
PROOF:        every row of every rubric is accounted for, including the ones you failed
TIME:         150 min
BLOCKER IF:   the audit skips requirements you know you failed
```

### Tuesday — Fill the gaps

```text
🎯 OBJECTIVE:   Fix every "missing" row from the audit, or record it as a known shortfall
WHY:          A documented shortfall is honest. A silently missing artifact is not.
INPUT:        reports/final-audit.md
OUTPUT:       missing artifacts created OR a written shortfall note in SELF-GRADE.md
              notes/daily/week-13/tue.md
PROOF:        every "missing" row is now either present or explicitly recorded as a shortfall with a reason
TIME:         180 min
BLOCKER IF:   you invent an artifact on Tuesday to fill a row (e.g. backfilling 5 daily notes you did not write)
```

⚠️ **Do not backfill notes.** If you are missing daily notes, record the
shortfall and take the grade hit. Backfilled notes are fiction, and the point of
the notes vault is that it is a contemporaneous record.

### Wednesday — The writeup

```text
🎯 OBJECTIVE:   Write capstone/writeup.md from capstone/writeup-template.md
WHY:          This is the artifact a stranger reads first. It is also the artifact where vagueness is most tempting and least forgivable.
INPUT:        everything, capstone/writeup-template.md
OUTPUT:       capstone/writeup.md
              notes/daily/week-13/wed.md
PROOF:        every number in the writeup is traceable to a file in the repo; no unattributed claims
TIME:         180 min
BLOCKER IF:   any claim in the writeup has no corresponding artifact
```

Required sections: what I built, what died and why, what survived and by how
much, what I would do differently, and what I still do not know. The last two are
the ones people skip.

### Thursday — The portfolio page and the README

```text
🎯 OBJECTIVE:   Write capstone/portfolio.md and rewrite the repo README as a public document
WHY:          The README is the front door. A clone-and-run that works in one command is the difference between a portfolio piece and a folder.
INPUT:        capstone/portfolio-template.md, strategy-ledger.md
OUTPUT:       capstone/portfolio.md, README.md (rewritten)
              notes/daily/week-13/thu.md
PROOF:        a clean clone + `pip install -r requirements.txt` + `pytest -q` + one strategy run works from the README's instructions alone
TIME:         150 min
BLOCKER IF:   the README's quick start does not work from a clean checkout
```

### Friday — Export and index the notes vault

```text
🎯 OBJECTIVE:   Export the notes vault to NOTES.md with an index, and verify the count
WHY:          The vault is 15% of the grade. An unindexed folder of 140 markdown files is not a vault, it is a dumping ground.
INPUT:        notes/**
OUTPUT:       NOTES.md (index: by type, by week, by concept; with counts)
              notes/daily/week-13/fri.md
PROOF:        the index reports counts by type and links every note; the total matches grading.md's requirement
TIME:         120 min
BLOCKER IF:   the note count is below 100 (course fail territory) and you have not recorded it
```

### Saturday — Self-grade

```text
🎯 OBJECTIVE:   Complete SELF-GRADE.md: every rubric scored with evidence file paths
WHY:          Self-grading is only meaningful if each score links to a file. A score without evidence is an opinion.
INPUT:        grading.md, all phase rubrics, capstone/rubric.md
OUTPUT:       SELF-GRADE.md
              notes/daily/week-13/sat.md
PROOF:        all 6 components of grading.md scored, each with ≥1 evidence path, and a justified total
TIME:         150 min
BLOCKER IF:   any component is scored without an evidence path
```

### Sunday — Publish, and answer the three questions one last time

```text
🎯 OBJECTIVE:   Push the repo public and write the final journal entry with the three feedback-loop answers
WHY:          Shipping is the last gate. An unpublished repo is a private project with an audience of one.
INPUT:        everything
OUTPUT:       public repo (pushed), journal/lessons.md (Week 13 + final feedback-loop answers)
              notes/daily/week-13/sun.md
PROOF:        the repo is public, `pytest -q` passes from a clean clone, and the three feedback-loop questions are answered with numbers from all 13 weeks
TIME:         120 min
BLOCKER IF:   the final journal entry does not reference the graveyard
```

---

## 📐 CONCEPT INJECTION (the last one)

### 📐 CONCEPT — What a strategy actually is, after 13 weeks

```text
📐 CONCEPT: A strategy is a claim, a cost structure, and a capacity limit
WHY NOW:   Wednesday's writeup. You have 16 folders and need to say what they add up to. They are
           not 16 things; they are 16 instances of one thing, and being able to state that thing
           is the difference between a portfolio and a pile.
FORMULA:   strategy = (edge per trade) x (trades per year) - (cost per trade x trades per year)
                    - (capacity limit: at what AUM does impact consume the edge?)
           edge per trade must be stated in BPS, not in Sharpe. Sharpe hides turnover.
           capacity: max_AUM ~ (edge_bps / impact_coefficient)^2 x ADV
CODE:      edge_bps = (gross_cagr - bench_cagr) / (trades_per_year * 2) * 1e4
           breakeven = cost_bps                        # the strategy needs edge_bps > cost_bps
           print(f"edge {edge_bps:.1f} bps/trade vs cost {cost_bps:.1f} bps -> "
                 f"{'viable' if edge_bps > cost_bps else 'dead'}")
EXAMPLE:   S05: +6.8%/yr over benchmark on 22 trades/yr = ~155 bps per round trip, against ~6 bps
           of cost. Comfortable. S03: +9.4%/yr on 118 trades/yr = ~40 bps per round trip against
           6 bps -- viable in theory, but the per-trade edge is 4x smaller and any slippage
           increase kills it first. That single comparison explains the entire graveyard.
TIME:      20 min
NOTE:      write notes/concepts/what-a-strategy-is.md
DONE WHEN: you can convert any strategy into bps-per-trade in 3 lines, explain in 2 sentences why
           bps-per-trade is more informative than Sharpe for comparing turnover regimes, and spot
           a writeup that ranks strategies by Sharpe alone
```

---

## ✅ CHECKPOINT RUBRIC — Week 13 gate (final gate)

- [ ] `capstone/writeup.md` complete, every claim traceable
- [ ] `capstone/portfolio.md` complete
- [ ] `README.md` rewritten; quick start works from a clean clone
- [ ] `NOTES.md` index complete with counts
- [ ] `graveyard/graveyard.md` complete (≥10 rows)
- [ ] `SELF-GRADE.md`: all 6 components scored with evidence paths
- [ ] Repo is public; `pytest -q` passes
- [ ] 7 daily notes; final journal entry with all three feedback-loop answers

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT — the last one

> Write one graveyard entry for **the course itself**: the belief about trading
> you held in Week 1 that your own data has now killed. It must cite a file.
>
> Example: *"Week 1: I believed a good backtest meant a good strategy. Killed by
> S03, whose gross Sharpe was +0.94 and net Sharpe was −0.21 — and by the Week 7
> sweep, which showed the best-of-24 Sharpe was mostly selection."*

## After

The course is over. Three things are now true that were not true 13 weeks ago:

1. You can tell, in about an hour, whether a strategy claim is worth testing.
2. You have a public record that proves it.
3. You know what you do not know, in writing, with numbers.

That third one is the most valuable and the rarest. Do not lose it.
