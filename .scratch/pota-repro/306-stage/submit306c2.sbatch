#!/bin/bash
#SBATCH --job-name=t306c-corpus
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 306 Stage C3 -- extract axes for all 163 corpus pieces into a NEW out/axes path.
# MODE=paper  : the paper chain (run_potsac, single seed, 10-deg dedup, cost*1.1 prune)
# MODE=papernotrunc : the same chain with the walls WHOLE (B1 default) -- the B1-only arm
# MODE=union  : the S=10 seed union (no cost*1.1 prune, worst-wall ranking, cap 6)
# Corpus read-only: md5 before and after.
set -uo pipefail

RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RUN=$SLURM_SUBMIT_DIR
RUNID=$(basename "$RUN")
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
CODE=$WORK/code
OUT=$RUN/out
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$OUT/axes" "$OUT/logs" "$OUT/timing" logs

MODE=${MODE:-union}
echo "[JOB] runid=$RUNID job=$JOBID mode=$MODE"
echo "[JOB] code=$CODE"
md5sum "$CODE"/sfs_axes/*.py > logs/code.md5 2>&1
cat logs/code.md5

md5_corpus() {
  { ls "$CORP/Surfaces"/*.xyz; ls "$CORP/Axes"/*.xyz; } 2>/dev/null | sort | xargs -d '\n' md5sum
}
md5_corpus > logs/corpus_before.md5
echo "[JOB] corpus files md5'd: $(wc -l < logs/corpus_before.md5)"

# piece list straight from the corpus: one line "POT NN" per piece with a Surface_0
ls "$CORP/Surfaces" | sed -n 's/^Pot_\([A-J]\)_Piece_\([0-9][0-9]\)_Surface_0.xyz$/\1 \2/p' \
  | sort > "$WORK/pieces.txt"
echo "[JOB] pieces: $(wc -l < "$WORK/pieces.txt")"
awk '{print $1}' "$WORK/pieces.txt" | uniq -c | tr '\n' ' '; echo

cat > "$WORK/run_one_306c.sh" <<'EOS'
#!/bin/bash
P=$1; NN=$2
RUN=$3; CORP=$4; PY=$5; CODE=$6
MODE=${MODE:-union}
OUT=$RUN/out
T0=$(date +%s)
case "$MODE" in
  paper)        EXTRA="--paper-chain --truncate" ;;
  papernotrunc) EXTRA="--paper-chain" ;;
  *)            EXTRA="" ;;
esac
PYTHONPATH=$CODE $PY -m sfs_axes.cli extract-pot-a --surfaces "$CORP/Surfaces" \
    --out "$OUT/axes" --pot "$P" --pieces "$NN" $EXTRA --verbose > "$OUT/logs/${P}${NN}.log" 2>&1
RC=$?
T1=$(date +%s)
printf '%s\t%s\t%s\t%s\n' "$P" "$NN" "$RC" "$((T1-T0))" > "$OUT/timing/${P}${NN}.txt"
EOS
chmod +x "$WORK/run_one_306c.sh"

echo "[JOB] start $(date -u +%FT%TZ)"
export MODE
awk -v run="$RUN" -v corp="$CORP" -v py="$PY" -v code="$CODE" \
    '{print $1, $2, run, corp, py, code}' "$WORK/pieces.txt" \
  | xargs -P 16 -L 1 bash "$WORK/run_one_306c.sh"
echo "[JOB] extraction done $(date -u +%FT%TZ)"

cat "$OUT/timing"/*.txt > "$OUT/timing.tsv"
echo "[JOB] pieces ok: $(awk -F'\t' '$3==0' "$OUT/timing.tsv" | wc -l) / $(wc -l < "$OUT/timing.tsv")"
awk -F'\t' '$3!=0 {print "[JOB] FAILED", $0}' "$OUT/timing.tsv"
echo "[JOB] total cpu-seconds: $(awk -F'\t' '{s+=$4} END {print s}' "$OUT/timing.tsv")"
echo "[JOB] slowest:"; sort -t$'\t' -k4 -n -r "$OUT/timing.tsv" | head -5

ls "$OUT/axes" | wc -l

md5_corpus > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus Surfaces+Axes unchanged"; fi
echo "[JOB] complete at $(date -u +%FT%TZ)"