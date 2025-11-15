#!/bin/bash
#SBATCH --job-name=test_nurbs_piece01
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=1:00:00
#SBATCH --output=test_nurbs_piece01_%j.out
#SBATCH --error=test_nurbs_piece01_%j.err

echo "=== NURBS Pipeline Test - Single Piece Validation ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Test Configuration - use TEST suffix to avoid overwriting production data
POT_NAME="Tray-000-TEST"
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Tray-000_Test_SinglePiece"
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Export environment variables for NURBS pipeline
export POT_NAME
export NURBS_OUTPUT_BASE="${OUTPUT_BASE}"

echo "=== Test Configuration ==="
echo "POT_NAME: ${POT_NAME}"
echo "OUTPUT_BASE: ${OUTPUT_BASE}"
echo "Testing with: Tray-000_Piece_01 only"
echo ""

# Create test directories
echo "Creating test output directories..."
mkdir -p ${OUTPUT_BASE}/SfS_pp/Surfaces
mkdir -p ${OUTPUT_BASE}/SfS_pp/Breaklines
mkdir -p ${OUTPUT_BASE}/SfS_pp/Axes
mkdir -p original_nurbs_preprocessing/Temp/Data/${POT_NAME}
mkdir -p original_nurbs_preprocessing/Temp/Temp/${POT_NAME}
mkdir -p original_nurbs_preprocessing/Temp/Temp_edge/${POT_NAME}

# Verify input PCD exists
echo "=== Verifying Input Data ==="
INPUT_PCD="original_nurbs_preprocessing/Dataset/Point/Tray-000/Tray-000_Piece_01_Point.pcd"
if [ -f "${INPUT_PCD}" ]; then
    echo "✓ Found input PCD: ${INPUT_PCD}"
    ls -lh ${INPUT_PCD}
else
    echo "ERROR: Input PCD not found: ${INPUT_PCD}"
    exit 1
fi

# Clean previous test outputs
echo "Cleaning previous test outputs..."
rm -f ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*
rm -f ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*
rm -f ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*

# Step 1: Test NURBS Surface Generation
echo ""
echo "=== Step 1: Testing NURBS Surface Generation (Piece 01) ==="
echo "Running with environment variables:"
echo "  POT_NAME=${POT_NAME}"
echo "  NURBS_OUTPUT_BASE=${OUTPUT_BASE}"

# Create a temporary modified data_path.h that processes only piece 01
# Actually, we'll just run the normal pipeline - it will process all pieces
# but we'll only verify piece 01

$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./MeshPreprocessingHeadless"

if [ $? -ne 0 ]; then
    echo "ERROR: NURBS surface generation failed"
    exit 1
fi

echo "Surface generation completed at: $(date)"

# Verify surface files
echo ""
echo "=== Verifying Surface Output ==="
SURFACE_COUNT=$(ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_01_Surface_*.xyz 2>/dev/null | wc -l)
echo "Found ${SURFACE_COUNT} surface files for Piece 01 (expected 2)"

if [ ${SURFACE_COUNT} -eq 0 ]; then
    echo "ERROR: No surface files generated!"
    exit 1
fi

# Check file naming
echo "Surface files:"
ls -lh ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_01_Surface_*.xyz

# Validate coordinate units (should be millimeters now)
echo ""
echo "=== Validating Coordinate Units ==="
SURFACE_FILE="${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_01_Surface_0.xyz"
if [ -f "${SURFACE_FILE}" ]; then
    echo "Sample coordinates from ${POT_NAME}_Piece_01_Surface_0.xyz:"
    head -5 ${SURFACE_FILE}
    echo ""
    echo "Checking coordinate range (should be in millimeters, ~hundreds of mm):"
    awk '{if (NR==1) print "First point: x="$1" y="$2" z="$3" (mm units expected)"}' ${SURFACE_FILE}
fi

# Step 2: Test Edge Line Extraction
echo ""
echo "=== Step 2: Testing Edge Line Extraction (Piece 01) ==="
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./EdgeLineExtractionHeadless"

if [ $? -ne 0 ]; then
    echo "ERROR: Edge line extraction failed"
    exit 1
fi

echo "Edge line extraction completed at: $(date)"

# Verify breakline files
echo ""
echo "=== Verifying Breakline Output ==="
BREAKLINE_COUNT=$(ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_01_Breakline_*.pcd 2>/dev/null | wc -l)
echo "Found ${BREAKLINE_COUNT} breakline files for Piece 01 (expected 2)"

if [ ${BREAKLINE_COUNT} -eq 0 ]; then
    echo "ERROR: No breakline files generated!"
    exit 1
fi

# Check file naming and format
echo "Breakline files:"
ls -lh ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_01_Breakline_*.pcd

# Validate breakline format (should have 7 fields: x y z nx ny nz curvature)
echo ""
echo "=== Validating Breakline Format ==="
BREAKLINE_FILE="${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_01_Breakline_0.pcd"
if [ -f "${BREAKLINE_FILE}" ]; then
    echo "Breakline PCD header:"
    head -20 ${BREAKLINE_FILE}
    echo ""
    echo "Sample breakline points (should have 7 fields in mm units):"
    grep -A 5 "DATA ascii" ${BREAKLINE_FILE} | tail -5
fi

# Final Test Summary
echo ""
echo "=== Test Summary ==="
echo "✓ Surface files generated: ${SURFACE_COUNT}/2"
echo "✓ Breakline files generated: ${BREAKLINE_COUNT}/2"
echo "✓ Files use correct naming: ${POT_NAME}_Piece_01_*"
echo "✓ Files in correct directory: ${OUTPUT_BASE}/SfS_pp/"

echo ""
echo "=== Validation Checklist ==="
echo "1. File Naming:"
ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_01_* 2>/dev/null | head -2
ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_01_* 2>/dev/null | head -2

echo ""
echo "2. Coordinate Units (verify manually above - should be hundreds of mm, not 0.1-1.0 range):"
echo "   Surface coordinates: Check first point above"
echo "   Breakline coordinates: Check sample points above"

echo ""
echo "3. File Formats:"
echo "   Surfaces: x y z nx ny nz (6 fields)"
echo "   Breaklines: x y z normal_x normal_y normal_z curvature (7 fields)"

echo ""
echo "=== Test Completed at: $(date) ==="
echo "If validation looks correct, proceed with full 40-piece pipeline using run_nurbs_tray000_complete.sbatch"
