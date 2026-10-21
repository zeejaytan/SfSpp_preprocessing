#include <iostream>
#include <iomanip>
#include <cmath>
#include <time.h>
#include <vector>
#include <fstream>
#include <algorithm>
#include <Eigen/Dense>
#include <Eigen/Core>
#include <boost/thread/thread.hpp>
#include <pcl/common/common_headers.h>
#include <pcl/features/normal_3d.h>
#include <pcl/io/pcd_io.h>
#include <pcl/io/obj_io.h>
#include <pcl/console/parse.h>
#include <pcl/common/transforms.h>
#include <experimental/filesystem>
#include <string>
#include <filesystem>
#include <stdio.h>
#include <cstdlib>
#include <pcl/filters/uniform_sampling.h>
#include <chrono>
#include <thread>
#include <pcl/point_types.h>
#include <pcl/io/ply_io.h>
#include <pcl/surface/convex_hull.h>
#include <pcl/surface/concave_hull.h>
#include <pcl/common/common.h>
#include <pcl/sample_consensus/sac_model_plane.h>
#include <pcl/filters/project_inliers.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/segmentation/region_growing.h>
#include <pcl/segmentation/conditional_euclidean_clustering.h>
#include <pcl/console/time.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/features/boundary.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/surface/gp3.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <pcl/features/moment_of_inertia_estimation.h>
#include <pcl/filters/radius_outlier_removal.h>
#include <pcl/segmentation/extract_polygonal_prism_data.h>
#include <pcl/features/normal_3d_omp.h>
#include <pcl/filters/conditional_removal.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/segmentation/impl/extract_clusters.hpp>
#include <pcl/features/don.h>
#include <boost/algorithm/string.hpp>
int main() {
#ifdef qh
#pragma message("MACRO qh DEFINED")
#endif
#ifdef queue
#pragma message("MACRO queue DEFINED")
#endif
#ifdef cur
#pragma message("MACRO cur DEFINED")
#endif
#ifdef region
#pragma message("MACRO region DEFINED")
#endif
#ifdef order
#pragma message("MACRO order DEFINED")
#endif
#ifdef N
#pragma message("MACRO N DEFINED")
#endif
#ifdef seed
#pragma message("MACRO seed DEFINED")
#endif
#ifdef mean
#pragma message("MACRO mean DEFINED")
#endif
    return 0;
}
