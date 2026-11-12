#!/bin/bash
# Ticket 331 Part B -- the 3x Juglet through the unmodified chain, plus the unscaled control.
# One sbatch: extract b1e1580, build the two binaries in the SIF, sample the nine 3x meshes,
# run two cells (Juglet_large @ normal radius 1.0 mm = the shipped stage66 recipe; Juglet
# corpus @ 1.0 mm = the control) and one diagnostic cell (Juglet_large @ 3.0 mm = the
# scale-equivalent normal neighbourhood, NOT the shipped recipe, reported separately), then
# the shipped axis estimator on each arm's own walls.
# Nothing under Dataset/ is written: the only writes are under RUN and the cells' out/.
#SBATCH --job-name=t331L
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
set -uo pipefail

RUN=${SLURM_SUBMIT_DIR:?}
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
DS=$CANON/Dataset
GT=$DS/Juglet_GT
LG=/data/gpfs/projects/punim2657/Dataset/Juglet_large
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
NEW=b1e1580
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"

export OMP_NUM_THREADS=1
for v in $(env | awk -F= '/^(SFS_|POT_NAME=)/{print $1}'); do unset "$v"; done
mkdir -p "$RUN/logs" "$RUN/pins" "$RUN/tools"

trap 'rc=$?; echo "job ${SLURM_JOB_ID:-na} exit $rc" >> "$RUN/logs/job_status.log"' EXIT
fail() { echo "FAIL $1"; echo "FAIL $1" >> "$RUN/logs/job_status.log"; echo "run-failed" > "$RUN/RUN-FAILED.txt"; exit "${2:-1}"; }
step() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

echo "[JOB] runid=$(basename "$RUN") job=$JOBID host=$(hostname) start=$(date -u +%FT%TZ)"
echo "[JOB] commit=$NEW pot_large=Juglet_large source meshes=Dataset/Mesh/Juglet (mm) x3"
echo "[JOB] attempt 2: job 34874502 (02:00:00 wall) was killed after large_jug piece 1; wall raised, control cell moved first, the nine 3x clouds are reused when their md5 still matches the pins"

# ---------------------------------------------------------------- A. Part A outputs intact
step "A. Juglet_large integrity vs scale_census.tsv"
$PY - "$LG" > "$RUN/pins/partA_verify.txt" 2>&1 <<'PYEOF'
import csv, hashlib, os, sys
LG = sys.argv[1]
def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
rows = list(csv.DictReader(open(os.path.join(LG, 'scale_census.tsv')), delimiter='\t'))
bad = 0
for r in rows:
    name = r['out_obj'].split('/')[-1]
    got = md5(os.path.join(LG, name))
    ok = (got == r['out_md5'])
    print('%-20s out_md5 disk=%s census=%s %s' % (name, got, r['out_md5'], 'OK' if ok else 'MISMATCH'))
    if not ok:
        bad += 1
print('n_pieces=%d' % len(rows))
print('RESULT %s' % ('OK' if not bad else 'BAD %d' % bad))
PYEOF
cat "$RUN/pins/partA_verify.txt"
grep -q '^RESULT OK' "$RUN/pins/partA_verify.txt" || fail "A: Juglet_large md5 mismatch" 2
( cd "$LG" && md5sum Piece0*.obj Juglet_Piece_*_T.txt Juglet_Piece_*_Axis.xyz Juglet_simple_graph.txt scale_census.tsv scale_checks.json ) > "$RUN/pins/juglet_large.md5"

# ------------------------------------------------- B. the nine 3x meshes under their chain names
step "B. mesh_large copies (chain names) + equality to Dataset/Juglet_large"
rm -rf "$RUN/mesh_large"; mkdir -p "$RUN/mesh_large"
for i in 1 2 3 4 5 6 7 8 9; do
  n=$(printf '%02d' $i)
  cp -f "$LG/Piece$n.obj" "$RUN/mesh_large/Juglet_Piece_${i}_Mesh.obj" || fail "B: cp piece$i" 2
  cmp -s "$LG/Piece$n.obj" "$RUN/mesh_large/Juglet_Piece_${i}_Mesh.obj" || fail "B: cmp piece$i" 2
done
( cd "$RUN/mesh_large" && md5sum *_Mesh.obj ) > "$RUN/pins/mesh_large.md5"
cat "$RUN/pins/mesh_large.md5"

