#!/bin/bash
#SBATCH --job-name=t327-swap
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 327 bar 4: causality proof on COPIES. Two trees under work/trees, both copied
# from the 326 juglet GT tree (stage67 inputs, answer-key axes): juglet_GT_ctrl (untouched)
# and juglet_SWAP (S0<->S1 and Breakline_0<-Bl1 on pieces 2, 6 and 9 only). diag326 pair
# harness, pristine 9195c01 objects. Nothing outside this run dir is written.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1640_22151d0_t325-juglet/work
cd "$RUN" || exit 1
mkdir -p logs out "$WORK/logs"
echo "[JOB] $(basename $RUN) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) sif_md5=$(md5sum $SIF | cut -d' ' -f1)"
md5sum $WORK/tools/diag326_pairs.cpp $WORK/diag326.sh
echo "[TREES] ctrl=$(cd $WORK/trees/juglet_GT_ctrl && md5sum Surfaces/* Breaklines/* | md5sum) swap=$(cd $WORK/trees/juglet_SWAP && md5sum Surfaces/* Breaklines/* | md5sum)"

$APT exec --writable-tmpfs --bind "$WORK":/panel "$SIF" bash -c '
  mkdir -p /panel/build && cd /panel/build
  cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
  make -j16 > /panel/logs/make.log 2>&1' || { echo "warm-up failed"; exit 9; }

export OMP_NUM_THREADS=2
one() {
  local LABEL=$1 TREE=$2
  $APT exec --writable-tmpfs --bind "$WORK":/panel --bind "$JUG/inc_jug":/inc:ro --bind "$TREE":/Dataset/SfS_pp:ro \
     "$SIF" bash /panel/diag326.sh "$LABEL" /inc 20 -DJUGLET_ORIG > "out/diag_${LABEL}.txt" 2>&1
  echo "diag $LABEL rc=$?"
}
one jug_GTctrl "$WORK/trees/juglet_GT_ctrl" &
one jug_SWAPr1 "$WORK/trees/juglet_SWAP" &
one jug_SWAPr2 "$WORK/trees/juglet_SWAP" &
wait
echo "[JOB] complete $(date -u +%FT%TZ)"