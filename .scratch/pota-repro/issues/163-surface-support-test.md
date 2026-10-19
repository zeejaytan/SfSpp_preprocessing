# Surface-support test: true edge has surface on one side only, false edge sits amid surface

GOAL: TEST EACH DOT AGAINST ITS SOURCE SURFACE, NOT AGAINST OTHER DOTS.

**Answers:** E1

**Blocked by:** 162 (dot-vs-dot emptiness fails backwards -- wrong substrate) + user correction 2026-10-19 + 155 (extraction code sites).

**Status:** results-in

**User's correction (verbatim):** the dot comes from a surface; that surface's true edge one side is empty, but the false edge has point cloud or vertices on all sides. So put it back to the surface to test -- not whether a DOT is next to another DOT. (Open: how the surface is represented in the code -- mesh, point cloud, grid -- the worker establishes this first.)

**What to deliver:** (a) SUBSTRATE: identify the surface representation feeding the veto-site dots (mesh triangles? point cloud? from which stage output -- mesh-stage Surface xyz / Point PCD / Dataset). (b) SCORE: for the 364 C01 veto-site dots + Pot A rim dots, a support-asymmetry score measured on the SURFACE (e.g. surface present in a half-ball on one side only vs all around; boundary-distance of the dot's source location). Labels via ORIG overlay as in 160/162. One cutoff separating rim from face on BOTH pots? (c) RULE (if it separates): support-gated veto in the worktree variant, both pots run + 98-gated. Bar: Pot A cure kept AND C01 rim kept (at-or-better-than fresh 5.61/22.9). (d) If it straddles, negative with plots.

**Starting position:** 155 Comments (extraction code + stages); 160/162 Comments (veto-site dots, ORIG labels, gate scripts); staged worktree. New scratch pota163_repro/; renders artifacts/pota163/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-162 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] substrate identified (representation + stage + paths)
- [x] support-asymmetry scores A + C01 (rim vs face vs ORIG)
- [ ] (if separates) support-gated veto built + both pots run + gated -- NOT BUILT (bar failed, nothing gate-passing to build; same entailment as 162)
- [x] Verdict + render paths
- [x] snap arm e1 (snap stage + pre-snap inputs located) + e2 (pre-vs-post vs ORIG) -- e3 not warranted (no drag)

## Added arm (user, 2026-10-19): snap-displacement, move-back instead of delete

User recalls dots were moved by snap refinement (cf. 123/124: r1 + disp-cap-2.5 snap-drag). Hypothesis: the false-loop dots sat ON the edge pre-snap and were dragged OFF it -- so the cure is move-back-to-edge (or no-snap), not deletion. Worker adds: (e1) locate the snap stage in the sub-copy code + its inputs (pre-snap positions); (e2) compare pre-snap vs post-snap positions of the 364 C01 veto-site dots vs ORIG -- did snap move rim dots off-rim? (e3) if yes, build a no-snap (or snap-back) variant and gate it on both pots alongside the support test. Pre-snap evidence decides: dots born false -> support test stands; dots born true then dragged -> move-back is the fix.
## Comments (worker, 2026-10-19) -- CLEAN NEGATIVE, both arms, analysis-only

### 1. Substrate finding (user's open question: mesh, point cloud, or grid?)

POINT CLOUD -- established from `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`. Veto-site dots are PCL `BoundaryEstimation` points computed on a `PointNormal` sheet cloud `cloud_Surface_AllSamples_Cleaned.pcd`, built by `cleanSamples()` from the mesh-stage `*_Surface_0/1.xyz` files (6-col xyz+normal, dense ~30k pts/sheet). No mesh triangles are consulted at veto time. The K=1 snap (lines 951-972) snaps each boundary dot to the nearest point of the `unclustered` cloud.

Frame-match (laptop, scipy cKDTree): Pot A veto CSVs match the local `NURBS_Dataset_20250905_ProperSegmentation/SfS_pp/Surfaces` sheets at med 0.25-0.3 mm (even-c tags -> Surface_0, odd-c -> Surface_1). C01 c0 (364 dots) is frame-EXACT (med 0.000 mm) to `.scratch/pota123_repro/Pot_C_Piece_01_Surface_0.xyz`. The `sfs_main` backup surfaces are a different segmentation (med 4.16 mm) -- REJECTED.

### 2. Support-asymmetry scores vs ORIG (tangent-plane maxgap of DENSE surface neighbours at R=12 mm)

