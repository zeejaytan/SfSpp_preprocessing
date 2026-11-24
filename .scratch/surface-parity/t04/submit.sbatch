#!/bin/bash
#SBATCH --job-name=t04-normals
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
# Ticket 04: wall-normal transfer at 1.000 mm on Pot E 27/28, frozen shipped selector.
# Submit from the run directory: sbatch --parsable submit.sbatch
set -uo pipefail
RUN="${SLURM_SUBMIT_DIR:?submit from the run directory}"
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
export SFS_IMPL="$SHIP/work/impl_t03"
export PYTHONPATH="$SFS_IMPL:$SHIP/work:$RUN/work/t04"
export MPLBACKEND=Agg
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd "$RUN" || exit 2
mkdir -p logs evidence out/axes04 renders
printf 'job_id\tstate\texit_code\n' > evidence/jobs.tsv
printf '%s\tSUBMITTED\t\n' "$SLURM_JOB_ID" >> evidence/jobs.tsv
rc=0
$PY work/t04/extract04.py --fixtures --run "$RUN" || rc=$?
if [ "$rc" -eq 0 ]; then $PY work/t04/extract04.py --run "$RUN" || rc=$?; fi
if [ "$rc" -eq 0 ]; then $PY work/t04/check04.py --run "$RUN" | tee evidence/check.txt || rc=$?; fi
exit "$rc"
