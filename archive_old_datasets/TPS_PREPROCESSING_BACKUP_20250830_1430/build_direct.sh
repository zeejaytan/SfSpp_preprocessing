#!/bin/bash

# Direct build of SFS preprocessing tools on host system
echo "=== Direct Build SFS Preprocessing Tools ==="

# Configuration
BUILD_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/direct_build"
PREFIX="/data/gpfs/projects/punim2657/sfs_preprocessing/install"
LOG_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/logs"

mkdir -p "$BUILD_DIR" "$PREFIX" "$LOG_DIR"
cd "$BUILD_DIR"

# Set environment for this build
export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="$PREFIX/lib:$LD_LIBRARY_PATH"
export CMAKE_PREFIX_PATH="$PREFIX:$CMAKE_PREFIX_PATH"

echo "Build directory: $BUILD_DIR"
echo "Install prefix: $PREFIX"
echo "Log directory: $LOG_DIR"

# Check if we have basic build tools
echo "Checking build environment..."
which g++ cmake wget || {
    echo "Missing basic build tools. Loading modules..."
    module load GCCcore/11.3.0
    module load CMake/3.24.3-GCCcore-11.3.0
}

echo "Current environment:"
echo "  G++ version: $(g++ --version | head -1)"
echo "  CMake version: $(cmake --version | head -1)"

# Stage 1: Build VTK 8.2 from source  
echo "[STAGE 1] Building VTK 8.2 from source..."
if [ ! -d "VTK-8.2.0" ]; then
    echo "Downloading VTK 8.2.0..."
    wget -q https://www.vtk.org/files/release/8.2/VTK-8.2.0.tar.gz
    tar -xf VTK-8.2.0.tar.gz
fi

cd VTK-8.2.0
mkdir -p build
cd build

echo "Configuring VTK 8.2..."
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DVTK_MODULE_ENABLE_VTK_RenderingContextOpenGL2=YES \
    -DBUILD_SHARED_LIBS=ON \
    2>&1 | tee "$LOG_DIR/vtk_configure.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ VTK configuration failed!"
    tail -20 "$LOG_DIR/vtk_configure.log"
    exit 1
fi

echo "Building VTK 8.2 (this will take a while)..."
make -j4 2>&1 | tee "$LOG_DIR/vtk_build.log" || {
    echo "Parallel build failed, trying single-threaded..."
    make -j1 2>&1 | tee -a "$LOG_DIR/vtk_build.log"
}

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ VTK build failed!"
    tail -20 "$LOG_DIR/vtk_build.log"
    exit 1
fi

echo "Installing VTK 8.2..."
make install 2>&1 | tee "$LOG_DIR/vtk_install.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ VTK installation failed!"
    tail -20 "$LOG_DIR/vtk_install.log"
    exit 1
fi

echo "✓ VTK 8.2 built and installed successfully"
cd "$BUILD_DIR"

# Stage 2: Build PCL 1.9.1 from source
echo "[STAGE 2] Building PCL 1.9.1 from source..."
if [ ! -d "pcl-pcl-1.9.1" ]; then
    echo "Downloading PCL 1.9.1..."
    wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
fi

cd pcl-pcl-1.9.1
mkdir -p build
cd build

echo "Configuring PCL 1.9.1..."
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DVTK_RENDERING_BACKEND=OpenGL2 \
    -DVTK_DIR="$PREFIX/lib/cmake/vtk-8.2" \
    -DBUILD_SHARED_LIBS=ON \
    2>&1 | tee "$LOG_DIR/pcl_configure.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ PCL configuration failed!"
    tail -20 "$LOG_DIR/pcl_configure.log"
    exit 1
fi

echo "Building PCL 1.9.1 (this will take a while)..."
make -j4 2>&1 | tee "$LOG_DIR/pcl_build.log" || {
    echo "Parallel build failed, trying single-threaded..."
    make -j1 2>&1 | tee -a "$LOG_DIR/pcl_build.log"
}

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ PCL build failed!"
    tail -20 "$LOG_DIR/pcl_build.log"
    exit 1
