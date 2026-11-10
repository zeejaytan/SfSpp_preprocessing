#!/bin/bash
#SBATCH --job-name=t328wall
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#
# Ticket 328, job A. Build the WORKTREE source (ticket 328's two patches: mesh-stage
# self-checking filing + edge-stage per-point wall normals) and measure:
#   cell gt_jug  Juglet 1-9, GT axes (Dataset/Juglet_GT)   -- bar 1/2/3 cured arm
#   cell ds_jug  Juglet 1-9, shipped Dataset/Axes/Juglet   -- bar 1 under the bad axis
#   new_pota / new_potc   Pot_A 01-08, Pot_C 01, shipped defaults, new binaries
#   old_pota / old_potc   same cells, t66 binaries (fab76f5) -- run-to-run draw control
#   326 harness (diag326_pairs.cpp, pristine objects) on
#     trees/juglet_before = t66 outU_jug geom (shipped) + GT axes
#     trees/juglet_after  = gt_jug geom (cured)         + GT axes
# Corpus is read-only; nothing is written outside this run directory.
set -uo pipefail
: "${RUNID:?}" "${NEW:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t328-wallside
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
GT=$DS/Juglet_GT
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T66=$RUNS/20261103-1332_fab76f5_t66-admitsign-default
T325=$RUNS/20261110-1640_22151d0_t325-juglet
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
rm -rf "$RUN/build"; mkdir -p "$BT/build"
tar -xf "$RUN/src.tar" -C "$BT" || fail 3 "src.tar extract failed"
for f in mesh_processing_headless.cpp edgeline_extraction_headless.cpp; do
  printf "%s\t%s\t%s\n" "$(md5sum "$BT/$f" | cut -d' ' -f1)" "$f" "$(stat -c %s "$BT/$f") bytes" >> "$RUN/src.md5"
done
grep -q "T328-LINENORMALS" "$BT/edgeline_extraction_headless.cpp" || fail 4 "T328-LINENORMALS missing from the archived edge source"
grep -q "PAPER-234] t328:" "$BT/mesh_processing_headless.cpp" || fail 4 "t328 classify line missing from the archived mesh source"
[ -d "$BT/alglib" ] || fail 3 "alglib missing from the tar"

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
  { echo "src	$NEW (worktree tar, ticket 328 patches)"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d' ' -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d' ' -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > "$RUN/binaries.md5"
  cat "$RUN/binaries.md5"
else
  grep -n -B2 -A6 -i "error" "$RUN/logs/build.log" | head -80 || true
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
  echo "[JOB] cell $name: $(ls "$RUN"/out${name}/geom/*.S0 2>/dev/null | wc -l) S0, $(ls "$RUN"/out${name}/geom/*.S1 2>/dev/null | wc -l) S1, $(ls "$RUN"/out${name}/geom/*.Bl0 2>/dev/null | wc -l) Bl0; classify lines $(wc -l < "$RUN/pass${name}.classify.txt"); t328 lines $(grep -c 't328:' "$RUN/pass${name}.classify.txt" 2>/dev/null || echo 0); linenormals lines $(wc -l < "$RUN/pass${name}.linenormals.txt")"
}

RC_ANY=0
UNSET="-u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR -u SFS_NORMAL_MODE -u SFS_NORMAL_RADIUS_MM"
run_cell() {
  local name=$1 pot=$2 pcs=$3 w=$4 menv=$5 cdir=$6 mdir=$7 adir=$8 man=$9 mcol=${10} pcol=${11} mb=${12:-} eb=${13:-} extra rc
  if [ "$pot" = Juglet ]; then extra="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0"; else extra=""; fi
  local MB=${mb:-$MESH_BIN} EB=${eb:-$EDGE_BIN}
  echo "[JOB] cell $name: pot=$pot worness=${w:-unset} axes=$adir mesh_bin=$(basename $MB) mesh_env=[$menv]"
  env $UNSET $extra POT_NAME="$pot" PIECES="$pcs" WORNESS="$w" MESH_ENV="$menv" OUT="$RUN/out$name" \
      CLOUD_DIR="$cdir" MESH_DIR="$mdir" AXIS_DIR="$adir" MANIFEST="$man" MAN_MD5_COL="$mcol" MAN_PTS_COL="$pcol" \
      MESH_BIN="$MB" EDGE_BIN="$EB" \
      bash "$INSTR/run_cell66.sh" > "$RUN/logs/pass$name.cells.log" 2>&1
  rc=$?
  echo "[JOB] cell $name rc=$rc"; tail -6 "$RUN/logs/pass$name.cells.log" || true
  [ "$rc" -ne 0 ] && RC_ANY=$rc
  record_cell "$name"
}

