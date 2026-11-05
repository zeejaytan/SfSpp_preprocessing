#!/bin/bash
#SBATCH --job-name=t305-e2e
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
# Ticket 305 Stage 0/3 -- ONE pot, the four-arm grid (Breaklines, Axes) = OO/MO/OM/MM,
# N repeats per arm, floor 50 (the assembler's own), best-of-N reported.
#   O = authors' released input   M = ours from this ticket
# Vehicle: sfs_pristine_assembly.sif, patch_guard67.py k=5/b=3 shim (arm67.sh), pinned by md5.
# Ineligible pieces (no GT T file / empty breakline / empty axis) get a zero-byte axis file,
# i.e. shard_on_off=false, so each arm's denominators count only what it had.
# MMu (Pot A only) = the truncation-OFF comparator axes, everything else identical to MM.
# Report number = the assembler's own '1. Acc.txt'; score305.py is the strict diagnostic.
# Corpus read-only: md5 of every corpus input this pot reads, before and after.

# ---- baked by driver.py ----
set -uo pipefail

POT=A
NAMED=8
NP=8
FLOOR=50
ARMSPEC="MM:2"
LANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom
AXDIR=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0406_e6adf69_t307a-axes/out/pota/b5_s2
NOTRUNC=NONE

RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$SLURM_SUBMIT_DIR
IXTAG=t305-e2e-$POT
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
GT="$CORP/Ground Truth"
WORK=$RUN/work
TREES=$RUN/trees
TREES_U=$RUN/trees_u
OUT=$RUN/out
SC=$RUN/score
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID pot=$POT named=$NAMED np=$NP floor=$FLOOR arms=$ARMSPEC"
echo "[JOB] lanes=$LANES axes=$AXDIR notrunc=$NOTRUNC"

