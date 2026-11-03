set -e
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
echo "== top =="
ls "$C"
echo "== counts =="
for d in "Ground Truth Axes" "Ground Truth" "Surfaces" "Breaklines" "Axes" "Point"; do
  n=$(ls "$C/$d" 2>/dev/null | wc -l); printf "%-20s %s\n" "$d" "$n";
done
echo "== GT Axes sample =="
ls "$C/Ground Truth Axes" | head -8
echo "== Axes sample =="
ls "$C/Axes" | head -8
echo "== Surfaces sample =="
ls "$C/Surfaces" | head -8
echo "== Breaklines sample =="
ls "$C/Breaklines" | head -8
echo "== GT sample =="
ls "$C/Ground Truth" | head -6
echo "== per-pot counts =="
for p in A B C D E F G H I J; do
  printf "%s GTaxes=%s Axes=%s Surf=%s Bl=%s\n" "$p" "$(ls "$C/Ground Truth Axes" | grep -c "Pot_${p}_")" "$(ls "$C/Axes" | grep -c "Pot_${p}_")" "$(ls "$C/Surfaces" | grep -c "Pot_${p}_")" "$(ls "$C/Breaklines" | grep -c "Pot_${p}_")";
done
