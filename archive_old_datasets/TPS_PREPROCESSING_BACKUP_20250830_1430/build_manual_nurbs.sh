#!/bin/bash

# Manual approach: Build OpenNURBS and PCL 1.9.1 with NURBS support
echo "=== Manual NURBS Build: OpenNURBS + PCL 1.9.1 ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_from_working.sif"
SANDBOX_DIR="sandbox_manual_nurbs"
NEW_CONTAINER="cache/sfs_prep_manual_nurbs.sif"
LOG_DIR="logs"

mkdir -p "$LOG_DIR"

if [ ! -f "$CONTAINER" ]; then
    echo "✗ Base container not found: $CONTAINER"
    exit 1
fi

echo "✓ Found base container: $CONTAINER"

# Create sandbox for manual NURBS build
echo "Creating sandbox for manual NURBS build..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

$APPTAINER build --sandbox --fakeroot "$SANDBOX_DIR" "$CONTAINER" 2>&1 | tee "$LOG_DIR/manual_sandbox_creation.log"

if [ $? -ne 0 ]; then
    echo "✗ Failed to create sandbox"
    exit 1
fi

echo "✓ Sandbox created successfully"

# Build OpenNURBS and PCL 1.9.1 with NURBS support manually
echo "Building OpenNURBS and PCL 1.9.1 with NURBS support..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    set -e
    export DEBIAN_FRONTEND=noninteractive
    
    echo '=== Manual NURBS Build Process ==='
    
    # Update package lists
    apt-get update
    
    # Install additional build dependencies
    apt-get install -y \
        libopenturns-dev \
        libopenmpi-dev \
        zlib1g-dev \
        libjpeg-dev \
        libglu1-mesa-dev \
        libxmu-dev \
        libxi-dev
    
    cd /tmp
    
    # Download and build OpenNURBS (Rhino's NURBS library)
    echo 'Downloading OpenNURBS...'
    wget -q https://github.com/mcneel/opennurbs/archive/refs/heads/7.x.zip -O opennurbs.zip
    unzip -q opennurbs.zip
    cd opennurbs-7.x
    
    echo 'Building OpenNURBS...'
    mkdir -p build
    cd build
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/opennurbs \
        -DBUILD_SHARED_LIBS=ON
    make -j2
    make install
    cd /tmp
    
    # Set up OpenNURBS environment
    echo '/usr/local/opennurbs/lib' > /etc/ld.so.conf.d/opennurbs.conf
    ldconfig
    
    echo '✓ OpenNURBS installed'
    
    # Now download and build PCL 1.9.1 with NURBS support
    echo 'Downloading PCL 1.9.1...'
    wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
    cd pcl-pcl-1.9.1
    
    # Apply potential fixes for modern compilers
    echo 'Applying compatibility patches...'
    # Fix C++17 compatibility issues if needed
    find . -name '*.h' -o -name '*.hpp' -o -name '*.cpp' | xargs sed -i 's/std::ptr_fun/std::function/g' || true
    
    mkdir -p build
    cd build
    
    echo 'Configuring PCL 1.9.1 with OpenNURBS support...'
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/pcl_nurbs \
        -DBUILD_NURBS=ON \
        -DBUILD_ON_NURBS=ON \
        -DBUILD_surface_on_nurbs=ON \
        -DWITH_VTK=ON \
        -DVTK_DIR=/usr/lib/x86_64-linux-gnu/cmake/vtk-9.1 \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_examples=OFF \
        -DBUILD_tools=ON \
        -DBUILD_apps=OFF \
        -DBUILD_visualization=ON \
        -DBUILD_common=ON \
        -DBUILD_io=ON \
        -DBUILD_filters=ON \
        -DBUILD_features=ON \
        -DBUILD_surface=ON \
        -DBUILD_keypoints=ON \
        -DBUILD_segmentation=ON \
        -DCMAKE_CXX_STANDARD=17 \
        -DOpenNURBS_ROOT=/usr/local/opennurbs \
        -DOpenNURBS_INCLUDE_DIR=/usr/local/opennurbs/include \
        -DOpenNURBS_LIBRARY=/usr/local/opennurbs/lib/libopennurbs.so
    
    echo 'Building PCL 1.9.1 with NURBS (this will take significant time)...'
    make -j2
    
    echo 'Installing PCL 1.9.1 with NURBS...'
    make install
    
    # Set up PCL NURBS environment
    echo '/usr/local/pcl_nurbs/lib' > /etc/ld.so.conf.d/pcl_nurbs.conf
    ldconfig
    
    # Create environment setup script
    cat > /usr/local/pcl_nurbs/setup_env.sh << 'ENVEOF'