JMAN=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
RMAN=$CORP/Point/MANIFEST_released.tsv
CMAN=$RUN/pins/MANIFEST_potc_pinned.tsv
printf "piece\tpcd_md5\tkept_points\n" > "$CMAN"
printf "Pot_C_Piece_01\t651dd0488038bcca65f6b57db6eb9861\t840835\n" >> "$CMAN"

run_cell gt_jug  Juglet "$JUG"  0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$GT"              "$JMAN" pcd_md5 kept_points
run_cell ds_jug  Juglet "$JUG"  0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$DS/Axes/Juglet"  "$JMAN" pcd_md5 kept_points
run_cell new_pota Pot_A "$POTA" ""  "$SHIPPED" "$CORP/Point/Pot_A" "$CORP/Mesh" "$DS/Axes/Pot_A" "$RMAN" md5 points
run_cell new_potc Pot_C "$POTC" ""  "$SHIPPED" "$DS/Point/Pot_C" "$DS/Mesh/Pot_C" "$CORP/Axes" "$CMAN" pcd_md5 kept_points
run_cell old_pota Pot_A "$POTA" ""  "$SHIPPED" "$CORP/Point/Pot_A" "$CORP/Mesh" "$DS/Axes/Pot_A" "$RMAN" md5 points \
     "$T66/bin-MeshPreprocessingHeadless" "$T66/bin-EdgeLineExtractionHeadless"
run_cell old_potc Pot_C "$POTC" ""  "$SHIPPED" "$DS/Point/Pot_C" "$DS/Mesh/Pot_C" "$CORP/Axes" "$CMAN" pcd_md5 kept_points \
     "$T66/bin-MeshPreprocessingHeadless" "$T66/bin-EdgeLineExtractionHeadless"

sfiles() { awk -F'\t' '$2 ~ /\.(S[01]|Bl[01])$/ {print $2"\t"$1}' "$1" | sort; }
cmp_pair() {
  join -t $'\t' <(sfiles "$3") <(sfiles "$4") \
    | awk -F'\t' -v tag="$2" '{print tag"\t"$1"\t"$2"\t"$3"\t"($2==$3?"same":"DIFF")}' >> "$RUN/out/pot_identity.tsv"
}
: > "$RUN/out/pot_identity.tsv"
for c in pota potc; do
  cmp_pair "$RUN/out/pot_identity.tsv" "new_vs_t66_$c"  "$RUN/passnew_$c.files.md5"  "$T66/passU_$c.files.md5"
  cmp_pair "$RUN/out/pot_identity.tsv" "old_vs_t66_$c"  "$RUN/passold_$c.files.md5"  "$T66/passU_$c.files.md5"
  cmp_pair "$RUN/out/pot_identity.tsv" "new_vs_old_$c"  "$RUN/passnew_$c.files.md5"  "$RUN/passold_$c.files.md5"
done
echo "[JOB] pot identity rows: $(wc -l < "$RUN/out/pot_identity.tsv"); DIFF rows: $(grep -c DIFF "$RUN/out/pot_identity.tsv" || true)"
awk -F'\t' '$5=="DIFF"{print "  DIFF", $2, $3, $1}' "$RUN/out/pot_identity.tsv" | head -30

