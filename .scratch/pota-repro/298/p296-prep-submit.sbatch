#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p296prep
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 296 run P (prep + Phase 0). Build both binaries from git archive of the ticket commit,
# run the shipped preprocessing chain on the 8 Pot A pieces -- mesh stage with SFS_AXIS_FILE set
# (the [PAPER-234] classify line is REQUIRED, ticket 277), edge stage at the shipped defaults --
# then measure Phase 0 on the staged bundle: which of our two surfaces is the physical interior,
# and which surface our Breakline_0 rides.  Nothing is tuned; no SFS_* variable overrides a default.
# Geometry stays until both assembly arms have been read (deleted afterwards, recorded).
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
COMMIT=3d5d5379175d0731dffa1f0edb186a848093508e
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

unset NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out $RUN/out/logs $RUN/out/geom $RUN/bin/edge $RUN/bin/mesh $RUN/scripts $RUN/stage
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_') (0 expected)"

# ---- build both binaries from the archive of the ticket commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e ${COMMIT}^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p296-build-$SLURM_JOB_ID
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
echo "[RUN] instrument (uploaded, not in the commit):" >> $RUN/out/source.md5
for f in p296_interior.py p295_q1.py p295_lib.py; do
  printf "instrument\t%s\t%s\n" "$f" "$(md5_of $RUN/scripts/$f)" >> $RUN/out/source.md5
done

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

# ---- the eight pieces ----
printf "%s\n" Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08 > $RUN/out/pieces.tsv
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
  AXISSTAGED="$ST/Dataset/Axes/${P}_Axis.xyz"
  [ -f "$AXISSTAGED" ] || { echo "[RUN] FATAL AXIS_MISSING $P"; exit 7; }
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$AXISSTAGED" "$MESH" ) >> "$LOG" 2>&1; MS=$?
  echo "[RUN] mesh exit=$MS axis=$AXISSTAGED" | tee -a "$LOG"
  CLS=$(grep -m1 "PAPER-234] classify: face0" "$LOG" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOG" || true)
  if [ -z "$CLS" ]; then echo "[RUN] FATAL CLASSIFY_MISSING $P -- SFS_AXIS_FILE was not read"; exit 6; fi
  THETA=$(grep -m1 "PAPER-234] paper grow" "$LOG" | sed "s/.*thetaDeg=//; s/ .*//")
  echo "[RUN] $P theta=$THETA" | tee -a "$LOG"
  echo "[RUN] $P classify: $CLS | $SW" | tee -a "$LOG"
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_0.xyz" $RUN/out/geom/${P}.S0.xyz || { echo "[RUN] SURFACE0_MISSING $P"; exit 8; }
  cp -f "$ST/Temp/Data/$POT/${P}_Surface_1.xyz" $RUN/out/geom/${P}.S1.xyz || { echo "[RUN] SURFACE1_MISSING $P"; exit 8; }
  rm -rf "$ST/Dataset/Breaklines/$POT"; mkdir -p "$ST/Dataset/Breaklines/$POT"
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGE" ) >> "$LOG" 2>&1; ES=$?
  echo "[RUN] edge exit=$ES" | tee -a "$LOG"
  for K in 0 1; do
    cp -f "$ST/Dataset/Breaklines/$POT/${P}_Breakline_${K}.pcd" $RUN/out/geom/${P}.Bl${K}.pcd 2>/dev/null || echo "[RUN] EXPORT_MISSING $P $K"
  done
  printf "%s\t%s\t%s\t%s\n" "$P" "$POT" "$THETA" "$MESHOBJ" >> $RUN/out/pieces_run.tsv
  printf "%s\t%s\t%s\t%s\n" "$P" "$CLS" "$SW" "$THETA" >> $RUN/out/classify.tsv
done < $RUN/out/pieces.tsv
echo "[RUN] pieces run: $(wc -l < $RUN/out/pieces_run.tsv) of 8; classify lines: $(wc -l < $RUN/out/classify.tsv) of 8"

# ---- md5 of every input and every exported file this run will be judged on ----
: > $RUN/out/files.md5
for P in $(cat $RUN/out/pieces.tsv); do
  for f in $RUN/out/geom/${P}.S0.xyz $RUN/out/geom/${P}.S1.xyz $RUN/out/geom/${P}.Bl0.pcd $RUN/out/geom/${P}.Bl1.pcd; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5_of $f)" "$f" "$(stat -c %s $f)" >> $RUN/out/files.md5
  done
  for f in "$CORP/Axes/${P}_Axis.xyz" "$CORP/Mesh/${P}_Mesh.obj" "$CORP/Surfaces/${P}_Surface_0.xyz" "$CORP/Surfaces/${P}_Surface_1.xyz"; do
    printf "%s\t%s\t%s bytes\n" "$(md5_of "$f")" "$f" "$(stat -c %s "$f")" >> $RUN/out/files.md5
  done
done
echo "[RUN] files.md5 rows: $(wc -l < $RUN/out/files.md5)"

# ---- Phase 0: which surface is the physical interior, and which surface Bl0 rides ----
$PY $RUN/scripts/p296_interior.py --ours $RUN/out/geom --authors-surf "$CORP/Surfaces" --authors-brk "$CORP/Breaklines" --out $RUN/out > $RUN/out/interior.log 2>&1
IEX=$?; echo "[RUN] interior exit=$IEX"
[ $IEX -eq 0 ] || tail -30 $RUN/out/interior.log
cat $RUN/out/q0_summary.txt 2>/dev/null || true

# the build tree is source plus objects, not record
rm -rf $BT
echo "[RUN] done $(date -Is); stage trees and out/geom KEPT for the two assembly arms"
