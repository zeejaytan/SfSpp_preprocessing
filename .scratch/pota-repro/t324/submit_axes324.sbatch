#!/bin/bash
#SBATCH --job-name=t324-axes324
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1202_e94d8fb_t324-axes/logs/axes324_%j.out
# Ticket 324: the shipped path (select.select_union_lines through run_potsac_union) over the
# 172 pieces axes322 used, via the same writer (run_benchmark_172.py copied beside the code),
# same python, same arguments. Pass 1: line rule on (default) -> axes324, cmp vs axes323.
# Pass 2: --no-line-rule -> axes324_off, cmp vs axes322 (ladder step 3, every pot).
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1202_e94d8fb_t324-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
A322=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes/out/axes322
A323=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
export OMP_NUM_THREADS=1
corpus_state() { ls -l --time-style=full-iso "$CORPUS/Surfaces" "$CORPUS/Axes" "$JUG"; }
corpus_state > "$R/out/corpus_before.txt"
cd "$R/impl"
md5sum sfs_axes/*.py run_benchmark_172.py > "$R/out/axes324_code.md5"
"$PY" -c "import numpy, scipy; print('numpy', numpy.__version__, 'scipy', scipy.__version__)"

"$PY" run_benchmark_172.py --out "$R/out/axes324" --jobs 24 --cap 6 --seeds 10 --step 10
"$PY" run_benchmark_172.py --out "$R/out/axes324_off" --jobs 24 --cap 6 --seeds 10 --step 10 --no-line-rule

compare() {  # compare <ours> <reference> <label>: every ours file except the Pot_JUGLET copies
  local ours=$1 ref=$2 label=$3 same=0 diff=0 miss=0
  for f in "$ours"/*_Axis.xyz; do
    b=$(basename "$f")
    case "$b" in Pot_JUGLET_*) continue ;; esac
    if [ ! -f "$ref/$b" ]; then miss=$((miss+1)); echo "$label MISSING-IN-REF $b"
    elif cmp -s "$f" "$ref/$b"; then same=$((same+1))
    else diff=$((diff+1)); echo "$label DIFFERS $b lines $(wc -l < "$f") vs $(wc -l < "$ref/$b")"; fi
  done
  echo "$label IDENTICAL $same DIFFER $diff MISSING $miss"
}
compare "$R/out/axes324" "$A323" "rule-on-vs-axes323" | tee "$R/out/cmp_axes323.txt"
compare "$R/out/axes324_off" "$A322" "rule-off-vs-axes322" | tee "$R/out/cmp_axes322.txt"
echo "lines axes324 $(cat "$R"/out/axes324/Pot_[A-J]_*_Axis.xyz "$R"/out/axes324/Juglet_*_Axis.xyz | wc -l)"

corpus_state > "$R/out/corpus_after.txt"
if cmp -s "$R/out/corpus_before.txt" "$R/out/corpus_after.txt"; then echo CORPUS-UNCHANGED; else echo CORPUS-CHANGED; fi
