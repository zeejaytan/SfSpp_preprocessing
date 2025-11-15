#!/bin/bash

# Simple build approach - use available system libraries
echo "=== Simple Build SFS Preprocessing Tools ==="

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Create a minimal build environment
export BUILD_DIR="build_simple"
export LOG_DIR="logs"

mkdir -p "$BUILD_DIR" "$LOG_DIR"

echo "Installing required system packages..."

# Install VTK and PCL development packages
sudo yum install -y vtk-devel pcl-devel || {
    echo "Failed to install system packages. Continuing with available libraries..."
}

# Install CGAL development packages
sudo yum install -y CGAL-devel || {
    echo "CGAL not available via yum. Trying alternative approach..."
}

# Download tiny_obj_loader.h if not present
if [ ! -f "tiny_obj_loader.h" ]; then
    echo "Downloading tiny_obj_loader.h..."
    wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h
fi

# Create a simplified CMakeLists.txt that's more flexible with versions
cat > CMakeLists_simple.txt << 'EOF'
cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(Pre-processing)

# C++17 Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Ignore old-style cast warnings
add_compile_options(-Wno-old-style-cast)

# More flexible PCL finding - accept any version
find_package(PCL REQUIRED COMPONENTS common io)
if(PCL_FOUND)
    message(STATUS "Found PCL version: ${PCL_VERSION}")
    include_directories(${PCL_INCLUDE_DIRS})
    link_directories(${PCL_LIBRARY_DIRS})
    add_definitions(${PCL_DEFINITIONS})
else()
    message(WARNING "PCL not found - using manual includes")
    # Try to find PCL headers manually
    find_path(PCL_INCLUDE_DIR pcl/point_cloud.h
        PATHS /usr/include /usr/local/include /opt/pcl/include
        PATH_SUFFIXES pcl-1.12 pcl-1.11 pcl-1.10 pcl-1.9)
    if(PCL_INCLUDE_DIR)
        include_directories(${PCL_INCLUDE_DIR})
        message(STATUS "Found PCL headers at: ${PCL_INCLUDE_DIR}")
    endif()
endif()

# More flexible CGAL finding
find_package(CGAL QUIET)
if(CGAL_FOUND)
    message(STATUS "Found CGAL version: ${CGAL_VERSION}")
    include_directories(${CGAL_INCLUDE_DIRS})
    link_directories(${CGAL_LIBRARY_DIRS})
    add_definitions(${CGAL_DEFINITIONS})
else()
    message(WARNING "CGAL not found - using manual includes")
    # Try to find CGAL headers manually
    find_path(CGAL_INCLUDE_DIR CGAL/Polygon_2.h
        PATHS /usr/include /usr/local/include /opt/cgal/include)
    if(CGAL_INCLUDE_DIR)
        include_directories(${CGAL_INCLUDE_DIR})
        message(STATUS "Found CGAL headers at: ${CGAL_INCLUDE_DIR}")
    endif()
endif()

# Include alglib source files
file(GLOB PROJ_DEP "alglib/src/*.cpp" "alglib/src/*.h")

# Add current source directory to include path for relative includes
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Try to build executables with error handling
try_compile(MESH_COMPILE_SUCCESS
    ${CMAKE_BINARY_DIR}/test_compile
    ${CMAKE_CURRENT_SOURCE_DIR}/mesh_processing.cpp
    CMAKE_FLAGS "-DCMAKE_CXX_STANDARD=17"
    OUTPUT_VARIABLE MESH_COMPILE_OUTPUT)

if(NOT MESH_COMPILE_SUCCESS)
    message(STATUS "Mesh processing compilation test failed:")
    message(STATUS "${MESH_COMPILE_OUTPUT}")
    message(STATUS "Will attempt to build with available libraries...")
endif()

# Build executables
add_executable(MeshPreprocessing mesh_processing.cpp)
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})

# Link available libraries
if(PCL_FOUND)
    target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES})
    target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES})
else()
    # Try to link standard PCL library names
    target_link_libraries(MeshPreprocessing pcl_common pcl_io pcl_surface pcl_on_nurbs)
    target_link_libraries(EdgeLineExtraction pcl_common pcl_io pcl_surface pcl_on_nurbs)
endif()

if(CGAL_FOUND)
    target_link_libraries(MeshPreprocessing ${CGAL_LIBRARIES})
    target_link_libraries(EdgeLineExtraction ${CGAL_LIBRARIES})
else()
    # Try to link standard CGAL library names
    target_link_libraries(MeshPreprocessing CGAL)
    target_link_libraries(EdgeLineExtraction CGAL)
endif()

# Standard system libraries
target_link_libraries(MeshPreprocessing stdc++fs)
target_link_libraries(EdgeLineExtraction stdc++fs)

# Build target
add_custom_target(all_targets ALL DEPENDS MeshPreprocessing EdgeLineExtraction)
EOF

cd "$BUILD_DIR"

echo "Configuring simple build..."
cmake .. -f ../CMakeLists_simple.txt \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations" \
    2>&1 | tee "../$LOG_DIR/simple_configure.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✗ Configuration failed, but let's try manual compilation..."
    
    # Manual compilation approach
    echo "Attempting manual compilation..."
    cd /data/gpfs/projects/punim2657/sfs_preprocessing
    
    # Find available headers
    echo "Searching for available headers..."
    PCL_INCLUDE=""
    CGAL_INCLUDE=""
    
    for dir in /usr/include /usr/local/include /opt/*/include; do
        if [ -d "$dir/pcl" ]; then
            PCL_INCLUDE="$PCL_INCLUDE -I$dir"
            echo "Found PCL headers in: $dir"
        fi
        if [ -f "$dir/CGAL/Polygon_2.h" ]; then
            CGAL_INCLUDE="$CGAL_INCLUDE -I$dir"
            echo "Found CGAL headers in: $dir"
        fi
    done
    
    # Compile with found headers
    echo "Compiling with manual flags..."
    g++ -std=c++17 -O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations \
        $PCL_INCLUDE $CGAL_INCLUDE -I. \
        -o MeshPreprocessing mesh_processing.cpp \
        -lpcl_common -lpcl_io -lpcl_surface -lCGAL -lstdc++fs \
        2>&1 | tee "$LOG_DIR/manual_mesh_compile.log"
    
    if [ -f "MeshPreprocessing" ]; then
        echo "✓ MeshPreprocessing compiled successfully!"
    else
        echo "✗ MeshPreprocessing compilation failed"
        tail -10 "$LOG_DIR/manual_mesh_compile.log"
    fi
    
    # Compile edge line extraction
    g++ -std=c++17 -O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations \
        $PCL_INCLUDE $CGAL_INCLUDE -I. \
        -o EdgeLineExtraction edgeline_extraction.cpp alglib/src/*.cpp \
        -lpcl_common -lpcl_io -lpcl_surface -lCGAL -lstdc++fs \
        2>&1 | tee "$LOG_DIR/manual_edge_compile.log"
        
    if [ -f "EdgeLineExtraction" ]; then
        echo "✓ EdgeLineExtraction compiled successfully!"
    else
        echo "✗ EdgeLineExtraction compilation failed"
        tail -10 "$LOG_DIR/manual_edge_compile.log"
    fi
    
else
    echo "Configuration successful, building..."
    make -j4 2>&1 | tee "../$LOG_DIR/simple_build.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Build successful!"
        ls -la MeshPreprocessing EdgeLineExtraction
    else
        echo "✗ Build failed"
        tail -20 "../$LOG_DIR/simple_build.log"
    fi
fi

echo "=== Simple build attempt completed ==="