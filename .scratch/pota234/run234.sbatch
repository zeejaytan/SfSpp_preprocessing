#!/bin/bash
# POTA-234 plane-continuity split: single piece mesh (+edge) per tree.
# Env: POT (Pot_D|Juglet) PIECE (22|12|1) TAG (label) MODE (plane|old|paper) EDGE (1|0)
#SBATCH --job-name=fix234-run
#SBATCH --account=punim2657
#SBATCH --partition=sapphire,cascade
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=run234_%j.out
#SBATCH --error=run234_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-fix-234
BUILD="$WROOT/build-234"
EDGEBIN=/data/gpfs/projects/punim2657/sfs-fix-232/build-220/EdgeLineExtractionHeadless
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
ORIG=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
JORIG=/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916/SfS_pp
SAMPLED=/data/gpfs/projects/punim2657/sfs-potD-214/Dataset_Input/Point/Pot_D
: "${POT:?need POT}" "${PIECE:?need PIECE}" "${TAG:?need TAG}" "${MODE:?need MODE}" "${EDGE:?need EDGE}"
TREE=/data/gpfs/projects/punim2657/pota234_${TAG}
echo "===== 234 ${POT} P${PIECE} mode=${MODE} edge=${EDGE} tag=${TAG} ====="; date; hostname
[ -x "$BUILD/MeshPreprocessingHeadless" ] || { echo MESH-BINARY-MISSING; exit 1; }
md5sum "$BUILD/MeshPreprocessingHeadless"
if [ "$EDGE" = "1" ]; then [ -x "$EDGEBIN" ] || { echo EDGE-BINARY-MISSING; exit 1; }; md5sum "$EDGEBIN"; fi
rm -rf "$TREE"
mkdir -p "$TREE/Temp/Data/$POT" "$TREE/Dataset/Mesh/$POT" "$TREE/Dataset/Point/$POT" "$TREE/Dataset/Axes" "$TREE/Dataset/Breaklines/$POT" "$TREE/Dataset/Surfaces/$POT"
if [ "$POT" = "Juglet" ]; then
  cp -L "$JORIG/Mesh/Juglet_Piece_${PIECE}_Mesh.obj" "$TREE/Dataset/Mesh/$POT/Juglet_Piece_${PIECE}_Mesh.obj"
  cp -L "$JORIG/Surfaces/Juglet_Piece_${PIECE}_Point.pcd" "$TREE/Dataset/Point/$POT/"
  cp -L "$JORIG/Axes/Juglet_Piece_${PIECE}_Axis.xyz" "$TREE/Dataset/Axes/"
  ls "$TREE/Dataset/Point/$POT/"
else
  cp -L "$SAMPLED/${POT}_Piece_${PIECE}_Point.pcd" "$TREE/Dataset/Point/$POT/"
  cp -L "$ORIG/Mesh/${POT}_Piece_${PIECE}_Mesh_DS.obj" "$TREE/Dataset/Mesh/$POT/${POT}_Piece_${PIECE}_Mesh.obj"
  cp -L "$ORIG/Axes/${POT}_Piece_${PIECE}_Axis.xyz" "$TREE/Dataset/Axes/"
fi
export SFS_PLANE_RULE=0 SFS_PAPER_CHAIN=0
if [ "$MODE" = "plane" ]; then
  export SFS_PLANE_RULE=1 SFS_PLANE_JOIN_DEG=60 SFS_PLANE_DIST_MM=2.0 SFS_PLANE_WINDOW=100 SFS_SINGLE_SHOT=1
elif [ "$MODE" = "paper" ]; then
  export SFS_PAPER_CHAIN=1 SFS_SINGLE_SHOT=1
  export SFS_AXIS_FILE="$TREE/Dataset/Axes/${POT}_Piece_${PIECE}_Axis.xyz"
  export SFS_PAPER_RHOD="${SFS_PAPER_RHOD:-1.0}" SFS_PAPER_RHON="${SFS_PAPER_RHON:-0.95}" SFS_PAPER_RHOC="${SFS_PAPER_RHOC:-0.1}" SFS_PAPER_RHOINN="${SFS_PAPER_RHOINN:-0.75}" SFS_PAPER_RHOINC="${SFS_PAPER_RHOINC:-0.25}"
else
  export SFS_SMOOTHNESS_DEG=4.5 SFS_SINGLE_SHOT=1
fi
( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_PLANE_RULE="$SFS_PLANE_RULE" SFS_PLANE_JOIN_DEG="${SFS_PLANE_JOIN_DEG:-}" SFS_PLANE_DIST_MM="${SFS_PLANE_DIST_MM:-}" SFS_PLANE_WINDOW="${SFS_PLANE_WINDOW:-}" SFS_SMOOTHNESS_DEG="${SFS_SMOOTHNESS_DEG:-}" SFS_PAPER_CHAIN="$SFS_PAPER_CHAIN" SFS_AXIS_FILE="${SFS_AXIS_FILE:-}" SFS_PAPER_RHOD="${SFS_PAPER_RHOD:-}" SFS_PAPER_RHON="${SFS_PAPER_RHON:-}" SFS_PAPER_RHOC="${SFS_PAPER_RHOC:-}" SFS_PAPER_RHOINN="${SFS_PAPER_RHOINN:-}" SFS_PAPER_RHOINC="${SFS_PAPER_RHOINC:-}" SFS_SINGLE_SHOT=1 "$BUILD/MeshPreprocessingHeadless" ) > "$TREE/mesh_${TAG}.log" 2>&1
grep -a "Number of clusters\|SPLITTER-234\|PLANE-234" "$TREE/mesh_${TAG}.log" | head
if [ "$EDGE" = "1" ]; then
  ( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGEBIN" ) > "$TREE/edge_${TAG}.log" 2>&1
  echo "edge done"
  grep -a -c "LOOP-SELECT" "$TREE/edge_${TAG}.log" || true
fi
echo DONE; date
