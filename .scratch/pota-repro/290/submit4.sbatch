#!/bin/bash
#SBATCH --job-name=p290ascii
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --output=logs/p290ascii_%j.out

# Ticket 290 Phase 1 item 2 asks for the reading of the five ASCII clouds to be PROVED, and Phase 2
# only proves the binary one. This runs the mesh stage (the stage that loads the cloud) on one of
# the five, no scoring, no edge stage, no corpus.
set -u
: "$RUN_DIR"; : "$CANONICAL"
RUN=$RUN_DIR
CANON=$CANONICAL
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PIECE=Pot_I_Piece_28
POT=Pot_I
MESH=$RUN/bin/MeshPreprocessingHeadless
O=$RUN/out/ascii_read_test.txt
D=$RUN/ascii/st
mkdir -p "$RUN/logs" "$D/Dataset/Point/$POT" "$D/Dataset/Mesh/$POT" "$D/Dataset/Axes" "$D/Temp/Data/$POT"
ln -sfn "$CORPUS/Point/$POT/${PIECE}_Point.pcd" "$D/Dataset/Point/$POT/${PIECE}_Point.pcd"
ln -sfn "$CORPUS/Mesh/${PIECE}_Mesh_DS.obj" "$D/Dataset/Mesh/$POT/${PIECE}_Mesh.obj"
cp "$CORPUS/Axes/${PIECE}_Axis.xyz" "$D/Dataset/Axes/"
{
  echo "ticket 290 - does the pipeline read the five ASCII-derived clouds?"
  echo "piece: $PIECE  (ascii, xyz first, normals second)"
  echo "cloud: $CORPUS/Point/$POT/${PIECE}_Point.pcd  md5 $(md5sum "$CORPUS/Point/$POT/${PIECE}_Point.pcd" | cut -d" " -f1)"
  head -12 "$D/Dataset/Point/$POT/${PIECE}_Point.pcd" | grep -E "FIELDS|SIZE|TYPE|POINTS|DATA"
  echo "binary: $MESH  md5 $(md5sum "$MESH" | cut -d" " -f1)"
  echo
} > "$O"
( cd "$D" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=$POT SFS_AXIS_FILE="$D/Dataset/Axes/${PIECE}_Axis.xyz" "$MESH" > "$RUN/logs/ascii_mesh.log" 2>&1 ; echo "MESH_EXIT=$?" | tee -a "$O" )
grep -E "\[PAPER-234\] classify|\[PAPER-234\] paper grow|\[SPLITTER-234\]|Copied Point file|Selected file|rows=|cleanSamples|Write|surface" "$RUN/logs/ascii_mesh.log" | head -40 >> "$O"
{
  echo
  echo "== sheets written"
  for f in "$D/Temp/Data/$POT"/*_Surface_*.xyz; do
    [ -e "$f" ] || { echo "MISSING $f"; continue; }
    echo "$(basename "$f") rows=$(wc -l < "$f") md5=$(md5sum "$f" | cut -d" " -f1)"
  done
  echo "== classify line present: $(grep -c "PAPER-234. classify" "$RUN/logs/ascii_mesh.log")"
} >> "$O"
cat "$O"
echo "KEPT: out/ascii_read_test.txt (numbers). DELETED: ascii/ (staging tree and its sheets)." >> "$RUN/out/GEOMETRY_DELETED.txt"
rm -rf "$RUN/ascii"

