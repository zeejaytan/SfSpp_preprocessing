#!/bin/bash

# Submit parallel axis extraction jobs using SLURM
echo "=== SUBMITTING PARALLEL AXIS EXTRACTION JOBS ==="

# Create logs directory
mkdir -p logs

# Clean up any existing axis files to ensure fresh generation
echo "Cleaning up existing axis files..."
rm -f TPS_Output/Axes/Pot_A_Piece_*_Axis.xyz

# Submit SLURM job array for pieces 1-8
echo "Submitting SLURM job array for pieces 1-8..."
JOB_ID=$(sbatch --parsable slurm_axis_extraction.sh)

if [ $? -eq 0 ]; then
    echo "✅ Jobs submitted successfully with Job ID: $JOB_ID"
    echo "Jobs will run in parallel for pieces 1-8"
    echo ""
    echo "Monitor progress with:"
    echo "  squeue -u $USER"
    echo "  squeue -j $JOB_ID"
    echo ""
    echo "Check individual job logs in: logs/"
    echo "  logs/axis_extract_${JOB_ID}_*.out"
    echo "  logs/axis_extract_${JOB_ID}_*.err"
    echo ""
    echo "Wait for completion and check results with:"
    echo "  ./check_axis_results.sh"
else
    echo "❌ Failed to submit jobs"
    exit 1
fi