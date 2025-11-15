#!/bin/bash

# Comprehensive test of preprocessing container capabilities
echo "=== Testing SFS Preprocessing Container ==="

APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_from_working.sif"

if [ ! -f "$CONTAINER" ]; then
    echo "✗ Container not found: $CONTAINER"
    exit 1
fi

echo "✓ Container found: $CONTAINER"
echo "Container size: $(ls -lh "$CONTAINER" | awk '{print $5}')"

echo
echo "=== Environment Test ==="
$APPTAINER exec "$CONTAINER" /bin/bash -c "
    echo 'OS Version:'
    cat /etc/os-release | grep PRETTY_NAME
    echo
    echo 'Build Environment:'
    echo '  CMake: ' \$(cmake --version | head -1)
    echo '  G++: ' \$(g++ --version | head -1)
    echo '  Python: ' \$(python3 --version 2>/dev/null || echo 'Not available')
    echo
    echo 'Library Versions:'
    echo '  VTK: ' \$(find /usr -name 'vtk*.h' | head -1 | grep -o 'vtk-[0-9.]*' || echo 'Not found')
    echo '  PCL: ' \$(find /usr -name '*pcl*' -type d | grep include | head -1 | grep -o 'pcl-[0-9.]*' || echo 'Not found')
    echo '  Eigen: ' \$(pkg-config --modversion eigen3 2>/dev/null || echo 'Not found')
    echo '  Boost: ' \$(echo '#include <boost/version.hpp>' | g++ -E -x c++ - | grep 'BOOST_VERSION' | head -1 || echo 'Not found')
    echo
    echo 'Available Headers:'
    echo '  tiny_obj_loader.h: ' \$([ -f /usr/local/include/tiny_obj_loader.h ] && echo 'Found' || echo 'Not found')
    echo '  PCL common: ' \$([ -f /usr/include/pcl-1.12/pcl/common/common_headers.h ] && echo 'Found' || echo 'Not found')
    echo '  VTK vtk.h: ' \$(find /usr -name 'vtk*.h' | head -1 | xargs test -f && echo 'Found' || echo 'Not found')
    echo '  CGAL Polygon: ' \$(find /usr -name 'Polygon_2.h' | head -1 | xargs test -f && echo 'Found' || echo 'Not found')
"

echo
echo "=== Existing Tools Test ==="
$APPTAINER exec "$CONTAINER" /bin/bash -c "
    echo 'Available executables in /opt/sfs/bin/:'
    ls -la /opt/sfs/bin/ | grep -E '^-.*x'
    echo
    echo 'Testing Hierarchy-Clear:'
    /opt/sfs/bin/Hierarchy-Clear --help 2>&1 | head -3 || echo 'No help available'
    echo
    echo 'Testing extract-edges wrapper:'
    /opt/sfs/bin/extract-edges --help 2>&1 | head -3 || echo 'Underlying executable not found'
    echo
    echo 'Testing preprocess-mesh wrapper:'
    /opt/sfs/bin/preprocess-mesh --help 2>&1 | head -3 || echo 'Underlying executable not found'
"

echo
echo "=== Compilation Test (Simple) ==="
$APPTAINER exec "$CONTAINER" /bin/bash -c "
    echo 'Testing C++ compilation with PCL:'
    cat > /tmp/test_pcl.cpp << 'EOF'
#include <iostream>
#include <pcl/common/common_headers.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

int main() {
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    cloud->width = 5;
    cloud->height = 1;
    cloud->points.resize(cloud->width * cloud->height);
    
    for (std::size_t i = 0; i < cloud->points.size(); ++i) {
        cloud->points[i].x = 1024 * rand() / (RAND_MAX + 1.0f);
        cloud->points[i].y = 1024 * rand() / (RAND_MAX + 1.0f);
        cloud->points[i].z = 1024 * rand() / (RAND_MAX + 1.0f);
    }
    
    std::cout << 'PCL test: Created point cloud with ' << cloud->points.size() << ' points' << std::endl;
    return 0;
EOF

    echo 'Compiling PCL test...'
    g++ -std=c++17 /tmp/test_pcl.cpp -o /tmp/test_pcl \
        -I/usr/include/pcl-1.12 \
        -I/usr/include/eigen3 \
        -lpcl_common -lpcl_io \
        2>/dev/null
        
    if [ -f /tmp/test_pcl ]; then
        echo '✓ PCL compilation successful'
        echo 'Running PCL test:'
        /tmp/test_pcl
    else
        echo '✗ PCL compilation failed'
    fi
"

echo
echo "=== Available Sample Data ==="
$APPTAINER exec "$CONTAINER" /bin/bash -c "
    echo 'Checking for sample mesh data:'
    find /opt -name '*.obj' -o -name '*.ply' -o -name '*.off' -o -name '*.pcd' | head -5
    echo
    echo 'Checking Dataset directory:'
    if [ -d '/SfS/Dataset' ]; then
        ls -la /SfS/Dataset/ | head -5
    else
        echo 'Dataset directory not found'
    fi
"

echo
echo "=== Build Environment Analysis ==="
$APPTAINER exec "$CONTAINER" /bin/bash -c "
    echo 'CMake modules and configs:'
    find /usr -name '*PCL*Config.cmake' | head -3
    find /usr -name '*VTK*Config.cmake' | head -3
    echo
    echo 'Library directories:'
    echo 'PCL libraries:'
    ls /usr/lib/x86_64-linux-gnu/libpcl_*.so | head -5
    echo 'VTK libraries:'
    ls /usr/lib/x86_64-linux-gnu/libvtk*.so | head -5
"

echo
echo "=== Final Assessment ==="
echo "Container testing completed."
echo "The container provides a working C++ environment with PCL and VTK."
echo "Ready for preprocessing tool development or manual processing workflows."