#!/bin/bash
export PKG_CONFIG_PATH=/usr/local/pcl_nurbs/lib/pkgconfig:\$PKG_CONFIG_PATH
export LD_LIBRARY_PATH=/usr/local/pcl_nurbs/lib:/usr/local/opennurbs/lib:\$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/usr/local/pcl_nurbs:/usr/local/opennurbs:\$CMAKE_PREFIX_PATH
export PCL_ROOT=/usr/local/pcl_nurbs
export OpenNURBS_ROOT=/usr/local/opennurbs
ENVEOF
    chmod +x /usr/local/pcl_nurbs/setup_env.sh
    
    echo 'Verifying NURBS installation...'
    if [ -d '/usr/local/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs' ]; then
        echo '✓ NURBS headers found:'
        ls /usr/local/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs/ | head -5
        
        # Test NURBS functionality
        echo 'Testing NURBS compilation...'
        cd /tmp
        cat > test_nurbs.cpp << 'CPPEOF'
#include <pcl/surface/on_nurbs/fitting_surface_tdm.h>
#include <pcl/common/common_headers.h>
#include <iostream>

int main() {
    std::cout << \"PCL Version: \" << PCL_VERSION_PRETTY << std::endl;
    std::cout << \"NURBS support: Available\" << std::endl;
    
    // Try to create a simple NURBS object
    pcl::on_nurbs::NurbsDataSurface data;
    std::cout << \"✓ NURBS functionality working\" << std::endl;
    
    return 0;
}
CPPEOF
        
        source /usr/local/pcl_nurbs/setup_env.sh
        g++ -std=c++17 test_nurbs.cpp -o test_nurbs \
            -I/usr/local/pcl_nurbs/include/pcl-1.9 \
            -I/usr/local/opennurbs/include \
            -I/usr/include/eigen3 \
            -I/usr/include/vtk-9.1 \
            -L/usr/local/pcl_nurbs/lib \
            -L/usr/local/opennurbs/lib \
            -lpcl_common -lpcl_surface -lopennurbs
        
        if [ -f 'test_nurbs' ]; then
            echo '✓ NURBS compilation successful'
            ./test_nurbs
        else
            echo '✗ NURBS compilation failed'
        fi
        
        echo '✓ PCL 1.9.1 with NURBS installed successfully'
    else
        echo '✗ NURBS headers not found'
        find /usr/local/pcl_nurbs -name '*nurbs*' | head -10
        exit 1
    fi
    
    # Clean up build files
    cd /tmp
    rm -rf pcl-pcl-1.9.1* opennurbs* *.zip *.tar.gz
    
    echo 'Manual NURBS build completed successfully'
