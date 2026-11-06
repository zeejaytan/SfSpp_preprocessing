#!/bin/bash
#SBATCH --job-name=t311b2-k23
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=120G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 311 Stage B companion run: E_K2 (R1, R2) and E_K3 (R1, R2) on 4 dedicated
# 12-CPU slices (4 x 12 = 48 CPUs, matching NUMBER_OF_THREAD=12 in data_structure.h:18),
# with E_MO, E_BASE, E_K1, E_K6 staged in the same run to prove substitution.tsv.
set -uo pipefail

POT=E
NAMED=31
NP=31
FLOOR=50
ARMS="E_MO E_BASE E_K1 E_K2 E_K3 E_K6"
RUN_ARMS="E_K2 E_K3"
NREP=2

RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
GT="$CORP/Ground Truth"

RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
LANES=$RUNS/20261105-0445_9c5eec2_t305-lane-e2/out/geom
AX_MO=$CORP/Axes
AX_BASE=$RUNS/20261105-0532_d330469_t308a-axes/out/axes_paper
AX_310=$RUNS/20261105-1215_1a6f16e_t310b3-timing/out/axes310

WORK=$RUN/work
TREES=$RUN/trees
OUT=$RUN/out
SC=$RUN/score
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$WORK/axes_k" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID pot=$POT named=$NAMED np=$NP floor=$FLOOR start=$(date -u +%FT%TZ)"
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
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > "$RUN/logs/corpus_before.md5"

for K in 1 2 3 6; do
  mkdir -p "$WORK/axes_k/K$K"
  for f in "$AX_310"/Pot_E_Piece_*_Axis.xyz; do
    head -n "$K" "$f" > "$WORK/axes_k/K$K/$(basename "$f")"
  done
done

$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1 || fail 4 "guard patch failed"
$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
mkdir -p "$WORK/inc_$POT/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_$POT/class/data_path.h" "$POT" > logs/mk_inc.log 2>&1 || fail 6 "mk_inc failed"

stage_arm() {
  local A=$1 MODE=$2 AXD=$3
  for r in $(seq 1 "$NREP"); do
    local TDIR="$TREES/${A}R${r}"
    mkdir -p "$TDIR"
    $PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXD" \
        --out "$TDIR" --arms "$MODE" --named "$NAMED" --np "$NP" > "logs/stage_${A}R${r}.log" 2>&1 \
        || fail 7 "stage ${A}R${r} failed"
  done
}

stage_arm "E_MO"   "MO" "$AX_MO"
stage_arm "E_BASE" "MM" "$AX_BASE"
stage_arm "E_K1"   "MM" "$WORK/axes_k/K1"
stage_arm "E_K2"   "MM" "$WORK/axes_k/K2"
stage_arm "E_K3"   "MM" "$WORK/axes_k/K3"
stage_arm "E_K6"   "MM" "$WORK/axes_k/K6"

tree_path() {
  local L=$1
  case $L in
    E_MOR*) echo "$TREES/$L/E/MO";;
    *)      echo "$TREES/$L/E/MM";;
  esac
}

check_diff() {
  local f="logs/diff_$1.txt" tot axes other
  diff -rq -x arm_inputs.md5 "$2" "$3" > "$f" || true
  tot=$(grep -c . "$f" || true)
  axes=$(grep -c "/Axes/" "$f" || true)
  other=$(grep -v "/Axes/" "$f" | grep -c . || true)
  if [ "$other" -ne 0 ]; then fail 8 "$1 differs outside Axes/"; fi
  printf '%s\t%s\t%s\t%s\n' "$1" "$tot" "$axes" "$other" >> logs/substitution.tsv
}

printf 'comparison\tdiffering\tunder_axes\telsewhere\n' > logs/substitution.tsv
check_diff "E_MO_vs_E_BASE" "$(tree_path E_MOR1)" "$(tree_path E_BASER1)"
check_diff "E_MO_vs_E_K1"   "$(tree_path E_MOR1)" "$(tree_path E_K1R1)"
check_diff "E_MO_vs_E_K2"   "$(tree_path E_MOR1)" "$(tree_path E_K2R1)"
check_diff "E_MO_vs_E_K3"   "$(tree_path E_MOR1)" "$(tree_path E_K3R1)"
check_diff "E_MO_vs_E_K6"   "$(tree_path E_MOR1)" "$(tree_path E_K6R1)"
check_diff "E_K6_vs_E_K1"   "$(tree_path E_K6R1)" "$(tree_path E_K1R1)"
check_diff "E_K6_vs_E_K2"   "$(tree_path E_K6R1)" "$(tree_path E_K2R1)"
check_diff "E_K6_vs_E_K3"   "$(tree_path E_K6R1)" "$(tree_path E_K3R1)"
for A in $ARMS; do
  check_diff "${A}_R1_vs_R2" "$(tree_path ${A}R1)" "$(tree_path ${A}R2)"
