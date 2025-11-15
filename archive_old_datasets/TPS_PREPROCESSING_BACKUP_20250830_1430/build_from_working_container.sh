#!/bin/bash

# Build preprocessing tools using the existing working SFS container as base
echo "=== Building Preprocessing Tools Using Working SFS Container ==="

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Define paths
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
WORKING_CONTAINER="../sfs_main/sfspreproc.sif"
SANDBOX_DIR="sandbox_prep"
LOG_DIR="logs"
NEW_CONTAINER="cache/sfs_prep_from_working.sif"

mkdir -p cache "$LOG_DIR"

# Check if working container exists
if [ ! -f "$WORKING_CONTAINER" ]; then
    echo "✗ Working SFS container not found at: $WORKING_CONTAINER"
    exit 1
fi

echo "✓ Found working container: $WORKING_CONTAINER"
echo "Container size: $(ls -lh "$WORKING_CONTAINER" | awk '{print $5}')"

# Create sandbox from working container
echo "Creating sandbox from working container..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

$APPTAINER build --sandbox --fakeroot "$SANDBOX_DIR" "$WORKING_CONTAINER" 2>&1 | tee "$LOG_DIR/sandbox_creation.log"

if [ $? -ne 0 ]; then
    echo "✗ Failed to create sandbox"
    exit 1
fi

echo "✓ Sandbox created successfully"

# Check the environment inside the sandbox
echo "Checking sandbox environment..."
$APPTAINER exec "$SANDBOX_DIR" /bin/bash -c "
    echo 'Environment check:'
    echo 'OS: ' && cat /etc/os-release | grep PRETTY_NAME
    echo 'VTK: ' && find /usr/local -name 'vtk*.h' | head -3 | wc -l
    echo 'PCL: ' && find /usr/local -name '*pcl*' -type d | head -3 | wc -l
    echo 'CMake: ' && cmake --version | head -1
    echo 'G++: ' && g++ --version | head -1
    ls /usr/local/lib/ | grep vtk | head -3
    ls /usr/local/lib/ | grep pcl | head -3
" 2>&1 | tee "$LOG_DIR/sandbox_env_check.log"

# Copy preprocessing source files into sandbox
echo "Copying preprocessing source files into sandbox..."
mkdir -p "$SANDBOX_DIR/opt/sfs_prep/src"
cp -r mesh_processing.cpp edgeline_extraction.cpp CMakeLists.txt data_path.h alglib/ "$SANDBOX_DIR/opt/sfs_prep/src/"

# Install tiny_obj_loader.h into sandbox
echo "Installing tiny_obj_loader.h..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    cd /tmp
    wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h
    mv tiny_obj_loader.h /usr/local/include/
    echo 'tiny_obj_loader.h installed'
" 2>&1 | tee "$LOG_DIR/tiny_obj_install.log"

# Build preprocessing tools inside sandbox
echo "Building preprocessing tools inside sandbox..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    set -e
    echo 'Starting preprocessing build...'
    cd /opt/sfs_prep/src
    mkdir -p build bin
    cd build
    
    echo 'Configuring with CMake...'
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/sfs_prep \
        -DCMAKE_CXX_STANDARD=17 \
        -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations'
    
    echo 'Building executables...'
    make -j2 VERBOSE=1
    
    echo 'Installing executables...'
    make install
    
    echo 'Verifying build results...'
    ls -la /opt/sfs_prep/bin/
    
    if [ -f '/opt/sfs_prep/bin/MeshPreprocessing' ] && [ -f '/opt/sfs_prep/bin/EdgeLineExtraction' ]; then
        echo '✓ Both preprocessing executables built successfully'
        exit 0
    else
        echo '✗ Some executables are missing'
        exit 1
    fi
" 2>&1 | tee "$LOG_DIR/preprocessing_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✓ Preprocessing tools built successfully inside sandbox!"
    
    # Convert sandbox back to SIF container
    echo "Converting sandbox to SIF container..."
    $APPTAINER build --fakeroot "$NEW_CONTAINER" "$SANDBOX_DIR" 2>&1 | tee "$LOG_DIR/sif_conversion.log"
    
    if [ $? -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
        echo "✓ Final container created successfully!"
        echo "Container location: $NEW_CONTAINER"
        echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
        
        # Test the final container
        echo "Testing final container..."
        $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
            echo 'Final container test:'
            ls -la /opt/sfs_prep/bin/
            /opt/sfs_prep/bin/MeshPreprocessing --help 2>/dev/null | head -3 || echo 'MeshPreprocessing executable exists but no help available'
            /opt/sfs_prep/bin/EdgeLineExtraction --help 2>/dev/null | head -3 || echo 'EdgeLineExtraction executable exists but no help available'
        "
        
        echo "✓ Preprocessing container completed successfully!"
        echo "You can use the container with: apptainer exec $NEW_CONTAINER /opt/sfs_prep/bin/MeshPreprocessing"
        
        # Clean up sandbox (optional)
        echo "Cleaning up sandbox..."
        rm -rf "$SANDBOX_DIR"
        
    else
        echo "✗ Failed to convert sandbox to SIF container"
        tail -20 "$LOG_DIR/sif_conversion.log"
        exit 1
    fi
    
else
    echo "✗ Preprocessing tools build failed!"
    tail -20 "$LOG_DIR/preprocessing_build.log"
    exit 1
fi

echo "=== Build process completed ==="