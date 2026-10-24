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
#include <functional>
#include <map>
#include <limits>
#include <algorithm>
#include <sstream>
#define _SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING
#include <experimental/filesystem>
#include <filesystem>
#include <stdio.h>
#include <cstdlib> // POTA-247: getenv(SFS_VOTE_ORDER)
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
	Vector3d sphereCenter(3);
	double sphereRadius = 1.8;
	sphereCenter << P(0, 0), P(0, 1), P(0, 2);
	// std::cout << "Initial Sphere Center: " << sphereCenter.transpose() << ", Radius: " << sphereRadius << std::endl;

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
		}
		i++;
	}

	MatrixXd smoothedBreakLine(smoothBreakLineVector.size(), 3);
	// std::cout << "Smoothed Break Line Size: " << smoothedBreakLine.rows() << "x" << smoothedBreakLine.cols() << std::endl;
	for (int i = 0; i < smoothBreakLineVector.size(); ++i) {
		smoothedBreakLine.row(i) << smoothBreakLineVector[i](0), smoothBreakLineVector[i](1), smoothBreakLineVector[i](2);
		// std::cout << "Smoothed Break Line[" << i << "]: " << smoothedBreakLine.row(i) << std::endl;
	}
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



// POTA-247: paper vote-ordered loop port (SfSpp § "edge line": K-D tree filter,
// resample equidistant d=1.9mm, reorder CCW by normals+voting, corner segmentation
// at peaks of the distance-score distribution). BEHIND SFS_VOTE_ORDER ONLY;
// default path still calls getPointsInSequence (greedy split-walk, untouched).
// Paper-quote anchors: resample d=1.9mm (constant below); CCW-by-voting;
// distance-score = deviation from local linear trend; NO numeric corner threshold
// in the paper, so the peak rule below is a STATED ASSUMPTION (local max over
// +/-8 window above max(2.0mm, 3*median)), corners LOGGED ONLY -- the emitted
// lane stays one ordered loop because the downstream B-spline expects one lane
// per face (splitting the output would change Bl file structure).
// Substitution (stated): this bag is PointXYZ (no per-point normals), so the
// "normals" vote uses the PCA best-fit plane normal of the loop as the
// geometric normal surrogate, oriented by majority vote of per-edge turn signs.
static void getPointsInSequence_Vote247(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud,
                                        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced)
{
	const float RESAMPLE_D_MM = 1.9f; // paper constant
	size_t n = cloud->points.size();
	if (n == 0) { cloud_sequenced->width = 0; cloud_sequenced->height = 1; return; }
	if (n < 8) { // too few for plane/vote statistics: pass through (logged)
		std::cout << "[VOTE-247] passthrough n=" << n << std::endl;
		for (size_t i = 0; i < n; i++) cloud_sequenced->points.push_back(cloud->points[i]);
		cloud_sequenced->width = cloud_sequenced->points.size();
		cloud_sequenced->height = 1;
		return;
	}
	// 1. Deterministic seed (centroid-nearest; no cloud[0] order dependence), then
	// pure nearest-unvisited chain. Jump chords here are harmless: step 3 re-derives
	// topology geometrically (angular sort), so no gate is applied at this stage.
	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(cloud);
	std::vector<char> used(n, 0);
	// POTA-247b: paper's K-D tree filter surrogate. The rim bag carries satellite
	// fragments the greedy path discards via its COMP_GAP split (it walks comp[0]
	// only); angular voting is defined on ONE loop, so restrict to the largest
	// COMP_GAP-connected component (BFS, 5.0mm edge gate = greedy COMP_GAP =
	// same population the greedy walker would sequence). Logged; no-op when
	// the bag is already single-component.
	// POTA-261: comp gap env-tunable (default 5.0 = greedy COMP_GAP, 247b value).
	// SFS_COMP_KEEP=all skips the largest-comp restriction (keeps every point).
	double COMP_GAP_MM = 5.0;
	if (const char* e = std::getenv("SFS_COMP_GAP")) { double v = std::atof(e); if (v > 0.5 && v < 50.0) COMP_GAP_MM = v; }
	bool compKeepAll = false;
	if (const char* e = std::getenv("SFS_COMP_KEEP")) { if (*e && (std::string(e) == "all" || std::string(e) == "ALL")) compKeepAll = true; }
	std::vector<int> comp(n, -1);
	int ncomp = 0; int biggest = 0; size_t biggestSize = 0;
	std::vector<int> stack; std::vector<int> nb; std::vector<float> nd;
	for (size_t s = 0; s < n; s++) if (comp[s] < 0) {
		size_t sz = 0;
		stack.clear(); stack.push_back((int)s); comp[s] = ncomp;
		while (!stack.empty()) {
			int u = stack.back(); stack.pop_back(); sz++;
			int nn = kdtree.radiusSearch(cloud->points[u], COMP_GAP_MM, nb, nd);
			for (int k = 0; k < nn; k++) {
				int w = nb[k];
				if (w < 0 || (size_t)w >= n || comp[w] >= 0) continue;
				comp[w] = ncomp; stack.push_back(w);
			}
		}
		if (sz > biggestSize) { biggestSize = sz; biggest = ncomp; }
		ncomp++;
	}
	// POTA-263 (lead steer 2026-10-23): FULL_WALK (SFS_FULL_WALK=1) orders the whole bag
	// as ONE closed walk with no discard (comp-filter bypassed, clock sort skipped) and a
	// heading-guarded chain (cross-jump fix). Default OFF so VOTE/GATED replicate.
	bool fullWalk263 = true; // POTA-267 LANDED: no-discard full walk is the default; SFS_FULL_WALK=0 restores the clock-sort vote arm
	if (const char* e = std::getenv("SFS_FULL_WALK")) { fullWalk263 = (*e && std::string(e) != "0"); }
	// POTA-267: TERMINAL STOP AT THE WELD. Ticket 266 proved the P03-Bl1 walk is clean and
	// the rim loop is already welded shut when the chain's last step fires: the fresh-candidate
	// set is empty, so the code below fetches the nearest remaining dot ANYWHERE (124.590 mm),
	// and the implicit wrap then closes 124.773 mm back over the start = 27.8% of the loop, which
	// is the chord the resample and the score see. The fix is termination, not ordering: if the
	// nearest fresh dot is farther than R, END the chain here instead of fetching it.
	// SFS_STOP_NOFRESH=R (mm) enables the rule; unset/0 = pre-267 behaviour, byte-identical.
	// SFS_STOP_NOFRESH_DIAG=1 only PRINTS the per-step instrument that picks R (read-only).
	float stopR267 = 12.0f; // POTA-267 LANDED: 12mm from the six-lane instrument (worst guard step 4.69mm, 2.56x margin); SFS_STOP_NOFRESH=0 disables
	if (const char* e = std::getenv("SFS_STOP_NOFRESH")) { float v = (float)std::atof(e); if (v >= 0.0f && v < 1000.0f) stopR267 = v; }
	bool stopOn267 = (stopR267 > 0.0f);
	bool diagStop267 = false;
	if (const char* e = std::getenv("SFS_STOP_NOFRESH_DIAG")) { if (*e && std::string(e) != "0") diagStop267 = true; }
	std::vector<float> dall267;
	size_t keptN = 0;
	if (fullWalk263) { keptN = n; std::cout << "[FULL-263] no-discard kept " << keptN << "/" << n << " (" << ncomp << " comps @ " << COMP_GAP_MM << "mm)" << std::endl; }
	else if (compKeepAll) { keptN = n; std::cout << "[VOTE-247] comp-filter SKIPPED (SFS_COMP_KEEP=all) kept " << keptN << "/" << n << " (" << ncomp << " comps @ " << COMP_GAP_MM << "mm)" << std::endl; }
	else { for (size_t i = 0; i < n; i++) { if (comp[i] != biggest) used[i] = 1; else keptN++; }
	std::cout << "[VOTE-247] comp-filter kept " << keptN << "/" << n
	          << " (comp " << biggest << " of " << ncomp << " @ " << COMP_GAP_MM << "mm)" << std::endl; }
	// Deterministic seed: kept-component centroid-nearest (no cloud[0] order dependence).
	// POTA-287: seed inside the LARGEST lump, not nearest the middle of the bag. When the bag has
	// split (cracks, holes, scan gaps) the whole-bag centroid can land in a debris lump tens of mm
	// from the rim; the walk traces that lump and the 12 mm stop ends it as a stub. Restricting both
	// the centroid and the seed to comp[i]==biggest is a no-op where the bag is a single lump
	// (comp[i]==biggest for every dot, so same summands in the same order and the same divisor) and a
	// no-op under SFS_FULL_WALK=0 too, where the comp-filter above already marked every other lump
	// used. SFS_COMP_KEEP=all is the one arm whose start dot moves: it still keeps every lump but now
	// begins in the largest.
	Eigen::Vector3f cent(0,0,0);
	size_t seedN = 0;
	for (size_t i = 0; i < n; i++) if (!used[i] && comp[i] == biggest) {
		cent += Eigen::Vector3f(cloud->points[i].x, cloud->points[i].y, cloud->points[i].z);
		seedN++;
	}
	cent /= (float)seedN;
	size_t seed = 0; float seedD2 = std::numeric_limits<float>::max();
	for (size_t i = 0; i < n; i++) if (!used[i] && comp[i] == biggest) {
		Eigen::Vector3f d(cloud->points[i].x - cent(0), cloud->points[i].y - cent(1), cloud->points[i].z - cent(2));
		if (d.squaredNorm() < seedD2) { seedD2 = d.squaredNorm(); seed = i; }
	}
	std::cout << "[SEED-287] ncomp=" << ncomp << " biggest=" << biggest << " size=" << seedN << "/" << n;
	if (!diagStop267) std::cout << " seed=" << cloud->points[seed].x << " " << cloud->points[seed].y << " " << cloud->points[seed].z;
	std::cout << std::endl;
	std::vector<Eigen::Vector3f> chain; chain.reserve(n);
	size_t cur = seed;
	if (diagStop267) {
		std::cout << "[STOP-267] BEGIN bag=" << n << " seed=" << cloud->points[seed].x << " " << cloud->points[seed].y << " " << cloud->points[seed].z
		          << " R=" << stopR267 << " rule=" << (stopOn267 ? "ON" : "OFF") << std::endl;
	}
	for (size_t done = 0; done < n; done++) {
		chain.push_back(Eigen::Vector3f(cloud->points[cur].x, cloud->points[cur].y, cloud->points[cur].z));
		used[cur] = 1;
		if (done + 1 == n) break;
		// nearest unvisited: KNN probe first, exhaustive fallback (chain must cover all n)
		std::vector<int> idx(50); std::vector<float> dist(50);
		int found = kdtree.nearestKSearch(cloud->points[cur], 50, idx, dist);
		int best = -1; float bestD2 = std::numeric_limits<float>::max();
		// POTA-263 FULL_WALK cross-jump fix: heading-guarded pick among K=50 nearest
		// unvisited (score = dist*(1+2*(1-cos)), alpha=2 stated knob); first 2 points
		// and degenerate headings fall through to pure NN below.
		if (fullWalk263 && chain.size() >= 2) {
			Eigen::Vector3f hh263 = chain.back() - chain[chain.size()-2];
			float hl263 = hh263.norm();
			if (hl263 > 1e-9f) {
				hh263 /= hl263;
				double bestS263 = 1e100; int bestH263 = -1;
				for (int k = 0; k < found; k++) {
					int cand = idx[k];
					if (cand < 0 || (size_t)cand >= n || used[cand]) continue;
					Eigen::Vector3f dc263(cloud->points[cand].x - chain.back()(0), cloud->points[cand].y - chain.back()(1), cloud->points[cand].z - chain.back()(2));
					float dl263 = dc263.norm();
					if (dl263 < 1e-9f) continue;
					double cos263 = dc263.dot(hh263) / dl263;
					if (cos263 > 1.0) cos263 = 1.0; if (cos263 < -1.0) cos263 = -1.0;
					double s263 = (double)dl263 * (1.0 + 2.0 * (1.0 - cos263));
					if (s263 < bestS263) { bestS263 = s263; bestH263 = cand; }
				}
				if (bestH263 < 0) for (size_t i = 0; i < n; i++) if (!used[i]) {
					Eigen::Vector3f dc263(cloud->points[i].x - chain.back()(0), cloud->points[i].y - chain.back()(1), cloud->points[i].z - chain.back()(2));
					float dl263 = dc263.norm();
					if (dl263 < 1e-9f) continue;
					double cos263 = dc263.dot(hh263) / dl263;
					if (cos263 > 1.0) cos263 = 1.0; if (cos263 < -1.0) cos263 = -1.0;
					double s263 = (double)dl263 * (1.0 + 2.0 * (1.0 - cos263));
					if (s263 < bestS263) { bestS263 = s263; bestH263 = (int)i; }
				}
				best = bestH263;
			}
		}
		// POTA-267 instrument: how many fresh dots the K=50 probe actually offers, and the
		// nearest fresh one among them (the pick below is that dot whenever f50267 > 0).
		int f50267 = 0; float d50267 = -1.0f;
		for (int k = 0; k < found; k++) { int c267 = idx[k]; if (c267 < 0 || (size_t)c267 >= n || used[c267]) continue; f50267++; float dl267 = std::sqrt(dist[k]); if (dl267 > d50267) d50267 = dl267; }
		if (f50267 == 0) d50267 = -1.0f;
		for (int k = 0; k < found; k++) {
			int cand = idx[k];
			if (cand < 0 || (size_t)cand >= n || used[cand]) continue;
			if (dist[k] < bestD2) { bestD2 = dist[k]; best = cand; }
		}
		if (best < 0) for (size_t i = 0; i < n; i++) if (!used[i]) {
			Eigen::Vector3f d(cloud->points[i].x - chain.back()(0), cloud->points[i].y - chain.back()(1), cloud->points[i].z - chain.back()(2));
			if (d.squaredNorm() < bestD2) { bestD2 = d.squaredNorm(); best = (int)i; }
		}
		if (stopOn267 || diagStop267) {
			// Distance to the nearest FRESH dot anywhere. This is the quantity the exhaustive
			// fallback below fetches, so it is the one the stop rule must test (a K-window
			// emptiness test alone is R-independent: the 50 nearest points are all taken near the
			// weld while a fresh neighbour can still be sub-millimetre away).
			float dFresh267 = std::numeric_limits<float>::max();
			for (size_t i = 0; i < n; i++) if (!used[i]) {
				Eigen::Vector3f d267(cloud->points[i].x - chain.back()(0), cloud->points[i].y - chain.back()(1), cloud->points[i].z - chain.back()(2));
				float dl267 = d267.norm(); if (dl267 < dFresh267) dFresh267 = dl267;
			}
			float gap267 = -1.0f;
			if (best >= 0) { Eigen::Vector3f d267(cloud->points[best].x - chain.back()(0), cloud->points[best].y - chain.back()(1), cloud->points[best].z - chain.back()(2)); gap267 = d267.norm(); }
			if (diagStop267) {
				dall267.push_back(dFresh267);
				std::cout << "[STOP-267] S i=" << (chain.size() - 1) << " gap=" << gap267 << " f50=" << f50267
				          << " d50=" << (f50267 > 0 ? d50267 : -1.0f) << " dall=" << dFresh267
				          << " src=" << (f50267 > 0 ? "k" : "e");
				if (best >= 0) std::cout << " p=" << cloud->points[best].x << " " << cloud->points[best].y << " " << cloud->points[best].z;
				std::cout << std::endl;
			}
			if (stopOn267 && dFresh267 > stopR267) {
				std::cout << "[STOP-267] CHAIN-END step=" << (chain.size() - 1) << " of " << n
				          << ": nearest fresh dot " << dFresh267 << "mm > R=" << stopR267 << "mm ; refusing it"
				          << " ; left=" << (n - chain.size()) << " dots unvisited" << std::endl;
				break;
			}
		}
		if (best < 0) break; // unreachable (all used)
		cur = (size_t)best;
	}
	if (diagStop267 && !dall267.empty()) {
		const float Rs267[8] = {1.5f, 2.0f, 3.0f, 5.0f, 8.0f, 12.0f, 20.0f, 40.0f};
		std::cout << "[STOP-267] SUMMARY bag=" << n << " steps=" << dall267.size() << " chain=" << chain.size();
		for (int r267 = 0; r267 < 8; r267++) {
			int fires267 = 0; long first267 = -1;
			for (size_t i = 0; i < dall267.size(); i++) if (dall267[i] > Rs267[r267]) { fires267++; if (first267 < 0) first267 = (long)i; }
			std::cout << " R=" << Rs267[r267] << ":fires=" << fires267 << ",left=" << (first267 < 0 ? 0L : (long)(n - (size_t)first267 - 1));
		}
		std::cout << std::endl;
	}
	if (fullWalk263) {
		double maxjump263 = 0.0;
		for (size_t i = 1; i < chain.size(); i++) { double g263 = (chain[i] - chain[i-1]).norm(); if (g263 > maxjump263) maxjump263 = g263; }
		std::cout << "[FULL-263] chain=" << chain.size() << " maxjump=" << maxjump263 << "mm" << std::endl;
	}
	// 2. PCA best-fit plane of the chain (normal surrogate), angular sort about centroid.
	Eigen::Vector3f mean(0,0,0);
	for (size_t i = 0; i < chain.size(); i++) mean += chain[i];
	mean /= (float)chain.size();
	Eigen::Matrix3f cov = Eigen::Matrix3f::Zero();
	for (size_t i = 0; i < chain.size(); i++) { Eigen::Vector3f d = chain[i] - mean; cov += d * d.transpose(); }
	Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> es(cov);
	Eigen::Vector3f un = es.eigenvectors().col(0); // smallest eigenvalue = plane normal
	Eigen::Vector3f u = (chain[0] - mean); u -= un * u.dot(un); u.normalize();
	Eigen::Vector3f v = un.cross(u);
	std::vector<Eigen::Vector3f> loop;
	if (fullWalk263) { loop = chain;
		std::cout << "[FULL-263] kept chain order n=" << loop.size() << " (clock sort skipped)" << std::endl; }
	else {
		std::vector<std::pair<float, Eigen::Vector3f> > keyed; keyed.reserve(chain.size());
		for (size_t i = 0; i < chain.size(); i++) {
			Eigen::Vector3f d = chain[i] - mean;
			keyed.push_back(std::make_pair(std::atan2(d.dot(v), d.dot(u)), chain[i]));
		}
		std::sort(keyed.begin(), keyed.end(),
			[](const std::pair<float, Eigen::Vector3f>& a, const std::pair<float, Eigen::Vector3f>& b){ return a.first < b.first; });
		loop.reserve(keyed.size());
		for (size_t i = 0; i < keyed.size(); i++) loop.push_back(keyed[i].second);
	}
	// 3. Vote: signed turn sum of the sorted loop; enforce CCW (positive). The vote
	// is the majority direction of per-edge turns, not any single seed choice.
	double turnSum = 0.0;
	size_t M0 = loop.size();
	for (size_t i = 0; i < M0; i++) {
		Eigen::Vector3f a = loop[(i + 1) % M0] - loop[i];
		Eigen::Vector3f b = loop[(i + 2) % M0] - loop[(i + 1) % M0];
		Eigen::Vector3f an = a - un * a.dot(un), bn = b - un * b.dot(un);
		if (an.norm() < 1e-9f || bn.norm() < 1e-9f) continue;
		an.normalize(); bn.normalize();
		turnSum += std::atan2(un.dot(an.cross(bn)), an.dot(bn));
	}
	bool ccw = (turnSum >= 0.0);
	if (!ccw) std::reverse(loop.begin(), loop.end());
	std::cout << "[VOTE-247] chain=" << chain.size() << " turnSum=" << turnSum
	          << (ccw ? " CCW-kept" : " CW-reversed-to-CCW") << std::endl;
	// 4. Closed-loop arc-length resample at d=1.9mm (paper constant).
	std::vector<float> cum(M0 + 1, 0.0f);
	for (size_t i = 0; i < M0; i++) cum[i+1] = cum[i] + (loop[(i+1) % M0] - loop[i]).norm();
	float L = cum[M0];
	size_t M = (L >= RESAMPLE_D_MM) ? (size_t)std::max<size_t>(8, (size_t)std::llround(L / RESAMPLE_D_MM)) : M0;
	std::vector<Eigen::Vector3f> res; res.reserve(M);
	if (L >= RESAMPLE_D_MM) {
		size_t seg = 0;
		for (size_t j = 0; j < M; j++) {
			float s = (float)j * L / (float)M;
			while (seg + 1 < M0 && cum[seg+1] < s) seg++;
			float segLen = cum[seg+1] - cum[seg];
			float t = (segLen > 1e-9f) ? (s - cum[seg]) / segLen : 0.0f;
			res.push_back(loop[seg] * (1.0f - t) + loop[(seg+1) % M0] * t);
		}
	} else { res = loop; }
	// 5. Corner segmentation (paper: peaks of distance-score = deviation from local
	// linear trend). Score = perpendicular distance from chord (i-w, i+w), w=8
	// (STATED ASSUMPTION: paper gives no window/threshold). Logged only.
	size_t MR = res.size();
	const int W = 8;
	std::vector<float> score(MR, 0.0f);
	for (size_t i = 0; i < MR; i++) {
		Eigen::Vector3f a = res[(i + MR - W) % MR], b = res[(i + W) % MR];
		Eigen::Vector3f ab = b - a; float abl = ab.norm();
		if (abl < 1e-9f) { score[i] = 0.0f; continue; }
		Eigen::Vector3f ap = res[i] - a;
		score[i] = (ap - ab * (ap.dot(ab) / (abl * abl))).norm();
	}
	std::vector<float> srt = score;
	std::sort(srt.begin(), srt.end());
	float med = srt[srt.size()/2];
	float thr = std::max(2.0f, 3.0f * med);
	size_t corners = 0; std::string cidx;
	for (size_t i = 0; i < MR; i++) {
		bool peak = true;
		for (int k = 1; k <= W; k++)
			if (score[(i + k) % MR] > score[i] || score[(i + MR - k) % MR] > score[i]) { peak = false; break; }
		if (peak && score[i] > thr) {
			if (corners < 12) { if (corners) cidx += ","; cidx += std::to_string(i); }
			corners++;
		}
	}
	std::cout << "[VOTE-247] resampled=" << MR << " (L=" << L << "mm) corners=" << corners
	          << " thr=" << thr << " med=" << med << " idx=[" << cidx << "]" << std::endl;
	for (size_t i = 0; i < MR; i++)
		cloud_sequenced->points.push_back(pcl::PointXYZ(res[i](0), res[i](1), res[i](2)));
	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;
}

