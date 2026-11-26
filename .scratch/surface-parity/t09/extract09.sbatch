#!/bin/bash
#SBATCH --job-name=t09-extract
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=logs/slurm-extract-%j.out
#SBATCH --error=logs/slurm-extract-%j.err
#
# Surface Parity Ticket 09, Stage 3: verify the 314 regenerated walls, re-derive the Ticket 08
# baseline, and run the frozen SHIP axis extraction on the regenerated surfaces.
# Submit from the run directory AFTER the regen array has finished:
#   cd <RUN> && sbatch work/t09/extract09.sbatch
set -uo pipefail

RUN=${SLURM_SUBMIT_DIR:?submit from the run directory}
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
LOGS=$RUN/logs
cd "$RUN" || exit 9
echo "[EXTRACT] runid=$(basename "$RUN") job=${SLURM_JOB_ID:-na} host=$(hostname) at $(date -u +%FT%TZ)"
"$PY" work/t09/extract09.py --run "$RUN" --jobs "${SLURM_CPUS_PER_TASK:-16}" \
    > "$LOGS/extract09.log" 2>&1
RC=$?
tail -40 "$LOGS/extract09.log"
echo "[EXTRACT] rc=$RC"
exit "$RC"
