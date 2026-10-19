# Source elimination — stop the outer loop entering the bag at prep

GOAL: CLOSE THE TAP, NOT JUST MOP THE FLOOR.

**Answers:** E1

**Blocked by:** 148 (outer 195 = 182 C-base + 11 GridX; letting-in stage = prep fixed-r BoundaryEstimation admits both lip faces + dead ROR reload-over, 67 §1) + 67 (split-then-select prescription §4)

**Status:** results-in

**What to deliver:** a prep-side elimination method for the outer-face loop, prototyped login-node-numpy against the C-base inputs (NOT the 314 bag — go upstream of it): (1) reproduce the admission — show the fixed-r BoundaryEstimation cloud containing both lip faces at one station sample, and the dead ROR reload-over path (file:line for both); (2) implement 67 §4 split-then-select at the boundary cloud + forward-cone guard + revived ROR as a prototype filter on that cloud, and measure outer-face admission before/after (bar: >=90% outer reduction with inner kept >=95%, ORIG-free rule only); (3) name the exact prep files/lines to patch for production and the GridX secondary (X2/X4 rings + SURF-C1 re-admitting outer faces at C36-46/C94-97/O37-fringe). A prototype that cannot separate the faces at cloud level must say so with the overlap numbers — that verdict sends the fix back to bag-space filtering (149's rule) as the permanent method.

**Starting position:** 67 Comments §1+§4 (mechanism + prescription), 148 §2 (per-stage table), prep sources boundary_filter.cpp + edgeline_extraction_headless.cpp. Login-node numpy only — no Slurm, no E2E. New scratch pota150_repro/; renders under laptop artifacts/pota150/.

**Rules:** ORIG Bl_0 ruler-only; control = reproduce 148's C-base outer fraction (182/195) from the upstream cloud first or stop; COMMIT NOTHING (prototype scripts only, patch named not applied); Comments-only ticket edits.

- [ ] Admission reproduced at cloud level (both faces + ROR path, file:line)
- [ ] Prototype split-select + guard + ROR, before/after numbers vs bar
- [ ] Production patch named (files/lines) + GridX secondary
## Comments (worker, 2026-10-19 -- login-node/laptop numpy only; COMMIT NOTHING)

**Verdict: TAP CAN BE CLOSED AT THE C-BASE CLOUD LEVEL -- face-side select (align<=+0.5) drops 180/182 outer (98.9% reduction, bar >=90%) while keeping 88/88 inner (100%, bar >=95%). Both bars pass with margin. Revived-ROR alone is dead-or-harmful; guard-without-select fails; the pipeline order is select-FIRST, then walk.**

**0. Control GREEN (reproduce-or-stop PASSED, p150_step0_control.py).** Rebuilt from read-only 143/148 banked inputs: bag 314, C-base 270, all-bag inner/outer/mid 116/195/3, C-base inner/outer 88/182, C-base share of outer 182/195 = 0.933 -- all exact-equals 148. ORIG Bl_0 ruler-only (station frame + dr classes for scoring); zero ORIG points in any cloud. No Slurm, no E2E; tickets 39-149 read-only; COMMIT NOTHING done. Scratch .scratch/pota150_repro/ (5 scripts + txts/npy); texts mirrored to artifacts/pota150/.

**1. Admission reproduced at cloud level (both faces + dead-ROR path, file:line).**
- Letting-in stage: edgeline_extraction_headless.cpp:921 PCL BoundaryEstimation, :944 setRadiusSearch (adaptive radius; 67's fixed-r=4mm era), :949 setAngleThreshold(0.6pi -- admits both lip faces as boundary), :955-962 boundary-point collection, :967 save boundary.pcd. The fixed 0.6pi angle gate is the diameters-wide door: no face discrimination at any radius.
- Dead-ROR reload-over: :1001-1030 RadiusOutlierRemoval computed + saved to cloud_Filtered.pcd (:1030), then :1032 pcl::io::loadPCDFile(tempEdgeFolder + "boundary.pcd", *boundaryCloud_Improved) reloads the UNFILTERED cloud over the improved one -- the one filter that could drop a loop is dead code in effect. Sequencer getPointsInSequence (:806-892, greedy KNN K=adaptive-size/10 at :824-826, no heading/component guard) is then called at :1034 on the unfiltered cloud.
- Cloud-level numbers (C-base-only, 270 dots): 22 straddle stations hold BOTH faces in the upstream cloud at the same ORIG station (s1,3,5,6,16,20,64,74,82,85,122,126,137,149,154,185,194,197,198,201,208,209); inner-seated 61 vs outer-seated 110 stations; C-base-only band med +3.83 p90-p10 5.92 (= full-bag 5.91 -- the bag's width is born here). Ruler-vs-observable agreement: dr-inner dots are 98% face-in, dr-outer 99% face-out -- the mesh-normal face observable sees the same two loops ORIG does.

**2. Prototype before/after vs bars (ORIG-free rules, ORIG-scored; p150_step2_filter.py).**
- Face-side select keep-align<=+0.5: kept 90 / dropped 180; outer kept 2/182, reduction 0.989 PASS; inner kept 88/88 = 1.000 PASS. The 2 surviving outer dots are lip-edge-face (align~0) seats, not wall-face.
- Revived-ROR ball-count: production-adaptive r=9.7/k6 drops 2 dots (reduction 0.005 -- confirms 67's dead-filter diagnosis: both loops are dense, ROR has nothing to grip); r=6/k6 drops 108 but kills the TRUE edge first (inner kept 46/88 = 0.523 -- ROR revival without a face rule attacks the sparser inner loop, i.e. actively harmful); r=14 drops 0. Verdict: do NOT revive ROR as a standalone fix.
- Component split at 5mm gaps (67 presc): 35 fragments, top comps FACE-PURE (27 all-outer, 24 all-inner, 22 all-outer, 17 all-outer) -- split-then-select works at fragment level with the face-side rule as the selector; fragments still need chaining (hence the walker).
- Face-select + ROR r=6 remainder: outer 0 kept (1.000) but inner 46/88 -- ROR adds nothing once face-select has done the job; drop it from the patch.
- Guard walk (p150_step3_guard.py / step3b): on the FULL 270 cloud, heading guards do NOT beat naive (naive 23 hops/15 direct vs half-plane 25/17 vs cone-60 33/25; cone-60 teleports: jumps 39->63) -- guard-without-select fails because loops touch at fold points where heading cannot disambiguate. Real pipeline order (face-select FIRST, walk the kept-90 cloud): direct in/out hops = 0 (7 residual = in/edge flicker), jumps>5mm = 16 at gap stations (12,21,28,64,67,74,77,80,89,122,135,148,156,182,185,192 -- flanking 148's predicted honest spans (102,120)/(169,171)/(179,181)). Production guard choice: distance-gated half-plane (cos>=0 + 6mm gate), NOT cone-60 (over-constrains on high-curvature lip, teleports).

**3. Production patch named (not applied) + GridX secondary.**
- Primary (edgeline_extraction_headless.cpp): (a) DELETE the killer reload at :1032 (or repoint :1034 sequencing at cloud_filtered) -- one-line resurrection, but alone insufficient per ROR numbers above; (b) insert face-side veto between :999 (boundaryImproved save) and :1034: drop dots whose nearest-surface-face alignment > +0.5, reusing the unclustered-surface cloud already loaded at :977-996 (first production probe per 67 §4: verify outer-loop dots' nearest-unclustered sources sit on the outer-face strip near the lip -- decides the exact veto field; mesh-face align is the demonstrated equivalent); (c) split-then-select in getPointsInSequence (:806-892): emit one loop per >5mm-gap component + distance-gated half-plane heading guard (cos>=0, 6mm gate) in the K-stepper; (d) do NOT add standalone ROR tightening (harms inner loop).
- GridX secondary (11 outer dots at C36-46/C94-97/O37-fringe, 148 §2): the X2/X4 rescan rings admit via SURF-C1 (disp<=2.5 + dmid<=5 union -- prototype gates .scratch/pota143_repro/p143_step2.py:124, p143_step5.py:106 admit_rung/SURF-C1 lines) which licenses outer-loop faces at span seats; same face-side veto (align>+0.5) must gate every rescan/grid admission before banking, or the 11 dots re-enter through the side door after the tap is closed.
- Honest cost (unmasked, matches 148 prediction): walking the thin 90-dot cloud leaves ~16 jump gaps flanking the (102,120)+(169,171)+(179,181) honest spans -- that is 147's true-extraction target, now unmasked from fake outer-loop cover, and goes to 149's thin-line walk as banked input.

**Renders (eye-checked).** artifacts/pota150/p150_admit.png (C-base-only station-vs-dr: two bands at shared stations) | p150_filter.png (before/after histograms) | p150_walk.png (filtered-walk face trace + step-length jumps = honest voids). Scratch .scratch/pota150_repro/; tickets 39-149 untouched; COMMIT NOTHING done.

