#!/usr/bin/env bash
#SBATCH --job-name=p292rescore
#SBATCH --array=0-147%10
#SBATCH --time=00:40:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=logs/slurm-%A_%a.out
# Ticket 292 job B: one array element per corpus piece. Stage by symlink, mesh stage with the
# corpus axis, edge stage at the shipped defaults, score both lanes, picture the misses, delete
# the geometry. Nothing is carried between elements.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
RUN=$RUN_DIR
export MPLCONFIGDIR=/tmp/mpl292_${SLURM_ARRAY_TASK_ID}
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
EDGE=$RUN/bin/edge/EdgeLineExtractionHeadless
MESH=$RUN/bin/mesh/MeshPreprocessingHeadless

IDX=${SLURM_ARRAY_TASK_ID}
PIECE=$(sed -n "$((IDX + 1))p" "$RUN/out/pieces.tsv")
POT=${PIECE%%_Piece_*}
if [ -z "$PIECE" ]; then echo "[TASK] no piece for index $IDX"; exit 1; fi

# node-local scratch, so no geometry touches the run directory at all
AVAIL=$(df -Pm /tmp | awk 'NR==2 {print $4}')
if [ "${AVAIL:-0}" -lt 8000 ]; then STAGEROOT=$RUN/work; else STAGEROOT=/tmp; fi
STAGE=$STAGEROOT/p292_${SLURM_ARRAY_JOB_ID}_${IDX}
LOG=$RUN/out/logs/${PIECE}.log
t0=$(date +%s)
status_stage=0; status_mesh=0; status_edge=0; classify=0

mkdir -p "$RUN/out/logs" "$RUN/out/lanes" "$RUN/out/png" "$RUN/out/tiles" "$RUN/out/status" \
         "$RUN/out/errors" "$RUN/out/recheck" "$RUN/out/deleted"
: > "$LOG"
echo "[TASK] idx=$IDX piece=$PIECE pot=$POT node=$(hostname) stage=$STAGE start=$(date -Is)" | tee -a "$LOG"
echo "[TASK] binaries edge $(md5sum "$EDGE" | awk '{print $1}') mesh $(md5sum "$MESH" | awk '{print $1}')" | tee -a "$LOG"

# no knob may be set: only POT_NAME and SFS_AXIS_FILE are passed (NURBS_OUTPUT_BASE would
# redirect the exports away from the stage, into the corpus)
unset NURBS_OUTPUT_BASE
KNOBS=$(env | grep -E '^SFS_' | cut -d= -f1 | sort | tr '\n' ' ')
if [ -n "$(echo $KNOBS | tr -d ' ')" ]; then
  printf '%s\t%s\t-\tknoberror\t1\tSFS_ variables set: %s\n' "$POT" "$PIECE" "$KNOBS" > "$RUN/out/errors/${PIECE}.tsv"
  echo "[TASK] refusing to run with knobs set: $KNOBS"; exit 1
fi

cleanup() {
  if [ -d "$STAGE" ]; then
    { echo "piece=$PIECE node=$(hostname) stage=$STAGE";
      du -sh "$STAGE"; find "$STAGE" -type f | wc -l; } > "$RUN/out/deleted/${PIECE}.tsv"
    rm -rf "$STAGE"
  fi
  [ ! -e "$STAGE" ] || { echo "[TASK] DELETE FAILED $STAGE" >> "$LOG"; echo "DELETE_FAILED=1" >> "$RUN/out/deleted/${PIECE}.tsv"; }
  rm -rf "$MPLCONFIGDIR"
}
trap cleanup EXIT

# ---- 1. stage by symlink ----
# Retried on purpose: the committed stage_piece.sh reads the PCD header with
#   head -20 "$1" | awk '/^POINTS/{print $2; exit}'
# and under its own `set -o pipefail` the early awk exit can hand head a SIGPIPE, which aborts the
# whole script with 141 before it says anything (measured on Pot_A_Piece_02, 2026-10-25). That is a
# race in the helper, not in the inputs, so the element re-runs it; the inputs are re-resolved and
# re-checked against the manifests on every attempt. The helper is not modified.
status_stage=1; stage_tries=0
for try in 1 2 3; do
  stage_tries=$try
  bash "$RUN/scripts/stage_piece.sh" "$STAGE" "$POT" "$PIECE" >> "$LOG" 2>&1
  status_stage=$?
  [ "$status_stage" -eq 0 ] && break
  echo "[TASK] staging attempt $try exited $status_stage; retrying" >> "$LOG"
  rm -rf "$STAGE"
  sleep 2
done

