#!/bin/bash
#SBATCH --job-name=t59arm
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/logs/slurm-%j.err
# ticket 59 Stage 1+2 ARM run (job 4 of <=4 budget; stage0=34194028, control=34194631,
# pota-relabel OOM=34199355 whose chunked retry is folded in here).
# Steps: build BOTH binaries from pushed commit 638504b with the ONLY source change being
# the uploaded mesh_processing_headless.patched.cpp (diff recorded); pass U runs all nine
# Juglet pieces with every SFS_BREAK_STOP* variable unset (byte-identity gate vs the
# unpatched control passA on pieces whose flip draw matches); only if that gate passes,
# pass G re-runs the nine pieces with SFS_BREAK_STOP=1 (defaults 0.9/7.2/0.45/-0.4);
# check_separation.py scores both arms (exact t57 invocation); chunked Pot A relabel
# retry; Task-4 renders. Nothing is written into t55/t57/t54 run dirs; corpus read-only.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm
RUNID=20261102-1416_638504b_t59-breakstop-arm
NEW=638504bf4bb8559c689da463cd541c3a6103a8ea
IXTAG=t59-breakstop-arm
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CTL=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1155_638504b_t59-control-gateclosed
T55=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines
T57=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep
T54W=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1613_83edd76_t54-worness-dial/out/wall40
S0RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1144_638504b_t59-breakstop-stage0
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
IDX=$RUNS/index.tsv
JOBID=$SLURM_JOB_ID; [ -n "$JOBID" ] || JOBID=na
P=$SLURM_CPUS_PER_TASK; [ -n "$P" ] || P=8
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN SFS_SMOOTHNESS_DEG SFS_CURVATURE_THRESH SFS_REASSIGN_MODE SFS_WINDOW_REPORT SFS_MERGE_SCALE SFS_GROWTH_MODE SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK SFS_WORNESS SFS_AXIS_FILE SFS_STATUS_FILE POT_NAME SFS_BREAK_STOP SFS_BREAK_STOP_MIN_MM SFS_BREAK_STOP_MAX_MM SFS_BREAK_STOP_EPS_MM SFS_BREAK_STOP_EXIT_DOT 2>/dev/null || true

cd "$RUN" || exit 1
mkdir -p logs outU outG work out/png

fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > RUN-FAILED.txt
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"
  printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
  exit "$rc"
}
echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG new=$NEW host=$(hostname)"

