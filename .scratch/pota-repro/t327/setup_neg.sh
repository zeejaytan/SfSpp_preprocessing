#!/bin/bash
# Ticket 327 bar 4 follow-up: sign variants of the SAME swapped trees.
# Only Breakline_0 normals are negated (PCD ASCII, FIELDS x y z normal_x normal_y normal_z curvature).
set -uo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-2028_1b131dc_t327-swap
W=$R/work/trees
[ -d "$W/juglet_SWAP" ] || { echo "no SWAP tree"; exit 1; }
for t in neg neg7 negall; do rm -rf "$W/juglet_SWAP$t"; cp -a "$W/juglet_SWAP" "$W/juglet_SWAP$t"; done
neg() {
  f=$1
  awk 'BEGIN{d=0} /^DATA ascii/{print; d=1; next} d==1 && NF==7 {printf "%s %s %s %.6f %.6f %.6f %s\n",$1,$2,$3,-$4,-$5,-$6,$7; next} {print}' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}
for p in 2 6 9; do
  neg "$W/juglet_SWAPneg/Breaklines/Juglet_Piece_${p}_Breakline_0.pcd"
  neg "$W/juglet_SWAPnegall/Breaklines/Juglet_Piece_${p}_Breakline_0.pcd"
done
neg "$W/juglet_SWAPneg7/Breaklines/Juglet_Piece_7_Breakline_0.pcd"
neg "$W/juglet_SWAPnegall/Breaklines/Juglet_Piece_7_Breakline_0.pcd"
echo "[NEG] trees built"
for t in neg neg7 negall; do
  echo "[$t] $(cd "$W/juglet_SWAP$t" && md5sum Surfaces/* Breaklines/* | md5sum)"
done
echo "[files differing vs juglet_SWAP]"
diff -rq "$W/juglet_SWAP" "$W/juglet_SWAPneg"    | sed 's/^/neg: /'
diff -rq "$W/juglet_SWAP" "$W/juglet_SWAPneg7"   | sed 's/^/neg7: /'
diff -rq "$W/juglet_SWAP" "$W/juglet_SWAPnegall" | sed 's/^/negall: /'
echo "[xyz unchanged check for P9 neg tree]"
paste <(awk 'BEGIN{d=0} /^DATA ascii/{d=1;next} d==1&&NF==7{print $1,$2,$3}' "$W/juglet_SWAP/Breaklines/Juglet_Piece_9_Breakline_0.pcd" | md5sum) <(awk 'BEGIN{d=0} /^DATA ascii/{d=1;next} d==1&&NF==7{print $1,$2,$3}' "$W/juglet_SWAPneg/Breaklines/Juglet_Piece_9_Breakline_0.pcd" | md5sum)
echo "[negated normal of P9 first row]"
awk 'BEGIN{d=0} /^DATA ascii/{d=1;next} d==1&&NF==7{print; c++; if(c==2) exit}' "$W/juglet_SWAPneg/Breaklines/Juglet_Piece_9_Breakline_0.pcd"