// POTA-212 PORT NOTE (pristine line): this is the POTA-153 split-walk cure verbatim except this
// header. Staged anchor was edgeline_extraction_headless.cpp:806-892 @ 4accb8d/main-line;
// pristine anchor is :533-613 @ b1ed4d1 (pristine walker: seed cloud[0], greedy K=50,
// dead iterations). Signature UNCHANGED. Requires <functional>, <map>, <limits>, <algorithm>.
void getPointsInSequence(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced)
{

	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;

	kdtree.setInputCloud(cloud);

	const float COMP_GAP_MM = 5.0f;
	const float GUARD_GATE_MM = 6.0f;

	size_t n = cloud->points.size();
	if (n == 0) { cloud_sequenced->width = 0; cloud_sequenced->height = 1; return; }

	// union-find components at COMP_GAP_MM (pairwise; n is O(hundreds))
	std::vector<int> parent(n);
	for (size_t i = 0; i < n; i++) parent[i] = (int)i;
	std::function<int(int)> findRoot = [&](int a) {
		while (parent[a] != a) { parent[a] = parent[parent[a]]; a = parent[a]; }
		return a;
	};
	for (size_t i = 0; i < n; i++) for (size_t j = i + 1; j < n; j++)
	{
		float dx = cloud->points[i].x - cloud->points[j].x;
		float dy = cloud->points[i].y - cloud->points[j].y;
		float dz = cloud->points[i].z - cloud->points[j].z;
		if (dx*dx + dy*dy + dz*dz < COMP_GAP_MM * COMP_GAP_MM)
		{ int ri = findRoot((int)i), rj = findRoot((int)j); if (ri != rj) parent[ri] = rj; }
	}
	std::map<int, std::vector<int>> comps;
	for (size_t i = 0; i < n; i++) comps[findRoot((int)i)].push_back((int)i);
	std::vector<std::vector<int>> ordered;
	for (auto &kv : comps) ordered.push_back(kv.second);
	std::sort(ordered.begin(), ordered.end(), [](const std::vector<int> &a, const std::vector<int> &b){ return a.size() > b.size(); });
	std::cout << "[SPLIT-WALK] components=" << ordered.size();
	for (auto &c : ordered) std::cout << " " << c.size();
	std::cout << std::endl;

	// ADAPTIVE: Scale K with boundary size (5-50 range, ~10% of points)
	int K = std::max(5, std::min(50, (int)n / 10));
	std::cout << "[ADAPTIVE SEQUENCING] Boundary has " << n
	          << " points, using K=" << K << " for point sequencing" << std::endl;

	std::vector<char> visited(n, 0);
	std::vector<size_t> cuts;
	for (size_t ci = 0; ci < ordered.size(); ci++)
	{
		std::vector<int> &comp = ordered[ci];
		if (comp.empty()) continue;
		int seed = comp[0];
		pcl::PointXYZ currentPoint = cloud->points[seed];
		pcl::PointXYZ previousPoint = currentPoint;
		cloud_sequenced->points.push_back(currentPoint);
		visited[seed] = 1;
		size_t compDone = 1;
		bool first = true;
		while (compDone < comp.size())
		{
			std::vector<int> pointIdxNKNSearch(K);
			std::vector<float> pointNKNSquaredDistance(K);
			int found = kdtree.nearestKSearch(currentPoint, K, pointIdxNKNSearch, pointNKNSquaredDistance);
			int best = -1;
			float bestD2 = std::numeric_limits<float>::max();
			float fwdx = currentPoint.x - previousPoint.x;
			float fwdy = currentPoint.y - previousPoint.y;
			float fwdz = currentPoint.z - previousPoint.z;
			for (int k = 0; k < found; k++)
			{
				int cand = pointIdxNKNSearch[k];
				if (cand < 0 || (size_t)cand >= n || visited[cand]) continue;
				float vx = cloud->points[cand].x - currentPoint.x;
				float vy = cloud->points[cand].y - currentPoint.y;
				float vz = cloud->points[cand].z - currentPoint.z;
				float d2 = vx*vx + vy*vy + vz*vz;
				if (!first)
				{
					if (d2 > GUARD_GATE_MM * GUARD_GATE_MM) continue;
					if (vx*fwdx + vy*fwdy + vz*fwdz < 0.0f) continue;
				}
				if (d2 < bestD2) { bestD2 = d2; best = cand; }
			}
			if (best < 0)
			{
				// guard starved: nearest unvisited dot of this component (records a cut)
				float bn = std::numeric_limits<float>::max();
				for (int cand : comp) if (!visited[cand])
				{
					float dx = cloud->points[cand].x - currentPoint.x;
					float dy = cloud->points[cand].y - currentPoint.y;
					float dz = cloud->points[cand].z - currentPoint.z;
					float d2 = dx*dx + dy*dy + dz*dz;
					if (d2 < bn) { bn = d2; best = cand; }
				}
				if (best >= 0) cuts.push_back(cloud_sequenced->points.size());
			}
			if (best < 0) break;
			previousPoint = currentPoint;
			currentPoint = cloud->points[best];
			cloud_sequenced->points.push_back(currentPoint);
			visited[best] = 1;
			compDone++;
			first = false;
		}
		if (ci + 1 < ordered.size()) cuts.push_back(cloud_sequenced->points.size());
	}

	std::cout << "[SPLIT-WALK] sequenced=" << cloud_sequenced->points.size() << " cuts=" << cuts.size();
	for (size_t c : cuts) std::cout << " @" << c;
	std::cout << std::endl;

	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;
}


