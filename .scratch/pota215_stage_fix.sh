#!/bin/bash
# POTA-215: fix tree with reclaimed Surface xyz for P16, unchanged binary.
set -euo pipefail
SRC=/data/gpfs/projects/punim2657/pota214_pipe/Temp/Data/Pot_D
NEW=/data/gpfs/projects/punim2657/sfs-potD-214
AX=/data/gpfs/projects/punim2657/pota214_pipe/Dataset/Axes
TREE=/data/gpfs/projects/punim2657/pota215_fix
POT=Pot_D
rm -rf $TREE
mkdir -p $TREE/Temp/Data/$POT $TREE/Temp/Temp_edge/$POT $TREE/Dataset/Axes $TREE/Dataset/Breaklines/$POT
cp -L $SRC/Pot_D_Piece_16_Mesh.obj $SRC/Pot_D_Piece_16_Point.pcd $SRC/Pot_D_Piece_16_SampledWithNormals.ply $SRC/Pot_D_Piece_16_unclustered.ply $SRC/Pot_D_Piece_16_unclustered.plyCluster_0.pcd $TREE/Temp/Data/$POT/
cp -L $NEW/new_Piece_16_Surface_0.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_0.xyz
cp -L $NEW/new_Piece_16_Surface_1.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_1.xyz
cp -L $AX/Pot_D_Piece_16_Axis.xyz $TREE/Dataset/Axes/
wc -l $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_0.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_1.xyz
md5sum $SRC/Pot_D_Piece_16_unclustered.ply $TREE/Temp/Data/$POT/Pot_D_Piece_16_unclustered.ply