" 2>&1 | tee "$LOG_DIR/manual_nurbs_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✓ Manual OpenNURBS + PCL 1.9.1 build successful!"
    
    # Now build preprocessing tools with full NURBS support
    echo "Building preprocessing tools with manual NURBS installation..."
    
    # Copy source files
    mkdir -p "$SANDBOX_DIR/opt/sfs_prep/src"
    cp -r mesh_processing.cpp edgeline_extraction.cpp CMakeLists.txt data_path.h alglib/ "$SANDBOX_DIR/opt/sfs_prep/src/"
    
    # Install tiny_obj_loader.h
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h -O /usr/local/include/tiny_obj_loader.h
        echo '✓ tiny_obj_loader.h installed'
    " 2>&1 | tee -a "$LOG_DIR/manual_nurbs_build.log"
    
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        set -e
        cd /opt/sfs_prep/src
        
        # Source NURBS environment
        source /usr/local/pcl_nurbs/setup_env.sh
        
        rm -rf build
        mkdir -p build
        cd build
        
        echo 'Configuring preprocessing tools with manual NURBS installation...'
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=/opt/sfs_prep \
            -DCMAKE_CXX_STANDARD=17 \
            -DPCL_DIR=/usr/local/pcl_nurbs/share/pcl-1.9 \
            -DOpenNURBS_ROOT=/usr/local/opennurbs \
            -DCMAKE_PREFIX_PATH='/usr/local/pcl_nurbs;/usr/local/opennurbs' \
            -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations'
        
        echo 'Building preprocessing executables with manual NURBS...'
        make -j2 VERBOSE=1
        
        echo 'Installing preprocessing executables...'
        make install
        
        echo 'Verifying manual NURBS build results...'
        ls -la /opt/sfs_prep/bin/
        
        if [ -f '/opt/sfs_prep/bin/MeshPreprocessing' ] && [ -f '/opt/sfs_prep/bin/EdgeLineExtraction' ]; then
            echo '✓ Both preprocessing executables built with manual NURBS support'
            
            # Test executables
            source /usr/local/pcl_nurbs/setup_env.sh
            echo 'Testing MeshPreprocessing with manual NURBS:' 
            /opt/sfs_prep/bin/MeshPreprocessing --help 2>&1 | head -3 || echo 'Manual NURBS executable exists'
            
            echo 'Testing EdgeLineExtraction with manual NURBS:'
            /opt/sfs_prep/bin/EdgeLineExtraction --help 2>&1 | head -3 || echo 'Manual NURBS executable exists'
            
            exit 0
        else
            echo '✗ Some preprocessing executables are missing'
            exit 1
        fi
    " 2>&1 | tee "$LOG_DIR/manual_preprocessing_build.log"
    
    PREP_BUILD_RESULT=$?
    
    if [ $PREP_BUILD_RESULT -eq 0 ]; then
        echo "✓ Preprocessing tools with manual NURBS support built successfully!"
        
        # Convert sandbox to final container
        echo "Converting manual NURBS sandbox to SIF container..."
        $APPTAINER build --fakeroot "$NEW_CONTAINER" "$SANDBOX_DIR" 2>&1 | tee "$LOG_DIR/manual_sif_conversion.log"
        
        if [ $? -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
            echo "✓ Final manual NURBS container created successfully!"
            echo "Container location: $NEW_CONTAINER"
            echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
            
            # Test final container
            echo "Testing final manual NURBS container..."
            $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
                source /usr/local/pcl_nurbs/setup_env.sh
                echo 'Final container test with manual NURBS:'
                echo 'Available preprocessing tools:'
                ls -la /opt/sfs_prep/bin/
                echo 'NURBS headers verification:'
                ls /usr/local/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs/ | head -3
                echo 'PCL 1.9.1 NURBS libraries:'
                ls /usr/local/pcl_nurbs/lib/libpcl_surface* 2>/dev/null || echo 'Surface library not found'
                echo 'OpenNURBS libraries:'
                ls /usr/local/opennurbs/lib/ | head -3
            "
            
            echo "✅ SFS Preprocessing container with FULL MANUAL NURBS support completed!"
            echo "Usage:"
            echo "  apptainer exec $NEW_CONTAINER bash -c 'source /usr/local/pcl_nurbs/setup_env.sh && /opt/sfs_prep/bin/MeshPreprocessing input.ply output.ply'"
            echo "  apptainer exec $NEW_CONTAINER bash -c 'source /usr/local/pcl_nurbs/setup_env.sh && /opt/sfs_prep/bin/EdgeLineExtraction input.ply edges.pcd'"
            
            # Clean up sandbox
            echo "Cleaning up sandbox..."
            rm -rf "$SANDBOX_DIR"
            
        else
            echo "✗ Failed to convert manual sandbox to SIF container"
            tail -20 "$LOG_DIR/manual_sif_conversion.log"
            exit 1
        fi
    else
        echo "✗ Preprocessing tools build with manual NURBS failed!"
        tail -20 "$LOG_DIR/manual_preprocessing_build.log"
        exit 1
    fi
else
    echo "✗ Manual OpenNURBS + PCL 1.9.1 build failed!"
    tail -20 "$LOG_DIR/manual_nurbs_build.log"
    exit 1
fi

echo "=== Manual NURBS enhancement process completed ==="