C01 S0 (86 NEAR-rim / 223 FAR-face): NEAR med ~160 deg (half-ball empty = true edge), FAR med ~80-88 deg (surface all around = interior false positive). AUC(rim>face) 0.83 at R=12, rising to 0.92 at R=16 -- the face gap SHRINKS with scale (more sheet enters the ball = interior signature).

Pot A 6 two-face surfaces (labels reproduce 162: rim=630, face=445~441): ALL SIX FLIP -- face gaps >= rim gaps, AUCs 0.16-0.49 at every radius 3-16 mm, radius-INVARIANT (stable lip-edge geometry, not interior). A rim-side cutoff keeping C01 rim keeps the Pot A FACE and kills the Pot A rim; the reverse kills C01 rim.

Mechanism: C01's false dots are BoundaryEstimation interior false positives (sheet extends well past the false loop); Pot A's false dots sit on the outer face's OWN lip edge (true boundary of the second sheet, cf. 150 guard: loops touch on flaring lips). Different birthplaces -- no single asymmetry direction can serve both pots.

### 3. Formal one-cutoff bar (rim-kept>=95% AND face-dropped>=90% simultaneously, C01 + all 6 Pot A surfaces)

Keep-high-gap direction: best worst-case 9.2% rim-kept / 0.0% face-drop (thr=60). Keep-low-gap direction: best 0.8% / 22.7% (thr=60). Every threshold in both directions fails with HUGE margins. RULE NOT BUILT -- nothing gate-passing to build; per-pot cutoffs/directions would need pot identity, which is not mesh-observable (bar explicitly one cutoff both pots).

### 4. Snap arm (e1-e3) -- drag hypothesis REFUTED

Staging recovered from Spartan `pota160_repro/pota160_C/` (S1 xyz, `unclustered.ply` 2343 verts, leftover VAR `boundary.pcd` + `boundaryImproved.pcd`, S1 109 pts, veto log kept=109/dropped=0) -> `.scratch/pota163_repro/inputs/`. CONTROL: recomputed K=1 snap reproduces `boundaryImproved.pcd` EXACTLY (109/109). e2 on C01 S0: snap displaces dots (med 2.19 mm, 281/364 >1 mm, max 10.6) but ALL 86 pre-NEAR dots stay NEAR post-snap (off>2 mm: 0/86, med 1.42->0.90 mm -- they move ON-rim); FAR dots are born far and stay far (37.6->38.2); preNEAR-postFAR = 0. S1's 109 dots sit >5 mm from ORIG (non-rim lower edge -- veto kept them, VAR gate failed on rim coverage, not S1). e3 (no-snap variant) NOT warranted -- false dots were never on-rim.

### 5. Banked context (cited, not rerun -- tickets read-only)

Pot A pairs BASE->VAR (160): P01 193->191, P02 727->79, P03 485->117, P04 242->101, P05 326->55, P06 144->105, P07 64->37, P08 61->16. C01 gate (160): BASE 5.61 mm/22.9% vs VAR 5.96 mm/1.3%.

### Verdict

CLEAN NEGATIVE twice over: (a) source-surface support asymmetry points the WRONG way on Pot A vs C01 -- the user's one-side-vs-all-sides picture holds on C01 but is inverted on Pot A (lip-edge false loops); (b) snap moves dots but never off-rim -- no move-back cure exists. Veto-site dots on the two pots are different phenomena sharing a name. Next Dijkstra/A* work should treat Pot A lip-edges and C01 interior loops as separate targets, or find a feature both share (neither asymmetry, angle/160, dot-density/162, nor support/this ticket).

### Renders (eye-checked: axes, legends, both loops visible)

- `artifacts/pota163/C163_C01_scores.png` -- rim/face gap histograms + AUC-vs-R sweep
- `artifacts/pota163/C163_PotA_scores.png` -- per-surface medians + all-AUC<0.5 bars
- `artifacts/pota163/C163_C01_spatial.png` -- gap-coloured dots + veto-vs-ORIG overlay (outer loop on-ORIG, inner false loop off-ORIG)
- `artifacts/pota163/C163_snap.png` -- displacement hists + pre/post ORIG scatter (diagonal hug)

Scripts: `.scratch/pota163_repro/p163_framematch.py, p163_c01match.py, p163_snap.py, p163_e2.py, p163_support.py, p163_support_lib.py, p163_sweep.py, p163_bar.py, p163_plots.py` (+npz). Staged inputs: `.scratch/pota163_repro/inputs/`.

### Discipline

Analysis-only: relay worktree untouched (no build, no Slurm -- nothing for sacct), COMMIT NOTHING, tickets 39-162 read-only. Same-binary ORIG control N/A (no variant built -- same entailment as 162).
