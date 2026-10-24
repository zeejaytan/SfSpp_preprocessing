// Headless version - removed Windows graphics libraries

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
// Removed VTK headers for headless build (PCL built with -DWITH_VTK=OFF)
// #include <pcl/io/vtk_lib_io.h>
// #include <pcl/io/impl/vtk_lib_io.hpp>
// Removed visualization header for headless operation
#include <pcl/console/parse.h>
#include <pcl/common/transforms.h>
#define _SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING
#include <experimental/filesystem>

#define PCL_NO_PRECOMPILE 1

#define VTK_LEGACY_SILENT

#include <string>
#include <filesystem>
#include <stdio.h>
#include <cstdlib>  // TICKET 234: getenv
#include <pcl/filters/uniform_sampling.h>

#include <chrono>
#include <thread>

#include <pcl/point_types.h>
// Removed all VTK smoothing headers for headless build
// #include <pcl/io/vtk_io.h>
// #include <pcl/surface/vtk_smoothing/vtk.h>
// #include <pcl/surface/vtk_smoothing/vtk_mesh_smoothing_laplacian.h>
// #include <pcl/surface/vtk_smoothing/vtk_utils.h>
// #include <vtkSmartPointer.h>
// #include <vtkSmoothPolyDataFilter.h>
#include <pcl/io/ply_io.h>
#include <pcl/surface/convex_hull.h>
#include <pcl/surface/concave_hull.h>
#include <pcl/common/common.h>
#include <pcl/sample_consensus/sac_model_plane.h>
#include <pcl/filters/project_inliers.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/sac_segmentation.h>

// Removed cloud viewer header for headless operation
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
// Removed point picking header for headless operation


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
#include <tiny_obj_loader.h>
#include <pcl/tracking/normal_coherence.h>
//#include <Windows.h>


using namespace pcl;
using namespace pcl::io;
using namespace std;

using namespace pcl;
using namespace pcl::io;
using namespace pcl::console;

#include <pcl/point_cloud.h>

#include <pcl/surface/on_nurbs/fitting_surface_tdm.h>
#include <pcl/surface/on_nurbs/fitting_curve_2d_asdm.h>
#include <pcl/surface/on_nurbs/triangulation.h>
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
// Removed ColorHandlerXYZ typedef for headless operation
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
std::string datasetPath_global = getPointDatasetPath(potID); 

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

