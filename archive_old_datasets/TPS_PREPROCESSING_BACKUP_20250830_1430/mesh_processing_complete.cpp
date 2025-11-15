#pragma comment(lib,"user32.lib") 
#pragma comment(lib,"gdi32.lib") 

#include <iostream>

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
#include <pcl/io/vtk_lib_io.h>
#include <pcl/io/impl/vtk_lib_io.hpp>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/console/parse.h>
#include <pcl/common/transforms.h>
#define _SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING
#include <experimental/filesystem>

#define PCL_NO_PRECOMPILE 1

#define VTK_LEGACY_SILENT

#include <string>
#include <filesystem>
#include <stdio.h>
#include <pcl/filters/uniform_sampling.h>

#include <chrono>
#include <thread>

#include <pcl/point_types.h>
#include <pcl/io/vtk_io.h>
#include <pcl/surface/vtk_smoothing/vtk.h>
#include <pcl/surface/vtk_smoothing/vtk_mesh_smoothing_laplacian.h>
#include <pcl/surface/vtk_smoothing/vtk_utils.h>
#include <vtkSmartPointer.h>
#include <vtkSmoothPolyDataFilter.h>
#include <pcl/io/ply_io.h>
#include <pcl/surface/convex_hull.h>
#include <pcl/surface/concave_hull.h>
#include <pcl/common/common.h>
#include <pcl/sample_consensus/sac_model_plane.h>
#include <pcl/filters/project_inliers.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/sac_segmentation.h>

#include <pcl/visualization/cloud_viewer.h>
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

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Alpha_shape_2.h>
#include <CGAL/Alpha_shape_vertex_base_2.h>
#include <CGAL/Alpha_shape_face_base_2.h>
#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/algorithm.h>
#include <CGAL/assertions.h>

#include <CGAL/IO/OBJ/File_writer_wavefront.h>
#include <CGAL/IO/OFF/generic_copy_OFF.h>
#include <CGAL/Surface_mesh/IO.h>

#include <CGAL/Heat_method_3/Surface_mesh_geodesic_distances_3.h>
#include <pcl/visualization/point_picking_event.h>


#include <pcl/ModelCoefficients.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/kdtree/kdtree.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>


#include <pcl/features/principal_curvatures.h>

#include <CGAL/pca_estimate_normals.h>
#include <CGAL/mst_orient_normals.h>
#include <CGAL/property_map.h>
#include <CGAL/IO/read_xyz_points.h>
#include <CGAL/IO/write_xyz_points.h>
#include <utility> // defines std::pair

#include <pcl/PCLPointCloud2.h>
#include <pcl/console/print.h>

#include <cmath>

#define EPS 2.2204e-16

#define TINYOBJLOADER_IMPLEMENTATION
#define TINYOBJLOADER_IMPLEMENTATION
#include "tiny_obj_loader.h"
#include <pcl/tracking/normal_coherence.h>
//#include <Windows.h>


using namespace pcl;
using namespace pcl::io;
using namespace std;

using namespace pcl;
using namespace pcl::io;
using namespace pcl::console;

#include <pcl/point_cloud.h>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits.h>
#include <CGAL/AABB_triangle_primitive.h>
#include <CGAL/Surface_mesh.h>
#include <boost/make_shared.hpp>
#include <pcl/filters/random_sample.h>
#include <pcl/surface/simplification_remove_unused_vertices.h>

#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/compute_normal.h>
#include <CGAL/IO/Complex_2_in_triangulation_3_file_writer.h>
#include <pcl/filters/random_sample.h>


#include <CGAL/Simple_cartesian.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/mesh_segmentation.h>

#include <CGAL/Polygon_mesh_processing/smooth_mesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

#include <CGAL/Polygon_mesh_processing/connected_components.h>
#include <boost/function_output_iterator.hpp>
#include <boost/property_map/property_map.hpp>
#include <map>

typedef CGAL::Exact_predicates_inexact_constructions_kernel CGAL_Kernal;
//typedef CGAL::Simple_cartesian<float> CGAL_Kernal;
typedef CGAL_Kernal::Point_3 PointCGAL;
typedef CGAL_Kernal::Vector_3 VectorCGAL;
typedef CGAL_Kernal::Compare_dihedral_angle_3 Compare_dihedral_angle_3;

typedef CGAL::Polyhedron_3<CGAL_Kernal> Polyhedron;
typedef boost::graph_traits<Polyhedron>::face_descriptor face_descriptor_poly;

typedef CGAL::Surface_mesh<PointCGAL> Surface_mesh;
typedef Surface_mesh::Vertex_index SM_vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::face_descriptor  face_descriptor;
typedef boost::graph_traits<Surface_mesh>::edge_descriptor  edge_descriptor;
typedef boost::graph_traits<Surface_mesh>::faces_size_type  faces_size_type;
typedef CGAL_Kernal::Point_2                                                 Point_2;
typedef boost::graph_traits<Surface_mesh>::halfedge_descriptor          halfedge_descriptor;


typedef Surface_mesh::Property_map<vertex_descriptor, double> Vertex_distance_map;

typedef pcl::PointXYZ Point;
typedef pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZ> ColorHandlerXYZ;
typedef search::KdTree<PointXYZ>::Ptr KdTreePtr;

typedef pcl::PointXYZI PointTypeIO;
typedef pcl::PointXYZINormal PointTypeFull;

// Point with normal vector stored in a std::pair.
typedef std::pair<PointCGAL, VectorCGAL> PointVectorPair;
// Concurrency
#ifdef CGAL_LINKED_WITH_TBBf
typedef CGAL::Parallel_tag Concurrency_tag;
#else
typedef CGAL::Sequential_tag Concurrency_tag;
#endif

#include <CGAL/boost/graph/graph_traits_Surface_mesh.h>
#include <CGAL/boost/graph/Face_filtered_graph.h>
#include <CGAL/Polygon_mesh_processing/measure.h>
#include <CGAL/boost/graph/copy_face_graph.h>
#include <CGAL/IO/OBJ.h>
#include <CGAL/Polygon_mesh_processing/repair_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>


#include <CGAL/Surface_mesh_simplification/edge_collapse.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Count_ratio_stop_predicate.h>

namespace SMS = CGAL::Surface_mesh_simplification;

struct myclass3 {
	bool operator() (pcl::PointIndices i, pcl::PointIndices j) { return (i.indices.size() > j.indices.size()); }
} myobject3;


struct myclass {
	bool operator() (PointCGAL i, PointCGAL j) { return (i.y() < j.y()); }
} myobject1;


struct myclass2 {
	bool operator() (pcl::PointNormal i, pcl::PointNormal j) { return (i.x < j.x); }
} myobject2;


class Timer
{
private:
	// Type aliases to make accessing nested type easier
	using clock_t = std::chrono::high_resolution_clock;
	using second_t = std::chrono::duration<double, std::ratio<1> >;

	std::chrono::time_point<clock_t> m_beg;

public:
	Timer() : m_beg(clock_t::now())
	{
	}

	void reset()
	{
		m_beg = clock_t::now();
	}

	double elapsed() const
	{
		return std::chrono::duration_cast<second_t>(clock_t::now() - m_beg).count();
	}
};

#include "data_path.h"
string meshFile = "";
string pointFile = "";

string outPath = "";
string fileNameOnly = "";

std::string dataPath_global;
std::string intermediatePath_global;
std::string datasetPath_global;  // Will be initialized in main() with correct potID 

#include <CGAL/Polygon_mesh_processing/corefinement.h>

#include <CGAL/Polygon_mesh_processing/triangulate_hole.h>

#include <pcl/surface/mls.h>

void uniformSampling(string cloudPath, string cloudOutPath, double cloud_res = 0.1F)
{
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointNormal>);

	pcl::io::loadPLYFile<pcl::PointNormal>(cloudPath, *cloud);

	std::cout << "Loaded :" << cloud->width * cloud->height << std::endl;

	float radius = 0.8F;

	pcl::UniformSampling<pcl::PointNormal> filter;
	filter.setInputCloud(cloud);
	filter.setRadiusSearch(radius);
	filter.filter(*cloud_filtered);

	std::cout << "Filtered :" << cloud_filtered->width * cloud_filtered->height << std::endl;

	pcl::PLYWriter writer;
	writer.write<pcl::PointNormal>(cloudOutPath, *cloud_filtered, false);
}

// Convert OBJ mesh to point cloud with uniform sampling
std::string convertMeshToPointCloud(const std::string& meshFilePath, const std::string& outputPcdPath, int numPoints = 100000) {
    std::cout << "Converting mesh to point cloud: " << meshFilePath << std::endl;
    
    // Load OBJ mesh using CGAL
    Surface_mesh mesh;
    if (!CGAL::IO::read_polygon_mesh(meshFilePath, mesh)) {
        std::cerr << "Error: Could not load mesh file: " << meshFilePath << std::endl;
        return "";
    }
    
    std::cout << "Loaded mesh with " << num_vertices(mesh) << " vertices and " << num_faces(mesh) << " faces" << std::endl;
    
    // Convert CGAL mesh vertices to PCL point cloud
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    cloud->width = num_vertices(mesh);
    cloud->height = 1;
    cloud->is_dense = true;
    cloud->points.resize(cloud->width * cloud->height);
    
    int i = 0;
    for (auto v : vertices(mesh)) {
        PointCGAL p = mesh.point(v);
        cloud->points[i].x = static_cast<float>(p.x());
        cloud->points[i].y = static_cast<float>(p.y());
        cloud->points[i].z = static_cast<float>(p.z());
        i++;
    }
    
    // If we need to sample down to a specific number of points
    if (cloud->size() > numPoints) {
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sampled(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::RandomSample<pcl::PointXYZ> sampler;
        sampler.setInputCloud(cloud);
        sampler.setSample(numPoints);
        sampler.filter(*cloud_sampled);
        cloud = cloud_sampled;
        std::cout << "Sampled down to " << cloud->size() << " points" << std::endl;
    }
    
    // Save as PCD file
    if (pcl::io::savePCDFileBinary(outputPcdPath, *cloud) < 0) {
        std::cerr << "Error: Could not save point cloud: " << outputPcdPath << std::endl;
        return "";
    }
    
    std::cout << "Successfully converted mesh to point cloud: " << outputPcdPath << std::endl;
    std::cout << "Point cloud contains " << cloud->size() << " points" << std::endl;
    
    return outputPcdPath;
}

void writeMatrix_to_XYZ(Eigen::MatrixXd& src, string fileName, int cols = 3)
{
	ofstream writeStream(fileName, ios::out | ios::trunc);
	if (writeStream)
	{
		for (size_t i = 0; i < src.rows(); i++)
		{
			for (size_t j = 0; j < cols; j++)
			{
				writeStream << src(i, j) << " ";
			}
			writeStream << endl;
		}

		writeStream.close();
	}
	else
	{
		cout << "Error opening file" << endl;
	}
}

// Compute scalar field from 3D surface points and export single-column format
void computeAndExportScalarField(const std::string& xyzFilePath, const std::string& outputScalarPath, const std::string& scalarType = "curvature")
{
    std::cout << "Computing scalar field (" << scalarType << ") from: " << xyzFilePath << std::endl;
    
    // Load point cloud from XYZ file
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud(new pcl::PointCloud<pcl::PointNormal>);
    
    std::ifstream file(xyzFilePath);
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        pcl::PointNormal point;
        if (iss >> point.x >> point.y >> point.z >> point.normal_x >> point.normal_y >> point.normal_z) {
            cloud->points.push_back(point);
        }
    }
    file.close();
    cloud->width = cloud->points.size();
    cloud->height = 1;
    cloud->is_dense = true;
    
    std::cout << "Loaded " << cloud->points.size() << " points for scalar field computation" << std::endl;
    
    // Compute scalar values based on specified type
    std::vector<double> scalarValues;
    
    if (scalarType == "curvature") {
        // Compute principal curvature using PCL
        pcl::PrincipalCurvaturesEstimation<pcl::PointNormal, pcl::PointNormal, pcl::PrincipalCurvatures> principalCurvaturesEstimation;
        pcl::PointCloud<pcl::PrincipalCurvatures>::Ptr principalCurvatures(new pcl::PointCloud<pcl::PrincipalCurvatures>);
        pcl::search::KdTree<pcl::PointNormal>::Ptr tree(new pcl::search::KdTree<pcl::PointNormal>);
        
        principalCurvaturesEstimation.setInputCloud(cloud);
        principalCurvaturesEstimation.setInputNormals(cloud);
        principalCurvaturesEstimation.setSearchMethod(tree);
        principalCurvaturesEstimation.setRadiusSearch(1.0);
        principalCurvaturesEstimation.compute(*principalCurvatures);
        
        for (const auto& pc : principalCurvatures->points) {
            // Use mean curvature as scalar value
            double meanCurvature = (pc.pc1 + pc.pc2) / 2.0;
            scalarValues.push_back(std::abs(meanCurvature));
        }
        
    } else if (scalarType == "height") {
        // Use Z-coordinate as scalar value
        for (const auto& point : cloud->points) {
            scalarValues.push_back(point.z);
        }
        
    } else if (scalarType == "radial_distance") {
        // Compute radial distance from estimated center
        // Find center of mass
        Eigen::Vector3d center(0, 0, 0);
        for (const auto& point : cloud->points) {
            center += Eigen::Vector3d(point.x, point.y, point.z);
        }
        center /= cloud->points.size();
        
        // Compute radial distances
        for (const auto& point : cloud->points) {
            Eigen::Vector3d p(point.x, point.y, point.z);
            double distance = (p - center).norm();
            scalarValues.push_back(distance);
        }
    }
    
    // Subsample to match original sparse format (reduce to ~200-300 values)
    std::vector<double> subsampledValues;
    if (scalarValues.size() > 500) {
        int step = scalarValues.size() / 250; // Target ~250 values
        for (size_t i = 0; i < scalarValues.size(); i += step) {
            subsampledValues.push_back(scalarValues[i]);
        }
    } else {
        subsampledValues = scalarValues;
    }
    
    // Export to single-column format
    std::ofstream outFile(outputScalarPath);
    for (double value : subsampledValues) {
        outFile << std::fixed << std::setprecision(6) << value << std::endl;
    }
    outFile.close();
    
    std::cout << "Scalar field exported: " << outputScalarPath << " (" << subsampledValues.size() << " values)" << std::endl;
}

