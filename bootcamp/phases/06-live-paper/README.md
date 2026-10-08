# Phase 06 — Live paper trading (Week 12)

**Paper mode only. $0 at risk. 30 calendar days.**

---

## ⚠️ Safety rules (non-negotiable)

1. **The harness cannot trade real money.** `harness/assert_paper()` runs on every
   client construction and refuses any endpoint that does not contain `paper`,
   `sandbox`, `testnet`, or `demo`. There is no override flag. `test_harness.py`
   proves this for live Alpaca and live Binance.
2. **Dry-run is the default.** Real submission requires `--execute` **and**
   `I_UNDERSTAND=1` in the environment. Either one alone does nothing.
3. **Leverage is hard-capped at 1.0x.** `HarnessConfig` raises if you set
   `max_gross_leverage > 1`.
4. **No secrets in the repo.** Credentials come from environment variables.
   `.gitignore` excludes `.env`, `*.key`, and `live/credentials.*`.
5. **22 safety tests.** `pytest harness/test_harness.py -q` must be green before
   your first live day.

## Quick start

```bash
# 1. verify the guards
pytest harness/test_harness.py -q          # expect 22 passed

# 2. plan only (submits nothing)
python harness/harness.py --plan

# 3. when you are ready (paper account first!)
export ALPACA_KEY=... ALPACA_SECRET=...    # paper keys only
python harness/harness.py --execute        # still needs I_UNDERSTAND=1
I_UNDERSTAND=1 python harness/harness.py --execute

# 4. daily reconciliation
python harness/harness.py --reconcile
```

## Files

| Path | What |
|---|---|
| `harness/harness.py` | the paper-only harness: guards, limits, orders, reconciliation |
| `harness/test_harness.py` | 22 safety tests (the guard tests are the important ones) |
| `reconciliation-notebook.ipynb` | the 6-panel daily reconciliation dashboard template |
| `reconciliation-dashboard-spec.md` | what to build, thresholds, what NOT to build |
| `live-config.example.json` | safe-default config, no secrets |
| `week-12.md` | daily objectives, concepts, rubric, graveyard |
| `rubric.md` | Phase 6 gate |

## The one number that is graded hardest

**Unexplained gaps = 0.** Every row in `live/reconciliation.csv` with
`status != OK` must have a written `explanation`. The notebook asserts this in
panel 2. If you cannot explain a gap, you do not go to the next trading day.

## What live trading will teach you that backtesting cannot

Expect to hit at least three of these. Each becomes an incident entry:

- Orders rejected for insufficient buying power (settlement timing)
- Partial fills that leave you at 94% of target
- Paper-account quirks that a real account would not have (and vice versa)
- Halts, odd-lot rules, and market-on-close cutoffs
- Your own inattention on day 9, which is why you automate the mechanics

## Start the clock early

The 30 days are calendar days. Create the paper account on Sunday of Week 11.
Some brokers take days to approve.
