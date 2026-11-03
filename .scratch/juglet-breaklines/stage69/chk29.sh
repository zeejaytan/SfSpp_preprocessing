R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
cat $R/logs/panel.tsv
sacct -j 34275210 -P -o JobID,State,ExitCode,Elapsed | head -3
echo '--- jug ---'; cat $R/out/JUG09F50/'1. Acc.txt' 2>/dev/null
echo '--- tail ---'; tail -3 $R/logs/slurm-34275210.out
