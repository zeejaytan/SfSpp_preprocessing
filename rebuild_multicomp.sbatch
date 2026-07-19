#!/bin/bash
#SBATCH --job-name=rebuild_edge
#SBATCH --output=rebuild_multicomp_%j.log
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== Rebuilding EdgeLineExtractionHeadless with multi-component boundary fix ==="
date

module load Apptainer

# Use the container with PCL 1.9.1 and NURBS support
CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BUILD_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/build_new"
SRC_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

echo "Container: $CONTAINER"
echo "Build dir: $BUILD_DIR"

# Check container exists
if [ ! -f "$CONTAINER" ]; then
    echo "ERROR: Container not found: $CONTAINER"
    exit 1
fi

# Clear cmake cache to force reconfigure with container paths
rm -f "$BUILD_DIR/CMakeCache.txt"
rm -rf "$BUILD_DIR/CMakeFiles"

cd "$BUILD_DIR"

# Build using container with PCL 1.9.1 NURBS
echo ""
echo "Running cmake and make inside container (PCL 1.9.1 NURBS)..."
apptainer exec \
    --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
    --pwd "$BUILD_DIR" \
    "$CONTAINER" bash -c "
        set -e
        echo 'Inside container...'
        echo 'CMake version:' && cmake --version | head -1
        echo 'GCC version:' && g++ --version | head -1

        # Check for NURBS headers
        echo ''
        echo 'Checking NURBS headers...'
        NURBS_HEADER=\$(find /usr -name 'fitting_surface_tdm.h' 2>/dev/null | head -1)
        if [ -n \"\$NURBS_HEADER\" ]; then
            echo 'Found NURBS header: '\$NURBS_HEADER
            PCL_DIR=\$(dirname \$(dirname \$(dirname \$(dirname \$NURBS_HEADER))))
            echo 'PCL include dir: '\$PCL_DIR
        else
            echo 'WARNING: NURBS header not found!'
            find /usr -name 'pcl_common.so*' 2>/dev/null | head -3
        fi

        echo ''
        echo 'Configuring with cmake...'
        cmake '$SRC_DIR' \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_CXX_STANDARD=17 \
            -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations -Wno-error'

        echo ''
        echo 'Building EdgeLineExtractionHeadless...'
        make EdgeLineExtractionHeadless -j4

        echo ''
        echo 'Build complete:'
        ls -la EdgeLineExtractionHeadless
    " 2>&1

BUILD_STATUS=$?

echo ""
echo "Build exit status: $BUILD_STATUS"

if [ $BUILD_STATUS -eq 0 ] && [ -f "$BUILD_DIR/EdgeLineExtractionHeadless" ]; then
    echo ""
    echo "SUCCESS! Binary info:"
    file "$BUILD_DIR/EdgeLineExtractionHeadless"
    ls -la "$BUILD_DIR/EdgeLineExtractionHeadless"

    echo ""
    echo "Testing binary inside container..."
    apptainer exec \
        --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 \
        --pwd "$BUILD_DIR" \
        "$CONTAINER" ./EdgeLineExtractionHeadless --help 2>&1 | head -5 || echo "Binary runs (no help text)"
else
    echo "BUILD FAILED!"
fi

echo ""
echo "=== Build complete ==="
date
