// Generate unclustered.ply and SampledWithNormals.ply for a Pot piece
// Input: Temp/Data/Pot_A/Pot_A_Piece_XX_Point.pcd
// Output:
//   Temp/Data/Pot_A/Pot_A_Piece_XX_unclustered.ply (xyz only)
//   Temp/Data/Pot_A/Pot_A_Piece_XX_SampledWithNormals.ply (xyz + normals)

#include <pcl/io/pcd_io.h>
#include <pcl/io/ply_io.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/features/normal_3d_omp.h>
#include <pcl/console/print.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <piece_id (01..40)> [leaf=1.0]" << std::endl;
    return 1;
  }
  std::string pid = argv[1];
  float leaf = (argc > 2) ? std::atof(argv[2]) : 1.0f;

  std::string base = "Temp/Data/Pot_A/Pot_A_Piece_" + pid;
  std::string in_pcd = base + "_Point.pcd";
  std::string out_uncl = base + "_unclustered.ply";
  std::string out_norm = base + "_SampledWithNormals.ply";

  pcl::console::print_highlight("Loading %s\n", in_pcd.c_str());
  pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
  if (pcl::io::loadPCDFile(in_pcd, *cloud) != 0) {
    pcl::console::print_error("Failed to read %s\n", in_pcd.c_str());
    return 2;
  }
  pcl::console::print_info("Loaded %zu points\n", cloud->size());

  // Downsample to manageable size
  pcl::PointCloud<pcl::PointXYZ>::Ptr ds(new pcl::PointCloud<pcl::PointXYZ>);
  pcl::VoxelGrid<pcl::PointXYZ> vg;
  vg.setInputCloud(cloud);
  vg.setLeafSize(leaf, leaf, leaf);
  vg.filter(*ds);
  if (ds->empty()) ds = cloud; // fallback
  pcl::console::print_info("Downsampled to %zu points (leaf=%.3f)\n", ds->size(), leaf);

  // Save unclustered (xyz only)
  if (pcl::io::savePLYFile(out_uncl, *ds, true) != 0) {
    pcl::console::print_error("Failed to write %s\n", out_uncl.c_str());
    return 3;
  }

  // Estimate normals
  pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
  pcl::NormalEstimationOMP<pcl::PointXYZ, pcl::Normal> ne;
  ne.setInputCloud(ds);
  pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
  ne.setSearchMethod(tree);
  ne.setKSearch(20);
  ne.compute(*normals);

  // Concatenate
  pcl::PointCloud<pcl::PointNormal>::Ptr with_normals(new pcl::PointCloud<pcl::PointNormal>);
  pcl::concatenateFields(*ds, *normals, *with_normals);

  // Save PLY with normals
  if (pcl::io::savePLYFile(out_norm, *with_normals, true) != 0) {
    pcl::console::print_error("Failed to write %s\n", out_norm.c_str());
    return 4;
  }

  pcl::console::print_info("Wrote:\n  %s\n  %s\n", out_uncl.c_str(), out_norm.c_str());
  return 0;
}