done
cat logs/substitution.tsv

echo "[JOB] warming up /panel/build $(date -u +%FT%TZ)"
$APT exec --writable-tmpfs \
   --bind "$MAIN":/workspace --bind "$WORK":/panel \
   "$SIF" bash -c '
     mkdir -p /panel/build /panel/logs
     cd /panel/build
     cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
     make -j12 > /panel/logs/make.log 2>&1
   ' || fail 9 "cmake/make warm-up failed"
echo "[JOB] warm-up build complete $(date -u +%FT%TZ)"

# Compute 4 disjoint 12-CPU slices from this allocation's CPU affinity mask
mapfile -t SLICE_MASKS < <($PY -c '
import os
cpus = sorted(os.sched_getaffinity(0))
n = len(cpus)
k = 4
for i in range(k):
    sub = cpus[i*(n//k):(i+1)*(n//k)]
    print(",".join(str(c) for c in sub))
')

run_and_score() {
  local LABEL=$1 ARM=$2 MASK=$3
  local TREE
  TREE=$(tree_path "$LABEL")
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL mask=$MASK tree=$TREE $(date -u +%FT%TZ)"
  taskset -c "$MASK" $APT exec --writable-tmpfs \
     --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" "/panel/inc_$POT" "$NP" NONE > "logs/run_${LABEL}.log" 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$LABEL" "$FLOOR" "/panel/inc_$POT" "$TREE" "$NP" "$RC" "$DT" > "logs/panel_${LABEL}.row"
  echo "##### DONE $LABEL exit=$RC wall=${DT}s $(date -u +%FT%TZ)"
  if [ -d "$OUT/$LABEL" ]; then
    local PTS="$TREES/$LABEL/arm_pieces_$POT.tsv"
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc_${LABEL}.row" >> "logs/acc_${LABEL}.log" 2>&1
    [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
    $PY "$WORK/score305.py" "$OUT/$LABEL" "$GT" "$POT" "$PTS" "$SC/$LABEL.tsv" "$LABEL" >> "logs/score_${LABEL}.log" 2>&1
    $PY "$WORK/score311_cpp.py" "$OUT/$LABEL" "$GT" "$POT" "$SC/${LABEL}_cpp.json" "$LABEL" >> "logs/score_${LABEL}.log" 2>&1
  fi
}

pids=()
idx=0
for A in $RUN_ARMS; do
  for r in $(seq 1 "$NREP"); do
    mask="${SLICE_MASKS[$idx]}"
    run_and_score "${A}R${r}" "$A" "$mask" &
    pids+=($!)
    idx=$((idx + 1))
    sleep 1
  done
done

echo "[JOB] waiting for ${#pids[@]} parallel arm runs (4 x 12 CPUs)..."
for pid in "${pids[@]}"; do
  wait "$pid"
done

printf 'arm\tfloor\tinc\ttree\tnp\texit\twall_s\n' > logs/panel.tsv
printf 'label\ttime_s\tsherd\tedge\traw\n' > "$SC/acc.tsv"
for A in $RUN_ARMS; do
  for r in $(seq 1 "$NREP"); do
    L="${A}R${r}"
    [ -f "logs/panel_${L}.row" ] && cat "logs/panel_${L}.row" >> logs/panel.tsv
    [ -f "$SC/acc_${L}.row" ] && cat "$SC/acc_${L}.row" >> "$SC/acc.tsv"
  done
done

cat logs/panel.tsv
cat "$SC/acc.tsv"
$PY "$WORK/summarise311b.py" "$SC" > "$SC/summary311b.txt" 2>&1 || true
cat "$SC/summary311b.txt"

md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > logs/corpus_inputs.diff || true
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > "$RUN/logs/corpus_after.md5"
diff "$RUN/logs/corpus_before.md5" "$RUN/logs/corpus_after.md5" > logs/corpus.diff || true
echo "[JOB] complete at $(date -u +%FT%TZ)"
