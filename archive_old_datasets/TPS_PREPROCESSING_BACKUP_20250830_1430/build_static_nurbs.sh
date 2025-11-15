#!/bin/bash

# Static linking approach - build PCL 1.9.1 with static VTK to avoid conflicts
echo "=== Static Linking NURBS Solution ==="

# This approach builds VTK 8.2 as static libraries, then links PCL 1.9.1 statically
# This should work even with VTK 9.1 system libraries present

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
BASE_CONTAINER="../sfs_main/cache/sfspreproc-base.sif"

cat > static_nurbs.def << 'EOF'
Bootstrap: localimage
From: ../sfs_main/cache/sfspreproc-base.sif

%post
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    
    # Install build dependencies
    apt-get install -y build-essential cmake ninja-build \
        libgl1-mesa-dev libglu1-mesa-dev libxt-dev python3-dev \
        libjpeg-dev libtiff-dev libpng-dev libexpat1-dev \
        libfreetype6-dev zlib1g-dev qtbase5-dev
    
    cd /tmp
    
    # Build VTK 8.2 as STATIC libraries
    wget -q https://www.vtk.org/files/release/8.2/VTK-8.2.0.tar.gz
    tar -xf VTK-8.2.0.tar.gz
    cd VTK-8.2.0/build
    
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/vtk82_static \
        -DBUILD_SHARED_LIBS=OFF \
        -DVTK_BUILD_TESTING=OFF \
        -DVTK_BUILD_EXAMPLES=OFF \
        -GNinja
    
    ninja -j2 && ninja install
    
    # Build PCL 1.9.1 with static VTK
    cd /tmp
    wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
    cd pcl-pcl-1.9.1/build
    
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local/pcl191_static \
        -DBUILD_NURBS=ON \
        -DBUILD_ON_NURBS=ON \
        -DWITH_VTK=ON \
        -DVTK_DIR=/usr/local/vtk82_static/lib/cmake/vtk-8.2 \
        -DBUILD_SHARED_LIBS=OFF \
        -DCMAKE_CXX_STANDARD=14
    
    make -j2 && make install
    
    # Clean up
    rm -rf /tmp/*
    apt-get clean

%environment
    export PKG_CONFIG_PATH=/usr/local/pcl191_static/lib/pkgconfig:$PKG_CONFIG_PATH
    export CMAKE_PREFIX_PATH=/usr/local/pcl191_static:/usr/local/vtk82_static:$CMAKE_PREFIX_PATH
EOF

echo "This static linking approach might work - should I try it?"