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
# Ticket 301 -- ONE piece, both arms, one node, built from a pushed commit.
# The ctrl arm assembles Pot D with the authors' corpus axis for every piece; the swap arm assembles
# the same bundle with ONLY the target piece's axis replaced by the direction its own reference pose
# implies. Ticket 299 measured that two replays of an identical bundle disagree (886 vs 888 pruned
# pairs, poses tens of degrees apart), so a swap run is only readable next to a control assembled in
# the same job, on the same node, from the same bytes.
#
# Submit from the ctrl run directory, so that logs/slurm-%j.out lands in a run directory:
#   cd <RUN_CTRL> && sbatch --export=ALL RUN_CTRL=<RUN_CTRL> RUN_SWAP=<RUN_SWAP> \
#       TARGET=Pot_D_Piece_18 COMMIT=<sha> submit.sbatch
#
# The tree is unpacked from the pushed commit by run_from_commit.sh and deleted when the job exits
# (docs/agents/workspace-hygiene.md, "One ticket, start to finish"). The canonical Spartan checkout
# is only read, never edited.
set -uo pipefail

: ${RUN_CTRL:?RUN_CTRL must be exported: the ctrl run directory}
: ${RUN_SWAP:?RUN_SWAP must be exported: the swap run directory}
: ${TARGET:?TARGET must be exported: e.g. Pot_D_Piece_18}
: ${COMMIT:?COMMIT must be exported: the pushed commit this job builds from}

CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RFC=/data/gpfs/projects/punim2657/agent/pr-workspace/scripts/run_from_commit.sh
PYRUN=${PYRUN:-/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3}
TARGET_NUM=$((10#${TARGET##*_Piece_}))
CTRL_ID=$(basename "$RUN_CTRL")
SWAP_ID=$(basename "$RUN_SWAP")

mkdir -p "$RUN_CTRL/logs" "$RUN_CTRL/out" "$RUN_CTRL/scripts" \
         "$RUN_SWAP/logs" "$RUN_SWAP/out" "$RUN_SWAP/scripts"
echo "[JOB] job=${SLURM_JOB_ID:-none} node=$(hostname) start=$(date -Is) target=$TARGET commit=$COMMIT"
echo "[JOB] ctrl run: $RUN_CTRL"
echo "[JOB] swap run: $RUN_SWAP"

# ---------------------------------------------------------------- the tree, from the pushed commit
source "$RFC" "$CANON" "$COMMIT" "$RUN_CTRL" || { echo "[JOB] FATAL run_from_commit failed"; exit 30; }
cd "$SRC" || exit 30
S="$SRC/.scratch/pota-repro/301"
echo "[JOB] src=$SRC commit=$SOURCE_COMMIT"
cp -f "$S/p301-submit.sbatch" "$RUN_CTRL/submit.sbatch"
cp -f "$S/p301-submit.sbatch" "$RUN_SWAP/submit.sbatch"
[ -f "$RUN_CTRL/source.txt" ] && cp -f "$RUN_CTRL/source.txt" "$RUN_SWAP/source.txt"

# ---------------------------------------------------------------- what each run IS (run.json, start)
"$PYRUN" "$S/p301_runjson.py" --run-dir "$RUN_CTRL" --phase start --role ctrl --target "$TARGET_NUM" \
    --runid "$CTRL_ID" --tag "${CTRL_ID#*_*_}" --commit "$SOURCE_COMMIT" --sibling "$SWAP_ID"
"$PYRUN" "$S/p301_runjson.py" --run-dir "$RUN_SWAP" --phase start --role swap --target "$TARGET_NUM" \
    --runid "$SWAP_ID" --tag "${SWAP_ID#*_*_}" --commit "$SOURCE_COMMIT" --sibling "$CTRL_ID"

# ---------------------------------------------------------------- arm 1: control
echo "[JOB] ---- ctrl arm $(date -Is)"
bash "$S/p301-arm.sh" "$RUN_CTRL" ctrl "$TARGET" 2>&1 | tee "$RUN_CTRL/logs/arm.log"
RC_C=${PIPESTATUS[0]}
echo "$RC_C" > "$RUN_CTRL/out/arm_exit.txt"
echo "[JOB] ctrl arm exit $RC_C $(date -Is)"

# ---------------------------------------------------------------- arm 2: the swap
echo "[JOB] ---- swap arm $(date -Is)"
bash "$S/p301-arm.sh" "$RUN_SWAP" swap "$TARGET" 2>&1 | tee "$RUN_SWAP/logs/arm.log"
RC_S=${PIPESTATUS[0]}
echo "$RC_S" > "$RUN_SWAP/out/arm_exit.txt"
echo "[JOB] swap arm exit $RC_S $(date -Is)"

# ---------------------------------------------------------------- what each run DID (run.json, end)
"$PYRUN" "$S/p301_runjson.py" --run-dir "$RUN_CTRL" --phase end --role ctrl
"$PYRUN" "$S/p301_runjson.py" --run-dir "$RUN_SWAP" --phase end --role swap
for R in "$RUN_CTRL" "$RUN_SWAP"; do
  echo "[JOB] summary $R"
  cat "$R/out/summary.txt" 2>/dev/null
  md5sum "$R/run.json" 2>/dev/null
done

echo "[JOB] done $(date -Is) ctrl=$RC_C swap=$RC_S"
[ "$RC_C" = "0" ] && [ "$RC_S" = "0" ] && exit 0
exit 1
