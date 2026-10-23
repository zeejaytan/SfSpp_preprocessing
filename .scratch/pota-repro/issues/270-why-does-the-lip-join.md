# 270 — Why does the lip join the surface? (one cluster, or two merged?)

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-248 (diagnosis only: NO C++ change, NO build, NO main commits)
Needs-eye: no

## Why

Ticket 269 cleared the boundary step: radius 1.5-8 mm, angle 60-170 deg, the (inert) veto, the
snap and the paper's rule as written all return the same 4 mm-outboard curve, because that curve
is the silhouette of the surface cloud we hand it. The surface cloud itself (Pot D Piece 03,
`Surface_1`) runs **4.4-5.0 mm past the crest** of the lip (p99.5 +4.36, max +5.04 mm of the
19 194 points within 8 mm of the stretch), while the author's breakline sits **at** the crest,
where the face is flattest (6.4-8.7 deg tilt versus 22.2 deg median at our line).

The paper separates surfaces by region growing with a normal threshold tau_theta, then merges
clusters to a fixpoint, then selects the **two largest clusters** as inner and outer surfaces
(C:/PR/papers/text/sfspp-2502.13986v1.md:147-162, :155). Then and only then is the edge line the
boundary of the interior surface (:164, verified in 269).

So the lip is in our surface for one of two reasons, and they need different fixes:

* **(P) parameter** — region growing walked around the crest: the per-step normal change never
  exceeded tau_theta at the lip, so the flat face and the roll-over are ONE cluster. Fix = a
  number (tau_theta), paper-faithful, no new criterion.
* **(R) rule** — the roll-over grew as its own cluster and was then merged into / selected with
  the face by our merging or top-2 selection. Fix = the merge/selection rule, also paper-faithful,
  but a different place in the code entirely.

This ticket answers P or R and names the number or the rule. It builds nothing.

## Goal

**1. Quote the paper verbatim** (path:line) for: the region-growing criterion and tau_theta; the
cluster-merging criterion and its fixpoint; the "two largest clusters" selection; anything that
says how far the interior cluster may run into the break face. List every parameter the text gives
and every one it omits. Check the trap 269 hit: TABLE I at :464-473 is captioned "Parameters used
in cluster merging algorithm" — record which of its numbers belong to which step.

**2. Instrument the clustering on Pot D Piece 03**, and say for the lip faces whether they are
*one* cluster with the flat face or a separate cluster that got merged/selected in:
- how many clusters exist near the piece, their sizes, and which are the top two before and after
  our merging step (i.e. does the lip have its own cluster at all?);
- for the mesh faces within about +-8 mm of the stretch, the cluster id of each, and the normal
  tilt by cross-lane band (269 already has the tilt profile: reuse it, do not re-fit it);
- the **per-step normal-angle distribution along the grow path across the crest** — on the flat
  face versus at the lip — with our code's actual tau_theta marked on it. This is the P/R
  discriminator: if the median per-step angle at the crest is below tau_theta and the cluster is
  contiguous, it is P; if the lip is a distinct cluster with its own id, it is R.
- if merged: which rule fired, and what the top-2 selection would have been **without** the merge
  (does the roll-over take a top-2 slot and displace something?).

**3. Two guard pieces.** Run the same cluster-membership instrument on two pieces whose lanes are
already at bar — Pot D Piece 22 Bl1 (264/267: 0.57/95.1) and Pot D Piece 01 Bl1 (0.98/95.4); the
surfaces for both are already local under C:/PR/SfSpp_preprocessing-248/artifacts/pota269/ (Pot H)
and the Pot_D trees used by 267/268, else pull the few files from Spartan (no rebuild). Question:
**does our surface also run past the crest on a lane that scores at bar?** If yes, crest extent
alone does not explain the miss and the lever is somewhere else — say so plainly.

**4. Recommend**, with the specific value or rule change, what it would do to the two guards, and
what would overturn the recommendation.

## Boundary

- Diagnosis only. Do not edit C++ (no `edgeline_extraction_headless.cpp`, no
  `mesh_processing_headless.cpp`), do not build, do not commit to main. New files go under
  `artifacts/pota270/` and `pota270_*.py` in C:/PR/SfSpp_preprocessing-248 (untracked).
- You may run the **existing** binaries with **existing** inputs; no rebuild. Reuse ticket 268/269
  instruments (`artifacts/pota269/pota269_common.py`, `pota269_bagtilt.py`) rather than
  re-deriving s, tilt or the author lanes.
