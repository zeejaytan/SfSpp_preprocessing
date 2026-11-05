#!/bin/bash
#SBATCH --job-name=t307-axis
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 307 Stage B -- the axis sets, one variable per arm.
#   Pot A: every arm x seed 0/1/2 -> out/pota/<arm>_s<seed>/   (8 pieces each)
#   Corpus: the 163 pieces in the shipped default and in B1's setting -> out/axes_<arm>/
#   Then out/K.tsv (Pot A shapes), out/census_<arm>.tsv (A2/C3 line counts) and the
#   tier tables of analyse306c.py (coverage of the released lines).
# Arms, one line of code each (ticket 307 Stage A):
#   base = shipped default     COST_PRUNE=1, under-5k step rule ON, stale stage-1 cost
#   b1   = the paper's set     SFS_AXES_COST_PRUNE=0            (no cost<cost[0]*1.1 prune)
#   b5   = the paper's sample  SFS_AXES_ADAPTIVE_UNDER_5K=0     (step=10 always, run_potsac.m:18)
#   b4   = a ranking change    SFS_AXES_POST_REFINE_COST=1      (cost recomputed on all points)
# Corpus read-only: md5 of Surfaces+Axes before and after.
set -uo pipefail

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
mkdir -p "$OUT/pota/timing" "$OUT/logs" "$OUT/timing" logs

ARMS="${ARMS:-base b1 b5 b4}"
SEEDS="${SEEDS:-0 1 2}"