void writeMatrix_to_XYZ(Eigen::MatrixXd& src, string fileName, int cols = 3, bool convertToMM = true)
{
	ofstream writeStream(fileName, ios::out | ios::trunc);
	if (writeStream)
	{
		// Check if this is for CGAL processing (temporary files)
		bool isCGALFile = (fileName.find("fileForNormalEst") != string::npos);
		// Check if this is for EdgeLineExtraction (Surface_ files need clean XYZ without headers)
		bool isEdgeLineFile = (fileName.find("_Surface_") != string::npos);

		if (!isCGALFile && !isEdgeLineFile) {
			// Add SFS-compatible header format only for final output files (not Surface_ files)
			writeStream << "# SFS-compatible surface file" << endl;
			writeStream << "# 1 " << src.rows() << " 1" << endl;
			writeStream << "segment 0 0 " << (src.rows() - 1) << endl;
			// Add padding lines to match expected header structure (total 12 lines)
			for (int i = 0; i < 9; i++) {
				writeStream << "#" << endl;
			}
		}

		for (size_t i = 0; i < src.rows(); i++)
		{
			for (size_t j = 0; j < cols; j++)
			{
				double value = src(i, j);
				// Convert coordinates (x,y,z) to millimeters, keep normals as-is
				if (convertToMM && j < 3) {
					value *= 1000.0;  // meters to millimeters
				}
				writeStream << value << " ";
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

// Adaptive parameter infrastructure for sparse/dense point clouds
struct AdaptiveParams {
    int k_neighbors;        // For KNN searches
    double radius_mm;       // For radius searches (in millimeters)
    int min_cluster;        // For clustering
    int max_cluster;
    double boundary_radius_m; // For boundary detection (in meters)
};

AdaptiveParams computeAdaptiveParams(int num_points, double avg_spacing_m) {
    AdaptiveParams p;
    double avg_spacing_mm = avg_spacing_m * 1000.0;

    // K neighbors: scale with density, clamp 5-50
    p.k_neighbors = std::max(5, std::min(50, num_points / 200));

    // Radius searches: 3-5× average point spacing
    p.radius_mm = std::max(0.5, std::min(10.0, avg_spacing_mm * 4.0));

    // Clustering: 0.2-1% of points
    p.min_cluster = std::max(10, std::min(100, num_points / 500));
    p.max_cluster = std::max(1000, num_points * 3);

    // Boundary: 5-7× spacing in meters
    p.boundary_radius_m = std::max(0.001, std::min(0.015, avg_spacing_m * 6.0));

    std::cout << "[ADAPTIVE PARAMS] N=" << num_points << ", spacing=" << avg_spacing_mm
              << "mm, K=" << p.k_neighbors << ", boundary_r=" << (p.boundary_radius_m*1000)
              << "mm, cluster=[" << p.min_cluster << "-" << p.max_cluster << "]" << std::endl;

    return p;
}

// Forward declarations for curvature computation
std::vector<int> getKNNPoints(const Eigen::Vector3f& center_point, const pcl::PointCloud<pcl::PointNormal>::Ptr& cloud, int K);
std::pair<float, float> getCurvature(const Eigen::Vector3f& center_point, const Eigen::Vector3f& center_normal, const std::vector<Eigen::Vector3f>& knn_points);

bool getNormalsOnSurface(pcl::PointCloud<Point>::Ptr sampledPointCloud, pcl::PointCloud<pcl::PointNormal>::Ptr surfaceWithNormals)
{
	std::cout << "[DEBUG getNormalsOnSurface] Starting function. Input points: " << sampledPointCloud->points.size() << std::endl;
	string fragmentMeshFile = "fileForNormalEst";
	std::cout << "[DEBUG getNormalsOnSurface] Creating Eigen matrix..." << std::endl;
	Eigen::MatrixXd pointCloudMatrix(sampledPointCloud->points.size(), 3);
	for (size_t i = 0; i < sampledPointCloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << sampledPointCloud->points[i].x, sampledPointCloud->points[i].y, sampledPointCloud->points[i].z;
	}
	std::cout << "[DEBUG getNormalsOnSurface] Writing matrix to XYZ file..." << std::endl;
	writeMatrix_to_XYZ(pointCloudMatrix, fragmentMeshFile + "_Sampled.xyz", 3, false);

	string fName = fragmentMeshFile + "_Sampled.xyz";
	const char* fname = fName.c_str();
	// Reads a .xyz point set file in points[].
	std::cout << "[DEBUG getNormalsOnSurface] Reading XYZ file: " << fname << std::endl;
	std::list<PointVectorPair> points;
	std::ifstream stream(fname);
	if (!stream ||
		!CGAL::IO::read_XYZ(stream,
			std::back_inserter(points),
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>())))
	{
		std::cerr << "Error: cannot read file " << fname << std::endl;
		return false;
	}
	std::cout << "[DEBUG getNormalsOnSurface] XYZ file read successfully. Points loaded: " << points.size() << std::endl;

	// ADAPTIVE: Scale K neighbors with density (5 for dense, 15-20 for sparse)
	int nb_neighbors = std::max(5, std::min(20, (int)points.size() / 1000));
	std::cout << "[ADAPTIVE CGAL] Using " << nb_neighbors << " neighbors for "
	          << points.size() << " points (density-aware)" << std::endl;

	// Estimates normals direction.
	CGAL::pca_estimate_normals<Concurrency_tag>
		(points, nb_neighbors,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	std::cout << "[DEBUG getNormalsOnSurface] PCA normal estimation complete." << std::endl;

	// Orients normals.
	std::cout << "[DEBUG getNormalsOnSurface] Orienting normals with MST..." << std::endl;
	std::list<PointVectorPair>::iterator unoriented_points_begin =
		CGAL::mst_orient_normals(points, nb_neighbors,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	std::cout << "[DEBUG getNormalsOnSurface] MST orientation complete." << std::endl;
	points.erase(unoriented_points_begin, points.end());
	std::cout << "[DEBUG getNormalsOnSurface] Erased unoriented points. Remaining: " << points.size() << std::endl;


	/// Saves point set.
	std::ofstream out(fragmentMeshFile + "_SampledWithNormals.xyz");
	out.precision(17);
	if (!out ||
		!CGAL::IO::write_XYZ(
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

	// CRITICAL FIX: Compute curvature using PCL's robust PCA-based estimation
	std::cout << "[DEBUG getNormalsOnSurface] Computing curvature for " << surfaceWithNormals->points.size() << " points..." << std::endl;

	// Use PCL's NormalEstimation which computes curvature from PCA eigenvalues
	pcl::NormalEstimation<pcl::PointNormal, pcl::PointNormal> ne;
	pcl::search::KdTree<pcl::PointNormal>::Ptr tree(new pcl::search::KdTree<pcl::PointNormal>());
	ne.setInputCloud(surfaceWithNormals);
	ne.setSearchMethod(tree);

	// ADAPTIVE: Scale curvature K with density (10-50 range)
	int curv_k = std::max(10, std::min(50, (int)surfaceWithNormals->points.size() / 300));
	ne.setKSearch(curv_k);
	std::cout << "[ADAPTIVE CURVATURE] Using K=" << curv_k << " for "
	          << surfaceWithNormals->points.size() << " points" << std::endl;

	// Compute curvature (stored in the curvature field automatically)
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_with_curvature(new pcl::PointCloud<pcl::PointNormal>());
	ne.compute(*cloud_with_curvature);

	// Copy curvature values back to original cloud (positions/normals already correct)
	for (size_t i = 0; i < surfaceWithNormals->points.size(); i++)
	{
		surfaceWithNormals->points[i].curvature = cloud_with_curvature->points[i].curvature;
	}

	std::cout << "[DEBUG getNormalsOnSurface] Curvature computation complete." << std::endl;


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

	// Validate point cloud before saving
	if (surfaceWithNormals->points.empty()) {
		std::cerr << "Warning: Empty surface point cloud, skipping PLY save" << std::endl;
	} else {
		// Ensure all points have valid data
		bool valid = true;
		for (const auto& point : surfaceWithNormals->points) {
			if (!std::isfinite(point.x) || !std::isfinite(point.y) || !std::isfinite(point.z) ||
				!std::isfinite(point.normal_x) || !std::isfinite(point.normal_y) || !std::isfinite(point.normal_z)) {
				valid = false;
				break;
			}
		}
		if (valid) {
			std::cout << "[DEBUG getNormalsOnSurface] Saving PLY in ASCII mode..." << std::endl;
			pcl::io::savePLYFile(fragmentMeshFile + "_SampledWithNormals.ply", *surfaceWithNormals, false); // ASCII mode
		} else {
			std::cerr << "Error: Surface point cloud contains invalid data, skipping PLY save" << std::endl;
		}
	}
	return true;
}

#include <pcl/surface/mls.h>

pcl::PointCloud<pcl::PointNormal>::Ptr downsampledCloud(new pcl::PointCloud<pcl::PointNormal>);
pcl::UniformSampling<pcl::PointNormal> uniformSampler;
pcl::PointCloud<pcl::PointXYZ>::Ptr downsampledCloudPoints(new pcl::PointCloud<pcl::PointXYZ>);
pcl::PointCloud<pcl::PointNormal>::Ptr downsampledCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
std::string outputFile = "";

// POTA-244: targetSamples == 0 restores the pre-48fb588 fixed-radius path
// (pristine-splitwalk: UniformSampling at samplingRadius, no target loop);
// targetSamples < 0 skips downsampling (raw cloud, 48fb588); > 0 auto-tunes to target (48fb588).
// Default 0 = restored density. SFS_DOWNSAMPLE_TARGET=N overrides (19000 = current behavior).
std::string downsamplePointCloud(std::string inputPcdFile, float samplingRadius = 0.6F, int targetSamples = 0) {
	pcl::PointCloud<pcl::PointXYZ>::Ptr originalPointCloudXYZ(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointNormal>::Ptr originalPointCloud(new pcl::PointCloud<pcl::PointNormal>);

	if (pcl::io::loadPCDFile<pcl::PointXYZ>(inputPcdFile, *originalPointCloudXYZ) == -1) {
		PCL_ERROR("Couldn't read file\n");
		return "";
	}

	// Convert XYZ to PointNormal (normals will be computed later)
	pcl::copyPointCloud(*originalPointCloudXYZ, *originalPointCloud);

	pcl::PointCloud<pcl::PointNormal>::Ptr originalCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
	pcl::copyPointCloud(*originalPointCloud, *originalCloudWithNormals);

	// SPECIAL CASE: If targetSamples < 0, skip downsampling and use raw cloud
	if (targetSamples < 0) {
		std::cout << "[NO DOWNSAMPLING] Using raw point cloud with " << originalCloudWithNormals->size() << " points" << std::endl;
		// Use raw cloud directly - copy to downsampledCloud
		pcl::copyPointCloud(*originalCloudWithNormals, *downsampledCloud);
		pcl::copyPointCloud(*downsampledCloud, *downsampledCloudPoints);
		getNormalsOnSurface(downsampledCloudPoints, downsampledCloudWithNormals);

		pcl::PLYWriter writer;
		outputFile = outPath + fileNameOnly + "_SampledWithNormals.ply";
		std::cout << "[NO DOWNSAMPLING] Saving PLY with normals..." << std::endl;
		writer.write<pcl::PointNormal>(outputFile, *downsampledCloudWithNormals, false);
		return outputFile;
	}

	// POTA-244 RESTORE (targetSamples == 0): fixed-radius path, pre-48fb588 behavior.
	if (targetSamples == 0) {
		uniformSampler.setInputCloud(originalCloudWithNormals);
		uniformSampler.setRadiusSearch(samplingRadius);
		uniformSampler.filter(*downsampledCloud);
		std::cout << "[DOWNSAMPLING RESTORE-244] Fixed radius=" << std::fixed << std::setprecision(5) << samplingRadius
		          << ", input=" << originalCloudWithNormals->size() << " points, Result=" << downsampledCloud->size() << " points" << std::endl;
	} else {
	pcl::KdTreeFLANN<pcl::PointNormal> kdTree;
	kdTree.setInputCloud(originalCloudWithNormals);

    uniformSampler.setInputCloud(originalCloudWithNormals);

    // Estimate bounding box diagonal as proxy for scale
    float minx=std::numeric_limits<float>::max(), miny=minx, minz=minx;
    float maxx=-minx, maxy=-minx, maxz=-minx;
    for (const auto& p : originalPointCloudXYZ->points) {
        if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) continue;
        if (p.x < minx) minx = p.x; if (p.x > maxx) maxx = p.x;
        if (p.y < miny) miny = p.y; if (p.y > maxy) maxy = p.y;
        if (p.z < minz) minz = p.z; if (p.z > maxz) maxz = p.z;
    }
    float dx = maxx - minx, dy = maxy - miny, dz = maxz - minz;
    float diag = std::sqrt(dx*dx + dy*dy + dz*dz);

    // Target sample size and tolerance (with configurable targetSamples)
    const int lowerBound = targetSamples * 0.8;  // 80% of target
    const int upperBound = targetSamples * 1.2;  // 120% of target

    // Initialize leaf from scale (smaller -> denser). Start moderately dense.
    float leaf = std::max(0.0005f, 0.0015f * diag);
    int iter = 0;
    do {
        uniformSampler.setRadiusSearch(leaf);
        uniformSampler.filter(*downsampledCloud);
        if (downsampledCloud->size() > (size_t)upperBound) {
            // Too many points -> increase radius modestly
            leaf *= 1.25f;
        } else if (downsampledCloud->size() < (size_t)lowerBound) {
            // Too few -> shrink radius
            leaf *= 0.75f;
        } else {
            break;
        }
    } while (++iter < 12);

    // Safety minimum: ensure not extremely sparse
    if (downsampledCloud->size() < 2000) {
        int attempts = 0;
        while (downsampledCloud->size() < 2000 && leaf > 1e-5f && attempts < 8) {
            leaf *= 0.6f;
            uniformSampler.setRadiusSearch(leaf);
            uniformSampler.filter(*downsampledCloud);
            attempts++;
        }
    }

    // Log downsampling result
    std::cout << "[DOWNSAMPLING RESULT] Target=" << targetSamples << " points, "
              << "Bounds=[" << lowerBound << "-" << upperBound << "], "
              << "Result=" << downsampledCloud->size() << " points, "
              << "Radius(leaf)=" << std::fixed << std::setprecision(5) << leaf << std::endl;
	} // end POTA-244 adaptive branch (targetSamples > 0)

	pcl::copyPointCloud(*downsampledCloud, *downsampledCloudPoints);
    getNormalsOnSurface(downsampledCloudPoints, downsampledCloudWithNormals);

	pcl::PLYWriter writer;
	outputFile = outPath + fileNameOnly + "_SampledWithNormals.ply";
	std::cout << "[DEBUG downsamplePointCloud] Saving PLY in ASCII mode to avoid camera data issues..." << std::endl;
	writer.write<pcl::PointNormal>(outputFile, *downsampledCloudWithNormals, false); // Changed to ASCII (false) to avoid camera element
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

	// ADAPTIVE: Scale cluster size thresholds with point cloud density
	int num_pts = missedPoints->points.size();
	int min_cluster = std::max(10, std::min(100, num_pts / 500));
	int max_cluster = std::max(1000, num_pts * 3);
	ec.setMinClusterSize(min_cluster);
	ec.setMaxClusterSize(max_cluster);
	std::cout << "[ADAPTIVE CLUSTER 1] N=" << num_pts << ", min=" << min_cluster
	          << ", max=" << max_cluster << std::endl;
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

void PointCloud2Vector3d(pcl::PointCloud<Point>::Ptr cloud, pcl::on_nurbs::vector_vec3d& data)
{
	for (unsigned i = 0; i < cloud->size(); i++)
	{
		Point& p = cloud->at(i);
		if (!std::isnan(p.x) && !std::isnan(p.y) && !std::isnan(p.z))
			data.push_back(Eigen::Vector3d(p.x, p.y, p.z));
	}
}

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
	pcl::on_nurbs::NurbsDataSurface data;

	if (pcl::io::loadPCDFile(pcd_file, cloud2) == -1)
		throw std::runtime_error("  PCD file not found.");

	fromPCLPointCloud2(cloud2, *cloud);
	PointCloud2Vector3d(cloud, data.interior);
	printf("  %zu points in data set\n", cloud->size()); //sisung_change

	// ############################################################################
	// fit B-spline surface

	unsigned order(3);
	unsigned refinement(3);
	unsigned iterations(8);
	unsigned mesh_resolution(128);

	pcl::on_nurbs::FittingSurface::Parameter params;
	params.interior_smoothness = 0.2;
	params.interior_weight = 1.0;
	params.boundary_smoothness = 0.4;
	params.boundary_weight = 0.0;

	// initialize
	printf("  surface fitting ...\n");
	ON_NurbsSurface nurbs = pcl::on_nurbs::FittingSurface::initNurbsPCABoundingBox(order, &data);
	pcl::on_nurbs::FittingSurface fit(&data, nurbs);

	// mesh for visualization
	pcl::PolygonMesh mesh;
	pcl::PointCloud<pcl::PointXYZ>::Ptr mesh_cloud(new pcl::PointCloud<pcl::PointXYZ>);
	std::vector<pcl::Vertices> mesh_vertices;
	std::string mesh_id = "mesh_nurbs";
	pcl::on_nurbs::Triangulation::convertSurface2PolygonMesh(fit.m_nurbs, mesh, mesh_resolution);

	// surface refinement
	for (unsigned i = 0; i < refinement; i++)
	{
		fit.refine(0);
		fit.refine(1);
		fit.assemble(params);
		fit.solve();
		pcl::on_nurbs::Triangulation::convertSurface2Vertices(fit.m_nurbs, mesh_cloud, mesh_vertices, mesh_resolution);
	}

	// surface fitting with final refinement level
	for (unsigned i = 0; i < iterations; i++)
	{
		fit.assemble(params);
		fit.solve();
		pcl::on_nurbs::Triangulation::convertSurface2Vertices(fit.m_nurbs, mesh_cloud, mesh_vertices, mesh_resolution);
	}

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
		Eigen::Vector2d paramsB = fit.inverseMapping(fit.m_nurbs, originalPt, hintPt, error, pt, tu, tv, im_max_steps, im_accuracy);

		double point[9];
		ON_3dVector normalEst;
		fit.m_nurbs.Evaluate(paramsB(0), paramsB(1), 1, 3, point);
		fit.m_nurbs.EvNormal(paramsB(0), paramsB(1), normalEst);

		pcl::PointXYZ ptOnFittedSurface;
		ptOnFittedSurface.x = point[0];
		ptOnFittedSurface.y = point[1];
		ptOnFittedSurface.z = point[2];

		pcl::PointXYZ ptOnOriginalMesh;
		ptOnOriginalMesh.x = meshPointCloud->points[i].x;
		ptOnOriginalMesh.y = meshPointCloud->points[i].y;
		ptOnOriginalMesh.z = meshPointCloud->points[i].z;

		pcl::Normal normOnFittedSurface;
		normOnFittedSurface.normal_x = -normalEst.x;
		normOnFittedSurface.normal_y = -normalEst.y;
		normOnFittedSurface.normal_z = -normalEst.z;

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
		ptTmp_b.normal_x = -normalEst.x;  //-normalEst.x;
		ptTmp_b.normal_y = -normalEst.y; //-normalEst.y;
		ptTmp_b.normal_z = -normalEst.z; //-normalEst.z;
		bSplineSurface->points.push_back(ptTmp_b);


		pcl::PointNormal ptTmp;

		ptTmp.x = meshPointCloud->points[i].x; // point[0];
		ptTmp.y = meshPointCloud->points[i].y; // point[1];
		ptTmp.z = meshPointCloud->points[i].z; // point[2];
		ptTmp.normal_x = -normalEst.x;
		ptTmp.normal_y = -normalEst.y;
		ptTmp.normal_z = -normalEst.z;
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

		// ADAPTIVE: Compute boundary radius based on cluster density
		// Note: Point cloud coordinates are in MILLIMETERS after coordinate fix
		// Estimate average spacing from point count (assuming ~1m^2 pottery piece)
		int num_pts = cloudWithoutNormals->points.size();
		double estimated_spacing_m = std::sqrt(1.0 / std::max(100, num_pts));  // sqrt(area / density)
		double estimated_spacing_mm = estimated_spacing_m * 1000.0;  // Convert to millimeters

		// Calculate radius in millimeters (6x the estimated spacing)
		double boundary_radius_mm = estimated_spacing_mm * 6.0;
		// Cap between 1mm and 50mm (original uses 3mm fixed)
		boundary_radius_mm = std::max(1.0, std::min(50.0, boundary_radius_mm));

		boundary_est.setRadiusSearch(boundary_radius_mm);  // PCL expects same units as coordinates (mm)
		std::cout << "[ADAPTIVE BOUNDARY] Cluster " << t << " has " << num_pts
		          << " points, spacing≈" << estimated_spacing_mm << "mm, boundary_r="
		          << boundary_radius_mm << "mm" << std::endl;
		//boundary_est.setAngleThreshold(PI/4);
		boundary_est.setSearchMethod(pcl::search::KdTree<pcl::PointXYZ>::Ptr(new pcl::search::KdTree<pcl::PointXYZ>));
		boundary_est.compute(boundary);


		//get points which on the boundary form point cloud;
		pcl::PointCloud<pcl::PointXYZ>::Ptr boundaryCloud(new pcl::PointCloud<pcl::PointXYZ>);

		// DEBUG: Check array sizes match expectations
		std::cout << "[DEBUG BOUNDARY] cloud size: " << cloud->points.size()
		          << ", cloudWithoutNormals size: " << cloudWithoutNormals->points.size()
		          << ", boundary size: " << boundary.points.size() << std::endl;

		if (boundary.points.size() != cloud->points.size()) {
			std::cerr << "[ERROR] Boundary size mismatch! Expected " << cloud->points.size()
			          << " but got " << boundary.points.size() << std::endl;
			std::cerr << "[ERROR] Skipping boundary extraction for cluster " << t << std::endl;
			continue;  // Skip this cluster
		}

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

		// Check if boundary cloud is empty before processing
		if (boundaryCloud->points.empty()) {
			std::cerr << "[WARNING] Cluster " << t << " has no boundary points! Skipping getPointsInSequence." << std::endl;
			std::cerr << "[WARNING] This may indicate the boundary radius (" << boundary_radius_mm
			          << "mm) is too small for the point spacing." << std::endl;
			continue;  // Skip to next cluster
		}

		std::cout << "[INFO] Cluster " << t << " boundary extraction: "
		          << boundaryCloud->points.size() << " boundary points found" << std::endl;

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
	pcl::io::savePLYFile(basePath + ".ply", *cloud, false); // ASCII mode

	Eigen::MatrixXd pointCloudMatrix(cloud->points.size(), 6);
	for (size_t i = 0; i < cloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << cloud->points[i].x, cloud->points[i].y, cloud->points[i].z,
			cloud->points[i].normal_x, cloud->points[i].normal_y, cloud->points[i].normal_z;
	}
	writeMatrix_to_XYZ(pointCloudMatrix, basePath + ".xyz", 6, false);
}

void convertPLYtoXYZ(string inputFile, string outFile, bool convertToMM = true)
{
	pcl::PointCloud<pcl::PointNormal>::Ptr mesh_cloud(new pcl::PointCloud<pcl::PointNormal>);
	pcl::io::loadPLYFile(inputFile, *mesh_cloud);
	Eigen::MatrixXd pointCloudMatrix(mesh_cloud->points.size(), 6);
	for (size_t i = 0; i < mesh_cloud->points.size(); i++)
	{
		pointCloudMatrix.row(i) << mesh_cloud->points[i].x, mesh_cloud->points[i].y, mesh_cloud->points[i].z, mesh_cloud->points[i].normal_x, mesh_cloud->points[i].normal_y, mesh_cloud->points[i].normal_z;
	}
	writeMatrix_to_XYZ(pointCloudMatrix, outFile, 6, convertToMM);
}

// ============================================================================
// TICKET 234 -- plane-continuity split rule (user-specified, 2026-10-22).
// A dot joins the region iff it agrees with the region's fitted plane: the
// reference is the plane fit over the last `planeWindow` accepted dots
// (sliding window, refit on every accept, normal oriented to the seed), so
// accumulated twist stays inside tolerance. A sharp departure (angle to the
// window plane > joinDeg, or point-to-plane distance > distMM) is left
// unfiled and seeds a new face later. The fit is LOCAL: a full 360deg
// annulus tracks itself and does not self-split at closure (ring control).
// ============================================================================
static bool fitPlaneWindow234(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud,
    const std::vector<int>& region, int planeWindow,
    const Eigen::Vector3f& refNormal,
    Eigen::Vector3f& outNormal, Eigen::Vector3f& outPoint)
{
    int n = static_cast<int>(region.size());
    int w = std::min(planeWindow, n);
    if (w < 3) {
        int s = region.back();
        outPoint = cloud->points[s].getVector3fMap();
        outNormal = refNormal;
        return true;
    }
    Eigen::Vector3f mean(0.0f, 0.0f, 0.0f);
    for (int i = n - w; i < n; ++i) mean += cloud->points[region[i]].getVector3fMap();
    mean /= static_cast<float>(w);
    Eigen::Matrix3f cov = Eigen::Matrix3f::Zero();
    for (int i = n - w; i < n; ++i) {
        Eigen::Vector3f d = cloud->points[region[i]].getVector3fMap() - mean;
        cov += d * d.transpose();
    }
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> es(cov);
    Eigen::Vector3f normal = es.eigenvectors().col(0);
    if (normal.dot(refNormal) < 0.0f) normal = -normal;
    outNormal = normal;
    outPoint = mean;
    return true;
}

static double angleToPlaneNormal234(const Eigen::Vector3f& n, const Eigen::Vector3f& planeN)
{
    Eigen::Vector4f a(n(0), n(1), n(2), 0.0f);
    Eigen::Vector4f b(planeN(0), planeN(1), planeN(2), 0.0f);
    return pcl::getAngle3D(a, b, true);
}

static std::vector<pcl::PointIndices> growRegionsPlaneContinuity234(
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud,
    pcl::PointCloud<pcl::Normal>::Ptr normals,
    int minClusterSize, int numberOfNeighbours,
    double joinDeg, double distMM, int planeWindow,
    double curvatureSeedThresh)
{
    std::vector<pcl::PointIndices> clusters;
    const int N = static_cast<int>(cloud->points.size());
    if (N == 0) return clusters;
    std::vector<char> taken(N, 0);
    std::vector<int> order(N);
    for (int i = 0; i < N; ++i) order[i] = i;
    std::sort(order.begin(), order.end(), [&](int a, int b) {
        return normals->points[a].curvature < normals->points[b].curvature;
    });
    pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
    kdtree.setInputCloud(cloud);
    std::vector<int> nbrs;
    std::vector<float> dists;
    std::vector<int> queue;
    std::vector<int> region;
    queue.reserve(2048);  // NOTE: frontier index is `fh`: qhull headers + -Dqh_QHpointer hijack the name `qh`
    region.reserve(8192);
    for (int s = 0; s < N; ++s) {
        int seed = order[s];
        if (taken[seed]) continue;
        if (normals->points[seed].curvature > curvatureSeedThresh) continue;
        region.clear();
        region.push_back(seed);
        taken[seed] = 1;
        Eigen::Vector3f seedN(normals->points[seed].normal_x,
                              normals->points[seed].normal_y,
                              normals->points[seed].normal_z);
        Eigen::Vector3f planeN, planeP;
        fitPlaneWindow234(cloud, region, planeWindow, seedN, planeN, planeP);
        queue.clear();
        queue.push_back(seed);
        size_t fh = 0;
        while (fh < queue.size()) {
            int cur = queue[fh++];
            nbrs.clear(); dists.clear();
            if (kdtree.nearestKSearch(cloud->points[cur], numberOfNeighbours + 1, nbrs, dists) <= 0) continue;
            for (size_t k = 0; k < nbrs.size(); ++k) {
                int nb = nbrs[k];
                if (nb == cur || taken[nb]) continue;
                Eigen::Vector3f nn(normals->points[nb].normal_x,
                                   normals->points[nb].normal_y,
                                   normals->points[nb].normal_z);
                double ang = angleToPlaneNormal234(nn, planeN);
                Eigen::Vector3f pp = cloud->points[nb].getVector3fMap();
                double dd = std::fabs((pp - planeP).dot(planeN));
                if (ang <= joinDeg && dd <= distMM) {
                    taken[nb] = 1;
                    region.push_back(nb);
                    queue.push_back(nb);
                    fitPlaneWindow234(cloud, region, planeWindow, seedN, planeN, planeP);
                }
            }
        }
        if (static_cast<int>(region.size()) >= minClusterSize) {
            pcl::PointIndices pi;
            pi.indices = region;
            clusters.push_back(pi);
        }
    }
    return clusters;
}

// ============================================================================
// TICKET 234 PAPER ARM (lead redirect 2026-10-22, SfS++ Sec IV-B1 verbatim).
// (1) region growing from the min-curvature point: n_b neighbours, join iff
// curvature < tau_kappa AND normal angle to the CURRENT front-point normal
// < tau_theta (Rabbani [35] / PCL semantics: the reference drifts with the
// front, so gradual twist is followed and only sharp turns split; a fixed
// seed reference over-segments -- verified v1 vs v2).
// (2) cluster merging to fixpoint (paper criteria, numeric choices reported
// at the call site): kNN close pairs between clusters (dist <= closeMM),
// patch-average normal similarity (<= patchDeg), boundary-point curvature
// comparison (rel diff <= curvRel), internal-point normal+curvature
// verification (same gates); merge all passing pairs, repeat to fixpoint.
// B-spline boundary refine + resample is the existing postamble
// (improveSurfaceBoundaryByFittingBSplineSurface) -- not duplicated here.
// (3) axis-ray classification (below): Surface_0 = interior.
// NOTE: no local named `qh` (qhull -Dqh_QHpointer hijacks it) and no `queue`
// shadowing games -- names below are collision-checked against this TU.
// ============================================================================
static std::vector<pcl::PointIndices> growPaper234(
    pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    int minClusterSize, int nb, double thetaDeg, double kappaThresh)
{
    std::vector<pcl::PointIndices> pclusters;
    const int NP = static_cast<int>(pcloud->points.size());
    if (NP == 0) return pclusters;
    std::vector<int> seedOrder(NP);
    for (int i = 0; i < NP; ++i) seedOrder[i] = i;
    std::sort(seedOrder.begin(), seedOrder.end(), [&](int a, int b) {
        return pnormals->points[a].curvature < pnormals->points[b].curvature;
    });
    pcl::KdTreeFLANN<pcl::PointXYZ> pkdtree;
    pkdtree.setInputCloud(pcloud);
    std::vector<int> pnb;
    std::vector<float> pdist;
    std::vector<int> pfront;
    std::vector<int> preg;
    std::vector<char> pclaimed(NP, 0);
    pfront.reserve(2048);
    preg.reserve(8192);
    for (int s = 0; s < NP; ++s) {
        int sd = seedOrder[s];
        if (pclaimed[sd]) continue;
        preg.clear();
        preg.push_back(sd);
        pclaimed[sd] = 1;
        pfront.clear();
        pfront.push_back(sd);
        size_t fh2 = 0;
        while (fh2 < pfront.size()) {
            int cf = pfront[fh2++];
            Eigen::Vector4f curN4(pnormals->points[cf].normal_x,
                                  pnormals->points[cf].normal_y,
                                  pnormals->points[cf].normal_z, 0.0f);
            pnb.clear(); pdist.clear();
            if (pkdtree.nearestKSearch(pcloud->points[cf], nb + 1, pnb, pdist) <= 0) continue;
            for (size_t k = 0; k < pnb.size(); ++k) {
                int cand = pnb[k];
                if (cand == cf || pclaimed[cand]) continue;
                if (pnormals->points[cand].curvature >= kappaThresh) continue;
                Eigen::Vector4f nn4(pnormals->points[cand].normal_x,
                                    pnormals->points[cand].normal_y,
                                    pnormals->points[cand].normal_z, 0.0f);
                if (pcl::getAngle3D(curN4, nn4, true) > thetaDeg) continue;
                pclaimed[cand] = 1;
                preg.push_back(cand);
                pfront.push_back(cand);
            }
        }
        if (static_cast<int>(preg.size()) >= minClusterSize) {
            pcl::PointIndices pi;
            pi.indices = preg;
            pclusters.push_back(pi);
        }
    }
    return pclusters;
}

static Eigen::Vector3f meanNormal234(const std::vector<int>& idx,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += Eigen::Vector3f(pnormals->points[id].normal_x, pnormals->points[id].normal_y, pnormals->points[id].normal_z);
    float n = m.norm();
    if (n > 1e-9f) m /= n;
    else m = Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    return m;
}

static double meanCurv234(const std::vector<int>& idx,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals)
{
    if (idx.empty()) return 0.0;
    double s = 0.0;
    for (int id : idx) s += static_cast<double>(pnormals->points[id].curvature);
    return s / static_cast<double>(idx.size());
}

static Eigen::Vector3f pcaAxis234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<int>& idx)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += pcloud->points[id].getVector3fMap();
    if (!idx.empty()) m /= static_cast<float>(idx.size());
    Eigen::Matrix3f cov = Eigen::Matrix3f::Zero();
    for (int id : idx) { Eigen::Vector3f d = pcloud->points[id].getVector3fMap() - m; cov += d * d.transpose(); }
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> es(cov);
    return es.eigenvectors().col(2);
}

static int medianInternal234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<int>& idx, const Eigen::Vector3f& axis)
{
    if (idx.empty()) return -1;
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += pcloud->points[id].getVector3fMap();
    m /= static_cast<float>(idx.size());
    Eigen::Vector3f an = axis.norm() > 1e-9f ? axis.normalized() : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    std::vector<std::pair<float,int> > dv;
    dv.reserve(idx.size());
    for (int id : idx) {
        Eigen::Vector3f w = pcloud->points[id].getVector3fMap() - m;
        float along = w.dot(an);
        float perp = (w - along * an).norm();
        dv.push_back(std::make_pair(perp, id));
    }
    std::nth_element(dv.begin(), dv.begin() + dv.size() / 2, dv.end());
    return dv[dv.size() / 2].second;
}

static Eigen::Vector3f k2AvgNormal234(pcl::KdTreeFLANN<pcl::PointXYZ>& ctree,
    const std::vector<int>& cidx,
    pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals, int qid, int k2)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    if (cidx.empty() || k2 <= 0) return Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    std::vector<int> rr; std::vector<float> dd;
    int K = std::min<int>(k2, static_cast<int>(cidx.size()));
    if (ctree.nearestKSearch(pcloud->points[qid], K, rr, dd) <= 0) return Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    for (int r : rr) {
        int gid = cidx[r];
        m += Eigen::Vector3f(pnormals->points[gid].normal_x, pnormals->points[gid].normal_y, pnormals->points[gid].normal_z);
    }
    float n = m.norm();
    if (n > 1e-9f) m /= n;
    else m = Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    return m;
}


// ---- ticket 276 Phase 2: per-cluster-pair test values (SFS_MERGE_PAIRS=1) ----
// Diagnostic only: prints every Appendix-A test quantity for every cluster pair
// examined, in every pass. Inert when the switch is unset (no output, no work).
static bool gPairs276 = false;

static void pairPrefix276(int pass, int ci, int cj, size_t nA, size_t nB,
    size_t bA, size_t bB, size_t scanned, size_t smallTot,
    size_t npairs, bool cap, const std::vector<double>& pd)
{
    double dmin = 0.0, dmed = 0.0;
    if (!pd.empty()) {
        std::vector<double> v = pd;
        std::sort(v.begin(), v.end());
        dmin = v.front();
        dmed = v[v.size() / 2];
    }
    std::cout << "[PAIR-276] pass=" << pass << " c" << ci << "-c" << cj
              << " nA=" << nA << " nB=" << nB
              << " bnd=" << bA << "/" << bB
              << " scan=" << scanned << "/" << smallTot
              << " cut=" << (smallTot - scanned)
              << " pairs=" << npairs << " cap=" << (cap ? 1 : 0)
              << " dmin=" << dmin << " dmed=" << dmed;
}

// One merge verdict for a cluster pair. All thresholds are the paper-arm
// operating point (logged by the caller).
// Appendix-A-normative pair verdict (provenance in patch234d.py header).
static bool tryMergePair234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    const std::vector<int>& A, const std::vector<int>& B,
    const std::vector<char>& isBnd,
    const Eigen::Vector3f& axisA, const Eigen::Vector3f& axisB,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k2,
    int ci = -1, int cj = -1, int pass = 0)
{
    if (A.empty() || B.empty()) return false;
    // ---- Step 1: boundary subsets, pairs within rhoD, need >= 3 ----
    std::vector<int> bA, bB;
    for (int id : A) if (isBnd[id]) bA.push_back(id);
    for (int id : B) if (isBnd[id]) bB.push_back(id);
    if (bA.empty() || bB.empty()) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), 0, 0, 0, false, std::vector<double>());
            std::cout << " verdict=REJECT:empty-boundary" << std::endl;
        }
        return false;
    }
    const std::vector<int> *sP = &bA, *lP = &bB;
    bool sIsA = true;
    if (bA.size() > bB.size()) { sP = &bB; lP = &bA; sIsA = false; }
    pcl::PointCloud<pcl::PointXYZ>::Ptr lC(new pcl::PointCloud<pcl::PointXYZ>);
    for (int id : *lP) lC->points.push_back(pcloud->points[id]);
    lC->width = lC->points.size(); lC->height = 1;
    pcl::KdTreeFLANN<pcl::PointXYZ> lT;
    lT.setInputCloud(lC);
    std::vector<std::pair<int,int> > pairs;
    std::vector<int> oneI; std::vector<float> oneD;
    std::vector<double> pd276;
    size_t scanned276 = 0;
    for (size_t i = 0; i < sP->size() && pairs.size() < 200; ++i) {
        ++scanned276;
        int sid = (*sP)[i];
        oneI.clear(); oneD.clear();
        if (lT.nearestKSearch(pcloud->points[sid], 1, oneI, oneD) <= 0) continue;
        if (oneD[0] <= rhoD * rhoD) {
            int a = sIsA ? sid : (*lP)[oneI[0]];
            int b = sIsA ? (*lP)[oneI[0]] : sid;
            pairs.push_back(std::make_pair(a, b));
            if (gPairs276) pd276.push_back(std::sqrt(static_cast<double>(oneD[0])));
        }
    }
    const bool cap276 = (pairs.size() >= 200) && (scanned276 < sP->size());
    if (pairs.size() < 3) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " rhoD2=" << rhoD * rhoD << " verdict=REJECT:pairs<3" << std::endl;
        }
        return false;
    }
    // ---- Step 2: k2-average normals + mean curvature over pair members ----
    pcl::PointCloud<pcl::PointXYZ>::Ptr cA(new pcl::PointCloud<pcl::PointXYZ>), cB(new pcl::PointCloud<pcl::PointXYZ>);
    for (int id : A) cA->points.push_back(pcloud->points[id]);
    for (int id : B) cB->points.push_back(pcloud->points[id]);
    cA->width = cA->points.size(); cA->height = 1;
    cB->width = cB->points.size(); cB->height = 1;
    pcl::KdTreeFLANN<pcl::PointXYZ> tA, tB;
    tA.setInputCloud(cA); tB.setInputCloud(cB);
    Eigen::Vector3f sNA(0,0,0), sNB(0,0,0);
    double sCA = 0.0, sCB = 0.0;
    for (size_t i = 0; i < pairs.size(); ++i) {
        sNA += k2AvgNormal234(tA, A, pcloud, pnormals, pairs[i].first, k2);
        sNB += k2AvgNormal234(tB, B, pcloud, pnormals, pairs[i].second, k2);
        sCA += static_cast<double>(pnormals->points[pairs[i].first].curvature);
        sCB += static_cast<double>(pnormals->points[pairs[i].second].curvature);
    }
    float nA = sNA.norm(), nB = sNB.norm();
    if (nA < 1e-9f || nB < 1e-9f) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " verdict=REJECT:normal-zero" << std::endl;
        }
        return false;
    }
    sNA /= nA; sNB /= nB;
    const double nrm276 = static_cast<double>(sNA.dot(sNB));
    const double cuv276 = std::fabs(sCA / pairs.size() - sCB / pairs.size());
    if (nrm276 < rhoN) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " rhoN=" << rhoN << " rhoC=" << rhoC << " verdict=REJECT:rhoN" << std::endl;
        }
        return false;
    }
    if (cuv276 >= rhoC) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " rhoN=" << rhoN << " rhoC=" << rhoC << " verdict=REJECT:rhoC" << std::endl;
        }
        return false;
    }
    // ---- Step 3: internal median-point verification ----
    int ia = medianInternal234(pcloud, A, axisA);
    int ib = medianInternal234(pcloud, B, axisB);
    if (ia < 0 || ib < 0) return false;
    Eigen::Vector3f na(pnormals->points[ia].normal_x, pnormals->points[ia].normal_y, pnormals->points[ia].normal_z);
    Eigen::Vector3f nb(pnormals->points[ib].normal_x, pnormals->points[ib].normal_y, pnormals->points[ib].normal_z);
    float la = na.norm(), lb = nb.norm();
    if (la < 1e-9f || lb < 1e-9f) return false;
    const double inn276 = static_cast<double>(na.dot(nb) / (la * lb));
    const double icuv276 = std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature));
    if (inn276 < rhoInN) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=REJECT:rhoInN" << std::endl;
        }
        return false;
    }
    if (icuv276 >= rhoInC) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=REJECT:rhoInC" << std::endl;
        }
        return false;
    }
    if (gPairs276) {
        pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
        std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=ACCEPT" << std::endl;
    }
    return true;
}

