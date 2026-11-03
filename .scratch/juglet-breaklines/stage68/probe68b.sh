#!/bin/bash
# read-only: t67 run dir layout for the F20 rerun
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly
ls "$R" "$R"/work "$R"/trees 2>&1 | head -60
cat "$R"/run.json
head -60 "$R"/submit.sbatch
ls "$R"/work/* 2>&1 | head -40