fi

echo "Installing PCL 1.9.1..."
make install 2>&1 | tee "$LOG_DIR/pcl_install.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ PCL installation failed!"
    tail -20 "$LOG_DIR/pcl_install.log"
    exit 1
fi

echo "✓ PCL 1.9.1 built and installed successfully"
cd "$BUILD_DIR"

# Stage 3: Install tiny_obj_loader.h header
echo "[STAGE 3] Installing tiny_obj_loader.h..."
mkdir -p "$PREFIX/include"
wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h -O "$PREFIX/include/tiny_obj_loader.h"

if [ -f "$PREFIX/include/tiny_obj_loader.h" ]; then
    echo "✓ tiny_obj_loader.h installed successfully"
else
    echo "✗ Failed to install tiny_obj_loader.h"
    exit 1
fi

# Stage 4: Build preprocessing tools
echo "[STAGE 4] Building preprocessing tools..."
cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Create a modified CMakeLists.txt for our custom build
cat > CMakeLists_direct.txt << 'EOF'
cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(Pre-processing)

# C++17 Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Ignore old-style cast warnings
add_compile_options(-Wno-old-style-cast)

# Use our custom VTK/PCL installation
set(CMAKE_PREFIX_PATH "/data/gpfs/projects/punim2657/sfs_preprocessing/install")

# PCL
find_package(PCL 1.9.1 REQUIRED)
find_package(PCL 1.9.1 REQUIRED COMPONENTS common io)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

# CGAL (system version)
find_package(CGAL REQUIRED)
include_directories(${CGAL_INCLUDE_DIRS})
link_directories(${CGAL_LIBRARY_DIRS})
add_definitions(${CGAL_DEFINITIONS})

if (MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj")
  add_definitions(-D _CRT_SECURE_NO_WARNINGS)
endif()

file(GLOB PROJ_DEP "alglib/src/*.cpp" "alglib/src/*.h")

# Add current source directory to include path for relative includes
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Add our custom include directory for tiny_obj_loader.h
include_directories("/data/gpfs/projects/punim2657/sfs_preprocessing/install/include")

# Build executables
add_executable(MeshPreprocessing mesh_processing.cpp)
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})

# Link Libraries
target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)

# Build all targets
add_custom_target(all_targets ALL DEPENDS MeshPreprocessing EdgeLineExtraction)
EOF

# Create build directory for preprocessing tools
mkdir -p build_direct
cd build_direct

echo "Configuring preprocessing tools build..."
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_FLAGS="-O2 -DNDEBUG -Wno-old-style-cast" \
    -f ../CMakeLists_direct.txt \
    2>&1 | tee "$LOG_DIR/preprocessing_configure.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ Preprocessing tools configuration failed!"
    tail -20 "$LOG_DIR/preprocessing_configure.log"
    exit 1
fi

echo "Building preprocessing tools..."
make -j4 2>&1 | tee "$LOG_DIR/preprocessing_build.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ Preprocessing tools build failed!"
    tail -20 "$LOG_DIR/preprocessing_build.log"
    exit 1
fi

# Verify build results
if [ -f "MeshPreprocessing" ] && [ -f "EdgeLineExtraction" ]; then
    echo "✓ Preprocessing tools built successfully!"
    echo "Executables:"
    ls -la MeshPreprocessing EdgeLineExtraction
    
    # Copy to install directory
    mkdir -p "$PREFIX/bin"
    cp MeshPreprocessing EdgeLineExtraction "$PREFIX/bin/"
    echo "Executables installed to: $PREFIX/bin/"
    
else
    echo "✗ Some executables are missing!"
    ls -la
    exit 1
fi

echo "=== Direct build completed successfully ==="
echo "Installation directory: $PREFIX"
echo "Executables available at: $PREFIX/bin/"