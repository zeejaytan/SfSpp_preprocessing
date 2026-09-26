// Tests for the edge-line ordering seam.
//
// SEAM: getPointsInSequence(in, out) -- the boundary between the boundary
// detection stage and the ordering stage. Every assertion below is a
// property of the OUTPUT CLOUD, so the implementation can be rewritten
// freely. The test compiles edge_line_ordering.cpp, the SAME file the
// pipeline compiles; a test that could pass against different code than
// production runs would be worthless here.
//
// No test framework: the container has PCL, Eigen and CGAL but none, and
// adding one is a dependency this seam should not take. The harness is a
// few lines and reports the pass/fail CTest needs.
//
// WHY COVERAGE IS THE ASSERTION
// -----------------------------
// A traversal of a rim visits essentially every rim point. So the contract
// is: out.size() >= 0.9 * in.size().
//
// An earlier version of this file asserted on the ratio of the largest step
// to the median step, and it PASSED -- while the function was in fact
// discarding 85% of the rim. A walk that stops early takes small steps;
// it does not take large ones. The assertion was measuring the wrong
// failure and would not have caught the real one. Coverage is the property
// that actually distinguishes a rim walk from a stub.
//
// Thresholds are measured, not chosen. Clean synthetic rings give
// coverage 1.000; the real Juglet cloud gives 0.153; a ring with the
// Juglet's measured 20x spacing variation gives 0.153 as well. The 0.9
// bound sits in a wide empty gap between those populations, so it is not
// a tuned number that happens to separate them.
//
// DISABLED_ prefix: a test that fails is registered disabled so the suite
// stays green, and the prefix marks exactly the known-broken behaviour.
// Tests that PASS today are enabled. The prefix is removed by the ticket
// that turns that test green, never in a batch. Current state:
//
//   enabled   clean-rim          the case that already works (Pot_A-like)
//   enabled   no-revisit         invariant, cheap
//   disabled  juglet-boundary    THE DEFECT, on a real sherd edge
//   disabled  dense-patch        the same defect from a synthetic cause
//   disabled  offplane-scatter   a second, independent trigger

#include "../edge_line_ordering.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#ifndef JUGLET_FIXTURE_DIR
#error "JUGLET_FIXTURE_DIR must be defined by the build"
#endif

