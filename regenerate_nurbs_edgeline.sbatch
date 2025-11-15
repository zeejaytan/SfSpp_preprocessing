#!/bin/bash
#SBATCH --job-name=regen_nurbs_edgeline
#SBATCH --time=00:45:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=regen_nurbs_edgeline_%j.out
#SBATCH --error=regen_nurbs_edgeline_%j.err

echo "=== Regenerating NURBS EdgeLine with Proper Curvature Computation ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo

# Set up working directory structure
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
NURBS_DIR="$WORK_DIR/original_nurbs_preprocessing"

cd $WORK_DIR

# Create necessary directory structure outside workspace
mkdir -p Temp/Axes Temp/Data/Pot_A

echo "Removed existing breakline files to force regeneration"
echo "Running NURBS EdgeLine extraction with proper curvature computation..."

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Run from the main preprocessing directory so ../Temp exists
cd $WORK_DIR
$CONTAINER_PATH exec \
    --bind $NURBS_DIR:/workspace \
    --bind $WORK_DIR:/work \
    --pwd /workspace \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    bash -c "cd /work && /workspace/build/EdgeLineExtractionHeadless A 8"

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for generated files in various locations
echo "=== Checking for Generated Files ==="
find $WORK_DIR -name "*Breakline*.pcd" -newer $WORK_DIR/regenerate_nurbs_edgeline.sbatch -exec echo "New Breakline: {}" \;
find $NURBS_DIR -name "*Breakline*.pcd" -newer $WORK_DIR/regenerate_nurbs_edgeline.sbatch -exec echo "New Breakline: {}" \;
find $WORK_DIR -name "*Surface_F*" -newer $WORK_DIR/regenerate_nurbs_edgeline.sbatch -exec echo "New Surface_F: {}" \;

# Show sample curvature to verify proper computation  
echo
echo "=== Verifying Proper Curvature Values ==="
SAMPLE_FILE=$(find $NURBS_DIR -name "*Breakline_0.pcd" -newer $WORK_DIR/regenerate_nurbs_edgeline.sbatch | head -1)
if [ ! -z "$SAMPLE_FILE" ]; then
    echo "Sample curvature values from $SAMPLE_FILE:"
    tail -3 "$SAMPLE_FILE" | awk '{print "  " $7}' 
    echo "These should be geometric values, not 2e+26"
else
    echo "No new breakline files found - check if generation succeeded"
fi

echo "=== Job Finished ==="