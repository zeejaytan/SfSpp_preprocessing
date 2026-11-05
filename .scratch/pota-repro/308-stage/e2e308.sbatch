#!/bin/bash
#SBATCH --job-name=t308b-e2e
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 308 Stage B -- ONE pot, three arms in one allocation so the prune effect is
# read off the same binary, the same include and the same session:
#   MO   our breaklines (lanes)  + authors' axes (corpus Axes)   <- ticket 308's "OO"
#   MM   our breaklines          + our axes, shipped default     <- ticket 308's "MM"
#   MMp  our breaklines          + our axes, SFS_AXES_COST_PRUNE=1 <- ticket 308's "MMp"
# N repeats per arm, floor 50 (the assembler's own), best-of-N reported.
# Pot A only (SEEDS != NONE): one extra MM tree per axis seed, one run each (B4).
# Trees are staged ONCE PER ARM (stage305.py rewrites its arm_pieces tsv per call), so
# the MO-vs-MM and MM-vs-MMp substitution is proved with diff -rq over the staged trees.
set -uo pipefail

POT=__POT__
NAMED=__NAMED__
NP=__NP__
FLOOR=__FLOOR__
ARMSPEC="__ARMSPEC__"
LANES=__LANES__
AXC=__AXC__
AXP=__AXP__
AXQ=__AXQ__
SEEDS=__SEEDS__
SEEDDIR=__SEEDDIR__

