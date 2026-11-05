#!/bin/bash
#SBATCH --job-name=t310p-offparity
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:40:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 B4: is the OFF value of SFS_AXES_CONVERGE_BEFORE_RANK the pre-310 code?
# Two copies of the package -- HEAD (this ticket's base commit) and the worktree edit --
# run the same pool on the same seeds; the axis arrays are then compared to the last bit.
set -uo pipefail
POT="__POT__"
PIECES="__PIECES__"
SEEDS="__SEEDS__"
CAP="__CAP__"
SWITCH_OFF="__SWOFF__"
RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out
echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ) pot=$POT pieces=$PIECES seeds=$SEEDS cap=$CAP"
{ echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null
  echo "--- instruments"; md5sum work/*.py work/new/sfs_axes/*.py work/head/sfs_axes/*.py
  echo "--- head potsac differs from new in these hunks:"
  diff -u work/head/sfs_axes/potsac.py work/new/sfs_axes/potsac.py | head -80
} > logs/provenance.log 2>&1
# Same pool, same seeds: the only difference between the two runs is the package.
$PY work/stage310p.py --out "$RUN/out" --pkg "$RUN/work/head" --tag head \
   --pot "$POT" --pieces "$PIECES" --seeds "$SEEDS" --cap "$CAP" --corpus "$CORP" \
   > logs/head.log 2>&1
echo "[JOB] head rc=$?"
SFS_AXES_CONVERGE_BEFORE_RANK="$SWITCH_OFF" $PY work/stage310p.py --out "$RUN/out" \
   --pkg "$RUN/work/new" --tag newoff --pot "$POT" --pieces "$PIECES" \
   --seeds "$SEEDS" --cap "$CAP" --corpus "$CORP" > logs/newoff.log 2>&1
echo "[JOB] newoff rc=$?"
cat logs/head.log logs/newoff.log
echo "--- comparison: HEAD package vs worktree package with the switch OFF"
$PY work/cmp310p.py --a "$RUN/out/head" --b "$RUN/out/newoff" \
   --label "HEAD vs new(switch=$SWITCH_OFF)" --good "$RUN/work/good310.xyz" \
   > logs/compare.log 2>&1
cat logs/compare.log
echo "[JOB] done $(date -u +%FT%TZ)"
