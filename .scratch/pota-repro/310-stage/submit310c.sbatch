#!/bin/bash
#SBATCH --job-name=t310b2-basin
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
# Ticket 310 stage B2: the basin rule (converge-before-rank) vs the authors' order,
# same pool, same seeds, Piece A_08 x 12 seeds. Axes only; no assembly here.
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
} > logs/provenance.log 2>&1
{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"
echo "[JOB] good310.xyz (scoring only, one line expected):"
cat work/good310.xyz

$PY work/stage310b2.py --out "$RUN/out" --pot A --pieces 8 --seeds 0:12 \
    --arms ON,OFF --cap 6 --jobs 7 --good "$RUN/work/good310.xyz" \
    > logs/stageb2.log 2>&1
BRC=$?
echo "[JOB] stage310b2 rc=$BRC"
tail -40 logs/stageb2.log

{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
[ -s logs/corpus.diff ] && { echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; } || echo "[JOB] corpus unchanged"
[ -f out/b2.tsv ] && { echo "[JOB] out/b2.tsv:"; cat out/b2.tsv; }
echo "[JOB] done $(date -u +%FT%TZ) brc=$BRC"
exit $BRC
