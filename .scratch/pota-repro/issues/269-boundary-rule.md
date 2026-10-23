# 269 — The boundary line sits 4 mm up the roll-over: what does the paper say it should be?

Answers: E1
Status: results-in
Working in: C:/PR/SfSpp_preprocessing-248 (scripts + one cluster job at most; NO main commits)
Needs-eye: no

## Why

Ticket 268 settled where P03-Bl1's 4 mm is made: in the boundary/edge step, before sequencing, before the walk, before the filter. The evidence: the first breakline artifact (_breakLineFromConcaveHull.pcd, = cloud_sequenced, written at edgeline_extraction_headless.cpp:1604-1605) already carries 4.119 mm over the stretch; the bag holds no dot within 2 mm of the author's lane there (min 1.394, med 4.140); and our reconstructed surface passes 0.233 mm median from that same lane with 100% inside 1 mm. Our geometry covers the line; our boundary set refuses to use it. 88.4% of the bag dots on the stretch have further material beyond them within 3 mm — a boundary dot with material outside it is not on a boundary.

The mechanism is a roll-over: the author's line sits at the crease where the face is flattest (local tilt about 7 deg), and our dots sit 4.1 mm out where the face has tilted 43-45 deg. The rim turns 90 deg of orientation in about 5 mm.

This is the third substitute found standing in for the author's method (the K-D filter in 248/264, the "B-spline" that is a sphere-marcher, and now the boundary rule). Read the spec before tuning the substitute.

## Goal

Three phases, in order. Each phase gates the next.

### Phase 0 — what does the paper actually say the boundary is?

Find the paper text in C:/PR/papers (the file used before is the SfS++ paper, sfspp-2502.13986v1, method section around line 164). Quote VERBATIM, with file path and line numbers, every sentence that describes how the boundary / breakline points are obtained before the ordering step: the criterion, any threshold, any radius, any smoothing, any input (mesh, point cloud, which surface). Then state in one short paragraph what rule the authors prescribe, and mark with "to verify" anything the text leaves open.

If the paper does not specify the rule in enough detail to implement, say so plainly and quote what it does say. That is a finding, not a failure.

### Phase 1 — replicate our detector in Python, find which part puts it at +4 mm

Our step is PCL BoundaryEstimation (edgeline_extraction_headless.cpp:1330) plus FACE_ALIGN_VETO (declared :1365, tested :1387) plus a K=1 snap (about :1525-1535). Read those lines and state exactly what each does, including what "align" is measured against and what the veto removes.

Then reimplement the detector in Python over the SAME inputs (the extracted surface / the unclustered cloud that the C++ step reads for P03-Bl1) and GATE on replication: your replica must reproduce the C++ boundary set — same dot count, positions within tolerance, and the same 4.1 mm offset profile on the stretch. If your replica does not reproduce it, the replica is wrong; say so and stop, do not sweep variants against a model that does not match the code.

