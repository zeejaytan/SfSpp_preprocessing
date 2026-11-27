#!/bin/bash
#SBATCH --job-name=t16-cell
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 16 array cell: Pot J (11 pieces, 21 GT joins) assembled by the pinned
# Hierarchy-T13 binary with ONLY Pot_J_Piece_01_Axis.xyz swapped.  J02..J12 axes and all
# 11 breaklines are checked byte-identical to Ticket 13 T09_ALL before the run, and the
# axis pack plus the tree are hashed before and after.  Scored by the exact Ticket 13
# acc305/score305 pair.  REPORT mode (first arg REPORT) runs the report + render job.
set -uo pipefail

MODE=cell
if [ "$#" -ge 1 ]; then MODE=$1; fi
RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work/t16
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
STATUS=$RUN/logs/run_status.txt

utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
say() { echo "$*" >> "$STATUS"; }

if [ "$MODE" = "REPORT" ]; then
  "$PY" "$WORK/report16.py" --run "$RUN" > "$RUN/logs/report16.log" 2>&1
  RC=$?
  tail -n 60 "$RUN/logs/report16.log" >> "$STATUS" 2>/dev/null || true
  if [ $RC -eq 0 ]; then
    say "report-done $(utc) job=$SLURM_JOB_ID rc=$RC"
  else
    say "report-FAIL $(utc) job=$SLURM_JOB_ID rc=$RC"
  fi
  exit $RC
fi

IDX=$SLURM_ARRAY_TASK_ID
ROW=$(awk -F'\t' -v i="$IDX" '$1==i{print; exit}' "$RUN/logs/array_map.tsv")
ARM=$(printf '%s' "$ROW" | cut -f2)
REP=$(printf '%s' "$ROW" | cut -f3)
AXIS_DIR=$(printf '%s' "$ROW" | cut -f4)
TAG="$ARM"_"$REP"
# Inside an array task SLURM_JOB_ID is the array id; sacct reports the per-task id.
JOBID="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
RESULT=$RUN/out/$TAG
SCORE=$RUN/score/$TAG.tsv
ACCROW=$RUN/score/$TAG.acc.tsv
mkdir -p "$RESULT"
say "cell-start $(utc) job=$JOBID idx=$IDX arm=$ARM rep=$REP"

# ---- inputs: the arm's J01 axis, everything else Ticket 13 T09_ALL ----------------
J01_SHA=$(awk -F'\t' -v a="$ARM" 'NR>1 && $1==a{print $6}' "$RUN/evidence/j01_axes16.tsv")
IDOK=0
if "$PY" "$WORK/verify_tree16.py" --run "$RUN" --tree "$TREE" \
     --axes-dir "$AXIS_DIR" --j01-sha "$J01_SHA" --label "$TAG" \
     > "$RUN/logs/verify_$TAG.log" 2>&1; then
  IDOK=1
fi
say "cell $TAG identity ok=$IDOK j01_sha=$J01_SHA"

# ---- snapshot the tree and the axis pack ------------------------------------------
AXB=$RUN/logs/axis_before_$TAG.txt
AXA=$RUN/logs/axis_after_$TAG.txt
TRB=$RUN/logs/tree_before_$TAG.txt
TRA=$RUN/logs/tree_after_$TAG.txt
( cd "$AXIS_DIR" && sha256sum *_Axis.xyz | sort ) > "$AXB"
( cd "$TREE" && find . -maxdepth 2 -type f | sort | xargs -r sha256sum ) > "$TRB"

WALL0=$(date +%s)
timeout 5400 "$APT" exec --writable-tmpfs \
  --bind "$MAIN:/workspace" \
  --bind "$PANEL:/panel:ro" \
  --bind "$TREE:/Dataset/SfS_pp:ro" \
  --bind "$AXIS_DIR:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" \
  --env OMP_NUM_THREADS=8 \
  "$SIF" bash -euc 'sha256sum -c /panel/logs/executable.sha256; exec /panel/build/Hierarchy-T13 19' \
  > "$RUN/logs/run_$TAG.log" 2>&1
RC=$?
WALL=$(( $(date +%s) - WALL0 ))
( cd "$AXIS_DIR" && sha256sum *_Axis.xyz | sort ) > "$AXA"
( cd "$TREE" && find . -maxdepth 2 -type f | sort | xargs -r sha256sum ) > "$TRA"
POST_SHA=$(sha256sum "$EXE" | awk '{print $1}')
EXEOK=0
if [ $RC -eq 0 ] && [ "$POST_SHA" = "$WANT_SHA" ] && grep -q ': OK$' "$RUN/logs/run_$TAG.log"; then
  EXEOK=1
