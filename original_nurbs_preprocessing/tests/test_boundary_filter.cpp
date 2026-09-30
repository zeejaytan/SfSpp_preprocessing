// Tests for the boundary noise filter seam (ticket 05).
//
// Every assertion is on the RETURNED cloud, never on log text. The test
// calls filterBoundaryNoise -- the same function the pipeline calls.

#include "../boundary_filter.h"

#include <cmath>
#include <cstdio>
#include <string>

namespace {

int g_failures = 0;
int g_checks = 0;

void check(bool ok, const std::string &what)
{
    ++g_checks;
    std::printf("    %s %s\n", ok ? "ok  " : "FAIL", what.c_str());
    if (!ok) ++g_failures;
}

// 60-point circle at r=15mm (2mm spacing, production-like) plus one
// gross outlier 100mm off the rim.
pcl::PointCloud<pcl::PointXYZ>::Ptr circle_with_outlier()
{
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(
        new pcl::PointCloud<pcl::PointXYZ>);
    for (int i = 0; i < 60; ++i) {
        const double t = 2.0 * M_PI * i / 60;
        pcl::PointXYZ p;
        p.x = 15.0 * std::cos(t);
        p.y = 15.0 * std::sin(t);
        p.z = 0.0;
        cloud->points.push_back(p);
    }
    pcl::PointXYZ far;
    far.x = 100.0;
    far.y = -100.0;
    far.z = 50.0;
    cloud->points.push_back(far);
    cloud->width = cloud->points.size();
    cloud->height = 1;
    return cloud;
}

bool has_point_near(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud,
                    float x, float y, float z, float tol)
{
    for (const auto &p : cloud->points) {
        const float dx = p.x - x, dy = p.y - y, dz = p.z - z;
        if (dx * dx + dy * dy + dz * dz < tol * tol) return true;
    }
    return false;
}

void test_gross_outlier_dropped_circle_kept()
{
    std::printf("  gross-outlier: circle kept, outlier dropped\n");
    pcl::PointCloud<pcl::PointXYZ>::Ptr in = circle_with_outlier();
    pcl::PointCloud<pcl::PointXYZ>::Ptr out(
        new pcl::PointCloud<pcl::PointXYZ>);
    // 4mm radius, 3 neighbors: circle points (~1.6mm spacing) survive
    // with margin, the lone far point cannot.
    const std::size_t kept = filterBoundaryNoise(in, out, 4.0, 3);
    check(kept == 60, "60 circle points kept");
    check(out->points.size() == 60, "output holds exactly the circle");
    check(!has_point_near(out, 100.0f, -100.0f, 50.0f, 1.0f),
          "gross outlier is gone");
    check(has_point_near(out, 15.0f, 0.0f, 0.0f, 0.5f),
          "rim point (15,0,0) survives");
}

void test_empty_input_does_not_crash()
{
    std::printf("  empty: no crash, empty out\n");
    pcl::PointCloud<pcl::PointXYZ>::Ptr in(
        new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PointCloud<pcl::PointXYZ>::Ptr out(
        new pcl::PointCloud<pcl::PointXYZ>);
    const std::size_t kept = filterBoundaryNoise(in, out, 3.0, 3);
    check(kept == 0, "kept count is 0");
    check(out->points.empty(), "output is empty");
}

} // namespace

int main(int argc, char **argv)
{
    const std::string which = argc > 1 ? argv[1] : "all";
    std::printf("boundary_filter tests [%s]\n", which.c_str());

    if (which == "all" || which == "gross-outlier")
        test_gross_outlier_dropped_circle_kept();
    if (which == "all" || which == "empty")
        test_empty_input_does_not_crash();

    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
