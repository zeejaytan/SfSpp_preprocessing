#!/bin/bash
#SBATCH --job-name=t309a-axes
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
# Ticket 309 Stage A -- is each of the 44 released axis lines (13 pieces) a stationary
# point of OUR cost on the surfaces we ship, and how dear is it against our own best line.
#   V3 first: B-spline resampled surfaces (our implementation, paper :155), then A1-A3
#   on V1 (shipped, walls whole), V2 (read_surfaces.m truncate), V3.
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
cd "$RUN" || exit 1
mkdir -p logs out

fail() { local rc=$1; shift; { echo "jobid=$JOBID"; echo "rc=$rc"; echo "reason: $*"; } > "$RUN/RUN-FAILED.txt"; echo "[JOB] FATAL rc=$rc $*"; exit "$rc"; }

corpus_md5() {
  { md5sum "$CORP"/Axes/*.xyz
    md5sum "$CORP"/Surfaces/*_Surface_*.xyz
    md5sum "$CORP"/Breaklines/*_Breakline_0.pcd
  } | sort -k2 > "$1"
}

echo "[JOB] jobid=$JOBID start $(date -u +%FT%TZ)"
{ echo "jobid $JOBID"; date -u +%FT%TZ
  echo "--- instruments"; md5sum work/*.py work/sfs_axes/*.py
  echo "--- commit"; cat work/code_commit.txt 2>/dev/null
} > logs/provenance.log 2>&1
corpus_md5 logs/corpus_before.md5
echo "[JOB] corpus paths before: $(wc -l < logs/corpus_before.md5)"

$PY work/bspline309.py --corpus "$CORP" --out "$RUN/out/v3" > logs/v3.log 2>&1
VRC=$?
tail -20 logs/v3.log
echo "[JOB] bspline309 rc=$VRC"

$PY work/stagea309.py --corpus "$CORP" --v3 "$RUN/out/v3" --out "$RUN/out" --seed 0 > logs/stagea.log 2>&1
ARC=$?
tail -40 logs/stagea.log
echo "[JOB] stagea309 rc=$ARC"

corpus_md5 logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus unchanged ($(wc -l < logs/corpus_before.md5) paths)"; fi

wc -l out/stageA.tsv out/variants.tsv out/errors.tsv out/v3/v3.tsv 2>/dev/null
echo "[JOB] done $(date -u +%FT%TZ) v3rc=$VRC arc=$ARC"
[ "$VRC" -eq 0 ] || exit 10
[ "$ARC" -eq 0 ] || exit 11
