#!/bin/bash

# SFS Preprocessing Job Submission Script
# Usage: ./submit_preprocessing_jobs.sh [POT_ID] [NUM_PIECES]
# Example: ./submit_preprocessing_jobs.sh A 8
# Example: ./submit_preprocessing_jobs.sh B 12

set -e

# Default parameters
POT_ID="${1:-A}"
NUM_PIECES="${2:-8}"

# Validate inputs
if [[ ! "$POT_ID" =~ ^[A-J]$ ]]; then
    echo "❌ Error: POT_ID must be A-J, got: $POT_ID"
    exit 1
fi

if [[ ! "$NUM_PIECES" =~ ^[0-9]+$ ]] || [ "$NUM_PIECES" -lt 1 ] || [ "$NUM_PIECES" -gt 20 ]; then
    echo "❌ Error: NUM_PIECES must be 1-20, got: $NUM_PIECES"
    exit 1
fi

# Check if SLURM script exists
SLURM_SCRIPT="slurm_complete_preprocessing.sbatch"
if [ ! -f "$SLURM_SCRIPT" ]; then
    echo "❌ Error: SLURM script not found: $SLURM_SCRIPT"
    exit 1
fi

# Create a temporary SLURM script for this pot
TEMP_SLURM="slurm_preprocessing_pot_${POT_ID}.sbatch"
cp "$SLURM_SCRIPT" "$TEMP_SLURM"

# Update POT_ID in the temporary script
sed -i "s/POT_ID=\"A\"/POT_ID=\"${POT_ID}\"/" "$TEMP_SLURM"
sed -i "s/#SBATCH --array=1-8/#SBATCH --array=1-${NUM_PIECES}/" "$TEMP_SLURM"
sed -i "s/#SBATCH --job-name=sfs_preprocessing/#SBATCH --job-name=sfs_prep_pot_${POT_ID}/" "$TEMP_SLURM"

echo "🚀 Submitting SFS preprocessing jobs for Pot $POT_ID"
echo "📊 Processing pieces: 1-$NUM_PIECES"
echo "📋 SLURM script: $TEMP_SLURM"
echo ""

# Check if input files exist
MESH_DIR="Dataset/Mesh/Pot_${POT_ID}"
if [ ! -d "$MESH_DIR" ]; then
    echo "❌ Error: Mesh directory not found: $MESH_DIR"
    exit 1
fi

missing_files=0
for i in $(seq 1 $NUM_PIECES); do
    piece_id=$(printf "%02d" $i)
    mesh_file="${MESH_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Mesh.obj"
    if [ ! -f "$mesh_file" ]; then
        echo "⚠️  Warning: Mesh file not found: $mesh_file"
        ((missing_files++))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo "❌ Error: $missing_files mesh files missing for Pot $POT_ID"
    echo "Please ensure all mesh files exist before submitting jobs"
    exit 1
fi

# Submit the job array
JOB_ID=$(sbatch "$TEMP_SLURM" | awk '{print $4}')

if [ $? -eq 0 ]; then
    echo "✅ Jobs submitted successfully"
    echo "🆔 Job Array ID: $JOB_ID"
    echo "📋 Monitor with: squeue -u $USER | grep sfs_prep"
    echo "📋 Cancel with: scancel $JOB_ID"
    echo ""
    echo "📁 Expected outputs:"
    echo "   - Surfaces: sfs_preprocessing/Surfaces/Pot_${POT_ID}_Piece_*_Surface_*.xyz"
    echo "   - Axes: sfs_main/sfs_test_reconstruction/Dataset/SfS_pp/Axes/Pot_${POT_ID}_Piece_*_Axis.xyz" 
    echo "   - Breaklines: sfs_main/sfs_test_reconstruction/Dataset/SfS_pp/Breaklines/Pot_${POT_ID}/"
    echo ""
    echo "🔄 Processing time estimate: ~2-5 minutes per piece"
    echo "📧 Email notifications: Check SLURM configuration"
else
    echo "❌ Error: Job submission failed"
    exit 1
fi

# Clean up temporary script
rm "$TEMP_SLURM"

echo ""
echo "🎯 Next steps after jobs complete:"
echo "1. Verify all outputs generated: ls sfs_main/sfs_test_reconstruction/Dataset/SfS_pp/Axes/Pot_${POT_ID}*"
echo "2. Run SFS assembly test: cd sfs_main && ./run_sfs_test.sh"
echo "3. Check results: ls sfs_main/results/"