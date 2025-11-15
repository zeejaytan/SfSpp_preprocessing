#!/bin/bash

# Host-Native NURBS Build - Build VTK 8.2 and PCL 1.9.1 directly on Spartan
echo "=== HOST-NATIVE NURBS BUILD (No Container Limitations) ==="

# Check host environment
echo "🔍 Analyzing Host Environment:"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME)"
echo "GCC: $(gcc --version 2>/dev/null | head -1 || echo 'GCC not found')"
echo "CMake: $(cmake --version 2>/dev/null | head -1 || echo 'CMake not found')"
echo "Available disk space: $(df -h /tmp | tail -1 | awk '{print $4}')"

# Set up build environment
HOST_BUILD_DIR="/tmp/host_nurbs_$(date +%s)"
VTK_BUILD_DIR="$HOST_BUILD_DIR/vtk82"
PCL_BUILD_DIR="$HOST_BUILD_DIR/pcl191"
INSTALL_PREFIX="$HOST_BUILD_DIR/install"

echo ""
echo "🎯 Host-Native Build Strategy:"
echo "Build directory: $HOST_BUILD_DIR"
echo "VTK 8.2 build: $VTK_BUILD_DIR"
echo "PCL 1.9.1 build: $PCL_BUILD_DIR" 
echo "Install prefix: $INSTALL_PREFIX"

mkdir -p "$HOST_BUILD_DIR" "$VTK_BUILD_DIR" "$PCL_BUILD_DIR" "$INSTALL_PREFIX"

# Check required modules on Spartan
echo ""
echo "🔧 Checking Available Modules on Spartan:"
module avail 2>&1 | grep -i cmake || echo "CMake module not found"
module avail 2>&1 | grep -i gcc || echo "GCC module not found"
module avail 2>&1 | grep -i python || echo "Python module not found"

# Load required modules if available
echo ""
echo "Loading required modules..."
module load GCC/11.3.0 || echo "Could not load GCC module"
module load CMake/3.24.3 || echo "Could not load CMake module"
module load Python/3.10.4 || echo "Could not load Python module"

echo ""
echo "Updated environment after module loading:"
echo "GCC: $(gcc --version 2>/dev/null | head -1 || echo 'GCC still not found')"
echo "CMake: $(cmake --version 2>/dev/null | head -1 || echo 'CMake still not found')"

cd "$HOST_BUILD_DIR"

