#!/bin/bash
#SBATCH --job-name=t06-cell
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=02:30:00
#SBATCH --output=logs/slurm-cell-%j.out
#SBATCH --error=logs/slurm-cell-%j.err
# Ticket 06 assembly cell: ARM REP, or REPORT report|terminal.
#
# One cell per job at 8 CPUs, the Ticket 19 launch shape: four cells per wave,
# Slurm holds 32 cores, and every per-cell guard and the scorer call are Ticket
# 19's. Only /Dataset/SfS_pp/Axes varies between the four arms; Breaklines,
# Surfaces, Mesh and Ground Truth are bound read-only from the fixed Ticket 03
# tree, so no regenerated surface or breakline from OWN_MAIN_T09 can reach the
# assembler. posecheck06.sh must pass (31/31 nonempty T_<i>to_<i>.txt) before
# score305.py runs.
set -uo pipefail

ARM=${1:?arm}
REP=${2:?repeat}
MAIN=/data/gpfs/projects/punim2657/sfs_main
BASE=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9
T03E=${BASE}_t03-potE
T19=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions
T19WORK="$T19/work/t19"
FIXED="$T03E/trees/E_K3R1/E/MM"
SIF="$MAIN/sfs_pristine_assembly.sif"
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SCORER="$T03E/work/score305.py"
PIECES="$T03E/trees/E_K3R1/arm_pieces_E.tsv"
WANT_SHA=0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9
RUN="${SLURM_SUBMIT_DIR:?}"
WORK="$RUN/work/t06"
PANEL="$RUN/panel"
EXE="$PANEL/build/Hierarchy-T19"
SC="$RUN/score"
EV="$RUN/evidence"
mkdir -p "$RUN/logs" "$SC" "$EV"
print_status() { echo "$@" | tee -a "$RUN/logs/run_status.txt"; }
fail() { print_status "RUN-FAIL $1 :: $2 ($ARM $REP)"; exit "$1"; }

if [ "$ARM" = "REPORT" ]; then
  printf '%s\t%s\t%s\t%s\n' "$SLURM_JOB_ID" "report-$REP" "-" "-" >> "$RUN/logs/jobs_submitted.tsv"
  AUX="$RUN/evidence/jobs_aux.tsv"
  [ -f "$AUX" ] || printf 'job_id\tstage\tnote\n' > "$AUX"
  printf '%s\t%s\t%s\n' "$SLURM_JOB_ID" "report-$REP" "verification job; final state from the laptop poll" >> "$AUX"
  cd "$RUN" || exit 1
  RC=0
  case "$REP" in
    report)
      "$PY" "$WORK/report06.py" --run "$RUN" --fixed "$FIXED"; RC=$?
      if [ "$RC" -eq 0 ]; then
        "$PY" "$WORK/check06.py" --run "$RUN" --fixed "$FIXED" 2>&1 | tee "$RUN/evidence/check_injob.txt"; RC=$?
      fi ;;
    terminal) "$PY" "$WORK/check06.py" --run "$RUN" --fixed "$FIXED" --expect-terminal; RC=$? ;;
    *) fail 10 "unknown report mode $REP" ;;
  esac
  print_status "[REPORT] $REP rc=$RC"
  exit "$RC"
fi

case "$ARM" in
  AUTHOR|OWN_NOV5|OWN_NOV5_DEDUP|OWN_MAIN_T09) DATA="$FIXED"; AXIS_DIR="$RUN/axes/$ARM" ;;
  *) fail 10 "unknown arm $ARM" ;;
esac

printf '%s\t%s\t%s\t%s\n' "$SLURM_JOB_ID" cell "$ARM" "$REP" >> "$RUN/logs/jobs_submitted.tsv"
[ -x "$EXE" ] || fail 11 "panel executable missing: $EXE"
[ -d "$AXIS_DIR" ] || fail 12 "axis pack missing: $AXIS_DIR"
print_status "cells-start $(date -u +%FT%TZ) job=$SLURM_JOB_ID arm=$ARM rep=$REP exe=$WANT_SHA"
mkdir -p "$RUN/mount" || fail 6 mount

RESULT="$RUN/out/${ARM}_${REP}"
LOG="$RUN/logs/run_${ARM}_${REP}.log"
if ! mkdir "$RESULT"; then print_status "[CELL] EXISTS $ARM $REP"; exit 0; fi
PRE=$(sha256sum "$EXE" | cut -d' ' -f1)
printf '%s  %s\n' "$PRE" "$EXE" > "$RUN/logs/exec_have_${ARM}_${REP}.txt"
"$PY" "$T19WORK/inputs19.py" --root "$DATA" --axes "$AXIS_DIR" --label "${ARM}_${REP}" \
  --out "$RUN/logs/inputs_before_${ARM}_${REP}.tsv" > "$RUN/logs/inputs_before_${ARM}_${REP}.log" 2>&1 \
  || print_status "[CELL] INHASH-BEFORE-FAIL $ARM $REP"