# ---- 2. mesh stage, axis set, classify line required ----
if [ "$status_stage" -eq 0 ]; then
  ( cd "$STAGE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$STAGE/Dataset/Axes/${PIECE}_Axis.xyz" "$MESH" ) >> "$LOG" 2>&1; status_mesh=$?
  if grep -q "PAPER-234\] classify: face0" "$LOG"; then classify=1; fi
fi

# ---- 3. edge stage, shipped defaults only ----
if [ "$status_stage" -eq 0 ] && [ "$status_mesh" -eq 0 ] && [ "$classify" -eq 1 ]; then
  ( cd "$STAGE" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGE" ) >> "$LOG" 2>&1; status_edge=$?
fi

# ---- 4. score both lanes against the author lane of the SAME index ----
RECHECK=" Pot_A_Piece_01:0 Pot_D_Piece_03:0 Pot_H_Piece_02:1 Pot_J_Piece_09:1 "
for K in 0 1; do
  OURS=$STAGE/Dataset/Breaklines/$POT/${PIECE}_Breakline_${K}.pcd
  AUTH=$CORP/Breaklines/${PIECE}_Breakline_${K}.pcd
  if [ "$status_stage" -ne 0 ] || [ "$status_mesh" -ne 0 ] || [ "$classify" -ne 1 ]; then
    printf '%s\t%s\t%s\tpipeline\t%s\tstage=%s mesh=%s edge=%s classify=%s\n' "$POT" "$PIECE" "$K" "$status_edge" "$status_stage" "$status_mesh" "$status_edge" "$classify" >> "$RUN/out/errors/${PIECE}.tsv"
    continue
  fi
  if [ ! -s "$OURS" ]; then
    printf '%s\t%s\t%s\texport\t1\tno exported breakline at %s\n' "$POT" "$PIECE" "$K" "$OURS" >> "$RUN/out/errors/${PIECE}.tsv"
    continue
  fi
  if [ ! -s "$AUTH" ]; then
    printf '%s\t%s\t%s\tauthor\t1\tno author breakline at %s\n' "$POT" "$PIECE" "$K" "$AUTH" >> "$RUN/out/errors/${PIECE}.tsv"
    continue
  fi
  ROW=$("$PY" "$RUN/scripts/score292.py" "$POT" "$PIECE" "$K" "$OURS" "$AUTH" 2>>"$LOG")
  STATUS=$?
  if [ $STATUS -ne 0 ] || [ -z "$ROW" ]; then
    printf '%s\t%s\t%s\tscore\t%s\tscore292.py exited %s\n' "$POT" "$PIECE" "$K" "$STATUS" "$STATUS" >> "$RUN/out/errors/${PIECE}.tsv"
    continue
  fi
  printf '%s\n' "$ROW" >> "$RUN/out/lanes/${PIECE}.tsv"
  ATBAR=$(printf '%s' "$ROW" | awk -F'\t' '{print $13}')
  "$PY" "$RUN/scripts/miss_png.py" "$PIECE" "$K" "$OURS" "$AUTH" "$RUN/out/png" "$RUN/out/tiles" "$ATBAR" >> "$LOG" 2>&1 || echo "[TASK] WARN png failed $PIECE lane $K" >> "$LOG"
  case "$RECHECK" in
    *" $PIECE:$K "*) "$PY" "$RUN/scripts/recompute292.py" "$PIECE" "$K" "$OURS" "$AUTH" "$RUN/out/lanes/${PIECE}.tsv" > "$RUN/out/recheck/${PIECE}_Bl${K}.txt" 2>>"$LOG" ;;
  esac
done

# ---- 5. record, then let the trap delete the geometry ----
DUR=$(( $(date +%s) - t0 ))
BIG=$(find "$RUN/out" -type f -size +1M | wc -l)
printf '%s\tstage=%s\tmesh=%s\tedge=%s\tclassify=%s\tsecs=%s\tlanes=%s\tbigfiles_in_out=%s\tstage_root=%s\tstage_tries=%s\tbody_bag=%s\tseed_lines=%s\tstop_lines=%s\tfull263=%s\tvote247=%s\n' \
  "$PIECE" "$status_stage" "$status_mesh" "$status_edge" "$classify" "$DUR" \
  "$(wc -l < "$RUN/out/lanes/${PIECE}.tsv" 2>/dev/null || echo 0)" "$BIG" "$STAGEROOT" "$stage_tries" \
  "$(grep -c "FULL-263\] no-discard" "$LOG")" "$(grep -c "SEED-287" "$LOG")" \
  "$(grep -c "STOP-267" "$LOG")" "$(grep -c "FULL-263\]" "$LOG")" "$(grep -c "VOTE-247" "$LOG")" > "$RUN/out/status/${PIECE}.tsv"
echo "[TASK] done $PIECE in ${DUR}s stage=$status_stage mesh=$status_mesh edge=$status_edge classify=$classify" | tee -a "$LOG"
exit 0