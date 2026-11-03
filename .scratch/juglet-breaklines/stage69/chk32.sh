R5=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
ls $R5
echo '--- out_pota ---'; ls $R5/out_pota | head
echo '--- find geom ---'; find $R5 -maxdepth 3 -name 'geom*' -type d | head
