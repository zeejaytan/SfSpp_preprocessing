#!/bin/bash
#SBATCH --job-name=t66adm
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
# Ticket 66. Build commit NEW (SFS_ADMIT_SIGN default ON), record binary md5s, then six cells,
# one binary:
#   jug  Juglet 1-9, SFS_WORNESS=0.7 SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 (t65 recipe)
#   pota Pot_A 01-08, shipped defaults (t41 run.json): released corpus cloud + corpus mesh +
#        Dataset/Axes/Pot_A axis (exactly the t41-pota inputs.md5)
#   potc Pot_C 01, shipped defaults: Dataset derived cloud (840,835 pts) + Dataset mesh + corpus axis
# each in arm U (SFS_ADMIT_SIGN unset = new default ON) and arm Z (SFS_ADMIT_SIGN=0 = OFF).
# Then: Part B md5 tables vs t65 outT/outC, Part C U-vs-Z tables, J1 scoring with the frozen
# t57 ruler + t65 sector/stage1 tools, J1 before/after figures.
# Submit with: sbatch -o $RUN/logs/slurm-%j.out -e $RUN/logs/slurm-%j.err --export=ALL,NEW=<sha>,RUNID=<id> submit66.sbatch
# Corpus read-only. Nothing is written outside this run directory.
set -uo pipefail

: "${NEW:?}" "${RUNID:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t66-admitsign-default
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
T65=$RUNS/20261103-0709_a47d478_t65-admitsign
T57=$RUNS/20261102-0450_05be12c_t57-sweep
T54W=$RUNS/20261101-1613_83edd76_t54-worness-dial/out/wall40
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
POTA="Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
POTC="Pot_C_Piece_01"
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done

cd "$RUN" || exit 1
mkdir -p logs work pins out/fig

fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"
  exit "$rc"
}
echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG new=$NEW host=$(hostname) start=$(date -u +%FT%TZ)"

