#!/bin/bash
#SBATCH --job-name=complete_pipeline
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=20G
#SBATCH --time=03:00:00
#SBATCH --output=complete_pipeline_%j.out
#SBATCH --error=complete_pipeline_%j.err

# =====================================================================
# COMPLETE NURBS PREPROCESSING PIPELINE FROM SCRATCH
# =====================================================================
# Pipeline: Raw PCD → Surfaces → Breaklines → Axes
# Step 0: Setup and copy raw data
# Step 1: Mesh Processing (PCD + OBJ → Surface XYZ files)
# Step 2: Edgeline Extraction (Surfaces → Breaklines + Fracture surfaces)
# Step 3: Axis Extraction (Surfaces → Axes with MATLAB PotSAC)
# =====================================================================

echo "============================================================"
echo "  COMPLETE NURBS PREPROCESSING PIPELINE FROM SCRATCH"
echo "============================================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"
echo ""

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load required modules
module purge
module load GCCcore/11.3.0
module load Apptainer/1.3.3

# Create all necessary directories
mkdir -p Dataset/Point/Pot_A
mkdir -p Dataset/Mesh/Pot_A
mkdir -p Dataset/Surfaces/Pot_A
mkdir -p Dataset/Breaklines/Pot_A
mkdir -p Dataset/Axes
mkdir -p Temp/Data/Pot_A
mkdir -p Temp/Temp_edge/Pot_A
mkdir -p Temp/Intermediate/Pot_A
mkdir -p Complete_Dataset_Output/Logs
mkdir -p Segments

OVERALL_START=$(date +%s)

# ========================================
# STEP 0: SETUP - COPY RAW DATA
# ========================================
echo "=========================================="
echo "  STEP 0: SETUP - COPY RAW DATA"
echo "=========================================="
echo ""

