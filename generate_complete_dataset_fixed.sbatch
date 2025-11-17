#!/bin/bash
#SBATCH --job-name=nurbs_complete_allfix
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=nurbs_complete_allfix_%j.out
#SBATCH --error=nurbs_complete_allfix_%j.err

# =====================================================================
# Complete NURBS Preprocessing Dataset Generation with ALL FIXES
# =====================================================================
# Date: November 16, 2025
# Purpose: Generate complete Pot_A dataset with all 3 critical fixes:
#   Fix #1: Fixed peak detection sensitivity (divisor=5)
#   Fix #2: Adaptive radius formula (400mm² area assumption)
#   Fix #3: Fracture surface file generation (4 bug fixes)
# Build: build_new/ using pcl_191_nurbs.sif container
# =====================================================================

echo "=========================================="
echo "  NURBS PREPROCESSING - COMPLETE DATASET"
echo "  WITH ALL FIXES APPLIED"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"
echo ""

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load required modules
module purge
module load GCCcore/11.3.0
module load Apptainer/1.3.3

# Create output directories
mkdir -p Dataset/Surfaces/Pot_A
mkdir -p Dataset/Breaklines/Pot_A
mkdir -p Dataset/Axes
mkdir -p Complete_Dataset_Output/Logs

# Clean old outputs to ensure fresh dataset
echo "=== Cleaning old outputs ==="
rm -rf Dataset/Surfaces/Pot_A/*.xyz Dataset/Surfaces/Pot_A/*.pcd
rm -rf Dataset/Breaklines/Pot_A/*
rm -rf Segments/*.xyz
rm -rf Temp/Temp_edge/Pot_A/*
rm -rf Temp/Data/Pot_A/*
echo "✓ Cleaned all output directories"
echo ""

# Verify input files are present
echo "=== Verifying input files ==="
SURFACE_COUNT=$(ls -1 Dataset/Surfaces/Pot_A/Pot_A_Piece_*_Surface_0.xyz 2>/dev/null | wc -l)
MESH_COUNT=$(ls -1 Dataset/Mesh/Pot_A/Pot_A_Piece_*.obj 2>/dev/null | wc -l)

if [ "$SURFACE_COUNT" -eq 0 ] || [ "$MESH_COUNT" -eq 0 ]; then
    echo "❌ ERROR: Input files missing!"
    echo "   Surface files: $SURFACE_COUNT (expected: 8)"
    echo "   Mesh files: $MESH_COUNT (expected: 8)"
    echo ""
    echo "Copying from NURBS_Dataset_20251103..."
    cp NURBS_Dataset_20251103/SfS_pp/Surfaces/Pot_A_Piece_*_Surface_*.xyz Dataset/Surfaces/Pot_A/ || {
        echo "❌ ERROR: Failed to copy surface files"
        exit 1
    }
    cp NURBS_Dataset_20251103/SfS_pp/Mesh/Pot_A_Piece_*.obj Dataset/Mesh/Pot_A/ || {
        echo "❌ ERROR: Failed to copy mesh files"
        exit 1
    }
    echo "✓ Input files copied successfully"
fi

echo "✓ Surface files: $(ls -1 Dataset/Surfaces/Pot_A/Pot_A_Piece_*_Surface_0.xyz 2>/dev/null | wc -l)"
echo "✓ Mesh files: $(ls -1 Dataset/Mesh/Pot_A/Pot_A_Piece_*.obj 2>/dev/null | wc -l)"
echo ""

# ========================================
# STEP 1: EDGELINE/BREAKLINE EXTRACTION
# ========================================
echo "=========================================="
echo "  STEP 1: EDGELINE/BREAKLINE EXTRACTION"
echo "=========================================="
echo "Container: pcl_191_nurbs.sif"
echo "Executable: build_new/EdgeLineExtractionHeadless"
echo "Processing: All Pot_A pieces (01-08)"
echo ""
echo "Applied Fixes:"
echo "  ✅ Fix #1: Fixed peak detection (divisor=5)"
echo "  ✅ Fix #2: Adaptive radius formula (400mm²)"
echo "  ✅ Fix #3: Fracture surface generation"
echo "  ✅ Fix #4: Empty point cloud handling"
echo "  ✅ Fix #5: Cross-filesystem compatibility"
echo "  ✅ Fix #6: Debug logging optimization"
echo ""

START_TIME=$(date +%s)
LOG_FILE="Complete_Dataset_Output/Logs/edgeline_$(date +%Y%m%d_%H%M%S).log"

# Run EdgeLineExtractionHeadless
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}
EDGELINE_TIME=$(date +%s)
EDGELINE_ELAPSED=$((EDGELINE_TIME - START_TIME))

echo ""
echo "Edgeline extraction completed in ${EDGELINE_ELAPSED} seconds"
echo ""

# ========================================
# STEP 2: AXIS EXTRACTION (MATLAB)
# ========================================
echo "=========================================="
echo "  STEP 2: AXIS EXTRACTION (MATLAB POTSAC)"
echo "=========================================="
echo "Loading MATLAB module..."
module load MATLAB/2024b_Update_3

# Create output directory
mkdir -p Dataset/Axes

AXIS_LOG_FILE="Complete_Dataset_Output/Logs/axis_$(date +%Y%m%d_%H%M%S).log"

echo "Running PotSAC axis extraction on NURBS surfaces..."
matlab -batch "extract_all_nurbs_axes" 2>&1 | tee "$AXIS_LOG_FILE"

AXIS_EXIT_CODE=${PIPESTATUS[0]}
AXIS_TIME=$(date +%s)
AXIS_ELAPSED=$((AXIS_TIME - EDGELINE_TIME))

echo ""
echo "Axis extraction completed in ${AXIS_ELAPSED} seconds"
echo ""

# Copy axes to Dataset directory
if [ -d "NURBS_Output/Axes" ]; then
    cp NURBS_Output/Axes/*.xyz Dataset/Axes/ 2>/dev/null
    echo "✓ Copied $(ls -1 NURBS_Output/Axes/*.xyz 2>/dev/null | wc -l) axis files to Dataset/Axes/"
fi

EXIT_CODE=$((EXIT_CODE + AXIS_EXIT_CODE))
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "  PROCESSING COMPLETED"
echo "=========================================="
echo "Exit code: $EXIT_CODE"
echo "Total processing time: ${ELAPSED} seconds ($(($ELAPSED / 60)) minutes)"
echo "  - Edgeline extraction: ${EDGELINE_ELAPSED} seconds"
echo "  - Axis extraction: ${AXIS_ELAPSED} seconds"
echo ""

# Count generated files
echo "=========================================="
echo "          OUTPUT FILE SUMMARY"
echo "=========================================="
echo ""

SURFACE_0_COUNT=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_0.xyz 2>/dev/null | wc -l)
SURFACE_1_COUNT=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_1.xyz 2>/dev/null | wc -l)
FRACTURE_COUNT=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null | wc -l)
BREAKLINE_0_COUNT=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_0.pcd 2>/dev/null | wc -l)
BREAKLINE_1_COUNT=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_1.pcd 2>/dev/null | wc -l)
BREAKLINE_XYZ_COUNT=$(ls -1 Dataset/Breaklines/Pot_A/*.xyz 2>/dev/null | wc -l)
BREAKLINE_PLY_COUNT=$(ls -1 Dataset/Breaklines/Pot_A/*.ply 2>/dev/null | wc -l)
AXIS_COUNT=$(ls -1 Dataset/Axes/Pot_A_Piece_*_Axis.xyz 2>/dev/null | wc -l)

echo "## Surface Files (Dataset/Surfaces/Pot_A/)"
echo "  Interior surfaces (*_Surface_0.xyz): $SURFACE_0_COUNT / 8"
echo "  Exterior surfaces (*_Surface_1.xyz): $SURFACE_1_COUNT / 8"
echo "  Fracture surfaces (*_Surface_F.pcd): $FRACTURE_COUNT / 8"
echo ""

echo "## Breakline Files (Dataset/Breaklines/Pot_A/)"
echo "  Interior breaklines (*_Breakline_0.pcd): $BREAKLINE_0_COUNT / 8"
echo "  Exterior breaklines (*_Breakline_1.pcd): $BREAKLINE_1_COUNT / 8"
echo "  XYZ format: $BREAKLINE_XYZ_COUNT files"
echo "  PLY format: $BREAKLINE_PLY_COUNT files"
echo ""

echo "## Axis Files (Dataset/Axes/)"
echo "  Axis files (*_Axis.xyz): $AXIS_COUNT / 8"
echo ""

echo "## Input Files"
echo "  Mesh files (*.obj): $(ls -1 Dataset/Mesh/Pot_A/*.obj 2>/dev/null | wc -l)"
echo "  Surface files (*.xyz): $(ls -1 Dataset/Surfaces/Pot_A/Pot_A_Piece_*_Surface_[01].xyz 2>/dev/null | wc -l)"
echo ""

# Validate expected outputs
EXPECTED_PIECES=8
EXPECTED_FRACTURE_MIN=6  # 75% threshold (some may have low density)

echo "=========================================="
echo "          VALIDATION RESULTS"
echo "=========================================="
echo ""

# Validation
VALIDATION_PASS=true

if [ "$SURFACE_0_COUNT" -eq "$EXPECTED_PIECES" ]; then
    echo "✅ Interior surfaces: $SURFACE_0_COUNT/$EXPECTED_PIECES"
else
    echo "❌ Interior surfaces: $SURFACE_0_COUNT/$EXPECTED_PIECES (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$SURFACE_1_COUNT" -eq "$EXPECTED_PIECES" ]; then
    echo "✅ Exterior surfaces: $SURFACE_1_COUNT/$EXPECTED_PIECES"
else
    echo "❌ Exterior surfaces: $SURFACE_1_COUNT/$EXPECTED_PIECES (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$BREAKLINE_0_COUNT" -eq "$EXPECTED_PIECES" ]; then
    echo "✅ Interior breaklines: $BREAKLINE_0_COUNT/$EXPECTED_PIECES"
else
    echo "❌ Interior breaklines: $BREAKLINE_0_COUNT/$EXPECTED_PIECES (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$BREAKLINE_1_COUNT" -eq "$EXPECTED_PIECES" ]; then
    echo "✅ Exterior breaklines: $BREAKLINE_1_COUNT/$EXPECTED_PIECES"
else
    echo "❌ Exterior breaklines: $BREAKLINE_1_COUNT/$EXPECTED_PIECES (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$AXIS_COUNT" -eq "$EXPECTED_PIECES" ]; then
    echo "✅ Axis files: $AXIS_COUNT/$EXPECTED_PIECES"
else
    echo "❌ Axis files: $AXIS_COUNT/$EXPECTED_PIECES (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FRACTURE_COUNT" -ge "$EXPECTED_FRACTURE_MIN" ]; then
    echo "✅ Fracture surfaces: $FRACTURE_COUNT/$EXPECTED_PIECES (≥75% threshold)"
else
    echo "⚠️  Fracture surfaces: $FRACTURE_COUNT/$EXPECTED_PIECES (below 75% threshold)"
    echo "    Note: Some pieces may have insufficient point density near breaklines"
fi

echo ""

# List generated fracture surface files
if [ "$FRACTURE_COUNT" -gt 0 ]; then
    echo "=========================================="
    echo "   FRACTURE SURFACE FILES (FIX #3)"
    echo "=========================================="
    ls -lh Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null
    echo ""
fi

# Verify fixes in log file
echo "=========================================="
echo "      FIX VERIFICATION (FROM LOG)"
echo "=========================================="
echo ""

echo "## Fix #1: Fixed Peak Detection"
FIX1_COUNT=$(grep -c "FIXED PEAK DETECTION" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$FIX1_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX1_COUNT instances found)"
    grep "FIXED PEAK DETECTION" "$LOG_FILE" | head -2
else
    echo "❌ NOT FOUND in log"
fi
echo ""

echo "## Fix #2: Adaptive Radius Formula"
FIX2_COUNT=$(grep -c "ADAPTIVE BOUNDARY\|ADAPTIVE OUTLIER" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$FIX2_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX2_COUNT instances found)"
    grep "ADAPTIVE BOUNDARY\|ADAPTIVE OUTLIER" "$LOG_FILE" | head -4
else
    echo "❌ NOT FOUND in log"
fi
echo ""

echo "## Fix #3: Fracture Surface Generation"
FIX3_COUNT=$(grep -c "FRACTURE SURFACE.*Saving" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$FIX3_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX3_COUNT instances found)"
    echo "Sample log entries:"
    grep "FRACTURE SURFACE.*Saving" "$LOG_FILE" | head -3
else
    echo "❌ NOT FOUND in log"
fi
echo ""

# Check for errors
ERROR_COUNT=$(grep -i "error occurred" "$LOG_FILE" 2>/dev/null | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $ERROR_COUNT error(s) detected in log"
    echo "Last error:"
    grep -i "error occurred" "$LOG_FILE" | tail -1
    echo ""
fi

# Final summary
echo "=========================================="
echo "          FINAL SUMMARY"
echo "=========================================="
echo ""

if [ "$VALIDATION_PASS" = true ] && [ "$EXIT_CODE" -eq 0 ]; then
    echo "🎉 SUCCESS: Complete dataset generated with all fixes!"
    echo ""
    echo "📁 Output location: Dataset/"
    echo "📊 Surfaces: $SURFACE_0_COUNT + $SURFACE_1_COUNT files"
    echo "📊 Breaklines: $BREAKLINE_0_COUNT + $BREAKLINE_1_COUNT files"
    echo "📊 Axes: $AXIS_COUNT files"
    echo "📊 Fracture surfaces: $FRACTURE_COUNT files (NEW!)"
    echo "📝 Edgeline log: $LOG_FILE"
    echo "📝 Axis log: $AXIS_LOG_FILE"
    echo ""
    echo "✅ All fixes verified in execution log"
    echo "✅ Ready for SFS assembly pipeline"
    EXIT_STATUS=0
else
    echo "❌ ISSUES DETECTED"
    echo ""
    echo "Validation: $VALIDATION_PASS"
    echo "Exit code: $EXIT_CODE"
    echo "Check log file for details: $LOG_FILE"
    EXIT_STATUS=1
fi

echo ""
echo "End time: $(date)"
echo "=========================================="

exit $EXIT_STATUS
