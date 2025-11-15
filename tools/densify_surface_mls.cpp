// Densify an XYZ+Normals surface using PCL Moving Least Squares upsampling.
// Usage: densify_surface_mls <in.xyz> <out.xyz> <target_count>

#include <pcl/io/pcd_io.h>
#include <pcl/io/ply_io.h>
#include <pcl/point_types.h>
#include <pcl/filters/random_sample.h>
#include <pcl/surface/mls.h>
#include <pcl/common/common.h>
#include <fstream>
#include <sstream>
#include <random>
#include <iostream>

using PN = pcl::PointNormal;
using P = pcl::PointXYZ;

static bool load_xyz_normals(const std::string& path, pcl::PointCloud<PN>::Ptr cloud) {
  std::ifstream in(path);
  if (!in) return false;
  cloud->clear();
  PN pt; double x,y,z,nx,ny,nz; std::string line;
  while (std::getline(in, line)) {
    if (line.empty()) continue;
    std::istringstream ss(line);
    if (!(ss >> x >> y >> z >> nx >> ny >> nz)) continue;
    pt.x = static_cast<float>(x); pt.y = static_cast<float>(y); pt.z = static_cast<float>(z);
    pt.normal_x = static_cast<float>(nx); pt.normal_y = static_cast<float>(ny); pt.normal_z = static_cast<float>(nz);
    cloud->push_back(pt);
  }
  cloud->width = cloud->size(); cloud->height = 1; cloud->is_dense = false;
  return !cloud->empty();
}

static bool save_xyz_normals(const std::string& path, const pcl::PointCloud<PN>::Ptr& cloud) {
  std::ofstream out(path);
  if (!out) return false;
  out.setf(std::ios::fixed); out.precision(6);
  for (const auto& p : cloud->points) {
    out << p.x << ' ' << p.y << ' ' << p.z << ' ' << p.normal_x << ' ' << p.normal_y << ' ' << p.normal_z << '\n';
  }
  return true;
}

static void save_ply_sidecar(const std::string& xyz_path, const pcl::PointCloud<PN>::Ptr& cloud) {
  // Save PLY next to XYZ if possible
  std::string ply = xyz_path;
  auto pos = ply.find_last_of('.');
  if (pos != std::string::npos) ply = ply.substr(0, pos);
  ply += ".ply";
  try {
    pcl::io::savePLYFile(ply, *cloud, true);
  } catch (...) {
    // ignore
  }
}

int main(int argc, char** argv) {
  if (argc < 4) {
    std::cerr << "Usage: " << argv[0] << " <in.xyz> <out.xyz> <target_count>" << std::endl;
    return 1;
  }
  std::string in_path = argv[1];
  std::string out_path = argv[2];
  const int target = std::max(1, std::atoi(argv[3]));

  pcl::PointCloud<PN>::Ptr in_cloud(new pcl::PointCloud<PN>);
  if (!load_xyz_normals(in_path, in_cloud)) {
    std::cerr << "Failed to load XYZ normals: " << in_path << std::endl;
    return 2;
  }

  // Convert to XYZ for MLS input
  pcl::PointCloud<P>::Ptr xyz(new pcl::PointCloud<P>);
  xyz->reserve(in_cloud->size());
  for (const auto& pn : in_cloud->points) {
    P p; p.x = pn.x; p.y = pn.y; p.z = pn.z; xyz->push_back(p);
  }
  xyz->width = xyz->size(); xyz->height = 1;

  // Compute bounding box diagonal as scale
  P minp, maxp; pcl::getMinMax3D(*xyz, minp, maxp);
  const double dx = maxp.x - minp.x, dy = maxp.y - minp.y, dz = maxp.z - minp.z;
  const double diag = std::sqrt(dx*dx + dy*dy + dz*dz);

  // MLS parameters (heuristics)
  pcl::MovingLeastSquares<P, PN> mls;
  mls.setPolynomialOrder(2);
  mls.setComputeNormals(true);
  mls.setInputCloud(xyz);
  double search_radius = std::max(1e-6, 0.01 * diag);
  mls.setSearchRadius(search_radius);
  mls.setUpsamplingMethod(pcl::MovingLeastSquares<P, PN>::SAMPLE_LOCAL_PLANE);

  // Iteratively refine step size to approach target count
  double step = std::max(1e-6, 0.005 * diag);
  double up_radius = 2.0 * step;

  pcl::PointCloud<PN>::Ptr out(new pcl::PointCloud<PN>);
  int iter = 0; const int max_iter = 12;
  while (iter < max_iter) {
    mls.setUpsamplingRadius(up_radius);
    mls.setUpsamplingStepSize(step);
    out->clear();
    mls.process(*out);
    if ((int)out->size() >= target) break;
    // too few points → increase density by reducing step
    step *= 0.6; if (step < 1e-6) step = 1e-6;
    up_radius = std::max(up_radius*0.8, step*1.5);
    iter++;
  }

  // If we overshot, randomly downsample to target exactly
  if ((int)out->size() > target) {
    pcl::RandomSample<PN> rs; rs.setInputCloud(out); rs.setSample(target);
    pcl::PointCloud<PN>::Ptr tmp(new pcl::PointCloud<PN>);
    rs.filter(*tmp); out = tmp;
  }

  if (!save_xyz_normals(out_path, out)) {
    std::cerr << "Failed to save: " << out_path << std::endl;
    return 3;
  }
  save_ply_sidecar(out_path, out);
  std::cout << "Input=" << in_cloud->size() << " Output=" << out->size() << " Target=" << target
            << " step=" << step << " up_radius=" << up_radius << " search_radius=" << search_radius << std::endl;
  return 0;
}
