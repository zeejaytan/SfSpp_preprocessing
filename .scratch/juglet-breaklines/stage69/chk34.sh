R5=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- proof (Part D restated gate) ---'
cat $R5/proof/proof.tsv 2>/dev/null || ls $R5/proof
echo '--- potd rows ---'; cat $R5/out_potd/pieces69.tsv 2>/dev/null | tail -4
echo '--- tail log ---'; tail -2 $R5/logs/slurm-34274535.out
sacct -j 34274535,34275406 -P -o JobID,JobName,State,ExitCode,Elapsed | grep -v '\.'
