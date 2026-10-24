#!/bin/bash
#SBATCH --job-name=p291det
#SBATCH --partition=cascade
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:30:00
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 291 follow-up: is the Pot H 02 mesh stage reproducible at all?
# The gate job (33748798) found Pot J 09 bit-identical between a copied and a symlinked
# stage but Pot H 02 different (max 0.717 mm) with identical classify counts. Four runs on
# the SAME frozen input decide whether that spread belongs to the staging method or to the
# pipeline: A2/A3 staged by cp, B2/B3 staged by scripts/stage_piece.sh (symlinks).
set -uo pipefail

RUN=${RUN_DIR:?RUN_DIR must be set}
OUT=$RUN/out
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
EDGE=$RUN/bin/EdgeLineExtractionHeadless
MESH=$RUN/bin/MeshPreprocessingHeadless
PY=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
POT=Pot_H
PIECE=Pot_H_Piece_02
AXIS=$CORPUS/Axes/${PIECE}_Axis.xyz
MOBJ=$CORPUS/Mesh/${PIECE}_Mesh_DS.obj
CLOUD=$CORPUS/Point/$POT/${PIECE}_Point.pcd

echo "det probe start $(date) on $(hostname)"
mkdir -p "$OUT/sheets" "$OUT/det"
: > "$OUT/det_sheets.md5"
: > "$OUT/det_exits.txt"
echo "inputs: mesh $(md5sum "$MOBJ" | cut -d" " -f1) cloud $(md5sum "$CLOUD" | cut -d" " -f1) axis $(md5sum "$AXIS" | cut -d" " -f1)"

prep_cp() {
  local st=$1
  mkdir -p "$st/Dataset/Mesh/$POT" "$st/Dataset/Point/$POT" "$st/Dataset/Axes" \
           "$st/Dataset/Breaklines/$POT" "$st/Dataset/Surfaces/$POT" \
           "$st/Temp/Data/$POT" "$st/Temp/Temp_edge/$POT"
  cp "$MOBJ"  "$st/Dataset/Mesh/$POT/${PIECE}_Mesh.obj"
  cp "$CLOUD" "$st/Dataset/Point/$POT/${PIECE}_Point.pcd"
  cp "$AXIS"  "$st/Dataset/Axes/${PIECE}_Axis.xyz"
}

run_mesh() {
  local st=$1 lab=$2 rc=0
  ( cd "$st" && POT_NAME=$POT SFS_AXIS_FILE="$st/Dataset/Axes/${PIECE}_Axis.xyz" \
      "$APT" exec --bind /data:/data "$SIF" "$MESH" > "$OUT/det_mesh_$lab.log" 2>&1 ) || rc=$?
  echo "MESH_EXIT[$lab]=$rc" >> "$OUT/det_exits.txt"
  grep -E "\[PAPER-234\] classify:" "$OUT/det_mesh_$lab.log" > "$OUT/det_classify_$lab.txt" 2>/dev/null
  local i s
  for i in 0 1; do
    s="$st/Temp/Data/$POT/${PIECE}_Surface_$i.xyz"
    if [ -f "$s" ]; then
      echo "$lab Surface_$i $(md5sum "$s" | cut -d" " -f1) rows=$(wc -l < "$s")" >> "$OUT/det_sheets.md5"
      cp "$s" "$OUT/sheets/${PIECE}_${lab}_Surface_$i.xyz"
    else
      echo "$lab Surface_$i MISSING" >> "$OUT/det_sheets.md5"
    fi
  done
}

run_edge() {
  local st=$1 lab=$2 rc=0 i e
  rm -f "$st"/Dataset/Breaklines/$POT/*
  ( cd "$st" && POT_NAME=$POT "$APT" exec --bind /data:/data "$SIF" "$EDGE" > "$OUT/det_edge_$lab.log" 2>&1 ) || rc=$?
  echo "EDGE_EXIT[$lab]=$rc" >> "$OUT/det_exits.txt"
  for i in 0 1; do
    e="$st/Dataset/Breaklines/$POT/${PIECE}_Breakline_$i.pcd"
    if [ -f "$e" ]; then cp "$e" "$OUT/det/${lab}_Bl$i.pcd"; else echo "MISSING export $lab Bl$i" >> "$OUT/det_exits.txt"; fi
  done
}

for lab in A2 A3; do
  st=$RUN/stage${lab}_$PIECE
  prep_cp "$st" || { echo "PREP_FAILED $lab"; continue; }
  run_mesh "$st" "$lab"
  run_edge "$st" "$lab"
done

for lab in B2 B3; do
  st=$RUN/stage${lab}_$PIECE
  bash "$RUN/stage_piece.sh" "$st" "$POT" "$PIECE" > "$OUT/det_stage_$lab.log" 2>&1
  echo "STAGE_EXIT[$lab]=$?" >> "$OUT/det_exits.txt"
  run_mesh "$st" "$lab"
  run_edge "$st" "$lab"
done

echo "--- sheet md5s ---"
cat "$OUT/det_sheets.md5"
echo "--- exits ---"
cat "$OUT/det_exits.txt"

"$PY" "$RUN/cmp2.py" "$OUT" > "$OUT/cmp2.txt" 2>&1
echo "CMP2_EXIT=$?"
cat "$OUT/cmp2.txt"

"$PY" "$RUN/gate3_fix.py" "$OUT" > "$OUT/gate3_fixed.txt" 2>&1
echo "GATE3FIX_EXIT=$?"
cat "$OUT/gate3_fixed.txt"

echo "--- delete the four stage trees and the kept geometry copies ---"
rm -rf "$RUN"/stageA2_"$PIECE" "$RUN"/stageA3_"$PIECE" "$RUN"/stageB2_"$PIECE" "$RUN"/stageB3_"$PIECE"
rm -rf "$OUT/sheets" "$OUT/det"
{ echo "ticket 291 determinism probe, $(date)"
  echo "deleted: the four stage trees (stageA2/A3/B2/B3), out/sheets/ (12 Surface sheets), out/det/ (8 exports)"
  echo "kept: logs (det_mesh_*.log, det_edge_*.log, det_stage_*.log), text results (det_sheets.md5, det_exits.txt, det_classify_*.txt, cmp2.txt, gate3_fixed.txt), binaries"
  echo "not touched: the frozen corpus (input)"
} > "$OUT/GEOMETRY_DELETED2.txt"
ls -1 "$RUN" | grep -c "^stage" | sed "s/^/STAGE_DIRS_REMAINING=/"
echo "det probe done $(date)"
