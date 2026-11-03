sacct -j 34275210,34274535 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS 2>&1
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- C log ---'; tail -15 $R/logs/slurm-34275210.out 2>/dev/null
echo '--- B rows ---'; wc -l /data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel/out_potd/pieces.tsv 2>/dev/null
