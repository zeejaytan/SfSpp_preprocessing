#!/bin/bash
# read-only progress/outcome of t68 job 2
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1535_ffcb350_t68-densify
J=34268041
sacct -j $J -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
tail -45 $RUN/logs/slurm-$J.out
echo "--- err"; tail -8 $RUN/logs/slurm-$J.err
ls $RUN/out
