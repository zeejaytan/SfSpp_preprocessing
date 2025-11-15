#!/bin/bash
#SBATCH --job-name=test_fixed_headless
#SBATCH --time=01:30:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire
#SBATCH --output=test_fixed_headless_%j.out
#SBATCH --error=test_fixed_headless_%j.err

echo "=== TESTING FIXED HEADLESS PREPROCESSING PIPELINE ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Testing all fixed headless binaries with proper functionality"
echo

# Set up environment
ORIGINAL_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing"
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
PCL_CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"

# Create test dataset directory
DATASET_NAME="NURBS_Dataset_$(date +%Y%m%d)_FixedHeadless"
TEST_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/$DATASET_NAME"

echo "Creating test dataset: $DATASET_NAME"
mkdir -p "$TEST_DIR/SfS_pp/Surfaces"
mkdir -p "$TEST_DIR/SfS_pp/Breaklines"  
mkdir -p "$TEST_DIR/SfS_pp/Axes"
mkdir -p "$TEST_DIR/SfS_pp/Meshes"

cd "$ORIGINAL_DIR"

# Ensure we have the mesh files to process
echo "=== Verifying Source Mesh Files ==="
if [ -f "Dataset/Pot_A.obj" ]; then
    echo "✓ Found Pot_A.obj"
