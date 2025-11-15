#!/bin/bash
#SBATCH --job-name=nurbs_pipeline_fixed
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_pipeline_fixed_%j.out
#SBATCH --error=nurbs_pipeline_fixed_%j.err

echo "=== NURBS Pipeline with Fixed Curvature Computation ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Step 1: Run MeshPreprocessing to generate PLY files 
echo "=== Step 1: MeshPreprocessing A 8 ==="
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace/build \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./MeshPreprocessingHeadless A 8

echo
echo "=== Step 1 Completed - Checking generated PLY files ==="
find ../Temp -name "*.ply" | head -5
echo

# Step 2: Run EdgeLineExtraction with fixed NURBS curvature computation
echo "=== Step 2: EdgeLineExtraction A 8 with Fixed NURBS Curvature ==="
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace/build \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./EdgeLineExtractionHeadless A 8

echo
echo "=== Pipeline Completed at: $(date) ==="

# Verify proper curvature values in generated files
echo "=== Verifying Fixed Curvature Values ==="
BREAKLINE_FILE=$(find /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing -name "*Breakline_0.pcd" -newer /data/gpfs/projects/punim2657/sfs_preprocessing/run_nurbs_pipeline_fixed.sbatch | head -1)

if [ ! -z "$BREAKLINE_FILE" ]; then
    echo "Sample curvature values from: $BREAKLINE_FILE"
    echo "First 3 breakline points:"
    grep -E "^[0-9\.\-e]" "$BREAKLINE_FILE" | head -3 | awk '{
        printf "  Point: %.3f %.3f %.3f | Normal: %.3f %.3f %.3f | Curvature: %.6f\n", 
        $1, $2, $3, $4, $5, $6, $7
    }'
    
    echo "Last 3 breakline points:"
    grep -E "^[0-9\.\-e]" "$BREAKLINE_FILE" | tail -3 | awk '{
        printf "  Point: %.3f %.3f %.3f | Normal: %.3f %.3f %.3f | Curvature: %.6f\n", 
        $1, $2, $3, $4, $5, $6, $7
    }'
    
    # Check curvature statistics
    echo "Curvature value statistics:"
    grep -E "^[0-9\.\-e]" "$BREAKLINE_FILE" | awk '{print $7}' | sort -n | awk '
    BEGIN { count=0; sum=0; min=1e10; max=-1e10 }
    { 
        count++; sum+=$1
        if($1 < min) min=$1
        if($1 > max) max=$1
        values[count] = $1
    }
    END {
        avg = sum/count
        printf "  Min: %.6f, Max: %.6f, Average: %.6f, Count: %d\n", min, max, avg, count
        if(max < 1e20) {
            printf "  ✓ Curvature values appear reasonable (no massive 2e+26 corruption)\n"
        } else {
            printf "  ✗ Still has corrupted curvature values > 1e20\n"
        }
    }'
else
    echo "No new breakline files found - check errors above"
fi

echo "=== NURBS Pipeline with Fixed Curvature Computation Complete ==="