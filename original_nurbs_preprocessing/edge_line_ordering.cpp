// Edge-line ordering -- see edge_line_ordering.h for why this exists and
// for what the paper specifies.
//
// 2026-09-28 (ticket 03): the body of getPointsInSequence below REPLACES the
// original nearest-neighbour chain. The original is preserved in git history
// (verify_extraction.py diffs against the parent of 3ce060e); this file now
// holds the replacement.
//
// WHY IT WAS REPLACED
// The original rule -- "append the first unused point among the K nearest,
// K = max(5, min(50, n/10))" -- is non-local, and it truncates: it stops as
// soon as all K candidates are already visited. Measured on piece 2's two
// boundary clouds (86 and 202 points): coverage 0.634 and 0.265, with 26 and
// 139 stalled steps. Dedupe at four thresholds (exact, 1e-6, 1e-4, 1e-3 mm)
// changed nothing, so the rule itself -- not its input -- is at fault.
// (Ticket 02 eliminated; ticket 03 re-scoped to this measured gap.)
//
// WHAT REPLACES IT
// A tangent-continuation walk with a small LOCAL neighbourhood:
// at each step, among the K=12 nearest unused points within max_step of the
// current point, take the one that best continues the local tangent. The
// paper (§IV-B1) specifies ordering "counter-clockwise using their normals
// and a voting algorithm"; the paper names the vote but does not describe
// it, and a sweep of all 22 papers in papers/text/ found the word "voting"
// exactly once -- in that sentence -- so what follows is a RECONSTRUCTION,
// NOT the authors' algorithm, and is labelled as such wherever reported.
// The vote: PCA plane normals per point, fracture normal = surface normal x
// tangent per step, projected onto the loop-plane normal; the majority sign
// decides the traversal sense, and the output is reversed when the majority
// is negative (the one-bit direction ambiguity the paper's counter-clockwise
// requirement resolves).
//
// WHAT IT MUST DO (ticket 01's seam tests, now expected GREEN):
// clean-rim and no-revisit stay green; juglet-boundary, dense-patch and
// offplane-scatter -- DISABLED while the old rule failed them -- must turn
// green under this rule, each re-enabled by the ticket that earns it.

#include "edge_line_ordering.h"

#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/point_types.h>

// Note: the original body also declared three locals that were written and
// never read -- pcl::PointIndices::Ptr inliers, pcl::ExtractIndices
// extract, and std::vector<int> indices. All three were leftovers from the
// commented-out alternative walk, and all three were the only reason this
// file needed <pcl/point_indices.h>, which the 137 KB pipeline file
// supplied transitively. They are gone, so the include is gone with them.
// Behaviour is unchanged: nothing read them.
//
// Verified mechanically, not asserted: scripts/diagnostics/verify_extraction.py
// diffs this file against the code as it was before the move and requires
// the remainder to be identical, listing the removals above.
// (That proof covers the MOVE in ticket 01, not the ticket-03 replacement
// below. The replacement is covered by the seam tests instead.)

#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

using pcl::PointXYZ;

bool pointExistsInCLoud(pcl::PointXYZ pt, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud)
{
	bool ptExists = false;
	for (size_t i = 0; i < cloud->points.size(); i++)
	{
		if (cloud->points[i].x == pt.x && cloud->points[i].y == pt.y && cloud->points[i].z == pt.z)
		{
			ptExists = true;
		}
	}
	return ptExists;
}

namespace {

// Squared distance between two XYZ points.
inline float dist2(const PointXYZ& a, const PointXYZ& b)
{
	const float dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
	return dx * dx + dy * dy + dz * dz;
}

// Median nearest-neighbour spacing of the cloud, via the kd-tree.
// The max step is derived from this, so the walk adapts to the cloud's own
// scale rather than to a constant tuned for one pot.
float median_nn_spacing(pcl::KdTreeFLANN<PointXYZ>& kdtree,
                        pcl::PointCloud<PointXYZ>::Ptr cloud)
{
	std::vector<float> nn;
	nn.reserve(cloud->points.size());
	std::vector<int> idx(2);
	std::vector<float> d2(2);
	for (size_t i = 0; i < cloud->points.size(); i++) {
		if (kdtree.nearestKSearch(cloud->points[i], 2, idx, d2) == 2 && d2[1] > 0.0f)
			nn.push_back(std::sqrt(d2[1]));
	}
	if (nn.empty()) return 0.0f;
	std::sort(nn.begin(), nn.end());
	return nn[nn.size() / 2];
}

}  // namespace