fi
INOK=0
if cmp -s "$AXB" "$AXA" && cmp -s "$TRB" "$TRA"; then INOK=1; fi
POSES=$(find "$RESULT" -maxdepth 1 -name 'T_*to_*.txt' -size +0 | wc -l)
ONPIECES=$(awk -F'\t' '$1=="J" && $5=="on" {printf "%s%s", sep, $3; sep=","}' "$PIECES_TSV")

bash "$WORK/posecheck13.sh" "$RESULT" "$ONPIECES" > "$RUN/logs/pose_$TAG.log" 2>&1
POSE_RC=$?
say "cell $TAG run rc=$RC wall=$WALL seconds exeok=$EXEOK inok=$INOK poses=$POSES pose_rc=$POSE_RC"

"$PY" "$ACC" "$RESULT" "cell_$TAG" "$ACCROW" > "$RUN/logs/acc_$TAG.log" 2>&1
ACCRC=$?
"$PY" "$SCORER" "$RESULT" "$TREE/Ground Truth" J "$PIECES_TSV" "$SCORE" "cell_$TAG" \
  > "$RUN/logs/score_$TAG.log" 2>&1
SCRC=$?

SHERD_P=0
SHERD_N=0
JOINS_OK=0
JOINS_DEN=0
J01_OK=0
J01_DEN=0
NON_OK=0
NON_DEN=0
if [ $SCRC -eq 0 ] && [ -f "$SCORE" ]; then
  JOINS_DEN=$(awk -F'\t' 'NF==5 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {n++} END{printf "%d", n+0}' "$SCORE")
  JOINS_OK=$(awk -F'\t' 'NF==5 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ && $5=="PASS" {n++} END{printf "%d", n+0}' "$SCORE")
  J01_DEN=$(awk -F'\t' 'NF==5 && ($1==1 || $2==1) {n++} END{printf "%d", n+0}' "$SCORE")
  J01_OK=$(awk -F'\t' 'NF==5 && ($1==1 || $2==1) && $5=="PASS" {n++} END{printf "%d", n+0}' "$SCORE")
  NON_OK=$(( JOINS_OK - J01_OK ))
  NON_DEN=$(( JOINS_DEN - J01_DEN ))
  SHERD_P=$(awk -F'\t' 'NF==4 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9.]+$/ && $4=="PASS" {p++} END{printf "%d", p+0}' "$SCORE")
  SHERD_N=$(awk -F'\t' 'NF==4 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9.]+$/ {n++} END{printf "%d", n+0}' "$SCORE")
else
  say "cell $TAG score missing (acc_rc=$ACCRC score_rc=$SCRC)"
fi
say "cell $TAG joins=$JOINS_OK/$JOINS_DEN j01=$J01_OK/$J01_DEN sherds=$SHERD_P/$SHERD_N"

USABLE=0
if [ $EXEOK -eq 1 ] && [ $INOK -eq 1 ] && [ $IDOK -eq 1 ] && [ $POSE_RC -eq 0 ] \
   && [ "$JOINS_DEN" = "21" ] && [ "$SHERD_N" = "11" ] && [ "$J01_DEN" = "5" ]; then
  USABLE=1
fi
# One row file per cell: the ten array tasks never append to a shared table, so no
# interleaving and no header race; report16.py assembles logs/panel16.tsv from these.
mkdir -p "$RUN/logs/panelrows"
ROWTSV=$RUN/logs/panelrows/$TAG.tsv
printf 'arm\trep\tjobid\tsherds_ok\tsherds_total\tjoins_ok\tjoins_total\tj01_joins_ok\tj01_joins_total\tnon_j01_joins_ok\tnon_j01_joins_total\tusable\tscore\n' > "$ROWTSV"
printf '%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n' \
  "$ARM" "$REP" "$JOBID" "$SHERD_P" "$SHERD_N" "$JOINS_OK" "$JOINS_DEN" \
  "$J01_OK" "$J01_DEN" "$NON_OK" "$NON_DEN" "$USABLE" "$SCORE" >> "$ROWTSV"
say "cell-done $(utc) $TAG usable=$USABLE"
if [ $USABLE -eq 1 ]; then exit 0; else exit 20; fi
