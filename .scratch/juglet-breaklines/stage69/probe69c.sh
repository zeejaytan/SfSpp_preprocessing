C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
echo "== surface sizes =="
du -sh "$C/Surfaces" "$C/Breaklines" "$C/Axes" "$C/Ground Truth Axes" "$C/Point"
ls -l "$C/Surfaces/Pot_A_Piece_01_Surface_0.xyz" "$C/Surfaces/Pot_A_Piece_01_Surface_1.xyz"
echo "== n lines surf A01 s1 =="; wc -l "$C/Surfaces/Pot_A_Piece_01_Surface_1.xyz"
echo "== GT axes line counts (any multi-line?) =="
for f in "$C/Ground Truth Axes"/*.xyz; do n=$(wc -l < "$f"); if [ "$n" != "1" ]; then echo "$f $n"; fi; done
echo "== released axes line counts =="
for f in "$C/Axes"/*.xyz; do n=$(wc -l < "$f"); if [ "$n" != "1" ]; then echo "$f $n"; fi; done
echo "== pieces with GT axis but no released axis (or vice versa) =="
ls "$C/Ground Truth Axes" | sed "s/_Axis.xyz//" | sort > /tmp/gt.txt
ls "$C/Axes" | sed "s/_Axis.xyz//" | sort > /tmp/rx.txt
echo "GT not in released:"; comm -23 /tmp/gt.txt /tmp/rx.txt
echo "released not in GT:"; comm -13 /tmp/gt.txt /tmp/rx.txt
echo "== Point dir listing =="; ls "$C/Point/Pot_A" | head -4; ls "$C/Point/Pot_J" | head -3
