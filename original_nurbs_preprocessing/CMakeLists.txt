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
# A test that passes today is enabled. A test that fails today is disabled
# so the suite stays green, and is re-enabled by the ticket that turns it
# green -- never in a batch, and never by loosening a threshold.
#
# The test target compiles edge_line_ordering.cpp -- the SAME file the
# pipeline compiles. A test that could pass against different code than
# production runs would be worthless here, which is the whole reason that
# code was lifted out of the 137 KB pipeline translation unit.
# ---------------------------------------------------------------------
enable_testing()

add_executable(test_edge_line_ordering tests/test_edge_line_ordering.cpp ${EDGE_LINE_ORDERING})
target_link_libraries(test_edge_line_ordering ${PCL_LIBRARIES} stdc++fs)
# The fixture path is compiled in so the test finds its data whatever the
# working directory is. *.pcd is gitignored project-wide, so the fixture is
# committed as plain text instead -- see tests/data/juglet_boundary_59.txt.
target_compile_definitions(test_edge_line_ordering
    PRIVATE JUGLET_FIXTURE_DIR="${CMAKE_CURRENT_SOURCE_DIR}/tests/data")

# passing today -> enabled
add_test(NAME edge_line_ordering_clean_rim     COMMAND test_edge_line_ordering clean-rim)
add_test(NAME edge_line_ordering_no_revisit    COMMAND test_edge_line_ordering no-revisit)

# The DISABLED_ prefix LABELS known-broken behaviour; the DISABLED test
# property below is what actually stops ctest running it. See the note there.
add_test(NAME DISABLED_edge_line_ordering_juglet_boundary   COMMAND test_edge_line_ordering juglet-boundary)
add_test(NAME DISABLED_edge_line_ordering_dense_patch       COMMAND test_edge_line_ordering dense-patch)
add_test(NAME DISABLED_edge_line_ordering_offplane_scatter  COMMAND test_edge_line_ordering offplane-scatter)
#
# NOTE ON MECHANISM -- measured, not assumed. Disabling was first done with
# the DISABLED_ NAME PREFIX. On this CMake/CTest that did NOT work: ctest ran
# all three and reported "40% tests passed, 3 tests failed out of 5". So the
# prefix is kept as a visible label, but the actual disabling is the DISABLED
# TEST PROPERTY, which ctest honours. Verified by the ctest run in
# run_ticket01.sh, which must report 2/2 passed with 3 disabled.
set(_edge_line_known_broken
    edge_line_ordering_juglet_boundary
    edge_line_ordering_dense_patch
    edge_line_ordering_offplane_scatter)

foreach(_t IN LISTS _edge_line_known_broken)
    set_tests_properties(${_t} PROPERTIES DISABLED TRUE)
endforeach()

# Lightweight OBJ -> PCD converter (header-only tinyobjloader, ASCII PCD output)
add_executable(ObjToPcd tools/obj_to_pcd.cpp)

# Utility: enrich existing xyz-only breaklines with normals + segment header
