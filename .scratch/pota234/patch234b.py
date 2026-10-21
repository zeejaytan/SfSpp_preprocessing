SRC = "C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp"

with open(SRC, "rb") as f:
    txt = f.read().replace(b"\r\n", b"\n").decode("utf-8", errors="surrogateescape")

def once(old, new):
    global txt
    n = txt.count(old)
    assert n == 1, f"anchor x{n}: {old[:70]!r}"
    txt = txt.replace(old, new)

PAPER = '''// ============================================================================
// TICKET 234 PAPER ARM (lead redirect 2026-10-22, SfS++ Sec IV-B1 verbatim).
// (1) region growing from the min-curvature point: n_b neighbours, join iff
// curvature < tau_kappa AND normal angle to the REGION SEED normal < tau_theta.
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
        Eigen::Vector3f seedN(pnormals->points[sd].normal_x,
                              pnormals->points[sd].normal_y,
                              pnormals->points[sd].normal_z);
        Eigen::Vector4f seedN4(seedN(0), seedN(1), seedN(2), 0.0f);
        pfront.clear();
        pfront.push_back(sd);
        size_t fh2 = 0;
        while (fh2 < pfront.size()) {
            int cf = pfront[fh2++];
            pnb.clear(); pdist.clear();
            if (pkdtree.nearestKSearch(pcloud->points[cf], nb + 1, pnb, pdist) <= 0) continue;
            for (size_t k = 0; k < pnb.size(); ++k) {
                int cand = pnb[k];
                if (cand == cf || pclaimed[cand]) continue;
                if (pnormals->points[cand].curvature >= kappaThresh) continue;
                Eigen::Vector4f nn4(pnormals->points[cand].normal_x,
                                    pnormals->points[cand].normal_y,
                                    pnormals->points[cand].normal_z, 0.0f);
                if (pcl::getAngle3D(seedN4, nn4, true) > thetaDeg) continue;
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

static double curvRelDiff234(double a, double b)
{
    double d = std::fabs(a - b);
    double m = std::max(std::fabs(a), std::fabs(b));
    if (m < 1e-9) return 0.0;
    return d / m;
}

// One merge verdict for a cluster pair. All thresholds are the paper-arm
// operating point (logged by the caller).
static bool tryMergePair234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    const std::vector<int>& A, const std::vector<int>& B,
    double closeMM, double patchDeg, double curvRel)
{
    if (A.empty() || B.empty()) return false;
    const std::vector<int> *smallP = &A, *largeP = &B;
    if (A.size() > B.size()) { smallP = &B; largeP = &A; }
    pcl::KdTreeFLANN<pcl::PointXYZ> largeTree;
    pcl::PointCloud<pcl::PointXYZ>::Ptr largeCloud(new pcl::PointCloud<pcl::PointXYZ>);
    for (int id : *largeP) largeCloud->points.push_back(pcloud->points[id]);
    largeCloud->width = largeCloud->points.size();
    largeCloud->height = 1;
    largeTree.setInputCloud(largeCloud);
    // stride-sample the smaller cluster (deterministic, no RNG)
    size_t stride = std::max<size_t>(1, smallP->size() / 150);
    std::vector<std::pair<int,int> > closePairs; // (smallIdx, largePos)
    std::vector<int> oneIdx(1); std::vector<float> oneDist(1);
    for (size_t i = 0; i < smallP->size(); i += stride) {
        int sid = (*smallP)[i];
        oneIdx.clear(); oneDist.clear();
        if (largeTree.nearestKSearch(pcloud->points[sid], 1, oneIdx, oneDist) <= 0) continue;
        if (oneDist[0] <= closeMM * closeMM) closePairs.push_back(std::make_pair(sid, oneIdx[0]));
    }
    if (closePairs.empty()) return false;
    if (closePairs.size() > 40) closePairs.resize(40);
    // map largePos -> global index
    std::vector<int> closeA, closeB;
    if (smallP == &A) {
        for (size_t i = 0; i < closePairs.size(); ++i) { closeA.push_back(closePairs[i].first); closeB.push_back((*largeP)[closePairs[i].second]); }
    } else {
        for (size_t i = 0; i < closePairs.size(); ++i) { closeB.push_back(closePairs[i].first); closeA.push_back((*largeP)[closePairs[i].second]); }
    }
    // patch normals: cluster points within closeMM of any close point on that side
    std::vector<int> patchA, patchB;
    {
        pcl::KdTreeFLANN<pcl::PointXYZ> caTree, cbTree;
        pcl::PointCloud<pcl::PointXYZ>::Ptr caC(new pcl::PointCloud<pcl::PointXYZ>), cbC(new pcl::PointCloud<pcl::PointXYZ>);
        for (int id : closeA) caC->points.push_back(pcloud->points[id]);
        for (int id : closeB) cbC->points.push_back(pcloud->points[id]);
        caC->width = caC->points.size(); caC->height = 1;
        cbC->width = cbC->points.size(); cbC->height = 1;
        caTree.setInputCloud(caC); cbTree.setInputCloud(cbC);
        std::vector<int> rr; std::vector<float> dd;
        for (int id : A) {
            if (patchA.size() >= 300) break;
            rr.clear(); dd.clear();
            if (caTree.nearestKSearch(pcloud->points[id], 1, rr, dd) > 0 && dd[0] <= closeMM * closeMM) patchA.push_back(id);
        }
        for (int id : B) {
            if (patchB.size() >= 300) break;
            rr.clear(); dd.clear();
            if (cbTree.nearestKSearch(pcloud->points[id], 1, rr, dd) > 0 && dd[0] <= closeMM * closeMM) patchB.push_back(id);
        }
    }
    if (patchA.empty() || patchB.empty()) return false;
    Eigen::Vector3f ma = meanNormal234(patchA, pnormals), mb = meanNormal234(patchB, pnormals);
    Eigen::Vector4f ma4(ma(0), ma(1), ma(2), 0.0f), mb4(mb(0), mb(1), mb(2), 0.0f);
    if (pcl::getAngle3D(ma4, mb4, true) > patchDeg) return false;
    if (curvRelDiff234(meanCurv234(closeA, pnormals), meanCurv234(closeB, pnormals)) > curvRel) return false;
    // internal-point verification: points > 5mm from any close point on either side
    std::vector<int> intA, intB;
    {
        pcl::KdTreeFLANN<pcl::PointXYZ> allCloseTree;
        pcl::PointCloud<pcl::PointXYZ>::Ptr allClose(new pcl::PointCloud<pcl::PointXYZ>);
        for (int id : closeA) allClose->points.push_back(pcloud->points[id]);
        for (int id : closeB) allClose->points.push_back(pcloud->points[id]);
        allClose->width = allClose->points.size(); allClose->height = 1;
        allCloseTree.setInputCloud(allClose);
        std::vector<int> rr; std::vector<float> dd;
        size_t stA = std::max<size_t>(1, A.size() / 60), stB = std::max<size_t>(1, B.size() / 60);
        for (size_t i = 0; i < A.size() && intA.size() < 50; i += stA) {
            int id = A[i];
            rr.clear(); dd.clear();
            if (allCloseTree.nearestKSearch(pcloud->points[id], 1, rr, dd) > 0 && dd[0] > 25.0f) intA.push_back(id);
        }
        for (size_t i = 0; i < B.size() && intB.size() < 50; i += stB) {
            int id = B[i];
            rr.clear(); dd.clear();
            if (allCloseTree.nearestKSearch(pcloud->points[id], 1, rr, dd) > 0 && dd[0] > 25.0f) intB.push_back(id);
        }
    }
    if (intA.size() >= 10 && intB.size() >= 10) {
        Eigen::Vector3f ia = meanNormal234(intA, pnormals), ib = meanNormal234(intB, pnormals);
        Eigen::Vector4f ia4(ia(0), ia(1), ia(2), 0.0f), ib4(ib(0), ib(1), ib(2), 0.0f);
        if (pcl::getAngle3D(ia4, ib4, true) > patchDeg) return false;
        if (curvRelDiff234(meanCurv234(intA, pnormals), meanCurv234(intB, pnormals)) > curvRel) return false;
    }
    return true;
}

static void mergePaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals,
    std::vector<pcl::PointIndices>& pclusters,
    double closeMM, double patchDeg, double curvRel)
{
    std::cout << "[PAPER-234] merge to fixpoint: closeMM=" << closeMM << " patchDeg=" << patchDeg << " curvRel=" << curvRel << std::endl;
    int pass = 0;
    bool any = true;
    while (any) {
        any = false;
        ++pass;
        std::vector<char> dead(pclusters.size(), 0);
        for (size_t i = 0; i < pclusters.size(); ++i) {
            if (dead[i]) continue;
            for (size_t j = i + 1; j < pclusters.size(); ++j) {
                if (dead[j]) continue;
                if (tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, closeMM, patchDeg, curvRel)) {
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

void surfaceSegmentation(std::string filePath,''' 

