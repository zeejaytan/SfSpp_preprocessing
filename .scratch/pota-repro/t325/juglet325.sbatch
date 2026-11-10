#!/bin/bash
#SBATCH --job-name=t325-juglet
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 325 bar 5: Juglet end to end, two repeats.
#   O   = Dataset/Axes/Juglet as staged (our September output, the shipped baseline)
#   K3  = axes325 (this ticket) top 3 lines per piece
#   GT  = Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz used directly (oracle control)
# Pre-registration is in the ticket, written before this file was submitted.
# Derived from /data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
JUGLANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
AX_K3=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes/out/axes325
AX_GT=/data/gpfs/projects/punim2657/Dataset/Juglet_GT
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
BLOCK=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel/work/juglet_orig_block.inc

WORK=$RUN/work
TREES=$WORK/trees   # stage67_inputs.py writes here; the tree mount is this path
OUT=$RUN/out
SC=$RUN/score
FLOOR=20
NP=9
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E "^(SFS_|POT_NAME$)"); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID start=$(date -u +%FT%TZ)"

# Patch guard & block
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1 || exit 4
$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log
mkdir -p "$WORK/inc_jug/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_jug/class/data_path.h" NONE --append "$BLOCK" > logs/mk_inc.log 2>&1 || exit 6

# Stage input trees
$PY "$WORK/stage67_inputs.py" --lanes "$JUGLANES" --dataset "$DS" --pota "$CORP" --out "$WORK/trees" > logs/stage.log 2>&1 || exit 7

# Three arms x two repeats. O keeps the staged axes; K3 and GT replace them.
for r in 1 2; do
  for arm in O K3 GT; do
    rm -rf "$TREES/juglet_${arm}_r${r}"
    cp -a "$TREES/juglet" "$TREES/juglet_${arm}_r${r}"
  done
  for i in $(seq 1 9); do
    head -n 3 "$AX_K3/Juglet_Piece_${i}_Axis.xyz" > "$TREES/juglet_K3_r${r}/Axes/Juglet_Piece_${i}_Axis.xyz"
    head -n 3 "$AX_GT/Juglet_Piece_${i}_Axis.xyz" > "$TREES/juglet_GT_r${r}/Axes/Juglet_Piece_${i}_Axis.xyz"
  done
done

# Prove the three trees differ only in Axes/
for r in 1 2; do
  diff -rq "$TREES/juglet_O_r${r}" "$TREES/juglet_K3_r${r}" | grep -v "/Axes/" > logs/treediff_K3_r${r}.log || true
  diff -rq "$TREES/juglet_O_r${r}" "$TREES/juglet_GT_r${r}" | grep -v "/Axes/" > logs/treediff_GT_r${r}.log || true
done

# Warm up /panel/build
$APT exec --writable-tmpfs \
   --bind /data/gpfs:/data/gpfs --bind "$MAIN":/workspace --bind "$WORK":/panel \
   "$SIF" bash -c '
     mkdir -p /panel/build /panel/logs
     cd /panel/build
     cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
     make -j8 > /panel/logs/make.log 2>&1
   ' || exit 9

export OMP_NUM_THREADS=4

runarm() {
  local LABEL=$1 TREE=$2
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs \
     --bind /data/gpfs:/data/gpfs --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" /panel/inc_jug "$NP" -DJUGLET_ORIG > "logs/run_${LABEL}.log" 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$LABEL" "$FLOOR" /panel/inc_jug "$TREE" "$NP" "$RC" "$DT" > "logs/panel_${LABEL}.row"
  echo "##### DONE $LABEL exit=$RC wall=${DT}s $(date -u +%FT%TZ)"
  if [ -d "$OUT/$LABEL" ]; then
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc_${LABEL}.row" >> "logs/acc_${LABEL}.log" 2>&1
    [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
    $PY "$WORK/score58.py" --result "$OUT/$LABEL" --gt "$DS/Juglet_GT" \
        --mesh "$WORK/trees/juglet/Mesh" --lanes "$WORK/trees/juglet/Breaklines" \
        --out "$SC/$LABEL.json" --label "$LABEL" > "logs/score_${LABEL}.log" 2>&1
  fi
}

for r in 1 2; do
  runarm "O_r${r}"  "$TREES/juglet_O_r${r}"
  runarm "K3_r${r}" "$TREES/juglet_K3_r${r}"
  runarm "GT_r${r}" "$TREES/juglet_GT_r${r}"
done

printf "arm\tfloor\tinc\ttree\tnp\texit\twall_s\n" > logs/panel.tsv
printf "label\ttime_s\tsherd\tedge\traw\n" > "$SC/acc.tsv"
for arm in O_r1 K3_r1 GT_r1 O_r2 K3_r2 GT_r2; do
  [ -f "logs/panel_${arm}.row" ] && cat "logs/panel_${arm}.row" >> logs/panel.tsv
  [ -f "$SC/acc_${arm}.row" ] && cat "$SC/acc_${arm}.row" >> "$SC/acc.tsv"
done
cat logs/panel.tsv
cat "$SC/acc.tsv"
echo "[JOB] complete at $(date -u +%FT%TZ)"