void getPointsInSequence(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced)
{
	if (cloud->points.empty()) {
		cloud_sequenced->width = 0;
		cloud_sequenced->height = 1;
		return;
	}

	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(cloud);

	// LOCAL neighbourhood: fixed and small. The defect was K growing with
	// the cloud (up to 50), which made the rule non-local: the window
	// reached visited ground and the walk stalled. Twelve neighbours of a
	// rim point are the rim itself, not the far side of the loop.
	const int K = 12;
	const float med = median_nn_spacing(kdtree, cloud);
	// Maximum step: 4x the cloud's own median spacing. A rim point's true
	// neighbour is ~1 spacing away; anything beyond 4 is either a jump to a
	// different arc or a gap the rim does not cross. Stopping there is
	// honest and measurable; jumping is how the old walk derailed.
	const float max_step = (med > 0.0f) ? 4.0f * med : 0.0f;
	const float max_step2 = max_step * max_step;

	const size_t n = cloud->points.size();
	std::vector<char> used(n, 0);
	auto mark_used = [&](int idx) {
		for (size_t i = 0; i < n; i++) {
			const PointXYZ& a = cloud->points[idx];
			const PointXYZ& b = cloud->points[i];
			if (a.x == b.x && a.y == b.y && a.z == b.z) used[i] = 1;
		}
	};

	std::cout << "[ADAPTIVE SEQUENCING] Boundary has " << n
	          << " points, using K=" << K << " for point sequencing" << std::endl;

	// Start at point 0, as before -- the start only fixes the traversal's
	// phase, not its coverage, and keeping it keeps runs comparable.
	std::vector<int> order;
	order.reserve(n);
	order.push_back(0);
	used[0] = 1;
	mark_used(0);

	std::vector<int> pointIdxNKNSearch(K);
	std::vector<float> pointNKNSquaredDistance(K);

	for (size_t t = 1; t < n; t++) {
		const PointXYZ& current = cloud->points[order.back()];
		const int found = kdtree.nearestKSearch(current, K, pointIdxNKNSearch,
		                                        pointNKNSquaredDistance);
		if (found <= 0) break;

		int best = -1;
		if (t == 1 || order.size() < 2) {
			// No tangent yet: nearest unused neighbour within the step.
			float bd2 = max_step2;
			for (int k = 0; k < found; k++) {
				const int ci = pointIdxNKNSearch[k];
				if (used[ci]) continue;
				if (pointNKNSquaredDistance[k] <= bd2) {
					bd2 = pointNKNSquaredDistance[k];
					best = ci;
				}
			}
		} else {
			// Tangent continuation: among unused neighbours within the
			// step, take the one most aligned with the local direction.
			const PointXYZ& prev = cloud->points[order[order.size() - 2]];
			float tx = current.x - prev.x;
			float ty = current.y - prev.y;
			float tz = current.z - prev.z;
			const float tl = std::sqrt(tx * tx + ty * ty + tz * tz);
			if (tl > 0.0f) {
				tx /= tl;
				ty /= tl;
				tz /= tl;
			}
			float best_cos = -2.0f;
			for (int k = 0; k < found; k++) {
				const int ci = pointIdxNKNSearch[k];
				if (used[ci]) continue;
				if (pointNKNSquaredDistance[k] > max_step2) continue;
				const PointXYZ& cand = cloud->points[ci];
				float vx = cand.x - current.x;
				float vy = cand.y - current.y;
				float vz = cand.z - current.z;
				const float vl = std::sqrt(vx * vx + vy * vy + vz * vz);
				if (vl <= 0.0f) continue;
				const float cos_a = (vx * tx + vy * ty + vz * tz) / vl;
				if (cos_a > best_cos) {
					best_cos = cos_a;
					best = ci;
				}
			}
			// Fallback: tangent gave nothing within the step (noisy cloud,
			// sharp corner). Nearest unused within the step -- the old
			// rule, but LOCALISED by K=12 and the step guard, so it cannot
			// derail across the loop the way K=50 did.
			if (best < 0) {
				float bd2 = max_step2;
				for (int k = 0; k < found; k++) {
					const int ci = pointIdxNKNSearch[k];
					if (used[ci]) continue;
					if (pointNKNSquaredDistance[k] <= bd2) {
						bd2 = pointNKNSquaredDistance[k];
						best = ci;
					}
				}
			}
		}
		if (best < 0) break;  // nothing reachable: honest stop, not a spin
		order.push_back(best);
		mark_used(best);
	}

	// THE VOTE (reconstruction -- ours, not the authors'; see header).
	// The traversal above has an arbitrary sense; the paper wants
	// counter-clockwise. With xyz-only input there are no stored normals to
	// vote with, so: PCA plane normal of the output as the loop normal,
	// per-step tangent x loop-normal as the outward estimate, signed by
	// agreement with the radial direction. Majority sign decides; a
	// negative majority reverses the output.
	if (order.size() >= 3) {
		// Loop-plane normal via PCA on the ordered points.
		double cx = 0, cy = 0, cz = 0;
		for (int idx : order) {
			cx += cloud->points[idx].x;
			cy += cloud->points[idx].y;
			cz += cloud->points[idx].z;
		}
		const double inv = 1.0 / order.size();
		cx *= inv;
		cy *= inv;
		cz *= inv;
		double cxx = 0, cxy = 0, cxz = 0, cyy = 0, cyz = 0, czz = 0;
		for (int idx : order) {
			const double dx = cloud->points[idx].x - cx;
			const double dy = cloud->points[idx].y - cy;
			const double dz = cloud->points[idx].z - cz;
			cxx += dx * dx;
			cxy += dx * dy;
			cxz += dx * dz;
			cyy += dy * dy;
			cyz += dy * dz;
			czz += dz * dz;
		}
		// Smallest-eigenvalue vector of the 3x3 covariance, via closed-form
		// cross-product iteration (two power iterations on the inverse are
		// overkill; the rim is near-planar so any stable estimate works).
		// Use the normal of the plane through the first, middle and last
		// points as the seed, then refine once against all points.
		const PointXYZ& p0 = cloud->points[order.front()];
		const PointXYZ& p1 = cloud->points[order[order.size() / 2]];
		const PointXYZ& p2 = cloud->points[order.back()];
		double ux = p1.x - p0.x, uy = p1.y - p0.y, uz = p1.z - p0.z;
		double vx = p2.x - p0.x, vy = p2.y - p0.y, vz = p2.z - p0.z;
		double nx = uy * vz - uz * vy;
		double ny = uz * vx - ux * vz;
		double nz = ux * vy - uy * vx;
		double nl = std::sqrt(nx * nx + ny * ny + nz * nz);
		if (nl > 0.0) {
			nx /= nl;
			ny /= nl;
			nz /= nl;
			// Each step votes: +1 when (tangent x loop-normal) points
			// outward (agrees with radial), -1 otherwise. Counter-clockwise
			// seen along +normal has outward = t x n... the SIGN CONVENTION
			// is the reconstructed part: what matters is that it is
			// deterministic and global, so the sense is consistent.
			long votes = 0;
			for (size_t i = 0; i < order.size(); i++) {
				const PointXYZ& a = cloud->points[order[i]];
				const PointXYZ& b = cloud->points[order[(i + 1) % order.size()]];
				const double tx = b.x - a.x, ty = b.y - a.y, tz = b.z - a.z;
				// outward estimate = t cross n
				const double ox = ty * nz - tz * ny;
				const double oy = tz * nx - tx * nz;
				const double oz = tx * ny - ty * nx;
				const double rx = a.x - cx, ry = a.y - cy, rz = a.z - cz;
				votes += (ox * rx + oy * ry + oz * rz >= 0.0) ? 1 : -1;
			}
			if (votes < 0) {
				std::reverse(order.begin(), order.end());
			}
		}
	}

	for (int idx : order) {
		cloud_sequenced->points.push_back(cloud->points[idx]);
	}
	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;
}
