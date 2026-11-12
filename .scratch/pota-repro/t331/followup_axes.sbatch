#!/bin/bash
# Ticket 331 Part B, follow-up -- the axes stage + the counts, on the geometries that job 34874502
# leaves behind. Chained with --dependency=afterany:34874502 so it starts the moment the run ends.
# It writes nothing outside RUN and reads the corpus read-only; it never touches outlarge_rad3's
# completeness (the diagnostic arm may be short: that job's 02:00:00 wall).
#SBATCH --job-name=t331A
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-axes-%j.out
#SBATCH --error=logs/slurm-axes-%j.err
set -uo pipefail

RUN=${SLURM_SUBMIT_DIR:?}
JOBID=${SLURM_JOB_ID:-na}
PREV=34874502
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
DS=$CANON/Dataset
GT=$DS/Juglet_GT
LG=/data/gpfs/projects/punim2657/Dataset/Juglet_large
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
NEW=b1e1580

export OMP_NUM_THREADS=1
for v in $(env | awk -F= '/^(SFS_|POT_NAME=)/{print $1}'); do unset "$v"; done
mkdir -p "$RUN/logs" "$RUN/pins"

trap 'rc=$?; echo "job ${SLURM_JOB_ID:-na} (axes follow-up) exit $rc" >> "$RUN/logs/job_status.log"' EXIT
fail() { echo "FAIL $1"; echo "FAIL $1" >> "$RUN/logs/job_status.log"; echo "axes-failed: $1" > "$RUN/AXES-FAILED.txt"; exit "${2:-1}"; }
step() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

echo "[JOB] axes follow-up runid=$(basename "$RUN") job=$JOBID host=$(hostname) start=$(date -u +%FT%TZ) prev=$PREV"

# ---------------------------------------------------------------- A. what the run left behind
step "A. inventory of the previous job"
sacct -j $PREV --format=JobID,JobName%12,State,ExitCode,Elapsed,Timelimit,MaxRSS -P > "$RUN/pins/sacct_$PREV.tsv" 2>&1 || true
cat "$RUN/pins/sacct_$PREV.tsv"
for ARM in ctl_jug large_jug large_rad3; do
  G="$RUN/out$ARM/geom"
  N=$(ls "$G"/*.Bl0 2>/dev/null | wc -l)
  echo "arm $ARM geom=$G  Bl0_files=$N"
  [ -f "$RUN/out$ARM/pieces66.tsv" ] && echo "  pieces66: $(($(wc -l < "$RUN/out$ARM/pieces66.tsv") - 1)) rows"
done
[ "$(ls "$RUN"/outctl_jug/geom/*.Bl0 2>/dev/null | wc -l)" -ge 18 ] || echo "WARN control arm incomplete"
[ "$(ls "$RUN"/outlarge_jug/geom/*.Bl0 2>/dev/null | wc -l)" -ge 18 ] || echo "WARN large arm incomplete"

# ------------------------------------------------------------------- B. the tree (for sfs_axes)
step "B. extract $NEW into RUN/build/axes_src (tar overwrites; no deletion)"
BTX="$RUN/build/axes_src"
mkdir -p "$BTX"
git -C "$CANON" archive "$NEW" 2>>"$RUN/logs/axes_tools.log" | tar -x -C "$BTX" 2>>"$RUN/logs/axes_tools.log"
[ -d "$BTX/sfs_axes" ] || fail "B: sfs_axes not in the archive" 3
( cd "$BTX" && md5sum scripts/run_benchmark_172.py ) > "$RUN/pins/axes_src.md5"
ls "$BTX/sfs_axes" | head -5

# --------------------------------------------------------------------------- C. axes per arm
step "C. axis estimator on each arm's own walls (the shipped arguments from run_benchmark_172.py)"
for pair in "ctl_jug|$GT|ctl" "large_jug|$LG|large" "large_rad3|$LG|rad3"; do
  ARM=$(printf '%s' "$pair" | cut -d'|' -f1)
  AXT=$(printf '%s' "$pair" | cut -d'|' -f2)
  TAG=$(printf '%s' "$pair" | cut -d'|' -f3)
  G="$RUN/out$ARM/geom"
  if [ -d "$G" ] && [ -n "$(ls "$G"/*.S0 2>/dev/null)" ]; then
    $PY "$RUN/tools/run_axes_t331.py" --tree "$BTX" --geom "$G" --out "$RUN/axes_$TAG" --gt "$AXT" --tag "$TAG" > "$RUN/logs/axes_$TAG.log" 2>&1
    echo "axes $TAG rc=$? out=$RUN/axes_$TAG pieces=$(ls "$RUN/axes_$TAG"/*_Axis.xyz 2>/dev/null | wc -l)"
    grep -a '^\[AXES\]' "$RUN/logs/axes_$TAG.log" | tail -10
  else
    echo "axes $TAG SKIPPED (no walls at $G)"
  fi
done

# ----------------------------------------------------------------------- D. the dot-count table
step "D. dot-count table"
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

# ------------------------------------------------------- E. the corpus did not move (read-only)
step "E. read-only proof"
( cd "$LG" && md5sum Piece0*.obj Juglet_Piece_*_T.txt Juglet_Piece_*_Axis.xyz Juglet_simple_graph.txt scale_census.tsv scale_checks.json ) > "$RUN/pins/juglet_large_after.md5"
if diff -q "$RUN/pins/juglet_large.md5" "$RUN/pins/juglet_large_after.md5" > /dev/null 2>&1; then echo "Juglet_large unchanged"; else echo "Juglet_large CHANGED or no before-image"; diff "$RUN/pins/juglet_large.md5" "$RUN/pins/juglet_large_after.md5" | head; fi
( cd "$GT" && md5sum * ) > "$RUN/pins/juglet_gt_after.md5"
( cd "$DS/Point/Juglet" && md5sum *.pcd ) > "$RUN/pins/juglet_cloud_after.md5"
( cd "$DS/Mesh/Juglet" && md5sum *.obj ) > "$RUN/pins/juglet_mesh_after.md5"
wc -l "$RUN/pins/juglet_gt_after.md5" "$RUN/pins/juglet_cloud_after.md5" "$RUN/pins/juglet_mesh_after.md5"

echo
echo "[JOB] axes follow-up done $(date -u +%FT%TZ)"
