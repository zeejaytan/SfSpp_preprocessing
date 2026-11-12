#!/bin/bash
# Ticket 331 Part B, follow-up -- starts the moment job 34874502 ends (--dependency=afterany).
# Three jobs of work, all on artefacts that job leaves behind:
#   1. the unscaled control run a SECOND time (outctl2), to measure the control's own run-to-run
#      spread in dot count and in matched stretch -- the quantity the 2.7-3.3x window is exposed to;
#   2. the shipped axis estimator on each arm's own walls (skipped for an arm whose summary exists);
#   3. the dot-count table (now with both control repeats) and the matched-stretch tables.
# Nothing outside RUN is written; the corpus is read only.
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
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"

export OMP_NUM_THREADS=1
for v in $(env | awk -F= '/^(SFS_|POT_NAME=)/{print $1}'); do unset "$v"; done
mkdir -p "$RUN/logs" "$RUN/pins"

trap 'rc=$?; echo "job ${SLURM_JOB_ID:-na} (follow-up) exit $rc" >> "$RUN/logs/job_status.log"' EXIT
step() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

echo "[JOB] follow-up runid=$(basename "$RUN") job=$JOBID host=$(hostname) start=$(date -u +%FT%TZ) prev=$PREV"

step "A. what the run left behind"
sacct -j $PREV --format=JobID,JobName%12,State,ExitCode,Elapsed,Timelimit,MaxRSS -P > "$RUN/pins/sacct_$PREV.tsv" 2>&1 || true
cat "$RUN/pins/sacct_$PREV.tsv"
for ARM in ctl_jug large_jug large_rad3; do
  echo "arm $ARM  Bl0_files=$(ls "$RUN/out$ARM/geom"/*.Bl0 2>/dev/null | wc -l)  rows=$([ -f "$RUN/out$ARM/pieces66.tsv" ] && echo $(($(wc -l < "$RUN/out$ARM/pieces66.tsv") - 1)) || echo none)"
done
echo "--- main job log tail"
tail -6 "$RUN/logs/slurm-$PREV.out" 2>/dev/null

step "B. extract $NEW into RUN/build/axes_src (tar overwrites; nothing deleted)"
BTX="$RUN/build/axes_src"
mkdir -p "$BTX"
git -C "$CANON" archive "$NEW" 2>>"$RUN/logs/axes_tools.log" | tar -x -C "$BTX" 2>>"$RUN/logs/axes_tools.log"
[ -d "$BTX/sfs_axes" ] || { echo "FAIL B: sfs_axes not in the archive"; echo "follow-up failed: B" > "$RUN/FOLLOWUP-FAILED.txt"; exit 3; }
( cd "$BTX" && md5sum scripts/run_benchmark_172.py .scratch/juglet-breaklines/stage66/run_cell66.sh ) > "$RUN/pins/axes_src.md5"
cat "$RUN/pins/axes_src.md5"

