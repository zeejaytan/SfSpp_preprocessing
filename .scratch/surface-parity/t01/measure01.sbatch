#!/bin/bash
#SBATCH --job-name=t01-surface
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:40:00
#SBATCH --output=logs/slurm-surface-%j.out
#SBATCH --error=logs/slurm-surface-%j.err
# Ticket 01 surface measurement and locked surface renders, one compute-node job.
set -uo pipefail
P=/data/gpfs/projects/punim2657
SHIP=$P/SfSpp/runs/20261121-1319_2e951d9_t03-ship
T03E=$P/SfSpp/runs/20261121-1319_2e951d9_t03-potE
FIXED="$T03E/trees/E_K3R1/E/MM"
ORIG=$P/sfs_main/original_samples/SfS_pp
PY=$P/TORA/envs/tora/bin/python3
RUN="${SLURM_SUBMIT_DIR:?}"
export PYTHONPATH="$SHIP/work/impl_t03:$SHIP/work"
export OMP_NUM_THREADS=4
mkdir -p "$RUN/evidence" "$RUN/evidence/renders"
"$PY" "$RUN/work/t01/surface01.py" --run "$RUN" --fixed "$FIXED" --orig "$ORIG" \
  --out "$RUN/evidence" --renders "$RUN/evidence/renders"