# ------------------------------------------------------------------------ C. build the chain
step "C. extract $NEW and build MeshPreprocessingHeadless + EdgeLineExtractionHeadless"
BT="$RUN/build/src"
rm -rf "$RUN/build"; mkdir -p "$BT"
git -C "$CANON" archive "$NEW" 2>>"$RUN/logs/build.log" | tar -x -C "$BT" 2>>"$RUN/logs/build.log"
[ -f "$BT/CMakeLists.txt" ] || fail "C: archive/tar" 3
( cd "$BT" && md5sum mesh_processing_headless.cpp edgeline_extraction_headless.cpp cc_mesh_to_pcd.sh .scratch/juglet-breaklines/stage66/run_cell66.sh .scratch/juglet-breaklines/stage55/instruments/stage_synth_p40.sh ) > "$RUN/pins/src.md5"
cat "$RUN/pins/src.md5"
{ grep -c 'T328-LINENORMALS' "$BT/edgeline_extraction_headless.cpp"; grep -c 'PAPER-234] t328:' "$BT/mesh_processing_headless.cpp"; } > "$RUN/pins/marker_linenormals.txt"
cat "$RUN/pins/marker_linenormals.txt"
mkdir -p "$BT/build"
"$APT" exec --bind /data:/data "$SIF" bash -c "cd '$BT/build' && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j$P MeshPreprocessingHeadless EdgeLineExtractionHeadless" >> "$RUN/logs/build.log" 2>&1
[ "$?" -eq 0 ] || fail "C: build" 4
mkdir -p "$RUN/bin-$NEW"
cp -f "$BT/build/MeshPreprocessingHeadless" "$BT/build/EdgeLineExtractionHeadless" "$RUN/bin-$NEW/" || fail "C: cp binaries" 4
( cd "$RUN/bin-$NEW" && md5sum * ) | tee "$RUN/pins/binaries.md5"
tail -3 "$RUN/logs/build.log"

# ---------------------------------------------------------- D. sample the nine 3x meshes
step "D. CloudCompare sampling of the nine 3x meshes into RUN/cloud_mesh"
PIN="$RUN/pins/MANIFEST_JUGLET_LARGE.tsv"
SKIP=no
if [ -f "$PIN" ]; then
  SKIP=yes
  for i in 1 2 3 4 5 6 7 8 9; do
    PC="$RUN/cloud_mesh/Juglet_Piece_${i}_Point.pcd"
    WANT=$(awk -F'\t' -v p="Juglet_Piece_$i" '$1==p{print $5}' "$PIN")
    HAVE=$([ -f "$PC" ] && md5sum "$PC" | cut -d' ' -f1 || true)
    if [ -z "${WANT:-}" ] || [ "${HAVE:-none}" != "$WANT" ]; then
      SKIP=no; echo "re-sample piece $i (want=${WANT:-none} have=${HAVE:-none})"
    fi
  done
fi
if [ "$SKIP" = yes ]; then
  echo "D. SKIPPED -- the nine 3x clouds match pins/MANIFEST_JUGLET_LARGE.tsv (the draw made by job 34874502 is preserved)"
  cat "$PIN"
  ( cd "$RUN/cloud_mesh" && md5sum *.pcd ) > "$RUN/pins/cloud_mesh.md5"
else
  rm -rf "$RUN/cloud_mesh"; mkdir -p "$RUN/cloud_mesh"
  for i in 1 2 3 4 5 6 7 8 9; do
    M="$RUN/mesh_large/Juglet_Piece_${i}_Mesh.obj"
    bash "$BT/cc_mesh_to_pcd.sh" -i "$M" -o "$RUN/cloud_mesh" -m 1000000 -f >> "$RUN/logs/sample.log" 2>&1
    rc=$?
    N=$([ -f "$RUN/cloud_mesh/Juglet_Piece_${i}_Point.pcd" ] && grep -am1 '^POINTS' "$RUN/cloud_mesh/Juglet_Piece_${i}_Point.pcd" | awk '{print $2}')
    echo "sample piece $i rc=$rc points=${N:-none}"
    [ "$rc" -eq 0 ] && [ -n "${N:-}" ] || fail "D: sample piece $i" 5
  done
  {
    printf 'piece\tsource_mesh\tmesh_md5\tkept_points\tpcd_md5\tpcd_bytes\tcc_log\tdate\tcommand\n'
    for i in 1 2 3 4 5 6 7 8 9; do
      PC="$RUN/cloud_mesh/Juglet_Piece_${i}_Point.pcd"
      printf 'Juglet_Piece_%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$i" "$RUN/mesh_large/Juglet_Piece_${i}_Mesh.obj" "$(md5sum "$RUN/mesh_large/Juglet_Piece_${i}_Mesh.obj" | cut -d' ' -f1)" \
        "$(grep -am1 '^POINTS' "$PC" | awk '{print $2}')" "$(md5sum "$PC" | cut -d' ' -f1)" "$(stat -c %s "$PC")" \
        "$RUN/cloud_mesh/Juglet_Piece_${i}_Point_cc.log" "$(date -u +%FT%TZ)" \
        "cc_mesh_to_pcd.sh -m 1000000 -f (shipped corpus converter, unseeded draw)"
    done
  } > "$RUN/pins/MANIFEST_JUGLET_LARGE.tsv"
  cat "$RUN/pins/MANIFEST_JUGLET_LARGE.tsv"
  ( cd "$RUN/cloud_mesh" && md5sum *.pcd ) > "$RUN/pins/cloud_mesh.md5"
