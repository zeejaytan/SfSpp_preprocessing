// See boundary_filter.h. Called by the edgeline pipeline (ticket 05) and
// by tests/test_boundary_filter.cpp -- one implementation, both callers.

#include "boundary_filter.h"

#include <pcl/filters/radius_outlier_removal.h>

#include <iostream>

std::size_t filterBoundaryNoise(
    const pcl::PointCloud<pcl::PointXYZ>::Ptr &in,
    pcl::PointCloud<pcl::PointXYZ>::Ptr &out,
    double radius, int minNeighbors)
{
    const std::size_t n_in = in ? in->points.size() : 0;
    if (n_in == 0) {
        out->points.clear();
        std::cout << "[SFS-T05] noise filter: 0 kept / 0 removed of 0" << std::endl;
        return 0;
    }
    pcl::RadiusOutlierRemoval<pcl::PointXYZ> outrem;
    outrem.setInputCloud(in);
    outrem.setRadiusSearch(radius);
    outrem.setMinNeighborsInRadius(minNeighbors);
    // Removals vanish (not NaN-kept): NaNs would poison the ordering walk.
    outrem.setKeepOrganized(false);
    outrem.filter(*out);
    const std::size_t n_kept = out->points.size();
    std::cout << "[SFS-T05] noise filter: " << n_kept << " kept / "
              << (n_in - n_kept) << " removed of " << n_in << std::endl;
    return n_kept;
}