static void mergePaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k1, int k2)
{
    gPairs276 = false;
    if (const char* e276 = std::getenv("SFS_MERGE_PAIRS")) gPairs276 = (*e276 && std::string(e276) != "0");
    if (gPairs276) std::cout << "[PAIR-276] enabled: printing every cluster pair's test values" << std::endl;
    std::cout << "[PAPER-234] appendix-A merge: rhoD=" << rhoD << " rhoN=" << rhoN << " rhoC=" << rhoC
              << " rhoInN=" << rhoInN << " rhoInC=" << rhoInC << " k1=" << k1 << " k2=" << k2 << std::endl;
    const int NP = static_cast<int>(pcloud->points.size());
    pcl::KdTreeFLANN<pcl::PointXYZ> allTree;
    allTree.setInputCloud(pcloud);
    std::vector<int> rr; std::vector<float> dd;
    int pass = 0;
    bool any = true;
    while (any) {
        any = false;
        ++pass;
        std::vector<int> memberOf(NP, -1);
        for (size_t c = 0; c < pclusters.size(); ++c)
            for (int id : pclusters[c].indices) memberOf[id] = static_cast<int>(c);
        // boundary status via k1 neighbours (Alg 1 Step 1)
        std::vector<char> isBnd(NP, 0);
        for (int p = 0; p < NP; ++p) {
            if (memberOf[p] < 0) continue;
            rr.clear(); dd.clear();
            int K = std::min(k1 + 1, NP);
            if (allTree.nearestKSearch(pcloud->points[p], K, rr, dd) <= 0) continue;
            for (size_t i = 0; i < rr.size(); ++i) {
                if (rr[i] == p) continue;
                if (memberOf[rr[i]] != memberOf[p]) { isBnd[p] = 1; break; }
            }
        }
        std::vector<Eigen::Vector3f> axes(pclusters.size());
        for (size_t c = 0; c < pclusters.size(); ++c) axes[c] = pcaAxis234(pcloud, pclusters[c].indices);
        std::vector<char> dead(pclusters.size(), 0);
        for (size_t i = 0; i < pclusters.size(); ++i) {
            if (dead[i]) continue;
            for (size_t j = i + 1; j < pclusters.size(); ++j) {
                if (dead[j]) continue;
                if (tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, isBnd,
                        axes[i], axes[j], rhoD, rhoN, rhoC, rhoInN, rhoInC, k2,
                        static_cast<int>(i), static_cast<int>(j), pass)) {
                    std::cout << "[PAPER-234] pass " << pass << ": merge " << pclusters[j].indices.size() << " into " << pclusters[i].indices.size() << std::endl;
                    pclusters[i].indices.insert(pclusters[i].indices.end(), pclusters[j].indices.begin(), pclusters[j].indices.end());
                    dead[j] = 1;
                    any = true;
                }
            }
        }
        if (any) {
            std::vector<pcl::PointIndices> kept;
            for (size_t i = 0; i < pclusters.size(); ++i) if (!dead[i]) kept.push_back(pclusters[i]);
            pclusters.swap(kept);
        }
        std::cout << "[PAPER-234] pass " << pass << " done: " << pclusters.size() << " clusters" << std::endl;
        if (pass > 25) break;
    }
}

