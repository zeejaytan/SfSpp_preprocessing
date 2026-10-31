#!/bin/bash
# POTA-215: S1-cloud-as-both-faces tree to capture S1 walk bag.
set -euo pipefail
SRC=/data/gpfs/projects/punim2657/pota214_pipe/Temp/Data/Pot_D
AX=/data/gpfs/projects/punim2657/pota214_pipe/Dataset/Axes
TREE=/data/gpfs/projects/punim2657/pota215_s1bag
POT=Pot_D
rm -rf $TREE
mkdir -p $TREE/Temp/Data/$POT $TREE/Temp/Temp_edge/$POT $TREE/Dataset/Axes $TREE/Dataset/Breaklines/$POT
cp -L $SRC/Pot_D_Piece_16_Mesh.obj $SRC/Pot_D_Piece_16_Point.pcd $SRC/Pot_D_Piece_16_SampledWithNormals.ply $SRC/Pot_D_Piece_16_unclustered.ply $SRC/Pot_D_Piece_16_unclustered.plyCluster_0.pcd $TREE/Temp/Data/$POT/
cp -L $SRC/Pot_D_Piece_16_Surface_1.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_0.xyz
cp -L $SRC/Pot_D_Piece_16_Surface_1.ply $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_0.ply
cp -L $SRC/Pot_D_Piece_16_Surface_1.xyz $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_1.xyz
cp -L $SRC/Pot_D_Piece_16_Surface_1.ply $TREE/Temp/Data/$POT/Pot_D_Piece_16_Surface_1.ply
cp -L $AX/Pot_D_Piece_16_Axis.xyz $TREE/Dataset/Axes/
ls $TREE/Temp/Data/$POT