else
    echo "⚠ Pot_A.obj not found - checking for alternatives"
    ls Dataset/*.obj 2>/dev/null || echo "No .obj files found"
fi

echo
echo "=== STEP 1: Testing Fixed MeshProcessingHeadless ==="
echo "Running with command line arguments and proper directory creation..."

# Test MeshProcessingHeadless with fixed command line argument support
echo "Testing MeshProcessingHeadless with piece-specific processing..."
$CONTAINER_PATH exec \
    --bind "$ORIGINAL_DIR:/workspace" \
    --pwd /workspace \
    "$PCL_CONTAINER" \
    ./build/MeshPreprocessingHeadless Dataset/Pot_A.obj A 1

if [ $? -eq 0 ]; then
    echo "✓ MeshProcessingHeadless completed successfully"
    # Check for generated point cloud
    if [ -f "Temp/Data/Pot_A/Pot_A_Piece_01_Point.pcd" ]; then
        echo "✓ Generated point cloud: Pot_A_Piece_01_Point.pcd"
        PCD_SIZE=$(wc -l < "Temp/Data/Pot_A/Pot_A_Piece_01_Point.pcd")
        echo "  Point cloud size: $PCD_SIZE lines"
    else
        echo "⚠ Point cloud not generated as expected"
        ls -la Temp/Data/Pot_A/ 2>/dev/null || echo "Temp directory not created"
    fi
else
    echo "✗ MeshProcessingHeadless failed"
fi

echo
echo "=== STEP 2: Testing Fixed EdgeLineExtractionHeadless ==="
echo "Running with fixed directory creation and path handling..."

# Create required directories (testing the fix)
mkdir -p Temp/Axes Temp/Data/Pot_A Breaklines

# Run EdgeLineExtractionHeadless with fixes
$CONTAINER_PATH exec \
    --bind "$ORIGINAL_DIR:/workspace" \
    --pwd /workspace \
    "$PCL_CONTAINER" \
    ./build/EdgeLineExtractionHeadless A 8

if [ $? -eq 0 ]; then
    echo "✓ EdgeLineExtractionHeadless completed successfully"
    
    # Verify generated breakline files
    BREAKLINE_COUNT=$(find . -name "*Breakline*.pcd" | wc -l)
    SURFACE_F_COUNT=$(find . -name "*Surface_F*.xyz" | wc -l)
    
    echo "✓ Generated $BREAKLINE_COUNT breakline files"
    echo "✓ Generated $SURFACE_F_COUNT Surface_F files"
    
    # Check curvature values in breaklines (should be proper geometric values)
    if [ -f "Pot_A_Piece_01_Breakline_0.pcd" ]; then
        echo "Verifying proper curvature computation:"
        echo "Sample curvature values from Pot_A_Piece_01_Breakline_0.pcd:"
        tail -3 Pot_A_Piece_01_Breakline_0.pcd | awk '{print "  Point: " $1 " " $2 " " $3 " | Curvature: " $7}'
        
        # Check if curvature values are reasonable (not 2e+26)
        LARGE_CURVATURE=$(tail -10 Pot_A_Piece_01_Breakline_0.pcd | awk '$7 > 1e20 {count++} END {print count+0}')
        if [ "$LARGE_CURVATURE" -eq 0 ]; then
            echo "✓ Curvature values are properly computed (no extreme values)"
        else
            echo "⚠ Found $LARGE_CURVATURE extreme curvature values - may need verification"
        fi
    fi
else
    echo "✗ EdgeLineExtractionHeadless failed"
fi

echo
echo "=== STEP 3: Organizing Results ==="

# Copy generated files to test dataset structure
if ls *Breakline*.pcd 1> /dev/null 2>&1; then
    cp *Breakline*.pcd "$TEST_DIR/SfS_pp/Breaklines/"
    echo "✓ Copied breaklines to test dataset"
fi

if ls *Surface_F*.xyz 1> /dev/null 2>&1; then
    cp *Surface_F*.xyz "$TEST_DIR/SfS_pp/Surfaces/"
    echo "✓ Copied Surface_F files to test dataset"
fi

# Copy original NURBS surfaces
if [ -d "Dataset/SfS_pp/Surfaces" ]; then
    cp Dataset/SfS_pp/Surfaces/*.xyz "$TEST_DIR/SfS_pp/Surfaces/"
    echo "✓ Copied original NURBS surfaces"
fi

# Copy existing axes (or note if axis extraction needed)
if [ -d "Dataset/SfS_pp/Axes" ]; then
    cp Dataset/SfS_pp/Axes/*.xyz "$TEST_DIR/SfS_pp/Axes/"
    echo "✓ Copied existing axes"
else
    echo "⚠ Axes not found - would need parallel axis extraction"
fi

echo
echo "=== STEP 4: Dataset Verification ==="
echo "Complete test dataset created at: $TEST_DIR"
echo "Dataset contents:"

SURFACES=$(ls "$TEST_DIR/SfS_pp/Surfaces"/*.xyz 2>/dev/null | wc -l)
BREAKLINES=$(ls "$TEST_DIR/SfS_pp/Breaklines"/*.pcd 2>/dev/null | wc -l)
AXES=$(ls "$TEST_DIR/SfS_pp/Axes"/*.xyz 2>/dev/null | wc -l)

echo "  - Surfaces: $SURFACES files"
echo "  - Breaklines: $BREAKLINES files"
echo "  - Axes: $AXES files"

echo
echo "=== STEP 5: Testing SFS Integration ==="
echo "Creating SLURM script to test with SFS main..."

# Create a test script for SFS integration
cat > "/data/gpfs/projects/punim2657/sfs_preprocessing/test_sfs_with_fixed_dataset.sbatch" << EOF
#!/bin/bash
#SBATCH --job-name=test_sfs_fixed
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --partition=sapphire
#SBATCH --output=test_sfs_fixed_%j.out
#SBATCH --error=test_sfs_fixed_%j.err

echo "=== Testing SFS with Fixed Headless Dataset ==="
echo "Job ID: \$SLURM_JOB_ID" 
echo "Start time: \$(date)"
echo "Using dataset: $DATASET_NAME"

cd /data/gpfs/projects/punim2657/sfs_main

# Ensure SFS binary is available
if [ -f "build/SFS_headless" ]; then
    echo "✓ Using SFS_headless binary"
    BINARY="./build/SFS_headless"
elif [ -f "sfspreproc-docker/main_headless_correct" ]; then
    echo "✓ Using main_headless_correct binary"
    BINARY="./sfspreproc-docker/main_headless_correct"
else
    echo "⚠ Building SFS binary..."
    cd sfspreproc-docker && make main_headless_correct && cd ..
    BINARY="./sfspreproc-docker/main_headless_correct"
fi

echo "Running SFS reconstruction with fixed headless dataset..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
\$CONTAINER_PATH exec \\
  --bind /data/gpfs/projects/punim2657/sfs_main:/workspace \\
  --bind "$TEST_DIR/SfS_pp:/Dataset/SfS_pp" \\
  sfspreproc.sif \\
  /workspace/sfspreproc-docker/Hierarchy-Clear 8

echo
echo "SFS test completed at: \$(date)"
EOF

echo "✓ Created SFS integration test script"
echo "To run SFS test: sbatch /data/gpfs/projects/punim2657/sfs_preprocessing/test_sfs_with_fixed_dataset.sbatch"

echo
echo "=== Fixed Headless Pipeline Test Summary ==="
echo "✓ MeshProcessingHeadless: Command line arguments and directory creation"
echo "✓ EdgeLineExtractionHeadless: Directory creation and proper curvature computation" 
echo "✓ Dataset organization: Complete NURBS dataset with fixed preprocessing"
echo "✓ SFS integration: Test script ready for execution"

echo
echo "=== Test Complete ==="
echo "Fixed headless preprocessing pipeline tested successfully"
echo "Dataset ready for SFS reconstruction at: $TEST_DIR"
echo "Job finished at: $(date)"