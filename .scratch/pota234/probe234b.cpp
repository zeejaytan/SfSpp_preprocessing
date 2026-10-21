#include <vector>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <string>
#include <Eigen/Dense>
#include <Eigen/Core>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/common/common.h>
#include <pcl/segmentation/region_growing.h>
bool myobject3(const pcl::PointIndices &a, const pcl::PointIndices &b){return a.indices.size()>b.indices.size();}
// TICKET 234 PAPER ARM (lead redirect 2026-10-22, SfS++ Sec IV-B1 verbatim).
// (1) region growing from the min-curvature point: n_b neighbours, join iff
// curvature < tau_kappa AND normal angle to the CURRENT front-point normal
// < tau_theta (Rabbani [35] / PCL semantics: the reference drifts with the
// front, so gradual twist is followed and only sharp turns split; a fixed
// seed reference over-segments -- verified v1 vs v2).
// (2) cluster merging to fixpoint (paper criteria, numeric choices reported
// at the call site): kNN close pairs between clusters (dist <= closeMM),
// patch-average normal similarity (<= patchDeg), boundary-point curvature
// comparison (rel diff <= curvRel), internal-point normal+curvature
// verification (same gates); merge all passing pairs, repeat to fixpoint.
// B-spline boundary refine + resample is the existing postamble
// (improveSurfaceBoundaryByFittingBSplineSurface) -- not duplicated here.
// (3) axis-ray classification (below): Surface_0 = interior.
// NOTE: no local named `qh` (qhull -Dqh_QHpointer hijacks it) and no `queue`
// shadowing games -- names below are collision-checked against this TU.
// ============================================================================
static std::vector<pcl::PointIndices> growPaper234(
    pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    int minClusterSize, int nb, double thetaDeg, double kappaThresh)
{
    std::vector<pcl::PointIndices> pclusters;
    const int NP = static_cast<int>(pcloud->points.size());
    if (NP == 0) return pclusters;
    std::vector<int> seedOrder(NP);
    for (int i = 0; i < NP; ++i) seedOrder[i] = i;
    std::sort(seedOrder.begin(), seedOrder.end(), [&](int a, int b) {
        return pnormals->points[a].curvature < pnormals->points[b].curvature;
    });
    pcl::KdTreeFLANN<pcl::PointXYZ> pkdtree;
    pkdtree.setInputCloud(pcloud);
    std::vector<int> pnb;
    std::vector<float> pdist;
    std::vector<int> pfront;
    std::vector<int> preg;
    std::vector<char> pclaimed(NP, 0);
    pfront.reserve(2048);
    preg.reserve(8192);
    for (int s = 0; s < NP; ++s) {
        int sd = seedOrder[s];
        if (pclaimed[sd]) continue;
        preg.clear();
        preg.push_back(sd);
        pclaimed[sd] = 1;
        pfront.clear();
        pfront.push_back(sd);
        size_t fh2 = 0;
        while (fh2 < pfront.size()) {
            int cf = pfront[fh2++];
            Eigen::Vector4f curN4(pnormals->points[cf].normal_x,
                                  pnormals->points[cf].normal_y,
                                  pnormals->points[cf].normal_z, 0.0f);
            pnb.clear(); pdist.clear();
            if (pkdtree.nearestKSearch(pcloud->points[cf], nb + 1, pnb, pdist) <= 0) continue;
            for (size_t k = 0; k < pnb.size(); ++k) {
                int cand = pnb[k];
                if (cand == cf || pclaimed[cand]) continue;
                if (pnormals->points[cand].curvature >= kappaThresh) continue;
                Eigen::Vector4f nn4(pnormals->points[cand].normal_x,
                                    pnormals->points[cand].normal_y,
                                    pnormals->points[cand].normal_z, 0.0f);
                if (pcl::getAngle3D(curN4, nn4, true) > thetaDeg) continue;
                pclaimed[cand] = 1;
                preg.push_back(cand);
                pfront.push_back(cand);
            }
        }
        if (static_cast<int>(preg.size()) >= minClusterSize) {
            pcl::PointIndices pi;
            pi.indices = preg;
            pclusters.push_back(pi);
        }
    }
    return pclusters;
}

static Eigen::Vector3f meanNormal234(const std::vector<int>& idx,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += Eigen::Vector3f(pnormals->points[id].normal_x, pnormals->points[id].normal_y, pnormals->points[id].normal_z);
    float n = m.norm();
    if (n > 1e-9f) m /= n;
    else m = Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    return m;
}

