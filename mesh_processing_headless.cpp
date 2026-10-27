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


// TICKET 27: this orders the de-duplication's copy of a finished surface. It used to compare x
// alone, which cannot put equal (x,y,z) positions next to each other, so the adjacent-equality
// loop in finishImprovedSurface could not group them. No other code sorts with it.
struct myclass2 {
	bool operator() (pcl::PointNormal i, pcl::PointNormal j)
	{
		if (i.x != j.x) return (i.x < j.x);
		if (i.y != j.y) return (i.y < j.y);
		return (i.z < j.z);
	}
} myobject2;

// TICKET 27: SFS_DEDUPE=on writes each distinct position of a finished surface once. Unset, empty,
// "off" or anything else keeps today's cloud, duplicates included. Declared here because
// finishImprovedSurface reads it and is defined further down.
static bool g_dedupeOn27 = false;


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

// ---------------------------------------------------------------------------------------
// TICKET 24: how many neighbours a surface normal is estimated from.
//
// Today (the line this ticket is about) the count is a function of the point count:
//     nb_neighbors = std::max(5, std::min(20, (int)points.size() / 1000));
// so a 2 000-point sherd is triangulated from five neighbours whatever its sampling radius
// is, and only a cloud past 20 000 points ever gets twenty. That is a rule about how big the
// cloud is, not about the surface, and it is the count the two walls of a sherd are read with.
//
//   SFS_NORMAL_MODE=count|radius   count (default) is today's rule, untouched below; radius
//                                  picks neighbours by a physical radius instead.
//   SFS_NORMAL_RADIUS_MM=<mm|auto> the radius. auto = SFS_NORMAL_RADIUS_MULT x the piece's own
//                                  measured nearest-neighbour spacing s0 (the ticket-22 probe,
//                                  [SPACING-22] s0MM). 0 (default) is today.
//   SFS_NORMAL_RADIUS_MULT=<f>     multiple of s0 for auto (default 2).
//   SFS_NORMAL_MIN_K=<n>           floor on the neighbours a radius picks (default 5, today's
//   SFS_NORMAL_MAX_K=<n>           floor) and cap (default 20, today's cap): a radius on a
//                                  sparse cloud can otherwise pick two neighbours, which is
//                                  worse than five.
//   SFS_NBRS_FILE=<path>           optional instrument; per-point rows "call<TAB>index<TAB>count".
//
// Every default leaves the count path exactly as it was: the mode is "count", the radius is 0,
// and the count branch is the code that was already there plus one log line.
// ---------------------------------------------------------------------------------------
static std::string g_normalMode = "count";
static double g_normalRadiusMM = 0.0;
static std::string g_normalRadiusMMRaw = "0";
static bool g_normalRadiusAuto = false;
static double g_normalRadiusMult = 2.0;
static int g_normalMinK = 5;
static int g_normalMaxK = 20;
static double g_pieceS0MM = 0.0;
static double g_pieceDiagMM = 0.0;
static std::string g_nbrsFile;
static int g_normalCall = 0;

// TICKET 24: median of a count vector (0 when empty).
static int n24Median(std::vector<int> v)
{
	if (v.empty()) return 0;
	std::sort(v.begin(), v.end());
	return v[v.size() / 2];
}

// TICKET 24: PCA normals from a physical radius. CGAL's pca_estimate_normals takes a count, so
// the radius path does its own PCA over the neighbours a radius picks and leaves the count path
// on CGAL untouched. Reports the clamps and returns the k to hand MST orientation.
static int estimateNormalsRadius(std::list<PointVectorPair>& pts, double radiusMM,
                                 int minK, int maxK, std::vector<int>& used,
                                 int& floored, int& capped, double& cloudSpacingMM)
{
	std::vector<Eigen::Vector3d> P;
	P.reserve(pts.size());
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
	cloud->points.reserve(pts.size());
	for (std::list<PointVectorPair>::const_iterator it = pts.begin(); it != pts.end(); ++it)
	{
		const double x = CGAL::to_double(it->first.x());
		const double y = CGAL::to_double(it->first.y());
		const double z = CGAL::to_double(it->first.z());
		P.push_back(Eigen::Vector3d(x, y, z));
		pcl::PointXYZ q; q.x = (float)x; q.y = (float)y; q.z = (float)z;
		cloud->points.push_back(q);
	}
	cloud->width = (uint32_t)cloud->points.size();
	cloud->height = 1;
	cloud->is_dense = true;
	const int nAll = (int)cloud->points.size();
	pcl::KdTreeFLANN<pcl::PointXYZ> tree;
	tree.setInputCloud(cloud);

	// the cloud's own spacing, so a radius can be read against what it is sampling
	std::vector<double> nn;
	nn.reserve(nAll);
	for (int i = 0; i < nAll && nAll > 1; ++i)
	{
		std::vector<int> k2(2); std::vector<float> d2(2);
		if (tree.nearestKSearch(cloud->points[i], 2, k2, d2) >= 2)
			nn.push_back(std::sqrt((double)d2[1]));
	}
	if (!nn.empty()) { std::sort(nn.begin(), nn.end()); cloudSpacingMM = nn[nn.size() / 2]; }

	// auto = a multiple of the spacing of the cloud this call is handed (the downsampled surface
	// cloud), not of the raw scan: the raw scan is 0.02-0.08 mm spaced and a radius that small
	// picks two neighbours. The raw probe's s0 is printed beside it ([NORMAL-24-SWITCH] s0MM).
	double rEff = radiusMM;
	if (g_normalRadiusAuto && cloudSpacingMM > 0.0)
	{
		rEff = g_normalRadiusMult * cloudSpacingMM;
		g_normalRadiusMM = rEff;
	}

	std::vector<int> idx; std::vector<float> sqd;
	used.assign(P.size(), 0);
	floored = 0; capped = 0;
	int i = 0;
	for (std::list<PointVectorPair>::iterator it = pts.begin(); it != pts.end(); ++it, ++i)
	{
		idx.clear(); sqd.clear();
		int got = tree.radiusSearch(cloud->points[i], (float)rEff, idx, sqd, 0);
		if (got < minK)
		{
			++floored;
			got = tree.nearestKSearch(cloud->points[i], std::min(nAll, minK), idx, sqd);
		}
		else if (got > maxK)
		{
			++capped;
			got = maxK;
		}
		if (got < 3 && nAll >= 3)   // a plane cannot be fitted to fewer than three points
			got = tree.nearestKSearch(cloud->points[i], 3, idx, sqd);
		used[i] = got;

		Eigen::Vector3d c = Eigen::Vector3d::Zero();
		for (int k = 0; k < got; ++k) c += P[idx[k]];
		c /= (double)got;
		Eigen::Matrix3d cov = Eigen::Matrix3d::Zero();
		for (int k = 0; k < got; ++k)
		{
			const Eigen::Vector3d d = P[idx[k]] - c;
			cov += d * d.transpose();
		}
		cov /= (double)got;
		Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> es(cov);
		Eigen::Vector3d n = es.eigenvectors().col(0);   // smallest eigenvalue = plane normal
		const double ln = n.norm();
		if (ln > 0.0) n /= ln;
		it->second = VectorCGAL(n[0], n[1], n[2]);
	}
	if (!g_nbrsFile.empty())
	{
		std::ofstream nf(g_nbrsFile.c_str(), std::ofstream::app);
		if (nf.is_open())
		{
			for (size_t k = 0; k < used.size(); ++k)
				nf << g_normalCall << "\t" << k << "\t" << used[k] << "\n";
		}
	}
	return std::max(minK, std::min(maxK, n24Median(used)));
}

// TICKET 24: instrument only. When SFS_NORMAL_DUMP_DIR is set, each call's own normals PLY is
// copied there under its call index, so the per-point angle against the mesh can be measured
// before the stage (and the copy) is deleted with the counted record.
static std::string g_normalDumpDir;

static void dumpNormalsPly24(const std::string& src, int call)
{
	if (g_normalDumpDir.empty() || fileNameOnly.empty()) return;
	const std::string dst = g_normalDumpDir + "/" + fileNameOnly + "_call" + std::to_string(call) + ".ply";
	std::ifstream in(src.c_str(), std::ios::binary);
	if (!in.is_open()) return;
	std::ofstream out(dst.c_str(), std::ios::binary);
	if (!out.is_open()) return;
	out << in.rdbuf();
	std::cout << "[NORMAL-24] dump piece=" << fileNameOnly << " call=" << call
	          << " path=" << dst << std::endl;
}