// Axis-ray classification (paper Sec IV-B1): ray along the point normal meets
// the symmetry axis; intersection on the positive normal side = interior.
// Both assignments tried; the one with more satisfying points wins; the
// interior face is moved to clusters[0] so Surface_0 = interior (redirect).
static void classifyAndOrderPaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters)
{
    if (pclusters.size() < 2) return;
    const char* axPath = std::getenv("SFS_AXIS_FILE");
    if (!axPath || !*axPath) { std::cout << "[PAPER-234] classify: no SFS_AXIS_FILE, keep size order" << std::endl; return; }
    std::ifstream axf(axPath);
    if (!axf.is_open()) { std::cout << "[PAPER-234] classify: cannot open axis file, keep size order" << std::endl; return; }
    double ax, ay, az, dx, dy, dz;
    axf >> ax >> ay >> az >> dx >> dy >> dz;
    if (axf.fail()) { std::cout << "[PAPER-234] classify: bad axis parse, keep size order" << std::endl; return; }
    Eigen::Vector3f axPt(static_cast<float>(ax), static_cast<float>(ay), static_cast<float>(az));
    Eigen::Vector3f axDir(static_cast<float>(dx), static_cast<float>(dy), static_cast<float>(dz));
    float dl = axDir.norm();
    if (dl < 1e-9f) { std::cout << "[PAPER-234] classify: zero axis dir, keep size order" << std::endl; return; }
    axDir /= dl;
    double inFrac[2] = {0.0, 0.0};
    for (int f = 0; f < 2; ++f) {
        long inN = 0;
        for (int id : pclusters[f].indices) {
            Eigen::Vector3f pp = pcloud->points[id].getVector3fMap();
            Eigen::Vector3f nn(pnormals->points[id].normal_x, pnormals->points[id].normal_y, pnormals->points[id].normal_z);
            Eigen::Vector3f w = pp - axPt;
            float t = w.dot(axDir);
            Eigen::Vector3f cp = axPt + t * axDir;
            Eigen::Vector3f v = cp - pp;
            if (v.dot(nn) > 0.0f) ++inN;
        }
        inFrac[f] = pclusters[f].indices.empty() ? 0.0 : static_cast<double>(inN) / static_cast<double>(pclusters[f].indices.size());
    }
    double n0 = static_cast<double>(pclusters[0].indices.size()), n1 = static_cast<double>(pclusters[1].indices.size());
    double satA = inFrac[0] * n0 + (1.0 - inFrac[1]) * n1; // [0]=interior
    double satB = (1.0 - inFrac[0]) * n0 + inFrac[1] * n1; // [1]=interior
    std::cout << "[PAPER-234] classify: face0 n=" << pclusters[0].indices.size() << " interior_frac=" << inFrac[0]
              << " face1 n=" << pclusters[1].indices.size() << " interior_frac=" << inFrac[1]
              << " satA=" << satA << " satB=" << satB << std::endl;
    if (satB > satA) {
        pcl::PointIndices tmp = pclusters[0];
        pclusters[0] = pclusters[1];
        pclusters[1] = tmp;
        std::cout << "[PAPER-234] classify: swapped -> Surface_0=interior" << std::endl;
    } else {
        std::cout << "[PAPER-234] classify: kept -> Surface_0=interior" << std::endl;
    }
}


