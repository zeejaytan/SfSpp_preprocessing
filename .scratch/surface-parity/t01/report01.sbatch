#!/bin/bash
#SBATCH --job-name=t01-report
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:40:00
#SBATCH --output=logs/slurm-report-%j.out
#SBATCH --error=logs/slurm-report-%j.err
# Ticket 01 reduction: evidence tables plus the locked join renders.
set -euo pipefail
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RUN="${SLURM_SUBMIT_DIR:?}"
MAIN=/data/gpfs/projects/punim2657/sfs_main
T19=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions
T03E=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-potE
FIXED="$T03E/trees/E_K3R1/E/MM"
exec "$PY" "$RUN/work/t01/report01.py" \
  --run "$RUN" --fixed "$FIXED" --orig "$MAIN/original_samples/SfS_pp" \
  --gt "$FIXED/Ground Truth" --t19 "$T19" \
  --evidence "$RUN/evidence" --renders "$RUN/evidence/renders"
