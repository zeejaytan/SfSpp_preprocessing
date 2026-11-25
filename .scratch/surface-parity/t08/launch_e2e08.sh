#!/bin/bash
# Ticket 08 Stage 2 -- gated 10-pot + def_3x Juglet E2E assembly on the frozen
# Ticket 03 templates, with only the axis pack and the run tag swapped.
#
#   launch_e2e08.sh <extract-run-dir> 2A       Pot E G D J (4 arms each) + def_3x Juglet
#   launch_e2e08.sh <extract-run-dir> 2B       Pot A B C F H I (4 arms each)
#   launch_e2e08.sh <extract-run-dir> report   evidence tables + 20 mm render job
set -euo pipefail

EXTRACT_RUN=${1:?usage: launch_e2e08.sh <extract-run-dir> <2A|2B|report>}
STAGE=${2:?usage: launch_e2e08.sh <extract-run-dir> <2A|2B|report>}
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIP=$RUNS/20261121-1319_2e951d9_t03-ship
GIT7=2e951d9

BASENAME=$(basename "$EXTRACT_RUN")
STAMP=${BASENAME%%_*}
AX08=$EXTRACT_RUN/out/axes08_own_dedup
AXJ=$EXTRACT_RUN/out/axes08_juglet_def3x_dedup
T08=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
JOBS=$EXTRACT_RUN/out/jobs_submitted.tsv

[ -d "$EXTRACT_RUN" ] || { echo "missing run dir $EXTRACT_RUN" >&2; exit 2; }
[ -d "$AX08" ] || { echo "missing $AX08 (Stage 1 not complete)" >&2; exit 2; }
[ -d "$AXJ" ] || { echo "missing $AXJ (Stage 1 not complete)" >&2; exit 2; }
NPOT=$(ls "$AX08" | wc -l)
NJUG=$(ls "$AXJ" | wc -l)
[ "$NPOT" -eq 148 ] || { echo "axes08_own_dedup has $NPOT stems, need 148" >&2; exit 2; }
[ "$NJUG" -eq 9 ] || { echo "axes08_juglet_def3x_dedup has $NJUG stems, need 9" >&2; exit 2; }
[ -f "$JOBS" ] || printf "job_id\tstage\tvessel\n" > "$JOBS"

record() { printf "%s\t%s\t%s\n" "$1" "$2" "$3" >> "$JOBS"; }