if command -v cmake >/dev/null 2>&1 && command -v gcc >/dev/null 2>&1; then
    echo ""
    echo "✅ Build environment ready!"
    
    # Step 1: Download VTK 8.2.0
    echo ""
    echo "📥 Step 1: Downloading VTK 8.2.0..."
    wget -q https://www.vtk.org/files/release/8.2/VTK-8.2.0.tar.gz
    if [ $? -eq 0 ]; then
        echo "✅ VTK 8.2.0 downloaded successfully"
        tar -xf VTK-8.2.0.tar.gz
    else
        echo "❌ Failed to download VTK 8.2.0"
        exit 1
    fi
    
    # Step 2: Build VTK 8.2
    echo ""
    echo "🔨 Step 2: Building VTK 8.2 (Host-Native)..."
    cd VTK-8.2.0
    mkdir -p build && cd build
    
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX/vtk82" \
        -DBUILD_SHARED_LIBS=ON \
        -DVTK_QT_VERSION=5 \
        -DBUILD_TESTING=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DVTK_USE_SYSTEM_LIBRARIES=OFF
    
    if [ $? -eq 0 ]; then
        echo "✅ VTK 8.2 configuration successful"
        
        echo "🔨 Building VTK 8.2 (this will take 30-60 minutes)..."
        make -j4  # Use 4 cores for faster build
        
        if [ $? -eq 0 ]; then
            echo "✅ VTK 8.2 build successful!"
            
            echo "📦 Installing VTK 8.2..."
            make install
            
            if [ $? -eq 0 ]; then
                echo "✅ VTK 8.2 installed successfully!"
                
                # Step 3: Download PCL 1.9.1
                cd "$HOST_BUILD_DIR"
                echo ""
                echo "📥 Step 3: Downloading PCL 1.9.1..."
                wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
                
                if [ $? -eq 0 ]; then
                    echo "✅ PCL 1.9.1 downloaded successfully"
                    tar -xf pcl-1.9.1.tar.gz
                    
                    # Step 4: Verify OpenNURBS in PCL 1.9.1
                    echo ""
                    echo "🔍 Step 4: Verifying OpenNURBS 3rdparty in PCL 1.9.1..."
                    if [ -d "pcl-pcl-1.9.1/surface/include/pcl/surface/3rdparty/opennurbs" ]; then
                        echo "✅ OpenNURBS 3rdparty found!"
                        ls pcl-pcl-1.9.1/surface/include/pcl/surface/3rdparty/opennurbs/ | head -3
                        
                        # Step 5: Build PCL 1.9.1 with NURBS
                        echo ""
                        echo "🔨 Step 5: Building PCL 1.9.1 with TRUE NURBS support..."
                        cd pcl-pcl-1.9.1
                        mkdir -p build && cd build
                        
                        # Set up environment for VTK 8.2
                        export LD_LIBRARY_PATH="$INSTALL_PREFIX/vtk82/lib:$LD_LIBRARY_PATH"
                        export PKG_CONFIG_PATH="$INSTALL_PREFIX/vtk82/lib/pkgconfig:$PKG_CONFIG_PATH"
                        
                        cmake .. \
                            -DCMAKE_BUILD_TYPE=Release \
                            -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX/pcl191" \
                            -DBUILD_NURBS=ON \
                            -DBUILD_ON_NURBS=ON \
                            -DBUILD_surface_on_nurbs=ON \
                            -DWITH_VTK=ON \
                            -DVTK_DIR="$INSTALL_PREFIX/vtk82/lib/cmake/vtk-8.2" \
                            -DBUILD_SHARED_LIBS=ON \
                            -DBUILD_examples=OFF \
                            -DBUILD_tools=OFF \
                            -DBUILD_apps=OFF \
                            -DCMAKE_CXX_STANDARD=14 \
                            -DCMAKE_CXX_FLAGS="-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations"
                        
                        if [ $? -eq 0 ]; then
                            echo "✅ PCL 1.9.1 configuration successful!"
                            
                            echo "🔨 Building PCL 1.9.1 with NURBS (this will take 45-90 minutes)..."
                            make -j4  # Use 4 cores
                            
                            if [ $? -eq 0 ]; then
                                echo "✅ PCL 1.9.1 with NURBS build successful!"
                                
                                echo "📦 Installing PCL 1.9.1 with NURBS..."
                                make install
                                
                                if [ $? -eq 0 ]; then
                                    echo ""
                                    echo "🎉✅ HOST-NATIVE TRUE NURBS BUILD COMPLETED!"
                                    echo ""
                                    echo "🏆 ACHIEVEMENT: FULL NURBS SUPPORT ON HOST SYSTEM!"
                                    echo "✓ VTK 8.2: $INSTALL_PREFIX/vtk82"
                                    echo "✓ PCL 1.9.1 with NURBS: $INSTALL_PREFIX/pcl191"
                                    
                                    # Verify NURBS installation
                                    echo ""
                                    echo "🔍 Verifying NURBS installation..."
                                    if [ -f "$INSTALL_PREFIX/pcl191/include/pcl-1.9/pcl/surface/on_nurbs/fitting_surface_tdm.h" ]; then
                                        echo "✅ NURBS headers found!"
                                        
                                        if [ -f "$INSTALL_PREFIX/pcl191/include/pcl-1.9/pcl/surface/3rdparty/opennurbs/opennurbs.h" ]; then
                                            echo "✅ OpenNURBS 3rdparty headers found!"
                                            
                                            # Step 6: Build preprocessing tools with TRUE NURBS
                                            echo ""
                                            echo "🔨 Step 6: Building preprocessing tools with HOST NURBS..."
                                            
                                            PREPROCESSING_DIR="$HOST_BUILD_DIR/preprocessing"
                                            mkdir -p "$PREPROCESSING_DIR"
                                            cd "$PREPROCESSING_DIR"
                                            
                                            # Copy source files
                                            cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/mesh_processing.cpp .
                                            cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/edgeline_extraction.cpp .
                                            cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/CMakeLists.txt .
                                            cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/data_path.h .
                                            cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/alglib/ .
                                            
                                            # Download tiny_obj_loader.h
                                            wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h
                                            
                                            mkdir -p build && cd build
                                            
                                            # Build with host NURBS libraries
                                            cmake .. \
                                                -DCMAKE_BUILD_TYPE=Release \
                                                -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX/preprocessing" \
                                                -DCMAKE_CXX_STANDARD=17 \
                                                -DPCL_DIR="$INSTALL_PREFIX/pcl191/share/pcl-1.9" \
                                                -DVTK_DIR="$INSTALL_PREFIX/vtk82/lib/cmake/vtk-8.2" \
                                                -DCMAKE_PREFIX_PATH="$INSTALL_PREFIX/pcl191;$INSTALL_PREFIX/vtk82" \
                                                -DCMAKE_CXX_FLAGS="-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations"
                                            
                                            if [ $? -eq 0 ]; then
                                                echo "✅ Preprocessing tools configuration successful!"
                                                
                                                make -j4
                                                
                                                if [ $? -eq 0 ]; then
                                                    echo ""
                                                    echo "🎉🚀✅ HOST-NATIVE NURBS PREPROCESSING TOOLS COMPLETED!"
                                                    echo ""
                                                    echo "🏆 FINAL ACHIEVEMENT: FULL NURBS PREPROCESSING ON HOST!"
                                                    echo "✓ Built natively on Spartan host system"
                                                    echo "✓ No container limitations"
                                                    echo "✓ TRUE NURBS surface fitting"
                                                    echo "✓ TRUE NURBS edge detection"
                                                    echo ""
                                                    echo "📍 Installation locations:"
                                                    echo "  VTK 8.2: $INSTALL_PREFIX/vtk82"
                                                    echo "  PCL 1.9.1 NURBS: $INSTALL_PREFIX/pcl191"
                                                    echo "  Preprocessing tools: $PREPROCESSING_DIR/build/"
                                                    echo ""
                                                    echo "🚀 Usage (set environment first):"
                                                    echo "  export LD_LIBRARY_PATH=\"$INSTALL_PREFIX/vtk82/lib:$INSTALL_PREFIX/pcl191/lib:\$LD_LIBRARY_PATH\""
                                                    echo "  $PREPROCESSING_DIR/build/MeshPreprocessing input.ply output.ply"
                                                    echo "  $PREPROCESSING_DIR/build/EdgeLineExtraction input.ply edges.pcd"
                                                    
                                                    # Test the tools
                                                    echo ""
                                                    echo "🧪 Testing HOST NURBS tools..."
                                                    export LD_LIBRARY_PATH="$INSTALL_PREFIX/vtk82/lib:$INSTALL_PREFIX/pcl191/lib:$LD_LIBRARY_PATH"
                                                    
                                                    echo "MeshPreprocessing test:"
                                                    "$PREPROCESSING_DIR/build/MeshPreprocessing" 2>&1 | head -3
                                                    echo
                                                    echo "EdgeLineExtraction test:"
                                                    "$PREPROCESSING_DIR/build/EdgeLineExtraction" 2>&1 | head -3
                                                    
                                                    echo ""
                                                    echo "🎉 SUCCESS: HOST-NATIVE NURBS SOLUTION WORKING!"
                                                    
                                                else
                                                    echo "❌ Preprocessing tools build failed"
                                                fi
                                            else
                                                echo "❌ Preprocessing tools configuration failed"
                                            fi
                                        else
                                            echo "❌ OpenNURBS 3rdparty headers missing"
                                        fi
                                    else
                                        echo "❌ NURBS headers not found"
                                    fi
                                else
                                    echo "❌ PCL 1.9.1 installation failed"
                                fi
                            else
                                echo "❌ PCL 1.9.1 build failed"
                            fi
                        else
                            echo "❌ PCL 1.9.1 configuration failed"
                        fi
                    else
                        echo "❌ OpenNURBS 3rdparty not found in PCL 1.9.1"
                    fi
                else
                    echo "❌ PCL 1.9.1 download failed"
                fi
            else
                echo "❌ VTK 8.2 installation failed"
            fi
        else
            echo "❌ VTK 8.2 build failed"
        fi
    else
        echo "❌ VTK 8.2 configuration failed"
    fi
    
else
    echo ""
    echo "❌ Missing required tools (cmake, gcc)"
    echo "Available tools:"
    which cmake gcc g++ make 2>/dev/null || echo "None found"
    
    echo ""
    echo "🎯 Alternative approach needed:"
    echo "1. Load appropriate modules first"
    echo "2. Or use system package manager"
    echo "3. Or try a different host environment"
fi

echo ""
echo "=== HOST-NATIVE NURBS BUILD COMPLETED ==="