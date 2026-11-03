B=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel
echo '--- piece start timestamps in joblog ---'; grep -a 'PIECE69\|CELL69' $B/logs/slurm-34274535.out | tail -12
echo '--- potd geom18 count ---'; ls $B/out_potd/geom18 2>/dev/null | wc -l; ls $B/out_potd/geom18 2>/dev/null | tail -4
echo '--- elapsed now ---'; date -u
