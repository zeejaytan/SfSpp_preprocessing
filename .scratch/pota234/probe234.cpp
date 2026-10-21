#include <vector>
#include <algorithm>
#include <cmath>
#include <Eigen/Dense>
#include <Eigen/Core>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/common/common.h>

static bool fitPlaneWindow234(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud,
    const std::vector<int>& region, int planeWindow,
    const Eigen::Vector3f& refNormal,
    Eigen::Vector3f& outNormal, Eigen::Vector3f& outPoint)
{
    int n = static_cast<int>(region.size());
    int w = std::min(planeWindow, n);
    if (w < 3) {
        int s = region.back();
        outPoint = cloud->points[s].getVector3fMap();
        outNormal = refNormal;
        return true;
    }
    Eigen::Vector3f mean(0.0f, 0.0f, 0.0f);
    for (int i = n - w; i < n; ++i) mean += cloud->points[region[i]].getVector3fMap();
    mean /= static_cast<float>(w);
    Eigen::Matrix3f cov = Eigen::Matrix3f::Zero();
    for (int i = n - w; i < n; ++i) {
        Eigen::Vector3f d = cloud->points[region[i]].getVector3fMap() - mean;
        cov += d * d.transpose();
    }
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> es(cov);
    Eigen::Vector3f normal = es.eigenvectors().col(0);
    if (normal.dot(refNormal) < 0.0f) normal = -normal;
    outNormal = normal;
    outPoint = mean;
    return true;
}

static double angleToPlaneNormal234(const Eigen::Vector3f& n, const Eigen::Vector3f& planeN)
{
    Eigen::Vector4f a(n(0), n(1), n(2), 0.0f);
    Eigen::Vector4f b(planeN(0), planeN(1), planeN(2), 0.0f);
    return pcl::getAngle3D(a, b, true);
}

static std::vector<pcl::PointIndices> growRegionsPlaneContinuity234(
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud,
    pcl::PointCloud<pcl::Normal>::Ptr normals,
    int minClusterSize, int numberOfNeighbours,
    double joinDeg, double distMM, int planeWindow,
    double curvatureSeedThresh)
{
    std::vector<pcl::PointIndices> clusters;
    const int N = static_cast<int>(cloud->points.size());
    if (N == 0) return clusters;
    std::vector<char> taken(N, 0);
    std::vector<int> order(N);
    for (int i = 0; i < N; ++i) order[i] = i;
    std::sort(order.begin(), order.end(), [&](int a, int b) {
        return normals->points[a].curvature < normals->points[b].curvature;
    });
    pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
    kdtree.setInputCloud(cloud);
    std::vector<int> nbrs;
    std::vector<float> dists;
    std::vector<int> queue;
    std::vector<int> region;
    queue.reserve(2048);
    region.reserve(8192);
    for (int s = 0; s < N; ++s) {
        int seed = order[s];
        if (taken[seed]) continue;
        if (normals->points[seed].curvature > curvatureSeedThresh) continue;
        region.clear();
        region.push_back(seed);
        taken[seed] = 1;
        Eigen::Vector3f seedN(normals->points[seed].normal_x,
                              normals->points[seed].normal_y,
                              normals->points[seed].normal_z);
        Eigen::Vector3f planeN, planeP;
        fitPlaneWindow234(cloud, region, planeWindow, seedN, planeN, planeP);
        queue.clear();
        queue.push_back(seed);
        size_t qh = 0;
        while (qh < queue.size()) {
            int cur = queue[qh++];
            nbrs.clear(); dists.clear();
            if (kdtree.nearestKSearch(cloud->points[cur], numberOfNeighbours + 1, nbrs, dists) <= 0) continue;
            for (size_t k = 0; k < nbrs.size(); ++k) {
                int nb = nbrs[k];
                if (nb == cur || taken[nb]) continue;
                Eigen::Vector3f nn(normals->points[nb].normal_x,
                                   normals->points[nb].normal_y,
                                   normals->points[nb].normal_z);
                double ang = angleToPlaneNormal234(nn, planeN);
                Eigen::Vector3f pp = cloud->points[nb].getVector3fMap();
                double dd = std::fabs((pp - planeP).dot(planeN));
                if (ang <= joinDeg && dd <= distMM) {
                    taken[nb] = 1;
                    region.push_back(nb);
                    queue.push_back(nb);
                    fitPlaneWindow234(cloud, region, planeWindow, seedN, planeN, planeP);
                }
            }
        }
        if (static_cast<int>(region.size()) >= minClusterSize) {
            pcl::PointIndices pi;
            pi.indices = region;
            clusters.push_back(pi);
        }
    }
    return clusters;
}

int main() { return 0; }
