# 2025-01-13 — Week 1 · Mon

BUILT:
- ran `python fetcher.py AAPL --out data/clean/aapl.parquet` (fell back to
  synthetic — no network on this machine; noted it, will re-run on real data)
- notes/strategies/S01.md (thesis + pre-registration)

BROKE:
- Nothing yet, which is suspicious. Also: fetcher.py returned a synthetic twin
  and I nearly didn't notice. The stderr line was easy to miss.

LEARNED:
Writing kill criteria BEFORE the backtest is uncomfortable in a way I didn't
expect. I kept wanting to soften "net Sharpe < 0.5" to "net Sharpe < 0.3" because
0.5 felt strict. That instinct is exactly the bias the pre-registration is meant
to stop, so I left it at 0.5.

QUESTION I STILL HAVE:
My expected turnover estimate (7/yr) is a guess from monthly crossing frequency.
Is there a way to get it from the daily signal without running the backtest? (I
think: count sign changes of MA10-MA50 on daily data. Will try Tuesday.)

TOMORROW'S FIRST MOVE:
python -c "import pandas as pd, numpy as np; px=pd.read_parquet('data/clean/aapl.parquet')['adj_close']; d=px.rolling(10).mean()-px.rolling(50).mean(); print(int(np.sign(d).diff().abs().gt(0).sum()))"
