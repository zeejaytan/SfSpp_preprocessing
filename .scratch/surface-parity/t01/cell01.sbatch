#!/bin/bash
#SBATCH --job-name=t01-cell
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=02:30:00
#SBATCH --output=logs/slurm-cell-%j.out
#SBATCH --error=logs/slurm-cell-%j.err
# Ticket 01 single cell: ARM REP as arguments.
#
# Fork of $T19/work/t19/cell19.sbatch (Ticket 19). One cell per 8-CPU job, four per
# wave, as the archived run already did (see T19 run.json launch_note).
# Differences from the archived script, all required by Ticket 01 section 2:
#   * DATA and GT are the Ticket 03 fixed tree in every cell; only $RUN/axes/$ARM varies.
#   * WANT_SHA is pinned to the Ticket 19 hash; WORK is the archived work/t19 (no build).
#   * every archived error exit that used to return 0 now returns nonzero:
#     duplicate result dir 7, executable hash 8, input manifest 9, container 11,
#     missing pose 12, scorer 13, before/after input drift 14, container inventory 15.
#   * a container-side inventory of /Dataset/SfS_pp is written to Result/container_inputs.tsv
#     so the bound Axes bytes are verified inside the container, not just on the host.
#   * the missing-pose guard requires all 31 nonempty T_<i>to_<i>.txt exports
#     (posecheck.sh, the same function the fixtures exercise), not just T_0to_0.txt.
set -uo pipefail
ARM=${1:?arm}
REP=${2:?repeat}
MAIN=/data/gpfs/projects/punim2657/sfs_main
T19=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions
T03E=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-potE
FIXED="$T03E/trees/E_K3R1/E/MM"
SIF="$MAIN/sfs_pristine_assembly.sif"
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SCORER="$T03E/work/score305.py"
PIECES="$T03E/trees/E_K3R1/arm_pieces_E.tsv"
DATA="$FIXED"
GT="$FIXED/Ground Truth"
WANT_SHA=0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9
RUN="${SLURM_SUBMIT_DIR:?}"
WORK="$T19/work/t19"
SC="$RUN/score"
PRE=""
POST=""
OK=""
RC=""
# the documented pose check lives in posecheck.sh beside this script
# shellcheck source=posecheck.sh
. "$(dirname "$0")/posecheck.sh" || { echo "RUN-FAIL 12 posecheck-missing"; exit 12; }
print_status() { echo "$@" | tee -a "$RUN/logs/run_status.txt"; }
note_cell() { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$ARM" "$REP" "${SLURM_JOB_ID:--}" "$1" "$2" "${OK:-}" "${PRE:-}" "${POST:-}" "${RC:-}" \
  >> "$RUN/logs/cell_status.tsv"; }
fail() {
  print_status "RUN-FAIL $1 :: $2 ($ARM $REP job=${SLURM_JOB_ID:--})"
  note_cell failed "$2"
  exit "$1"
}

case "$ARM" in
  OWN|AUTHOR|OWN_E27_AUTHOR|AUTHOR_E27_OWN) ;;
  *) fail 10 "unknown arm $ARM" ;;
esac
mkdir -p "$RUN/mount" || fail 6 mount
for d in Axes Breaklines "Ground Truth" Mesh Result Surfaces; do
  mkdir -p "$RUN/mount/$d" || fail 6 "mount/$d"
done
print_status "cells-start $(date -u +%FT%TZ) job=$SLURM_JOB_ID arm=$ARM rep=$REP exe=$WANT_SHA"

RESULT="$RUN/out/${ARM}_${REP}"
LOG="$RUN/logs/run_${ARM}_${REP}.log"
if ! mkdir "$RESULT"; then fail 7 "duplicate-result-dir"; fi
if [ ! -f "$WORK/build/Hierarchy-T19" ]; then fail 8 "no-executable"; fi
PRE=$(sha256sum "$WORK/build/Hierarchy-T19" | cut -d' ' -f1)
printf '%s  %s\n' "$PRE" "$WORK/build/Hierarchy-T19" > "$RUN/logs/exec_sha_${ARM}_${REP}.txt"
if [ "$PRE" != "$WANT_SHA" ]; then fail 8 "exe-hash-before $PRE"; fi
"$PY" "$WORK/inputs19.py" --root "$DATA" --axes "$RUN/axes/$ARM" --label "${ARM}_${REP}" \
  --out "$RUN/logs/inputs_before_${ARM}_${REP}.tsv" > "$RUN/logs/inputs_before_${ARM}_${REP}.log" 2>&1 \
  || fail 9 "input-manifest-before"