Then sweep the parts, one at a time, reporting the offset profile (the same instrument 268 used: signed in-sheet cross-lane offset s, per 21-dot station, against the author's lane):

- BoundaryEstimation radius and angle threshold;
- with the veto on and off, and the veto threshold swept;
- K=1 snap on and off;
- the paper's rule from Phase 0, implemented as written.

The question each variant answers: does the boundary set move to the crease (where the face tilt is minimal), and does anything else break. Report the variant that lands the line on the crease with the least change to the existing code, or report that none does.

### Phase 2 — is this the Pot H parallel-ridge family?

Cheap check, no rebuild: take the four Pot H Bl1 misses from ticket 257 (C:/PR/SfSpp_preprocessing/.scratch/pota-repro/issues/257-*.md — read its Comments for the lane ids and tree paths) and run 268's offset instrument on them. Report, per lane, whether the exported line sits systematically to one side of the author's lane at a few millimetres, with the same roll-over signature.

If the Pot H trees or author lanes are not retained, say so and stop this phase — 269's core is Phases 0 and 1.

## Boundary

- Worktree C:/PR/SfSpp_preprocessing-248: new untracked pota269_*.py scripts, plus one job on a compute node if the replication genuinely needs the cluster inputs. Nothing committed anywhere.
- Do NOT change C++ in this ticket. Phase 1 ends with a recommendation; the code change is a separate ticket.
- Do not reopen the walk, the stop rule, the guided filter, or the strand question. Their verdicts stand.

## Constraints

- Paper quotes must be verbatim with path and line numbers. No paraphrase passed off as quotation.
- Heavy Python goes to a compute node, never the laptop for anything long, never the login node.
- Every number cites its input file.
- If the paper's rule and our rule agree, say so — that would move the fault into the parameters or the input cloud rather than the rule, and that is a different next ticket.

## Acceptance criteria

1. Paper quotes (verbatim, path:line) and one-paragraph statement of the prescribed rule, with "to verify" flags where the text is thin.
2. Line-by-line statement of what BoundaryEstimation, FACE_ALIGN_VETO and the K=1 snap each do in our code.
3. Replication gate result: replica matches or does not, with the numbers.
4. Variant table: offset profile per variant, the effect on the crease, and the recommended minimal change — or an explicit "none of them lands on the crease".
5. Pot H cross-check table, or a clear statement that it could not be run and why.
6. One PNG: the crease region with the author's line black, the current boundary set, and the best variant — so the lead can see whether the line moved to the foot of the slope.

## Required evidence to report

Ticket Comments with all six, each number citing its file, and one line naming what would overturn the recommendation. No accept/reject verdict — judgement is the lead's.


## Comments (worker, 2026-10-23)

**Bottom line.** None of our three parts, at any setting, puts the line at the crease. Over
BoundaryEstimation radius 1.5-8 mm, angle 60-170 deg, veto threshold 0.99-0.60, snap on/off and the
paper's rule as written (PCL's default 90 deg), the boundary set is always the same curve at signed
in-sheet cross-lane offset **s = +3.3 to +3.9 mm** outboard of the author's lane, never once closer
than **+2.03 mm** (artifacts/pota269/sweep.log, all rows). That curve is the silhouette of
Surface_1 itself: PCL BoundaryEstimation on Surface_1 alone reproduces the C++ bag to 0.000 mm
median (artifacts/pota269/pota269_mech.json), and Surface_1's own material ends **p99.5 = +4.36,
max = +5.04 mm** outboard of the author's lane (pota269_mech.json, sheet extent). Cutting the sheet
at the crease and rerunning the unchanged detector lands the line at **s med +0.24 mm, author
coverage 0.34 mm median, 100% within 2 mm** (pota269_mech.json, "sheet cut s<=+0.5"). So the fault
is the extent of the input cloud, not the rule; and of our three parts the snap contributes +0.40 mm
of the 4.1 and the veto contributes exactly nothing.

Heavy Python note: no compute-node job was needed. The largest run (SOR + BoundaryEstimation over
111 526 points) takes 26.3 s on the laptop; every sweep row reuses one cached radius search. The
ticket's inputs were already local under artifacts/pota268.

---
### 1. The paper, verbatim (C:/PR/papers/text/sfspp-2502.13986v1.md)

The complete set of sentences that describe how boundary/breakline points are obtained before the
ordering step:

