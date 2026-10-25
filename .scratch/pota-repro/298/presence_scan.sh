#!/usr/bin/env bash
P=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
printf "pot\tpc\taxis\tsurf0\tsurf1\tbl0\tmesh_plain\tmesh_ds\tcloud\tgtT\n"
for pot in A B C D E F G H I J; do
  for f in "$P"/Surfaces/Pot_"$pot"_Piece_*_Surface_0.xyz; do
    b=$(basename "$f" _Surface_0.xyz); p=$(echo "$b" | sed -E "s/^Pot_"$pot"_Piece_//")
    a=0; [ -f "$P/Axes/""$b""_Axis.xyz" ] && a=1
    s1=0; [ -f "$P/Surfaces/""$b""_Surface_1.xyz" ] && s1=1
    bl=0; [ -f "$P/Breaklines/""$b""_Breakline_0.pcd" ] && bl=1
    mp=0; [ -f "$P/Mesh/""$b""_Mesh.obj" ] && mp=1
    md=0; [ -f "$P/Mesh/""$b""_Mesh_DS.obj" ] && md=1
    cl=0; [ -f "$P/Point/Pot_""$pot"/"$b""_Point.pcd" ] && cl=1
    n=$((10#$p))
    gt=0; [ -f "$P/Ground Truth/Pot_"$pot"_Piece_"$n"_T.txt" ] && gt=1
    printf "Pot_%s\t%s\t%s\t1\t%s\t%s\t%s\t%s\t%s\t%s\n" "$pot" "$p" "$a" "$s1" "$bl" "$mp" "$md" "$cl" "$gt"
  done
done