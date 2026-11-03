#!/bin/bash
#SBATCH --job-name=t302-pota
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 302 gate 2: Pot A regression vs MATLAB-run axes (t48 axis_output).
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SFS_AXES_REFINE_NOOP
echo "=== t302-pota job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $RUN/submit.sbatch $RUN/work/pota302.py $RUN/work/sfs_axes/*.py > $RUN/logs/provenance.log
$PY $RUN/work/pota302.py $RUN/out/pota302.tsv
RC=$?
echo "pota rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
