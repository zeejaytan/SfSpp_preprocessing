#!/bin/bash

# Build PCL 1.9.1 with NURBS using Ubuntu 20.04 base (better VTK compatibility)
echo "=== Building PCL 1.9.1 with NURBS on Ubuntu 20.04 ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
SANDBOX_DIR="sandbox_ubuntu20_nurbs"
NEW_CONTAINER="cache/sfs_prep_ubuntu20_nurbs.sif"
LOG_DIR="logs"

mkdir -p "$LOG_DIR"

# Create Ubuntu 20.04 sandbox
echo "Creating Ubuntu 20.04 sandbox for PCL 1.9.1 + NURBS..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

# Create Ubuntu 20.04 container definition
cat > ubuntu20_nurbs.def << 'EOF'
Bootstrap: library
From: ubuntu:20.04

%post
    # Set timezone and disable interactive prompts
    export DEBIAN_FRONTEND=noninteractive
    export TZ=Etc/UTC
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
    
    # Update packages
    apt-get update
    
    # Install essential build tools
    apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        pkg-config \
        software-properties-common
    
    # Install VTK 7/8 compatible with PCL 1.9.1 (Ubuntu 20.04 has VTK 7.1)
    apt-get install -y \
        libvtk7-dev \
        libvtk7-qt-dev
    
    # Install PCL build dependencies
    apt-get install -y \
        libboost-all-dev \
        libeigen3-dev \
        libflann-dev \
        libqhull-dev \
        libusb-1.0-0-dev \
        libopenni-dev \
        libopenni2-dev \
        libpcap-dev \
        libpng-dev \
        libgtest-dev \
        freeglut3-dev \
        libxml2-dev \
        libsuitesparse-dev
    
    # Install CGAL
    apt-get install -y \
        libcgal-dev \
        libcgal-qt5-dev
    
    # Install OpenNURBS development packages (if available)
    apt-get install -y libopenturns-dev || echo "OpenNURBS packages not available, will build PCL without external NURBS"
    
    # Download and build PCL 1.9.1 from source with NURBS support
    cd /tmp
    wget https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
    cd pcl-pcl-1.9.1
    
    mkdir build
    cd build
    
    # Configure PCL 1.9.1 with NURBS and VTK 7
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/pcl191 \
        -DBUILD_NURBS=ON \
        -DBUILD_ON_NURBS=ON \
        -DBUILD_surface_on_nurbs=ON \
        -DWITH_VTK=ON \
        -DVTK_DIR=/usr/lib/cmake/vtk-7.1 \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_examples=OFF \
        -DBUILD_tools=OFF \
        -DBUILD_apps=OFF \
        -DBUILD_visualization=ON \
        -DBUILD_common=ON \
        -DBUILD_io=ON \
        -DBUILD_filters=ON \
        -DBUILD_features=ON \
        -DBUILD_surface=ON
    
    # Build PCL 1.9.1
    make -j2
    
    # Install PCL 1.9.1
    make install
    
    # Set up library paths
    echo '/usr/local/pcl191/lib' > /etc/ld.so.conf.d/pcl191.conf
    ldconfig
    
    # Create environment setup script
    cat > /usr/local/pcl191/setup_env.sh << 'SETUPEOF'
