#!/bin/bash
#SBATCH --job-name=t69C-pota-seat
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit69c.sbatch -- ticket 69 Part C: the Pot A seating control, DENSITY ONLY.
#
# Two arms, SAME harness, SAME patch, SAME surfaces, SAME axes, SAME floor 50; the only
# difference is the lane set, and both lane sets come from ONE preprocessing job (job 5),
# where one mesh stage fed two edge stages. So this is a paired test of density alone.
#   POTA18  Pot A lanes at sphere 1.8 / resample 1.9   (shipped)
#   POTA09  Pot A lanes at sphere 0.9 / resample 0.95  (densified)
# Surfaces, axes, meshes and ground truth are the CORPUS files for both arms (the same ones the
# t67 PACTL control read), so the lane set is the ONLY difference.
# Gate: each arm must be 8/8 pieces and 15/15 joins in '1. Acc.txt'. Arm POTA18 is the
# in-harness control; the t67 PACTL reading (8/8, 15/15) is the cross-harness one.
#
# A third arm rides along, because it costs seconds and answers lead input 5:
#   JUG09F50  the nine Juglet lanes at 0.9 mm (t68's D2X geom) with the SHIPPED floor 50,
#             shipped (old) Juglet axes -- i.e. 2x density ALONE, no axis change, no floor change.
#             At 1.8 mm only 2 of 9 lanes clear 50 dots; at 0.9 mm 8 of 9 do (P9 is 49).
#
# The assembler is the pristine tree at cc1d859 (what every t66/t67/t68 arm ran) with the
# canonical guard68.patch -- the empty ext_state_ guard in StateManager::Initialize -- applied
# to a git-archive COPY, exactly as guard68's submit did. The patch is what keeps the batch
# from segfaulting on an empty state vector; it changes no geometry and no scoring.
# Submitted FROM the run directory with --export=ALL,NEW=<sha>,PREV=<preprocessing run dir>.
set -uo pipefail

: "${NEW:?}" "${PREV:?}"
RUN=$SLURM_SUBMIT_DIR
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CORP=$MAIN/original_samples/SfS_pp
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
COMMIT=cc1d859
WORK=$RUN/work
SRC=$WORK/src
OUT=$RUN/out
TREES=$RUN/trees
LOG=$RUN/logs
INS=$RUN/instruments
JOBID=${SLURM_JOB_ID:-na}

fail() { local rc=$1; shift; { echo "jobid=$JOBID"; echo "commit=$NEW"; echo "rc=$rc"; echo "reason: $*"; date -u +'at %Y-%m-%dT%H:%M:%SZ'; } > "$RUN/RUN-FAILED.txt"; echo "[C69] FATAL rc=$rc $*"; exit "$rc"; }
mkdir -p "$WORK/inc1/class" "$WORK/inc2/class" "$WORK/shim" "$WORK/logs" "$WORK/build" "$SRC" "$OUT" "$TREES" "$LOG" "$INS"
echo "[C69] job=$JOBID host=$(hostname) start=$(date -u +%FT%TZ)"

# ---------- instruments from the pushed commit ----------
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
git -C "$CANON" fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*' > "$LOG/fetch.log" 2>&1 || true
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" > /dev/null || fail 2 "commit $NEW not in $CANON"
ISRC=$RUN/instrsrc; rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage69 | tar -x -C "$ISRC" || fail 3 "archive of ticket-69 instruments failed"
for f in stage69_inputs.py stage69_piece.sh geomid69.py; do
  cp -f "$ISRC/.scratch/juglet-breaklines/stage69/$f" "$INS/" || fail 3 "$f missing from the pushed commit"
done
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"

# ---------- the ticket-68 guard instruments, copied read-only from that run's guard dir ----------
G68=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method/guard68/instruments
[ -f "$G68/guard68.patch" ] || fail 3 'guard68.patch not found at $G68'
[ -f "$G68/arm67.sh" ] || fail 3 'arm67.sh not found at $G68'
cp -f "$G68/guard68.patch" "$INS/guard68.patch"
cp -f "$G68/arm67.sh" "$INS/arm67.sh"
md5sum "$INS/guard68.patch" "$INS/arm67.sh" > "$LOG/instruments.md5"
cat "$LOG/instruments.md5"