- **:139** "Notations. We first define $P^{\mathrm{sample}}$ as the point cloud data uniformly sampled from the mesh representation. A point $\mathbf{p_{s}}\in P^{\mathrm{sample}}$ represents a point on the surface of a sherd in 3D space and the surface normal vector at that point is defined as $\hat{\mathbf{n}}_{s}$. For each of the surfaces, we extract an ordered line of points around its boundary, referred to as the edge line. The $i$-th point on the edge line of sherd $A$ is then defined as $\mathbf{q}^{A}_{i}=\left(\mathbf{p}^{A}_{i},\hat{\mathbf{n}}^{A}_{i}\right)\in\mathbb{R}^{6}$, where $\mathbf{p}^{A}_{i}\in\mathbb{R}^{3}$ represents the position of the point, and $\hat{\mathbf{n}}^{A}_{i}\in\mathbb{R}^{3}$ represents its normal vector."
- **:145** "The FE module extracts axis-based edge line descriptors for the initial pairwise matching candidates from the input object mesh. Inspired by SfM, which extracts image features to support matching and optimization, this module separates surfaces into interior and exterior regions, estimates edge lines from the interior surface, and extracts axis-based edge line descriptors using parameters such as height, radius, angle, and thickness relative to the axis of symmetry."
- **:149** "Firstly, we sample the point cloud data $\mathcal{S}$ from the mesh representation. Next, we segment the surfaces into inner and outer regions. From the inner surface, we compute the axis of symmetry and extract the edge line, which provides a concise representation of the sherd. Finally, we compute the geometric features required for further analysis. Compared to the previous work [9], we introduce cluster merging to ensure robust surface segmentation."
- **:155** "Subsequently, B-Spline fitting is performed for each cluster to refine surface boundaries and uniformly sample the point cloud. Finally, we select the two largest clusters, representing the inner and outer surfaces." (sentence only; the rest of :155 is about decorative parts)
- **:164** "Edge line extraction and segmentation. The interior surface point cloud boundary makes up the edge line extracted using the point cloud boundary-estimation method from the PCL library [30]. The extracted edge line is refined through B-spline surface fitting, which smooths the edge line and calculates normals for each point. Using a K-D tree-based search, points near the edge line are identified and filtered to remove noise and outliers. The filtered points are resampled to generate equidistant points with a point-to-point distance of $d$ = 1.9mm, an empirically optimized value. The resulting edge line points are reordered counter-clockwise using their normals and a voting algorithm, as visualized in Fig. 6. Finally, we segment the edge line based on corners detected by analyzing peaks in the distribution of distance scores, which measure the deviation of each point from its local linear trend."
- **:177** (rim detection, applied to edge lines *after* ordering, quoted only to show what is *not* the boundary rule) "First, we evaluate the consistency of height and radius, seeking sections with minimal variation, specifically where the standard deviation of both height and radius is 1.0 mm or less. Second, rim sections must exhibit gradual changes, defined as an average variation of 0.1 mm or less in both height and radius between adjacent points. Last, to minimize false positives in short edge segments, we only consider sections composed of at least 20 points that meet the previous criteria."

Traps checked: the parameter table at **:465-473** ($k_1$=10 "Neighbors for boundary evaluation", $\rho_d$=1.0 "Distance threshold for boundary pairs", ...) is captioned at **:464** "**TABLE I: Parameters used in cluster merging algorithm.**" and belongs to Appendix A cluster merging (:462 onwards). It must not be read as the boundary estimator's parameters.

**Prescribed rule, one paragraph.** The edge line is the *boundary of the interior surface point
cloud*, extracted with PCL's point cloud boundary-estimation method; it is then refined by B-spline
surface fitting (smoothing plus per-point normals), points near it are identified and filtered with a
K-D-tree search "to remove noise and outliers", and the survivors are resampled to an equidistant
1.9 mm pitch; only then are they ordered CCW by a normal vote and split at corners. The input is a
point cloud sampled from the mesh, restricted to the interior surface — i.e. the boundary is taken
*of the segment*, not of the mesh and not of the whole capture.
**To verify:** the text gives no search radius, no angle threshold, no neighbour count for the
boundary estimator (PCL's BoundaryEstimation cannot run without a user radius, and the authors do
not report it; PCL's own default angle threshold is pi/2); no radius and no k for the K-D-tree
filter; and nothing about how far the interior-surface cluster is allowed to run into the break
face. The paper therefore prescribes the METHOD and the INPUT, not the parameters — it is not
implementable to the digit from the text alone. That is the finding, not a failure.

**Does the paper's rule agree with ours?** At the level the paper states it, yes: same method (PCL
boundary estimation), same input type (the extracted surface cloud), same downstream order
(smooth, filter, resample). Implemented "as written" with PCL's 90 deg default at r = 2/4/6 mm it
returns the *same* curve as our 108 deg build, s med +3.75/+3.77/+3.75 mm (artifacts/pota269/sweep.log
rows "E. paper-as-written"). The divergence from the author's lane is therefore not in the rule and
not in its stated thresholds — it is in the extent of the surface cloud the rule is applied to
(item 4), which the paper also leaves open.

---
### 2. What our three parts do, line by line (C:/PR/SfSpp_preprocessing-248/edgeline_extraction_headless.cpp)

