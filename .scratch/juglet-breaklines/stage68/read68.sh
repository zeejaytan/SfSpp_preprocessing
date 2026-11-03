#!/bin/bash
# read-only: t68 Part A job outcome
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method
J=34267653
sacct -j $J -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
cd $RUN
ls logs out out/* score 2>&1 | head -40
tail -40 logs/slurm-$J.out
echo "--- err"; tail -20 logs/slurm-$J.err
echo "--- panel.tsv"; cat logs/panel.tsv
echo "--- axes_subst"; tail -12 logs/axes_subst.log
for A in F20O F20N; do echo "=== $A"; grep -E "T67-|SFS-|Total number|Sherd accuracy|Edge accuracy|segmentation|co-first" work/logs/binary_$A.log | tail -8; cat "out/$A/1. Acc.txt" 2>/dev/null; ls out/$A; done
