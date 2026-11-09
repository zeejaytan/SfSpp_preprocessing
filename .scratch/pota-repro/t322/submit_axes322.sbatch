#!/bin/bash
#SBATCH --job-name=t322-axes322
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=03:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes/logs/axes322_%j.out
# Ticket 322: write axes322 with the working-tree sfs_axes (profile ranking), through the
# unchanged 318/320 writer (run_benchmark_172.py, copied beside the code), so the files have
# the exact layout the assembly harness stages. Its printed Juglet score uses the broken
# Dataset/Axes/Juglet reference and is ignored; scoring is t322/dump_basins.py --before.
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
export OMP_NUM_THREADS=1
cd "$R/impl"
md5sum sfs_axes/*.py > "$R/out/axes322_code.md5"
"$PY" run_benchmark_172.py --out "$R/out/axes322" --jobs 24 --cap 6 --seeds 10 --step 10
ls "$R/out/axes322" | wc -l