- The author's lanes are ground truth as given: `sfs_main/original_samples/SfS_pp/Breaklines/`.
  Do not re-derive, resample or reorder them. Report the md5 of every input you read.
- Laptop Python is fine for sets of this size (269's biggest run was 26 s). If you use a cluster
  job at all, one job maximum, and check `df` first — the project filesystem has been near-full.
- Judgement stays with the lead. Report facts, tables and the P/R call with its evidence line;
  do not decide what gets built.

## Acceptance criteria

1. Verbatim paper quotes with path:line for grow / tau_theta / merge / top-2 selection, plus the
   list of parameters the text omits.
2. Cluster table: count, sizes, top two before and after merging, and the lip's own cluster id
   (or "no cluster of its own").
3. Per-step normal-angle profile across the crest with our tau_theta marked, and the code line
   where that threshold lives (`mesh_processing_headless.cpp`).
4. An explicit **P or R** verdict with the one evidence line that settles it.
5. The two guard pieces instrumented with the same table, and a plain statement of whether they
   show the same crest extent.
6. A recommendation naming the number or the rule, its effect on the guards, and what would
   overturn it.

## Required evidence to report

- Every input path + md5; every job id + State/ExitCode if any job is run.
- The tables above as numbers, not prose.
- One figure: the lip cross-section coloured by **cluster id** (author dot black, our line red),
  so the P/R call can be seen and not just tabulated — `artifacts/pota270/`.
- The single quoted line that settles P or R.

## Comments (worker, 2026-10-23)

**Bottom line: it is (P), and the number is tau_theta = 4.0 deg at mesh_processing_headless.cpp:1770.**
The roll-over never gets a cluster of its own, so the merge step and the top-2 selection have nothing
to add or remove: on P03 the merge fired **zero** merges (9 clusters before, 9 after, one pass, no
"merge X into Y" line at all - artifacts/pota270/mesh267_P03.log:71-72), and the top two are
56345 + 54075 both before and after. The past-crest material sits **inside** cluster 1
(= Surface_1, 56345 pts): over the 255 mm stretch the kept exterior cluster spans
s = -7.38 ... **+5.04 mm**, with 1718 points beyond +2, 828 beyond +3 and 232 beyond +4 mm.

The one evidence line: **inside that kept cluster the past-crest lip is per-step SMOOTHER than the
flat face - step_min p50 0.45 deg versus 0.90 deg - while its total tilt differs by 17 deg
(7.2 deg at the crest, 26.9 deg at s = +4..+5 mm); the cheapest face-to-lip path inside the cluster
is bottlenecked at 3.45 deg, i.e. the 4.0 deg gate keeps it by 0.55 deg.** The gate is differential -
it compares the frontier point's normal with the candidate's, never with the region's seed normal
(mesh_processing_headless.cpp:1770) - so a 25 deg fold crossed in 0.5-1.2 deg steps is invisible to it.

Replication gate first: the Python port of growPaper234 (pota270_replay.py, on the md5-verified
SampledWithNormals.ply the binary actually grew) reproduces the binary's own cluster sizes -
P03 56438/54081 vs 56345/54075 (0.17% / 0.01%), P22 6756/5262 vs 6721/5230 (0.5% / 0.6%),
P01 8943/7996 vs 8941/7983 (0.02% / 0.16%). The 269 tilt table reproduces **exactly**: all 13 band
medians (27.2 34.4 35.6 36.5 36.3 32.2 24.4 8.7 6.4 16.5 21.0 21.4 22.0 deg) come back identical to
0.1 deg over n = 19163 points in 269's own window (dA <= 8 mm, author stations 157..304).

No cluster job was run, so no job id / State / ExitCode to report: every number below is laptop
Python on inputs that were already local. df was never needed.

---

### 1. The paper, verbatim (C:/PR/papers/text/sfspp-2502.13986v1.md)

Region growing and tau_theta - :151:

> "To segment the point cloud into exterior and interior surfaces, we use the region growing algorithm
> [35]. This algorithm starts from the point with the minimum curvature and expands by combining the
> n_b=10 neighboring points that have a curvature value of less than tau_kappa and a normal angle less
> than tau_theta with the point's normal. We set the values of tau_theta=4 and tau_kappa=1 to achieve
> clear separation of interior, exterior, and fractured surfaces."

:149 (why merging exists at all):

> "...Compared to the previous work [9], we introduce cluster merging to ensure robust surface
> segmentation."

Cluster merging - :153:

> "Cluster merging. Following the initial segmentation, we apply a cluster merging algorithm to improve
> the results. This process starts by identifying close point pairs between clusters using the
> k-nearest neighbors method. We then calculate average normal vectors for local patches around these
> pairs to check for normal similarity and compute and compare the average curvature of boundary points
> for each cluster pair. Additionally, internal points from each cluster are selected to further verify
> normal and curvature similarities. Clusters satisfying all these criteria are merged, and the process
> repeats until no further merges are possible. This approach effectively combines parts of the same
> surface that were excessively separated in the initial segmentation. Further details can be found in
> the supplementary material [43]."

Fixpoint again, in the appendix - :479:

> "...Once the conditions are met, cluster C_j is merged into C_i (Alg. 1, Step 4), and this process is
> repeated until no further mergers can be performed (Alg. 1, Line 28)."

Two-largest selection - :155 (note the ORDER: B-spline first, selection second):

> "Subsequently, B-Spline fitting is performed for each cluster to refine surface boundaries and
> uniformly sample the point cloud. Finally, we select the two largest clusters, representing the inner
> and outer surfaces. Note that region-growing algorithm and clustering naturally facilitate the
> separation of decorative parts, such as the nose and handle. The effect of tau_theta and subsequent
> part removal results are shown in Fig. 5 (a) and (b)."

Edge line from the interior surface - :164:

> "The interior surface point cloud boundary makes up the edge line extracted using the point cloud
> boundary-estimation method from the PCL library [30]."

Interior/exterior decision - :160-162 (ray test along the normal towards the axis, configuration with
more satisfied points wins). Our build-267 log shows the same test running ("interior_frac=0.9656").

**TABLE I attributed correctly (the 269 trap).** :464 "*Parameters used in cluster merging
algorithm*" - so every number in it belongs to the MERGING step, none to growing:

| number | value | which step it belongs to (paper line) |
|---|---|---|
| k1 | 10 | merging, Step 1 - boundary status of a point by its k1 neighbours (:467, :477) |
| k2 | 30 | merging, Step 2 - average normal of a boundary point from k2 neighbours (:468, :477) |
| rho_d | 1.0 | merging, Step 1 - distance threshold for boundary point pairs (:469, :477) |
| rho_n | 0.95 | merging, Step 2 - boundary normal similarity, dot product (:470, :477) |
| rho_c | 0.1 | merging, Step 2 - boundary mean-curvature difference (:471, :477) |
| rho_in,n | 0.75 | merging, Step 3 - internal representative point normal similarity (:472, :479) |
| rho_in,c | 0.25 | merging, Step 3 - internal representative point curvature difference (:473, :479) |

The growing parameters are only ever given in the body at :151 (n_b = 10, tau_theta = 4,
tau_kappa = 1) and are not repeated anywhere in the appendix.

**Parameters the text gives**: n_b=10, tau_theta=4, tau_kappa=1 (:151); k1=10, k2=30, rho_d=1.0,
rho_n=0.95, rho_c=0.1, rho_in,n=0.75, rho_in,c=0.25 (:467-473); "at least three boundary point pairs"
(:477); internal representative point = "the median point sorted by perpendicular distance to the
principal axis" (:479).

**Parameters/decisions the text omits** (each one is a degree of freedom we had to invent):
- the k of the "k-nearest neighbors method" that finds the close point pairs between clusters (:153) -
  rho_d bounds the distance, nothing bounds k; our code uses k1 = 10 neighbours to test boundary status
  (:1950-1959).
- the minimum cluster size. Nothing anywhere; our dynMinCluster = max(30, N/500) = 328 for P03
  (mesh_processing_headless.cpp:2122) is ours alone. It only ever deletes clusters, so it cannot
  cause this bug - but it also cannot cure it.
- how many "internal points" - :153 says plural, :479 describes exactly one representative point per
  cluster; the appendix implementation is the singular one and our code follows it (:1924-1925).
- the sampling density the thresholds were tuned on. tau_theta is a PER-STEP angle, so its meaning is
  density-dependent; our cloud is downsampled to 0.6 mm (1616373 -> 164403 points, :25-26 of the log)
  and the paper never states its spacing.
- **anything bounding how far a cluster may run into the break face.** The paper has no constraint of
  this kind: growing + merging + "take the two biggest" is the entire rule. That hole is exactly where
  we fell in, and it is a paper-faithful hole - which is why the fix here can only be a number, not a
  new criterion, if we want to stay paper-faithful.

---

### 2. Cluster table, Pot D Piece 03 (build-267 run + validated replay)

Build-267 log: artifacts/pota270/mesh267_P03.log, md5 d94d1f3abe2c142d6c1e205430645d1f (identical to
the Spartan original). Grow input: Pot_D_Piece_03_SampledWithNormals.ply, md5
ccce36946124ae47c158783ddaa6f578, n = 164403, splitter line theta=4.00000 kappa=1.00000 nb=10.

| stage | clusters / sizes | top two | share |
|---|---|---|---|
| after region growing (log:57-67) | 9 clusters: 56345, 54075, 31700, 3384, 3142, 2584, 2562, 977, 375 (sum 155144; 9259 pts unclustered, all below dynMinCluster=328) | 56345 + 54075 | 67.1642% of all points, 71.1726% of clustered (log:68-69) |
| after the Appendix-A merge (log:70-72) | **9 clusters, unchanged** - the log prints the thresholds and then only "pass 1 done: 9 clusters"; there is no "merge X into Y" line for P03 at all | **56345 + 54075, unchanged** | unchanged |
| classification (log:200-203) | face0 n=56345 interior_frac=0.0000, face1 n=54075 interior_frac=0.9656, satA=1859 satB=108561 -> "swapped" | Surface_0 = 54075 = **interior**, Surface_1 = 56345 = **exterior** | - |

**Does the lip have its own cluster? No.** Three separate facts: (a) the merge fired nothing, so no
cluster was ever absorbed; (b) the kept exterior cluster itself contains the roll-over - in the
255 mm stretch it reaches s = +5.04 mm with 828 points beyond +3 and 232 beyond +4; (c) the material
that lies beyond the roll-over is a *different, larger* cluster (log cluster 3, 31700 pts; replay id 2,
n = 35179) whose stretch points are all outboard (s p50 +5.04, p95 +6.26, max +6.98) - it was never
merged and never competed for a top-2 slot.

Replay cluster extents in the stretch band (replay id 0 == log cluster 1 == Surface_1):

| replay id | n | n in stretch | s p50 | s p95 | s p99.5 | s max | n(s>+2) | n(s>+3) | n(s>+4) | tilt med |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 (= Surface_1) | 56438 | 10884 | -2.14 | +3.38 | +4.54 | **+5.04** | 1718 | 828 | 232 | 29.1 |
| 2 (log cluster 3) | 35179 | 3384 | +5.04 | +6.26 | +6.73 | +6.98 | 3384 | 3368 | 2937 | 65.5 |
| 7 | 380 | 187 | +4.48 | +5.09 | +5.19 | +5.21 | 187 | 187 | 175 | 84.9 |

For reference, the resampled surface cloud (artifacts/pota268/Surface_1.xyz, md5
e0e4bfb0fa682b9087190869c931f58f, 111526 pts) over the whole lane: within 8 mm of the lane its s
reaches p99.5 +4.06 / max +5.04 mm; in 269's stretch window the p99.5 is +4.36 / max +5.04 - the
B-spline resample keeps the cluster's crest extent rather than trimming it.

Trap recorded: the ten files ...unclustered.plyCluster_0..9.pcd (8371 / 369 / 137 / 102 / 55 / 46 /
37 / 31 / 25 / 22 points, log:100-131) are a SECOND, unrelated EuclideanDist pass over the 9259
unclustered points. They are not the region-growing clusters and must not be read as such.

---

### 3. Per-step normal angle along the grow path across the crest (the P/R discriminator)

What the code actually compares, mesh_processing_headless.cpp:1770 - the threshold lives here:

    :1762  if (pkdtree.nearestKSearch(pcloud->points[cf], nb + 1, pnb, pdist) <= 0) continue;
    :1766  if (pnormals->points[cand].curvature >= kappaThresh) continue;
    :1770  if (pcl::getAngle3D(curN4, nn4, true) > thetaDeg) continue;      <- tau_theta
    :1776  cluster kept only if size >= minClusterSize

curN4 is the normal of the FRONTIER point cf, nn4 the candidate's. So the test is a step-to-step angle
with no memory: a region can walk an arbitrarily large total turn as long as no single step exceeds
thetaDeg. thetaDeg = paperTheta, default 4.0 (declared :2039-2040, defaults set :2559, env override
SFS_PAPER_THETA :2558-2568); the run used theta=4.00000 (:24 of the log).

Table: only points of the KEPT exterior cluster (replay id 0) that lie in the 255 mm stretch
(dA <= 8 mm, author stations 156..304), n = 16257. step_min(p) = the smallest angle between p's normal
and any of its 10 nearest neighbours - i.e. the best single step the BFS could take out of p.

| s band | n | tilt med (deg) | step_min p50 | step_min p90 | frac(step_min) <= 4.0 deg (tau) | frac <= 3.45 deg |
|---|---|---|---|---|---|---|
| [-6,-5) | 1146 | 35.7 | 0.18 | 0.40 | 100.0% | 100.0% |
| [-5,-4) | 1169 | 36.4 | 0.17 | 0.42 | 100.0% | 100.0% |
| [-4,-3) | 1188 | 36.1 | 0.24 | 0.59 | 100.0% | 100.0% |
| [-3,-2) | 1174 | 31.8 | 0.46 | 0.94 | 100.0% | 100.0% |
| [-2,-1) | 1087 | 23.4 | 0.75 | 1.81 | 100.0% | 99.0% |
| [-1,+0) | 585 | 8.9 | 1.16 | 2.94 | 99.8% | 96.9% |
| [+0,+1) | 892 | 7.2 | 0.95 | 2.05 | 99.9% | 98.9% |
| [+1,+2) | 1010 | 16.9 | 0.55 | 1.37 | 100.0% | 99.9% |
| [+2,+3) | 890 | 22.2 | 0.36 | 1.48 | 99.9% | 99.6% |
| [+3,+4) | 596 | 22.9 | 0.36 | 1.68 | 100.0% | 99.5% |
| [+4,+5) | 231 | 26.9 | 1.15 | 2.59 | 99.6% | 96.5% |

Flat face (s in [-2,0)): n = 1672, tilt med 19.8 deg, step_min p50 0.90 deg.
Past-crest lip (s >= +3): n = 828, tilt med 24.1 deg, step_min p50 **0.45** deg.

So the gate is nowhere near binding (99.6-100% of every band passes 4.0 deg) and the lip is per-step
SMOOTHER than the face. The tilt, which is what distinguishes them, changes by 17-20 deg across the
crest - a quantity the gate never looks at.

Stuck points at other thresholds, out of the 56438-point exterior cluster (the whole cluster, so these
are the points that would be orphaned if the threshold were lowered):

| tau_theta | points with no neighbour under it | share |
|---|---|---|
| 4.0 deg (the build) | 7 | 0.01% |
| 3.0 | 201 | 0.36% |
| 2.0 | 675 | 1.20% |
| 1.5 | 1230 | 2.18% |

Bottleneck (minimax step angle, union-find over the 10-NN graph restricted to the kept cluster): the
cheapest face (s <= -2) to lip path is **3.45 deg**, at one edge (the 533022nd of 564380 edges when
sorted by angle) - and it is the same 3.45 deg edge whether "lip" is taken as s >= +2, s >= +3 or
s >= +4. The crest is a single 3.45 deg step, nothing more.

---

### 4. Verdict: **(P)**

The lip joins the surface because region growing walked around the crest - the flat face and the
roll-over are ONE cluster - and the number that lets it is **tau_theta = 4.0 deg against a 3.45 deg
bottleneck step** (mesh_processing_headless.cpp:1770, default :2039-2040 / :2559).

Evidence line, quotable: *the past-crest lip is per-step smoother than the flat face (step_min p50
0.45 vs 0.90 deg) while its tilt differs by 17 deg, and the whole face-to-lip path inside the kept
cluster is bottlenecked at 3.45 deg - 0.55 deg inside the 4.0 deg gate.*

(R) is excluded by two independent facts, not one:
- merge: zero merges fired on P03 (log:71-72), so no rule was exercised there at all. Also, had one
  fired, the top two could not have changed: 56345 and 54075 are the two largest by a factor of 1.7
  over the third (31700), and the only lip-sized candidates in the stretch are 828 and 232 points.
- selection: the lip is not a cluster, so it was never in a competition. A hypothetical lip cluster
  would need to exceed 54075 points to displace anything - it has 828 in the stretch and 56438-pt
  company id 0 already carries it.

What would have made it (R): a lip cluster that the merge then absorbed, or a lip cluster large enough
to take a top-2 slot. Neither exists in this run.

---

### 5. The two guard pieces (same instrument)

Same instruments, same code paths. Surface_1.xyz is the resampled exterior surface that feeds the
boundary step; "raw cluster" is the region-growing cluster on the SampledWithNormals cloud.

| piece | lane (264/267) | raw exterior cluster: n, pts at s>+3, s max | resampled Surface_1 within 8 mm of the lane: s p99.5 / s max | tilt by band (deg) | crest bottleneck | clusters at tau=3.0 |
|---|---|---|---|---|---|---|
| P22 Bl1 | 0.57 / 95.1 | 6756 pts, **399** at s>+3, s max **+6.08** | **+0.40 / +1.09** mm | -8:7.6 -6:7.1 -4:10.4 -2:7.4 -1:4.6 0:10.9 | 3.06 deg | 16 -> 18 clusters, top-2 coverage 0.654 -> 0.459 |
| P01 Bl1 | 0.98 / 95.4 | 8943 pts, 440 at s>+3, the surface near the lane is dominated by inboard points | **+7.69 / +7.99** mm | -8:4.1 -4:1.9 -2:9.0 0:16.7 +2:4.7 +3:2.9 +4:4.0 +6:5.2 +7:6.5 | 0.08 deg | 8 -> 8 clusters, top-2 coverage 0.802 -> 0.791 |
| P03 Bl1 (the miss) | 4.1 mm out | 56438 pts, 828 at s>+3, s max +5.04 | +4.06 / +5.04 mm | -8:9.5 -4:18.2 -1:6.2 0:7.8 +2:21.0 +3:21.4 +4:22.0 | **3.45 deg** | 8 -> 9 clusters, lip gone, top-2 coverage 0.672 -> 0.643 |

Plain answer to the ticket's question: **no - crest extent alone does not explain the miss.**
- **P01 runs further past the crest than P03 does** (resampled s p99.5 +7.69 / max +7.99 mm vs
  +4.06 / +5.04) and its lane is at bar. What is different there is that the past-crest material is
  nearly coplanar with the face - tilt stays 2.9-6.5 deg from s = +2 all the way to s = +7 - so the
  surface's silhouette does not move across the crest the way P03's does (P03: 7.8 deg at the crest,
  21-22 deg at s = +2..+4, i.e. a roll-over the surface keeps).
- **P22 carries the same lip inside its cluster** (399 points beyond +3, up to +6.08 mm) - but it
  never reaches the boundary step: the resampled Surface_1 stops at max +1.09 mm. So the lip joining
  the cluster is NECESSARY for the P03 miss but not sufficient; it only bites when the lip survives
  the B-spline resample into Surface_1.xyz. On P22 it does not; on P03 it does; on P01 it survives but
  is flat and harmless.

---

### 6. Recommendation

**Lower tau_theta from 4.0 to 3.0 deg** (mesh_processing_headless.cpp:1770; the value is paperTheta,
default declared :2039-2040 and set :2559, overridable at run time with SFS_PAPER_THETA :2558-2568).
Any value below **3.45 deg** severs the lip by construction; 3.0 is the rounded choice with margin,
and it is paper-faithful in kind (one number, no new criterion).

Measured effect on P03 (validated replay, pota270_theta_P03.json):

| tau_theta | clusters | top-2 sizes | top-2 coverage | kept-cluster s max | lip pts (s>+3) still in it |
|---|---|---|---|---|---|
| 4.0 (build) | 8 | 56438 / 54081 | 0.672 | +5.04 | 828 |
| 3.5 | 9 | 55804 / 53969 | 0.668 | +5.04 | 772 (NOT enough) |
| **3.0** | 9 | 53790 / 51943 | 0.643 | **+0.24** | **0** |
| 2.5 | 11 | 53430 / 51504 | 0.638 | -0.04 | 0 |
| 2.0 | 12 | 52071 / 51229 | 0.628 | -0.04 | 0 |
| 1.5 | 13 | 50676 / 32717 | 0.507 | -0.04 | 0 (face itself starts to break) |

At 3.0 the face cluster keeps 51943 of 56438 points (92.0%) and its outboard edge lands at
s = +0.24 mm, i.e. on the author's lane, instead of +5.04 mm. That is the whole mechanism of the miss
removed at its source rather than at the boundary step.

Effect on the guards:
- **P01: no effect worth reporting** - coverage 0.802 -> 0.791, top-2 8943/7996 -> 8895/7825, band
  tilts unchanged, and its crest bottleneck (0.08 deg) is so low that its clustering is insensitive to
  any of these thresholds. Its past-crest material stays flat and stays in.
- **P22: measurable fragmentation** - 16 -> 18 clusters, top-2 coverage 0.654 -> 0.459, top-1
  6756 -> 4614, and a 696-point cluster at 36.5 deg tilt appears at negative s. Its lip (+6.08 mm in
  the cluster) is cut. Whether P22's LANE survives that is **unmeasured** - it needs a build-267+
  run, and this ticket does not build. Note also that P22's lip is trimmed by the resample anyway
  (+1.09 mm in Surface_1), so its lane has less to lose than the cluster table suggests.

What would overturn the recommendation:
1. **A run at 3.0 that costs P22 its lane (0.57 / 95.1).** Then a global tau_theta is the wrong
   instrument and the lever becomes per-piece/adaptive (e.g. tie tau_theta to the downsampling radius,
   which is the only quantity that makes a per-step angle meaningful).
2. **A run at 3.0 that moves P03's line but not to the crest** - the prediction is s = +0.24 mm, i.e.
   slightly INBOARD of the author's lane, which would flip the error sign rather than remove it. The
   replay says the kept cluster ends at +0.24 mm, but the boundary/sequencing stage is not modelled
   here, so this is a prediction, not a measurement.
3. **Evidence that the paper's tau_theta=4 was tuned at a sparser sampling than our 0.6 mm** (it does
   not state its spacing). A per-step gate on a denser cloud is automatically more permissive, so
   part of our 4.0 deg is not the paper's 4.0 deg. If so, the principled fix is to re-tune tau_theta
   with the sampling radius, not to keep the paper's number at a density it was never tested on.

