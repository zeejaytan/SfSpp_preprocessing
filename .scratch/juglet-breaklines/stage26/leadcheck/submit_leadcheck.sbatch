#!/bin/bash
#SBATCH --job-name=p26-leadcheck
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=00:15:00
# Lead's independent re-measurement of four ticket-26 cells (own scorer, brute force).
# Cells come from the ticket-26 grid run; this job writes nothing but its own output.
set -uo pipefail
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CELLS=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1313_583c952_win26-grid116/out/cells
OUT=__RUNDIR__/out
mkdir -p "$OUT"
cd __RUNDIR__ || exit 1
date -u +"start %Y-%m-%dT%H:%M:%SZ"
"$PY" __RUNDIR__/lead_paircheck26.py "$CELLS" \
  W0T:Juglet:Juglet_Piece_1 \
  W2L:Juglet:Juglet_Piece_1 \
  W0L:Juglet:Juglet_Piece_5 \
  W0A:Pot_A:Pot_A_Piece_07 \
  W3A:Pot_A:Pot_A_Piece_07 \
  | tee "$OUT/lead_paircheck26.tsv"
echo "exit=$?"
date -u +"end %Y-%m-%dT%H:%M:%SZ"
