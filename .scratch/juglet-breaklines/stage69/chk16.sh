B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- potd piece dirs ---'; ls $B/out_potd/pieces/ 2>/dev/null
echo '--- potd geom18 files ---'; ls $B/out_potd/geom18/ 2>/dev/null
echo '--- log lines mentioning Pot_D ---'; grep -ac 'Pot_D_Piece' $B/logs/slurm-34274535.out
echo '--- last 5 non-row lines ---'; grep -av '^Pot_D_Piece' $B/logs/slurm-34274535.out | tail -6