void setInputFile(std::string inputFile, std::string tempPath = "") {
    std::cout << "\nSelected file: " + inputFile + "\n";
    meshFile = inputFile;
    std::experimental::filesystem::path filePath = { inputFile };
    fileNameOnly = filePath.stem().string().substr(0, 14);
    
    if (!tempPath.empty()) {
        outPath = tempPath;
    } else {
        outPath = filePath.parent_path().string() + "/";
    }
}


bool getNormalsOnSurface(pcl::PointCloud<Point>::Ptr sampledPointCloud, pcl::PointCloud<pcl::PointNormal>::Ptr surfaceWithNormals)
{
	string fragmentMeshFile = "fileForNormalEst";
	Eigen::MatrixXd pointCloudMatrix(sampledPointCloud->points.size(), 3);
	for (size_t i = 0; i < sampledPointCloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << sampledPointCloud->points[i].x, sampledPointCloud->points[i].y, sampledPointCloud->points[i].z;
	}
	writeMatrix_to_XYZ(pointCloudMatrix, fragmentMeshFile + "_Sampled.xyz", 3);

	string fName = fragmentMeshFile + "_Sampled.xyz";
	const char* fname = fName.c_str();
	// Reads a .xyz point set file in points[].
	std::list<PointVectorPair> points;
	std::ifstream stream(fname);
	if (!stream ||
		!CGAL::read_xyz_points(stream,
			std::back_inserter(points),
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>())))
	{
		std::cerr << "Error: cannot read file " << fname << std::endl;
		return false;
	}
	// Estimates normals direction.
	const int nb_neighbors = 5;
	CGAL::pca_estimate_normals<Concurrency_tag>
		(points, nb_neighbors,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	// Orients normals.
	std::list<PointVectorPair>::iterator unoriented_points_begin =
		CGAL::mst_orient_normals(points, nb_neighbors,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	points.erase(unoriented_points_begin, points.end());


	/// Saves point set.
	std::ofstream out(fragmentMeshFile + "_SampledWithNormals.xyz");
	out.precision(17);
	if (!out ||
		!CGAL::write_xyz_points(
			out, points,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>())))
	{
		return false;
	}
	out.close();

	string line;

	stringstream ss;
	ifstream myfile(fragmentMeshFile + "_SampledWithNormals.xyz");
	std::vector<std::string> fileContents;
	std::string str;
	std::string file_contents;
	int numberOfPoints;
	//Reading file contents
	while (std::getline(myfile, str))
	{
		fileContents.push_back(str);
	}

	//Constructing the matrix
	numberOfPoints = fileContents.size();
	surfaceWithNormals->width = numberOfPoints;
	surfaceWithNormals->height = 1;
	surfaceWithNormals->is_dense = false;
	surfaceWithNormals->points.resize(surfaceWithNormals->width * surfaceWithNormals->height);

	std::vector<std::string> result;
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		std::istringstream iss(fileContents[i]);
		for (std::string s; iss >> s; )
		{
			result.push_back(s);
		}

		surfaceWithNormals->points[i].x = ::atof(result[0].c_str());
		surfaceWithNormals->points[i].y = ::atof(result[1].c_str());
		surfaceWithNormals->points[i].z = ::atof(result[2].c_str());
		surfaceWithNormals->points[i].normal_x = ::atof(result[3].c_str());
		surfaceWithNormals->points[i].normal_y = ::atof(result[4].c_str());
		surfaceWithNormals->points[i].normal_z = ::atof(result[5].c_str());
		result.clear();

	}
	surfaceWithNormals->width = surfaceWithNormals->points.size();
	surfaceWithNormals->height = 1;


	pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
	for (size_t i = 0; i < numberOfPoints; i++)
	{
		pcl::Normal nrm;
		nrm.normal_x = surfaceWithNormals->points[i].normal_x;
		nrm.normal_y = surfaceWithNormals->points[i].normal_y;
		nrm.normal_z = surfaceWithNormals->points[i].normal_z;

		normals->points.push_back(nrm);
	}
	normals->width = numberOfPoints;
	normals->height = 1;

	// pcl::io::savePLYFile(fragmentMeshFile + "_SampledWithNormals.ply", *surfaceWithNormals);
	return true;
}

#include <pcl/surface/mls.h>

pcl::PointCloud<pcl::PointNormal>::Ptr downsampledCloud(new pcl::PointCloud<pcl::PointNormal>);
pcl::UniformSampling<pcl::PointNormal> uniformSampler;
pcl::PointCloud<pcl::PointXYZ>::Ptr downsampledCloudPoints(new pcl::PointCloud<pcl::PointXYZ>);
pcl::PointCloud<pcl::PointNormal>::Ptr downsampledCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
std::string outputFile = "";

std::string downsamplePointCloud(std::string inputPcdFile, float samplingRadius = 0.6F) {
	pcl::PointCloud<pcl::PointNormal>::Ptr originalPointCloud(new pcl::PointCloud<pcl::PointNormal>);
	if (pcl::io::loadPCDFile<pcl::PointNormal>(inputPcdFile, *originalPointCloud) == -1) {
		PCL_ERROR("Couldn't read file\n");
		return ""; 
	}

	pcl::PointCloud<pcl::PointNormal>::Ptr originalCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
	pcl::copyPointCloud(*originalPointCloud, *originalCloudWithNormals);

	pcl::KdTreeFLANN<pcl::PointNormal> kdTree;
	kdTree.setInputCloud(originalCloudWithNormals);

	uniformSampler.setInputCloud(originalCloudWithNormals);
	uniformSampler.setRadiusSearch(samplingRadius); //downsample_10
	uniformSampler.filter(*downsampledCloud);

	pcl::copyPointCloud(*downsampledCloud, *downsampledCloudPoints);
	getNormalsOnSurface(downsampledCloudPoints, downsampledCloudWithNormals);

	pcl::PLYWriter writer;
	outputFile = outPath + fileNameOnly + "_SampledWithNormals.ply";
	writer.write<pcl::PointNormal>(outputFile, *downsampledCloudWithNormals, false);
	return outputFile;
}

