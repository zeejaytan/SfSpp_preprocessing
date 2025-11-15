#!/bin/bash
#SBATCH --job-name=axis_extract
#SBATCH --array=1-8
#SBATCH --time=00:10:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/axis_extract_%A_%a.out
#SBATCH --error=logs/axis_extract_%A_%a.err

# Create logs directory if it doesn't exist
mkdir -p logs

# Load MATLAB module
module load MATLAB/2024b_Update_3

# Change to preprocessing directory
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Get piece number from SLURM array task ID
PIECE_NUM=$SLURM_ARRAY_TASK_ID

echo "=== SLURM Job $SLURM_JOB_ID Array Task $SLURM_ARRAY_TASK_ID ==="
echo "Processing Pot A Piece $PIECE_NUM"
echo "Start time: $(date)"
echo "Running on node: $HOSTNAME"
echo "Working directory: $(pwd)"

# Run MATLAB function with piece number as parameter
matlab -batch "extract_single_axis($PIECE_NUM)"

echo "End time: $(date)"
echo "=== SLURM Job Complete ==="