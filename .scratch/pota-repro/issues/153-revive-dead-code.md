# Revive the dead code — apply the 150 patch to prep sources

GOAL: THE TAP CLOSED IN PRODUCTION, NOT IN PROTOTYPE.

**Answers:** E1

**Blocked by:** 150 (production patch named not applied: face gate at edgeline_extraction_headless.cpp:949 angle gate + un-kill :1032 ROR reload-over; GridX secondary: SURF-C1 veto at p143_step2.py:124 / p143_step5.py:106)

**Status:** results-in

**What to deliver:** (1) apply the patch to the prep sources in a working tree (face-discrimination gate at the :949 boundary admission + remove the :1032 raw-cloud reload-over so cloud_Filtered survives; GridX SURF-C1 veto); (2) rebuild whatever the patch touches — if the build needs Spartan or otherwise exceeds login-node/login-laptop means, STOP after staging the exact diff + build instructions and say so (do NOT submit jobs); (3) if built: re-run the C-base extraction and prove the outer loop blocked at source (outer share vs 150's 182/195 baseline, inner kept count) with the 148/150 counters. Production-illegal shortcuts forbidden: no ORIG-derived constants anywhere in the patch; the gate must be mesh-observable only.

**Starting position:** 150 Comments (file:line + prototype numbers), prep sources per 150 §1. New scratch pota153_repro/; renders under laptop artifacts/pota153/.

**Rules:** ORIG Bl_0 ruler-only everywhere; worker COMMIT NOTHING (diff staged as files in scratch, lead lands); tickets 39-152 read-only; Comments-only ticket edits.

- [ ] Patch applied in working tree (diff staged, ORIG-free)
- [ ] Build result (binary or stop-with-instructions)
- [ ] Re-extraction proof vs 182/195 baseline (or staged for lead)
## Comments (worker, 2026-10-19 -- laptop/lumpy numpy + staged C++ patch; COMMIT NOTHING, repo sources untouched)

**Verdict: TAP PATCH STAGED, VETO FIELD DECIDED -- STOPPED BEFORE BUILD (no toolchain on laptop).**
Control GREEN (270/88/182 + 182/195 share exact vs 150). Centroid-radial veto field
probe: outer kept 1/182 (red 0.995, bar >=0.90 PASS), inner 88/88 (bar >=95% PASS),
99.6% mask-agreement with 150's ORIG-axis align -- the production gate needs NO ORIG
axis. Patch staged as files in .scratch/pota153_repro/ (lead lands); build + C-base
re-extraction staged as instructions (needs Spartan/container: no cmake/PCL on laptop).

**0. Control GREEN (p153_step0_control.py).** Banked 150 inputs reloaded read-only:
C-base 270, inner 88, outer 182, all-bag outer 195, share 182/195 = 0.933 -- all exact.

**1. Veto-field probe DECIDED (p153_step1_vetofield.py -> p153_vetofield.txt).**
Production question from 150 section 3b: which mesh-observable field carries the veto.
Tested: per-dot nearest-mesh-face normal dotted with MESH-VERTEX-centroid radial
(no ORIG axis/station anywhere in the field; ORIG dr classes used SOLELY for scoring).
Frame check first: inverse-TF-mapped dots sit on Piece_01 DS mesh (dmin med 0.78mm).
Results: keep align<=+0.5 -> kept 89 / dropped 181; outer kept 1/182 red=0.995 PASS;
inner kept 88/88 = 1.000 PASS. Threshold sweep th=0.3/0.4/0.5 identical; th=0.6 still
passes (outer kept 9, red 0.951). Face-class split: dr-inner 86% face-in/0% face-out;
dr-outer 0% face-in/99% face-out. Production translation: surfCentroid = in-function
mean of the input surface cloud (ORIG-free by construction); per-dot normal = input
cloud normal (pipeline already loads it); unclustered-ply change NOT needed (its
nx ny nz confirmed present anyway -- p153_ply_header.txt). Residual: probe centroid
(mesh verts) vs production centroid (surface samples) -- covered by the full-band
class gap + the [FACE VETO] log line (see ORIG-free note).

**2. Patch staged (not applied -- boundary owns scratch only; COMMIT NOTHING).**
Target: edgeline_extraction_headless.cpp @ 4accb8d (prep production path; backup/
non-headless copies deliberately untouched -- lead decides porting).
- pota153_patch_edgeline_headless_part1.diff: hunk 0 (<functional>/<map>/
  <limits>/<algorithm> includes); hunk 1 face veto at boundary selection
  (:954-965: centroid + align gate keep<=0.5, counts to [FACE VETO] log);
  hunk 2 DELETE :1032 killer reload-over (sequence the vetoed cloud;
  cloud_Filtered.pcd stays diagnostic-only per 150 section 2 -- ROR revival is
  dead-or-harmful, never feeds sequencing).
- pota153_walker_new_function.cpp: full replacement getPointsInSequence
  (:806-892, signature unchanged): 5mm-gap union-find components walked
  largest-first + distance-gated half-plane guard (cos>=0, 6mm gate), cuts
  recorded in file order for detectSeparateLineSegments -- never teleports.
- pota153_gridx_surfc1_veto.named.diff: STAGED TEXT ONLY -- SURF-C1 gates live
  in read-only prototype scripts (p143_step2.py:124, p143_step5.py:106, tickets
  39-152 rule) and no production rescan/grid path exists in prep sources
  (verified by grep); lead ports the same align<=0.5 veto into any future prep
  rescan path.
- pota153_origfree.md: ORIG-free justification (no ORIG coordinate/axis/station
  in any hunk; 0.5/5mm/6mm are evidence-calibrated cut points on
  mesh-observable fields; Bl_0 ruler-only).
- pota153_build_instructions.md: STOP-WITH-INSTRUCTIONS (no cmake/PCL on laptop;
  Pot_C inputs Spartan-only) + build recipe + re-extraction counters to beat
  (outer 182->~1, inner 88/88, [FACE VETO]/[SPLIT-WALK] log watches).

**3. Re-extraction proof: STAGED FOR LEAD (not run -- no binary).**
p153_build_instructions.md section "Re-extraction proof" names inputs, counters,
log watches, and render extensions. Baseline to beat: 150's 182/195.

**Renders (eye-checked).** artifacts/pota153/p153_vetofield.png (centroid-align
histograms: blue inner cluster ~-0.75, orange outer ~+0.8, veto line +0.5 clean).
Scratch .scratch/pota153_repro/ (3 scripts + txts/npy); tickets 39-152 untouched;
COMMIT NOTHING done.

