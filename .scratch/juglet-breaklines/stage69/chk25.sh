R=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0754_b23aedf_t69-pota-seat
echo '--- corpus axes in tree? ---'; md5sum $R/trees/pota09/Axes/Pot_A_Piece_01_Axis.xyz
echo '--- what t67 stage67_inputs used for pota ---'; grep -n 'Axes' /data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68/instruments/stage67_inputs.py | head
