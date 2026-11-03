R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- JUG09F50 ---'; cat $R/out/JUG09F50/'1. Acc.txt' 2>/dev/null || echo none
ls $R/out/JUG09F50/ 2>/dev/null | head
echo '--- job5 pota geom ---'
G=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel/out_pota/geom
ls $G | head -6; ls $G | wc -l
