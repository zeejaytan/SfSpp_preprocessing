#!/bin/bash
#SBATCH --job-name=t302-unit
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 302 gate 1: per-point Cao cost unit proof vs MATLAB.
# Inputs from the released corpus (read only); MATLAB side runs the pristine
# AxisExtraction .m files; port side runs the worktree-fixed sfs_axes uploaded
# under work/. The job appends NO index.tsv row.
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
W=$RUN/work
export RUN302=$RUN
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SFS_AXES_REFINE_NOOP

echo "=== t302-unit job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $RUN/submit.sbatch $W/gen302_unit_inputs.py $W/unit302.m $W/compare302_unit.py $W/sfs_axes/*.py > $RUN/logs/provenance.log

$PY $W/gen302_unit_inputs.py $W/inputs
GEN_RC=$?
echo "gen rc=$GEN_RC"
[ $GEN_RC -ne 0 ] && exit $GEN_RC

module load MATLAB/2024b_Update_3
cd $RUN/work/inputs
matlab -batch "run('$W/unit302.m')" > $RUN/logs/matlab.log 2>&1
MAT_RC=$?
echo "matlab rc=$MAT_RC"
tail -5 $RUN/logs/matlab.log
[ $MAT_RC -ne 0 ] && exit $MAT_RC
grep -c . $W/inputs/CELLS/*/ml_J6.tsv | wc -l > /dev/null

$PY $W/compare302_unit.py $W/inputs $RUN/out/unit302.tsv
CMP_RC=$?
echo "compare rc=$CMP_RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $CMP_RC
