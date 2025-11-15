#!/bin/bash

# Add NURBS support to existing container by building PCL 1.9.1 with NURBS
echo "=== Adding NURBS Support to SFS Preprocessing Container ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_from_working.sif"
SANDBOX_DIR="sandbox_nurbs"
NEW_CONTAINER="cache/sfs_prep_with_nurbs.sif"
LOG_DIR="logs"

mkdir -p "$LOG_DIR"

if [ ! -f "$CONTAINER" ]; then
    echo "✗ Base container not found: $CONTAINER"
    exit 1
fi

echo "✓ Found base container: $CONTAINER"

# Create sandbox from existing container
echo "Creating sandbox for NURBS enhancement..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

$APPTAINER build --sandbox --fakeroot "$SANDBOX_DIR" "$CONTAINER" 2>&1 | tee "$LOG_DIR/nurbs_sandbox_creation.log"

if [ $? -ne 0 ]; then
    echo "✗ Failed to create sandbox"
    exit 1
fi

echo "✓ Sandbox created successfully"

# Build PCL 1.9.1 with NURBS support inside sandbox
echo "Building PCL 1.9.1 with NURBS support..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    set -e
    echo 'Setting up build environment for PCL 1.9.1 with NURBS...'
    
    # Remove existing PCL installation to avoid conflicts
    echo 'Removing existing PCL packages...'
    apt-get update
    apt-get remove -y libpcl-dev libpcl1.12 || echo 'PCL packages not found, continuing...'
    
    # Install build dependencies for PCL with NURBS
    echo 'Installing build dependencies...'
    apt-get install -y \
        wget \
        build-essential \
        cmake \
        git \
        libboost-all-dev \
        libeigen3-dev \
        libflann-dev \
        libqhull-dev \
        libusb-1.0-0-dev \
        libopenni-dev \
        libopenni2-dev \
        libpcap-dev \
        libpng-dev \
        libvtk9-dev \
        libgtest-dev \
        freeglut3-dev \
        libxml2-dev \
        libsuitesparse-dev

    # Download and build PCL 1.9.1 with NURBS
    cd /tmp
    echo 'Downloading PCL 1.9.1...'
    wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
    cd pcl-pcl-1.9.1
    
    mkdir -p build
    cd build
    
    echo 'Configuring PCL 1.9.1 with NURBS support...'
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/pcl191 \
        -DBUILD_NURBS=ON \
        -DBUILD_ON_NURBS=ON \
        -DBUILD_surface_on_nurbs=ON \
        -DVTK_RENDERING_BACKEND=OpenGL2 \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_examples=OFF \
        -DBUILD_tools=OFF \
        -DBUILD_apps=OFF
    
    echo 'Building PCL 1.9.1 (this will take a while)...'
    make -j2
    
    echo 'Installing PCL 1.9.1...'
    make install
    
    echo 'Setting up environment for PCL 1.9.1...'
    echo 'export PKG_CONFIG_PATH=/usr/local/pcl191/lib/pkgconfig:\$PKG_CONFIG_PATH' >> /etc/environment
    echo 'export LD_LIBRARY_PATH=/usr/local/pcl191/lib:\$LD_LIBRARY_PATH' >> /etc/environment
    
    # Create symlinks for compatibility
    ln -sf /usr/local/pcl191/include/pcl-1.9 /usr/include/pcl-1.9
    
    # Verify NURBS headers are installed
    echo 'Verifying NURBS installation...'
    if [ -f '/usr/local/pcl191/include/pcl-1.9/pcl/surface/on_nurbs/fitting_surface_tdm.h' ]; then
        echo '✓ NURBS headers found'
        ls /usr/local/pcl191/include/pcl-1.9/pcl/surface/on_nurbs/ | head -5
    else
        echo '✗ NURBS headers not found'
        find /usr/local/pcl191 -name '*nurbs*' | head -5
        exit 1
    fi
    
    # Clean up build files to save space
    cd /tmp
    rm -rf pcl-pcl-1.9.1*
    
    echo 'PCL 1.9.1 with NURBS support installed successfully'
