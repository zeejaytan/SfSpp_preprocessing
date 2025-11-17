#!/bin/bash
# Verification test for all 3 fixes on existing dataset

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "=== TESTING NURBS PREPROCESSING FIXES ==="
echo "Date: $(date)"
echo ""

# Load container
module load Apptainer/1.3.3

# Create test output directory
TEST_DIR="Test_Verification_$(date +%Y%m%d_%H%M%S)"
mkdir -p $TEST_DIR

# Copy one surface file for focused testing
mkdir -p Dataset/Surfaces/Pot_A
cp NURBS_Dataset_20251103/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz Dataset/Surfaces/Pot_A/
cp NURBS_Dataset_20251103/SfS_pp/Mesh/Pot_A_Piece_01_Mesh.obj Dataset/Mesh/Pot_A/ 2>/dev/null || mkdir -p Dataset/Mesh/Pot_A && cp NURBS_Dataset_20251103/SfS_pp/Mesh/Pot_A_Piece_01_Mesh.obj Dataset/Mesh/Pot_A/

echo "Running EdgeLineExtractionHeadless with all fixes..."
echo ""

# Run with container
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | tee $TEST_DIR/execution.log

echo ""
echo "=== VERIFICATION CHECKLIST ==="
echo ""

# Check Fix #1: Fixed Peak Detection
echo "Fix #1: Fixed Peak Detection (sensitivity=5.0)"
grep "FIXED PEAK DETECTION" $TEST_DIR/execution.log && echo "  ✓ Fixed peak detection confirmed" || echo "  ✗ Fixed peak detection NOT found"
echo ""

# Check Fix #2: Adaptive Radius
echo "Fix #2: Adaptive Radius Formula"
grep "ADAPTIVE BOUNDARY" $TEST_DIR/execution.log | head -3
grep "ADAPTIVE OUTLIER" $TEST_DIR/execution.log | head -3
echo ""

# Check Fix #3: Fracture Surface Files
echo "Fix #3: Fracture Surface File Generation"
FRACTURE_FILES=$(find Dataset/Surfaces/Pot_A -name "*_Surface_F.pcd" 2>/dev/null)
if [ -n "$FRACTURE_FILES" ]; then
  echo "  ✓ Fracture surface files generated:"
  ls -lh Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null
else
  echo "  ✗ No fracture surface files found"
fi
echo ""

# Save results
echo "Test completed. Logs saved to: $TEST_DIR/"