- **BoundaryEstimation, :1330-1353.** :1303 declares getInitialBoundary_UsingPCL_BoundaryAlgo; :1305-1326 split the PointNormal cloud into positions and normals; :1330 constructs pcl::BoundaryEstimation<pcl::PointXYZ, pcl::Normal, pcl::Boundary>; :1331 setInputCloud(cloudWithoutNormals); :1332 setInputNormals(normals); :1348 setRadiusSearch(4) — 4 mm, inside an #else so -DPOTA218_ARM_B replaces it with an adaptive 3x-spacing radius clamped to 1.5-8 mm; :1351 setAngleThreshold(M_PI * 0.6) — 108 deg; :1352 KdTree search; :1353 compute(boundary). PCL's algorithm (verified against pcl-1.10.1 boundary.hpp): neighbours = radiusSearch(p, r) including p itself; fewer than 3 neighbours -> not a boundary; each neighbour's direction in the tangent plane is quantised as atan2(v.delta, u.delta) for an arbitrary orthonormal (u,v) built from the query normal; the angles are sorted and the largest gap, including the wraparound 2*pi - last + first, is compared with the threshold (strict >). It is a *hole/edge* test on the neighbourhood, nothing else.
- **FACE_ALIGN_VETO, :1365 and :1387.** :1365 declares "const float FACE_ALIGN_VETO = 2.0f"; :1366-1368 compute surfCentroid as the mean of the whole cloud; :1383 forms rp = p_i - surfCentroid; :1387 rejects the point "if (align <= FACE_ALIGN_VETO)" where align = n_i . rp/|rp|. Because n_i and rp/|rp| are both unit vectors, align is in [-1,+1] and a threshold of 2.0 admits every point: **the veto is inert on this build**, exactly as the comment at :1358-1364 says it is intended to be ("the principled Pot-A gate keeps the whole bag (align in [-1,1] always passes)"). Measured on the real input: align range +0.5628 .. +0.9997, kept 1121, dropped 0 (pota269_repl.py output; C++ log artifacts/pota268/edge267_FULL.log:909 says the same). The neighbour-field arms that would make it bite (ARM A / ARM C, :1389-1470) are not compiled in the control build.
- **K=1 snap, :1508-1539.** :1508-1518 loads the sparse retained cloud "<piece>_unclustered.ply" and builds a pcl::KdTreeFLANN; :1522 "int K = 1;"; :1525-1535 for every boundary dot takes nearestKSearch with K=1 and pushes the *unclustered* point instead (:1532). Each boundary dot is therefore replaced by the nearest retained-cloud dot — a many-to-one map onto a cloud 20x sparser (9259 pts vs 111 526). Measured displacement: mean 0.303 mm, median 0.000, max 4.218 mm (pota269_repl.py). It moves the line *outward*, not inward: s median +3.32 -> +3.72 mm (sweep.log rows A3 vs A).
- Provenance, for completeness: the cloud the detector sees is written at :2761 by cleanSamples() (:2699) from the 6-column surface .xyz, after StatisticalOutlierRemoval(:2754-2758) with setMeanK(50)/setStddevMulThresh(9); it is loaded at :2557 and passed at :2558. For P03-Bl1 that file is the Surface_1 pass (artifacts/pota268/edge267_FULL.log:903-925).

---
### 3. Replication gate: PASSED, exactly

Script: pota269_repl.py (with pota269_common.py). Inputs: artifacts/pota268/Surface_1.xyz (111 564
x 6), unclustered.ply (9259 declared), bag_boundaryImproved.pcd (1121). Output:

| step | replica | C++ / ground truth | verdict |
|---|---|---|---|
| StatisticalOutlierRemoval(50, 9) | kept 111 526 (mean 1.011240, std 0.114122, thr 2.038334) | edge267_FULL.log:904 "after SOR pts=111526" | match |
| BoundaryEstimation r=4, a=108 | 1121 flags | edge267_FULL.log:909/910 kept=1121 | match |
| FACE_ALIGN_VETO thr 2.0 | kept 1121, dropped 0 (align +0.5628..+0.9997) | edge267_FULL.log:909 "kept=1121 dropped=0" | match |
| K=1 snap | 1121 dots | boundaryImproved.pcd 1121 dots | match |
| replica vs bag_boundaryImproved.pcd | 923 unique positions, every one coincides; replica->bag med 0.0000 max 0.0000 mm; bag->replica med 0.0000 max 0.0000 mm |  | **exact** |

