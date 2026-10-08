# Week 12 — Thirty days of live paper trading

> **Phase 06 · Live paper** · Hours: 10–14 study time + **30 calendar days**
> · Deliverable: `live/live-log.md` with 30 daily entries
>
> The clock is calendar time. If you have not created the paper account yet, do
> it today and start logging day 1 — you can finish Weeks 10–11 while the clock
> runs.

---

## 🎯 WEEK OBJECTIVE

```text
🎯 OBJECTIVE:   Run 2–3 surviving strategies (or P01) in PAPER mode for 30 consecutive trading days, with a daily reconciliation that has zero unexplained gaps
WHY:          Live execution is where the last category of self-deception lives: the gap between what your backtester assumes and what a broker actually does. Nothing else in the course exposes it.
INPUT:        phases/06-live-paper/harness/harness.py, strategies/P01_combined_portfolio/, a paper broker account
OUTPUT:       live/live-log.md (30 daily entries)
              live/reconciliation.csv (one row per day per symbol)
              live/reconciliation.ipynb (filled)
              live/incidents.md (every error, with a root cause)
              notes/daily/week-12/*.md (7)
              notes/concepts/operational-risk.md
PROOF:        30 consecutive dated entries; every status != OK has a written explanation; realized slippage is reported against the backtest assumption
TIME:         600–840 min study + 30 calendar days
BLOCKER IF:   any SIDE_DIFF is unresolved — stop trading, root-cause it, then resume and extend the 30 days
```

---

## Daily objectives

### Monday — Set up, dry-run, prove the guard works

```text
🎯 OBJECTIVE:   Create the paper account, configure the harness, and run it in dry-run for one full cycle
WHY:          Day 1 should touch nothing. You are validating the plumbing, not the strategy.
INPUT:        harness/harness.py, live-config.example.json
OUTPUT:       live/config.json (no secrets), live/orders.log (dry-run entries)
              notes/daily/week-12/mon.md
PROOF:        `python harness.py --plan` prints targets and orders and submits nothing; `pytest harness/test_harness.py -q` is green (22 tests)
TIME:         120 min
BLOCKER IF:   any credential appears in the repo, config, or logs — rotate it immediately
```

Secrets live in environment variables ONLY:

```bash
export ALPACA_KEY="..."       # paper key
export ALPACA_SECRET="..."
# or
export CCXT_KEY="..."
export CCXT_SECRET="..."
```

`.gitignore` already excludes `live/credentials.*` and `.env`. Verify with
`git status` that no secret file is trackable before your first commit of the
week.

### Tuesday — Go live (paper). Log day 1.

```text
🎯 OBJECTIVE:   Submit your first paper orders and complete the first reconciliation
WHY:          The first real day surfaces every wiring mistake at once. Better day 1 than day 20.
INPUT:        harness.py, your targets
OUTPUT:       live/reconciliation.csv (day 1 rows), live/live-log.md (day 1)
              notes/daily/week-12/tue.md
PROOF:        day 1 has a row per symbol with intended, actual, diff, status, and an explanation for every non-OK row
TIME:         90 min
BLOCKER IF:   you cannot explain a single gap — do not proceed to day 2
```

### Wednesday — Automation and the first incident

```text
🎯 OBJECTIVE:   Automate the daily cycle (scheduled job or a cron you run manually) and write your first incident entry
WHY:          Manual execution fails on day 9 when you are busy. Automate the mechanics; keep the reconciliation manual.
INPUT:        harness.py, your day-1 experience
OUTPUT:       live/run-daily.sh (or a documented manual checklist you follow every day)
              live/incidents.md (first entry, with a root cause)
              notes/daily/week-12/wed.md
PROOF:        the daily cycle is reproducible in under 10 minutes, and the incident entry names a root cause rather than a symptom
TIME:         120 min
BLOCKER IF:   the daily cycle depends on you remembering a step
```

### Thursday — Measure slippage against your assumption

```text
🎯 OBJECTIVE:   Compute realized slippage from your fills and compare it to the 5 bps your backtests assumed
WHY:          This is the single most valuable measurement of the week. If realized slippage is 3x your assumption, several of your verdicts are wrong and you must restate them.
INPUT:        live/reconciliation.csv
OUTPUT:       reports/live-slippage.md (distribution, mean, p95, vs assumed)
              notes/daily/week-12/thu.md
PROOF:        the report states the ratio of realized to assumed slippage
TIME:         90 min
BLOCKER IF:   you report realized slippage without comparing it to the backtest assumption
```

