import io, sys

P = r"C:\PR\worktrees\sfs\276\mesh_processing_headless.cpp"
raw = io.open(P, "r", newline="", encoding="utf-8", errors="surrogateescape").read()
lf = raw.replace("\r\n", "\n")

def sub(text, old, new, tag):
    n = text.count(old)
    assert n == 1, "%s anchor count %d" % (tag, n)
    return text.replace(old, new)

# ---- 1. globals + prefix helper inserted before tryMergePair234 ----
anchor1 = "// One merge verdict for a cluster pair. All thresholds are the paper-arm\n"
ins1 = """// ---- ticket 276 Phase 2: per-cluster-pair test values (SFS_MERGE_PAIRS=1) ----
// Diagnostic only: prints every Appendix-A test quantity for every cluster pair
// examined, in every pass. Inert when the switch is unset (no output, no work).
static bool gPairs276 = false;

static void pairPrefix276(int pass, int ci, int cj, size_t nA, size_t nB,
    size_t bA, size_t bB, size_t scanned, size_t smallTot,
    size_t npairs, bool cap, const std::vector<double>& pd)
{
    double dmin = 0.0, dmed = 0.0;
    if (!pd.empty()) {
        std::vector<double> v = pd;
        std::sort(v.begin(), v.end());
        dmin = v.front();
        dmed = v[v.size() / 2];
    }
    std::cout << "[PAIR-276] pass=" << pass << " c" << ci << "-c" << cj
              << " nA=" << nA << " nB=" << nB
              << " bnd=" << bA << "/" << bB
              << " scan=" << scanned << "/" << smallTot
              << " cut=" << (smallTot - scanned)
              << " pairs=" << npairs << " cap=" << (cap ? 1 : 0)
              << " dmin=" << dmin << " dmed=" << dmed;
}

"""
lf = sub(lf, anchor1, ins1 + anchor1, "anchor1 globals")

# ---- 2. signature gains the cluster ids and the pass number ----
lf = sub(lf,
 "    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k2)\n{\n    if (A.empty() || B.empty()) return false;\n",
 "    double rhoD, double rhoN, double rhoC, double rhoInN, double rhoInC, int k2,\n    int ci = -1, int cj = -1, int pass = 0)\n{\n    if (A.empty() || B.empty()) return false;\n",
 "anchor2 signature")

# ---- 3. empty boundary set ----
lf = sub(lf,
 "    if (bA.empty() || bB.empty()) return false;\n",
 """    if (bA.empty() || bB.empty()) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), 0, 0, 0, false, std::vector<double>());
            std::cout << " verdict=REJECT:empty-boundary" << std::endl;
        }
        return false;
    }
""",
 "anchor3 empty-boundary")

# ---- 4. the pair search: count scanned points and the cap ----
lf = sub(lf,
 """    std::vector<std::pair<int,int> > pairs;
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
""",
 """    std::vector<std::pair<int,int> > pairs;
    std::vector<int> oneI; std::vector<float> oneD;
    std::vector<double> pd276;
    size_t scanned276 = 0;
    for (size_t i = 0; i < sP->size() && pairs.size() < 200; ++i) {
        ++scanned276;
        int sid = (*sP)[i];
        oneI.clear(); oneD.clear();
        if (lT.nearestKSearch(pcloud->points[sid], 1, oneI, oneD) <= 0) continue;
        if (oneD[0] <= rhoD * rhoD) {
            int a = sIsA ? sid : (*lP)[oneI[0]];
            int b = sIsA ? (*lP)[oneI[0]] : sid;
            pairs.push_back(std::make_pair(a, b));
            if (gPairs276) pd276.push_back(std::sqrt(static_cast<double>(oneD[0])));
        }
    }
    const bool cap276 = (pairs.size() >= 200) && (scanned276 < sP->size());
    if (pairs.size() < 3) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " rhoD2=" << rhoD * rhoD << " verdict=REJECT:pairs<3" << std::endl;
        }
        return false;
    }
""",
 "anchor4 pair search")