// ======================= TICKET 276: merge diagnostics =======================
// SFS_MERGE_DIAG reads once per piece:
//   unset / empty / "0" -> every function below is skipped (inert)
//   "1"                 -> dump per-point post-merge cluster labels
//   "split"             -> also split the largest cluster in two by a plane
//                          through its centroid (normal = its PCA axis) BEFORE
//                          merging, then report whether the halves are rejoined.
// The dump labels every point of the segmented cloud: cluster 0 = Surface_0,
// cluster 1 = Surface_1, cluster >= 2 = dropped, -1 = in no cluster.
static std::string mergeDiagMode276()
{
    const char* e = std::getenv("SFS_MERGE_DIAG");
    if (!e || !*e || std::string(e) == "0") return std::string();
    return std::string(e);
}

static void splitLargestCluster276(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    std::vector<pcl::PointIndices>& pclusters, std::vector<char>& half276)
{
    if (pclusters.empty()) return;
    size_t rank276 = 0;
    if (const char* e276 = std::getenv("SFS_MERGE_SPLIT_RANK"))
    {
        int r276 = std::atoi(e276);
        if (r276 > 0) rank276 = static_cast<size_t>(r276);
    }
    std::vector<size_t> order276(pclusters.size());
    for (size_t c276 = 0; c276 < order276.size(); ++c276) order276[c276] = c276;
    std::sort(order276.begin(), order276.end(), [&pclusters](size_t a276, size_t b276) {
        return pclusters[a276].indices.size() > pclusters[b276].indices.size();
    });
    if (rank276 >= order276.size()) rank276 = 0;
    size_t big = order276[rank276];
    const std::vector<int> src = pclusters[big].indices;
    if (src.size() < 2) return;
    Eigen::Vector3f ax = pcaAxis234(pcloud, src);
    Eigen::Vector3f c0(0.0f, 0.0f, 0.0f);
    for (int id : src) c0 += pcloud->points[id].getVector3fMap();
    c0 /= static_cast<float>(src.size());
    half276.assign(pcloud->points.size(), static_cast<char>(2));
    std::vector<int> ha, hb;
    for (int id : src) {
        Eigen::Vector3f p = pcloud->points[id].getVector3fMap();
        if ((p - c0).dot(ax) >= 0.0f) { ha.push_back(id); half276[id] = 0; }
        else { hb.push_back(id); half276[id] = 1; }
    }
    std::cout << "[MERGE-DIAG-276] split: rank=" << rank276 << " cluster " << big << " n=" << src.size()
              << " -> halfA=" << ha.size() << " halfB=" << hb.size()
              << " plane n=(" << ax.x() << "," << ax.y() << "," << ax.z() << ")"
              << " c=(" << c0.x() << "," << c0.y() << "," << c0.z() << ")" << std::endl;
    pcl::PointIndices pa, pb;
    pa.indices = ha;
    pb.indices = hb;
    pclusters[big] = pa;
    pclusters.push_back(pb);
}