# ---------- the assembler source, patched ----------
git -C $MAIN/sfspreproc-docker archive $COMMIT | tar x -C $SRC || fail 4 'assembler archive failed'
[ -f "$SRC/class/ranking_system.cpp" ] || fail 4 'assembler archive empty'
# guard68.patch was cut against a CRLF checkout; the blobs are LF, so strip CR before applying
tr -d '\r' < "$INS/guard68.patch" > "$WORK/guard68.lf.patch"
( cd "$SRC" && git init -q && git add -A && git -c user.email=t69@local -c user.name=t69 commit -qm "archive $COMMIT" && git apply --check "$WORK/guard68.lf.patch" && git apply "$WORK/guard68.lf.patch" ) >> "$LOG/apply.log" 2>&1
ARC=$?
echo "[C69] patch apply rc=$ARC (see logs/apply.log)"
[ "$ARC" -eq 0 ] || fail 4 "git apply failed rc=$ARC"
grep -n 'ext_state_.empty()' "$SRC/class/ranking_system.cpp" | head -3 >> "$LOG/apply.log" 2>&1 || true
cp "$SRC/hpc/tools/main_pristine_batch.cpp" "$WORK/shim/P.cpp" || fail 4 'shim source missing'

# ---------- arm script: arm67.sh with the patched copy in place of /opt/sfs-pristine ----------
sed -e 's|/opt/sfs-pristine|/src|g' "$INS/arm67.sh" > "$WORK/arm68g.sh"
chmod +x "$WORK/arm68g.sh"

# ---------- include roots ----------
$APT exec $SIF cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc2/class/data_path.h" 2>>"$LOG/provenance.log" || fail 4 'cannot read the SIF data_path.h'
cp "$WORK/inc2/class/data_path.h" "$WORK/inc1/class/data_path.h"
# inc1 = the Juglet dataset block (t58/t67 recipe): POT_A renamed out of the way, then the
# Juglet block appended so the tree can be mounted as Dataset/SfS_pp
cp -f "$G68/juglet_orig_block.inc" "$INS/juglet_orig_block.inc" || fail 3 "juglet_orig_block.inc missing from $G68"
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' "$WORK/inc1/class/data_path.h"
grep -q "POT_A_INFRA_OFF_JUGLET" "$WORK/inc1/class/data_path.h" || fail 3 "the POT_A rename did not apply to inc1"
cat "$INS/juglet_orig_block.inc" >> "$WORK/inc1/class/data_path.h"
grep -c "JUGLET_ORIG_BASE" "$WORK/inc1/class/data_path.h" > "$LOG/inc1.log" 2>&1 || true
cat "$LOG/inc1.log"

# ---------- cold build ----------
$APT exec --bind $SRC:/src --bind $WORK:/panel $SIF bash -c 'cd /panel/build && cmake /src -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1 && make -j8 > /panel/logs/make.log 2>&1'
BRC=$?
echo "[C69] cold build rc=$BRC"
[ "$BRC" -eq 0 ] || { tail -30 "$WORK/logs/make.log" 2>/dev/null; fail 5 'assembler build failed'; }
md5sum $WORK/build/Hierarchy-Clear > "$LOG/md5_clear.txt"
cat "$LOG/md5_clear.txt"

