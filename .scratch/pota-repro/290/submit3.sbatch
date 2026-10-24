#!/bin/bash
#SBATCH --job-name=p290cmp
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=logs/p290cmp_%j.out

# Ticket 290 follow-up: job 33748615 found the scores identical across two edge runs but the
# exported files not byte-identical. This locates the difference: header, order, or values.
set -u
: "$RUN_DIR"; : "$CANONICAL"
RUN=$RUN_DIR
CANON=$CANONICAL
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PYC=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
POINT=$CORPUS/Point
PIECE=Pot_J_Piece_09
MESH=$RUN/bin/MeshPreprocessingHeadless
EDGE=$RUN/bin/EdgeLineExtractionHeadless
D=$RUN/cmp
mkdir -p "$RUN/logs" "$D/st"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "job $SLURM_JOB_ID"
mkdir -p "$D/st/Dataset/Point/Pot_J" "$D/st/Dataset/Mesh/Pot_J" "$D/st/Dataset/Axes" "$D/st/Dataset/Breaklines/Pot_J" "$D/st/Temp/Data/Pot_J" "$D/st/Temp/Temp_edge/Pot_J"
ln -sfn "$POINT/Pot_J/"$PIECE"_Point.pcd" "$D/st/Dataset/Point/Pot_J/"$PIECE"_Point.pcd"
cp "$CORPUS/Mesh/"$PIECE"_Mesh_DS.obj" "$D/st/Dataset/Mesh/Pot_J/"$PIECE"_Mesh.obj"
cp "$CORPUS/Axes/"$PIECE"_Axis.xyz" "$D/st/Dataset/Axes/"
( cd "$D/st" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J SFS_AXIS_FILE="$D/st/Dataset/Axes/"$PIECE"_Axis.xyz" "$MESH" > "$RUN/logs/mesh_cmp.log" 2>&1 ; echo "MESH_EXIT=$?" )
for r in A B; do
  cp -a "$D/st" "$D/$r"
  ( cd "$D/$r" && rm -f Dataset/Breaklines/Pot_J/*.pcd && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$EDGE" > "$RUN/logs/edge_cmp$r.log" 2>&1 ; echo "EDGE_${r}_EXIT=$?" )
done
for st in 0 1; do
  echo "=== lane $st"
  "$PYC" "$RUN/cmp290.py" "$D/A/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_$st.pcd" "$D/B/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_$st.pcd" | tee -a "$RUN/out/bytes_vs_numbers.txt"
done
sed -n "1,14p" "$D/A/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" | tee -a "$RUN/out/bytes_vs_numbers.txt"
cmp -l "$D/A/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" "$D/B/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" 2>/dev/null | head -5 | tee -a "$RUN/out/bytes_vs_numbers.txt"
echo "cmp_exit=$?" | tee -a "$RUN/out/bytes_vs_numbers.txt"
cp "$D/A/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" "$RUN/out/cmpA_lane0.pcd"
cp "$D/B/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" "$RUN/out/cmpB_lane0.pcd"
{
  md5sum "$RUN/out/cmpA_lane0.pcd" "$RUN/out/cmpB_lane0.pcd"
  echo "cmp_stage_files=$(find "$D" -type f | wc -l)"
} | tee -a "$RUN/out/geometry.md5"
echo "KEPT two tiny exports for the byte diff: out/cmpA_lane0.pcd out/cmpB_lane0.pcd" >> "$RUN/out/GEOMETRY_DELETED.txt"
echo "DELETED: cmp/ (staging trees and their Temp products)." >> "$RUN/out/GEOMETRY_DELETED.txt"
rm -rf "$D"
say "DONE"
