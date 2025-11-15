#!/bin/bash

# Build SFS Preprocessing Container (Working Version)
echo "=== Building SFS Preprocessing Container (Working Version) ==="

# Load modules
module load Apptainer/1.3.3

# Configuration
CONTAINER_NAME="sfs_prep_working.sif"
DEFINITION_FILE="sfs_prep_working.def"
BUILD_LOG="logs/sfs_prep_working_build.log"

# Create logs directory
mkdir -p logs

echo "Building container: $CONTAINER_NAME"
echo "Using definition: $DEFINITION_FILE"
echo "Build log: $BUILD_LOG"

# Check if required files exist
echo "Checking source files..."
required_files=(
    "mesh_processing.cpp"
    "edgeline_extraction.cpp" 
    "CMakeLists.txt"
    "data_path.h"
    "alglib/"
)

for file in "${required_files[@]}"; do
    if [ ! -e "$file" ]; then
        echo "✗ Required file/directory not found: $file"
        exit 1
    else
        echo "✓ Found: $file"
    fi
done

# Remove old container if it exists
if [ -f "cache/$CONTAINER_NAME" ]; then
    echo "Removing old container..."
    rm "cache/$CONTAINER_NAME"
fi

# Create cache directory
mkdir -p cache

# Build the container with detailed logging
echo "Starting container build..."
echo "Build started at: $(date)"

apptainer build \
    --force \
    --fakeroot \
    cache/$CONTAINER_NAME \
    $DEFINITION_FILE \
    2>&1 | tee "$BUILD_LOG"

# Check build result
if [ ${PIPESTATUS[0]} -eq 0 ] && [ -f "cache/$CONTAINER_NAME" ]; then
    echo "✓ Container built successfully!"
    echo "Container size: $(ls -lh cache/$CONTAINER_NAME | awk '{print $5}')"
    
    # Test the container
    echo "Testing container functionality..."
    apptainer exec cache/$CONTAINER_NAME /bin/bash -c "
        echo 'Testing preprocessing tools:'
        ls -la /opt/sfs_prep/bin/ 2>/dev/null || echo 'No executables found'
        echo 'Testing dependencies:'
        ls -la /usr/local/include/tiny_obj_loader.h || echo 'tiny_obj_loader.h not found'
        find /usr -name '*wavefront*' -type f 2>/dev/null | head -3
        echo 'VTK/PCL verification:'
        find /usr/local -name '*pcl*' -type d 2>/dev/null | head -2
        find /usr/local -name '*vtk*' -type d 2>/dev/null | head -2
    "
    
    echo "Build completed successfully at: $(date)"
    
else
    echo "✗ Container build failed!"
    echo "Check the build log for details: $BUILD_LOG"
    tail -50 "$BUILD_LOG"
    exit 1
fi