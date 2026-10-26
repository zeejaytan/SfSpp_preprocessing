#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p07prep
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 07 stage 1. Rebuild the Juglet preprocessing bundle from its nine
# staged meshes with the shipped chain, and rebuild Pot A in the SAME job as
# the positive control (the t14_patches 15/15 bar).
#
# Shipped defaults only. The only SFS_* variables this job sets are:
#   POT_NAME          -- picks Dataset/*/<pot>/ (data_path.h:46-53)
#   SFS_AXIS_FILE     -- mandatory for the [PAPER-234] classify vote (ticket 277)
#   SFS_SMOOTHNESS_DEG-- ONLY on the bounded cluster retries for a piece that
#                        fuses to one cluster: 4.5 (default) then 3.5 then 3.0.
#                        Lowering is the direction that splits a fused wall pair
#                        (ticket 12: at 25 deg Pot A fuses to one cluster).
#
# Why the Juglet needs two mesh passes: classifyAndOrderPaper234 runs at
# mesh_processing_headless.cpp:2190 BEFORE the surfaces are written (:2290),
# so no axis means no surfaces; PotSAC cannot be run until two walls exist.
# Pass 1 therefore uses a PCA bootstrap axis (out/boot/) whose only job is to
# satisfy that gate; its face labels are discarded. Pass 2 uses the PotSAC axis
# from sfs_axes (today's axis code) computed over pass 1's two walls.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
COMMIT=d8af9d288214b1a72bfba69f8fb99a4ecf09d071
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DSET=$CANON/Dataset
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-07

unset NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out/geom $RUN/out/logs $RUN/out/axes $RUN/out/boot $RUN/bin/edge $RUN/bin/mesh $RUN/scripts $RUN/stage
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT"
echo "[RUN] SFS_ variables inherited from the environment: $(env | grep -cE '^SFS_') (0 expected)"
md5_of() { md5sum "$1" | awk '{print $1}'; }

# ---- frozen-corpus manifest BEFORE anything runs (criterion 6) ----
corpus_manifest() {
  : > "$1"
  local N P f
  for N in 1 2 3 4 5 6 7 8 9; do
    for f in "$DSET/Point/Juglet/Juglet_Piece_${N}_Point.pcd" \
             "$DSET/Mesh/Juglet/Juglet_Piece_${N}_Mesh.obj" \
             "$DSET/Mesh/Juglet/Juglet_Piece_0${N}_Mesh.obj" \
             "$DSET/Juglet/Piece0${N}.obj" \
             "$DSET/Axes/Juglet/Juglet_Piece_${N}_Axis.xyz"; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5_of "$f")" "$f" >> "$1"
    done
  done
  for N in 1 2 3 4 5 6 7 8; do
    P=$(printf "Pot_A_Piece_%02d" $N)
    for f in "$CORP/Axes/${P}_Axis.xyz" "$CORP/Mesh/${P}_Mesh.obj" \
             "$CORP/Point/Pot_A/${P}_Point.pcd" \
             "$CORP/Surfaces/${P}_Surface_0.xyz" "$CORP/Surfaces/${P}_Surface_1.xyz" \
             "$CORP/Breaklines/Pot_A/${P}_Breakline_0.pcd" "$CORP/Breaklines/Pot_A/${P}_Breakline_1.pcd"; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5_of "$f")" "$f" >> "$1"
    done
  done
}
corpus_manifest $RUN/out/corpus_md5_before.tsv
echo "[RUN] corpus files hashed before: $(wc -l < $RUN/out/corpus_md5_before.tsv)"

