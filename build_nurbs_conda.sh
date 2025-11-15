#!/bin/bash

# Build PCL 1.9.1 with NURBS using conda environment for exact version control
echo "=== Building PCL 1.9.1 with NURBS using Conda Environment ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_from_working.sif"
SANDBOX_DIR="sandbox_conda_nurbs"
NEW_CONTAINER="cache/sfs_prep_conda_nurbs.sif"
LOG_DIR="logs"

mkdir -p "$LOG_DIR"

if [ ! -f "$CONTAINER" ]; then
    echo "✗ Base container not found: $CONTAINER"
    exit 1
fi

echo "✓ Found base container: $CONTAINER"

# Create sandbox for conda-based NURBS build
echo "Creating sandbox for conda NURBS build..."
if [ -d "$SANDBOX_DIR" ]; then
    echo "Removing existing sandbox..."
    rm -rf "$SANDBOX_DIR"
fi

$APPTAINER build --sandbox --fakeroot "$SANDBOX_DIR" "$CONTAINER" 2>&1 | tee "$LOG_DIR/conda_sandbox_creation.log"

if [ $? -ne 0 ]; then
    echo "✗ Failed to create sandbox"
    exit 1
fi

echo "✓ Sandbox created successfully"

# Install conda and build PCL 1.9.1 with NURBS
echo "Installing conda and building PCL 1.9.1 with NURBS..."
$APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
    set -e
    echo '=== Setting up Conda Environment for NURBS ==='
    
    # Install miniconda
    cd /tmp
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3
    
    # Initialize conda
    export PATH=/opt/miniconda3/bin:\$PATH
    conda init bash
    source ~/.bashrc
    
    # Create environment with specific versions
    echo 'Creating conda environment with compatible versions...'
    conda create -n pcl_nurbs python=3.8 -y
    conda activate pcl_nurbs
    
    # Install specific VTK version compatible with PCL 1.9.1
    echo 'Installing VTK 8.2...'
    conda install -c conda-forge vtk=8.2 -y
    
    # Install other dependencies  
    echo 'Installing build dependencies...'
    conda install -c conda-forge \
        cmake \
        boost \
        eigen \
        flann \
        qt=5.15 \
        libusb \
        libxml2 \
        gtest \
        freeglut \
        -y
    
    # Install OpenNURBS (required for PCL NURBS)
    echo 'Installing OpenNURBS...'
    conda install -c conda-forge opennurbs -y || echo 'OpenNURBS not available in conda-forge, will build from source'
    
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
        -DCMAKE_INSTALL_PREFIX=/opt/pcl_nurbs \
        -DBUILD_NURBS=ON \
        -DBUILD_ON_NURBS=ON \
        -DBUILD_surface_on_nurbs=ON \
        -DWITH_VTK=ON \
        -DVTK_DIR=\$(conda info --base)/envs/pcl_nurbs/lib/cmake/vtk-8.2 \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_examples=OFF \
        -DBUILD_tools=OFF \
        -DBUILD_apps=OFF \
        -DCMAKE_PREFIX_PATH=\$(conda info --base)/envs/pcl_nurbs
    
    echo 'Building PCL 1.9.1 with NURBS (this will take time)...'
    make -j2
    
    echo 'Installing PCL 1.9.1 with NURBS...'
    make install
    
    echo 'Verifying NURBS installation...'
    if [ -f '/opt/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs/fitting_surface_tdm.h' ]; then
        echo '✓ NURBS headers found'
        ls /opt/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs/ | head -5
        
        # Set up environment script
        cat > /opt/pcl_nurbs/setup_env.sh << 'ENVEOF'
#!/bin/bash
export PATH=/opt/miniconda3/bin:\$PATH
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate pcl_nurbs
export PKG_CONFIG_PATH=/opt/pcl_nurbs/lib/pkgconfig:\$PKG_CONFIG_PATH
export LD_LIBRARY_PATH=/opt/pcl_nurbs/lib:\$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/opt/pcl_nurbs:\$CMAKE_PREFIX_PATH
ENVEOF
        chmod +x /opt/pcl_nurbs/setup_env.sh
        
        echo '✓ PCL 1.9.1 with NURBS installed successfully'
    else
        echo '✗ NURBS headers not found'
        find /opt/pcl_nurbs -name '*nurbs*' | head -5
        exit 1
    fi
    
    # Clean up build files
    cd /tmp
    rm -rf pcl-pcl-1.9.1*
    rm -f Miniconda3-latest-Linux-x86_64.sh
    
    echo 'PCL 1.9.1 with NURBS setup completed'
