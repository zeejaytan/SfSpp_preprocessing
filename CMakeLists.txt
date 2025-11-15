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

# Build both MeshPreprocessing and EdgeLineExtraction (geometric segmentation fix)
add_executable(MeshPreprocessing mesh_processing.cpp)
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})

# Link Libraries
target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