fi

# ------------------------------------------------- E. the run-dir stager (mesh root movable)
step "E. tools/stage_synth_t331.sh vs the pinned stage55 stager (expect one changed line)"
STAGER_ORIG="$BT/.scratch/juglet-breaklines/stage55/instruments/stage_synth_p40.sh"
diff -u "$STAGER_ORIG" "$RUN/tools/stage_synth_t331.sh" > "$RUN/tools/stage_t331.diff"
ND=$(grep -c '^[-+][^-+]' "$RUN/tools/stage_t331.diff")
echo "stager diff changed-lines=$ND"
cat "$RUN/tools/stage_t331.diff"
[ "$ND" -eq 2 ] || fail "E: stager diff is not exactly one line" 6
chmod +x "$RUN/tools/stage_synth_t331.sh"
( md5sum "$RUN/tools/stage_synth_t331.sh" "$STAGER_ORIG" ) | tee "$RUN/pins/stager.md5"

# ------------------------------------------------------------------------- F. the three cells
step "F. cells"
CELLDRV="$BT/.scratch/juglet-breaklines/stage66/run_cell66.sh"
INSTR="$BT/.scratch/juglet-breaklines/stage55/instruments"
MESH_BIN="$RUN/bin-$NEW/MeshPreprocessingHeadless"
EDGE_BIN="$RUN/bin-$NEW/EdgeLineExtractionHeadless"
STAGER="$RUN/tools/stage_synth_t331.sh"
export MESH_ROOT="$RUN/mesh_large"
NORMAL_ENV="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0"

