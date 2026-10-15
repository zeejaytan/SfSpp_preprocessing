// Edge-line ordering -- see edge_line_ordering.h for why this exists and
// for what the paper specifies.
//
// Bodies below are the ORIGINAL implementations, moved here unchanged
// from edgeline_extraction_headless.cpp. Nothing has been "cleaned up":
// the commented-out alternative walk and the exact float comparison in
// pointExistsInCLoud are both defects under discussion, and tidying them
// in the same commit would make the move unreviewable.
//
// Verified behaviour-preserving by re-running the extraction and
// diffing against the known-good bundle (8/9 pieces byte-identical, the
// ninth differing only in its segment header -- the pre-existing
// non-determinism recorded in patches/SOURCE_ANCHOR.md).

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

#include <algorithm>
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

void getPointsInSequence(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_sequenced)
{

	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;

	kdtree.setInputCloud(cloud);

	pcl::PointXYZ searchPoint;

	pcl::PointXYZ currentPoint, nextPoint, previousPoint;


	currentPoint = cloud->points[0];
	cloud_sequenced->points.push_back(currentPoint);

	// ADAPTIVE: Scale K with boundary size (5-50 range, ~10% of points)
	int boundary_size = cloud->points.size();
	int K = std::max(5, std::min(50, boundary_size / 10));
	std::cout << "[ADAPTIVE SEQUENCING] Boundary has " << boundary_size
	          << " points, using K=" << K << " for point sequencing" << std::endl;

	for (size_t t = 1; t < cloud->points.size(); t++)
	{
		searchPoint = currentPoint;
		std::vector<int> pointIdxNKNSearch(K);
		std::vector<float> pointNKNSquaredDistance(K);
		if (kdtree.nearestKSearch(searchPoint, K, pointIdxNKNSearch, pointNKNSquaredDistance) > 0)
		{

			if (t == 1)
			{
				PointXYZ p;
				p.x = (*cloud)[pointIdxNKNSearch[1]].x; p.y = (*cloud)[pointIdxNKNSearch[1]].y; p.z = (*cloud)[pointIdxNKNSearch[1]].z;
				cloud_sequenced->points.push_back(p);
				previousPoint = currentPoint;
				currentPoint = p;
			}
			else
			{
				if (pointIdxNKNSearch.size() > 0)
				{
					for (std::size_t x = 0; x < pointIdxNKNSearch.size(); ++x)
					{
						PointXYZ p1;
						p1.x = (*cloud)[pointIdxNKNSearch[x]].x; p1.y = (*cloud)[pointIdxNKNSearch[x]].y; p1.z = (*cloud)[pointIdxNKNSearch[x]].z;
						if (!pointExistsInCLoud(p1, cloud_sequenced))
						{
							cloud_sequenced->points.push_back(p1);
							previousPoint = currentPoint;
							currentPoint = p1;
							break;
						}
					}
				}
			}
		}
	}

	cloud_sequenced->width = cloud_sequenced->points.size();
	cloud_sequenced->height = 1;

	// SFS-T13 second chance (ticket 13): the greedy walk above stalls dead
	// the moment the current point's K nearest neighbours are all visited,
	// which is then true on every remaining iteration -- the walk covers
	// the first boundary component and silently drops the rest. On a
	// single-loop boundary the walk covers ~all of the input and nothing
	// below fires; on a fragmented boundary (Pot_A piece 2 wall: 45 of
	// 183 sequenced, traced 91mm of a ~300mm rim) the missing rim
	// resamples under the assembler's 50-point load minimum
	// (main_pristine_batch.cpp load loop: point_.cols() < 50 -> off,
	// no log line), and the piece vanishes from the reassembly with no
	// error. Calibration over the 16 Pot_A wall surfaces (pota06_fresh
	// edgeline_stage.log, sequenced->sphere-marched): p1 0.87/0.51,
	// p2 0.25/0.41, p3 0.86/0.67, p4 0.90/0.81, p5 0.64/0.82,
	// p6 0.89/0.86, p7 0.91/0.67, p8 0.74/0.90. Threshold 0.40 fires on
	// exactly one surface (p2 S0, the wall whose rim must be recovered);
	// the p2 S1 scrap (0.41) and all 14 other surfaces keep byte-identical
	// output. Provisional like the T04 guards (8 sherds, one pot).
	// Appended components stay contiguous, so the downstream peak
	// detector splits at the jumps and each component is classified on
	// its own merits.
	{
		const double coverage = static_cast<double>(cloud_sequenced->points.size())
			/ static_cast<double>(boundary_size > 0 ? boundary_size : 1);
		if (coverage < 0.40 && cloud_sequenced->points.size() < cloud->points.size())
		{
			int jumps = 0;
			while (cloud_sequenced->points.size() < cloud->points.size())
			{
				// One greedy step from currentPoint; on dead end, jump
				// to the nearest unvisited input point and continue.
				searchPoint = currentPoint;
				std::vector<int> idx(K);
				std::vector<float> dist(K);
				bool advanced = false;
				if (kdtree.nearestKSearch(searchPoint, K, idx, dist) > 0)
				{
					for (std::size_t x = 0; x < idx.size(); ++x)
					{
						PointXYZ p1;
						p1.x = (*cloud)[idx[x]].x; p1.y = (*cloud)[idx[x]].y; p1.z = (*cloud)[idx[x]].z;
						if (!pointExistsInCLoud(p1, cloud_sequenced))
						{
							cloud_sequenced->points.push_back(p1);
							previousPoint = currentPoint;
							currentPoint = p1;
							advanced = true;
							break;
						}
					}
				}
				if (!advanced)
				{
					double best = -1.0;
					PointXYZ pjump = currentPoint;
					for (size_t i = 0; i < cloud->points.size(); ++i)
					{
						PointXYZ q = (*cloud)[i];
						if (pointExistsInCLoud(q, cloud_sequenced))
							continue;
						const double dx = q.x - currentPoint.x;
						const double dy = q.y - currentPoint.y;
						const double dz = q.z - currentPoint.z;
						const double d2 = dx * dx + dy * dy + dz * dz;
						if (best < 0.0 || d2 < best)
						{
							best = d2;
							pjump = q;
						}
					}
					if (best < 0.0)
						break; // nothing unvisited left
					cloud_sequenced->points.push_back(pjump);
					previousPoint = currentPoint;
					currentPoint = pjump;
					++jumps;
				}
			}
			std::cout << "[SFS-T13] second-chance: coverage " << coverage
			          << " -> " << static_cast<double>(cloud_sequenced->points.size())
			              / static_cast<double>(boundary_size > 0 ? boundary_size : 1)
			          << " (" << cloud_sequenced->points.size() << "/" << boundary_size
			          << ", " << jumps << " jumps)" << std::endl;
			cloud_sequenced->width = cloud_sequenced->points.size();
			cloud_sequenced->height = 1;
		}
		else
		{
			std::cout << "[SFS-T13] pass: coverage " << coverage
			          << " (" << cloud_sequenced->points.size() << "/" << boundary_size
			          << "), no second chance" << std::endl;
		}
	}
}
