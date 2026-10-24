#!/bin/bash
#SBATCH --job-name=p291gate
#SBATCH --time=00:40:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 291 gate: one piece staged by cp (A) and by scripts/stage_piece.sh (B), same inputs, same
# binaries, mesh stage then edge stage in each. Pre-registered: identity of the exported lanes, no
# geometry in the symlinked stage, provenance resolving to the corpus, scores merely reported.
set -uo pipefail

RUN=${RUN_DIR:?RUN_DIR must be exported at submit time}
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
SRC_BIN=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2328_d36a33e_p290-corpus/bin
BIN_EDGE=$RUN/bin/EdgeLineExtractionHeadless
BIN_MESH=$RUN/bin/MeshPreprocessingHeadless
OUT=$RUN/out
PIECES="Pot_J:Pot_J_Piece_09 Pot_H:Pot_H_Piece_02"
CORPUS_INPUTS="$CORPUS/Mesh/Pot_J_Piece_09_Mesh_DS.obj $CORPUS/Mesh/Pot_H_Piece_02_Mesh_DS.obj $CORPUS/Point/Pot_J/Pot_J_Piece_09_Point.pcd $CORPUS/Point/Pot_H/Pot_H_Piece_02_Point.pcd $CORPUS/Axes/Pot_J_Piece_09_Axis.xyz $CORPUS/Axes/Pot_H_Piece_02_Axis.xyz"

step() { echo; echo "=== $* ==="; }
mkdir -p "$OUT" "$RUN/bin" "$RUN/logs"
echo "job=$SLURM_JOB_ID run=$RUN host=$(hostname) start=$(date "+%F %T")"

step "0 record the tools, and the script under test"
cp -f "$SRC_BIN/EdgeLineExtractionHeadless" "$BIN_EDGE"
cp -f "$SRC_BIN/MeshPreprocessingHeadless" "$BIN_MESH"
chmod +x "$BIN_EDGE" "$BIN_MESH"
md5sum "$BIN_EDGE" "$BIN_MESH" | tee "$OUT/binaries.md5"
echo "expected_edge=a28d10afab2b50bbe750d599ee2b7214 expected_mesh=0171f471d0558d2676df7c4b113c1e9d" | tee -a "$OUT/binaries.md5"
echo "SEED287_strings=$(strings "$BIN_EDGE" | grep -c SEED-287)" | tee -a "$OUT/binaries.md5"
md5sum "$RUN/stage_piece.sh" "$RUN/cmp291.py" | tee "$OUT/scripts.md5"
for f in $CORPUS_INPUTS; do md5sum "$f"; done > "$OUT/corpus_before.md5"
echo "corpus inputs recorded: $(wc -l < "$OUT/corpus_before.md5")"

prep_cp() { # prep_cp <stage> <pot> <piece>  -- the old way: copy every input in
  local st=$1 pot=$2 piece=$3 cand
  mkdir -p "$st/Dataset/Mesh/$pot" "$st/Dataset/Point/$pot" "$st/Dataset/Axes" "$st/Dataset/Breaklines/$pot" "$st/Dataset/Surfaces/$pot" "$st/Temp/Data/$pot" "$st/Temp/Temp_edge/$pot"
  for cand in "$CORPUS/Mesh/$pot/${piece}_Mesh.obj" "$CORPUS/Mesh/${piece}_Mesh.obj" "$CORPUS/Mesh/$pot/${piece}_Mesh_DS.obj" "$CORPUS/Mesh/${piece}_Mesh_DS.obj"; do
    if [ -f "$cand" ]; then cp -f "$cand" "$st/Dataset/Mesh/$pot/${piece}_Mesh.obj"; break; fi
  done
  cp -f "$CORPUS/Point/$pot/${piece}_Point.pcd" "$st/Dataset/Point/$pot/"
  cp -f "$CORPUS/Axes/${piece}_Axis.xyz" "$st/Dataset/Axes/"
}

census() { # census <stage> <label> <piece>
  local st=$1 lab=$2 piece=$3
  {
    echo "## pre-run census: $lab $piece"
    echo "-- count: $(find "$st" -type f -size +1M | wc -l)"
    find "$st" -type f -size +1M -printf "%s %p\n" | sort -k2
    echo "-- symlinks: $(find "$st" -type l | wc -l)"
    find "$st" -type l -printf "%p -> %l\n" | sort
    echo "-- du: $(du -sh "$st" | cut -f1)"
    echo "-- files: $(find "$st" -type f | wc -l)"
  } > "$OUT/census_${lab}_${piece}.txt" 2>&1
}