# ---- build both binaries from the archive of the ticket commit ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e ${COMMIT}^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p07-build-$SLURM_JOB_ID
rm -rf $BT; mkdir -p $BT/src
git -C $CANON archive $COMMIT | tar -x -C $BT/src
cp -a $CANON/alglib $BT/src/alglib
echo "[RUN] archived $(find $BT/src -type f | wc -l) files into $BT/src"
: > $RUN/out/source.md5
for f in edgeline_extraction_headless.cpp mesh_processing_headless.cpp data_path.h; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of $BT/src/$f)" "$(wc -l < $BT/src/$f)" >> $RUN/out/source.md5
done
cp -f $BT/src/scripts/stage_piece.sh $RUN/scripts/stage_piece.sh
echo "[RUN] instrument (uploaded to the run dir, not in the commit):" >> $RUN/out/source.md5
for f in stage_juglet.sh boot_axis.py potsac_axis.py; do
  printf "instrument\t%s\t%s\n" "$f" "$(md5_of $RUN/scripts/$f)" >> $RUN/out/source.md5
done

mkdir -p $BT/src/build; cd $BT/src/build
"$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. > $RUN/logs/cmake.log 2>&1
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
printf '{"commit": "%s", "edge_md5": "%s", "mesh_md5": "%s", "jobid": "%s"}\n' \
  "$COMMIT" "$(md5_of $EDGE)" "$(md5_of $MESH)" "$SLURM_JOB_ID" > $RUN/out/build.json

run_mesh() {  # <stage> <axis file inside stage> <smoothness | empty> <log>
  local ST=$1 AX=$2 SM=$3 LOG=$4
  if [ -n "$SM" ]; then
    ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Juglet SFS_AXIS_FILE="$AX" SFS_SMOOTHNESS_DEG="$SM" "$MESH" ) >> "$LOG" 2>&1
  else
    ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Juglet SFS_AXIS_FILE="$AX" "$MESH" ) >> "$LOG" 2>&1
  fi
}

# ================= the nine Juglet pieces =================
printf "piece\tattempt\tsmoothness_deg\tmesh_exit\tclusters\tsingle_cluster_lines\tsurface_0\tsurface_1\tlog\n" > $RUN/out/juglet_attempts.tsv
printf "piece\tstatus\tsmoothness_deg\tclusters\tclassify\tdecision\taxis\ttheta_deg\tbl0_dots\tbl1_dots\tnote\n" > $RUN/out/juglet_pieces.tsv

