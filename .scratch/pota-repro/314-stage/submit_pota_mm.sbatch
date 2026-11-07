#!/bin/bash
#SBATCH --job-name=t314c-pota
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=05:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 314 Stage C: Pot A MMR1 and MMR2 resumption (MOR1 and MOR2 already complete).
set -uo pipefail

POT=A
NAMED=8
NP=8
FLOOR=50

RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
GT="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Ground Truth"

WORK=$RUN/work
TREES=$RUN/trees
OUT=$RUN/out
SC=$RUN/score
JOBID=${SLURM_JOB_ID:-na}

cd "$RUN" || exit 1

tree_path() {
  local L=$1
  case $L in
    MOR*) echo "$TREES/$L/$POT/MO";;
    MMR*) echo "$TREES/$L/$POT/MM";;
  esac
}

export OMP_NUM_THREADS=8

run_and_score() {
  local LABEL=$1 ARM=$2
  local TREE
  TREE=$(tree_path "$LABEL")
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs \
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
for arm in MMR1 MMR2; do
  base_arm="${arm%R*}"
  run_and_score "$arm" "$base_arm" &
  pids+=($!)
  sleep 2
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

printf 'arm\tfloor\tinc\ttree\tnp\texit\twall_s\n' > logs/panel.tsv
printf 'label\ttime_s\tsherd\tedge\traw\n' > "$SC/acc.tsv"
for arm in MOR1 MOR2 MMR1 MMR2; do
  [ -f "logs/panel_${arm}.row" ] && cat "logs/panel_${arm}.row" >> logs/panel.tsv
  [ -f "$SC/acc_${arm}.row" ] && cat "$SC/acc_${arm}.row" >> "$SC/acc.tsv"
done

echo "=== panel.tsv ==="
cat logs/panel.tsv
echo "=== score/acc.tsv ==="
cat "$SC/acc.tsv"

echo "[JOB] complete at $(date -u +%FT%TZ)"
