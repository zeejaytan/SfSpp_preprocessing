#!/bin/bash
#SBATCH --job-name=juglet_axes
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=1:00:00
#SBATCH --output=juglet_axes_%j.out
#SBATCH --error=juglet_axes_%j.err

# Standalone Juglet axis run (Step 3 only; surfaces/breaklines already done).
cd /data/gpfs/projects/punim2657/sfs_preprocessing
module load MATLAB/2024b_Update_3
matlab -batch "run_juglet_axes"
MEX=$?
echo "matlab exit: ${MEX}"
[ "${MEX}" -ne 0 ] && { echo "ERROR: axis extraction failed"; exit 1; }
echo "Axes: $(ls Juglet_Dataset_20260916/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l) (expected 9)"
echo "Done: $(date)"
