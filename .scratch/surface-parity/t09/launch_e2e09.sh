#!/usr/bin/env bash
# Ticket 09 Stage 3: end-to-end runs on the axes extracted from the REGENERATED own surfaces.
#   usage: T09_RUN=<regen run dir> launch_e2e09.sh 3A|3B [DEP_JOBID]
# 3A = Pot E G D J + def_3x Juglet + jugsum; 3B = Pot A B C F H I.
# The two make-scripts are generated here (they are launch-time products, not ticket files).
# Only AX_318 (pot) and OWN/axes (juglet) are re-aimed at the regenerated axes; the arms,
# repeats, floors, scoring, src362 rig and per-pot cpus/mem stay exactly as the frozen
# Ticket 03 chain had them.
set -euo pipefail
STAGE=${1:?usage: launch_e2e09.sh 3A|3B [DEP_JOBID]}
DEP=${2:-}
RUN=${T09_RUN:?set T09_RUN to the t09-own-surfaces run directory}
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
SHIP=$RUNS/20261121-1319_2e951d9_t03-ship
GIT7=a50f8cc
STAMP=$(date -u +%Y%m%d-%H%M)
AXPOT=$RUN/out/axes09_own_regen
AXJUG=$RUN/out/axes09_juglet_def3x_regen
W=$RUN/work/t09
mkdir -p "$W"
test -d "$AXPOT" || { echo "missing $AXPOT (run extract09 first)" >&2; exit 1; }
test -d "$AXJUG" || { echo "missing $AXJUG (run extract09 first)" >&2; exit 1; }
cp -f "$SHIP/work/submit_t03_jugsum.sbatch" "$W/submit_t09_jugsum.sbatch"
export T09_RUN=$RUN

cat > "$W/make_t09_e2e.sh" <<'E2E'
#!/bin/bash
# Ticket 09 Stage 3 (pots): ten-pot end-to-end jobs on the axes extracted from the regenerated
# own surfaces at a50f8cc.  Derived from the frozen Ticket 03 make_t03_e2e.sh: ONLY AX_318 ->
# $AX03, the job-name, the ticket number and the t09 tags change; each pot keeps its t319 arms
# (<POT>_MOR1, <POT>_MOR2, <POT>_K3R1, <POT>_K3R2) and two repeats.
#   usage: T09_RUN=<regen run> make_t09_e2e.sh <STAMP> "A B C" [DEP]
set -euo pipefail
STAMP=$1
ONLY="${2:-A B C D E F G H I J}"
DEP="${3:-}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
GIT7=a50f8cc
AX03=${T09_RUN:?set T09_RUN}/out/axes09_own_regen
test -d "$AX03" || { echo "missing $AX03" >&2; exit 1; }
N=$(ls "$AX03" | grep -c '_Axis.xyz$' || true)
echo "axes09_own_regen: $N files (148 pot pieces in the ticket; non-GT pieces included)"
GT=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/"Ground Truth Axes"
MISS=0
for f in "$GT"/Pot_*_Axis.xyz; do
  S=$(basename "$f" _Axis.xyz)
  test -f "$AX03/${S}_Axis.xyz" || { echo "missing axis for GT stem $S" >&2; MISS=$((MISS+1)); }
done
test "$MISS" -eq 0 || { echo "$MISS of 141 GT stems have no axis file" >&2; exit 1; }
echo "all 141 GT pot stems present"

for P in $ONLY; do
  SRC=$RUNS/20261109-1426_ecd5bb8_t319-pot$P
  RUN=$RUNS/${STAMP}_${GIT7}_t09-pot$P
  mkdir -p "$RUN"/{logs,out,score,trees,work/axes_k3}
  ( cd "$SRC/work" && cp -r *.py arm67.sh shim inc_src "$RUN/work/" )
  SED="s#^AX_318=.*#AX_318=$AX03#; s#--job-name=t319-pot$P#--job-name=t09-pot$P#; s|^# Ticket 319:.*|# Ticket 09: pot end-to-end, MO control + axes extracted from the regenerated own surfaces at a50f8cc (no canonicalize), two repeats, derived from $SRC.|"
  case $P in
    D) SED="$SED; s|^#SBATCH --cpus-per-task=.*|#SBATCH --cpus-per-task=32|; s|^#SBATCH --mem=.*|#SBATCH --mem=64G|" ;;
    G|J) SED="$SED; s|^#SBATCH --cpus-per-task=.*|#SBATCH --cpus-per-task=16|; s|^#SBATCH --mem=.*|#SBATCH --mem=32G|" ;;
    E|I) SED="$SED; s|^#SBATCH --cpus-per-task=.*|#SBATCH --cpus-per-task=32|; s|^#SBATCH --mem=.*|#SBATCH --mem=64G|" ;;
  esac
  sed -e "$SED" "$SRC/submit.sbatch" > "$RUN/submit.sbatch"
  grep -q "^AX_318=$AX03" "$RUN/submit.sbatch"
  grep -q '_MOR1' "$RUN/submit.sbatch"
  cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 9, "pot": "$P", "tag": "t09-pot$P", "commit": "$GIT7",
 "axes": "$AX03", "arms": ["${P}_MOR1", "${P}_MOR2", "${P}_K3R1", "${P}_K3R2"], "template": "$SRC",
 "depends_on": "$DEP"}
EOF
  if [ -n "$DEP" ]; then
    JID=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$DEP submit.sbatch)
  else
    JID=$(cd "$RUN" && sbatch --parsable submit.sbatch)
  fi
  printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "$GIT7" "t09-pot$P" >> "$RUNS/index.tsv"
  echo "$P $(basename "$RUN") $JID"
