#!/bin/bash
#SBATCH --job-name=t13-cell
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-cell-%j.out
#SBATCH --error=logs/slurm-cell-%j.err
#
# Ticket 13 cell: one Hierarchy-T13 assembly per job.
#
#   sbatch --array=0-N-1%4 cell13.sbatch            # array mode: row SLURM_ARRAY_TASK_ID
#   sbatch cell13.sbatch ARM REP                    # ad-hoc single cell / rerun
#   sbatch cell13.sbatch REPORT report|terminal     # report13.py then check13.py
#
# The array row comes from logs/array_map.tsv written by prep13.sbatch:
#   index<TAB>stage<TAB>arm<TAB>rep<TAB>axis_dir
# Everyone runs the SAME pinned executable (WANT_SHA) against the SAME read-only Pot J tree;
# only /Dataset/SfS_pp/Axes (staged per arm) and the writable Result mount vary.  That makes
# changed_axis_files a real measurement of the arm, not of the staging.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work/t13
PANEL=$RUN/panel
EXE=$PANEL/build/Hierarchy-T13
WANT_SHA=de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
TREE=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/J/MM
PIECES_TSV=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/arm_pieces_J.tsv
SCORER=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/work/score305.py
ACC=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/work/acc305.py
T09_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen
NP=19
SC=$RUN/score
mkdir -p "$RUN/logs" "$SC" "$RUN/mount" "$RUN/out" "$RUN/evidence"

print_status() { echo "$@" | tee -a "$RUN/logs/run_status.txt"; }
fail() { local rc=$1; shift; print_status "RUN-FAIL $rc :: $*"; exit "$rc"; }

# The eligible piece numbers (on_off == on; piece 9 is off, no GT axis).
ONPIECES=$(awk -F'\t' '$1=="J" && $5=="on" {printf "%s%s", sep, $3; sep=","}' "$PIECES_TSV")
[ -n "$ONPIECES" ] || fail 12 "could not read eligible pieces from $PIECES_TSV"

if [ "${1:-}" = "REPORT" ]; then
  MODE=${2:-}
  cd "$RUN" || exit 1
  RC=0
  case "$MODE" in
    report)
      "$PY" "$WORK/report13.py" --run "$RUN"; RC=$?
      if [ "$RC" -eq 0 ]; then
        "$PY" "$WORK/check13.py" --run "$RUN" 2>&1 | tee "$RUN/evidence/check_injob.txt"; RC=$?
      fi ;;
    terminal) "$PY" "$WORK/check13.py" --run "$RUN" --expect-terminal; RC=$? ;;
    *) fail 10 "unknown report mode $MODE" ;;
  esac
  print_status "[REPORT] $MODE rc=$RC"
  exit "$RC"
fi

