#!/bin/bash
#SBATCH --job-name=t302-corpus
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 302 gate 3: corrected corpus axes -> NEW paths under out/axes302/.
# The corpus itself is never written; md5s unchanged (checked after the run).
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SFS_AXES_REFINE_NOOP
echo "=== t302-corpus job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
{
  echo "--- corpus Surfaces+Axes md5 BEFORE"
  md5sum $C/Surfaces/*.xyz $C/Axes/*.xyz | md5sum
} > $RUN/logs/corpus_md5_before.log 2>&1
md5sum $RUN/submit.sbatch $RUN/work/corpus302.py $RUN/work/sfs_axes/*.py > $RUN/logs/provenance.log
$PY $RUN/work/corpus302.py $RUN/out 8
RC=$?
echo "corpus rc=$RC"
{
  echo "--- corpus Surfaces+Axes md5 AFTER"
  md5sum $C/Surfaces/*.xyz $C/Axes/*.xyz | md5sum
  echo "--- axes302 files:"
  ls $RUN/out/axes302 | wc -l
} > $RUN/logs/corpus_md5_after.log 2>&1
cat $RUN/logs/corpus_md5_before.log $RUN/logs/corpus_md5_after.log
diff <(grep -o '[0-9a-f]\{32\}' $RUN/logs/corpus_md5_before.log) <(grep -o '[0-9a-f]\{32\}' $RUN/logs/corpus_md5_after.log) > $RUN/logs/corpus_md5_diff.log || echo "!!!! CORPUS CHANGED"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
