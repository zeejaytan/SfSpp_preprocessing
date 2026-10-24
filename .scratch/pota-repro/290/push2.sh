#!/bin/bash
set -eu
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2328_d36a33e_p290-corpus
cp /tmp/p290/submit2.sbatch /tmp/p290/repeat290.py "$RUN/"
cd "$RUN"
ls -l submit2.sbatch repeat290.py
export RUN_DIR="$RUN"
export CANONICAL=/data/gpfs/projects/punim2657/sfs_preprocessing
sbatch submit2.sbatch
