RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
L=$RUN/out_potc/pieces/Pot_C_Piece_03/edge09.log
echo '--- surface lines ---'; grep -an 'Surface 0 point cloud file\|Surface 1 point cloud file\|Surface_1' $L | head -6
echo '--- how many segment loops started (per surface) ---'; grep -ac 'DEBUG LOOP' $L
echo '--- savePCDFile / Breakline writes ---'; grep -an 'Breakline_\|Writing\|Saved' $L | tail -6
echo '--- edge18 same ---'; grep -ac 'DEBUG LOOP' $RUN/out_potc/pieces/Pot_C_Piece_03/edge18.log
echo '--- geom09 dir ---'; ls -la $RUN/out_potc/geom09/ | grep Piece_03
