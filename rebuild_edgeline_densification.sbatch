#!/bin/bash
#SBATCH --job-name=rebuild_edge
#SBATCH --time=00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire
#SBATCH --account=punim2657

echo "=== Rebuilding EdgeLineExtractionHeadless with Densification Fixes ===="
echo "Started: $(date)"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

echo "Rebuilding EdgeLineExtractionHeadless..."
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && make EdgeLineExtractionHeadless"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ EdgeLineExtractionHeadless rebuild successful!"
    ls -lh original_nurbs_preprocessing/build/EdgeLineExtractionHeadless
    echo ""
    echo "=== Combination Approach Implemented ==="
    echo "✅ PART 1: Relaxed outlier removal (min_neighbors: 3 for <100 points, 6 for ≥100)"
    echo "✅ PART 2: Adaptive sphere-marching retry (60% smaller radius if <15 points)"
    echo "✅ PART 3: Linear interpolation safety net (densify to 10+ points if needed)"
else
    echo "❌ EdgeLineExtractionHeadless rebuild failed!"
    exit 1
fi

echo ""
echo "Completed: $(date)"
