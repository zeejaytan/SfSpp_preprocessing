#!/bin/bash
#SBATCH --job-name=pot_a_adaptive
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

# Rerun Pot A preprocessing with adaptive sensitivity to match sample dataset
# This uses divisor=4.0 for dense breaklines (>80 points)

echo "=== Pot A Preprocessing with Adaptive Sensitivity ==="
echo "Started: $(date)"
echo ""

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load modules
module load GCCcore/11.3.0
module load Apptainer/1.3.3
module load MATLAB/2023a

# Clean previous output
echo "Cleaning previous Dataset/ output..."
rm -rf Dataset/
mkdir -p Dataset/Surfaces/Pot_A
mkdir -p Dataset/Breaklines/Pot_A
mkdir -p Dataset/Axes

echo ""
echo "=== Step 1: Mesh Processing ==="
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/MeshPreprocessingHeadless

echo ""
echo "=== Step 2: Edgeline Extraction (Adaptive Sensitivity) ==="
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless

echo ""
echo "=== Step 3: Axis Extraction ==="
# Copy surfaces to expected location for MATLAB
mkdir -p Dataset/SfS_pp/Surfaces
cp Dataset/Surfaces/Pot_A/*.xyz Dataset/SfS_pp/Surfaces/

matlab -batch "extract_all_nurbs_axes"

echo ""
echo "=== Preprocessing Complete ==="
echo "Ended: $(date)"
echo ""

# Summary
echo "=== Output Summary ==="
echo "Surfaces: $(find Dataset/Surfaces/Pot_A -name "*.xyz" 2>/dev/null | wc -l) files"
echo "Breaklines (PCD): $(find Dataset/Breaklines/Pot_A -name "*.pcd" 2>/dev/null | wc -l) files"
echo "Axes: $(find Dataset/Axes -name "*.xyz" 2>/dev/null | wc -l) files"
echo ""
echo "Check for adaptive sensitivity in output:"
grep "ADAPTIVE PEAK DETECTION" slurm-${SLURM_JOB_ID}.out | head -5
