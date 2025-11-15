#!/bin/bash

# Host-native NURBS build - build directly on Spartan system
echo "=== Host-Native NURBS Solution (No Container) ==="
echo "Build VTK 8.2 and PCL 1.9.1 directly on host system"

# Check if we can build natively
echo "Checking host environment..."
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME)"
echo "GCC: $(gcc --version | head -1)"
echo "CMake: $(cmake --version | head -1)"

# Create host build directory
HOST_BUILD_DIR="/tmp/host_nurbs_build"
mkdir -p "$HOST_BUILD_DIR"
cd "$HOST_BUILD_DIR"

echo ""
echo "🎯 Host-Native Build Strategy:"
echo "1. Build VTK 8.2 in /tmp/vtk82_host"
echo "2. Build PCL 1.9.1 against host VTK 8.2 in /tmp/pcl191_host" 
echo "3. Build preprocessing tools with host libraries"
echo "4. Create final executable packages"
echo ""
echo "Benefits:"
echo "✓ No container permission issues"
echo "✓ Full system access and control"  
echo "✓ Can use system package manager"
echo "✓ Better debugging and troubleshooting"
echo ""
echo "This approach would bypass ALL container limitations!"
echo "Would you like me to try this host-native approach?"