#!/bin/bash
export PKG_CONFIG_PATH=/usr/local/pcl191/lib/pkgconfig:$PKG_CONFIG_PATH
export LD_LIBRARY_PATH=/usr/local/pcl191/lib:$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/usr/local/pcl191:$CMAKE_PREFIX_PATH
export PCL_ROOT=/usr/local/pcl191
SETUPEOF
    chmod +x /usr/local/pcl191/setup_env.sh
    
    # Clean up
    cd /tmp
    rm -rf pcl-pcl-1.9.1*
    
    # Clean up packages
    apt-get clean
    rm -rf /var/lib/apt/lists/*

%environment
    export PKG_CONFIG_PATH=/usr/local/pcl191/lib/pkgconfig:$PKG_CONFIG_PATH
    export LD_LIBRARY_PATH=/usr/local/pcl191/lib:$LD_LIBRARY_PATH
    export CMAKE_PREFIX_PATH=/usr/local/pcl191:$CMAKE_PREFIX_PATH
    export PCL_ROOT=/usr/local/pcl191

%runscript
    echo "Ubuntu 20.04 container with PCL 1.9.1 + NURBS support"
    echo "PCL installation: /usr/local/pcl191"
    echo "Setup environment: source /usr/local/pcl191/setup_env.sh"
EOF

echo "Building Ubuntu 20.04 container with PCL 1.9.1 + NURBS..."
$APPTAINER build --fakeroot "$NEW_CONTAINER" ubuntu20_nurbs.def 2>&1 | tee "$LOG_DIR/ubuntu20_nurbs_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
    echo "✓ Ubuntu 20.04 PCL 1.9.1 container built successfully!"
    echo "Container location: $NEW_CONTAINER"
    echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
    
    # Test the PCL NURBS installation
    echo "Testing PCL 1.9.1 with NURBS installation..."
    $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
        echo '=== PCL 1.9.1 NURBS Installation Test ==='
        echo 'OS Version:'
        cat /etc/os-release | grep PRETTY_NAME
        echo
        echo 'PCL 1.9.1 installation:'
        ls -la /usr/local/pcl191/
        echo
        echo 'PCL 1.9.1 includes:'
        ls /usr/local/pcl191/include/pcl-1.9/pcl/ | head -10
        echo
        echo 'NURBS headers check:'
        if [ -d '/usr/local/pcl191/include/pcl-1.9/pcl/surface/on_nurbs' ]; then
            echo '✓ NURBS headers found:'
            ls /usr/local/pcl191/include/pcl-1.9/pcl/surface/on_nurbs/ | head -5
        else
            echo '✗ NURBS headers not found'
            find /usr/local/pcl191 -name '*nurbs*' | head -5
        fi
        echo
        echo 'PCL 1.9.1 libraries:'
        ls /usr/local/pcl191/lib/libpcl_*.so | head -5
        echo
        echo 'VTK version used:'
        dpkg -l | grep vtk | head -3
        echo
        echo 'Testing simple PCL compilation:'
        source /usr/local/pcl191/setup_env.sh
        cd /tmp
        cat > test_pcl191.cpp << 'CPPEOF'
#include <pcl/common/common_headers.h>
#include <iostream>
int main() {
    std::cout << \"PCL Version: \" << PCL_VERSION_PRETTY << std::endl;
    return 0;
}
CPPEOF
        g++ -std=c++14 test_pcl191.cpp -o test_pcl191 \
            -I/usr/local/pcl191/include/pcl-1.9 \
            -I/usr/include/eigen3 \
            -L/usr/local/pcl191/lib \
            -lpcl_common
        
        if [ -f 'test_pcl191' ]; then
            echo '✓ PCL 1.9.1 compilation successful'
            ./test_pcl191
        else
            echo '✗ PCL 1.9.1 compilation failed'
        fi
    " 2>&1 | tee "$LOG_DIR/ubuntu20_nurbs_test.log"
    
    # If PCL installation is successful, build preprocessing tools
    if grep -q "✓ NURBS headers found" "$LOG_DIR/ubuntu20_nurbs_test.log"; then
        echo "✓ NURBS support confirmed! Building preprocessing tools..."
        
        # Build preprocessing tools in this container
        $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
            set -e
            source /usr/local/pcl191/setup_env.sh
            
            mkdir -p /opt/sfs_prep/src
            cd /opt/sfs_prep/src
            
            # We'll copy source files from host - for now create placeholder
            echo 'Preprocessing source files will be copied from host'
            echo 'Container is ready for preprocessing tool compilation'
            
            # Install tiny_obj_loader.h
            wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h -O /usr/local/include/tiny_obj_loader.h
            echo '✓ tiny_obj_loader.h installed'
        " 2>&1 | tee "$LOG_DIR/ubuntu20_prep_setup.log"
        
        echo "✓ Ubuntu 20.04 PCL 1.9.1 NURBS container is ready!"
        echo "Next: Copy preprocessing source files and build tools"
        
    else
        echo "⚠ NURBS headers not found, but PCL 1.9.1 container built"
        echo "Container can be used for basic PCL functionality"
    fi
    
    # Clean up definition file
    rm -f ubuntu20_nurbs.def
    
else
    echo "✗ Ubuntu 20.04 PCL 1.9.1 container build failed!"
    tail -20 "$LOG_DIR/ubuntu20_nurbs_build.log"
    exit 1
fi

echo "=== Ubuntu 20.04 PCL 1.9.1 NURBS build completed ==="