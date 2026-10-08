# Reconciliation dashboard — spec

**What this is:** a spec, not infrastructure. Build the minimum that answers one
question every single day: *do I hold what my strategy says I should hold, and if
not, why?*

The gap between intended and actual positions is the only number in live trading
that you control completely. Everything else (returns, Sharpe, drawdown) is
partly luck. Reconciliation is the operational discipline, and it is graded.

---

## The daily record

One row per day in `live/live-log.md`, and one row per (day, symbol) in
`live/reconciliation.csv`:

| Field | Type | Notes |
|---|---|---|
| `date` | date | trading day |
| `symbol` | str | |
| `intended_weight` | float | from your strategy, computed BEFORE the market open |
| `intended_shares` | int | target shares at the previous close |
| `actual_shares` | int | from the broker, after the session |
| `actual_weight` | float | actual_shares × close / equity |
| `diff_shares` | int | actual − intended |
| `diff_weight` | float | actual_weight − intended_weight |
| `status` | enum | OK / NEW / MISSING / SIZE_DIFF / SIDE_DIFF |
| `explanation` | str | **mandatory unless status is OK** |
| `price` | float | close used |
| `filled_avg_px` | float | average fill price, if orders were submitted |
| `slippage_bps` | float | (fill − decision price) / decision price, in bps |
| `order_ids` | str | broker order IDs, for audit |

## The four statuses and what each one means

| Status | Meaning | Usual cause | Severity |
|---|---|---|---|
| `OK` | within 1% of target | — | none |
| `NEW` | intended a position, do not hold it | order rejected, insufficient buying power, halted symbol, market closed | **high** — you are not running your strategy |
| `MISSING` | hold a position you did not intend | a sell failed, a previous order partially filled, manual intervention | **high** — unintended risk |
| `SIZE_DIFF` | right direction, wrong size | partial fill, rounding to whole shares, turnover cap | medium |
| `SIDE_DIFF` | long where you intended short | **stop trading and investigate** | **critical** |

## The dashboard (minimum viable)

Build it as the notebook `live/reconciliation.ipynb`. Six panels:

1. **Daily status counts** — a stacked bar of OK / NEW / MISSING / SIZE_DIFF per
   day. A healthy run is almost all OK; the exceptions are the story.
2. **Cumulative unexplained gap** — sum of |diff_weight| for rows with a blank
   `explanation`. This must be zero. It is the single number the grader checks.
3. **Slippage distribution** — histogram of `slippage_bps` per fill, with the
   backtest's assumption (5 bps) marked as a vertical line. This is where you
   find out whether your cost model was honest.
4. **Intended vs actual equity** — two lines. The gap between them is the total
   cost of execution error, in dollars.
5. **Fill rate** — orders submitted vs orders filled, per day. Any unfilled order
   gets a row in `live/incidents.md`.
6. **Turnover realized vs backtested** — if live turnover exceeds backtest
   turnover, your live signal differs from your backtested signal. That is a bug
   until proven otherwise.

## Thresholds that should trigger a written incident

| Condition | Action |
|---|---|
| Any `SIDE_DIFF` | stop trading, write an incident, do not resume until root-caused |
| `NEW` or `MISSING` on >10% of symbols | write an incident |
| Realized slippage > 2× the backtest assumption, 3 days running | write an incident, and restate every affected verdict's cost assumption |
| Realized turnover > 1.5× backtest turnover | investigate a signal/live discrepancy |
| Any row with a blank `explanation` and status != OK | fix before the next trading day |

## What NOT to build

- A web dashboard. A notebook is enough and is easier to share.
- Real-time streaming. End-of-day reconciliation is the requirement.
- Automatic remediation. If the harness auto-fixes a gap, you never learn why it
  happened. Log it, fix it manually, and write the cause.

## Why this is 15% of the grade

Anyone can run a backtest. Very few people can run a strategy daily for 30 days
and account, to the share, for every difference between what the model said and
what the account holds. That discipline is the difference between a portfolio of
notebooks and a system you could actually operate.
