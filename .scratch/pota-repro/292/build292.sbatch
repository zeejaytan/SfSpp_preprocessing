#!/usr/bin/env bash
#SBATCH --job-name=p292build
#SBATCH --time=00:40:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/slurm-%j.out
# Ticket 292 job A: build both binaries from git archive of THIS ticket commit, then
# write the 148-piece list, precheck it, and snapshot the corpus cloud md5s.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
COMMIT=787c149a3e5b8e4b23093746677b7842452e9316
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

mkdir -p $RUN/logs $RUN/out $RUN/out/logs $RUN/out/lanes $RUN/out/png $RUN/out/tiles \
         $RUN/out/status $RUN/out/errors $RUN/out/recheck $RUN/out/deleted $RUN/bin/edge $RUN/bin/mesh $RUN/scripts

echo "[BUILD] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT"

# ---- source archive of the ticket commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
if ! git -C $CANON cat-file -e $COMMIT^{commit}; then echo "[BUILD] FATAL commit $COMMIT not in $CANON"; exit 2; fi
BT=$BUILDROOT/p292-build-$SLURM_JOB_ID
rm -rf $BT; mkdir -p $BT/src
git -C $CANON archive $COMMIT | tar -x -C $BT/src
cp -a $CANON/alglib $BT/src/alglib
echo "[BUILD] archived $(find $BT/src -type f | wc -l) files into $BT/src"

md5_of() { md5sum "$1" | awk '{print $1}'; }
for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp; do
  printf '%s\t%s\t%s lines\n' "$f" "$(md5_of $BT/src/$f)" "$(wc -l < $BT/src/$f)" >> $RUN/out/source.md5
done
grep -c "SEED-287" $BT/src/edgeline_extraction_headless.cpp >> $RUN/out/source.md5
echo "[BUILD] local edits check: $(find $BT/src -maxdepth 1 -name '*.cpp' -newer $BT/src/CMakeLists.txt | wc -l) cpp newer than CMakeLists.txt (0 expected)"

# ---- build inside the pinned container ----
mkdir -p $BT/src/build; cd $BT/src/build
$APT exec --bind /data:/data $SIF cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON .. > $RUN/logs/cmake.log 2>&1
CMAKE_EXIT=$?
echo "[BUILD] cmake exit=$CMAKE_EXIT"
if [ $CMAKE_EXIT -ne 0 ]; then tail -20 $RUN/logs/cmake.log; exit 3; fi
$APT exec --bind /data:/data $SIF make -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless > $RUN/logs/make.log 2>&1
MAKE_EXIT=$?
echo "[BUILD] make exit=$MAKE_EXIT"
if [ $MAKE_EXIT -ne 0 ]; then tail -40 $RUN/logs/make.log; exit 4; fi

E=$(find $BT/src/build -type f -name EdgeLineExtractionHeadless | head -1)
M=$(find $BT/src/build -type f -name MeshPreprocessingHeadless | head -1)
if [ -z "$E" ] || [ -z "$M" ]; then echo "[BUILD] FATAL binaries not found"; exit 5; fi
cp -f $E $RUN/bin/edge/EdgeLineExtractionHeadless
cp -f $M $RUN/bin/mesh/MeshPreprocessingHeadless
chmod +x $RUN/bin/edge/EdgeLineExtractionHeadless $RUN/bin/mesh/MeshPreprocessingHeadless
EDGE_MD5=$(md5_of $RUN/bin/edge/EdgeLineExtractionHeadless)
MESH_MD5=$(md5_of $RUN/bin/mesh/MeshPreprocessingHeadless)
echo "[BUILD] edge $EDGE_MD5 built from $E"
echo "[BUILD] mesh $MESH_MD5 built from $M"

$PY - <<PYEOF >> $RUN/out/build.json
import json, subprocess
print(json.dumps({"commit": "$COMMIT", "node": "$(hostname)", "job": "$SLURM_JOB_ID",
  "edge_md5": "$EDGE_MD5", "mesh_md5": "$MESH_MD5",
  "edge_source_md5": open("$RUN/out/source.md5").read().split()[1],
  "built_at": "$(date -Is)", "cmake_exit": $CMAKE_EXIT, "make_exit": $MAKE_EXIT}, indent=1))
PYEOF

# ---- scripts the array reuses, copied from the same archive (record, not geometry) ----
cp -f $BT/src/.scratch/pota-repro/292/score292.py $RUN/scripts/score292.py
cp -f $BT/src/scripts/stage_piece.sh $RUN/scripts/stage_piece.sh
echo "[BUILD] score292.py $(md5_of $RUN/scripts/score292.py) stage_piece.sh $(md5_of $RUN/scripts/stage_piece.sh)"

# ---- piece list: one line per corpus cloud, sorted ----
{ awk -F'\t' 'NR>1 && $2 ~ /_Piece_/ {print $2}' $CORP/Point/MANIFEST_released.tsv
  awk -F'\t' 'NR>1 && $1 ~ /_Piece_/ {print $1}' $CORP/Point/MANIFEST_derived.tsv; } | sort -u > $RUN/out/pieces.tsv
NP=$(wc -l < $RUN/out/pieces.tsv)
echo "[BUILD] pieces=$NP (148 expected)"

# ---- precheck every piece: cloud, mesh (plain or _DS), axis, both author breaklines ----
: > $RUN/out/precheck.txt
while read -r P; do
  [ -n "$P" ] || continue
  POT=${P%%_Piece_*}
  C=$CORP/Point/$POT/${P}_Point.pcd
  [ -f "$C" ] || echo "MISSING cloud $P" >> $RUN/out/precheck.txt
  M=""
  for cand in $CORP/Mesh/$POT/${P}_Mesh.obj $CORP/Mesh/${P}_Mesh.obj $CORP/Mesh/$POT/${P}_Mesh_DS.obj $CORP/Mesh/${P}_Mesh_DS.obj; do
    [ -f "$cand" ] && M=$cand && break
  done
  [ -n "$M" ] || echo "MISSING mesh $P" >> $RUN/out/precheck.txt
  [ -f $CORP/Axes/${P}_Axis.xyz ] || echo "MISSING axis $P" >> $RUN/out/precheck.txt
  for K in 0 1; do
    [ -f $CORP/Breaklines/${P}_Breakline_${K}.pcd ] || echo "MISSING author lane $P $K" >> $RUN/out/precheck.txt
  done
done < $RUN/out/pieces.tsv
echo "[BUILD] precheck problems: $(wc -l < $RUN/out/precheck.txt) (0 expected)"

# ---- corpus snapshot: md5 of every staged cloud, before the array ----
: > $RUN/out/corpus_before.md5
while read -r P; do
  POT=${P%%_Piece_*}
  echo $CORP/Point/$POT/${P}_Point.pcd
done < $RUN/out/pieces.tsv > $RUN/out/cloud_paths.txt
xargs -a $RUN/out/cloud_paths.txt -P 8 -n 1 md5sum | sort -k2 > $RUN/out/corpus_before.md5
echo "[BUILD] corpus_before rows=$(wc -l < $RUN/out/corpus_before.md5)"

# ---- the build tree is source plus objects, not record: delete it ----
rm -rf $BT
echo "[BUILD] removed build tree $BT"
echo "[BUILD] done $(date -Is)"