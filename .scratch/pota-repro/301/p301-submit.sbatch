#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p301swap
#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 301 -- ONE piece, both arms, one node. The ctrl arm assembles Pot D with the authors' corpus
# axis for every piece; the swap arm assembles the same bundle with ONLY the target piece's axis
# replaced by the direction its own reference pose implies. Ticket 299 measured that two replays of an
# identical bundle disagree (886 vs 888 pruned pairs, poses tens of degrees apart), so a swap run is
# only readable next to a control assembled in the same job, on the same node, from the same bytes.
#
# Submit from the ctrl run directory, so that logs/slurm-%j.out lands in a run directory:
#   cd <RUN_CTRL> && TARGET=Pot_D_Piece_18 sbatch --export=ALL \
#       RUN_CTRL=<RUN_CTRL> RUN_SWAP=<RUN_SWAP> TARGET=$TARGET submit.sbatch
set -uo pipefail

: ${RUN_CTRL:?RUN_CTRL must be exported: the ctrl run directory}
: ${RUN_SWAP:?RUN_SWAP must be exported: the swap run directory}
: ${TARGET:?TARGET must be exported: e.g. Pot_D_Piece_18}

mkdir -p "$RUN_CTRL/logs" "$RUN_CTRL/out" "$RUN_SWAP/logs" "$RUN_SWAP/out"
echo "[JOB] job=$SLURM_JOB_ID node=$(hostname) start=$(date -Is) target=$TARGET"
echo "[JOB] ctrl run: $RUN_CTRL"
echo "[JOB] swap run: $RUN_SWAP"
echo "[JOB] this job runs both arms sequentially; each arm is ~40-55 min"

bash "$RUN_CTRL/scripts/p301-arm.sh" "$RUN_CTRL" ctrl "$TARGET" 2>&1 | tee "$RUN_CTRL/logs/arm.log"
RC_C=${PIPESTATUS[0]}
echo "[JOB] ctrl arm exit $RC_C"
echo "$RC_C" > "$RUN_CTRL/out/arm_exit.txt"

bash "$RUN_SWAP/scripts/p301-arm.sh" "$RUN_SWAP" swap "$TARGET" 2>&1 | tee "$RUN_SWAP/logs/arm.log"
RC_S=${PIPESTATUS[0]}
echo "[JOB] swap arm exit $RC_S"
echo "$RC_S" > "$RUN_SWAP/out/arm_exit.txt"

echo "[JOB] done $(date -Is) ctrl=$RC_C swap=$RC_S"
[ "$RC_C" = "0" ] && [ "$RC_S" = "0" ] && exit 0
exit 1
