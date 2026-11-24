#!/bin/bash
#SBATCH --job-name=t01-strict
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=supplements/t01-turn2/logs/slurm-strict-%j.out
#SBATCH --error=supplements/t01-turn2/logs/slurm-strict-%j.err
# Ticket 01 turn-2 strict acceptance replay: recompute the pinned scorer's joins
# from the archived pose exports and record which cells are usable. Read-only over
# the frozen run; writes only into $RUN/supplements/t01-turn2.
set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-1431_1233d62_t01-surface-parity
T03E=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-potE
FIXED="$T03E/trees/E_K3R1/E/MM"
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
OUT="$RUN/supplements/t01-turn2"
mkdir -p "$OUT"
"$PY" "$RUN/supplements/t01-turn2/work/strict01.py" \
  --run "$RUN" --gt "$FIXED/Ground Truth" \
  --pieces "$T03E/trees/E_K3R1/arm_pieces_E.tsv" --out "$OUT"
