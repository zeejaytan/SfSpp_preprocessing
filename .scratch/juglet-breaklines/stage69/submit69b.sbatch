#!/bin/bash
#SBATCH --job-name=t69B-prep
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit69b.sbatch -- ticket 69 preprocessing: build the ticket-69 tree, prove the Part D
# defaults byte-for-byte, then run the density panel. STAGE selects which cells:
#   STAGE=all   build + Part D proof + all four cells (job 5, the default)
#   STAGE=prep  build + Part D proof + Pot A only
#   STAGE=rest  build + Pot C 4, Pot D 10, Pot J 11 only
#
# ONE mesh stage per piece feeds TWO edge stages: shipped (sphere 1.8 / resample 1.9) and
# densified (sphere 0.9 / resample 0.95). Varying only the edgeline constants on one staged
# surface pair is the only clean density comparison -- the mesh stage draws 30 unseeded
# ray-cast points (mesh_processing_headless.cpp:1526-1527), so two full chains are not the
# same input (t68 noise floor: identical geometry still moved a panel by 1 candidate).
#
# Submitted from the run directory with --export=ALL,NEW=<sha>,RUNID=<id>,STAGE=<prep|rest>.
# Corpus read-only; nothing written outside this run dir.
set -uo pipefail

: "${NEW:?}" "${RUNID:?}"
STAGE=${STAGE:-all}
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t69-axis-density-corpus
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}

POTA="Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
POTC="Pot_C_Piece_01 Pot_C_Piece_02 Pot_C_Piece_03 Pot_C_Piece_04"
POTD="Pot_D_Piece_01 Pot_D_Piece_02 Pot_D_Piece_03 Pot_D_Piece_04 Pot_D_Piece_05 Pot_D_Piece_06 Pot_D_Piece_07 Pot_D_Piece_08 Pot_D_Piece_09 Pot_D_Piece_10"
POTJ="Pot_J_Piece_01 Pot_J_Piece_02 Pot_J_Piece_03 Pot_J_Piece_04 Pot_J_Piece_05 Pot_J_Piece_06 Pot_J_Piece_07 Pot_J_Piece_08 Pot_J_Piece_09 Pot_J_Piece_10 Pot_J_Piece_11"
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done

cd "$RUN" || exit 1
mkdir -p logs work pins out/fig

fail() {
  local rc=$1; shift
  { echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "stage=$STAGE"; echo "commit=$NEW"; echo "tag=$IXTAG"; echo "rc=$rc"; echo "reason: $*"; date -u +"at %Y-%m-%dT%H:%M:%SZ"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see RUN-FAILED.txt)"; exit "$rc"
}
echo "[JOB] runid=$RUNID job=$JOBID stage=$STAGE tag=$IXTAG new=$NEW host=$(hostname) start=$(date -u +%FT%TZ)"

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
git -C "$CANON" archive "$NEW" .scratch/juglet-breaklines/stage55 .scratch/juglet-breaklines/stage66 .scratch/juglet-breaklines/stage69 | tar -x -C "$ISRC" || fail 3 "git archive instruments failed"
INS=$ISRC/.scratch/juglet-breaklines/stage69
STAGER=$INS/stage69_piece.sh
for f in run_cell69.sh stage69_piece.sh stage69_inputs.py; do [ -f "$INS/$f" ] || fail 3 "$f missing from the archive"; done

# ---------- build: the ticket-69 tree, both switches present and defaulted OFF ----------
BT=$RUN/build/src
rm -rf "$RUN/build"; mkdir -p "$BT/build"
git -C "$CANON" archive "$NEW" | tar -x -C "$BT" || fail 3 "git archive $NEW failed"
[ -d "$BT/alglib" ] || cp -a "$CANON/alglib" "$BT/alglib"
grep -q 'SFS_SPHERE_RADIUS_MM' "$BT/edgeline_extraction_headless.cpp" || fail 4 "SFS_SPHERE_RADIUS_MM missing from the archive"
grep -q 'SFS_RESAMPLE_D_MM' "$BT/edgeline_extraction_headless.cpp" || fail 4 "SFS_RESAMPLE_D_MM missing from the archive"
SPH=$(grep -c 'double sphereRadius = 1.8;' "$BT/edgeline_extraction_headless.cpp")
RSP=$(grep -c 'float RESAMPLE_D_MM = 1.9f;' "$BT/edgeline_extraction_headless.cpp")
[ "$SPH" -eq 1 ] || fail 4 "sphereRadius default literal count $SPH (want 1)"
[ "$RSP" -eq 1 ] || fail 4 "RESAMPLE_D_MM default literal count $RSP (want 1)"
{ echo "commit	$NEW"; echo "stage	$STAGE"; echo "sphere default literal count	$SPH"; echo "resample default literal count	$RSP";
  grep -n 'sphereRadius = 1.8;\|RESAMPLE_D_MM = 1.9f;\|SFS_SPHERE_RADIUS_MM\|SFS_RESAMPLE_D_MM' "$BT/edgeline_extraction_headless.cpp"; } > "$RUN/logs/switches.log" 2>&1
