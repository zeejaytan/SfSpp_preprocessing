RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
grep -n 'SIF=\|SIF_\|pcl_191\|apptainer\|APT exec' $RUN/submit.sbatch | head -20
echo '--- run_cell69 edge call ---'; grep -n 'EdgeLineExtractionHeadless' /data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel/run_cell69.sh | head
