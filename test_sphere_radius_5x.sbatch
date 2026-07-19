#!/bin/bash
#SBATCH --job-name=test_sphere_5x
#SBATCH --time=00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "==========================================="
echo "TEST: 5× Sphere Radius for Sample-Like Variation"
echo "==========================================="
echo "Started: $(date)"
echo ""

# Load modules
module load GCCcore/11.3.0
module load CMake
module load Apptainer

echo "========== Rebuilding EdgeLineExtractionHeadless =========="
cd build_new
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
  bash -c "cmake .. && make EdgeLineExtractionHeadless -j4" 2>&1 | tail -20

echo ""
echo "========== Running Breakline Extraction (Test Piece 01) =========="
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Clean previous breaklines
rm -f Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_*.pcd

# Run extraction
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | grep -E "Piece_01|SPHERE-MARCHING|Natural variation|multiplier" | head -30

echo ""
echo "========== Results =========="
echo "Breakline 0:"
grep "^POINTS " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd 2>/dev/null

echo "Breakline 1:"
grep "^POINTS " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd 2>/dev/null

echo ""
echo "========== Comparison =========="
echo "  Sample Piece 01:"
echo "    Breakline_0: 59 points"
echo "    Breakline_1: 150 points"
echo ""
echo "  Previous (1.5× radius + densification):"
echo "    Breakline_0: 360 points"
echo "    Breakline_1: 351 points"
echo ""
echo "  New (5.0× radius, no densification):"
echo "    Breakline_0: $(grep "^POINTS " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_0.pcd 2>/dev/null | awk '{print $2}') points"
echo "    Breakline_1: $(grep "^POINTS " Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_1.pcd 2>/dev/null | awk '{print $2}') points"
echo ""
echo "Expected: ~30-200 points range (sample-like variation)"
echo ""
echo "Completed: $(date)"