// POTA-213: per-surface loop separation (ORIG-free, Pot-A calibrated).
// Splits the walk-input bag (boundaryCloud_Improved) into rim vs wall-base
// step-ring by mesh-observable cylindrical shape about the piece pipeline
// axis (Dataset/Axes/<Piece>_Axis.xyz, 6-number pipeline product). Rule
// (stated in ticket 213 BEFORE building): RING iff 20<=r_med<=35 mm AND
// r_std<2.0 AND h_span<4.0 AND 50<=count<=500. Fallbacks keep 212 whole-bag
// behavior and are always logged, never silent.
void writeMatrix_to_XYZ(MatrixXd& src, string fileName, int cols);
static bool splitRimVsStepRing_213(
    pcl::PointCloud<pcl::PointXYZ>::Ptr bag,
    const Eigen::Vector3f& axisC, const Eigen::Vector3f& axisD, bool axisOK,
    pcl::PointCloud<pcl::PointXYZ>::Ptr rimOut,
    pcl::PointCloud<pcl::PointXYZ>::Ptr ringOut)
{
    rimOut->points.clear(); ringOut->points.clear();
    size_t n = bag->points.size();
    if (n == 0) { std::cout << "[LOOP-SELECT] empty bag, nothing to split" << std::endl; return axisOK; }
    pcl::KdTreeFLANN<pcl::PointXYZ> kd; kd.setInputCloud(bag);
    const float CGAP = 5.0f;
    std::vector<int> comp(n, -1);
    std::vector<std::vector<int> > comps;
    std::vector<int> stack; std::vector<float> dist; std::vector<int> nbr;
    for (size_t s = 0; s < n; s++) {
        if (comp[s] != -1) continue;
        std::vector<int> members; members.push_back((int)s); comp[s] = (int)comps.size();
        stack.clear(); stack.push_back((int)s);
        while (!stack.empty()) {
            int cur = stack.back(); stack.pop_back();
            nbr.clear(); dist.clear();
            if (kd.radiusSearch(bag->points[cur], CGAP, nbr, dist) > 0) {
                for (size_t k = 0; k < nbr.size(); k++) {
                    if (comp[nbr[k]] == -1) { comp[nbr[k]] = (int)comps.size(); members.push_back(nbr[k]); stack.push_back(nbr[k]); }
                }
            }
        }
        comps.push_back(members);
    }
    std::sort(comps.begin(), comps.end(), [](const std::vector<int>& a, const std::vector<int>& b){ return a.size() > b.size(); });
    std::cout << "[LOOP-SELECT] bag=" << n << " comps=" << comps.size();
    if (!axisOK) std::cout << " axis=MISSING(fallback: whole-bag walk)";
    std::cout << std::endl;
    if (!axisOK) { rimOut->points = bag->points; return false; }
    std::vector<char> isRingComp(comps.size(), 0);
    size_t ringDots = 0;
    for (size_t c = 0; c < comps.size(); c++) {
        const std::vector<int>& m = comps[c];
        std::vector<float> rr; rr.reserve(m.size());
        float hmin = 1e30f, hmax = -1e30f;
        for (size_t k = 0; k < m.size(); k++) {
            Eigen::Vector3f v = bag->points[m[k]].getVector3fMap() - axisC;
            float h = v.dot(axisD);
            Eigen::Vector3f rad = v - h * axisD;
            rr.push_back(rad.norm());
            if (h < hmin) hmin = h; if (h > hmax) hmax = h;
        }
        size_t mid = rr.size() / 2;
        std::nth_element(rr.begin(), rr.begin() + mid, rr.end());
        float rmed = rr[mid];
        double mean = 0; for (size_t k = 0; k < rr.size(); k++) mean += rr[k];
        mean /= rr.size();
        double var = 0; for (size_t k = 0; k < rr.size(); k++) { double d = rr[k] - mean; var += d * d; }
        float rstd = (float)std::sqrt(var / rr.size());
        float hspan = hmax - hmin;
        bool ring = (rmed >= 20.0f && rmed <= 35.0f && rstd < 2.0f && hspan < 4.0f && m.size() >= 50 && m.size() <= 500);
        isRingComp[c] = ring ? 1 : 0;
        if (ring) ringDots += m.size();
        std::cout << "[LOOP-SELECT] comp" << c << " count=" << m.size() << " r_med=" << rmed
                  << " r_std=" << rstd << " h_span=" << hspan << " -> " << (ring ? "RING" : "RIM") << std::endl;
    }
    if (ringDots == 0) {
        std::cout << "[LOOP-SELECT] no ring found -> whole-bag walk, sidecar empty" << std::endl;
        rimOut->points = bag->points; return true;
    }
    if (ringDots == n) {
        std::cout << "[LOOP-SELECT] FALLBACK: all-ring bag -> Bl=largest comp, rest sidecar" << std::endl;
        for (size_t k = 0; k < comps[0].size(); k++) rimOut->points.push_back(bag->points[comps[0][k]]);
        for (size_t c = 1; c < comps.size(); c++)
            for (size_t k = 0; k < comps[c].size(); k++) ringOut->points.push_back(bag->points[comps[c][k]]);
        rimOut->width = (int)rimOut->points.size(); rimOut->height = 1;
        ringOut->width = (int)ringOut->points.size(); ringOut->height = 1;
        return true;
    }
    for (size_t c = 0; c < comps.size(); c++) {
        const std::vector<int>& m = comps[c];
        for (size_t k = 0; k < m.size(); k++) {
            if (isRingComp[c]) ringOut->points.push_back(bag->points[m[k]]);
            else rimOut->points.push_back(bag->points[m[k]]);
        }
    }
    rimOut->width = (int)rimOut->points.size(); rimOut->height = 1;
    ringOut->width = (int)ringOut->points.size(); ringOut->height = 1;
    std::cout << "[LOOP-SELECT] rim=" << rimOut->points.size() << " ring=" << ringOut->points.size() << std::endl;
    return true;
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
    // POTA-218 ARM B (radius shrink, compile with -DPOTA218_ARM_B): tightened
    // adaptive rule 3x-spacing / clamp 1.5-8mm. NOTE the cure-line baseline here
    // is a FIXED 4mm (main line carries 6x/3-50 adaptive, ~line 968 there); the
    // arm ports that adaptive form in tightened parameters, below both (P16-S1
    // N=6134: spacing 0.26 -> 0.77 -> clamped 1.5mm vs 4mm control / 3mm main).
    // No flag = control: fixed 4mm cure-line behavior, byte-logic unchanged.
#ifdef POTA218_ARM_B
	int num_pts218 = (int)cloudWithoutNormals->points.size();
	double spacing218 = std::sqrt(400.0 / (double)std::max(50, num_pts218));
	double radius218 = std::max(1.5, std::min(8.0, spacing218 * 3.0));
	boundary_est.setRadiusSearch(radius218);
	std::cout << "[ARM-B radius] pts=" << num_pts218 << " spacing~" << spacing218
	          << "mm r=" << radius218 << "mm" << std::endl;
#else
    // Original boundary search radius
    boundary_est.setRadiusSearch(4);
#endif
	//boundary_est.setAngleThreshold(0.6 * M_PI);//M_PI
	boundary_est.setAngleThreshold(M_PI * 0.6);//M_PI
	boundary_est.setSearchMethod(pcl::search::KdTree<pcl::PointXYZ>::Ptr(new pcl::search::KdTree<pcl::PointXYZ>));
	boundary_est.compute(boundary);


	//get points which on the boundary form point cloud; guard against size mismatch
	pcl::PointCloud<pcl::PointXYZ>::Ptr boundaryCloud(new pcl::PointCloud<pcl::PointXYZ>);
	// POTA-213 keep-all veto (no ORIG geometry enters this gate). P01-S1 showed the
	// centroid-radial alignment does NOT separate lip faces on Pot-A: the 0.5 gate kept
	// 345/dropped 794 and shattered the true rim to 8 fragments (largest kept 113 < 214
	// author pts), while veto-off input is already a clean 2-group (808 rim + 331
	// wall-base step ring at 5mm). Any dropping threshold shatters the rim, so the
	// principled Pot-A gate keeps the whole bag (align in [-1,1] always passes) and
	// separation moves downstream to shape, inside this face's bag (175 stands).
	const float FACE_ALIGN_VETO = 2.0f;
	Eigen::Vector3f surfCentroid(0.0f, 0.0f, 0.0f);
	for (const auto &p : cloudWithoutNormals->points) surfCentroid += p.getVector3fMap();
	if (!cloudWithoutNormals->points.empty()) surfCentroid /= (float)cloudWithoutNormals->points.size();
	size_t faceVetoKept = 0, faceVetoDropped = 0;
#if defined(POTA218_ARM_A) || defined(POTA218_ARM_C)
	// POTA-218 ARM A/C neighbor field: same-patch dots around each candidate.
	// (ORIG-free: pipeline input cloud geometry + input normals only.)
	pcl::KdTreeFLANN<pcl::PointXYZ> armTree218;
	armTree218.setInputCloud(cloudWithoutNormals);
	size_t armKept218 = 0, armDropped218 = 0;
#endif
	std::size_t N = std::min<std::size_t>(boundary.points.size(), cloudWithoutNormals->points.size());
	N = std::min<std::size_t>(N, normals->points.size());
	for (std::size_t i = 0; i < N; i++)
	{
		if (boundary.points[i].boundary_point == 1)
		{
			Eigen::Vector3f rp = cloudWithoutNormals->points[i].getVector3fMap() - surfCentroid;
			float rl = rp.norm();
			Eigen::Vector3f nn(normals->points[i].normal_x, normals->points[i].normal_y, normals->points[i].normal_z);
			float align = (rl > 1e-6f) ? nn.dot(rp / rl) : 0.0f;
			if (align <= FACE_ALIGN_VETO)
			{
#ifdef POTA218_ARM_A
				// ARM A (surround test, -DPOTA218_ARM_A): drop candidate dots fully
				// surrounded by same-patch dots. K=12 neighbors projected on the
				// tangent plane (input normal); max angular gap < 120deg means no
				// void beside the dot => twisted-face interior, not a true edge
				// (a rim dot on a straight edge sees a ~180deg+ void sector).
				{
					const int K218 = 12;
					std::vector<int> aIdx218(K218);
					std::vector<float> aDist218(K218);
					int aFound218 = armTree218.nearestKSearch(cloudWithoutNormals->points[i], K218, aIdx218, aDist218);
					bool drop218 = false;
					if (aFound218 >= 6)
						{
							Eigen::Vector3f nrm218(nn(0), nn(1), nn(2));
							if (nrm218.norm() < 1e-9f) nrm218 = Eigen::Vector3f(0, 0, 1);
							else nrm218.normalize();
							Eigen::Vector3f help218 = (std::fabs(nrm218(2)) < 0.9f) ? Eigen::Vector3f(0, 0, 1) : Eigen::Vector3f(0, 1, 0);
							Eigen::Vector3f t1218 = nrm218.cross(help218).normalized();
							Eigen::Vector3f t2218 = nrm218.cross(t1218).normalized();
							Eigen::Vector3f pi218 = cloudWithoutNormals->points[i].getVector3fMap();
							std::vector<double> ang218;
							for (int kk = 1; kk < aFound218; kk++)
								{
									Eigen::Vector3f off218 = cloudWithoutNormals->points[aIdx218[kk]].getVector3fMap() - pi218;
									double x218 = off218.dot(t1218), y218 = off218.dot(t2218);
									if (x218 * x218 + y218 * y218 < 1e-12) continue;
									ang218.push_back(std::atan2(y218, x218));
								}
							if (ang218.size() >= 5)
								{
									std::sort(ang218.begin(), ang218.end());
									double maxGap218 = 0.0;
									for (size_t gg = 0; gg < ang218.size(); gg++)
										{
											double g218 = ang218[(gg + 1) % ang218.size()] - ang218[gg];
											if (g218 < 0) g218 += 2.0 * M_PI;
											if (g218 > maxGap218) maxGap218 = g218;
										}
									if (maxGap218 < 2.094) drop218 = true; // 120deg
								}
						}
					if (drop218) armDropped218++;
					else { boundaryCloud->points.push_back(cloudWithoutNormals->points[i]); armKept218++; }
					faceVetoKept++;
				}
#else
#ifdef POTA218_ARM_C
				// ARM C (normal gate, -DPOTA218_ARM_C): keep only candidates near a
				// normal discontinuity (face/fracture transition). Max deviation of
				// the input normals among K=12 same-patch neighbors < 30deg means
				// coherent face interior => drop. (215 measured face p90 18deg vs
				// fracture p10 28deg; 30deg sits just above that split.)
				{
					const int K218 = 12;
					std::vector<int> cIdx218(K218);
					std::vector<float> cDist218(K218);
					int cFound218 = armTree218.nearestKSearch(cloudWithoutNormals->points[i], K218, cIdx218, cDist218);
					bool drop218 = false;
					if (cFound218 >= 6)
						{
							Eigen::Vector3f n0218(normals->points[i].normal_x, normals->points[i].normal_y, normals->points[i].normal_z);
							if (n0218.norm() < 1e-9f) n0218 = Eigen::Vector3f(0, 0, 1);
							else n0218.normalize();
							double maxDev218 = 0.0;
							for (int kk = 1; kk < cFound218; kk++)
								{
									Eigen::Vector3f nk218(normals->points[cIdx218[kk]].normal_x, normals->points[cIdx218[kk]].normal_y, normals->points[cIdx218[kk]].normal_z);
									if (nk218.norm() < 1e-9f) continue;
									nk218.normalize();
									double d218 = n0218.dot(nk218);
									if (d218 > 1.0) d218 = 1.0;
									if (d218 < -1.0) d218 = -1.0;
									double dev218 = std::acos(d218);
									if (dev218 > maxDev218) maxDev218 = dev218;
								}
							if (maxDev218 < 0.5236) drop218 = true; // 30deg
						}
					if (drop218) armDropped218++;
					else { boundaryCloud->points.push_back(cloudWithoutNormals->points[i]); armKept218++; }
					faceVetoKept++;
				}
#else
				boundaryCloud->points.push_back(cloudWithoutNormals->points[i]);
				faceVetoKept++;
#endif
#endif
			}
			else faceVetoDropped++;
		}
	}
	std::cout << "[FACE VETO] boundary kept=" << faceVetoKept << " dropped=" << faceVetoDropped
	          << " (align<= " << FACE_ALIGN_VETO << ", centroid-observable)" << std::endl;
	boundaryCloud->width = boundaryCloud->points.size();
	boundaryCloud->height = 1;
	boundaryCloud->is_dense = true;
	std::cout << "[EDGELINE DBG] boundaryCloud size=" << boundaryCloud->points.size() << std::endl;



	pcl::io::savePCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud);
	pcl::io::loadPCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud);
