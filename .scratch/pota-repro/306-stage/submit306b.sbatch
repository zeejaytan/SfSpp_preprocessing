#!/bin/bash
#SBATCH --job-name=t306b1-union-a
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
# Ticket 306 Stage B1/B2/B3/B4 -- the shipped CLI with the union rule on the
# eight Pot A pieces: every distinct Pottmann basin over 10 deterministic seeds,
# walls untruncated, capped at 6 lines. Writes out/union/ (the axes C1 will
# assemble with), out/rep7 out/rep8 (repeat runs -> determinism), out/paper7
# out/paper8 (the shipped --paper-chain, for comparison) and out/b3.tsv (angles
# to the released lines, worst-surface costs) plus per-piece timing.
#
# Code is the MODIFIED sfs_axes scp'd into work/code (nothing is committed or
# pushed under this ticket); md5 of every module is in logs/code.md5.
# The corpus is read-only: md5 of Surfaces/*.xyz and Axes/*.xyz before and after.
#
# Submit from the run dir: sbatch --export=ALL,RUNID=<id> submit.sbatch
set -uo pipefail

: "${RUNID:?}"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$RUNS/$RUNID
IXTAG=t306b1-union-a
export CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
export PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
export RUN
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

CODE=$RUN/work/code
{ echo "scp'd working tree (ticket 306, not committed)";
  md5sum "$CODE"/sfs_axes/*.py "$RUN"/work/*.py "$RUN"/work/*.sh; } > "$RUN/logs/code.md5"
cat "$RUN/logs/code.md5"
export PYTHONPATH="$CODE"

# --- tasks: "piece mode outdir"
: > "$RUN/work/tasks.txt"
for p in 1 2 3 4 5 6 7 8; do printf "%s union union\n" "$p" >> "$RUN/work/tasks.txt"; done
printf "7 union rep7\n" >> "$RUN/work/tasks.txt"
printf "8 union rep8\n" >> "$RUN/work/tasks.txt"
printf "7 paper paper7\n" >> "$RUN/work/tasks.txt"
printf "8 paper paper8\n" >> "$RUN/work/tasks.txt"
echo "[JOB] tasks: $(wc -l < "$RUN/work/tasks.txt")"

xargs -a "$RUN/work/tasks.txt" -n 3 -P "$P" bash "$RUN/work/run_one_306b.sh"
RC=$?
echo "[JOB] extraction rc=$RC"

echo "[JOB] --- timing (piece mode rc secs)"
cat "$RUN"/out/timing_*.txt 2>/dev/null | sort -k2,2

echo "[JOB] --- written files"
for d in union rep7 rep8 paper7 paper8; do
  echo "[$d]"
  for f in "$RUN"/out/$d/*.xyz; do [ -e "$f" ] && echo "  $(basename "$f") $(wc -l < "$f") lines"; done
done

echo "[JOB] --- determinism (repeat runs must be byte-identical)"
for p in 07 08; do
  d=$([ "$p" = 07 ] && echo rep7 || echo rep8)
  if cmp -s "$RUN/out/union/Pot_A_Piece_${p}_Axis.xyz" "$RUN/out/$d/Pot_A_Piece_${p}_Axis.xyz"; then
    echo "[JOB] piece $p repeat: identical"
  else
    echo "[JOB] piece $p repeat: DIFFERS"
  fi
done

echo "[JOB] --- B3 diagnostics"
"$PY" "$RUN/work/analyse306b.py" --corp "$CORP" --out "$RUN/out" --res "$RUN/out/b3.tsv"

md5_corpus "$RUN/logs/corpus_md5_after.log"
diff "$RUN/logs/corpus_md5_before.log" "$RUN/logs/corpus_md5_after.log" > "$RUN/logs/corpus_md5.diff" || true
if [ -s "$RUN/logs/corpus_md5.diff" ]; then echo "[JOB] WARN corpus changed"; else echo "[JOB] corpus Surfaces+Axes unchanged"; fi
{ echo "runid=$RUNID"; echo "jobid=$JOBID"; echo "commit=working-tree (uncommitted, ticket 306)"; echo "tag=$IXTAG";
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN/run-meta.txt"
echo "[JOB] complete at $(date -u +%FT%TZ)"