// TICKET 24: one line per normal-estimation call, so no arm has to be believed about itself.
static void printNormalLine24(size_t npts, const std::vector<int>& used, int kCount,
                              int kOrient, int floored, int capped, double cloudSpacingMM)
{
	const bool radiusMode = (g_normalMode == "radius" && (g_normalRadiusMM > 0.0 || g_normalRadiusAuto));
	std::cout << "[NORMAL-24] piece=" << (fileNameOnly.empty() ? "NA" : fileNameOnly)
	          << " call=" << g_normalCall
	          << " mode=" << (radiusMode ? "radius" : "count")
	          << " n=" << npts;
	if (radiusMode)
	{
		std::cout << " radiusMM=" << g_normalRadiusMM
		          << " radiusFrom=" << (g_normalRadiusAuto ? "auto" : "fixed")
		          << " mult=" << g_normalRadiusMult
		          << " s0MM=" << g_pieceS0MM
		          << " minK=" << g_normalMinK << " maxK=" << g_normalMaxK;
	}
	else
	{
		std::cout << " k=" << kCount;
	}
	if (radiusMode && !used.empty())
	{
		std::vector<int> v(used);
		std::sort(v.begin(), v.end());
		double sum = 0.0;
		for (size_t i = 0; i < v.size(); ++i) sum += v[i];
		const int p50 = v[v.size() / 2];
		const int p90 = v[(size_t)(0.9 * (double)(v.size() - 1))];
		std::cout << " nbrMin=" << v.front() << " nbrMedian=" << p50
		          << " nbrP90=" << p90 << " nbrMax=" << v.back()
		          << " nbrMean=" << (sum / (double)v.size())
		          << " flooredToMinK=" << floored << " cappedAtMaxK=" << capped
		          << " orientK=" << kOrient << " cloudSpacingMM=" << cloudSpacingMM;
	}
	if (!g_normalDumpDir.empty() && !fileNameOnly.empty())
		std::cout << " dumpCall=" << g_normalDumpDir << "/" << fileNameOnly
		          << "_call" << g_normalCall << ".ply";
	std::cout << std::endl;
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

	// TICKET 24: in radius mode the neighbours are chosen by a physical distance instead of by
	// how many points the cloud happens to have. CGAL's pca_estimate_normals takes a count only,
	// so the radius path fits its own plane per point (estimateNormalsRadius) and leaves the
	// count path below byte-for-byte as it was; MST orientation is CGAL's in both modes.
	const size_t n24npts = points.size();
	const bool n24radius = (g_normalMode == "radius" && (g_normalRadiusMM > 0.0 || g_normalRadiusAuto));
	std::vector<int> n24used;
	int n24floored = 0;
	int n24capped = 0;
	double n24spacing = 0.0;
	int n24orientK = nb_neighbors;

	if (n24radius)
	{
		const int n24minK = std::max(3, std::min(g_normalMinK, g_normalMaxK));
		n24orientK = estimateNormalsRadius(points, g_normalRadiusMM, n24minK, g_normalMaxK,
		                                   n24used, n24floored, n24capped, n24spacing);
	}
	else
	{
		// Estimates normals direction.
		CGAL::pca_estimate_normals<Concurrency_tag>
			(points, nb_neighbors,
				CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
				normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	}
	std::cout << "[DEBUG getNormalsOnSurface] PCA normal estimation complete." << std::endl;

	// Orients normals.
	std::cout << "[DEBUG getNormalsOnSurface] Orienting normals with MST..." << std::endl;
	std::list<PointVectorPair>::iterator unoriented_points_begin =
		CGAL::mst_orient_normals(points, n24orientK,
			CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()).
			normal_map(CGAL::Second_of_pair_property_map<PointVectorPair>()));
	std::cout << "[DEBUG getNormalsOnSurface] MST orientation complete." << std::endl;
	printNormalLine24(n24npts, n24used, nb_neighbors, n24orientK, n24floored, n24capped, n24spacing);
	const int n24callId = g_normalCall;
	++g_normalCall;
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
			dumpNormalsPly24(fragmentMeshFile + "_SampledWithNormals.ply", n24callId); // TICKET 24 instrument
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

// TICKET 22: the B-spline boundary step. The fit is shared by both reassignment modes,
// so that only the admission rule differs between them.
struct FittedSplineSurface
{
	pcl::on_nurbs::NurbsDataSurface data;
	pcl::on_nurbs::FittingSurface* fit;
	FittedSplineSurface() : fit(nullptr) {}
	~FittedSplineSurface() { delete fit; }
};

// TICKET 22: spacing this piece was sampled at, and the count scale derived from it.
static double g_effectiveSpacingMM = 0.6;
static double g_countScale = 1.0;

// TICKET 23: a piece that keeps one cluster is one surface, not nothing.
// SFS_SINGLE_CLUSTER=off (default) keeps today's behaviour exactly: the single cluster is
// built, dropped, and main warns twice about two temp files that were never written.
// =write runs the same boundary improvement the two-cluster path runs on that cluster and
// writes it as tmpSurfaceCluster_Improved_0.ply, so it becomes Surface_0.
static std::string g_singleClusterMode = "off";
// TICKET 23: SFS_FLOOR_CEILING=<fraction> (default off) bounds the scaled minCluster at
// that fraction of the piece's own post-downsample point count, so a finer spacing cannot
// ask for a floor larger than the piece; off leaves the floor exactly as it was.
static double g_floorCeilingFrac = 0.0;
static bool g_floorCeilingOn = false;
static bool g_countScaleAuto = false;

// TICKET 26: the admission window in the B-spline boundary step is a measurement, not the
// literal 3 mm. SFS_WINDOW_MODE picks the scheme, SFS_WINDOW_K scales W1's residual,
// SFS_WINDOW_CLAMP_MM bounds every scheme, SFS_WINDOW_REPORT appends one row per fitted
// surface. Defaults reproduce the 3 mm window exactly.
static std::string g_windowMode = "literal";
static double g_windowK = 5.0;
static double g_windowClampLoMM = 0.5;
static double g_windowClampHiMM = 6.0;
static std::string g_windowReport;

// TICKET 23: per-piece record, filled by surfaceSegmentation and printed by main, so every
// piece announces two surfaces, one, or none -- with the numbers that decided it.
struct PieceStatus23
{
	std::string piece;
	int npts = -1;
	int retries = 0;
	int finalClusters = -1;
	std::string finalSizes = "none";
	int floorUsed = -1;
	int floorFrom = -1;
	bool capped = false;
	int singleSurfacePoints = -1;
};
static PieceStatus23 g_status23;

// TICKET 23: vertex count from a PLY header, so the status can state what was written.
static int plyVertexCount23(const std::string& f)
{
	std::ifstream in(f.c_str());
	if (!in.is_open()) return -1;
	std::string line;
	int n = -1;
	while (std::getline(in, line))
	{
		std::istringstream ls(line);
		std::string a, b;
		ls >> a;
		if (a == "end_header") break;
		if (a == "element") { ls >> b; if (b == "vertex") ls >> n; }
	}
	return n;
}

void fitSplineSurfaceToCluster(pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud, FittedSplineSurface& out)
{
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_OriginalSurface(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_Sampled(new pcl::PointCloud<pcl::PointXYZ>);

	pcl::copyPointCloud(*segmentedSurfacePointCloud, *cloud_OriginalSurface);

	pcl::RandomSample<pcl::PointXYZ> rs;
	rs.setInputCloud(cloud_OriginalSurface);
	rs.setSample(10000);
	rs.filter(*cloud_Sampled);

	pcl::io::savePCDFile("cloudForSpline.pcd", *cloud_Sampled);

	string pcd_file = "cloudForSpline.pcd";

	printf("  loading %s\n", pcd_file.c_str());
	pcl::PointCloud<Point>::Ptr cloud(new pcl::PointCloud<Point>);
	pcl::PCLPointCloud2 cloud2;

	if (pcl::io::loadPCDFile(pcd_file, cloud2) == -1)
		throw std::runtime_error("  PCD file not found.");

	fromPCLPointCloud2(cloud2, *cloud);
	PointCloud2Vector3d(cloud, out.data.interior);
	printf("  %zu points in data set\n", cloud->size());

	unsigned order(3);
	unsigned refinement(3);
	unsigned iterations(8);

	pcl::on_nurbs::FittingSurface::Parameter params;
	params.interior_smoothness = 0.2;
	params.interior_weight = 1.0;
	params.boundary_smoothness = 0.4;
	params.boundary_weight = 0.0;

	printf("  surface fitting ...\n");
	ON_NurbsSurface nurbs = pcl::on_nurbs::FittingSurface::initNurbsPCABoundingBox(order, &out.data);
	out.fit = new pcl::on_nurbs::FittingSurface(&out.data, nurbs);

	for (unsigned i = 0; i < refinement; i++)
	{
		out.fit->refine(0);
		out.fit->refine(1);
		out.fit->assemble(params);
		out.fit->solve();
	}

	for (unsigned i = 0; i < iterations; i++)
	{
		out.fit->assemble(params);
		out.fit->solve();
	}
}

void finishImprovedSurface(pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud,
	pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud_other,
	pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud,
	int surfaceIndex27 = -1) // TICKET 27: which written surface this call finishes, for the log line
{
	if (improvedSurfacePointCloud_other->points.size() > improvedSurfacePointCloud->points.size())
	{
		pcl::copyPointCloud(*improvedSurfacePointCloud_other, *improvedSurfacePointCloud);
	}

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

	const long dedupeIn27 = (long)vectorPointNormal.size();
	long dedupeOut27 = 0;
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
		// TICKET 27: the last sorted element has no successor to differ from, so it is always kept.
		// The loop stops at size()-1 and used to drop it.
		improvedSurfacePointCloudNoDuplicates->points.push_back(vectorPointNormal[vectorPointNormal.size() - 1]);

		improvedSurfacePointCloudNoDuplicates->width = improvedSurfacePointCloudNoDuplicates->points.size();
		improvedSurfacePointCloudNoDuplicates->height = 1;
		dedupeOut27 = (long)improvedSurfacePointCloudNoDuplicates->points.size();

		// TICKET 27: with the switch on, the de-duplicated cloud is what the callers export; with it
		// unset nothing is assigned and the surface is the cloud this function built.
		if (g_dedupeOn27)
		{
			improvedSurfacePointCloud->points = improvedSurfacePointCloudNoDuplicates->points;
			improvedSurfacePointCloud->width = improvedSurfacePointCloudNoDuplicates->width;
			improvedSurfacePointCloud->height = improvedSurfacePointCloudNoDuplicates->height;
		}
	}
	std::cout << "[DEDUPE-27] surface=" << surfaceIndex27
		<< " mode=" << (g_dedupeOn27 ? "on" : "off")
		<< " in=" << dedupeIn27 << " out=" << dedupeOut27 << std::endl;
}

// TICKET 22: SFS_SPACING_POLICY=piece needs the piece's bounding-box diagonal and its
// own median nearest-neighbour spacing, both measured on the raw cloud.
void measurePieceSpacing(const std::string& pcdFile, double& diagMM, double& s0MM)
{
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
	if (pcl::io::loadPCDFile<pcl::PointXYZ>(pcdFile, *cloud) == -1)
		throw std::runtime_error("  PCD file not found: " + pcdFile);

	pcl::PointCloud<pcl::PointXYZ>::Ptr finiteCloud(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < cloud->points.size(); i++)
	{
		const pcl::PointXYZ& p = cloud->points[i];
		if (std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z))
			finiteCloud->points.push_back(p);
	}
	finiteCloud->width = static_cast<int>(finiteCloud->points.size());
	finiteCloud->height = 1;
	if (finiteCloud->points.empty())
		throw std::runtime_error("  PCD file has no finite points: " + pcdFile);

	Eigen::Vector4f minPt, maxPt;
	pcl::getMinMax3D(*finiteCloud, minPt, maxPt);
	double dx = maxPt[0] - minPt[0];
	double dy = maxPt[1] - minPt[1];
	double dz = maxPt[2] - minPt[2];
	diagMM = std::sqrt(dx * dx + dy * dy + dz * dz);

	pcl::KdTreeFLANN<pcl::PointXYZ> tree;
	tree.setInputCloud(finiteCloud);
	std::vector<double> nnDist;
	nnDist.reserve(finiteCloud->points.size());
	std::vector<int> nbrIdx(2);
	std::vector<float> nbrSqDist(2);
	for (size_t i = 0; i < finiteCloud->points.size(); i++)
	{
		if (tree.nearestKSearch(finiteCloud->points[i], 2, nbrIdx, nbrSqDist) >= 2)
			nnDist.push_back(std::sqrt(static_cast<double>(nbrSqDist[1])));
	}
	if (nnDist.empty())
		throw std::runtime_error("  could not measure nearest-neighbour spacing: " + pcdFile);
	std::sort(nnDist.begin(), nnDist.end());
	s0MM = nnDist[nnDist.size() / 2];
}

// TICKET 26: what the window is worth on this piece. residualMM is W1's r -- the median
// distance from the cluster's own points to its fitted spline; otherMM is W2's d -- the
// shortest distance between the fitted surface and any other surviving cluster. Both are
// NaN when the data to measure them is not there, and the caller says so rather than
// substituting a plausible number.
struct Window26Window
{
	double residualMM;
	double otherGridMM;
	double otherProjMM;
	double otherMM;
	double rawMM;
	double clampedMM;
	double clampLoMM;
	double clampHiMM;
	long residualN;
	long otherN;
	long ownN;
	long otherPointsN;
	std::string rule;
	std::string reason;
	Window26Window()
		: residualMM(NAN), otherGridMM(NAN), otherProjMM(NAN), otherMM(NAN)
		, rawMM(3.0), clampedMM(3.0), clampLoMM(0.5), clampHiMM(6.0)
		, residualN(0), otherN(0), ownN(0), otherPointsN(0)
		, rule("literal"), reason("ok") {}
};

static void window26FormatMM(char* buf, size_t n, double v)
{
	if (std::isfinite(v)) snprintf(buf, n, "%.6f", v);
	else snprintf(buf, n, "na");
}

// ============================================================================
// TICKET 25: dump the geometry at every step. Observation only, one switch.
//
// SFS_DUMP_STAGE=<dir> arms it: rung files go to <dir>/<piece>/r<N>_<name>.ply with a
// r<N>_<name>.json sidecar stating the values the step actually used. Unset (the
// default) writes nothing at all -- no directory is created, no file is opened.
// SFS_DUMP_PIECES=<name,name,...> restricts which pieces are dumped.
//
// Nothing below changes a threshold, a tolerance, a growth rule, a merge rule, a
// reassignment rule or a write rule. Every label written here is a copy of one the
// step had already decided, and the reason code only records which branch of the
// existing code that point took.
//
// Rungs, all five over the same point set except rung 1:
//   r1_downsampled        the cloud the clustering will read (written by the density call)
//   r2_clusters_premerge  cluster id per point, as growPaper234 left it, before any merge
//   r3_after_merge        cluster id per point after mergePaper234 + classifyAndOrderPaper234
//   r4_after_reassign     cluster id per point + the admission decision of the boundary step
//   r5_write              which written surface carries each point's position, and which none
// ============================================================================
static const int DR25_NONE = 0;          // r1: no label exists yet
static const int DR25_CLAIMED = 1;       // r2/r3: claimed by a cluster that is still its own
static const int DR25_MERGED = 2;        // r3: its pre-merge cluster was absorbed into another
static const int DR25_ADMIT_OWN = 3;     // r4: admitted to its own cluster's surface
static const int DR25_ADMIT_OTHER = 4;   // r4: admitted to the other cluster's surface only
static const int DR25_REJECT_DIST = 5;   // r4: rejected, further from the spline than the window
static const int DR25_REJECT_NORMAL = 6; // r4: inside the window, angle in [40,140] deg
static const int DR25_WRITTEN = 7;       // r5: a vertex of a written surface carries this position
static const int DR25_NOT_WRITTEN = 8;   // r5: no written surface carries this position

static std::string g_dumpStageRoot25;             // SFS_DUMP_STAGE, empty = off
static std::vector<std::string> g_dumpPieceList25; // SFS_DUMP_PIECES
static std::string g_dumpPieceName25;
static std::string g_dumpPieceDir25;
static bool g_dumpOn25 = false;

// Per-point and per-pass records the steps fill while the switch is armed.
static std::vector<int> g_r4Code25;       // rung 4 decision per point of the segmentation cloud
static Window26Window g_r4Window25[2];    // the window each fit actually used
static long g_r4Own25[2] = { 0, 0 };
static long g_r4Other25[2] = { 0, 0 };
static long g_r4Cand25[2] = { 0, 0 };
static long g_r4Final25[2] = { 0, 0 };
static int g_r4OtherCopied25[2] = { 0, 0 };
static int g_r4Passes25 = 0;

struct DumpPairStats25
{
	long pairs;
	double nDot;
	double curvInto, curvFrom;
	double inNDot, inCDiff;
	bool fired;
	DumpPairStats25() : pairs(0), nDot(NAN), curvInto(NAN), curvFrom(NAN)
		, inNDot(NAN), inCDiff(NAN), fired(false) {}
};
static DumpPairStats25 g_pairStats25;

struct DumpMergeEvent25
{
	int pass;
	int idInto, idFrom;
	int sizeIntoBefore, sizeFromBefore;
	std::vector<int> tagsInto, tagsFrom;
	DumpPairStats25 stats;
};
static std::vector<DumpMergeEvent25> g_mergeEvents25;
static int g_mergePasses25 = 0;
static long g_mergeTested25 = 0;

// TICKET 25: per-point labels indexed by the point's own position, so the caller's re-sort
// and its interior-face swap cannot move them. Orig is the cluster the point entered the
// merge in; winner is the pre-merge id of the cluster that survived into its final cluster.
static std::vector<int> g_pointOrigTags25;
static std::vector<int> g_pointWinnerTags25;
// -1 when the classify step did not run, 1 when it swapped the two faces, 0 when it kept them.
static int g_classifySwap25 = -1;

struct DumpPoint25 { float x, y, z, nx, ny, nz; };

// A position key with plain float comparison: every coordinate here is copied from the
// same source values, so exact equality is the right test and no bit pattern is needed.
struct DumpPos25
{
	float x, y, z;
	bool operator<(const DumpPos25& o) const
	{
		if (x != o.x) return x < o.x;
		if (y != o.y) return y < o.y;
		return z < o.z;
	}
	bool operator==(const DumpPos25& o) const
	{
		return x == o.x && y == o.y && z == o.z;
	}
};

static std::string dumpFmt25(double v)
{
	if (!std::isfinite(v)) return std::string("null");
	char buf[64];
	snprintf(buf, sizeof(buf), "%.6f", v);
	return std::string(buf);
}

static std::string dumpJsonStr25(const std::string& s)
{
	std::string out = "\"";
	for (size_t i = 0; i < s.size(); ++i)
	{
		const char c = s[i];
		if (c == '"' || c == '\\') { out += '\\'; out += c; }
		else if (c == '\n') out += "\\n";
		else out += c;
	}
	out += "\"";
	return out;
}

