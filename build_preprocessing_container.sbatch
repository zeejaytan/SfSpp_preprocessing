#!/bin/bash
#SBATCH --job-name=build_sfs_prep
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=build_sfs_prep_%j.out
#SBATCH --error=build_sfs_prep_%j.err

echo "=== Building SfS Preprocessing Container ==="
echo "Job started at: $(date)"

# Load required modules
module load Apptainer/1.3.3

# Set working directory
cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Building preprocessing container with:"
echo "- PCL (Point Cloud Library) 1.9.1"
echo "- CGAL 5.0"
echo "- VTK 8.1.2"
echo "- Ubuntu 20.04 base"

# Build the container
echo "Starting container build..."
apptainer build sfs_preprocessing.sif sfs_preprocessing.def

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ Container build successful!"
    echo "Container info:"
    ls -lh sfs_preprocessing.sif
    
    echo "Testing container:"
    apptainer exec sfs_preprocessing.sif /bin/bash -c "echo 'Container test successful'"
    
else
    echo "❌ Container build failed with exit code: $BUILD_EXIT_CODE"
fi

echo ""
echo "=== Build completed at: $(date) ==="