# ------------------------------------------------ C. the control, a second time (run-to-run spread)
step "C. control cell repeat (POT=Juglet, corpus inputs, GT axes) -> outctl2"
CELLDRV="$BTX/.scratch/juglet-breaklines/stage66/run_cell66.sh"
INSTR="$BTX/.scratch/juglet-breaklines/stage55/instruments"
MESH_BIN="$RUN/bin-$NEW/MeshPreprocessingHeadless"
EDGE_BIN="$RUN/bin-$NEW/EdgeLineExtractionHeadless"
STAGER="$RUN/tools/stage_synth_t331.sh"
[ -f "$MESH_BIN" ] && [ -f "$EDGE_BIN" ] && [ -f "$STAGER" ] || echo "WARN C: missing binaries or stager"
unset MESH_ROOT   # the control stages from the corpus mesh root, not the 3x copy root
( cd "$RUN" && env POT_NAME=Juglet PIECES="$JUG" WORNESS=0.7 MESH_ENV="" \
    OUT="$RUN/outctl2" CLOUD_DIR="$DS/Point/Juglet" MESH_DIR="$DS/Mesh/Juglet" AXIS_DIR="$GT" \
    MANIFEST="$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv" \
    MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points MAN_SPACING_COL=spacing_mm \
    INSTR="$INSTR" PY="$PY" DS="$DS" CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp \
    APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer \
    SIF="$CANON/pcl_191_nurbs.sif" STAGER="$STAGER" RUN="$RUN" JOBID="$JOBID" \
    MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" bash "$CELLDRV" ) > "$RUN/logs/cell_ctl2.log" 2>&1
RC2=$?
echo "cell ctl2 rc=$RC2 out=$RUN/outctl2"
tail -6 "$RUN/logs/cell_ctl2.log"
[ -f "$RUN/outctl2/pieces66.tsv" ] && cut -f1,5,6 "$RUN/outctl2/pieces66.tsv"

# --------------------------------------------------------------------------- D. axes per arm
step "D. axis estimator on each arm's own walls (shipped arguments)"
for pair in "ctl_jug|$GT|ctl" "large_jug|$LG|large" "large_rad3|$LG|rad3"; do
  ARM=$(printf '%s' "$pair" | cut -d'|' -f1)
  AXT=$(printf '%s' "$pair" | cut -d'|' -f2)
  TAG=$(printf '%s' "$pair" | cut -d'|' -f3)
  G="$RUN/out$ARM/geom"
  SUM="$RUN/axes_$TAG/axes_summary_$TAG.tsv"
  if [ -f "$SUM" ] && [ "$(($(wc -l < "$SUM") - 1))" -ge 9 ]; then
    echo "axes $TAG SKIPPED (already complete: $SUM)"
    continue
  fi
  if [ -d "$G" ] && [ -n "$(ls "$G"/*.S0 2>/dev/null)" ]; then
    echo "--- axes $TAG on $(ls "$G"/*.S0 | wc -l) walls"
    $PY "$RUN/tools/run_axes_t331.py" --tree "$BTX" --geom "$G" --out "$RUN/axes_$TAG" --gt "$AXT" --tag "$TAG" > "$RUN/logs/axes_$TAG.log" 2>&1
    echo "axes $TAG rc=$? pieces=$(ls "$RUN/axes_$TAG"/*_Axis.xyz 2>/dev/null | wc -l)"
    grep -a '^\[AXES\]' "$RUN/logs/axes_$TAG.log" | tail -10
    [ -f "$SUM" ] && cat "$SUM"
  else
    echo "axes $TAG SKIPPED (no walls at $G)"
  fi
done

# ------------------------------------------------------------------ E. the matched-stretch tables
step "E. matched stretch, both arms and the control repeat"
$PY "$RUN/tools/stretch_t331.py" --geom-large "$RUN/outlarge_jug/geom" --key-large "$LG" \
   --geom-ctl "$RUN/outctl_jug/geom" --key-ctl "$GT" --out "$RUN/out/stretch" > "$RUN/logs/stretch.log" 2>&1
echo "stretch (ctl vs ctl2) rc=$?"
grep -a '^SUMMARY' "$RUN/logs/stretch.log"
if [ -f "$RUN/outctl2/geom/Juglet_Piece_1.Bl0" ]; then
  $PY "$RUN/tools/stretch_t331.py" --geom-large "$RUN/outlarge_jug/geom" --key-large "$LG" \
     --geom-ctl "$RUN/outctl2/geom" --key-ctl "$GT" --out "$RUN/out/stretch_ctl2" > "$RUN/logs/stretch_ctl2.log" 2>&1
  echo "stretch (ctl2 vs large) rc=$?"
  grep -a '^SUMMARY' "$RUN/logs/stretch_ctl2.log"
fi

# ----------------------------------------------------------------------- F. the dot-count table
step "F. dot-count table"
$PY - "$RUN" > "$RUN/out/dotcounts.tsv" 2>>"$RUN/logs/summary.log" <<'PYEOF'
import os, sys
RUN = sys.argv[1]
ARMS = ['ctl_jug', 'ctl2', 'large_jug', 'large_rad3']
TICKET = [59, 32, 44, 31, 43, 45, 54, 40, 22]
data = {}
for a in ARMS:
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
cols = ['piece', 'ticket_t68'] + ['%s_bl0' % a for a in ARMS] + ['ratio_vs_ticket', 'ratio_vs_ctl', 'ratio_vs_ctl2']
print('\t'.join(cols))
for i in range(1, 10):
    P = 'Juglet_Piece_%d' % i
    def g(a, col='bl0_points'):
        r = data[a].get(P)
        return r.get(col, '') if r else ''
    def rat(num, den):
        try:
            return '%.4f' % (float(num) / float(den))
        except Exception:
            return ''
    lb = g('large_jug')
    print('\t'.join([P, str(TICKET[i-1]), g('ctl_jug'), g('ctl2'), lb, g('large_rad3'),
                     rat(lb, TICKET[i-1]), rat(lb, g('ctl_jug')), rat(lb, g('ctl2'))]))
print()
print('\t'.join(['piece', 'ctl_bl1', 'ctl2_bl1', 'large_bl1', 'rad3_bl1']))
for i in range(1, 10):
    P = 'Juglet_Piece_%d' % i
    def g(a, col='bl1_points'):
        r = data[a].get(P)
        return r.get(col, '') if r else ''
    print('\t'.join([P, g('ctl_jug'), g('ctl2'), g('large_jug'), g('large_rad3')]))
for a in ARMS:
    print('# %s: %s rows' % (a, len(data[a])))
PYEOF
cat "$RUN/out/dotcounts.tsv"

# ------------------------------------------------------- G. the corpus did not move (read-only)
step "G. read-only proof"
( cd "$LG" && md5sum Piece0*.obj Juglet_Piece_*_T.txt Juglet_Piece_*_Axis.xyz Juglet_simple_graph.txt scale_census.tsv scale_checks.json ) > "$RUN/pins/juglet_large_after2.md5"
if diff -q "$RUN/pins/juglet_large.md5" "$RUN/pins/juglet_large_after2.md5" > /dev/null 2>&1; then echo "Juglet_large unchanged"; else echo "Juglet_large CHANGED or no before-image"; fi
( cd "$GT" && md5sum * ) > "$RUN/pins/juglet_gt_after.md5"
( cd "$DS/Point/Juglet" && md5sum *.pcd ) > "$RUN/pins/juglet_cloud_after.md5"
( cd "$DS/Mesh/Juglet" && md5sum *.obj ) > "$RUN/pins/juglet_mesh_after.md5"
wc -l "$RUN/pins/juglet_gt_after.md5" "$RUN/pins/juglet_cloud_after.md5" "$RUN/pins/juglet_mesh_after.md5"

echo
echo "[JOB] follow-up done $(date -u +%FT%TZ)"
