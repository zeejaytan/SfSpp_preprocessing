set -uo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1733_45ba206_t69-axis-corpus
sleep 60
sacct -j 34273111 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
echo ---
tail -6 $RUN/logs/partA.stdout 2>/dev/null || tail -20 $RUN/logs/slurm-34273111.out 2>/dev/null
cat $RUN/logs/slurm-34273111.err 2>/dev/null | tail -5
