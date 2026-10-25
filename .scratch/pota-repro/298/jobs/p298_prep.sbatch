#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p298prep
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 298 prep, one pot per job. Builds both preprocessing binaries from git archive of the
# pushed ticket commit, then runs the shipped chain on every ACTIVE piece of the pot:
#   stage_piece.sh (the authors' released cloud, symlinked -- none is derived) -> mesh stage with
#   SFS_AXIS_FILE set (the [PAPER-234] classify line is REQUIRED, ticket 277) -> edge stage.
# Shipped defaults only; no SFS_* override; no sweep. Exports out/geom/<Piece>.{S0,S1,Bl0,Bl1}
# = OUR bundle for this pot, which is a DELIVERABLE (unseeded stages, cannot be regenerated
# byte-identically -- ticket 284) and is kept. Nothing is assembled here.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
: ${POT:?POT must be exported, e.g. Pot_B}
: ${COMMIT:?COMMIT must be exported: the pushed ticket commit to build from}
RUN=$RUN_DIR
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PIECES=$RUN/scripts/pieces.txt

unset NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out/logs $RUN/out/geom $RUN/bin/edge $RUN/bin/mesh $RUN/scripts $RUN/stage
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) pot=$POT commit=$COMMIT"
echo "[RUN] pieces: $(wc -l < $PIECES) from $PIECES"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_') (0 expected)"

# ---- build both binaries from the archive of the ticket commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e ${COMMIT}^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p298-prep-$POT-$SLURM_JOB_ID
rm -rf $BT; mkdir -p $BT/src
git -C $CANON archive $COMMIT | tar -x -C $BT/src
cp -a $CANON/alglib $BT/src/alglib
echo "[RUN] archived $(find $BT/src -type f | wc -l) files into $BT/src"
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > $RUN/out/source.md5
for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of $BT/src/$f)" "$(wc -l < $BT/src/$f)" >> $RUN/out/source.md5
done
cp -f $BT/src/scripts/stage_piece.sh $RUN/scripts/stage_piece.sh
printf "chain\t%s\t%s lines\n" "scripts/stage_piece.sh" "$(wc -l < $RUN/scripts/stage_piece.sh)" >> $RUN/out/source.md5
printf "job\t%s\t%s\n" "$(basename $0)" "$(md5_of $RUN/submit.sbatch)" >> $RUN/out/source.md5

mkdir -p $BT/src/build; cd $BT/src/build
"$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. > $RUN/logs/cmake.log 2>&1
CMAKE_EXIT=$?; echo "[RUN] cmake exit=$CMAKE_EXIT"
[ $CMAKE_EXIT -eq 0 ] || { tail -20 $RUN/logs/cmake.log; exit 3; }
"$APT" exec --bind /data:/data "$SIF" make -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless > $RUN/logs/make.log 2>&1
MAKE_EXIT=$?; echo "[RUN] make exit=$MAKE_EXIT"
[ $MAKE_EXIT -eq 0 ] || { tail -40 $RUN/logs/make.log; exit 4; }
E=$(find $BT/src/build -type f -name EdgeLineExtractionHeadless -print -quit)
M=$(find $BT/src/build -type f -name MeshPreprocessingHeadless -print -quit)
[ -n "$E" ] && [ -n "$M" ] || { echo "[RUN] FATAL binaries not found"; exit 5; }
cp -f $E $RUN/bin/edge/EdgeLineExtractionHeadless; cp -f $M $RUN/bin/mesh/MeshPreprocessingHeadless
chmod +x $RUN/bin/edge/EdgeLineExtractionHeadless $RUN/bin/mesh/MeshPreprocessingHeadless
EDGE=$RUN/bin/edge/EdgeLineExtractionHeadless
MESH=$RUN/bin/mesh/MeshPreprocessingHeadless
EDGE_MD5=$(md5_of $EDGE); MESH_MD5=$(md5_of $MESH)
echo "[RUN] edge $EDGE_MD5"; echo "[RUN] mesh $MESH_MD5"
printf '{"commit": "%s", "edge_md5": "%s", "mesh_md5": "%s", "jobid": "%s", "pot": "%s"}\n' \
    "$COMMIT" "$EDGE_MD5" "$MESH_MD5" "$SLURM_JOB_ID" "$POT" > $RUN/out/build.json

