#!/bin/bash
#SBATCH --job-name=t310a4iii
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 A4(iii): the pool x10. A_08, three seeds, 10 000 draws each.
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
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null; } > logs/provenance.log 2>&1
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"
$PY work/stage310h.py --out "$RUN/out" --pot A --piece 8 --seeds 0,1,2 \
    --draws 10000 --good "$RUN/work/good310.xyz" > logs/a4iii.log 2>&1
BRC=$?
echo "[JOB] stage310h rc=$BRC"
cat logs/a4iii.log
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
[ -s logs/corpus.diff ] && { echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; } || echo "[JOB] corpus unchanged"
echo "[JOB] done $(date -u +%FT%TZ) brc=$BRC"
exit $BRC