fail() { local rc=$1; shift
  { echo "pot=$POT"; echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }

mesh_of() { local s=$1; if [ -f "$CORP/Mesh/${s}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${s}_Mesh_DS.obj"; else echo "$CORP/Mesh/${s}_Mesh.obj"; fi; }
md5_inputs() { local out=$1 p stem
  { for p in $(seq 1 "$NAMED"); do
      stem=$(printf "Pot_%s_Piece_%02d" "$POT" "$p")
      for f in "$(mesh_of "$stem")" "$CORP/Axes/${stem}_Axis.xyz" \
               "$CORP/Breaklines/${stem}_Breakline_0.pcd" "$CORP/Surfaces/${stem}_Surface_0.xyz" \
               "$CORP/Surfaces/${stem}_Surface_1.xyz"; do
        [ -f "$f" ] && printf "%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
      [ -f "$GT/Pot_${POT}_Piece_${p}_T.txt" ] && printf "%s\t%s\n" "$(md5sum "$GT/Pot_${POT}_Piece_${p}_T.txt" | cut -d" " -f1)" "$GT/Pot_${POT}_Piece_${p}_T.txt"
    done
  } | sort -k2 > "$out"; }

md5_inputs "$RUN/logs/corpus_inputs_before.md5"

{
  echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- SIF"; ls -l "$SIF"; md5sum "$SIF"
  echo "--- shipped shim"; md5sum "$SHIPPED"
  echo "--- instruments"; md5sum "$WORK"/*.py "$WORK"/arm67.sh 2>/dev/null
  echo "--- lanes (our breaklines, read-only input)"; ls "$LANES" 2>/dev/null | head -3; md5sum "$LANES"/*.Bl0 2>/dev/null | head -40
  echo "--- our axes"; ls "$AXDIR" 2>/dev/null | head -3; md5sum "$AXDIR"/*.xyz 2>/dev/null | head -40
} > "$RUN/logs/provenance.log" 2>&1

[ -f "$SIF" ] || fail 5 "SIF missing"
[ -f "$WORK/arm67.sh" ] || fail 5 "arm67.sh missing from work/"
[ -d "$LANES" ] || fail 5 "lanes missing: $LANES"
[ -d "$AXDIR" ] || fail 5 "axes missing: $AXDIR"

# ---------- guarded base shim (k=5/b=3 + the two t67 guards) ----------
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1
GRC=$?
diff -u "$SHIPPED" "$WORK/shim/G.cpp" > logs/diff_guard.txt 2>&1
md5sum "$SHIPPED" "$WORK/shim/G.cpp" >> logs/guard.log
cat logs/guard.log
[ "$GRC" -eq 0 ] || fail 4 "guard patch failed rc=$GRC"

# ---------- include root: pristine header from the SIF, this pot activated ----------
$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
[ -s "$WORK/inc_src/class/data_path.h" ] || fail 6 "could not extract data_path.h from SIF"
mkdir -p "$WORK/inc_$POT/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_$POT/class/data_path.h" "$POT" > logs/mk_inc.log 2>&1
MRC=$?
cat logs/mk_inc.log
[ "$MRC" -eq 0 ] || fail 6 "mk_inc failed rc=$MRC"
grep -n "^#define POT_" "$WORK/inc_$POT/class/data_path.h" > logs/active_pot.log 2>&1
cat logs/active_pot.log

# ---------- the four-arm trees ----------
$PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXDIR" \
    --out "$TREES" --arms OO,MO,OM,MM --named "$NAMED" --np "$NP" > logs/stage.log 2>&1
SRC=$?
cat logs/stage.log
[ "$SRC" -eq 0 ] || fail 7 "stage305 failed rc=$SRC"
if [ "$NOTRUNC" != "NONE" ]; then
  $PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$NOTRUNC" \
      --out "$TREES_U" --arms MM --named "$NAMED" --np "$NP" > logs/stage_u.log 2>&1
  echo "[JOB] truncation-off tree rc=$?"; tail -3 logs/stage_u.log
fi
{ for a in OO MO OM MM; do echo "== $a"; md5sum "$TREES/$POT/$a/arm_inputs.md5" 2>/dev/null; done; } > logs/trees.md5 2>&1
cat "$TREES/arm_pieces_$POT.tsv"

# ---------- arms ----------
printf 'arm\tfloor\tinc\ttree\tnp\texit\twall_s\n' > logs/panel.tsv
tree_for() { case $1 in MMu) echo "$TREES_U/$POT/MM";; *) echo "$TREES/$POT/$1";; esac; }
runarm() { local LABEL=$1 TREE=$2
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" "/panel/inc_$POT" "$NP" NONE >> logs/panel.log 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$LABEL" "$FLOOR" "/panel/inc_$POT" "$TREE" "$NP" "$RC" "$DT" >> logs/panel.tsv
  echo "##### $LABEL exit=$RC wall=${DT}s"
  return 0; }

for spec in $ARMSPEC; do
  ARM=${spec%%:*}; NREP=${spec##*:}
  TREE=$(tree_for "$ARM")
  if [ ! -d "$TREE" ]; then echo "[JOB] SKIP $ARM: tree $TREE absent"; continue; fi
  for r in $(seq 1 "$NREP"); do runarm "${ARM}R${r}" "$TREE"; done
done
cat logs/panel.tsv

# ---------- score: the binary's own number, then the strict diagnostic ----------
printf 'label\ttime_s\tsherd\tedge\traw\n' > "$SC/acc.tsv"
for spec in $ARMSPEC; do
  ARM=${spec%%:*}; NREP=${spec##*:}
  for r in $(seq 1 "$NREP"); do
    LABEL="${ARM}R${r}"
    [ -d "$OUT/$LABEL" ] || { echo "[JOB] no Result for $LABEL"; continue; }
    PTS=$TREES/arm_pieces_$POT.tsv
    case "$ARM" in MMu) PTS=$TREES_U/arm_pieces_$POT.tsv;; esac
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc.tsv" >> logs/acc.log 2>&1
    $PY "$WORK/score305.py" "$OUT/$LABEL" "$GT" "$POT" "$PTS" \
        "$SC/$LABEL.tsv" "$LABEL" >> logs/score.log 2>&1
    echo "[JOB] scored $LABEL"
  done
done
echo "=== the counter's own numbers ==="; cat "$SC/acc.tsv"
echo "=== strict relative-edge diagnostic ==="; grep -H "^SUMMARY" "$SC"/*.tsv 2>/dev/null || true

md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > logs/corpus_inputs.diff || true
if [ -s logs/corpus_inputs.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus_inputs.diff; else echo "[JOB] corpus inputs unchanged"; fi

md5sum "$WORK/build/Hierarchy-"* > logs/binaries.md5 2>/dev/null || true
cat logs/binaries.md5
{ echo "pot=$POT"; echo "jobid=$JOBID"; echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)";
  echo "lane files: $(ls "$LANES"/*.Bl0 2>/dev/null | wc -l)"; } > "$RUN/run-meta.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"
