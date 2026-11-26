#!/bin/bash
#SBATCH --job-name=t09-build
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-build-%j.out
#SBATCH --error=logs/slurm-build-%j.err
#
# Surface Parity Ticket 09, Stage 1 -- build the three post-Ticket-09 targets from the
# pinned commit a50f8cc in the canonical checkout, run the dedupe unit test, pin the
# binaries, and capture the before-state of the frozen corpus (pots + t331 juglet).
# Submit from the run directory:  cd <RUN> && sbatch work/t09/build09.sbatch
set -euo pipefail

RUN=${SLURM_SUBMIT_DIR:?submit from the run directory}
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
T305=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2
T331=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large
NEW=a50f8cc0ebe17621e2ce32424808c7414c2d7bbf
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
LOGS=$RUN/logs

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
export OMP_NUM_THREADS=1
cd "$RUN"
mkdir -p "$LOGS" "$RUN/out" "$RUN/work/t09" "$RUN/pins" "$RUN/evidence"

fail() { local rc=$1; shift
  { echo "runid=$(basename "$RUN")"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "stage=build";
    echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED-build.txt"
  echo "[BUILD] FATAL rc=$rc $*"; exit "$rc"; }

echo "[BUILD] runid=$(basename "$RUN") job=$JOBID host=$(hostname) at $(date -u +%FT%TZ)"

# ---- the pinned commit: fetch if the node can, otherwise the login-node fetch stands ----
fetch_ok=0
for i in 1 2 3 4 5; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$LOGS/fetch.log" 2>&1; then
    fetch_ok=1; break
  fi
  sleep $((10 * i))
done
if [ "$fetch_ok" -eq 1 ]; then
  echo "[BUILD] fetch=ok"
else
  echo "[BUILD] fetch=offline-reused-local (compute node has no network; the login node fetched)"
fi
git -C "$CANON" cat-file -e "$NEW^{commit}" 2>>"$LOGS/fetch.log" || fail 2 "commit $NEW not in $CANON"
COMMIT_FULL=$(git -C "$CANON" rev-parse "$NEW")
[ "$COMMIT_FULL" = "$NEW" ] || fail 2 "commit resolves to $COMMIT_FULL, expected $NEW"
echo "[BUILD] commit verified: $COMMIT_FULL" | tee "$LOGS/build_step1.txt"
git -C "$CANON" log -1 --format='%H%n%s%n%ci' "$NEW" >> "$LOGS/build_step1.txt"

# ---- source from the pinned commit, then build inside the frozen SIF ----
BT=$RUN/build/src
rm -rf "$RUN/build"
mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
( cd "$BT/build" \
  && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
  && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless EdgeLineExtractionHeadless SurfaceDedupeTest
) > "$LOGS/build.log" 2>&1 || { grep -n -B2 -A8 -i "error" "$LOGS/build.log" | head -60 || true; fail 5 "build failed"; }

for t in MeshPreprocessingHeadless EdgeLineExtractionHeadless SurfaceDedupeTest; do
  [ -x "$BT/build/$t" ] || fail 5 "target $t not built (see logs/build.log)"
done
echo "[BUILD] three targets built: $(cd "$BT/build" && ls -l MeshPreprocessingHeadless EdgeLineExtractionHeadless SurfaceDedupeTest | awk '{print $9, $5}')"

MESH_BIN=$RUN/bin-MeshPreprocessingHeadless
EDGE_BIN=$RUN/bin-EdgeLineExtractionHeadless
TEST_BIN=$RUN/bin-SurfaceDedupeTest
cp -f "$BT/build/MeshPreprocessingHeadless" "$MESH_BIN"
cp -f "$BT/build/EdgeLineExtractionHeadless" "$EDGE_BIN"
cp -f "$BT/build/SurfaceDedupeTest" "$TEST_BIN"
{ printf "MeshPreprocessingHeadless\t%s\n" "$(sha256sum "$MESH_BIN" | cut -d" " -f1)"
  printf "EdgeLineExtractionHeadless\t%s\n" "$(sha256sum "$EDGE_BIN" | cut -d" " -f1)"
  printf "SurfaceDedupeTest\t%s\n" "$(sha256sum "$TEST_BIN" | cut -d" " -f1)"
} > "$RUN/binaries.sha256"
{ printf "MeshPreprocessingHeadless\t%s\n" "$(md5sum "$MESH_BIN" | cut -d" " -f1)"
  printf "EdgeLineExtractionHeadless\t%s\n" "$(md5sum "$EDGE_BIN" | cut -d" " -f1)"
} > "$RUN/binaries.md5"
cat "$RUN/binaries.sha256"

# ---- the dedupe unit test must pass inside the same SIF ----
( cd "$BT/build" && "$APT" exec --bind /data:/data "$SIF" ./SurfaceDedupeTest ) > "$LOGS/unit_test.txt" 2>&1 \
  || { tail -30 "$LOGS/unit_test.txt" || true; fail 6 "SurfaceDedupeTest failed"; }
CASES=$(grep -c -E "^CASE [^ ]+ PASS" "$LOGS/unit_test.txt" || true)
TAIL=$(grep -a "SURFACE-DEDUPE-09" "$LOGS/unit_test.txt" | tail -1 || true)
[ "$CASES" -eq 5 ] || fail 6 "expected 5 PASS cases, saw $CASES (see logs/unit_test.txt)"
case "$TAIL" in *"fail=0"*) ;; *) fail 6 "no fail=0 line in the unit test tail: $TAIL" ;; esac
echo "[BUILD] unit test: $CASES/5 PASS | $TAIL"

