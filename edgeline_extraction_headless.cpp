/*	Mainly this code approximates the parameters for a bicubic patch on a surface
	and sorts, samples and smoothes the breaklines.
	Additionally it also calculates the following features:
	Gaussian and mean curvature on surface and breakline and
	the thickness along a breakline.
*/

// Headless version - removed Windows graphics libraries 


#define PCL_NO_PRECOMPILE 1
#include <iostream>
#include <Eigen/Dense>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#define _SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING
#include <experimental/filesystem>
#include <filesystem>
#include <stdio.h>
#include <pcl/filters/uniform_sampling.h>

#include <chrono>

#include <thread>

#include <pcl/common/transforms.h>

#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
// Removed VTK headers for headless build (PCL built with -DWITH_VTK=OFF)
// #include <pcl/io/vtk_io.h>
// #include <pcl/io/vtk_lib_io.h>
#include <pcl/io/ply_io.h>
#include <pcl/features/normal_3d.h>
#include <pcl/surface/convex_hull.h>
#include <pcl/surface/concave_hull.h>
#include <pcl/common/common.h>
#include <pcl/sample_consensus/sac_model_plane.h>
#include <pcl/filters/project_inliers.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/console/time.h>

// Removed cloud viewer header for headless operation
#include <pcl/segmentation/region_growing.h>
#include <pcl/segmentation/conditional_euclidean_clustering.h>


#include <pcl/filters/voxel_grid.h>

#include <pcl/features/boundary.h>

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

// Removed PCL visualizer header for headless operation

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Alpha_shape_2.h>
#include <CGAL/Alpha_shape_vertex_base_2.h>
#include <CGAL/Alpha_shape_face_base_2.h>
#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/algorithm.h>
#include <CGAL/assertions.h>
#include <list>
#include "alglib/src/dataanalysis.h"

#include <pcl/ModelCoefficients.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/kdtree/kdtree.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>

#include <CGAL/pca_estimate_normals.h>
#include <CGAL/mst_orient_normals.h>
#include <CGAL/property_map.h>
#include <CGAL/IO/read_xyz_points.h>
#include <CGAL/IO/write_xyz_points.h>
#include <utility> // defines std::pair

#include <pcl/PCLPointCloud2.h>
#include <pcl/console/print.h>
#include <pcl/console/parse.h>

#include <algorithm>
#include <cmath>

#define EPS 2.2204e-16


#define TINYOBJLOADER_IMPLEMENTATION
#include <tiny_obj_loader.h>
#include <pcl/tracking/normal_coherence.h>

using namespace pcl;
using namespace pcl::io;
using namespace std;

//using namespace bh_tsne;

using namespace pcl;
using namespace pcl::io;
using namespace pcl::console;

#include <pcl/point_cloud.h>

#include <pcl/surface/on_nurbs/fitting_surface_tdm.h>
#include <pcl/surface/on_nurbs/fitting_curve_2d_asdm.h>
#include <pcl/surface/on_nurbs/triangulation.h>
#include <pcl/surface/simplification_remove_unused_vertices.h>

#include <pcl/surface/marching_cubes.h>

#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/compute_normal.h>
#include <CGAL/IO/Complex_2_in_triangulation_3_file_writer.h>
#include <CGAL/Advancing_front_surface_reconstruction.h>
#include <pcl/filters/random_sample.h>


#include <CGAL/Polyhedron_3.h>
#include <CGAL/mesh_segmentation.h>
#include <CGAL/Polygon_mesh_processing/smooth_mesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>
#include <pcl/surface/gp3.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel CGAL_Kernal;
typedef CGAL_Kernal::Point_3 PointCGAL;
typedef CGAL_Kernal::Vector_3 VectorCGAL;

typedef CGAL::Polyhedron_3<CGAL_Kernal> Polyhedron;
typedef boost::graph_traits<Polyhedron>::face_descriptor face_descriptor_poly;


typedef CGAL::Surface_mesh<PointCGAL> Surface_mesh;
typedef boost::graph_traits<Surface_mesh>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::face_descriptor  face_descriptor;
typedef boost::graph_traits<Surface_mesh>::edge_descriptor  edge_descriptor;
typedef std::array<std::size_t, 3> Facet;


typedef pcl::PointXYZ Point;
// Removed ColorHandlerXYZ typedef for headless operation
typedef search::KdTree<PointXYZ>::Ptr KdTreePtr;


// Typess
// Point with normal vector stored in a std::pair.
typedef std::pair<PointCGAL, VectorCGAL> PointVectorPair;
// Concurrency
#ifdef CGAL_LINKED_WITH_TBB
typedef CGAL::Parallel_tag Concurrency_tag;
#else
typedef CGAL::Sequential_tag Concurrency_tag;
#endif

// ---- Robust loaders to prevent crashes on malformed files ----
static bool is_valid_normals(const pcl::PointCloud<pcl::PointNormal>::Ptr& cloud) {
    if (!cloud || cloud->empty()) return false;
    size_t good = 0;
    for (const auto& p : cloud->points) {
        if (std::isfinite(p.normal_x) && std::isfinite(p.normal_y) && std::isfinite(p.normal_z)) {
            if (p.normal_x != 0.0f || p.normal_y != 0.0f || p.normal_z != 0.0f) {
                good++;
                if (good > 32) return true; // enough evidence
            }
        }
    }
    return false;
}

static void estimate_normals_from_xyz(const pcl::PointCloud<pcl::PointXYZ>::Ptr& in,
                                      pcl::PointCloud<pcl::PointNormal>::Ptr& out,
                                      int k = 20) {
    out.reset(new pcl::PointCloud<pcl::PointNormal>());
    out->points.resize(in->size());
    pcl::NormalEstimationOMP<pcl::PointXYZ, pcl::Normal> ne;
    ne.setInputCloud(in);
    pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>());
    ne.setSearchMethod(tree);
    ne.setKSearch(k);
    pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>());
    ne.compute(*normals);
    for (size_t i = 0; i < in->points.size(); ++i) {
        pcl::PointNormal pn;
        pn.x = in->points[i].x; pn.y = in->points[i].y; pn.z = in->points[i].z;
        if (i < normals->size()) {
            pn.normal_x = normals->points[i].normal_x;
            pn.normal_y = normals->points[i].normal_y;
            pn.normal_z = normals->points[i].normal_z;
        } else { pn.normal_x = 0; pn.normal_y = 0; pn.normal_z = 1; }
        out->points[i] = pn;
    }
    out->width = static_cast<uint32_t>(out->points.size());
    out->height = 1;
}

static bool load_ply_pointnormals_robust(const std::string& path,
                                         pcl::PointCloud<pcl::PointNormal>::Ptr& cloud) {
    cloud.reset(new pcl::PointCloud<pcl::PointNormal>());
    std::cerr << "[EDGELINE DEBUG] Load PLY normals: " << path << std::endl;
    if (pcl::io::loadPLYFile<pcl::PointNormal>(path, *cloud) == 0 && is_valid_normals(cloud)) {
        std::cerr << "[EDGELINE DEBUG] Loaded PointNormal PLY ok, size=" << cloud->size() << std::endl;
        return true;
    }
    // Fallback: load as XYZ and estimate normals
    pcl::PointCloud<pcl::PointXYZ>::Ptr xyz(new pcl::PointCloud<pcl::PointXYZ>());
    if (pcl::io::loadPLYFile<pcl::PointXYZ>(path, *xyz) == 0 && !xyz->empty()) {
        std::cerr << "[EDGELINE DEBUG] Loaded XYZ PLY, estimating normals. size=" << xyz->size() << std::endl;
        estimate_normals_from_xyz(xyz, cloud, 20);
        std::cerr << "[EDGELINE DEBUG] Estimated normals size=" << cloud->size() << std::endl;
        return true;
    }
    // Fallback failed
    cloud->clear();
    std::cerr << "[EDGELINE DEBUG] Failed to load PLY: " << path << std::endl;
    return false;
}

// moved below after data_path.h include where tempEdgeFolder is defined

struct Construct {
	Surface_mesh& mesh;
	template < typename PointIterator>
	Construct(Surface_mesh& mesh, PointIterator b, PointIterator e)
		: mesh(mesh)
	{
		for (; b != e; ++b) {
			boost::graph_traits<Surface_mesh>::vertex_descriptor v;
			v = add_vertex(mesh);
			mesh.point(v) = *b;
		}
	}
	Construct& operator=(const Facet f)
	{
		typedef boost::graph_traits<Surface_mesh>::vertices_size_type size_type;
		mesh.add_face(vertex_descriptor(static_cast<size_type>(f[0])),
			vertex_descriptor(static_cast<size_type>(f[1])),
			vertex_descriptor(static_cast<size_type>(f[2])));
		return *this;
	}
	Construct&
		operator*() { return *this; }
	Construct&
		operator++() { return *this; }
	Construct
		operator++(int) { return *this; }
};

struct myclass {
	bool operator() (pcl::PointXYZ i, pcl::PointXYZ j) { return (i.z < j.z); }
} myobject1;

struct myclass2 {
	bool operator() (pcl::PointNormal i, pcl::PointNormal j) { return (i.x < j.x); }
} myobject2;

struct myclass3 {
	bool operator() (pcl::PointIndices i, pcl::PointIndices j) { return (i.indices.size() > j.indices.size()); }
} myobject3;


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


pcl::console::TicToc tt;
vector<string> colorList{ "F2F3F4", "222222", "F3C300", "875692", "F38400", "A1CAF1", "BE0032", "C2B280", "848482", "008856", "E68FAC", "0067A5", "F99379", "604E97", "F6A600", "B3446C", "DCD300", "882D17", "8DB600", "654522", "E25822", "2B3D26" };

using namespace Eigen;
using namespace std;
namespace fs = std::experimental::filesystem;

typedef Matrix<double, 3, 1> Vector3d;

#include "data_path.h"

string currentFileName = "";
string currentMeshFile = "";

// 최종 결과 저장 경로
const std::string datasetBreaklinesFolder = getBreaklineDatasetPath(potID);
const std::string datasetSurfacesFolder   = getSurfaceDatasetPath(potID);

const std::string tempEdgeFolder          = tempEdgePath(potID);
const std::string datasetPath_global      = tempDataPath(potID);
const std::string axesFolder = "Dataset/Axes/";  // Changed for container compatibility

Eigen::Vector3f avgNormalDirection;
bool next_step = false;

#include <pcl/io/obj_io.h>

// Helper: load normals from cleaned surface cloud in Temp/Temp_edge if PLY is invalid
static bool load_pointnormals_from_cleaned_surface(pcl::PointCloud<pcl::PointNormal>::Ptr& cloud) {
    std::string path = tempEdgeFolder + std::string("cloud_Surface_AllSamples_Cleaned.pcd");
    pcl::PointCloud<pcl::PointNormal>::Ptr tmp(new pcl::PointCloud<pcl::PointNormal>());
    if (pcl::io::loadPCDFile<pcl::PointNormal>(path, *tmp) == 0 && !tmp->empty()) {
        cloud = tmp;
        std::cerr << "[EDGELINE DEBUG] Loaded cleaned surface normals from " << path << " size=" << cloud->size() << std::endl;
        return true;
    }
    // Try XYZ + estimate
    pcl::PointCloud<pcl::PointXYZ>::Ptr xyz(new pcl::PointCloud<pcl::PointXYZ>());
    if (pcl::io::loadPCDFile<pcl::PointXYZ>(path, *xyz) == 0 && !xyz->empty()) {
        estimate_normals_from_xyz(xyz, cloud, 20);
        std::cerr << "[EDGELINE DEBUG] Estimated normals from cleaned XYZ, size=" << cloud->size() << std::endl;
        return true;
    }
    std::cerr << "[EDGELINE DEBUG] Failed to load cleaned surface normals at " << path << std::endl;
    return false;
}
// Removed global viewers for headless operation


// Removed rgbVis function for headless operation



MatrixXd readFile(string fileName, int noOfCols = 3)
{
	stringstream ss;
	ifstream myfile(fileName);
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
    MatrixXd P(noOfCols, numberOfPoints);

	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		ss << fileContents[i];
		for (size_t j = 0; j < noOfCols; j++)
		{
			ss >> P(j, i);
		}
		ss.str(std::string());
	}

    std::cerr << "[EDGELINE DEBUG] readFile cols=" << noOfCols << " file=" << fileName << " rows=" << numberOfPoints << std::endl;
    return P.transpose();
}


MatrixXd readFile(string fileName)
{
	stringstream ss;
	ifstream myfile(fileName);
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
    MatrixXd P(3, numberOfPoints);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		ss << fileContents[i];
		ss >> P(0, i);
		ss >> P(1, i);
		ss >> P(2, i);
		ss.str(std::string());
	}

    std::cerr << "[EDGELINE DEBUG] readFile3 file=" << fileName << " rows=" << numberOfPoints << std::endl;
    return P.transpose();
}

void Change_Sequence(MatrixXd& src)
{
	int Row = src.rows();
	int Col = src.cols();
	MatrixXd Inverse(Row, Col);

	for (size_t i = 0; i < Row; i++) {
		for (size_t j = 0; j < Col; j++) {
			Inverse(i, j) = src(Row - i - 1, j);
		}
	}
	src = Inverse;
}

// Rearrange the matrix array to countclockwise 
bool Matrix_Rearrange(MatrixXd& src, MatrixXd& src_N)
{
	// In this function the matrix should be 3*numberofpoints
	double Decision(0);
	int numberOfPoints = src.rows();
	MatrixXd Dummy(3, numberOfPoints), Dummy_N(3, numberOfPoints);

	if (src.rows() != 3 && src.cols() == 3)
	{
		Dummy = src.transpose();
	}
	else Dummy = src;

	if (src_N.rows() != 3 && src_N.cols() == 3)
	{
		Dummy_N = src_N.transpose();
	}
	else Dummy_N = src_N;


	Vector3d Center(3);
	Vector3d Cross(3);
	double Dot(0);
	Vector3d tmp(3);
	Center(0, 0) = Dummy.row(0).mean();
	Center(1, 0) = Dummy.row(1).mean();
	Center(2, 0) = Dummy.row(2).mean();
	Vector3d Base_Axis = Dummy.col(0) - Center;

	for (int i = 0; i < static_cast<int>(numberOfPoints / 2); i++) {    //(int)(numberOfPoints / 2)
		tmp = Dummy.col(i) - Center;
		Cross = Base_Axis.cross(tmp);
		Dot = Cross.dot(Dummy_N.col(i));
		if (Dot > 0) {
			Decision++;
		}
		else Decision--;
	}


	cout << Decision << endl;
	if (Decision > 0) {
		cout << "CountClock Wise - Right" << endl;
		return false;
	}

	else {
		cout << "Clock Wise - Changing sequence" << endl;
		Change_Sequence(src);
		Change_Sequence(src_N);
		return true;
	}
}

// Forward declaration for adaptive densification function
MatrixXd adaptiveDensifyBreakline(const MatrixXd& breakline, double target_spacing_mm);

vector<Vector3d> FindLineSphereIntersections(Vector3d linePoint0, Vector3d linePoint1, Vector3d circleCenter, double circleRadius)
{
	vector<Vector3d> solutionSet;
	Vector3d intersectionPoint(0, 0, 0);

	double cx = circleCenter(0);
	double cy = circleCenter(1);
	double cz = circleCenter(2);

	double px = linePoint0(0);
	double py = linePoint0(1);
	double pz = linePoint0(2);

	double vx = linePoint1(0) - px;
	double vy = linePoint1(1) - py;
	double vz = linePoint1(2) - pz;

	double A = vx * vx + vy * vy + vz * vz;
	double B = 2.0 * (px * vx + py * vy + pz * vz - vx * cx - vy * cy - vz * cz);
	double C = px * px - 2 * px * cx + cx * cx + py * py - 2 * py * cy + cy * cy +
		pz * pz - 2 * pz * cz + cz * cz - circleRadius * circleRadius;

	// discriminant
	double D = B * B - 4 * A * C;

	if (D < 0)
	{
		return solutionSet;
	}

	double t1 = (-B - std::sqrt(D)) / (2.0 * A);

	Vector3d solution1(linePoint0(0) * (1 - t1) + t1 * linePoint1(0),
		linePoint0(1) * (1 - t1) + t1 * linePoint1(1),
		linePoint0(2) * (1 - t1) + t1 * linePoint1(2));
	if (D == 0)
	{
		solutionSet.push_back(solution1);
		return solutionSet;
	}

	double t2 = (-B + std::sqrt(D)) / (2.0 * A);
	Vector3d solution2(linePoint0(0) * (1 - t2) + t2 * linePoint1(0),
		linePoint0(1) * (1 - t2) + t2 * linePoint1(1),
		linePoint0(2) * (1 - t2) + t2 * linePoint1(2));

	// prefer a solution that's on the line segment itself

	if (std::abs(t1 - 0.5) < std::abs(t2 - 0.5))
	{
		solutionSet.push_back(solution1);
		solutionSet.push_back(solution2);
		return solutionSet;
	}

	solutionSet.push_back(solution2);
	solutionSet.push_back(solution1);
	return solutionSet;
}

