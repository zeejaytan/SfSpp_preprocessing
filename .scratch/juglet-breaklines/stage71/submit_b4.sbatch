#!/bin/bash
#SBATCH --job-name=t71-pottmann
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:40:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "=== b4 job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
$PY $RUN/work/.scratch/juglet-breaklines/stage71/b4_pottmann.py $RUN/out
RC=$?
echo "b4 rc=$RC"
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
