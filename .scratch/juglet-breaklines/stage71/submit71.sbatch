#!/bin/bash
#SBATCH --job-name=t71-objective
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 71 stages A, B2, B3. Submitted from the run directory.
# The corpus is read only. Appends no index row (submit71.sh does).
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
W=$RUN/work
S=$W/.scratch/juglet-breaklines/stage71
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export SFS_AXES_REFINE_NOOP=1
echo "=== t71 job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
md5sum $S/costs71.py $S/b1_synthetic.py $S/corpus71.py $W/sfs_axes/*.py > $RUN/logs/provenance.log
$PY $S/b1_synthetic.py $RUN/out/b1_synthetic.tsv
echo "b1 rc=$?"
$PY $S/corpus71.py $C $RUN/out --jobs "${SLURM_CPUS_PER_TASK}" --refine noop --seeds 20
RC=$?
echo "corpus rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
