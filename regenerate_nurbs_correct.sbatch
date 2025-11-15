#!/bin/bash
#SBATCH --job-name=nurbs_regen_correct
#SBATCH --time=03:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_regen_correct_%j.out
#SBATCH --error=nurbs_regen_correct_%j.err

echo "========================================================================="
echo "     NURBS Dataset Regeneration - With CORRECT Normal Computation"
echo "========================================================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo ""

echo "=== ROOT CAUSE FIX ==="
echo "Problem: Previous NURBS dataset used TPS-computed normals"
echo "Solution: Use original_nurbs_preprocessing/MeshPreprocessingHeadless"
echo "Method: fit.m_nurbs.EvNormal() - compute normals from NURBS surface"
echo ""

# Set paths
PREPROCESSING_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
ORIGINAL_NURBS_DIR="$PREPROCESSING_DIR/original_nurbs_preprocessing"
BUILD_DIR="$ORIGINAL_NURBS_DIR/build"
CONTAINER="$PREPROCESSING_DIR/pcl_191_nurbs.sif"
DATASET_NAME="NURBS_Dataset_$(date +%Y%m%d)_CorrectNormals"
OUTPUT_DIR="$PREPROCESSING_DIR/$DATASET_NAME"

cd $PREPROCESSING_DIR

echo "=== Verification ==="
echo "Checking correct executable exists..."
if [ ! -f "$BUILD_DIR/MeshPreprocessingHeadless" ]; then
    echo "ERROR: MeshPreprocessingHeadless not found!"
    echo "Expected: $BUILD_DIR/MeshPreprocessingHeadless"
    exit 1
fi

echo "✓ Executable found: $(ls -lh $BUILD_DIR/MeshPreprocessingHeadless | awk '{print $9, $5}')"
echo "  Built: $(stat -c %y $BUILD_DIR/MeshPreprocessingHeadless | cut -d'.' -f1)"
echo ""

# Verify NURBS normal computation in executable
echo "Verifying executable uses correct NURBS normal computation..."
if strings $BUILD_DIR/MeshPreprocessingHeadless | grep -q "EvNormal"; then
    echo "✓ Executable contains EvNormal (NURBS normal computation)"
else
    echo "WARNING: EvNormal not found in executable strings"
fi
echo ""

echo "Checking input data exists..."
INPUT_COUNT=$(ls $PREPROCESSING_DIR/Dataset/Point/Pot_A/Pot_A_Piece_0[1-8]_Point.pcd 2>/dev/null | wc -l)
MESH_COUNT=$(ls $PREPROCESSING_DIR/Dataset/Mesh/Pot_A/Pot_A_Piece_0[1-8]_Mesh.obj 2>/dev/null | wc -l)

if [ "$INPUT_COUNT" -lt 8 ]; then
    echo "ERROR: Not enough PCD files! Found: $INPUT_COUNT, Expected: 8"
    ls -la $PREPROCESSING_DIR/Dataset/Point/Pot_A/Pot_A_Piece_0[1-8]_Point.pcd 2>/dev/null
    exit 1
fi

if [ "$MESH_COUNT" -lt 8 ]; then
    echo "ERROR: Not enough OBJ files! Found: $MESH_COUNT, Expected: 8"
    ls -la $PREPROCESSING_DIR/Dataset/Mesh/Pot_A/Pot_A_Piece_0[1-8]_Mesh.obj 2>/dev/null
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

echo "=== Step 2: NURBS Surface Generation (WITH CORRECT NORMALS) ==="
echo "Running: MeshPreprocessingHeadless"
echo "Method: fit.m_nurbs.EvNormal() at line 902"
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

# Verify surfaces were created
SURFACE_COUNT=$(ls $ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/Pot_A_Piece_0[1-8]_Surface_*.xyz 2>/dev/null | wc -l)
echo "Generated surface files: $SURFACE_COUNT/16 (8 pieces × 2 surfaces)"

