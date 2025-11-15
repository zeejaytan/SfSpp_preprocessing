#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/features/normal_3d.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <iostream>

int main(int argc, char** argv)
{
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " input.pcd output.pcd" << std::endl;
        return -1;
    }

    // Load point cloud
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    
    if (pcl::io::loadPCDFile<pcl::PointXYZ>(argv[1], *cloud) == -1) {
        std::cerr << "Error: Could not read file " << argv[1] << std::endl;
        return -1;
    }
    
    std::cout << "Loaded " << cloud->points.size() << " points from " << argv[1] << std::endl;

    // Create point cloud with normals
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_with_normals(new pcl::PointCloud<pcl::PointNormal>);

    // Estimate normals
    pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> ne;
    pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
    pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>());

    ne.setInputCloud(cloud);
    ne.setSearchMethod(tree);
    ne.setKSearch(20);  // Use 20 nearest neighbors for normal estimation
    ne.compute(*normals);

    std::cout << "Computed normals for " << normals->points.size() << " points" << std::endl;

    // Combine points and normals
    cloud_with_normals->points.resize(cloud->points.size());
    for (size_t i = 0; i < cloud->points.size(); ++i) {
        cloud_with_normals->points[i].x = cloud->points[i].x;
        cloud_with_normals->points[i].y = cloud->points[i].y;
        cloud_with_normals->points[i].z = cloud->points[i].z;
        cloud_with_normals->points[i].normal_x = normals->points[i].normal_x;
        cloud_with_normals->points[i].normal_y = normals->points[i].normal_y;
        cloud_with_normals->points[i].normal_z = normals->points[i].normal_z;
        cloud_with_normals->points[i].curvature = normals->points[i].curvature;
    }

    cloud_with_normals->width = cloud->width;
    cloud_with_normals->height = cloud->height;
    cloud_with_normals->is_dense = cloud->is_dense;

    // Save the result
    if (pcl::io::savePCDFileASCII(argv[2], *cloud_with_normals) == -1) {
        std::cerr << "Error: Could not save file " << argv[2] << std::endl;
        return -1;
    }

    std::cout << "Saved " << cloud_with_normals->points.size() << " points with normals to " << argv[2] << std::endl;
    return 0;
}