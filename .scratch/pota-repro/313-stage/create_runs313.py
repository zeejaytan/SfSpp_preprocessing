#!/usr/bin/env python3
"""create_runs313.py -- create run directories and submit.sbatch for Ticket 313.

Stages:
  Stage B: Pot E K-ladder (E_MO, E_BASE, E_K1, E_K2, E_K3, E_K6), 2 repeats each
  Stage C: Non-regression gate across Pots A, B, D, G, I (MO:2, MM:2)
"""

import os
import shutil
import subprocess

RUNS_DIR = "/data/gpfs/projects/punim2657/SfSpp/runs"
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MAIN = "/data/gpfs/projects/punim2657/sfs_main"
SIF = f"{MAIN}/sfs_pristine_assembly.sif"
PY = "/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3"
SHIPPED = f"{MAIN}/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp"
GT = f"{CORP}/Ground Truth"
COMMIT = "fe906ab"
AX_313 = f"{RUNS_DIR}/20261106-1316_fe906ab_t313a-axes/out/axes313"
AX_MO = f"{CORP}/Axes"
AX_BASE = f"{RUNS_DIR}/20261105-0532_d330469_t308a-axes/out/axes_paper"
TEMPLATE_WORK = f"{RUNS_DIR}/20261106-0454_3695976_t311b-kladder-E/work"

POT_SPECS = {
    "E": {
        "tag": "t313b-kladder-E",
        "named": 31, "np": 31, "floor": 50,
        "cpus": 48, "mem": "160G", "time": "12:00:00",
        "lanes": f"{RUNS_DIR}/20261105-0445_9c5eec2_t305-lane-e2/out/geom",
        "is_kladder": True
    },
    "A": {
        "tag": "t313c-pota",
        "named": 8, "np": 8, "floor": 50,
        "cpus": 16, "mem": "64G", "time": "03:00:00",
        "lanes": f"{RUNS_DIR}/20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom",
        "is_kladder": False
    },
    "B": {
        "tag": "t313c-potb",
        "named": 9, "np": 9, "floor": 50,
        "cpus": 16, "mem": "64G", "time": "03:00:00",
        "lanes": f"{RUNS_DIR}/20261105-0445_9c5eec2_t305-lane-b2/out/geom",
        "is_kladder": False
    },
    "G": {
        "tag": "t313c-potg",
        "named": 7, "np": 7, "floor": 50,
        "cpus": 16, "mem": "64G", "time": "03:00:00",
        "lanes": f"{RUNS_DIR}/20261105-0445_9c5eec2_t305-lane-g2/out/geom",
        "is_kladder": False
    },
    "D": {
        "tag": "t313c-potd",
        "named": 29, "np": 29, "floor": 50,
        "cpus": 32, "mem": "96G", "time": "06:00:00",
        "lanes": f"{RUNS_DIR}/20261105-0445_9c5eec2_t305-lane-d2/out/geom",
        "is_kladder": False
    },
    "I": {
        "tag": "t313c-poti",
        "named": 30, "np": 30, "floor": 50,
        "cpus": 32, "mem": "96G", "time": "06:00:00",
        "lanes": f"{RUNS_DIR}/20261105-0520_9c5eec2_t305-lane-i3/out/geom",
        "is_kladder": False
    }
}

SCRIPTS_TO_COPY = [
    "acc305.py", "arm67.sh", "mk_inc.py", "patch_guard67.py",
    "score305.py", "score311_cpp.py", "stage305.py", "summarise311b.py"
]