static void reportSplit276(const std::vector<char>& half276,
    const std::vector<pcl::PointIndices>& pclusters, int nBefore)
{
    std::map<int, long> h0, h1;
    for (size_t c = 0; c < pclusters.size(); ++c)
        for (int id : pclusters[c].indices) {
            if (static_cast<size_t>(id) >= half276.size()) continue;
            if (half276[id] == 0) h0[static_cast<int>(c)]++;
            else if (half276[id] == 1) h1[static_cast<int>(c)]++;
        }
    long n0 = 0, n1 = 0;
    int d0 = -1, d1 = -1;
    for (auto& kv : h0) if (kv.second > n0) { n0 = kv.second; d0 = kv.first; }
    for (auto& kv : h1) if (kv.second > n1) { n1 = kv.second; d1 = kv.first; }
    std::cout << "[MERGE-DIAG-276] split-check: halfA -> cluster " << d0 << " (" << n0
              << " pts), halfB -> cluster " << d1 << " (" << n1 << " pts), rejoined="
              << ((d0 == d1 && d0 >= 0) ? "YES" : "NO")
              << ", clusters before-split=" << nBefore << " after-split=" << (nBefore + 1)
              << " after-merge=" << pclusters.size() << std::endl;
}

static void dumpMergeDiag276(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<pcl::PointIndices>& pclusters, double theta,
    const std::vector<char>& half276)
{
    const std::string dumpName = "mergeDiag276_" + fileNameOnly + ".txt";
    std::ofstream f(dumpName.c_str());
    if (!f.is_open()) {
        std::cout << "[MERGE-DIAG-276] cannot open " << dumpName << std::endl;
        return;
    }
    std::vector<int> lab(pcloud->points.size(), -1);
    for (size_t c = 0; c < pclusters.size(); ++c)
        for (int id : pclusters[c].indices)
            if (static_cast<size_t>(id) < lab.size()) lab[id] = static_cast<int>(c);
    long s0 = pclusters.size() > 0 ? static_cast<long>(pclusters[0].indices.size()) : 0;
    long s1 = pclusters.size() > 1 ? static_cast<long>(pclusters[1].indices.size()) : 0;
    long dropped = 0, unclustered = 0;
    for (size_t i = 0; i < lab.size(); ++i) {
        if (lab[i] < 0) ++unclustered;
        else if (lab[i] >= 2) ++dropped;
    }
    f << std::setprecision(7);
    f << "# npoints " << pcloud->points.size() << " nclusters " << pclusters.size()
      << " thetaDeg " << theta << " split " << (half276.empty() ? 0 : 1) << "\n";
    for (size_t c = 0; c < pclusters.size(); ++c)
        f << "# cluster " << c << " size " << pclusters[c].indices.size()
          << " surface " << ((c < 2) ? 1 : 0) << "\n";
    f << "# columns: index cluster x y z half\n";
    for (size_t i = 0; i < pcloud->points.size(); ++i) {
        int hv = (half276.empty() || i >= half276.size()) ? -1 : static_cast<int>(half276[i]);
        f << i << " " << lab[i] << " " << pcloud->points[i].x << " "
          << pcloud->points[i].y << " " << pcloud->points[i].z << " " << hv << "\n";
    }
    f.close();
    std::cout << "[MERGE-DIAG-276] labels: npoints=" << pcloud->points.size()
              << " nclusters=" << pclusters.size() << " surface0=" << s0 << " surface1=" << s1
              << " dropped=" << dropped << " unclustered=" << unclustered
              << " -> " << dumpName << std::endl;
}


