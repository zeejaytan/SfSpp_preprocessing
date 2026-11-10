#!/bin/bash
#SBATCH --job-name=t325-measure
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/RUNDIR/logs/measure_%j.out
# Ticket 325 step 1: measure scale-free gate statistics over every trusted axis
# (axes323 rank0 x172, authors' released x163, corpus Ground Truth Axes, Juglet_GT x9).
# Read-only over the corpus; writes only inside this run directory.
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/RUNDIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
corpus_state() { ls -l --time-style=full-iso "$CORPUS/Surfaces" "$CORPUS/Axes" "$JUG" "$R/../../Dataset/Juglet_GT" 2>/dev/null || ls -l --time-style=full-iso "$CORPUS/Surfaces" "$CORPUS/Axes" "$JUG"; }
corpus_state > "$R/out/corpus_before.txt"
export OMP_NUM_THREADS=1
cd "$R"
"$PY" -c "import numpy; print('numpy', numpy.__version__)"
"$PY" measure_gate_stats.py "$R/out" | tee "$R/out/measure_summary.txt"
corpus_state > "$R/out/corpus_after.txt"
if cmp -s "$R/out/corpus_before.txt" "$R/out/corpus_after.txt"; then echo CORPUS-UNCHANGED; else echo CORPUS-CHANGED; fi
