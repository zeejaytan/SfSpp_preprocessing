#!/bin/bash
#SBATCH --job-name=t306a-pool
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 306 Stage A -- the axis candidate pool BEFORE dedup and before the cost
# prune, for Pot A pieces 01 (control), 07, 08; truncation on and off; seeds 0,1;
# plus the A3 provenance probe on Piece 08's released line 1.
#
# Code is pinned by commit: work/code is 'git archive <NEW> sfs_axes' from the
# canonical checkout; probe306.py is scp'd into work/ and its md5 recorded.
# Nothing here writes to the corpus; md5 of Surfaces/*.xyz and Axes/*.xyz is taken
# before and after and must match.
#
# Submit from the run dir: sbatch --export=ALL,NEW=<sha>,RUNID=<id> submit.sbatch
set -uo pipefail

: "${NEW:?}" "${RUNID:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t306a-pool
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-16}

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p logs work out

echo "[JOB] runid=$RUNID job=$JOBID host=$(hostname) at $(date -u +%FT%TZ)"
echo "[JOB] env SFS_* present: $(compgen -e | grep -c '^SFS_') (expect 0)"

md5_corpus() { local out=$1
  { md5sum "$CORP"/Surfaces/*.xyz "$CORP"/Axes/*.xyz; } | sort -k2 > "$out"; }
md5_corpus "$RUN/logs/corpus_md5_before.log"

fetch_ok=0
for i in 1 2 3 4 5; do
  if git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> "$RUN/logs/fetch.log" 2>&1; then fetch_ok=1; break; fi
  sleep $((10 * i))
done
[ "$fetch_ok" -eq 1 ] || { echo "[JOB] FATAL fetch"; exit 2; }
git -C "$CANON" rev-parse --verify --quiet "$NEW^{commit}" >/dev/null 2>&1 || { echo "[JOB] FATAL commit $NEW absent on origin"; exit 2; }
CODE=$RUN/work/code
rm -rf "$CODE"; mkdir -p "$CODE"
git -C "$CANON" archive "$NEW" sfs_axes | tar -x -C "$CODE" || { echo "[JOB] FATAL archive sfs_axes"; exit 3; }
{ echo "commit $NEW"; md5sum "$CODE"/sfs_axes/*.py; md5sum "$RUN/work/probe306.py"; } > "$RUN/logs/code.md5"
cat "$RUN/logs/code.md5"
export PYTHONPATH="$CODE"

# --- pool: 3 pieces x 2 truncation settings x 2 seeds = 12 cases, one process each
: > "$RUN/work/tasks_pool.txt"
for piece in 1 7 8; do
  for tr in 0 1; do
    for seed in 0 1; do
      printf "%s %s %s\n" "$piece" "$tr" "$seed" >> "$RUN/work/tasks_pool.txt"
    done
  done
done
echo "[JOB] pool cases: $(wc -l < "$RUN/work/tasks_pool.txt")"

PROBE_NO_SUMMARY=1 xargs -a "$RUN/work/tasks_pool.txt" -n 3 -P "$P" \
  bash -c 'PROBE_NO_SUMMARY=1 "$0" "$1" --surfaces "$2" --out "$3" --pot A \
           --pieces "$4" --trunc "$5" --seeds "$6" \
           > "$3"/../log_$4_t$5_s$6.txt 2>&1' \
  "$PY" "$RUN/work/probe306.py" "$CORP/Surfaces" "$RUN/out" 
RC_POOL=$?
echo "[JOB] pool rc=$RC_POOL"

# --- A3: released-line provenance probe, Piece 08, both clouds
for tr in 0 1; do
  $PY "$RUN/work/probe306.py" --mode released --surfaces "$CORP/Surfaces" \
      --out "$RUN/out" --pot A --pieces 8 --trunc "$tr" --line 1 \
      > "$RUN/logs/released_t$tr.log" 2>&1
  echo "[JOB] released trunc=$tr rc=$?"
done

# --- inventory
find "$RUN/out" -name '*.tsv' -o -name '*.json' -o -name '*.xyz' | sort > "$RUN/logs/out_files.txt"
wc -l "$RUN/logs/out_files.txt"
head -3 "$RUN/out/pool"/*/*/clusters.tsv 2>/dev/null | head -40

md5_corpus "$RUN/logs/corpus_md5_after.log"
diff "$RUN/logs/corpus_md5_before.log" "$RUN/logs/corpus_md5_after.log" > "$RUN/logs/corpus_md5.diff" || true
if [ -s "$RUN/logs/corpus_md5.diff" ]; then echo "[JOB] WARN corpus changed"; else echo "[JOB] corpus Surfaces+Axes unchanged"; fi
{ echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=$NEW"; echo "tag=$IXTAG";
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN/run-meta.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"
