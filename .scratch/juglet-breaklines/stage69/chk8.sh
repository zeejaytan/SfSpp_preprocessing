sacct -j 34275210,34274535 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS 2>&1
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- C log tail ---'; tail -12 $R/logs/slurm-34275210.out 2>/dev/null
B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- B potd rows ---'; wc -l $B/out_potd/pieces.tsv 2>/dev/null; tail -3 $B/logs/slurm-34274535.out