static double meanCurv234(const std::vector<int>& idx,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals)
{
    if (idx.empty()) return 0.0;
    double s = 0.0;
    for (int id : idx) s += static_cast<double>(pnormals->points[id].curvature);
    return s / static_cast<double>(idx.size());
}

static Eigen::Vector3f pcaAxis234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<int>& idx)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += pcloud->points[id].getVector3fMap();
    if (!idx.empty()) m /= static_cast<float>(idx.size());
    Eigen::Matrix3f cov = Eigen::Matrix3f::Zero();
    for (int id : idx) { Eigen::Vector3f d = pcloud->points[id].getVector3fMap() - m; cov += d * d.transpose(); }
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> es(cov);
    return es.eigenvectors().col(2);
}

static int medianInternal234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<int>& idx, const Eigen::Vector3f& axis)
{
    if (idx.empty()) return -1;
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    for (int id : idx) m += pcloud->points[id].getVector3fMap();
    m /= static_cast<float>(idx.size());
    Eigen::Vector3f an = axis.norm() > 1e-9f ? axis.normalized() : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    std::vector<std::pair<float,int> > dv;
    dv.reserve(idx.size());
    for (int id : idx) {
        Eigen::Vector3f w = pcloud->points[id].getVector3fMap() - m;
        float along = w.dot(an);
        float perp = (w - along * an).norm();
        dv.push_back(std::make_pair(perp, id));
    }
    std::nth_element(dv.begin(), dv.begin() + dv.size() / 2, dv.end());
    return dv[dv.size() / 2].second;
}

static Eigen::Vector3f k2AvgNormal234(pcl::KdTreeFLANN<pcl::PointXYZ>& ctree,
    const std::vector<int>& cidx,
    pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals, int qid, int k2)
{
    Eigen::Vector3f m(0.0f, 0.0f, 0.0f);
    if (cidx.empty() || k2 <= 0) return Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    std::vector<int> rr; std::vector<float> dd;
    int K = std::min<int>(k2, static_cast<int>(cidx.size()));
    if (ctree.nearestKSearch(pcloud->points[qid], K, rr, dd) <= 0) return Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    for (int r : rr) {
        int gid = cidx[r];
        m += Eigen::Vector3f(pnormals->points[gid].normal_x, pnormals->points[gid].normal_y, pnormals->points[gid].normal_z);
    }
    float n = m.norm();
    if (n > 1e-9f) m /= n;
    else m = Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    return m;
}


