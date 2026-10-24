#!/usr/bin/env bash
#SBATCH --job-name=p294run
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
# Ticket 294 job A: build both binaries from git archive of the ticket commit, then run the nine
# below-bar pieces at the shipped defaults -- inputs staged by symlink, mesh stage with
# SFS_AXIS_FILE set (the [PAPER-234] classify line is required, ticket 277), edge stage with no
# SFS_* override. Scores every lane and writes out/manifest.json for the renderer (job B).
# Geometry is kept until job B has drawn it.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
COMMIT=0f8a4a417221647e7d6e7f7d031a90109930d44d
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
PREV=/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0134_787c149_p292-rescore

unset NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out $RUN/out/logs $RUN/out/geom $RUN/out/png $RUN/bin/edge $RUN/bin/mesh $RUN/scripts $RUN/stage
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE "^SFS_") (0 expected)"

# ---- build both binaries from the archive of the ticket commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e $COMMIT^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p294-build-$SLURM_JOB_ID
rm -rf $BT; mkdir -p $BT/src
git -C $CANON archive $COMMIT | tar -x -C $BT/src
cp -a $CANON/alglib $BT/src/alglib
echo "[RUN] archived $(find $BT/src -type f | wc -l) files into $BT/src"
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > $RUN/out/source.md5
for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of $BT/src/$f)" "$(wc -l < $BT/src/$f)" >> $RUN/out/source.md5
done
echo "[RUN] local edits: $(find $BT/src -maxdepth 1 -name "*.cpp" -newer $BT/src/CMakeLists.txt | wc -l) cpp newer than CMakeLists.txt (0 expected)"
cp -f $BT/src/.scratch/pota-repro/292/score292.py $RUN/scripts/score292.py
cp -f $BT/src/scripts/stage_piece.sh $RUN/scripts/stage_piece.sh

mkdir -p $BT/src/build; cd $BT/src/build
"$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON .. > $RUN/logs/cmake.log 2>&1
CMAKE_EXIT=$?; echo "[RUN] cmake exit=$CMAKE_EXIT"
[ $CMAKE_EXIT -eq 0 ] || { tail -20 $RUN/logs/cmake.log; exit 3; }
"$APT" exec --bind /data:/data "$SIF" make -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless > $RUN/logs/make.log 2>&1
MAKE_EXIT=$?; echo "[RUN] make exit=$MAKE_EXIT"
[ $MAKE_EXIT -eq 0 ] || { tail -40 $RUN/logs/make.log; exit 4; }
E=$(find $BT/src/build -type f -name EdgeLineExtractionHeadless | head -1)
M=$(find $BT/src/build -type f -name MeshPreprocessingHeadless | head -1)
[ -n "$E" ] && [ -n "$M" ] || { echo "[RUN] FATAL binaries not found"; exit 5; }
cp -f $E $RUN/bin/edge/EdgeLineExtractionHeadless; cp -f $M $RUN/bin/mesh/MeshPreprocessingHeadless
chmod +x $RUN/bin/edge/EdgeLineExtractionHeadless $RUN/bin/mesh/MeshPreprocessingHeadless
EDGE=$RUN/bin/edge/EdgeLineExtractionHeadless
MESH=$RUN/bin/mesh/MeshPreprocessingHeadless
EDGE_MD5=$(md5_of $EDGE); MESH_MD5=$(md5_of $MESH)
echo "[RUN] edge $EDGE_MD5"; echo "[RUN] mesh $MESH_MD5"
printf '{"commit": "%s", "edge_md5": "%s", "mesh_md5": "%s", "jobid": "%s"}\n' "$COMMIT" "$EDGE_MD5" "$MESH_MD5" "$SLURM_JOB_ID" > $RUN/out/build.json

# ---- the nine pieces, and the eleven lanes the pictures are for ----
printf "%s\n" Pot_C_Piece_03 Pot_D_Piece_22 Pot_D_Piece_27 Pot_E_Piece_16 Pot_H_Piece_02 Pot_H_Piece_10 Pot_I_Piece_06 Pot_I_Piece_13 Pot_I_Piece_25 > $RUN/out/pieces.tsv
printf "%s\t%s\n" Pot_C_Piece_03 1 Pot_D_Piece_22 0 Pot_D_Piece_27 0 Pot_D_Piece_27 1 Pot_E_Piece_16 0 Pot_H_Piece_02 1 Pot_H_Piece_10 1 Pot_I_Piece_06 1 Pot_I_Piece_13 1 Pot_I_Piece_25 0 Pot_I_Piece_25 1 > $RUN/out/lanes_wanted.tsv
: > $RUN/out/pieces_run.tsv; : > $RUN/out/classify.tsv

