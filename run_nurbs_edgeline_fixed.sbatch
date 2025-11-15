#!/bin/bash
#SBATCH --job-name=nurbs_edgeline_fixed
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_edgeline_fixed_%j.out
#SBATCH --error=nurbs_edgeline_fixed_%j.err

echo "=== NURBS EdgeLine Extraction with Curvature Fix ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Using newly built EdgeLineExtractionHeadless with curvature fix"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Create necessary directories
mkdir -p Temp/Axes
mkdir -p Temp/Data/Pot_A
mkdir -p Breaklines

echo "Running EdgeLine extraction with PCL NURBS container..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./build/EdgeLineExtractionHeadless A 8

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for generated files
echo "=== Generated NURBS Breakline Files with Curvature Fix ==="
find . -name "*Breakline*.pcd" -exec echo "NURBS Breakline: {}" \;
find . -name "*Surface_F*" -exec echo "NURBS Surface_F: {}" \;

# Show sample curvature values to verify fix
echo
echo "=== Verifying Curvature Fix (should show ~1.9e-42, not 2e+26) ==="
if [ -f "Pot_A_Piece_01_Breakline_0.pcd" ]; then
    echo "Sample curvature values from Pot_A_Piece_01_Breakline_0.pcd:"
    tail -5 Pot_A_Piece_01_Breakline_0.pcd | awk '{print "  " $7}'
fi

echo "=== Job Finished ==="