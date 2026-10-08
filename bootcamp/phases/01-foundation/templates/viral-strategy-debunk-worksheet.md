# Viral Strategy Debunk Worksheet

Use this every time you see a strategy on YouTube / Twitter / a blog with a
pretty equity curve. It takes 20 minutes and it is the fastest way to build the
muscle that protects your own work.

Do this **once in Week 1** on a strategy you find yourself. Bring the filled
worksheet to Sunday's journal entry.

---

## The claim

- **Source** (URL, author, date):
- **The strategy, in one sentence:**
- **The headline number they claim** (CAGR / Sharpe / win rate):
- **Their sample period:**
- **Do they state costs?** ☐ yes ☐ no ☐ "assumed zero"

---

## Step 1 — Reproduce the claim in your own words (5 min)

Write their rules so precisely that someone who has never seen the video could
implement them. If you cannot, **the claim is not well-defined enough to be
either true or false** — that is finding #1.

Rules as I understand them:
```
entry:
exit:
sizing:
universe:
```

Ambiguities I had to guess at:

## Step 2 — The five questions (10 min)

| # | Question | Their answer | Red flag? |
|---|---|---|---|
| 1 | Are costs included, and at what bps? | | |
| 2 | Is there any out-of-sample period, with dates? | | |
| 3 | How many trades are in the sample? (<30 means the result is noise) | | |
| 4 | Does the equity curve include the worst drawdown, and is it shown? | | |
| 5 | Would this have worked on a DIFFERENT symbol, in the same period? | | |

## Step 3 — The three attacks (5 min, on your own data)

1. **Cost attack.** Add 10 bps slippage. What happens to their headline number?
2. **Symbol swap.** Run their rules on SPY. Then on IWM. Report all three.
3. **Period swap.** Run 2015–2019 only, then 2020–2024 only. Report both.

| Attack | Their number | Your number | Verdict |
|---|---|---|---|
| +10 bps slippage | | | |
| Different symbol | | | |
| Different period | | | |

## Step 4 — Verdict

- **Is the claim reproducible?** ☐ yes ☐ partially ☐ no
- **Is it reproducible NET of costs?** ☐ yes ☐ no
- **Is it reproducible out of sample?** ☐ yes ☐ no
- **Most likely explanation for their result** (pick one, and justify):
  - ☐ no costs modeled
  - ☐ in-sample only / curve-fit
  - ☐ look-ahead (entry or exit uses data they did not have)
  - ☐ survivorship (universe chosen with hindsight)
  - ☐ one lucky month / one lucky symbol
  - ☐ leverage presented as alpha
  - ☐ it is real but too small to survive costs at size

## Step 5 — What you steal from it

Even a bogus claim often contains one reusable idea. Name it:

---

**Now apply this worksheet to YOUR OWN S01.** Same five questions, same three
attacks. If any answer is worse for your strategy than for the viral one, you
have learned something worth more than the strategy.
