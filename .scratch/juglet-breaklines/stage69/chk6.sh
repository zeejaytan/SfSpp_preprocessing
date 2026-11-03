JG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1546_6761aed_t68-densify2x/outD2X/geom
echo '--- t68 D2X geom ---'; ls $JG 2>&1 | head -12; echo count=$(ls $JG 2>/dev/null | wc -l)
echo '--- juglet axes ---'; ls /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Axes/Juglet/
echo '--- juglet mesh ---'; ls /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/ | head -3
echo '--- juglet gt ---'; ls /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet_GT/ | head -4
echo '--- corpus pota surfaces ---'; ls /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/ | grep -c 'Pot_A'
