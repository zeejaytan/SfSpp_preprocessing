#!/bin/bash
# t327 bar 4 setup: copy the 326 juglet GT tree twice under my run dir, then swap
# Surface_0<->Surface_1 and Breakline_0<-Bl1 for pieces 2, 6, 9 IN THE COPIES ONLY.
set -euo pipefail
RUN=$1
SRC=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1640_22151d0_t325-juglet/work/trees/juglet_GT_r1
GEOM=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
T=$RUN/work/trees
mkdir -p "$T"
cp -a "$SRC" "$T/juglet_GT_ctrl"
cp -a "$SRC" "$T/juglet_SWAP"
echo '== source tree md5 (before)'; (cd "$SRC" && find . -type f -print0 | sort -z | xargs -0 md5sum | md5sum)
for P in 2 6 9; do
  D=$T/juglet_SWAP
  mv "$D/Surfaces/Juglet_Piece_${P}_Surface_0.xyz" "$D/Surfaces/.tmp_${P}_s0"
  mv "$D/Surfaces/Juglet_Piece_${P}_Surface_1.xyz" "$D/Surfaces/Juglet_Piece_${P}_Surface_0.xyz"
  mv "$D/Surfaces/.tmp_${P}_s0" "$D/Surfaces/Juglet_Piece_${P}_Surface_1.xyz"
  cp "$D/Breaklines/Juglet_Piece_${P}_Breakline_0.pcd" "$D/Breaklines/Juglet_Piece_${P}_Breakline_1.pcd"
  cp "$GEOM/Juglet_Piece_${P}.Bl1" "$D/Breaklines/Juglet_Piece_${P}_Breakline_0.pcd"
done
echo '== ctrl vs SWAP, per-piece surface and breakline md5'
(cd "$T/juglet_GT_ctrl" && md5sum Surfaces/* Breaklines/* | sed 's|^|ctrl |') > "$RUN/work/md5_ctrl.txt"
(cd "$T/juglet_SWAP" && md5sum Surfaces/* Breaklines/* | sed 's|^|swap |') > "$RUN/work/md5_swap.txt"
diff <(cut -d' ' -f2- "$RUN/work/md5_ctrl.txt") <(cut -d' ' -f2- "$RUN/work/md5_swap.txt") || true
echo '== which files differ (should be exactly P2/P6/P9 x S0,S1,Bl0)'
join -j 2 <(sort -k2 "$RUN/work/md5_ctrl.txt") <(sort -k2 "$RUN/work/md5_swap.txt") | awk '$2!=$3{print $1}'
echo '== source tree md5 (after)'; (cd "$SRC" && find . -type f -print0 | sort -z | xargs -0 md5sum | md5sum)
echo '== geom Bl1 vs tree Breakline_0 for the six untouched pieces (sanity: unchanged)'
ls "$T/juglet_SWAP/Surfaces" | wc -l; ls "$T/juglet_SWAP/Breaklines" | wc -l