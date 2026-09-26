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

// Note: the original body also declared pcl::PointIndices::Ptr inliers
// and pcl::ExtractIndices extract. Both were dead -- written, never read,
// left over from the commented-out alternative walk -- and both were the
// only reason this file needed <pcl/point_indices.h>, which the 137 KB
// pipeline file supplied transitively. They are gone, so the include is
// gone with them. Behaviour is unchanged: nothing read them.

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
}
