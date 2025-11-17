#!/bin/bash
# Generate Complete NURBS Preprocessing Dataset with All Fixes
# Date: November 16, 2025

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "=========================================="
echo "  NURBS PREPROCESSING - COMPLETE DATASET"
echo "=========================================="
echo ""
echo "Start time: $(date)"
echo ""

# Load modules
module load Apptainer/1.3.3

# Create output directories
mkdir -p Dataset/Surfaces/Pot_A
mkdir -p Dataset/Breaklines/Pot_A
mkdir -p Dataset/Axes
mkdir -p Complete_Dataset_Output/Logs

# Run preprocessing pipeline
echo "=== Running EdgeLineExtractionHeadless ==="
echo "Processing all 8 Pot_A pieces..."
echo ""

START_TIME=$(date +%s)

apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | tee Complete_Dataset_Output/Logs/preprocessing_$(date +%Y%m%d_%H%M%S).log

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "End time: $(date)"
echo "Total processing time: ${ELAPSED} seconds"
echo ""

# Count generated files
echo "=========================================="
echo "          OUTPUT FILE SUMMARY"
echo "=========================================="
echo ""

echo "## Surface Files (Dataset/Surfaces/Pot_A/)"
echo "  Interior surfaces (*_Surface_0.xyz): $(ls -1 Dataset/Surfaces/Pot_A/*_Surface_0.xyz 2>/dev/null | wc -l)"
echo "  Exterior surfaces (*_Surface_1.xyz): $(ls -1 Dataset/Surfaces/Pot_A/*_Surface_1.xyz 2>/dev/null | wc -l)"
echo "  Fracture surfaces (*_Surface_F.pcd): $(ls -1 Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null | wc -l)"
echo ""

echo "## Breakline Files (Dataset/Breaklines/Pot_A/)"
echo "  Interior breaklines (*_Breakline_0.pcd): $(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_0.pcd 2>/dev/null | wc -l)"
echo "  Exterior breaklines (*_Breakline_1.pcd): $(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_1.pcd 2>/dev/null | wc -l)"
echo "  XYZ files: $(ls -1 Dataset/Breaklines/Pot_A/*.xyz 2>/dev/null | wc -l)"
echo "  PLY files: $(ls -1 Dataset/Breaklines/Pot_A/*.ply 2>/dev/null | wc -l)"
echo ""

echo "## Input Files"
echo "  Mesh files: $(ls -1 Dataset/Mesh/Pot_A/*.obj 2>/dev/null | wc -l)"
echo "  Surface files: $(ls -1 Dataset/Surfaces/Pot_A/*.xyz 2>/dev/null | wc -l)"
echo ""

# Validate expected outputs
EXPECTED_SURFACE_0=8
EXPECTED_SURFACE_1=8
EXPECTED_BREAKLINE_0=8
EXPECTED_BREAKLINE_1=8
EXPECTED_FRACTURE=8  # May be less due to low density

ACTUAL_SURFACE_0=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_0.xyz 2>/dev/null | wc -l)
ACTUAL_SURFACE_1=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_1.xyz 2>/dev/null | wc -l)
ACTUAL_BREAKLINE_0=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_0.pcd 2>/dev/null | wc -l)
ACTUAL_BREAKLINE_1=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_1.pcd 2>/dev/null | wc -l)
ACTUAL_FRACTURE=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null | wc -l)

echo "=========================================="
echo "          VALIDATION RESULTS"
echo "=========================================="
echo ""

if [ "$ACTUAL_SURFACE_0" -eq "$EXPECTED_SURFACE_0" ]; then
    echo "✅ Interior surfaces: $ACTUAL_SURFACE_0/$EXPECTED_SURFACE_0"
else
    echo "❌ Interior surfaces: $ACTUAL_SURFACE_0/$EXPECTED_SURFACE_0 (MISMATCH)"
fi

if [ "$ACTUAL_SURFACE_1" -eq "$EXPECTED_SURFACE_1" ]; then
    echo "✅ Exterior surfaces: $ACTUAL_SURFACE_1/$EXPECTED_SURFACE_1"
else
    echo "❌ Exterior surfaces: $ACTUAL_SURFACE_1/$EXPECTED_SURFACE_1 (MISMATCH)"
fi

if [ "$ACTUAL_BREAKLINE_0" -eq "$EXPECTED_BREAKLINE_0" ]; then
    echo "✅ Interior breaklines: $ACTUAL_BREAKLINE_0/$EXPECTED_BREAKLINE_0"
else
    echo "❌ Interior breaklines: $ACTUAL_BREAKLINE_0/$EXPECTED_BREAKLINE_0 (MISMATCH)"
fi

if [ "$ACTUAL_BREAKLINE_1" -eq "$EXPECTED_BREAKLINE_1" ]; then
    echo "✅ Exterior breaklines: $ACTUAL_BREAKLINE_1/$EXPECTED_BREAKLINE_1"
else
    echo "❌ Exterior breaklines: $ACTUAL_BREAKLINE_1/$EXPECTED_BREAKLINE_1 (MISMATCH)"
fi

if [ "$ACTUAL_FRACTURE" -ge 6 ]; then
    echo "✅ Fracture surfaces: $ACTUAL_FRACTURE/$EXPECTED_FRACTURE (≥75% is acceptable)"
else
    echo "⚠️  Fracture surfaces: $ACTUAL_FRACTURE/$EXPECTED_FRACTURE (low density pieces may be skipped)"
fi

echo ""
echo "=========================================="
echo ""

# List generated fracture surface files
if [ "$ACTUAL_FRACTURE" -gt 0 ]; then
    echo "Generated Fracture Surface Files:"
    ls -lh Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null
    echo ""
fi

# Check for any errors in log
ERROR_COUNT=$(grep -i "error occurred" Complete_Dataset_Output/Logs/preprocessing_*.log | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $ERROR_COUNT error(s) detected in log"
    echo "Check log file for details: Complete_Dataset_Output/Logs/preprocessing_*.log"
else
    echo "✅ No errors detected in processing"
fi

echo ""
echo "Dataset generation complete!"
echo "Output location: Dataset/"
echo "Log file: Complete_Dataset_Output/Logs/"
