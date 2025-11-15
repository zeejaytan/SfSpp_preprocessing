#!/bin/bash

# Patch PCL 1.9.1 to work with VTK 9.1 - fix CMake compatibility
echo "=== Patched NURBS Solution: Fix PCL 1.9.1 for VTK 9.1 ==="

# Download PCL 1.9.1 and apply VTK 9.1 compatibility patches
cat > pcl_vtk91_patches.patch << 'EOF'
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -360,7 +360,7 @@ if(WITH_VTK)
   endif()
   
   if(VTK_FOUND)
-    find_package(VTK REQUIRED COMPONENTS vtkCommonCore vtkRenderingCore vtkFiltersCore)
+    find_package(VTK REQUIRED COMPONENTS CommonCore RenderingCore FiltersCore)
     if(VTK_VERSION VERSION_LESS 6.0)
       message(FATAL_ERROR "VTK 6.0 or greater is required.")
     endif()
EOF

echo "This approach patches PCL 1.9.1 CMake scripts to work with VTK 9.1 API"
echo "Would fix the root cause: CMake module compatibility"