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
// K = max(5, min(50, boundary_size/10)). That rule is non-local. On a
// boundary cloud containing near-duplicate points it consumes a tight
// cluster and then stalls, because every one of its K candidates is
// already used. Measured on the Juglet: traced length 0.27-2.15x the rim
// it should cover, internal jumps of 10-24 mm against a 0.3 mm median
// step, one sherd reduced to a 3.6 mm stub.
//
// This ordering step is the paper's, and the released code never had it.
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
