#!/bin/bash
#SBATCH --job-name=t328p
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#
# Ticket 328, job D: rebuild with the plane-fit line normal and re-measure bars 1-3.
#   The edge-stage normal is now the smallest principal direction of a 3 mm disc of the
#   ridden wall (sign from the fitted surface normal), replacing the k=5 mean of the wall's
#   own vertex normals -- measured locally that mean is contaminated by the break face and
#   lowered every touching pair, while the 3 mm plane recovers the wall's orientation.
#   Cell gt_jug (GT axes) -> bars 1/2/3; ds_jug (shipped bad axis) -> bar 1.
#   new_pota / new_potc -> pot slot-0 decisions under the same rule (regression on pots).
#   326 harness on the cured tree -> bar 3 (before table copied from 326's run).
# Source: seeded by a copy of the previous run's extracted worktree (commits are forbidden),
# with the two patched files replaced; md5s recorded.
set -uo pipefail
: "${RUNID:?}" "${NEW:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t328-planenorm
PREV=$RUNS/20261110-2205_123f2ca_t328-wallside-short
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
GT=$DS/Juglet_GT
SIF=$CANON/pcl_191_nurbs.sif
SIFA=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T66=$RUNS/20261103-1332_fab76f5_t66-admitsign-default
T325=$RUNS/20261110-1640_22151d0_t325-juglet
T326=$RUNS/20261110-1844_6925cb0_t326-diag
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
POTA="Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
POTC="Pot_C_Piece_01"
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done

cd "$RUN" || exit 1
mkdir -p logs work out pins trees
fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"
  exit "$rc"
}
echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG src=$NEW host=$(hostname) start=$(date -u +%FT%TZ)"

corpus_list() {
  local out=$1
  { echo "## $DS"; ls -laR "$DS" | head -500
    echo "## $CORP"; ls -la "$CORP"; ls -la "$CORP/Point" "$CORP/Mesh" "$CORP/Axes" 2>/dev/null | head -300; } > "$out"
}
corpus_list "$RUN/list_corpus_before.txt"

BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$RUN/build"
cp -a "$PREV/build/src" "$BT" || fail 3 "cannot seed the source tree from $PREV"
rm -rf "$BT/build"; mkdir -p "$BT/build"   # a copied CMakeCache names the old run dir; cmake refuses it
tar -xf "$RUN/patch2.tar" -C "$BT" || fail 3 "patch2.tar extract failed"
for f in mesh_processing_headless.cpp edgeline_extraction_headless.cpp; do
  printf "%s\t%s\t%s\n" "$(md5sum "$BT/$f" | cut -d' ' -f1)" "$f" "$(stat -c %s "$BT/$f") bytes" >> "$RUN/src.md5"
done
cat "$RUN/src.md5"
grep -q "T328-LINENORMALS" "$BT/edgeline_extraction_headless.cpp" || fail 4 "T328-LINENORMALS missing"
grep -q "PAPER-234] t328:" "$BT/mesh_processing_headless.cpp" || fail 4 "t328 classify line missing"
[ -d "$BT/alglib" ] || fail 3 "alglib missing"

( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless
) > "$RUN/logs/build.log" 2>&1
BRC=$?
if [ "$BRC" -eq 0 ] && [ -x "$BT/build/MeshPreprocessingHeadless" ] && [ -x "$BT/build/EdgeLineExtractionHeadless" ]; then
  MESH_BIN=$RUN/bin-MeshPreprocessingHeadless
  EDGE_BIN=$RUN/bin-EdgeLineExtractionHeadless
  cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
  cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
  { echo "src	$NEW (worktree copy, ticket 328 patches, plane-fit line normal)"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d' ' -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d' ' -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > "$RUN/binaries.md5"
  cat "$RUN/binaries.md5"
else
  grep -n -B2 -A6 -i "error" "$RUN/logs/build.log" | head -60 || true
  fail 5 "build failed rc=$BRC"
fi
INSTR=$BT/.scratch/juglet-breaklines/stage66
STAGER=$BT/.scratch/juglet-breaklines/stage55/instruments/stage_synth_p40.sh
[ -f "$INSTR/run_cell66.sh" ] || fail 3 "run_cell66.sh missing"
[ -f "$STAGER" ] || fail 3 "stage_synth_p40.sh missing"
export CANON CORP DS SIF APT PY RUN RUNID NEW IXTAG JOBID P MESH_BIN EDGE_BIN INSTR STAGER GT

record_cell() {
  local name=$1 f
  : > "$RUN/pass${name}.files.md5"
  for f in "$RUN"/out${name}/geom/*; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d' ' -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/pass${name}.files.md5"
  done
  grep -aH "PAPER-234" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.classify.txt" || true
  grep -aH "T328-LINENORMALS" "$RUN"/out${name}/pieces/*/edge.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.linenormals.txt" || true
  grep -aH "Normals flipped" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.flips.txt" || true
  echo "[JOB] cell $name: $(ls "$RUN"/out${name}/geom/*.S0 2>/dev/null | wc -l) S0, $(ls "$RUN"/out${name}/geom/*.Bl0 2>/dev/null | wc -l) Bl0; t328 lines $(grep -c 't328:' "$RUN/pass${name}.classify.txt" 2>/dev/null || echo 0); linenormals $(wc -l < "$RUN/pass${name}.linenormals.txt")"
}

RC_ANY=0
UNSET="-u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR -u SFS_NORMAL_MODE -u SFS_NORMAL_RADIUS_MM"
run_cell() {
  local name=$1 pot=$2 pcs=$3 w=$4 menv=$5 cdir=$6 mdir=$7 adir=$8 man=$9 mcol=${10} pcol=${11} mb=${12:-} eb=${13:-} extra rc
  if [ "$pot" = Juglet ]; then extra="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0"; else extra=""; fi
  local MB=${mb:-$MESH_BIN} EB=${eb:-$EDGE_BIN}
  echo "[JOB] cell $name: pot=$pot worness=${w:-unset} axes=$adir"
  env $UNSET $extra POT_NAME="$pot" PIECES="$pcs" WORNESS="$w" MESH_ENV="$menv" OUT="$RUN/out$name" \
      CLOUD_DIR="$cdir" MESH_DIR="$mdir" AXIS_DIR="$adir" MANIFEST="$man" MAN_MD5_COL="$mcol" MAN_PTS_COL="$pcol" \
      MESH_BIN="$MB" EDGE_BIN="$EB" \
      bash "$INSTR/run_cell66.sh" > "$RUN/logs/pass$name.cells.log" 2>&1
  rc=$?
  echo "[JOB] cell $name rc=$rc"; tail -4 "$RUN/logs/pass$name.cells.log" || true
  [ "$rc" -ne 0 ] && RC_ANY=$rc
  record_cell "$name"
}

JMAN=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
RMAN=$CORP/Point/MANIFEST_released.tsv
CMAN=$RUN/pins/MANIFEST_potc_pinned.tsv
printf "piece\tpcd_md5\tkept_points\n" > "$CMAN"
printf "Pot_C_Piece_01\t651dd0488038bcca65f6b57db6eb9861\t840835\n" >> "$CMAN"

run_cell gt_jug  Juglet "$JUG"  0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$GT"             "$JMAN" pcd_md5 kept_points
run_cell ds_jug  Juglet "$JUG"  0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$DS/Axes/Juglet" "$JMAN" pcd_md5 kept_points
run_cell new_pota Pot_A "$POTA" ""  "$SHIPPED" "$CORP/Point/Pot_A" "$CORP/Mesh" "$DS/Axes/Pot_A" "$RMAN" md5 points
run_cell new_potc Pot_C "$POTC" ""  "$SHIPPED" "$DS/Point/Pot_C" "$DS/Mesh/Pot_C" "$CORP/Axes" "$CMAN" pcd_md5 kept_points

WORKH=$RUN/work/diag326
mkdir -p "$WORKH/tools" "$WORKH/logs"
cp -f "$RUN/work/diag326_pairs.cpp" "$WORKH/tools/diag326_pairs.cpp" || fail 6 "harness source missing"
cp -f "$RUN/work/diag326.sh" "$WORKH/diag326.sh" || fail 6 "harness script missing"
cp -a "$T325/work/inc_jug" "$RUN/inc_jug" || fail 6 "inc_jug copy failed"
cp -f "$T326/out/diag_jug_GT.txt" "$RUN/out/diag_jug_before.txt" || echo "[JOB] WARN no before table"
cp -al "$T326/work/build" "$WORKH/build" || fail 6 "cannot clone the pristine build"

mk_tree() {
  local G=$1 T=$2 i
  rm -rf "$T"; mkdir -p "$T/Axes" "$T/Breaklines" "$T/Surfaces" "$T/Mesh" "$T/Ground Truth"
  for i in 1 2 3 4 5 6 7 8 9; do
    "$PY" - "$G/Juglet_Piece_$i.S0" "$T/Surfaces/Juglet_Piece_${i}_Surface_0.xyz" <<'PYEOF' || return 1
import sys
src, dst = sys.argv[1], sys.argv[2]
n = 0; hdr = True; rows = []
with open(src) as f:
    for line in f:
        if hdr:
            t = line.split()
            if t and t[0] == 'element' and t[1] == 'vertex': n = int(t[2])
            if t and t[0] == 'end_header': hdr = False
            continue
        if len(rows) < n:
            rows.append(' '.join(line.split()[:6]))
open(dst, 'w').write('\n'.join(rows) + '\n')
PYEOF
    "$PY" - "$G/Juglet_Piece_$i.S1" "$T/Surfaces/Juglet_Piece_${i}_Surface_1.xyz" <<'PYEOF' || return 1
import sys
src, dst = sys.argv[1], sys.argv[2]
n = 0; hdr = True; rows = []
with open(src) as f:
    for line in f:
        if hdr:
            t = line.split()
            if t and t[0] == 'element' and t[1] == 'vertex': n = int(t[2])
            if t and t[0] == 'end_header': hdr = False
            continue
        if len(rows) < n:
            rows.append(' '.join(line.split()[:6]))
open(dst, 'w').write('\n'.join(rows) + '\n')
PYEOF
    cp -f "$G/Juglet_Piece_$i.Bl0" "$T/Breaklines/Juglet_Piece_${i}_Breakline_0.pcd" || return 1
    cp -f "$GT/Juglet_Piece_${i}_Axis.xyz" "$T/Axes/Juglet_Piece_${i}_Axis.xyz" || return 1
    cp -f "$GT/Juglet_Piece_${i}_T.txt" "$T/Ground Truth/Juglet_Piece_${i}_T.txt" || return 1
    ln -sf "$DS/Mesh/Juglet/Juglet_Piece_${i}_Mesh.obj" "$T/Mesh/Juglet_Piece_${i}_Mesh.obj"
  done
  cp -f "$GT/Juglet_simple_graph.txt" "$T/Ground Truth/Juglet_simple_graph.txt"
  ( cd "$T" && find . -type f | sort | xargs md5sum > "$RUN/out/tree_$(basename $T).md5" )
}
mk_tree "$RUN/outgt_jug/geom" "$RUN/trees/juglet_after" || fail 7 "after tree build failed"

echo "[JOB] diag326 after $(date -u +%FT%TZ)"
$APT exec --writable-tmpfs --bind "$WORKH":/panel --bind "$RUN/inc_jug":/inc:ro --bind "$RUN/trees/juglet_after":/Dataset/SfS_pp:ro \
   "$SIFA" bash /panel/diag326.sh jug_after /inc 20 -DJUGLET_ORIG > "$RUN/out/diag_jug_after.txt" 2>&1
echo "[JOB] diag326 after rc=$?"
tail -3 "$RUN/out/diag_jug_after.txt" || true

corpus_list "$RUN/list_corpus_after.txt"
diff "$RUN/list_corpus_before.txt" "$RUN/list_corpus_after.txt" > "$RUN/list_corpus.diff" 2>&1
echo "[JOB] corpus listing diff lines: $(wc -l < "$RUN/list_corpus.diff")"
echo "[JOB] cells rc_any=$RC_ANY complete $(date -u +%FT%TZ)"
echo "$RC_ANY" > "$RUN/out/rc_any.txt"
exit "$RC_ANY"
