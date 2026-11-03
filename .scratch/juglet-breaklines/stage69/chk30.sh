sacct -j 34274535,34275210 -P -o JobID,JobName,State,ExitCode,Elapsed | grep -v '\.' 
echo '--- job5 cells ---'
R5=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
for c in out_pota out_potc out_potd out_potj; do echo -n "$c "; wc -l < $R5/$c/pieces.tsv 2>/dev/null || echo 0; done
tail -5 $R5/logs/slurm-34274535.out