cat "$RUN/logs/switches.log"
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
    echo "MeshPreprocessingHeadless	$(md5sum "$MESH_BIN" | cut -d' ' -f1)	$(stat -c %s "$MESH_BIN") bytes"
    echo "EdgeLineExtractionHeadless	$(md5sum "$EDGE_BIN" | cut -d' ' -f1)	$(stat -c %s "$EDGE_BIN") bytes"
  } > "$RUN/binaries.md5"
  cat "$RUN/binaries.md5"
else
  grep -n -B2 -A6 "error" "$RUN/logs/build.log" | head -60 || true
  fail 5 "build failed rc=$BRC"
fi
export CANON CORP DS SIF APT PY RUN RUNID NEW IXTAG JOBID P MESH_BIN EDGE_BIN INS STAGER

# ---------- Part D proof: unset vs explicit defaults, one piece, byte identity ----------
if [ "$STAGE" = prep ] || [ "$STAGE" = all ]; then
PROOF=$RUN/proof
mkdir -p "$PROOF"
PS=$PROOF/stage_Pot_A_Piece_01
MESH_DIR_69=$CORP/Mesh bash "$STAGER" "$PS" Pot_A Pot_A_Piece_01 "$CORP/Axes/Pot_A_Piece_01_Axis.xyz" "$CORP/Point/Pot_A/Pot_A_Piece_01_Point.pcd" REAL-RELEASED-CLOUD > "$PROOF/stage.log" 2>&1 \
  || fail 6 "proof staging failed"
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_A SFS_AXIS_FILE="$PS/Dataset/Axes/Pot_A_Piece_01_Axis.xyz" SFS_STATUS_FILE="$PROOF/status.tsv" $SHIPPED "$MESH_BIN" > "$PROOF/mesh.log" 2>&1
[ $? -eq 0 ] || fail 6 "proof mesh stage failed"
grep -q 'PAPER-234] classify: face0' "$PROOF/mesh.log" || fail 6 "proof mesh stage missing the classify line"
printf 'run\tenv\tbl0_md5\tbl0_dots\tbl1_md5\tbl1_dots\n' > "$PROOF/proof.tsv"
proof_run() {
  local NAME=$1; shift
  rm -rf "$PS/Dataset/Breaklines/Pot_A"; mkdir -p "$PS/Dataset/Breaklines/Pot_A"
  ( cd "$PS" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_A "$@" "$EDGE_BIN" ) > "$PROOF/edge_$NAME.log" 2>&1
  local rc=$?
  local B0=$PS/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd
  local B1=$PS/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd
  local M0=absent M1=absent D0=- D1=-
  [ -f "$B0" ] && { M0=$(md5sum "$B0" | cut -d' ' -f1); D0=$(grep -am1 '^POINTS' "$B0" | awk '{print $2}'); }
  [ -f "$B1" ] && { M1=$(md5sum "$B1" | cut -d' ' -f1); D1=$(grep -am1 '^POINTS' "$B1" | awk '{print $2}'); }
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$NAME" "$*" "$M0" "$D0" "$M1" "$D1" >> "$PROOF/proof.tsv"
  echo "[PROOF] $NAME rc=$rc env=[$*] Bl0=$M0 ($D0 dots) Bl1=$M1 ($D1 dots)"
  grep -am2 'SPHERE-69\|RESAMPLE-69' "$PROOF/edge_$NAME.log" | tr -d '\r' | sed 's/^/[PROOF]   /' || true
}
proof_run unset
proof_run explicit SFS_SPHERE_RADIUS_MM=1.8 SFS_RESAMPLE_D_MM=1.9
UNSET_L0=$(awk -F'\t' '$1=="unset"{print $3}' "$PROOF/proof.tsv")
UNSET_L1=$(awk -F'\t' '$1=="unset"{print $5}' "$PROOF/proof.tsv")
EXPL_L0=$(awk -F'\t' '$1=="explicit"{print $3}' "$PROOF/proof.tsv")
EXPL_L1=$(awk -F'\t' '$1=="explicit"{print $5}' "$PROOF/proof.tsv")
PROOF_OK=no
if [ -n "$UNSET_L0" ] && [ "$UNSET_L0" = "$EXPL_L0" ] && [ "$UNSET_L1" = "$EXPL_L1" ]; then PROOF_OK=yes; fi
echo "[PROOF] byte identity unset vs explicit defaults: $PROOF_OK (Bl0 $UNSET_L0 vs $EXPL_L0; Bl1 $UNSET_L1 vs $EXPL_L1)"
printf 'unset_bl0\t%s\nunset_bl1\t%s\nexplicit_bl0\t%s\nexplicit_bl1\t%s\nidentical\t%s\n' \
  "$UNSET_L0" "$UNSET_L1" "$EXPL_L0" "$EXPL_L1" "$PROOF_OK" > "$PROOF/verdict.tsv"
