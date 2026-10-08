# Walk-forward, purge, embargo

## The three-layer defense against self-deception

```
in-sample (IS)   -> choose the idea
validation (VAL) -> choose the parameters
test / OOS       -> report the number, once, and live with it
```

You will be tempted to use two. Use three. The moment you look at the test set
to make a decision, it becomes part of validation and you have no honest number
left.

## Anchored vs rolling windows

```python
# ANCHORED: train always starts at t0 and grows. Mimics how you'd really trade.
train = idx[0:end];  test = idx[end + embargo : end + embargo + test_len]

# ROLLING: fixed-length train window slides. Better when the world changes.
train = idx[end - train_len : end];  test = idx[end + embargo : end + embargo + test_len]
```

Default for this course: **anchored**. You accumulate data in reality; your
backtest should too. Switch to rolling in Week 11 when you test regime
sensitivity.

## The embargo rule

```
embargo >= longest forward-looking window in your features
```

| Feature | Required embargo |
|---|---|
| Signal uses only trailing data (MA, RSI) | 1 bar (execution lag) |
| Label is a 5-day forward return | 5 bars |
| Label is a 20-day forward return | 20 bars |
| Signal uses a 60-day realized vol estimate | 60 bars (it looks backward, but if it is used to *scale* a forward-labelled target, 20) |

When in doubt, use the largest. An over-long embargo costs you a few rows; an
under-long one costs you the honesty of the entire result.

## Reference implementation

```python
def walk_forward_splits(index, n_splits=5, train_frac=0.6, embargo=5):
    """Anchored walk-forward. Returns [(train_idx, test_idx), ...]."""
    n = len(index)
    test_size = max(int((n * (1 - train_frac)) / n_splits), 1)
    splits = []
    for k in range(n_splits):
        test_end = n - (n_splits - 1 - k) * test_size
        test_start = test_end - test_size
        train_end = test_start - embargo
        if train_end <= 10 or test_start < 0:
            continue                      # skip the fold, do not shrink it quietly
        splits.append((index[:train_end], index[test_start:test_end]))
    return splits
```

## The aggregation question

Once you have N fold Sharpes, how do you report one number?

- **Mean of fold Sharpes** — simple, and biases *downward* on short folds. Use
  this as the headline.
- **Sharpe of the stitched OOS return stream** — concatenate the folds' returns
  and compute one Sharpe. Usually higher and arguably more correct, but it hides
  fold dispersion.
- **Report both, plus the dispersion.** Minimum, maximum, and the fraction of
  profitable folds.

```python
oos = pd.DataFrame(fold_results)
report = {
    "mean_fold_sharpe": oos.sharpe.mean(),
    "stitched_sharpe": sharpe(pd.concat(fold_returns)),
    "min_fold": oos.sharpe.min(),
    "max_fold": oos.sharpe.max(),
    "pct_positive_folds": (oos.sharpe > 0).mean(),
}
```

**Kill criterion tied to this:** if `min_fold < 0` and `max_fold > 1.0` on the
same 5 folds, you do not have a strategy, you have a coin flip with a good
average. Say so.

## Common mistakes

1. **Optimizing on the test set.** Even once. Then it is validation.
2. **Embargo shorter than the label window.** See the table above.
3. **Reporting only the best fold.** Report all of them, always.
4. **Folds of different lengths because of the embargo** — normalize, or the mean
   is weighted by data availability rather than by time.
5. **Purge/embargo applied to the test set instead of the train set.** You purge
   TRAINING rows near the boundary; you never delete test rows.
6. **Re-using walk-forward folds across strategies to "save time."** That is
   fine — but then your N for multiple-comparisons purposes includes every
   strategy-fold combination you looked at.
