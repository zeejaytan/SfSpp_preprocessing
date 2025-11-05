#!/bin/bash
#SBATCH --job-name=nurbs_coord_fix
#SBATCH --time=03:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_coord_fix_%j.out
#SBATCH --error=nurbs_coord_fix_%j.err

echo "========================================================================="
echo "   NURBS Dataset Regeneration - WITH COORDINATE SCALING FIX"
echo "========================================================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo ""

echo "=== CRITICAL BUG FIX APPLIED ==="
echo "Bug: convertToMM=true multiplied already-mm coordinates by 1000"
echo "Result: Coordinates became 52 million instead of 32mm"
echo "Fix: Added 'false' parameter to 4 locations in mesh_processing_headless.cpp:"
echo "  - Line 399: writeMatrix_to_XYZ(..., 3, false)"
echo "  - Line 1511: writeMatrix_to_XYZ(..., 6, false)"
echo "  - Line 2025: convertPLYtoXYZ(..., false)"
echo "  - Line 2032: convertPLYtoXYZ(..., false)"
echo ""

# Set paths
PREPROCESSING_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
ORIGINAL_NURBS_DIR="$PREPROCESSING_DIR/original_nurbs_preprocessing"
BUILD_DIR="$ORIGINAL_NURBS_DIR/build"
CONTAINER="$PREPROCESSING_DIR/pcl_191_nurbs.sif"
DATASET_NAME="NURBS_Dataset_$(date +%Y%m%d_%H%M%S)_CoordinateFix"
OUTPUT_DIR="$PREPROCESSING_DIR/$DATASET_NAME"

cd $PREPROCESSING_DIR

echo "=== Verification ==="
echo "Checking fixed executable exists..."
if [ ! -f "$BUILD_DIR/MeshPreprocessingHeadless" ]; then
    echo "ERROR: MeshPreprocessingHeadless not found!"
    echo "Expected: $BUILD_DIR/MeshPreprocessingHeadless"
    exit 1
fi

echo "✓ Executable found: $(ls -lh $BUILD_DIR/MeshPreprocessingHeadless | awk '{print $9, $5}')"
echo "  Built: $(stat -c %y $BUILD_DIR/MeshPreprocessingHeadless | cut -d'.' -f1)"
echo ""

echo "Checking input data exists..."
INPUT_COUNT=$(ls $PREPROCESSING_DIR/Dataset/Point/Pot_A/Pot_A_Piece_0[1-8]_Point.pcd 2>/dev/null | wc -l)
MESH_COUNT=$(ls $PREPROCESSING_DIR/Dataset/Mesh/Pot_A/Pot_A_Piece_0[1-8]_Mesh.obj 2>/dev/null | wc -l)

if [ "$INPUT_COUNT" -lt 8 ]; then
    echo "ERROR: Not enough PCD files! Found: $INPUT_COUNT, Expected: 8"
    exit 1
fi

if [ "$MESH_COUNT" -lt 8 ]; then
    echo "ERROR: Not enough OBJ files! Found: $MESH_COUNT, Expected: 8"
    exit 1
fi

echo "✓ Input PCD files: $INPUT_COUNT/8"
echo "✓ Input OBJ files: $MESH_COUNT/8"
echo ""