// One merge verdict for a cluster pair. All thresholds are the paper-arm
// operating point (logged by the caller).
// Appendix-A-normative pair verdict (provenance in patch234d.py header).
static bool tryMergePair234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    const std::vector<int>& A, const std::vector<int>& B,
    const std::vector<char>& isBnd,
    const Eigen::Vector3f& axisA, const Eigen::Vector3f& axisB,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k2)
{
    if (A.empty() || B.empty()) return false;
    // ---- Step 1: boundary subsets, pairs within rhoD, need >= 3 ----
    std::vector<int> bA, bB;
    for (int id : A) if (isBnd[id]) bA.push_back(id);
    for (int id : B) if (isBnd[id]) bB.push_back(id);
    if (bA.empty() || bB.empty()) return false;
    const std::vector<int> *sP = &bA, *lP = &bB;
    bool sIsA = true;
    if (bA.size() > bB.size()) { sP = &bB; lP = &bA; sIsA = false; }
    pcl::PointCloud<pcl::PointXYZ>::Ptr lC(new pcl::PointCloud<pcl::PointXYZ>);
    for (int id : *lP) lC->points.push_back(pcloud->points[id]);
    lC->width = lC->points.size(); lC->height = 1;
    pcl::KdTreeFLANN<pcl::PointXYZ> lT;
    lT.setInputCloud(lC);
    std::vector<std::pair<int,int> > pairs;
    std::vector<int> oneI; std::vector<float> oneD;
    for (size_t i = 0; i < sP->size() && pairs.size() < 200; ++i) {
        int sid = (*sP)[i];
        oneI.clear(); oneD.clear();
        if (lT.nearestKSearch(pcloud->points[sid], 1, oneI, oneD) <= 0) continue;
        if (oneD[0] <= rhoD * rhoD) {
            int a = sIsA ? sid : (*lP)[oneI[0]];
            int b = sIsA ? (*lP)[oneI[0]] : sid;
            pairs.push_back(std::make_pair(a, b));
        }
    }
    if (pairs.size() < 3) return false;
    // ---- Step 2: k2-average normals + mean curvature over pair members ----
    pcl::PointCloud<pcl::PointXYZ>::Ptr cA(new pcl::PointCloud<pcl::PointXYZ>), cB(new pcl::PointCloud<pcl::PointXYZ>);
    for (int id : A) cA->points.push_back(pcloud->points[id]);
    for (int id : B) cB->points.push_back(pcloud->points[id]);
    cA->width = cA->points.size(); cA->height = 1;
    cB->width = cB->points.size(); cB->height = 1;
    pcl::KdTreeFLANN<pcl::PointXYZ> tA, tB;
    tA.setInputCloud(cA); tB.setInputCloud(cB);
    Eigen::Vector3f sNA(0,0,0), sNB(0,0,0);
    double sCA = 0.0, sCB = 0.0;
    for (size_t i = 0; i < pairs.size(); ++i) {
        sNA += k2AvgNormal234(tA, A, pcloud, pnormals, pairs[i].first, k2);
        sNB += k2AvgNormal234(tB, B, pcloud, pnormals, pairs[i].second, k2);
        sCA += static_cast<double>(pnormals->points[pairs[i].first].curvature);
        sCB += static_cast<double>(pnormals->points[pairs[i].second].curvature);
    }
    float nA = sNA.norm(), nB = sNB.norm();
    if (nA < 1e-9f || nB < 1e-9f) return false;
    sNA /= nA; sNB /= nB;
    if (sNA.dot(sNB) < rhoN) return false;
    if (std::fabs(sCA / pairs.size() - sCB / pairs.size()) >= rhoC) return false;
    // ---- Step 3: internal median-point verification ----
    int ia = medianInternal234(pcloud, A, axisA);
    int ib = medianInternal234(pcloud, B, axisB);
    if (ia < 0 || ib < 0) return false;
    Eigen::Vector3f na(pnormals->points[ia].normal_x, pnormals->points[ia].normal_y, pnormals->points[ia].normal_z);
    Eigen::Vector3f nb(pnormals->points[ib].normal_x, pnormals->points[ib].normal_y, pnormals->points[ib].normal_z);
    float la = na.norm(), lb = nb.norm();
    if (la < 1e-9f || lb < 1e-9f) return false;
    if (na.dot(nb) / (la * lb) < rhoInN) return false;
    if (std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature)) >= rhoInC) return false;
    return true;
}

static void mergePaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters,
    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k1, int k2)
{
    std::cout << "[PAPER-234] appendix-A merge: rhoD=" << rhoD << " rhoN=" << rhoN << " rhoC=" << rhoC
              << " rhoInN=" << rhoInN << " rhoInC=" << rhoInC << " k1=" << k1 << " k2=" << k2 << std::endl;
    const int NP = static_cast<int>(pcloud->points.size());
    pcl::KdTreeFLANN<pcl::PointXYZ> allTree;
    allTree.setInputCloud(pcloud);
    std::vector<int> rr; std::vector<float> dd;
    int pass = 0;
    bool any = true;
    while (any) {
        any = false;
        ++pass;
        std::vector<int> memberOf(NP, -1);
        for (size_t c = 0; c < pclusters.size(); ++c)
            for (int id : pclusters[c].indices) memberOf[id] = static_cast<int>(c);
        // boundary status via k1 neighbours (Alg 1 Step 1)
        std::vector<char> isBnd(NP, 0);
        for (int p = 0; p < NP; ++p) {
            if (memberOf[p] < 0) continue;
            rr.clear(); dd.clear();
            int K = std::min(k1 + 1, NP);
            if (allTree.nearestKSearch(pcloud->points[p], K, rr, dd) <= 0) continue;
            for (size_t i = 0; i < rr.size(); ++i) {
                if (rr[i] == p) continue;
                if (memberOf[rr[i]] != memberOf[p]) { isBnd[p] = 1; break; }
            }
        }
        std::vector<Eigen::Vector3f> axes(pclusters.size());
        for (size_t c = 0; c < pclusters.size(); ++c) axes[c] = pcaAxis234(pcloud, pclusters[c].indices);
        std::vector<char> dead(pclusters.size(), 0);
        for (size_t i = 0; i < pclusters.size(); ++i) {
            if (dead[i]) continue;
            for (size_t j = i + 1; j < pclusters.size(); ++j) {
                if (dead[j]) continue;
                if (tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, isBnd,
                        axes[i], axes[j], rhoD, rhoN, rhoC, rhoInN, rhoInC, k2)) {
                    std::cout << "[PAPER-234] pass " << pass << ": merge " << pclusters[j].indices.size() << " into " << pclusters[i].indices.size() << std::endl;
                    pclusters[i].indices.insert(pclusters[i].indices.end(), pclusters[j].indices.begin(), pclusters[j].indices.end());
                    dead[j] = 1;
                    any = true;
                }
            }
        }
        if (any) {
            std::vector<pcl::PointIndices> kept;
            for (size_t i = 0; i < pclusters.size(); ++i) if (!dead[i]) kept.push_back(pclusters[i]);
            pclusters.swap(kept);
        }
        std::cout << "[PAPER-234] pass " << pass << " done: " << pclusters.size() << " clusters" << std::endl;
        if (pass > 25) break;
    }
}

