#!/bin/bash
#SBATCH --job-name=rebuild_adaptive
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire
#SBATCH --account=punim2657

echo "=== Rebuilding NURBS Executables with Adaptive Parameters ===="
echo "Started: $(date)"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

echo "Rebuilding MeshPreprocessingHeadless with adaptive parameters..."
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && make MeshPreprocessingHeadless"

if [ $? -eq 0 ]; then
    echo "✅ MeshPreprocessingHeadless rebuild successful!"
    ls -lh original_nurbs_preprocessing/build/MeshPreprocessingHeadless
else
    echo "❌ MeshPreprocessingHeadless rebuild failed!"
    exit 1
fi

echo ""
echo "Rebuilding EdgeLineExtractionHeadless with adaptive parameters..."
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && make EdgeLineExtractionHeadless"

if [ $? -eq 0 ]; then
    echo "✅ EdgeLineExtractionHeadless rebuild successful!"
    ls -lh original_nurbs_preprocessing/build/EdgeLineExtractionHeadless
else
    echo "❌ EdgeLineExtractionHeadless rebuild failed!"
    exit 1
fi

echo ""
echo "=== Adaptive Parameters Summary ==="
echo "✅ CGAL normal estimation: K = 5-20 (density-aware)"
echo "✅ PCL curvature: K = 10-50 (density-aware)"
echo "✅ Boundary detection: radius = 1-15mm adaptive (meters-based)"
echo "✅ Point sequencing: K = 5-50 (10% of boundary)"
echo "✅ Outlier removal: radius = 2-20mm adaptive"
echo "✅ Euclidean clustering: min/max = adaptive (0.2-1% of points)"
echo "✅ PotSAC downsampling: step = 1-10 (density-aware)"

echo ""
echo "Completed: $(date)"
