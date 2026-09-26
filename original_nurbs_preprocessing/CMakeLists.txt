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

# Edge-line ordering, in its own translation unit so the pipeline and the
# tests compile the same code (SfS++ ticket 01). See edge_line_ordering.h.
set(EDGE_LINE_ORDERING edge_line_ordering.cpp)

# Build both original and headless versions
add_executable(MeshPreprocessing mesh_processing.cpp)
add_executable(EdgeLineExtraction edgeline_extraction.cpp ${PROJ_DEP})
add_executable(MeshPreprocessingHeadless mesh_processing_headless.cpp)
add_executable(EdgeLineExtractionHeadless edgeline_extraction_headless.cpp ${EDGE_LINE_ORDERING} ${PROJ_DEP})
add_executable(EdgeLineExtractionLegacy edgeline_extraction_backup.cpp ${PROJ_DEP})

# Link Libraries
target_link_libraries(MeshPreprocessing ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtraction ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(MeshPreprocessingHeadless ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtractionHeadless ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)
target_link_libraries(EdgeLineExtractionLegacy ${PCL_LIBRARIES} ${CGAL_LIBRARIES} stdc++fs)

# Build all targets
add_custom_target(all_targets ALL DEPENDS MeshPreprocessing EdgeLineExtraction MeshPreprocessingHeadless EdgeLineExtractionHeadless EdgeLineExtractionLegacy)

# ---------------------------------------------------------------------
# Tests (SfS++ ticket 01)
#
# One CTest entry per test, so a failure names the property that broke
# rather than reporting one aggregate "tests failed".
#
# The tests are registered DISABLED_ on purpose. They assert the contract
# from the paper, and today's implementation does not meet it -- the
# ordering is a non-local nearest-neighbour chain that stalls on
# duplicate-heavy boundaries. Keeping them enabled would leave the suite
# permanently red and train people to ignore it. Disabled, they stay
# armed and visible: `ctest` lists them, and tests/README.md records the
# failures that were actually observed. Ticket 02 removes the prefix on
# the tests it turns green; each prefix is removed by the ticket that
# earns it, never in a batch.
#
# The test target compiles edge_line_ordering.cpp -- the SAME file the
# pipeline compiles. A test that could pass against different code than
# production runs would be worthless here, which is the whole reason
# that code was lifted out of the 137 KB pipeline translation unit.
# ---------------------------------------------------------------------
enable_testing()

add_executable(test_edge_line_ordering tests/test_edge_line_ordering.cpp ${EDGE_LINE_ORDERING})
target_link_libraries(test_edge_line_ordering ${PCL_LIBRARIES} stdc++fs)

add_test(NAME DISABLED_edge_line_ordering_clean_rim   COMMAND test_edge_line_ordering clean-rim)
add_test(NAME DISABLED_edge_line_ordering_eroded_rim COMMAND test_edge_line_ordering eroded-rim)
add_test(NAME DISABLED_edge_line_ordering_no_revisit COMMAND test_edge_line_ordering no-revisit)

# Lightweight OBJ -> PCD converter (header-only tinyobjloader, ASCII PCD output)
add_executable(ObjToPcd tools/obj_to_pcd.cpp)

# Utility: enrich existing xyz-only breaklines with normals + segment header
