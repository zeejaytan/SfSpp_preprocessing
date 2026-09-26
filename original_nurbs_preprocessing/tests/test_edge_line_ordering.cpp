// Tests for the edge-line ordering seam.
//
// Seam: getPointsInSequence(in, out) -- the public boundary between the
// boundary-detection stage and the ordering stage. Everything asserted
// here is a property of the OUTPUT CLOUD, not of how it was produced, so
// tickets 02 and 03 can rewrite the body freely.
//
// No Google Test: the container has PCL, Eigen and CGAL but no test
// framework, and adding one is a dependency this ticket should not
// introduce. The harness below is a few lines and reports the same
// pass/fail CTest needs.
//
// WHY THESE TESTS ARE CURRENTLY EXPECTED TO FAIL
// ---------------------------------------------
// The current implementation is a non-local nearest-neighbour chain. On
// a boundary cloud containing near-duplicate points it consumes a tight
// cluster and stalls, or jumps between disconnected arcs. The Juglet
// measurements behind that claim: traced length 0.27-2.15x the rim it
// should cover, internal jumps of 10-24 mm against a 0.3 mm median step,
// one sherd reduced to a 3.6 mm stub.
//
// These tests therefore assert the CONTRACT and fail against today's
// code. That is the point of ticket 01: make the defect visible and
// falsifiable from a test, so tickets 02 and 03 can be shown to fix it
// without a cluster pipeline run. They are registered with CTest under
// the DISABLED_ prefix until ticket 02 lands, so the suite stays green
// for everyone else while the failing assertions stay armed and visible
// in the source. See tests/README.md for how to run them and what the
// observed failures were.

#include "../edge_line_ordering.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace {

int g_failures = 0;
int g_checks = 0;

void check(bool condition, const std::string &what)
{
    ++g_checks;
    if (condition) {
        std::printf("    ok   %s\n", what.c_str());
    } else {
        ++g_failures;
        std::printf("    FAIL %s\n", what.c_str());
    }
}

