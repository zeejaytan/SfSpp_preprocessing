
// ======================= TICKET 276: merge diagnostics =======================
// SFS_MERGE_DIAG reads once per piece:
//   unset / empty / "0" -> every function below is skipped (inert)
//   "1"                 -> dump per-point post-merge cluster labels
//   "split"             -> also split the largest cluster in two by a plane
//                          through its centroid (normal = its PCA axis) BEFORE
//                          merging, then report whether the halves are rejoined.
// The dump labels every point of the segmented cloud: cluster 0 = Surface_0,
// cluster 1 = Surface_1, cluster >= 2 = dropped, -1 = in no cluster.
static std::string mergeDiagMode276()
{
    const char* e = std::getenv("SFS_MERGE_DIAG");
    if (!e || !*e || std::string(e) == "0") return std::string();
    return std::string(e);
}

static void splitLargestCluster276(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    std::vector<pcl::PointIndices>& pclusters, std::vector<char>& half276)
{
    if (pclusters.empty()) return;
    size_t big = 0;
    for (size_t c = 1; c < pclusters.size(); ++c)
        if (pclusters[c].indices.size() > pclusters[big].indices.size()) big = c;
    const std::vector<int> src = pclusters[big].indices;
    if (src.size() < 2) return;
    Eigen::Vector3f ax = pcaAxis234(pcloud, src);
    Eigen::Vector3f c0(0.0f, 0.0f, 0.0f);
    for (int id : src) c0 += pcloud->points[id].getVector3fMap();
    c0 /= static_cast<float>(src.size());
    half276.assign(pcloud->points.size(), static_cast<char>(2));
    std::vector<int> ha, hb;
    for (int id : src) {
        Eigen::Vector3f p = pcloud->points[id].getVector3fMap();
        if ((p - c0).dot(ax) >= 0.0f) { ha.push_back(id); half276[id] = 0; }
        else { hb.push_back(id); half276[id] = 1; }
    }
    std::cout << "[MERGE-DIAG-276] split: cluster " << big << " n=" << src.size()
              << " -> halfA=" << ha.size() << " halfB=" << hb.size()
              << " plane n=(" << ax.x() << "," << ax.y() << "," << ax.z() << ")"
              << " c=(" << c0.x() << "," << c0.y() << "," << c0.z() << ")" << std::endl;
    pcl::PointIndices pa, pb;
    pa.indices = ha;
    pb.indices = hb;
    pclusters[big] = pa;
    pclusters.push_back(pb);
}

static void reportSplit276(const std::vector<char>& half276,
    const std::vector<pcl::PointIndices>& pclusters, int nBefore)
{
    std::map<int, long> h0, h1;
    for (size_t c = 0; c < pclusters.size(); ++c)
        for (int id : pclusters[c].indices) {
            if (static_cast<size_t>(id) >= half276.size()) continue;
            if (half276[id] == 0) h0[static_cast<int>(c)]++;
            else if (half276[id] == 1) h1[static_cast<int>(c)]++;
        }
    long n0 = 0, n1 = 0;
    int d0 = -1, d1 = -1;
    for (auto& kv : h0) if (kv.second > n0) { n0 = kv.second; d0 = kv.first; }
    for (auto& kv : h1) if (kv.second > n1) { n1 = kv.second; d1 = kv.first; }
    std::cout << "[MERGE-DIAG-276] split-check: halfA -> cluster " << d0 << " (" << n0
              << " pts), halfB -> cluster " << d1 << " (" << n1 << " pts), rejoined="
              << ((d0 == d1 && d0 >= 0) ? "YES" : "NO")
              << ", clusters before-split=" << nBefore << " after-split=" << (nBefore + 1)
              << " after-merge=" << pclusters.size() << std::endl;
}

static void dumpMergeDiag276(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    const std::vector<pcl::PointIndices>& pclusters, double theta,
    const std::vector<char>& half276)
{
    const std::string dumpName = "mergeDiag276_" + fileNameOnly + ".txt";
    std::ofstream f(dumpName.c_str());
    if (!f.is_open()) {
        std::cout << "[MERGE-DIAG-276] cannot open " << dumpName << std::endl;
        return;
    }
    std::vector<int> lab(pcloud->points.size(), -1);
    for (size_t c = 0; c < pclusters.size(); ++c)
        for (int id : pclusters[c].indices)
            if (static_cast<size_t>(id) < lab.size()) lab[id] = static_cast<int>(c);
    long s0 = pclusters.size() > 0 ? static_cast<long>(pclusters[0].indices.size()) : 0;
    long s1 = pclusters.size() > 1 ? static_cast<long>(pclusters[1].indices.size()) : 0;
    long dropped = 0, unclustered = 0;
    for (size_t i = 0; i < lab.size(); ++i) {
        if (lab[i] < 0) ++unclustered;
        else if (lab[i] >= 2) ++dropped;
    }
    f << std::setprecision(7);
    f << "# npoints " << pcloud->points.size() << " nclusters " << pclusters.size()
      << " thetaDeg " << theta << " split " << (half276.empty() ? 0 : 1) << "\n";
    for (size_t c = 0; c < pclusters.size(); ++c)
        f << "# cluster " << c << " size " << pclusters[c].indices.size()
          << " surface " << ((c < 2) ? 1 : 0) << "\n";
    f << "# columns: index cluster x y z half\n";
    for (size_t i = 0; i < pcloud->points.size(); ++i) {
        int hv = (half276.empty() || i >= half276.size()) ? -1 : static_cast<int>(half276[i]);
        f << i << " " << lab[i] << " " << pcloud->points[i].x << " "
          << pcloud->points[i].y << " " << pcloud->points[i].z << " " << hv << "\n";
    }
    f.close();
    std::cout << "[MERGE-DIAG-276] labels: npoints=" << pcloud->points.size()
              << " nclusters=" << pclusters.size() << " surface0=" << s0 << " surface1=" << s1
              << " dropped=" << dropped << " unclustered=" << unclustered
              << " -> " << dumpName << std::endl;
}

