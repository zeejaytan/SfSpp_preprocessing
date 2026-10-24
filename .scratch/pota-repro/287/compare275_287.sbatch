#!/bin/bash
#SBATCH --job-name=p287cmp
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
# Ticket 287 item 2: compare our after-run exports on the two bar lanes against the parked 275
# selector run's exports, to show the same closed loop and how far the chosen start dot sits.
set -u
RUN=${RUN_DIR:?}
P275=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "compare job $SLURM_JOB_ID on $(hostname)"
OURS="$RUN/out" P275="$P275/out" python3 "$RUN/compare275_287.py" 2>&1 | tee "$RUN/out/compare275_287.txt"
say "=== also: chain / lump lines for every lane ==="
for d in "$RUN"/out/*_before "$RUN"/out/*_after; do
  echo "-- $(basename "$d")"
  grep -hE 'FULL-263\] (no-discard|chain=)|SEED-287|STOP-267\] CHAIN-END' "$d/edge.log" 2>/dev/null | head -8
done | tee "$RUN/out/chain_lines.txt"
say "done"
