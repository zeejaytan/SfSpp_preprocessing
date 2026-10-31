#!/bin/bash
# POTA-214: sample ORIG Pot_D Mesh_DS OBJs -> legacy-format Point PCDs (29 pieces).
# Density rule: legacy Pot_A scan density (P01: 843433 pts / 23273.6 mm2 = 36.24 pts/mm2).
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --job-name=pota214_sample
#SBATCH --output=pota214_sample_%j.out
#SBATCH --error=pota214_sample_%j.err
set -euo pipefail
ORIG=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh
WROOT=/data/gpfs/projects/punim2657/sfs-potD-214
OUT=$WROOT/Dataset_Input/Point/Pot_D
SAMPLE=$WROOT/pota214_sample_points.py
mkdir -p "$OUT"
ls "$SAMPLE" "$ORIG/Pot_D_Piece_01_Mesh_DS.obj"
FILES=""; for i in $(seq -w 1 29); do FILES="$FILES Pot_D_Piece_${i}_Mesh_DS.obj"; done
python3 "$WROOT/pota214_mesh_areas.py" "$ORIG" $(echo $FILES | tr ' ' ',') | tail -35
python3 "$SAMPLE" "$ORIG" "$OUT" 36.24 $FILES
 echo "### output census"
ls "$OUT" | wc -l
du -sh "$OUT"
head -12 "$OUT/Pot_D_Piece_01_Point.pcd"
