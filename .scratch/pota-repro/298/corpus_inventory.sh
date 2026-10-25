#!/usr/bin/env bash
D=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
cd "$D" || exit 1
echo "### top-level"; ls -d */
for d in Mesh Axes Surfaces Breaklines "Ground Truth"; do
  echo "### $d total: $(ls "$D/$d" | wc -l)"
  for p in A B C D E F G H I J; do
    n=$(ls "$D/$d" | grep -c "^Pot_${p}_" || true)
    pieces=$(ls "$D/$d" | grep "^Pot_${p}_" | sed -n "s/.*_Piece_\([0-9]*\).*/\1/p" | sort -n -u | tr "\n" " ")
    other=$(ls "$D/$d" | grep "^Pot_${p}_" | grep -v "_Piece_[0-9]" | tr "\n" " ")
    printf "%s Pot_%s: %3s | pieces: %s | other: %s\n" "$d" "$p" "$n" "$pieces" "$other"
  done
done
