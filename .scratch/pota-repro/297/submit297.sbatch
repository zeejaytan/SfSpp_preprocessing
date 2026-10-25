#!/usr/bin/env bash
#SBATCH --job-name=p297chord
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
# Ticket 297 -- Pot D 22 Bl0: is the authors' chord the better break edge?
#
# Builds both binaries from the git archive of this ticket's commit, then runs Pot D 22's mesh and
# edge stages THREE times at the shipped defaults, changing nothing: the three repeats exist to
# measure the piece's own run-to-run spread, because the mesh stage draws 30 random ray-cast points
# from an unseeded generator (mesh_processing_headless.cpp:1526-1527) -- a gate compared against
# zero would be comparing against an assumption.  SFS_AXIS_FILE is set for the mesh stage (ticket
# 277: without it the stage keeps size order silently and Bl0/Bl1 swap).  Then the five
# measurements of the ticket and the one picture, then the staged geometry is deleted.
set -uo pipefail

: "$RUN_DIR"
RUN=$RUN_DIR
COMMIT=\${SOURCE_COMMIT:-0f8a4a417221647e7d6e7f7d031a90109930d44d}
CANON=\${CANONICAL:-/data/gpfs/projects/punim2657/sfs_preprocessing}
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
PIECE=Pot_D_Piece_22
POT=Pot_D
LANE=0
EXPECT_EDGE=a28d10afab2b50bbe750d599ee2b7214

unset NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out $RUN/out/logs $RUN/out/geom $RUN/out/png $RUN/bin/edge $RUN/bin/mesh $RUN/scripts $RUN/stage
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT"
echo "[RUN] SFS_ variables already in this environment: $(env | grep -cE '^SFS_') (0 expected)"

# ---- build both binaries from the archive of this ticket's commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e $COMMIT^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p297-build-$SLURM_JOB_ID
rm -rf $BT; mkdir -p $BT/src
git -C $CANON archive $COMMIT | tar -x -C $BT/src
cp -a $CANON/alglib $BT/src/alglib
echo "[RUN] archived $(find $BT/src -type f | wc -l) files into $BT/src"
md5_of() { md5sum "$1" | awk '{print $1}'; }
: > $RUN/out/source.md5
for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of $BT/src/$f)" "$(wc -l < $BT/src/$f)" >> $RUN/out/source.md5
done
echo "[RUN] local edits: $(find $BT/src -maxdepth 1 -name '*.cpp' -newer $BT/src/CMakeLists.txt | wc -l) cpp newer than CMakeLists.txt (0 expected)"
cp -f $BT/src/.scratch/pota-repro/292/score292.py $RUN/scripts/score292.py
cp -f $BT/src/.scratch/pota-repro/297/measure297.py $RUN/scripts/measure297.py
cp -f $BT/src/.scratch/pota-repro/297/render297.py $RUN/scripts/render297.py
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
if [ "$EDGE_MD5" = "$EXPECT_EDGE" ]; then
  echo "[RUN] edge binary md5 matches ticket 294's (the instrument is the same binary)"
else
  echo "[RUN] WARNING edge binary md5 $EDGE_MD5 differs from ticket 294's $EXPECT_EDGE -- say so in the ticket"
fi
printf '{"commit": "%s", "edge_md5": "%s", "mesh_md5": "%s", "jobid": "%s", "expect_edge_md5": "%s", "edge_md5_matches_294": %s}\n' \
  "$COMMIT" "$EDGE_MD5" "$MESH_MD5" "$SLURM_JOB_ID" "$EXPECT_EDGE" \
  "$([ "$EDGE_MD5" = "$EXPECT_EDGE" ] && echo true || echo false)" > $RUN/out/build.json

# ---- the inputs that are not ours: the authors' line and their mesh (frozen corpus, read-only) ----
cp -f $CORP/Breaklines/\${PIECE}_Breakline_\${LANE}.pcd $RUN/out/geom/authors.Bl0.pcd
{ md5sum $CORP/Breaklines/\${PIECE}_Breakline_\${LANE}.pcd
  md5sum $CORP/Mesh/\${PIECE}_Mesh_DS.obj
  md5sum $CORP/Surfaces/\${PIECE}_Surface_0.xyz
  md5sum $CORP/Surfaces/\${PIECE}_Surface_1.xyz
  md5sum $CORP/Axes/\${PIECE}_Axis.xyz ; } > $RUN/out/inputs.authors.md5
cat $RUN/out/inputs.authors.md5

