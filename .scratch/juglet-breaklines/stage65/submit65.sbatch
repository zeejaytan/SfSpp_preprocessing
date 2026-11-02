#!/bin/bash
#SBATCH --job-name=t65adm
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0709_a47d478_t65-admitsign/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0709_a47d478_t65-admitsign/logs/slurm-%j.err
# Ticket 65 stage 3. Build commit a47d478 unpatched (SFS_ADMIT_SIGN, default off), record binary
# md5s, then run all nine Juglet pieces at SFS_WORNESS=0.7, SFS_NORMAL_MODE=radius
# SFS_NORMAL_RADIUS_MM=1.0 (the t62 cell F recipe):
#   cell C -- SFS_ADMIT_SIGN unset (control; geom compared to t62 passF.files.md5)
#   cell T -- SFS_ADMIT_SIGN=1 (treatment)
# Corpus read-only. Nothing is written outside this run directory.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0709_a47d478_t65-admitsign
RUNID=20261103-0709_a47d478_t65-admitsign
NEW=a47d47872978062a710480524f4c604560883c40
IXTAG=t65-admitsign
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T62F=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0035_ca520fe_t62-normalfix-s2/passF.files.md5
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY SFS_NORMAL_DUMP_DIR SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN SFS_SMOOTHNESS_DEG SFS_CURVATURE_THRESH SFS_REASSIGN_MODE SFS_WINDOW_REPORT SFS_MERGE_SCALE SFS_GROWTH_MODE SFS_GROWTH_FORMULA SFS_GROWTH_CAP SFS_GROWTH_WALK SFS_WORNESS SFS_AXIS_FILE SFS_STATUS_FILE POT_NAME SFS_BREAK_STOP SFS_BREAK_STOP_MIN_MM SFS_BREAK_STOP_MAX_MM SFS_BREAK_STOP_EPS_MM SFS_BREAK_STOP_EXIT_DOT SFS_NORMAL_MODE SFS_NORMAL_RADIUS_MM SFS_NORMAL_RADIUS_MULT SFS_NORMAL_MIN_K SFS_NORMAL_MAX_K SFS_NBRS_FILE SFS_DEDUPE SFS_ADMIT_SIGN 2>/dev/null || true

cd "$RUN" || exit 1
mkdir -p logs work outC outT

fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"
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
md5_corpus "$RUN/inputs_before.md5"

[ -x "$APT" ] || fail 5 "apptainer missing at $APT"
[ -f "$SIF" ] || fail 5 "sif missing at $SIF"

fetch_ok=0
for i in 1 2 3 4 5 6 7 8; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then
    fetch_ok=1
    break
  fi
  echo "[JOB] fetch retry $i" >> "$RUN/logs/fetch.log"
  sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || fail 2 "git fetch failed"
git -C "$CANON" rev-parse --verify --quiet "$NEW" > /dev/null 2>>"$RUN/logs/fetch.log" || fail 2 "commit $NEW not in $CANON"
echo "[JOB] commit verified: $(git -C "$CANON" rev-parse "$NEW")"

ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 | tar -x -C "$ISRC" || fail 3 "git archive instruments failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage55/instruments
STAGER=$INSTR/stage_synth_p40.sh
[ -f "$INSTR/run_cell55.sh" ] || fail 3 "run_cell55.sh missing"
[ -f "$STAGER" ] || fail 3 "stage_synth_p40.sh missing"

BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
grep -q g_admitSign65 "$BT/mesh_processing_headless.cpp" || fail 4 "g_admitSign65 missing from archive"