static std::string dumpIntList25(const std::vector<int>& v)
{
	std::ostringstream o;
	o << "[";
	for (size_t i = 0; i < v.size(); ++i) { if (i) o << ", "; o << v[i]; }
	o << "]";
	return o.str();
}

static std::string dumpSizesJson25(const std::vector<pcl::PointIndices>& clusters)
{
	std::ostringstream o;
	o << "[";
	for (size_t i = 0; i < clusters.size(); ++i) { if (i) o << ", "; o << clusters[i].indices.size(); }
	o << "]";
	return o.str();
}

static std::string dumpMergesJson25()
{
	std::ostringstream o;
	o << "[";
	for (size_t i = 0; i < g_mergeEvents25.size(); ++i)
	{
		const DumpMergeEvent25& e = g_mergeEvents25[i];
		if (i) o << ", ";
		o << "{ \"pass\": " << e.pass
			<< ", \"into_id\": " << e.idInto << ", \"from_id\": " << e.idFrom
			<< ", \"into_size_before\": " << e.sizeIntoBefore << ", \"from_size_before\": " << e.sizeFromBefore
			<< ", \"into_tags\": " << dumpIntList25(e.tagsInto)
			<< ", \"from_tags\": " << dumpIntList25(e.tagsFrom)
			<< ", \"boundary_pairs\": " << e.stats.pairs
			<< ", \"normal_dot\": " << dumpFmt25(e.stats.nDot)
			<< ", \"curv_into\": " << dumpFmt25(e.stats.curvInto)
			<< ", \"curv_from\": " << dumpFmt25(e.stats.curvFrom)
			<< ", \"internal_normal_dot\": " << dumpFmt25(e.stats.inNDot)
			<< ", \"internal_curv_diff\": " << dumpFmt25(e.stats.inCDiff)
			<< " }";
	}
	o << "]";
	return o.str();
}

// Selection is per piece. An unset SFS_DUMP_STAGE disables everything, so this is also
// the one place that decides whether a dump directory is ever created.
static bool dumpPieceSelected25(const std::string& piece)
{
	if (g_dumpStageRoot25.empty()) return false;
	if (g_dumpPieceList25.empty()) return true;
	for (size_t i = 0; i < g_dumpPieceList25.size(); ++i)
		if (g_dumpPieceList25[i] == piece) return true;
	return false;
}

static void dumpReadSwitch25()
{
	g_dumpStageRoot25.clear();
	g_dumpPieceList25.clear();
	if (const char* e = std::getenv("SFS_DUMP_STAGE")) { if (*e) g_dumpStageRoot25 = e; }
	if (const char* e = std::getenv("SFS_DUMP_PIECES"))
	{
		if (*e)
		{
			const std::string s = e;
			size_t start = 0;
			while (start <= s.size())
			{
				size_t comma = s.find(',', start);
				if (comma == std::string::npos) comma = s.size();
				std::string tok = s.substr(start, comma - start);
				while (!tok.empty() && (tok[0] == ' ' || tok[0] == '\t')) tok.erase(0, 1);
				while (!tok.empty() && (tok[tok.size() - 1] == ' ' || tok[tok.size() - 1] == '\t')) tok.erase(tok.size() - 1);
				if (!tok.empty()) g_dumpPieceList25.push_back(tok);
				if (comma == s.size()) break;
				start = comma + 1;
			}
		}
	}
}

// Called once per piece before any step runs.
static void dumpBeginPiece25(const std::string& piece)
{
	g_dumpOn25 = false;
	g_dumpPieceName25 = piece;
	g_dumpPieceDir25.clear();
	dumpReadSwitch25();
	if (g_dumpStageRoot25.empty()) return;
	if (!dumpPieceSelected25(piece))
	{
		std::cout << "[DUMP-25] piece=" << piece << " on=no reason=not-selected" << std::endl;
		return;
	}
	std::string dir = g_dumpStageRoot25;
	if (dir[dir.size() - 1] != '/' && dir[dir.size() - 1] != '\\') dir += "/";
	dir += piece;
	dir += "/";
	std::error_code ec25;
	std::experimental::filesystem::create_directories(std::experimental::filesystem::path(dir), ec25);
	g_dumpPieceDir25 = dir;
	g_dumpOn25 = true;
	std::cout << "[DUMP-25] piece=" << piece << " on=yes dir=" << dir << std::endl;
}

static void dumpWritePly25(const std::string& base, const std::vector<DumpPoint25>& pts,
	const std::vector<int>& cid, const std::vector<int>& reason)
{
	if (!g_dumpOn25) return;
	if (cid.size() != pts.size() || reason.size() != pts.size())
	{
		std::cerr << "[DUMP-25] REFUSED " << base << ".ply: " << pts.size() << " points but "
			<< cid.size() << " cluster ids and " << reason.size() << " reason codes" << std::endl;
		return;
	}
	const std::string path = g_dumpPieceDir25 + base + ".ply";
	std::ofstream o(path.c_str(), std::ios::out | std::ios::trunc | std::ios::binary);
	if (!o.is_open()) { std::cerr << "[DUMP-25] CANNOT WRITE " << path << std::endl; return; }
	o << "ply\nformat ascii 1.0\n";
	o << "comment ticket-25 geometry dump piece=" << g_dumpPieceName25 << " rung=" << base << "\n";
	o << "element vertex " << pts.size() << "\n";
	o << "property float x\nproperty float y\nproperty float z\n";
	o << "property float nx\nproperty float ny\nproperty float nz\n";
	o << "property int cluster_id\nproperty uchar reason\nend_header\n";
	char buf[256];
	for (size_t i = 0; i < pts.size(); ++i)
	{
		snprintf(buf, sizeof(buf), "%.6f %.6f %.6f %.6f %.6f %.6f %d %d",
			(double)pts[i].x, (double)pts[i].y, (double)pts[i].z,
			(double)pts[i].nx, (double)pts[i].ny, (double)pts[i].nz, cid[i], reason[i]);
		o << buf << "\n";
	}
	o.close();
	std::cout << "[DUMP-25] wrote " << path << " points=" << pts.size() << std::endl;
}

static void dumpWriteJson25(const std::string& base, const std::string& fields)
{
	if (!g_dumpOn25) return;
	const std::string path = g_dumpPieceDir25 + base + ".json";
	std::ofstream o(path.c_str(), std::ios::out | std::ios::trunc | std::ios::binary);
	if (!o.is_open()) { std::cerr << "[DUMP-25] CANNOT WRITE " << path << std::endl; return; }
	o << "{ \"rung\": " << dumpJsonStr25(base) << ", \"piece\": " << dumpJsonStr25(g_dumpPieceName25)
		<< ", " << fields << " }\n";
	o.close();
}

// TICKET 25: the input cloud's own point count, read from its PCD header.
static long dumpPcdPoints25(const std::string& path)
{
	std::ifstream f(path.c_str(), std::ios::in | std::ios::binary);
	if (!f.is_open()) return -1;
	std::string line;
	for (int i = 0; i < 30 && std::getline(f, line); ++i)
	{
		if (line.compare(0, 6, "POINTS") == 0) return std::strtol(line.c_str() + 6, NULL, 10);
		if (line.compare(0, 4, "DATA") == 0) break;
	}
	return -1;
}

// The density call's own output, read back: rung 1 is the cloud the next step loads.
static void dumpRung1_25(const std::string& plyPath, const std::string& fields)
{
	if (!g_dumpOn25) return;
	pcl::PointCloud<pcl::PointNormal>::Ptr c(new pcl::PointCloud<pcl::PointNormal>);
	if (pcl::io::loadPLYFile<pcl::PointNormal>(plyPath, *c) != 0)
	{
		std::cerr << "[DUMP-25] cannot read " << plyPath << " for rung 1" << std::endl;
		return;
	}
	std::vector<DumpPoint25> pts;
	std::vector<int> cid, reason;
	for (size_t i = 0; i < c->points.size(); ++i)
	{
		DumpPoint25 p;
		p.x = c->points[i].x; p.y = c->points[i].y; p.z = c->points[i].z;
		p.nx = c->points[i].normal_x; p.ny = c->points[i].normal_y; p.nz = c->points[i].normal_z;
		pts.push_back(p);
		cid.push_back(-1);
		reason.push_back(DR25_NONE);
	}
	dumpWritePly25("r1_downsampled", pts, cid, reason);
	std::ostringstream o;
	o << "\"points_out\": " << c->points.size()
		<< ", \"ply\": " << dumpJsonStr25(g_dumpPieceDir25 + "r1_downsampled.ply")
		<< ", " << fields;
	dumpWriteJson25("r1_downsampled", o.str());
}

// Rungs 2-5 are all over the segmentation cloud, in its own point order, so the four
// files can be diffed point by point. A point whose normal was dropped upstream keeps
// its position and carries a zero normal; the count is reported, not silently filled.
static void dumpRungXYZ25(const std::string& base, const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud,
	const pcl::PointCloud<pcl::Normal>::Ptr& normals,
	const std::vector<int>& cid, const std::vector<int>& reason)
{
	if (!g_dumpOn25) return;
	if (cid.size() != cloud->points.size() || reason.size() != cloud->points.size())
	{
		std::cerr << "[DUMP-25] REFUSED " << base << ".ply: cloud has " << cloud->points.size()
			<< " points, labels " << cid.size() << "/" << reason.size() << std::endl;
		return;
	}
	std::vector<DumpPoint25> pts;
	pts.reserve(cloud->points.size());
	for (size_t i = 0; i < cloud->points.size(); ++i)
	{
		DumpPoint25 p;
		p.x = cloud->points[i].x; p.y = cloud->points[i].y; p.z = cloud->points[i].z;
		if (i < normals->points.size())
		{
			p.nx = normals->points[i].normal_x; p.ny = normals->points[i].normal_y; p.nz = normals->points[i].normal_z;
		}
		else { p.nx = 0.0f; p.ny = 0.0f; p.nz = 0.0f; }
		pts.push_back(p);
	}
	dumpWritePly25(base, pts, cid, reason);
}

// TICKET 25: one fitted surface's window, exactly as ticket 26 printed it for that call.
static std::string dumpWindow25(int surface, const Window26Window& w)
{
	std::ostringstream o;
	o << "{ \"surface\": " << surface
		<< ", \"raw_mm\": " << dumpFmt25(w.rawMM)
		<< ", \"clamped_mm\": " << dumpFmt25(w.clampedMM)
		<< ", \"clamp_lo_mm\": " << dumpFmt25(w.clampLoMM)
		<< ", \"clamp_hi_mm\": " << dumpFmt25(w.clampHiMM)
		<< ", \"rule\": " << dumpJsonStr25(w.rule)
		<< ", \"reason\": " << dumpJsonStr25(w.reason)
		<< ", \"residual_mm\": " << dumpFmt25(w.residualMM)
		<< ", \"other_mm\": " << dumpFmt25(w.otherMM)
		<< ", \"residual_n\": " << w.residualN
		<< ", \"other_n\": " << w.otherN
		<< ", \"own_n\": " << w.ownN
		<< ", \"other_points_n\": " << w.otherPointsN
		<< " }";
	return o.str();
}

// TICKET 25: how many points carry each reason code, so a sidecar reads without a script.
static std::string dumpReasonCounts25(const std::vector<int>& reasons)
{
	long c25[9] = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };
	for (size_t i = 0; i < reasons.size(); ++i)
	{
		const int r25 = reasons[i];
		if (r25 >= 0 && r25 <= 8) ++c25[r25];
	}
	std::ostringstream o;
	o << "{ \"none\": " << c25[0] << ", \"claimed\": " << c25[1]
		<< ", \"merged\": " << c25[2] << ", \"admitted_own\": " << c25[3]
		<< ", \"admitted_other\": " << c25[4] << ", \"rejected_distance\": " << c25[5]
		<< ", \"rejected_normal\": " << c25[6] << ", \"written\": " << c25[7]
		<< ", \"not_written\": " << c25[8] << " }";
	return o.str();
}

// Rung 5 asks the written clouds themselves which positions they carry: the export is
// what the rest of the pipeline reads, so nothing here is inferred from the labels.
static void dumpRung5_25(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud,
	const pcl::PointCloud<pcl::Normal>::Ptr& normals,
	const std::vector<pcl::PointCloud<pcl::PointNormal>::Ptr>& surfaces,
	const std::string& gate, int retry, const std::vector<pcl::PointIndices>& clusters,
	const std::string& fields)
{
	if (!g_dumpOn25) return;
	std::vector<std::vector<DumpPos25> > keys(surfaces.size());
	std::ostringstream o;
	o << "\"surface_vertices\": [";
	for (size_t s = 0; s < surfaces.size(); ++s)
	{
		long distinct = 0;
		if (surfaces[s])
		{
			keys[s].reserve(surfaces[s]->points.size());
			for (size_t i = 0; i < surfaces[s]->points.size(); ++i)
			{
				DumpPos25 k;
				k.x = surfaces[s]->points[i].x; k.y = surfaces[s]->points[i].y; k.z = surfaces[s]->points[i].z;
				if (std::isfinite(k.x) && std::isfinite(k.y) && std::isfinite(k.z)) keys[s].push_back(k);
			}
			std::sort(keys[s].begin(), keys[s].end());
			distinct = (long)(std::unique(keys[s].begin(), keys[s].end()) - keys[s].begin());
			if (s) o << ", ";
			o << "{ \"surface\": " << s << ", \"vertices\": " << surfaces[s]->points.size()
				<< ", \"distinct_positions\": " << distinct << " }";
		}
		else
		{
			if (s) o << ", ";
			o << "{ \"surface\": " << s << ", \"vertices\": 0, \"distinct_positions\": 0 }";
		}
	}
	o << "], \"write_gate\": " << dumpJsonStr25(gate)
		<< ", \"retry\": " << retry
		<< ", \"clusters\": " << dumpSizesJson25(clusters)
		<< ", \"points\": " << cloud->points.size()
		<< ", \"points_without_normal\": " << (cloud->points.size() > normals->points.size() ? cloud->points.size() - normals->points.size() : 0)
		<< ", " << fields;
	std::vector<int> cid(cloud->points.size(), -1);
	std::vector<int> reason(cloud->points.size(), DR25_NOT_WRITTEN);
	long reached0 = 0, reached1 = 0;
	for (size_t i = 0; i < cloud->points.size(); ++i)
	{
		DumpPos25 q;
		q.x = cloud->points[i].x; q.y = cloud->points[i].y; q.z = cloud->points[i].z;
		for (size_t s = 0; s < keys.size(); ++s)
		{
			if (!surfaces[s]) continue;
			if (std::binary_search(keys[s].begin(), keys[s].end(), q))
			{
				cid[i] = (int)s;
				reason[i] = DR25_WRITTEN;
				if (s == 0) ++reached0; else ++reached1;
				break;
			}
		}
	}
	o << ", \"points_on_surface_0\": " << reached0 << ", \"points_on_surface_1\": " << reached1
		<< ", \"points_on_neither\": " << (long)cloud->points.size() - reached0 - reached1;
	dumpRungXYZ25("r5_write", cloud, normals, cid, reason);
	dumpWriteJson25("r5_write", o.str());
}

