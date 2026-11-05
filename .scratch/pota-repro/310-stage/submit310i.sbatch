#!/bin/bash
#SBATCH --job-name=t310b2-cap
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 stage B2 boundary test: what the converge-before-rank step buys when the
# candidate budget is tight.  Same pool, same seeds, cap baked in (this cluster does not
# export the submitter's environment into the job, so nothing is read from env).
#   UNION0  rank the stage-1 basins, cap, refine the survivors (pre-310 order)
#   BASIN   converge every basin on all points, re-cluster, rank by the worse wall, cap
set -uo pipefail
ARMS="__ARMS__"
SEEDS="__SEEDS__"
CAP="__CAP__"
JOBS="__JOBS__"
RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out
echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ) arms=$ARMS seeds=$SEEDS cap=$CAP"
{ echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- instruments"; md5sum work/*.py work/sfs_axes/*.py
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null
  echo "--- arms/seeds/cap"; echo "$ARMS $SEEDS $CAP"
} > logs/provenance.log 2>&1
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"
$PY work/stage310b2.py --out "$RUN/out" --pot A --pieces 8 --seeds "$SEEDS" \
    --arms "$ARMS" --cap "$CAP" --jobs "$JOBS" --good "$RUN/work/good310.xyz" \
    > logs/stageb2.log 2>&1
BRC=$?
echo "[JOB] stage310b2 rc=$BRC"
grep -E "^\[B2\]|^\[stage310b2\]" logs/stageb2.log || true
[ -f out/b2.tsv ] && cat out/b2.tsv
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
[ -s logs/corpus.diff ] && { echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; } || echo "[JOB] corpus unchanged"
echo "[JOB] done $(date -u +%FT%TZ) brc=$BRC"
exit $BRC
