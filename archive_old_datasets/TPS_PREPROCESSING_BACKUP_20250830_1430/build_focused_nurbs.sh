#!/bin/bash

# Focused approach: Build only what's needed for NURBS support
echo "=== Focused NURBS Build: Minimal PCL 1.9.1 NURBS Headers ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_from_working.sif"
SANDBOX_DIR="sandbox_focused_nurbs"
NEW_CONTAINER="cache/sfs_prep_focused_nurbs.sif"
LOG_DIR="logs"

mkdir -p "$LOG_DIR"

if [ ! -f "$CONTAINER" ]; then
    echo "✗ Base container not found: $CONTAINER"
    exit 1
fi

echo "✓ Found base container: $CONTAINER"

# Create sandbox for focused NURBS build
echo "Creating sandbox for focused NURBS build..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

$APPTAINER build --sandbox --fakeroot "$SANDBOX_DIR" "$CONTAINER" 2>&1 | tee "$LOG_DIR/focused_sandbox_creation.log"

if [ $? -ne 0 ]; then
    echo "✗ Failed to create sandbox"
    exit 1
fi

echo "✓ Sandbox created successfully"

# Build minimal PCL 1.9.1 NURBS support
echo "Building minimal PCL 1.9.1 NURBS components..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    set -e
    export DEBIAN_FRONTEND=noninteractive
    
    echo '=== Focused NURBS Build: Headers Only ==='
    
    cd /tmp
    
    # Download PCL 1.9.1 source
    echo 'Downloading PCL 1.9.1 source...'
    wget -q https://github.com/PointCloudLibrary/pcl/archive/refs/tags/pcl-1.9.1.tar.gz
    tar -xf pcl-1.9.1.tar.gz
    cd pcl-pcl-1.9.1
    
    # Extract and install only NURBS headers (no compilation)
    echo 'Installing PCL 1.9.1 NURBS headers...'
    mkdir -p /usr/local/include/pcl-1.9/pcl/surface/on_nurbs
    cp surface/include/pcl/surface/on_nurbs/*.h /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/ 2>/dev/null || echo 'NURBS headers not found in expected location'
    
    # Check alternative locations
    find . -path '*/pcl/surface/on_nurbs/*.h' -exec cp {} /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/ \\;
    
    # Also copy any NURBS implementation files
    find . -name '*nurbs*' -name '*.hpp' -exec cp {} /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/ \\; 2>/dev/null || true
    
    # Verify NURBS headers are available
    echo 'Verifying NURBS headers installation...'
    if [ -f '/usr/local/include/pcl-1.9/pcl/surface/on_nurbs/fitting_surface_tdm.h' ]; then
        echo '✓ Key NURBS header found'
        ls /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/
    else
        echo '✗ Key NURBS header not found, searching...'
        find . -name 'fitting_surface_tdm.h' -exec cp {} /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/ \\;
        find . -name '*nurbs*.h' | head -10
    fi
    
    # Create symlinks for PCL compatibility
    ln -sf /usr/local/include/pcl-1.9 /usr/include/pcl-1.9 2>/dev/null || true
    
    echo 'NURBS headers setup completed'
    
    # Clean up source
    cd /tmp
    rm -rf pcl-pcl-1.9.1*
" 2>&1 | tee "$LOG_DIR/focused_nurbs_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✓ Focused NURBS headers installation completed!"
    
    # Copy original preprocessing source files with NURBS support
    echo "Copying original preprocessing source files..."
    mkdir -p "$SANDBOX_DIR/opt/sfs_prep_nurbs/src"
    cp -r mesh_processing.cpp edgeline_extraction.cpp CMakeLists.txt data_path.h alglib/ "$SANDBOX_DIR/opt/sfs_prep_nurbs/src/"
    
    # Install tiny_obj_loader.h
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        wget -q https://raw.githubusercontent.com/tinyobjloader/tinyobjloader/release/tiny_obj_loader.h -O /usr/local/include/tiny_obj_loader.h
        echo '✓ tiny_obj_loader.h installed'
    " 2>&1 | tee -a "$LOG_DIR/focused_nurbs_build.log"
    
    # Try to build preprocessing tools with mixed PCL versions (headers from 1.9.1, libs from 1.12)
    echo "Building preprocessing tools with focused NURBS headers..."
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        set -e
        cd /opt/sfs_prep_nurbs/src
        
        rm -rf build
        mkdir -p build
        cd build
        
        echo 'Configuring preprocessing tools with focused NURBS headers...'
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=/opt/sfs_prep_nurbs \
            -DCMAKE_CXX_STANDARD=17 \
            -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations -I/usr/local/include/pcl-1.9 -I/usr/include/pcl-1.12 -DUSE_NURBS_HEADERS_ONLY' \
            -DCMAKE_PREFIX_PATH='/usr/local;/usr'
        
        echo 'Building preprocessing executables with focused NURBS...'
        make -j2 VERBOSE=1 2>&1 | head -50  # Limit output to see errors
        
        echo 'Build result check...'
        if [ -f 'MeshPreprocessing' ] && [ -f 'EdgeLineExtraction' ]; then
            echo '✓ Both preprocessing executables built with focused NURBS approach'
            make install
            exit 0
        else
            echo '✗ Build failed, trying fallback compilation approach...'
            
            # Fallback: Try to compile directly with g++
            cd ..
            echo 'Direct g++ compilation with NURBS headers...'
            g++ -std=c++17 mesh_processing.cpp -o MeshPreprocessing \\\
                -I/usr/local/include/pcl-1.9 \\\
                -I/usr/include/pcl-1.12 \\\
                -I/usr/include/eigen3 \\\
                -I/usr/include/vtk-9.1 \\\
                -I/usr/local/include \\\
                -L/usr/lib/x86_64-linux-gnu \\\
                -lpcl_common -lpcl_io -lpcl_filters -lpcl_surface -lpcl_features -lpcl_kdtree -lpcl_search \\\
                -O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations \\\
                -DUSE_FALLBACK_NURBS 2>&1 | head -20
            
            g++ -std=c++17 edgeline_extraction.cpp -o EdgeLineExtraction \\\
                -I/usr/local/include/pcl-1.9 \\\
                -I/usr/include/pcl-1.12 \\\
                -I/usr/include/eigen3 \\\
                -I/usr/include/vtk-9.1 \\\
                -I/usr/local/include \\\
                -L/usr/lib/x86_64-linux-gnu \\\
                -lpcl_common -lpcl_io -lpcl_filters -lpcl_surface -lpcl_features -lpcl_kdtree -lpcl_search \\\
                -O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations \\\
                -DUSE_FALLBACK_NURBS 2>&1 | head -20
            
            if [ -f 'MeshPreprocessing' ] && [ -f 'EdgeLineExtraction' ]; then
                echo '✓ Direct compilation successful'
                mkdir -p /opt/sfs_prep_nurbs/bin
                cp MeshPreprocessing EdgeLineExtraction /opt/sfs_prep_nurbs/bin/
                exit 0
            else
                echo '✗ Direct compilation also failed'
                exit 1
            fi
        fi
    " 2>&1 | tee "$LOG_DIR/focused_preprocessing_build.log"
    
    PREP_BUILD_RESULT=$?
    
    if [ $PREP_BUILD_RESULT -eq 0 ]; then
        echo "✓ Focused NURBS preprocessing tools built successfully!"
        
        # Convert sandbox to final container
        echo "Converting focused NURBS sandbox to SIF container..."
        $APPTAINER build --fakeroot "$NEW_CONTAINER" "$SANDBOX_DIR" 2>&1 | tee "$LOG_DIR/focused_sif_conversion.log"
        
        if [ $? -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
            echo "✓ Final focused NURBS container created successfully!"
            echo "Container location: $NEW_CONTAINER"
            echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
            
            # Test final container
            echo "Testing focused NURBS container..."
            $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
                echo 'Final focused NURBS container test:'
                echo 'Available preprocessing tools:'
                ls -la /opt/sfs_prep_nurbs/bin/ 2>/dev/null || echo 'Tools not in expected location'
                echo 'NURBS headers verification:'
                ls /usr/local/include/pcl-1.9/pcl/surface/on_nurbs/ | head -3 2>/dev/null || echo 'NURBS headers not found'
                echo 'Testing tools:'
                /opt/sfs_prep_nurbs/bin/MeshPreprocessing 2>&1 | head -3 || echo 'MeshPreprocessing test failed'
                /opt/sfs_prep_nurbs/bin/EdgeLineExtraction 2>&1 | head -3 || echo 'EdgeLineExtraction test failed'
            "
            
            echo "✅ Focused NURBS container completed!"
            echo "Usage:"
            echo "  apptainer exec $NEW_CONTAINER /opt/sfs_prep_nurbs/bin/MeshPreprocessing input.ply output.ply"
            echo "  apptainer exec $NEW_CONTAINER /opt/sfs_prep_nurbs/bin/EdgeLineExtraction input.ply edges.pcd"
            
            # Clean up sandbox
            echo "Cleaning up sandbox..."
            rm -rf "$SANDBOX_DIR"
            
        else
            echo "✗ Failed to convert focused sandbox to SIF container"
            tail -20 "$LOG_DIR/focused_sif_conversion.log"
            exit 1
        fi
    else
        echo "✗ Focused NURBS preprocessing tools build failed!"
        tail -30 "$LOG_DIR/focused_preprocessing_build.log"
        
        # Show what NURBS headers are available
        echo "Available NURBS headers:"
        $APPTAINER exec "$SANDBOX_DIR" find /usr/local/include -name '*nurbs*' 2>/dev/null || echo "No NURBS headers found"
        exit 1
    fi
else
    echo "✗ Focused NURBS headers installation failed!"
    tail -20 "$LOG_DIR/focused_nurbs_build.log"
    exit 1
fi

echo "=== Focused NURBS enhancement process completed ==="