while read -r P; do
  [ -n "$P" ] || continue
  POT=${P%%_Piece_*}
  ST=$RUN/stage/$P
  LOG=$RUN/out/logs/${P}.log
  : > "$LOG"
  echo "[RUN] ==== $P pot=$POT stage=$ST" | tee -a "$LOG"
  bash "$RUN/scripts/stage_piece.sh" "$ST" "$POT" "$P" >> "$LOG" 2>&1; SS=$?
  echo "[RUN] stage exit=$SS" | tee -a "$LOG"
  [ $SS -eq 0 ] || { echo "[RUN] STAGE_FAILED $P"; continue; }
  MESHOBJ=$(readlink -f "$ST/Dataset/Mesh/$POT/${P}_Mesh.obj")
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ST/Dataset/Axes/${P}_Axis.xyz" "$MESH" ) >> "$LOG" 2>&1; MS=$?
  echo "[RUN] mesh exit=$MS" | tee -a "$LOG"
  CLS=$(grep -m1 "PAPER-234] classify: face0" "$LOG" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOG" || true)
  if [ -z "$CLS" ]; then echo "[RUN] FATAL CLASSIFY_MISSING $P -- SFS_AXIS_FILE was not read"; exit 6; fi
  THETA=$(grep -m1 "PAPER-234] paper grow" "$LOG" | sed "s/.*thetaDeg=//; s/ .*//")
  echo "[RUN] $P theta=$THETA" | tee -a "$LOG"
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_0.xyz" "$RUN/out/geom/${P}.S0.xyz" || echo "[RUN] SURFACE0_MISSING $P"
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_1.xyz" "$RUN/out/geom/${P}.S1.xyz" || echo "[RUN] SURFACE1_MISSING $P"
  rm -rf "$ST/Dataset/Breaklines/$POT"; mkdir -p "$ST/Dataset/Breaklines/$POT"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGE" ) >> "$LOG" 2>&1; ES=$?
  echo "[RUN] edge exit=$ES" | tee -a "$LOG"
  for K in 0 1; do
    cp -f "$ST/Dataset/Breaklines/$POT/${P}_Breakline_${K}.pcd" "$RUN/out/geom/${P}.Bl${K}.pcd" 2>/dev/null || echo "[RUN] EXPORT_MISSING $P $K"
  done
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$P" "$POT" "$THETA" "$MESHOBJ" "$RUN/out/geom/${P}.S0.xyz" "$RUN/out/geom/${P}.S1.xyz" >> "$RUN/out/pieces_run.tsv"
  printf "%s\t%s\t%s\t%s\n" "$P" "$CLS" "$SW" "$THETA" >> "$RUN/out/classify.tsv"
done < "$RUN/out/pieces.tsv"
echo "[RUN] pieces run: $(wc -l < $RUN/out/pieces_run.tsv) of 9; classify lines: $(wc -l < $RUN/out/classify.tsv) of 9"

# ---- score every lane of every piece, lane k against the authors lane k ----
: > $RUN/out/lanes_fresh.tsv
while IFS=$(printf "\t") read -r P POT THETA MOBJ S0 S1; do
  for K in 0 1; do
    O=$RUN/out/geom/${P}.Bl${K}.pcd
    A=$CORP/Breaklines/${P}_Breakline_${K}.pcd
    if [ -f "$O" ] && [ -f "$A" ]; then
      "$PY" "$RUN/scripts/score292.py" "$POT" "$P" "$K" "$O" "$A" >> $RUN/out/lanes_fresh.tsv
    else
      echo "[RUN] cannot score $P Bl$K (ours $( [ -f "$O" ] && echo yes || echo no ), authors $( [ -f "$A" ] && echo yes || echo no ))"
    fi
  done
done < $RUN/out/pieces_run.tsv
echo "[RUN] fresh lane rows: $(wc -l < $RUN/out/lanes_fresh.tsv) (18 expected)"

# ---- manifest for the renderer: fresh rows joined with the ticket-292 rows ----
"$PY" "$RUN/scripts/manifest294.py" "$RUN" "$PREV" > $RUN/out/manifest.log 2>&1
MEXIT=$?; echo "[RUN] manifest exit=$MEXIT"; [ $MEXIT -eq 0 ] || tail -20 $RUN/out/manifest.log
[ -f $RUN/out/manifest.json ] && echo "[RUN] manifest lanes=$(python3 -c "import json;print(len(json.load(open("$RUN/out/manifest.json"))["lanes"]))" 2>/dev/null || echo "?")"

# the build tree is source plus objects, not record
rm -rf $BT
echo "[RUN] done $(date -Is); stage trees kept for job B"