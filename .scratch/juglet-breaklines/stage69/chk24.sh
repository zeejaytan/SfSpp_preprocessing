T=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly
echo '--- t67 submit: pota staging ---'; grep -n 'stage67_inputs\|--axis\|--pota\|AXIS' $T/submit.sbatch | head -20
echo '--- pota tree axes md5 ---'; md5sum $T/trees/pota/Axes/*.xyz 2>/dev/null | head -4
echo '--- corpus axes md5 ---'; md5sum /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_0{1,2}_Axis.xyz
echo '--- Dataset axes md5 ---'; md5sum /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Axes/Pot_A/Pot_A_Piece_0{1,2}_Axis.xyz 2>/dev/null
echo '--- C tree axes md5 ---'; md5sum /data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat/trees/pota18/Axes/*.xyz 2>/dev/null | head -3
