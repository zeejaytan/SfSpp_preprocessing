RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- geom18 ---'; ls $RUN/out_pota/geom18/ | head -30
echo '--- geom09 ---'; ls $RUN/out_pota/geom09/ | head -30
echo '--- bins ---'; ls -la $RUN/bin-* 2>/dev/null
echo '--- sif used in job5 ---'; grep -n 'SIF=\|pcl_191\|sfs_pristine' $RUN/submit.sbatch | head -10
echo '--- det run dir ---'; ls /data/gpfs/projects/punim2657/SfSpp/runs/20261103-1926_detprobe7_t69d-det/ 2>&1
echo '--- det out ---'; ls -R /data/gpfs/projects/punim2657/SfSpp/runs/20261103-1926_detprobe7_t69d-det/out 2>&1 | head -40
