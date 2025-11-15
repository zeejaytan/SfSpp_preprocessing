#!/bin/bash

echo "=== Testing Preprocessing with Main SfS Container ==="

# The main SfS container already has PCL and other dependencies
# Let's see if we can use it for preprocessing

SFS_MAIN_CONTAINER="/data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif"

if [ -f "$SFS_MAIN_CONTAINER" ]; then
    echo "✅ Found main SfS container: $SFS_MAIN_CONTAINER"
    
    echo "Testing container capabilities..."
    module load Apptainer/1.3.3
    
    # Test container functionality
    echo "1. Testing basic functionality:"
    apptainer exec "$SFS_MAIN_CONTAINER" /bin/bash -c "echo 'Container functional'"
    
    echo "2. Checking PCL availability:"
    apptainer exec "$SFS_MAIN_CONTAINER" /bin/bash -c "find /opt -name '*pcl*' | head -5"
    
    echo "3. Checking build tools:"
    apptainer exec "$SFS_MAIN_CONTAINER" /bin/bash -c "which cmake && which g++"
    
    echo "4. Testing preprocessing source compilation:"
    apptainer exec --bind $(pwd):/workspace "$SFS_MAIN_CONTAINER" /bin/bash -c "
        cd /workspace
        echo 'Testing preprocessing compilation in main SfS container...'
        mkdir -p build_test && cd build_test
        cmake .. -DCMAKE_BUILD_TYPE=Release 2>&1 || echo 'CMake configuration issues detected'
    "
    
else
    echo "❌ Main SfS container not found at: $SFS_MAIN_CONTAINER"
fi

echo ""
echo "=== Test completed ==="