# ---- 5. degenerate normals ----
lf = sub(lf,
 "    float nA = sNA.norm(), nB = sNB.norm();\n    if (nA < 1e-9f || nB < 1e-9f) return false;\n",
 """    float nA = sNA.norm(), nB = sNB.norm();
    if (nA < 1e-9f || nB < 1e-9f) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " verdict=REJECT:normal-zero" << std::endl;
        }
        return false;
    }
""",
 "anchor5 normal zero")

# ---- 6. rhoN / rhoC ----
lf = sub(lf,
 """    if (sNA.dot(sNB) < rhoN) return false;
    if (std::fabs(sCA / pairs.size() - sCB / pairs.size()) >= rhoC) return false;
""",
 """    const double nrm276 = static_cast<double>(sNA.dot(sNB));
    const double cuv276 = std::fabs(sCA / pairs.size() - sCB / pairs.size());
    if (nrm276 < rhoN) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " rhoN=" << rhoN << " rhoC=" << rhoC << " verdict=REJECT:rhoN" << std::endl;
        }
        return false;
    }
    if (cuv276 >= rhoC) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " rhoN=" << rhoN << " rhoC=" << rhoC << " verdict=REJECT:rhoC" << std::endl;
        }
        return false;
    }
""",
 "anchor6 rhoN rhoC")

# ---- 7. inner representative point ----
lf = sub(lf,
 """    if (na.dot(nb) / (la * lb) < rhoInN) return false;
    if (std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature)) >= rhoInC) return false;
    return true;
""",
 """    const double inn276 = static_cast<double>(na.dot(nb) / (la * lb));
    const double icuv276 = std::fabs(static_cast<double>(pnormals->points[ia].curvature) - static_cast<double>(pnormals->points[ib].curvature));
    if (inn276 < rhoInN) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=REJECT:rhoInN" << std::endl;
        }
        return false;
    }
    if (icuv276 >= rhoInC) {
        if (gPairs276) {
            pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
            std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=REJECT:rhoInC" << std::endl;
        }
        return false;
    }
    if (gPairs276) {
        pairPrefix276(pass, ci, cj, A.size(), B.size(), bA.size(), bB.size(), scanned276, sP->size(), pairs.size(), cap276, pd276);
        std::cout << " nrm=" << nrm276 << " curv=" << cuv276 << " inner=" << inn276 << " icurv=" << icuv276 << " verdict=ACCEPT" << std::endl;
    }
    return true;
""",
 "anchor7 inner")

# ---- 8. the switch: read once at the start of mergePaper234 ----
lf = sub(lf,
 """    std::cout << "[PAPER-234] appendix-A merge: rhoD=" << rhoD << " rhoN=" << rhoN << " rhoC=" << rhoC
""",
 """    gPairs276 = false;
    if (const char* e276 = std::getenv("SFS_MERGE_PAIRS")) gPairs276 = (*e276 && std::string(e276) != "0");
    if (gPairs276) std::cout << "[PAIR-276] enabled: printing every cluster pair's test values" << std::endl;
    std::cout << "[PAPER-234] appendix-A merge: rhoD=" << rhoD << " rhoN=" << rhoN << " rhoC=" << rhoC
""",
 "anchor8 switch")

# ---- 9. call site passes the cluster ids and the pass ----
lf = sub(lf,
 """                if (tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, isBnd,
                        axes[i], axes[j], rhoD, rhoN, rhoC, rhoInN, rhoInC, k2)) {
""",
 """                if (tryMergePair234(pcloud, pnormals, pclusters[i].indices, pclusters[j].indices, isBnd,
                        axes[i], axes[j], rhoD, rhoN, rhoC, rhoInN, rhoInC, k2,
                        static_cast<int>(i), static_cast<int>(j), pass)) {
""",
 "anchor9 call site")

out = lf.replace("\n", "\r\n")
io.open(P, "w", newline="", encoding="utf-8", errors="surrogateescape").write(out)
print("patched bytes", len(out))