T0=$SECONDS
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)' || true); do unset "$v"; done
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$PANEL:/panel:ro" \
  --bind "$RUN/mount:/Dataset/SfS_pp:ro" \
  --bind "$DATA/Breaklines:/Dataset/SfS_pp/Breaklines:ro" \
  --bind "$DATA/Surfaces:/Dataset/SfS_pp/Surfaces:ro" \
  --bind "$DATA/Mesh:/Dataset/SfS_pp/Mesh:ro" \
  --bind "$DATA/Ground Truth:/Dataset/SfS_pp/Ground Truth:ro" \
  --bind "$AXIS_DIR:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" \
  --env OMP_NUM_THREADS=8 --env T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl \
  --env T19_TRACE=/Dataset/SfS_pp/Result/t19_decisions.jsonl "$SIF" bash -euc '
    sha256sum -c /panel/logs/executable.sha256
    find "/Dataset/SfS_pp" -maxdepth 3 -name "Pot_E*" -type f | wc -l | sed "s/^/CONTAINER-POT-E=/"
    exec /panel/build/Hierarchy-T19 31
  ' > "$LOG" 2>&1
RC=$?; DT=$((SECONDS - T0))
POST=$(sha256sum "$EXE" | cut -d' ' -f1)
OK=0; grep -q ': OK$' "$LOG" && OK=1
CONTAINER=$(sed -n 's/^CONTAINER-POT-E=\([0-9][0-9]*\).*/\1/p' "$LOG" | head -1); CONTAINER=${CONTAINER:-0}
"$PY" "$T19WORK/inputs19.py" --root "$DATA" --axes "$AXIS_DIR" --label "${ARM}_${REP}" \
  --out "$RUN/logs/inputs_after_${ARM}_${REP}.tsv" > "$RUN/logs/inputs_after_${ARM}_${REP}.log" 2>&1 \
  || print_status "[CELL] INHASH-AFTER-FAIL $ARM $REP"
INOK=0
cmp -s "$RUN/logs/inputs_before_${ARM}_${REP}.tsv" "$RUN/logs/inputs_after_${ARM}_${REP}.tsv" && INOK=1
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ARM" "$REP" "$WANT_SHA" "$PRE" "$POST" "$OK" "$RC" "$DT" "$CONTAINER" "$INOK" >> "$RUN/logs/panel.tsv"
print_status "[CELL] done $ARM $REP rc=$RC wall=${DT}s ok=$OK inok=$INOK container=$CONTAINER pre=$PRE post=$POST"

POSES=$(find "$RESULT" -maxdepth 1 -name 'T_*to_*.txt' -size +0 | wc -l)
POSE_OK=0
bash "$WORK/posecheck06.sh" "$RESULT" 31 > "$RUN/logs/posecheck_${ARM}_${REP}.log" 2>&1 && POSE_OK=1
print_status "[CELL] posecheck $ARM $REP poses=$POSES pass=$POSE_OK"

SCORED=0
if [ "$PRE" = "$WANT_SHA" ] && [ "$POST" = "$WANT_SHA" ] && [ "$OK" = 1 ] && [ "$INOK" = 1 ] \
   && [ "$RC" -eq 0 ] && [ "$POSE_OK" = 1 ]; then
  "$PY" "$SCORER" "$RESULT" "$DATA/Ground Truth" E "$PIECES" "$SC/${ARM}_${REP}.tsv" "${ARM}_${REP}" \
    > "$RUN/logs/score_${ARM}_${REP}.log" 2>&1
  [ -s "$SC/${ARM}_${REP}.tsv" ] && SCORED=1
  print_status "[CELL] scored $ARM $REP :: $(tail -1 "$RUN/logs/score_${ARM}_${REP}.log")"
else
  print_status "[CELL] NOT-SCORED $ARM $REP (hash/ok/in/rc/pose)"; : > "$RUN/logs/not_scored_${ARM}_${REP}.flag"
fi
USABLE=0
if [ "$SCORED" = 1 ] && [ "$POSES" -eq 31 ] && [ "$CONTAINER" -ge 187 ]; then USABLE=1; fi
printf '{"arm":"%s","rep":"%s","job_id":"%s","exe_sha_ok":%d,"inputs_unchanged":%d,"container_files":%d,"wall_secs":%d,"exported_poses":%d,"usable":%d,"rc":%d,"scored":%d}\n' \
  "$ARM" "$REP" "$SLURM_JOB_ID" "$OK" "$INOK" "$CONTAINER" "$DT" "$POSES" "$USABLE" "$RC" "$SCORED" \
  > "$RUN/logs/cell_raw_${ARM}_${REP}.json"
print_status "[CELL] raw $ARM $REP usable=$USABLE scored=$SCORED"
exit 0