md5_corpus() {
  local out=$1 f p
  { for f in "$DS"/Point/Juglet/*.pcd "$DS"/Point/Juglet/MANIFEST_JUGLET_CC.tsv "$DS"/Mesh/Juglet/*.obj "$DS"/Axes/Juglet/*.xyz \
             "$CORP"/Point/MANIFEST_released.tsv "$DS"/Point/Pot_C/Pot_C_Piece_01_Point.pcd "$DS"/Mesh/Pot_C/Pot_C_Piece_01_Mesh.obj \
             "$CORP"/Axes/Pot_C_Piece_01_Axis.xyz; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
    done
    for p in $POTA; do
      for f in "$CORP/Point/Pot_A/${p}_Point.pcd" "$CORP/Mesh/${p}_Mesh.obj" "$DS/Axes/Pot_A/${p}_Axis.xyz"; do
        [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
    done
  } | sort -k2 > "$out"
}
md5_corpus "$RUN/inputs_before.md5"

# Pot C 01's derived cloud is in no corpus manifest; it is pinned here to the md5 measured on
# 2026-11-03 before submission and the 840,835-point count recorded in SfSpp_preprocessing/AGENTS.md.
printf "piece\tpcd_md5\tkept_points\n" > pins/MANIFEST_potc_pinned.tsv
printf "Pot_C_Piece_01\t651dd0488038bcca65f6b57db6eb9861\t840835\n" >> pins/MANIFEST_potc_pinned.tsv

[ -x "$APT" ] || fail 5 "apptainer missing at $APT"
[ -f "$SIF" ] || fail 5 "sif missing at $SIF"

fetch_ok=0
for i in 1 2 3 4 5 6 7 8; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then fetch_ok=1; break; fi
  echo "[JOB] fetch retry $i" >> "$RUN/logs/fetch.log"; sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || fail 2 "git fetch failed"
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" > /dev/null 2>>"$RUN/logs/fetch.log" || fail 2 "commit $NEW not in $CANON"
echo "[JOB] commit verified: $(git -C "$CANON" rev-parse "$NEW")"

ISRC=$RUN/instrsrc
rm -rf "$ISRC"; mkdir -p "$ISRC"
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 .scratch/juglet-breaklines/stage66 | tar -x -C "$ISRC" || fail 3 "git archive instruments failed"
INSTR=$ISRC/.scratch/juglet-breaklines/stage66
STAGER=$ISRC/.scratch/juglet-breaklines/stage55/instruments/stage_synth_p40.sh
[ -f "$INSTR/run_cell66.sh" ] || fail 3 "run_cell66.sh missing"
[ -f "$STAGER" ] || fail 3 "stage_synth_p40.sh missing"

BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
grep -q "ADMIT-SIGN-66" "$BT/mesh_processing_headless.cpp" || fail 4 "ADMIT-SIGN-66 missing from archive"

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
  local name=$1 f
  : > "$RUN/pass${name}.files.md5"
  for f in "$RUN"/out${name}/geom/*; do
    [ -f "$f" ] && printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | cut -d" " -f1)" "$(basename "$f")" "$(stat -c %s "$f")" >> "$RUN/pass${name}.files.md5"
  done
  grep -aH "ADMIT-SIGN-65" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.admit65.txt" || true
  grep -aH "ADMIT-SIGN-66" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.admit66.txt" || true
  grep -aH "Normals flipped" "$RUN"/out${name}/pieces/*/mesh.log 2>/dev/null | tr -d "\r" > "$RUN/pass${name}.flips.txt" || true
  echo "[JOB] cell $name: $(ls "$RUN"/out${name}/geom/*.S0 2>/dev/null | wc -l) S0, $(ls "$RUN"/out${name}/geom/*.S1 2>/dev/null | wc -l) S1; ADMIT-SIGN-65 lines $(wc -l < "$RUN/pass${name}.admit65.txt"); ADMIT-SIGN-66 lines $(wc -l < "$RUN/pass${name}.admit66.txt")"
}

RC_ANY=0
UNSET="-u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR -u SFS_NORMAL_MODE -u SFS_NORMAL_RADIUS_MM"
run_cell() { # name admit(unset|0) pot pieces worness meshenv clouddir meshdir axisdir manifest md5col ptscol
  local name=$1 adm=$2 pot=$3 pcs=$4 w=$5 menv=$6 cdir=$7 mdir=$8 adir=$9 man=${10} mcol=${11} pcol=${12} extra rc
  if [ "$pot" = Juglet ]; then extra="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0"; else extra=""; fi
  local aenv="-u SFS_ADMIT_SIGN"
  [ "$adm" = 0 ] && aenv="SFS_ADMIT_SIGN=0"
  echo "[JOB] cell $name: pot=$pot admit=$adm worness=${w:-unset} extra=[$extra] mesh_env=[$menv]"
  # shellcheck disable=SC2086
  env $UNSET $aenv $extra POT_NAME="$pot" PIECES="$pcs" WORNESS="$w" MESH_ENV="$menv" OUT="$RUN/out$name" \
      CLOUD_DIR="$cdir" MESH_DIR="$mdir" AXIS_DIR="$adir" MANIFEST="$man" MAN_MD5_COL="$mcol" MAN_PTS_COL="$pcol" \
      bash "$INSTR/run_cell66.sh" > "$RUN/logs/pass$name.cells.log" 2>&1
  rc=$?
  echo "[JOB] cell $name rc=$rc"; tail -14 "$RUN/logs/pass$name.cells.log" || true
  [ "$rc" -ne 0 ] && RC_ANY=$rc
  record_cell "$name"
}

JMAN=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv
RMAN=$CORP/Point/MANIFEST_released.tsv
CMAN=$RUN/pins/MANIFEST_potc_pinned.tsv
for A in U Z; do
  adm=unset; [ "$A" = Z ] && adm=0
  run_cell "${A}_jug"  "$adm" Juglet "$JUG"  0.7 "" "$DS/Point/Juglet" "$DS/Mesh/Juglet" "$DS/Axes/Juglet" "$JMAN" pcd_md5 kept_points
  run_cell "${A}_pota" "$adm" Pot_A  "$POTA" ""  "$SHIPPED" "$CORP/Point/Pot_A" "$CORP/Mesh" "$DS/Axes/Pot_A" "$RMAN" md5 points
  run_cell "${A}_potc" "$adm" Pot_C  "$POTC" ""  "$SHIPPED" "$DS/Point/Pot_C" "$DS/Mesh/Pot_C" "$CORP/Axes" "$CMAN" pcd_md5 kept_points
done

# ---- Part B: arm U == t65 outT, arm Z == t65 outC, surfaces only
sfiles() { awk -F'\t' '$2 ~ /\.S[01]$/ {print $2"\t"$1}' "$1" | sort; }
for pr in "U_jug T" "Z_jug C"; do
  set -- $pr
  join -t $'\t' <(sfiles "$RUN/pass$1.files.md5") <(sfiles "$T65/pass$2.files.md5") \
    | awk -F'\t' '{print $1"\t"$2"\t"$3"\t"($2==$3?"same":"DIFF")}' > "$RUN/out/partB_$1_vs_t65$2.tsv"
  echo "[JOB] Part B $1 vs t65 $2: $(grep -c same "$RUN/out/partB_$1_vs_t65$2.tsv") same, $(grep -c DIFF "$RUN/out/partB_$1_vs_t65$2.tsv") DIFF of $(wc -l < "$RUN/out/partB_$1_vs_t65$2.tsv")"
done
# ---- Part C (and Juglet): U vs Z per surface
for c in jug pota potc; do
  join -t $'\t' <(sfiles "$RUN/passU_$c.files.md5") <(sfiles "$RUN/passZ_$c.files.md5") \
    | awk -F'\t' '{print $1"\t"$2"\t"$3"\t"($2==$3?"same":"DIFF")}' > "$RUN/out/UvsZ_$c.tsv"
  echo "[JOB] U vs Z $c: $(grep -c same "$RUN/out/UvsZ_$c.tsv") same, $(grep -c DIFF "$RUN/out/UvsZ_$c.tsv") DIFF"
done

# ---- Part D: score J1 (and all nine) with the frozen ruler + the t65 tools; render J1
cp -f "$T65"/work/t65_sector.py "$T65"/work/t65_stage1.py "$RUN/work/"
cp -f "$INSTR/t66_render.py" "$RUN/work/"
for A in U Z; do
  "$PY" "$T57/check_separation.py" --geom "$RUN/out${A}_jug/geom" \
      --mesh-dir /data/gpfs/projects/punim2657/Dataset/Mesh/Juglet --walls "$T54W" \
      --out-tsv "$RUN/out/sep_$A.tsv" --quiet 2> "$RUN/out/sep_$A.err"
  echo "[JOB] sep $A rc=$?"
done
( cd "$RUN/work" && "$PY" t65_sector.py "$RUN/out/sector" U="$RUN/outU_jug/geom" Z="$RUN/outZ_jug/geom" ) > "$RUN/out/sector.log" 2>&1; echo "[JOB] sector rc=$?"
( cd "$RUN/work" && "$PY" t65_stage1.py "$RUN/out/stage1" U="$RUN/outU_jug/geom" Z="$RUN/outZ_jug/geom" ) > "$RUN/out/stage1.log" 2>&1; echo "[JOB] stage1 rc=$?"
"$PY" "$RUN/work/t66_render.py" "$T65/outC/geom/Juglet_Piece_1.Bl0" "$RUN/outU_jug/geom/Juglet_Piece_1.Bl0" \
    "$T65/out/sector/j1_C.npz" "$RUN/out/fig" "$RUNID" > "$RUN/out/render.log" 2>&1; echo "[JOB] render rc=$?"; cat "$RUN/out/render.log"

{
  echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG"
  echo "host=$(hostname)"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mesh_md5=$(md5sum "$MESH_BIN" | cut -d" " -f1)"
  echo "edge_md5=$(md5sum "$EDGE_BIN" | cut -d" " -f1)"
  echo "rc_any=$RC_ANY"
} > "$RUN/run-meta.txt"
md5_corpus "$RUN/inputs_after.md5"
diff "$RUN/inputs_before.md5" "$RUN/inputs_after.md5" > "$RUN/inputs.diff" || true
[ -s "$RUN/inputs.diff" ] && echo "[JOB] WARN frozen inputs changed" || echo "[JOB] frozen inputs unchanged"
echo "[JOB] complete rc=$RC_ANY end=$(date -u +%FT%TZ)"
exit "$RC_ANY"
