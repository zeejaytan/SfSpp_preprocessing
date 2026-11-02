# ticket 59 Stage 1 draft patch -- SFS_BREAK_STOP opt-in growth stop (NOT APPLIED YET)
# Gate: apply only after the Stage-0 decision table is recorded and >=1 signal separates
# fracture+roll from wall with stated margin AND Pot A control stays clean.
# Param values marked __STAGE0__ are filled from the decision table margins.
#
# 1) globals (place near the worness-54 globals, ~:4870):
static bool  g_breakStop59 = false;         // SFS_BREAK_STOP=1 arms it; default OFF
static double g_breakStopMinMM59 = __STAGE0_MIN__;   // slab lower bound, mm
static double g_breakStopMaxMM59 = __STAGE0_MAX__;   // slab upper bound, mm
static double g_breakStopEpsMM59 = __STAGE0_EPS__;   // nearest-hit radius, mm
static double g_breakStopExitDot59 = __STAGE0_DOT__; // opposing-normal dot bound
static std::vector<uint8_t> g_breakStopFlags59;      // 1 = break-like point
#
# 2) env parse (place with the SFS_* reads in main, after :4925):
if (const char* e59 = std::getenv("SFS_BREAK_STOP")) {
    if (*e59 && std::string(e59) != "0") g_breakStop59 = true;
}
if (const char* e59 = std::getenv("SFS_BREAK_STOP_MIN_MM")) { if (*e59) g_breakStopMinMM59 = std::stod(e59); }
if (const char* e59 = std::getenv("SFS_BREAK_STOP_MAX_MM")) { if (*e59) g_breakStopMaxMM59 = std::stod(e59); }
if (const char* e59 = std::getenv("SFS_BREAK_STOP_EPS_MM")) { if (*e59) g_breakStopEpsMM59 = std::stod(e59); }
#
# 3) flag computation (new static function before growPaper234):
// TICKET 59: per-point wall-pairing flags. March along +/-normal from each point;
// a nearest-cloud hit within epsMM whose normal opposes the query normal
// (dot <= exitDot) within [minMM,maxMM] marks the point WALL-LIKE (flag 0);
// no such hit in either direction marks it BREAK-LIKE (flag 1). Only called when
// SFS_BREAK_STOP arms the stop; with the env unset this function never runs and
// outputs are byte-identical to the shipped chain.
static void computeBreakStopFlags59(pcl::PointCloud<pcl::PointXYZ>::Ptr pcloud,
    pcl::PointCloud<pcl::Normal>::Ptr pnormals)
{
    const int NP = static_cast<int>(pcloud->points.size());
    g_breakStopFlags59.assign(NP, 1);
    if (NP == 0) return;
    pcl::KdTreeFLANN<pcl::PointXYZ> kdt59;
    kdt59.setInputCloud(pcloud);
    const double step59 = std::max(0.10, g_breakStopEpsMM59 * 0.75);
    long nWall59 = 0;
    for (int i = 0; i < NP; ++i) {
        const Eigen::Vector3f p(pcloud->points[i].x, pcloud->points[i].y, pcloud->points[i].z);
        const Eigen::Vector3f n(pnormals->points[i].normal_x, pnormals->points[i].normal_y, pnormals->points[i].normal_z);
        for (int dir59 = 0; dir59 < 2; ++dir59) {
            const Eigen::Vector3f d = (dir59 == 0 ? n : -n);
            for (double t = g_breakStopMinMM59; t <= g_breakStopMaxMM59 + 1e-9; t += step59) {
                pcl::PointXYZ q;
                q.x = p.x() + static_cast<float>(d.x() * t);
                q.y = p.y() + static_cast<float>(d.y() * t);
                q.z = p.z() + static_cast<float>(d.z() * t);
                std::vector<int> idx59(1); std::vector<float> dist59(1);
                if (kdt59.nearestKSearch(q, 1, idx59, dist59) > 0
                    && std::sqrt(dist59[0]) <= g_breakStopEpsMM59
                    && idx59[0] != i) {
                    const pcl::Normal& hn = pnormals->points[idx59[0]];
                    const float dot59 = hn.normal_x * n.x() + hn.normal_y * n.y() + hn.normal_z * n.z();
                    if (dot59 <= g_breakStopExitDot59) { g_breakStopFlags59[i] = 0; ++nWall59; break; }
                }
            }
            if (g_breakStopFlags59[i] == 0) break;
        }
    }
    std::cout << "[BREAK-59] piece=" << fileNameOnly << " wall_like=" << nWall59
              << " break_like=" << (NP - nWall59) << " of " << NP
              << " min_mm=" << g_breakStopMinMM59 << " max_mm=" << g_breakStopMaxMM59
              << " eps_mm=" << g_breakStopEpsMM59 << " exit_dot=" << g_breakStopExitDot59 << std::endl;
}
#
# 4) growth stop in the candidate loop (after the kappa test :3349, before the angle test :3353):
+                if (g_breakStop59 && !g_breakStopFlags59.empty() && g_breakStopFlags59[cand]) continue;  // TICKET 59
#
# 5) compute-once-armed at the paper-grow call site (:3851-3853):
 if (paperChain) {
+    if (g_breakStop59) computeBreakStopFlags59(cloud, normals);   // TICKET 59 (recomputed per rung: cloud rebuilt each iteration)
     std::cout << "[PAPER-234] paper grow: thetaDeg=" << thetaEff42 << ...
#
# Notes: rejection applies to CANDIDATES only, not seeds (minimal change; break faces are
# high-curvature and already fail kappa at seed sort); the theta ladder still selects its
# rung per outcome rules -- with the stop armed, floor-clearing counts may shift rung
# selection (to be measured in Stage 2); plane/PCL growth paths untouched.
