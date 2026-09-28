// Ticket 04 implementation: put the interior surface first.
//
// See surface_classify.h for the paper reference. This file is the glue
// between that pure function and the pipeline: it loads the two Surface
// xyz files (x y z nx ny nz) and the axis file (one point + one direction),
// runs the vote, and -- only when Surface_1 wins -- exchanges the contents
// of the two input files so that the downstream code, which builds
// Breakline_0 from Surface_0, traces the interior wall.
//
// Exchange, not overwrite: the ablation that demonstrated the fix copied
// Surface_1 over Surface_0 and left both paths holding the same content,
// so Breakline_1 was a duplicate. Exchanging keeps both breaklines tracing
// distinct walls.
//
// A separate translation unit so the whole of ticket 04 is one removable
// file plus the call-site block marked SFS-T04.

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "surface_classify.h"

namespace {

bool load_xyz6(const std::string& path, std::vector<sfspp::Vec3>& pts,
               std::vector<sfspp::Vec3>& nrm, std::string& why)
{
    std::ifstream in(path);
    if (!in) {
        why = "cannot open " + path;
        return false;
    }
    std::string line;
    std::size_t skipped = 0;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::istringstream ss(line);
        double x, y, z, nx, ny, nz;
        if (!(ss >> x >> y >> z)) {
            if (++skipped < 4) continue;
            why = "unparseable rows in " + path;
            return false;
        }
        if (!(ss >> nx >> ny >> nz)) {
            // xyz-only row: a point with no normal direction. The vote
            // needs normals, so these cannot count either way.
            continue;
        }
        pts.push_back(sfspp::Vec3{ x, y, z });
        nrm.push_back(sfspp::Vec3{ nx, ny, nz });
    }
    if (pts.empty()) {
        why = "no usable points in " + path;
        return false;
    }
    return true;
}

bool load_axis(const std::string& path, sfspp::AxisLine& axis, std::string& why)
{
    std::ifstream in(path);
    if (!in) {
        why = "cannot open " + path;
        return false;
    }
    double px, py, pz, dx, dy, dz;
    // First non-comment row: axis point + axis direction.
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::istringstream ss(line);
        if (ss >> px >> py >> pz >> dx >> dy >> dz) break;
        why = "axis file needs 'px py pz dx dy dz' in " + path;
        return false;
    }
    const double dl = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (!(dl > 1e-12)) {
        why = "degenerate axis direction in " + path;
        return false;
    }
    axis.point = sfspp::Vec3{ px, py, pz };
    axis.direction = sfspp::Vec3{ dx / dl, dy / dl, dz / dl };
    return true;
}

bool exchange_files(const std::string& a, const std::string& b, std::string& why)
{
    // Exchange via a temp sibling so a crash mid-write cannot lose both.
    const std::string tmp = a + ".sfs-t04-tmp";
    std::ifstream sa(a, std::ios::binary);
    std::ifstream sb(b, std::ios::binary);
    if (!sa || !sb) {
        why = "cannot reopen inputs for exchange";
        return false;
    }
    std::string ca((std::istreambuf_iterator<char>(sa)), std::istreambuf_iterator<char>());
    std::string cb((std::istreambuf_iterator<char>(sb)), std::istreambuf_iterator<char>());
    sa.close();
    sb.close();
    // tmp holds A's content; then A <- B's content, B <- tmp. The previous
    // version of this function wrote A <- A and B <- B (each file onto
    // itself) while logging success -- caught only because the fetched
    // breaklines were byte-identical to baseline on the exchanged pieces.
    // Never trust this function's log line; verify with cmp.
    {
        std::ofstream t(tmp, std::ios::binary | std::ios::trunc);
        if (!t) {
            why = "cannot write " + tmp;
            return false;
        }
        t << ca;
    }
    {
        std::ofstream oa(a, std::ios::binary | std::ios::trunc);
        if (!oa) {
            why = "cannot write " + a;
            std::remove(tmp.c_str());
            return false;
        }
        oa << cb;
    }
    {
        std::ofstream ob(b, std::ios::binary | std::ios::trunc);
        if (!ob) {
            why = "cannot write " + b;
            return false;
        }
        std::ifstream t(tmp, std::ios::binary);
        ob << t.rdbuf();
    }
    std::remove(tmp.c_str());
    // Verify the exchange took: re-read both and require them swapped.
    {
        std::ifstream va(a, std::ios::binary);
        std::ifstream vb(b, std::ios::binary);
        const std::string na((std::istreambuf_iterator<char>(va)),
                             std::istreambuf_iterator<char>());
        const std::string nb((std::istreambuf_iterator<char>(vb)),
                             std::istreambuf_iterator<char>());
        if (na != cb || nb != ca) {
            why = "post-exchange verification failed for " + a + " / " + b;
            return false;
        }
    }
    return true;
}

}  // namespace

// Returns true when the classification ran. Exchanges the two files only
// when Surface_1 wins the interior vote. All outcomes are logged; the
// caller falls back to historic order on false.
bool ticket04_place_interior_first(const std::string& surf0_path,
                                   const std::string& surf1_path,
                                   const std::string& axis_path)
{
    std::vector<sfspp::Vec3> p0, n0, p1, n1;
    sfspp::AxisLine axis;
    std::string why;
    if (!load_xyz6(surf0_path, p0, n0, why) ||
        !load_xyz6(surf1_path, p1, n1, why) || !load_axis(axis_path, axis, why)) {
        std::cout << "[SFS-T04] unavailable (" << why << ")" << std::endl;
        return false;
    }
    std::size_t win = 0, lose = 0;
    // 5 mm: the same eps the unit test calibrates against, and well under
    // the ~70 mm vessel scale, so a ray that "meets" the axis genuinely
    // points at it rather than passing nearby by accident.
    const bool s0_interior = sfspp::first_is_interior(
        p0.data(), n0.data(), p0.size(), p1.data(), n1.data(), p1.size(),
        axis, 5.0, &win, &lose);
    const std::size_t total = win + lose;
    std::cout << "[SFS-T04] vote: Surface_0 interior-consistent with "
              << (s0_interior ? "WINNING" : "losing") << " configuration "
              << win << " vs " << lose << " of " << total << " sampled points"
              << std::endl;
    if (s0_interior) {
        std::cout << "[SFS-T04] keeping order: Surface_0 is interior"
                  << std::endl;
        return true;
    }
    if (!exchange_files(surf0_path, surf1_path, why)) {
        std::cout << "[SFS-T04] Surface_1 won but exchange failed (" << why
                  << ") -- keeping historic order" << std::endl;
        return false;
    }
    std::cout << "[SFS-T04] exchanged: interior surface now feeds Breakline_0"
              << std::endl;
    return true;
}