echo "[JOB] runid=$RUNID job=$JOBID arms=[$ARMS] seeds=[$SEEDS]"
md5sum "$CODE"/sfs_axes/*.py > logs/code.md5 2>&1
cat logs/code.md5

md5_corpus() { { ls "$CORP/Surfaces"/*.xyz; ls "$CORP/Axes"/*.xyz; } 2>/dev/null | sort | xargs -d '\n' md5sum; }
md5_corpus > logs/corpus_before.md5
echo "[JOB] corpus files md5'd: $(wc -l < logs/corpus_before.md5)"

cat > "$WORK/one307.sh" <<'EOS'
#!/bin/bash
# one307.sh ARM SEED PIECE RUN CORP PY CODE  -- one Pot A piece in one arm at one seed
A=$1; S=$2; NN=$3; RUN=$4; CORP=$5; PY=$6; CODE=$7
OUT=$RUN/out
case "$A" in
  base) E="SFS_AXES_COST_PRUNE=1" ;;
  b1)   E="SFS_AXES_COST_PRUNE=0" ;;
  b5)   E="SFS_AXES_ADAPTIVE_UNDER_5K=0" ;;
  b4)   E="SFS_AXES_POST_REFINE_COST=1" ;;
  *)    E="SFS_AXES_COST_PRUNE=1" ;;
esac
T0=$(date +%s)
env $E PYTHONPATH=$CODE $PY -m sfs_axes.cli extract-pot-a --surfaces "$CORP/Surfaces" \
    --out "$OUT/pota/${A}_s${S}" --pot A --pieces "$NN" --seed "$S" --verbose \
    > "$OUT/logs/pota_${A}_s${S}_p${NN}.log" 2>&1
RC=$?
T1=$(date +%s)
printf '%s\t%s\t%s\t%s\t%s\n' "$A" "$S" "$NN" "$RC" "$((T1-T0))" > "$OUT/pota/timing/${A}_s${S}_p${NN}.txt"
EOS

cat > "$WORK/one307c.sh" <<'EOS'
#!/bin/bash
# one307c.sh ARM POT NN RUN CORP PY CODE  -- one corpus piece in one arm
A=$1; P=$2; NN=$3; RUN=$4; CORP=$5; PY=$6; CODE=$7
OUT=$RUN/out
case "$A" in
  base) E="SFS_AXES_COST_PRUNE=1" ;;
  b1)   E="SFS_AXES_COST_PRUNE=0" ;;
  b5)   E="SFS_AXES_ADAPTIVE_UNDER_5K=0" ;;
  b4)   E="SFS_AXES_POST_REFINE_COST=1" ;;
  *)    E="SFS_AXES_COST_PRUNE=1" ;;
esac
T0=$(date +%s)
env $E PYTHONPATH=$CODE $PY -m sfs_axes.cli extract-pot-a --surfaces "$CORP/Surfaces" \
    --out "$OUT/axes_$A" --pot "$P" --pieces "$NN" --verbose \
    > "$OUT/logs/${A}_${P}${NN}.log" 2>&1
RC=$?
T1=$(date +%s)
printf '%s\t%s\t%s\t%s\t%s\n' "$A" "$P" "$NN" "$RC" "$((T1-T0))" > "$OUT/timing/${A}_${P}${NN}.txt"
EOS
chmod +x "$WORK/one307.sh" "$WORK/one307c.sh"

echo "[JOB] --- Pot A: $(echo $ARMS | wc -w) arms x $(echo $SEEDS | wc -w) seeds x 8 pieces"
for A in $ARMS; do for S in $SEEDS; do mkdir -p "$OUT/pota/${A}_s${S}"; done; done
for A in $ARMS; do for S in $SEEDS; do for NN in 1 2 3 4 5 6 7 8; do
  printf '%s %s %s\n' "$A" "$S" "$NN"
done; done; done > "$WORK/pota_tasks.txt"
awk -v run="$RUN" -v corp="$CORP" -v py="$PY" -v code="$CODE" \
    '{print $1, $2, $3, run, corp, py, code}' "$WORK/pota_tasks.txt" \
  | xargs -P 8 -L 1 bash "$WORK/one307.sh"
cat "$OUT/pota/timing"/*.txt > "$OUT/pota/timing.tsv"
echo "[JOB] pot A ok: $(awk -F'\t' '$4==0' "$OUT/pota/timing.tsv" | wc -l) / $(wc -l < "$OUT/pota/timing.tsv")"
awk -F'\t' '$4!=0 {print "[JOB] FAILED", $0}' "$OUT/pota/timing.tsv"

echo "[JOB] --- corpus, 163 pieces"
ls "$CORP/Surfaces" | sed -n 's/^Pot_\([A-J]\)_Piece_\([0-9][0-9]\)_Surface_0.xyz$/\1 \2/p' \
  | sort > "$WORK/pieces.txt"
echo "[JOB] pieces: $(wc -l < "$WORK/pieces.txt")"
for A in ${CORPUS_ARMS:-base b1}; do
  echo "[JOB] corpus arm $A start $(date -u +%FT%TZ)"
  awk -v a="$A" -v run="$RUN" -v corp="$CORP" -v py="$PY" -v code="$CODE" \
      '{print a, $1, $2, run, corp, py, code}' "$WORK/pieces.txt" \
    | xargs -P 16 -L 1 bash "$WORK/one307c.sh"
  cat "$OUT/timing"/${A}_*.txt > "$OUT/timing_$A.tsv"
  echo "[JOB] corpus arm $A ok: $(awk -F'\t' '$4==0' "$OUT/timing_$A.tsv" | wc -l) / $(wc -l < "$OUT/timing_$A.tsv")  axes=$(ls "$OUT/axes_$A" | wc -l)  cpu-s=$(awk -F'\t' '{s+=$5} END {print s}' "$OUT/timing_$A.tsv")"
  awk -F'\t' '$4!=0 {print "[JOB] FAILED", $0}' "$OUT/timing_$A.tsv"
  echo "[JOB] corpus arm $A done $(date -u +%FT%TZ)"
done

echo "[JOB] --- tables"
$PY "$WORK/census307.py" pota --pota "$OUT/pota" --released "$CORP/Axes" --out "$OUT/pota/K.tsv" \
  | tee "$OUT/pota/K.txt"
for A in ${CORPUS_ARMS:-base b1}; do
  $PY "$WORK/census307.py" corpus --ours "$OUT/axes_$A" --released "$CORP/Axes" \
      --out "$OUT/census_$A.tsv" --label "$A" | tee "$OUT/census_$A.txt"
  $PY "$WORK/analyse306c.py" --ours "$OUT/axes_$A" --released "$CORP/Axes" \
      --out "$OUT/tier_$A.tsv" | tee "$OUT/tier_$A.txt"
done

md5_corpus > logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; else echo "[JOB] corpus Surfaces+Axes unchanged"; fi
echo "[JOB] complete at $(date -u +%FT%TZ)"