md5_corpus() {
  local out=$1 f
  { for f in "$DS"/Point/Juglet/*.pcd "$DS"/Point/Juglet/MANIFEST_JUGLET_CC.tsv "$DS"/Mesh/Juglet/*.obj "$DS"/Axes/Juglet/*.xyz; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
    done
  } | sort -k2 > "$out"
}
md5_corpus inputs_before.md5

# ---- 1. fetch + verify commit, archive source
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
git -C "$CANON" rev-parse --verify --quiet "$NEW" > /dev/null 2>>logs/fetch.log || fail 2 "commit $NEW not in $CANON"

# ---- 2. instruments (same as control/t55)
ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 | tar -x -C "$ISRC" || fail 3 "git archive $NEW instruments failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage55/instruments
[ -d "$INSTR" ] || fail 3 "no stage55 instruments in commit $NEW"
STAGER=$INSTR/stage_synth_p40.sh
echo "[JOB] instruments: $(ls "$INSTR" | tr "
" " ")"

# ---- 3. build sources = archive of NEW + patched mesh_processing_headless.cpp
BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
SRCCPP=$(find "$BT" -name mesh_processing_headless.cpp | head -1)
[ -n "$SRCCPP" ] || fail 3 "mesh_processing_headless.cpp not in archive"
cp -f "$SRCCPP" work/mesh_orig.cpp
cp -f work/mesh_processing_headless.patched.cpp "$SRCCPP" || fail 3 "patched cpp upload missing"
md5sum work/mesh_processing_headless.patched.cpp "$SRCCPP" | tee work/patch_source.md5
diff -u work/mesh_orig.cpp "$SRCCPP" > work/patch.diff || true
echo "[JOB] patch: $(grep -c '^+[^+]' work/patch.diff) added lines, $(grep -c '^-[^-]' work/patch.diff) removed lines"

# ---- 4. build both binaries (patched tree)
( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless
) > logs/build.log 2>&1
BRC=$?
if [ "$BRC" -eq 0 ] && [ -x "$BT/build/MeshPreprocessingHeadless" ] && [ -x "$BT/build/EdgeLineExtractionHeadless" ]; then
  MESH_BIN=$RUN/bin-MeshPreprocessingHeadless
  EDGE_BIN=$RUN/bin-EdgeLineExtractionHeadless
  cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
  cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
  { echo "commit	$NEW (patched, see work/patch.diff)"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d" " -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d" " -f1)	$(stat -c %s "$EDGE_BIN") bytes"
    echo "control-unpatched-mesh	$(md5sum "$CTL/bin-MeshPreprocessingHeadless" | cut -d" " -f1)"
    echo "control-unpatched-edge	$(md5sum "$CTL/bin-EdgeLineExtractionHeadless" | cut -d" " -f1)"
  } > binaries.md5
  cat binaries.md5
else
  tail -40 logs/build.log || true
  fail 5 "patched build failed"
fi
export CANON CORP DS SIF APT PY RUN RUNID NEW IXTAG JOBID P MESH_BIN EDGE_BIN INSTR STAGER

RC_ANY=0

# ---- 5. pass U: gate CLOSED (all SFS_BREAK_STOP* unset by the top-level unset)
echo "[JOB] pass U: cells into outU (SFS_BREAK_STOP unset)"
PIECES="$JUG" WORNESS=0.7 OUT=$RUN/outU bash "$INSTR/run_cell55.sh" > "$RUN/logs/passU.cells.log" 2>&1
rcU=$?
tail -40 "$RUN/logs/passU.cells.log"
[ "$rcU" -ne 0 ] && echo "[JOB] WARN passU rc=$rcU"
: > "$RUN/passU.files.md5"
for f in "$RUN"/outU/geom/*; do
  [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/passU.files.md5"
done
grep -aH "Normals flipped" "$RUN"/outU/pieces/*/mesh.log | tr -d "\r" > "$RUN/passU.flips.txt" || true
cat "$RUN/passU.flips.txt"
N_S0U=$(ls "$RUN"/outU/geom/*.S0 2>/dev/null | wc -l)
echo "[JOB] passU S0 files: $N_S0U"

# ---- 6. identity gate: patched-unset vs unpatched control passA
GATE=gate-fail
if [ "$N_S0U" -eq 9 ]; then
"$PY" - <<'PYEOF'
import re, sys

def load_md5(p):
    d = {}
    try:
        for ln in open(p, errors="replace"):
            t = ln.rstrip("\n").split("\t")
            if len(t) >= 2:
                d[t[1].split("/")[-1]] = t[0]
    except FileNotFoundError:
        pass
    return d

def load_flips(p):
    d = {}
    try:
        for ln in open(p, errors="replace"):
            m = re.match(r"(Juglet_Piece_\d+)[^:]*:\s*Normals flipped:\s*(\S+)", ln.strip())
            if m:
                d[m.group(1)] = m.group(2).lower() in ("1", "true", "yes", "on")
    except FileNotFoundError:
        pass
    return d

RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm"
CTL = "/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1155_638504b_t59-control-gateclosed"
U = load_md5(RUN + "/passU.files.md5")
A = load_md5(CTL + "/passA.files.md5")
fu = load_flips(RUN + "/passU.flips.txt")
fa = load_flips(CTL + "/passA.flips.txt")
rows, hard = [], 0
for k in range(1, 10):
    p = "Juglet_Piece_%d" % k
    for ext in ("S0", "S1", "Bl0", "Bl1"):
        n = p + "." + ext
        u, a = U.get(n, "-"), A.get(n, "-")
        if u == a and u != "-":
            v = "EQ"
        elif ext in ("S0", "S1"):
            v = "FLIP-LOTTERY" if fu.get(p) != fa.get(p) else "GATE-FAIL"
            if v == "GATE-FAIL":
                hard += 1
        else:
            v = "bl-nondeterministic (pre-existing, not gated)"
        rows.append((n, u[:12], a[:12], str(fu.get(p)), str(fa.get(p)), v))
with open(RUN + "/identity_gate.tsv", "w") as f:
    f.write("file\tU_md5\tcontrolA_md5\tflipU\tflipA\tverdict\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print("identity gate: %d hard S0/S1 mismatches beyond flip lottery" % hard)
gp = RUN + ("/gate.pass" if hard == 0 else "/gate.failnote")
open(gp, "w").write("hard_mismatches=%d\n" % hard)
sys.exit(0 if hard == 0 else 1)
PYEOF
grc=$?
if [ "$grc" -eq 0 ]; then GATE=gate-pass; else GATE=gate-fail; fi
fi
echo "[JOB] identity gate: $GATE"
cat "$RUN/identity_gate.tsv" 2>/dev/null || true

# ---- 7. pass G: gate ARMED (SFS_BREAK_STOP=1, code defaults 0.9/7.2/0.45/-0.4)
if [ "$GATE" = "gate-pass" ]; then
  echo "[JOB] pass G: cells into outG with SFS_BREAK_STOP=1"
  SFS_BREAK_STOP=1 PIECES="$JUG" WORNESS=0.7 OUT=$RUN/outG bash "$INSTR/run_cell55.sh" > "$RUN/logs/passG.cells.log" 2>&1
  rcG=$?
  tail -40 "$RUN/logs/passG.cells.log"
  [ "$rcG" -ne 0 ] && { echo "[JOB] WARN passG rc=$rcG"; RC_ANY=$rcG; }
  : > "$RUN/passG.files.md5"
  for f in "$RUN"/outG/geom/*; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/passG.files.md5"
  done
  grep -aH "Normals flipped" "$RUN"/outG/pieces/*/mesh.log | tr -d "\r" > "$RUN/passG.flips.txt" || true
  grep -aH "[BREAK-59]" "$RUN"/outG/pieces/*/mesh.log | tr -d "\r" > "$RUN/passG.breakstop.txt" || true
  NB=$(wc -l < "$RUN/passG.breakstop.txt")
  echo "[JOB] [BREAK-59] marker lines in passG: $NB"
  head -40 "$RUN/passG.breakstop.txt"
  [ "$NB" -ge 9 ] || { echo "[JOB] WARN expected >=9 BREAK-59 markers, got $NB"; }
else
  echo "[JOB] pass G SKIPPED (identity gate did not pass)"
  : > "$RUN/passG.SKIPPED"
fi

# ---- 8. metrics: exact t57 check_separation invocation on U (and G if present)
run_metrics() {
  local arm=$1 geom=$2
  ( cd "$T57" && "$PY" check_separation.py --geom "$geom" --mesh-dir "$DS/Mesh/Juglet" \
      --walls "$T54W" --k 15 --out-tsv "$RUN/metrics_"$arm".tsv" --out-json "$RUN/metrics_"$arm".json" ) \
    > "$RUN/logs/metrics_"$arm".log" 2>&1
  local rc=$?
  echo "[JOB] metrics $arm rc=$rc"
  cat "$RUN/metrics_"$arm".tsv" 2>/dev/null || tail -20 "$RUN/logs/metrics_"$arm".log"
  return $rc
}
run_metrics U "$RUN/outU/geom" || RC_ANY=$?
[ -f "$RUN/passG.SKIPPED" ] || run_metrics G "$RUN/outG/geom" || RC_ANY=$?
echo "[JOB] baseline_t55 reference:"
head -12 "$T57/baseline_t55.tsv" 2>/dev/null || true

# ---- 9. Pot A relabel retry (chunked slab; independent rc)
if [ -f "$RUN/work/pota_relabel.py" ]; then
  ( cd "$RUN" && OMP_NUM_THREADS=$P "$PY" work/pota_relabel.py ) > "$RUN/logs/pota_relabel.log" 2>&1
  rcP=$?
  echo "[JOB] pota_relabel rc=$rcP"
  tail -25 "$RUN/logs/pota_relabel.log"
  [ "$rcP" -ne 0 ] && echo "[JOB] WARN pota_relabel failed (recorded, not fatal)"
else
  echo "[JOB] WARN pota_relabel.py missing"
fi

# ---- 10. Task-4 renders
RARGS=""
[ -f "$RUN/passG.SKIPPED" ] && RARGS="--skip-after"
( cd "$RUN" && "$PY" work/render59.py --mesh-dir "$DS/Mesh/Juglet" --labels "$S0RUN/out/labels" \
    --outU "$RUN/outU/geom" --outG "$RUN/outG/geom" --out "$RUN/out/png" $RARGS ) > "$RUN/logs/render59.log" 2>&1
rcR=$?
echo "[JOB] render59 rc=$rcR"; tail -15 "$RUN/logs/render59.log"
ls -la "$RUN/out/png" | head -30

# ---- 11. housekeeping
{
  echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"
  echo "host=$(hostname)"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "gate=$GATE passes=U(gate-closed,patched)$( [ -f "$RUN/passG.SKIPPED" ] || echo ",G(SFS_BREAK_STOP=1)")"
} > run-meta.txt
md5_corpus inputs_after.md5
diff inputs_before.md5 inputs_after.md5 > inputs.diff || true
[ -s inputs.diff ] && echo "[JOB] WARN frozen inputs changed" || echo "[JOB] frozen inputs unchanged"
printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
echo "[JOB] index row appended (verdict and human_note left empty)"
if [ "$RC_ANY" -ne 0 ]; then echo "[JOB] note: some measured steps returned non-zero (see logs)"; fi
echo "[JOB] complete rc=0"
