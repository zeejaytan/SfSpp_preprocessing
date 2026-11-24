#!/bin/bash
# realcell_posecheck.sh — run the documented pose check over the eight archived
# cells (read-only) and record cell, exit code and verdict.
set -uo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-1431_1233d62_t01-surface-parity
. "$RUN/supplements/t01-turn2/work/posecheck.sh"
LOG="$RUN/supplements/t01-turn2/logs/posecheck_real_cells.tsv"
printf 'cell\trc\tverdict\n' > "$LOG"
for c in OWN_1 OWN_2 AUTHOR_1 AUTHOR_2 OWN_E27_AUTHOR_1 OWN_E27_AUTHOR_2 AUTHOR_E27_OWN_1 AUTHOR_E27_OWN_2; do
  out=$(check_poses "$RUN/out/$c" 31); rc=$?
  printf '%s\t%d\t%s\n' "$c" "$rc" "$out" >> "$LOG"
done
cat "$LOG"