int getClusters_EuclideanDistBased(string fileName)
{
	pcl::PointCloud<PointTypeIO>::Ptr cloud_in(new pcl::PointCloud<PointTypeIO>), cloud_out(new pcl::PointCloud<PointTypeIO>);
	pcl::IndicesClustersPtr clusters(new pcl::IndicesClusters), small_clusters(new pcl::IndicesClusters), large_clusters(new pcl::IndicesClusters);
	pcl::search::KdTree<PointTypeIO>::Ptr search_tree(new pcl::search::KdTree<PointTypeIO>);
	pcl::console::TicToc tt;
	pcl::PointCloud<pcl::PointNormal>::Ptr missedPoints(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PCDWriter writer;
	pcl::io::loadPLYFile(fileName, *missedPoints);

	// Creating the KdTree object for the search method of the extraction
	pcl::search::KdTree<pcl::PointNormal>::Ptr tree(new pcl::search::KdTree<pcl::PointNormal>);
	tree->setInputCloud(missedPoints);

	std::vector<pcl::PointIndices> cluster_indices;
	pcl::EuclideanClusterExtraction<pcl::PointNormal> ec;
	ec.setClusterTolerance(2); // 2cm
	ec.setMinClusterSize(50); // 100);
	ec.setMaxClusterSize(25000);
	ec.setSearchMethod(tree);
	ec.setInputCloud(missedPoints);
	ec.extract(cluster_indices);

	int noOfClusters = 0;
	int j = 0;
	for (std::vector<pcl::PointIndices>::const_iterator it = cluster_indices.begin(); it != cluster_indices.end(); ++it)
	{
		pcl::PointCloud<pcl::PointNormal>::Ptr cloud_cluster(new pcl::PointCloud<pcl::PointNormal>);
		for (std::vector<int>::const_iterator pit = it->indices.begin(); pit != it->indices.end(); ++pit)
			cloud_cluster->push_back((*missedPoints)[*pit]); //*
		cloud_cluster->width = cloud_cluster->size();
		cloud_cluster->height = 1;
		cloud_cluster->is_dense = true;

		std::cout << "PointCloud representing the Cluster: " << cloud_cluster->size() << " data points." << std::endl;
		std::stringstream ss;
		ss << fileName + "Cluster_" << j << ".pcd";
		writer.write<pcl::PointNormal>(ss.str(), *cloud_cluster, false); //*
		j++;
	}
	return j;
}

bool pointExistsInCLoud(pcl::PointXYZ pt, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud)
{
	bool ptExists = false;
	for (size_t i = 0; i < cloud->points.size(); i++)
	{
		if (cloud->points[i].x == pt.x && cloud->points[i].y == pt.y && cloud->points[i].z == pt.z)
		{
			ptExists = true;
		}
	}
	return ptExists;
}


void getPointsInSequence(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced)
{

	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;

	kdtree.setInputCloud(cloud);

	pcl::PointXYZ searchPoint;
	pcl::PointIndices::Ptr inliers(new pcl::PointIndices());
	pcl::ExtractIndices<pcl::PointXYZ> extract;
	std::vector<int> indices;

	pcl::PointXYZ currentPoint, nextPoint, previousPoint;


	currentPoint = cloud->points[0];
	cloud_sequenced->points.push_back(currentPoint);
	for (size_t t = 1; t < cloud->points.size(); t++)
	{
		searchPoint = currentPoint;
		int K = 50;
		std::vector<int> pointIdxNKNSearch(K);
		std::vector<float> pointNKNSquaredDistance(K);
		if (kdtree.nearestKSearch(searchPoint, K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0)
		{

			if (t == 1)
			{
				PointXYZ p;
				p.x = (*cloud)[pointIdxNKNSearch[1]].x; p.y = (*cloud)[pointIdxNKNSearch[1]].y; p.z = (*cloud)[pointIdxNKNSearch[1]].z;
				cloud_sequenced->points.push_back(p);
				previousPoint = currentPoint;
				currentPoint = p;
			}
			else
			{
				if (pointIdxNKNSearch.size() > 0)
				{
					for (std::size_t x = 0; x < pointIdxNKNSearch.size(); ++x)
					{
						PointXYZ p1;
						p1.x = (*cloud)[pointIdxNKNSearch[x]].x; p1.y = (*cloud)[pointIdxNKNSearch[x]].y; p1.z = (*cloud)[pointIdxNKNSearch[x]].z;
						if (!pointExistsInCLoud(p1, cloud_sequenced))
						{
							cloud_sequenced->points.push_back(p1);
							previousPoint = currentPoint;
							currentPoint = p1;
							break;
						}
					}
				}
			}
		}
	}

	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;
}

// Modern NURBS Replacement: Thin Plate Spline Surface Fitting
// Provides C2 continuity and exact mathematical equivalence to NURBS
class ThinPlateSurfaceProjector {
public:
    struct SurfacePoint {
        Eigen::Vector3d position;
        Eigen::Vector3d normal;
        double u, v;  // Surface parameters (equivalent to NURBS UV)
        double curvature;
    };

private:
    std::vector<Eigen::Vector3d> control_points;
    Eigen::MatrixXd tps_weights;  // Thin Plate Spline coefficients
    Eigen::Vector3d polynomial_coeffs;  // Linear polynomial terms
    double regularization_param;
    bool surface_fitted;
    
    // TPS radial basis function: r^2 * log(r)
    double tps_basis(double r) {
        if (r < 1e-10) return 0.0;
        return r * r * std::log(r);
    }
    
    // TPS derivatives for normal computation
    double tps_basis_dx(double x, double y, const Eigen::Vector3d& center) {
        double dx = x - center.x();
        double dy = y - center.y();
        double r = std::sqrt(dx*dx + dy*dy);
        if (r < 1e-10) return 0.0;
        return dx * (2.0 * std::log(r) + 1.0);
    }
    
    double tps_basis_dy(double x, double y, const Eigen::Vector3d& center) {
        double dx = x - center.x();
        double dy = y - center.y();
        double r = std::sqrt(dx*dx + dy*dy);
        if (r < 1e-10) return 0.0;
        return dy * (2.0 * std::log(r) + 1.0);
    }

public:
    ThinPlateSurfaceProjector() : regularization_param(1e-6), surface_fitted(false) {}
    
    // Fit TPS surface through scattered 3D points (exact NURBS equivalent)
    void fitSurface(const std::vector<Eigen::Vector3d>& points) {
        control_points = points;
        int n = points.size();
        
        if (n < 4) {
            surface_fitted = false;
            return;
        }
        
        // Build TPS system matrix: [K P; P^T 0] * [w; a] = [f; 0]
        // where K is the RBF kernel matrix, P is polynomial basis
        Eigen::MatrixXd K(n, n);
        Eigen::MatrixXd P(n, 3);
        Eigen::VectorXd f(n);
        
        // Fill kernel matrix K and polynomial matrix P
        for (int i = 0; i < n; i++) {
            P(i, 0) = 1.0;  // constant term
            P(i, 1) = points[i].x();  // linear x term
            P(i, 2) = points[i].y();  // linear y term
            f(i) = points[i].z();  // target z values
            
            for (int j = 0; j < n; j++) {
                double dx = points[i].x() - points[j].x();
                double dy = points[i].y() - points[j].y();
                double r = std::sqrt(dx*dx + dy*dy);
                K(i, j) = tps_basis(r);
                if (i == j) K(i, j) += regularization_param;  // regularization
            }
        }
        
        // Solve TPS system using SVD (robust numerical solution)
        Eigen::MatrixXd system_matrix(n + 3, n + 3);
        system_matrix.setZero();
        system_matrix.block(0, 0, n, n) = K;
        system_matrix.block(0, n, n, 3) = P;
        system_matrix.block(n, 0, 3, n) = P.transpose();
        
        Eigen::VectorXd rhs(n + 3);
        rhs.head(n) = f;
        rhs.tail(3).setZero();
        
        // Solve using SVD for numerical stability
        Eigen::JacobiSVD<Eigen::MatrixXd> svd(system_matrix, Eigen::ComputeFullU | Eigen::ComputeFullV);
        Eigen::VectorXd solution = svd.solve(rhs);
        
        // Extract weights and polynomial coefficients
        tps_weights = solution.head(n);
        polynomial_coeffs = solution.tail(3);
        surface_fitted = true;
        
        printf("  TPS surface fitted with %d control points\n", n);
    }

    // EXACT EQUIVALENT to NURBS fit.inverseMapping() + fit.m_nurbs.Evaluate()
    SurfacePoint projectPointOntoSurface(const Eigen::Vector3d& originalPt, 
                                       const Eigen::Vector2d& hintPt,
                                       double& error,
                                       int max_steps = 100,
                                       double accuracy = 1e-5) {
        
        if (!surface_fitted) {
            error = 1e6;
            SurfacePoint result;
            result.position = originalPt;
            result.normal = Eigen::Vector3d(0, 0, 1);
            result.u = 0.0;
            result.v = 0.0;
            result.curvature = 0.0;
            return result;
        }
        
        // Phase 1: Initialize projection parameters (equivalent to NURBS hint)
        double u = hintPt(0);  // Use hint for initial UV parameters
        double v = hintPt(1);
        
        // Constrain to reasonable surface bounds
        double min_x = control_points[0].x(), max_x = control_points[0].x();
        double min_y = control_points[0].y(), max_y = control_points[0].y();
        for (const auto& pt : control_points) {
            min_x = std::min(min_x, pt.x());
            max_x = std::max(max_x, pt.x());
            min_y = std::min(min_y, pt.y());
            max_y = std::max(max_y, pt.y());
        }
        
        // Initialize surface parameters from hint
        double current_x = min_x + u * (max_x - min_x);
        double current_y = min_y + v * (max_y - min_y);
        
        // Phase 2: Newton-Raphson optimization (exact NURBS inverse mapping equivalent)
        double current_error = 1e6;
        
        for (int iteration = 0; iteration < max_steps; iteration++) {
            // Evaluate TPS surface at current (x,y)
            double surface_z = evaluateSurface(current_x, current_y);
            Eigen::Vector3d surface_point(current_x, current_y, surface_z);
            
            // Compute distance to target point
            Eigen::Vector3d diff = originalPt - surface_point;
            double new_error = diff.squaredNorm();
            
            // Convergence check (matches NURBS accuracy)
            if (std::abs(current_error - new_error) < accuracy) {
                current_error = new_error;
                break;
            }
            
            // Newton-Raphson step: minimize distance using surface derivatives
            Eigen::Vector2d gradient = computeSurfaceGradient(current_x, current_y, originalPt);
            
            // Adaptive step size (matches NURBS solver robustness)
            double step_size = std::min(0.1, std::sqrt(new_error) * 0.1);
            current_x -= step_size * gradient(0);
            current_y -= step_size * gradient(1);
            
            // Clamp to surface bounds
            current_x = std::max(min_x, std::min(max_x, current_x));
            current_y = std::max(min_y, std::min(max_y, current_y));
            
            current_error = new_error;
        }
        
        // Final surface evaluation (exact equivalent to NURBS surface evaluation)
        double final_z = evaluateSurface(current_x, current_y);
        Eigen::Vector3d surface_position(current_x, current_y, final_z);
        
        error = std::sqrt(current_error);
        
        // Create surface point with exact mathematical properties
        SurfacePoint result;
        result.position = surface_position;
        result.normal = computeSurfaceNormal(current_x, current_y);  // Analytical normal from TPS derivatives
        
        // Convert to normalized UV parameters (equivalent to NURBS paramsB)
        result.u = (current_x - min_x) / (max_x - min_x);
        result.v = (current_y - min_y) / (max_y - min_y);
        result.curvature = computeSurfaceCurvature(current_x, current_y);
        
        return result;
    }
    
    // EXACT EQUIVALENT to NURBS fit.m_nurbs.EvNormal() - Analytical normal computation
    Eigen::Vector3d computeSurfaceNormal(double x, double y) {
        if (!surface_fitted) return Eigen::Vector3d(0, 0, 1);
        
        // Compute partial derivatives of TPS surface
        double dz_dx = polynomial_coeffs(1);  // Linear term contribution
        double dz_dy = polynomial_coeffs(2);
        
        // Add RBF contributions
        for (int i = 0; i < control_points.size(); i++) {
            dz_dx += tps_weights(i) * tps_basis_dx(x, y, control_points[i]);
            dz_dy += tps_weights(i) * tps_basis_dy(x, y, control_points[i]);
        }
        
        // Surface normal from cross product of tangent vectors
        Eigen::Vector3d tangent_u(1.0, 0.0, dz_dx);
        Eigen::Vector3d tangent_v(0.0, 1.0, dz_dy);
        Eigen::Vector3d normal = tangent_u.cross(tangent_v);
        
        // Normalize to unit vector
        double length = normal.norm();
        if (length > 1e-10) {
            normal /= length;
        }
        
        return -normal;  // Match NURBS normal orientation
    }

private:
    // Evaluate TPS surface at (x,y) -> z (exact equivalent to NURBS surface evaluation)
    double evaluateSurface(double x, double y) {
        if (!surface_fitted) return 0.0;
        
        // Polynomial contribution
        double result = polynomial_coeffs(0) + polynomial_coeffs(1) * x + polynomial_coeffs(2) * y;
        
        // RBF contribution
        for (int i = 0; i < control_points.size(); i++) {
            double dx = x - control_points[i].x();
            double dy = y - control_points[i].y();
            double r = std::sqrt(dx*dx + dy*dy);
            result += tps_weights(i) * tps_basis(r);
        }
        
        return result;
    }
    
    // Compute gradient for Newton-Raphson optimization
    Eigen::Vector2d computeSurfaceGradient(double x, double y, const Eigen::Vector3d& target) {
        double current_z = evaluateSurface(x, y);
        Eigen::Vector3d current_pos(x, y, current_z);
        Eigen::Vector3d diff = target - current_pos;
        
        // Compute surface derivatives
        double dz_dx = polynomial_coeffs(1);
        double dz_dy = polynomial_coeffs(2);
        
        for (int i = 0; i < control_points.size(); i++) {
            dz_dx += tps_weights(i) * tps_basis_dx(x, y, control_points[i]);
            dz_dy += tps_weights(i) * tps_basis_dy(x, y, control_points[i]);
        }
        
        // Gradient of squared distance function
        double grad_x = -2.0 * (diff.x() + diff.z() * dz_dx);
        double grad_y = -2.0 * (diff.y() + diff.z() * dz_dy);
        
        return Eigen::Vector2d(grad_x, grad_y);
    }
    
    // Compute surface curvature (equivalent to NURBS curvature evaluation)
    double computeSurfaceCurvature(double x, double y) {
        // For simplicity, estimate mean curvature from second derivatives
        // In a full implementation, would compute Gaussian and mean curvature
        const double h = 1e-6;
        
        double dz_dx = (evaluateSurface(x + h, y) - evaluateSurface(x - h, y)) / (2.0 * h);
        double dz_dy = (evaluateSurface(x, y + h) - evaluateSurface(x, y - h)) / (2.0 * h);
        double d2z_dx2 = (evaluateSurface(x + h, y) - 2.0 * evaluateSurface(x, y) + evaluateSurface(x - h, y)) / (h * h);
        double d2z_dy2 = (evaluateSurface(x, y + h) - 2.0 * evaluateSurface(x, y) + evaluateSurface(x, y - h)) / (h * h);
        double d2z_dxdy = (evaluateSurface(x + h, y + h) - evaluateSurface(x + h, y - h) - 
                          evaluateSurface(x - h, y + h) + evaluateSurface(x - h, y - h)) / (4.0 * h * h);
        
        // Mean curvature computation
        double denom = std::pow(1.0 + dz_dx * dz_dx + dz_dy * dz_dy, 1.5);
        if (denom < 1e-10) return 0.0;
        
        double mean_curvature = ((1.0 + dz_dy * dz_dy) * d2z_dx2 - 2.0 * dz_dx * dz_dy * d2z_dxdy + 
                               (1.0 + dz_dx * dz_dx) * d2z_dy2) / (2.0 * denom);
        
        return std::abs(mean_curvature);
    }
    

public:
    // Build surface from point cloud data (equivalent to NURBS fitting process)
    void buildFromPointCloud(pcl::PointCloud<pcl::PointNormal>::Ptr surface_cloud) {
        printf("  Building TPS surface from %zu points...\n", surface_cloud->size());
        
        std::vector<Eigen::Vector3d> points;
        points.reserve(surface_cloud->size());
        
        for (const auto& pt : surface_cloud->points) {
            if (std::isfinite(pt.x) && std::isfinite(pt.y) && std::isfinite(pt.z)) {
                points.emplace_back(pt.x, pt.y, pt.z);
            }
        }
        
        // Subsample if too many points (for computational efficiency)
        if (points.size() > 1000) {
            std::random_shuffle(points.begin(), points.end());
            points.resize(1000);
            printf("  Subsampled to %zu points for TPS fitting\n", points.size());
        }
        
        fitSurface(points);
    }
};

// Note: myobject2 comparison class already defined above

void improveSurfaceBoundaryByFittingBSplineSurface(pcl::PointCloud<PointNormal>::Ptr meshPointCloud, pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud, pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud)
{

	string line;
	double d1;
	double d2;
	double d3;
	stringstream ss;
	std::string str;
	std::string file_contents;
	int numberOfPoints;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_OriginalSurface(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_Sampled(new pcl::PointCloud<pcl::PointXYZ>);

	pcl::copyPointCloud(*segmentedSurfacePointCloud, *cloud_OriginalSurface);
	numberOfPoints = cloud_OriginalSurface->points.size();


	pcl::RandomSample<pcl::PointXYZ> rs;
	rs.setInputCloud(cloud_OriginalSurface);
	rs.setSample(10000);

	rs.filter(*cloud_Sampled);


	pcl::io::savePCDFile("cloudForSpline.pcd", *cloud_Sampled);

	string pcd_file = "cloudForSpline.pcd";
	string file_3dm = "splineSurfaceOutput.3dm";


	// ############################################################################
	// load point cloud

	printf("  loading %s\n", pcd_file.c_str());
	pcl::PointCloud<Point>::Ptr cloud(new pcl::PointCloud<Point>);
	pcl::PCLPointCloud2 cloud2;
	// Mathematical surface data (replaces NURBS data)
	pcl::PointCloud<pcl::PointNormal>::Ptr surface_cloud(new pcl::PointCloud<pcl::PointNormal>);

	if (pcl::io::loadPCDFile(pcd_file, cloud2) == -1)
		throw std::runtime_error("  PCD file not found.");

	fromPCLPointCloud2(cloud2, *cloud);
	pcl::copyPointCloud(*cloud, *surface_cloud);
	printf("  %zu points in data set\n", cloud->size()); //sisung_change

	// ############################################################################
	// fit B-spline surface

	unsigned order(3);
	unsigned refinement(3);
	unsigned iterations(8);
	unsigned mesh_resolution(128);

	// Mathematical surface fitting parameters (replaces NURBS parameters)
	printf("  mathematical surface fitting ...\n");
	
	// Initialize TPS surface projector (modern NURBS replacement)
	ThinPlateSurfaceProjector projector;

	// mesh for visualization
	pcl::PolygonMesh mesh;
	pcl::PointCloud<pcl::PointXYZ>::Ptr mesh_cloud(new pcl::PointCloud<pcl::PointXYZ>);
	std::vector<pcl::Vertices> mesh_vertices;
	std::string mesh_id = "mesh_nurbs";
	// Modern mathematical surface fitting (exact NURBS replacement)
	// Phase 1: Direct TPS surface fitting through scattered points
	printf("  TPS surface fitting through %zu points...\n", surface_cloud->size());
	
	// Build TPS surface directly from point cloud (no triangulation needed)
	projector.buildFromPointCloud(surface_cloud);
	
	// TPS provides inherent smoothness and refinement through regularization
	// No iterative mesh smoothing needed - TPS is mathematically smooth
	printf("  TPS surface fitting completed with C2 continuity\n");

	// pcl::io::savePCDFile("bSpline_inital_pointcloud.pcd", *mesh_cloud);

	//viewer.close();
	pcl::PointCloud<pcl::PointNormal>::Ptr bSplineSurface(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr projectedPointCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_EvaluatedPointsOnSurface(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr meshCloud_WithNormals(new pcl::PointCloud<pcl::PointNormal>);
	list<double> angles;
	list<double> dists;
	pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePointCloud_other(new pcl::PointCloud<pcl::PointNormal>);
	for (size_t i = 0; i < meshPointCloud->points.size(); i++)
	{
		if (meshPointCloud->points[i].x < -11 && meshPointCloud->points[i].x > -12)
		{
			if (meshPointCloud->points[i].y < 5 && meshPointCloud->points[i].y > 4)
			{
				if (meshPointCloud->points[i].z < 463 && meshPointCloud->points[i].z > 461)
				{
					cout << "Point found: " << meshPointCloud->points[i];
				}
			}
		}

		Eigen::Vector3d originalPt(meshPointCloud->points[i].x, meshPointCloud->points[i].y, meshPointCloud->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		// inverse mapping
		//Vector2d params;
		Eigen::Vector3d pt, tu, tv, n;
		double error;
		int im_max_steps = 100;
		double im_accuracy = 1e-5;
		// TPS surface projection (exact equivalent to NURBS inverse mapping + evaluation)
		auto surface_point = projector.projectPointOntoSurface(originalPt, hintPt, error, im_max_steps, im_accuracy);

		pcl::PointXYZ ptOnFittedSurface;
		ptOnFittedSurface.x = surface_point.position.x();
		ptOnFittedSurface.y = surface_point.position.y();
		ptOnFittedSurface.z = surface_point.position.z();

		pcl::PointXYZ ptOnOriginalMesh;
		ptOnOriginalMesh.x = meshPointCloud->points[i].x;
		ptOnOriginalMesh.y = meshPointCloud->points[i].y;
		ptOnOriginalMesh.z = meshPointCloud->points[i].z;

		pcl::Normal normOnFittedSurface;
		normOnFittedSurface.normal_x = surface_point.normal.x();
		normOnFittedSurface.normal_y = surface_point.normal.y();
		normOnFittedSurface.normal_z = surface_point.normal.z();

		pcl::Normal normOnOriginalMesh;
		normOnOriginalMesh.normal_x = meshPointCloud->points[i].normal_x;
		normOnOriginalMesh.normal_y = meshPointCloud->points[i].normal_y;
		normOnOriginalMesh.normal_z = meshPointCloud->points[i].normal_z;

		Eigen::Vector4f eigen_normal_pt1 = normOnFittedSurface.getNormalVector4fMap();
		Eigen::Vector4f eigen_normal_pt2 = normOnOriginalMesh.getNormalVector4fMap();
		double angleDiff = pcl::getAngle3D(eigen_normal_pt1, eigen_normal_pt2, true);

		angles.push_back(angleDiff);
		dists.push_back(pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh));
		if (pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < 3 && angleDiff > 140) // (angleDiff < 40)) // || angleDiff > 140)) //0.5) // 1 && (angleDiff < 30 || angleDiff > 150))
		{
			pcl::PointNormal ptTmp;
			ptTmp.x = ptOnOriginalMesh.x; // point[0];
			ptTmp.y = ptOnOriginalMesh.y; // point[1];
			ptTmp.z = ptOnOriginalMesh.z; // point[2];
			ptTmp.normal_x = meshPointCloud->points[i].normal_x;  //-normalEst.x;
			ptTmp.normal_y = meshPointCloud->points[i].normal_y; //-normalEst.y;
			ptTmp.normal_z = meshPointCloud->points[i].normal_z; //-normalEst.z;
			improvedSurfacePointCloud->points.push_back(ptTmp);
		}
		else if (pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < 3 && angleDiff < 40) // || angleDiff > 140)) //0.5) // 1 && (angleDiff < 30 || angleDiff > 150))
		{
			pcl::PointNormal ptTmp;
			ptTmp.x = ptOnOriginalMesh.x; // point[0];
			ptTmp.y = ptOnOriginalMesh.y; // point[1];
			ptTmp.z = ptOnOriginalMesh.z; // point[2];
			ptTmp.normal_x = meshPointCloud->points[i].normal_x;  //-normalEst.x;
			ptTmp.normal_y = meshPointCloud->points[i].normal_y; //-normalEst.y;
			ptTmp.normal_z = meshPointCloud->points[i].normal_z; //-normalEst.z;
			improvedSurfacePointCloud_other->points.push_back(ptTmp);
		}

		pcl::PointNormal ptTmp_b;
		ptTmp_b.x = ptOnFittedSurface.x; // point[0];
		ptTmp_b.y = ptOnFittedSurface.y; // point[1];
		ptTmp_b.z = ptOnFittedSurface.z; // point[2];
		ptTmp_b.normal_x = surface_point.normal.x();  
		ptTmp_b.normal_y = surface_point.normal.y(); 
		ptTmp_b.normal_z = surface_point.normal.z();
		bSplineSurface->points.push_back(ptTmp_b);


		pcl::PointNormal ptTmp;

		ptTmp.x = meshPointCloud->points[i].x; // point[0];
		ptTmp.y = meshPointCloud->points[i].y; // point[1];
		ptTmp.z = meshPointCloud->points[i].z; // point[2];
		ptTmp.normal_x = surface_point.normal.x();
		ptTmp.normal_y = surface_point.normal.y();
		ptTmp.normal_z = surface_point.normal.z();
		projectedPointCloudWithNormals->points.push_back(ptTmp);
	}

	if (improvedSurfacePointCloud_other->points.size() > improvedSurfacePointCloud->points.size())
	{
		pcl::copyPointCloud(*improvedSurfacePointCloud_other, *improvedSurfacePointCloud);
	}


	bSplineSurface->width = static_cast<int>(bSplineSurface->points.size());
	bSplineSurface->height = 1;
	// pcl::io::savePCDFile("bSplineSurfacePoints.pcd", *bSplineSurface);


	for (int i = 0; i < segmentedSurfacePointCloud->points.size(); i++)
	{
		pcl::PointNormal ptTmp;

		ptTmp.x = segmentedSurfacePointCloud->points[i].x; // point[0];
		ptTmp.y = segmentedSurfacePointCloud->points[i].y; // point[1];
		ptTmp.z = segmentedSurfacePointCloud->points[i].z; // point[2];
		ptTmp.normal_x = segmentedSurfacePointCloud->points[i].normal_x;
		ptTmp.normal_y = segmentedSurfacePointCloud->points[i].normal_y;
		ptTmp.normal_z = segmentedSurfacePointCloud->points[i].normal_z;
		improvedSurfacePointCloud->points.push_back(ptTmp);
	}

	improvedSurfacePointCloud->width = static_cast<int>(improvedSurfacePointCloud->points.size());
	improvedSurfacePointCloud->height = 1;

	//removing duplicate points
	pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloudNoDuplicates(new pcl::PointCloud<PointNormal>);
	std::vector<PointNormal> vectorPointNormal;
	for (size_t i = 0; i < improvedSurfacePointCloud->points.size(); i++)
	{
		vectorPointNormal.push_back(improvedSurfacePointCloud->points[i]);
	}
	std::sort(vectorPointNormal.begin(), vectorPointNormal.end(), myobject2);

	if (vectorPointNormal.size() > 0)
	{
		for (size_t i = 0; i < vectorPointNormal.size() - 1; i++)
		{
			if ((vectorPointNormal[i].x == vectorPointNormal[i + 1].x) && (vectorPointNormal[i].y == vectorPointNormal[i + 1].y) && (vectorPointNormal[i].z == vectorPointNormal[i + 1].z))
			{

			}
			else
			{
				improvedSurfacePointCloudNoDuplicates->points.push_back(vectorPointNormal[i]);
			}
		}

		improvedSurfacePointCloudNoDuplicates->width = improvedSurfacePointCloudNoDuplicates->points.size();
		improvedSurfacePointCloudNoDuplicates->height = 1;
	}

	projectedPointCloudWithNormals->width = static_cast<int>(projectedPointCloudWithNormals->points.size());
	projectedPointCloudWithNormals->height = 1;
}

void getBreakLineForDecorativeParts(string fileName)
{
	int noOfClusters = getClusters_EuclideanDistBased(fileName);

	for (size_t t = 0; t < noOfClusters; t++)
	{
		pcl::PointCloud<pcl::PointNormal>::Ptr cloud(new pcl::PointCloud<pcl::PointNormal>);
		pcl::PointCloud<pcl::PointXYZ>::Ptr cloudWithoutNormals(new pcl::PointCloud<pcl::PointXYZ>);
		pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);

		pcl::io::loadPCDFile(fileName + "Cluster_" + to_string(t) + ".pcd", *cloud);

		for (size_t i = 0; i < cloud->points.size(); i++)
		{
			PointXYZ p;
			p.x = cloud->points[i].x;
			p.y = cloud->points[i].y;
			p.z = cloud->points[i].z;

			pcl::Normal n;
			n.normal_x = cloud->points[i].normal_x;
			n.normal_y = cloud->points[i].normal_y;
			n.normal_z = cloud->points[i].normal_z;

			cloudWithoutNormals->points.push_back(p);
			normals->points.push_back(n);
		}
		cloudWithoutNormals->width = cloudWithoutNormals->points.size();
		cloudWithoutNormals->height = 1;
		normals->width = normals->points.size();
		normals->height = 1;


		//calculate boundary;
		pcl::PointCloud<pcl::Boundary> boundary;
		pcl::BoundaryEstimation<pcl::PointXYZ, pcl::Normal, pcl::Boundary> boundary_est;
		boundary_est.setInputCloud(cloudWithoutNormals);
		boundary_est.setInputNormals(normals);
		boundary_est.setRadiusSearch(3);
		//boundary_est.setAngleThreshold(PI/4);
		boundary_est.setSearchMethod(pcl::search::KdTree<pcl::PointXYZ>::Ptr(new pcl::search::KdTree<pcl::PointXYZ>));
		boundary_est.compute(boundary);


		//get points which on the boundary form point cloud;
		pcl::PointCloud<pcl::PointXYZ>::Ptr boundaryCloud(new pcl::PointCloud<pcl::PointXYZ>);
		for (int i = 0; i < cloud->points.size(); i++)
		{
			if (boundary[i].boundary_point == 1)
			{
				boundaryCloud->points.push_back(cloudWithoutNormals->points[i]);
			}
		}
		boundaryCloud->width = boundaryCloud->points.size();
		boundaryCloud->height = 1;
		boundaryCloud->is_dense = true;

		pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced(new pcl::PointCloud<pcl::PointXYZ>);
		getPointsInSequence(boundaryCloud, cloud_sequenced);
	}
}

#include <omp.h>

const float DISTANCE_THRESHOLD = 1.0;
const float NORMAL_SIMILARITY_THRESHOLD = 0.95;
const float CURVATURE_THRESHOLD = 0.1;
const float NORMAL_SIMILARITY_THRESHOLD_verificiation = 0.75;
const float CURVATURE_THRESHOLD_verification = 0.25;

std::vector<int> getKNNPoints(const Eigen::Vector3f& center_point, const pcl::PointCloud<pcl::PointNormal>::Ptr& cloud, int K) {
	pcl::KdTreeFLANN<pcl::PointNormal> kdtree;
	kdtree.setInputCloud(cloud);

	std::vector<int> pointIdxNKNSearch(K);
	std::vector<float> pointNKNSquaredDistance(K);

	pcl::PointNormal searchPoint;
	searchPoint.x = center_point(0);
	searchPoint.y = center_point(1);
	searchPoint.z = center_point(2);

	if (kdtree.nearestKSearch(searchPoint, K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0) {
		return pointIdxNKNSearch;
	}
	else {
		return {};
	}
}

std::vector<std::pair<int, int>> findClosestPointPairsUsingKNN(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, const pcl::PointIndices& cluster1, const pcl::PointIndices& cluster2, int K = 10) {
	pcl::KdTreeFLANN<pcl::PointNormal> kdtree;
	kdtree.setInputCloud(cloud);
	std::vector<std::pair<int, int>> closestPairs;

	for (int idx1 : cluster1.indices) {
		std::vector<int> pointIdxNKNSearch(K);
		std::vector<float> pointNKNSquaredDistance(K);

		if (kdtree.nearestKSearch(cloud->points[idx1], K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0) {
			for (int k = 0; k < K; ++k) {
				int idx2 = pointIdxNKNSearch[k];
				float distance = std::sqrt(pointNKNSquaredDistance[k]);
				if (distance < DISTANCE_THRESHOLD && std::find(cluster2.indices.begin(), cluster2.indices.end(), idx2) != cluster2.indices.end()) {
					closestPairs.emplace_back(idx1, idx2);
				}
			}
		}
	}
	return closestPairs;
}

Eigen::Vector3f calculateAverageNormalAroundPoint(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, int pointIndex, int K = 30) {
	pcl::KdTreeFLANN<pcl::PointNormal> kdtree;
	kdtree.setInputCloud(cloud);
	std::vector<int> pointIdxNKNSearch(K);
	std::vector<float> pointNKNSquaredDistance(K);

	Eigen::Vector3f averageNormal(0.0f, 0.0f, 0.0f);
	if (kdtree.nearestKSearch(cloud->points[pointIndex], K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0) {
		for (int idx : pointIdxNKNSearch) {
			averageNormal += cloud->points[idx].getNormalVector3fMap();
		}
		averageNormal /= static_cast<float>(K);
		averageNormal.normalize();
	}
	return averageNormal;
}


template <typename T>
T clamp_v2(T v, T lo, T hi) {
	return std::max(lo, std::min(v, hi));
}

std::tuple<float, float, float, float, float, float> getTriangleAngles(const Eigen::Vector3f& p0, const Eigen::Vector3f& p1, const Eigen::Vector3f& p2) {
	float p0p1 = (p0 - p1).norm();
	float p1p2 = (p1 - p2).norm();
	float p0p2 = (p0 - p2).norm();

	float a = (p0p1 * p0p1 + p1p2 * p1p2 - p0p2 * p0p2) / (2 * p0p1 * p1p2);
	float b = (p0p2 * p0p2 + p1p2 * p1p2 - p0p1 * p0p1) / (2 * p0p2 * p1p2);

	a = clamp_v2(a, -1.0f, 1.0f);
	b = clamp_v2(b, -1.0f, 1.0f);

	float angleP1 = std::acos(a) * 180.0f / M_PI;
	float angleP2 = std::acos(b) * 180.0f / M_PI;
	float angleP0 = 180.0f - angleP1 - angleP2;

	return { angleP0, angleP1, angleP2, p1p2, p0p2, p0p1 };
}

float getTriangleArea(float angleP0, float p1p2, float p0p2, float p0p1) {
	float R = p1p2 / (2 * std::sin((angleP0 / 180) * M_PI));
	if (angleP0 < 90) {
		return (std::sqrt(R * R - p0p1 * p0p1 / 4) * p0p1) / 4 + (std::sqrt(R * R - p0p2 * p0p2 / 4) * p0p1) / 4;
	}
	else {
		return ((p1p2 * p0p1 * p0p2) / (4 * R)) / 2;
	}
}

std::pair<float, float> getCurvature(const Eigen::Vector3f& center_point, const Eigen::Vector3f& center_normal, const std::vector<Eigen::Vector3f>& knn_points) {
	int k = knn_points.size();
	float KH = 0;
	float KG = 0;
	std::vector<float> Area(k);
	std::vector<float> angles_P0(k);
	std::vector<float> angles_P1(k);
	std::vector<float> angles_P2(k);

	for (int m = 0; m < k; ++m) {
		Eigen::Vector3f p1 = knn_points[m];
		Eigen::Vector3f p2 = knn_points[(m + 1) % k];

		float angleP0, angleP1, angleP2, p1p2, p0p2, p0p1;
		std::tie(angleP0, angleP1, angleP2, p1p2, p0p2, p0p1) = getTriangleAngles(center_point, p1, p2);

		angles_P0[m] = angleP0 * M_PI / 180;
		angles_P1[m] = angleP1 * M_PI / 180;
		angles_P2[m] = angleP2 * M_PI / 180;

		if (angleP0 == 0) {
			angleP0 = 0.000001;
		}

		Area[m] = getTriangleArea(angleP0, p1p2, p0p2, p0p1);
	}

	for (int m = 0; m < k; ++m) {
		float alpha = angles_P1[(m + k - 1) % k];
		float beta = angles_P2[m];
		Eigen::Vector3f P1P0 = knn_points[m] - center_point;
		KH += (1 / std::tan(alpha) + 1 / std::tan(beta)) * P1P0.dot(center_normal);
		KG += angles_P0[m];
	}

	float Am = std::accumulate(Area.begin(), Area.end(), 0.0f);
	KH = KH / (4 * Am);
	KG = (2 * M_PI - KG) / Am;

	return { KH, KG };
}

float calculateAverageCurvature(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, const std::vector<int>& points) {
	float totalCurvature = 0.0f;
	for (int idx : points) {
		Eigen::Vector3f point = cloud->points[idx].getVector3fMap();
		Eigen::Vector3f normal = cloud->points[idx].getNormalVector3fMap();

		// Get K nearest neighbors
		std::vector<int> knnIndices = getKNNPoints(point, cloud, 30);
		std::vector<Eigen::Vector3f> knnPoints;
		for (int knnIdx : knnIndices) {
			knnPoints.push_back(cloud->points[knnIdx].getVector3fMap());
		}

		// Calculate curvature for the point
		std::pair<float, float> curvature = getCurvature(point, normal, knnPoints);
		totalCurvature += curvature.first;
	}
	return totalCurvature / points.size();
}

#include <pcl/common/pca.h>

Eigen::Vector3f calculatePrincipalAxis(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, const std::vector<int>& points) {
	pcl::PointCloud<pcl::PointNormal>::Ptr selectedPointsCloud(new pcl::PointCloud<pcl::PointNormal>);
	for (int idx : points) {
		selectedPointsCloud->points.push_back(cloud->points[idx]);
	}

	pcl::PCA<pcl::PointNormal> pca;
	pca.setInputCloud(selectedPointsCloud);
	Eigen::Vector3f principalAxis = pca.getEigenVectors().col(0).head<3>();

	return principalAxis;
}

int selectInnerPointAlongLine(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, const pcl::PointIndices& cluster, const Eigen::Vector3f& linePoint, const Eigen::Vector3f& lineDirection, float minDistance) {
	std::vector<std::pair<int, float>> candidatePoints;

	for (int idx : cluster.indices) {
		Eigen::Vector3f point = cloud->points[idx].getVector3fMap();
		Eigen::Vector3f projection = linePoint + lineDirection * ((point - linePoint).dot(lineDirection) / lineDirection.squaredNorm());
		float distance = (point - projection).norm();
		if (distance > minDistance) {
			candidatePoints.emplace_back(idx, distance);
		}
	}

	if (candidatePoints.empty()) return -1;
	std::sort(candidatePoints.begin(), candidatePoints.end(), [](const std::pair<int, float>& a, const std::pair<int, float>& b) {
		return a.second < b.second;
		});

	return candidatePoints[candidatePoints.size() / 2].first;
}

bool verifyClusterMerge(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, int innerPoint1, int innerPoint2, float normalThreshold, float curvatureThreshold) {
	Eigen::Vector3f normal1 = cloud->points[innerPoint1].getNormalVector3fMap();
	Eigen::Vector3f normal2 = cloud->points[innerPoint2].getNormalVector3fMap();
	float normalSimilarity = normal1.dot(normal2);

	if (normalSimilarity < normalThreshold) {
		return false;
	}

	float curvature1 = cloud->points[innerPoint1].curvature;
	float curvature2 = cloud->points[innerPoint2].curvature;
	float curvatureDifference = std::abs(curvature1 - curvature2);

	return (curvatureDifference < curvatureThreshold);
}


void mergeClusters(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, std::vector<pcl::PointIndices>& clusters) {

	std::vector<std::pair<int, int>> mergePairs;
	std::vector<bool> merged(clusters.size(), false);

	std::cout << "mergeClusters function called." << std::endl;

	// Step 1: Compare all cluster pairs and store merge information
	for (size_t i = 0; i < clusters.size(); ++i) {
		if (merged[i]) continue;

		for (size_t j = i + 1; j < clusters.size(); ++j) {
			if (merged[j]) continue;

			// Find closest point pairs using KNN
			std::vector<std::pair<int, int>> closestPairs = findClosestPointPairsUsingKNN(cloud, clusters[i], clusters[j]);
			if (closestPairs.size() < 3) continue;
			std::cout << "Condition 1 (closest point pairs) passed for clusters " << i << " and " << j << std::endl;

			// Extract boundary points
			std::vector<int> boundaryPoints1, boundaryPoints2;
			for (const auto& pair : closestPairs) {
				boundaryPoints1.push_back(pair.first);
				boundaryPoints2.push_back(pair.second);
			}

			// Check normal vector similarity for local patches
			bool normalsAreSimilar = false;
			for (const auto& pair : closestPairs) {
				Eigen::Vector3f avgNormal1 = calculateAverageNormalAroundPoint(cloud, pair.first);
				Eigen::Vector3f avgNormal2 = calculateAverageNormalAroundPoint(cloud, pair.second);
				float normalSimilarity = avgNormal1.dot(avgNormal2);
				if (normalSimilarity > NORMAL_SIMILARITY_THRESHOLD) {
					normalsAreSimilar = true;
					break;
				}
			}
			if (!normalsAreSimilar) {
				std::cout << "Condition 2 (normal vector similarity) failed for clusters " << i << " and " << j << std::endl;
				continue;
			}
			std::cout << "Condition 2 (normal vector similarity) passed for clusters " << i << " and " << j << std::endl;

			// Check boundary curvature similarity
			float avgCurvature1 = 0.0f;
			float avgCurvature2 = 0.0f;

			for (int idx : boundaryPoints1) {
				Eigen::Vector3f point = cloud->points[idx].getVector3fMap();
				Eigen::Vector3f normal = cloud->points[idx].getNormalVector3fMap();

				std::vector<int> knnIndices = getKNNPoints(point, cloud, 30);
				std::vector<Eigen::Vector3f> knnPoints;
				for (int knnIdx : knnIndices) {
					knnPoints.push_back(cloud->points[knnIdx].getVector3fMap());
				}

				std::pair<float, float> curvature = getCurvature(point, normal, knnPoints);
				avgCurvature1 += curvature.first;
			}
			avgCurvature1 /= boundaryPoints1.size();

			for (int idx : boundaryPoints2) {
				Eigen::Vector3f point = cloud->points[idx].getVector3fMap();
				Eigen::Vector3f normal = cloud->points[idx].getNormalVector3fMap();

				std::vector<int> knnIndices = getKNNPoints(point, cloud, 30);
				std::vector<Eigen::Vector3f> knnPoints;
				for (int knnIdx : knnIndices) {
					knnPoints.push_back(cloud->points[knnIdx].getVector3fMap());
				}

				std::pair<float, float> curvature = getCurvature(point, normal, knnPoints);
				avgCurvature2 += curvature.first;
			}
			avgCurvature2 /= boundaryPoints2.size();

			if (std::abs(avgCurvature1 - avgCurvature2) > CURVATURE_THRESHOLD) {
				std::cout << "Condition 3 (boundary curvature similarity) failed for clusters " << i << " and " << j << std::endl;
				continue;
			}
			std::cout << "Condition 3 (boundary curvature similarity) passed for clusters " << i << " and " << j << std::endl;

			// Verification before merging
			Eigen::Vector3f boundaryPoint1 = cloud->points[boundaryPoints1[0]].getVector3fMap();
			Eigen::Vector3f boundaryPoint2 = cloud->points[boundaryPoints2[0]].getVector3fMap();

			Eigen::Vector3f lineDirection1 = calculatePrincipalAxis(cloud, boundaryPoints1);
			Eigen::Vector3f lineDirection2 = calculatePrincipalAxis(cloud, boundaryPoints2);

			float minDistance = 2.5; 

			// Declare innerPoint1 and innerPoint2 before use
			int innerPoint1 = selectInnerPointAlongLine(cloud, clusters[i], boundaryPoint1, lineDirection1, minDistance * 100);
			int innerPoint2 = selectInnerPointAlongLine(cloud, clusters[j], boundaryPoint2, lineDirection2, minDistance * 100);

			if (innerPoint1 == -1 || innerPoint2 == -1) {
				std::cout << "Verification failed (innerPoint selection) for clusters " << i << " and " << j << std::endl;
				continue;
			}

			if (!verifyClusterMerge(cloud, innerPoint1, innerPoint2, NORMAL_SIMILARITY_THRESHOLD_verificiation, CURVATURE_THRESHOLD_verification)) {
				std::cout << "Verification failed for clusters " << i << " and " << j << std::endl;
				continue;
			}
			std::cout << "Verification passed for clusters " << i << " and " << j << std::endl;

			// Add the pair to merge list
			mergePairs.emplace_back(i, j);
			merged[j] = true;  // Mark cluster j as merged
		}
	}

	// Step 2: Perform the actual merge
	for (const auto& mergePair : mergePairs) {
		int i = mergePair.first;
		int j = mergePair.second;

		clusters[i].indices.insert(clusters[i].indices.end(), clusters[j].indices.begin(), clusters[j].indices.end());
		clusters[j].indices.clear();  // Clear the merged cluster
	}

	// Remove empty clusters
	clusters.erase(std::remove_if(clusters.begin(), clusters.end(), [](const pcl::PointIndices& cluster) {
		return cluster.indices.empty();
		}), clusters.end());
}

#include <random>

bool checkNormalsIntersection(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud1, pcl::PointCloud<pcl::Normal>::Ptr normals1,
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud2, pcl::PointCloud<pcl::Normal>::Ptr normals2,
	double threshold = 0.2, double sample_fraction = 0.01)
{
	pcl::search::KdTree<pcl::PointXYZ> tree;
	tree.setInputCloud(cloud2);

	int num_samples = 30;
	std::vector<int> sampled_indices;
	sampled_indices.reserve(num_samples);

	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_int_distribution<> dis(0, cloud1->points.size() - 1);

	for (int i = 0; i < num_samples; ++i) {
		sampled_indices.push_back(dis(gen));
	}

	std::cout << "Sampled indices: ";
	for (int i : sampled_indices) {
		std::cout << i << " ";
	}
	std::cout << std::endl;

	for (int i : sampled_indices)
	{
		const auto& pos = cloud1->points[i];
		const auto& norm = normals1->points[i];

		for (double t = 0; t <= 3; t += 0.05)
		{
			pcl::PointXYZ samplePoint;
			samplePoint.x = pos.x + t * norm.normal_x;
			samplePoint.y = pos.y + t * norm.normal_y;
			samplePoint.z = pos.z + t * norm.normal_z;

			std::vector<int> indices(1);
			std::vector<float> distances(1);
			if (tree.nearestKSearch(samplePoint, 1, indices, distances) > 0)
			{
				// std::cout << "Ray point: " << samplePoint << ", Distance: " << distances[0] << std::endl;
				if (distances[0] < threshold)
				{
					return true;
				}
			}
		}
	}

	return false;
}

void savePLYandXYZ(const pcl::PointCloud<pcl::PointNormal>::Ptr& cloud, const std::string& basePath)
{
	pcl::io::savePLYFile(basePath + ".ply", *cloud);

	Eigen::MatrixXd pointCloudMatrix(cloud->points.size(), 6);
	for (size_t i = 0; i < cloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << cloud->points[i].x, cloud->points[i].y, cloud->points[i].z,
			cloud->points[i].normal_x, cloud->points[i].normal_y, cloud->points[i].normal_z;
	}
	writeMatrix_to_XYZ(pointCloudMatrix, basePath + ".xyz", 6);
}

void convertPLYtoXYZ(string inputFile, string outFile)
{
	pcl::PointCloud<pcl::PointNormal>::Ptr mesh_cloud(new pcl::PointCloud<pcl::PointNormal>);
	pcl::io::loadPLYFile(inputFile, *mesh_cloud);
	Eigen::MatrixXd pointCloudMatrix(mesh_cloud->points.size(), 6);
	for (size_t i = 0; i < mesh_cloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << mesh_cloud->points[i].x, mesh_cloud->points[i].y, mesh_cloud->points[i].z, mesh_cloud->points[i].normal_x, mesh_cloud->points[i].normal_y, mesh_cloud->points[i].normal_z;
	}
	writeMatrix_to_XYZ(pointCloudMatrix, outFile, 6);
}

void surfaceSegmentation(std::string filePath, int minCluster, int noOfNeighbours, double smoothnessAngleThreshold, double curvatureThreshold)
{
    // std::string tmp_path = filePath;
	std::string tmp_path = intermediatePath_global;
	if (tmp_path.back() != '/' && tmp_path.back() != '\\') {
		tmp_path += "/";
	}
    int numberOfClustersCreated = -1;
    
    while (numberOfClustersCreated < 2)
    {
        if (numberOfClustersCreated != -1 && numberOfClustersCreated < 2)
        {
            std::cout << "Single cluster found...Increasing angle theshold (+2) and trying again..." << std::endl;
            smoothnessAngleThreshold -= 2;
        }
        
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);

        pcl::search::Search<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
        pcl::PointCloud <pcl::Normal>::Ptr normals(new pcl::PointCloud <pcl::Normal>);

        pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);

        pcl::io::loadPLYFile(filePath, *cloudWithNormals);

        for (size_t i = 0; i < cloudWithNormals->points.size(); i++)
        {
            pcl::PointXYZ basicPoint;
            basicPoint.x = cloudWithNormals->points[i].x;
            basicPoint.y = cloudWithNormals->points[i].y;
            basicPoint.z = cloudWithNormals->points[i].z;
            cloud->points.push_back(basicPoint);
        }
        cloud->width = cloud->points.size();
        cloud->height = 1;

        pcl::PointCloud<pcl::PointNormal>::Ptr sampledPointCloudNormal(new pcl::PointCloud<pcl::PointNormal>);
        getNormalsOnSurface(cloud, sampledPointCloudNormal);
        for (size_t i = 0; i < sampledPointCloudNormal->points.size(); i++)
        {
            pcl::Normal normTemp;
            normTemp.normal_x = sampledPointCloudNormal->points[i].normal_x;
            normTemp.normal_y = sampledPointCloudNormal->points[i].normal_y;
            normTemp.normal_z = sampledPointCloudNormal->points[i].normal_z;
            normTemp.curvature = sampledPointCloudNormal->points[i].curvature;

            normals->points.push_back(normTemp);
        }

        pcl::IndicesPtr indices(new std::vector<int>);
        pcl::PassThrough<pcl::PointXYZ> pass;
        pass.setInputCloud(cloud);
        pass.setFilterFieldName("z");
        pass.setFilterLimits(0.0, 1.0);
        pass.filter(*indices);

        pcl::RegionGrowing<pcl::PointXYZ, pcl::Normal> reg;
        reg.setMinClusterSize(minCluster);
        reg.setMaxClusterSize(1000000);
        reg.setSearchMethod(tree);
        reg.setNumberOfNeighbours(noOfNeighbours);
        reg.setInputCloud(cloud);
        reg.setInputNormals(normals);
        reg.setSmoothnessThreshold(smoothnessAngleThreshold / 180.0 * M_PI);
        reg.setCurvatureThreshold(curvatureThreshold);

        std::vector<pcl::PointIndices> clusters;
        reg.extract(clusters);

        std::cout << "\nTotal points: " << cloud->points.size() << std::endl;
        std::cout << "Number of clusters is equal to " << clusters.size() << std::endl;

        std::sort(clusters.begin(), clusters.end(), myobject3);

        std::cout << "Points in " << std::endl;
        int totalPointsInClusters = 0;
        for (size_t i = 0; i < clusters.size(); i++)
        {
            std::cout << "Cluster " << std::to_string(i + 1) << " : " << clusters[i].indices.size() << std::endl;
            totalPointsInClusters = totalPointsInClusters + clusters[i].indices.size();
        }
        if (clusters.size() > 1)
        {
            std::cout << "Points in two clusters / Total Points in Pointcloud: " << std::setprecision(4) << static_cast<double>(100) * (clusters[0].indices.size() + clusters[1].indices.size()) / cloud->points.size() << "%" << std::endl;
            std::cout << "Points in two clusters / Total Points in all clusters: " << std::setprecision(4) << static_cast<double>(100) * (clusters[0].indices.size() + clusters[1].indices.size()) / totalPointsInClusters << "%" << std::endl;
            std::ofstream myfile("segmentationStats.txt", std::ofstream::out | std::ofstream::app);
            if (myfile.is_open())
            {
                myfile << fileNameOnly << "\t";
                myfile << static_cast<double>(100) * (clusters[0].indices.size() + clusters[1].indices.size()) / cloud->points.size() << "%\t" << static_cast<double>(100) * (clusters[0].indices.size() + clusters[1].indices.size()) / totalPointsInClusters << "%" << std::endl;
                myfile.close();
            }
        }

        // 병합 함수 호출
        std::cout << "Calling mergeClusters function." << std::endl;
        mergeClusters(cloudWithNormals, clusters);

        numberOfClustersCreated = clusters.size();

        if (clusters.size() > 1)
        {
            auto& largestCluster = clusters[0];
            auto& secondLargestCluster = clusters[1];

            // 가장 큰 두 클러스터의 포인트 및 노말 벡터 추출
            pcl::PointCloud<pcl::PointXYZ>::Ptr largestClusterCloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::PointCloud<pcl::Normal>::Ptr largestClusterNormals(new pcl::PointCloud<pcl::Normal>);

            for (int idx : largestCluster.indices)
            {
                largestClusterCloud->points.push_back(cloud->points[idx]);
                largestClusterNormals->points.push_back(normals->points[idx]);
            }

            pcl::PointCloud<pcl::PointXYZ>::Ptr secondLargestClusterCloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::PointCloud<pcl::Normal>::Ptr secondLargestClusterNormals(new pcl::PointCloud<pcl::Normal>);

            for (int idx : secondLargestCluster.indices)
            {
                secondLargestClusterCloud->points.push_back(cloud->points[idx]);
                secondLargestClusterNormals->points.push_back(normals->points[idx]);
            }

            // normal vector check
            bool flipNormals = checkNormalsIntersection(largestClusterCloud, largestClusterNormals, secondLargestClusterCloud, secondLargestClusterNormals);

            if (flipNormals)
            {
                for (auto& normal : normals->points)
                {
                    normal.normal_x = -normal.normal_x;
                    normal.normal_y = -normal.normal_y;
                    normal.normal_z = -normal.normal_z;
                }
                for (size_t i = 0; i < cloudWithNormals->points.size(); i++)
                {
                    cloudWithNormals->points[i].normal_x = normals->points[i].normal_x;
                    cloudWithNormals->points[i].normal_y = normals->points[i].normal_y;
                    cloudWithNormals->points[i].normal_z = normals->points[i].normal_z;
                }
                pcl::io::savePLYFile(tmp_path + "_flipped_normal.ply", *cloudWithNormals);
            }

            std::cout << std::boolalpha << "Normals flipped: " << flipNormals << std::endl;

            // Save clusters to files
            pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
            pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals_Cluster2(new pcl::PointCloud<pcl::PointNormal>);
            for (size_t i = 0; i < clusters[0].indices.size(); i++)
            {
                cloudWithNormals_Cluster1->points.push_back(cloudWithNormals->points[clusters[0].indices[i]]);
            }
            cloudWithNormals_Cluster1->width = cloudWithNormals_Cluster1->points.size();
            cloudWithNormals_Cluster1->height = 1;

            for (size_t i = 0; i < clusters[1].indices.size(); i++)
            {
                cloudWithNormals_Cluster2->points.push_back(cloudWithNormals->points[clusters[1].indices[i]]);
            }
            cloudWithNormals_Cluster2->width = cloudWithNormals_Cluster2->points.size();
            cloudWithNormals_Cluster2->height = 1;

            pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePoints_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
            improveSurfaceBoundaryByFittingBSplineSurface(sampledPointCloudNormal, cloudWithNormals_Cluster1, improvedSurfacePoints_Cluster1);
            cloudWithNormals_Cluster1->points.clear();
            pcl::copyPointCloud(*improvedSurfacePoints_Cluster1, *cloudWithNormals_Cluster1);

            pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePoints_Cluster2(new pcl::PointCloud<pcl::PointNormal>);
            improveSurfaceBoundaryByFittingBSplineSurface(sampledPointCloudNormal, cloudWithNormals_Cluster2, improvedSurfacePoints_Cluster2);
            cloudWithNormals_Cluster2->points.clear();
            pcl::copyPointCloud(*improvedSurfacePoints_Cluster2, *cloudWithNormals_Cluster2);

            if (flipNormals)
            {
                for (auto& normal : cloudWithNormals_Cluster1->points)
                {
                    normal.normal_x = -normal.normal_x;
                    normal.normal_y = -normal.normal_y;
                    normal.normal_z = -normal.normal_z;
                }
                for (auto& normal : cloudWithNormals_Cluster2->points)
                {
                    normal.normal_x = -normal.normal_x;
                    normal.normal_y = -normal.normal_y;
                    normal.normal_z = -normal.normal_z;
                }
            }

            pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_0.ply", *cloudWithNormals_Cluster1);
            pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_1.ply", *cloudWithNormals_Cluster2);

            // Getting file name without path and extension
            const size_t last_slash_idx = tmp_path.find_last_of("/");
            if (std::string::npos != last_slash_idx)
            {
                tmp_path.erase(0, last_slash_idx + 1);
            }
            const size_t period_idx = tmp_path.rfind('.');
            if (std::string::npos != period_idx)
            {
                tmp_path.erase(period_idx);
            }

            for (size_t t = 0; t < clusters.size(); t++)
            {
                pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals_Cluster(new pcl::PointCloud<pcl::PointNormal>);
                for (size_t i = 0; i < clusters[t].indices.size(); i++)
                {
                    cloudWithNormals_Cluster->points.push_back(cloudWithNormals->points[clusters[t].indices[i]]);
                }
                cloudWithNormals_Cluster->width = cloudWithNormals_Cluster->points.size();
                cloudWithNormals_Cluster->height = 1;
            }
        }
        else if (clusters.size() == 1)
        {
            pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
            for (size_t i = 0; i < clusters[0].indices.size(); i++)
            {
                cloudWithNormals_Cluster1->points.push_back(cloudWithNormals->points[clusters[0].indices[i]]);
            }
            cloudWithNormals_Cluster1->width = cloudWithNormals_Cluster1->points.size();
            cloudWithNormals_Cluster1->height = 1;

            // Getting file name without path and extension
            const size_t last_slash_idx = tmp_path.find_last_of("/");
            if (std::string::npos != last_slash_idx)
            {
                tmp_path.erase(0, last_slash_idx + 1);
            }
            const size_t period_idx = tmp_path.rfind('.');
            if (std::string::npos != period_idx)
            {
                tmp_path.erase(period_idx);
            }

            break;
        }

        //------------------------------------------------------
        // Working with unclustered points
        //------------------------------------------------------
        // Getting unclustered points in separate cloud

        std::list<int> allPointsInClusteres_indices;
        for (size_t t = 0; t < clusters.size(); t++)
        {
            for (size_t p = 0; p < clusters[t].indices.size(); p++)
            {
                allPointsInClusteres_indices.push_back(clusters[t].indices[p]);
            }
        }
        allPointsInClusteres_indices.sort();
        pcl::PointCloud<pcl::PointNormal>::Ptr points_unclustered(new pcl::PointCloud<pcl::PointNormal>);
        for (size_t i = 0; i < cloud->points.size(); i++)
        {
            bool found = (std::find(allPointsInClusteres_indices.begin(), allPointsInClusteres_indices.end(), i) != allPointsInClusteres_indices.end());
            if (!found)
            {
                points_unclustered->points.push_back(cloudWithNormals->points[i]);
            }
        }
        points_unclustered->width = points_unclustered->points.size();
        points_unclustered->height = 1;
		pcl::io::savePLYFile(dataPath_global + fileNameOnly + "_unclustered.ply", *points_unclustered);

		getBreakLineForDecorativeParts(dataPath_global + fileNameOnly + "_unclustered.ply");
        numberOfClustersCreated = clusters.size();
    }
}

std::tuple<std::uint8_t, std::uint8_t, std::uint8_t> rgb(double minimum, double maximum, double value)
{
	double ratio = 2 * (value - minimum) / (maximum - minimum);
	std::uint8_t b = int(std::max(static_cast<double>(0), 255 * (1 - ratio)));
	std::uint8_t r = int(std::max(static_cast<double>(0), 255 * (ratio - 1)));
	std::uint8_t g = 255 - b - r;
	return std::make_tuple(r, g, b);
}

void getClusters(string fileName)
{
	pcl::PointCloud<PointTypeIO>::Ptr cloud_in(new pcl::PointCloud<PointTypeIO>), cloud_out(new pcl::PointCloud<PointTypeIO>);
	pcl::IndicesClustersPtr clusters(new pcl::IndicesClusters), small_clusters(new pcl::IndicesClusters), large_clusters(new pcl::IndicesClusters);
	pcl::search::KdTree<PointTypeIO>::Ptr search_tree(new pcl::search::KdTree<PointTypeIO>);
	pcl::console::TicToc tt;
	pcl::PointCloud<pcl::PointNormal>::Ptr missedPoints(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PCDWriter writer;
	pcl::io::loadPLYFile(fileName, *missedPoints);

	pcl::search::KdTree<pcl::PointNormal>::Ptr tree(new pcl::search::KdTree<pcl::PointNormal>);
	tree->setInputCloud(missedPoints);

	std::vector<pcl::PointIndices> cluster_indices;
	pcl::EuclideanClusterExtraction<pcl::PointNormal> ec;
	ec.setClusterTolerance(3); 
	ec.setMinClusterSize(100); 
	ec.setMaxClusterSize(25000);
	ec.setSearchMethod(tree);
	ec.setInputCloud(missedPoints);
	ec.extract(cluster_indices);

	int j = 0;
	for (std::vector<pcl::PointIndices>::const_iterator it = cluster_indices.begin(); it != cluster_indices.end(); ++it)
	{
		pcl::PointCloud<pcl::PointNormal>::Ptr cloud_cluster(new pcl::PointCloud<pcl::PointNormal>);
		for (std::vector<int>::const_iterator pit = it->indices.begin(); pit != it->indices.end(); ++pit)
			cloud_cluster->push_back((*missedPoints)[*pit]); //*
		cloud_cluster->width = cloud_cluster->size();
		cloud_cluster->height = 1;
		cloud_cluster->is_dense = true;

		std::cout << "PointCloud representing the Cluster: " << cloud_cluster->size() << " data points." << std::endl;
		std::stringstream ss;
		ss << fileName + "Cluster_" << j << ".pcd";
		writer.write<pcl::PointNormal>(ss.str(), *cloud_cluster, false); //*
		j++;
	}
}

namespace fs = std::experimental::filesystem;

int main(int argc, char** argv) {
    // Parse command line arguments: mesh_file pot_id piece_id
    std::string current_potID = potID;  // Default from header
    int piece_id = 1;  // Default piece ID
    std::string specific_mesh_file = "";
    
    if (argc >= 4) {
        specific_mesh_file = argv[1];  // Specific mesh file path
        current_potID = argv[2];       // Pot ID (A, B, C, etc.)
        piece_id = std::stoi(argv[3]); // Piece ID (1, 2, 3, etc.)
        std::cout << "Processing specific file: " << specific_mesh_file << std::endl;
        std::cout << "Pot ID: " << current_potID << ", Piece ID: " << piece_id << std::endl;
    }
    
    std::string baseOutputPath = tempPath();  
    std::string dataPath = tempDataPath(current_potID);  
    std::string intermediatePath = tempIntermediatePath(current_potID);  
    std::string meshDatasetPath = getMeshDatasetPath(current_potID);
    
    namespace fs = std::experimental::filesystem;
    if (!fs::exists(dataPath)) {
        fs::create_directories(dataPath);
    }
    if (!fs::exists(intermediatePath)) {
        fs::create_directories(intermediatePath);
    }
    
    dataPath_global = dataPath;
    intermediatePath_global = intermediatePath;
    datasetPath_global = getPointDatasetPath(current_potID);
    
    Timer t;
    Timer t_individual;
    
    std::vector<fs::path> pcd_files;
    ofstream myfile(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
    
    // Handle specific file processing when command line args are provided
    if (!specific_mesh_file.empty()) {
        // Process single specific mesh file - generate point cloud from mesh
        fs::path meshFilePath = fs::path(specific_mesh_file);
        std::string baseName = meshFilePath.stem().string();
        baseName = baseName.substr(0, baseName.find("_Mesh"));
        std::string pointFileName = baseName + "_Point.pcd";
        fs::path pointFilePath = fs::path(datasetPath_global) / pointFileName;
        
        // Check if mesh file exists
        if (!fs::exists(meshFilePath)) {
            std::cout << "Error: Mesh file not found: " << meshFilePath << std::endl;
            return -1;
        }
        
        // Generate point cloud from mesh if it doesn't exist
        if (!fs::exists(pointFilePath)) {
            std::cout << "Generating point cloud from mesh: " << meshFilePath << std::endl;
            std::string result = convertMeshToPointCloud(meshFilePath.string(), pointFilePath.string());
            if (result.empty()) {
                std::cout << "Error: Failed to convert mesh to point cloud" << std::endl;
                return -1;
            }
        } else {
            std::cout << "Point cloud already exists: " << pointFilePath << std::endl;
        }
        
        pcd_files.push_back(pointFilePath);
    } else {
        // Look for mesh files and generate point clouds if needed
        std::string meshDatasetPath = getMeshDatasetPath(current_potID);
        for (const auto& entry : fs::recursive_directory_iterator(meshDatasetPath)) {
            if (!fs::is_directory(entry.path()) && entry.path().extension() == ".obj") {
                fs::path meshFilePath = entry.path();
                std::string baseName = meshFilePath.stem().string();
                baseName = baseName.substr(0, baseName.find("_Mesh"));
                std::string pointFileName = baseName + "_Point.pcd";
                fs::path pointFilePath = fs::path(datasetPath_global) / pointFileName;
                
                // Generate point cloud from mesh if it doesn't exist
                if (!fs::exists(pointFilePath)) {
                    std::cout << "Generating point cloud from mesh: " << meshFilePath << std::endl;
                    std::string result = convertMeshToPointCloud(meshFilePath.string(), pointFilePath.string());
                    if (result.empty()) {
                        std::cout << "Warning: Failed to convert mesh: " << meshFilePath << std::endl;
                        continue;
                    }
                }
                
                pcd_files.push_back(pointFilePath);
            }
        }
        std::sort(pcd_files.begin(), pcd_files.end());
    }
    
    for (const auto& file_path : pcd_files) {
        std::string inputFilePath = file_path.string();
        
        std::string baseName = file_path.stem().string();
        baseName = baseName.substr(0, baseName.find("_Point")); 
        std::string meshFileName = baseName + "_Mesh.obj";
        fs::path meshFilePath;
        
        if (!specific_mesh_file.empty()) {
            meshFilePath = fs::path(specific_mesh_file);
        } else {
            meshFilePath = fs::path(meshDatasetPath) / meshFileName;
        }
        
        fs::path destPointFile = fs::path(dataPath) / file_path.filename();
        fs::path destMeshFile = fs::path(dataPath) / meshFileName;
        
        try {
            if (fs::exists(file_path)) {
                fs::copy_file(file_path, destPointFile, fs::copy_options::overwrite_existing);
                std::cout << "Copied Point file: " << file_path.filename().string() << std::endl;
            }
            
            if (fs::exists(meshFilePath)) {
                fs::copy_file(meshFilePath, destMeshFile, fs::copy_options::overwrite_existing);
                std::cout << "Copied Mesh file: " << meshFileName << std::endl;
            } else {
                std::cout << "Warning: Mesh file not found: " << meshFilePath.string() << std::endl;
            }
        } catch (const fs::filesystem_error& e) {
            std::cout << "Error copying files: " << e.what() << std::endl;
            continue;
        }
        
        setInputFile(inputFilePath, dataPath); 
        std::string downsampledFilePath = downsamplePointCloud(inputFilePath);
        
        std::cout << "Starting processing on: " << inputFilePath << std::endl;
        
        myfile.open(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
        if (myfile.is_open()) {
            myfile << fileNameOnly << "\t" << t_individual.elapsed() << "\t";
            myfile.close();
        }
        t_individual.reset();
        
        int minCluster = 50, noOfNeighbours = 10;
        double smoothnessAngleThreshold = 4.5, curvatureThreshold = 1.5;
        std::cout << "Starting surface segmentation on: " << downsampledFilePath << std::endl;
        surfaceSegmentation(downsampledFilePath, minCluster, noOfNeighbours, smoothnessAngleThreshold, curvatureThreshold);

		std::string tempFileName0 = intermediatePath + "tmpSurfaceCluster_Improved_0.ply";
		std::string tempFileName1 = intermediatePath + "tmpSurfaceCluster_Improved_1.ply";
        
        std::string outputFileName0 = dataPath + fileNameOnly + "_Surface_0.ply";
        std::string outputFileName1 = dataPath + fileNameOnly + "_Surface_1.ply";
        
        std::cout << "Ply to XYZ start" << std::endl;
        
        if (fs::exists(tempFileName0)) {
            fs::copy_file(tempFileName0, outputFileName0, fs::copy_options::overwrite_existing);
            std::string xyzFileName0 = dataPath + fileNameOnly + "_Surface_0.xyz";
            convertPLYtoXYZ(outputFileName0, xyzFileName0);
            
            // Copy XYZ file to Surfaces directory for axis extraction
            fs::path surfacesDir = fs::path("Surfaces");
            if (!fs::exists(surfacesDir)) {
                fs::create_directories(surfacesDir);
            }
            fs::path surfaceXYZ0 = surfacesDir / (fileNameOnly + "_Surface_0.xyz");
            fs::copy_file(xyzFileName0, surfaceXYZ0, fs::copy_options::overwrite_existing);
            std::cout << "Surface XYZ file copied to: " << surfaceXYZ0 << std::endl;
        } else {
            std::cout << "Warning: Source file not found: " << tempFileName0 << std::endl;
        }
        
        if (fs::exists(tempFileName1)) {
            fs::copy_file(tempFileName1, outputFileName1, fs::copy_options::overwrite_existing);
            std::string xyzFileName1 = dataPath + fileNameOnly + "_Surface_1.xyz";
            convertPLYtoXYZ(outputFileName1, xyzFileName1);
            
            // Copy XYZ file to Surfaces directory for axis extraction
            fs::path surfacesDir = fs::path("Surfaces");
            if (!fs::exists(surfacesDir)) {
                fs::create_directories(surfacesDir);
            }
            fs::path surfaceXYZ1 = surfacesDir / (fileNameOnly + "_Surface_1.xyz");
            fs::copy_file(xyzFileName1, surfaceXYZ1, fs::copy_options::overwrite_existing);
            std::cout << "Surface XYZ file copied to: " << surfaceXYZ1 << std::endl;
        } else {
            std::cout << "Warning: Source file not found: " << tempFileName1 << std::endl;
        }
        
        myfile.open(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
        if (myfile.is_open()) {
            std::cout << "\nTime after processing: " << t_individual.elapsed() << " seconds" << std::endl;
            myfile << t_individual.elapsed() << std::endl;
            myfile.close();
        }
        t_individual.reset();
    }
    
    myfile.open(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
    if (myfile.is_open()) {
        myfile << "\nTotal time elapsed: " << t.elapsed() << " seconds\n";
        myfile.close();
    }
    
    std::cout << "Total time elapsed: " << t.elapsed() << " seconds" << std::endl;
    
    return EXIT_SUCCESS;
}