run_cell() { # name pot worness mesh_env cloud_dir mesh_dir axis_dir manifest
  local NAME=$1 POT=$2 W=$3 MENV=$4 CL=$5 MD=$6 AX=$7 MAN=$8
  step "cell $NAME (pot=$POT worness=$W mesh_env=[$MENV])"
  ( cd "$RUN" && env POT_NAME="$POT" PIECES="$JUG" WORNESS="$W" MESH_ENV="$MENV" \
      OUT="$RUN/out$NAME" CLOUD_DIR="$CL" MESH_DIR="$MD" AXIS_DIR="$AX" MANIFEST="$MAN" \
      MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points MAN_SPACING_COL=spacing_mm \
      INSTR="$INSTR" PY="$PY" DS="$DS" CORP="$CORP" APT="$APT" SIF="$SIF" \
      STAGER="$STAGER" RUN="$RUN" JOBID="$JOBID" MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" \
      bash "$CELLDRV" ) > "$RUN/logs/cell_$NAME.log" 2>&1
  local rc=$?
  echo "cell $NAME rc=$rc out=$RUN/out$NAME"
  tail -14 "$RUN/logs/cell_$NAME.log"
  return $rc
}

run_cell ctl_jug Juglet 0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$GT" "$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv"
RCC=$?
run_cell large_jug Juglet_large 0.7 "$NORMAL_ENV" "$RUN/cloud_mesh" "$RUN/mesh_large" "$LG" "$RUN/pins/MANIFEST_JUGLET_LARGE.tsv"
RCL=$?
run_cell large_rad3 Juglet_large 0.7 "SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=3.0" "$RUN/cloud_mesh" "$RUN/mesh_large" "$LG" "$RUN/pins/MANIFEST_JUGLET_LARGE.tsv"
RCR=$?
echo "cell rcs: large_jug=$RCL ctl_jug=$RCC large_rad3=$RCR"
[ "$RCL" -eq 0 ] || echo "NOTE large_jug rc=$RCL (rows still in outlarge_jug/pieces66.tsv)"
[ "$RCC" -eq 0 ] || echo "NOTE ctl_jug  rc=$RCC (rows still in outctl_jug/pieces66.tsv)"

# ----------------------------------------------------------------------------- G. axes stage
step "G. axis estimator on each arm's own walls (shipped arguments)"
for pair in "large_jug|$LG|large" "ctl_jug|$GT|ctl" "large_rad3|$LG|rad3"; do
  ARM=$(printf '%s' "$pair" | cut -d'|' -f1)
  AXT=$(printf '%s' "$pair" | cut -d'|' -f2)
  TAG=$(printf '%s' "$pair" | cut -d'|' -f3)
  G="$RUN/out$ARM/geom"
  if [ -d "$G" ]; then
    $PY "$RUN/tools/run_axes_t331.py" --tree "$BT" --geom "$G" --out "$RUN/axes_$TAG" --gt "$AXT" --tag "$TAG" > "$RUN/logs/axes_$TAG.log" 2>&1
    echo "axes $TAG rc=$? out=$RUN/axes_$TAG"
    grep -a '^\[AXES\]' "$RUN/logs/axes_$TAG.log" | tail -10
  else
    echo "axes $TAG SKIPPED (no geom dir $G)"
  fi
done

# ------------------------------------------------------------------- H. the counts, side by side
step "H. dot-count table"
[ -f "$RUN/out/dotcounts.tsv" ] && cp -f "$RUN/out/dotcounts.tsv" "$RUN/out/dotcounts.attempt1.tsv" || true
$PY - "$RUN" > "$RUN/out/dotcounts.tsv" 2>>"$RUN/logs/summary.log" <<'PYEOF'
import os, sys
RUN = sys.argv[1]
ARMS = [('ctl_jug', 'unscaled'), ('large_jug', 'large-r1.0'), ('large_rad3', 'large-r3.0')]
data = {}
for a, _ in ARMS:
    p = os.path.join(RUN, 'out' + a, 'pieces66.tsv')
    rows = {}
    if os.path.exists(p):
        lines = open(p).read().splitlines()
        hdr = lines[0].split('\t')
        for ln in lines[1:]:
            f = ln.split('\t')
            if len(f) != len(hdr):
                continue
            r = dict(zip(hdr, f))
            rows[r['piece']] = r
    data[a] = rows
print('\t'.join(['piece', 'ctl_bl0', 'large_bl0', 'rad3_bl0', 'ratio_large_ctl', 'ctl_bl1', 'large_bl1', 'rad3_bl1']))
for i in range(1, 10):
    P = 'Juglet_Piece_%d' % i
    def g(a, col):
        r = data[a].get(P)
        return r.get(col, '-') if r else '-'
    cb, lb, rb = g('ctl_jug', 'bl0_points'), g('large_jug', 'bl0_points'), g('large_rad3', 'bl0_points')
    try:
        ratio = '%.4f' % (float(lb) / float(cb))
    except Exception:
        ratio = '-'
    print('\t'.join([P, cb, lb, rb, ratio,
                      g('ctl_jug', 'bl1_points'), g('large_jug', 'bl1_points'), g('large_rad3', 'bl1_points')]))
for a, _ in ARMS:
    p = os.path.join(RUN, 'out' + a, 'pieces66.tsv')
    if os.path.exists(p):
        print('# %s: %d rows' % (a, len(open(p).read().splitlines()) - 1))
    else:
        print('# %s: NO pieces66.tsv' % a)
PYEOF
cat "$RUN/out/dotcounts.tsv"

# ------------------------------------------------- I. nothing in the corpus moved (read-only)
step "I. corpus read-only proof"
( cd "$LG" && md5sum Piece0*.obj Juglet_Piece_*_T.txt Juglet_Piece_*_Axis.xyz Juglet_simple_graph.txt scale_census.tsv scale_checks.json ) > "$RUN/pins/juglet_large_after.md5"
if diff -q "$RUN/pins/juglet_large.md5" "$RUN/pins/juglet_large_after.md5" > /dev/null; then echo "Juglet_large unchanged (md5 before == after)"; else echo "Juglet_large CHANGED"; fi
( cd "$GT" && md5sum * ) > "$RUN/pins/juglet_gt_after.md5"
( cd "$DS/Juglet" && md5sum *.obj ) > "$RUN/pins/juglet_raw_after.md5"
( cd "$DS/Point/Juglet" && md5sum *.pcd ) > "$RUN/pins/juglet_cloud_after.md5"
( cd "$DS/Mesh/Juglet" && md5sum *.obj ) > "$RUN/pins/juglet_mesh_after.md5"
wc -l "$RUN/pins/juglet_gt_after.md5" "$RUN/pins/juglet_cloud_after.md5" "$RUN/pins/juglet_mesh_after.md5"

# -------------------------------------------------------------------------- J. tidy and stop
step "J. tidy (keep the two sources + the patch record)"
cp -f "$BT/mesh_processing_headless.cpp" "$BT/edgeline_extraction_headless.cpp" "$RUN/pins/" 2>/dev/null
rm -rf "$BT"
echo
echo "[JOB] summary"
echo "  run dir        $RUN"
echo "  cell rcs       large_jug=$RCL ctl_jug=$RCC large_rad3=$RCR"
echo "  dot counts     $RUN/out/dotcounts.tsv"
echo "  axes           $RUN/axes_{large,ctl,rad3}/axes_summary_*.tsv"
echo "  binaries       $RUN/pins/binaries.md5"
echo "  job_status     $RUN/logs/job_status.log"
echo "[JOB] done $(date -u +%FT%TZ)"
