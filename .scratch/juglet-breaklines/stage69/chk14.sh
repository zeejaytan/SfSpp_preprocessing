sacct -j 34275210,34274535 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS 2>&1 | head -8
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- C tail ---'; tail -3 $R/logs/slurm-34275210.out 2>/dev/null
echo '--- C panel ---'; cat $R/logs/panel.tsv 2>/dev/null
B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- B potd18/09 ---'; ls $B/out_potd/geom18 2>/dev/null|wc -l; ls $B/out_potd/geom09 2>/dev/null|wc -l
