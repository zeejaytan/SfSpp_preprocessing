#!/bin/bash

# Build script for original NURBS preprocessing using PCL 1.9.1 container
# This will run once the PCL 1.9.1 container build completes

set -e

echo "=== Building Original NURBS Preprocessing with PCL 1.9.1 ==="

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
PCL_CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"

# Check if PCL 1.9.1 container exists
if [ ! -f "$PCL_CONTAINER" ]; then
    echo "ERROR: PCL 1.9.1 container not found at $PCL_CONTAINER"
    echo "Make sure the container build job has completed successfully"
    exit 1
fi

# Test PCL 1.9.1 NURBS headers availability
echo "=== Testing PCL 1.9.1 NURBS Headers ==="
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace "$PCL_CONTAINER" \
    /bin/bash -c "find /usr/local/include -name 'fitting_surface_tdm.h' 2>/dev/null || echo 'NURBS headers not found'"

# Clean previous build
cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing
rm -rf build/*
mkdir -p build

echo "=== Configuring NURBS Preprocessing Build ==="
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace "$PCL_CONTAINER" \
    /bin/bash -c "cd /workspace/original_nurbs_preprocessing/build && \
                  cmake .. -DCMAKE_BUILD_TYPE=Release \
                           -DPCL_DIR=/usr/local/lib/cmake/pcl \
                           -DCGAL_DIR=/usr/lib64/cmake/CGAL"

echo "=== Building NURBS Preprocessing ==="
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace "$PCL_CONTAINER" \
    /bin/bash -c "cd /workspace/original_nurbs_preprocessing/build && make -j4"

echo "=== Verifying Build Results ==="
if [ -f "build/MeshPreprocessing" ] && [ -f "build/EdgeLineExtraction" ]; then
    echo "✅ NURBS preprocessing successfully built!"
    echo "Binaries:"
    ls -la build/MeshPreprocessing build/EdgeLineExtraction
else
    echo "❌ Build failed - binaries not found"
    exit 1
fi

echo "=== Build Complete ==="
echo "Next steps:"
echo "1. Test MeshPreprocessing with sample data"
echo "2. Test EdgeLineExtraction with generated surfaces"
echo "3. Compare NURBS vs TPS surface outputs"