MatrixXd smoothAndSampleBreaklinesVer4UsingBSpline(MatrixXd& P) {
	// Calculate adaptive sphere radius based on actual point spacing
	double avgSpacing = 0.0;
	int spacingCount = 0;
	for (int j = 0; j < std::min((int)P.rows() - 1, 20); j++) {
		Vector3d p1(P(j, 0), P(j, 1), P(j, 2));
		Vector3d p2(P(j + 1, 0), P(j + 1, 1), P(j + 1, 2));
		avgSpacing += (p2 - p1).norm();
		spacingCount++;
	}
	avgSpacing /= std::max(spacingCount, 1);

	// ADAPTIVE MAXIMUM RADIUS: Adjust maximum based on point sparsity
	// Sparse data needs larger sphere radius to avoid over-reduction
	int num_points = P.rows();
	double max_radius;
	if (num_points < 50) {
		max_radius = 0.015;  // 15mm for very sparse data (pottery rims)
	} else if (num_points < 100) {
		max_radius = 0.010;  // 10mm for sparse data
	} else {
		max_radius = 0.005;  // 5mm for dense data (original)
	}

	// Use 1.5× average spacing, with adaptive maximum and minimum of 0.5mm
	// NOTE: Point cloud units are in METERS, so convert mm to meters
	double sphereRadius = std::max(0.0005, std::min(max_radius, avgSpacing * 1.5));
	std::cout << "[ADAPTIVE SPHERE-MARCHING] Input points: " << P.rows() << ", avgSpacing: " << avgSpacing << "m ("
	          << (avgSpacing * 1000) << "mm), max_radius: " << (max_radius * 1000) << "mm, adaptiveRadius: "
	          << sphereRadius << "m (" << (sphereRadius * 1000) << "mm)" << std::endl;

	// COMBINATION APPROACH PART 2: Retry with smaller radius if we get too few points
	MatrixXd smoothedBreakLine;
	int attempt = 0;
	int min_required = 15;

	while (attempt < 2) {  // Try twice: original radius and 60% of original
		Vector3d sphereCenter(3);
		sphereCenter << P(0, 0), P(0, 1), P(0, 2);

		vector<MatrixXd> smoothBreakLineVector;
		Vector3d smoothedPoint(3);

		smoothedPoint << P(0, 0), P(0, 1), P(0, 2);
		smoothBreakLineVector.push_back(smoothedPoint);

		int i = 0;
		double distTmp = 0;
		while (i < P.rows() - 2) {
			Vector3d nextPointOutsideSphere(3);
			nextPointOutsideSphere << P(i + 1, 0), P(i + 1, 1), P(i + 1, 2);

			distTmp = (nextPointOutsideSphere - sphereCenter).norm();
			while (distTmp < sphereRadius && i < P.rows() - 2) {
				i++;
				nextPointOutsideSphere << P(i + 1, 0), P(i + 1, 1), P(i + 1, 2);
				distTmp = (nextPointOutsideSphere - sphereCenter).norm();
			}

			vector<Vector3d> intersectionPointSet = FindLineSphereIntersections(sphereCenter, nextPointOutsideSphere, sphereCenter, sphereRadius);

			if (!intersectionPointSet.empty()) {
				smoothedPoint = intersectionPointSet[0];
				for (const auto& pt : intersectionPointSet) {
					if ((pt - nextPointOutsideSphere).norm() < (smoothedPoint - nextPointOutsideSphere).norm()) {
						smoothedPoint = pt;
					}
				}
				smoothBreakLineVector.push_back(smoothedPoint);
				sphereCenter = smoothedPoint;
			} else {
				// Fallback: if no intersection found, add midpoint between sphere center and next point
				smoothedPoint = (sphereCenter + nextPointOutsideSphere) / 2.0;
				smoothBreakLineVector.push_back(smoothedPoint);
				sphereCenter = smoothedPoint;
			}
			i++;
		}

		smoothedBreakLine = MatrixXd(smoothBreakLineVector.size(), 3);
		std::cout << "[BREAKLINE DEBUG] Smoothed breakline output points: " << smoothedBreakLine.rows() << std::endl;
		for (int i = 0; i < smoothBreakLineVector.size(); ++i) {
			smoothedBreakLine.row(i) << smoothBreakLineVector[i](0), smoothBreakLineVector[i](1), smoothBreakLineVector[i](2);
		}

		// Check if we have enough points
		if (smoothedBreakLine.rows() >= min_required || attempt == 1) {
			break;  // Success or last attempt
		}

		// Retry with smaller radius for denser sampling
		sphereRadius *= 0.6;
		attempt++;
		std::cout << "[ADAPTIVE RETRY] Too few points (" << smoothedBreakLine.rows()
		          << "), retrying with radius=" << (sphereRadius * 1000) << "mm" << std::endl;
	}

	// COMBINATION APPROACH PART 3: Linear interpolation as final safety net
	int min_safe = 10;
	if (smoothedBreakLine.rows() < min_safe) {
		if (P.rows() >= 10) {
			// If original has enough points, use them as input to Integration Point #1
			std::cerr << "[BREAKLINE WARNING] Sphere marching produced only " << smoothedBreakLine.rows()
			          << " points from " << P.rows() << " input points. Using original boundary points (proceeding to Integration Point #1)." << std::endl;
			smoothedBreakLine = P;  // Set smoothedBreakLine to continue to Integration Point #1, not early return
		} else if (smoothedBreakLine.rows() >= 2) {
			// Linear interpolation to reach minimum of 10 points
			int points_to_add = min_safe - smoothedBreakLine.rows();
			std::cout << "[LINEAR INTERPOLATION] Densifying " << smoothedBreakLine.rows()
			          << " points to " << min_safe << " by adding " << points_to_add << " interpolated points" << std::endl;

			vector<MatrixXd> densifiedPoints;
			int points_per_segment = std::max(1, (int)(points_to_add / (smoothedBreakLine.rows() - 1)));

			for (int i = 0; i < smoothedBreakLine.rows() - 1; i++) {
				// Add original point
				Vector3d p1(smoothedBreakLine(i, 0), smoothedBreakLine(i, 1), smoothedBreakLine(i, 2));
				densifiedPoints.push_back(p1);

				// Add interpolated points between i and i+1
				Vector3d p2(smoothedBreakLine(i + 1, 0), smoothedBreakLine(i + 1, 1), smoothedBreakLine(i + 1, 2));
				int interp_count = (i == 0) ? points_per_segment + (int)(points_to_add % (smoothedBreakLine.rows() - 1))
				                             : points_per_segment;

				for (int j = 1; j <= interp_count && (int)densifiedPoints.size() < min_safe - 1; j++) {
					double t = j / (double)(interp_count + 1);
					Vector3d interp = (1.0 - t) * p1 + t * p2;
					densifiedPoints.push_back(interp);
				}
			}

			// Add last point
			Vector3d last(smoothedBreakLine(smoothedBreakLine.rows() - 1, 0),
			             smoothedBreakLine(smoothedBreakLine.rows() - 1, 1),
			             smoothedBreakLine(smoothedBreakLine.rows() - 1, 2));
			densifiedPoints.push_back(last);

			// Convert back to MatrixXd
			MatrixXd densified(densifiedPoints.size(), 3);
			for (int i = 0; i < (int)densifiedPoints.size(); i++) {
				densified.row(i) << densifiedPoints[i](0), densifiedPoints[i](1), densifiedPoints[i](2);
			}

			std::cout << "[LINEAR INTERPOLATION] Intermediate breakline: " << densified.rows() << " points (proceeding to Integration Point #1)" << std::endl;
			smoothedBreakLine = densified;  // Set smoothedBreakLine to continue to Integration Point #1, not early return
		}
	}

	// INTEGRATION POINT #1: ADAPTIVE DENSIFICATION after sphere-marching
	// Ensure breakline has sufficient density for downstream segment detection and rim classification
	std::cout << "[INTEGRATION POINT #1] Pre-densification: " << smoothedBreakLine.rows() << " points" << std::endl;
	smoothedBreakLine = adaptiveDensifyBreakline(smoothedBreakLine, 2.0);
	std::cout << "[INTEGRATION POINT #1] Post-densification: " << smoothedBreakLine.rows() << " points" << std::endl;

	return smoothedBreakLine;
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

// ADAPTIVE DENSIFICATION: Ensure breaklines have sufficient point density for downstream operations
MatrixXd adaptiveDensifyBreakline(const MatrixXd& breakline, double target_spacing_mm = 2.0) {
	int num_points = breakline.rows();

	// Safety: Need at least 2 points to densify
	if (num_points < 2) {
		std::cerr << "[DENSIFY] Too few points (" << num_points << ") to densify, returning as-is" << std::endl;
		return breakline;
	}

	// Calculate perimeter (total arc length) in meters
	double perimeter_m = 0.0;
	for (int i = 0; i < num_points - 1; i++) {
		Eigen::Vector3d p1(breakline(i,0), breakline(i,1), breakline(i,2));
		Eigen::Vector3d p2(breakline(i+1,0), breakline(i+1,1), breakline(i+1,2));
		perimeter_m += (p2 - p1).norm();
	}
	double perimeter_mm = perimeter_m * 1000.0;

	// Calculate target point count based on perimeter and target spacing
	double target_spacing_m = target_spacing_mm / 1000.0;
	int target_count = (int)(perimeter_m / target_spacing_m);

	// Apply bounds: minimum 30 points, maximum 200 points
	target_count = std::max(30, std::min(200, target_count));

	// If already dense enough (within 20% of target), skip densification
	if (num_points >= (int)(target_count * 0.8)) {
		std::cout << "[DENSIFY] Breakline already dense (" << num_points
		          << " points >= " << (int)(target_count * 0.8) << " target), skipping densification" << std::endl;
		return breakline;
	}

	std::cout << "[DENSIFY] Perimeter=" << perimeter_mm << "mm, current="
	          << num_points << " points, target=" << target_count
	          << " points (spacing=" << target_spacing_mm << "mm)" << std::endl;

	// Use linear interpolation for densification (simple and preserves geometry)
	// Calculate uniform arc-length parameter for each target point
	std::vector<double> cumulative_lengths;
	cumulative_lengths.push_back(0.0);
	for (int i = 0; i < num_points - 1; i++) {
		Eigen::Vector3d p1(breakline(i,0), breakline(i,1), breakline(i,2));
		Eigen::Vector3d p2(breakline(i+1,0), breakline(i+1,1), breakline(i+1,2));
		double segment_length = (p2 - p1).norm();
		cumulative_lengths.push_back(cumulative_lengths.back() + segment_length);
	}

	// Generate densified points at uniform arc-length intervals
	MatrixXd densified(target_count, 3);
	double interval = perimeter_m / (target_count - 1);

	int source_idx = 0;
	for (int i = 0; i < target_count; i++) {
		double target_length = i * interval;

		// Find which segment this target length falls into
		while (source_idx < num_points - 2 && cumulative_lengths[source_idx + 1] < target_length) {
			source_idx++;
		}

		// Interpolate within the segment
		double segment_start = cumulative_lengths[source_idx];
		double segment_end = cumulative_lengths[source_idx + 1];
		double segment_length = segment_end - segment_start;

		double t = 0.0;
		if (segment_length > 1e-10) {
			t = (target_length - segment_start) / segment_length;
			t = std::max(0.0, std::min(1.0, t)); // Clamp to [0,1]
		}

		Eigen::Vector3d p1(breakline(source_idx,0), breakline(source_idx,1), breakline(source_idx,2));
		Eigen::Vector3d p2(breakline(source_idx+1,0), breakline(source_idx+1,1), breakline(source_idx+1,2));
		Eigen::Vector3d interpolated = (1.0 - t) * p1 + t * p2;

		densified.row(i) << interpolated(0), interpolated(1), interpolated(2);
	}

	std::cout << "[DENSIFY] Successfully densified from " << num_points
	          << " to " << densified.rows() << " points" << std::endl;

	return densified;
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

	// ADAPTIVE: Scale K with boundary size (5-50 range, ~10% of points)
	int boundary_size = cloud->points.size();
	int K = std::max(5, std::min(50, boundary_size / 10));
	std::cout << "[ADAPTIVE SEQUENCING] Boundary has " << boundary_size
	          << " points, using K=" << K << " for point sequencing" << std::endl;

	for (size_t t = 1; t < cloud->points.size(); t++)
	{
		searchPoint = currentPoint;
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

					/*PointXYZ p1;
					p1.x = (*cloud)[pointIdxNKNSearch[1]].x; p1.y = (*cloud)[pointIdxNKNSearch[1]].y; p1.z = (*cloud)[pointIdxNKNSearch[1]].z;
					PointXYZ p2;
					p2.x = (*cloud)[pointIdxNKNSearch[2]].x; p2.y = (*cloud)[pointIdxNKNSearch[2]].y; p2.z = (*cloud)[pointIdxNKNSearch[2]].z;
					if (p1.x == previousPoint.x && p1.y == previousPoint.y && p1.z == previousPoint.z)
					{
						if (cloud_sequenced->points[0].x != p2.x && cloud_sequenced->points[0].y != p2.y && cloud_sequenced->points[0].z != p2.z)
						{
							cloud_sequenced->points.push_back(p2);
						}
						previousPoint = currentPoint;
						currentPoint = p2;
					}
					else
					{
						if (cloud_sequenced->points[0].x != p1.x && cloud_sequenced->points[0].y != p1.y && cloud_sequenced->points[0].z != p1.z)
						{
							cloud_sequenced->points.push_back(p1);
						}
						previousPoint = currentPoint;
						currentPoint = p1;
					}*/
				}
			}
		}
	}

	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;
}

void getInitialBoundary_UsingPCL_BoundaryAlgo(pcl::PointCloud<pcl::PointNormal>::Ptr cloud, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BorderPointsCombined, string outPath)
{
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloudWithoutNormals(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);

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

	// ADAPTIVE: Compute boundary radius based on point cloud density
	// For N points distributed over a surface, estimate spacing = sqrt(area/N)
	// Pottery fragment surfaces typically span 100-1000 mm² (10-30mm characteristic length)
	// Use 400mm² as representative area (20mm × 20mm surface patch)
	int num_pts = cloudWithoutNormals->points.size();
	double estimated_area_mm2 = 400.0;  // Typical surface area for pottery fragment patches
	double estimated_spacing_mm = std::sqrt(estimated_area_mm2 / std::max(50, num_pts));

	// Boundary radius should be 6x the point spacing to capture local neighborhood
	double boundary_radius_mm = estimated_spacing_mm * 6.0;

	// Clamp to reasonable range: 3-50mm for pottery fragments
	// Dense clouds (>2000 pts) → ~3mm radius (fine detail)
	// Medium clouds (100-500 pts) → 8-12mm radius (standard)
	// Sparse clouds (<100 pts) → up to 17mm radius (robust to gaps)
	boundary_radius_mm = std::max(3.0, std::min(50.0, boundary_radius_mm));

	// IMPORTANT: Point cloud coordinates are in MILLIMETERS after coordinate fix (PREPROCESSING_FIXES.md)
	// PCL BoundaryEstimation expects radius in same units as point coordinates
	boundary_est.setRadiusSearch(boundary_radius_mm);
	std::cout << "[ADAPTIVE BOUNDARY EDGE] " << num_pts << " points, spacing≈"
	          << estimated_spacing_mm << "mm, boundary_r="
	          << boundary_radius_mm << "mm" << std::endl;
	//boundary_est.setAngleThreshold(0.6 * M_PI);//M_PI
	boundary_est.setAngleThreshold(M_PI * 0.6);//M_PI
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

	pcl::io::savePCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud);
	pcl::io::loadPCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud);
	pcl::PointCloud<pcl::PointXYZ>::Ptr unclusteredPoints(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr boundaryCloud_Improved(new pcl::PointCloud<pcl::PointXYZ>);
	
	std::experimental::filesystem::path filePathNew = { currentMeshFile };
	string fileNameOnly = filePathNew.stem().string().substr(0,14);
	// string outPathNew = filePathNew.parent_path().string() + "\\";
	string outPathNew = tempDataPath(potID);
	
	pcl::io::loadPLYFile(outPathNew + fileNameOnly + "_unclustered.ply", *unclusteredPoints);
	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(unclusteredPoints);

	pcl::PointXYZ searchPoint;
	// K nearest neighbor search
	int K = 1;
	std::vector<int> pointIdxNKNSearch(K);
	std::vector<float> pointNKNSquaredDistance(K);
	for (size_t i = 0; i < boundaryCloud->points.size(); i++)
	{
		searchPoint = boundaryCloud->points[i];
		if (kdtree.nearestKSearch(searchPoint, K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0)
		{
			for (std::size_t j = 0; j < pointIdxNKNSearch.size(); j++)
			{
				boundaryCloud_Improved->points.push_back(unclusteredPoints->points[pointIdxNKNSearch[j]]);
			}
		}
	}
	boundaryCloud_Improved->width = static_cast<int>(boundaryCloud_Improved->points.size());
	boundaryCloud_Improved->height = 1;
	pcl::io::savePCDFile(tempEdgeFolder + "boundaryImproved.pcd", *boundaryCloud_Improved);
	//-----------------------------------------------------------------------------
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::RadiusOutlierRemoval<pcl::PointXYZ> outrem;
	// build the filter
	outrem.setInputCloud(boundaryCloud_Improved);

	// ADAPTIVE: Outlier removal radius based on boundary point density
	// Use same area-based estimation as boundary detection
	int num_boundary = boundaryCloud_Improved->points.size();
	double estimated_area_mm2 = 400.0;  // Same assumption as boundary detection
	double outlier_spacing_mm = std::sqrt(estimated_area_mm2 / std::max(50, num_boundary));

	// Outlier removal needs slightly larger radius (8x spacing vs 6x for boundary)
	// This prevents removing valid isolated points near fragment edges
	double outlier_radius_mm = outlier_spacing_mm * 8.0;

	// Clamp to reasonable range: 4-50mm
	// Wider range than boundary detection to be more conservative about removing points
	outlier_radius_mm = std::max(4.0, std::min(50.0, outlier_radius_mm));
	outrem.setRadiusSearch(outlier_radius_mm);

	// COMBINATION APPROACH PART 1: Relax outlier removal for small boundaries
	int min_neighbors = (num_boundary < 100) ? 3 : 6;  // Less strict for small boundaries
	outrem.setMinNeighborsInRadius(min_neighbors);
	std::cout << "[ADAPTIVE OUTLIER] " << num_boundary << " boundary points, spacing≈"
	          << outlier_spacing_mm << "mm, outlier_r="
	          << outlier_radius_mm << "mm, min_neighbors=" << min_neighbors << std::endl;
	outrem.setKeepOrganized(true);
	// apply filter
	outrem.filter(*cloud_filtered);
	pcl::io::savePCDFileASCII(tempEdgeFolder + "cloud_Filtered.pcd", *cloud_filtered);

	pcl::io::loadPCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud_Improved);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced(new pcl::PointCloud<pcl::PointXYZ>);
	getPointsInSequence(boundaryCloud_Improved, cloud_sequenced);

	std::cout << "[EDGELINE DEBUG] Saving breakLineFromConcaveHull in ASCII mode..." << std::endl;
	pcl::io::savePLYFile(tempEdgeFolder + "_breakLineFromConcaveHull.ply", *cloud_sequenced, false); // ASCII mode
	pcl::io::savePCDFileASCII(tempEdgeFolder + "_breakLineFromConcaveHull.pcd", *cloud_sequenced);
	cloud_BorderPointsCombined->points.clear();
	pcl::io::loadPLYFile(tempEdgeFolder + "_breakLineFromConcaveHull.ply", *cloud_BorderPointsCombined);
}

//--------------------------- testing bspline curve ---------------------------------//
void PointCloud2Vector3d(pcl::PointCloud<Point>::Ptr cloud, pcl::on_nurbs::vector_vec3d& data)
{
	for (unsigned i = 0; i < cloud->size(); i++)
	{
		Point& p = cloud->at(i);
		if (!std::isnan(p.x) && !std::isnan(p.y) && !std::isnan(p.z))
			data.push_back(Eigen::Vector3d(p.x, p.y, p.z));
	}
}