def make_pote_sbatch(rundir, spec):
    return f"""#!/bin/bash
#SBATCH --job-name={spec['tag']}
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={spec['cpus']}
#SBATCH --mem={spec['mem']}
#SBATCH --time={spec['time']}
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 313 Stage B: Pot E K-ladder + both controls in one job:
#   E_MO    authors' released Axes/ (control: 31/31 + 62/62)
#   E_BASE  ticket 308 paper-chain axes (control: 21/31 + 36/62)
#   E_K1    normalized axes (axes313), top 1 line per piece
#   E_K2    normalized axes (axes313), top 2 lines per piece
#   E_K3    normalized axes (axes313), top 3 lines per piece
#   E_K6    normalized axes (axes313), top 6 lines per piece
# Two repeats per arm (R1, R2). Executed in 3 waves to prevent node throttling.
set -uo pipefail

POT=E
NAMED={spec['named']}
NP={spec['np']}
FLOOR={spec['floor']}
ARMS="E_MO E_BASE E_K1 E_K2 E_K3 E_K6"
NREP=2

RUN=$SLURM_SUBMIT_DIR
CORP={CORP}
MAIN={MAIN}
SIF={SIF}
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY={PY}
SHIPPED={SHIPPED}
GT="{GT}"

LANES={spec['lanes']}
AX_MO={AX_MO}
AX_BASE={AX_BASE}
AX_313={AX_313}

WORK=$RUN/work
TREES=$RUN/trees
OUT=$RUN/out
SC=$RUN/score
JOBID=${{SLURM_JOB_ID:-na}}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$WORK/axes_k" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID pot=$POT named=$NAMED np=$NP floor=$FLOOR start=$(date -u +%FT%TZ)"
{{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"; md5sum "$WORK"/*.py "$WORK"/arm67.sh 2>/dev/null; }} > logs/code.md5

fail() {{ local rc=$1; shift
  {{ echo "pot=$POT"; echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; }} > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }}

mesh_of() {{ local s=$1; if [ -f "$CORP/Mesh/${{s}}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${{s}}_Mesh_DS.obj"; else echo "$CORP/Mesh/${{s}}_Mesh.obj"; fi; }}
md5_inputs() {{ local out=$1 p stem
  {{ for p in $(seq 1 "$NAMED"); do
      stem=$(printf "Pot_%s_Piece_%02d" "$POT" "$p")
      for f in "$(mesh_of "$stem")" "$CORP/Axes/${{stem}}_Axis.xyz" \\
               "$CORP/Breaklines/${{stem}}_Breakline_0.pcd" "$CORP/Surfaces/${{stem}}_Surface_0.xyz" \\
               "$CORP/Surfaces/${{stem}}_Surface_1.xyz"; do
        [ -f "$f" ] && printf "%s\\t%s\\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
      [ -f "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt" ] && printf "%s\\t%s\\n" "$(md5sum "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt" | cut -d" " -f1)" "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt"
    done
  }} | sort -k2 > "$out"; }}

md5_inputs "$RUN/logs/corpus_inputs_before.md5"
{{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; }} | sort -k2 > "$RUN/logs/corpus_before.md5"

[ -f "$SIF" ] || fail 5 "SIF missing"
[ -f "$WORK/arm67.sh" ] || fail 5 "arm67.sh missing"
[ -d "$LANES" ] || fail 5 "lanes missing: $LANES"
[ -d "$AX_BASE" ] || fail 5 "AX_BASE missing: $AX_BASE"
[ -d "$AX_313" ] || fail 5 "AX_313 missing: $AX_313"

CR=$(printf '\\r')
for h in "$WORK/arm67.sh" "$WORK/stage305.py" "$WORK/mk_inc.py"; do
  if grep -q "$CR" "$h" 2>/dev/null; then fail 5 "helper carries CRLF: $h"; fi
done

# ---------- Build K1, K2, K3, K6 axis directories from AX_313 ----------
for K in 1 2 3 6; do
  mkdir -p "$WORK/axes_k/K$K"
  for f in "$AX_313"/Pot_E_Piece_*_Axis.xyz; do
    head -n "$K" "$f" > "$WORK/axes_k/K$K/$(basename "$f")"
  done
  echo "[JOB] K$K axes: $(ls "$WORK/axes_k/K$K"/*.xyz | wc -l) files, $(cat "$WORK/axes_k/K$K"/*.xyz | wc -l) total lines"
done

# ---------- Guarded base shim & include root ----------
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1 || fail 4 "guard patch failed"
diff -u "$SHIPPED" "$WORK/shim/G.cpp" > logs/diff_guard.txt 2>&1 || true

$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
[ -s "$WORK/inc_src/class/data_path.h" ] || fail 6 "could not extract data_path.h"
mkdir -p "$WORK/inc_$POT/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_$POT/class/data_path.h" "$POT" > logs/mk_inc.log 2>&1 || fail 6 "mk_inc failed"

# ---------- Stage trees for all 6 arms x 2 repeats ----------
stage_arm() {{
  local A=$1 MODE=$2 AXD=$3
  for r in $(seq 1 "$NREP"); do
    local TDIR="$TREES/${{A}}R${{r}}"
    mkdir -p "$TDIR"
    $PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXD" \\
        --out "$TDIR" --arms "$MODE" --named "$NAMED" --np "$NP" > "logs/stage_${{A}}R${{r}}.log" 2>&1 \\
        || fail 7 "stage ${{A}}R${{r}} failed"
  done
}}

stage_arm "E_MO"   "MO" "$AX_MO"
stage_arm "E_BASE" "MM" "$AX_BASE"
stage_arm "E_K1"   "MM" "$WORK/axes_k/K1"
stage_arm "E_K2"   "MM" "$WORK/axes_k/K2"
stage_arm "E_K3"   "MM" "$WORK/axes_k/K3"
stage_arm "E_K6"   "MM" "$WORK/axes_k/K6"

tree_path() {{
  local L=$1
  case $L in
    E_MOR*) echo "$TREES/$L/E/MO";;
    *)      echo "$TREES/$L/E/MM";;
  esac
}}

# ---------- Substitution checks ----------
check_diff() {{
  local f="logs/diff_$1.txt" tot axes other
  diff -rq -x arm_inputs.md5 "$2" "$3" > "$f" || true
  tot=$(grep -c . "$f" || true)
  axes=$(grep -c "/Axes/" "$f" || true)
  other=$(grep -v "/Axes/" "$f" | grep -c . || true)
  echo "[JOB] $1: $tot differing entries, $axes under Axes/, $other elsewhere"
  if [ "$other" -ne 0 ]; then
    echo "[JOB] FATAL $1 differs outside Axes/"
    grep -v "/Axes/" "$f" | head -10
    fail 8 "$1 differs outside Axes/"
  fi
  printf '%s\\t%s\\t%s\\t%s\\n' "$1" "$tot" "$axes" "$other" >> logs/substitution.tsv
}}

printf 'comparison\\tdiffering\\tunder_axes\\telsewhere\\n' > logs/substitution.tsv
check_diff "E_MO_vs_E_BASE" "$(tree_path E_MOR1)" "$(tree_path E_BASER1)"
check_diff "E_MO_vs_E_K1"   "$(tree_path E_MOR1)" "$(tree_path E_K1R1)"
check_diff "E_MO_vs_E_K2"   "$(tree_path E_MOR1)" "$(tree_path E_K2R1)"
check_diff "E_MO_vs_E_K3"   "$(tree_path E_MOR1)" "$(tree_path E_K3R1)"
check_diff "E_MO_vs_E_K6"   "$(tree_path E_MOR1)" "$(tree_path E_K6R1)"
for A in $ARMS; do
  check_diff "${{A}}_R1_vs_R2" "$(tree_path ${{A}}R1)" "$(tree_path ${{A}}R2)"
done
cat logs/substitution.tsv

# ---------- Warm up /panel/build ----------
echo "[JOB] warming up /panel/build $(date -u +%FT%TZ)"
$APT exec --writable-tmpfs \\
   --bind "$MAIN":/workspace --bind "$WORK":/panel \\
   "$SIF" bash -c '
     mkdir -p /panel/build /panel/logs
     cd /panel/build
     cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
     make -j8 > /panel/logs/make.log 2>&1
   ' || fail 9 "cmake/make warm-up failed"
[ -f "$WORK/build/CMakeCache.txt" ] || fail 9 "CMakeCache.txt missing after warm-up"
echo "[JOB] warm-up build complete $(date -u +%FT%TZ)"

# ---------- Run arms in waves ----------
export OMP_NUM_THREADS=8

run_and_score() {{
  local LABEL=$1 ARM=$2
  local TREE
  TREE=$(tree_path "$LABEL")
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs \\
     --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \\
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" "/panel/inc_$POT" "$NP" NONE > "logs/run_${{LABEL}}.log" 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$LABEL" "$FLOOR" "/panel/inc_$POT" "$TREE" "$NP" "$RC" "$DT" > "logs/panel_${{LABEL}}.row"
  echo "##### DONE $LABEL exit=$RC wall=${{DT}}s $(date -u +%FT%TZ)"
  if [ -d "$OUT/$LABEL" ]; then
    local PTS="$TREES/$LABEL/arm_pieces_$POT.tsv"
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc_${{LABEL}}.row" >> "logs/acc_${{LABEL}}.log" 2>&1
    [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
    $PY "$WORK/score305.py" "$OUT/$LABEL" "$GT" "$POT" "$PTS" "$SC/$LABEL.tsv" "$LABEL" >> "logs/score_${{LABEL}}.log" 2>&1
    $PY "$WORK/score311_cpp.py" "$OUT/$LABEL" "$GT" "$POT" "$SC/${{LABEL}}_cpp.json" "$LABEL" >> "logs/score_${{LABEL}}.log" 2>&1
  fi
}}

run_wave() {{
  local wave_name=$1
  shift
  local wave_arms=("$@")
  echo "=== STARTING WAVE $wave_name: ${{wave_arms[*]}} at $(date -u +%FT%TZ) ==="
  local pids=()
  for arm in "${{wave_arms[@]}}"; do
    local base_arm="${{arm%R*}}"
    run_and_score "$arm" "$base_arm" &
    pids+=($!)
    sleep 2
  done
  for pid in "${{pids[@]}}"; do
    wait "$pid"
  done
  echo "=== COMPLETED WAVE $wave_name at $(date -u +%FT%TZ) ==="
}}

# Wave 1: Controls and K1 (6 parallel runs)
run_wave "1_CONTROLS_K1" E_MOR1 E_MOR2 E_BASER1 E_BASER2 E_K1R1 E_K1R2

# Wave 2: K2 and K3 (4 parallel runs)
run_wave "2_K2_K3" E_K2R1 E_K2R2 E_K3R1 E_K3R2

# Wave 3: K6 (2 parallel runs, maximum compute)
run_wave "3_K6" E_K6R1 E_K6R2

# ---------- Compile final tables ----------
printf 'arm\\tfloor\\tinc\\ttree\\tnp\\texit\\twall_s\\n' > logs/panel.tsv
printf 'label\\ttime_s\\tsherd\\tedge\\traw\\n' > "$SC/acc.tsv"
for A in $ARMS; do
  for r in $(seq 1 "$NREP"); do
    L="${{A}}R${{r}}"
    [ -f "logs/panel_${{L}}.row" ] && cat "logs/panel_${{L}}.row" >> logs/panel.tsv
    [ -f "$SC/acc_${{L}}.row" ] && cat "$SC/acc_${{L}}.row" >> "$SC/acc.tsv"
  done
done

echo "=== panel.tsv ==="
cat logs/panel.tsv
echo "=== score/acc.tsv ==="
cat "$SC/acc.tsv"
$PY "$WORK/summarise311b.py" "$SC" > "$SC/summary311b.txt" 2>&1 || true
cat "$SC/summary311b.txt"

md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > logs/corpus_inputs.diff || true
if [ -s logs/corpus_inputs.diff ]; then echo "[JOB] WARN corpus_inputs changed"; cat logs/corpus_inputs.diff; else echo "[JOB] corpus inputs unchanged"; fi

{{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; }} | sort -k2 > "$RUN/logs/corpus_after.md5"
diff "$RUN/logs/corpus_before.md5" "$RUN/logs/corpus_after.md5" > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus unchanged"; fi

echo "[JOB] complete at $(date -u +%FT%TZ)"
"""