The replica reproduces the C++ boundary set to the last coordinate, including the 4.1 mm offset
profile on the stretch (row A2 of sweep.log is identical to row A = the C++ bag in every field).
1121 dots collapse to 923 unique positions because the K=1 snap is many-to-one. The gate is met, so
the sweep is admissible.

---
### 4. Variant sweep and the recommended change

Instrument (same as ticket 268, artifacts/pota268/pota268_keys.json stretch = author dots 157-304):
for each variant dot, nearest author dot jA, s = (p - A[jA]).S[jA], along/off on T[jA]/Nn[jA];
coverage = author 157..304 -> nearest variant dot; tilt = angle between the sheet's supplied normal
and Nn at that author dot. 7 stations of 21 author dots. Rows: artifacts/pota269/sweep.log, cached
in artifacts/pota269/pota269_sweep.json.

| variant | n | nS | s med | s min | s max | author cov med | <2mm | stations 157-304 |
|---|---|---|---|---|---|---|---|---|
| C++ bag (reference) | 1121 | 482 | +3.72 | +2.03 | +5.28 | 4.14 | 0.7% | +2.70 +2.86 +3.76 +4.81 +4.86 +4.40 +3.03 |
| replica r4/a108 (gate) | 1121 | 482 | +3.72 | +2.03 | +5.28 | 4.14 | 0.7% | identical to row 1 |
| snap OFF | 1121 | 483 | +3.32 | +1.44 | +5.04 | 3.46 | 4.1% | +2.55 +2.47 +3.41 +4.39 +4.51 +3.88 +2.48 |
| r=1.5 / 2 / 3 / 5 / 6 / 8 mm, a=108 | 1134-1121 | 482-486 | +3.72 | +2.03 | +5.28 | 4.14 | 0.7% | identical to row 1 at every radius |
| a=60 deg (r=4) | 1894 | 760 | +3.80 | +2.03 | +5.28 | 4.14 | 0.7% | +2.69 +2.86 +3.77 +4.80 +4.85 +4.40 +3.03 |
| a=75 deg | 1543 | 645 | +3.85 | +2.03 | +5.28 | 4.14 | 0.7% | +2.68 +2.86 +3.76 +4.81 +4.86 +4.40 +3.03 |
| a=90 deg | 1309 | 553 | +3.75 | +2.03 | +5.28 | 4.14 | 0.7% | +2.69 +2.87 +3.75 +4.81 +4.86 +4.40 +3.03 |
| a=120 deg | 1009 | 442 | +3.72 | +2.03 | +5.28 | 4.14 | 0.7% | +2.70 +2.87 +3.76 +4.82 +4.86 +4.41 +3.02 |
| a=135 deg | 843 | 380 | +3.69 | +2.03 | +5.28 | 4.14 | 0.0% | +2.78 +2.87 +3.78 +4.82 +4.88 +4.40 +3.03 |
| a=150 deg | 663 | 299 | +3.65 | +2.03 | +5.28 | 4.16 | 0.0% | +2.90 +2.89 +3.76 +4.84 +4.87 +4.40 +3.02 |
| a=170 deg | 314 | 138 | +3.87 | +2.03 | +5.28 | 4.54 | 0.0% | +2.90 +2.92 +3.87 +4.84 +4.91 +4.40 +2.94 |
| veto 0.99 | 1057 | 456 | +3.66 | +2.03 | +5.28 | 4.14 | 0.7% | +2.70 +2.86 +3.76 +4.84 +4.86 +4.40 +3.03 |
| veto 0.95 | 775 | 337 | +3.29 | +2.03 | +5.05 | 4.22 | 0.7% | +2.70 +2.86 +3.71 +4.82 +4.80 +4.40 +3.03 |
| veto 0.90 | 423 | 141 | +2.90 | +2.25 | +4.73 | 4.97 | 0.7% | +2.84 +2.99 +3.62 - - +3.87 +2.81 |
| veto 0.80 | 103 | 16 | +2.53 | +2.53 | +2.90 | 50.87 | 0.0% | +2.53 - - - - - - |
| veto 0.70 / 0.60 | 15 / 3 | 0 | - | - | - | 79.6 / 100.6 | 0.0% | - |
| paper as written, a=90 r=2 | 1314 | 555 | +3.77 | +2.03 | +5.28 | 4.14 | 0.7% | +2.69 +2.87 +3.75 +4.81 +4.86 +4.40 +3.03 |
| paper as written, a=90 r=4 | 1309 | 553 | +3.75 | +2.03 | +5.28 | 4.14 | 0.7% | identical to row above |
| paper as written, a=90 r=6 | 1309 | 553 | +3.75 | +2.03 | +5.28 | 4.14 | 0.7% | identical |
| paper's interior = Surface_0 pass | 713 | 0 | - | - | - | 51.94 | 0.0% | - |

