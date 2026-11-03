R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- POTA18 pieces placed ---'; ls $R/out/POTA18/*OBJ*.obj 2>/dev/null | wc -l
echo '--- POTA09 state ---'; ls $R/out/POTA09 2>/dev/null | wc -l; cat $R/out/POTA09/'1. Acc.txt' 2>/dev/null
echo '--- panel ---'; cat $R/logs/panel.tsv
sacct -j 34275210 -P -o State,Elapsed 2>&1|head -3
