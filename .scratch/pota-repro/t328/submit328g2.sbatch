#!/bin/bash
#SBATCH --job-name=t328h
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:40:00
#
# Ticket 328, job D2: the 326 harness only. Job 34703082 ran all four cells (the cured geom is in
# outgt_jug/geom) and then died at its own line 143, which looked for diag326_pairs.cpp under
# $RUN/work/ while it had been placed at $RUN/ (a path slip in the submit script, not a run fault).
# This script rebuilds the two comparison trees from the geom that job already produced and runs
# the identical harness on both: jug_before (t66 shipped lanes, the defect) and jug_after (the cure).
set -uo pipefail
: "${RUNID:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
DS=$CANON/Dataset
GT=$DS/Juglet_GT
SIFA=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T66=$RUNS/20261103-1332_fab76f5_t66-admitsign-default
T325=$RUNS/20261110-1640_22151d0_t325-juglet
T326=$RUNS/20261110-1844_6925cb0_t326-diag
JOBID=${SLURM_JOB_ID:-na}
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
fail() { local rc=$1; shift; { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > "$RUN/RUN-FAILED2.txt"; echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }
echo "[JOB] runid=$RUNID job=$JOBID host=$(hostname) start=$(date -u +%FT%TZ)"

WORKH=$RUN/work/diag326
mkdir -p "$WORKH/tools" "$WORKH/logs" "$RUN/trees"
cp -f "$RUN/diag326_pairs.cpp" "$WORKH/tools/diag326_pairs.cpp" || fail 6 "harness source missing at $RUN/diag326_pairs.cpp"
cp -f "$RUN/diag326.sh" "$WORKH/diag326.sh" || fail 6 "harness script missing"
md5sum "$WORKH/tools/diag326_pairs.cpp" "$WORKH/diag326.sh" > "$RUN/out/harness.md5"
[ -d "$RUN/inc_jug/class" ] || cp -a "$T325/work/inc_jug" "$RUN/inc_jug" || fail 6 "inc_jug copy failed"
cp -f "$T326/out/diag_jug_GT.txt" "$RUN/out/diag_jug_326table.txt" || echo "[JOB] WARN no 326 table"
[ -d "$WORKH/build" ] || cp -al "$T326/work/build" "$WORKH/build" || fail 6 "cannot clone the pristine build"

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
  ( cd "$T" && find . -type f -print0 | sort -z | xargs -0 md5sum > "$RUN/out/tree_$(basename $T).md5" )
}

mk_tree "$T66/outU_jug/geom" "$RUN/trees/jug_before" || fail 7 "before tree build failed"
mk_tree "$RUN/outgt_jug/geom" "$RUN/trees/jug_after"  || fail 7 "after tree build failed"

for T in jug_before jug_after; do
  echo "[JOB] harness $T $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs --bind "$WORKH":/panel --bind "$RUN/inc_jug":/inc:ro --bind "$RUN/trees/$T":/Dataset/SfS_pp:ro \
     "$SIFA" bash /panel/diag326.sh "$T" /inc 20 -DJUGLET_ORIG > "$RUN/out/diag_${T}.txt" 2>&1
  echo "[JOB] harness $T rc=$? $(date -u +%FT%TZ)"
  grep -c GTPAIR "$RUN/out/diag_${T}.txt" || true
done

cp -f "$RUN/out/diag_jug_after.txt" "$RUN/out/diag_jug_after.txt"
echo "[JOB] complete $(date -u +%FT%TZ)"
