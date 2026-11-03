#!/bin/bash
#SBATCH --job-name=t302-pota-ml
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 302 gate 2 (correct protocol): MATLAB run_potsac on the CORPUS Pot A
# clouds vs the corrected Python port, same adaptive step. The 2025
# axis_output files (500-pt clouds, different frame) are NOT the reference.
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
AXDIR=/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SFS_AXES_REFINE_NOOP
mkdir -p $RUN/out_ml $RUN/out
echo "=== t302-pota-ml job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $AXDIR/run_potsac.m $AXDIR/compute_axis_of_symmetry.m $AXDIR/compute_biaxial_cao_error.m $RUN/work/*.py > $RUN/logs/provenance.log
module purge
module load MATLAB/2024b_Update_3
export OUTDIR=$RUN/out_ml AXDIR=$AXDIR
matlab -batch "run('$RUN/work/pota_ml302.m')" > $RUN/logs/matlab.log 2>&1
MRC=$?
echo "matlab rc=$MRC"
tail -12 $RUN/logs/matlab.log
[ $MRC -ne 0 ] && exit $MRC
$PY $RUN/work/pota302.py $RUN/out_ml $RUN/out/pota302.tsv
RC=$?
echo "pota rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