**Readings.**

1. **Radius does nothing.** 1.5 to 8 mm all return the same curve (station medians identical to
   0.01 mm). The detector is not mis-tuned in radius; it is reporting the true outer edge of the
   cloud it is handed.
2. **Angle threshold only changes how many dots, never where the curve is.** a=60 gives 1894 dots,
   a=170 gives 314, and the *minimum* |s| is +2.03 in every one of them. Even the most permissive
   test cannot put a dot inside 2.03 mm of the author's lane, because no such dot exists in the
   cloud on the stretch.
3. **The veto can only delete dots, and deleting rim dots does not move the line inboard** — the
   survivors are still the rim (veto 0.90: s med +2.90 but only 141 dots on the stretch and two
   empty stations, coverage 4.97 mm, i.e. broken). Below 0.80 the set collapses (103, 15, 3 dots).
   At its compiled value 2.0 it removes nothing.
4. **The snap costs +0.40 mm outboard** (3.32 -> 3.72), the single largest identifiable contribution
   of our three parts — but only 0.40 of 4.1.
5. **The paper's rule as written reproduces our error** (rows E): +3.75 mm, same stations. It is not
   the rule.
6. **Surface_0 is not this lane's surface** (row F: 713 dots, 51.94 mm median from the Bl1 author
   lane) — the P03-Bl1 author lane is the boundary of Surface_1 (author->Surface_1 med 0.233 mm,
   100% <1 mm, ticket 268). Naming either pass "interior" changes nothing.

**Why no parameter can work (mechanism, artifacts/pota269/pota269_mech.json).**

- BoundaryEstimation on Surface_1 alone (r=4, a=108, supplied normals, no snap) = 1121 dots with
  s med +3.29 (min +1.44, max +5.04), matching the C++ bag to 0.000 mm median. **The bag is the
  sheet's own silhouette.**
- Surface_1's extent near the stretch (19 194 points within 8 mm of the lane): s p50 -2.67,
  p95 +2.80, p98 +3.66, **p99.5 +4.36, max +5.04 mm**. The sheet *ends* 4.4-5.0 mm outboard of the
  author's lane. There is nothing for a boundary detector to find inboard of that.
