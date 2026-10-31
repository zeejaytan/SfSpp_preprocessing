#!/bin/bash
# POTA-215 F24: per-face strip-UN trees with ORIG clouds, unchanged binary.
set -euo pipefail
SRC=/data/gpfs/projects/punim2657/pota214_pipe/Temp/Data/Pot_D
NEW=/data/gpfs/projects/punim2657/sfs-potD-214
AX=/data/gpfs/projects/punim2657/pota214_pipe/Dataset/Axes
POT=Pot_D
for FACE in S0 S1; do
TREE=/data/gpfs/projects/punim2657/pota215_strip$FACE
rm -rf $TREE
mkdir -p $TREE/Temp/Data/$POT $TREE/Temp/Temp_edge/$POT $TREE/Dataset/Axes $TREE/Dataset/Breaklines/$POT
cp -L $SRC/Pot_D_Piece_16_Mesh.obj $SRC/Pot_D_Piece_16_Point.pcd $SRC/Pot_D_Piece_16_SampledWithNormals.ply $SRC/Pot_D_Piece_16_unclustered.plyCluster_0.pcd $TREE/Temp/Data/$POT/
cp -L $SRC/Pot_D_Piece_16_Surface_0.xyz $SRC/Pot_D_Piece_16_Surface_0.ply $SRC/Pot_D_Piece_16_Surface_1.xyz $SRC/Pot_D_Piece_16_Surface_1.ply $TREE/Temp/Data/$POT/
cp -L $NEW/strip_un_P16_$FACE.ply $TREE/Temp/Data/$POT/Pot_D_Piece_16_unclustered.ply
cp -L $AX/Pot_D_Piece_16_Axis.xyz $TREE/Dataset/Axes/
md5sum $SRC/Pot_D_Piece_16_Surface_0.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_0.xyz
ls -la $TREE/Temp/Data/$POT/Pot_D_Piece_16_unclustered.ply
done
echo STAGED-BOTH