done
E2E

cat > "$W/make_t09_juglet.sh" <<'E2EJ'
#!/bin/bash
# Ticket 09 Stage 3 (Juglet): build a 4-repeat def_3x juglet run from the t05-juglet rig
# (same src362.tar.gz, tools, floor-10 shim, staging, scoring, gates); only the axes change,
# to <regen run>/out/axes09_juglet_def3x_regen (native 3x tree units).
#   usage: T09_RUN=<regen run> make_t09_juglet.sh <STAMP> [DEP]
set -euo pipefail
STAMP=$1
DEP="${2:-}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
GIT7=a50f8cc
SRC=$RUNS/20261120-1106_9e0fe6a_t05-juglet
RUN=$RUNS/${STAMP}_${GIT7}_t09-juglet
AX=${T09_RUN:?set T09_RUN}/out/axes09_juglet_def3x_regen
STAGE=$(cd "$(dirname "$0")" && pwd)
test -d "$AX" || { echo "missing $AX" >&2; exit 1; }
N=$(ls "$AX" | grep -c 'Juglet_Piece_.*_Axis.xyz$' || true)
echo "axes09_juglet_def3x_regen: $N piece axes"
test "$N" -ge 9 || { echo "too few juglet axes" >&2; exit 1; }
# native 3x sanity: Piece_1 position must be ~548,431,-380 -- NOT /3
head -1 "$AX/Juglet_Piece_1_Axis.xyz"

mkdir -p "$RUN"/{logs,out,work,score,tools,runs}
cp -f "$SRC"/src362.tar.gz "$RUN"/
cp -a "$SRC"/tools/. "$RUN"/tools/
cp -f "$SRC"/work/checkacc333.py "$SRC"/work/sum_t05_juglet.py "$RUN"/work/
sed -i 's#^OWN=\$RUN/out/axes05_juglet_def3x#OWN=\$RUN/out/axes09_juglet_def3x_regen#' "$RUN"/tools/stage363.sh
grep -q 'axes09_juglet_def3x_regen' "$RUN"/tools/stage363.sh || { echo "stage363 OWN not rewritten" >&2; exit 1; }
printf 'juglet_own_xy_r1\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n' > "$RUN"/work/arm363_map.tsv
printf 'juglet_own_xy_r2\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n' >> "$RUN"/work/arm363_map.tsv
printf 'juglet_own_xy_r3\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n' >> "$RUN"/work/arm363_map.tsv
printf 'juglet_own_xy_r4\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n' >> "$RUN"/work/arm363_map.tsv
sed -e 's#--job-name=t05-juglet#--job-name=t09-juglet#' \
    -e 's#SOURCE_COMMIT=4beb57f#SOURCE_COMMIT=a50f8cc#' \
    -e 's|^# submit363.sbatch -- ticket 363 Part B.*|# submit363 clone -- ticket 09 Stage 3: the four def_3x juglet repeats on axes extracted from the regenerated own surfaces (out/axes09_juglet_def3x_regen, native 3x tree units).|' \
    -e 's#RUN/out/axes05_juglet_def3x#RUN/out/axes09_juglet_def3x_regen#g' \
    -e 's#t05-juglet#t09-juglet#g' \
    "$SRC"/submit_t05_juglet.sbatch > "$RUN"/submit_t09_juglet.sbatch
grep -q 'axes09_juglet_def3x_regen' "$RUN"/submit_t09_juglet.sbatch || { echo "juglet submit AXREF not rewritten" >&2; exit 1; }
cp -r "$AX" "$RUN"/out/axes09_juglet_def3x_regen
cat > "$RUN/run.json" <<EOF
{"runid": "$(basename "$RUN")", "ticket": 9, "tag": "t09-juglet", "commit": "$GIT7",
 "axes": "$AX", "arms": ["juglet_own_xy_r1", "juglet_own_xy_r2", "juglet_own_xy_r3", "juglet_own_xy_r4"],
 "template": "$SRC", "depends_on": "$DEP"}
EOF
if [ -n "$DEP" ]; then
  JID=$(cd "$RUN" && sbatch --parsable --export=ALL,RUN_DIR="$RUN",SOURCE_COMMIT="$GIT7" --dependency=afterok:$DEP submit_t09_juglet.sbatch)
else
  JID=$(cd "$RUN" && sbatch --parsable --export=ALL,RUN_DIR="$RUN",SOURCE_COMMIT="$GIT7" submit_t09_juglet.sbatch)
fi
printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "$JID" "$GIT7" "t09-juglet" >> "$RUNS/index.tsv"
echo "juglet $(basename "$RUN") $JID"
sed -e "s#^RUN=.*#RUN=$RUN#" "$STAGE"/submit_t09_jugsum.sbatch > "$RUN"/submit_t09_jugsum.sbatch
JID2=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$JID submit_t09_jugsum.sbatch)
echo "jugsum $JID2 (afterok:$JID)"
E2EJ

chmod +x "$W/make_t09_e2e.sh" "$W/make_t09_juglet.sh"
echo "[launch09] stage=$STAGE dep=${DEP:-none} stamp=$STAMP axes=$AXPOT"
case "$STAGE" in
  3A) bash "$W/make_t09_e2e.sh" "$STAMP" "E G D J"
      bash "$W/make_t09_juglet.sh" "$STAMP" ;;
  3B) bash "$W/make_t09_e2e.sh" "$STAMP" "A B C F H I" ;;
  *) echo "unknown stage $STAGE (3A or 3B)" >&2; exit 2 ;;
esac
echo "[launch09] stage $STAGE submitted; poll each job id above, and the jugsum job, to a terminal sacct state"