run_mesh() { # run_mesh <stage> <pot> <piece> <label>
  local st=$1 pot=$2 piece=$3 lab=$4
  ( cd "$st" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" SFS_AXIS_FILE="$st/Dataset/Axes/${piece}_Axis.xyz" "$BIN_MESH" ) > "$OUT/mesh_${lab}_${piece}.log" 2>&1
  echo "MESH_EXIT[$lab $piece]=$?" | tee -a "$OUT/exits.txt"
  grep -E "^\[PAPER-234\] classify: |^\[SPLITTER-234\] rule=|^\[PAPER-234\] paper grow:" "$OUT/mesh_${lab}_${piece}.log" >> "$OUT/classify_lines.txt"
  ( cd "$st" && md5sum Temp/Data/"$pot"/*_Surface_*.xyz ) > "$OUT/sheets_${lab}_${piece}.md5" 2>/dev/null
  [ -s "$OUT/sheets_${lab}_${piece}.md5" ] || echo "NO_SHEETS[$lab $piece]" >> "$OUT/sheets_${lab}_${piece}.md5"
}

run_edge() { # run_edge <stage> <pot> <piece> <label>
  local st=$1 pot=$2 piece=$3 lab=$4 i src
  rm -f "$st"/Dataset/Breaklines/"$pot"/* 2>/dev/null
  ( cd "$st" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" "$BIN_EDGE" ) > "$OUT/edge_${lab}_${piece}.log" 2>&1
  echo "EDGE_EXIT[$lab $piece]=$?" | tee -a "$OUT/exits.txt"
  grep -E "^\[(SEED-287|FULL-263|STOP-267)" "$OUT/edge_${lab}_${piece}.log" >> "$OUT/walk_lines.txt"
  for i in 0 1; do
    src="$st/Dataset/Breaklines/$pot/${piece}_Breakline_$i.pcd"
    if [ -f "$src" ]; then cp -f "$src" "$OUT/${lab}_${piece}_Bl$i.pcd"; else echo "MISSING_EXPORT[$lab $piece Bl$i]" >> "$OUT/missing.txt"; fi
  done
}

for spec in $PIECES; do
  pot=${spec%%:*}
  piece=${spec#*:}
  stA=$RUN/stageA_$piece
  stB=$RUN/stageB_$piece
  rm -rf "$stA" "$stB"
  step "$pot $piece: stage A by cp, stage B by stage_piece.sh"
  prep_cp "$stA" "$pot" "$piece"
  echo "A: $(find "$stA" -type f | wc -l) files, $(du -sh "$stA" | cut -f1)"
  bash "$RUN/stage_piece.sh" "$stB" "$pot" "$piece" > "$OUT/stageB_$piece.log" 2>&1
  echo "STAGE_EXIT[$piece]=$?" | tee -a "$OUT/exits.txt"
  tail -3 "$OUT/stageB_$piece.log"
  cp -f "$stB/inputs.md5" "$OUT/inputs_B_$piece.md5" 2>/dev/null
  census "$stA" A "$piece"
  census "$stB" B "$piece"
  for lab in A B; do
    if [ "$lab" = A ]; then st=$stA; else st=$stB; fi
    step "$pot $piece: $lab mesh stage, then $lab edge stage"
    run_mesh "$st" "$pot" "$piece" "$lab"
    grep -E "^\[PAPER-234\] classify: " "$OUT/mesh_${lab}_${piece}.log" | tail -2
    run_edge "$st" "$pot" "$piece" "$lab"
    tail -1 "$OUT/edge_${lab}_${piece}.log"
  done
done

step "corpus unchanged?"
for f in $CORPUS_INPUTS; do md5sum "$f"; done > "$OUT/corpus_after.md5"
if diff -q "$OUT/corpus_before.md5" "$OUT/corpus_after.md5" > /dev/null; then
  echo "CORPUS_UNCHANGED=YES (no input file changed)" | tee "$OUT/corpus_check.txt"
else
  echo "CORPUS_UNCHANGED=NO" | tee "$OUT/corpus_check.txt"
  diff "$OUT/corpus_before.md5" "$OUT/corpus_after.md5" | tee -a "$OUT/corpus_check.txt"
fi

step "gate analysis"
"$PY" "$RUN/cmp291.py" "$RUN" > "$OUT/cmp291.txt" 2>&1
CMP_EXIT=$?
cat "$OUT/cmp291.txt"
echo "CMP_EXIT=$CMP_EXIT" | tee -a "$OUT/exits.txt"

step "delete the stage trees (geometry dies with the ticket)"
{
  echo "ticket 291 gate: stage trees deleted $(date "+%F %T")"
  for d in "$RUN"/stageA_* "$RUN"/stageB_*; do [ -d "$d" ] && echo "deleted $(du -sh "$d" | cut -f1)  $d"; done
  echo "kept: run.json, submit.sbatch, stage_piece.sh, cmp291.py, logs/, bin/, out/ (lane exports, per-arm logs, censuses, inputs.md5 records, md5 lists)"
} > "$OUT/GEOMETRY_DELETED.txt"
rm -rf "$RUN"/stageA_* "$RUN"/stageB_*
echo "STAGE_DIRS_REMAINING=$(find "$RUN" -maxdepth 1 -type d -name "stage*" | wc -l)" | tee -a "$OUT/GEOMETRY_DELETED.txt"
echo
echo "done=$(date "+%F %T") CMP_EXIT=$CMP_EXIT"