// W1's r: median distance from the cluster's own points to its fitted spline, measured with
// the same inverse mapping the admission loop uses.
static double window26ResidualMedianMM(pcl::on_nurbs::FittingSurface& fit, const pcl::PointCloud<PointNormal>::Ptr& cluster, long& used)
{
	used = 0;
	if (!cluster || cluster->points.empty()) return NAN;
	std::vector<double> dists;
	dists.reserve(cluster->points.size());
	for (size_t i = 0; i < cluster->points.size(); i++)
	{
		Eigen::Vector3d originalPt(cluster->points[i].x, cluster->points[i].y, cluster->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		Eigen::Vector3d pt, tu, tv, n;
		double error;
		Eigen::Vector2d paramsB = fit.inverseMapping(fit.m_nurbs, originalPt, hintPt, error, pt, tu, tv, 100, 1e-5);
		double point[9];
		fit.m_nurbs.Evaluate(paramsB(0), paramsB(1), 1, 3, point);
		double dx = point[0] - originalPt(0);
		double dy = point[1] - originalPt(1);
		double dz = point[2] - originalPt(2);
		double d = std::sqrt(dx * dx + dy * dy + dz * dz);
		if (!std::isfinite(d)) continue;
		dists.push_back(d);
	}
	if (dists.empty()) return NAN;
	std::sort(dists.begin(), dists.end());
	used = (long)dists.size();
	return dists[dists.size() / 2];
}

// W2's d: the shortest distance between the fitted surface and any other surviving cluster.
// Both directions are measured and the smaller reported -- (a) the fitted surface sampled on a
// 33x33 grid over its own knot domain against the other cluster's points, (b) the other
// cluster's points, strided deterministically to at most 2000, inverse-mapped onto the fit.
static double window26OtherDistanceMM(pcl::on_nurbs::FittingSurface& fit, const pcl::PointCloud<PointNormal>::Ptr& other,
	double& gridMM, double& projMM, long& used)
{
	gridMM = NAN;
	projMM = NAN;
	used = 0;
	if (!other || other->points.empty()) return NAN;

	pcl::PointCloud<pcl::PointXYZ>::Ptr otherXYZ(new pcl::PointCloud<pcl::PointXYZ>);
	otherXYZ->points.reserve(other->points.size());
	for (size_t i = 0; i < other->points.size(); i++)
	{
		pcl::PointXYZ p;
		p.x = other->points[i].x;
		p.y = other->points[i].y;
		p.z = other->points[i].z;
		otherXYZ->points.push_back(p);
	}
	otherXYZ->width = static_cast<int>(otherXYZ->points.size());
	otherXYZ->height = 1;
	pcl::KdTreeFLANN<pcl::PointXYZ> tree;
	tree.setInputCloud(otherXYZ);

	// the fit's parameter domain is [0,1]: PCL's on_nurbs surfaces are initialised over it, and
	// the admission loop's own hint point is (0.5, 0.5).
	double s0 = 0.0, s1 = 1.0, t0 = 0.0, t1 = 1.0;
	const int GRID = 33;
	double bestGrid = HUGE_VAL;
	for (int i = 0; i < GRID; i++)
	{
		double s = s0 + (s1 - s0) * (double)i / (double)(GRID - 1);
		for (int j = 0; j < GRID; j++)
		{
			double t = t0 + (t1 - t0) * (double)j / (double)(GRID - 1);
			double point[9];
			fit.m_nurbs.Evaluate(s, t, 1, 3, point);
			if (!std::isfinite(point[0]) || !std::isfinite(point[1]) || !std::isfinite(point[2])) continue;
			pcl::PointXYZ q;
			q.x = (float)point[0];
			q.y = (float)point[1];
			q.z = (float)point[2];
			std::vector<int> idx;
			std::vector<float> sqd;
			if (tree.nearestKSearch(q, 1, idx, sqd) > 0 && sqd[0] >= 0.0f)
			{
				double d = std::sqrt((double)sqd[0]);
				if (d < bestGrid) bestGrid = d;
			}
		}
	}
	gridMM = (bestGrid == HUGE_VAL) ? NAN : bestGrid;

	size_t stride = otherXYZ->points.size() / 2000;
	if (stride < 1) stride = 1;
	double bestProj = HUGE_VAL;
	for (size_t i = 0; i < otherXYZ->points.size(); i += stride)
	{
		Eigen::Vector3d originalPt(otherXYZ->points[i].x, otherXYZ->points[i].y, otherXYZ->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		Eigen::Vector3d pt, tu, tv, n;
		double error;
		Eigen::Vector2d paramsB = fit.inverseMapping(fit.m_nurbs, originalPt, hintPt, error, pt, tu, tv, 100, 1e-5);
		double point[9];
		fit.m_nurbs.Evaluate(paramsB(0), paramsB(1), 1, 3, point);
		double dx = point[0] - originalPt(0);
		double dy = point[1] - originalPt(1);
		double dz = point[2] - originalPt(2);
		double d = std::sqrt(dx * dx + dy * dy + dz * dz);
		if (!std::isfinite(d)) continue;
		used++;
		if (d < bestProj) bestProj = d;
	}
	projMM = (bestProj == HUGE_VAL) ? NAN : bestProj;

	if (std::isfinite(gridMM) && std::isfinite(projMM)) return std::min(gridMM, projMM);
	if (std::isfinite(gridMM)) return gridMM;
	return projMM;
}

// TICKET 26: pick this fitted surface's window and clamp it. Unavailable measurements fall
// back to the literal 3 mm and say which one was missing; nothing is substituted.
static Window26Window window26Select(pcl::on_nurbs::FittingSurface& fit,
	const pcl::PointCloud<PointNormal>::Ptr& ownCluster,
	const pcl::PointCloud<PointNormal>::Ptr& otherCluster)
{
	Window26Window w;
	w.clampLoMM = g_windowClampLoMM;
	w.clampHiMM = g_windowClampHiMM;
	w.ownN = (long)(ownCluster ? ownCluster->points.size() : 0);
	w.otherPointsN = (long)(otherCluster ? otherCluster->points.size() : 0);

	w.residualMM = window26ResidualMedianMM(fit, ownCluster, w.residualN);
	w.otherMM = window26OtherDistanceMM(fit, otherCluster, w.otherGridMM, w.otherProjMM, w.otherN);
	std::string missing;
	if (!std::isfinite(w.residualMM)) missing = "residual_unavailable";
	if (!std::isfinite(w.otherMM))
	{
		std::string o = (w.otherPointsN == 0) ? "no_other_cluster" : "other_unavailable";
		missing = missing.empty() ? o : (missing + "+" + o);
	}
	if (!missing.empty()) w.reason = missing;

	double raw = 3.0;
	std::string rule = "literal";
	const bool haveResidual = std::isfinite(w.residualMM);
	const bool haveOther = std::isfinite(w.otherMM);
	if (g_windowMode == "literal")
	{
		rule = "literal";
	}
	else if (g_windowMode == "residual")
	{
		if (haveResidual) { raw = g_windowK * w.residualMM; rule = "residual"; }
		else { rule = "literal_fallback"; }
	}
	else if (g_windowMode == "other")
	{
		if (haveOther) { raw = 0.45 * w.otherMM; rule = "other"; }
		else { rule = "literal_fallback"; }
	}
	else if (g_windowMode == "both")
	{
		if (haveResidual && haveOther) { raw = std::min(g_windowK * w.residualMM, 0.45 * w.otherMM); rule = "both"; }
		else if (haveResidual) { raw = g_windowK * w.residualMM; rule = "both_residual_only"; }
		else if (haveOther) { raw = 0.45 * w.otherMM; rule = "both_other_only"; }
		else { rule = "literal_fallback"; }
	}
	else
	{
		rule = "literal_unknown_mode";
	}
	w.rule = rule;
	w.rawMM = raw;
	w.clampedMM = raw;
	if (w.clampedMM < w.clampLoMM) w.clampedMM = w.clampLoMM;
	if (w.clampedMM > w.clampHiMM) w.clampedMM = w.clampHiMM;
	return w;
}

// TICKET 26: the specified line, once per fitted surface per piece, plus a detail line that
// carries the parts the specified line has no room for, plus the optional TSV row.
static void window26Print(int surfaceIndex, const Window26Window& w, long admittedOwn, long admittedOther, long candidates)
{
	char residualBuf[32], otherBuf[32], rawBuf[32], clampedBuf[32];
	char gridBuf[32], projBuf[32];
	window26FormatMM(residualBuf, sizeof(residualBuf), w.residualMM);
	window26FormatMM(otherBuf, sizeof(otherBuf), w.otherMM);
	window26FormatMM(rawBuf, sizeof(rawBuf), w.rawMM);
	window26FormatMM(clampedBuf, sizeof(clampedBuf), w.clampedMM);
	window26FormatMM(gridBuf, sizeof(gridBuf), w.otherGridMM);
	window26FormatMM(projBuf, sizeof(projBuf), w.otherProjMM);

	std::cout << "[WINDOW-26] piece=" << fileNameOnly << " surface=" << surfaceIndex
		<< " mode=" << g_windowMode << " k=" << g_windowK
		<< " residual_mm=" << residualBuf << " other_mm=" << otherBuf
		<< " raw_mm=" << rawBuf << " clamped_mm=" << clampedBuf
		<< " admitted_own=" << admittedOwn << " admitted_other=" << admittedOther << std::endl;

	const bool clampBites = (w.clampedMM != w.rawMM);
	std::cout << "[WINDOW-26-MEASURE] piece=" << fileNameOnly << " surface=" << surfaceIndex
		<< " rule=" << w.rule << " reason=" << w.reason
		<< " clamp_lo_mm=" << w.clampLoMM << " clamp_hi_mm=" << w.clampHiMM
		<< " clamped=" << (clampBites ? "yes" : "no") << " clamped_from_mm=" << rawBuf
		<< " residual_n=" << w.residualN << " other_n=" << w.otherN
		<< " other_grid_mm=" << gridBuf << " other_proj_mm=" << projBuf
		<< " own_cluster_points=" << w.ownN << " other_cluster_points=" << w.otherPointsN
		<< " candidates=" << candidates << std::endl;

	if (!g_windowReport.empty())
	{
		std::ofstream out(g_windowReport.c_str(), std::ios::app);
		if (out.is_open())
		{
			out << fileNameOnly << '\t' << surfaceIndex << '\t' << g_windowMode << '\t' << g_windowK
				<< '\t' << w.rule << '\t' << w.reason
				<< '\t' << residualBuf << '\t' << otherBuf
				<< '\t' << gridBuf << '\t' << projBuf
				<< '\t' << rawBuf << '\t' << clampedBuf
				<< '\t' << w.clampLoMM << '\t' << w.clampHiMM
				<< '\t' << (clampBites ? "yes" : "no") << '\t' << rawBuf
				<< '\t' << w.ownN << '\t' << w.otherPointsN << '\t' << candidates
				<< '\t' << admittedOwn << '\t' << admittedOther
				<< '\t' << w.residualN << '\t' << w.otherN << '\n';
		}
	}
}

// TICKET 26: what the surface actually is after finishImprovedSurface, which is where an empty
// recruited set stops being empty.
static void window26PrintFinal(int surfaceIndex, long ownBefore, long otherBefore, long finalPoints)
{
	std::cout << "[WINDOW-26-FINAL] piece=" << fileNameOnly << " surface=" << surfaceIndex
		<< " admitted_own=" << ownBefore << " admitted_other=" << otherBefore
		<< " other_copied_over=" << ((otherBefore > ownBefore) ? "yes" : "no")
		<< " final_points=" << finalPoints << std::endl;
}

void improveSurfaceBoundaryByFittingBSplineSurface(pcl::PointCloud<PointNormal>::Ptr meshPointCloud,
	pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud,
	pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud,
	int surfaceIndex = 0,
	pcl::PointCloud<PointNormal>::Ptr otherSurvivingCloud = pcl::PointCloud<PointNormal>::Ptr())
{

	string line;
	double d1;
	double d2;
	double d3;
	stringstream ss;
	std::string str;
	std::string file_contents;
	int numberOfPoints;

	FittedSplineSurface fitted;
	fitSplineSurfaceToCluster(segmentedSurfacePointCloud, fitted);
	pcl::on_nurbs::FittingSurface& fit = *fitted.fit;

	// TICKET 26: the admission window for THIS fitted surface, measured on this piece.
	// Literal mode still measures and prints both quantities; only the rule ignores them.
	Window26Window window26 = window26Select(fit, segmentedSurfacePointCloud, otherSurvivingCloud);
	const double windowLenMM = window26.clampedMM;
	long window26AdmittedOwn = 0;
	long window26AdmittedOther = 0;


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
		if (pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < windowLenMM && angleDiff > 140) // TICKET 26: the 3 mm literal is now this surface's clamped measured window (3.0 by default).
		{
			window26AdmittedOwn++;
			pcl::PointNormal ptTmp;
			ptTmp.x = ptOnOriginalMesh.x; // point[0];
			ptTmp.y = ptOnOriginalMesh.y; // point[1];
			ptTmp.z = ptOnOriginalMesh.z; // point[2];
			ptTmp.normal_x = meshPointCloud->points[i].normal_x;  //-normalEst.x;
			ptTmp.normal_y = meshPointCloud->points[i].normal_y; //-normalEst.y;
			ptTmp.normal_z = meshPointCloud->points[i].normal_z; //-normalEst.z;
			improvedSurfacePointCloud->points.push_back(ptTmp);
		}
		else if (pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < windowLenMM && angleDiff < 40) // TICKET 26: same window, other-angle branch.
		{
			window26AdmittedOther++;
			pcl::PointNormal ptTmp;
			ptTmp.x = ptOnOriginalMesh.x; // point[0];
			ptTmp.y = ptOnOriginalMesh.y; // point[1];
			ptTmp.z = ptOnOriginalMesh.z; // point[2];
			ptTmp.normal_x = meshPointCloud->points[i].normal_x;  //-normalEst.x;
			ptTmp.normal_y = meshPointCloud->points[i].normal_y; //-normalEst.y;
			ptTmp.normal_z = meshPointCloud->points[i].normal_z; //-normalEst.z;
			improvedSurfacePointCloud_other->points.push_back(ptTmp);
		}

		// TICKET 25: the same two tests that just admitted or dropped this point, recorded
		// for rung 4. A point touched by both surfaces keeps its strongest claim.
		if (g_dumpOn25 && (size_t)i < g_r4Code25.size())
		{
			const double d25 = pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh);
			int code25 = DR25_REJECT_NORMAL;
			int rank25 = 1;
			if (d25 >= windowLenMM) { code25 = DR25_REJECT_DIST; rank25 = 2; }
			else if (angleDiff > 140) { code25 = DR25_ADMIT_OWN; rank25 = 4; }
			else if (angleDiff < 40) { code25 = DR25_ADMIT_OTHER; rank25 = 3; }
			const int prev25 = g_r4Code25[i];
			int prevRank25 = 0;
			if (prev25 == DR25_ADMIT_OWN) prevRank25 = 4;
			else if (prev25 == DR25_ADMIT_OTHER) prevRank25 = 3;
			else if (prev25 == DR25_REJECT_DIST) prevRank25 = 2;
			else if (prev25 == DR25_REJECT_NORMAL) prevRank25 = 1;
			if (rank25 > prevRank25) g_r4Code25[i] = code25;
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

	bSplineSurface->width = static_cast<int>(bSplineSurface->points.size());
	bSplineSurface->height = 1;
	// pcl::io::savePCDFile("bSplineSurfacePoints.pcd", *bSplineSurface);


	window26Print(surfaceIndex, window26, window26AdmittedOwn, window26AdmittedOther,
		(long)meshPointCloud->points.size());
	if (g_dumpOn25 && surfaceIndex >= 0 && surfaceIndex < 2)
	{
		// TICKET 25: rung 4's sidecar gets the window this call actually used, not a recompute.
		g_r4Window25[surfaceIndex] = window26;
		g_r4Own25[surfaceIndex] = window26AdmittedOwn;
		g_r4Other25[surfaceIndex] = window26AdmittedOther;
		g_r4Cand25[surfaceIndex] = (long)meshPointCloud->points.size();
		++g_r4Passes25;
	}
	const long window26OwnBefore = (long)improvedSurfacePointCloud->points.size();
	const long window26OtherBefore = (long)improvedSurfacePointCloud_other->points.size();

	finishImprovedSurface(improvedSurfacePointCloud, improvedSurfacePointCloud_other, segmentedSurfacePointCloud, surfaceIndex);

	window26PrintFinal(surfaceIndex, window26OwnBefore, window26OtherBefore, (long)improvedSurfacePointCloud->points.size());
	if (g_dumpOn25 && surfaceIndex >= 0 && surfaceIndex < 2)
	{
		g_r4Final25[surfaceIndex] = (long)improvedSurfacePointCloud->points.size();
		g_r4OtherCopied25[surfaceIndex] = (window26OtherBefore > window26OwnBefore) ? 1 : 0;
	}

	projectedPointCloudWithNormals->width = static_cast<int>(projectedPointCloudWithNormals->points.size());
	projectedPointCloudWithNormals->height = 1;
}

// TICKET 22: SFS_REASSIGN_MODE=own. Both clusters are fitted before either surface is
// rewritten, and a candidate point may join a surface only when that surface's spline is
// the nearer of the two; the 3 mm radius and the 140/40 degree angle gates stay as outer caps.
void improveSurfaceBoundaryByFittingBSplineSurfaceOwn(pcl::PointCloud<PointNormal>::Ptr meshPointCloud,
	pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud1,
	pcl::PointCloud<PointNormal>::Ptr segmentedSurfacePointCloud2,
	pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud1,
	pcl::PointCloud<PointNormal>::Ptr improvedSurfacePointCloud2,
	pcl::PointCloud<PointNormal>::Ptr otherSurvivingCloud1 = pcl::PointCloud<PointNormal>::Ptr(),
	pcl::PointCloud<PointNormal>::Ptr otherSurvivingCloud2 = pcl::PointCloud<PointNormal>::Ptr())
{
	FittedSplineSurface fitted1;
	FittedSplineSurface fitted2;
	fitSplineSurfaceToCluster(segmentedSurfacePointCloud1, fitted1);
	fitSplineSurfaceToCluster(segmentedSurfacePointCloud2, fitted2);

	pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePointCloud1_other(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePointCloud2_other(new pcl::PointCloud<pcl::PointNormal>);

	pcl::on_nurbs::FittingSurface* fits[2] = { fitted1.fit, fitted2.fit };

	// TICKET 26: one measured window per fitted surface. "Other surviving" is the caller's union
	// of every other cluster when given, and the opposite cluster otherwise.
	Window26Window window26[2];
	window26[0] = window26Select(*fits[0], segmentedSurfacePointCloud1,
		otherSurvivingCloud1 ? otherSurvivingCloud1 : segmentedSurfacePointCloud2);
	window26[1] = window26Select(*fits[1], segmentedSurfacePointCloud2,
		otherSurvivingCloud2 ? otherSurvivingCloud2 : segmentedSurfacePointCloud1);
	double windowLenMM[2] = { window26[0].clampedMM, window26[1].clampedMM };
	long window26AdmittedOwn[2] = { 0, 0 };
	long window26AdmittedOther[2] = { 0, 0 };

	for (size_t i = 0; i < meshPointCloud->points.size(); i++)
	{
		Eigen::Vector3d originalPt(meshPointCloud->points[i].x, meshPointCloud->points[i].y, meshPointCloud->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		int im_max_steps = 100;
		double im_accuracy = 1e-5;

		pcl::PointXYZ ptOnOriginalMesh;
		ptOnOriginalMesh.x = meshPointCloud->points[i].x;
		ptOnOriginalMesh.y = meshPointCloud->points[i].y;
		ptOnOriginalMesh.z = meshPointCloud->points[i].z;

		pcl::Normal normOnOriginalMesh;
		normOnOriginalMesh.normal_x = meshPointCloud->points[i].normal_x;
		normOnOriginalMesh.normal_y = meshPointCloud->points[i].normal_y;
		normOnOriginalMesh.normal_z = meshPointCloud->points[i].normal_z;
		Eigen::Vector4f eigen_normal_pt2 = normOnOriginalMesh.getNormalVector4fMap();

		double dist[2];
		double angleDiff[2];

		for (int k = 0; k < 2; k++)
		{
			Eigen::Vector3d pt, tu, tv, n;
			double error;
			Eigen::Vector2d paramsB = fits[k]->inverseMapping(fits[k]->m_nurbs, originalPt, hintPt, error, pt, tu, tv, im_max_steps, im_accuracy);

			double point[9];
			ON_3dVector normalEst;
			fits[k]->m_nurbs.Evaluate(paramsB(0), paramsB(1), 1, 3, point);
			fits[k]->m_nurbs.EvNormal(paramsB(0), paramsB(1), normalEst);

			pcl::PointXYZ ptOnFittedSurface;
			ptOnFittedSurface.x = point[0];
			ptOnFittedSurface.y = point[1];
			ptOnFittedSurface.z = point[2];

			pcl::Normal normOnFittedSurface;
			normOnFittedSurface.normal_x = -normalEst.x;
			normOnFittedSurface.normal_y = -normalEst.y;
			normOnFittedSurface.normal_z = -normalEst.z;

			dist[k] = pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh);
			angleDiff[k] = pcl::getAngle3D(normOnFittedSurface.getNormalVector4fMap(), eigen_normal_pt2, true);
		}

		for (int k = 0; k < 2; k++)
		{
			if (!(dist[k] < windowLenMM[k])) continue; // TICKET 26: this surface's clamped measured window (3.0 by default).
			if (!(dist[k] < dist[1 - k])) continue;

			pcl::PointCloud<pcl::PointNormal>::Ptr own = (k == 0) ? improvedSurfacePointCloud1 : improvedSurfacePointCloud2;
			pcl::PointCloud<pcl::PointNormal>::Ptr other = (k == 0) ? improvedSurfacePointCloud1_other : improvedSurfacePointCloud2_other;

			if (angleDiff[k] > 140)
			{
				window26AdmittedOwn[k]++;
				pcl::PointNormal ptTmp;
				ptTmp.x = meshPointCloud->points[i].x;
				ptTmp.y = meshPointCloud->points[i].y;
				ptTmp.z = meshPointCloud->points[i].z;
				ptTmp.normal_x = meshPointCloud->points[i].normal_x;
				ptTmp.normal_y = meshPointCloud->points[i].normal_y;
				ptTmp.normal_z = meshPointCloud->points[i].normal_z;
				own->points.push_back(ptTmp);
			}
			else if (angleDiff[k] < 40)
			{
				window26AdmittedOther[k]++;
				pcl::PointNormal ptTmp;
				ptTmp.x = meshPointCloud->points[i].x;
				ptTmp.y = meshPointCloud->points[i].y;
				ptTmp.z = meshPointCloud->points[i].z;
				ptTmp.normal_x = meshPointCloud->points[i].normal_x;
				ptTmp.normal_y = meshPointCloud->points[i].normal_y;
				ptTmp.normal_z = meshPointCloud->points[i].normal_z;
				other->points.push_back(ptTmp);
			}
		}
	}

	const long window26OwnBefore[2] = { (long)improvedSurfacePointCloud1->points.size(), (long)improvedSurfacePointCloud2->points.size() };
	const long window26OtherBefore[2] = { (long)improvedSurfacePointCloud1_other->points.size(), (long)improvedSurfacePointCloud2_other->points.size() };
	const long window26Candidates = (long)meshPointCloud->points.size();
	window26Print(0, window26[0], window26AdmittedOwn[0], window26AdmittedOther[0], window26Candidates);
	window26Print(1, window26[1], window26AdmittedOwn[1], window26AdmittedOther[1], window26Candidates);

	finishImprovedSurface(improvedSurfacePointCloud1, improvedSurfacePointCloud1_other, segmentedSurfacePointCloud1, 0);
	finishImprovedSurface(improvedSurfacePointCloud2, improvedSurfacePointCloud2_other, segmentedSurfacePointCloud2, 1);

	window26PrintFinal(0, window26OwnBefore[0], window26OtherBefore[0], (long)improvedSurfacePointCloud1->points.size());
	window26PrintFinal(1, window26OwnBefore[1], window26OtherBefore[1], (long)improvedSurfacePointCloud2->points.size());
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


// One merge verdict for a cluster pair. All thresholds are the paper-arm
// operating point (logged by the caller).
// Appendix-A-normative pair verdict (provenance in patch234d.py header).
static bool tryMergePair234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    const std::vector<int>& A, const std::vector<int>& B,
    const std::vector<char>& isBnd,
    const Eigen::Vector3f& axisA, const Eigen::Vector3f& axisB,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k2)
{
    if (A.empty() || B.empty()) return false;
    if (g_dumpOn25) g_pairStats25 = DumpPairStats25();   // TICKET 25: observation only
    // ---- Step 1: boundary subsets, pairs within rhoD, need >= 3 ----
    std::vector<int> bA, bB;
    for (int id : A) if (isBnd[id]) bA.push_back(id);
    for (int id : B) if (isBnd[id]) bB.push_back(id);
    if (bA.empty() || bB.empty()) return false;
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
    for (size_t i = 0; i < sP->size() && pairs.size() < 200; ++i) {
        int sid = (*sP)[i];
        oneI.clear(); oneD.clear();
        if (lT.nearestKSearch(pcloud->points[sid], 1, oneI, oneD) <= 0) continue;
        if (oneD[0] <= rhoD * rhoD) {
            int a = sIsA ? sid : (*lP)[oneI[0]];
            int b = sIsA ? (*lP)[oneI[0]] : sid;
            pairs.push_back(std::make_pair(a, b));
        }
    }
    if (pairs.size() < 3) return false;
    if (g_dumpOn25) g_pairStats25.pairs = (long)pairs.size();
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
    if (nA < 1e-9f || nB < 1e-9f) return false;
    sNA /= nA; sNB /= nB;
    if (g_dumpOn25) g_pairStats25.nDot = (double)sNA.dot(sNB);
    if (sNA.dot(sNB) < rhoN) return false;
    if (g_dumpOn25) { g_pairStats25.curvInto = sCA / (double)pairs.size(); g_pairStats25.curvFrom = sCB / (double)pairs.size(); }
    if (std::fabs(sCA / pairs.size() - sCB / pairs.size()) >= rhoC) return false;
    // ---- Step 3: internal median-point verification ----
    int ia = medianInternal234(pcloud, A, axisA);
    int ib = medianInternal234(pcloud, B, axisB);
    if (ia < 0 || ib < 0) return false;
    Eigen::Vector3f na(pnormals->points[ia].normal_x, pnormals->points[ia].normal_y, pnormals->points[ia].normal_z);
    Eigen::Vector3f nb(pnormals->points[ib].normal_x, pnormals->points[ib].normal_y, pnormals->points[ib].normal_z);
    float la = na.norm(), lb = nb.norm();
    if (la < 1e-9f || lb < 1e-9f) return false;
    if (g_dumpOn25) g_pairStats25.inNDot = (double)(na.dot(nb) / (la * lb));
    if (na.dot(nb) / (la * lb) < rhoInN) return false;
    if (g_dumpOn25) g_pairStats25.inCDiff = std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature));
    if (std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature)) >= rhoInC) return false;
    if (g_dumpOn25) g_pairStats25.fired = true;
    return true;
}