cat "$PROOF/verdict.tsv"
rm -rf "$PS"
fi

# ---------- the density panel ----------
run_cell() { # name pot pieces worness meshenv clouddir meshdir axisdir manifest md5col ptscol
  local name=$1 pot=$2 pcs=$3 w=$4 menv=$5 cdir=$6 mdir=$7 adir=$8 man=$9 mcol=${10} pcol=${11} rc
  echo "[JOB] cell $name: pot=$pot pieces=$(echo $pcs | wc -w) worness=${w:-unset} mesh_env=[$menv]"
  env -u SFS_ADMIT_SIGN -u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K \
      -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR -u SFS_NORMAL_MODE -u SFS_NORMAL_RADIUS_MM \
      POT_NAME="$pot" PIECES="$pcs" WORNESS="$w" MESH_ENV="$menv" OUT="$RUN/out$name" \
      CLOUD_DIR="$cdir" MESH_DIR="$mdir" AXIS_DIR="$adir" MANIFEST="$man" MAN_MD5_COL="$mcol" MAN_PTS_COL="$pcol" \
      bash "$INS/run_cell69.sh" > "$RUN/logs/pass$name.cells.log" 2>&1
  rc=$?
  echo "[JOB] cell $name rc=$rc"; tail -6 "$RUN/logs/pass$name.cells.log" || true
  return $rc
}

RMAN=$CORP/Point/MANIFEST_released.tsv
RC_ANY=0
if [ "$STAGE" = prep ] || [ "$STAGE" = all ]; then
  # Pot A: the shipped t66 control's own axis dir (Dataset/Axes/Pot_A), corpus mesh
  run_cell _pota Pot_A "$POTA" "" "$SHIPPED" "$CORP/Point/Pot_A" "$CORP/Mesh" "$DS/Axes/Pot_A" "$RMAN" md5 points || RC_ANY=1
fi
if [ "$STAGE" = rest ] || [ "$STAGE" = all ]; then
  printf 'piece\tpcd_md5\tkept_points\n' > "$RUN/pins/MANIFEST_potc_pinned.tsv"
  for i in 01 02 03 04; do
    f=$CORP/Point/Pot_C/Pot_C_Piece_${i}_Point.pcd
    printf 'Pot_C_Piece_%s\t%s\t%s\n' "$i" "$(md5sum "$f" | cut -d' ' -f1)" "$(grep -am1 '^POINTS' "$f" | awk '{print $2}')" >> "$RUN/pins/MANIFEST_potc_pinned.tsv"
  done
  cat "$RUN/pins/MANIFEST_potc_pinned.tsv"
  run_cell _potc Pot_C "$POTC" "" "$SHIPPED" "$CORP/Point/Pot_C" "$CORP/Mesh" "$CORP/Axes" "$RUN/pins/MANIFEST_potc_pinned.tsv" pcd_md5 kept_points || RC_ANY=1
  run_cell _potd Pot_D "$POTD" "" "$SHIPPED" "$CORP/Point/Pot_D" "$CORP/Mesh" "$CORP/Axes" "$RMAN" md5 points || RC_ANY=1
  run_cell _potj Pot_J "$POTJ" "" "$SHIPPED" "$CORP/Point/Pot_J" "$CORP/Mesh" "$CORP/Axes" "$RMAN" md5 points || RC_ANY=1
fi

# ---------- record what every lane set is ----------
{ for C in pota potc potd potj; do
    for G in geom18 geom09; do
      for f in "$RUN/out$C/$G"/*; do [ -f "$f" ] && printf '%s\t%s\t%s bytes\n' "$(md5sum "$f" | cut -d' ' -f1)" "${f#$RUN/out$C/}" "$(stat -c %s "$f")"; done
    done
  done; } | sort -k2 > "$RUN/lanes.md5"
wc -l "$RUN/lanes.md5"

echo "=== t69b job finished stage=$STAGE $(date -u +%FT%TZ) rc_any=$RC_ANY"
exit $RC_ANY