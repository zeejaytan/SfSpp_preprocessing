#!/bin/bash
#SBATCH --job-name=t325-axes325
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes/logs/axes325_%j.out
# Ticket 325 acceptance 2: byte identity of the shipped writer (profile ranker, line rule on)
# over the 172 pieces, after the scale-free conversion of the archived normal-branch gates.
# The shipped path executes zero changed lines (profile return at potsac.py:482 precedes every
# edit); identity is by construction and this run is the proof. Juglet axes land in the same
# out dir (same writer); the compare covers all 172 files including Juglet_*.
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
A323=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
export OMP_NUM_THREADS=1
corpus_state() { ls -l --time-style=full-iso "$CORPUS/Surfaces" "$CORPUS/Axes" "$JUG"; }
corpus_state > "$R/out/corpus_before.txt"
cd "$R/impl"
md5sum sfs_axes/*.py run_benchmark_172.py > "$R/out/axes325_code.md5"
"$PY" -c "import numpy, scipy; print('numpy', numpy.__version__, 'scipy', scipy.__version__)"

"$PY" run_benchmark_172.py --out "$R/out/axes325" --jobs 24 --cap 6 --seeds 10 --step 10

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
compare "$R/out/axes325" "$A323" "axes325-vs-axes323" | tee "$R/out/cmp_axes323.txt"
echo "files ours $(ls "$R"/out/axes325/*_Axis.xyz | grep -v Pot_JUGLET | wc -l) ref $(ls "$A323"/*_Axis.xyz | wc -l)"

corpus_state > "$R/out/corpus_after.txt"
if cmp -s "$R/out/corpus_before.txt" "$R/out/corpus_after.txt"; then echo CORPUS-UNCHANGED; else echo CORPUS-CHANGED; fi