echo "[JOB] build: $APT exec --bind /data:/data $SIF cmake -DCMAKE_BUILD_TYPE=Release .. && make -j$P MeshPreprocessingHeadless EdgeLineExtractionHeadless"
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
  { echo "commit	$NEW (unpatched)"
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d" " -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d" " -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > "$RUN/binaries.md5"
  cat "$RUN/binaries.md5"
else
  grep -n -B2 -A6 "error" "$RUN/logs/build.log" | head -80 || true
  fail 5 "build failed rc=$BRC"
fi
export CANON CORP DS SIF APT PY RUN RUNID NEW IXTAG JOBID P MESH_BIN EDGE_BIN INSTR STAGER

record_cell() {
  local name=$1
  : > "$RUN/pass${name}.files.md5"
  local f
  for f in "$RUN"/out${name}/geom/*; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/pass${name}.files.md5"
  done
  grep -aH "Normals flipped" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.flips.txt" || true
  grep -aH "ADMIT-SIGN-65" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.admit65.txt" || true
  grep -aH "WINDOW-26-FINAL" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.final26.txt" || true
  echo "[JOB] cell $name geom files: $(ls "$RUN"/out${name}/geom/*.S0 2>/dev/null | wc -l) S0; ADMIT-SIGN-65 lines: $(wc -l < "$RUN/pass${name}.admit65.txt")"
}

RC_ANY=0
UNSET="-u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR"

echo "[JOB] cell C env: SFS_WORNESS=0.7 SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 ; SFS_ADMIT_SIGN unset"
env $UNSET -u SFS_ADMIT_SIGN SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 \
    PIECES="$JUG" WORNESS=0.7 OUT="$RUN/outC" \
    bash "$INSTR/run_cell55.sh" > "$RUN/logs/passC.cells.log" 2>&1
rcC=$?
echo "[JOB] cell C rc=$rcC"; tail -12 "$RUN/logs/passC.cells.log" || true
[ "$rcC" -ne 0 ] && RC_ANY=$rcC
record_cell C

echo "[JOB] cell T env: SFS_WORNESS=0.7 SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_ADMIT_SIGN=1"
env $UNSET SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_ADMIT_SIGN=1 \
    PIECES="$JUG" WORNESS=0.7 OUT="$RUN/outT" \
    bash "$INSTR/run_cell55.sh" > "$RUN/logs/passT.cells.log" 2>&1
rcT=$?
echo "[JOB] cell T rc=$rcT"; tail -12 "$RUN/logs/passT.cells.log" || true
[ "$rcT" -ne 0 ] && RC_ANY=$rcT
record_cell T

# Control vs t62 cell F, surfaces only (Bl* come from the non-deterministic edge stage).
if [ -f "$T62F" ]; then
  join -1 2 -2 2 -t $'\t' <(awk -F'\t' '$2 ~ /\.S[01]$/' "$T62F" | sort -t $'\t' -k2,2) \
                          <(awk -F'\t' '$2 ~ /\.S[01]$/' "$RUN/passC.files.md5" | sort -t $'\t' -k2,2) \
    | awk -F'\t' '{print $1"\t"($2==$4?"same":"DIFF")"\t"$2"\t"$4}' > "$RUN/C_vs_t62F.S.tsv"
  echo "[JOB] control vs t62F surfaces: $(grep -c same "$RUN/C_vs_t62F.S.tsv") same, $(grep -c DIFF "$RUN/C_vs_t62F.S.tsv") diff"
fi

{
  echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"
  echo "host=$(hostname)"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "cells=C,T rcC=$rcC rcT=$rcT"
  echo "mesh_md5=$(md5sum "$MESH_BIN" | cut -d" " -f1)"
  echo "edge_md5=$(md5sum "$EDGE_BIN" | cut -d" " -f1)"
} > "$RUN/run-meta.txt"
md5_corpus "$RUN/inputs_after.md5"
diff "$RUN/inputs_before.md5" "$RUN/inputs_after.md5" > "$RUN/inputs.diff" || true
[ -s "$RUN/inputs.diff" ] && echo "[JOB] WARN frozen inputs changed" || echo "[JOB] frozen inputs unchanged"
echo "[JOB] complete rc=$RC_ANY"
exit "$RC_ANY"