### Friday — The turn-over discrepancy check

```text
🎯 OBJECTIVE:   Compare live turnover to backtest turnover and resolve any difference
WHY:          If your live strategy trades more than your backtest did, the live signal differs from the backtested signal. That is a bug until proven otherwise.
INPUT:        live/reconciliation.csv, your P01 tear sheet
OUTPUT:       reports/live-turnover.md (live vs backtest turnover, and the explanation for any gap)
              notes/daily/week-12/fri.md
PROOF:        the ratio is reported and any ratio above 1.5 has a named cause
TIME:         90 min
BLOCKER IF:   the ratio exceeds 1.5 with no explanation
```

### Saturday — The halfway reconciliation review

```text
🎯 OBJECTIVE:   Fill the reconciliation notebook through day 15 and review every incident
WHY:          Halfway is the right time to fix systemic problems, while there is still time to log 15 clean days.
INPUT:        live/reconciliation.csv, live/incidents.md
OUTPUT:       live/reconciliation.ipynb (panels 1–6 filled through day 15)
              live/incidents.md (each incident has a root cause AND a prevention)
              notes/daily/week-12/sat.md
PROOF:        zero unexplained gaps through day 15
TIME:         120 min
BLOCKER IF:   any unexplained gap remains — the grader checks this exact number
```

### Sunday — Journal + operational-risk concept note

```text
🎯 OBJECTIVE:   Write notes/concepts/operational-risk.md and the Week 12 journal entry
WHY:          Operational risk is the risk your backtester has never heard of: API outages, halts, stale data, corporate actions, your own inattention.
INPUT:        live/incidents.md
OUTPUT:       notes/concepts/operational-risk.md
              journal/lessons.md (Week 12 entry)
              notes/daily/week-12/sun.md
PROOF:        the concept note lists every operational failure you hit and the control you added for each
TIME:         90 min
BLOCKER IF:   the note lists failures without controls
```

> **Note:** days 16–30 continue past this week. Keep logging daily. The Week 13
> work (capstone) can proceed in parallel once you are past ~day 15 with clean
> reconciliation, but the 30 days must be complete before the capstone is
> published.

---

## Deliverables

| Artifact | Path |
|---|---|
| Live log (30 entries) | `live/live-log.md` |
| Reconciliation data | `live/reconciliation.csv` |
| Reconciliation notebook | `live/reconciliation.ipynb` (filled) |
| Incidents | `live/incidents.md` |
| Slippage report | `reports/live-slippage.md` |
| Turnover report | `reports/live-turnover.md` |
| Config (no secrets) | `live/config.json` |
| Notes | `notes/daily/week-12/*.md` × 7, `notes/concepts/operational-risk.md` |

### Daily log entry template (copy into `live/live-log.md`)

```markdown
## Day N — YYYY-MM-DD

INTENDED (computed before open):
- SPY 20% | QQQ 20% | IWM 20% | TLT 20% | GLD 20%

ACTUAL (after close):
- SPY 19.4% | QQQ 20% | IWM 20% | TLT 20% | GLD 18.9%

DIFFERENCES:
- SPY -0.6%: partial fill, order capped by max_order_notional ($2,000)
- GLD -1.1%: order rejected — "insufficient buying power" (paper account quirk)

SLIPPAGE: mean 4.2 bps across 3 fills (backtest assumed 5.0) — 0.84x

INCIDENTS: none new.

WHAT I LEARNED TODAY:
The max_order_notional cap silently scales every order on rebalance days, so my
live weights never match targets exactly on day 1. Fix: pre-scale targets, then
let the cap be a true safety net rather than a routine limit.

TOMORROW: apply the pre-scaling, re-run, confirm the day-2 gap closes.
```

---

## 📐 CONCEPT INJECTIONS

### 📐 CONCEPT — Operational risk