static void mergePaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k1, int k2)
{
    std::cout << "[PAPER-234] appendix-A merge: rhoD=" << rhoD << " rhoN=" << rhoN << " rhoC=" << rhoC
              << " rhoInN=" << rhoInN << " rhoInC=" << rhoInC << " k1=" << k1 << " k2=" << k2 << std::endl;
    const int NP = static_cast<int>(pcloud->points.size());
    // TICKET 25: each cluster's pre-merge ids, carried through every pass and its
    // compaction, so a merge can be reported by identity instead of by size.
    std::vector<std::vector<int> > tags25(pclusters.size());
    for (size_t c25 = 0; c25 < pclusters.size(); ++c25) tags25[c25].push_back(static_cast<int>(c25));
    if (g_dumpOn25)
    {
        g_mergeEvents25.clear();
        g_mergeTested25 = 0;
        g_mergePasses25 = 0;
        g_pointOrigTags25.assign(NP, -1);
        g_pointWinnerTags25.clear();
        for (size_t c25 = 0; c25 < pclusters.size(); ++c25)
            for (size_t k25 = 0; k25 < pclusters[c25].indices.size(); ++k25)
                g_pointOrigTags25[pclusters[c25].indices[k25]] = static_cast<int>(c25);
    }
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
                const bool merged25 = tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, isBnd,
                        axes[i], axes[j], rhoD, rhoN, rhoC, rhoInN, rhoInC, k2);
                if (g_dumpOn25) ++g_mergeTested25;
                if (merged25) {
                    std::cout << "[PAPER-234] pass " << pass << ": merge " << pclusters[j].indices.size() << " into " << pclusters[i].indices.size() << std::endl;
                    if (g_dumpOn25)
                    {
                        DumpMergeEvent25 ev25;
                        ev25.pass = pass;
                        ev25.idInto = static_cast<int>(i);
                        ev25.idFrom = static_cast<int>(j);
                        ev25.sizeIntoBefore = static_cast<int>(pclusters[i].indices.size());
                        ev25.sizeFromBefore = static_cast<int>(pclusters[j].indices.size());
                        ev25.tagsInto = tags25[i];
                        ev25.tagsFrom = tags25[j];
                        ev25.stats = g_pairStats25;
                        g_mergeEvents25.push_back(ev25);
                    }
                    pclusters[i].indices.insert(pclusters[i].indices.end(), pclusters[j].indices.begin(), pclusters[j].indices.end());
                    tags25[i].insert(tags25[i].end(), tags25[j].begin(), tags25[j].end());
                    dead[j] = 1;
                    any = true;
                }
            }
        }
        if (any) {
            std::vector<pcl::PointIndices> kept;
            std::vector<std::vector<int> > keptTags25;
            for (size_t i = 0; i < pclusters.size(); ++i) if (!dead[i]) { kept.push_back(pclusters[i]); keptTags25.push_back(tags25[i]); }
            pclusters.swap(kept);
            tags25.swap(keptTags25);
        }
        std::cout << "[PAPER-234] pass " << pass << " done: " << pclusters.size() << " clusters" << std::endl;
        if (g_dumpOn25) g_mergePasses25 = pass;
        if (pass > 25) break;
    }
    if (g_dumpOn25)
    {
        g_pointWinnerTags25.assign(NP, -1);
        for (size_t c25 = 0; c25 < pclusters.size(); ++c25)
        {
            int winner25 = -1;
            for (size_t k25 = 0; k25 < tags25[c25].size(); ++k25)
                if (winner25 < 0 || tags25[c25][k25] < winner25) winner25 = tags25[c25][k25];
            for (size_t k25 = 0; k25 < pclusters[c25].indices.size(); ++k25)
                g_pointWinnerTags25[pclusters[c25].indices[k25]] = winner25;
        }
    }
}