make_pot() {
  local P=$1
  local SRC=$RUNS/20261109-1426_ecd5bb8_t319-pot$P
  local RUN=$RUNS/${STAMP}_${GIT7}_t08-pot$P
  [ -d "$SRC" ] || { echo "missing template $SRC" >&2; return 2; }
  mkdir -p "$RUN"/logs "$RUN"/out "$RUN"/score "$RUN"/work/axes_k3
  cp -r "$SRC"/work/*.py "$SRC"/work/arm67.sh "$SRC"/work/shim "$SRC"/work/inc_src "$RUN"/work/
  sed -e "s#^AX_318=.*#AX_318=$AX08#" -e "s#--job-name=t319-pot$P#--job-name=t08-pot$P#" \
      "$SRC"/submit.sbatch > "$RUN"/submit.sbatch
  cat > "$RUN"/run.json <<JSON
{"runid": "${STAMP}_${GIT7}_t08-pot$P", "ticket": 8, "pot": "$P", "tag": "t08-pot$P",
 "commit": "$GIT7", "axes": "$AX08", "arms": ["${P}_MOR1", "${P}_MOR2", "${P}_K3R1", "${P}_K3R2"],
 "template": "$SRC", "depends_on": "$EXTRACT_RUN"}
JSON
  grep -q "^AX_318=$AX08$" "$RUN"/submit.sbatch || { echo "gate FAIL: AX_318 not swapped in $RUN" >&2; return 3; }
  grep -q '_MOR1.*_MOR2.*_K3R1.*_K3R2' "$RUN"/submit.sbatch || { echo "gate FAIL: four arms missing in $RUN" >&2; return 3; }
  # K<=3 axes: the template writes these into $WORK/axes_k3 at job time, so the
  # directory must exist BEFORE submission (a missing dir silently gave the K3
  # arms an empty axis pack and zero candidates in the first 2A attempt).
  local NAX NK
  NAX=$(ls "$AX08"/Pot_${P}_Piece_*_Axis.xyz | wc -l)
  for f in "$AX08"/Pot_${P}_Piece_*_Axis.xyz; do
    head -n 3 "$f" > "$RUN"/work/axes_k3/"$(basename "$f")"
  done
  NK=$(ls "$RUN"/work/axes_k3 | wc -l)
  [ "$NK" -eq "$NAX" ] || { echo "gate FAIL: axes_k3 has $NK stems, expected $NAX in $RUN" >&2; return 4; }
  for f in "$RUN"/work/axes_k3/*.xyz; do
    [ -s "$f" ] || { echo "gate FAIL: empty K<=3 axis $f" >&2; return 4; }
  done
  local JID
  JID=$(cd "$RUN" && sbatch --parsable submit.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "${STAMP}_${GIT7}_t08-pot$P" "$JID" "$GIT7" "t08-pot$P" >> "$RUNS"/index.tsv
  record "$JID" "$STAGE" "POT$P"
  echo "[t08-$STAGE] Pot $P -> $RUN (job $JID)"
}

make_juglet() {
  local SRC=$RUNS/20261120-1106_9e0fe6a_t05-juglet
  local RUN=$RUNS/${STAMP}_${GIT7}_t08-juglet
  [ -d "$SRC" ] || { echo "missing template $SRC" >&2; return 2; }
  mkdir -p "$RUN"/logs "$RUN"/out "$RUN"/work "$RUN"/score "$RUN"/tools "$RUN"/runs
  cp "$SRC"/src362.tar.gz "$RUN"/
  cp -r "$SRC"/tools/. "$RUN"/tools/
  cp "$SRC"/work/checkacc333.py "$SRC"/work/sum_t05_juglet.py "$RUN"/work/
  sed -i 's#^OWN=\$RUN/out/axes05_juglet_def3x#OWN=\$RUN/out/axes08_juglet_def3x_dedup#' "$RUN"/tools/stage363.sh
  grep -q '^OWN=\$RUN/out/axes08_juglet_def3x_dedup$' "$RUN"/tools/stage363.sh || { echo "gate FAIL: stage363 OWN not swapped" >&2; return 3; }
  printf "juglet_own_xy_r1\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n" > "$RUN"/work/arm363_map.tsv
  printf "juglet_own_xy_r2\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n" >> "$RUN"/work/arm363_map.tsv
  printf "juglet_own_xy_r3\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n" >> "$RUN"/work/arm363_map.tsv
  printf "juglet_own_xy_r4\tjuglet_own\tfull\t1\t1\t10\tinc_jug\t-DJUGLET_ORIG\ton\n" >> "$RUN"/work/arm363_map.tsv
  cp -r "$AXJ" "$RUN"/out/axes08_juglet_def3x_dedup
  sed -e "s#--job-name=t05-juglet#--job-name=t08-juglet#" \
      -e "s#SOURCE_COMMIT=4beb57f#SOURCE_COMMIT=2e951d9#" \
      -e "s#RUN/out/axes05_juglet_def3x#RUN/out/axes08_juglet_def3x_dedup#g" \
      -e "s#t05-juglet#t08-juglet#g" \
      "$SRC"/submit_t05_juglet.sbatch > "$RUN"/submit_t08_juglet.sbatch
  grep -q "axes08_juglet_def3x_dedup" "$RUN"/submit_t08_juglet.sbatch || { echo "gate FAIL: juglet AXREF not swapped" >&2; return 3; }
  cat > "$RUN"/run.json <<JSON
{"runid": "${STAMP}_${GIT7}_t08-juglet", "ticket": 8, "tag": "t08-juglet",
 "commit": "$GIT7", "axes": "$AXJ", "arms": ["juglet_own_xy_r1", "juglet_own_xy_r2", "juglet_own_xy_r3", "juglet_own_xy_r4"],
 "template": "$SRC", "depends_on": "$EXTRACT_RUN"}
JSON
  local JID JID2
  JID=$(cd "$RUN" && sbatch --parsable --export=ALL,RUN_DIR=$RUN,SOURCE_COMMIT=$GIT7 submit_t08_juglet.sbatch)
  printf "%s\t%s\t%s\t%s\t\t\n" "${STAMP}_${GIT7}_t08-juglet" "$JID" "$GIT7" "t08-juglet" >> "$RUNS"/index.tsv
  record "$JID" "$STAGE" "JUGLET"
  echo "[t08-$STAGE] Juglet -> $RUN (job $JID)"
  sed -e "s#^RUN=.*#RUN=$RUN#" -e "s#--job-name=t03-jugsum#--job-name=t08-jugsum#" \
      "$SHIP"/work/submit_t03_jugsum.sbatch > "$RUN"/submit_t08_jugsum.sbatch
  JID2=$(cd "$RUN" && sbatch --parsable --dependency=afterok:$JID submit_t08_jugsum.sbatch)
  record "$JID2" "jugsum" "JUGLET"
  echo "[t08-$STAGE] Juglet scoring -> job $JID2 (afterok $JID)"
}

do_report() {
  local JID
  JID=$(sbatch --parsable --job-name=t08-report --cpus-per-task=2 --mem=16G --time=01:00:00 \
        --output="$EXTRACT_RUN"/logs/t08-report_%j.out --error="$EXTRACT_RUN"/logs/t08-report_%j.err \
        --wrap="$PY $T08/report08.py --run $EXTRACT_RUN --phase all")
  record "$JID" "report" "ALL"
  echo "[t08-report] evidence+tables+render job $JID"
}

case "$STAGE" in
  2A) for P in ${T08_POTS:-E G D J}; do make_pot "$P"; done
      [ -n "${T08_SKIP_JUG:-}" ] || make_juglet ;;
  2B) for P in ${T08_POTS:-A B C F H I}; do make_pot "$P"; done ;;
  report) do_report ;;
  *) echo "unknown stage $STAGE (use 2A|2B|report)" >&2; exit 2 ;;
esac

echo "[t08-$STAGE] submitted:"
tail -n +2 "$JOBS"
