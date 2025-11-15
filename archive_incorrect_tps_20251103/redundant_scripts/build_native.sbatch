#!/bin/bash
#SBATCH --job-name=native_sfs_prep
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=native_sfs_prep_%j.out
#SBATCH --error=native_sfs_prep_%j.err

echo "=== Building SfS Preprocessing Natively ==="
echo "Job started at: $(date)"

# Load required modules (try to use system libraries)
module load CMake/3.24.3-GCCcore-11.3.0
module load Eigen/3.4.0-GCCcore-11.3.0  
module load Boost/1.79.0-GCC-11.3.0

# Check for PCL - if available use it, otherwise note the need
echo "Checking for available point cloud libraries..."
find /apps -name "*pcl*" 2>/dev/null | head -5 || echo "PCL not found in modules"
find /apps -name "*cgal*" 2>/dev/null | head -5 || echo "CGAL not found in modules"
find /apps -name "*vtk*" 2>/dev/null | head -5 || echo "VTK not found in modules"

# Set working directory
cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Available system libraries check complete."
echo "Note: SfS preprocessing requires PCL, CGAL, and VTK which may need manual installation"
echo "Alternative: Use pre-built container from main SfS system or Docker approach"

echo ""
echo "=== Native build check completed at: $(date) ==="