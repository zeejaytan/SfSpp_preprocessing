#!/bin/bash
#SBATCH --job-name=t59ctl
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1155_638504b_t59-control-gateclosed/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1155_638504b_t59-control-gateclosed/logs/slurm-%j.err
# ticket 59 Stage 1 CONTROL -- rebuild BOTH binaries UNPATCHED from the pushed ticket-59
# branch commit (mesh_processing_headless.cpp identical to t55's 05be12c), run all nine
# Juglet pieces through the shipped chain at SFS_WORNESS=0.7 TWICE (passA, passB) with no
# SFS_BREAK_STOP in the environment (the gate does not exist in this code), then compare
# out{A,B}/geom md5 by basename: A==B measures the mesh stage's own run-to-run spread on
# Juglet (checkNormalsIntersection draws 30 points from an unseeded random_device --
# t55 logs show Normals flipped=true on J1/J6/J8, false on the rest), and A vs the t55
# run-of-record files.md5 (basename-keyed) proves a fresh rebuild of this commit
# reproduces t55 byte-identically wherever the stage is deterministic. No renders here
# (Stage 2 renders); nothing written into t55/t57 run dirs; corpus read-only.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1155_638504b_t59-control-gateclosed
RUNID=20261102-1155_638504b_t59-control-gateclosed
NEW=638504bf4bb8559c689da463cd541c3a6103a8ea
IXTAG=t59-control-gateclosed
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T55=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
IDX=$RUNS/index.tsv
JOBID=$SLURM_JOB_ID; [ -n "$JOBID" ] || JOBID=na
P=$SLURM_CPUS_PER_TASK; [ -n "$P" ] || P=8
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY       SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES       SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN SFS_SMOOTHNESS_DEG       SFS_CURVATURE_THRESH SFS_REASSIGN_MODE SFS_WINDOW_REPORT SFS_MERGE_SCALE SFS_GROWTH_MODE       SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK SFS_WORNESS SFS_AXIS_FILE SFS_STATUS_FILE POT_NAME SFS_BREAK_STOP 2>/dev/null || true

cd "$RUN" || exit 1
mkdir -p logs outA outB

fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > RUN-FAILED.txt
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"
  exit "$rc"
}
echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG new=$NEW host=$(hostname)"

git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
git -C "$CANON" rev-parse --verify --quiet "$NEW" > /dev/null 2>>logs/fetch.log || fail 2 "commit $NEW not in $CANON"

ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 | tar -x -C "$ISRC" || fail 3 "git archive $NEW instruments failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage55/instruments
[ -d "$INSTR" ] || fail 3 "no stage55 instruments in commit $NEW"
STAGER=$INSTR/stage_synth_p40.sh
echo "[JOB] instruments from commit $NEW: $(ls "$INSTR" | tr "\n" " ")"

md5_corpus() {
  local out=$1 f
  { for f in "$DS"/Point/Juglet/*.pcd "$DS"/Point/Juglet/MANIFEST_JUGLET_CC.tsv "$DS"/Mesh/Juglet/*.obj "$DS"/Axes/Juglet/*.xyz; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
    done
  } | sort -k2 > "$out"
}
md5_corpus inputs_before.md5

BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
echo "[BUILD] both binaries from $NEW (unpatched)"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
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
  { echo "commit	$NEW"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d" " -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d" " -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > binaries.md5
  cat binaries.md5
  echo "[JOB] t55 binaries for the record:"
  cat "$T55/out/binaries.md5" || true
else
  tail -40 logs/build.log || true
  fail 5 "binary build failed (see logs/build.log)"
fi
export CANON CORP DS SIF APT PY RUN RUNID NEW IXTAG JOBID P MESH_BIN EDGE_BIN INSTR STAGER

RC_ANY=0
for PASS in A B; do
  OUT=$RUN/out$PASS
  export OUT
  echo "[JOB] pass $PASS: cells into $OUT"
  PIECES="$JUG" WORNESS=0.7 OUT=$OUT bash "$INSTR/run_cell55.sh" > "$RUN/logs/pass$PASS.cells.log" 2>&1
  rc=$?
  tail -40 "$RUN/logs/pass$PASS.cells.log"
  [ "$rc" -ne 0 ] && { echo "[JOB] WARN pass $PASS rc=$rc"; RC_ANY=$rc; }
  : > "$RUN/pass$PASS.files.md5"
  for f in "$OUT"/geom/*; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/pass$PASS.files.md5"
  done
  echo "[JOB] pass $PASS geom files: $(wc -l < "$RUN/pass$PASS.files.md5")"
  grep -aH "Normals flipped" "$OUT"/pieces/*/mesh.log | tr -d "\r" > "$RUN/pass$PASS.flips.txt" || true
  cat "$RUN/pass$PASS.flips.txt"
done
unset OUT

# ---- the control verdict: A vs B (determinism), A vs t55 (rebuild identity), basename-keyed

"$PY" - <<'EOF'
import sys
def load(p):
    d = {}
    try:
        for ln in open(p, "r", errors="replace"):
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 2:
                d[parts[1].split("/")[-1]] = parts[0]
    except FileNotFoundError:
        pass
    return d
run = "/data/gpfs/projects/punim2657/SfSpp/runs"
A = load(run + "/20261102-1155_638504b_t59-control-gateclosed/passA.files.md5")
B = load(run + "/20261102-1155_638504b_t59-control-gateclosed/passB.files.md5")
T = {}
for ln in open(run + "/20261101-2004_05be12c_t55-worness07-breaklines/out/files.md5", "r", errors="replace"):
    parts = ln.rstrip("\n").split("\t")
    if len(parts) >= 2 and "/geom/" in parts[1]:
        T[parts[1].split("/")[-1]] = parts[0]
names = sorted(set(A) | set(B) | set(T))
rows = []
nAB = nAT = 0
for n in names:
    a, b, t = A.get(n, "-"), B.get(n, "-"), T.get(n, "-")
    eqab = "yes" if (a == b and a != "-") else ("both-absent" if a == b else "NO")
    eqat = "yes" if (a == t and a != "-") else ("both-absent" if a == t else "NO")
    if eqab == "yes": nAB += 1
    if eqat == "yes": nAT += 1
    rows.append((n, a[:12], b[:12], t[:12], eqab, eqat))
with open(run + "/20261102-1155_638504b_t59-control-gateclosed/control_verdict.tsv", "w") as f:
    f.write("file\tA_md5\tB_md5\tt55_md5\tA_eq_B\tA_eq_t55\n")
    for r in rows: f.write("\t".join(r) + "\n")
    f.write(f"# A_eq_B {nAB}/{len(names)}  A_eq_t55 {nAT}/{len(names)}\n")
print(f"control verdict: A_eq_B {nAB}/{len(names)}, A_eq_t55 {nAT}/{len(names)}")
EOF
cat control_verdict.tsv

{
  echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"
  echo "host=$(hostname)"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "passes=A,B unpatched gate-closed (SFS_BREAK_STOP unset and absent from code)"
} > run-meta.txt
md5_corpus inputs_after.md5
diff inputs_before.md5 inputs_after.md5 > inputs.diff || true
[ -s inputs.diff ] && echo "[JOB] WARN frozen inputs changed" || echo "[JOB] frozen inputs unchanged"
printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
echo "[JOB] index row appended (verdict and human_note left empty)"
if [ "$RC_ANY" -ne 0 ]; then echo "[JOB] FAILED: a pass returned non-zero"; exit "$RC_ANY"; fi
echo "[JOB] complete rc=0"
