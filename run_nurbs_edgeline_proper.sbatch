#!/bin/bash
#SBATCH --job-name=nurbs_edgeline_proper
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_edgeline_proper_%j.out
#SBATCH --error=nurbs_edgeline_proper_%j.err

echo "=== NURBS EdgeLine Extraction with Proper Curvature Computation ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Surface files ready: $(ls -1 /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/Temp/Data/Pot_A/*.xyz | wc -l)"
echo "OBJ files ready: $(ls -1 /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/Temp/*.obj | wc -l)"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

echo "Running NURBS EdgeLine extraction with proper curvature computation..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace/build \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./EdgeLineExtractionHeadless A 8

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for newly generated files
echo "=== Generated NURBS Breakline Files ==="
find /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing -name "*Breakline*.pcd" -newer /data/gpfs/projects/punim2657/sfs_preprocessing/run_nurbs_edgeline_proper.sbatch -exec echo "Generated: {}" \;

# Show sample curvature values to verify proper computation
echo
echo "=== Verifying Proper Curvature Values ==="
NEW_FILE=$(find /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing -name "*Breakline_0.pcd" -newer /data/gpfs/projects/punim2657/sfs_preprocessing/run_nurbs_edgeline_proper.sbatch | head -1)
if [ ! -z "$NEW_FILE" ]; then
    echo "Sample curvature values from $NEW_FILE:"
    tail -3 "$NEW_FILE" | awk '{print "  Point: " $1 " " $2 " " $3 " | Curvature: " $7}'
    echo "These should be geometric values computed from NURBS derivatives"
else
    echo "No new breakline files generated - check for errors above"
fi

echo "=== Job Finished ==="