once("void surfaceSegmentation(std::string filePath,", PAPER)

# signature: extend with paper params
once(
 "bool planeRule = false, double planeJoinDeg = 60.0, double planeDistMM = 2.0, int planeWindow = 100)",
 "bool planeRule = false, double planeJoinDeg = 60.0, double planeDistMM = 2.0, int planeWindow = 100,\n        bool paperChain = false, double paperTheta = 4.0, double paperKappa = 1.0, int paperNB = 10,\n        double paperCloseMM = 3.0, double paperPatchDeg = 15.0, double paperCurvRel = 0.30)",
)

# grow dispatch: three-way
once(
 "        if (planeRule) {",
 "        if (paperChain) {\n"
 "            std::cout << \"[PAPER-234] paper grow: thetaDeg=\" << paperTheta << \" kappa=\" << paperKappa << \" nb=\" << paperNB << std::endl;\n"
 "            clusters = growPaper234(cloud, normals, dynMinCluster, paperNB, paperTheta, paperKappa);\n"
 "        } else if (planeRule) {",
)

# merge dispatch: paper merge + resort + classify instead of mergeClusters
once(
 '        std::cout << "Calling mergeClusters function." << std::endl;\n        mergeClusters(cloudWithNormals, clusters);',
 '        if (paperChain) {\n'
 '            std::cout << "Calling mergePaper234 function." << std::endl;\n'
 '            mergePaper234(cloud, normals, clusters, paperCloseMM, paperPatchDeg, paperCurvRel);\n'
 '            std::sort(clusters.begin(), clusters.end(), myobject3);\n'
 '            classifyAndOrderPaper234(cloud, normals, clusters);\n'
 '        } else {\n'
 '        std::cout << "Calling mergeClusters function." << std::endl;\n'
 '        mergeClusters(cloudWithNormals, clusters);\n'
 '        }',
)

