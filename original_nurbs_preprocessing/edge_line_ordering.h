// Edge-line ordering: the seam SfS++ ticket 01 exists to make testable.
//
// Lifted verbatim out of edgeline_extraction_headless.cpp so that the
// pipeline and the tests compile the SAME code. If this were copied into
// a test file the test could pass against code production never runs,
// which is the one thing the seam must not allow.
//
// The function keeps its historical name. "getPointsInSequence" is a poor
// name for what it does, but renaming it is a refactor and belongs in
// review, not in the ticket that creates the seam -- keeping the move
// mechanical is what makes it provably behaviour-preserving.
//
// WHAT IT IS SUPPOSED TO DO (SfS++ paper, arXiv 2502.13986, section
// IV-B1 "Edge line extraction and segmentation"):
//   "The resulting edge line points are reordered counter-clockwise using
//    their normals and a voting algorithm."
//
// WHAT IT ACTUALLY DOES: a nearest-neighbour chain that, at each step,
// appends the first unused point among K nearest neighbours, with
// K = max(5, min(50, boundary_size/10)).
//
// THE DEFECT, AS MEASURED (ticket 01)
// The chain truncates. It stops as soon as every one of its K candidates is
// already visited, and the outer loop then spins without appending
// anything. Two properties of the input decide whether that happens:
//
//   1. DENSITY CONTRAST. Where part of the rim is sampled at least K times
//      denser than the rim's median spacing, the K-nearest window reaches
//      only ground already covered. The real Juglet cloud varies 20x in
//      local spacing (0.096-1.96 mm) and 85% of its points sit in that
//      regime. Result: 59 points in, 9 out, 2.1 mm traced of a 36.8 mm
//      rim -- 6% of the rim.
//   2. OFF-PLANE SCATTER. Where points scatter further off the rim than
//      the local spacing, the neighbourhood stops being a 1-D curve and
//      the same saturation occurs. Reproduced independently of (1).
//
// A walk that stops early takes SMALL steps; it does not take large ones.
// So this defect is invisible to any check on step size, and was invisible
// for exactly that reason.
//
// A NOTE ON A NUMBER THAT DOES NOT BELONG HERE: the "10-24 mm internal
// jumps, 0.27-2.15x traced length" figures quoted in the old ticket 02
// were measured on the EMITTED breakline files, after B-spline resampling
// and 200-point padding. They describe a later stage and say nothing about
// this function. They were previously quoted in this header as if they
// did; that was wrong, and no test here asserts on them.
//
// The ordering step IS the paper's: "the resulting edge line points are
// reordered counter-clockwise using their normals and a voting algorithm"
// (arXiv 2502.13986 section IV-B1). The released code never had it.
// Tickets 02 and 03 replace the body; this ticket only makes it visible.

#pragma once

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>

// Orders an unordered boundary cloud into a traversal.
//
// Contract, as the method specifies it:
//   - every input point is visited at most once
//   - consecutive output points are adjacent along the rim, so no step
//     dwarfs the typical spacing
//   - the traversal direction is the one the per-point normal vote
//     selects
//
// The current implementation satisfies none of these in general. The
// tests in tests/ pin the current behaviour and are expected to fail
// until tickets 02 and 03 land; see tests/README.md.
void getPointsInSequence(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud,
                         pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced);

// True when an exactly-equal point is already present in the cloud.
// Note the exact float comparison: near-duplicates are NOT equal. Ticket
// 02 attacks that at the call site by removing near-duplicates first,
// rather than by changing this predicate, so that the "visited" test
// stays exact.
bool pointExistsInCLoud(pcl::PointXYZ pt, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud);
