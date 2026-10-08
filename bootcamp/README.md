# Quant Trading Bootcamp — 13 Weeks, Solo, Ship-Or-Die

**Start Week 1 Day 1: run `bootstrap.sh`, open `phases/01-foundation/week-01.md`.**

Outcomes: you ship **16 tested strategies** (each with costs, out-of-sample, and a written verdict), build and unit-test your **own backtester**, replicate **3 published papers**, and run **30 days of live paper trading** with daily reconciliation — all in a public repo plus a graded notes vault (~140 notes).

```bash
git clone <this-repo> && cd animated-enigma/bootcamp
./bootstrap.sh ~/quant-bootcamp     # creates your working repo
cd ~/quant-bootcamp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                 # must be green on Day 1
open phases/01-foundation/week-01.md   # or: cat phases/01-foundation/week-01.md
```

---

## What this is

A project-driven bootcamp for someone who already knows pandas and wants to stop
reading about trading and start shipping. Every week ends in a **gate**: you ship
the artifact or you do not advance. There is no partial credit for "I
understand the concept now" — concepts are injected only when a deliverable is
failing and cannot be fixed without them.

**The five rules you will be graded against**

| Rule | What it means in practice |
|---|---|
| Build first, theory second | You write the strategy on Tuesday. The math arrives Thursday, when the strategy breaks. |
| Single-purpose deliverables | One artifact teaches one thing. A file that teaches two things is two files. |
| Failure is graded | The graveyard is a required, structured artifact. Killed strategies are the point. |
| Ship or don't advance | Every week has a pass/fail gate with an explicit checklist. |
| Costs, OOS, verdicts mandatory | A strategy without all three is not a strategy, it is a screenshot. |

## What you need

- Python 3.10+, 10–20 hrs/week, and the discipline to write notes the same day.
- Dependencies: `pandas`, `numpy`, `matplotlib`, `pyarrow`, `pytest`. **No paid
  APIs.** See `requirements.txt`.
- Money: **$0**. Data is free (stooq), broker is paper mode (Alpaca paper or
  CCXT sandbox). Nothing in this course requires a funded account.

## How the week runs

```
Mon  Pick the strategy. Write a 1-paragraph thesis BEFORE writing code.
Tue  Build v0. Ugly, but it runs.
Wed  Backtest it. No filters, no excuses.
Thu  Break it. Costs, out-of-sample, walk-forward.
Fri  Diagnose. Learn the one concept that explains the break. Write a concept note.
Sat  Rebuild it with the fix.
Sun  Verdict. Journal. Graveyard. Strategy note.
```

Seven daily notes. Every day. That is the tax for the whole course.

## The tree

```
bootcamp/
├── README.md              <- you are here
├── syllabus.md            <- 13 weeks, phases, milestones, hours
├── grading.md             <- weights, gates, feedback-loop questions
├── strategy-ledger.md     <- the 16 strategies; you fill it in as you ship
├── bootstrap.sh           <- creates your working repo
├── requirements.txt
├── phases/
│   ├── 01-foundation/         W1-2   5 strategies on a borrowed backtester
│   ├── 02-engine/             W3-4   build + test your own event-driven engine
│   ├── 03-strategy-factory/   W5-7   8 strategies, config-driven
│   ├── 04-paper-replication/  W8-9   3 published papers reproduced
│   ├── 05-risk-portfolio/     W10-11 sizing, risk, portfolio of survivors
│   ├── 06-live-paper/         W12    30 days live, daily reconciliation
│   └── 07-synthesis/          W13    capstone writeup + public repo
├── shared/                <- copy-paste templates + runnable modules
│   ├── repo-scaffold/     the repo you clone
│   ├── data-fetcher/      fetcher.py + tests
│   ├── metrics-module/    metrics.py + tests
│   ├── backtester/        backtester.py + tests  (the minimal engine)
│   ├── journal-template.md
│   └── notes-templates/   concept / strategy / failure / daily
└── capstone/              rubric, writeup template, portfolio template
```

## Grading at a glance

| Component | Weight |
|---|---|
| Strategy verdicts (16 shipped) | 25% |
| Backtester quality (custom, tested, documented) | 15% |
| Paper replications (3) | 15% |
| Live paper log (30 days + reconciliation) | 15% |
| Journal + graveyard | 15% |
| Notes vault (~140 notes) | 15% |

Full rubrics: `grading.md`, per-phase `rubric.md`, `capstone/rubric.md`.

## The one thing that will actually kill your progress

Look-ahead bias. Not leverage, not costs, not overfitting — **look-ahead**. It
makes dead strategies look like genius, and it is invisible in code review if you
do not know where to look. `shared/backtester/test_backtester.py` contains the
tests that catch it, written before you need them. Read
`test_peeking_signal_is_caught_by_an_absurd_sharpe` today. It will save you a
month.

## License / disclaimer

Educational. Paper trading only. Nothing here is investment advice; the example
harness in `phases/06-live-paper/` is hard-wired to demo/paper mode and refuses
to run against a live account.
