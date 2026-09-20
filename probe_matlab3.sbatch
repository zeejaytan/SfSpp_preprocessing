#!/bin/bash
#SBATCH --job-name=juglet_matprobe3
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=0:20:00
#SBATCH --output=juglet_matprobe3_%j.out
#SBATCH --error=juglet_matprobe3_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing
module load MATLAB/2024b_Update_3
echo "--- two-line batch (literal newline inside quotes):"
matlab -batch "disp('LINE-ONE');
disp('LINE-TWO'); quit;"
echo "exit: $?"