" 2>&1 | tee "$LOG_DIR/nurbs_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✓ PCL 1.9.1 with NURBS built successfully!"
    
    # Now try to build preprocessing tools with PCL 1.9.1
    echo "Building preprocessing tools with PCL 1.9.1 + NURBS..."
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        set -e
        cd /opt/sfs_prep/src
        rm -rf build
        mkdir -p build
        cd build
        
        # Configure with PCL 1.9.1 paths
        export PKG_CONFIG_PATH=/usr/local/pcl191/lib/pkgconfig:\$PKG_CONFIG_PATH
        export LD_LIBRARY_PATH=/usr/local/pcl191/lib:\$LD_LIBRARY_PATH
        
        echo 'Configuring preprocessing tools with PCL 1.9.1...'
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=/opt/sfs_prep \
            -DCMAKE_CXX_STANDARD=17 \
            -DPCL_DIR=/usr/local/pcl191/share/pcl-1.9 \
            -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations -I/usr/local/pcl191/include/pcl-1.9'
        
        echo 'Building preprocessing executables...'
        make -j2 VERBOSE=1
        
        echo 'Installing preprocessing executables...'
        make install
        
        echo 'Verifying build results...'
        ls -la /opt/sfs_prep/bin/
        
        if [ -f '/opt/sfs_prep/bin/MeshPreprocessing' ] && [ -f '/opt/sfs_prep/bin/EdgeLineExtraction' ]; then
            echo '✓ Both preprocessing executables built successfully with NURBS support'
            
            # Test executables
            echo 'Testing MeshPreprocessing executable:'
            /opt/sfs_prep/bin/MeshPreprocessing --help 2>/dev/null | head -3 || echo 'Executable exists but no help available'
            
            echo 'Testing EdgeLineExtraction executable:'
            /opt/sfs_prep/bin/EdgeLineExtraction --help 2>/dev/null | head -3 || echo 'Executable exists but no help available'
            
            exit 0
        else
            echo '✗ Some preprocessing executables are missing'
            exit 1
        fi
    " 2>&1 | tee "$LOG_DIR/preprocessing_with_nurbs_build.log"
    
    PREP_BUILD_RESULT=$?
    
    if [ $PREP_BUILD_RESULT -eq 0 ]; then
        echo "✓ Preprocessing tools with NURBS support built successfully!"
        
        # Convert sandbox to final container
        echo "Converting enhanced sandbox to SIF container..."
        $APPTAINER build --fakeroot "$NEW_CONTAINER" "$SANDBOX_DIR" 2>&1 | tee "$LOG_DIR/nurbs_sif_conversion.log"
        
        if [ $? -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
            echo "✓ Final container with NURBS support created successfully!"
            echo "Container location: $NEW_CONTAINER"
            echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
            
            # Test final container
            echo "Testing final container with NURBS support..."
            $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
                echo 'Final container test:'
                echo 'Available preprocessing tools:'
                ls -la /opt/sfs_prep/bin/
                echo 'NURBS headers check:'
                ls /usr/local/pcl191/include/pcl-1.9/pcl/surface/on_nurbs/ | head -3
                echo 'PCL 1.9.1 libraries:'
                ls /usr/local/pcl191/lib/libpcl_*.so | head -3
            "
            
            echo "✓ SFS Preprocessing container with NURBS support completed successfully!"
            echo "Usage: apptainer exec $NEW_CONTAINER /opt/sfs_prep/bin/MeshPreprocessing [args]"
            
            # Clean up sandbox
            echo "Cleaning up sandbox..."
            rm -rf "$SANDBOX_DIR"
            
        else
            echo "✗ Failed to convert sandbox to SIF container"
            tail -20 "$LOG_DIR/nurbs_sif_conversion.log"
            exit 1
        fi
    else
        echo "✗ Preprocessing tools build with NURBS failed!"
        tail -20 "$LOG_DIR/preprocessing_with_nurbs_build.log"
        exit 1
    fi
else
    echo "✗ PCL 1.9.1 with NURBS build failed!"
    tail -20 "$LOG_DIR/nurbs_build.log"
    exit 1
fi

echo "=== NURBS enhancement process completed ==="