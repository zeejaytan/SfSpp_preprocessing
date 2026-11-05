#!/bin/bash
#SBATCH --job-name=t307-render
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
# Ticket 307 C5: Pot A render, the paper's candidate set vs the authors' 1.1 prune.
# Both panels share one view box (render305.py), so they are comparable.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
A=$RUNS/20261105-0424_e6adf69_t307-b1-s1-np8/out/MMR1
B=$RUNS/20261105-0424_e6adf69_t307-base-s1-np8/out/MMR1
OUT=$RUN/out/pota307_b1-s1_vs_base-s1.png
echo "[JOB] A=$A"; ls "$A" | wc -l
echo "[JOB] B=$B"; ls "$B" | wc -l
$PY "$RUN/work/render305.py" "$OUT" \
  "Pot A, our axes, seed 1 -- left: paper candidate set (no cost prune) 8/8 sherds 15/15 joins; right: authors' cost<cost[0]*1.1 prune 7/8 sherds 12/15 joins" \
  "paper set 8/8 15/15=$A" \
  "authors' prune 7/8 12/15=$B"
RC=$?
echo "[JOB] render rc=$RC"
ls -l "$OUT" 2>/dev/null
