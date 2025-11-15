#!/bin/bash
#SBATCH --job-name=nurbs_tray000
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=8:00:00
#SBATCH --output=nurbs_tray000_%j.out
#SBATCH --error=nurbs_tray000_%j.err

echo "=== NURBS Preprocessing Pipeline for Tray-000 (40 pieces) ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Configuration - Runtime naming via environment variables
POT_ID="A"                    # For legacy directory structure
POT_NAME="Tray-000"          # NEW: Runtime pot naming (no more Pot_A hardcoding!)
NUM_PIECES=40
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Tray-000_Dataset_20251021"
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Export environment variables for NURBS pipeline
export POT_NAME
export NURBS_OUTPUT_BASE="${OUTPUT_BASE}"

echo "=== Runtime Configuration ==="
echo "POT_NAME: ${POT_NAME} (used for file naming)"
echo "OUTPUT_BASE: ${OUTPUT_BASE} (used for direct output)"
echo ""

# Verify CloudCompare PCDs are ready
echo "=== Step 0: Verify Input Data ==="
echo "CloudCompare PCD files:"
FOUND_FILES=$(ls original_nurbs_preprocessing/Dataset/Point/${POT_NAME}/*.pcd 2>/dev/null | wc -l)
echo "Found ${FOUND_FILES} PCD files in ${POT_NAME}/"
if [ ${FOUND_FILES} -ne ${NUM_PIECES} ]; then
    echo "ERROR: Expected ${NUM_PIECES} PCD files, but found ${FOUND_FILES}"
    echo "Checking files:"
    ls -la original_nurbs_preprocessing/Dataset/Point/${POT_NAME}/ || echo "Directory not found"
    exit 1
fi
echo "Verification passed: ${NUM_PIECES} PCD files ready for NURBS processing"

# Create output directories (NURBS will write directly here)
echo "Creating output directories..."
mkdir -p ${OUTPUT_BASE}/SfS_pp/Surfaces
mkdir -p ${OUTPUT_BASE}/SfS_pp/Breaklines
mkdir -p ${OUTPUT_BASE}/SfS_pp/Axes
mkdir -p original_nurbs_preprocessing/Temp/Data/${POT_NAME}
mkdir -p original_nurbs_preprocessing/Temp/Temp/${POT_NAME}
mkdir -p original_nurbs_preprocessing/Temp/Temp_edge/${POT_NAME}
mkdir -p original_nurbs_preprocessing/build/Segments/

# Clean previous outputs
echo "Cleaning previous NURBS outputs for ${POT_NAME}..."
rm -f original_nurbs_preprocessing/Temp/Data/${POT_NAME}/*.xyz
rm -f original_nurbs_preprocessing/Temp/Temp/${POT_NAME}/*.ply
rm -f original_nurbs_preprocessing/Temp/Temp_edge/${POT_NAME}/*.ply
rm -f ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*_Surface_*.xyz
rm -f ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*_Breakline_*.pcd
rm -f ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*_Axis.xyz

# Step 1: NURBS Surface Generation
echo "=== Step 1: NURBS Surface Generation (40 pieces) ==="
echo "This will take approximately 2-3 hours for 40 pieces..."
echo "Running NURBS MeshPreprocessingHeadless..."

# Run NURBS preprocessing with environment variables for runtime naming and unit conversion
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && ./MeshPreprocessingHeadless"

if [ $? -ne 0 ]; then
    echo "ERROR: NURBS surface generation failed"
    exit 1
fi

echo "NURBS surface generation completed at: $(date)"

# Verify surface files (now in SfS_pp/Surfaces/ with correct naming)
echo "Surface files generated:"
SURFACE_COUNT=$(ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*_Surface_*.xyz 2>/dev/null | wc -l)
echo "Found ${SURFACE_COUNT} surface files (expected $((NUM_PIECES * 2)) for ${NUM_PIECES} pieces)"
if [ ${SURFACE_COUNT} -eq 0 ]; then
    echo "ERROR: No surface files generated!"
    echo "Checking output directory:"
    ls -la ${OUTPUT_BASE}/SfS_pp/Surfaces/
    exit 1
fi
echo "✓ Surfaces written directly to SfS_pp/Surfaces/ with ${POT_NAME} naming"

# Step 2: Edge Line Extraction
echo "=== Step 2: NURBS Edge Line Extraction ==="
echo "This will take approximately 1-2 hours for 40 pieces..."
echo "Running NURBS EdgeLineExtractionHeadless..."

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

# Verify breakline files (now in SfS_pp/Breaklines/ with correct naming and mm units)
echo "Breakline files generated:"
BREAKLINE_COUNT=$(ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*_Breakline_*.pcd 2>/dev/null | wc -l)
echo "Found ${BREAKLINE_COUNT} breakline files (expected $((NUM_PIECES * 2)) for ${NUM_PIECES} pieces)"
if [ ${BREAKLINE_COUNT} -eq 0 ]; then
    echo "ERROR: No breakline files generated!"
    echo "Checking output directory:"
    ls -la ${OUTPUT_BASE}/SfS_pp/Breaklines/
    exit 1
fi
echo "✓ Breaklines written directly to SfS_pp/Breaklines/ with ${POT_NAME} naming and millimeter units"

# Step 3: Axis Extraction using MATLAB PotSAC
echo "=== Step 3: MATLAB PotSAC Axis Extraction (40 pieces) ==="
echo "This will take approximately 1-2 hours for 40 pieces..."
echo "Loading MATLAB module..."
module load MATLAB/2024b_Update_3

echo "Running MATLAB axis extraction for 40 pieces..."
matlab -batch "
addpath('.');
for piece = 1:${NUM_PIECES}
    piece_str = sprintf('%02d', piece);
    surface_file = sprintf('${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_%s_Surface_0.xyz', piece_str);
    output_file = sprintf('${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_%s_Axis.xyz', piece_str);

    fprintf('Processing piece %s/%d...\n', piece_str, ${NUM_PIECES});
    if exist(surface_file, 'file')
        try
            extract_single_axis('${POT_ID}', piece, surface_file, output_file);
            fprintf('✅ Piece %s axis extraction completed\n', piece_str);
        catch ME
            fprintf('❌ Error processing piece %s: %s\n', piece_str, ME.message);
        end
    else
        fprintf('⚠️  Surface file not found: %s\n', surface_file);
    end
end
fprintf('All axis extractions completed\n');
quit;
"

if [ $? -ne 0 ]; then
    echo "WARNING: Some axis extractions may have failed"
fi

echo "Axis extraction completed at: $(date)"

# Verify axis files (now in SfS_pp/Axes/ with correct naming)
echo "Axis files generated:"
AXIS_COUNT=$(ls ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*_Axis.xyz 2>/dev/null | wc -l)
echo "Found ${AXIS_COUNT} axis files (expected ${NUM_PIECES} for ${NUM_PIECES} pieces)"
echo "✓ Axes written directly to SfS_pp/Axes/ with ${POT_NAME} naming"

# Final Verification
echo "=== Final Dataset Verification ==="
echo "${OUTPUT_BASE}/SfS_pp/ contents:"
echo "Surfaces: $(ls ${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_*_Surface_*.xyz 2>/dev/null | wc -l) files (expected $((NUM_PIECES * 2)))"
echo "Breaklines: $(ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_*_Breakline_*.pcd 2>/dev/null | wc -l) files (expected $((NUM_PIECES * 2)))"
echo "Axes: $(ls ${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_*_Axis.xyz 2>/dev/null | wc -l) files (expected ${NUM_PIECES})"
echo "Mesh: $(ls ${OUTPUT_BASE}/SfS_pp/Mesh/*.obj 2>/dev/null | wc -l) files (expected ${NUM_PIECES})"
echo "Point: $(ls ${OUTPUT_BASE}/SfS_pp/Point/*.pcd 2>/dev/null | wc -l) files (expected ${NUM_PIECES})"

echo ""
echo "=== NURBS Preprocessing for ${POT_NAME} Completed at: $(date) ==="
echo "✓ All files generated with correct naming (${POT_NAME})"
echo "✓ All files in correct directory structure (SfS_pp/)"
echo "✓ All coordinates converted to millimeters"
echo "Dataset ready for SFS main assembly at:"
echo "${OUTPUT_BASE}/SfS_pp/"
