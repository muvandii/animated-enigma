#!/usr/bin/env bash
# bootstrap.sh — create your working repo. Run once, on Day 1.
#
#   ./bootstrap.sh ~/quant-bootcamp
#
# Creates the directory skeleton, copies the three shared Python modules
# (fetcher.py, metrics.py, backtester.py) and their tests to the repo ROOT so
# that plain `import fetcher` works from anywhere, and writes a starter README.
set -euo pipefail

TARGET="${1:-$HOME/quant-bootcamp}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED="$SRC/shared"

if [ -d "$TARGET" ]; then
  echo "!! $TARGET already exists. Refusing to clobber your work." >&2
  echo "   Pick a new path, or delete it manually if you are sure." >&2
  exit 1
fi

echo "==> creating $TARGET"
mkdir -p "$TARGET"/{data/{raw,clean},strategies,engine,notes/{daily,concepts,strategies,failures},papers/{dossiers,replications},live,reports,graveyard,tests,journal}

# --- shared python modules, flattened to repo root -------------------------
# Library modules go to the ROOT (so `import backtester` works from anywhere).
# Test modules go ONLY to tests/ -- copying them to both places makes pytest
# collect them twice and fail with an "import file mismatch" error.
for mod in data-fetcher metrics-module backtester; do
  for f in "$SHARED"/$mod/*.py; do
    case "$(basename "$f")" in
      test_*) ;;                 # skip: handled below
      *) cp "$f" "$TARGET/$(basename "$f")" ;;
    esac
  done
  for f in "$SHARED"/$mod/test_*.py; do
    [ -e "$f" ] && cp "$f" "$TARGET/tests/$(basename "$f")"
  done
done

cp "$SHARED/repo-scaffold/requirements.txt" "$TARGET/requirements.txt"
cp "$SHARED/repo-scaffold/gitignore"         "$TARGET/.gitignore"
cp "$SHARED/repo-scaffold/STUDENT-README.md" "$TARGET/README.md"
cp "$SHARED/journal-template.md"             "$TARGET/journal/lessons.md"
cp "$SHARED/repo-scaffold/graveyard.md"      "$TARGET/graveyard/graveyard.md"

# --- seed the weekly note dirs --------------------------------------------
for w in 01 02 03 04 05 06 07 08 09 10 11 12 13; do
  mkdir -p "$TARGET/notes/daily/week-$w"
done

# --- seed the strategy dirs ------------------------------------------------
for s in S01_ma_crossover S02_ma_crossover_filtered S03_rsi2_reversal \
         S04_bollinger_reversion S05_donchian_breakout S06_ts_momentum \
         S07_xs_momentum S08_distance_pairs S09_vol_target_overlay \
         S10_turn_of_month S11_gap_fade S12_dual_momentum S13_mr_basket \
         S14_tsmom_paper S15_vol_managed_momentum S16_ggR_pairs; do
  mkdir -p "$TARGET/strategies/$s"
done

cat > "$TARGET/conftest.py" <<'PY'
"""Makes `import fetcher` / `import backtester` work from the repo root and from
inside tests/. pytest auto-loads this file; you do not need to import it."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PY

echo "==> done. Next:"
echo ""
echo "    cd $TARGET"
echo "    python3 -m venv .venv && source .venv/bin/activate"
echo "    pip install -r requirements.txt"
echo "    python -m pytest -q            # expect: all green"
echo "    python fetcher.py AAPL --out data/clean/aapl.parquet"
echo ""
echo "    Then open: $SRC/phases/01-foundation/week-01.md"