- Face tilt by s band (supplied normals vs the author's frame normal): s[-6,-5) 35.6, [-4,-3) 36.3,
  [-2,-1) 24.4, **[-1,0) 8.7, [0,+1) 6.4**, [+1,+2) 16.5, [+2,+3) 21.0, [+3,+4) 21.4, [+4,+5) 22.0
  deg. The author's lane sits on a ~2 mm flat crest and the face rolls away on both sides — this
  reproduces ticket 268's instrument 8 (~7 deg at the lane) with supplied normals and is directly
  comparable with the Pot H table below.
- Tilt actually at our line: the C++ bag's 482 stretch dots have median face tilt **22.2 deg**
  (p10 15.7, p90 32.5), **0.0% below 10 deg, 94.6% above 15 deg** (pota269_bagtilt.py output). Not
  one dot of our line is on the flat part of the face. That is the whole of the 4.1 mm.
- **Positive control** (mechanism demo, deliberately supervised): cut Surface_1 where s > +0.5 mm
  inside a 12 mm band around the lane, rerun SOR(50,9) + BoundaryEstimation(4, 108) unchanged ->
  1400 dots, **s med +0.24 (min -0.44, max +0.50), author coverage 0.34 mm median, 100% <2 mm**,
  stations +0.27 +0.24 +0.26 +0.26 +0.27 +0.21 +0.18 -0.07. Cut at s <= 0.0: s med -0.27, same
  0.34 mm coverage. The detector finds the author's lane exactly when the cloud ends there.

**Recommendation (least change that lands on the crease).** No variant of the detector does; the
only thing that does is changing where the *input cloud* ends. Concretely, the smallest change that
lands the line on the crease is to trim the surface cloud at the crease before BoundaryEstimation —
one normal-deviation gate in cleanSamples() (edgeline_extraction_headless.cpp:2699-2761), keeping
the points whose face normal stays within ~10-15 deg of the local flat-face normal and dropping the
rolled strip (tilt >= 16.5 deg by s = +1 mm, 21 deg by +2 mm; pota269_mech.json). That is a C++
change and therefore a separate ticket, per this ticket's boundary. Second option, more faithful to
what the crease is: replace the *criterion* (hole/edge) with a crease/ridge criterion on the normal
field — the crease is where the face tilt is minimal (6-9 deg) between two rolling flanks
(16-36 deg), which is a curvature feature and not a cloud boundary at all. Both are the same class
of change: the boundary rule is not broken, it is answering a different question than the author's
line asks. The paper cannot arbitrate this, because the paper never says how far the interior surface
runs into the break face.

**What would overturn the recommendation:** a boundary detector run on a cloud that ends at the
crease and still landing 4 mm out (it does not — the control above), or an author lane that is *not*
the crest of this roll-over (it is: 6.4-8.7 deg tilt at s = 0 vs 21 deg at our line), or a
Surface_1 pass that in fact stops at the crease on the production inputs (it does not: max +5.04 mm).

---
### 5. Pot H cross-check (ticket 257's four Bl1 misses)

Trees and author lanes are retained on Spartan, so this ran: /data/gpfs/projects/punim2657/pota257_paper_Pot_H_NN/Dataset/Breaklines/Pot_H/Pot_H_Piece_NN_Breakline_1.pcd (fresh lanes),
/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_H_Piece_NN_Breakline_1.pcd
(author lanes), .../Temp/Data/Pot_H/Pot_H_Piece_NN_Surface_1.xyz (surfaces). Twelve files (2.0 MB)
pulled to artifacts/pota269/pota269_poth/; script pota269_poth.py, results
artifacts/pota269/pota269_poth.json. md5 fresh P01 7c49c0aeb14a6a888856168b7eadc478, P02
65c661627ab5d5b9e0aa7861e318eee9, P03 6b4a917228064b7d9bbef762752842d5, P10
c489368ea3497cbe88f2683d7c04f45b; author P01 89a999b236e70af2df20ea52975da92f, P02
56f422f6159426e770e4f7bdcb760a06, P03 ff245dd8324b43ba44038655c655feeb, P10
c787c64a0a2d310609108c9bb94f9fa9.

| piece | n author/fresh | fresh->author med / <2mm | s med (min, max) mm | per-station s (8 bins over the loop) | sheet s-extent p99.5 / max | tilt at s=0 | tilt at fresh-s |
|---|---|---|---|---|---|---|---|
| P01 Bl1 | 235 / 242 | 0.62 / 64.0% | +0.20 (-0.75, +6.93) | +4.51 +5.59 +5.85 +0.22 +0.06 -0.07 +0.01 -0.01 +0.32 | +5.88 / +6.92 | 6.8 | 28.6 deg |
| P02 Bl1 | 137 / 147 | 0.89 / 70.1% | -0.08 (-6.41, +1.40) | +0.03 -0.20 -5.56 -5.28 -0.32 +0.03 +0.12 +0.20 +0.02 | +8.46 / +8.96 | 5.4 | 30.2 deg |
| P03 Bl1 | 99 / 122 | 0.73 / 54.9% | -0.08 (-6.64, +5.48) | +0.12 -0.07 -0.08 +0.10 +0.06 +0.27 -5.10 -4.94 -4.45 | +8.40 / +8.86 | 6.0 | 21.4 deg |
| P10 Bl1 | 88 / 101 | 0.70 / 68.3% | -0.08 (-6.96, +5.96) | +0.03 -0.13 +0.08 -1.26 -5.04 -0.11 +0.18 -0.02 | +7.81 / +8.54 | 7.5 | 10.2 deg |

**Verdict: not the Pot D signature.** On every one of the four lanes the fresh line sits *on* the
author's lane (|s| <= 0.3 mm) for 6 of the 8 stations and jumps to |s| = 4.5-5.9 mm on **one
contiguous 2-3 station span** (a fifth to a third of the loop — consistent with 257's rev 66.8-77.3%).
The sign varies: P01 goes outboard (+5.9), P02/P03/P10 go inboard (-5.6, -5.1, -5.0). So Pot H is a
local excursion with either sign, not the uniform parallel +4 mm offset that P03-Bl1 in Pot D shows
over its whole stretch. What Pot H *does* share is the geometry underneath: the sheet is flat at the
author's lane (5.4-7.5 deg at s = 0) and rolls to 27-39 deg by s = +2..+4 mm, and the sheet extends
5.9-8.5 mm outboard. The Pot D rule finding therefore does not close the Pot H misses; those need
their own ticket (suspicion, to verify there: each excursion starts where the bag has a gap or a
second component, i.e. a local cloud defect rather than a global rule error).

---
### 6. Figure

artifacts/pota269/pota269_crease.png (rendered by pota269_png.py). Left: the crease cross-section
over author dots 222-266, sheet points coloured by face tilt, the author's dot black at (s=0,
offset 0), the current C++ boundary set red, and the crease-cut control green. Right: the same three
sets unwrapped as signed s against author dot index over the whole stretch 157-304 (the Surface_1
sheet in pale blue behind). Red runs +2.5 to +5 mm out; green sits within +-0.5 mm of the black
line; the black line is where the sheet is flat.

Files written (all untracked, nothing committed): pota269_common.py, pota269_repl.py,
pota269_sweep.py, pota269_mech.py, pota269_poth.py, pota269_bagtilt.py, pota269_chk.py,
pota269_png.py, plus artifacts/pota269/{sweep.log, pota269_sweep.json, pota269_mech.json,
pota269_poth.json, pota269_crease.png, pota269_bnd_flags.npy, pota269_keep.npy,
pota269_ctrl_cut05.npy, pota269_poth/}.


---

## Lead verdict (269) — 2026-10-23

**ACCEPTED.** The detector is innocent; the fault is the *extent of the cloud we hand it*.

What the lead checked independently, not taken on report:
- `pota269_s1_s_extent.npy` recomputed (numpy, lead): p50 **-2.675**, p95 **+2.801**, p98 **+3.659**, p99.5 **+4.358**, max **+5.039**, min -7.384 — matches the ticket to 3 dp. The sheet really does end 4.4-5.0 mm outboard of the author's lane.
- `edgeline_extraction_headless.cpp:1365` `const float FACE_ALIGN_VETO = 2.0f;` and the test at `:1387` `if (align <= FACE_ALIGN_VETO)` with `align = nn.dot(rp/rl)` in [-1,+1] — the veto cannot reject anything. Confirmed inert by construction, per the `:1358-1364` comment; it is not a lever on this defect either way.
- Paper quotes at `C:/PR/papers/text/sfspp-2502.13986v1.md` `:145`/`:149`/`:155`/`:164` read verbatim and match what is quoted above.

Consequences recorded:
1. **Not off-spec at the detector.** The paper's rule implemented as written (PCL boundary estimation, 90 deg default, r = 2/4/6) returns our curve (+3.75 mm). Our radius/angle/veto/snap are not the fault, and no setting of them reaches the crease. That is a cleaner negative than a parameter story.
2. **The positive control is supervised — do not cite it as a cure.** The cut uses the author's lane to define `s > +0.5`; it proves where the defect is born (cloud extent), not that we can fix it. Any future ticket must find the crest without the author.
3. **Pot H is a different animal.** 6 of 8 stations at |s| <= 0.3 mm, one contiguous 2-3 station excursion with either sign (P01 +5.9, P02/P03/P10 -5.6/-5.1/-5.0). This finding does NOT close the parallel-ridge family; that stays open for its own ticket.
4. **Next question, deliberately left open here:** *where* do the roll-over faces join `Surface_1` — the same region-growing cluster (tau_theta too permissive) or a separate cluster merged/selected in? That decides whether the faithful fix is a parameter (tau_theta / merge criterion, paper :147-162) or a new criterion. Instrument first; a trim gate is the fallback, not the first move.
5. **Third substitute in a row** (K-D filter, "B-spline" sphere-marcher, now the crease gate). The paper prescribes none of the three; the faithful path is checked first each time.

Landed: ticket only. No C++ change, nothing built, nothing run by the lead.