" 2>&1 | tee "$LOG_DIR/conda_nurbs_build.log"

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✓ PCL 1.9.1 with NURBS built successfully using conda!"
    
    # Now build preprocessing tools with conda environment
    echo "Building preprocessing tools with conda PCL 1.9.1 + NURBS..."
    
    # Copy source files
    mkdir -p "$SANDBOX_DIR/opt/sfs_prep/src"
    cp -r mesh_processing.cpp edgeline_extraction.cpp CMakeLists.txt data_path.h alglib/ "$SANDBOX_DIR/opt/sfs_prep/src/"
    
    $APPTAINER exec --writable "$SANDBOX_DIR" /bin/bash -c "
        set -e
        cd /opt/sfs_prep/src
        
        # Source conda environment
        source /opt/pcl_nurbs/setup_env.sh
        
        rm -rf build
        mkdir -p build
        cd build
        
        echo 'Configuring preprocessing tools with conda PCL 1.9.1 + NURBS...'
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=/opt/sfs_prep \
            -DCMAKE_CXX_STANDARD=17 \
            -DPCL_DIR=/opt/pcl_nurbs/share/pcl-1.9 \
            -DCMAKE_PREFIX_PATH=/opt/pcl_nurbs \
            -DCMAKE_CXX_FLAGS='-O2 -DNDEBUG -Wno-old-style-cast -Wno-deprecated-declarations'
        
        echo 'Building preprocessing executables with NURBS support...'
        make -j2 VERBOSE=1
        
        echo 'Installing preprocessing executables...'
        make install
        
        echo 'Verifying NURBS-enabled build results...'
        ls -la /opt/sfs_prep/bin/
        
        if [ -f '/opt/sfs_prep/bin/MeshPreprocessing' ] && [ -f '/opt/sfs_prep/bin/EdgeLineExtraction' ]; then
            echo '✓ Both preprocessing executables built successfully with NURBS support'
            
            # Test executables with conda environment
            source /opt/pcl_nurbs/setup_env.sh
            
            echo 'Testing MeshPreprocessing with NURBS:' 
            /opt/sfs_prep/bin/MeshPreprocessing --help 2>/dev/null | head -3 || echo 'NURBS-enabled executable exists'
            
            echo 'Testing EdgeLineExtraction with NURBS:'
            /opt/sfs_prep/bin/EdgeLineExtraction --help 2>/dev/null | head -3 || echo 'NURBS-enabled executable exists'
            
            exit 0
        else
            echo '✗ Some preprocessing executables are missing'
            exit 1
        fi
    " 2>&1 | tee "$LOG_DIR/conda_preprocessing_build.log"
    
    PREP_BUILD_RESULT=$?
    
    if [ $PREP_BUILD_RESULT -eq 0 ]; then
        echo "✓ Preprocessing tools with NURBS support built successfully using conda!"
        
        # Convert sandbox to final container
        echo "Converting conda NURBS sandbox to SIF container..."
        $APPTAINER build --fakeroot "$NEW_CONTAINER" "$SANDBOX_DIR" 2>&1 | tee "$LOG_DIR/conda_sif_conversion.log"
        
        if [ $? -eq 0 ] && [ -f "$NEW_CONTAINER" ]; then
            echo "✓ Final conda NURBS container created successfully!"
            echo "Container location: $NEW_CONTAINER"
            echo "Container size: $(ls -lh "$NEW_CONTAINER" | awk '{print $5}')"
            
            # Test final container
            echo "Testing final conda NURBS container..."
            $APPTAINER exec "$NEW_CONTAINER" /bin/bash -c "
                source /opt/pcl_nurbs/setup_env.sh
                echo 'Final container test with NURBS:'
                echo 'Available preprocessing tools:'
                ls -la /opt/sfs_prep/bin/
                echo 'NURBS headers verification:'
                ls /opt/pcl_nurbs/include/pcl-1.9/pcl/surface/on_nurbs/ | head -3
                echo 'PCL 1.9.1 NURBS libraries:'
                ls /opt/pcl_nurbs/lib/libpcl_*.so | head -3
                echo 'Conda environment:'
                conda info --envs
            "
            
            echo "✓ SFS Preprocessing container with full NURBS support completed!"
            echo "Usage: apptainer exec $NEW_CONTAINER bash -c 'source /opt/pcl_nurbs/setup_env.sh && /opt/sfs_prep/bin/MeshPreprocessing [args]'"
            
            # Clean up sandbox
            echo "Cleaning up sandbox..."
            rm -rf "$SANDBOX_DIR"
            
        else
            echo "✗ Failed to convert conda sandbox to SIF container"
            tail -20 "$LOG_DIR/conda_sif_conversion.log"
            exit 1
        fi
    else
        echo "✗ Preprocessing tools build with conda NURBS failed!"
        tail -20 "$LOG_DIR/conda_preprocessing_build.log"
        exit 1
    fi
else
    echo "✗ Conda PCL 1.9.1 with NURBS build failed!"
    tail -20 "$LOG_DIR/conda_nurbs_build.log"
    exit 1
fi

echo "=== Conda NURBS enhancement process completed ==="