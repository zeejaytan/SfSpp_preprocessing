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

#include <cmath>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <boost/filesystem.hpp>

#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

// Minimum rim length worth appending. The measured fracture rims that
// matter run 69-240 points; but the 1.5mm tolerance also shatters
// unclustered zones into ~10-point fragments (pieces 1 and 3 emitted 8+2
// of them in the first full run), which are noise at the gate, not rims.
// 30 is far below any real rim and far above the fragments. The first
// version of this constant was 8, which let the fragments through -- caught
// by reading the append log, not the gate score.
static const std::size_t kMinPatchRimPoints = 30;

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
        // SFS-T23b (pota-repro ticket 23): the appended points previously
        // carried whatever curvature the Decorative PCDs held (uninitialized
        // memory from the mesh stage, run-varying ~1e32 garbage), while the
        // assembler loads column 7 into feature_[6] and scores triangle
        // curvature coherence off it -- a real E2E nondeterminism vector.
        // Compute the SAME |dN/ds| curvature the wall-rim path uses
        // (edgeline_extraction_headless.cpp fractured-surface loop: central
        // difference of neighbour normals over arc length, capped at 1.0,
        // endpoints 0.01), so patch rows are consistent with wall rows.
        const std::size_t n = rim->points.size();
        for (std::size_t i = 0; i < n; ++i) {
            pcl::PointNormal p = rim->points[i];
            double curvature = 0.01;
            if (i > 0 && i + 1 < n) {
                const pcl::PointNormal& a = rim->points[i - 1];
                const pcl::PointNormal& b = rim->points[i + 1];
                const double dnx = b.normal_x - a.normal_x;
                const double dny = b.normal_y - a.normal_y;
                const double dnz = b.normal_z - a.normal_z;
                const double dpx = b.x - a.x;
                const double dpy = b.y - a.y;
                const double dpz = b.z - a.z;
                const double nl = std::sqrt(dnx * dnx + dny * dny + dnz * dnz);
                const double al = std::sqrt(dpx * dpx + dpy * dpy + dpz * dpz);
                if (al > 1e-6) {
                    curvature = nl / al;
                    if (curvature > 1.0) curvature = 1.0;
                }
            }
            p.curvature = static_cast<float>(curvature);
            cloud->points.push_back(p);
        }
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
