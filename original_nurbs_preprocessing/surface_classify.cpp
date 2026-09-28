// Interior/exterior classification -- see surface_classify.h for the paper
// reference and for what this is and is not.
//
// GEOMETRY, stated once so the code below can be checked against it.
// Ray: p + t*n, t real. Axis line: A + s*d, s real, |d| = 1.
// Closest approach: minimise |p + t*n - A - s*d|^2 over (t, s).
// With w = p - A, and n, d unit (n is normalised defensively at use):
//   t* = ( (w.d)(n.d) - (w.n) ) / ( 1 - (n.d)^2 )
//   min distance = |w + t*n - ((w + t*n).d) d|
// Degenerate when n is parallel to d (denominator ~ 0): the ray runs
// parallel to the axis and never meets it -- correctly exterior-consistent,
// since the axis is not in front of such a surface point.
// A point is interior-consistent when min distance <= eps AND t* > 0.

#include "surface_classify.h"

#include <cmath>

namespace sfspp {
namespace {

inline double dot(const Vec3& a, const Vec3& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline double norm(const Vec3& a)
{
    return std::sqrt(dot(a, a));
}

// Closest approach of ray p+t*n to the axis. Returns (min_distance, t_star).
// n is normalised inside, so callers may pass raw stored normals.
inline void ray_axis_closest(const Vec3& p, const Vec3& n_raw,
                             const AxisLine& axis, double& dist, double& t_star)
{
    const double nl = norm(n_raw);
    // A zero normal carries no direction; treat as never meeting the axis.
    if (!(nl > 1e-12)) {
        dist = 1e30;
        t_star = 0.0;
        return;
    }
    const Vec3 n{ n_raw.x / nl, n_raw.y / nl, n_raw.z / nl };
    const Vec3 w{ p.x - axis.point.x, p.y - axis.point.y, p.z - axis.point.z };
    const double nd = dot(n, axis.direction);
    const double denom = 1.0 - nd * nd;
    if (std::fabs(denom) < 1e-9) {
        dist = 1e30;  // parallel: never meets
        t_star = 0.0;
        return;
    }
    const double wn = dot(w, n);
    const double wd = dot(w, axis.direction);
    t_star = (wd * nd - wn) / denom;
    // Closest point on the ray to the axis, then its distance to the axis.
    const Vec3 q{ p.x + t_star * n.x, p.y + t_star * n.y, p.z + t_star * n.z };
    const Vec3 v{ q.x - axis.point.x, q.y - axis.point.y, q.z - axis.point.z };
    const double s = dot(v, axis.direction);
    const double dx = v.x - s * axis.direction.x;
    const double dy = v.y - s * axis.direction.y;
    const double dz = v.z - s * axis.direction.z;
    dist = std::sqrt(dx * dx + dy * dy + dz * dz);
}

}  // namespace

SurfaceVote vote_surface(const Vec3* points, const Vec3* normals,
                         std::size_t n, const AxisLine& axis, double eps_mm,
                         std::size_t max_samples)
{
    SurfaceVote v;
    if (n == 0 || points == nullptr || normals == nullptr) return v;
    // Even stride so the vote covers the whole surface.
    const std::size_t stride = (n <= max_samples) ? 1 : n / max_samples;
    for (std::size_t i = 0; i < n; i += stride) {
        double dist, t_star;
        ray_axis_closest(points[i], normals[i], axis, dist, t_star);
        ++v.points_tested;
        if (dist <= eps_mm && t_star > 0.0)
            ++v.interior_consistent;
        else
            ++v.exterior_consistent;
    }
    return v;
}

bool first_is_interior(const Vec3* a_pts, const Vec3* a_nrm, std::size_t na,
                       const Vec3* b_pts, const Vec3* b_nrm, std::size_t nb,
                       const AxisLine& axis, double eps_mm,
                       std::size_t* score_win, std::size_t* score_lose)
{
    const SurfaceVote va = vote_surface(a_pts, a_nrm, na, axis, eps_mm);
    const SurfaceVote vb = vote_surface(b_pts, b_nrm, nb, axis, eps_mm);
    // Configuration (a=interior, b=exterior) vs swapped, per the paper:
    // greatest number of satisfying points from both surfaces wins.
    const std::size_t s_ab = va.interior_consistent + vb.exterior_consistent;
    const std::size_t s_ba = vb.interior_consistent + va.exterior_consistent;
    if (score_win) *score_win = (s_ab >= s_ba) ? s_ab : s_ba;
    if (score_lose) *score_lose = (s_ab >= s_ba) ? s_ba : s_ab;
    return s_ab >= s_ba;  // tie keeps current behaviour
}

}  // namespace sfspp