#if defined(POTA218_ARM_A) || defined(POTA218_ARM_B) || defined(POTA218_ARM_C)
	// POTA-218 diagnostic only (no logic effect): per-face copy of the post-arm
	// pre-snap dots. The shared tempEdgeFolder keeps ONE face (last writer wins,
	// 217 gap); scoring needs both faces, so each face saves its own copy here.
	{
		std::string armFace218 = "Sx";
		if (currentFileName.find("Surface_0") != std::string::npos) armFace218 = "S0";
		else if (currentFileName.find("Surface_1") != std::string::npos) armFace218 = "S1";
		pcl::io::savePCDFile(tempEdgeFolder + "boundary_" + armFace218 + ".pcd", *boundaryCloud);
	}
#endif
#ifdef POTA218_ARM_A
	std::cout << "[ARM-A surround] kept=" << armKept218 << " dropped=" << armDropped218 << " (K=12, gap<120deg)" << std::endl;
#endif
#ifdef POTA218_ARM_C
	std::cout << "[ARM-C normalgate] kept=" << armKept218 << " dropped=" << armDropped218 << " (K=12, dev<30deg)" << std::endl;
#endif
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
	std::cout << "[EDGELINE DBG] boundaryCloud_Improved size=" << boundaryCloud_Improved->points.size() << std::endl;
	pcl::io::savePCDFile(tempEdgeFolder + "boundaryImproved.pcd", *boundaryCloud_Improved);
	//-----------------------------------------------------------------------------
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::RadiusOutlierRemoval<pcl::PointXYZ> outrem;
	// build the filter
	outrem.setInputCloud(boundaryCloud_Improved);
	outrem.setRadiusSearch(2.5);
	outrem.setMinNeighborsInRadius(6);
	outrem.setKeepOrganized(true);
	// apply filter
	outrem.filter(*cloud_filtered);
	std::cout << "[EDGELINE DBG] cloud_filtered size=" << cloud_filtered->points.size() << std::endl;
	pcl::io::savePCDFileASCII(tempEdgeFolder + "cloud_Filtered.pcd", *cloud_filtered);

	// POTA-212 port of POTA-153: DELETED killer reload-over (was: loadPCDFile(boundary.pcd) into
	// boundaryCloud_Improved, discarding the face-vetoed, unclustered-snapped cloud). Sequencing now
	// consumes boundaryCloud_Improved as built above. cloud_Filtered.pcd remains a diagnostic
	// artifact only: ROR revival alone must not feed sequencing.
	std::cout << "[EDGELINE DBG] boundary improved (no reload) size=" << boundaryCloud_Improved->points.size() << std::endl;
	// POTA-213 loop separation: classify walk-input components by cylindrical shape
	// about the piece pipeline axis; walk RIM for the Bl file (B-spline downstream
	// sees rim only, no rim-ring chord) and sidecar the walked step-ring per face.
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_rimIn(new pcl::PointCloud<pcl::PointXYZ>);
	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_ringIn(new pcl::PointCloud<pcl::PointXYZ>);
	{
		Eigen::Vector3f axC(0,0,0), axD(0,0,1); bool axOK = false;
		string axPath = axesFolder + fileNameOnly + "_Axis.xyz";
		MatrixXd axM = readFile(axPath, 6);
		if (axM.rows() >= 1 && axM.cols() >= 6) {
			axC = Eigen::Vector3f((float)axM(0,0), (float)axM(0,1), (float)axM(0,2));
			axD = Eigen::Vector3f((float)axM(0,3), (float)axM(0,4), (float)axM(0,5));
			float dl = axD.norm(); if (dl > 1e-9f) axD /= dl;
			axOK = true;
		}
		if (!axOK) std::cout << "[LOOP-SELECT] axis missing/unreadable: " << axPath << std::endl;
		splitRimVsStepRing_213(boundaryCloud_Improved, axC, axD, axOK, cloud_rimIn, cloud_ringIn);
	}
	bool voteOrder247 = true; // POTA-267 LANDED: this arm now hosts the full walk; SFS_VOTE_ORDER=0 restores the greedy split-walk
	if (const char* evo = std::getenv("SFS_VOTE_ORDER")) { voteOrder247 = (*evo && std::string(evo) != "0"); }
	std::cout << "[VOTE-247] " << (voteOrder247 ? "ON (paper CCW vote-order)" : "OFF (greedy split-walk intact)") << std::endl;
	if (voteOrder247) getPointsInSequence_Vote247(cloud_rimIn, cloud_sequenced);
	else getPointsInSequence(cloud_rimIn, cloud_sequenced);
	std::cout << "[EDGELINE DBG] cloud_sequenced (rim) size=" << cloud_sequenced->points.size() << std::endl;
	{
		string blBase = currentFileName;
		{ size_t pp = blBase.find("Surface"); if (pp != string::npos) blBase.replace(pp, 7, "Breakline"); }
		pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_ringWalked(new pcl::PointCloud<pcl::PointXYZ>);
		if (!cloud_ringIn->points.empty()) getPointsInSequence(cloud_ringIn, cloud_ringWalked);
		if (!cloud_ringWalked->points.empty()) {
			pcl::io::savePCDFileASCII(tempEdgeFolder + "_breakLineFromConcaveHull_ring.pcd", *cloud_ringWalked);
			pcl::io::savePCDFileASCII(datasetBreaklinesFolder + blBase + "_stepring.pcd", *cloud_ringWalked);
		}
		MatrixXd ringM((int)cloud_ringWalked->points.size(), 3);
		for (int qi = 0; qi < (int)cloud_ringWalked->points.size(); qi++) {
			ringM(qi,0) = cloud_ringWalked->points[qi].x;
			ringM(qi,1) = cloud_ringWalked->points[qi].y;
			ringM(qi,2) = cloud_ringWalked->points[qi].z;
		}
		writeMatrix_to_XYZ(ringM, tempEdgeFolder + "_breakLineFromConcaveHull_ring.xyz", 3);
		writeMatrix_to_XYZ(ringM, datasetBreaklinesFolder + blBase + "_stepring.xyz", 3);
		std::cout << "[LOOP-SELECT] sidecar " << blBase << "_stepring pts=" << cloud_ringWalked->points.size() << std::endl;
	}

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

