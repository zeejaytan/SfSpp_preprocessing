sacct -j 34275210,34274535 -P -o JobID,JobName,State,ExitCode,Elapsed 2>&1 | head -6
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
tail -2 $R/logs/slurm-34275210.out 2>/dev/null; cat $R/logs/panel.tsv 2>/dev/null
B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo -n 'potd18 '; ls $B/out_potd/geom18 2>/dev/null|wc -l; echo -n 'potj18 '; ls $B/out_potj/geom18 2>/dev/null|wc -l
