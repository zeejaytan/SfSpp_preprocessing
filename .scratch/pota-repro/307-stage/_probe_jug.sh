#!/bin/bash
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0422_e6adf69_t307d-jug
echo "== ls"; ls $R
echo "== RUN-FAILED"; cat $R/RUN-FAILED.txt 2>/dev/null
echo "== slurm out"; tail -40 $R/logs/slurm-*.out 2>/dev/null
echo "== slurm err"; tail -20 $R/logs/slurm-*.err 2>/dev/null
