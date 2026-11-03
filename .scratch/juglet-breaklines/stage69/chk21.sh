sacct -j 34275210,34274535 -P -o JobID,JobName,State,ExitCode,Elapsed 2>&1 | head -6
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- panel ---'; cat $R/logs/panel.tsv 2>/dev/null
echo '--- POTA09 acc ---'; cat $R/out/POTA09/'1. Acc.txt' 2>/dev/null
echo '--- tail ---'; tail -2 $R/logs/slurm-34275210.out