# ---- the frozen stagers the cells need, copied read-only from their runs ----
cp -f "$T305/work/stage305.sh" "$RUN/work/stage305.sh"
T80=/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on
cp -f "$T80/tools/stage_synth_t73.sh" "$RUN/work/stage_synth_t73.sh"
chmod +x "$RUN/work/stage305.sh" "$RUN/work/stage_synth_t73.sh"
{ printf "stage305.sh\t%s\t%s\n" "$(sha256sum "$T305/work/stage305.sh" | cut -d" " -f1)" "$T305/work/stage305.sh"
  printf "stage_synth_t73.sh\t%s\t%s\n" "$(sha256sum "$T80/tools/stage_synth_t73.sh" | cut -d" " -f1)" "$T80/tools/stage_synth_t73.sh"
  printf "run_cell66.sh\t%s\t%s\n" "$(sha256sum "$BT/.scratch/juglet-breaklines/stage66/run_cell66.sh" | cut -d" " -f1)" "build/src (commit a50f8cc)"
} > "$LOGS/stagers.sha256"
cat "$LOGS/stagers.sha256"

# ---- before-state of every frozen corpus file this ticket reads ----
PYTHONPATH="$SHIP/work:$SHIP/work/impl_t03:$SHIP/work/impl_t03/scripts" SFS_IMPL="$SHIP/work/impl_t03" \
  "$PY" "$SHIP/work/corpus_md5_t03.py" --out "$LOGS/corpus_inputs_before.md5" \
  || fail 7 "corpus_md5_t03.py failed"
( cd "$T331" && sha256sum cloud_mesh/*.pcd mesh_large/*.obj | sort -k2 ) > "$LOGS/t331_inputs_before.md5" \
  || fail 7 "t331 input manifest failed"
echo "[BUILD] corpus inputs before: $(wc -l < "$LOGS/corpus_inputs_before.md5") files; t331 inputs before: $(wc -l < "$LOGS/t331_inputs_before.md5") files"

cat > "$RUN/run.json" <<JSON
{
 "runid": "$(basename "$RUN")",
 "ticket": 9,
 "tag": "t09-own-surfaces",
 "stage": "1 build",
 "commit": "$NEW",
 "commit_full": "$COMMIT_FULL",
 "jobid": "$JOBID",
 "sif": "$SIF",
 "apptainer": "$APT",
 "python": "$PY",
 "build_log": "$LOGS/build.log",
 "unit_test": "$LOGS/unit_test.txt",
 "binaries_sha256": "$RUN/binaries.sha256",
 "corpus_inputs_before": "$LOGS/corpus_inputs_before.md5",
 "t331_inputs_before": "$LOGS/t331_inputs_before.md5",
 "fetch": "ok-or-login-node",
 "utc": "$(date -u +%FT%TZ)"
}
JSON
printf '%s\t%s\t%s\t%s\t\t\n' "$(basename "$RUN")" "$JOBID" "a50f8cc" "t09-own-surfaces" \
  >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
tail -1 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv

echo "[BUILD] complete at $(date -u +%FT%TZ)"
echo "T09-BUILD-OK"
