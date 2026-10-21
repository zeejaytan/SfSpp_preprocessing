# T234 plane arm (PARKED) — exam results, join60/dist2.0/W100, SFS_PLANE_RULE=1

- Mesh binary md5: 88b6f406e768ce4bbbde3ca814643b4f (build-234, job 33615566 COMPLETED 0:0)
- Edge binary md5: dc472b0e87c934b6c487ff8637209864 (reused 221-pattern)
- Jobs (all sacct COMPLETED 0:0): 33615652 P22-plane (37s), 33615653 P12-plane (26s), 33615654 P12-old45 (17s), 33615655 Jug1-plane mesh-only (39s)
- Patched file: .scratch/pota234/mesh_processing_headless.cpp (md5 a26e98f90e241a1810452c159a105298); diff vs origin/main: .scratch/pota234/splitter234.diff (154 lines)
- Build lesson: NEVER name a local `qh` — qhull headers + -Dqh_QHpointer hijack it (parse error at use site, probe-clean). Renamed to `fh`.

## Cluster health (mesh-log cluster sizes + UN ply `element vertex`)

| run | clusters | top2 | third | UN | cloud |
|---|---|---|---|---|---|
| P22-plane | 14: 4951/3751/2713/1438/1395/1046/799/707/271/270/197/186/141/129 | 48.4% FAIL (8702/17994) | 15.1% FAIL | 61 (0.3%) | 18055 |
| P12-plane | 11: 6720/6069/2960/2608/1145/1105/368/322/162/129/80 | 59.0% FAIL | 13.7% FAIL | 182 (0.8%) | 21850 |
| P12-old45 (PCL path, new bin) | 9: 9674/6441/1114/1009/389/308/240/104/77 | 83.3% PASS | 5.8% PASS | 2494 (11.4%) | 21850 |
| Jug1-plane | 18: 4762/3785/3649/3521/2424/1832/... | 35.0% FAIL | — | 137 (0.6%) | 24567 |

## Gap table (222 method, filed resampled faces) + fork zone (turn [-4.15, 18.58, 439.21])

| run | symmin | p1 | p50 | frac<2mm | fork zone S0/S1 |
|---|---|---|---|---|---|
| P22-plane | 0.218 FAIL | 0.84 | 4.89 | 6.48% | 0/383 SINGLE-FACE PASS |
| P12-plane | 0.000 FAIL | 1.20 | 9.12 | 2.11% | — |
| P12-old45 | 1.725 (closest, still <2) | 4.93 | 9.15 | 0.08% | — |

## Lanes (slot-verified, bar med<2 cov>=90%)

- P22-plane: SINGLE 40-dot lane: Bl0->o0 5.10/10.0, Bl0->o1 5.31/5.0 — stub FAIL.
- P12-plane: SWAPPED slots; Bl0->o1 7.12/0.6, Bl1->o0 10.04/10.1 — garbage FAIL.
- P12-old45: SWAPPED slots; Bl0->o1 0.81/63.6 below-bar, Bl1->o0 0.77/99.3 AT-BAR (vs 223: 0.63/89.0 + 0.77/98.8; new-binary PCL path differs from 221 faces — sanity anchor only).

## Plane-arm verdict: HONEST-NEGATIVE

Separates P22's fork (single-face, 383 S1 dots) but shatters every face (P22/P12/Jug all multi-fragment, top2 36-59%) and destroys lanes (P12 med 7-10, P22 stub). The 60deg/2mm windowed gate over-segments twist+noise; merging (not present in this arm) would be needed. UN tiny (rule over-files, never starves).