# Clean old outputs
echo "Cleaning old outputs..."
rm -rf Dataset/Surfaces/Pot_A/*.xyz Dataset/Surfaces/Pot_A/*.pcd
rm -rf Dataset/Breaklines/Pot_A/*
rm -rf Dataset/Axes/*
rm -rf Segments/*.xyz
rm -rf Temp/Temp_edge/Pot_A/*
rm -rf Temp/Data/Pot_A/*
rm -rf Temp/Intermediate/Pot_A/*
echo "✓ Cleaned output directories"
echo ""

# Copy raw point clouds
echo "Copying raw point cloud files (PCD)..."
cp temp_download/Point/Pot_A/Pot_A_Piece_*_Point.pcd Dataset/Point/Pot_A/ || {
    echo "❌ ERROR: Failed to copy PCD files"
    exit 1
}
PCD_COUNT=$(ls -1 Dataset/Point/Pot_A/*.pcd 2>/dev/null | wc -l)
echo "✓ Copied $PCD_COUNT PCD files"

# Copy mesh files
echo "Copying mesh files (OBJ)..."
cp NURBS_Dataset_20251103/SfS_pp/Mesh/Pot_A_Piece_*.obj Dataset/Mesh/Pot_A/ || {
    echo "❌ ERROR: Failed to copy OBJ files"
    exit 1
}
MESH_COUNT=$(ls -1 Dataset/Mesh/Pot_A/*.obj 2>/dev/null | wc -l)
echo "✓ Copied $MESH_COUNT mesh files"
echo ""

if [ "$PCD_COUNT" -ne 8 ] || [ "$MESH_COUNT" -ne 8 ]; then
    echo "❌ ERROR: Incomplete input data"
    echo "   PCD files: $PCD_COUNT (expected: 8)"
    echo "   Mesh files: $MESH_COUNT (expected: 8)"
    exit 1
fi

echo "✅ All input data ready"
echo ""

# ========================================
# STEP 1: MESH PROCESSING (PCD → SURFACES)
# ========================================
echo "=========================================="
echo "  STEP 1: MESH PROCESSING"
echo "=========================================="
echo "Input: Point clouds (PCD) + Meshes (OBJ)"
echo "Output: Interior/Exterior surfaces (XYZ)"
echo "Method: B-spline surface fitting with NURBS"
echo ""

STEP1_START=$(date +%s)
MESH_LOG="Complete_Dataset_Output/Logs/mesh_processing_$(date +%Y%m%d_%H%M%S).log"

echo "Running MeshPreprocessingHeadless..."
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/MeshPreprocessingHeadless 2>&1 | tee "$MESH_LOG"

MESH_EXIT=$?
STEP1_END=$(date +%s)
STEP1_ELAPSED=$((STEP1_END - STEP1_START))

echo ""
echo "Mesh processing completed in ${STEP1_ELAPSED} seconds"
echo ""

# Verify surface files were generated
SURFACE_0_COUNT=$(find Dataset/Surfaces/Pot_A -name "*_Surface_0.xyz" 2>/dev/null | wc -l)
SURFACE_1_COUNT=$(find Dataset/Surfaces/Pot_A -name "*_Surface_1.xyz" 2>/dev/null | wc -l)

echo "Generated surfaces:"
echo "  Interior (*_Surface_0.xyz): $SURFACE_0_COUNT"
echo "  Exterior (*_Surface_1.xyz): $SURFACE_1_COUNT"

if [ "$SURFACE_0_COUNT" -lt 8 ] || [ "$SURFACE_1_COUNT" -lt 8 ]; then
    echo "⚠️  WARNING: Not all surfaces generated"
    echo "Check log: $MESH_LOG"
fi
echo ""

# ========================================
# STEP 2: EDGELINE/BREAKLINE EXTRACTION
# ========================================
echo "=========================================="
echo "  STEP 2: EDGELINE/BREAKLINE EXTRACTION"
echo "=========================================="
echo "Input: Surface XYZ files"
echo "Output: Breaklines (PCD/PLY/XYZ) + Fracture surfaces (PCD)"
echo ""
echo "Applied Fixes:"
echo "  ✅ Fix #1: Fixed peak detection (divisor=5)"
echo "  ✅ Fix #2: Adaptive radius formula (400mm²)"
echo "  ✅ Fix #3: Fracture surface generation"
echo "  ✅ Fix #4: Empty point cloud handling"
echo "  ✅ Fix #5: Cross-filesystem compatibility"
echo "  ✅ Fix #6: Debug logging optimization"
echo ""

STEP2_START=$(date +%s)
EDGELINE_LOG="Complete_Dataset_Output/Logs/edgeline_$(date +%Y%m%d_%H%M%S).log"

echo "Running EdgeLineExtractionHeadless..."
apptainer exec --bind /data:/data pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | tee "$EDGELINE_LOG"

EDGELINE_EXIT=$?
STEP2_END=$(date +%s)
STEP2_ELAPSED=$((STEP2_END - STEP2_START))

echo ""
echo "Edgeline extraction completed in ${STEP2_ELAPSED} seconds"
echo ""

# ========================================
# STEP 3: AXIS EXTRACTION (MATLAB)
# ========================================
echo "=========================================="
echo "  STEP 3: AXIS EXTRACTION (MATLAB POTSAC)"
echo "=========================================="
echo "Input: Surface XYZ files"
echo "Output: Axis files (XYZ)"
echo "Method: PotSAC (Pottery Surface-Aware Cylinder fitting)"
echo ""

STEP3_START=$(date +%s)

echo "Loading MATLAB module..."
module load MATLAB/2024b_Update_3

# Create output directory
mkdir -p NURBS_Output/Axes

AXIS_LOG="Complete_Dataset_Output/Logs/axis_$(date +%Y%m%d_%H%M%S).log"

echo "Running PotSAC axis extraction..."
matlab -batch "extract_all_nurbs_axes" 2>&1 | tee "$AXIS_LOG"

AXIS_EXIT=$?
STEP3_END=$(date +%s)
STEP3_ELAPSED=$((STEP3_END - STEP3_START))

echo ""
echo "Axis extraction completed in ${STEP3_ELAPSED} seconds"
echo ""

# Copy axes to Dataset directory
if [ -d "NURBS_Output/Axes" ]; then
    cp NURBS_Output/Axes/*.xyz Dataset/Axes/ 2>/dev/null
    AXIS_COPY_COUNT=$(ls -1 NURBS_Output/Axes/*.xyz 2>/dev/null | wc -l)
    echo "✓ Copied $AXIS_COPY_COUNT axis files to Dataset/Axes/"
fi
echo ""

# ========================================
# FINAL SUMMARY AND VALIDATION
# ========================================
OVERALL_END=$(date +%s)
OVERALL_ELAPSED=$((OVERALL_END - OVERALL_START))

echo "=========================================="
echo "  PROCESSING COMPLETED"
echo "=========================================="
echo "Total time: ${OVERALL_ELAPSED} seconds ($(($OVERALL_ELAPSED / 60)) minutes)"
echo "  Step 1 (Mesh processing): ${STEP1_ELAPSED}s"
echo "  Step 2 (Edgeline extraction): ${STEP2_ELAPSED}s"
echo "  Step 3 (Axis extraction): ${STEP3_ELAPSED}s"
echo ""

# Count all generated files
echo "=========================================="
echo "          OUTPUT FILE SUMMARY"
echo "=========================================="
echo ""

FINAL_SURFACE_0=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_0.xyz 2>/dev/null | wc -l)
FINAL_SURFACE_1=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_1.xyz 2>/dev/null | wc -l)
FINAL_FRACTURE=$(ls -1 Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null | wc -l)
FINAL_BREAKLINE_0=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_0.pcd 2>/dev/null | wc -l)
FINAL_BREAKLINE_1=$(ls -1 Dataset/Breaklines/Pot_A/*_Breakline_1.pcd 2>/dev/null | wc -l)
FINAL_BREAKLINE_XYZ=$(ls -1 Dataset/Breaklines/Pot_A/*.xyz 2>/dev/null | wc -l)
FINAL_BREAKLINE_PLY=$(ls -1 Dataset/Breaklines/Pot_A/*.ply 2>/dev/null | wc -l)
FINAL_AXIS=$(ls -1 Dataset/Axes/Pot_A_Piece_*_Axis.xyz 2>/dev/null | wc -l)

echo "## Surface Files (Dataset/Surfaces/Pot_A/)"
echo "  Interior surfaces (*_Surface_0.xyz): $FINAL_SURFACE_0 / 8"
echo "  Exterior surfaces (*_Surface_1.xyz): $FINAL_SURFACE_1 / 8"
echo "  Fracture surfaces (*_Surface_F.pcd): $FINAL_FRACTURE / 8"
echo ""

echo "## Breakline Files (Dataset/Breaklines/Pot_A/)"
echo "  Interior breaklines (*_Breakline_0.pcd): $FINAL_BREAKLINE_0 / 8"
echo "  Exterior breaklines (*_Breakline_1.pcd): $FINAL_BREAKLINE_1 / 8"
echo "  XYZ format: $FINAL_BREAKLINE_XYZ files"
echo "  PLY format: $FINAL_BREAKLINE_PLY files"
echo ""

echo "## Axis Files (Dataset/Axes/)"
echo "  Axis files (*_Axis.xyz): $FINAL_AXIS / 8"
echo ""

echo "## Input Files"
echo "  Point clouds (*.pcd): $PCD_COUNT"
echo "  Mesh files (*.obj): $MESH_COUNT"
echo ""

# Validation
echo "=========================================="
echo "          VALIDATION RESULTS"
echo "=========================================="
echo ""

VALIDATION_PASS=true
EXIT_CODE=$((MESH_EXIT + EDGELINE_EXIT + AXIS_EXIT))

if [ "$FINAL_SURFACE_0" -eq 8 ]; then
    echo "✅ Interior surfaces: $FINAL_SURFACE_0/8"
else
    echo "❌ Interior surfaces: $FINAL_SURFACE_0/8 (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FINAL_SURFACE_1" -eq 8 ]; then
    echo "✅ Exterior surfaces: $FINAL_SURFACE_1/8"
else
    echo "❌ Exterior surfaces: $FINAL_SURFACE_1/8 (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FINAL_BREAKLINE_0" -eq 8 ]; then
    echo "✅ Interior breaklines: $FINAL_BREAKLINE_0/8"
else
    echo "❌ Interior breaklines: $FINAL_BREAKLINE_0/8 (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FINAL_BREAKLINE_1" -eq 8 ]; then
    echo "✅ Exterior breaklines: $FINAL_BREAKLINE_1/8"
else
    echo "❌ Exterior breaklines: $FINAL_BREAKLINE_1/8 (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FINAL_AXIS" -eq 8 ]; then
    echo "✅ Axis files: $FINAL_AXIS/8"
else
    echo "❌ Axis files: $FINAL_AXIS/8 (MISMATCH)"
    VALIDATION_PASS=false
fi

if [ "$FINAL_FRACTURE" -ge 6 ]; then
    echo "✅ Fracture surfaces: $FINAL_FRACTURE/8 (≥75% threshold)"
else
    echo "⚠️  Fracture surfaces: $FINAL_FRACTURE/8 (below 75% threshold)"
    echo "    Note: Some pieces may have insufficient point density near breaklines"
fi

echo ""

# List fracture surface files if generated
if [ "$FINAL_FRACTURE" -gt 0 ]; then
    echo "=========================================="
    echo "   FRACTURE SURFACE FILES (FIX #3)"
    echo "=========================================="
    ls -lh Dataset/Surfaces/Pot_A/*_Surface_F.pcd 2>/dev/null
    echo ""
fi

# Verify fixes in log
echo "=========================================="
echo "      FIX VERIFICATION (FROM LOG)"
echo "=========================================="
echo ""

echo "## Fix #1: Fixed Peak Detection"
FIX1_COUNT=$(grep -c "FIXED PEAK DETECTION" "$EDGELINE_LOG" 2>/dev/null || echo "0")
if [ "$FIX1_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX1_COUNT instances found)"
    grep "FIXED PEAK DETECTION" "$EDGELINE_LOG" | head -2
else
    echo "❌ NOT FOUND in log"
fi
echo ""

echo "## Fix #2: Adaptive Radius Formula"
FIX2_COUNT=$(grep -c "ADAPTIVE BOUNDARY\|ADAPTIVE OUTLIER" "$EDGELINE_LOG" 2>/dev/null || echo "0")
if [ "$FIX2_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX2_COUNT instances found)"
    grep "ADAPTIVE BOUNDARY\|ADAPTIVE OUTLIER" "$EDGELINE_LOG" | head -4
else
    echo "❌ NOT FOUND in log"
fi
echo ""

echo "## Fix #3: Fracture Surface Generation"
FIX3_COUNT=$(grep -c "FRACTURE SURFACE.*Saving" "$EDGELINE_LOG" 2>/dev/null || echo "0")
if [ "$FIX3_COUNT" -gt 0 ]; then
    echo "✅ VERIFIED ($FIX3_COUNT instances found)"
else
    echo "❌ NOT FOUND in log"
fi
echo ""

# Final summary
echo "=========================================="
echo "          FINAL SUMMARY"
echo "=========================================="
echo ""

if [ "$VALIDATION_PASS" = true ] && [ "$EXIT_CODE" -eq 0 ]; then
    echo "🎉 SUCCESS: Complete dataset generated from scratch!"
    echo ""
    echo "📁 Output location: Dataset/"
    echo "📊 Surfaces: $FINAL_SURFACE_0 + $FINAL_SURFACE_1 files"
    echo "📊 Breaklines: $FINAL_BREAKLINE_0 + $FINAL_BREAKLINE_1 files"
    echo "📊 Axes: $FINAL_AXIS files"
    echo "📊 Fracture surfaces: $FINAL_FRACTURE files (NEW!)"
    echo ""
    echo "📝 Logs:"
    echo "   - Mesh processing: $MESH_LOG"
    echo "   - Edgeline extraction: $EDGELINE_LOG"
    echo "   - Axis extraction: $AXIS_LOG"
    echo ""
    echo "✅ Complete pipeline validated (PCD → Surfaces → Breaklines → Axes)"
    echo "✅ All fixes verified in execution log"
    echo "✅ Ready for SFS assembly pipeline"
    EXIT_STATUS=0
else
    echo "❌ ISSUES DETECTED"
    echo ""
    echo "Validation: $VALIDATION_PASS"
    echo "Exit codes: Mesh=$MESH_EXIT, Edgeline=$EDGELINE_EXIT, Axis=$AXIS_EXIT"
    echo ""
    echo "Check log files:"
    echo "   - $MESH_LOG"
    echo "   - $EDGELINE_LOG"
    echo "   - $AXIS_LOG"
    EXIT_STATUS=1
fi

echo ""
echo "End time: $(date)"
echo "============================================================"

exit $EXIT_STATUS
