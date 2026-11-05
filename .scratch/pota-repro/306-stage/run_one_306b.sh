#!/bin/bash
# One extraction task for submit306b.sbatch: piece mode outdir.
# Env: RUN, CORP, PY, PYTHONPATH (exported by the submit script).
set -uo pipefail
piece=$1; mode=$2; outdir=$3
extra=()
[ "$mode" = paper ] && extra=(--paper-chain)
t0=$(date +%s)
"$PY" -m sfs_axes.cli extract-pot-a --surfaces "$CORP/Surfaces" \
      --out "$RUN/out/$outdir" --pot A --pieces "$piece" "${extra[@]}" --verbose \
      > "$RUN/out/log_${mode}_${piece}.txt" 2>&1
rc=$?
t1=$(date +%s)
echo "piece $piece mode $mode rc $rc secs $((t1-t0))" >> "$RUN/out/timing_$mode.txt"
exit $rc
