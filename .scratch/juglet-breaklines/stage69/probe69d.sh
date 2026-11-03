C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
echo "== python on login node =="; python3 -c "import numpy,sys;print(sys.version);print(numpy.__version__)" 2>&1 | head -3
echo "== tora python =="; /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 -c "import numpy,scipy,sys;print(sys.version.split()[0], numpy.__version__, scipy.__version__)" 2>&1 | head -3
echo "== is Juglet axis the same as Pot_J_Piece_0N axis? =="
md5sum "$C/Axes/Juglet_Piece_2_Axis.xyz" "$C/Axes/Pot_J_Piece_02_Axis.xyz" "$C/Axes/Pot_J_Piece_2_Axis.xyz" 2>&1
echo "== Pot_J axes =="; ls "$C/Axes" | grep Pot_J
echo "== Pot_J GT axes =="; ls "$C/Ground Truth Axes" | grep Pot_J
echo "== Juglet_Piece_2_Axis content =="; cat "$C/Axes/Juglet_Piece_2_Axis.xyz" 2>&1
echo "== Pot_J_Piece_02 content =="; cat "$C/Axes/Pot_J_Piece_02_Axis.xyz" 2>&1
echo "== Pot_J_Piece_02 GT =="; cat "$C/Ground Truth Axes/Pot_J_Piece_02_Axis.xyz" 2>&1
echo "== Pot J surface list =="; ls "$C/Surfaces" | grep Pot_J | head -8
echo "== surface 6 or 7 cols? =="; head -2 "$C/Surfaces/Pot_J_Piece_02_Surface_0.xyz" | cat -A | head -2
