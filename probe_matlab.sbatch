#!/bin/bash
#SBATCH --job-name=juglet_matprobe
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=0:20:00
#SBATCH --output=juglet_matprobe_%j.out
#SBATCH --error=juglet_matprobe_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing
echo "which matlab: $(which matlab 2>&1)"
module load MATLAB/2024b_Update_3 2>&1
echo "module exit: $?"
echo "which matlab after: $(which matlab 2>&1)"
matlab -batch "disp('HELLO-MATLAB'); quit;" 2>&1 | head -n 20
echo "matlab exit: ${PIPESTATUS[0]}"
ls extract_single_axis.m
echo "surface sample: $(ls Juglet_Dataset_20260916/SfS_pp/Surfaces/Juglet_Piece_1_Surface_0.xyz)"
echo "Done: $(date)"
