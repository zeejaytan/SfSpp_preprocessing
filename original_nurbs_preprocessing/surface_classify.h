// Interior/exterior surface classification, SfS++ paper section IV-B1.
//
// PAPER (arXiv 2502.13986, "Interior and exterior surface classification"):
//   "for each point p_s on the surface, we project a ray along its surface
//    normal direction n_s towards the axis of symmetry and define the point
//    p_s' where it meets the axis of symmetry. ... If p_s' lies on the
//    positive surface normal, the surface to which p_s belongs is classified
//    as the interior surface. On the other hand, if p_s lies in the negative
//    direction, the surface is classified as the exterior surface."
//   "We test two configurations: one surface as interior and the other as
//    exterior, and vice versa, and we select the configuration that had the
//    greatest number of surface points from both surfaces that satisfied the
//    above geometry (by checking the sign of the ray's normal scalar
//    coefficient)."
//
// WHAT THIS IS
// A pure function on points, normals, and an axis line. No PCL, no file IO,
// so it is unit-testable without the container and reviewable without the
// 137 KB pipeline file around it.
//
// WHAT IT IS NOT
// The paper's region-growing segmentation (tau_theta=4, tau_kappa=1) is a
// different step and is not touched here. This answers only: given two
// surface point clouds and the symmetry axis, which one is interior.

#pragma once

#include <cstddef>

namespace sfspp {

// A 3D point or vector. Plain array so the unit needs no linear-algebra
// dependency; the pipeline converts to/from Eigen at the call site.
struct Vec3 {
    double x, y, z;
};

// The symmetry axis as a point on the axis and a unit direction.
struct AxisLine {
    Vec3 point;
    Vec3 direction;  // must be unit length; checked, not assumed
};

// Result of classifying one surface against the axis.
struct SurfaceVote {
    // Points whose normal-ray passes within eps_mm of the axis with the
    // intersection in front of the surface (t > 0): interior-consistent.
    std::size_t interior_consistent = 0;
    // Points where the axis is NOT in front of the surface: exterior-consistent.
    std::size_t exterior_consistent = 0;
    std::size_t points_tested = 0;
};

// Vote one surface. Tests up to max_samples points (evenly strided, so the
// vote covers the whole surface rather than its first rows).
SurfaceVote vote_surface(const Vec3* points, const Vec3* normals,
                         std::size_t n, const AxisLine& axis, double eps_mm,
                         std::size_t max_samples = 500);

// Classify two surfaces. Returns true when the FIRST surface (a) is the
// interior one, i.e. configuration (a=interior, b=exterior) has at least as
// many satisfying points as the swapped configuration. Ties keep the
// current behaviour (a first), so this never reorders on ambiguous input
// without saying so -- the caller logs the margin.
bool first_is_interior(const Vec3* a_pts, const Vec3* a_nrm, std::size_t na,
                       const Vec3* b_pts, const Vec3* b_nrm, std::size_t nb,
                       const AxisLine& axis, double eps_mm,
                       std::size_t* score_win = nullptr,
                       std::size_t* score_lose = nullptr);

}  // namespace sfspp