```text
📐 CONCEPT: Operational risk (the risk your backtester cannot see)
WHY NOW:   Wednesday's incident entry. Your backtester assumes fills are instant, markets are
           open, data is correct, and you are paying attention. None of those are guaranteed.
FORMULA:   There is no formula. That is the point. Operational risk is a LIST, and the control
           for each item is a check that runs before you trade:
             - data staleness     -> assert latest bar is < 1 day old
             - symbol halt        -> check tradable flag before submitting
             - insufficient bp    -> check buying power against intended notional
             - duplicate orders   -> idempotency key = (date, strategy, symbol)
             - corporate action   -> re-fetch adjusted prices before sizing
             - API failure        -> retry with backoff, then FLAT, never "assume filled"
CODE:      assert (pd.Timestamp.utcnow().tz_localize(None) - px.index[-1]).days <= 1, "stale data"
           assert not orders.duplicated(['symbol']).any(), "duplicate orders"
EXAMPLE:   Day 3: TLT order rejected for insufficient buying power because the paper account had
           not settled prior sales. The backtester has no concept of settlement. Control added:
           check `buying_power >= intended_gross_notional * 1.1` before submitting, and shrink
           proportionally if not. Documented in incidents.md, tested in test_harness.py.
TIME:      15 min
NOTE:      write notes/concepts/operational-risk.md
DONE WHEN: you can list every operational failure you hit with a control for each, explain in
           2 sentences why a backtester structurally cannot model them, and spot the retry loop
           that assumes an order filled when the API timed out
```

### 📐 CONCEPT — Realized vs assumed costs

```text
📐 CONCEPT: Measuring realized slippage and restating verdicts
WHY NOW:   Thursday's blocker. Every verdict you shipped assumed 5 bps. Now you have real fills
           and can check that number -- and if it is wrong, several verdicts are wrong.
FORMULA:   slippage_bps = (fill_price - decision_price) / decision_price * 1e4 * side
           (side = +1 for buys, -1 for sells; POSITIVE means you paid more than the decision price)
           restated_net_cagr = gross_cagr - turnover_yr * realized_bps / 1e4
CODE:      rec['slip_bps'] = (rec['filled_avg_px'] - rec['price']) / rec['price'] * 1e4 \\
                             * np.where(rec['side'] == 'buy', 1, -1)
           print(rec['slip_bps'].mean(), rec['slip_bps'].quantile(.95))
EXAMPLE:   Realized mean 14 bps vs the assumed 5 bps = 2.8x. S05 (turnover 22/yr) loses an extra
           0.20%/yr -- survives. S03 (turnover 118/yr) loses an extra 1.06%/yr -- it was already
           dead, now it is deader. Restate both verdicts with the realized number and note that
           only strategies under ~30 trades/yr are viable at this cost level on this broker.
TIME:      20 min
NOTE:      write notes/concepts/realized-vs-assumed-costs.md
DONE WHEN: you can compute signed slippage in 3 lines, explain in 2 sentences why the sign flips
           for sells, and spot a slippage calculation without the side flip (symptom: sells show
           NEGATIVE slippage, i.e. the strategy appears to profit from trading)
```

---

## ✅ CHECKPOINT RUBRIC — Week 12 gate (Phase 6 gate)

- [ ] **30 consecutive daily entries** in `live/live-log.md`
- [ ] Paper mode proven (screenshot or broker statement showing paper/testnet)
- [ ] `live/reconciliation.csv`: one row per day per symbol
- [ ] **Zero unexplained gaps** (every status != OK has an `explanation`)
- [ ] `live/reconciliation.ipynb`: all 6 panels filled
- [ ] `live/incidents.md`: every error, with root cause AND prevention
- [ ] `reports/live-slippage.md`: realized vs assumed, ratio stated
- [ ] `reports/live-turnover.md`: live vs backtest, ratio explained
- [ ] No secrets anywhere in the repo (`git log -p | grep -i key` returns nothing)
- [ ] 7 daily notes + 1 concept note

**GATE: PASS / FAIL**

## ⚰️ GRAVEYARD PROMPT

> 1. **Assume-fill attack:** deliberately let one order fail (e.g. submit an
>    untradable symbol) and record what your harness does. If it assumes the fill,
>    that is the most dangerous bug in the entire course. Log it and fix it.
> 2. **Stale-data attack:** run the harness on yesterday's data as if it were
>    today. Record the size of the position error.
> 3. **Cost-restatement attack:** take your best surviving strategy and restate
>    its verdict at the REALIZED slippage you measured. If it dies, kill it. This
>    is the only graveyard entry in the course that comes from live data.

## Next

Phase 7 (`../07-synthesis/`): the capstone writeup and the public repo.
