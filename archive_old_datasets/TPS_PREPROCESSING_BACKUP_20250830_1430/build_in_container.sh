#!/bin/bash

# Build preprocessing tools inside the working SFS container
echo "=== Building Preprocessing Tools in Working SFS Container ==="

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Define apptainer path
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

# Check if container exists
CONTAINER_PATH="../sfspreproc.sif"
if [ ! -f "$CONTAINER_PATH" ]; then
    CONTAINER_PATH="/data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif"
    if [ ! -f "$CONTAINER_PATH" ]; then
        echo "✗ SFS container not found!"
        echo "Checked: ../sfspreproc.sif and /data/gpfs/projects/punim2657/sfs_main/sfspreproc.sif"
        exit 1
    fi
fi

echo "Container found: $CONTAINER_PATH"
echo "Container size: $(ls -lh "$CONTAINER_PATH" | awk '{print $5}')"

# Create build directory inside container workspace
mkdir -p container_build

# Copy preprocessing source files to build directory
cp -r mesh_processing.cpp edgeline_extraction.cpp CMakeLists.txt data_path.h alglib/ tiny_obj_loader.h container_build/ 2>/dev/null || echo "Some files may not exist"

# Create a container-compatible CMakeLists.txt
cat > container_build/CMakeLists_container.txt << 'EOF'
cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(Pre-processing)

# C++17 Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Use warnings but ignore old-style cast warnings (common in PCL 1.9.1)
add_compile_options(-Wno-old-style-cast -Wno-deprecated-declarations)

# Find PCL (should be 1.9.1 in container)
find_package(PCL 1.9 REQUIRED)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

# Find VTK (should be 8.2 in container)
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

# Find CGAL
find_package(CGAL REQUIRED)
include_directories(${CGAL_INCLUDE_DIRS})
link_directories(${CGAL_LIBRARY_DIRS})
add_definitions(${CGAL_DEFINITIONS})

# Find Boost (required by PCL)
find_package(Boost REQUIRED COMPONENTS system filesystem thread)

# Include alglib source files
file(GLOB PROJ_DEP "alglib/src/*.cpp" "alglib/src/*.h")

# Add current source directory for relative includes
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Build executables
add_executable(MeshPreprocessing mesh_processing.cpp)
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})

# Link libraries
target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES} ${VTK_LIBRARIES} ${CGAL_LIBRARIES} ${Boost_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES} ${VTK_LIBRARIES} ${CGAL_LIBRARIES} ${Boost_LIBRARIES} stdc++fs)

# Ensure executables are built
add_custom_target(all_targets ALL DEPENDS MeshPreprocessing EdgeLineExtraction)
EOF

# Build inside container
echo "Starting build inside container..."
$APPTAINER exec --bind $PWD:/workspace --pwd /workspace "$CONTAINER_PATH" /bin/bash -c "
    set -e
    echo 'Container environment check:'
    echo 'OS: ' && cat /etc/os-release | grep PRETTY_NAME
    echo 'CMake: ' && cmake --version | head -1
    echo 'G++: ' && g++ --version | head -1
    echo 
    echo 'Library paths:'
    ldconfig -p | grep -E '(vtk|pcl|cgal)' | head -5
    echo
    echo 'PCL headers:'
    find /usr/local -name 'common_headers.h' -path '*/pcl/*' 2>/dev/null | head -3
    echo
    echo 'VTK headers:'
    find /usr/local -name 'vtk*.h' -path '*/vtk*' 2>/dev/null | head -3
    echo
    echo 'Starting compilation...'
    cd container_build
    mkdir -p build && cd build
    
    # Configure
    echo 'Configuring with CMake...'
    cmake .. -f ../CMakeLists_container.txt -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations'
    
    # Build
    echo 'Building preprocessing tools...'
    make -j2 VERBOSE=1
    
    # Check results
    echo 'Build results:'
    ls -la MeshPreprocessing EdgeLineExtraction 2>/dev/null || echo 'Some executables missing'
    
    echo 'Done!'
" 2>&1 | tee logs/container_build.log

# Check if build succeeded
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✓ Container build completed!"
    
    # Copy executables back to host
    if [ -f "container_build/build/MeshPreprocessing" ] && [ -f "container_build/build/EdgeLineExtraction" ]; then
        cp container_build/build/MeshPreprocessing container_build/build/EdgeLineExtraction ./
        echo "✓ Preprocessing tools built successfully!"
        echo "Available executables:"
        ls -la MeshPreprocessing EdgeLineExtraction
    else
        echo "✗ Some executables are missing"
        ls -la container_build/build/
    fi
else
    echo "✗ Container build failed!"
    echo "Last 20 lines of build log:"
    tail -20 logs/container_build.log
fi

echo "=== Container build completed ==="