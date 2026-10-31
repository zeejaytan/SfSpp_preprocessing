#!/bin/bash
# POTA-215: stage P16-only tree reusing 214 inputs (separate out dir), reproduce walk.
set -euo pipefail
SRC=/data/gpfs/projects/punim2657/pota214_pipe
TREE=/data/gpfs/projects/punim2657/pota215_pipe
POT=Pot_D
rm -rf "$TREE"
mkdir -p "$TREE/Temp/Data/$POT" "$TREE/Temp/Temp_edge/$POT" "$TREE/Dataset/Axes" "$TREE/Dataset/Breaklines/$POT"
cp -L "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Mesh.obj "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Point.pcd \
  "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_SampledWithNormals.ply "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Surface_0.xyz \
  "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Surface_0.ply "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Surface_1.xyz \
  "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Surface_1.ply "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_unclustered.ply \
  "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_unclustered.plyCluster_0.pcd "$TREE/Temp/Data/$POT/"
cp -L "$SRC/Dataset/Axes"/Pot_D_Piece_16_Axis.xyz "$TREE/Dataset/Axes/"
ls "$TREE/Temp/Data/$POT" | wc -l
md5sum "$TREE/Temp/Data/$POT"/Pot_D_Piece_16_Surface_0.xyz "$SRC/Temp/Data/$POT"/Pot_D_Piece_16_Surface_0.xyz