RUN=$SLURM_SUBMIT_DIR
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
GT="$CORP/Ground Truth"
WORK=$RUN/work
TC=$RUN/trees_c
TM=$RUN/trees_m
TP=$RUN/trees_p
TS=$RUN/trees_s
OUT=$RUN/out
SC=$RUN/score
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$TC" "$TM" "$TP" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID pot=$POT named=$NAMED np=$NP floor=$FLOOR arms=$ARMSPEC seeds=$SEEDS"
echo "[JOB] lanes=$LANES"
echo "[JOB] axes: control=$AXC paper=$AXP prune=$AXQ seeddir=$SEEDDIR"
{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"; md5sum "$WORK"/*.py "$WORK"/arm67.sh 2>/dev/null; } > logs/code.md5

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
  echo "--- lanes"; ls "$LANES" 2>/dev/null | head -3; md5sum "$LANES"/*.Bl0 2>/dev/null | head -40
  echo "--- control axes"; md5sum "$AXC"/*.xyz 2>/dev/null | head -40
  echo "--- paper axes"; md5sum "$AXP"/*.xyz 2>/dev/null | head -40
  echo "--- prune axes"; md5sum "$AXQ"/*.xyz 2>/dev/null | head -40
} > "$RUN/logs/provenance.log" 2>&1

[ -f "$SIF" ] || fail 5 "SIF missing"
[ -f "$WORK/arm67.sh" ] || fail 5 "arm67.sh missing from work/"
[ -d "$LANES" ] || fail 5 "lanes missing: $LANES"
[ -d "$AXP" ] || fail 5 "paper axes missing: $AXP"
[ -d "$AXQ" ] || fail 5 "prune axes missing: $AXQ"

# A CRLF helper is a silent zero-length arm run (every arm exits 2 in 0 s, the job still
# reads COMPLETED 0:0).  Catch it before spending the allocation.
CR=$(printf '\r')
for h in "$WORK/arm67.sh" "$WORK/stage305.py" "$WORK/mk_inc.py"; do
  if grep -q "$CR" "$h" 2>/dev/null; then fail 5 "helper carries CRLF: $h"; fi
done

# ---------- guarded base shim ----------
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1
GRC=$?
diff -u "$SHIPPED" "$WORK/shim/G.cpp" > logs/diff_guard.txt 2>&1
md5sum "$SHIPPED" "$WORK/shim/G.cpp" >> logs/guard.log
cat logs/guard.log
[ "$GRC" -eq 0 ] || fail 4 "guard patch failed rc=$GRC"

# ---------- include root ----------
$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
[ -s "$WORK/inc_src/class/data_path.h" ] || fail 6 "could not extract data_path.h from SIF"
mkdir -p "$WORK/inc_$POT/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_$POT/class/data_path.h" "$POT" > logs/mk_inc.log 2>&1
MRC=$?
cat logs/mk_inc.log
[ "$MRC" -eq 0 ] || fail 6 "mk_inc failed rc=$MRC"
grep -n "^#define POT_" "$WORK/inc_$POT/class/data_path.h" > logs/active_pot.log 2>&1
cat logs/active_pot.log

# ---------- the three trees, one stage305.py call each ----------
$PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXC" \
    --out "$TC" --arms MO --named "$NAMED" --np "$NP" > logs/stage_c.log 2>&1
[ $? -eq 0 ] || fail 7 "stage MO failed"
$PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXP" \
    --out "$TM" --arms MM --named "$NAMED" --np "$NP" > logs/stage_m.log 2>&1
[ $? -eq 0 ] || fail 7 "stage MM failed"
$PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXQ" \
    --out "$TP" --arms MM --named "$NAMED" --np "$NP" > logs/stage_p.log 2>&1
[ $? -eq 0 ] || fail 7 "stage MMp failed"
tail -2 logs/stage_c.log logs/stage_m.log logs/stage_p.log

if [ "$SEEDS" != "NONE" ]; then
  mkdir -p "$TS"
  for S in $(echo "$SEEDS" | tr ',' ' '); do
    $PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" \
        --axes "$SEEDDIR/paper_s$S" --out "$TS/$S" --arms MM --named "$NAMED" --np "$NP" \
        > "logs/stage_s$S.log" 2>&1
    echo "[JOB] seed $S tree rc=$? : $(ls "$TS/$S/$POT/MM/Axes" 2>/dev/null | wc -l) axes"
  done
fi

# ---------- B2: the substitution is axes-only ----------
check_diff() {  # $1=label $2=left $3=right
  local f="logs/diff_$1.txt" tot axes other
  diff -rq -x arm_inputs.md5 "$2" "$3" > "$f" || true
  tot=$(grep -c . "$f" || true)
  axes=$(grep -c "/Axes/" "$f" || true)
  other=$(grep -v "/Axes/" "$f" | grep -c . || true)
  echo "[JOB] $1: $tot differing entries, $axes under Axes/, $other elsewhere"
  if [ "$other" -ne 0 ]; then echo "[JOB] WARN $1 differs outside Axes/"; grep -v "/Axes/" "$f" | head -10; fi
  printf '%s\t%s\t%s\t%s\n' "$1" "$tot" "$axes" "$other" >> logs/substitution.tsv
}
printf 'comparison\tdiffering\tunder_axes\telsewhere\n' > logs/substitution.tsv
check_diff "MO_vs_MM" "$TC/$POT/MO" "$TM/$POT/MM"
check_diff "MM_vs_MMp" "$TM/$POT/MM" "$TP/$POT/MM"
if [ "$SEEDS" != "NONE" ]; then
  for S in $(echo "$SEEDS" | tr ',' ' '); do
    check_diff "MM_vs_seed$S" "$TM/$POT/MM" "$TS/$S/$POT/MM"
  done
fi
cat logs/substitution.tsv
cat "$TM/arm_pieces_$POT.tsv"

# ---------- arms ----------
printf 'arm\tfloor\tinc\ttree\tnp\texit\twall_s\n' > logs/panel.tsv
tree_for() { case $1 in
    MO) echo "$TC/$POT/MO";;
    MM) echo "$TM/$POT/MM";;
    MMp) echo "$TP/$POT/MM";;
    PAs*) echo "$TS/${1#PAs}/$POT/MM";;
    *) echo "";;
  esac; }
pts_for() { case $1 in
    MO) echo "$TC/arm_pieces_$POT.tsv";;
    MM) echo "$TM/arm_pieces_$POT.tsv";;
    MMp) echo "$TP/arm_pieces_$POT.tsv";;
    PAs*) echo "$TS/${1#PAs}/arm_pieces_$POT.tsv";;
    *) echo "";;
  esac; }
runarm() { local LABEL=$1 ARM=$2 TREE=$3
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
  [ -n "$TREE" ] || { echo "[JOB] SKIP unknown arm $ARM"; continue; }
  [ -d "$TREE" ] || { echo "[JOB] SKIP $ARM: tree $TREE absent"; continue; }
  for r in $(seq 1 "$NREP"); do runarm "${ARM}R${r}" "$ARM" "$TREE"; done
done
if [ "$SEEDS" != "NONE" ]; then
  for S in $(echo "$SEEDS" | tr ',' ' '); do
    TREE=$(tree_for "PAs$S")
    [ -d "$TREE" ] || { echo "[JOB] SKIP seed $S: tree absent"; continue; }
    runarm "PAs$S" "PAs$S" "$TREE"
  done
fi
cat logs/panel.tsv

# ---------- score ----------
printf 'label\ttime_s\tsherd\tedge\traw\n' > "$SC/acc.tsv"
score_one() { local LABEL=$1 ARM=$2
  [ -d "$OUT/$LABEL" ] || { echo "[JOB] no Result for $LABEL"; return 0; }
  local PTS; PTS=$(pts_for "$ARM")
  $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc.tsv" >> logs/acc.log 2>&1
  [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
  $PY "$WORK/score305.py" "$OUT/$LABEL" "$GT" "$POT" "$PTS" "$SC/$LABEL.tsv" "$LABEL" >> logs/score.log 2>&1
  echo "[JOB] scored $LABEL"; }
for spec in $ARMSPEC; do
  ARM=${spec%%:*}; NREP=${spec##*:}
  for r in $(seq 1 "$NREP"); do score_one "${ARM}R${r}" "$ARM"; done
done
if [ "$SEEDS" != "NONE" ]; then
  for S in $(echo "$SEEDS" | tr ',' ' '); do score_one "PAs$S" "PAs$S"; done
fi
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