# ---- three repeats of the same thing: mesh stage, edge stage, score ----
: > $RUN/out/scores.tsv
: > $RUN/out/classify.tsv
for K in 1 2 3; do
  REP=rep$K
  ST=$RUN/stage/$REP
  LOG=$RUN/out/logs/$REP.log
  mkdir -p $RUN/out/geom/$REP
  : > "$LOG"
  echo "[RUN] ==== $REP start $(date -Is)" | tee -a "$LOG"
  bash $RUN/scripts/stage_piece.sh "$ST" "$POT" "$PIECE" >> "$LOG" 2>&1; SS=$?
  echo "[RUN] $REP stage exit=$SS" | tee -a "$LOG"
  [ $SS -eq 0 ] || { echo "[RUN] FATAL STAGE_FAILED $REP"; exit 7; }
  cp -f "$ST/inputs.md5" "$RUN/out/inputs.$REP.md5"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ST/Dataset/Axes/\${PIECE}_Axis.xyz" "$MESH" ) >> "$LOG" 2>&1
  echo "[RUN] $REP mesh exit=$?" | tee -a "$LOG"
  CLS=$(grep -m1 "PAPER-234] classify: face0" "$LOG" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOG" || true)
  if [ -z "$CLS" ]; then echo "[RUN] FATAL CLASSIFY_MISSING $REP -- SFS_AXIS_FILE was not read"; exit 6; fi
  THETA=$(grep -m1 "PAPER-234] paper grow" "$LOG" | sed "s/.*thetaDeg=//; s/ .*//")
  echo "[RUN] $REP theta=$THETA classify=$CLS" | tee -a "$LOG"
  printf "%s\t%s\t%s\t%s\n" "$REP" "$THETA" "$CLS" "$SW" >> $RUN/out/classify.tsv
  cp -f "$ST/Temp/Data/$POT/\${PIECE}_Surface_0.xyz" "$RUN/out/geom/$REP/ours.S0.xyz"
  cp -f "$ST/Temp/Data/$POT/\${PIECE}_Surface_1.xyz" "$RUN/out/geom/$REP/ours.S1.xyz"
  rm -rf "$ST/Dataset/Breaklines/$POT"; mkdir -p "$ST/Dataset/Breaklines/$POT"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGE" ) >> "$LOG" 2>&1
  echo "[RUN] $REP edge exit=$?" | tee -a "$LOG"
  for L in 0 1; do
    cp -f "$ST/Dataset/Breaklines/$POT/\${PIECE}_Breakline_\${L}.pcd" "$RUN/out/geom/$REP/ours.Bl$L.pcd"
  done
  "$PY" $RUN/scripts/score292.py "$POT" "$PIECE" "$LANE" "$RUN/out/geom/$REP/ours.Bl0.pcd" \
      "$RUN/out/geom/authors.Bl0.pcd" | sed "s/^/$REP\t/" >> $RUN/out/scores.tsv
done
echo "[RUN] scores (repeat, pot, piece, lane, n_ours, n_auth, median, cov_ours, cov_auth, jumps, max_step, len_ours, len_auth, at_bar):"
cat $RUN/out/scores.tsv
echo "[RUN] classify lines:"; cat $RUN/out/classify.tsv

# ---- the five measurements and the one picture ----
"$PY" $RUN/scripts/measure297.py $RUN rep1 rep2 rep3 > $RUN/logs/measure.log 2>&1; MEXIT=$?
echo "[RUN] measure exit=$MEXIT"
if grep -q "inside the repeats' range: True" $RUN/out/measure297.txt 2>/dev/null; then
  echo "[RUN] GATE PASS: ticket 294's row is inside this piece's own run-to-run spread"
else
  echo "[RUN] GATE WARNING: ticket 294's row is NOT inside this piece's own spread -- the ticket must say so"
fi
tail -60 $RUN/logs/measure.log
"$PY" $RUN/scripts/render297.py $RUN rep1 > $RUN/logs/render.log 2>&1; REXIT=$?
echo "[RUN] render exit=$REXIT"; cat $RUN/logs/render.log

# ---- keep the line files; delete the staged geometry, and say exactly what went ----
{
  echo "GEOMETRY_DELETED -- ticket 297, job $SLURM_JOB_ID, $(date -Is)"
  echo
  echo "The ticket keeps the two line files and one picture.  Everything below was removed:"
  for K in 1 2 3; do
    ST=$RUN/stage/rep$K
    [ -d "$ST" ] || continue
    printf "  %-28s symlinks %3s  real files %3s  real bytes %s\n" "stage/rep$K" \
      "$(find "$ST" -type l | wc -l)" "$(find "$ST" -type f | wc -l)" \
      "$(find "$ST" -type f -printf '%s\n' | awk '{s+=$1} END {print s+0}')"
  done
  echo "  (the symlinks point into the frozen corpus, which is unchanged: it is read-only to this job)"
  echo
  echo "KEPT -- this is what reproduces every number in the ticket, with the corpus mesh, the corpus"
  echo "authors' line and the corpus surfaces, all of which are permanent:"
  find $RUN/out/geom -type f -printf '  %-56p %8s bytes\n' | sort
  find $RUN/out/png -type f -printf '  %-56p %8s bytes\n' | sort
} > $RUN/out/GEOMETRY_DELETED.txt
rm -rf $RUN/stage
rm -f $RUN/out/geom/rep2/ours.S1.xyz $RUN/out/geom/rep3/ours.S1.xyz
rm -rf $BT
echo "[RUN] geometry deleted at $(date -Is); record in out/GEOMETRY_DELETED.txt"
echo "[RUN] done $(date -Is) measure=$MEXIT render=$REXIT"