void surfaceSegmentation(std::string filePath, int minCluster, int noOfNeighbours, double smoothnessAngleThreshold, double curvatureThreshold,
        bool planeRule = false, double planeJoinDeg = 60.0, double planeDistMM = 2.0, int planeWindow = 100,
        bool paperChain = true, double paperTheta = 3.4, double paperKappa = 1.0, int paperNB = 10,
        double paperRhoD = 1.0, double paperRhoN = 0.95, double paperRhoC = 0.1, double paperRhoInN = 0.75, double paperRhoInC = 0.25)
{
    // std::string tmp_path = filePath;
	std::string tmp_path = intermediatePath_global;
	if (tmp_path.back() != '/' && tmp_path.back() != '\\') {
		tmp_path += "/";
	}
    int numberOfClustersCreated = -1;
    int maxIterations = 30;  // Prevent infinite loops
    int currentIteration = 0;
    double minAngleThreshold = -50.0;  // Lower bound to prevent excessive iteration
    if (const char* sfs_ss = std::getenv("SFS_SINGLE_SHOT")) { if (*sfs_ss && std::string(sfs_ss) != "0") maxIterations = 1; }  // TICKET 234: ported ladder harness
    
    while (numberOfClustersCreated < 2 && currentIteration < maxIterations)
    {
        if (numberOfClustersCreated != -1 && numberOfClustersCreated < 2)
        {
            std::cout << "Single cluster found (iteration " << (currentIteration + 1) 
                      << "/" << maxIterations << ")...Increasing angle threshold (+2) and trying again..." << std::endl;
            smoothnessAngleThreshold += 2; // actually increase threshold to loosen smoothness criterion
            
            // Safety check: if angle threshold gets too negative, break out
            if (smoothnessAngleThreshold > 45.0)
            {
                std::cout << "Warning: Angle threshold reached maximum (45 deg)"
                          << "). Using single cluster result." << std::endl;
                break;
            }
        }
        currentIteration++;
        
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);

        pcl::search::Search<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
        pcl::PointCloud <pcl::Normal>::Ptr normals(new pcl::PointCloud <pcl::Normal>);

        pcl::PointCloud<pcl::PointNormal>::Ptr cloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);

        std::cout << "[DEBUG] Loading PLY file: " << filePath << std::endl;
        pcl::io::loadPLYFile(filePath, *cloudWithNormals);
        std::cout << "[DEBUG] PLY file loaded successfully. Points: " << cloudWithNormals->points.size() << std::endl;

        std::cout << "[DEBUG] Converting PointNormal to PointXYZ..." << std::endl;
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
        std::cout << "[DEBUG] Conversion complete. Cloud size: " << cloud->points.size() << std::endl;

        pcl::PointCloud<pcl::PointNormal>::Ptr sampledPointCloudNormal(new pcl::PointCloud<pcl::PointNormal>);
        std::cout << "[DEBUG] Calling getNormalsOnSurface..." << std::endl;
        std::cout << "[DEBUG] Input cloud size: " << cloud->points.size() << std::endl;
        getNormalsOnSurface(cloud, sampledPointCloudNormal);
        std::cout << "[DEBUG] getNormalsOnSurface completed successfully. Result points: " << sampledPointCloudNormal->points.size() << std::endl;

        std::cout << "[DEBUG] Extracting normals from sampled cloud..." << std::endl;
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

        // Tune parameters based on current cloud size to handle scale differences robustly
        int Npts = static_cast<int>(cloud->points.size());
        int dynMinCluster = std::max(minCluster, std::max(30, Npts / 500));          // ~0.2% of points, min 30
        int dynK          = std::max(noOfNeighbours, std::min(40, std::max(15, Npts / 500))); // 15..40 range

        std::vector<pcl::PointIndices> clusters;
        if (paperChain) {
            std::cout << "[PAPER-234] paper grow: thetaDeg=" << paperTheta << " kappa=" << paperKappa << " nb=" << paperNB << std::endl;
            clusters = growPaper234(cloud, normals, dynMinCluster, paperNB, paperTheta, paperKappa);
        } else if (planeRule) {
            std::cout << "[PLANE-234] windowed-plane gate: joinDeg=" << planeJoinDeg
                      << " distMM=" << planeDistMM << " window=" << planeWindow << std::endl;
            clusters = growRegionsPlaneContinuity234(cloud, normals, dynMinCluster, dynK,
                planeJoinDeg, planeDistMM, planeWindow, curvatureThreshold);
        } else {
        pcl::RegionGrowing<pcl::PointXYZ, pcl::Normal> reg;
        reg.setMinClusterSize(dynMinCluster);
        reg.setMaxClusterSize(1000000);
        reg.setSearchMethod(tree);
        reg.setNumberOfNeighbours(dynK);
        reg.setInputCloud(cloud);
        reg.setInputNormals(normals);
        reg.setSmoothnessThreshold(smoothnessAngleThreshold / 180.0 * M_PI);
        reg.setCurvatureThreshold(curvatureThreshold);

        reg.extract(clusters);
        }

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
        if (paperChain) {
            std::cout << "Calling mergePaper234 function." << std::endl;
            // TICKET 276: SFS_MERGE_DIAG unset/0 -> mdiag276 is empty and nothing below runs.
            const std::string mdiag276 = mergeDiagMode276();
            const bool split276 = (mdiag276 == "split");
            const int nBeforeSplit276 = static_cast<int>(clusters.size());
            std::vector<char> half276;
            if (split276) splitLargestCluster276(cloud, clusters, half276);
            mergePaper234(cloud, normals, clusters, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC, 10, 30);
            std::sort(clusters.begin(), clusters.end(), myobject3);
            classifyAndOrderPaper234(cloud, normals, clusters);
            if (split276) reportSplit276(half276, clusters, nBeforeSplit276);
            if (!mdiag276.empty()) dumpMergeDiag276(cloud, clusters, paperTheta, half276);
        } else {
        std::cout << "Calling mergeClusters function." << std::endl;
        mergeClusters(cloudWithNormals, clusters);
        }

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
                pcl::io::savePLYFile(tmp_path + "_flipped_normal.ply", *cloudWithNormals, false); // ASCII mode
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

            std::cout << "[DEBUG] Saving surface cluster PLY files in ASCII mode..." << std::endl;
            pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_0.ply", *cloudWithNormals_Cluster1, false); // ASCII mode
            pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_1.ply", *cloudWithNormals_Cluster2, false); // ASCII mode

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
        
        // Validate point cloud before saving
        if (points_unclustered->points.empty()) {
            std::cerr << "Warning: Empty point cloud, skipping PLY save" << std::endl;
        } else {
            // Ensure all points have valid data
            bool valid = true;
            for (const auto& point : points_unclustered->points) {
                if (!std::isfinite(point.x) || !std::isfinite(point.y) || !std::isfinite(point.z) ||
                    !std::isfinite(point.normal_x) || !std::isfinite(point.normal_y) || !std::isfinite(point.normal_z)) {
                    valid = false;
                    break;
                }
            }
            if (valid) {
                pcl::io::savePLYFile(dataPath_global + fileNameOnly + "_unclustered.ply", *points_unclustered, false); // ASCII mode
            } else {
                std::cerr << "Error: Point cloud contains invalid data, skipping PLY save" << std::endl;
            }
        }

		getBreakLineForDecorativeParts(dataPath_global + fileNameOnly + "_unclustered.ply");
        numberOfClustersCreated = clusters.size();
    }
    
    // Safety check: Handle cases where clustering couldn't achieve 2 clusters
    if (numberOfClustersCreated < 2)
    {
        std::cout << "Warning: Could not achieve 2 clusters after " << currentIteration 
                  << " iterations. Final cluster count: " << numberOfClustersCreated 
                  << ". Proceeding with available clusters." << std::endl;
    }
    else
    {
        std::cout << "Successfully found " << numberOfClustersCreated 
                  << " clusters after " << currentIteration << " iterations." << std::endl;
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

	// ADAPTIVE: Scale cluster size thresholds with point cloud density
	int num_pts = missedPoints->points.size();
	int min_cluster = std::max(10, std::min(100, num_pts / 500));
	int max_cluster = std::max(1000, num_pts * 3);
	ec.setMinClusterSize(min_cluster);
	ec.setMaxClusterSize(max_cluster);
	std::cout << "[ADAPTIVE CLUSTER 2] N=" << num_pts << ", min=" << min_cluster
	          << ", max=" << max_cluster << std::endl;
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
    
    // Handle specific file processing when command line args are provided
    if (!specific_mesh_file.empty()) {
        // Process only the specific file
        std::cout << "Processing single file mode" << std::endl;
        // Add specific file processing logic here if needed
        // For now, fall through to standard processing
    }
    
    for (const auto& entry : fs::recursive_directory_iterator(datasetPath_global)) {
        if (!fs::is_directory(entry.path()) && entry.path().extension() == ".pcd") {
            pcd_files.push_back(entry.path());
        }
    }
    std::sort(pcd_files.begin(), pcd_files.end());
    
    ofstream myfile(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
    
    for (const auto& file_path : pcd_files) {
        std::string inputFilePath = file_path.string();
        
        std::string baseName = file_path.stem().string();
        baseName = baseName.substr(0, baseName.find("_Point")); 
        std::string meshFileName = baseName + "_Mesh.obj";
        fs::path meshFilePath = fs::path(meshDatasetPath) / meshFileName;
        
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
        // POTA-244: default restores pre-48fb588 fixed 0.6mm radius (no target loop).
        // SFS_DOWNSAMPLE_TARGET=N overrides: 19000 = 48fb588 adaptive, <0 = skip (raw cloud).
        int dsTarget244 = 0;
        if (const char* e = std::getenv("SFS_DOWNSAMPLE_TARGET")) { if (*e) dsTarget244 = std::stoi(e); }
        std::string downsampledFilePath = downsamplePointCloud(inputFilePath, 0.6F, dsTarget244);
        
        std::cout << "Starting processing on: " << inputFilePath << std::endl;
        
        myfile.open(baseOutputPath + "segmentationTimes.txt", std::ofstream::out | std::ofstream::app);
        if (myfile.is_open()) {
            myfile << fileNameOnly << "\t" << t_individual.elapsed() << "\t";
            myfile.close();
        }
        t_individual.reset();
        
        int minCluster = 50, noOfNeighbours = 10;
        double smoothnessAngleThreshold = 4.5, curvatureThreshold = 1.5;
        if (const char* sfs_s = std::getenv("SFS_SMOOTHNESS_DEG")) { if (*sfs_s) smoothnessAngleThreshold = std::stod(sfs_s); }
        if (const char* sfs_c = std::getenv("SFS_CURVATURE_THRESH")) { if (*sfs_c) curvatureThreshold = std::stod(sfs_c); }
        double planeJoinDeg = 60.0, planeDistMM = 2.0;
        int planeWindow = 100;
        if (const char* e = std::getenv("SFS_PLANE_JOIN_DEG")) { if (*e) planeJoinDeg = std::stod(e); }
        if (const char* e = std::getenv("SFS_PLANE_DIST_MM")) { if (*e) planeDistMM = std::stod(e); }
        if (const char* e = std::getenv("SFS_PLANE_WINDOW")) { if (*e) planeWindow = std::stoi(e); }
        bool planeRule = false;
        if (const char* e = std::getenv("SFS_PLANE_RULE")) { if (*e && std::string(e) != "0") planeRule = true; }
        bool paperChain = true;
        if (const char* e = std::getenv("SFS_PAPER_CHAIN")) { if (*e && std::string(e) != "0") paperChain = true; else paperChain = false; }
        double paperTheta = 3.4, paperKappa = 1.0, paperRhoD = 1.0, paperRhoN = 0.95, paperRhoC = 0.1, paperRhoInN = 0.75, paperRhoInC = 0.25;
        int paperNB = 10;
        if (const char* e = std::getenv("SFS_PAPER_THETA")) { if (*e) paperTheta = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_KAPPA")) { if (*e) paperKappa = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_NB")) { if (*e) paperNB = std::stoi(e); }
        if (const char* e = std::getenv("SFS_PAPER_RHOD")) { if (*e) paperRhoD = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_RHON")) { if (*e) paperRhoN = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_RHOC")) { if (*e) paperRhoC = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_RHOINN")) { if (*e) paperRhoInN = std::stod(e); }
        if (const char* e = std::getenv("SFS_PAPER_RHOINC")) { if (*e) paperRhoInC = std::stod(e); }
        std::cout << "Starting surface segmentation on: " << downsampledFilePath << std::endl;
        std::cout << "[SPLITTER-234] rule=" << (planeRule ? "PLANE-CONTINUITY" : "PCL-REGION-GROWING")
                  << " smoothDeg=" << smoothnessAngleThreshold << " curv=" << curvatureThreshold
                  << " joinDeg=" << planeJoinDeg << " distMM=" << planeDistMM << " window=" << planeWindow
                  << " paper=" << (paperChain ? "PAPER-CHAIN" : "off") << " theta=" << paperTheta << " kappa=" << paperKappa << " nb=" << paperNB << std::endl;
        surfaceSegmentation(downsampledFilePath, minCluster, noOfNeighbours, smoothnessAngleThreshold, curvatureThreshold,
            planeRule, planeJoinDeg, planeDistMM, planeWindow,
            paperChain, paperTheta, paperKappa, paperNB, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC);

		std::string tempFileName0 = intermediatePath + "tmpSurfaceCluster_Improved_0.ply";
		std::string tempFileName1 = intermediatePath + "tmpSurfaceCluster_Improved_1.ply";
        
        std::string outputFileName0 = dataPath + fileNameOnly + "_Surface_0.ply";
        std::string outputFileName1 = dataPath + fileNameOnly + "_Surface_1.ply";
        
        std::cout << "Ply to XYZ start" << std::endl;
        
        if (fs::exists(tempFileName0)) {
            fs::copy_file(tempFileName0, outputFileName0, fs::copy_options::overwrite_existing);
            convertPLYtoXYZ(outputFileName0, dataPath + fileNameOnly + "_Surface_0.xyz", false);
        } else {
            std::cout << "Warning: Source file not found: " << tempFileName0 << std::endl;
        }

        if (fs::exists(tempFileName1)) {
            fs::copy_file(tempFileName1, outputFileName1, fs::copy_options::overwrite_existing);
            convertPLYtoXYZ(outputFileName1, dataPath + fileNameOnly + "_Surface_1.xyz", false);
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
