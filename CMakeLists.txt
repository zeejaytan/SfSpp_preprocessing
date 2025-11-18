cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project(Pre-processing)

# C++17 Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Ignore old-style cast warnings
add_compile_options(-Wno-old-style-cast)

# PCL
find_package(PCL 1.9.1 REQUIRED)
find_package(PCL 1.9.1 REQUIRED COMPONENTS common io)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

# Add current directory for tiny_obj_loader.h
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# CGAL
find_package(CGAL REQUIRED)
include_directories(${CGAL_INCLUDE_DIRS})
link_directories(${CGAL_LIBRARY_DIRS})
add_definitions(${CGAL_DEFINITIONS})

if (MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj")
  add_definitions(-D _CRT_SECURE_NO_WARNINGS)
endif()

file(GLOB PROJ_DEP "alglib/src/*.cpp" "alglib/src/*.h")

# Build both original and headless versions
# add_executable(MeshPreprocessing mesh_processing.cpp)  # Commented out - file doesn't exist
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})
add_executable(MeshPreprocessingHeadless mesh_processing_headless.cpp)
add_executable(EdgeLineExtractionHeadless edgeline_extraction_headless.cpp ${PROJ_DEP})
add_executable(EdgeLineExtractionLegacy edgeline_extraction_backup.cpp ${PROJ_DEP})
add_executable(AxisExtractionHeadless axis_extraction_cpp.cpp)

# Link Libraries
# target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)  # Commented out - target doesn't exist
target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(MeshPreprocessingHeadless ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtractionHeadless ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtractionLegacy ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(AxisExtractionHeadless stdc++fs)

# Build all targets
add_custom_target(all_targets ALL DEPENDS EdgeLineExtraction MeshPreprocessingHeadless EdgeLineExtractionHeadless EdgeLineExtractionLegacy AxisExtractionHeadless)

# Lightweight OBJ -> PCD converter (header-only tinyobjloader, ASCII PCD output)
add_executable(ObjToPcd tools/obj_to_pcd.cpp)

# Utility: enrich existing xyz-only breaklines with normals + segment header