echo "=== Step 1: Clean Previous Outputs ==="
rm -rf $ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/*.xyz
rm -f $BUILD_DIR/Pot_A_Piece_*_Breakline_*.pcd
rm -f $BUILD_DIR/Pot_A_Piece_*_Surface_*.pcd
echo "✓ Cleaned previous temporary files"
echo ""

echo "=== Step 2: NURBS Surface Generation (WITH COORDINATE FIX) ==="
echo "Running: MeshPreprocessingHeadless"
echo "Start: $(date)"
echo ""

cd $ORIGINAL_NURBS_DIR
time /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    --bind "$PREPROCESSING_DIR:/workspace" \
    $CONTAINER \
    bash -c "cd /workspace/original_nurbs_preprocessing && ./build/MeshPreprocessingHeadless"

MESH_STATUS=$?
echo ""
echo "MeshPreprocessingHeadless exit code: $MESH_STATUS"
echo "End: $(date)"
echo ""

if [ $MESH_STATUS -ne 0 ]; then
    echo "ERROR: NURBS surface generation failed!"
    exit 1
fi

echo "=== Step 2.1: IMMEDIATE COORDINATE VERIFICATION ==="
SURFACE_FILE="$ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz"
if [ -f "$SURFACE_FILE" ]; then
    echo "✓ Surface file generated: Pot_A_Piece_01_Surface_0.xyz"

    # Read first coordinate line
    FIRST_LINE=$(head -15 "$SURFACE_FILE" | grep -v "^#" | grep -v "^segment" | head -1)
    echo ""
    echo "First data point:"
    echo "$FIRST_LINE"

    # Extract x coordinate
    X_COORD=$(echo "$FIRST_LINE" | awk '{print $1}')
    X_ABS=$(echo "$X_COORD" | awk '{print ($1 < 0) ? -$1 : $1}')

    echo ""
    echo "X coordinate magnitude: $X_ABS"

    # Check coordinate scale
    if (( $(echo "$X_ABS < 1000" | bc -l) )); then
        echo "✅ COORDINATE FIX SUCCESSFUL!"
        echo "   Coordinates are in millimeters (< 1000mm)"
        echo "   Expected range: -500 to 500mm"
    elif (( $(echo "$X_ABS > 1000000" | bc -l) )); then
        echo "❌ COORDINATE FIX FAILED!"
        echo "   Coordinates still > 1,000,000 (in kilometers)"
        echo "   BUG STILL PRESENT - Aborting"
        exit 1
    else
        echo "⚠️  WARNING: Coordinates in unexpected range (1000-1000000)"
    fi
    echo ""
else
    echo "❌ Surface file not found: $SURFACE_FILE"
    echo "Processing may have failed"
    exit 1
fi

echo "=== Step 3: MATLAB Axis Extraction ==="
echo "Running: extract_axes_for_surfaces.m"
echo "Start: $(date)"
echo ""

cd $ORIGINAL_NURBS_DIR
module load MATLAB/2024b_Update_3
time matlab -nodisplay -nosplash -r "try; extract_axes_for_surfaces; catch ME; disp(ME.message); exit(1); end; exit(0);"

MATLAB_STATUS=$?
echo ""
echo "MATLAB axis extraction exit code: $MATLAB_STATUS"
echo "End: $(date)"
echo ""

if [ $MATLAB_STATUS -ne 0 ]; then
    echo "ERROR: MATLAB axis extraction failed!"
    exit 1
fi

echo "=== Step 4: Breakline Extraction ==="
echo "Running: EdgeLineExtractionHeadless"
echo "Start: $(date)"
echo ""

cd $ORIGINAL_NURBS_DIR
time /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    --bind "$PREPROCESSING_DIR:/workspace" \
    $CONTAINER \
    bash -c "cd /workspace/original_nurbs_preprocessing && ./build/EdgeLineExtractionHeadless"

EDGE_STATUS=$?
echo ""
echo "EdgeLineExtractionHeadless exit code: $EDGE_STATUS"
echo "End: $(date)"
echo ""

if [ $EDGE_STATUS -ne 0 ]; then
    echo "ERROR: Edgeline extraction failed!"
    exit 1
fi

echo "=== Step 5: Organize Output Dataset ==="
mkdir -p "$OUTPUT_DIR/SfS_pp/Surfaces"
mkdir -p "$OUTPUT_DIR/SfS_pp/Breaklines"
mkdir -p "$OUTPUT_DIR/SfS_pp/Axes"

# Copy Surface files
echo "Copying Surface files..."
cp $ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/Pot_A_Piece_0[1-8]_Surface_*.xyz "$OUTPUT_DIR/SfS_pp/Surfaces/" 2>/dev/null
SURFACE_COUNT=$(ls "$OUTPUT_DIR/SfS_pp/Surfaces/"Pot_A_Piece_*_Surface_*.xyz 2>/dev/null | wc -l)

# Copy Breakline files
echo "Copying Breakline files..."
cp $ORIGINAL_NURBS_DIR/Dataset/Breaklines/Pot_A/Pot_A_Piece_0[1-8]_Breakline_*.pcd "$OUTPUT_DIR/SfS_pp/Breaklines/" 2>/dev/null
cp $ORIGINAL_NURBS_DIR/Dataset/Breaklines/Pot_A/Pot_A_Piece_0[1-8]_Breakline_*.ply "$OUTPUT_DIR/SfS_pp/Breaklines/" 2>/dev/null
cp $ORIGINAL_NURBS_DIR/Dataset/Breaklines/Pot_A/Pot_A_Piece_0[1-8]_Breakline_*.xyz "$OUTPUT_DIR/SfS_pp/Breaklines/" 2>/dev/null
BREAKLINE_COUNT=$(ls "$OUTPUT_DIR/SfS_pp/Breaklines/"Pot_A_Piece_*_Breakline_*.pcd 2>/dev/null | wc -l)

# Copy Axis files
echo "Copying Axis files..."
cp $ORIGINAL_NURBS_DIR/Dataset/Axes/Pot_A_Piece_0[1-8]_*Axis.xyz "$OUTPUT_DIR/SfS_pp/Axes/" 2>/dev/null
# Create symlinks for SFS compatibility
cd "$OUTPUT_DIR/SfS_pp/Axes/"
for i in {01..08}; do
    if [ -f "Pot_A_Piece_${i}_NURBS_Axis.xyz" ] && [ ! -f "Pot_A_Piece_${i}_Axis.xyz" ]; then
        ln -s "Pot_A_Piece_${i}_NURBS_Axis.xyz" "Pot_A_Piece_${i}_Axis.xyz"
    fi
done
AXIS_COUNT=$(ls "$OUTPUT_DIR/SfS_pp/Axes/"Pot_A_Piece_*_Axis.xyz 2>/dev/null | wc -l)

echo ""
echo "✓ Surface files copied: $SURFACE_COUNT/16 expected"
echo "✓ Breakline files copied: $BREAKLINE_COUNT/16 expected"
echo "✓ Axis files copied: $AXIS_COUNT/8 expected"
echo ""

echo "=== Step 6: COMPREHENSIVE VERIFICATION ==="
echo ""

# Check coordinate scales for all pieces
echo "--- Coordinate Scale Verification (All 8 Pieces) ---"
COORD_OK=0
COORD_FAIL=0
for i in {01..08}; do
    SURF_FILE="$OUTPUT_DIR/SfS_pp/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz"
    if [ -f "$SURF_FILE" ]; then
        FIRST=$(head -15 "$SURF_FILE" | grep -v "^#" | grep -v "^segment" | head -1)
        X=$(echo "$FIRST" | awk '{print $1}')
        X_ABS=$(echo "$X" | awk '{print ($1 < 0) ? -$1 : $1}')

        if (( $(echo "$X_ABS < 1000" | bc -l) )); then
            echo "  Piece $i: ✅ ${X}mm (correct scale)"
            ((COORD_OK++))
        elif (( $(echo "$X_ABS > 1000000" | bc -l) )); then
            echo "  Piece $i: ❌ ${X_ABS} (WRONG - still multiplied)"
            ((COORD_FAIL++))
        else
            echo "  Piece $i: ⚠️  ${X_ABS} (unexpected range)"
        fi
    else
        echo "  Piece $i: ❌ Surface file missing"
    fi
done

echo ""
echo "Coordinate verification: $COORD_OK correct, $COORD_FAIL failed"

if [ $COORD_FAIL -gt 0 ]; then
    echo "❌ COORDINATE FIX VERIFICATION FAILED"
    echo "Some pieces still have wrong coordinate scale"
    exit 1
fi

# Check breakline point counts (pieces 06/08 problem)
echo ""
echo "--- Breakline Point Count (Pieces 06/08 Check) ---"
for i in {06..08}; do
    BL_FILE="$OUTPUT_DIR/SfS_pp/Breaklines/Pot_A_Piece_${i}_Breakline_0.pcd"
    if [ -f "$BL_FILE" ]; then
        # Count data lines (skip header)
        POINTS=$(grep -v "^#" "$BL_FILE" | grep -v "^VERSION" | grep -v "^FIELDS" | grep -v "^SIZE" | grep -v "^TYPE" | grep -v "^COUNT" | grep -v "^WIDTH" | grep -v "^HEIGHT" | grep -v "^VIEWPOINT" | grep -v "^POINTS" | grep -v "^DATA" | wc -l)

        if [ $POINTS -ge 50 ]; then
            echo "  Piece $i: ✅ ${POINTS} points (sufficient)"
        else
            echo "  Piece $i: ⚠️  ${POINTS} points (< 50, may cause exclusion)"
        fi
    else
        echo "  Piece $i: ❌ Breakline file missing"
    fi
done

# Compare with working reference
echo ""
echo "--- Comparison with Working Reference ---"
REF_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20250905_ProperSegmentation"
if [ -d "$REF_DIR" ]; then
    REF_SURF="$REF_DIR/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
    NEW_SURF="$OUTPUT_DIR/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz"

    if [ -f "$REF_SURF" ] && [ -f "$NEW_SURF" ]; then
        REF_COORD=$(head -15 "$REF_SURF" | grep -v "^#" | grep -v "^segment" | head -1 | awk '{print $1}')
        NEW_COORD=$(head -15 "$NEW_SURF" | grep -v "^#" | grep -v "^segment" | head -1 | awk '{print $1}')

        echo "Reference (working): ${REF_COORD}mm"
        echo "New (with fix):      ${NEW_COORD}mm"

        # Calculate difference
        DIFF=$(echo "$REF_COORD - $NEW_COORD" | bc -l)
        DIFF_ABS=$(echo "$DIFF" | awk '{print ($1 < 0) ? -$1 : $1}')

        if (( $(echo "$DIFF_ABS < 5" | bc -l) )); then
            echo "✅ Coordinates match (difference: ${DIFF}mm)"
        else
            echo "⚠️  Coordinates differ (difference: ${DIFF}mm)"
        fi
    fi
fi

echo ""
echo "=== FINAL SUMMARY ==="
echo "Output directory: $OUTPUT_DIR"
echo "Surface files: $SURFACE_COUNT/16"
echo "Breakline files: $BREAKLINE_COUNT/16"
echo "Axis files: $AXIS_COUNT/8"
echo "Coordinate verification: $COORD_OK/8 correct"
echo ""
echo "Regeneration completed: $(date)"
echo ""
echo "========================================================================="
echo "NEXT STEP: Test this dataset with SFS assembly"
echo "Command: Update data_path.h to point to: $OUTPUT_DIR"
echo "         then run: sbatch run_nurbs_sfs_timestamped.sbatch"
echo "========================================================================="
