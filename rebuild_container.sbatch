#!/bin/bash
#SBATCH --job-name=rebuild_pcl_container
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition=cascade
#SBATCH --output=rebuild_container_%j.out
#SBATCH --error=rebuild_container_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Rebuilding PCL 1.9.1 NURBS container..."
echo "Started: $(date)"

# Load Apptainer module
module load Apptainer/1.3.3

# Build container
apptainer build pcl_191_nurbs.sif pcl_191_nurbs.def

if [ -f "pcl_191_nurbs.sif" ]; then
    echo "✓ Container built successfully!"
    ls -lh pcl_191_nurbs.sif
else
    echo "✗ Container build failed!"
    exit 1
fi

echo "Completed: $(date)"