if [ $# -ge 2 ]; then
  ARM=$1; REP=$2; STAGE=adhoc
else
  IDX=0
  [ -n "$(printenv SLURM_ARRAY_TASK_ID)" ] && IDX=$(printenv SLURM_ARRAY_TASK_ID)
  MAP=$RUN/logs/array_map.tsv
  [ -f "$MAP" ] || fail 12 "no array map at $MAP"
  ARM=$(awk -F'\t' -v i="$IDX" '$1==i {print $3}' "$MAP")
  REP=$(awk -F'\t' -v i="$IDX" '$1==i {print $4}' "$MAP")
  STAGE=$(awk -F'\t' -v i="$IDX" '$1==i {print $2}' "$MAP")
  [ -n "$ARM" ] && [ -n "$REP" ] || fail 12 "array index $IDX not in $MAP"
fi
JOBID=$SLURM_JOB_ID
AJ=$(printenv SLURM_ARRAY_JOB_ID)
AT=$(printenv SLURM_ARRAY_TASK_ID)
[ -n "$AJ" ] && [ -n "$AT" ] && JOBID=$AJ"_"$AT
AXIS_DIR=$RUN/axes/$ARM
[ -d "$AXIS_DIR" ] || fail 12 "axis pack missing: $AXIS_DIR"
[ -x "$EXE" ] || fail 11 "panel executable missing: $EXE"
print_status "cell-start $(date -u +%FT%TZ) job=$JOBID stage=$STAGE arm=$ARM rep=$REP want=$WANT_SHA"

RESULT=$RUN/out/$ARM"_"$REP
LOG=$RUN/logs/run_$ARM"_"$REP.log
ACCROW=$RUN/logs/acc_$ARM"_"$REP.tsv
SCORE=$SC/$ARM"_"$REP.tsv
TAG=$ARM"_"$REP
if ! mkdir "$RESULT" 2>/dev/null; then print_status "[CELL] EXISTS $ARM $REP"; exit 0; fi
PRE=$(sha256sum "$EXE" | cut -d' ' -f1)
printf '%s  %s\n' "$PRE" "$EXE" > "$RUN/logs/exec_have_$TAG.txt"
[ "$PRE" = "$WANT_SHA" ] || print_status "[CELL] PRE-HASH-MISMATCH $TAG got=$PRE"
# Which of the 12 Pot J axis files differ from the Ticket 09 reference pack?
CHANGED=0
for f in "$TREE"/Axes/*.xyz; do
  n=$(basename "$f")
  if [ -f "$AXIS_DIR/$n" ] && cmp -s "$T09_AX/$n" "$AXIS_DIR/$n" 2>/dev/null; then :; else CHANGED=$((CHANGED + 1)); fi
done
{ cd "$AXIS_DIR" && sha256sum *.xyz; } | sort -k2 > "$RUN/logs/axis_before_$TAG.txt"
find "$TREE" -maxdepth 2 -type f -printf '%s %T@ %P\n' | sort -k3 > "$RUN/logs/tree_before_$TAG.txt"
print_status "[CELL] arm=$ARM rep=$REP changed_axis_files=$CHANGED exe_pre=$PRE"
START=$SECONDS
timeout 5400 "$APT" exec --writable-tmpfs \
  --bind "$MAIN:/workspace" \
  --bind "$PANEL:/panel:ro" \
  --bind "$TREE:/Dataset/SfS_pp:ro" \
  --bind "$AXIS_DIR:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" \
  --env OMP_NUM_THREADS=8 "$SIF" \
  bash -euc 'sha256sum -c /panel/logs/executable.sha256; exec /panel/build/Hierarchy-T13 19' \
  > "$LOG" 2>&1
RC=$?
WALL=$((SECONDS - START))
POST=$(sha256sum "$EXE" | cut -d' ' -f1)
{ cd "$AXIS_DIR" && sha256sum *.xyz; } | sort -k2 > "$RUN/logs/axis_after_$TAG.txt"
find "$TREE" -maxdepth 2 -path "$TREE/Result" -prune -o -type f -printf '%s %T@ %P\n' | sort -k3 > "$RUN/logs/tree_after_$TAG.txt"
INOK=0
if cmp -s "$RUN/logs/axis_before_$TAG.txt" "$RUN/logs/axis_after_$TAG.txt" && \
   cmp -s "$RUN/logs/tree_before_$TAG.txt" "$RUN/logs/tree_after_$TAG.txt"; then INOK=1; fi
EXEOK=0
if [ "$RC" -eq 0 ] && [ "$POST" = "$WANT_SHA" ] && grep -q ': OK$' "$LOG"; then EXEOK=1; fi
print_status "[CELL] done $TAG rc=$RC wall=$WALL exe_ok=$EXEOK inputs_unchanged=$INOK post=$POST"
POSES=$(find "$RESULT" -maxdepth 1 -name 'T_*to_*.txt' -size +0 | wc -l)
POSE_RC=0
bash "$WORK/posecheck13.sh" "$RESULT" "$ONPIECES" >> "$LOG" 2>&1 || POSE_RC=$?
SLABEL="cell_$TAG"
"$PY" "$ACC" "$RESULT" "$SLABEL" "$ACCROW" > "$RUN/logs/acc_stdout_$TAG.log" 2>&1
"$PY" "$SCORER" "$RESULT" "$TREE/Ground Truth" J "$PIECES_TSV" "$SCORE" "$SLABEL" > "$RUN/logs/score_stdout_$TAG.log" 2>&1
JOINS=0/0
SHERD=0/0
if [ -f "$SCORE" ]; then
  JOINS=$(grep '^SUMMARY' "$SCORE" | tail -1 | cut -f3 | sed 's/joins=//')
  [ -n "$JOINS" ] || JOINS=0/0
fi
if [ -f "$ACCROW" ]; then
  SHERD=$(tail -1 "$ACCROW" | cut -f3 | sed 's/^sherd //')
  [ -n "$SHERD" ] || SHERD=0/0
fi
JOIN_NUM=$(printf '%s' "$JOINS" | cut -d/ -f1)
JOIN_DEN=$(printf '%s' "$JOINS" | cut -d/ -f2)
SHERD_NUM=$(printf '%s' "$SHERD" | cut -d/ -f1)
SHERD_DEN=$(printf '%s' "$SHERD" | cut -d/ -f2)
USABLE=0
if [ "$EXEOK" -eq 1 ] && [ "$INOK" -eq 1 ] && [ "$POSE_RC" -eq 0 ] && \
   [ "$JOIN_DEN" = "21" ] && [ "$SHERD_DEN" = "11" ]; then USABLE=1; fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$ARM" "$REP" "$JOBID" "$STAGE" "$RC" "$WALL" "$CHANGED" "$EXEOK" "$INOK" "$POSES" "$USABLE" \
  >> "$RUN/logs/panel.tsv"
printf '{\n  "arm": "%s",\n  "rep": "%s",\n  "job_id": "%s",\n  "stage": "%s",\n  "axis_dir": "%s",\n  "rc": %s,\n  "wall_secs": %s,\n  "exe_sha_pre": "%s",\n  "exe_sha_post": "%s",\n  "exe_sha_ok": %s,\n  "inputs_unchanged": %s,\n  "changed_axis_files": %s,\n  "exported_poses": %s,\n  "posecheck_rc": %s,\n  "joins": "%s",\n  "sherd": "%s",\n  "usable": %s\n}\n' \
  "$ARM" "$REP" "$JOBID" "$STAGE" "$AXIS_DIR" "$RC" "$WALL" "$PRE" "$POST" \
  "$EXEOK" "$INOK" "$CHANGED" "$POSES" "$POSE_RC" "$JOINS" "$SHERD" "$USABLE" \
  > "$RUN/logs/cell_raw_$TAG.json"
print_status "[CELL] $TAG joins=$JOINS sherd=$SHERD poses=$POSES usable=$USABLE"
if [ "$USABLE" -eq 1 ]; then exit 0; fi
exit 20
