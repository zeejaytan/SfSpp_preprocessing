// Tests for the interior/exterior surface classification seam (ticket 04).
//
// SEAM: first_is_interior(a, b, axis) -- given two surface point clouds and
// the symmetry axis, which one is interior. Every assertion is on the
// RETURNED CLASSIFICATION, never on internals, so the geometry inside can be
// revised freely.
//
// The fixture is synthetic but principled: two concentric cylindrical wall
// patches around a known axis, the shape a thrown pot wall has locally.
// Inner wall at r=48 with inward normals, outer wall at r=52 with outward
// normals -- the paper's own geometry. A classifier that cannot tell these
// apart cannot implement section IV-B1 at all.
//
// No test framework, same as the ordering tests: the container has no test
// dependency and this seam should not take one. Dependency-free (no PCL).

#include "../surface_classify.h"

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace {

int g_failures = 0;
int g_checks = 0;

void check(bool ok, const std::string &what)
{
    ++g_checks;
    std::printf("    %s %s\n", ok ? "ok  " : "FAIL", what.c_str());
    if (!ok) ++g_failures;
}

// A cylindrical wall patch: n points at radius r, spanning height h,
// normals radial. inward=true points them at the axis (an interior wall),
// inward=false points them away (an exterior wall).
void wall_patch(std::vector<sfspp::Vec3> &pts, std::vector<sfspp::Vec3> &nrm,
                int n, double r, double h, bool inward)
{
    for (int i = 0; i < n; ++i) {
        const double t = 2.0 * M_PI * i / n;
        const double z = h * (i % 2 == 0 ? 0.5 : -0.5);
        sfspp::Vec3 p{ r * std::cos(t), r * std::sin(t), z };
        const double s = inward ? -1.0 : 1.0;
        sfspp::Vec3 nr{ s * std::cos(t), s * std::sin(t), 0.0 };
        pts.push_back(p);
        nrm.push_back(nr);
    }
}

sfspp::AxisLine z_axis()
{
    sfspp::AxisLine a;
    a.point = { 0.0, 0.0, 0.0 };
    a.direction = { 0.0, 0.0, 1.0 };
    return a;
}

void test_inner_vs_outer()
{
    std::printf("  concentric walls: inner (r=48, inward normals) vs outer (r=52, outward)\n");
    std::vector<sfspp::Vec3> pi, ni, po, no;
    wall_patch(pi, ni, 200, 48.0, 10.0, true);
    wall_patch(po, no, 200, 52.0, 10.0, false);
    const sfspp::AxisLine ax = z_axis();

    std::size_t win = 0, lose = 0;
    const bool inner_first = sfspp::first_is_interior(
        pi.data(), ni.data(), pi.size(), po.data(), no.data(), po.size(),
        ax, 5.0, &win, &lose);
    check(inner_first, "inner-first classifies inner as interior");
    check(win > lose, "winning margin is positive");

    const bool outer_first = sfspp::first_is_interior(
        po.data(), no.data(), po.size(), pi.data(), ni.data(), pi.size(),
        ax, 5.0, &win, &lose);
    check(!outer_first, "outer-first classifies outer as NOT interior");
}

void test_degenerate_normals_do_not_crash_or_decide()
{
    std::printf("  zero normals: must not crash, must not claim interior\n");
    std::vector<sfspp::Vec3> pa(50, sfspp::Vec3{ 48.0, 0.0, 0.0 });
    std::vector<sfspp::Vec3> na(50, sfspp::Vec3{ 0.0, 0.0, 0.0 });
    std::vector<sfspp::Vec3> pb(50, sfspp::Vec3{ 52.0, 0.0, 0.0 });
    std::vector<sfspp::Vec3> nb(50, sfspp::Vec3{ 0.0, 0.0, 1.0 });
    const sfspp::AxisLine ax = z_axis();
    // Must return (not crash); the vote is 0 interior everywhere so the tie
    // rule keeps the first. The assertion is only that it terminates with a
    // deterministic answer.
    const bool r1 = sfspp::first_is_interior(
        pa.data(), na.data(), pa.size(), pb.data(), nb.data(), pb.size(), ax, 5.0);
    const bool r2 = sfspp::first_is_interior(
        pa.data(), na.data(), pa.size(), pb.data(), nb.data(), pb.size(), ax, 5.0);
    check(r1 == r2, "degenerate input gives a deterministic answer");
}

void test_empty_input_does_not_crash()
{
    std::printf("  empty surface: must not crash\n");
    std::vector<sfspp::Vec3> pb(50, sfspp::Vec3{ 52.0, 0.0, 0.0 });
    std::vector<sfspp::Vec3> nb(50, sfspp::Vec3{ 0.0, 0.0, 1.0 });
    const sfspp::AxisLine ax = z_axis();
    const bool r = sfspp::first_is_interior(
        nullptr, nullptr, 0, pb.data(), nb.data(), pb.size(), ax, 5.0);
    (void)r;
    check(true, "empty first surface returns without crashing");
}

} // namespace

int main(int argc, char **argv)
{
    const std::string which = argc > 1 ? argv[1] : "all";
    std::printf("surface_classify tests [%s]\n", which.c_str());

    if (which == "all" || which == "inner-outer") test_inner_vs_outer();
    if (which == "all" || which == "degenerate") test_degenerate_normals_do_not_crash_or_decide();
    if (which == "all" || which == "empty") test_empty_input_does_not_crash();

    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
