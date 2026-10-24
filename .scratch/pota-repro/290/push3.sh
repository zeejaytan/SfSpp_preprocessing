#!/bin/bash
set -eu
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2328_d36a33e_p290-corpus
cp /tmp/p290/submit3.sbatch /tmp/p290/cmp290.py "$RUN/"
cd "$RUN"
export RUN_DIR="$RUN"
export CANONICAL=/data/gpfs/projects/punim2657/sfs_preprocessing
sbatch submit3.sbatch