void fitBSplineSurfaceAndGetNormalsOnProjectedPoints(string pointCloudDataFile, pcl::PointCloud<Point>::Ptr sampledBreaklinePointCloud, pcl::PointCloud<PointNormal>::Ptr projectedPointCloudWithNormals)
{
	string line;
	double d1;
	double d2;
	double d3;
	stringstream ss;
	ifstream myfile(pointCloudDataFile);
	std::vector<std::string> fileContents;
	std::string str;
	std::string file_contents;
	int numberOfPoints;


	//Reading file contents
	while (std::getline(myfile, str))
	{
		fileContents.push_back(str);
	}


	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_OriginalSurface(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_Sampled(new pcl::PointCloud<pcl::PointXYZ>);

	//Constructing the matrix
	numberOfPoints = fileContents.size();

	cloud_OriginalSurface->width = numberOfPoints;
	cloud_OriginalSurface->height = 1;
	cloud_OriginalSurface->is_dense = false;
	cloud_OriginalSurface->points.resize(cloud_OriginalSurface->width * cloud_OriginalSurface->height);

	MatrixXd P(3, numberOfPoints);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		ss << fileContents[i];
		ss >> P(0, i);
		ss >> P(1, i);
		ss >> P(2, i);

		cloud_OriginalSurface->points[i].x = P(0, i);
		cloud_OriginalSurface->points[i].y = P(1, i);
		cloud_OriginalSurface->points[i].z = P(2, i);

		ss.str(std::string());
	}

	pcl::RandomSample<pcl::PointXYZ> rs;
	rs.setInputCloud(cloud_OriginalSurface);
	rs.setSample(10000);

	rs.filter(*cloud_Sampled);


	// pcl::io::savePCDFile("cloudForSpline.pcd", *cloud_Sampled);
	pcl::io::savePCDFile(tempEdgeFolder + "cloudForSpline.pcd", *cloud_Sampled);

	string pcd_file = tempEdgeFolder + "cloudForSpline.pcd";
	string file_3dm = tempEdgeFolder + "splineSurfaceOutput.3dm";

	// Removed B-spline surface fitting viewer for headless operation



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
	// Removed point cloud visualization for headless operation
	printf("  %lu points in data set\n", cloud->size());

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

	pcl::PolygonMesh mesh;
	pcl::PointCloud<pcl::PointXYZ>::Ptr mesh_cloud(new pcl::PointCloud<pcl::PointXYZ>);
	std::vector<pcl::Vertices> mesh_vertices;
	std::string mesh_id = "mesh_nurbs";
	pcl::on_nurbs::Triangulation::convertSurface2PolygonMesh(fit.m_nurbs, mesh, mesh_resolution);
	// Removed mesh visualization for headless operation
	// viewer.addPolygonMesh(mesh, mesh_id);

	// surface refinement
	std::cout << "Surface refinement" << std::endl;
	for (unsigned i = 0; i < refinement; i++)
	{
		fit.refine(0);
		fit.refine(1);
		fit.assemble(params);
		fit.solve();
		pcl::on_nurbs::Triangulation::convertSurface2Vertices(fit.m_nurbs, mesh_cloud, mesh_vertices, mesh_resolution);
		// Removed mesh visualization update for headless operation
	}

	// surface fitting with final refinement level
	std::cout << "Surface fitting with final refinement level" << std::endl;
	for (unsigned i = 0; i < iterations; i++)
	{
		fit.assemble(params);
		fit.solve();
		pcl::on_nurbs::Triangulation::convertSurface2Vertices(fit.m_nurbs, mesh_cloud, mesh_vertices, mesh_resolution);
		// Removed mesh visualization update for headless operation
	}
	// Removed viewer close for headless operation

	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_EvaluatedPointsOnSurface(new pcl::PointCloud<pcl::PointNormal>);
	std::cout << "Evaluating points on surface" << std::endl;
	for (size_t i = 0; i < sampledBreaklinePointCloud->points.size(); i++)
	{
		Eigen::Vector3d originalPt(sampledBreaklinePointCloud->points[i].x, sampledBreaklinePointCloud->points[i].y, sampledBreaklinePointCloud->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		Vector3d pt, tu, tv, n;
		double error;
		int im_max_steps = 100;
		double im_accuracy = 1e-5;
		Vector2d paramsB = fit.inverseMapping(fit.m_nurbs, originalPt, hintPt, error, pt, tu, tv, im_max_steps, im_accuracy);

		double point[9];
		ON_3dVector normalEst;
		fit.m_nurbs.EvNormal(paramsB(0), paramsB(1), normalEst);

		pcl::PointNormal ptTmp;

		ptTmp.x = sampledBreaklinePointCloud->points[i].x; // point[0];
		ptTmp.y = sampledBreaklinePointCloud->points[i].y; // point[1];
		ptTmp.z = sampledBreaklinePointCloud->points[i].z; // point[2];
		ptTmp.normal_x = -normalEst.x;
		ptTmp.normal_y = -normalEst.y;
		ptTmp.normal_z = -normalEst.z;
		projectedPointCloudWithNormals->points.push_back(ptTmp);
	}

	projectedPointCloudWithNormals->width = static_cast<int>(projectedPointCloudWithNormals->points.size());
	projectedPointCloudWithNormals->height = 1;
	// pcl::io::savePCDFile(currentFileName + "cloudBreaklinePointsOnBSplineSurface.pcd", *projectedPointCloudWithNormals);
	pcl::io::savePCDFile(tempEdgeFolder + "cloudBreaklinePointsOnBSplineSurface.pcd", *projectedPointCloudWithNormals);

	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_AllPointsOnBSplineSurface(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_OriginalPointsOnSurface(new pcl::PointCloud<pcl::PointNormal>);
	pcl::io::loadPCDFile(pcd_file, *cloud_OriginalPointsOnSurface);
	for (size_t i = 0; i < cloud_OriginalPointsOnSurface->points.size(); i++)
	{
		Eigen::Vector3d originalPt(cloud_OriginalPointsOnSurface->points[i].x, cloud_OriginalPointsOnSurface->points[i].y, cloud_OriginalPointsOnSurface->points[i].z);
		Eigen::Vector2d hintPt(0.5, 0.5);
		// inverse mapping
		//Vector2d params;
		Vector3d pt, tu, tv, n;
		double error;
		int im_max_steps = 100;
		double im_accuracy = 1e-5;
		Vector2d paramsB = fit.inverseMapping(fit.m_nurbs, originalPt, hintPt, error, pt, tu, tv, im_max_steps, im_accuracy);
		/*cout << "Params: " << endl;
		cout << paramsB;*/

		double point[9];
		ON_3dVector normalEst;
		//fit.m_nurbs.Evaluate(paramsB(0), paramsB(1), 1, 3, point);
		fit.m_nurbs.EvNormal(paramsB(0), paramsB(1), normalEst);

		pcl::PointNormal ptTmp;

		ptTmp.x = cloud_OriginalPointsOnSurface->points[i].x; // point[0];
		ptTmp.y = cloud_OriginalPointsOnSurface->points[i].y; // point[1];
		ptTmp.z = cloud_OriginalPointsOnSurface->points[i].z; // point[2];
		ptTmp.normal_x = -normalEst.x;
		ptTmp.normal_y = -normalEst.y;
		ptTmp.normal_z = -normalEst.z;
		cloud_AllPointsOnBSplineSurface->points.push_back(ptTmp);
	}

	cloud_AllPointsOnBSplineSurface->width = static_cast<int>(cloud_AllPointsOnBSplineSurface->points.size());
	cloud_AllPointsOnBSplineSurface->height = 1;
	// pcl::io::savePCDFile(currentFileName + "cloudAllPointsOnBSplineSurface.pcd", *cloud_AllPointsOnBSplineSurface);
	pcl::io::savePCDFile(tempEdgeFolder + "cloudAllPointsOnBSplineSurface.pcd", *cloud_AllPointsOnBSplineSurface);

}

Vector3d closestPointOnSeg(Vector3d& P, Vector3d& Q, Vector3d& X)
{
	double lambda = ((X - P).dot(Q - P)) / ((Q - P).dot(Q - P));
	Vector3d S(3);
	if (lambda <= 0)
	{S = P;}
	else if (lambda >= 1)
	{S = Q;}
	else
	{ S = P + lambda * (Q - P);}

	return S;

}

void writeMatrix_to_XYZ(MatrixXd& src, string fileName, int cols = 3)
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

void writeMatrix_to_XYZ_withNormals(MatrixXd& src, string fileName)
{
	ofstream writeStream(fileName, ios::out | ios::trunc);
	if (writeStream)
	{
		for (size_t i = 0; i < src.rows(); i++)
		{
			writeStream << src(i, 0) << " ";
			writeStream << src(i, 1) << " ";
			writeStream << src(i, 2) << " ";
			writeStream << src(i, 3) << " ";
			writeStream << src(i, 4) << " ";
			writeStream << src(i, 5) << " " << endl;
		}

		writeStream.close();
	}
	else
	{
		cout << "Error opening file" << endl;
	}
}

// peak detection code//
//-----------------------------------------------------------------------------
void diff(vector<float> in, vector<float>& out)
{
	out = vector<float>(in.size() - 1);

	for (int i = 1; i < in.size(); ++i)
		out[i - 1] = in[i] - in[i - 1];
}

void vectorProduct(vector<float> a, vector<float> b, vector<float>& out)
{
	out = vector<float>(a.size());

	for (int i = 0; i < a.size(); ++i)
		out[i] = a[i] * b[i];
}

void findIndicesLessThan(vector<float> in, float threshold, vector<int>& indices)
{
	for (int i = 0; i < in.size(); ++i)
		if (in[i] < threshold)
			indices.push_back(i + 1);
}

template <typename T>
void selectElements(const std::vector<T>& in, 
                    const std::vector<int>& indices, 
                    std::vector<T>& out)
{
    for (int idx : indices)
    {
        out.push_back(in[idx]);
    }
}

void signVector(vector<float> in, vector<int>& out)
{
	out = vector<int>(in.size());

	for (int i = 0; i < in.size(); ++i)
	{
		if (in[i] > 0)
			out[i] = 1;
		else if (in[i] < 0)
			out[i] = -1;
		else
			out[i] = 0;
	}
}

// Custom PCD writer with segment headers for SFS compatibility
void writeBreaklinePCDWithSegments(const std::string& filename, const pcl::PointCloud<pcl::PointNormal>& cloud, const std::vector<std::string>& segmentIndex, const std::vector<int>& peakIndices = std::vector<int>(), bool convertToMM = true)
{
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << " for writing" << std::endl;
        return;
    }

    int totalPoints = cloud.points.size();

    // Use peak indices for proper segmentation if provided
    std::vector<std::pair<int, int>> properSegments;
    if (!peakIndices.empty()) {
        // Build segments from peak detection results
        int startIdx = 1; // 1-indexed for PCD format
        for (size_t i = 0; i < peakIndices.size(); i++) {
            int endIdx = peakIndices[i] + 1; // Convert to 1-indexed
            if (endIdx > totalPoints) endIdx = totalPoints;
            properSegments.push_back({startIdx, endIdx});
            startIdx = endIdx + 1;
        }
        // Add final segment if needed
        if (startIdx <= totalPoints) {
            properSegments.push_back({startIdx, totalPoints});
        }
    } else {
        // Fall back to using segmentIndex if no peak data
        for (const auto& segInfo : segmentIndex) {
            std::istringstream iss(segInfo);
            int start, end, flag;
            if (iss >> start >> end >> flag) {
                properSegments.push_back({start, end});
            }
        }
    }

    int totalSegments = properSegments.size();

    // Write PCD header with segment information
    file << "# .PCD v0.7 - Point Cloud Data file format" << std::endl;
    file << "# " << totalSegments << " " << totalPoints << " 0" << std::endl;

    // Write segment ranges
    for (const auto& seg : properSegments) {
        file << "# " << seg.first << " " << seg.second << " 0" << std::endl;
    }

    // Standard PCD header
    file << "VERSION 0.7" << std::endl;
    file << "FIELDS x y z normal_x normal_y normal_z curvature" << std::endl;
    file << "SIZE 4 4 4 4 4 4 4" << std::endl;
    file << "TYPE F F F F F F F" << std::endl;
    file << "COUNT 1 1 1 1 1 1 1" << std::endl;
    file << "WIDTH " << cloud.points.size() << std::endl;
    file << "HEIGHT 1" << std::endl;
    file << "VIEWPOINT 0 0 0 1 0 0 0" << std::endl;
    file << "POINTS " << cloud.points.size() << std::endl;
    file << "DATA ascii" << std::endl;

    // Write point data with coordinate unit conversion
    for (const auto& point : cloud.points) {
        // Convert coordinates to millimeters, keep normals normalized
        double x = convertToMM ? point.x * 1000.0 : point.x;
        double y = convertToMM ? point.y * 1000.0 : point.y;
        double z = convertToMM ? point.z * 1000.0 : point.z;

        file << x << " " << y << " " << z << " "
             << point.normal_x << " " << point.normal_y << " " << point.normal_z << " "
             << point.curvature << std::endl;
    }

    file.close();
    std::cout << "Saved PCD with " << totalSegments << " segments to: " << filename << std::endl;
}


void findPeaks(vector<float> x0, vector<int>& peakInds, double sensitivity_divisor = 4.0)
{

	int minIdx = distance(x0.begin(), min_element(x0.begin(), x0.end()));
	int maxIdx = distance(x0.begin(), max_element(x0.begin(), x0.end()));

	// ADAPTIVE: Use provided sensitivity divisor instead of fixed 4.0
	// Larger divisor = smaller sel = fewer peaks detected (for sparse data)
	// Smaller divisor = larger sel = more peaks detected (for dense data)
	float sel = (x0[maxIdx] - x0[minIdx]) / sensitivity_divisor;

	int len0 = x0.size();

	vector<float> dx;
	diff(x0, dx);
	replace(dx.begin(), dx.end(), 0.0, -EPS);
	vector<float> dx0(dx.begin(), dx.end() - 1);
	vector<float> dx1(dx.begin() + 1, dx.end());
	vector<float> dx2;

	vectorProduct(dx0, dx1, dx2);

	vector<int> ind;
	findIndicesLessThan(dx2, 0, ind); // Find where the derivative changes sign

	vector<float> x;

	vector<int> indAux(ind.begin(), ind.end());
	selectElements(x0, indAux, x);
	x.insert(x.begin(), x0[0]);
	x.insert(x.end(), x0[x0.size() - 1]);;


	ind.insert(ind.begin(), 0);
	ind.insert(ind.end(), len0);

	int minMagIdx = distance(x.begin(), min_element(x.begin(), x.end()));
	float minMag = x[minMagIdx];
	float leftMin = minMag;
	int len = x.size();

	if (len > 2)
	{
		float tempMag = minMag;
		bool foundPeak = false;
		int ii;

		vector<float> xSub0(x.begin(), x.begin() + 3);//tener cuidado subvector
		vector<float> xDiff;//tener cuidado subvector
		diff(xSub0, xDiff);

		vector<int> signDx;
		signVector(xDiff, signDx);

		if (signDx[0] <= 0) // The first point is larger or equal to the second
		{
			if (signDx[0] == signDx[1]) // Want alternating signs
			{
				x.erase(x.begin() + 1);
				ind.erase(ind.begin() + 1);
				len = len - 1;
			}
		}
		else // First point is smaller than the second
		{
			if (signDx[0] == signDx[1]) // Want alternating signs
			{
				x.erase(x.begin());
				ind.erase(ind.begin());
				len = len - 1;
			}
		}

		if (x[0] >= x[1])
			ii = 0;
		else
			ii = 1;

		float maxPeaks = ceil(static_cast<float>(len) / 2.0);
		vector<int> peakLoc(maxPeaks, 0);
		vector<float> peakMag(maxPeaks, 0.0);
		int cInd = 1;
		int tempLoc;

		while (ii < len)
		{
			ii = ii + 1;//This is a peak
			//Reset peak finding if we had a peak and the next peak is bigger
			//than the last or the left min was small enough to reset.
			if (foundPeak)
			{
				tempMag = minMag;
				foundPeak = false;
			}

			//Found new peak that was lager than temp mag and selectivity larger
			//than the minimum to its left.

			if (x[ii - 1] > tempMag && x[ii - 1] > leftMin + sel)
			{
				tempLoc = ii - 1;
				tempMag = x[ii - 1];
			}

			//Make sure we don't iterate past the length of our vector
			if (ii == len)
				break; //We assign the last point differently out of the loop

			ii = ii + 1; // Move onto the valley

			//Come down at least sel from peak
			if (!foundPeak && tempMag > sel + x[ii - 1])
			{
				foundPeak = true; //We have found a peak
				leftMin = x[ii - 1];
				peakLoc[cInd - 1] = tempLoc; // Add peak to index
				peakMag[cInd - 1] = tempMag;
				cInd = cInd + 1;
			}
			else if (x[ii - 1] < leftMin) // New left minima
				leftMin = x[ii - 1];

		}

		// Check end point
		if (x[x.size() - 1] > tempMag && x[x.size() - 1] > leftMin + sel)
		{
			peakLoc[cInd - 1] = len - 1;
			peakMag[cInd - 1] = x[x.size() - 1];
			cInd = cInd + 1;
		}
		else if (!foundPeak && tempMag > minMag)// Check if we still need to add the last point
		{
			peakLoc[cInd - 1] = tempLoc;
			peakMag[cInd - 1] = tempMag;
			cInd = cInd + 1;
		}

		//Create output
		if (cInd > 0)
		{
			vector<int> peakLocTmp(peakLoc.begin(), peakLoc.begin() + cInd - 1);
			selectElements(ind, peakLocTmp, peakInds);
			//peakMags = vector<float>(peakLoc.begin(), peakLoc.begin()+cInd-1);
		}
	}
}
//----------------------------------------------------------------------------
#include <pcl/surface/on_nurbs/fitting_curve_pdm.h>
// Removed global curve fitting viewer for headless operation

std::vector<int> detectSeparateLineSegments(string b1_FilePath, int len = 10) //len = 10
{
	// Read breakline to determine adaptive parameters
	MatrixXd b1_check = readFile(b1_FilePath, 3);
	int num_points = b1_check.rows();

	// ADAPTIVE WINDOW: Scale window size with breakline length
	int adaptive_len;
	if (num_points < 30) {
		// Small breaklines: use 20% window (min 2, max 5)
		adaptive_len = std::max(2, std::min(5, num_points / 5));
		std::cout << "[ADAPTIVE WINDOW] Small breakline (" << num_points
		          << " points) using window len=" << adaptive_len << std::endl;
	} else if (num_points < 60) {
		// Medium breaklines: use reduced window
		adaptive_len = 5;
		std::cout << "[ADAPTIVE WINDOW] Medium breakline (" << num_points
		          << " points) using window len=" << adaptive_len << std::endl;
	} else {
		// Large breaklines: use original window size
		adaptive_len = 10;
	}

	// Override the parameter with adaptive value
	len = adaptive_len;

	// SAFETY CHECK: Minimum points needed for wraparound buffer
	int min_required_points = 2 * len + 5;

	if (num_points < min_required_points) {
		std::cout << "[SEGMENT DETECTION] Breakline has only " << num_points
		          << " points (< " << min_required_points << " required for segment detection with window=" << len << ")" << std::endl;
		std::cout << "[SEGMENT DETECTION] Treating entire breakline as single segment" << std::endl;
		return std::vector<int>();  // Empty vector = single segment
	}

	//defining Kelly's list of contrast colors
	vector<int> colorList_R, colorList_G, colorList_B;
	colorList_R.push_back(197); colorList_G.push_back(90); colorList_B.push_back(17);
	colorList_R.push_back(146); colorList_G.push_back(208); colorList_B.push_back(80);
	colorList_R.push_back(46); colorList_G.push_back(117); colorList_B.push_back(182);
	colorList_R.push_back(112); colorList_G.push_back(48); colorList_B.push_back(160);
	colorList_R.push_back(255); colorList_G.push_back(192); colorList_B.push_back(0);


	colorList_R.push_back(193); colorList_G.push_back(0); colorList_B.push_back(32);
	colorList_R.push_back(0); colorList_G.push_back(125); colorList_B.push_back(52);
	colorList_R.push_back(255); colorList_G.push_back(179); colorList_B.push_back(0);
	colorList_R.push_back(0); colorList_G.push_back(83); colorList_B.push_back(138);

	colorList_R.push_back(255); colorList_G.push_back(104); colorList_B.push_back(0);

	colorList_R.push_back(246); colorList_G.push_back(118); colorList_B.push_back(142);
	colorList_R.push_back(128); colorList_G.push_back(62); colorList_B.push_back(117);
	colorList_R.push_back(255); colorList_G.push_back(122); colorList_B.push_back(92);
	colorList_R.push_back(283); colorList_G.push_back(55); colorList_B.push_back(122);
	colorList_R.push_back(255); colorList_G.push_back(142); colorList_B.push_back(0);
	colorList_R.push_back(179); colorList_G.push_back(40); colorList_B.push_back(81);
	colorList_R.push_back(244); colorList_G.push_back(200); colorList_B.push_back(0);


	//getting file name
	string fileName = b1_FilePath;
	const size_t last_slash_idx = fileName.find_last_of("/\\");
	if (std::string::npos != last_slash_idx)
	{
		fileName.erase(0, last_slash_idx + 1);
	}
	//removing extension
	const size_t period_idx = fileName.rfind('.');
	if (std::string::npos != period_idx)
	{
		fileName.erase(period_idx);
	}

    std::cerr << "[EDGELINE DEBUG] detectSeparateLineSegments: file=" << b1_FilePath << " len=" << len << std::endl;
    fs::remove_all("Segments");
	std::this_thread::sleep_for(std::chrono::milliseconds(100));
	fs::create_directory("Segments");
	string outPath = "Segments/";

	fs::remove_all("SegmentsRawPts");
	std::this_thread::sleep_for(std::chrono::milliseconds(100));
	fs::create_directory("SegmentsRawPts");
	string outPathRawPts = "SegmentsRawPts/";



	MatrixXd b1, b1_withN;
    b1 = readFile(b1_FilePath, 3);// 
    b1_withN = readFile(b1_FilePath, 6);
    if (b1_withN.cols() != 6 || b1_withN.rows() != b1.rows()) {
        std::cerr << "[EDGELINE DEBUG] b1_withN not 6 columns or size mismatch; synthesizing normals." << std::endl;
        // Compute simple tangent-based normals along the curve as fallback
        MatrixXd b1n(b1.rows(), 6);
        for (int i = 0; i < b1.rows(); ++i) {
            b1n(i,0)=b1(i,0); b1n(i,1)=b1(i,1); b1n(i,2)=b1(i,2);
            // finite differences to estimate tangent
            int i0 = std::max(0, i-1), i1 = std::min((int)b1.rows()-1, i+1);
            Vector3d t = (b1.row(i1) - b1.row(i0));
            if (t.norm() > 1e-9) t.normalize(); else t << 1,0,0;
            // pick an arbitrary normal orthogonal to tangent
            Vector3d n = t.cross(Vector3d(0,0,1)); if (n.norm()<1e-6) n = t.cross(Vector3d(0,1,0)); n.normalize();
            b1n(i,3)=n(0); b1n(i,4)=n(1); b1n(i,5)=n(2);
        }
        b1_withN = b1n;
    }
    std::cerr << "[EDGELINE DEBUG] b1 rows=" << b1.rows() << " cols=" << b1.cols() << " b1_withN rows=" << b1_withN.rows() << " cols=" << b1_withN.cols() << std::endl;
    if (b1.rows() == 0 || b1_withN.rows() == 0) {
        std::cerr << "[EDGELINE DEBUG] Empty breakline data, returning no segments." << std::endl;
        return std::vector<int>();
    }
	//int len = 60;
	int k = 0;
	int noOfPossiblePoints = b1.rows() - (2 * len);
	Vector3d segL, segS, pointClosest, tmp;


    MatrixXd dist_scoreB1(b1.rows() + 2 * len, 1);
    MatrixXd distScoreOriginalLength(b1.rows(), 1);//(len*2 -1)*noOfAvailableSegs, 1);
    std::cerr << "[EDGELINE DEBUG] dist_scoreB1 size=" << dist_scoreB1.rows() << "x" << dist_scoreB1.cols() << " distScoreOriginalLength size=" << distScoreOriginalLength.rows() << "x" << distScoreOriginalLength.cols() << std::endl;
	//MatrixXd angle_scoreB1(noOfPossiblePoints, 1);
	Vector3d segS_p1, segS_p2, segL_p1, segL_p2, segS_centerPt(3);
	int t = 0;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_b1_ptr(new pcl::PointCloud<pcl::PointXYZ>);

	pcl::PointCloud<pcl::PointXYZRGB>::Ptr pointCloud_b1_ptr(new pcl::PointCloud<pcl::PointXYZRGB>);

    for (size_t i = 0; i < b1.rows() + 2 * len; i++)
    {
        if (i >= (size_t)dist_scoreB1.rows()) { std::cerr << "[EDGELINE DEBUG] OOB write dist_scoreB1 i=" << i << std::endl; break; }
        dist_scoreB1(i, 0) = 0;
    }

	t = 0;
	pcl::PointXYZ p1, p2;
	int pointCount = 0;

    MatrixXd bCombined(b1.rows() + 2 * len, 3);
    std::cerr << "[EDGELINE DEBUG] bCombined size=" << bCombined.rows() << "x" << bCombined.cols() << std::endl;
    for (size_t i = 0; i < bCombined.rows(); i++)
    {
        bCombined(i, 0) = 0;
        bCombined(i, 1) = 0;
        bCombined(i, 2) = 0;
    }
	int q = len;
	for (size_t i = 0; i < len; i++)
	{
		bCombined(i, 0) = b1(b1.rows() - q, 0);
		bCombined(i, 1) = b1(b1.rows() - q, 1);
		bCombined(i, 2) = b1(b1.rows() - q, 2);
		q--;
	}
	for (size_t i = 0; i < b1.rows(); i++)
	{
		bCombined(i + len, 0) = b1(i, 0);
		bCombined(i + len, 1) = b1(i, 1);
		bCombined(i + len, 2) = b1(i, 2);
	}
	q = 0;
	for (size_t i = 0; i < len; i++)
	{
		bCombined(i + len + b1.rows(), 0) = b1(q, 0);
		bCombined(i + len + b1.rows(), 1) = b1(q, 1);
		bCombined(i + len + b1.rows(), 2) = b1(q, 2);
		q++;
	}

	for (int i = len; i < bCombined.rows() - len; i++)
	{
		segL = bCombined.row(i - len) - bCombined.row(i + len);
		segL_p1 << bCombined(i - len, 0), bCombined(i - len, 1), bCombined(i - len, 2);
		segL_p2 << bCombined(i + len, 0), bCombined(i + len, 1), bCombined(i + len, 2);
		segS_centerPt << bCombined(i, 0), bCombined(i, 1), bCombined(i, 2);// the actual point in the center
		pointClosest = closestPointOnSeg(segL_p1, segL_p2, segS_centerPt);

		dist_scoreB1(i, 0) = (pointClosest - segS_centerPt).squaredNorm();
		t++;
	}


    for (size_t i = 0; i < (size_t)distScoreOriginalLength.rows(); i++)
    {
        size_t src = i + (size_t)len;
        if (src >= (size_t)dist_scoreB1.rows()) src = dist_scoreB1.rows() - 1;
        distScoreOriginalLength(i, 0) = dist_scoreB1(src);
    }

	// find the peaks and their indexes
	bool lookingForPeak = true;
	bool lookingForValley = false;
	vector<double> peakData_value, tmpDataValue;
	vector<int> peakData_index, tmpDataIndex;

	vector<double> peakData_firstPartValues;
	vector<int> peakData_firstPartIndex;

	bool continuousHighValueFromStart = false;

	writeMatrix_to_XYZ(distScoreOriginalLength, currentFileName, 1);

	vector<float> in;
	for (size_t i = 0; i < distScoreOriginalLength.rows(); i++)
	{
		in.push_back(distScoreOriginalLength(i, 0));
	}
	vector<int> out;

	// FIXED PEAK DETECTION SENSITIVITY (Issue #1 fix)
	// Previously: Adaptive sensitivity (4.0-8.0) caused segment count mismatches
	// Problem: Fragments from same pot had different segment counts → LCS matching failed
	// Solution: Fixed sensitivity ensures consistent segmentation across all fragments
	// This is critical for downstream Structure-from-Sherds assembly system
	// Value 5.0 is middle ground: balances noise rejection with feature detection
	double sensitivity_divisor = 5.0;
	std::cout << "[FIXED PEAK DETECTION] Breakline (" << num_points
	          << " points) using fixed sensitivity (divisor=" << sensitivity_divisor
	          << ") for assembly consistency" << std::endl;

	findPeaks(in, out, sensitivity_divisor);

	// SAFETY CHECK: Prevent accessing empty vector
	if (out.empty()) {
		std::cout << "[BREAKLINE SAFETY] No peaks found in distance score - treating as single segment" << std::endl;
		return std::vector<int>();
	}

	if (out[out.size() - 1] == in.size())
	{
		out[out.size() - 1]--;
	}

	bool specialCase = false;
	if (out.size() > 0 && out[0] == 0 && out[out.size() - 1] == in.size() - 1)
	{
		if (out[0] >= out[out.size() - 1])
		{
			out.erase(out.end() - 1);
		}
		else
		{
			out.erase(out.begin());
		}
		specialCase = true;
	}
	for (size_t i = 0; i < out.size(); i++)
	{
		if (!specialCase)
		{
			if (out[i] != 0 && out[i] != in.size() - 1)
			{
				peakData_value.push_back(distScoreOriginalLength(out[i], 0));
				peakData_index.push_back(out[i]);
			}
		}
		else
		{
			peakData_value.push_back(distScoreOriginalLength(out[i], 0));
			peakData_index.push_back(out[i]);
		}
	}

	int randomColorR, randomColorG, randomColorB;
	randomColorR = std::floor(rand() * 256);
	randomColorG = std::floor(rand() * 256);
	randomColorB = std::floor(rand() * 256);

	t = 0;
	if (peakData_index.size() == 0)
	{
		peakData_index.push_back(b1.rows() - 1);
	}
	MatrixXd breakLineSeg(peakData_index[0] + 1, 6);
	int j = 0;
	vector <pcl::PointNormal> firstSeg, lastSeg;
	int noOfSegmentsDetected = 1;
	for (int i = 0; i < b1.rows(); i++)
	{
		breakLineSeg.row(j) = b1_withN.row(i);
		j++;

		pcl::PointXYZ basic_point;
		basic_point.x = b1(i, 0);
		basic_point.y = b1(i, 1);
		basic_point.z = b1(i, 2);
		cloud_b1_ptr->points.push_back(basic_point);

		pcl::PointXYZRGB point;
		point.x = basic_point.x;
		point.y = basic_point.y;
		point.z = basic_point.z;
		uint32_t rgb = (255, 255, 255);

		if (t <= peakData_index.size() - 1)
		{
			if (i >= peakData_index[t])
			{
				if (t == 0)
				{
					for (size_t q = 0; q < breakLineSeg.rows(); q++)
					{
						pcl::PointNormal pn;
						pn.x = breakLineSeg(q, 0);
						pn.y = breakLineSeg(q, 1);
						pn.z = breakLineSeg(q, 2);
						pn.normal_x = breakLineSeg(q, 3);
						pn.normal_y = breakLineSeg(q, 4);
						pn.normal_z = breakLineSeg(q, 5);
						firstSeg.push_back(pn);
					}
				}
				else
				{
					int rows = breakLineSeg.rows() - 1;
					// SEGMENT SIZE FILTER: Only save segments with >= 5 points
					int min_segment_points = 5;
					if (breakLineSeg.rows() >= min_segment_points) {
						writeMatrix_to_XYZ_withNormals(breakLineSeg, outPath + to_string(t + 1) + ".xyz");
						noOfSegmentsDetected++;
					} else {
						std::cout << "[SEGMENT FILTER] Skipping tiny segment with only "
						          << breakLineSeg.rows() << " points (< " << min_segment_points << " required)" << std::endl;
					}
				}


				t++;
				if (t <= peakData_index.size() - 1)
				{
					breakLineSeg = ArrayXXd::Zero(peakData_index[t] - peakData_index[t - 1] + 1, 6);
					j = 0;
					breakLineSeg.row(j) = b1_withN.row(i);
					j++;
				}
				else
				{
					breakLineSeg = ArrayXXd::Zero(b1.rows() - peakData_index[t - 1], 6);
					j = 0;
					breakLineSeg.row(j) = b1_withN.row(i);
					j++;
					if (i == b1.rows() - 1)
					{
						t--;
					}
				}
			}
		}

		if (t < peakData_index.size())
		{
			rgb = (static_cast<uint32_t>(colorList_R[t]) << 16 | static_cast<uint32_t>(colorList_G[t]) << 8 | static_cast<uint32_t>(colorList_B[t]));
		}
		else
		{
			rgb = (static_cast<uint32_t>(colorList_R[0]) << 16 | static_cast<uint32_t>(colorList_G[0]) << 8 | static_cast<uint32_t>(colorList_B[0]));
		}

		point.rgb = *reinterpret_cast<float*>(&rgb);
		pointCloud_b1_ptr->points.push_back(point);
	}

	for (size_t q = 0; q < breakLineSeg.rows(); q++)
	{
		pcl::PointNormal pn;
		pn.x = breakLineSeg(q, 0);
		pn.y = breakLineSeg(q, 1);
		pn.z = breakLineSeg(q, 2);
		pn.normal_x = breakLineSeg(q, 3);
		pn.normal_y = breakLineSeg(q, 4);
		pn.normal_z = breakLineSeg(q, 5);
		lastSeg.push_back(pn);
	}
	for (size_t i = 0; i < firstSeg.size(); i++)
	{
		lastSeg.push_back(firstSeg[i]);
	}
	MatrixXd segMatrix(lastSeg.size(), 6);
	for (size_t i = 0; i < lastSeg.size(); i++)
	{
		segMatrix(i, 0) = lastSeg[i].x;
		segMatrix(i, 1) = lastSeg[i].y;
		segMatrix(i, 2) = lastSeg[i].z;
		segMatrix(i, 3) = lastSeg[i].normal_x;
		segMatrix(i, 4) = lastSeg[i].normal_y;
		segMatrix(i, 5) = lastSeg[i].normal_z;
	}

	// SEGMENT SIZE FILTER: Only save first segment if >= 5 points
	int min_segment_points = 5;
	if (segMatrix.rows() >= min_segment_points) {
		writeMatrix_to_XYZ_withNormals(segMatrix, outPath + "1.xyz");
	} else {
		std::cout << "[SEGMENT FILTER] Skipping tiny first segment with only "
		          << segMatrix.rows() << " points (< " << min_segment_points << " required)" << std::endl;
	}

	cloud_b1_ptr->width = static_cast<int>(cloud_b1_ptr->points.size());
	cloud_b1_ptr->height = 1;
	pointCloud_b1_ptr->width = static_cast<int>(pointCloud_b1_ptr->points.size());
	pointCloud_b1_ptr->height = 1;

	cout << "Detected segments = " + noOfSegmentsDetected << endl;


	//finding the breakline segments fronm the raw breakline pts
	std::vector<int> nn_indices;
	std::vector<int> nn_indicesAll;
	std::vector<float> nn_dists;
	pcl::PointCloud<pcl::PointXYZ>::Ptr rawBreaklinePts(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr smoothedSegment(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr rawBreaklinePtsInSegment(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::KdTree<pcl::PointXYZ>::Ptr tree_(new pcl::KdTreeFLANN<pcl::PointXYZ>);
	//pcl::io::loadPCDFile("_breakLineFromSimpleAlgoVer2.pcd", *rawBreaklinePts);
	pcl::io::loadPCDFile(tempEdgeFolder + "CompleteBreakline.pcd", *rawBreaklinePts);
	tree_->setInputCloud(rawBreaklinePts);
	MatrixXd segmentMatrix, allPointsOnSegMatrix;
	for (size_t i = 0; i < noOfSegmentsDetected; i++)
	{
		segmentMatrix = readFile(outPath + to_string(i + 1) + ".xyz", 6);

		// SAFETY: Skip empty or missing segments (filtered out by minimum size)
		if (segmentMatrix.rows() == 0) {
			std::cout << "[SEGMENT SAFETY] Skipping empty/missing segment " << (i+1) << std::endl;
			continue;
		}

		for (size_t i = 0; i < segmentMatrix.rows(); i++)
		{
			smoothedSegment->points.push_back(PointXYZ(segmentMatrix(i, 0), segmentMatrix(i, 1), segmentMatrix(i, 2)));
		}
		smoothedSegment->width = smoothedSegment->points.size();
		smoothedSegment->height = 1;

		// SAFETY: Skip if smoothedSegment is empty (prevents underflow in size()-1)
		if (smoothedSegment->points.size() < 2) {
			std::cout << "[SEGMENT SAFETY] Skipping segment " << (i+1) << " with < 2 points" << std::endl;
			smoothedSegment->points.clear();
			continue;
		}

		for (size_t i = 1; i < smoothedSegment->points.size() - 1; i++)
		{
			tree_->nearestKSearch(smoothedSegment->points[i], 20, nn_indices, nn_dists);
			for (size_t i = 0; i < 20; i++)
			{
				if (nn_dists[i] <= 1.8)
				{
					nn_indicesAll.push_back(nn_indices[i]);
				}
				//rawBreaklinePtsInSegment->points.push_back(rawBreaklinePts->points[nn_indices[i]]);
			}
		}

		// Sort and remove duplicate indices
		std::sort(nn_indicesAll.begin(), nn_indicesAll.end());
		nn_indicesAll.erase(std::unique(nn_indicesAll.begin(), nn_indicesAll.end()), nn_indicesAll.end());

		MatrixXd allPointsOnSegMatrix(nn_indicesAll.size(), 3);
		for (size_t i = 0; i < nn_indicesAll.size(); i++)
		{
			allPointsOnSegMatrix.row(i) << rawBreaklinePts->points[nn_indicesAll[i]].x, rawBreaklinePts->points[nn_indicesAll[i]].y, rawBreaklinePts->points[nn_indicesAll[i]].z;
			//rawBreaklinePtsInSegment->points.push_back(rawBreaklinePts->points[nn_indicesAll[i]]);
		}

		writeMatrix_to_XYZ(allPointsOnSegMatrix, outPathRawPts + to_string(i + 1) + "_rawPts.xyz");
		nn_indicesAll.clear();
		smoothedSegment->points.clear();

	}

	// Removed RGB visualization for headless operation
	
	// Return peak indices for proper segment header generation
	return peakData_index;
}

void estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface(string fileName, bool outerSurface, double distThreshold = 2, double distThresholdForMatchingEndpoints = 20)
{
	int numberOfPointsInCloud = 0;
	MatrixXd R(3, 3);
	Vector3d origNormR(3);
	MatrixXd b_ij(16, 3);
	MatrixXd origData;
	MatrixXd dataCenter;
	MatrixXd projectedOnPatch;
	MatrixXd surfaceNormals;
	double U_min, U_max, V_min, V_max;
	string outPath = "";
	string origFilePath = fileName;

	MatrixXd originalPointCloudMatrix;
	originalPointCloudMatrix = readFile(origFilePath, 3);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_OriginalSurface(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < originalPointCloudMatrix.rows(); i++)
	{
		cloud_OriginalSurface->points.push_back(pcl::PointXYZ(originalPointCloudMatrix(i, 0), originalPointCloudMatrix(i, 1), originalPointCloudMatrix(i, 2)));
	}
	cloud_OriginalSurface->width = cloud_OriginalSurface->points.size();
	cloud_OriginalSurface->height = 1;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_FragmentBoundaryFromPointCloudData(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_FilteredBoundary(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_RimFromPointCloudData(new pcl::PointCloud<pcl::PointXYZ>);

	cout << "Getting the inital boundary..." << endl;
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_OriginalSurfaceWithNormals(new pcl::PointCloud<pcl::PointNormal>);
	pcl::io::loadPCDFile(tempEdgeFolder + "cloud_Surface_AllSamples_Cleaned.pcd", *cloud_OriginalSurfaceWithNormals);
	getInitialBoundary_UsingPCL_BoundaryAlgo(cloud_OriginalSurfaceWithNormals, cloud_FragmentBoundaryFromPointCloudData, outPath);

	int numberOfPoints = cloud_FragmentBoundaryFromPointCloudData->points.size();
	MatrixXd P(numberOfPoints, 3);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		P(i, 0) = cloud_FragmentBoundaryFromPointCloudData->points[i].x;
		P(i, 1) = cloud_FragmentBoundaryFromPointCloudData->points[i].y;
		P(i, 2) = cloud_FragmentBoundaryFromPointCloudData->points[i].z;
	}

	cout << "Initiating uniform sampling and smoothing of breakline segments..." << endl;

	MatrixXd sampledBreakLineResults = smoothAndSampleBreaklinesVer4UsingBSpline(P);

	// std::cout << "Sampled Break Line Results Size: " << sampledBreakLineResults.rows() << "x" << sampledBreakLineResults.cols() << std::endl;

	// std::cout << "Sampled Break Line Results:" << std::endl;
	for (int i = 0; i < sampledBreakLineResults.rows(); ++i) {
		for (int j = 0; j < sampledBreakLineResults.cols(); ++j) {
			// std::cout << sampledBreakLineResults(i, j) << " ";
		}
		// std::cout << std::endl;
	}

	MatrixXd matrixPointCloud = sampledBreakLineResults;
	if (sampledBreakLineResults.cols() != 3 && sampledBreakLineResults.rows() == 3)
	{
		matrixPointCloud = sampledBreakLineResults.transpose();
	}

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
	cloud->width = matrixPointCloud.rows();
	cloud->height = 1;
	cloud->is_dense = false;
	cloud->points.resize(cloud->width * cloud->height);

	for (size_t i = 0; i < matrixPointCloud.rows(); i++)
	{
		cloud->points[i].x = matrixPointCloud(i, 0);
		cloud->points[i].y = matrixPointCloud(i, 1);
		cloud->points[i].z = matrixPointCloud(i, 2);
	}

	pcl::io::savePCDFile(tempEdgeFolder + "smoothed.pcd", *cloud);

	pcl::PointCloud<pcl::PointNormal>::Ptr projectedCloudWithNormals(new pcl::PointCloud<pcl::PointNormal>);
	fitBSplineSurfaceAndGetNormalsOnProjectedPoints(fileName, cloud, projectedCloudWithNormals);

	numberOfPoints = projectedCloudWithNormals->points.size();
	MatrixXd MatrixXYZ;// (3, numberOfPoints);
	MatrixXd MatrixNormals;// (3, numberOfPoints);

	MatrixXd MatrixXYZ_tmp(3, numberOfPoints);
	MatrixXd MatrixNormals_tmp(3, numberOfPoints);

	float sumNX = 0, sumNY = 0, sumNZ = 0;

	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		sumNX = sumNX + projectedCloudWithNormals->points[i].normal_x;
		sumNY = sumNY + projectedCloudWithNormals->points[i].normal_y;
		sumNZ = sumNZ + projectedCloudWithNormals->points[i].normal_z;
	}
	Eigen::Vector3f avgDirectionBreaklines(sumNX / numberOfPoints, sumNY / numberOfPoints, sumNZ / numberOfPoints);
	double angle = pcl::getAngle3D(avgNormalDirection, avgDirectionBreaklines, true);
	if (angle <= 90 && angle >= -90)
	{
		for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
		{
			MatrixXYZ_tmp(0, i) = projectedCloudWithNormals->points[i].x;
			MatrixXYZ_tmp(1, i) = projectedCloudWithNormals->points[i].y;
			MatrixXYZ_tmp(2, i) = projectedCloudWithNormals->points[i].z;
			MatrixNormals_tmp(0, i) = projectedCloudWithNormals->points[i].normal_x;
			MatrixNormals_tmp(1, i) = projectedCloudWithNormals->points[i].normal_y;
			MatrixNormals_tmp(2, i) = projectedCloudWithNormals->points[i].normal_z;
		}
	}
	else
	{
		for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
		{
			MatrixXYZ_tmp(0, i) = projectedCloudWithNormals->points[i].x;
			MatrixXYZ_tmp(1, i) = projectedCloudWithNormals->points[i].y;
			MatrixXYZ_tmp(2, i) = projectedCloudWithNormals->points[i].z;
			MatrixNormals_tmp(0, i) = projectedCloudWithNormals->points[i].normal_x * -1;
			MatrixNormals_tmp(1, i) = projectedCloudWithNormals->points[i].normal_y * -1;
			MatrixNormals_tmp(2, i) = projectedCloudWithNormals->points[i].normal_z * -1;
		}
	}
	if (MatrixXYZ_tmp.cols() != 3 && MatrixXYZ_tmp.rows() == 3)
	{
		MatrixXYZ = MatrixXYZ_tmp.transpose();
	}
	else
	{
		MatrixXYZ = MatrixXYZ_tmp;
	}
	if (MatrixNormals_tmp.cols() != 3 && MatrixNormals_tmp.rows() == 3)
	{
		MatrixNormals = MatrixNormals_tmp.transpose();
	}
	else
	{
		MatrixNormals = MatrixNormals_tmp;
	}
	// Rearrange the breakline to countclockwise 
	Matrix_Rearrange(MatrixXYZ, MatrixNormals);

	numberOfPoints = projectedCloudWithNormals->points.size();
	MatrixXd ProjectedMatrix(numberOfPoints, 6);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		ProjectedMatrix(i, 0) = MatrixXYZ(i, 0);
		ProjectedMatrix(i, 1) = MatrixXYZ(i, 1);
		ProjectedMatrix(i, 2) = MatrixXYZ(i, 2);
		ProjectedMatrix(i, 3) = MatrixNormals(i, 0);
		ProjectedMatrix(i, 4) = MatrixNormals(i, 1);
		ProjectedMatrix(i, 5) = MatrixNormals(i, 2);;
	}
	writeMatrix_to_XYZ(ProjectedMatrix, tempEdgeFolder + "CompleteBreakline.xyz", 6);
	
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_New(new pcl::PointCloud<pcl::PointNormal>);
	cloud_New->width = ProjectedMatrix.rows();
	cloud_New->height = 1;
	cloud_New->is_dense = false;
	cloud_New->points.resize(cloud_New->width * cloud_New->height);

	for (size_t i = 0; i < ProjectedMatrix.rows(); i++)
	{
		cloud_New->points[i].x = ProjectedMatrix(i, 0);
		cloud_New->points[i].y = ProjectedMatrix(i, 1);
		cloud_New->points[i].z = ProjectedMatrix(i, 2);
		cloud_New->points[i].normal_x = ProjectedMatrix(i, 3);
		cloud_New->points[i].normal_y = ProjectedMatrix(i, 4);
		cloud_New->points[i].normal_z = ProjectedMatrix(i, 5);
	}

	pcl::io::savePCDFile(tempEdgeFolder + "CompleteBreakline.pcd", *cloud);
}

void cleanSamples(string pointCloudDataFile)
{

	string line;
	double d1;
	double d2;
	double d3;
	stringstream ss;
	ifstream myfile(pointCloudDataFile);
	std::vector<std::string> fileContents;
	std::string str;
	std::string file_contents;
	int numberOfPoints;


	//Reading file contents
	while (std::getline(myfile, str))
	{
		fileContents.push_back(str);
	}

	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_OriginalSurface(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_filteredB(new pcl::PointCloud<pcl::PointNormal>);

	//Constructing the matrix
	numberOfPoints = fileContents.size();

	cloud_OriginalSurface->width = numberOfPoints;
	cloud_OriginalSurface->height = 1;
	cloud_OriginalSurface->is_dense = false;
	cloud_OriginalSurface->points.resize(cloud_OriginalSurface->width * cloud_OriginalSurface->height);
	PointNormal pn;
	MatrixXd T(6, numberOfPoints);
	std::vector<std::string> results;

	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		boost::split(results, fileContents[i], [](char c) {return c == ' '; });

		cloud_OriginalSurface->points[i].x = stof(results[0]);
		cloud_OriginalSurface->points[i].y = stof(results[1]);
		cloud_OriginalSurface->points[i].z = stof(results[2]);
		cloud_OriginalSurface->points[i].normal_x = stof(results[3]);
		cloud_OriginalSurface->points[i].normal_y = stof(results[4]);
		cloud_OriginalSurface->points[i].normal_z = stof(results[5]);

		results.clear();

		ss.str(std::string());
	}
	cloud_OriginalSurface->height = 1;
	cloud_OriginalSurface->width = cloud_OriginalSurface->points.size();

	
	pcl::StatisticalOutlierRemoval<pcl::PointNormal> sor;
	sor.setInputCloud(cloud_OriginalSurface);
	sor.setMeanK(50);
	sor.setStddevMulThresh(9);
	sor.filter(*cloud_filteredB);
	// pcl::io::savePCDFileASCII("cloud_Surface_AllSamples_Cleaned.pcd", *cloud_filteredB);
	pcl::io::savePCDFileASCII(tempEdgeFolder + "cloud_Surface_AllSamples_Cleaned.pcd", *cloud_filteredB);

	float sumNX = 0, sumNY = 0, sumNZ = 0;\

	numberOfPoints = cloud_filteredB->points.size();
	MatrixXd P(numberOfPoints, 6);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		P(i, 0) = cloud_filteredB->points[i].x;
		P(i, 1) = cloud_filteredB->points[i].y;
		P(i, 2) = cloud_filteredB->points[i].z;
		P(i, 3) = cloud_filteredB->points[i].normal_x;
		P(i, 4) = cloud_filteredB->points[i].normal_y;
		P(i, 5) = cloud_filteredB->points[i].normal_z;

		sumNX = sumNX + P(i, 3);
		sumNY = sumNY + P(i, 4);
		sumNZ = sumNZ + P(i, 5);
	}

	avgNormalDirection << sumNX / numberOfPoints, sumNY / numberOfPoints, sumNZ / numberOfPoints;

	string fileName = pointCloudDataFile;
	//getting file name
	const size_t last_slash_idx = pointCloudDataFile.find_last_of("/\\");
	if (std::string::npos != last_slash_idx)
	{
		pointCloudDataFile.erase(0, last_slash_idx + 1);
		pointCloudDataFile.erase(0, last_slash_idx + 1);
	}
	//removing extension
	const size_t period_idx = pointCloudDataFile.rfind('.');
	if (std::string::npos != period_idx)
	{
		pointCloudDataFile.erase(period_idx);
	}

	// string outPath = "pointCloudFromMesh.xyz";
	string outPath = tempEdgeFolder + "pointCloudFromMesh.xyz";

	ofstream myfileWrite;
	myfileWrite.open(outPath);
	for (size_t i = 0; i < P.rows(); i++)
	{
		for (size_t j = 0; j < 6; j++)
		{
			myfileWrite << P(i, j) << " ";
		}
		myfileWrite << endl;
	}
	myfileWrite.close();

	// outPath = pointCloudDataFile + "_Cleaned.xyz";
	outPath = tempEdgeFolder + (pointCloudDataFile + "_Cleaned.xyz");
	myfileWrite.open(outPath);
	for (size_t i = 0; i < P.rows(); i++)
	{
		for (size_t j = 0; j < 6; j++)
		{
			myfileWrite << P(i, j) << " ";
		}
		myfileWrite << endl;
	}
	myfileWrite.close();
}

double getErrorInPlaneFitting(const pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster1)
{
	string line;
	double d1;
	double d2;
	double d3;
	stringstream ss;
	std::string str;
	std::string file_contents;
	int numberOfPoints;

	//Constructing the matrix
	numberOfPoints = cloud_Cluster1->points.size();
	MatrixXd P(3, numberOfPoints);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		P(0, i) = cloud_Cluster1->points[i].x;
		P(1, i) = cloud_Cluster1->points[i].y;
		P(2, i) = cloud_Cluster1->points[i].z;
	}

	//Centring the data about (0,0)
	MatrixXd P_norm(3, numberOfPoints);
	double Px_mean = P.row(0).mean();
	double Py_mean = P.row(1).mean();
	double Pz_mean = P.row(2).mean();
	MatrixXd Center(1, 3);
	Center << Px_mean, Py_mean, Pz_mean;
	for (int i = 0; i < numberOfPoints; i++)
	{
		P_norm(0, i) = P(0, i) - Px_mean;
		P_norm(1, i) = P(1, i) - Py_mean;
		P_norm(2, i) = P(2, i) - Pz_mean;
	}

	//compute covariance
	MatrixXd Cov_P = (P_norm * P_norm.transpose());// / (numberOfPoints - 1);

	//Appying SVD
	JacobiSVD<MatrixXd> svd(Cov_P, ComputeThinU | ComputeThinV);

	MatrixXd EigenValues = svd.singularValues();
	MatrixXd Sigma(3, 3);
	Sigma(0, 0) = EigenValues(0, 0);
	Sigma(1, 1) = EigenValues(1, 0);
	Sigma(2, 2) = EigenValues(2, 0);
	Sigma(0, 1) = Sigma(0, 2) = Sigma(1, 0) = Sigma(1, 2) = Sigma(2, 0) = Sigma(2, 1) = 0;

	MatrixXd U = svd.matrixU();
	MatrixXd V = svd.matrixV();

	//Finding the Rotation matrix which rotates the direction of the least data variance to z-axis [0 0 1]
	MatrixXd R_t(3, 3);
	MatrixXd R(3, 3);
	Vector3d v3 = U.col(2); //the third eigen vector is the last col of U --> which gives the direction of least variance
	Vector3d v1(3);
	Vector3d v2(3);
	Vector3d v1_hash(3); //Initializing a fake V1 to any point
	v1_hash(0, 0) = 1; v1_hash(1, 0) = 0; v1_hash(2, 0) = 0;

	Vector3d x_vector = v1_hash - ((v1_hash.dot(v3)) * v3);
	v1 = x_vector / x_vector.norm();
	v2 = v3.cross(v1);

	R_t.col(0) = v1;
	R_t.col(1) = v2;
	R_t.col(2) = v3;
	R = R_t.transpose();

	MatrixXd Q(3, numberOfPoints);
	Q = R * P_norm;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_Cluster1_Rotated(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < numberOfPoints; i++)
	{
		cloud_Cluster1_Rotated->points.push_back(pcl::PointXYZ(Q(0, i), Q(1, i), Q(2, i)));
	}
	cloud_Cluster1_Rotated->height = 1;
	cloud_Cluster1_Rotated->width = cloud_Cluster1_Rotated->points.size();

	double avgZValue = 0, sum = 0;
	for (size_t t = 0; t < cloud_Cluster1_Rotated->points.size(); t++)
	{
		sum += cloud_Cluster1_Rotated->points[t].z;
	}
	avgZValue = sum / cloud_Cluster1_Rotated->points.size();

	double sumsOfError = 0;
	for (size_t i = 0; i < cloud_Cluster1_Rotated->points.size(); i++)
	{
		sumsOfError = sumsOfError + std::pow((avgZValue - cloud_Cluster1_Rotated->points[i].z), 2);
	}
	return std::sqrt(sumsOfError / cloud_Cluster1_Rotated->points.size());
	//-----------------------------------------------------------------------
}

void clusteringOnNormals(const pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointNormalsNearBreaklineSeg, double& CV_C1, double& CV_C2, string fragSegPieceNo)
{
    // Guard against undersized inputs to k-means
    if (!cloud_PointNormalsNearBreaklineSeg || cloud_PointNormalsNearBreaklineSeg->points.size() < 10) {
        CV_C1 = 0; CV_C2 = 0;
        std::cerr << "[EDGELINE DEBUG] clusteringOnNormals: too few points (" << (cloud_PointNormalsNearBreaklineSeg?cloud_PointNormalsNearBreaklineSeg->points.size():0) << "), skipping." << std::endl;
        return;
    }
	int k = 2; //number of clusters used

	//1. run kmeans clustering on face normals
	double* normal_mat = static_cast<double*>(malloc(sizeof(double) * 3 * cloud_PointNormalsNearBreaklineSeg->points.size()));
	pcl::PointNormal pnTmp;
	for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
	{
		normal_mat[i * 3] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_x;
		normal_mat[i * 3 + 1] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_y;
		normal_mat[i * 3 + 2] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_z;
	}

	using namespace alglib;
	clusterizerstate s;
	kmeansreport rep;
	real_2d_array normals;
	normals.attach_to_ptr(cloud_PointNormalsNearBreaklineSeg->points.size(), 3, normal_mat);

	clusterizercreate(s);
	clusterizersetpoints(s, normals, 2);
	clusterizersetkmeanslimits(s, 5, 0);
	clusterizerrunkmeans(s, k, rep);

	//printf("%s\n", rep.cidx.tostring().c_str());
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster2(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster3(new pcl::PointCloud<pcl::PointNormal>);
	for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
	{
		if (rep.cidx[i] == 0)
		{
			cloud_Cluster1->points.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
		}
		else if (rep.cidx[i] == 1)
		{
			cloud_Cluster2->points.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
		}
	}
	cloud_Cluster1->width = cloud_Cluster1->points.size();
	cloud_Cluster1->height = 1;
	cloud_Cluster2->width = cloud_Cluster2->points.size();
	cloud_Cluster2->height = 1;

	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster1Filtered(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster2Filtered(new pcl::PointCloud<pcl::PointNormal>);

	MatrixXd normalsCluster1(cloud_Cluster1->points.size(), 3);
	MatrixXd normalsCluster2(cloud_Cluster2->points.size(), 3);

	double sum_x = 0, sum_y = 0, sum_z = 0;
	for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
	{
		sum_x = sum_x + cloud_Cluster1->points[i].normal_x;
		sum_y = sum_y + cloud_Cluster1->points[i].normal_y;
		sum_z = sum_z + cloud_Cluster1->points[i].normal_z;
	}
	pcl::PointNormal cluster1_MeanDirectionOfNormals;
	cluster1_MeanDirectionOfNormals.normal_x = sum_x / cloud_Cluster1->points.size();
	cluster1_MeanDirectionOfNormals.normal_y = sum_y / cloud_Cluster1->points.size();
	cluster1_MeanDirectionOfNormals.normal_z = sum_z / cloud_Cluster1->points.size();

	sum_x = 0; sum_y = 0; sum_z = 0;
	for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
	{
		sum_x = sum_x + cloud_Cluster2->points[i].normal_x;
		sum_y = sum_y + cloud_Cluster2->points[i].normal_y;
		sum_z = sum_z + cloud_Cluster2->points[i].normal_z;
	}
	pcl::PointNormal cluster2_MeanDirectionOfNormals;
	cluster2_MeanDirectionOfNormals.normal_x = sum_x / cloud_Cluster2->points.size();
	cluster2_MeanDirectionOfNormals.normal_y = sum_y / cloud_Cluster2->points.size();
	cluster2_MeanDirectionOfNormals.normal_z = sum_z / cloud_Cluster2->points.size();

	Eigen::Vector3f cluster1_MeanNormalDirection(cluster1_MeanDirectionOfNormals.normal_x, cluster1_MeanDirectionOfNormals.normal_y, cluster1_MeanDirectionOfNormals.normal_z);
	Eigen::Vector3f cluster2_MeanNormalDirection(cluster2_MeanDirectionOfNormals.normal_x, cluster2_MeanDirectionOfNormals.normal_y, cluster2_MeanDirectionOfNormals.normal_z);

	Eigen::Vector3f tmpVec;
	vector<double> angleCluster1;
	double angle = 0;
	for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
	{
		tmpVec << cloud_Cluster1->points[i].normal_x, cloud_Cluster1->points[i].normal_y, cloud_Cluster1->points[i].normal_z;
		angle = pcl::getAngle3D(tmpVec, cluster1_MeanNormalDirection, true);
		if (angle <= 90 && angle >= -90)
		{
			angleCluster1.push_back(angle);
			cloud_Cluster1Filtered->points.push_back(cloud_Cluster1->points[i]);
		}
	}
	cloud_Cluster1Filtered->width = cloud_Cluster1Filtered->points.size();
	cloud_Cluster1Filtered->height = 1;

	double sumC1 = std::accumulate(angleCluster1.begin(), angleCluster1.end(), 0.0);
	double meanC1 = sumC1 / angleCluster1.size();
	std::transform(angleCluster1.begin(), angleCluster1.end(), angleCluster1.begin(), [meanC1](double x) { return x - meanC1; });
	double sq_sumC1 = std::inner_product(angleCluster1.begin(), angleCluster1.end(), angleCluster1.begin(), 0.0);
	double stdC1 = std::sqrt(sq_sumC1 / angleCluster1.size());
	CV_C1 = stdC1 / meanC1;


	vector<double> angleCluster2;
	for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
	{
		tmpVec << cloud_Cluster2->points[i].normal_x, cloud_Cluster2->points[i].normal_y, cloud_Cluster2->points[i].normal_z;
		angle = pcl::getAngle3D(tmpVec, cluster2_MeanNormalDirection, true);
		if (angle <= 90 && angle >= -90)
		{
			angleCluster2.push_back(angle);
			cloud_Cluster2Filtered->points.push_back(cloud_Cluster2->points[i]);
		}
	}
	cloud_Cluster2Filtered->width = cloud_Cluster2Filtered->points.size();
	cloud_Cluster2Filtered->height = 1;

	double sumC2 = std::accumulate(angleCluster2.begin(), angleCluster2.end(), 0.0);
	double meanC2 = sumC2 / angleCluster2.size();
	std::transform(angleCluster2.begin(), angleCluster2.end(), angleCluster2.begin(), [meanC2](double x) { return x - meanC2; });
	double sq_sumC2 = std::inner_product(angleCluster2.begin(), angleCluster2.end(), angleCluster2.begin(), 0.0);
	double stdC2 = std::sqrt(sq_sumC2 / angleCluster2.size());
	CV_C2 = stdC2 / meanC2;

	CV_C1 = getErrorInPlaneFitting(cloud_Cluster1Filtered);
	CV_C2 = getErrorInPlaneFitting(cloud_Cluster2Filtered);
}
void clusteringOnNormalsForDetectingFracturedSurfacePts(const pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointNormalsNearBreaklineSeg, string fragSegPieceNo, pcl::PointCloud<pcl::PointNormal>::Ptr cloud_DetectedPointsOnSurface, pcl::PointCloud<pcl::PointNormal>::Ptr cloud_DetectedPointsOnIntExtSurface)
{
    // Guard against undersized inputs to k-means
    if (!cloud_PointNormalsNearBreaklineSeg || cloud_PointNormalsNearBreaklineSeg->points.size() < 10) {
        std::cerr << "[EDGELINE DEBUG] clusteringOnNormalsForDetectingFracturedSurfacePts: too few points, skipping." << std::endl;
        if (cloud_DetectedPointsOnSurface) cloud_DetectedPointsOnSurface->clear();
        if (cloud_DetectedPointsOnIntExtSurface) cloud_DetectedPointsOnIntExtSurface->clear();
        return;
    }
	int k = 3; //number of clusters used

	//1. run kmeans clustering on face normals
	double* normal_mat = static_cast<double*>(malloc(sizeof(double) * 3 * cloud_PointNormalsNearBreaklineSeg->points.size()));
	pcl::PointNormal pnTmp;
	for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
	{
		normal_mat[i * 3] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_x;
		normal_mat[i * 3 + 1] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_y;
		normal_mat[i * 3 + 2] = cloud_PointNormalsNearBreaklineSeg->points[i].normal_z;
	}

	using namespace alglib;
	clusterizerstate s;
	kmeansreport rep;
	real_2d_array normals;
	normals.attach_to_ptr(cloud_PointNormalsNearBreaklineSeg->points.size(), 3, normal_mat);

	clusterizercreate(s);
	clusterizersetpoints(s, normals, 2);
	clusterizersetkmeanslimits(s, 5, 0);
	clusterizerrunkmeans(s, k, rep);

	//printf("%s\n", rep.cidx.tostring().c_str());
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster1(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster2(new pcl::PointCloud<pcl::PointNormal>);
	pcl::PointCloud<pcl::PointNormal>::Ptr cloud_Cluster3(new pcl::PointCloud<pcl::PointNormal>);
	for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
	{
		if (rep.cidx[i] == 0)
		{
			cloud_Cluster1->points.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
		}
		else if (rep.cidx[i] == 1)
		{
			cloud_Cluster2->points.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
		}
		else if (rep.cidx[i] == 2)
		{
			cloud_Cluster3->points.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
		}
		//cout << i << " " << rep.cidx[i] << endl;
	}
	cloud_Cluster1->width = cloud_Cluster1->points.size();
	cloud_Cluster1->height = 1;
	cloud_Cluster2->width = cloud_Cluster2->points.size();
	cloud_Cluster2->height = 1;
	cloud_Cluster3->width = cloud_Cluster3->points.size();
	cloud_Cluster3->height = 1;

	double xn_sum = 0, yn_sum = 0, zn_sum = 0;
	double xn_avg = 0, yn_avg = 0, zn_avg = 0;
	for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
	{
		xn_sum = xn_sum + cloud_Cluster1->points[i].normal_x;
		yn_sum = yn_sum + cloud_Cluster1->points[i].normal_y;
		zn_sum = zn_sum + cloud_Cluster1->points[i].normal_z;
	}
	xn_avg = xn_sum / cloud_Cluster1->points.size();
	yn_avg = yn_sum / cloud_Cluster2->points.size();
	zn_avg = zn_sum / cloud_Cluster3->points.size();
	Eigen::Vector3f Cluster1_AvgNormal = Eigen::Vector3f(xn_avg, yn_avg, zn_avg);

	xn_sum = 0, yn_sum = 0, zn_sum = 0;
	xn_avg = 0, yn_avg = 0, zn_avg = 0;
	for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
	{
		xn_sum = xn_sum + cloud_Cluster2->points[i].normal_x;
		yn_sum = yn_sum + cloud_Cluster2->points[i].normal_y;
		zn_sum = zn_sum + cloud_Cluster2->points[i].normal_z;
	}
	xn_avg = xn_sum / cloud_Cluster2->points.size();
	yn_avg = yn_sum / cloud_Cluster2->points.size();
	zn_avg = zn_sum / cloud_Cluster3->points.size();
	Eigen::Vector3f Cluster2_AvgNormal = Eigen::Vector3f(xn_avg, yn_avg, zn_avg);

	xn_sum = 0, yn_sum = 0, zn_sum = 0;
	xn_avg = 0, yn_avg = 0, zn_avg = 0;
	for (size_t i = 0; i < cloud_Cluster3->points.size(); i++)
	{
		xn_sum = xn_sum + cloud_Cluster3->points[i].normal_x;
		yn_sum = yn_sum + cloud_Cluster3->points[i].normal_y;
		zn_sum = zn_sum + cloud_Cluster3->points[i].normal_z;
	}
	xn_avg = xn_sum / cloud_Cluster3->points.size();
	yn_avg = yn_sum / cloud_Cluster2->points.size();
	zn_avg = zn_sum / cloud_Cluster3->points.size();
	Eigen::Vector3f Cluster3_AvgNormal = Eigen::Vector3f(xn_avg, yn_avg, zn_avg);

	double angle12 = pcl::getAngle3D(Cluster1_AvgNormal, Cluster2_AvgNormal, true);
	double angle13 = pcl::getAngle3D(Cluster1_AvgNormal, Cluster3_AvgNormal, true);
	double angle23 = pcl::getAngle3D(Cluster2_AvgNormal, Cluster3_AvgNormal, true);

	if (max(angle12, max(angle13, angle23)) == angle12)
	{
		for (size_t i = 0; i < cloud_Cluster3->points.size(); i++)
		{
			cloud_DetectedPointsOnSurface->points.push_back(cloud_Cluster3->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster1->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster2->points[i]);
		}

	}
	else if (max(angle12, max(angle13, angle23)) == angle13)
	{
		for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
		{
			cloud_DetectedPointsOnSurface->points.push_back(cloud_Cluster2->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster1->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster3->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster3->points[i]);
		}
		//pcl::io::savePLYFile(fragSegPieceNo + "FracSurfPts.ply", *cloud_Cluster2);
	}
	else if (max(angle12, max(angle13, angle23)) == angle23)
	{
		for (size_t i = 0; i < cloud_Cluster1->points.size(); i++)
		{
			cloud_DetectedPointsOnSurface->points.push_back(cloud_Cluster1->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster2->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster2->points[i]);
		}
		for (size_t i = 0; i < cloud_Cluster3->points.size(); i++)
		{
			cloud_DetectedPointsOnIntExtSurface->points.push_back(cloud_Cluster3->points[i]);
		}
	}
}

bool isBreaklineSegARim(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BreakLineSeg, string sampledDataWithNormals, int segNo)
{
    pcl::PointCloud<PointNormal>::Ptr cloud_PointNormals(new pcl::PointCloud<PointNormal>);
    if (!load_ply_pointnormals_robust(sampledDataWithNormals, cloud_PointNormals) || cloud_PointNormals->empty()) {
        std::cerr << "Warning: Failed to load normals from " << sampledDataWithNormals << ", trying cleaned surface..." << std::endl;
        if (!load_pointnormals_from_cleaned_surface(cloud_PointNormals)) {
            std::cerr << "Warning: No normals available; skipping rim detection for seg " << segNo << std::endl;
            return false;
        }
    }
    if (cloud_PointNormals->size() < 10) {
        std::cerr << "[EDGELINE DEBUG] Normals cloud too small (" << cloud_PointNormals->size() << ") for rim detection; defaulting to not-rim." << std::endl;
        return false;
    }

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloudPointsOnly(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < cloud_PointNormals->points.size(); i++)
	{
		cloudPointsOnly->points.push_back(PointXYZ(cloud_PointNormals->points[i].x, cloud_PointNormals->points[i].y, cloud_PointNormals->points[i].z));
	}
	cloudPointsOnly->width = cloudPointsOnly->points.size();
	cloudPointsOnly->height = 1;

	pcl::PointXYZ searchPoint;


	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_PointsNearBreaklineSeg(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<PointNormal>::Ptr cloud_PointNormalsNearBreaklineSeg(new pcl::PointCloud<PointNormal>);
	vector<int> indices_PointsNearBreaklineSeg;
	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(cloudPointsOnly);
	float radius = 3;// 6;
	vector<int> all_Indices;

	// SAFETY: Rim detection requires at least 10 points (skip first/last 3 → need 4+ remaining)
	// After clipping: size - 6 must be >= 4 for meaningful rim detection
	if (cloud_BreakLineSeg->points.size() < 10) {
		std::cerr << "[RIM DETECTION SAFETY] Segment too small (" << cloud_BreakLineSeg->points.size()
		          << " points < 10 required for rim detection), defaulting to not-rim for seg " << segNo << std::endl;
		return false;
	}

	//skipping first and last three points from the breakline and splitting the rest in peices of 5 points each
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_ClippedBreakLineSeg(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 3; i < cloud_BreakLineSeg->points.size() - 3; i++)
	{
		cloud_ClippedBreakLineSeg->points.push_back(cloud_BreakLineSeg->points[i]);
	}
	cloud_ClippedBreakLineSeg->width = cloud_ClippedBreakLineSeg->points.size();
	cloud_ClippedBreakLineSeg->height = 1;

	int lengthOfEachPiece = 1;
	int startIndex = 0, endIndex = 0;
	int totalPointsForSplitting = cloud_ClippedBreakLineSeg->points.size();
	int noOfFullPieces = totalPointsForSplitting / lengthOfEachPiece;

	vector<double> CV_C1;
	vector<double> CV_C2;

	for (size_t p = 0; p < noOfFullPieces; p++)
	{
		startIndex = p * lengthOfEachPiece;
		endIndex = startIndex + lengthOfEachPiece;
		all_Indices.clear();
		cloud_PointsNearBreaklineSeg->points.clear();
		cloud_PointNormalsNearBreaklineSeg->points.clear();

		for (size_t i = startIndex; i < endIndex; i++)
		{
			searchPoint = cloud_ClippedBreakLineSeg->points[i];

			std::vector<int> pointIdxRadiusSearch;
			std::vector<float> pointRadiusSquaredDistance;



			if (kdtree.radiusSearch(searchPoint, radius, pointIdxRadiusSearch, pointRadiusSquaredDistance) > 0)
			{
				for (size_t i = 0; i < pointIdxRadiusSearch.size(); ++i)
				{
					all_Indices.push_back(pointIdxRadiusSearch[i]);
				}
			}
		}

		if (all_Indices.size() > 0)
		{
			// Sort and remove duplicate indices
			std::sort(all_Indices.begin(), all_Indices.end());
			all_Indices.erase(std::unique(all_Indices.begin(), all_Indices.end()), all_Indices.end());

			PointNormal pn;

			for (size_t i = 0; i < all_Indices.size(); i++)
			{
				cloud_PointsNearBreaklineSeg->points.push_back(cloudPointsOnly->points[all_Indices[i]]);
				indices_PointsNearBreaklineSeg.push_back(all_Indices[i]);
				pn.x = cloud_PointNormals->points[all_Indices[i]].x;
				pn.y = cloud_PointNormals->points[all_Indices[i]].y;
				pn.z = cloud_PointNormals->points[all_Indices[i]].z;
				pn.normal_x = cloud_PointNormals->points[all_Indices[i]].normal_x;
				pn.normal_y = cloud_PointNormals->points[all_Indices[i]].normal_y;
				pn.normal_z = cloud_PointNormals->points[all_Indices[i]].normal_z;
				cloud_PointNormalsNearBreaklineSeg->points.push_back(pn);
			}

			cloud_PointNormalsNearBreaklineSeg->width = cloud_PointNormalsNearBreaklineSeg->points.size();
			cloud_PointNormalsNearBreaklineSeg->height = 1;


			pcl::PointCloud<PointNormal>::Ptr cloud_FilteredPointNormalsNearBreaklineSeg(new pcl::PointCloud<PointNormal>);
			std::vector<PointNormal> vectorPointNormal;
			for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
			{
				vectorPointNormal.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
			}
			std::sort(vectorPointNormal.begin(), vectorPointNormal.end(), myobject2);


			for (size_t i = 0; i < vectorPointNormal.size() - 1; i++)
			{
				if ((vectorPointNormal[i].x == vectorPointNormal[i + 1].x) && (vectorPointNormal[i].y == vectorPointNormal[i + 1].y) && (vectorPointNormal[i].z == vectorPointNormal[i + 1].z))
				{

				}
				else
				{
					cloud_FilteredPointNormalsNearBreaklineSeg->points.push_back(vectorPointNormal[i]);
				}
			}
			cloud_FilteredPointNormalsNearBreaklineSeg->width = cloud_FilteredPointNormalsNearBreaklineSeg->points.size();
			cloud_FilteredPointNormalsNearBreaklineSeg->height = 1;
			double CV1 = 0, CV2 = 0;
			if (cloud_FilteredPointNormalsNearBreaklineSeg->points.size() >= 10)
			{
				clusteringOnNormals(cloud_FilteredPointNormalsNearBreaklineSeg, CV1, CV2, sampledDataWithNormals + "_" + to_string(segNo) + "_Piece" + to_string(p));
			}
			CV_C1.push_back(CV1);
			CV_C2.push_back(CV2);
		}
	}

	// SAFETY: Check if CV vectors are empty (happens when no nearby points found in any iteration)
	if (CV_C1.empty() || CV_C2.empty()) {
		std::cerr << "[RIM DETECTION SAFETY] No curvature values computed (CV vectors empty), defaulting to not-rim for seg " << segNo << std::endl;
		return false;
	}

	double sumCV_C1 = std::accumulate(CV_C1.begin(), CV_C1.end(), 0.0);
	double meanCV_C1 = sumCV_C1 / CV_C1.size();

	double sumCV_C2 = std::accumulate(CV_C2.begin(), CV_C2.end(), 0.0);
	double meanCV_C2 = sumCV_C2 / CV_C2.size();
	cout << "C1 " << meanCV_C1;
	cout << " C2 " << meanCV_C2 << endl;

	cout << "Mean = " << (meanCV_C1 + meanCV_C2) / 2 << endl;;

	if (((meanCV_C1 + meanCV_C2) / 2) > 0.12) //0.0992 for pot 3
	{
		return true; //rim
	}

	return false; //not a rim
}

tuple<MatrixXd, MatrixXd> readFileXYZ_WithNormals(string fileName)
{
	stringstream ss;
	ifstream myfile(fileName);
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
	MatrixXd P(3, numberOfPoints);
	MatrixXd N(3, numberOfPoints);
	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		ss << fileContents[i];
		ss >> P(0, i);
		ss >> P(1, i);
		ss >> P(2, i);
		ss >> N(0, i);
		ss >> N(1, i);
		ss >> N(2, i);
		ss.str(std::string());
	}

	return make_tuple(P.transpose(), N.transpose());
}


MatrixXd getDistFromAxis(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BreakLineSeg, string b1_axisFilePath)
{
	int numberOfPoints = cloud_BreakLineSeg->points.size();
	MatrixXd b1(3, numberOfPoints);

	for (int i = 0; i < numberOfPoints; i++) //points.size(); i++)
	{
		b1(0, i) = cloud_BreakLineSeg->points[i].x;
		b1(1, i) = cloud_BreakLineSeg->points[i].y;
		b1(2, i) = cloud_BreakLineSeg->points[i].z;
	}

    b1.transposeInPlace();

	MatrixXd ptTmp, diTmp;
	tie(ptTmp, diTmp) = readFileXYZ_WithNormals(b1_axisFilePath); 
	Vector3d axisB1Pt1(ptTmp(0, 0), ptTmp(0, 1), ptTmp(0, 2));
	Vector3d axisB1Direction(diTmp(0, 0), diTmp(0, 1), diTmp(0, 2));
	MatrixXd distFromBreakLinesToAxisB1(b1.rows(), 1);
	Vector3d v(3), P(3), tmp(3);
	double t = 0;
	for (int i = 0; i < b1.rows(); i++)
	{
		tmp(0) = b1(i, 0);
		tmp(1) = b1(i, 1);
		tmp(2) = b1(i, 2);
		v = tmp - axisB1Pt1;
		t = v.dot(axisB1Direction);
		P = axisB1Pt1 + t * axisB1Direction;
		distFromBreakLinesToAxisB1(i, 0) = (P - tmp).norm();
	}
	return distFromBreakLinesToAxisB1;
}

double isBreaklineSegARim_DistanceFromAxis(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BreakLineSeg, int segNo)
{
	std::string baseFileName = currentMeshFile.substr(0, currentMeshFile.find("_Mesh"));
	std::string axisFileName = baseFileName + "_Axis.xyz";
	std::string axisFilePath = "Dataset/Axes/" + axisFileName;  // Fixed: Use container-compatible path
	std::cerr << "[DEBUG AXIS PATH] Using axis file: " << axisFilePath << std::endl;
	MatrixXd distFromAxis = getDistFromAxis(cloud_BreakLineSeg, axisFilePath);


	std::vector<double> dist;
	for (size_t i = 0; i < distFromAxis.rows(); i++)
	{
		dist.push_back(distFromAxis(i, 0));
	}

	double sum = std::accumulate(dist.begin(), dist.end(), 0.0);
	double mean = sum / dist.size();

	std::vector<double> diff(dist.size());
	std::transform(dist.begin(), dist.end(), diff.begin(),
		std::bind2nd(std::minus<double>(), mean));
	double sq_sum = std::inner_product(diff.begin(), diff.end(), diff.begin(), 0.0);
	double stdev = std::sqrt(sq_sum / dist.size());

	cout << "Seg. " << segNo << " stdev: " << stdev << endl;
	return stdev;

}

void getPointsOnFracturedSurface(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BreakLineSeg, string fragmentMeshFile, string sampledDataWithNormals, int segNo, pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointsOnFracturedSurface, pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointsOnIntExtSurface)
{
	//using all points from mesh
	std::string inputfile = fragmentMeshFile;// "18-0702-03-05.obj";
	tinyobj::attrib_t attrib;
	std::vector<tinyobj::shape_t> shapes;
	std::vector<tinyobj::material_t> materials;

	std::string warn;
	std::string err;
	bool ret = tinyobj::LoadObj(&attrib, &shapes, &materials, &warn, &err, inputfile.c_str());

	if (!err.empty()) { // `err` may contain warning message.
		std::cerr << err << std::endl;
	}

	if (!ret) {
		exit(1);
	}

	//getting pointcloud from the vertices in the mesh
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_FromMeshIndices(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PointCloud<PointNormal>::Ptr cloud_PointNormals(new pcl::PointCloud<PointNormal>);
    if (!load_ply_pointnormals_robust(sampledDataWithNormals, cloud_PointNormals) || cloud_PointNormals->empty()) {
        std::cerr << "Warning: Failed to load normals from " << sampledDataWithNormals << ", fractured surface estimation may be degraded." << std::endl;
        return; // cannot proceed safely
    }

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloudPointsOnly(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < cloud_PointNormals->points.size(); i++)
	{
		cloudPointsOnly->points.push_back(PointXYZ(cloud_PointNormals->points[i].x, cloud_PointNormals->points[i].y, cloud_PointNormals->points[i].z));
	}
	cloudPointsOnly->width = cloudPointsOnly->points.size();
	cloudPointsOnly->height = 1;


	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_PointsNearBreaklineSeg(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<PointNormal>::Ptr cloud_PointNormalsNearBreaklineSeg(new pcl::PointCloud<PointNormal>);
	vector<int> indices_PointsNearBreaklineSeg;
	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(cloudPointsOnly);
	float radius = 3;
	vector<int> all_Indices;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_ClippedBreakLineSeg(new pcl::PointCloud<pcl::PointXYZ>);
	for (size_t i = 0; i < cloud_BreakLineSeg->points.size(); i++)
	{
		cloud_ClippedBreakLineSeg->points.push_back(cloud_BreakLineSeg->points[i]);
	}
	cloud_ClippedBreakLineSeg->width = cloud_ClippedBreakLineSeg->points.size();
	cloud_ClippedBreakLineSeg->height = 1;

	int lengthOfEachPiece = 1;
	int startIndex = 0, endIndex = 0;
	int totalPointsForSplitting = cloud_ClippedBreakLineSeg->points.size();
	int noOfFullPieces = totalPointsForSplitting / lengthOfEachPiece;

	vector<double> CV_C1;
	vector<double> CV_C2;
	pcl::PointXYZ searchPoint;
	for (size_t p = 0; p < noOfFullPieces; p++)
	{
		startIndex = p * lengthOfEachPiece;
		endIndex = startIndex + lengthOfEachPiece;
		all_Indices.clear();
		cloud_PointsNearBreaklineSeg->points.clear();
		cloud_PointNormalsNearBreaklineSeg->points.clear();

		for (size_t i = startIndex; i < endIndex; i++)
		{
			searchPoint = cloud_ClippedBreakLineSeg->points[i];

			std::vector<int> pointIdxRadiusSearch;
			std::vector<float> pointRadiusSquaredDistance;


			if (kdtree.radiusSearch(searchPoint, radius, pointIdxRadiusSearch, pointRadiusSquaredDistance) > 0)
			{
				for (size_t i = 0; i < pointIdxRadiusSearch.size(); ++i)
				{
					all_Indices.push_back(pointIdxRadiusSearch[i]);
				}
			}
		}

		if (all_Indices.size() > 5)
		{

			// Sort and remove duplicate indices
			std::sort(all_Indices.begin(), all_Indices.end());
			all_Indices.erase(std::unique(all_Indices.begin(), all_Indices.end()), all_Indices.end());

			PointNormal pn;

			for (size_t i = 0; i < all_Indices.size(); i++)
			{
				cloud_PointsNearBreaklineSeg->points.push_back(cloudPointsOnly->points[all_Indices[i]]);
				indices_PointsNearBreaklineSeg.push_back(all_Indices[i]);
				pn.x = cloud_PointNormals->points[all_Indices[i]].x;
				pn.y = cloud_PointNormals->points[all_Indices[i]].y;
				pn.z = cloud_PointNormals->points[all_Indices[i]].z;
				pn.normal_x = cloud_PointNormals->points[all_Indices[i]].normal_x;
				pn.normal_y = cloud_PointNormals->points[all_Indices[i]].normal_y;
				pn.normal_z = cloud_PointNormals->points[all_Indices[i]].normal_z;
				cloud_PointNormalsNearBreaklineSeg->points.push_back(pn);
			}

			cloud_PointNormalsNearBreaklineSeg->width = cloud_PointNormalsNearBreaklineSeg->points.size();
			cloud_PointNormalsNearBreaklineSeg->height = 1;


			pcl::PointCloud<PointNormal>::Ptr cloud_FilteredPointNormalsNearBreaklineSeg(new pcl::PointCloud<PointNormal>);
			std::vector<PointNormal> vectorPointNormal;
			for (size_t i = 0; i < cloud_PointNormalsNearBreaklineSeg->points.size(); i++)
			{
				vectorPointNormal.push_back(cloud_PointNormalsNearBreaklineSeg->points[i]);
			}
			std::sort(vectorPointNormal.begin(), vectorPointNormal.end(), myobject2);


			for (size_t i = 0; i < vectorPointNormal.size() - 1; i++)
			{
				if ((vectorPointNormal[i].x == vectorPointNormal[i + 1].x) && (vectorPointNormal[i].y == vectorPointNormal[i + 1].y) && (vectorPointNormal[i].z == vectorPointNormal[i + 1].z))
				{

				}
				else
				{
					cloud_FilteredPointNormalsNearBreaklineSeg->points.push_back(vectorPointNormal[i]);
				}
			}
			cloud_FilteredPointNormalsNearBreaklineSeg->width = cloud_FilteredPointNormalsNearBreaklineSeg->points.size();
			cloud_FilteredPointNormalsNearBreaklineSeg->height = 1;

			clusteringOnNormalsForDetectingFracturedSurfacePts(cloud_FilteredPointNormalsNearBreaklineSeg, sampledDataWithNormals + "_" + to_string(segNo) + "_Piece" + to_string(p), cloud_PointsOnFracturedSurface, cloud_PointsOnIntExtSurface);

		}

	}

}

void processFragmentData(string surfacePointCloudFilePath, string fragmentMeshFilePath)
{
    std::cerr << "[EDGELINE DEBUG] processFragmentData surface=" << surfacePointCloudFilePath << " mesh=" << fragmentMeshFilePath << std::endl;
    // -------------------- 파일명 추출 및 전역 변수 갱신 --------------------
    string fileName = surfacePointCloudFilePath;
    const size_t last_slash_idx = fileName.find_last_of("/\\");
    if (std::string::npos != last_slash_idx)
    {
        fileName.erase(0, last_slash_idx + 1);
    }
    const size_t period_idx = fileName.rfind('.');
    if (std::string::npos != period_idx)
    {
        fileName.erase(period_idx);
    }

    string meshFileName = fragmentMeshFilePath;
    const size_t last_slash_idxm = meshFileName.find_last_of("/\\");
    if (std::string::npos != last_slash_idxm)
    {
        meshFileName.erase(0, last_slash_idxm + 1);
    }
    const size_t period_idxm = meshFileName.rfind('.');
    if (std::string::npos != period_idxm)
    {
        meshFileName.erase(period_idxm);
    }

    currentFileName = fileName;
    currentMeshFile = meshFileName;

    cout << "Fragment: " + fragmentMeshFilePath << endl << endl;

    // -------------------- 전처리: 표면 포인트 클라우드 클린업 및 breakline 추출 --------------------
	cout << "Cleaning surface point cloud..." << endl;
    cleanSamples(surfacePointCloudFilePath); // (표면 포인트 클라우드 클린업 함수)
    cout << "Estimating patch normals and breaklines..." << endl;
    estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface(tempEdgeFolder + "pointCloudFromMesh.xyz", false);

    // NOTE: Integration Point #2 REMOVED - densifying CompleteBreakline breaks segment file format
    // Densification at Integration Point #1 (after sphere-marching) is sufficient

    cout << "Detecting separate line segments..." << endl;
    std::vector<int> detectedPeakIndices = detectSeparateLineSegments(tempEdgeFolder + "CompleteBreakline.xyz");
    std::cerr << "[EDGELINE DEBUG] detectedPeakIndices size=" << detectedPeakIndices.size() << std::endl;

    MatrixXd matrix_breakLineSeg;
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_breakLineSeg(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_CompleteBreakline(new pcl::PointCloud<pcl::PointNormal>);

    // -------------------- Rim 검출 및 클러스터 정보 산출 --------------------
    cout << "Detecting rim..." << endl;
    int segCount = 1;

    typedef vector<boost::filesystem::path> vec;
    vec v;  // "Segments" 폴더 내 파일들을 읽음
    boost::filesystem::path p("Segments/");
    copy(boost::filesystem::directory_iterator(p),
         boost::filesystem::directory_iterator(),
         back_inserter(v));
    sort(v.begin(), v.end());  // 정렬
    std::cerr << "[EDGELINE DEBUG] Segments files count=" << v.size() << std::endl;

    vector<string> index;
    int segStartIndex = 1;
    bool atLeastOneSegIsRim = false;
    int totalPtsCounter = 0;
    PointNormal tmpPtN;

    // 축 정보 확인 (Axes 폴더)
    std::string baseFileName = currentMeshFile.substr(0, currentMeshFile.find("_Mesh"));
    std::string axisFileName = baseFileName + "_Axis.xyz";
    std::string axisFilePath = "Dataset/Axes/" + axisFileName;  // Changed for container compatibility
    bool axisInfoAvailable = std::experimental::filesystem::exists(axisFilePath);
    std::cerr << "[EDGELINE DEBUG] axisInfoAvailable=" << axisInfoAvailable << " path=" << axisFilePath << std::endl;

    vector<double> stdDevList;
    for (vec::const_iterator it(v.begin()), it_end(v.end()); it != it_end; ++it)
    {
        string sTmp = (*it).string();
        matrix_breakLineSeg = readFile((*it).string(), 6);

        std::cerr << "[DEBUG MATRIX] Segment file " << sTmp << " matrix dimensions: "
                  << matrix_breakLineSeg.rows() << "x" << matrix_breakLineSeg.cols() << std::endl;

        // SAFETY: Skip empty segment files (filtered out by minimum segment size)
        if (matrix_breakLineSeg.rows() == 0) {
            std::cout << "[SEGMENT FILTER] Skipping empty segment file: " << sTmp << std::endl;
            continue;
        }

        // SAFETY: Verify matrix has 6 columns as expected
        if (matrix_breakLineSeg.cols() < 6) {
            std::cerr << "[FATAL ERROR] Segment file " << sTmp << " has only "
                      << matrix_breakLineSeg.cols() << " columns, expected 6!" << std::endl;
            continue;  // Skip this segment to avoid crash
        }

        cloud_breakLineSeg->points.clear();
        std::cerr << "[DEBUG LOOP] Starting segment processing loop, rows=" << matrix_breakLineSeg.rows()
                  << " cols=" << matrix_breakLineSeg.cols() << std::endl;

        for (size_t i = 0; i < matrix_breakLineSeg.rows() - 1; i++)
        {
            // Bounds check before access
            if (i >= matrix_breakLineSeg.rows() || i < 0) {
                std::cerr << "[FATAL] Loop index i=" << i << " out of bounds for matrix with "
                          << matrix_breakLineSeg.rows() << " rows!" << std::endl;
                break;
            }

            std::cerr << "[DEBUG ACCESS] i=" << i << " accessing row " << i << " of "
                      << matrix_breakLineSeg.rows() << "x" << matrix_breakLineSeg.cols() << " matrix" << std::endl;

            cloud_breakLineSeg->points.push_back(
                pcl::PointXYZ(matrix_breakLineSeg(i, 0),
                              matrix_breakLineSeg(i, 1),
                              matrix_breakLineSeg(i, 2)));
            tmpPtN.x = matrix_breakLineSeg(i, 0);
            tmpPtN.y = matrix_breakLineSeg(i, 1);
            tmpPtN.z = matrix_breakLineSeg(i, 2);

            std::cerr << "[DEBUG ACCESS] Accessing normals at i=" << i << std::endl;
            tmpPtN.normal_x = matrix_breakLineSeg(i, 3);
            tmpPtN.normal_y = matrix_breakLineSeg(i, 4);
            tmpPtN.normal_z = matrix_breakLineSeg(i, 5);
            
            // Compute geometric curvature for breakline point
            double curvature = 0.0;
            if (i > 0 && i < matrix_breakLineSeg.rows() - 1) {
                // Use discrete curvature approximation: |dN/ds| where N is normal, s is arc length
                Eigen::Vector3d curr_normal(matrix_breakLineSeg(i, 3), matrix_breakLineSeg(i, 4), matrix_breakLineSeg(i, 5));
                Eigen::Vector3d prev_normal(matrix_breakLineSeg(i-1, 3), matrix_breakLineSeg(i-1, 4), matrix_breakLineSeg(i-1, 5));
                Eigen::Vector3d next_normal(matrix_breakLineSeg(i+1, 3), matrix_breakLineSeg(i+1, 4), matrix_breakLineSeg(i+1, 5));
                
                Eigen::Vector3d curr_pos(matrix_breakLineSeg(i, 0), matrix_breakLineSeg(i, 1), matrix_breakLineSeg(i, 2));
                Eigen::Vector3d prev_pos(matrix_breakLineSeg(i-1, 0), matrix_breakLineSeg(i-1, 1), matrix_breakLineSeg(i-1, 2));
                Eigen::Vector3d next_pos(matrix_breakLineSeg(i+1, 0), matrix_breakLineSeg(i+1, 1), matrix_breakLineSeg(i+1, 2));
                
                // Central difference for normal derivative
                Eigen::Vector3d normal_diff = (next_normal - prev_normal);
                double arc_length = (next_pos - prev_pos).norm();
                
                if (arc_length > 1e-6) {
                    curvature = normal_diff.norm() / arc_length;
                }
                
                // Limit curvature to reasonable values
                if (curvature > 1.0) curvature = 1.0;
            } else {
                // For boundary points, use simpler approximation
                curvature = 0.01; // Small default value
            }
            
            tmpPtN.curvature = static_cast<float>(curvature);
            cloud_CompleteBreakline->points.push_back(tmpPtN);
            totalPtsCounter++;
        }
        cloud_breakLineSeg->width = cloud_breakLineSeg->points.size();
        cloud_breakLineSeg->height = 1;

        std::experimental::filesystem::path filePathTemp = { fragmentMeshFilePath };
        string fileNameOnly = filePathTemp.stem().string().substr(0, 14);
        // 임시 outPath는 "../Dataset/"로 지정 (향후 Surfaces 폴더 등으로 옮길 수 있음)
        string outPath = tempDataPath(potID);	
        bool isRim = isBreaklineSegARim(cloud_breakLineSeg, outPath + fileNameOnly + "_SampledWithNormals.ply", segCount);
        if (axisInfoAvailable)
        {
            double stdev = isBreaklineSegARim_DistanceFromAxis(cloud_breakLineSeg, segCount);
            stdDevList.push_back(stdev);
        }
        index.push_back(to_string(segStartIndex) + " " + to_string(totalPtsCounter) + " " + (isRim ? "1" : "0"));
        segStartIndex = totalPtsCounter + 1;
        segCount++;
    }
    cloud_CompleteBreakline->width = cloud_CompleteBreakline->points.size();
    cloud_CompleteBreakline->height = 1;

    if (axisInfoAvailable)
    {
        cout << "Axis information is available." << endl;
        double sum = std::accumulate(stdDevList.begin(), stdDevList.end(), 0.0);
        double mean = sum / stdDevList.size();
        for (size_t q = 0; q < stdDevList.size(); q++)
        {
            if (100 * stdDevList[q] / mean < 50)
            {
                index[q].pop_back();
                index[q].push_back('1');
                atLeastOneSegIsRim = true;
                cout << "Seg. " << q << " PercentDev= " << (100 * stdDevList[q] / mean) << " => Rim" << endl;
            }
            else
            {
                index[q].pop_back();
                index[q].push_back('0');
                cout << "Seg. " << q << " PercentDev= " << (100 * stdDevList[q] / mean) << " => Not Rim" << endl;
            }
        }
    }
    else
    {
        cout << "Axis information is not available." << endl;
    }
    
    // -------------------- 완성 Breakline 파일 저장 --------------------
    // 원래 currentFileName은 예: "Pot_A_Piece_01_Surface_0" 이었으므로, 이를 "Pot_A_Piece_01_Breakline_0"으로 수정
    string breaklineFileName = currentFileName;
    size_t posSurface = breaklineFileName.find("Surface_0");
    if (posSurface != string::npos)
        breaklineFileName.replace(posSurface, string("Surface_0").length(), "Breakline_0");
    else {
        posSurface = breaklineFileName.find("Surface_1");
        if (posSurface != string::npos)
            breaklineFileName.replace(posSurface, string("Surface_1").length(), "Breakline_1");
    }
    // 저장 폴더: Dataset/Breaklines
    const std::string breaklinesDir = "Dataset/Breaklines/";  // Changed for container compatibility
    // std::filesystem::create_directories(breaklinesDir);  // Disabled for container compatibility
	string completeBreaklinePath = tempEdgeFolder + "CompleteBreakline.xyz";
	// 최종 결과는 OUTPUT_BREAKLINES_FOLDER에 저장
	string pcdFilePath = datasetBreaklinesFolder + breaklineFileName + ".pcd";
	string plyFilePath = datasetBreaklinesFolder + breaklineFileName + ".ply";
	string xyzFilePath = datasetBreaklinesFolder + breaklineFileName + ".xyz";

	// Use custom PCD writer with segment headers for SFS compatibility
	writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline, index, detectedPeakIndices);
	std::cout << "[EDGELINE DEBUG] Saving CompleteBreakline PLY in ASCII mode..." << std::endl;
	pcl::io::savePLYFile(plyFilePath, *cloud_CompleteBreakline, false); // ASCII mode
	fs::rename(completeBreaklinePath, xyzFilePath);

    
    // -------------------- (추가) Fractured surface 관련 처리 --------------------
    cout << "Getting points on fractured surface..." << endl;
    segCount = 1;
    typedef vector<boost::filesystem::path> vecB;
    vecB vB;
    copy(boost::filesystem::directory_iterator(p), boost::filesystem::directory_iterator(), back_inserter(vB));
    sort(vB.begin(), vB.end());
    index.clear();
    segStartIndex = 1;
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointsOnFracturedSurface(new pcl::PointCloud<pcl::PointNormal>);
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_PointsOnIntExtSurfaceNearBreakline(new pcl::PointCloud<pcl::PointNormal>);
    totalPtsCounter = 0;
    for (vecB::const_iterator it(vB.begin()), it_end(vB.end()); it != it_end; ++it)
    {
        string sTmp = (*it).string();
        matrix_breakLineSeg = readFile((*it).string(), 6);
        cloud_breakLineSeg->points.clear();
        for (size_t i = 0; i < matrix_breakLineSeg.rows(); i++)
        {
            cloud_breakLineSeg->points.push_back(
                pcl::PointXYZ(matrix_breakLineSeg(i, 0),
                              matrix_breakLineSeg(i, 1),
                              matrix_breakLineSeg(i, 2)));
            tmpPtN.x = matrix_breakLineSeg(i, 0);
            tmpPtN.y = matrix_breakLineSeg(i, 1);
            tmpPtN.z = matrix_breakLineSeg(i, 2);
            tmpPtN.normal_x = matrix_breakLineSeg(i, 3);
            tmpPtN.normal_y = matrix_breakLineSeg(i, 4);
            tmpPtN.normal_z = matrix_breakLineSeg(i, 5);
            
            // Compute geometric curvature for breakline point
            double curvature = 0.0;
            if (i > 0 && i < matrix_breakLineSeg.rows() - 1) {
                // Use discrete curvature approximation: |dN/ds| where N is normal, s is arc length
                Eigen::Vector3d curr_normal(matrix_breakLineSeg(i, 3), matrix_breakLineSeg(i, 4), matrix_breakLineSeg(i, 5));
                Eigen::Vector3d prev_normal(matrix_breakLineSeg(i-1, 3), matrix_breakLineSeg(i-1, 4), matrix_breakLineSeg(i-1, 5));
                Eigen::Vector3d next_normal(matrix_breakLineSeg(i+1, 3), matrix_breakLineSeg(i+1, 4), matrix_breakLineSeg(i+1, 5));
                
                Eigen::Vector3d curr_pos(matrix_breakLineSeg(i, 0), matrix_breakLineSeg(i, 1), matrix_breakLineSeg(i, 2));
                Eigen::Vector3d prev_pos(matrix_breakLineSeg(i-1, 0), matrix_breakLineSeg(i-1, 1), matrix_breakLineSeg(i-1, 2));
                Eigen::Vector3d next_pos(matrix_breakLineSeg(i+1, 0), matrix_breakLineSeg(i+1, 1), matrix_breakLineSeg(i+1, 2));
                
                // Central difference for normal derivative
                Eigen::Vector3d normal_diff = (next_normal - prev_normal);
                double arc_length = (next_pos - prev_pos).norm();
                
                if (arc_length > 1e-6) {
                    curvature = normal_diff.norm() / arc_length;
                }
                
                // Limit curvature to reasonable values
                if (curvature > 1.0) curvature = 1.0;
            } else {
                // For boundary points, use simpler approximation
                curvature = 0.01; // Small default value
            }
            
            tmpPtN.curvature = static_cast<float>(curvature);
            cloud_CompleteBreakline->points.push_back(tmpPtN);
            totalPtsCounter++;
        }
        cloud_breakLineSeg->width = cloud_breakLineSeg->points.size();
        cloud_breakLineSeg->height = 1;
        std::experimental::filesystem::path filePathTemp = { fragmentMeshFilePath };
        string fileNameOnly = filePathTemp.stem().string().substr(0, 14);
        string outPathTemp = tempDataPath(potID);
        bool isRim = isBreaklineSegARim(cloud_breakLineSeg, outPathTemp + fileNameOnly + "_SampledWithNormals.ply", segCount);
        index.push_back(to_string(segStartIndex) + " " + to_string(totalPtsCounter) + " " + (isRim ? "1" : "0"));

        // BUG FIX #1: Call getPointsOnFracturedSurface to actually populate fracture surface data
        // This function was defined but never called, leaving cloud_PointsOnFracturedSurface empty
        std::cout << "[FRACTURE SURFACE] Extracting fracture surface points for segment " << segCount << std::endl;
        getPointsOnFracturedSurface(cloud_breakLineSeg, fragmentMeshFilePath,
                                     outPathTemp + fileNameOnly + "_SampledWithNormals.ply",
                                     segCount, cloud_PointsOnFracturedSurface,
                                     cloud_PointsOnIntExtSurfaceNearBreakline);

        segStartIndex = totalPtsCounter + 1;
        segCount++;
    }
    cloud_CompleteBreakline->width = cloud_CompleteBreakline->points.size();
    cloud_CompleteBreakline->height = 1;

    cloud_PointsOnFracturedSurface->width = int(cloud_PointsOnFracturedSurface->points.size());
    cloud_PointsOnFracturedSurface->height = 1;
    cloud_PointsOnIntExtSurfaceNearBreakline->width = int(cloud_PointsOnIntExtSurfaceNearBreakline->points.size());
    cloud_PointsOnIntExtSurfaceNearBreakline->height = 1;

    pcl::PointCloud<PointNormal>::Ptr cloud_PointsOnFracturedSurfaceNoDuplicates(new pcl::PointCloud<PointNormal>);
    vector<PointNormal> vectorPointNormal;
    for (size_t i = 0; i < cloud_PointsOnFracturedSurface->points.size(); i++)
    {
        vectorPointNormal.push_back(cloud_PointsOnFracturedSurface->points[i]);
    }
    sort(vectorPointNormal.begin(), vectorPointNormal.end(), myobject2);
    if (!vectorPointNormal.empty())
    {
        for (size_t i = 0; i < vectorPointNormal.size() - 1; i++)
        {
            if ((vectorPointNormal[i].x == vectorPointNormal[i + 1].x) &&
                (vectorPointNormal[i].y == vectorPointNormal[i + 1].y) &&
                (vectorPointNormal[i].z == vectorPointNormal[i + 1].z))
            {
                // 중복은 건너뛰기
            }
            else
            {
                cloud_PointsOnFracturedSurfaceNoDuplicates->points.push_back(vectorPointNormal[i]);
            }
        }
        cloud_PointsOnFracturedSurfaceNoDuplicates->width = cloud_PointsOnFracturedSurfaceNoDuplicates->points.size();
        cloud_PointsOnFracturedSurfaceNoDuplicates->height = 1;

        // BUG FIX #2, #3: Fix output path and filename format
        // Old: saves to "build/Pot_A_Piece_01_Surface_0_FracturedSurfacePts.pcd"
        // New: saves to "Dataset/Surfaces/Pot_A/Pot_A_Piece_01_Surface_F.pcd"
        string fractureSurfaceFileName = currentFileName;
        size_t posSurface = fractureSurfaceFileName.find("Surface_0");
        if (posSurface != string::npos) {
            fractureSurfaceFileName.replace(posSurface, string("Surface_0").length(), "Surface_F");
        } else {
            posSurface = fractureSurfaceFileName.find("Surface_1");
            if (posSurface != string::npos) {
                fractureSurfaceFileName.replace(posSurface, string("Surface_1").length(), "Surface_F");
            }
        }

        // Use same directory structure as surfaces (Dataset/Surfaces/Pot_X/)
        string surfacesDir = getSurfaceDatasetPath(potID);
        string fractureSurfaceFilePath = surfacesDir + fractureSurfaceFileName + ".pcd";

        std::cout << "[FRACTURE SURFACE] Saving " << cloud_PointsOnFracturedSurfaceNoDuplicates->points.size()
                  << " fracture surface points to: " << fractureSurfaceFilePath << std::endl;
        pcl::io::savePCDFile(fractureSurfaceFilePath, *cloud_PointsOnFracturedSurfaceNoDuplicates);
        
        pcl::PointCloud<PointNormal>::Ptr cloud_PointsOnIntExtSurfaceNoDuplicates(new pcl::PointCloud<PointNormal>);
        vector<PointNormal> vectorPointNormal2;
        for (size_t i = 0; i < cloud_PointsOnIntExtSurfaceNearBreakline->points.size(); i++)
        {
            vectorPointNormal2.push_back(cloud_PointsOnIntExtSurfaceNearBreakline->points[i]);
        }
        sort(vectorPointNormal2.begin(), vectorPointNormal2.end(), myobject2);
        for (size_t i = 0; i < vectorPointNormal2.size() - 1; i++)
        {
            if ((vectorPointNormal2[i].x == vectorPointNormal2[i + 1].x) &&
                (vectorPointNormal2[i].y == vectorPointNormal2[i + 1].y) &&
                (vectorPointNormal2[i].z == vectorPointNormal2[i + 1].z))
            {
                // 중복 건너뛰기
            }
            else
            {
                cloud_PointsOnIntExtSurfaceNoDuplicates->points.push_back(vectorPointNormal2[i]);
            }
        }
        cloud_PointsOnIntExtSurfaceNoDuplicates->width = cloud_PointsOnIntExtSurfaceNoDuplicates->points.size();
        cloud_PointsOnIntExtSurfaceNoDuplicates->height = 1;
        pcl::io::savePCDFile(currentFileName + "_IntExtSurfacePtsNearBreakline.pcd", *cloud_PointsOnIntExtSurfaceNoDuplicates);
    }
    
    cloud_CompleteBreakline->width = cloud_CompleteBreakline->points.size();
    cloud_CompleteBreakline->height = 1;
}

void loadOBJ(string objFilePath, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_BreakLine, Eigen::Matrix4f& transform)
{

	pcl::TextureMesh mesh1;
	// Use standard PCL OBJ loader instead of VTK-based loadPolygonFileOBJ
	pcl::io::loadOBJFile(objFilePath, mesh1);
	// No need for second mesh load since we're using the same function
	// pcl::TextureMesh mesh2;
	// pcl::io::loadOBJFile(objFilePath, mesh2);
	// mesh1.tex_materials = mesh2.tex_materials;

	pcl::PointCloud<pcl::PointXYZ> cloud;
	pcl::fromPCLPointCloud2(mesh1.cloud, cloud);
	pcl::transformPointCloud(cloud, cloud, transform);
	pcl::toPCLPointCloud2(cloud, mesh1.cloud);


	// Mesh and breakline visualization removed for headless operation

	pcl::transformPointCloud(*cloud_BreakLine, *cloud_BreakLine, transform);
	// Final result visualization removed for headless operation
}

namespace fs = std::experimental::filesystem;

int main()
{
    const std::string BASE_PATH = tempPath();
    const std::string AXES_PATH = BASE_PATH + "/Axes";  // Standard path joining
    const std::string SEGMENTS_PATH = tempEdgePath(potID);

    // Re-enabled directory creation for proper functionality
    fs::create_directories(AXES_PATH);
    fs::create_directories(SEGMENTS_PATH);
    fs::create_directories(datasetBreaklinesFolder);
    fs::create_directories(datasetSurfacesFolder);
    fs::create_directories(tempEdgeFolder);

    Timer t;
    Timer t_individual;
    std::ofstream myfile(BASE_PATH + "/breaklineExtractionTimes.txt", std::ofstream::out | std::ofstream::app);

    std::string searchPath = BASE_PATH;
    std::cout << "Processing directory: " << searchPath << std::endl;

    if (!myfile.is_open()) {
        std::cerr << "Could not open breaklineExtractionTimes.txt\n";
        // Continue processing even if timing file can't be opened
    }

    try {
        // Collect and sort file paths
        std::vector<fs::path> objFiles;
        for (const auto& entry : fs::recursive_directory_iterator(searchPath)) {
            if ((!fs::is_directory(entry.path())) && entry.path().extension() == ".obj") {
                objFiles.push_back(entry.path());
            }
        }
        
        // Sort by filename
        std::sort(objFiles.begin(), objFiles.end(), [](const fs::path& a, const fs::path& b) {
            return a.stem().string() < b.stem().string();
        });

        // Process files in sorted order
        for (const auto& objPath : objFiles) {
            std::string fileNameOnly = objPath.stem().string();
            fileNameOnly = fileNameOnly.substr(0, 14);
            std::string surfaceFile0 = fileNameOnly + "_Surface_0.xyz";
            std::string surfaceFile1 = fileNameOnly + "_Surface_1.xyz";

            const std::string inputSurfaceFolder = tempDataPath(potID);
            const std::string outputSurfaceFolder = getSurfaceDatasetPath(potID);
    
            std::cout << "Surface 0 point cloud file: " << inputSurfaceFolder + surfaceFile0 << std::endl;
            std::cout << "Surface 1 point cloud file: " << inputSurfaceFolder + surfaceFile1 << std::endl;

            fs::copy_file(inputSurfaceFolder + surfaceFile0, 
                         outputSurfaceFolder + surfaceFile0, 
                         fs::copy_options::overwrite_existing);
            fs::copy_file(inputSurfaceFolder + surfaceFile1, 
                         outputSurfaceFolder + surfaceFile1, 
                         fs::copy_options::overwrite_existing);

            processFragmentData(inputSurfaceFolder + surfaceFile0, objPath.string());
            processFragmentData(inputSurfaceFolder + surfaceFile1, objPath.string());

            std::cout << "\nProcessing time for " << fileNameOnly << ": " << t_individual.elapsed() << " seconds\n";
            myfile << fileNameOnly << "\t" << t_individual.elapsed() << std::endl;
            t_individual.reset();
        }
        
        std::cout << "Total processing time: " << t.elapsed() << " seconds\n";
        myfile << "\nTotal processing time: " << t.elapsed() << " seconds\n";
    }
    catch (const std::exception& e) {
        std::cerr << "Error occurred: " << e.what() << std::endl;
        std::cerr << "Time until error: " << t.elapsed() << " seconds\n";
        myfile << "\nTime until error: " << t.elapsed() << " seconds\n";
        myfile.close();
        return -1;
    }

    myfile.close();
    return 0;
}