T0=$SECONDS
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)' || true); do unset "$v"; done
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel:ro" \
  --bind "$RUN/mount:/Dataset/SfS_pp:ro" \
  --bind "$DATA/Breaklines:/Dataset/SfS_pp/Breaklines:ro" \
  --bind "$DATA/Surfaces:/Dataset/SfS_pp/Surfaces:ro" \
  --bind "$DATA/Mesh:/Dataset/SfS_pp/Mesh:ro" \
  --bind "$DATA/Ground Truth:/Dataset/SfS_pp/Ground Truth:ro" \
  --bind "$RUN/axes/$ARM:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" \
  --env OMP_NUM_THREADS=8 --env T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl \
  --env T19_TRACE=/Dataset/SfS_pp/Result/t19_decisions.jsonl "$SIF" bash -euc '
    sha256sum -c /panel/logs/executable.sha256
    cd /Dataset/SfS_pp
    for d in Axes Breaklines Surfaces Mesh "Ground Truth"; do
      for f in "$d"/*; do
        case "$f" in */Pot_E_*) printf "%s\t%s\n" "/Dataset/SfS_pp/$f" "$(sha256sum "$f" | cut -d" " -f1)";; esac
      done
    done > /Dataset/SfS_pp/Result/container_inputs.tsv
    exec /panel/build/Hierarchy-T19 31
  ' > "$LOG" 2>&1
RC=$?; DT=$((SECONDS - T0))
POST=$(sha256sum "$WORK/build/Hierarchy-T19" | cut -d' ' -f1)
OK=0; grep -q ': OK$' "$LOG" && OK=1
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$ARM" "$REP" "$WANT_SHA" "$PRE" "$POST" "$OK" "$RC" "$DT" "${SLURM_JOB_ID:--}" >> "$RUN/logs/panel.tsv"
print_status "[CELL] done $ARM $REP rc=$RC wall=${DT}s ok=$OK pre=$PRE post=$POST"
if [ "$POST" != "$WANT_SHA" ]; then fail 8 "exe-hash-after $POST"; fi
if [ "$OK" != 1 ]; then fail 11 "container-hash-check"; fi
if [ "$RC" -ne 0 ]; then fail 11 "container-rc $RC"; fi
# all 31 pose exports must be present and nonempty before the pinned scorer runs
if ! POSE="$(check_poses "$RESULT" 31)"; then
  fail 12 "missing-pose $POSE (need 31/31 nonempty T_<i>to_<i>.txt)"
fi
print_status "[CELL] $POSE for $ARM $REP"
"$PY" "$WORK/inputs19.py" --root "$DATA" --axes "$RUN/axes/$ARM" --label "${ARM}_${REP}" \
  --out "$RUN/logs/inputs_after_${ARM}_${REP}.tsv" > "$RUN/logs/inputs_after_${ARM}_${REP}.log" 2>&1 \
  || fail 9 "input-manifest-after"
if ! cmp -s "$RUN/logs/inputs_before_${ARM}_${REP}.tsv" "$RUN/logs/inputs_after_${ARM}_${REP}.tsv"; then
  fail 14 "input-manifest-drift"
fi
if [ ! -f "$RESULT/container_inputs.tsv" ]; then fail 15 "container-inventory-missing"; fi
NINV=$(grep -c '^/Dataset/SfS_pp/' "$RESULT/container_inputs.tsv" || true)
if [ "$NINV" -lt 187 ]; then fail 15 "container-inventory-short $NINV"; fi
"$PY" "$SCORER" "$RESULT" "$GT" E "$PIECES" "$SC/${ARM}_${REP}.tsv" "${ARM}_${REP}" \
  > "$RUN/logs/score_${ARM}_${REP}.log" 2>&1 || fail 13 "scorer-rc"
grep -q '^SUMMARY' "$SC/${ARM}_${REP}.tsv" || fail 13 "scorer-summary"
print_status "[CELL] scored $ARM $REP :: $(tail -1 "$RUN/logs/score_${ARM}_${REP}.log")"
note_cell scored "ok"
