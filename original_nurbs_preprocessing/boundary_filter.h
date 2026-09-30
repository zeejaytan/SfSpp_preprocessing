// Boundary noise filter seam (ticket 05: the paper's noise/outlier filter).
//
// SEAM: filterBoundaryNoise(in, out, radius, minNeighbors) -- radius
// outlier removal on a boundary cloud. The pipeline calls this exact
// function, so the test exercises production code, not a replica.
// keepOrganized=false: removals vanish instead of becoming NaNs (NaNs
// would poison the nearest-neighbour ordering walk downstream).
//
// The fixture is synthetic but principled: a 15mm-radius circle (the rim
// the ordering walk must traverse) plus one gross outlier 100mm off it.
// A filter that cannot drop that point while keeping the circle cannot
// implement the paper's outlier step at all.
//
// No test framework: the container has no test dependency. Needs PCL
// (RadiusOutlierRemoval), same as the ordering test binary.

#pragma once

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>

#include <cstddef>

// Drops points with fewer than minNeighbors inside radius. Returns the
// kept count. Logs kept/removed to stdout ([SFS-T05]) so a run that
// collapses most of its boundary is visible rather than silent.
std::size_t filterBoundaryNoise(
    const pcl::PointCloud<pcl::PointXYZ>::Ptr &in,
    pcl::PointCloud<pcl::PointXYZ>::Ptr &out,
    double radius, int minNeighbors);
