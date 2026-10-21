"""T234 paper arm v3: Appendix-A-normative cluster merge (Table I + Alg 1).
Provenance per criterion (-> Comments):
 - boundary pairs within rhoD=1.0, >=3 pairs, boundary status via k1=10 NN:
   Appendix A Alg 1 Step 1 (supplement repo 404 from laptop AND Spartan,
   so Appendix A is the implemented source).
 - k2=30-NN average normals, dot >= rhoN=0.95; |mean curv diff| < rhoC=0.1:
   Appendix A Step 2 + Table I.
 - internal point = median by perp distance to cluster PCA axis;
   dot >= rhoInN=0.75, |curv diff| < rhoInC=0.25: Appendix A Step 3 + Table I.
 - merge j into i, repeat to fixpoint: Appendix A Step 4 + Alg 1 line 28.
Grow provenance (unchanged): paper main-text Sec IV-B1 params (min-curvature
seed, n_b=10, tau_kappa=1, tau_theta=4) + Rabbani[35]/PCL current-front
reference (v2 correction; fixed-seed v1 over-segmented 85 grow clusters).
CGAL-manual check: CGAL 5.0 shape-detection region growing is a shape-fitting
family, not the paper's patch-segmentation params -- params implemented
directly from the paper text."""
SRC = "C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp"

with open(SRC, "rb") as f:
    txt = f.read().replace(b"\r\n", b"\n").decode("utf-8", errors="surrogateescape")

def once(old, new):
    global txt
    n = txt.count(old)
    assert n == 1, f"anchor x{n}: {old[:70]!r}"
    txt = txt.replace(old, new)

def span(startMark, endMark, new):
    global txt
    i = txt.index(startMark)
    j = txt.index(endMark)
    assert i < j, "span order"
    txt = txt[:i] + new + txt[j:]

HELPERS = '''static Eigen::Vector3f pcaAxis234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
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

'''

once("static double curvRelDiff234(double a, double b)\n{\n    double d = std::fabs(a - b);\n    double m = std::max(std::fabs(a), std::fabs(b));\n    if (m < 1e-9) return 0.0;\n    return d / m;\n}\n", HELPERS)

TRYMERGE = '''// Appendix-A-normative pair verdict (provenance in patch234d.py header).
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

'''

span("static bool tryMergePair234(", "static void mergePaper234(", TRYMERGE)

MERGE = '''static void mergePaper234(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
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

'''

span("static void mergePaper234(", "// Axis-ray classification", MERGE)

once("bool paperChain = false, double paperTheta = 4.0, double paperKappa = 1.0, int paperNB = 10,\n        double paperCloseMM = 3.0, double paperPatchDeg = 15.0, double paperCurvRel = 0.30)",
     "bool paperChain = false, double paperTheta = 4.0, double paperKappa = 1.0, int paperNB = 10,\n        double paperRhoD = 1.0, double paperRhoN = 0.95, double paperRhoC = 0.1, double paperRhoInN = 0.75, double paperRhoInC = 0.25)")

once("            mergePaper234(cloud, normals, clusters, paperCloseMM, paperPatchDeg, paperCurvRel);",
     "            mergePaper234(cloud, normals, clusters, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC, 10, 30);")

once("        double paperTheta = 4.0, paperKappa = 1.0, paperCloseMM = 3.0, paperPatchDeg = 15.0, paperCurvRel = 0.30;",
     "        double paperTheta = 4.0, paperKappa = 1.0, paperRhoD = 1.0, paperRhoN = 0.95, paperRhoC = 0.1, paperRhoInN = 0.75, paperRhoInC = 0.25;")

once('        if (const char* e = std::getenv("SFS_PAPER_CLOSE_MM")) { if (*e) paperCloseMM = std::stod(e); }',
     '        if (const char* e = std::getenv("SFS_PAPER_RHOD")) { if (*e) paperRhoD = std::stod(e); }')

once('        if (const char* e = std::getenv("SFS_PAPER_PATCH_DEG")) { if (*e) paperPatchDeg = std::stod(e); }',
     '        if (const char* e = std::getenv("SFS_PAPER_RHON")) { if (*e) paperRhoN = std::stod(e); }')

once('        if (const char* e = std::getenv("SFS_PAPER_CURV_REL")) { if (*e) paperCurvRel = std::stod(e); }',
     '        if (const char* e = std::getenv("SFS_PAPER_RHOC")) { if (*e) paperRhoC = std::stod(e); }\n        if (const char* e = std::getenv("SFS_PAPER_RHOINN")) { if (*e) paperRhoInN = std::stod(e); }\n        if (const char* e = std::getenv("SFS_PAPER_RHOINC")) { if (*e) paperRhoInC = std::stod(e); }')

once("            paperChain, paperTheta, paperKappa, paperNB, paperCloseMM, paperPatchDeg, paperCurvRel);",
     "            paperChain, paperTheta, paperKappa, paperNB, paperRhoD, paperRhoN, paperRhoC, paperRhoInN, paperRhoInC);")

with open(SRC, "wb") as f:
    f.write(txt.encode("utf-8", errors="surrogateescape"))
print("patch234d OK, bytes:", len(txt))