# ---- every active piece of this pot ----
: > $RUN/out/pieces_run.tsv; : > $RUN/out/classify.tsv
NPIECE=0
while read -r P; do
  [ -n "$P" ] || continue
  NPIECE=$((NPIECE + 1))
  ST=$RUN/stage/$P
  LOG=$RUN/out/logs/${P}.log
  : > "$LOG"
  echo "[RUN] ==== $P pot=$POT stage=$ST" | tee -a "$LOG"
  bash "$RUN/scripts/stage_piece.sh" "$ST" "$POT" "$P" >> "$LOG" 2>&1; SS=$?
  echo "[RUN] stage exit=$SS" | tee -a "$LOG"
  [ $SS -eq 0 ] || { echo "[RUN] FATAL STAGE_FAILED $P"; exit 6; }
  MESHOBJ=$(readlink -f "$ST/Dataset/Mesh/$POT/${P}_Mesh.obj")
  AXISSTAGED="$ST/Dataset/Axes/${P}_Axis.xyz"
  [ -f "$AXISSTAGED" ] || { echo "[RUN] FATAL AXIS_MISSING $P"; exit 7; }
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$AXISSTAGED" "$MESH" ) >> "$LOG" 2>&1; MS=$?
  echo "[RUN] mesh exit=$MS axis=$AXISSTAGED" | tee -a "$LOG"
  [ $MS -eq 0 ] || { echo "[RUN] FATAL MESH_FAILED $P exit=$MS"; exit 8; }
  CLS=$(grep -m1 "PAPER-234] classify: face0" "$LOG" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOG" || true)
  if [ -z "$CLS" ]; then echo "[RUN] FATAL CLASSIFY_MISSING $P -- SFS_AXIS_FILE was not read (ticket 277)"; exit 9; fi
  THETA=$(grep -m1 "PAPER-234] paper grow" "$LOG" | sed "s/.*thetaDeg=//; s/ .*//")
  echo "[RUN] $P theta=$THETA" | tee -a "$LOG"
  echo "[RUN] $P classify: $CLS | $SW" | tee -a "$LOG"
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_0.xyz" $RUN/out/geom/${P}.S0.xyz || { echo "[RUN] FATAL SURFACE0_MISSING $P"; exit 10; }
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_1.xyz" $RUN/out/geom/${P}.S1.xyz || { echo "[RUN] FATAL SURFACE1_MISSING $P"; exit 10; }
  rm -rf "$ST/Dataset/Breaklines/$POT"; mkdir -p "$ST/Dataset/Breaklines/$POT"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGE" ) >> "$LOG" 2>&1; ES=$?
  echo "[RUN] edge exit=$ES" | tee -a "$LOG"
  [ $ES -eq 0 ] || { echo "[RUN] FATAL EDGE_FAILED $P exit=$ES"; exit 11; }
  for K in 0 1; do
    cp -f "$ST/Dataset/Breaklines/$POT/${P}_Breakline_${K}.pcd" $RUN/out/geom/${P}.Bl${K}.pcd 2>/dev/null \
      || { echo "[RUN] FATAL EXPORT_MISSING $P Breakline_${K}"; exit 12; }
  done
  printf "%s\t%s\t%s\t%s\n" "$P" "$POT" "$THETA" "$MESHOBJ" >> $RUN/out/pieces_run.tsv
  printf "%s\t%s\t%s\t%s\n" "$P" "$CLS" "$SW" "$THETA" >> $RUN/out/classify.tsv
done < $PIECES
echo "[RUN] pieces run: $(wc -l < $RUN/out/pieces_run.tsv) of $NPIECE; classify lines: $(wc -l < $RUN/out/classify.tsv) of $NPIECE"

# ---- md5 of every input and every exported file this bundle is judged on ----
: > $RUN/out/files.md5
while read -r P; do
  [ -n "$P" ] || continue
  for f in $RUN/out/geom/${P}.S0.xyz $RUN/out/geom/${P}.S1.xyz $RUN/out/geom/${P}.Bl0.pcd $RUN/out/geom/${P}.Bl1.pcd; do
    printf "%s\t%s\t%s bytes\n" "$(md5_of $f)" "$f" "$(stat -c %s $f)" >> $RUN/out/files.md5
  done
  for f in "$CORP/Axes/${P}_Axis.xyz" "$CORP/Surfaces/${P}_Surface_0.xyz" "$CORP/Surfaces/${P}_Surface_1.xyz"; do
    printf "%s\t%s\t%s bytes\n" "$(md5_of "$f")" "$f" "$(stat -c %s "$f")" >> $RUN/out/files.md5
  done
  for f in "$CORP/Mesh/${P}_Mesh.obj" "$CORP/Mesh/${P}_Mesh_DS.obj" "$CORP/Point/$POT/${P}_Point.pcd"; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5_of "$f")" "$f" "$(stat -c %s $f)" >> $RUN/out/files.md5
  done
done < $PIECES
echo "[RUN] files.md5 rows: $(wc -l < $RUN/out/files.md5)"
echo "[RUN] geometry in out/geom: $(ls -1 $RUN/out/geom | wc -l) files, $(du -sh $RUN/out/geom | cut -f1) -- KEPT (deliverable)"

rm -rf $BT
echo "[RUN] done $(date -Is); stage trees kept until both assembly arms of $POT are read"
