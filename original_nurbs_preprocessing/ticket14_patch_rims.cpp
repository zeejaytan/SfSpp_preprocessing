// Ticket 14 implementation: append fracture-zone patch rims to Breakline_0.
//
// See the call site in edgeline_extraction_headless.cpp (SFS-T14) for why.
// The mesh stage persists one ordered rim per unclustered patch
// (<piece>_unclustered.plyDecorative_<t>.pcd) with mesh normals attached.
// This loads those files for the current piece and appends each rim as one
// more segment of the Breakline_0 cloud, with a segment-index entry to
// match. Existing segments are untouched: this only adds.
//
// A separate translation unit so the whole of ticket 14's edgeline side is
// one removable file plus the call-site block.

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <boost/filesystem.hpp>

#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

// Minimum rim length worth appending. Below this the ordering is
// meaningless and the points are noise at the gate. The measured patch
// rims run 69-134 points; 8 is far below any of them, so it only excludes
// degenerate output, never a real rim.
static const std::size_t kMinPatchRimPoints = 8;

void ticket14_append_patch_rims(
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud,
    std::vector<std::string>& seg_index,
    const std::string& surface_dir, const std::string& piece_key)
{
    namespace bfs = boost::filesystem;
    const std::string prefix = piece_key + "_unclustered.plyDecorative_";
    std::vector<std::string> rim_files;
    try {
        bfs::directory_iterator end;
        for (bfs::directory_iterator it(surface_dir); it != end; ++it) {
            const std::string name = it->path().filename().string();
            if (name.compare(0, prefix.size(), prefix) == 0 &&
                name.size() > 4 &&
                name.compare(name.size() - 4, 4, ".pcd") == 0) {
                rim_files.push_back(it->path().string());
            }
        }
    } catch (const std::exception& e) {
        std::cout << "[SFS-T14] cannot list " << surface_dir << " ("
                  << e.what() << ") -- no patch rims appended" << std::endl;
        return;
    }
    std::sort(rim_files.begin(), rim_files.end());
    if (rim_files.empty()) {
        std::cout << "[SFS-T14] no Decorative rim files for " << piece_key
                  << " -- Breakline_0 unchanged" << std::endl;
        return;
    }
    for (const std::string& path : rim_files) {
        pcl::PointCloud<pcl::PointNormal>::Ptr rim(
            new pcl::PointCloud<pcl::PointNormal>);
        // PointNormal load first (the mesh-normalled form). An xyz-only
        // file from a mesh without normals fails here and is skipped with
        // the reason logged: silent zero normals would score nothing and
        // hide the gap.
        if (pcl::io::loadPCDFile<pcl::PointNormal>(path, *rim) == -1 ||
            rim->points.empty()) {
            std::cout << "[SFS-T14] cannot load as PointNormal, skipping: "
                      << path << std::endl;
            continue;
        }
        bool any_normal = false;
        for (const auto& p : rim->points) {
            if (p.normal_x != 0.0f || p.normal_y != 0.0f || p.normal_z != 0.0f) {
                any_normal = true;
                break;
            }
        }
        if (!any_normal) {
            std::cout << "[SFS-T14] rim has no normals, skipping: " << path
                      << std::endl;
            continue;
        }
        if (rim->points.size() < kMinPatchRimPoints) {
            std::cout << "[SFS-T14] rim too short ("
                      << rim->points.size() << " pts), skipping: " << path
                      << std::endl;
            continue;
        }
        // Segment index is 1-based and contiguous: new segment starts after
        // the last existing point.
        const int start = static_cast<int>(cloud->points.size()) + 1;
        for (const auto& p : rim->points) cloud->points.push_back(p);
        const int end = static_cast<int>(cloud->points.size());
        std::ostringstream ss;
        ss << start << " " << end << " 1";
        seg_index.push_back(ss.str());
        std::cout << "[SFS-T14] appended " << rim->points.size()
                  << " fracture-rim points as segment " << start << ".."
                  << end << " from " << path << std::endl;
    }
    cloud->width = cloud->points.size();
    cloud->height = 1;
}
