#!/bin/bash
#SBATCH --job-name=t325-gatediag
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:40:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1642_22151d0_t325-gatediag/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1642_22151d0_t325-gatediag/logs/slurm-%j.err
#
# Ticket 325 bar 3 diagnostic: call the SHIPPED scale-free base test and cylindrical
# gate on the nine Juglet pieces (GT / axes323 / axes325) and on the corpus's released
# axes, printing every intermediate so the verdict is auditable.
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1642_22151d0_t325-gatediag
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd "$R"
echo "[JOB] job=${SLURM_JOB_ID:-na} start=$(date -u +%FT%TZ)"
"$PY" diagnose_base.py "$R/impl" | tee "$R/out/diagnose_base.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"