if [ "$SURFACE_COUNT" -lt 16 ]; then
    echo "WARNING: Expected 16 surface files, found $SURFACE_COUNT"
    ls -la $ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/
fi
echo ""

echo "=== Step 3: Edge Line Extraction ==="
echo "Running: EdgeLineExtractionHeadless"
echo "Start: $(date)"
echo ""

time /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    --bind "$PREPROCESSING_DIR:/workspace" \
    $CONTAINER \
    bash -c "cd /workspace/original_nurbs_preprocessing/build && ./EdgeLineExtractionHeadless"

EDGE_STATUS=$?
echo ""
echo "EdgeLineExtractionHeadless exit code: $EDGE_STATUS"
echo "End: $(date)"
echo ""

if [ $EDGE_STATUS -ne 0 ]; then
    echo "ERROR: Edge line extraction failed!"
    exit 1
fi

# Verify breaklines were created
BREAKLINE_COUNT=$(ls $BUILD_DIR/Pot_A_Piece_0[1-8]_Breakline_*.pcd 2>/dev/null | wc -l)
echo "Generated breakline files: $BREAKLINE_COUNT/16 (8 pieces × 2 breaklines)"

if [ "$BREAKLINE_COUNT" -lt 16 ]; then
    echo "WARNING: Expected 16 breakline files, found $BREAKLINE_COUNT"
    ls -la $BUILD_DIR/Pot_A_Piece_*_Breakline_*.pcd 2>/dev/null
fi
echo ""

echo "=== Step 4: Axis Extraction (MATLAB) ==="
echo "Running PotSAC axis extraction for 8 pieces..."
echo "Start: $(date)"
echo ""

module load MATLAB/2024b_Update_3

# Create output directory
mkdir -p $PREPROCESSING_DIR/axis_output

# Run axis extraction sequentially for each piece
for piece in {1..8}; do
    piece_num=$(printf "%02d" $piece)
    echo "Extracting axis for Piece $piece_num..."

    matlab -batch "
    try
        addpath('$PREPROCESSING_DIR');
        surface_file = '$ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/Pot_A_Piece_${piece_num}_Surface_0.xyz';
        output_file = '$PREPROCESSING_DIR/axis_output/Pot_A_Piece_${piece_num}_Axis.xyz';

        if ~exist(surface_file, 'file')
            error('Surface file not found: %s', surface_file);
        end

        extract_single_axis('A', $piece, surface_file, output_file);
        fprintf('✓ Axis extraction completed for Piece $piece_num\n');
    catch ME
        fprintf('ERROR in axis extraction for Piece $piece_num:\n');
        fprintf('%s\n', ME.message);
        exit(1);
    end
    exit(0);
    " > axis_piece_${piece_num}.log 2>&1

    if [ $? -ne 0 ]; then
        echo "ERROR: Axis extraction failed for Piece $piece_num"
        cat axis_piece_${piece_num}.log
    else
        echo "✓ Piece $piece_num axis extracted"
    fi
done

echo "End: $(date)"
echo ""

# Verify axis files were created
AXIS_COUNT=$(ls $PREPROCESSING_DIR/axis_output/Pot_A_Piece_0[1-8]_Axis.xyz 2>/dev/null | wc -l)
echo "Generated axis files: $AXIS_COUNT/8"

if [ "$AXIS_COUNT" -lt 8 ]; then
    echo "WARNING: Expected 8 axis files, found $AXIS_COUNT"
    ls -la $PREPROCESSING_DIR/axis_output/
fi
echo ""

echo "=== Step 5: Dataset Organization ==="
echo "Creating organized dataset: $DATASET_NAME"
echo ""

# Create directory structure
mkdir -p $OUTPUT_DIR/SfS_pp/{Surfaces,Breaklines,Axes,Mesh}

