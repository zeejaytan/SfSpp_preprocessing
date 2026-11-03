R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- POTA18 vs POTA09 identical gate? ---'
diff <(head -3 $R/out/POTA18/'1. Acc.txt') <(head -3 $R/out/POTA09/'1. Acc.txt') && echo IDENTICAL_GATE
echo '--- placed pieces per arm ---'
ls $R/out/POTA18/*OBJ*.obj | wc -l; ls $R/out/POTA09/*OBJ*.obj | wc -l
echo '--- edges per arm ---'; ls $R/out/POTA18/*Edgeline*.xyz|wc -l; ls $R/out/POTA09/*Edgeline*.xyz|wc -l
echo '--- corpus vs dataset axes used ---'; md5sum $R/trees/pota18/Axes/Pot_A_Piece_06_Axis.xyz $R/trees/pota18/Axes/Pot_A_Piece_08_Axis.xyz
md5sum /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_0{6,8}_Axis.xyz
