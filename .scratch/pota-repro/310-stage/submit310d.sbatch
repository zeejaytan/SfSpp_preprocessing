#!/bin/bash
#SBATCH --job-name=t310b3-corpus
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 stage B3/C3: every corpus piece through the basin rule, axes to NEW paths
# under out/axes310/. Corpus read only; before/after md5 over the 652 paths.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out
echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ)"
{ echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- instruments"; md5sum work/*.py work/sfs_axes/*.py
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null
  echo "--- rule switch: CONVERGE_BEFORE_RANK=${RULE:-1}"
} > logs/provenance.log 2>&1
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"

if [ -n "${ONLY:-}" ]; then
  $PY work/corpus310.py --out "$RUN/out" --jobs ${JOBS:-20} --cap 6 --seeds ${SEEDS:-10} \
      --only "${ONLY}" > logs/corpus310.log 2>&1
else
  $PY work/corpus310.py --out "$RUN/out" --jobs ${JOBS:-20} --cap 6 --seeds ${SEEDS:-10} \
      > logs/corpus310.log 2>&1
fi
BRC=$?
echo "[JOB] corpus310 rc=$BRC"
tail -60 logs/corpus310.log

{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
[ -s logs/corpus.diff ] && { echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; } || echo "[JOB] corpus unchanged"
echo "[JOB] corpus_before.md5 paths: $(wc -l < logs/corpus_before.md5)"
echo "[JOB] axes310 files: $(ls out/axes310/*.xyz 2>/dev/null | wc -l) lines: $(cat out/axes310/*.xyz 2>/dev/null | wc -l)"
echo "[JOB] done $(date -u +%FT%TZ) brc=$BRC"
exit $BRC