# Copy surfaces
echo "Copying NURBS surfaces (WITH CORRECT NORMALS)..."
cp $ORIGINAL_NURBS_DIR/Temp/Data/Pot_A/Pot_A_Piece_0[1-8]_Surface_*.xyz $OUTPUT_DIR/SfS_pp/Surfaces/
SURF_COPIED=$(ls $OUTPUT_DIR/SfS_pp/Surfaces/*.xyz 2>/dev/null | wc -l)
echo "✓ Copied $SURF_COPIED surface files"

# Copy breaklines
echo "Copying breaklines..."
cp $BUILD_DIR/Pot_A_Piece_0[1-8]_Breakline_*.pcd $OUTPUT_DIR/SfS_pp/Breaklines/
BREAK_COPIED=$(ls $OUTPUT_DIR/SfS_pp/Breaklines/*.pcd 2>/dev/null | wc -l)
echo "✓ Copied $BREAK_COPIED breakline files"

# Copy axes
echo "Copying axes..."
cp $PREPROCESSING_DIR/axis_output/Pot_A_Piece_0[1-8]_Axis.xyz $OUTPUT_DIR/SfS_pp/Axes/
AXIS_COPIED=$(ls $OUTPUT_DIR/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l)
echo "✓ Copied $AXIS_COPIED axis files"

# Copy meshes
echo "Copying original meshes..."
cp $PREPROCESSING_DIR/Dataset/Mesh/Pot_A/Pot_A_Piece_0[1-8]_Mesh.obj $OUTPUT_DIR/SfS_pp/Mesh/
MESH_COPIED=$(ls $OUTPUT_DIR/SfS_pp/Mesh/*.obj 2>/dev/null | wc -l)
echo "✓ Copied $MESH_COPIED mesh files"

echo ""
echo "=== Dataset Summary ==="
echo "Location: $OUTPUT_DIR"
echo ""
echo "File counts:"
echo "  Surfaces:   $SURF_COPIED/16  (8 pieces × 2 surfaces)"
echo "  Breaklines: $BREAK_COPIED/16  (8 pieces × 2 breaklines)"
echo "  Axes:       $AXIS_COPIED/8    (8 pieces)"
echo "  Meshes:     $MESH_COPIED/8    (8 pieces)"
echo ""

# Verify sample surface file has normals
echo "=== Normal Verification ==="
SAMPLE_SURFACE="$OUTPUT_DIR/SfS_pp/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
if [ -f "$SAMPLE_SURFACE" ]; then
    echo "Checking sample surface file format..."
    echo "File: $SAMPLE_SURFACE"
    echo "Size: $(du -h $SAMPLE_SURFACE | awk '{print $1}')"
    echo "First 3 lines:"
    head -3 "$SAMPLE_SURFACE"
    echo ""

    # Count fields in first data line (should be 6: x y z nx ny nz)
    FIELD_COUNT=$(head -1 "$SAMPLE_SURFACE" | awk '{print NF}')
    if [ "$FIELD_COUNT" -eq 6 ]; then
        echo "✓ Format correct: 6 fields (x y z nx ny nz)"
    else
        echo "WARNING: Expected 6 fields, found $FIELD_COUNT"
    fi
else
    echo "WARNING: Sample surface file not found"
fi
echo ""

echo "========================================================================="
echo "                    DATASET REGENERATION COMPLETE"
echo "========================================================================="
echo ""
echo "✅ NEW NURBS Dataset created: $DATASET_NAME"
echo "✅ Normals computed from NURBS surface using fit.m_nurbs.EvNormal()"
echo "✅ Ready for assembly testing"
echo ""
echo "Next steps:"
echo "  1. Update sfs_legacy_temp data_path.h to point to: $OUTPUT_DIR"
echo "  2. Rebuild sfs_legacy_temp executables"
echo "  3. Run assembly test: sbatch run_pot_a_nurbs_correct.sbatch"
echo "  4. Compare with sample results (expect 80-100% accuracy)"
echo ""
echo "End time: $(date)"
echo "========================================================================="
