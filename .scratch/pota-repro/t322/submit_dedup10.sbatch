#!/bin/bash
#SBATCH --job-name=t322-dedup10
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=logs/dedup10-%j.out
#SBATCH --error=logs/dedup10-%j.err
# Ticket 322 checkpoint 8: the one declared variant -- profile ranker dedup 10 deg instead of 15.
set -uo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
export OMP_NUM_THREADS=1
cd "$R/work" || exit 1
$PY profile_rank.py --basins ../out/basins_all.json --jugkey ../out/jugkey \
    --out ../out/profile_rank_dedup10.json --jobs 24 --dedup 10
echo "rc=$?"
