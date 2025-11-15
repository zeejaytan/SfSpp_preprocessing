#!/bin/bash
#SBATCH --job-name=test_coord_fix
#SBATCH --time=00:15:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=test_coord_fix_%j.out
#SBATCH --error=test_coord_fix_%j.err

echo "========================================================================="
echo "   COORDINATE SCALING FIX TEST - Single Piece Verification"
echo "========================================================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo ""

echo "=== FIX APPLIED ==="
echo "Fixed 4 locations in mesh_processing_headless.cpp:"
echo "  Line 399: writeMatrix_to_XYZ(..., false)"
echo "  Line 1511: writeMatrix_to_XYZ(..., false)"
echo "  Line 2025: convertPLYtoXYZ(..., false)"
echo "  Line 2032: convertPLYtoXYZ(..., false)"
echo ""

# Test configuration
POT_NAME="Pot_A"
TEST_PIECE="01"
WORKSPACE="/data/gpfs/projects/punim2657/sfs_preprocessing"
CONTAINER="${WORKSPACE}/pcl_191_nurbs.sif"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Output directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${WORKSPACE}/TEST_CoordinateFix_${TIMESTAMP}"

echo "=== TEST CONFIGURATION ==="
echo "Test piece: Pot_A_Piece_${TEST_PIECE}"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Create output directories
mkdir -p "${OUTPUT_DIR}/SfS_pp/Surfaces"
mkdir -p "${OUTPUT_DIR}/Temp/Temp/${POT_NAME}"
mkdir -p "${OUTPUT_DIR}/Temp/Data/${POT_NAME}"

# Copy single piece input data
echo "=== COPYING TEST DATA ==="
cp "${WORKSPACE}/Dataset/Mesh/${POT_NAME}/Pot_A_Piece_${TEST_PIECE}_Mesh.obj" "${OUTPUT_DIR}/Temp/Temp/${POT_NAME}/"
cp "${WORKSPACE}/Dataset/Point/${POT_NAME}/Pot_A_Piece_${TEST_PIECE}_Point.pcd" "${OUTPUT_DIR}/Temp/Temp/${POT_NAME}/"
echo "Input files copied"
echo ""

# Set environment variables
export POT_NAME="Pot_A"
export NURBS_OUTPUT_BASE="${OUTPUT_DIR}"

echo "=== RUNNING MESH PREPROCESSING (WITH FIX) ==="
echo "Executable: original_nurbs_preprocessing/build/MeshPreprocessingHeadless"
echo ""

cd "${WORKSPACE}"

time ${APPTAINER} exec \
    --bind ${WORKSPACE}:/workspace \
    ${CONTAINER} \
    bash -c "cd /workspace && \
             export POT_NAME='${POT_NAME}' && \
             export NURBS_OUTPUT_BASE='${OUTPUT_DIR}' && \
             ./original_nurbs_preprocessing/build/MeshPreprocessingHeadless"

echo ""
echo "=== VERIFICATION ==="

# Check if output files exist
SURFACE_0="${OUTPUT_DIR}/SfS_pp/Surfaces/Pot_A_Piece_${TEST_PIECE}_Surface_0.xyz"
SURFACE_1="${OUTPUT_DIR}/SfS_pp/Surfaces/Pot_A_Piece_${TEST_PIECE}_Surface_1.xyz"

if [ -f "${SURFACE_0}" ]; then
    echo "✓ Surface_0 file created"

    # Read first coordinate line
    FIRST_LINE=$(head -15 "${SURFACE_0}" | grep -v "^#" | grep -v "^segment" | head -1)
    echo ""
    echo "First data point from Surface_0.xyz:"
    echo "${FIRST_LINE}"
    echo ""

    # Extract first coordinate (x value)
    X_COORD=$(echo "${FIRST_LINE}" | awk '{print $1}')

    # Check coordinate scale
    echo "=== COORDINATE SCALE CHECK ==="
    echo "X coordinate: ${X_COORD}"

    # Convert to absolute value for comparison (remove minus sign if present)
    X_ABS=$(echo "${X_COORD}" | awk '{print ($1 < 0) ? -$1 : $1}')

    # Check if coordinate is in expected millimeter range (< 1000mm)
    if (( $(echo "${X_ABS} < 1000" | bc -l) )); then
        echo "✅ COORDINATE SCALE: CORRECT (millimeters)"
        echo "   Coordinate ${X_COORD} is in expected range (-500 to 500mm)"
        echo ""
        echo "🎉 FIX SUCCESSFUL! Coordinates are now in millimeters, not kilometers!"
    elif (( $(echo "${X_ABS} > 1000000" | bc -l) )); then
        echo "❌ COORDINATE SCALE: WRONG (still multiplied by 1000)"
        echo "   Coordinate ${X_ABS} is > 1,000,000 (coordinates in kilometers)"
        echo ""
        echo "⚠️  FIX FAILED - Bug still present"
    else
        echo "⚠️  COORDINATE SCALE: UNCLEAR"
        echo "   Coordinate ${X_ABS} is between 1000-1000000"
        echo "   Expected: < 1000 (millimeters)"
    fi

    # Compare with working reference dataset
    REF_SURFACE="/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20250905_ProperSegmentation/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
    if [ -f "${REF_SURFACE}" ]; then
        echo ""
        echo "=== COMPARISON WITH WORKING REFERENCE ==="
        REF_FIRST=$(head -15 "${REF_SURFACE}" | grep -v "^#" | grep -v "^segment" | head -1)
        echo "Reference (working dataset):"
        echo "${REF_FIRST}"
        echo ""
        echo "Current output (with fix):"
        echo "${FIRST_LINE}"
    fi

else
    echo "❌ Surface_0 file NOT created"
    echo "   Expected: ${SURFACE_0}"
    echo ""
    echo "⚠️  Processing may have failed"
fi

if [ -f "${SURFACE_1}" ]; then
    echo ""
    echo "✓ Surface_1 file created"
else
    echo "❌ Surface_1 file NOT created"
fi

echo ""
echo "=== TEST SUMMARY ==="
echo "Output directory: ${OUTPUT_DIR}"
echo "Test completed: $(date)"
echo ""

ls -lh "${OUTPUT_DIR}/SfS_pp/Surfaces/"

echo ""
echo "========================================================================="
echo "END OF COORDINATE FIX TEST"
echo "========================================================================="