Ruled out, with numbers, so it does not get re-opened: a **seed-referenced** variant (compare the
candidate against the region's seed normal instead of the frontier normal) is not a clean lever here -
the per-station mutual normal angle from the crest band to the lip band is only 50.7 deg median
(p90 56.0) while the crest band to the INBOARD face band is already 24.4 deg median (p90 46.1), so any
threshold low enough to cut the lip (about 40 deg) also cuts the face (pota270_drift.json).

---

### 7. What is on disk, and every input md5

Scripts (untracked, C:/PR/SfSpp_preprocessing-248):
- pota270_common.py - PLY reader + the 269 frame (reuses artifacts/pota269/pota269_common.py)
- pota270_replay.py - faithful port of growPaper234, validated against the binary's own size lists
- pota270_crest.py - per-s-band profile, per-cluster s extents, stuck-point counts
- pota270_tilt269.py - 269's tilt table reproduced exactly (fidelity gate) + the same table per guard
- pota270_theta.py - bottleneck (union-find minimax) + tau_theta sweep
- pota270_step.py - the item-3 table
- pota270_drift.py - per-station mutual normal angles (the ruled-out seed-referenced variant)
- pota270_fig.py - the figure

JSON / data: artifacts/pota270/pota270_replay_P{03,22,01}.json, pota270_lab_P{03,22,01}.npy,
pota270_crest_P03.json, pota270_tilt269.json, pota270_theta_P03.json, pota270_theta_guards.json,
pota270_step_P03.json, pota270_drift.json, pota270_fig.json.

Figure: **artifacts/pota270/pota270_P03_lip_crosssection.png** - cross-section at author station 237
of the stretch (the failing stretch), points coloured by region-growing cluster id, author dot black
at s = 0, our current edge line (artifacts/pota268/bag_boundaryImproved.pcd) red at s = +5.3 mm. The
blue cluster (0 = Surface_1) runs unbroken from the face across the crest to s = +5.0 mm; the lip has
no colour of its own.

Inputs read, md5 (local == Spartan for every one that also exists on Spartan):

| input | md5 |
|---|---|
| artifacts/pota270/mesh267_P03.log | d94d1f3abe2c142d6c1e205430645d1f |
| artifacts/pota270/mesh267_P22.log | 617750824943f39c9ba5b9c43ffd24cb |
| artifacts/pota270/mesh267_P01.log | ce82b6a2bab0ea0000bbbb2cdcfb89e7 |
| artifacts/pota270/P03_SampledWithNormals.ply | ccce36946124ae47c158783ddaa6f578 |
| artifacts/pota270/P22_SampledWithNormals.ply | 30691281f6cf892fbf623f3f5e3ba4c7 |
| artifacts/pota270/P01_SampledWithNormals.ply | cd9db0ad176262ef64f4c3182b013ad9 |
| artifacts/pota268/Surface_1.xyz (P03 exterior) | e0e4bfb0fa682b9087190869c931f58f |
| artifacts/pota268/Surface_0.xyz (P03 interior) | 56d8fb75158caa1aa36306b320af8467 |
| artifacts/pota270/P22_Surface_1.xyz | 9dfe440e0b73738e3df3da89eaaefbaa |
| artifacts/pota270/P01_Surface_1.xyz | 481c69fb3e6e04b28ff15481d4d105f9 |
| artifacts/pota268/author_P03_Bl1.pcd (= sfs_main original Pot_D_Piece_03_Breakline_1.pcd) | bbb490fc5b7b583445eb0809bc2b6c3c |
| artifacts/author_PP22_Bl1.pcd (= original Pot_D_Piece_22_Breakline_1.pcd) | 9d07f77c66c7644faa10530547fa0dee |
| artifacts/author_PP01_Bl1.pcd (= original Pot_D_Piece_01_Breakline_1.pcd) | 1e391ae988a000e7810d2f5dff73f1a9 |
| artifacts/pota268/bag_boundaryImproved.pcd (our current line) | b79c25b051fadba82e1772a50754584b |
| artifacts/pota268/export_P03_Bl1.pcd | ddaeb48e5daecceeeffc86baf1177f27 |
| artifacts/pota268/pota268_keys.json (stretch keys) | 71a4c0d9c436e32f3506ef9922c4e0fd |
| mesh_processing_headless.cpp (read only) | c11a1ac6089c24b8ccdf77c1faf12c9d |

Code lines cited are from that md5. No file outside artifacts/pota270/, pota270_*.py and this ticket
was written.



---

## Lead verdict (270) — 2026-10-23

**ACCEPTED: (P), parameter — with the recommended number replaced by a window.**

Verified by the lead, not taken on report:
- `mesh_processing_headless.cpp:1770` `if (pcl::getAngle3D(curN4, nn4, true) > thetaDeg) continue;` — the gate compares the candidate against the **frontier** point's normal, never the seed; a 25 deg fold crossed in 0.5-1.2 deg steps is invisible to it. `paperTheta = 4.0` default at :2040, env `SFS_PAPER_THETA` at :2561.
- `mesh_processing_headless.cpp:1766` `if (pnormals->points[cand].curvature >= kappaThresh) continue;` with `paperKappa = 1.0` (:2040, `SFS_PAPER_KAPPA` :2562). PCL surface variation is lambda0/(lambda0+lambda1+lambda2) and cannot exceed 1/3, so **the paper's curvature gate has been inert in every run we have ever scored** — the same defect class as the align veto 269 found. Under investigation as of this verdict.
- Ticket figure reviewed: cluster 0 (blue) runs unbroken from the face, over the crest, to s = +5.0 mm; cluster 2 (green) takes over down the flank. The lip is not a cluster, so (R) could not have happened.

What stands from the ticket: (R) excluded twice (zero merges fired on P03; top two 56345 + 54075 identical before and after; a lip-sized candidate is 828 pts against a 54075 threshold). Crest extent is **necessary but not sufficient** — P01 runs further past the crest (+7.99 mm) and scores at bar because its past-crest material is coplanar, and P22's lip never survives the B-spline resample into `Surface_1.xyz` (max +1.09 mm). Do not generalise this mechanism to the Pot H or P07/P12 families without that test.

**The number is not 3.0 yet.** The ticket's own measurements put P03's lip bottleneck at 3.45 deg and P22's at 3.06 deg, so a global tau in **(3.06, 3.45)** severs P03's lip while leaving P22's growth intact; 3.0 sits *below* P22's bottleneck, which is exactly why the ticket measured P22 fragmenting (coverage 0.654 -> 0.459). The recommendation must first sweep the window it already brackets, with a pre-registered rule, before any build.

Two consequences recorded for whoever cuts the next ticket:
1. **Any global change to tau_theta invalidates the 214-lane rollout scores** collected at tau = 4 (tickets 250-259). Budget the re-rollout with the fix, or find a lever that is inactive when the lip is coplanar (P01) by construction.
2. The replay is a prediction, not a result: it models growing and merging, not the B-spline resample or the boundary step, and its cluster sizes differ from the binary by 0.02-0.5% (P03 56438/54081 vs 56345/54075). Only a build + run decides whether the line lands on the crest.

No C++ change, no build, no job. Ticket only.

