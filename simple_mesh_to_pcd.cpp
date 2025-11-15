#include <pcl/io/obj_io.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/filters/uniform_sampling.h>
#include <iostream>

// OPTIMIZED: OBJ → PCD (XYZ only) - let CGAL handle normals
int main(int argc, char** argv)
{
    if (argc < 3) {
        std::cout << "Usage: " << argv[0] << " input.obj output.pcd [max_points]" << std::endl;
        std::cout << "Generates XYZ-only PCD (normals computed by CGAL in pipeline)" << std::endl;
        return -1;
    }

    std::string obj_file = argv[1];
    std::string pcd_file = argv[2];
    int max_points = (argc > 3) ? std::atoi(argv[3]) : 1000000;

    std::cout << "Loading OBJ mesh: " << obj_file << std::endl;

    // Load OBJ mesh
    pcl::PolygonMesh mesh;
    if (pcl::io::loadOBJFile(obj_file, mesh) == -1) {
        std::cerr << "Error loading OBJ file: " << obj_file << std::endl;
        return -1;
    }

    // Convert to point cloud (XYZ only)
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::fromPCLPointCloud2(mesh.cloud, *cloud);
    
    std::cout << "Original mesh points: " << cloud->size() << std::endl;

    // Sample to target count if needed
    if (cloud->size() > max_points) {
        pcl::PointCloud<pcl::PointXYZ>::Ptr sampled(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::UniformSampling<pcl::PointXYZ> uniform_sampling;
        uniform_sampling.setInputCloud(cloud);
        
        // Calculate sampling radius for target point count
        float sampling_radius = 0.001f;
        uniform_sampling.setRadiusSearch(sampling_radius);
        uniform_sampling.filter(*sampled);
        
        // Adjust if needed
        while (sampled->size() > max_points && sampling_radius < 1.0f) {
            sampling_radius *= 1.5f;
            uniform_sampling.setRadiusSearch(sampling_radius);
            uniform_sampling.filter(*sampled);
        }
        
        cloud = sampled;
        std::cout << "Sampled to: " << cloud->size() << " points" << std::endl;
    }

    // Remove invalid points
    pcl::PointCloud<pcl::PointXYZ>::Ptr valid_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    for (const auto& point : cloud->points) {
        if (std::isfinite(point.x) && std::isfinite(point.y) && std::isfinite(point.z)) {
            valid_cloud->points.push_back(point);
        }
    }
    valid_cloud->width = valid_cloud->size();
    valid_cloud->height = 1;
    valid_cloud->is_dense = true;

    // Save as simple XYZ PCD
    if (pcl::io::savePCDFileASCII(pcd_file, *valid_cloud) == -1) {
        std::cerr << "Error saving PCD file: " << pcd_file << std::endl;
        return -1;
    }

    std::cout << "SUCCESS: Generated " << pcd_file << " with " << valid_cloud->size() << " points (XYZ only)" << std::endl;
    std::cout << "Normals will be computed by CGAL in the pipeline (more accurate anyway!)" << std::endl;

    return 0;
}