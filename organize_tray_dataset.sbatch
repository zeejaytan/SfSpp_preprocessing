#!/bin/bash
#SBATCH --job-name=organize_tray
#SBATCH --partition=sapphire
#SBATCH --time=00:15:00
#SBATCH --mem=2G
#SBATCH --cpus-per-task=1
#SBATCH --output=organize_tray_%j.out
#SBATCH --error=organize_tray_%j.err

set -euo pipefail

BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
cd "$BASE_DIR"

DATASET_NAME="Tray-000"
DATE=$(date +%Y%m%d)
DEST="${DATASET_NAME}_Dataset_${DATE}"

mkdir -p "$DEST/SfS_pp/"{Surfaces,Breaklines,Axes,Mesh,Point/${DATASET_NAME}}

echo "Copying Surfaces..."
for f in Dataset/Surfaces/Pot_A/*.xyz; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  cp -f "$f" "$DEST/SfS_pp/Surfaces/${b/Pot_A/${DATASET_NAME}}"
done

echo "Copying Breaklines..."
for f in Dataset/Breaklines/Pot_A/*.pcd; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  cp -f "$f" "$DEST/SfS_pp/Breaklines/${b/Pot_A/${DATASET_NAME}}"
done

echo "Copying Axes..."
for f in Dataset/Axes/Pot_A_Piece_*_Axis.xyz; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  cp -f "$f" "$DEST/SfS_pp/Axes/${b/Pot_A/${DATASET_NAME}}"
done

echo "Copying Mesh..."
for f in Dataset/Mesh/Pot_A/*.obj; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  cp -f "$f" "$DEST/SfS_pp/Mesh/${b/Pot_A/${DATASET_NAME}}"
done

echo "Copying Point clouds..."
for f in Dataset/Point/Pot_A/Pot_A_Piece_*_Point.pcd; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  cp -f "$f" "$DEST/SfS_pp/Point/${DATASET_NAME}/${b/Pot_A/${DATASET_NAME}}"
done

ln -sfn "$DEST" latest_tray_dataset
echo "Organized dataset at: $DEST"