WORKH=$RUN/work/diag326
mkdir -p "$WORKH/tools" "$WORKH/logs"
cp -f "$RUN/work/diag326_pairs.cpp" "$WORKH/tools/diag326_pairs.cpp" || fail 6 "harness source missing"
cp -f "$RUN/work/diag326.sh" "$WORKH/diag326.sh" || fail 6 "harness script missing"
cp -a "$T325/work/inc_jug" "$RUN/inc_jug" || fail 6 "inc_jug copy failed"
$APT exec --writable-tmpfs --bind "$WORKH":/panel "$SIF" bash -c '
  mkdir -p /panel/build && cd /panel/build
  cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
  make -j'"$P"' > /panel/logs/make.log 2>&1' || fail 6 "pristine object build failed (see work/diag326/logs)"

mk_tree() {
  local G=$1 T=$2 i
  rm -rf "$T"; mkdir -p "$T/Axes" "$T/Breaklines" "$T/Surfaces" "$T/Mesh" "$T/Ground Truth"
  for i in 1 2 3 4 5 6 7 8 9; do
    cp -f "$G/Juglet_Piece_$i.S0" "$T/Surfaces/Juglet_Piece_${i}_Surface_0.xyz" || return 1
    cp -f "$G/Juglet_Piece_$i.S1" "$T/Surfaces/Juglet_Piece_${i}_Surface_1.xyz" || return 1
    cp -f "$G/Juglet_Piece_$i.Bl0" "$T/Breaklines/Juglet_Piece_${i}_Breakline_0.pcd" || return 1
    cp -f "$GT/Juglet_Piece_${i}_Axis.xyz" "$T/Axes/Juglet_Piece_${i}_Axis.xyz" || return 1
    cp -f "$GT/Juglet_Piece_${i}_T.txt" "$T/Ground Truth/Juglet_Piece_${i}_T.txt" || return 1
    ln -sf "$DS/Mesh/Juglet/Juglet_Piece_${i}_Mesh.obj" "$T/Mesh/Juglet_Piece_${i}_Mesh.obj"
  done
  cp -f "$GT/Juglet_simple_graph.txt" "$T/Ground Truth/Juglet_simple_graph.txt"
  ( cd "$T" && find . -type f | sort | xargs md5sum > "$RUN/out/tree_$(basename $T).md5" )
}
mk_tree "$T66/outU_jug/geom" "$RUN/trees/juglet_before" || fail 7 "before tree build failed"
mk_tree "$RUN/outgt_jug/geom" "$RUN/trees/juglet_after" || fail 7 "after tree build failed"

for L in before after; do
  echo "[JOB] diag326 $L $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs --bind "$WORKH":/panel --bind "$RUN/inc_jug":/inc:ro --bind "$RUN/trees/juglet_$L":/Dataset/SfS_pp:ro \
     "$SIF" bash /panel/diag326.sh "jug_$L" /inc 20 -DJUGLET_ORIG > "$RUN/out/diag_jug_$L.txt" 2>&1
  echo "[JOB] diag326 $L rc=$?"
done

corpus_list "$RUN/list_corpus_after.txt"
diff "$RUN/list_corpus_before.txt" "$RUN/list_corpus_after.txt" > "$RUN/list_corpus.diff" 2>&1 && echo "[JOB] corpus listings identical" || echo "[JOB] WARN corpus listing changed (see list_corpus.diff)"

{
  echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "src_tar=$NEW"; echo "tag=$IXTAG"
  echo "host=$(hostname)"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mesh_md5=$(md5sum "$MESH_BIN" | cut -d' ' -f1)"
  echo "edge_md5=$(md5sum "$EDGE_BIN" | cut -d' ' -f1)"
  echo "rc_any=$RC_ANY"
} > "$RUN/run-meta.txt"
echo "[JOB] complete rc=$RC_ANY end=$(date -u +%FT%TZ)"
exit "$RC_ANY"