# call site: env knobs + pass-through + log
once(
 '        bool planeRule = false;\n        if (const char* e = std::getenv("SFS_PLANE_RULE")) { if (*e && std::string(e) != "0") planeRule = true; }',
 '        bool planeRule = false;\n'
 '        if (const char* e = std::getenv("SFS_PLANE_RULE")) { if (*e && std::string(e) != "0") planeRule = true; }\n'
 '        bool paperChain = false;\n'
 '        if (const char* e = std::getenv("SFS_PAPER_CHAIN")) { if (*e && std::string(e) != "0") paperChain = true; }\n'
 '        double paperTheta = 4.0, paperKappa = 1.0, paperCloseMM = 3.0, paperPatchDeg = 15.0, paperCurvRel = 0.30;\n'
 '        int paperNB = 10;\n'
 '        if (const char* e = std::getenv("SFS_PAPER_THETA")) { if (*e) paperTheta = std::stod(e); }\n'
 '        if (const char* e = std::getenv("SFS_PAPER_KAPPA")) { if (*e) paperKappa = std::stod(e); }\n'
 '        if (const char* e = std::getenv("SFS_PAPER_NB")) { if (*e) paperNB = std::stoi(e); }\n'
 '        if (const char* e = std::getenv("SFS_PAPER_CLOSE_MM")) { if (*e) paperCloseMM = std::stod(e); }\n'
 '        if (const char* e = std::getenv("SFS_PAPER_PATCH_DEG")) { if (*e) paperPatchDeg = std::stod(e); }\n'
 '        if (const char* e = std::getenv("SFS_PAPER_CURV_REL")) { if (*e) paperCurvRel = std::stod(e); }',
)
once(
 '        surfaceSegmentation(downsampledFilePath, minCluster, noOfNeighbours, smoothnessAngleThreshold, curvatureThreshold,\n            planeRule, planeJoinDeg, planeDistMM, planeWindow);',
 '        surfaceSegmentation(downsampledFilePath, minCluster, noOfNeighbours, smoothnessAngleThreshold, curvatureThreshold,\n            planeRule, planeJoinDeg, planeDistMM, planeWindow,\n            paperChain, paperTheta, paperKappa, paperNB, paperCloseMM, paperPatchDeg, paperCurvRel);',
)
once(
 '<< " joinDeg=" << planeJoinDeg << " distMM=" << planeDistMM << " window=" << planeWindow << std::endl;',
 '<< " joinDeg=" << planeJoinDeg << " distMM=" << planeDistMM << " window=" << planeWindow\n                  << " paper=" << (paperChain ? "PAPER-CHAIN" : "off") << " theta=" << paperTheta << " kappa=" << paperKappa << " nb=" << paperNB << std::endl;',
)

with open(SRC, "wb") as f:
    f.write(txt.encode("utf-8", errors="surrogateescape"))
print("paper patch OK, bytes:", len(txt))
