C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
echo "== GTAxis A01 =="; cat "$C/Ground Truth Axes/Pot_A_Piece_01_Axis.xyz"
echo "== Axes A01 =="; cat "$C/Axes/Pot_A_Piece_01_Axis.xyz"
echo "== GT A1_T =="; cat "$C/Ground Truth/Pot_A_Piece_1_T.txt"
echo "== GT file list (n) =="; ls "$C/Ground Truth" | head -20
echo "== simple_graph =="; ls "$C/Ground Truth" | grep simple | head
echo "== surface A01 head =="; head -3 "$C/Surfaces/Pot_A_Piece_01_Surface_0.xyz"; wc -l "$C/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
echo "== breakline head =="; head -12 "$C/Breaklines/Pot_A_Piece_01_Breakline_0.pcd"
echo "== sizes =="; ls -l "$C/Ground Truth Axes" | head -3
echo "== does Juglet exist here? =="; ls "$C/Ground Truth Axes" | grep -c Juglet; ls "$C/Axes" | grep Juglet | head
echo "== Transformation dir =="; ls "$C/Transformation" | head -5
echo "== Point dir =="; ls "$C/Point" | head -20
