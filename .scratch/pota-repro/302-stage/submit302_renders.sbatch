#!/bin/bash
#SBATCH --job-name=t302-renders
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CORPUSRUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1612_01bff01_t302-corpus-axes
E2ERUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1620_01bff01_t302-e2e
echo "=== t302-renders job $SLURM_JOB_ID $(date -u +%FT%TZ)"
$PY $RUN/work/render302.py $RUN/out $CORPUSRUN/out/axes302 $E2ERUN/work/axes302_jug
RC=$?
echo "renders rc=$RC  files:"; ls -la $RUN/out/renders
echo "=== finished $(date -u +%FT%TZ)"
exit $RC
