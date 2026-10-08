# The Concept Injection Contract (copy-paste template)

A concept is injected **only** when a deliverable is failing and cannot be fixed
without it. Never on a schedule, never "while we're here," never because a text-
book puts it in chapter 3.

```text
📐 CONCEPT: <name>
WHY NOW:   <the specific failing artifact this unblocks — name the file>
FORMULA:   <the math, minimal, in the notation the code uses>
CODE:      <3–5 lines, runnable as-is>
EXAMPLE:   <applied to the student's CURRENT deliverable, with their numbers>
TIME:      <10–20 min>
NOTE:      write notes/concepts/<slug>.md using Concept Note Template
DONE WHEN: student can code it, explain it in 2 sentences, and spot it wrong
```

## Rules

- **WHY NOW must name a file.** "You'll need this later" is not a trigger.
  "S01's net Sharpe is 0.19 and gross is 0.21; you cannot say whether that gap
  is real until you can compute a cost drag" is.
- **CODE must run.** 3–5 lines, copy-paste into a REPL, produces the number.
  No `...`, no pseudocode, no imports the student does not already have.
- **EXAMPLE uses the student's actual deliverable**, with the numbers from their
  own run — not a toy about fruit.
- **TIME is 10–20 minutes.** If a concept needs 60 minutes, it is two concepts
  or it is a week's work; split it.
- **NOTE is mandatory and immediate.** Same day. The concept note is the artifact
  that proves the concept was learned.

## DONE WHEN is a three-part test

The student must be able to, out loud:

1. **Code it** — from scratch, without looking, in under 5 minutes.
2. **Explain it in 2 sentences** — to someone who knows pandas but not finance.
3. **Spot it wrong** — look at someone else's (buggy) code and say what is wrong.

If any of the three fails, the concept is not done. Write that in the note.

## Anti-patterns

- Injecting a concept "because it's in the syllabus for this week."
- A concept whose EXAMPLE does not touch the current deliverable.
- A concept with no note prompt. The note IS the assessment.
- Math that arrives before the artifact that needs it. (JIT or nothing.)