for N in 1 2 3 4 5 6 7 8 9; do
  P=Juglet_Piece_$N
  LOGP=$RUN/out/logs/$P.log; : > "$LOGP"
  echo "[RUN] ==== $P" | tee -a "$LOGP"

  BAX=$RUN/out/boot/${P}_boot_Axis.xyz
  $PY $RUN/scripts/boot_axis.py "$DSET/Point/Juglet/${P}_Point.pcd" > "$BAX" 2>> "$LOGP"
  BAXS=$?; echo "[RUN] $P bootstrap axis exit=$BAXS $(tr '\n' ' ' < "$BAX")" | tee -a "$LOGP"
  [ $BAXS -eq 0 ] || { echo "[RUN] BOOT_AXIS_FAILED $P"; continue; }

  chosen_sm=""; chosen_tag=""; chosen_stage=""; chosen_clusters=""; last_cl="none"; last_sc=0
  for SM in "" "3.5" "3.0"; do
    tag=${SM:-default}
    ST=$RUN/stage/$P/$tag
    LOG=$RUN/out/logs/${P}.attempt-$tag.log
    : > "$LOG"
    bash $RUN/scripts/stage_juglet.sh "$ST" "$N" "$BAX" >> "$LOG" 2>&1 || { echo "[RUN] STAGE_FAILED $P $tag" | tee -a "$LOG"; continue; }
    run_mesh "$ST" "$ST/Dataset/Axes/${P}_Axis.xyz" "$SM" "$LOG"; MS=$?
    CL=$(grep -m1 "Number of clusters is equal to" "$LOG" | sed "s/.*equal to //")
    SC=$(grep -c "Single cluster found (iteration" "$LOG")
    last_cl=${CL:-none}; last_sc=$SC
    S0=$ST/Temp/Data/Juglet/${P}_Surface_0.xyz; S1=$ST/Temp/Data/Juglet/${P}_Surface_1.xyz
    h0=no; h1=no; [ -s "$S0" ] && h0=yes; [ -s "$S1" ] && h1=yes
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$P" "$tag" "${SM:-4.5}" "$MS" "${CL:-none}" "$SC" "$h0" "$h1" "$LOG" >> $RUN/out/juglet_attempts.tsv
    echo "[RUN] $P attempt=$tag smoothness=${SM:-4.5} mesh_exit=$MS clusters=${CL:-none} single_cluster_lines=$SC S0=$h0 S1=$h1" | tee -a "$LOGP"
    if [ "$h0" = yes ] && [ "$h1" = yes ]; then chosen_sm=$SM; chosen_tag=$tag; chosen_stage=$ST; chosen_clusters=${CL:-none}; break; fi
  done

  if [ -z "$chosen_stage" ]; then
    printf "%s\tABSENT\t4.5/3.5/3.0\t%s\t-\t-\t-\t-\t-\t-\tno surface written at any of the three smoothness settings (last attempt: clusters=%s, single-cluster retry lines=%s); see out/juglet_attempts.tsv and out/logs/%s.attempt-*.log\n" "$P" "$last_cl" "$last_cl" "$last_sc" "$P" >> $RUN/out/juglet_pieces.tsv
    echo "[RUN] $P RESULT=ABSENT_NO_SURFACE" | tee -a "$LOGP"
    continue
  fi

  # today's axis code: PotSAC over the two walls this piece actually produced
  AX=$RUN/out/axes/${P}_Axis.xyz
  SFS_SRC=$BT/src $PY $RUN/scripts/potsac_axis.py --s0 "$chosen_stage/Temp/Data/Juglet/${P}_Surface_0.xyz" \
      --s1 "$chosen_stage/Temp/Data/Juglet/${P}_Surface_1.xyz" --out "$AX" --seed 0 --step 10 >> "$LOGP" 2>&1
  AXS=$?
  axsrc="potsac"
  if [ $AXS -ne 0 ] || [ ! -s "$AX" ]; then axsrc="bootstrap (PotSAC failed)"; cp -f "$BAX" "$AX"; fi
  echo "[RUN] $P axis=$axsrc exit=$AXS $(head -1 "$AX")" | tee -a "$LOGP"

  STF=$RUN/stage/$P/final
  LOGF=$RUN/out/logs/${P}.final.log; : > "$LOGF"
  bash $RUN/scripts/stage_juglet.sh "$STF" "$N" "$AX" >> "$LOGF" 2>&1 || { echo "[RUN] STAGE_FAILED $P final" | tee -a "$LOGF"; printf "%s\tSTAGE_FAILED\t%s\t%s\t-\t-\t%s\t-\t-\t-\tfinal staging failed\n" "$P" "$chosen_tag" "$chosen_clusters" "$axsrc" >> $RUN/out/juglet_pieces.tsv; continue; }
  run_mesh "$STF" "$STF/Dataset/Axes/${P}_Axis.xyz" "$chosen_sm" "$LOGF"; MS=$?
  CLS=$(grep -m1 "PAPER-234. classify: face0" "$LOGF" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOGF" || true)
  THETA=$(grep -m1 "PAPER-234. paper grow" "$LOGF" | sed "s/.*thetaDeg=//; s/ .*//")
  echo "[RUN] $P final mesh exit=$MS theta=$THETA" | tee -a "$LOGP"
  echo "[RUN] $P classify: $CLS | $SW" | tee -a "$LOGP"
  if [ -z "$CLS" ]; then echo "[RUN] CLASSIFY_MISSING $P (SFS_AXIS_FILE was not read)" | tee -a "$LOGP"; fi
  cp -f "$STF/Temp/Data/Juglet/${P}_Surface_0.xyz" $RUN/out/geom/${P}.S0.xyz || echo "[RUN] SURFACE0_MISSING $P"
  cp -f "$STF/Temp/Data/Juglet/${P}_Surface_1.xyz" $RUN/out/geom/${P}.S1.xyz || echo "[RUN] SURFACE1_MISSING $P"

  rm -rf "$STF/Dataset/Breaklines/Juglet"; mkdir -p "$STF/Dataset/Breaklines/Juglet"
  ( cd "$STF" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Juglet "$EDGE" ) >> "$LOGF" 2>&1; ES=$?
  echo "[RUN] $P edge exit=$ES" | tee -a "$LOGP"
  for K in 0 1; do
    cp -f "$STF/Dataset/Breaklines/Juglet/${P}_Breakline_${K}.pcd" $RUN/out/geom/${P}.Bl${K}.pcd 2>/dev/null || echo "[RUN] EXPORT_MISSING $P $K"
  done
  B0=$RUN/out/geom/${P}.Bl0.pcd; B1=$RUN/out/geom/${P}.Bl1.pcd
  d0=$([ -f "$B0" ] && grep -vc '^#' "$B0" || echo 0); d1=$([ -f "$B1" ] && grep -vc '^#' "$B1" || echo 0)
  DEC=$(echo "$SW" | grep -o "swapped\|kept" | head -1)
  printf "%s\tPRODUCED\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$P" "${chosen_sm:-4.5}" "$chosen_clusters" "$CLS" "$DEC" "$axsrc" "${THETA:-none}" "$d0" "$d1" "smoothness attempt=$chosen_tag; edge_exit=$ES" >> $RUN/out/juglet_pieces.tsv
  echo "[RUN] $P RESULT=PRODUCED decision=$DEC axis=$axsrc dots=Bl0:$d0 Bl1:$d1" | tee -a "$LOGP"
done
echo "[RUN] juglet rows: $(wc -l < $RUN/out/juglet_pieces.tsv)"

# ================= Pot A, same job, same settings (control) =================
printf "%s\n" Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08 > $RUN/out/pieces.tsv
: > $RUN/out/pieces_run.tsv; : > $RUN/out/classify.tsv
while read -r P <&3; do
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
  CLS=$(grep -m1 "PAPER-234. classify: face0" "$LOG" || true)
  SW=$(grep -m1 "classify: swapped\|classify: kept" "$LOG" || true)
  if [ -z "$CLS" ]; then echo "[RUN] FATAL CLASSIFY_MISSING $P -- SFS_AXIS_FILE was not read"; exit 6; fi
  THETA=$(grep -m1 "PAPER-234. paper grow" "$LOG" | sed "s/.*thetaDeg=//; s/ .*//")
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
done 3< $RUN/out/pieces.tsv
echo "[RUN] pot A pieces run: $(wc -l < $RUN/out/pieces_run.tsv) of 8; classify lines: $(wc -l < $RUN/out/classify.tsv) of 8"

# ---- md5 of every file this run will be judged on ----
: > $RUN/out/files.md5
for f in $(find $RUN/out/geom -type f | sort) $(find $RUN/out/axes -type f 2>/dev/null | sort) $(find $RUN/out/boot -type f 2>/dev/null | sort); do
  printf "%s\t%s\t%s bytes\n" "$(md5_of "$f")" "$f" "$(stat -c %s "$f")" >> $RUN/out/files.md5
done
echo "[RUN] files.md5 rows: $(wc -l < $RUN/out/files.md5)"

# ---- frozen-corpus manifest AFTER (criterion 6) ----
corpus_manifest $RUN/out/corpus_md5_after.tsv
if diff -q $RUN/out/corpus_md5_before.tsv $RUN/out/corpus_md5_after.tsv > /dev/null; then
  echo "[RUN] corpus md5 UNCHANGED ($(wc -l < $RUN/out/corpus_md5_after.tsv) files)" | tee $RUN/out/corpus_verdict.txt
else
  echo "[RUN] corpus md5 CHANGED -- see out/corpus_md5_diff.txt" | tee $RUN/out/corpus_verdict.txt
  diff $RUN/out/corpus_md5_before.tsv $RUN/out/corpus_md5_after.tsv > $RUN/out/corpus_md5_diff.txt
fi

# staged geometry stays: the run directory is the stage-2 input. Only the
# build tree goes.
rm -rf $BT
echo "[RUN] done $(date -Is); staged geometry and out/geom KEPT (stage 2 consumes this bundle)"