// TICKET 277: no symmetry axis is a hard failure, not a fallback. Keeping size order
// silently swaps the labels -- Surface_0 becomes whichever cluster is larger, so Bl0/Bl1
// stop matching the authors' lanes and the run reads downstream as a method failure.
static const int MESH_NO_AXIS_EXIT = 42;
[[noreturn]] static void dieNoAxis(const std::string& why)
{
    std::cerr << "[PAPER-234] FATAL: " << why << std::endl
              << "[PAPER-234] FATAL: refusing to keep size order -- Surface_0/Surface_1 would be mislabelled" << std::endl
              << "[PAPER-234] FATAL: and Bl0/Bl1 would stop matching the authors' lanes. Set SFS_AXIS_FILE" << std::endl
              << "[PAPER-234] FATAL: to the piece's axis file (Dataset/Axes/<Piece>_Axis.xyz) and re-run." << std::endl
              << "[PAPER-234] FATAL: exiting " << MESH_NO_AXIS_EXIT << std::endl;
    std::exit(MESH_NO_AXIS_EXIT);
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
    if (!axPath || !*axPath) dieNoAxis("SFS_AXIS_FILE is unset or empty");
    std::ifstream axf(axPath);
    if (!axf.is_open()) dieNoAxis(std::string("cannot open SFS_AXIS_FILE='") + axPath + "'");
    double ax, ay, az, dx, dy, dz;
    axf >> ax >> ay >> az >> dx >> dy >> dz;
    if (axf.fail()) dieNoAxis(std::string("SFS_AXIS_FILE='") + axPath + "' does not hold six numbers (axis point xyz + direction xyz)");
    Eigen::Vector3f axPt(static_cast<float>(ax), static_cast<float>(ay), static_cast<float>(az));
    Eigen::Vector3f axDir(static_cast<float>(dx), static_cast<float>(dy), static_cast<float>(dz));
    float dl = axDir.norm();
    if (dl < 1e-9f) dieNoAxis(std::string("SFS_AXIS_FILE='") + axPath + "' has a zero-length direction");
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
        if (g_dumpOn25) g_classifySwap25 = 1;
        std::cout << "[PAPER-234] classify: swapped -> Surface_0=interior" << std::endl;
    } else {
        if (g_dumpOn25) g_classifySwap25 = 0;
        std::cout << "[PAPER-234] classify: kept -> Surface_0=interior" << std::endl;
    }
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
        int minClusterEff = static_cast<int>(std::lround(minCluster * g_countScale));
        int dynMinCluster = std::max(minClusterEff, std::max(30, Npts / 500));          // ~0.2% of points, min 30
        int dynK          = std::max(noOfNeighbours, std::min(40, std::max(15, Npts / 500))); // 15..40 range

        // TICKET 23: SFS_FLOOR_CEILING=<fraction>. With the counts scaled to a finer spacing the
        // floor can outrun a small piece and no cluster survives; the ceiling bounds it by the
        // piece's own size. It applies only where the count scale is armed, and off leaves both
        // numbers untouched.
        const int dynMinClusterFrom23 = dynMinCluster;
        bool capped23 = false;
        if (g_floorCeilingOn && g_countScaleAuto)
        {
            int cap23 = static_cast<int>(std::lround(g_floorCeilingFrac * static_cast<double>(Npts)));
            if (cap23 < 1) cap23 = 1;
            if (dynMinCluster > cap23)
            {
                dynMinCluster = cap23;
                capped23 = true;
            }
            std::cout << "[FLOOR-23] piece=" << fileNameOnly << " npts=" << Npts
                      << " frac=" << g_floorCeilingFrac << " cap=" << cap23
                      << " minCluster=" << dynMinCluster << " from=" << dynMinClusterFrom23
                      << " clamped=" << (capped23 ? "yes" : "no") << std::endl;
        }
        g_status23.npts = Npts;
        g_status23.floorUsed = dynMinCluster;
        g_status23.floorFrom = dynMinClusterFrom23;
        g_status23.capped = capped23;

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
        const size_t preMergeCount23 = clusters.size();
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

        // TICKET 25 rung 2: the clusters growth handed to the merge, with the floor that was
        // actually applied to reach them. Cluster id is this array's index, -1 = never claimed.
        if (g_dumpOn25)
        {
            std::vector<int> cid25(cloud->points.size(), -1);
            std::vector<int> why25(cloud->points.size(), DR25_NONE);
            for (size_t c = 0; c < clusters.size(); ++c)
            {
                for (size_t k = 0; k < clusters[c].indices.size(); ++k)
                {
                    const int idx25 = clusters[c].indices[k];
                    if (idx25 < 0 || static_cast<size_t>(idx25) >= cid25.size()) continue;
                    cid25[idx25] = static_cast<int>(c);
                    why25[idx25] = DR25_CLAIMED;
                }
            }
            long unclaimed25 = 0;
            for (size_t i = 0; i < cid25.size(); ++i) if (cid25[i] < 0) ++unclaimed25;
            dumpRungXYZ25("r2_clusters_premerge", cloud, normals, cid25, why25);
            std::ostringstream o25;
            o25 << "\"retry\": " << currentIteration
                << ", \"npts\": " << Npts
                << ", \"clusters\": " << dumpSizesJson25(clusters)
                << ", \"min_cluster\": " << minCluster
                << ", \"min_cluster_eff\": " << minClusterEff
                << ", \"floor_applied\": " << dynMinCluster
                << ", \"floor_from\": " << dynMinClusterFrom23
                << ", \"floor_capped\": " << (capped23 ? "true" : "false")
                << ", \"count_scale\": " << dumpFmt25(g_countScale)
                << ", \"spacing_mm\": " << dumpFmt25(g_effectiveSpacingMM)
                << ", \"paper_chain\": " << (paperChain ? "true" : "false")
                << ", \"plane_rule\": " << (planeRule ? "true" : "false")
                << ", \"theta\": " << dumpFmt25(paperTheta)
                << ", \"kappa\": " << dumpFmt25(paperKappa)
                << ", \"nb\": " << paperNB
                << ", \"points_in_no_cluster\": " << unclaimed25
                << ", \"reason_counts\": " << dumpReasonCounts25(why25);
            dumpWriteJson25("r2_clusters_premerge", o25.str());
        }

        // TICKET 25: clear what the later rungs of this retry record.
        if (g_dumpOn25)
        {
            g_r4Code25.assign(cloud->points.size(), -1);
            for (int s25 = 0; s25 < 2; ++s25)
            {
                g_r4Window25[s25] = Window26Window();
                g_r4Own25[s25] = 0; g_r4Other25[s25] = 0; g_r4Cand25[s25] = 0;
                g_r4Final25[s25] = 0; g_r4OtherCopied25[s25] = 0;
            }
            g_r4Passes25 = 0;
            g_classifySwap25 = -1;
        }

        // 병합 함수 호출
        if (paperChain) {
            std::cout << "Calling mergePaper234 function." << std::endl;
            int k1Eff = static_cast<int>(std::lround(10 * g_countScale));
            int k2Eff = static_cast<int>(std::lround(30 * g_countScale));
            std::cout << "[COUNT-22] merge k1=" << k1Eff << " k2=" << k2Eff << " minCluster=" << minClusterEff << std::endl;
            mergePaper234(cloud, normals, clusters, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC, k1Eff, k2Eff);
            std::sort(clusters.begin(), clusters.end(), myobject3);
            classifyAndOrderPaper234(cloud, normals, clusters);
        } else {
        std::cout << "Calling mergeClusters function." << std::endl;
        mergeClusters(cloudWithNormals, clusters);
        }

        // TICKET 25 rung 3: what the merge and the interior classification left. Without the
        // paper chain there is no merge record to read, and the sidecar says so rather than
        // reporting every point as newly merged.
        if (g_dumpOn25)
        {
            std::vector<int> cid25(cloud->points.size(), -1);
            std::vector<int> why25(cloud->points.size(), DR25_NONE);
            const bool tracked25 = (!g_pointOrigTags25.empty() && g_pointOrigTags25.size() == cid25.size());
            for (size_t c = 0; c < clusters.size(); ++c)
            {
                for (size_t k = 0; k < clusters[c].indices.size(); ++k)
                {
                    const int idx25 = clusters[c].indices[k];
                    if (idx25 < 0 || static_cast<size_t>(idx25) >= cid25.size()) continue;
                    cid25[idx25] = static_cast<int>(c);
                    if (!tracked25) { why25[idx25] = DR25_CLAIMED; continue; }
                    const int orig25 = g_pointOrigTags25[idx25];
                    const int win25 = (static_cast<size_t>(idx25) < g_pointWinnerTags25.size()) ? g_pointWinnerTags25[idx25] : -1;
                    why25[idx25] = (orig25 == win25) ? DR25_CLAIMED : DR25_MERGED;
                }
            }
            long unclaimed25 = 0;
            for (size_t i = 0; i < cid25.size(); ++i) if (cid25[i] < 0) ++unclaimed25;
            dumpRungXYZ25("r3_after_merge", cloud, normals, cid25, why25);
            std::ostringstream tagJo25;
            tagJo25 << "[";
            for (size_t c = 0; c < clusters.size(); ++c)
            {
                std::vector<int> ids25;
                if (tracked25)
                {
                    for (size_t k = 0; k < clusters[c].indices.size(); ++k)
                    {
                        const int idx25 = clusters[c].indices[k];
                        if (idx25 < 0 || static_cast<size_t>(idx25) >= g_pointOrigTags25.size()) continue;
                        ids25.push_back(g_pointOrigTags25[idx25]);
                    }
                    std::sort(ids25.begin(), ids25.end());
                    ids25.erase(std::unique(ids25.begin(), ids25.end()), ids25.end());
                }
                if (c) tagJo25 << ", ";
                tagJo25 << dumpIntList25(ids25);
            }
            tagJo25 << "]";
            std::ostringstream o25;
            o25 << "\"retry\": " << currentIteration
                << ", \"clusters\": " << dumpSizesJson25(clusters)
                << ", \"cluster_pre_merge_tags\": " << tagJo25.str()
                << ", \"merge_tracking\": " << dumpJsonStr25(tracked25 ? std::string("paper-chain") : std::string("unavailable-mergeclusters"))
                << ", \"merge_passes\": " << (tracked25 ? g_mergePasses25 : 0)
                << ", \"merge_pairs_tested\": " << (tracked25 ? g_mergeTested25 : 0)
                << ", \"merges\": " << (tracked25 ? dumpMergesJson25() : std::string("[]"))
                << ", \"classify_swap\": " << dumpJsonStr25(g_classifySwap25 < 0 ? std::string("none") : (g_classifySwap25 ? std::string("swapped") : std::string("kept")))
                << ", \"points_in_no_cluster\": " << unclaimed25
                << ", \"reason_counts\": " << dumpReasonCounts25(why25);
            dumpWriteJson25("r3_after_merge", o25.str());
        }

        // TICKET 23: one line per retry with the numbers the retry ended on, so a piece that
        // keeps or loses a cluster says so whether or not a switch is armed.
        {
            std::ostringstream sz;
            for (size_t i = 0; i < clusters.size(); ++i) { if (i) sz << ","; sz << clusters[i].indices.size(); }
            std::cout << "[RETRY-23] piece=" << fileNameOnly << " retry=" << currentIteration
                      << " npts=" << Npts << " clusters_pre=" << preMergeCount23
                      << " clusters=" << clusters.size()
                      << " sizes=" << (clusters.empty() ? std::string("none") : sz.str())
                      << " minCluster=" << dynMinCluster << " minClusterFrom=" << dynMinClusterFrom23
                      << std::endl;
            g_status23.retries = currentIteration;
            g_status23.finalClusters = static_cast<int>(clusters.size());
            g_status23.finalSizes = clusters.empty() ? std::string("none") : sz.str();
            g_status23.floorUsed = dynMinCluster;
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
            pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePoints_Cluster2(new pcl::PointCloud<pcl::PointNormal>);
            std::string reassignMode = "radius";
            if (const char* e = std::getenv("SFS_REASSIGN_MODE")) { if (*e) reassignMode = e; }
            std::cout << "[REASSIGN-22] mode=" << reassignMode << std::endl;
            // TICKET 26: W2's "any other surviving cluster" is every cluster that is not the one
            // being fitted, so it is built once here and handed to the fit.
            pcl::PointCloud<pcl::PointNormal>::Ptr otherForCluster1(new pcl::PointCloud<pcl::PointNormal>);
            pcl::PointCloud<pcl::PointNormal>::Ptr otherForCluster2(new pcl::PointCloud<pcl::PointNormal>);
            for (size_t c26 = 0; c26 < clusters.size(); c26++)
            {
                for (size_t i26 = 0; i26 < clusters[c26].indices.size(); i26++)
                {
                    if (c26 != 0) otherForCluster1->points.push_back(cloudWithNormals->points[clusters[c26].indices[i26]]);
                    if (c26 != 1) otherForCluster2->points.push_back(cloudWithNormals->points[clusters[c26].indices[i26]]);
                }
            }
            otherForCluster1->width = static_cast<int>(otherForCluster1->points.size());
            otherForCluster1->height = 1;
            otherForCluster2->width = static_cast<int>(otherForCluster2->points.size());
            otherForCluster2->height = 1;

            if (reassignMode == "own")
            {
                improveSurfaceBoundaryByFittingBSplineSurfaceOwn(sampledPointCloudNormal, cloudWithNormals_Cluster1, cloudWithNormals_Cluster2, improvedSurfacePoints_Cluster1, improvedSurfacePoints_Cluster2, otherForCluster1, otherForCluster2);
            }
            else
            {
                improveSurfaceBoundaryByFittingBSplineSurface(sampledPointCloudNormal, cloudWithNormals_Cluster1, improvedSurfacePoints_Cluster1, 0, otherForCluster1);
                improveSurfaceBoundaryByFittingBSplineSurface(sampledPointCloudNormal, cloudWithNormals_Cluster2, improvedSurfacePoints_Cluster2, 1, otherForCluster2);
            }
            // TICKET 25 rung 4: the window each fit used and what became of every point.
            if (g_dumpOn25)
            {
                std::vector<int> cid25(cloud->points.size(), -1);
                for (size_t c = 0; c < clusters.size(); ++c)
                {
                    for (size_t k = 0; k < clusters[c].indices.size(); ++k)
                    {
                        const int idx25 = clusters[c].indices[k];
                        if (idx25 < 0 || static_cast<size_t>(idx25) >= cid25.size()) continue;
                        cid25[idx25] = static_cast<int>(c);
                    }
                }
                std::vector<int> why25(cloud->points.size(), DR25_NONE);
                for (size_t i = 0; i < why25.size() && i < g_r4Code25.size(); ++i)
                    if (g_r4Code25[i] >= 0) why25[i] = g_r4Code25[i];
                dumpRungXYZ25("r4_after_reassign", cloud, normals, cid25, why25);
                std::ostringstream o25;
                o25 << "\"retry\": " << currentIteration
                    << ", \"fitted\": true"
                    << ", \"reassign_mode\": " << dumpJsonStr25(reassignMode)
                    << ", \"normals_flipped\": " << (flipNormals ? "true" : "false")
                    << ", \"passes\": " << g_r4Passes25
                    << ", \"windows\": [";
                for (int s25 = 0; s25 < g_r4Passes25 && s25 < 2; ++s25) { if (s25) o25 << ", "; o25 << dumpWindow25(s25, g_r4Window25[s25]); }
                o25 << "]"
                    << ", \"admitted_own\": [" << g_r4Own25[0] << ", " << g_r4Own25[1] << "]"
                    << ", \"admitted_other\": [" << g_r4Other25[0] << ", " << g_r4Other25[1] << "]"
                    << ", \"candidates\": [" << g_r4Cand25[0] << ", " << g_r4Cand25[1] << "]"
                    << ", \"final_points\": [" << g_r4Final25[0] << ", " << g_r4Final25[1] << "]"
                    << ", \"other_copied_over\": [" << g_r4OtherCopied25[0] << ", " << g_r4OtherCopied25[1] << "]"
                    << ", \"clusters\": " << dumpSizesJson25(clusters)
                    << ", \"reason_counts\": " << dumpReasonCounts25(why25);
                dumpWriteJson25("r4_after_reassign", o25.str());
            }

            // Both improved surfaces are written back only after every call has run.
            cloudWithNormals_Cluster1->points.clear();
            pcl::copyPointCloud(*improvedSurfacePoints_Cluster1, *cloudWithNormals_Cluster1);
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

            // TICKET 25 rung 5: the two clouds that were just written, asked directly which of
            // this step's points they carry, rather than inferring it from the labels.
            if (g_dumpOn25)
            {
                std::vector<pcl::PointCloud<pcl::PointNormal>::Ptr> surfaces25;
                surfaces25.push_back(cloudWithNormals_Cluster1);
                surfaces25.push_back(cloudWithNormals_Cluster2);
                std::ostringstream fields25;
                fields25 << "\"fitted\": true, \"reassign_mode\": " << dumpJsonStr25(reassignMode)
                         << ", \"normals_flipped\": " << (flipNormals ? "true" : "false");
                dumpRung5_25(cloud, normals, surfaces25, "pair", currentIteration, clusters, fields25.str());
            }

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

            // TICKET 23: SFS_SINGLE_CLUSTER=write. One surviving cluster is a surface; run the
            // same boundary improvement the two-cluster path runs on a cluster and write it as
            // Surface_0. No interior/exterior flip: with one surface there is no decision to make,
            // and checkNormalsIntersection has no second cluster to test against.
            if (g_singleClusterMode == "write")
            {
                pcl::PointCloud<pcl::PointNormal>::Ptr improvedSurfacePoints_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
                improveSurfaceBoundaryByFittingBSplineSurface(sampledPointCloudNormal, cloudWithNormals_Cluster1, improvedSurfacePoints_Cluster1);
                cloudWithNormals_Cluster1->points.clear();
                pcl::copyPointCloud(*improvedSurfacePoints_Cluster1, *cloudWithNormals_Cluster1);
                cloudWithNormals_Cluster1->width = static_cast<int>(cloudWithNormals_Cluster1->points.size());
                cloudWithNormals_Cluster1->height = 1;
                pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_0.ply", *cloudWithNormals_Cluster1, false); // ASCII mode
                g_status23.singleSurfacePoints = static_cast<int>(cloudWithNormals_Cluster1->points.size());
                std::cout << "[SINGLE-23] piece=" << fileNameOnly << " mode=write cluster=1 clusterPoints="
                          << clusters[0].indices.size() << " surfacePoints=" << cloudWithNormals_Cluster1->points.size()
                          << " wrote=tmpSurfaceCluster_Improved_0.ply surface0=single no_flip=yes" << std::endl;
            }
            else
            {
                std::cout << "[SINGLE-23] piece=" << fileNameOnly << " mode=" << g_singleClusterMode
                          << " cluster=1 clusterPoints=" << clusters[0].indices.size()
                          << " wrote=none surface0=none" << std::endl;
            }

            // TICKET 25 rungs 4 and 5 for one surviving cluster. The fit runs only in write mode,
            // and both sidecars state which case this was instead of implying a reassignment.
            if (g_dumpOn25)
            {
                const bool fitted25 = (g_singleClusterMode == "write");
                std::vector<int> cid25(cloud->points.size(), -1);
                for (size_t k = 0; k < clusters[0].indices.size(); ++k)
                {
                    const int idx25 = clusters[0].indices[k];
                    if (idx25 < 0 || static_cast<size_t>(idx25) >= cid25.size()) continue;
                    cid25[idx25] = 0;
                }
                std::vector<int> why25(cloud->points.size(), DR25_NONE);
                for (size_t i = 0; i < why25.size(); ++i)
                {
                    if (cid25[i] < 0) continue;
                    if (fitted25 && i < g_r4Code25.size() && g_r4Code25[i] >= 0) why25[i] = g_r4Code25[i];
                    else why25[i] = DR25_CLAIMED;
                }
                dumpRungXYZ25("r4_after_reassign", cloud, normals, cid25, why25);
                std::ostringstream o25;
                o25 << "\"retry\": " << currentIteration
                    << ", \"fitted\": " << (fitted25 ? "true" : "false")
                    << ", \"reassign_mode\": \"single\""
                    << ", \"normals_flipped\": false"
                    << ", \"passes\": " << g_r4Passes25
                    << ", \"windows\": [";
                for (int s25 = 0; s25 < g_r4Passes25 && s25 < 2; ++s25) { if (s25) o25 << ", "; o25 << dumpWindow25(s25, g_r4Window25[s25]); }
                o25 << "]"
                    << ", \"admitted_own\": [" << g_r4Own25[0] << "]"
                    << ", \"admitted_other\": [" << g_r4Other25[0] << "]"
                    << ", \"candidates\": [" << g_r4Cand25[0] << "]"
                    << ", \"final_points\": [" << g_r4Final25[0] << "]"
                    << ", \"clusters\": " << dumpSizesJson25(clusters)
                    << ", \"reason_counts\": " << dumpReasonCounts25(why25);
                dumpWriteJson25("r4_after_reassign", o25.str());

                std::vector<pcl::PointCloud<pcl::PointNormal>::Ptr> surfaces25;
                if (fitted25) surfaces25.push_back(cloudWithNormals_Cluster1);
                std::ostringstream fields25;
                fields25 << "\"fitted\": " << (fitted25 ? "true" : "false") << ", \"reassign_mode\": \"single\"";
                dumpRung5_25(cloud, normals, surfaces25, fitted25 ? "single" : "single-off", currentIteration, clusters, fields25.str());
            }

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

        // TICKET 25: with fewer than two clusters this retry fits nothing and writes nothing,
        // so rungs 4 and 5 record that decision rather than leaving the rungs missing.
        if (g_dumpOn25 && clusters.size() < 2)
        {
            std::vector<int> cid25(cloud->points.size(), -1);
            std::vector<int> why25(cloud->points.size(), DR25_NONE);
            dumpRungXYZ25("r4_after_reassign", cloud, normals, cid25, why25);
            std::ostringstream o25;
            o25 << "\"retry\": " << currentIteration
                << ", \"fitted\": false, \"reassign_mode\": \"none\", \"normals_flipped\": false"
                << ", \"passes\": 0, \"windows\": []"
                << ", \"clusters\": " << dumpSizesJson25(clusters)
                << ", \"reason_counts\": " << dumpReasonCounts25(why25);
            dumpWriteJson25("r4_after_reassign", o25.str());
            std::vector<pcl::PointCloud<pcl::PointNormal>::Ptr> surfaces25;
            std::ostringstream fields25;
            fields25 << "\"fitted\": false, \"reassign_mode\": \"none\"";
            dumpRung5_25(cloud, normals, surfaces25, "none", currentIteration, clusters, fields25.str());
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
        // TICKET 25: the only place the dump switch is read, and the only place a dump
        // directory is ever created. Unset SFS_DUMP_STAGE means nothing below runs.
        dumpBeginPiece25(baseName);
        // POTA-244: default restores pre-48fb588 fixed 0.6mm radius (no target loop).
        // SFS_DOWNSAMPLE_TARGET=N overrides: 19000 = 48fb588 adaptive, <0 = skip (raw cloud).
        int dsTarget244 = 0;
        if (const char* e = std::getenv("SFS_DOWNSAMPLE_TARGET")) { if (*e) dsTarget244 = std::stoi(e); }
        float samplingRadius244 = 0.6F;
        std::string spacingPolicy = "fixed";
        if (const char* e = std::getenv("SFS_SPACING_POLICY")) { if (*e) spacingPolicy = e; }
        if (spacingPolicy == "piece")
        {
            int spacingSamples = 200;
            if (const char* e = std::getenv("SFS_SPACING_SAMPLES")) { if (*e) spacingSamples = std::stoi(e); }
            double diagMM = 0.0, s0MM = 0.0;
            measurePieceSpacing(inputFilePath, diagMM, s0MM);
            double sRaw = diagMM / static_cast<double>(spacingSamples);
            double sClamped = std::min(0.6, std::max(s0MM, sRaw));
            samplingRadius244 = static_cast<float>(sClamped);
            g_effectiveSpacingMM = sClamped;
            g_pieceDiagMM = diagMM;   // TICKET 24: the radius arm reads these instead of re-probing
            g_pieceS0MM = s0MM;
            std::cout << "[SPACING-22] policy=piece diagMM=" << diagMM << " s0MM=" << s0MM
                      << " samples=" << spacingSamples << " rawMM=" << sRaw
                      << " S=" << sClamped << std::endl;
        }
        else
        {
            g_effectiveSpacingMM = 0.6;
            // TICKET 24: policy=fixed measures nothing, so a radius arm probes for itself below
            // and must not inherit the previous piece's numbers.
            g_pieceS0MM = 0.0;
            g_pieceDiagMM = 0.0;
            std::cout << "[SPACING-22] policy=fixed S=" << g_effectiveSpacingMM << std::endl;
        }
        std::string countScale = "off";
        if (const char* e = std::getenv("SFS_COUNT_SCALE")) { if (*e) countScale = e; }
        g_countScale = (countScale == "auto") ? (0.6 / g_effectiveSpacingMM) * (0.6 / g_effectiveSpacingMM) : 1.0;
        g_countScaleAuto = (countScale == "auto");
        std::cout << "[COUNT-22] policy=" << countScale << " scale=" << g_countScale
                  << " minCluster=" << static_cast<int>(std::lround(50 * g_countScale))
                  << " k1=" << static_cast<int>(std::lround(10 * g_countScale))
                  << " k2=" << static_cast<int>(std::lround(30 * g_countScale)) << std::endl;

        // TICKET 23: the two switches. Both default to today's behaviour.
        if (const char* e23 = std::getenv("SFS_SINGLE_CLUSTER")) { if (*e23) g_singleClusterMode = e23; }
        g_floorCeilingOn = false;
        g_floorCeilingFrac = 0.0;
        if (const char* e23 = std::getenv("SFS_FLOOR_CEILING"))
        {
            if (*e23 && std::string(e23) != "off") { g_floorCeilingFrac = std::stod(e23); g_floorCeilingOn = true; }
        }
        std::cout << "[SWITCH-23] singleCluster=" << g_singleClusterMode
                  << " floorCeiling=" << (g_floorCeilingOn ? std::to_string(g_floorCeilingFrac) : std::string("off"))
                  << " countScaleAuto=" << (g_countScaleAuto ? "yes" : "no") << std::endl;

        // TICKET 26: how wide the admission window is. Every default here reproduces the
        // 3 mm literal, so a run without these switches is the run before this ticket.
        g_windowMode = "literal";
        g_windowK = 5.0;
        g_windowClampLoMM = 0.5;
        g_windowClampHiMM = 6.0;
        g_windowReport.clear();
        // TICKET 27: SFS_DEDUPE=on exports each distinct position of a written surface once.
        // Unset, empty, "off" and anything else keep today's apples-to-apples surface.
        g_dedupeOn27 = false;
        if (const char* e27 = std::getenv("SFS_DEDUPE")) { if (*e27 && std::string(e27) == "on") g_dedupeOn27 = true; }
        if (const char* e26 = std::getenv("SFS_WINDOW_MODE")) { if (*e26) g_windowMode = e26; }
        if (const char* e26 = std::getenv("SFS_WINDOW_K")) { if (*e26) g_windowK = std::stod(e26); }
        if (const char* e26 = std::getenv("SFS_WINDOW_CLAMP_MM"))
        {
            if (*e26)
            {
                const std::string clamp26 = e26;
                const size_t comma26 = clamp26.find(',');
                if (comma26 != std::string::npos)
                {
                    g_windowClampLoMM = std::stod(clamp26.substr(0, comma26));
                    g_windowClampHiMM = std::stod(clamp26.substr(comma26 + 1));
                }
                else
                {
                    std::cout << "[WINDOW-26-SWITCH] warn=clamp_unparsed value=" << clamp26
                              << " kept=" << g_windowClampLoMM << "," << g_windowClampHiMM << std::endl;
                }
            }
        }
        if (const char* e26 = std::getenv("SFS_WINDOW_REPORT")) { if (*e26) g_windowReport = e26; }
        std::cout << "[WINDOW-26-SWITCH] mode=" << g_windowMode << " k=" << g_windowK
                  << " clampMM=" << g_windowClampLoMM << "," << g_windowClampHiMM
                  << " report=" << (g_windowReport.empty() ? "none" : g_windowReport) << std::endl;

        // TICKET 24: how many neighbours a normal is estimated from. Every default here
        // reproduces today: mode=count ignores the radius and runs the untouched count rule.
        g_normalCall = 0;
        g_normalMode = "count";
        g_normalRadiusMM = 0.0;
        g_normalRadiusMMRaw = "0";
        g_normalRadiusAuto = false;
        g_normalRadiusMult = 2.0;
        g_normalMinK = 5;
        g_normalMaxK = 20;
        g_nbrsFile.clear();
        if (const char* e24 = std::getenv("SFS_NORMAL_MODE")) { if (*e24) g_normalMode = e24; }
        if (const char* e24 = std::getenv("SFS_NORMAL_RADIUS_MM")) { if (*e24) g_normalRadiusMMRaw = e24; }
        if (const char* e24 = std::getenv("SFS_NORMAL_RADIUS_MULT")) { if (*e24) g_normalRadiusMult = std::stod(e24); }
        if (const char* e24 = std::getenv("SFS_NORMAL_MIN_K")) { if (*e24) g_normalMinK = std::stoi(e24); }
        if (const char* e24 = std::getenv("SFS_NORMAL_MAX_K")) { if (*e24) g_normalMaxK = std::stoi(e24); }
        if (const char* e24 = std::getenv("SFS_NBRS_FILE")) { if (*e24) g_nbrsFile = e24; }
        g_normalDumpDir.clear();
        if (const char* e24 = std::getenv("SFS_NORMAL_DUMP_DIR")) { if (*e24) g_normalDumpDir = e24; }
        if (g_normalMode == "radius" && (g_pieceS0MM <= 0.0 || g_pieceDiagMM <= 0.0))
        {
            double d24 = 0.0, s24 = 0.0;
            measurePieceSpacing(inputFilePath, d24, s24);
            g_pieceDiagMM = d24;
            if (g_pieceS0MM <= 0.0) g_pieceS0MM = s24;
            std::cout << "[NORMAL-24] probe diagMM=" << d24 << " s0MM=" << s24 << std::endl;
        }
        if (g_normalRadiusMMRaw == "auto")
        {
            // resolved per call from the spacing of the cloud that call is handed; see
            // estimateNormalsRadius. 0 here means "not yet resolved".
            g_normalRadiusAuto = true;
            g_normalRadiusMM = 0.0;
        }
        else
        {
            g_normalRadiusMM = std::stod(g_normalRadiusMMRaw);
        }
        std::cout << "[NORMAL-24-SWITCH] mode=" << g_normalMode
                  << " radiusMMraw=" << g_normalRadiusMMRaw
                  << " radiusMM=" << (g_normalRadiusAuto ? std::string("autoPending") : std::to_string(g_normalRadiusMM))
                  << " radiusFrom=" << (g_normalRadiusAuto ? "auto" : "fixed")
                  << " mult=" << g_normalRadiusMult
                  << " s0MM=" << g_pieceS0MM
                  << " diagMM=" << g_pieceDiagMM
                  << " radiusOverDiag=" << ((g_normalMode == "radius" && !g_normalRadiusAuto && g_pieceDiagMM > 0.0 && g_normalRadiusMM > g_pieceDiagMM) ? "yes" : "no")
                  << " minK=" << g_normalMinK << " maxK=" << g_normalMaxK
                  << " nbrsFile=" << (g_nbrsFile.empty() ? "none" : g_nbrsFile)
                  << " dumpDir=" << (g_normalDumpDir.empty() ? "none" : g_normalDumpDir) << std::endl;
        // TICKET 23: a previous piece's temp surface must not be read back as this piece's on a
        // multi-piece run. Only armed under the switch, so the off path is untouched.
        if (g_singleClusterMode == "write")
        {
            std::error_code ec23;
            fs::remove(intermediatePath + "tmpSurfaceCluster_Improved_0.ply", ec23);
            fs::remove(intermediatePath + "tmpSurfaceCluster_Improved_1.ply", ec23);
        }
        g_status23 = PieceStatus23();
        g_status23.piece = fileNameOnly;
        std::string downsampledFilePath = downsamplePointCloud(inputFilePath, samplingRadius244, dsTarget244);

        // TICKET 25 rung 1: the cloud every later step loads, with the density policy that made it.
        if (g_dumpOn25)
        {
            std::ostringstream o25;
            o25 << "\"spacing_policy\": " << dumpJsonStr25(spacingPolicy)
                << ", \"S_mm\": " << dumpFmt25(g_effectiveSpacingMM)
                << ", \"diag_mm\": " << dumpFmt25(g_pieceDiagMM)
                << ", \"s0_mm\": " << dumpFmt25(g_pieceS0MM)
                << ", \"sampling_radius_mm\": " << dumpFmt25(static_cast<double>(samplingRadius244))
                << ", \"downsample_target\": " << dsTarget244
                << ", \"points_in\": " << dumpPcdPoints25(inputFilePath);
            dumpRung1_25(downsampledFilePath, o25.str());
        }
        
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

        // TICKET 23: announce the piece. Two surfaces, one, or none -- and a "none" carries the
        // numbers that produced it, so an absence is an announced absence rather than silence.
        {
            const bool got0_23 = fs::exists(tempFileName0);
            const bool got1_23 = fs::exists(tempFileName1);
            const int p0_23 = got0_23 ? plyVertexCount23(tempFileName0) : -1;
            const int p1_23 = got1_23 ? plyVertexCount23(tempFileName1) : -1;
            const std::string outcome23 = (got0_23 && got1_23) ? "two" : (got0_23 ? "one" : "none");
            std::ostringstream reason23;
            if (outcome23 == "two")
            {
                reason23 << "two surfaces written";
            }
            else if (outcome23 == "one")
            {
                reason23 << (g_singleClusterMode == "write"
                             ? "one cluster written as Surface_0 (SFS_SINGLE_CLUSTER=write)"
                             : "one temp surface present");
            }
            else
            {
                reason23 << "no temp surface; final clusters=" << g_status23.finalClusters
                         << " sizes=" << g_status23.finalSizes
                         << " floor=" << g_status23.floorUsed << " from=" << g_status23.floorFrom
                         << " singleCluster=" << g_singleClusterMode;
            }
            std::cout << "[STATUS-23] piece=" << fileNameOnly << " outcome=" << outcome23
                      << " retries=" << g_status23.retries << " clusters=" << g_status23.finalClusters
                      << " sizes=" << g_status23.finalSizes << " npts=" << g_status23.npts
                      << " floor=" << g_status23.floorUsed << " floor_from=" << g_status23.floorFrom
                      << " capped=" << (g_status23.capped ? "yes" : "no")
                      << " surf0_points=" << p0_23 << " surf1_points=" << p1_23
                      << " reason=" << reason23.str() << std::endl;
            if (const char* sf23 = std::getenv("SFS_STATUS_FILE"))
            {
                if (*sf23)
                {
                    std::ofstream st23(sf23, std::ofstream::out | std::ofstream::app);
                    if (st23.is_open())
                    {
                        st23 << fileNameOnly << "\t" << g_status23.npts << "\t" << g_status23.retries
                             << "\t" << g_status23.finalClusters << "\t" << g_status23.finalSizes
                             << "\t" << g_status23.floorUsed << "\t" << g_status23.floorFrom
                             << "\t" << (g_status23.capped ? "yes" : "no")
                             << "\t" << outcome23 << "\t" << p0_23 << "\t" << p1_23
                             << "\t" << g_singleClusterMode << "\t" << g_floorCeilingOn
                             << "\t" << reason23.str() << std::endl;
                        st23.close();
                    }
                }
            }
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
