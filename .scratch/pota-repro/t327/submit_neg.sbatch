#!/bin/bash
#SBATCH --job-name=t327-neg
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=64G
#SBATCH --time=00:40:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 327 bar 4 follow-up: three sign variants of the same juglet_SWAP tree.
#   juglet_SWAPneg     Bl0 normals negated on P2,P6,P9 (the swapped pieces)
#   juglet_SWAPneg7    Bl0 normals negated on P7 only (the untouched partner of pair 6-7)
#   juglet_SWAPnegall  all four negated
# Question: is the residual failure on pairs 1-9 and 6-7 a wall-side error or a
# stored-normal-sign error on the line that comes out of the two-walk writer?
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1640_22151d0_t325-juglet/work
cd "$RUN" || exit 1
mkdir -p logs out
echo "[JOB] $(basename $RUN) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) sif_md5=$(md5sum $SIF | cut -d' ' -f1)"
md5sum $WORK/tools/diag326_pairs.cpp $WORK/diag326.sh
for t in SWAPneg SWAPneg7 SWAPnegall; do
  echo "[TREE $t] $(cd $WORK/trees/juglet_$t && md5sum Surfaces/* Breaklines/* | md5sum)"
done
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
one jug_NEG     "$WORK/trees/juglet_SWAPneg" &
one jug_NEG7    "$WORK/trees/juglet_SWAPneg7" &
one jug_NEGALL  "$WORK/trees/juglet_SWAPnegall" &
wait
echo "[JOB] complete $(date -u +%FT%TZ)"