def make_pot_nonreg_sbatch(rundir, pot, spec):
    return f"""#!/bin/bash
#SBATCH --job-name={spec['tag']}
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={spec['cpus']}
#SBATCH --mem={spec['mem']}
#SBATCH --time={spec['time']}
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 313 Stage C: Pot {pot} non-regression run (MO:2, MM:2 in parallel).
set -uo pipefail

POT={pot}
NAMED={spec['named']}
NP={spec['np']}
FLOOR={spec['floor']}
ARMSPEC="MO:2 MM:2"

LANES={spec['lanes']}
AX_MO={AX_MO}
AX_313={AX_313}

RUN=$SLURM_SUBMIT_DIR
CORP={CORP}
MAIN={MAIN}
SIF={SIF}
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY={PY}
SHIPPED={SHIPPED}
GT="{GT}"

WORK=$RUN/work
TREES=$RUN/trees
OUT=$RUN/out
SC=$RUN/score
JOBID=${{SLURM_JOB_ID:-na}}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID pot=$POT named=$NAMED np=$NP floor=$FLOOR arms=$ARMSPEC"
{{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"; md5sum "$WORK"/*.py "$WORK"/arm67.sh 2>/dev/null; }} > logs/code.md5

fail() {{ local rc=$1; shift
  {{ echo "pot=$POT"; echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; }} > "$RUN/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }}

mesh_of() {{ local s=$1; if [ -f "$CORP/Mesh/${{s}}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${{s}}_Mesh_DS.obj"; else echo "$CORP/Mesh/${{s}}_Mesh.obj"; fi; }}
md5_inputs() {{ local out=$1 p stem
  {{ for p in $(seq 1 "$NAMED"); do
      stem=$(printf "Pot_%s_Piece_%02d" "$POT" "$p")
      for f in "$(mesh_of "$stem")" "$CORP/Axes/${{stem}}_Axis.xyz" \\
               "$CORP/Breaklines/${{stem}}_Breakline_0.pcd" "$CORP/Surfaces/${{stem}}_Surface_0.xyz" \\
               "$CORP/Surfaces/${{stem}}_Surface_1.xyz"; do
        [ -f "$f" ] && printf "%s\\t%s\\n" "$(md5sum "$f" | cut -d" " -f1)" "$f"
      done
      [ -f "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt" ] && printf "%s\\t%s\\n" "$(md5sum "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt" | cut -d" " -f1)" "$GT/Pot_${{POT}}_Piece_${{p}}_T.txt"
    done
  }} | sort -k2 > "$out"; }}

md5_inputs "$RUN/logs/corpus_inputs_before.md5"
{{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; }} | sort -k2 > "$RUN/logs/corpus_before.md5"

[ -f "$SIF" ] || fail 5 "SIF missing"
[ -f "$WORK/arm67.sh" ] || fail 5 "arm67.sh missing"
[ -d "$LANES" ] || fail 5 "lanes missing: $LANES"
[ -d "$AX_313" ] || fail 5 "AX_313 missing: $AX_313"

CR=$(printf '\\r')
for h in "$WORK/arm67.sh" "$WORK/stage305.py" "$WORK/mk_inc.py"; do
  if grep -q "$CR" "$h" 2>/dev/null; then fail 5 "helper carries CRLF: $h"; fi
done

# ---------- guarded base shim & inc ----------
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1 || fail 4 "guard patch failed"
diff -u "$SHIPPED" "$WORK/shim/G.cpp" > logs/diff_guard.txt 2>&1 || true

$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
[ -s "$WORK/inc_src/class/data_path.h" ] || fail 6 "could not extract data_path.h"
mkdir -p "$WORK/inc_$POT/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_$POT/class/data_path.h" "$POT" > logs/mk_inc.log 2>&1 || fail 6 "mk_inc failed"

# ---------- Stage trees ----------
stage_arm() {{
  local A=$1 MODE=$2 AXD=$3
  for r in $(seq 1 2); do
    local TDIR="$TREES/${{A}}R${{r}}"
    mkdir -p "$TDIR"
    $PY "$WORK/stage305.py" --pot "$POT" --corpus "$CORP" --lanes "$LANES" --axes "$AXD" \\
        --out "$TDIR" --arms "$MODE" --named "$NAMED" --np "$NP" > "logs/stage_${{A}}R${{r}}.log" 2>&1 \\
        || fail 7 "stage ${{A}}R${{r}} failed"
  done
}}

stage_arm "MO" "MO" "$AX_MO"
stage_arm "MM" "MM" "$AX_313"

tree_path() {{
  local L=$1
  case $L in
    MOR*) echo "$TREES/$L/$POT/MO";;
    MMR*) echo "$TREES/$L/$POT/MM";;
  esac
}}

check_diff() {{
  local f="logs/diff_$1.txt" tot axes other
  diff -rq -x arm_inputs.md5 "$2" "$3" > "$f" || true
  tot=$(grep -c . "$f" || true)
  axes=$(grep -c "/Axes/" "$f" || true)
  other=$(grep -v "/Axes/" "$f" | grep -c . || true)
  echo "[JOB] $1: $tot differing entries, $axes under Axes/, $other elsewhere"
  if [ "$other" -ne 0 ]; then
    echo "[JOB] FATAL $1 differs outside Axes/"
    grep -v "/Axes/" "$f" | head -10
    fail 8 "$1 differs outside Axes/"
  fi
  printf '%s\\t%s\\t%s\\t%s\\n' "$1" "$tot" "$axes" "$other" >> logs/substitution.tsv
}}

printf 'comparison\\tdiffering\\tunder_axes\\telsewhere\\n' > logs/substitution.tsv
check_diff "MO_vs_MM" "$(tree_path MOR1)" "$(tree_path MMR1)"
check_diff "MO_R1_vs_R2" "$(tree_path MOR1)" "$(tree_path MOR2)"
check_diff "MM_R1_vs_R2" "$(tree_path MMR1)" "$(tree_path MMR2)"
cat logs/substitution.tsv

# ---------- Warm up /panel/build ----------
echo "[JOB] warming up /panel/build $(date -u +%FT%TZ)"
$APT exec --writable-tmpfs \\
   --bind "$MAIN":/workspace --bind "$WORK":/panel \\
   "$SIF" bash -c '
     mkdir -p /panel/build /panel/logs
     cd /panel/build
     cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
     make -j8 > /panel/logs/make.log 2>&1
   ' || fail 9 "cmake/make warm-up failed"
[ -f "$WORK/build/CMakeCache.txt" ] || fail 9 "CMakeCache.txt missing after warm-up"
echo "[JOB] warm-up build complete $(date -u +%FT%TZ)"

# ---------- Run arms in parallel ----------
export OMP_NUM_THREADS=4

run_and_score() {{
  local LABEL=$1 ARM=$2
  local TREE
  TREE=$(tree_path "$LABEL")
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs \\
     --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \\
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" "/panel/inc_$POT" "$NP" NONE > "logs/run_${{LABEL}}.log" 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$LABEL" "$FLOOR" "/panel/inc_$POT" "$TREE" "$NP" "$RC" "$DT" > "logs/panel_${{LABEL}}.row"
  echo "##### DONE $LABEL exit=$RC wall=${{DT}}s $(date -u +%FT%TZ)"
  if [ -d "$OUT/$LABEL" ]; then
    local PTS="$TREES/$LABEL/arm_pieces_$POT.tsv"
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc_${{LABEL}}.row" >> "logs/acc_${{LABEL}}.log" 2>&1
    [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
    $PY "$WORK/score305.py" "$OUT/$LABEL" "$GT" "$POT" "$PTS" "$SC/$LABEL.tsv" "$LABEL" >> "logs/score_${{LABEL}}.log" 2>&1
    $PY "$WORK/score311_cpp.py" "$OUT/$LABEL" "$GT" "$POT" "$SC/${{LABEL}}_cpp.json" "$LABEL" >> "logs/score_${{LABEL}}.log" 2>&1
  fi
}}

pids=()
for arm in MOR1 MOR2 MMR1 MMR2; do
  base_arm="${{arm%R*}}"
  run_and_score "$arm" "$base_arm" &
  pids+=($!)
  sleep 2
done

for pid in "${{pids[@]}}"; do
  wait "$pid"
done

printf 'arm\\tfloor\\tinc\\ttree\\tnp\\texit\\twall_s\\n' > logs/panel.tsv
printf 'label\\ttime_s\\tsherd\\tedge\\traw\\n' > "$SC/acc.tsv"
for arm in MOR1 MOR2 MMR1 MMR2; do
  [ -f "logs/panel_${{arm}}.row" ] && cat "logs/panel_${{arm}}.row" >> logs/panel.tsv
  [ -f "$SC/acc_${{arm}}.row" ] && cat "$SC/acc_${{arm}}.row" >> "$SC/acc.tsv"
done

echo "=== panel.tsv ==="
cat logs/panel.tsv
echo "=== score/acc.tsv ==="
cat "$SC/acc.tsv"

md5_inputs "$RUN/logs/corpus_inputs_after.md5"
diff "$RUN/logs/corpus_inputs_before.md5" "$RUN/logs/corpus_inputs_after.md5" > logs/corpus_inputs.diff || true
if [ -s logs/corpus_inputs.diff ]; then echo "[JOB] WARN corpus_inputs changed"; cat logs/corpus_inputs.diff; else echo "[JOB] corpus inputs unchanged"; fi

{{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; }} | sort -k2 > "$RUN/logs/corpus_after.md5"
diff "$RUN/logs/corpus_before.md5" "$RUN/logs/corpus_after.md5" > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus unchanged"; fi

echo "[JOB] complete at $(date -u +%FT%TZ)"
"""


