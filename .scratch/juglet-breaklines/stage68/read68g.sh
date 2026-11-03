#!/bin/bash
# read68g.sh -- state of the t68 guard proof-build job
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68
sacct -j 34269496 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
tail -40 $RUN/logs/slurm-34269496.out 2>/dev/null
echo "--- err"; tail -5 $RUN/logs/slurm-34269496.err 2>/dev/null
echo "--- make tail"; tail -3 $RUN/work/logs/make.log 2>/dev/null
