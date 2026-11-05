#!/bin/bash
#SBATCH --job-name=t310b-refine
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 310 stage B probe -- A4(ii): refine every basin representative on ALL points at
# 1e-9 (what the written file gets) and re-cluster at 10 deg. Piece A_08 x 24 seeds.
# Axes only; no assembly here.
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

$PY work/stage310b.py --out "$RUN/out" --pot A --pieces 8 --seeds 0:24 --jobs 7 \
    --good "$RUN/work/good310.xyz" > logs/stageb.log 2>&1
BRC=$?
echo "[JOB] stage310b rc=$BRC cases=$(ls -d out/p8/s* 2>/dev/null | wc -l)"
tail -30 logs/stageb.log

{ md5sum "$CORP"/Axes/*.xyz; md5sum "$CORP"/Surfaces/*_Surface_*.xyz
  md5sum "$CORP"/Breaklines/*_Breakline_0.pcd; } | sort -k2 > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
[ -s logs/corpus.diff ] && { echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; } || echo "[JOB] corpus unchanged"
[ -f out/summary.tsv ] && { echo "[JOB] out/summary.tsv:"; cat out/summary.tsv; }
echo "[JOB] done $(date -u +%FT%TZ) brc=$BRC"
exit $BRC
