#!/bin/bash
#SBATCH --job-name=t322-tests
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=logs/tests-%j.out
#SBATCH --error=logs/tests-%j.err
# Ticket 322: tests/test_normalized.py on the reverted working tree (committed potsac.py + dormant profile.py).
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes
cd "$R/impl_revert" || exit 1
md5sum sfs_axes/potsac.py sfs_axes/profile.py tests/test_normalized.py
OMP_NUM_THREADS=2 /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 tests/test_normalized.py
echo "rc=$?"