double dist(const pcl::PointXYZ &a, const pcl::PointXYZ &b)
{
    const double dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

double median(std::vector<double> v)
{
    if (v.empty()) return 0.0;
    std::sort(v.begin(), v.end());
    return v[v.size() / 2];
}

pcl::PointCloud<pcl::PointXYZ>::Ptr makeCloud(const std::vector<pcl::PointXYZ> &pts)
{
    auto c = pcl::PointCloud<pcl::PointXYZ>::Ptr(new pcl::PointCloud<pcl::PointXYZ>());
    for (const auto &p : pts) c->points.push_back(p);
    c->width = c->points.size();
    c->height = 1;
    return c;
}

// A clean rim: n points evenly spaced on a circle of the given radius.
// This is the case the method already handles (Pot_A), so it must keep
// working -- a guard against the fix regressing the working sample.
std::vector<pcl::PointXYZ> cleanRim(int n, double radius)
{
    std::vector<pcl::PointXYZ> pts;
    for (int i = 0; i < n; i++) {
        const double t = 2.0 * M_PI * i / n;
        pcl::PointXYZ p;
        p.x = static_cast<float>(radius * std::cos(t));
        p.y = static_cast<float>(radius * std::sin(t));
        p.z = 0.0f;
        pts.push_back(p);
    }
    return pts;
}

// An eroded rim: the clean rim, plus a tight clump of near-duplicate
// points at one location, as a duplicate-dominated boundary detector
// produces. This is the case the Juglet presents and the current
// implementation gets wrong.
std::vector<pcl::PointXYZ> erodedRim(int n, double radius, int clumpSize, double clumpSpread)
{
    std::vector<pcl::PointXYZ> pts = cleanRim(n, radius);
    // Clump around the point at index 0, jittered by a tiny amount.
    for (int i = 0; i < clumpSize; i++) {
        pcl::PointXYZ p;
        const double t = 2.0 * M_PI * i / clumpSize;
        p.x = static_cast<float>(radius * (1.0 + clumpSpread * std::cos(t)));
        p.y = static_cast<float>(radius * (1.0 + clumpSpread * std::sin(t)));
        p.z = static_cast<float>(clumpSpread * 0.01 * i);
        pts.push_back(p);
    }
    return pts;
}

// The property under test: consecutive points in the traversal are
// adjacent along the rim. A derailed or stalled walk shows up as a step
// far larger than the typical spacing -- the 10-24 mm jumps measured on
// the Juglet against a 0.3 mm median step.
void expectNoDerailedJumps(const std::string &name,
                           const std::vector<pcl::PointXYZ> &pts,
                           double maxStepOverMedian)
{
    auto in = makeCloud(pts);
    auto out = pcl::PointCloud<pcl::PointXYZ>::Ptr(new pcl::PointCloud<pcl::PointXYZ>());
    getPointsInSequence(in, out);

    std::vector<double> steps;
    for (size_t i = 1; i < out->points.size(); i++)
        steps.push_back(dist(out->points[i - 1], out->points[i]));

    const double med = median(steps);
    const double worst = steps.empty() ? 0.0 : *std::max_element(steps.begin(), steps.end());
    const double ratio = med > 0.0 ? worst / med : 0.0;

    std::printf("  [%s] in=%zu out=%zu median_step=%.4f worst_step=%.4f ratio=%.1f\n",
                name.c_str(), in->points.size(), out->points.size(), med, worst, ratio);
    check(out->points.size() >= 2, name + ": produced a traversal");
    check(ratio <= maxStepOverMedian,
          name + ": no derailed jump (worst/median " + std::to_string(static_cast<int>(ratio)) +
              " <= " + std::to_string(static_cast<int>(maxStepOverMedian)) + ")");
}

void testCleanRimStaysOrdered()
{
    std::printf("  clean rim, no duplicates (the Pot_A case -- must keep working)\n");
    expectNoDerailedJumps("clean-rim", cleanRim(120, 15.0), 3.0);
}

void testErodedRimWithDuplicatesDoesNotDerail()
{
    std::printf("  eroded rim with a duplicate clump (the Juglet case -- currently broken)\n");
    expectNoDerailedJumps("eroded-rim", erodedRim(120, 15.0, 12, 1e-4), 3.0);
}

void testEveryPointVisitedAtMostOnce()
{
    std::printf("  every input point visited at most once\n");
    const auto pts = erodedRim(120, 15.0, 12, 1e-4);
    auto in = makeCloud(pts);
    auto out = pcl::PointCloud<pcl::PointXYZ>::Ptr(new pcl::PointCloud<pcl::PointXYZ>());
    getPointsInSequence(in, out);

    // Count exact duplicates in the OUTPUT: a repeated point means the
    // walk revisited ground, which no valid traversal does.
    size_t repeats = 0;
    for (size_t i = 0; i < out->points.size(); i++)
        for (size_t j = i + 1; j < out->points.size(); j++)
            if (dist(out->points[i], out->points[j]) == 0.0) { repeats++; break; }

    std::printf("  [%s] in=%zu out=%zu repeated_points=%zu\n", "no-revisit",
                in->points.size(), out->points.size(), repeats);
    check(repeats == 0, "no-revisit: no point appears twice in the traversal");
}

} // namespace

// CTest runs one test per entry, selected by name, so a failure names the
// property that broke instead of reporting one aggregate result.
// With no argument, runs everything (useful when iterating by hand).
int main(int argc, char **argv)
{
    const std::string which = argc > 1 ? argv[1] : "all";
    std::printf("edge_line_ordering tests [%s]\n", which.c_str());

    if (which == "all" || which == "clean-rim")
        testCleanRimStaysOrdered();
    if (which == "all" || which == "eroded-rim")
        testErodedRimWithDuplicatesDoesNotDerail();
    if (which == "all" || which == "no-revisit")
        testEveryPointVisitedAtMostOnce();

    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