namespace {

int g_failures = 0;
int g_checks = 0;

void check(bool ok, const std::string &what)
{
    ++g_checks;
    std::printf("    %s %s\n", ok ? "ok  " : "FAIL", what.c_str());
    if (!ok) ++g_failures;
}

typedef std::vector<pcl::PointXYZ> PtList;

double dist(const pcl::PointXYZ &a, const pcl::PointXYZ &b)
{
    const double dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

pcl::PointCloud<pcl::PointXYZ>::Ptr toCloud(const PtList &pts)
{
    auto c = pcl::PointCloud<pcl::PointXYZ>::Ptr(new pcl::PointCloud<pcl::PointXYZ>());
    c->points = pts;
    c->width = static_cast<int>(pts.size());
    c->height = 1;
    return c;
}

// Reference length for the rim, computed from the cloud alone: the total
// length of its minimum spanning tree. For points sampled along a smooth
// 1-D closed curve this tracks the curve length closely -- measured at
// within 1.7% on circles of radius 6.3, 15 and 40 mm. Prim's algorithm,
// O(n^2), which is nothing at these sizes and needs no dependency.
double mstLength(const PtList &pts)
{
    const size_t n = pts.size();
    if (n < 2) return 0.0;
    const double kInf = std::numeric_limits<double>::infinity();
    std::vector<double> best(n, kInf);
    std::vector<bool> done(n, false);
    best[0] = 0.0;
    double total = 0.0;
    for (size_t step = 0; step < n; ++step) {
        size_t pick = n;
        for (size_t i = 0; i < n; ++i)
            if (!done[i] && (pick == n || best[i] < best[pick])) pick = i;
        if (pick == n || !std::isfinite(best[pick])) break;
        done[pick] = true;
        total += best[pick];
        for (size_t i = 0; i < n; ++i)
            if (!done[i]) {
                const double d = dist(pts[pick], pts[i]);
                if (d < best[i]) best[i] = d;
            }
    }
    return total;
}

struct Traversal {
    size_t n_in = 0;
    size_t n_out = 0;
    double coverage = 0.0;
    double traced_mm = 0.0;
    double reference_mm = 0.0;
    double traced_over_reference = 0.0;
    double median_step_mm = 0.0;
    double worst_step_mm = 0.0;
    size_t repeats = 0;
};

Traversal runWalk(const PtList &pts)
{
    Traversal t;
    t.n_in = pts.size();
    auto in = toCloud(pts);
    auto out = pcl::PointCloud<pcl::PointXYZ>::Ptr(new pcl::PointCloud<pcl::PointXYZ>());
    getPointsInSequence(in, out);

    t.n_out = out->points.size();
    t.coverage = t.n_in ? static_cast<double>(t.n_out) / static_cast<double>(t.n_in) : 0.0;

    std::vector<double> steps;
    for (size_t i = 1; i < out->points.size(); ++i)
        steps.push_back(dist(out->points[i - 1], out->points[i]));
    for (double s : steps) t.traced_mm += s;
    if (!steps.empty()) {
        std::vector<double> sorted = steps;
        std::sort(sorted.begin(), sorted.end());
        t.median_step_mm = sorted[sorted.size() / 2];
        t.worst_step_mm = sorted.back();
    }

    t.reference_mm = mstLength(pts);
    t.traced_over_reference =
        t.reference_mm > 0.0 ? t.traced_mm / t.reference_mm : 0.0;

    for (size_t i = 0; i < out->points.size(); ++i)
        for (size_t j = i + 1; j < out->points.size(); ++j)
            if (dist(out->points[i], out->points[j]) == 0.0) { ++t.repeats; break; }

    return t;
}

void report(const std::string &name, const Traversal &t)
{
    std::printf("  [%-18s] in=%4zu out=%4zu cov=%.3f traced=%7.2fmm "
                "ref=%7.2fmm traced/ref=%.3f med_step=%.4f worst=%.4f repeats=%zu\n",
                name.c_str(), t.n_in, t.n_out, t.coverage, t.traced_mm,
                t.reference_mm, t.traced_over_reference, t.median_step_mm,
                t.worst_step_mm, t.repeats);
}

std::string num(double v, int dp = 3)
{
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%.*f", dp, v);
    return std::string(buf);
}

// The contract, stated once.
void expectFullRim(const std::string &name, const PtList &pts)
{
    const Traversal t = runWalk(pts);
    report(name, t);
    check(t.coverage >= 0.9,
          name + ": visits the rim -- coverage " + num(t.coverage) + " >= 0.900"
              + (t.coverage < 0.9
                     ? "  (walk returned " + num(static_cast<double>(t.n_out), 0) +
                           " of " + num(static_cast<double>(t.n_in), 0) + " points)"
                     : ""));
    check(t.traced_over_reference >= 0.3,
          name + ": traces the rim -- length/ref " + num(t.traced_over_reference) +
              " >= 0.300");
}

// --- inputs -------------------------------------------------------------

// A real sherd edge, 59 points, written by the pipeline. See the file's
// header for provenance and, importantly, for its scope: this is ONE sherd
// of nine, not a summary of the Juglet.
bool loadFixture(PtList &out)
{
    std::ifstream in(std::string(JUGLET_FIXTURE_DIR) + "/juglet_boundary_59.txt");
    if (!in) return false;
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::istringstream ss(line);
        double x, y, z;
        if (!(ss >> x >> y >> z)) continue;
        pcl::PointXYZ p;
        p.x = static_cast<float>(x);
        p.y = static_cast<float>(y);
        p.z = static_cast<float>(z);
        out.push_back(p);
    }
    return out.size() == 59;
}

// Evenly sampled circle. The case the method already handles, so it must
// keep working: a guard against a fix that breaks the working sample.
PtList cleanRim(int n, double radius)
{
    PtList pts;
    for (int i = 0; i < n; ++i) {
        const double t = 2.0 * M_PI * i / n;
        pcl::PointXYZ p;
        p.x = static_cast<float>(radius * std::cos(t));
        p.y = static_cast<float>(radius * std::sin(t));
        p.z = 0.0f;
        pts.push_back(p);
    }
    return pts;
}

// A circle with a dense patch: `frac` of the points crowded into a small
// arc, the rest spread over the remainder. Models an eroded rim that is
// densely sampled in one stretch.
//
// RECONSTRUCTION -- OURS, NOT THE AUTHORS'. The paper says nothing about
// sampling density. This case is built to match a property MEASURED on the
// real Juglet cloud (20x variation in local point spacing), and it is
// labelled as a reconstruction wherever it is reported.
PtList densePatchRim(int n, double radius, double frac, double squeeze,
                     unsigned seed)
{
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> jitter(0.0, 2 * M_PI);
    const int n_dense = std::max(6, static_cast<int>(n * frac));
    const int n_sparse = n - n_dense;
    const double dense_arc = (2.0 * M_PI) / squeeze;
    PtList pts;
    for (int i = 0; i < n_dense; ++i) {
        const double t = dense_arc * i / n_dense;
        pcl::PointXYZ p;
        p.x = static_cast<float>(radius * std::cos(t));
        p.y = static_cast<float>(radius * std::sin(t));
        p.z = 0.0f;
        pts.push_back(p);
    }
    for (int i = 0; i < n_sparse; ++i) {
        const double t = dense_arc + (2.0 * M_PI - dense_arc) * i / n_sparse;
        pcl::PointXYZ p;
        p.x = static_cast<float>(radius * std::cos(t));
        p.y = static_cast<float>(radius * std::sin(t));
        p.z = 0.0f;
        pts.push_back(p);
    }
    const double rot = jitter(rng);
    for (auto &p : pts) {
        const double x = p.x, y = p.y;
        p.x = static_cast<float>(x * std::cos(rot) - y * std::sin(rot));
        p.y = static_cast<float>(x * std::sin(rot) + y * std::cos(rot));
    }
    return pts;
}

// A circle whose points scatter off the rim plane by `sigma_mm`. Models the
// roughness of a hand-made pot edge.
//
// RECONSTRUCTION -- OURS, NOT THE AUTHORS', same caveat as densePatchRim.
PtList offplaneRim(int n, double radius, double sigma_mm, unsigned seed)
{
    std::mt19937 rng(seed);
    std::normal_distribution<double> gauss(0.0, sigma_mm);
    PtList pts;
    for (int i = 0; i < n; ++i) {
        const double t = 2.0 * M_PI * i / n;
        pcl::PointXYZ p;
        p.x = static_cast<float>(radius * std::cos(t));
        p.y = static_cast<float>(radius * std::sin(t));
        p.z = static_cast<float>(gauss(rng));
        pts.push_back(p);
    }
    return pts;
}

// --- tests --------------------------------------------------------------

void testCleanRim()
{
    std::printf("  even circle -- the case that already works, must keep working\n");
    PtList pts = cleanRim(400, 15.0);
    const Traversal t = runWalk(pts);
    report("clean-rim", t);
    check(t.coverage >= 0.9,
          "clean-rim: visits the rim -- coverage " + num(t.coverage) + " >= 0.900");
    check(t.traced_over_reference >= 0.3,
          "clean-rim: traces the rim -- length/ref " + num(t.traced_over_reference) +
              " >= 0.300");
}

void testJugletBoundary()
{
    std::printf("  REAL Juglet sherd edge, 59 points (tests/data)\n");
    PtList pts;
    if (!loadFixture(pts)) {
        check(false, "juglet-boundary: fixture tests/data/juglet_boundary_59.txt "
                     "readable and holds 59 points");
        return;
    }
    expectFullRim("juglet-boundary", pts);
}

void testDensePatch()
{
    std::printf("  dense patch on a rim (reconstruction -- ours, not the authors')\n");
    expectFullRim("dense-patch", densePatchRim(59, 15.0, 0.15, 40.0, 1));
}

void testOffplaneScatter()
{
    std::printf("  off-plane scatter on a rim (reconstruction -- ours)\n");
    expectFullRim("offplane-scatter", offplaneRim(400, 15.0, 0.6, 7));
}

void testNoRevisit()
{
    std::printf("  no point appears twice in the traversal\n");
    PtList pts;
    if (!loadFixture(pts)) pts = cleanRim(200, 15.0);
    const Traversal t = runWalk(pts);
    report("no-revisit", t);
    check(t.repeats == 0, "no-revisit: no point appears twice -- repeats " +
                              num(static_cast<double>(t.repeats), 0) + " == 0");
}

} // namespace

// One test per CTest entry, selected by name, so a failure names the
// property that broke instead of one aggregate result. No argument runs all.
int main(int argc, char **argv)
{
    const std::string which = argc > 1 ? argv[1] : "all";
    std::printf("edge_line_ordering tests [%s]\n", which.c_str());

    if (which == "all" || which == "clean-rim") testCleanRim();
    if (which == "all" || which == "juglet-boundary") testJugletBoundary();
    if (which == "all" || which == "dense-patch") testDensePatch();
    if (which == "all" || which == "offplane-scatter") testOffplaneScatter();
    if (which == "all" || which == "no-revisit") testNoRevisit();

    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
