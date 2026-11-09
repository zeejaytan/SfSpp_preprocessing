#!/bin/bash
#SBATCH --job-name=t322-hyb
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=logs/hyb-%j.out
#SBATCH --error=logs/hyb-%j.err
# Ticket 322 checkpoint 11: build the hybrid axis set and score axes320 / axes322 / hybrid side by side.
set -uo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
A320=/data/gpfs/projects/punim2657/SfSpp/runs/20261108-1350_e556fc8_t318a-axes/out/axes320
cd "$R/work" || exit 1
$PY build_hybrid.py "$R/out/axes322" "$A320" "$R/out/axes_hyb" || exit 2
D=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0446_d628fc0_t322-potG-diag/work/axes_mx
n=0; for f in "$D"/Pot_G_Piece_*_Axis.xyz; do cmp -s "$f" <(head -n 3 "$R/out/axes_hyb/$(basename "$f")") && n=$((n+1)); done
echo "G hybrid top-3 byte-identical to diag MX arm: $n of 7"
$PY score_set.py "$R/out/jugkey" axes320="$A320" axes322="$R/out/axes322" hybrid="$R/out/axes_hyb" > "$R/out/score_320_322_hyb.txt" 2>&1
echo "score rc=$?"
