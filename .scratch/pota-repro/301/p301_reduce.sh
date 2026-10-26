#!/usr/bin/env bash
# Ticket 301 Phase 2 -- reduce the ten runs.  bash p301_reduce.sh <corpus dir> <runs dir> [runid prefix]
#
# <corpus dir> holds Axes/ and "Ground Truth/" (only the axis files and the reference transforms are
# needed; the reduction never touches geometry). <runs dir> holds the ten run directories.
#
# Prints, for each of the five target pieces, a two-arm block (ctrl and swap) giving EVERY incident
# ground-truth edge's rotation and translation residual against the assembler's own bar, so the ctrl
# column can be set line by line against ticket 299 section 3. Then one ten-arm block giving the
# pot-level sherd and join counts of all ten runs and the pieces whose seated/failed state differs
# between arms -- the ticket's "did any non-target piece change its fate" question.
set -uo pipefail
CORP=${1:?usage: p301_reduce.sh <corpus dir> <runs dir> [runid prefix]}
RUNS=${2:?usage: p301_reduce.sh <corpus dir> <runs dir> [runid prefix]}
PREFIX=${3:?usage: p301_reduce.sh <corpus dir> <runs dir> [runid prefix]}
PY=${PY:-python3}
S=$(cd "$(dirname "$0")" && pwd)
PIECES=${PIECES:-18 25 26 28 29}

echo "corpus   : $CORP"
echo "runs     : $RUNS"
echo "prefix   : $PREFIX"
for P in $PIECES; do
  echo
  echo "################################################################ piece $P : ctrl against swap"
  "$PY" "$S/p301_report.py" --corpus "$CORP" \
      --arm "ctrl=$RUNS/${PREFIX}_p301-d${P}-ctrl" \
      --arm "swap=$RUNS/${PREFIX}_p301-d${P}-swap" --pieces
done

echo
echo "################################################################ all ten runs: pot-level counts"
args=()
for P in $PIECES; do
  for R in ctrl swap; do
    args+=(--arm "d${P}-${R}=$RUNS/${PREFIX}_p301-d${P}-${R}")
  done
done
"$PY" "$S/p301_report.py" --corpus "$CORP" "${args[@]}" --pieces
