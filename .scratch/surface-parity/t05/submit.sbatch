#!/bin/bash
#SBATCH --job-name=t05-sampling
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
# Ticket 05: ten sampling / coverage arms on Pot E 27 and 28, frozen shipped selector.
# Submit from the run directory: sbatch --parsable submit.sbatch
set -uo pipefail
RUN="${SLURM_SUBMIT_DIR:?submit from the run directory}"
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
export SFS_IMPL="$SHIP/work/impl_t03"
export PYTHONPATH="$SFS_IMPL:$SHIP/work:$RUN/work/t05"
export MPLBACKEND=Agg
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export T05_GIT=57a4da7
export T05_TAG=t05-sampling-coverage
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd "$RUN" || exit 2
mkdir -p logs evidence out/axes05 renders
printf 'job_id\tstate\texit_code\n' > evidence/jobs.tsv
printf '%s\tSUBMITTED\t\n' "$SLURM_JOB_ID" >> evidence/jobs.tsv
rc=0
$PY work/t05/extract05.py --run "$RUN" --fixtures || rc=$?
if [ "$rc" -eq 0 ]; then $PY work/t05/extract05.py --run "$RUN" || rc=$?; fi
if [ "$rc" -eq 0 ]; then $PY work/t05/check05.py --run "$RUN" | tee evidence/check.txt || rc=$?; fi
exit "$rc"