# ---------- stage the two Pot A trees ----------
for G in 18 09; do
  GD=$PREV/out_pota/geom$G
  [ -d "$GD" ] || fail 6 "preprocessing geom dir missing: $GD"
  T=$TREES/pota$G
  $PY "$INS/stage69_inputs.py" --geom "$GD" --pot Pot_A --pieces "Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08" --out "$T" --mesh-dir "$CORP/Mesh" --axis-dir "$DS/Axes/Pot_A" --surfaces-dir "$CORP/Surfaces" --gt-dir "$CORP/Ground Truth" --gt-graph "$CORP/Ground Truth/Pot_A_simple_graph.txt" > "$LOG/stage_$G.log" 2>&1 \
    || { tail -5 "$LOG/stage_$G.log"; fail 6 "staging pota$G failed"; }
  echo "[C69] tree pota$G staged: $(ls $T/Breaklines | wc -l) lanes, $(ls $T/Surfaces | wc -l) surfaces"
  { echo "--- pota$G lanes"; for f in "$T/Breaklines"/*.pcd; do printf '%s %s %s\n' "$(basename $f)" "$(md5sum $f | cut -d' ' -f1)" "$(grep -am1 '^POINTS' $f | awk '{print $2}')"; done; } >> "$LOG/lanes.tsv"
done
# the Juglet arm: lanes from t68's 0.9 mm cell, shipped (old) Juglet axes, shipped floor 50
JG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1546_6761aed_t68-densify2x/outD2X/geom
[ -d "$JG" ] || fail 6 "Juglet 0.9 mm geom missing: $JG"
JGP="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
$PY "$INS/stage69_inputs.py" --geom "$JG" --pot Juglet --pieces "$JGP" --out "$TREES/jug09" --mesh-dir "$DS/Mesh/Juglet" --axis-dir "$DS/Axes/Juglet" --gt-dir "$DS/Juglet_GT" --gt-graph "$DS/Juglet_GT/Juglet_simple_graph.txt" > "$LOG/stage_jug09.log" 2>&1 \
  || { tail -5 "$LOG/stage_jug09.log"; fail 6 "staging jug09 failed"; }
echo "[C69] tree jug09 staged: $(ls $TREES/jug09/Breaklines | wc -l) lanes"
{ echo "--- jug09 lanes"; for f in "$TREES/jug09/Breaklines"/*.pcd; do printf '%s %s %s\n' "$(basename $f)" "$(md5sum $f | cut -d' ' -f1)" "$(grep -am1 '^POINTS' $f | awk '{print $2}')"; done; } >> "$LOG/lanes.tsv"
cat "$LOG/lanes.tsv"

# ---------- two arms, floor 50 ----------
printf 'arm\tfloor\ttree\texit\twall_s\n' > "$LOG/panel.tsv"
runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  local T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $SRC:/src --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm68g.sh "$ARM" "$FLOOR" "$INC" "$NP" "$EXTRA" /panel/shim/P.cpp >> "$LOG/panel.log" 2>&1
  local RC=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$TREE" "$RC" "$((SECONDS - T0))" >> "$LOG/panel.tsv"
  echo "##### $ARM exit=$RC wall=$((SECONDS - T0))s"
}
runarm POTA18 50 /panel/inc2 $TREES/pota18 8 NONE
runarm POTA09 50 /panel/inc2 $TREES/pota09 8 NONE
runarm JUG09F50 50 /panel/inc1 $TREES/jug09 9 -DJUGLET_ORIG
cp "$WORK"/logs/* "$LOG"/ 2>/dev/null || true
md5sum $WORK/build/Hierarchy-* > "$LOG/md5_binaries.txt" 2>/dev/null || true
cat "$LOG/panel.tsv"

# ---------- read the gate ----------
printf 'arm\tpieces_seated\tjoins_seated\tacc_file\n' > "$LOG/gate.tsv"
for A in POTA18 POTA09 JUG09F50; do
  ACC="$OUT/$A/1. Acc.txt"
  P0=$(grep -aom1 '[0-9]*/[0-9]*' "$ACC" 2>/dev/null | head -1)
  J0=$(grep -ao '[0-9]*/[0-9]*' "$ACC" 2>/dev/null | sed -n 2p)
  printf '%s\t%s\t%s\t%s\n' "$A" "${P0:-none}" "${J0:-none}" "$ACC" >> "$LOG/gate.tsv"
  echo "[$A] Acc.txt: $(tr '\n' ' ' < "$ACC" 2>/dev/null | head -c 200)"
done
cat "$LOG/gate.tsv"
# ---------- Part D proof: unset vs explicit 1.8/1.9, geometry columns ----------
# Job 5 compared FULL-FILE md5 and got "identical no" even though the two edge logs differ only
# by the two env print lines and the timing lines. The reason is the seventh column: the lane PCD
# writes curvature from uninitialised memory (t68 measured the same thing: identical geometry,
# 1.1e+23 vs 1.5e-37 in column 7). So identity has to be measured on the GEOMETRY columns.
# This section re-runs the pair on ONE staged surface pair with job 5 binaries and compares
# (a) full-file md5, (b) md5 of columns 1-6, (c) the largest nearest-dot distance.
if [ -x "$PREV/bin-EdgeLineExtractionHeadless" ] && [ -x "$PREV/bin-MeshPreprocessingHeadless" ]; then
  PR=$RUN/proofgeom; rm -rf "$PR"; mkdir -p "$PR"
  PS=$PR/stage_Pot_A_Piece_01
  MESH_DIR_69=$CORP/Mesh bash "$INS/stage69_piece.sh" "$PS" Pot_A Pot_A_Piece_01 "$CORP/Axes/Pot_A_Piece_01_Axis.xyz" "$CORP/Point/Pot_A/Pot_A_Piece_01_Point.pcd" REAL-RELEASED-CLOUD > "$PR/stage.log" 2>&1 || fail 7 "proofgeom staging failed"
  ( cd "$PS" && $APT exec --bind /data:/data "$SIF" env POT_NAME=Pot_A SFS_AXIS_FILE="$PS/Dataset/Axes/Pot_A_Piece_01_Axis.xyz" SFS_STATUS_FILE="$PR/status.tsv" $SHIPPED "$PREV/bin-MeshPreprocessingHeadless" ) > "$PR/mesh.log" 2>&1 || fail 7 "proofgeom mesh stage failed"
  pg_run () {
    local NAME=$1; shift
    # wipe BOTH the previous run's lanes and its Temp/Temp_edge scratch, so run 2 does not
    # start from run 1's leavings (the edge stage saves and reloads boundary.pcd there,
    # edgeline_extraction_headless.cpp:1269-1270)
    rm -rf "$PS/Dataset/Breaklines/Pot_A"; mkdir -p "$PS/Dataset/Breaklines/Pot_A"
    rm -rf "$PS/Temp/Temp_edge/Pot_A"; mkdir -p "$PS/Temp/Temp_edge/Pot_A"
    ( cd "$PS" && $APT exec --bind /data:/data "$SIF" env POT_NAME=Pot_A "$@" "$PREV/bin-EdgeLineExtractionHeadless" ) > "$PR/edge_$NAME.log" 2>&1
    mkdir -p "$PR/$NAME"
    for K in 0 1; do cp -f "$PS/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_$K.pcd" "$PR/$NAME/Bl$K.pcd" 2>/dev/null || true; done
    echo "[PG] $NAME rc=$? env=[$*]"
  }
  pg_run unset
  pg_run explicit SFS_SPHERE_RADIUS_MM=1.8 SFS_RESAMPLE_D_MM=1.9
  printf "lane\tdots_unset\tdots_explicit\tgeom_md5_unset\tgeom_md5_explicit\tidentical\tmax_nn_mm\n" > "$PR/proofgeom.tsv"
  for K in 0 1; do
    U=$PR/unset/Bl$K.pcd; E=$PR/explicit/Bl$K.pcd
    if [ ! -f "$U" ] || [ ! -f "$E" ]; then
      printf "Bl%s\tabsent\tabsent\t-\t-\tno\t-\n" "$K" >> "$PR/proofgeom.tsv"; continue
    fi
    ROW=$($PY "$INS/geomid69.py" "$U" "$E") || fail 7 "geomid69.py failed on Bl$K"
    printf "Bl%s\t%s\n" "$K" "$ROW" >> "$PR/proofgeom.tsv"
    echo "[PG] Bl$K $ROW"
  done
  cat "$PR/proofgeom.tsv"
  rm -rf "$PS"
else
  echo "[PG] skipped: job 5 binaries not found under $PREV"
fi

echo "=== t69c job finished $(date -u +%FT%TZ)"