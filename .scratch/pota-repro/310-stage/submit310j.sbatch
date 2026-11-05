#!/bin/bash
#SBATCH --job-name=t310b2-big
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 B2 probe: the union path with and without converge-before-rank, on two
# large pieces (Pot D 01 = 35k points per wall, D 03 = 31k).  Parameters are baked:
# this cluster does not carry the submitter's environment into the job.
set -uo pipefail
ARMS="__ARMS__"
SEEDS="__SEEDS__"
CAP="__CAP__"
JOBS="__JOBS__"
POT="__POT__"
PIECES="__PIECES__"
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out
echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ) arms=$ARMS seeds=$SEEDS cap=$CAP pot=$POT pieces=$PIECES"
{ echo "jobid $JOBID"; date -u +%FT%TZ; echo "--- instruments"; md5sum work/*.py work/sfs_axes/*.py; echo "--- commit"; cat work/code_commit.txt 2>/dev/null; } > logs/provenance.log 2>&1
$PY work/stage310b2.py --out "$RUN/out" --pot "$POT" --pieces "$PIECES" --seeds "$SEEDS" --arms "$ARMS" --cap "$CAP" --jobs "$JOBS" --good "" > logs/stageb2.log 2>&1
BRC=$?
echo "[JOB] stage310b2 rc=$BRC"
grep -E '^\[B2\]|^\[stage310b2\]' logs/stageb2.log || true
echo "[JOB] done $(date -u +%FT%TZ)"
exit $BRC