// Axis-ray classification (paper Sec IV-B1): ray along the point normal meets
// the symmetry axis; intersection on the positive normal side = interior.
// Both assignments tried; the one with more satisfying points wins; the
// interior face is moved to clusters[0] so Surface_0 = interior (redirect).
static void classifyAndOrderPaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters)
{
    if (pclusters.size() < 2) return;
    const char* axPath = std::getenv("SFS_AXIS_FILE");
    if (!axPath || !*axPath) { std::cout << "[PAPER-234] classify: no SFS_AXIS_FILE, keep size order" << std::endl; return; }
    std::ifstream axf(axPath);
    if (!axf.is_open()) { std::cout << "[PAPER-234] classify: cannot open axis file, keep size order" << std::endl; return; }
    double ax, ay, az, dx, dy, dz;
    axf >> ax >> ay >> az >> dx >> dy >> dz;
    if (axf.fail()) { std::cout << "[PAPER-234] classify: bad axis parse, keep size order" << std::endl; return; }
    Eigen::Vector3f axPt(static_cast<float>(ax), static_cast<float>(ay), static_cast<float>(az));
    Eigen::Vector3f axDir(static_cast<float>(dx), static_cast<float>(dy), static_cast<float>(dz));
    float dl = axDir.norm();
    if (dl < 1e-9f) { std::cout << "[PAPER-234] classify: zero axis dir, keep size order" << std::endl; return; }
    axDir /= dl;
    double inFrac[2] = {0.0, 0.0};
    for (int f = 0; f < 2; ++f) {
        long inN = 0;
        for (int id : pclusters[f].indices) {
            Eigen::Vector3f pp = pcloud->points[id].getVector3fMap();
            Eigen::Vector3f nn(pnormals->points[id].normal_x, pnormals->points[id].normal_y, pnormals->points[id].normal_z);
            Eigen::Vector3f w = pp - axPt;
            float t = w.dot(axDir);
            Eigen::Vector3f cp = axPt + t * axDir;
            Eigen::Vector3f v = cp - pp;
            if (v.dot(nn) > 0.0f) ++inN;
        }
        inFrac[f] = pclusters[f].indices.empty() ? 0.0 : static_cast<double>(inN) / static_cast<double>(pclusters[f].indices.size());
    }
    double n0 = static_cast<double>(pclusters[0].indices.size()), n1 = static_cast<double>(pclusters[1].indices.size());
    double satA = inFrac[0] * n0 + (1.0 - inFrac[1]) * n1; // [0]=interior
    double satB = (1.0 - inFrac[0]) * n0 + inFrac[1] * n1; // [1]=interior
    std::cout << "[PAPER-234] classify: face0 n=" << pclusters[0].indices.size() << " interior_frac=" << inFrac[0]
              << " face1 n=" << pclusters[1].indices.size() << " interior_frac=" << inFrac[1]
              << " satA=" << satA << " satB=" << satB << std::endl;
    if (satB > satA) {
        pcl::PointIndices tmp = pclusters[0];
        pclusters[0] = pclusters[1];
        pclusters[1] = tmp;
        std::cout << "[PAPER-234] classify: swapped -> Surface_0=interior" << std::endl;
    } else {
        std::cout << "[PAPER-234] classify: kept -> Surface_0=interior" << std::endl;
    }
}

int main(){return 0;}