// Custom PCD writer with segment headers for SFS compatibility
//-----------------------------------------------------------------------------
void writeBreaklinePCDWithSegments(const std::string& filename, const pcl::PointCloud<pcl::PointNormal>& cloud)
{
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << " for writing" << std::endl;
        return;
    }

    // Read segment files to get segment information
    std::vector<std::pair<int, int>> segments; // start_index, end_index pairs
    int totalPoints = 0;
    
    // Read segment files from Segments/ directory
    boost::filesystem::path segDir("Segments/");
    if (boost::filesystem::exists(segDir)) {
        std::vector<boost::filesystem::path> segFiles;
        copy(boost::filesystem::directory_iterator(segDir), 
             boost::filesystem::directory_iterator(), 
             back_inserter(segFiles));
        sort(segFiles.begin(), segFiles.end());
        
        for (const auto& segFile : segFiles) {
            if (segFile.extension() == ".xyz") {
                MatrixXd segMatrix = readFile(segFile.string(), 6);
                int segSize = segMatrix.rows();
                int startIdx = totalPoints + 1; // 1-indexed
                int endIdx = totalPoints + segSize;
                segments.push_back({startIdx, endIdx});
                totalPoints += segSize;
            }
        }
    }
    
    // If no segments found, create single segment
    if (segments.empty()) {
        segments.push_back({1, (int)cloud.points.size()});
        totalPoints = cloud.points.size();
    }

    // Write PCD header with segment information
    file << "# .PCD v0.7 - Point Cloud Data file format" << std::endl;
    file << "# " << segments.size() << " " << totalPoints << " 0" << std::endl;
    
    // Write segment ranges
    for (const auto& seg : segments) {
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
    
    // Write point data
    for (const auto& point : cloud.points) {
        file << point.x << " " << point.y << " " << point.z << " "
             << point.normal_x << " " << point.normal_y << " " << point.normal_z << " "
             << point.curvature << std::endl;
    }
    
    file.close();
    std::cout << "Saved PCD with " << segments.size() << " segments to: " << filename << std::endl;
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


void findPeaks(vector<float> x0, vector<int>& peakInds)
{

	int minIdx = distance(x0.begin(), min_element(x0.begin(), x0.end()));
	int maxIdx = distance(x0.begin(), max_element(x0.begin(), x0.end()));

	float sel = (x0[maxIdx] - x0[minIdx]) / 4.0; // 10;// 20.0; //4.0;

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

void detectSeparateLineSegments(string b1_FilePath, int len = 10) //len = 10
{
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
	//int len = 60;
	int k = 0;
	int noOfPossiblePoints = b1.rows() - (2 * len);
	Vector3d segL, segS, pointClosest, tmp;


	MatrixXd dist_scoreB1(b1.rows() + 2 * len, 1);
	MatrixXd distScoreOriginalLength(b1.rows(), 1);//(len*2 -1)*noOfAvailableSegs, 1);
	//MatrixXd angle_scoreB1(noOfPossiblePoints, 1);
	Vector3d segS_p1, segS_p2, segL_p1, segL_p2, segS_centerPt(3);
	int t = 0;

	pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_b1_ptr(new pcl::PointCloud<pcl::PointXYZ>);

	pcl::PointCloud<pcl::PointXYZRGB>::Ptr pointCloud_b1_ptr(new pcl::PointCloud<pcl::PointXYZRGB>);

	for (size_t i = 0; i < b1.rows() + 2 * len; i++)
	{
		dist_scoreB1(i, 0) = 0;
	}

	t = 0;
	pcl::PointXYZ p1, p2;
	int pointCount = 0;

	MatrixXd bCombined(b1.rows() + 2 * len, 3);
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


	for (size_t i = 0; i < distScoreOriginalLength.rows(); i++)
	{
		distScoreOriginalLength(i, 0) = dist_scoreB1(i + 10);
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

	findPeaks(in, out);

	if (out[out.size() - 1] == in.size())
	{
		out[out.size() - 1]--;
	}

	bool specialCase = false;
	if (out[0] == 0 && out[out.size() - 1] == in.size() - 1)
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
					writeMatrix_to_XYZ_withNormals(breakLineSeg, outPath + to_string(t + 1) + ".xyz");
					noOfSegmentsDetected++;
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
	writeMatrix_to_XYZ_withNormals(segMatrix, outPath + "1.xyz");

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

		for (size_t i = 0; i < segmentMatrix.rows(); i++)
		{
			smoothedSegment->points.push_back(PointXYZ(segmentMatrix(i, 0), segmentMatrix(i, 1), segmentMatrix(i, 2)));
		}
		smoothedSegment->width = smoothedSegment->points.size();
		smoothedSegment->height = 1;

		for (size_t i = 1; i < smoothedSegment->points.size() - 1; i++)
		{
			// POTA-274: nearestKSearch clamps k to the cloud size and shrinks both
			// result vectors (PCL 1.9 kdtree_flann.hpp:139-143). Walk only what came
			// back: reading the k=20 slots regardless indexed a short chain's heap
			// tail and segfaulted at :2257 (garbage dist <= 1.8 -> garbage index).
			const int nnFound274 = tree_->nearestKSearch(smoothedSegment->points[i], 20, nn_indices, nn_dists);
			for (int j = 0; j < nnFound274; j++)
			{
				if (nn_dists[j] <= 1.8)
				{
					nn_indicesAll.push_back(nn_indices[j]);
				}
				//rawBreaklinePtsInSegment->points.push_back(rawBreaklinePts->points[nn_indices[j]]);
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

	// Headless: disable visualization spinner for breakline preview
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
    std::cout << "[DEBUG] cleanSamples: input pts=" << cloud_OriginalSurface->points.size() << std::endl;

	
	pcl::StatisticalOutlierRemoval<pcl::PointNormal> sor;
	sor.setInputCloud(cloud_OriginalSurface);
    sor.setMeanK(50);
	sor.setStddevMulThresh(9);
    sor.filter(*cloud_filteredB);
    std::cout << "[DEBUG] cleanSamples: after SOR pts=" << cloud_filteredB->points.size() << std::endl;
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
	pcl::io::loadPLYFile(sampledDataWithNormals, *cloud_PointNormals);

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

	b1 = b1.transpose();

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
	pcl::io::loadPLYFile(sampledDataWithNormals, *cloud_PointNormals);

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

    cout << "[DEBUG] processFragmentData: surface=" << surfacePointCloudFilePath
         << " mesh=" << fragmentMeshFilePath << endl;
    cout << "Fragment: " + fragmentMeshFilePath << endl << endl;

    // -------------------- 전처리: 표면 포인트 클라우드 클린업 및 breakline 추출 --------------------
	cout << "Cleaning surface point cloud..." << endl;
    cleanSamples(surfacePointCloudFilePath); // (표면 포인트 클라우드 클린업 함수)
    {
        // Inspect cleaned surface-with-normals cloud
        pcl::PointCloud<pcl::PointNormal>::Ptr surf_norm(new pcl::PointCloud<pcl::PointNormal>);
        std::string cleaned = tempEdgeFolder + std::string("cloud_Surface_AllSamples_Cleaned.pcd");
        if (pcl::io::loadPCDFile(cleaned, *surf_norm) == 0) {
            cout << "[DEBUG] cleaned surface normals pts=" << surf_norm->points.size() << " (" << cleaned << ")" << endl;
        } else {
            cout << "[DEBUG] cleaned surface normals missing: " << cleaned << endl;
        }
    }
    cout << "Estimating patch normals and breaklines..." << endl;
    estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface(tempEdgeFolder + std::string("pointCloudFromMesh.xyz"), false);
    {
        // Inspect CompleteBreakline artifacts
        pcl::PointCloud<pcl::PointXYZ>::Ptr br_xyz(new pcl::PointCloud<pcl::PointXYZ>);
        if (pcl::io::loadPCDFile(tempEdgeFolder + std::string("CompleteBreakline.pcd"), *br_xyz) == 0) {
            cout << "[DEBUG] CompleteBreakline.pcd pts=" << br_xyz->points.size() << endl;
        } else {
            cout << "[DEBUG] CompleteBreakline.pcd missing" << endl;
        }
    }
    cout << "Detecting separate line segments..." << endl;
    detectSeparateLineSegments(tempEdgeFolder + std::string("CompleteBreakline.xyz"));
    {
        // Count segment files produced
        using boost::filesystem::directory_iterator;
        size_t segCount = 0;
        boost::filesystem::path segDir("Segments/");
        if (boost::filesystem::exists(segDir)) {
            for (auto it = directory_iterator(segDir); it != directory_iterator(); ++it) {
                if (boost::filesystem::is_regular_file(*it) && it->path().extension() == ".xyz") segCount++;
            }
        }
        cout << "[DEBUG] Segments/*.xyz files=" << segCount << endl;
    }

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


        cloud_breakLineSeg->points.clear();
        std::cerr << "[DEBUG LOOP] Starting segment processing loop, rows=" << matrix_breakLineSeg.rows()
                  << " cols=" << matrix_breakLineSeg.cols() << std::endl;

        for (size_t i = 0; i < matrix_breakLineSeg.rows() - 1; i++)
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

        // Write with custom PCD writer to include segment header + normals
        writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline);
	std::cout << "[EDGELINE DEBUG] Saving CompleteBreakline PLY in ASCII mode..." << std::endl;
	pcl::io::savePLYFile(plyFilePath, *cloud_CompleteBreakline, false); // ASCII mode
	// Fix cross-device filesystem error: use copy+remove instead of rename
	fs::copy_file(completeBreaklinePath, xyzFilePath, fs::copy_options::overwrite_existing);
	fs::remove(completeBreaklinePath);

    
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
        pcl::io::savePCDFile(currentFileName + "_FracturedSurfacePts.pcd", *cloud_PointsOnFracturedSurfaceNoDuplicates);
        
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
    // Headless: avoid VTK/texture mesh and visualization. Only transform the breakline points.
    if (cloud_BreakLine && !cloud_BreakLine->empty()) {
        pcl::transformPointCloud(*cloud_BreakLine, *cloud_BreakLine, transform);
    }
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
        return 1;
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