def main():
    timestamp = "20261106-1330"
    created_runs = []

    for pot, spec in POT_SPECS.items():
        run_name = f"{timestamp}_{COMMIT}_{spec['tag']}"
        rundir = os.path.join(RUNS_DIR, run_name)
        workdir = os.path.join(rundir, "work")
        logsdir = os.path.join(rundir, "logs")
        os.makedirs(workdir, exist_ok=True)
        os.makedirs(logsdir, exist_ok=True)

        # Copy work scripts
        for sc in SCRIPTS_TO_COPY:
            src = os.path.join(TEMPLATE_WORK, sc)
            dst = os.path.join(workdir, sc)
            if os.path.isfile(src):
                shutil.copy2(src, dst)

        with open(os.path.join(workdir, "code_commit.txt"), "w") as fh:
            fh.write(COMMIT + "\n")

        # Write run.json
        run_json = {
            "runid": run_name,
            "ticket": "313",
            "stage": f"{'B: Pot E K-ladder' if spec['is_kladder'] else f'C: Pot {pot} non-regression gate'}",
            "commit": COMMIT,
            "pot": pot,
            "named": spec["named"],
            "np": spec["np"],
            "floor": spec["floor"],
            "axes_313": AX_313
        }
        import json
        with open(os.path.join(rundir, "run.json"), "w") as fh:
            json.dump(run_json, fh, indent=2)

        # Write submit.sbatch
        sbatch_path = os.path.join(rundir, "submit.sbatch")
        if spec["is_kladder"]:
            content = make_pote_sbatch(rundir, spec)
        else:
            content = make_pot_nonreg_sbatch(rundir, pot, spec)

        with open(sbatch_path, "w", newline="\n") as fh:
            fh.write(content)

        created_runs.append((pot, run_name, rundir))
        print(f"[SETUP] Created run {run_name} for Pot {pot}")

    print("\n[SETUP] Ready to submit. Submitting jobs via sbatch...")
    submitted = []
    for pot, run_name, rundir in created_runs:
        sbatch_path = os.path.join(rundir, "submit.sbatch")
        res = subprocess.run(["sbatch", sbatch_path], cwd=rundir, capture_output=True, text=True)
        if res.returncode == 0:
            out = res.stdout.strip()
            # output is e.g. "Submitted batch job 34441234"
            job_id = out.split()[-1]
            with open(os.path.join(rundir, "sbatch.id"), "w") as fh:
                fh.write(job_id + "\n")
            print(f"[SUBMIT] Pot {pot}: Job ID {job_id} in {run_name}")
            submitted.append((pot, job_id, run_name, rundir))
        else:
            print(f"[SUBMIT ERROR] Pot {pot} failed: {res.stderr}")

    with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_313/submitted_jobs313.json", "w") as fh:
        import json
        json.dump(submitted, fh, indent=2)


if __name__ == "__main__":
    main()
