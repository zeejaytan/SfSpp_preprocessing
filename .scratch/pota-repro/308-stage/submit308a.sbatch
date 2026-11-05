#!/bin/bash
#SBATCH --job-name=t308a-axis
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 308 Stage A -- the axis set at the shipped 308 default (MM), the prune-on
# set (MMp), the Pot A seed sweep, the Juglet axes, and the 305 reproduction; then
# the provenance + census tables (A1, A2, D1).  No assembly here.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
RUNID=$(basename "$RUN")
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
WORK=$RUN/work
OUT=$RUN/out
JUGG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
REF307=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0437_e6adf69_t307f-def/out/axes_paper
REF305=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0420_9c5eec2_t305-axes-corpus/out/axes305
REFJUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0422_e6adf69_t307d-jug/out/jug/axes307
JOBID=${SLURM_JOB_ID:-na}

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p logs work out

echo "[JOB] runid=$RUNID job=$JOBID host=$(hostname) at $(date -u +%FT%TZ)"
echo "[JOB] SFS_* env present: $(compgen -e | grep -c '^SFS_') (expect 0)"
{ echo "commit $(cat work/code_commit.txt 2>/dev/null || echo na)"
  md5sum "$WORK"/sfs_axes/*.py "$WORK"/axes305.py "$WORK"/census308.py \
         "$WORK"/census307.py "$WORK"/analyse306c.py 2>/dev/null; } > logs/code.md5
cat logs/code.md5

export PYTHONPATH="$WORK"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

# ---- D1 corpus guard: Axes, Breakline_0 and every surface
md5_corp() { local out=$1
  { md5sum "$CORP"/Axes/*.xyz "$CORP"/Breaklines/*_Breakline_0.pcd 2>/dev/null
    ls "$CORP"/Surfaces/*.xyz | xargs -r -P 8 md5sum 2>/dev/null; } | sort -k2 > "$out"; }
md5_corp logs/corpus_before.md5
echo "[JOB] corpus files md5'd before: $(wc -l < logs/corpus_before.md5)"

pieces_for() { ls "$CORP/Surfaces" | sed -n "s/^Pot_$1_Piece_\([0-9][0-9]\)_Surface_0\.xyz$/\1/p" \
                 | sort -n | paste -sd, -; }

run_cli() {  # $1=out $2=pot $3=pieces $4=seed
  $PY -m sfs_axes.cli extract-pot-a --surfaces "$CORP/Surfaces" --pot "$2" \
      --pieces "$3" --seed "${4:-0}" --out "$1"
}

extract_all() {  # $1=out $2=prune(0|1)
  local out=$1 prune=$2 P plist
  for P in A B C D E F G H I J; do
    (
      export SFS_AXES_COST_PRUNE=$prune
      plist=$(pieces_for "$P")
      [ -z "$plist" ] && exit 0
      run_cli "$out" "$P" "$plist" 0
    ) > "logs/extract_$(basename "$out")_$P.log" 2>&1 &
  done
  wait
}

echo "[JOB] == MM set: paper chain, walls whole, prune off (shipped 308 default)"
extract_all "$OUT/axes_paper" 0
echo "[JOB] MM files: $(ls "$OUT/axes_paper"/*.xyz 2>/dev/null | wc -l)"
grep -h "piece .* K=" logs/extract_axes_paper_*.log 2>/dev/null | wc -l

echo "[JOB] == MMp set: same, SFS_AXES_COST_PRUNE=1"
extract_all "$OUT/axes_prune" 1
echo "[JOB] MMp files: $(ls "$OUT/axes_prune"/*.xyz 2>/dev/null | wc -l)"

echo "[JOB] == Pot A seed sweep, 8 seeds"
mkdir -p "$OUT/pota"
for S in 0 1 2 3 4 5 6 7; do
  ( plist=$(pieces_for A); run_cli "$OUT/pota/paper_s$S" A "$plist" "$S" ) \
      > "logs/pota_s$S.log" 2>&1 &
done
wait
for S in 0 1 2 3 4 5 6 7; do
  echo "[JOB]   seed $S: $(ls "$OUT/pota/paper_s$S"/*.xyz 2>/dev/null | wc -l) files"
done

echo "[JOB] == Juglet axes (paper chain, walls whole, seed 0) from the t66 walls"
AD=$WORK/jugsurf
rm -rf "$AD"; mkdir -p "$AD"
for n in 1 2 3 4 5 6 7 8 9; do
  nn=$(printf "%02d" "$n")
  ln -sf "$JUGG/Juglet_Piece_${n}.S0" "$AD/Pot_JUGLET_Piece_${nn}_Surface_0.xyz"
  ln -sf "$JUGG/Juglet_Piece_${n}.S1" "$AD/Pot_JUGLET_Piece_${nn}_Surface_1.xyz"
done
$PY "$WORK/axes305.py" --surfaces "$AD" --out "$OUT/jug" --pot JUGLET --seeds 1 \
    --truncate 0 --jobs 9 --write-seeds 1 > logs/axes_jug.log 2>&1
echo "[JOB] juglet axes rc=$?"
mkdir -p "$OUT/jug/axes_paper"
for n in 1 2 3 4 5 6 7 8 9; do
  nn=$(printf "%02d" "$n")
  src=$OUT/jug/axes305/Pot_JUGLET_Piece_${nn}_Axis.xyz
  dst=$OUT/jug/axes_paper/Juglet_Piece_${n}_Axis.xyz
  if [ -s "$src" ]; then cp -f "$src" "$dst"; else : > "$dst"; fi
  printf "[JOB]   Juglet_Piece_%s %s lines\n" "$n" "$(wc -l < "$dst")"
done

echo "[JOB] == 305 reproduction: the 305 chain (truncate 1, prune on, seed-0 files)"
SFS_AXES_COST_PRUNE=1 $PY "$WORK/axes305.py" --surfaces "$CORP/Surfaces" \
    --out "$OUT/axes_305repro" --pot ALL --truncate 1 --seeds 0 --jobs 16 \
    > logs/axes_305repro.log 2>&1
echo "[JOB] 305repro rc=$?"
tail -4 logs/axes_305repro.log

echo "[JOB] == A1 provenance: fresh MM set vs the reused 307f set"
$PY "$WORK/census308.py" md5 --ours "$OUT/axes_paper" --ref "$REF307" \
    --out "$OUT/census_fresh_vs_307f.tsv" --label "fresh 308 MM vs reused 307f axes_paper"

echo "[JOB] == A2 change census: fresh MM set vs the 305 set"
$PY "$WORK/census308.py" md5 --ours "$OUT/axes_paper" --ref "$REF305" \
    --out "$OUT/census_fresh_vs_305.tsv" --label "fresh 308 MM vs 305 axes305"
$PY "$WORK/census308.py" k --ours "$OUT/axes_paper" --ref "$REF305" \
    --out "$OUT/census_k_vs_305.tsv" --label "308 MM vs 305 axes305 (K, line0, best line)"

echo "[JOB] == 305 reproduction check (expect 163 equal)"
$PY "$WORK/census308.py" md5 --ours "$OUT/axes_305repro/axes305" --ref "$REF305" \
    --out "$OUT/census_305repro.tsv" --label "305-repro vs 305 axes305"

echo "[JOB] == the prune effect on the axis set (MMp vs MM)"
$PY "$WORK/census308.py" k --ours "$OUT/axes_prune" --ref "$OUT/axes_paper" \
    --out "$OUT/census_prune_vs_paper.tsv" --label "MMp vs MM axis set"

echo "[JOB] == K census vs the released axis files (220 lines)"
$PY "$WORK/census307.py" corpus --ours "$OUT/axes_paper" --released "$CORP/Axes" \
    --out "$OUT/census_paper_vs_released.tsv" --label "308 MM" | tee logs/census_paper_vs_released.txt
$PY "$WORK/census307.py" corpus --ours "$OUT/axes_prune" --released "$CORP/Axes" \
    --out "$OUT/census_prune_vs_released.tsv" --label "308 MMp" | tee logs/census_prune_vs_released.txt

echo "[JOB] == tier census (5/10/20 deg) vs the released files"
$PY "$WORK/analyse306c.py" --ours "$OUT/axes_paper" --released "$CORP/Axes" \
    --out "$OUT/tier_paper.tsv" --summary "$OUT/tier_paper_summary.tsv" 2>&1 | tail -20
$PY "$WORK/analyse306c.py" --ours "$OUT/axes_prune" --released "$CORP/Axes" \
    --out "$OUT/tier_prune.tsv" --summary "$OUT/tier_prune_summary.tsv" 2>&1 | tail -20

echo "[JOB] == Pot A seed sweep census"
$PY "$WORK/census307.py" pota --pota "$OUT/pota" --released "$CORP/Axes" \
    --out "$OUT/census_pota_seeds.tsv" | tee logs/census_pota_seeds.txt

echo "[JOB] == consistency: paper_s0 vs the MM set's Pot A, and Juglet vs 307d"
nd=0
for f in "$OUT"/pota/paper_s0/Pot_A_Piece_*.xyz; do
  cmp -s "$f" "$OUT/axes_paper/$(basename "$f")" || { echo "[JOB]   DIFF $f"; nd=$((nd+1)); }
done
echo "[JOB]   paper_s0 vs axes_paper Pot A: $nd differing (expect 0)"
$PY "$WORK/census308.py" md5 --ours "$OUT/jug/axes_paper" --ref "$REFJUG" \
    --out "$OUT/census_jug_vs_307d.tsv" --label "308 Juglet axes vs 307d axes307"

# ---- D1 corpus guard after
md5_corp logs/corpus_after.md5
diff logs/corpus_before.md5 logs/corpus_after.md5 > logs/corpus.diff || true
if [ -s logs/corpus.diff ]; then echo "[JOB] WARN corpus changed"; cat logs/corpus.diff; \
  else echo "[JOB] corpus unchanged ($(wc -l < logs/corpus_after.md5) files)"; fi

echo "[JOB] == outputs"
for d in axes_paper axes_prune axes_305repro/axes305 jug/axes_paper pota; do
  echo "[JOB]   $d: $(ls "$OUT/$d"/*.xyz 2>/dev/null | wc -l) xyz"
done
echo "[JOB] complete at $(date -u +%FT%TZ)"
