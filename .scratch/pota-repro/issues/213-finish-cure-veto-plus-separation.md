# 213 - Finish the cure: veto recalibration + per-surface loop separation (212 follow-up)

Status: done
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20, option 1): finish the 154-port cure on the pristine
line so P01's second file carries the true rim and nothing else. 212 proved
the two gaps: (a) the Pot-C-calibrated face veto (align>0.5) drops 794/1139
P01-Surface_1 boundary dots and shatters the rim (largest kept component
113 < 214 needed -- count bet dead on arrival); (b) with the veto off the
walker covers the full rim 214/214 @ med 0.81 but files rim+ring mixed in
one slot (327 pts, 66.7% forward). Fix both, proved on P01 by the 211 bar.
175's rule STANDS (lead-verified 2026-10-20 from the port log: S0 -> 1x822
-> Bl0 207, S1 -> 8 comps -> Bl1 272, no pooling, slot filing clean) -- the
separation step works INSIDE one face's bag, never across faces.

## Boundary
Continue on branch pristine-splitwalk + worktree .scratch/.wt-pristine-
splitwalk + Spartan experiment copy sfs-splitwalk-212 (all exist from 212).
Do NOT touch: live main checkout, the 2 pre-E2E stashes (do NOT pop), 210's
v1 bundle and seating runs, bundle v0, the 208 pipe tree (read-only
reference). Port branch stays LOCAL until lead lands (COMMIT NOTHING).
Touch NO tracked file except this ticket. Fix scope ends at re-extract +
score -- NO assembly reseat here.

## Constraints
(a) Veto recalibration: Pot-A-geometry gate, ORIG-free (mesh-observable
only, 154 precedent). Target: rim survives as the largest connected
component at 5mm (veto-off shows the clean 2-group input: rim ~808 +
ring ~331 -- the gate must keep that whole, not shatter it). State the new
gate with numbers, not a tuned constant. (b) Loop separation: after the
walk, separate each face's loops into their own files (rim to Bl1, ring
aside -- never merged, never dropped silently); no choice at split time
means provenance first: which loop is rim-continuous vs step-circular is
decided by mesh-observable shape (closure, radius, wall-distance), stated
in the ticket before building. Minimal change to the 212 port; T24-pattern
discipline. Standing submit sign-off covers probe/rebuild/re-extract jobs;
held allocation for iterative work, sbatch only for long unattended runs
with laptop-side poll. Same-binary ORIG control in every scoring run.

## Acceptance
P01 fresh-Bl1 ~= author Bl1 (med <2mm, >=90% pts <2mm) AND fresh-Bl0
unchanged (still == author Bl0, med ~0.5/100%). Clean Spartan build from
the branch. Veto gate stated with keep/drop numbers; separation rule stated
with shape criteria; component table + picture paths filed. NO reseat.

## Required evidence
Comments: veto gate before/after (kept/dropped per surface), separation
rule + shape criteria, P01 before/after numbers both lanes, 212-bar
comparison (recipe 8.70/35%/42% -> now), picture paths, binary md5.
Final report: same, self-contained. Do NOT flip to done -- lead flips
after review.

## Lead verdict (2026-10-20)
ACCEPT. Numbers rechecked EXACT on laptop (Bl1 med 0.67/97.3 vs reported 0.67/97.32; Bl0 0.50/100); both jobs sacct-COMPLETED 0:0 (build 2:10, edge 0:59); branch = 1 file, base b1ed4d1; overlay picture eye-checked (rim coincides, ring cleanly split to sidecar). Bar met both lanes. Cure line for 214: branch pristine-splitwalk.

## Comments (worker)

### 213 RESULT (worker, 2026-10-21) -- BAR MET, both lanes, eye-confirmed

Build: clean, job 33514459 COMPLETED. Binary md5:
`6608ab9ac423f04db9fc4df245738786` (build-212/EdgeLineExtractionHeadless).
Edge re-extract: job 33514736 COMPLETED (Spartan checkout sfs-splitwalk-212,
pipe pota212_pipe; source = worktree patch uploaded, LF-normalised).

Veto before/after P01-S1: recipe 0.5 kept 345 / dropped 794 -> keep-all 2.0
kept 1139 / dropped 0. All 16 faces: dropped 0 everywhere.

LOOP-SELECT P01 (log edgeline_stage_212.log): S0 bag=829 comps=1 -> single
RIM (r_med 53.2), no ring, whole-bag walk, sidecar empty. S1 bag=1139
comps=2 -> comp0 808 RIM (r_med 54.2 / r_std 6.9 / h_span 15.0), comp1 331
RING (r_med 26.29 / r_std 0.72 / h_span 1.99); rim=808 ring=331 sidecar 331.
All other pieces P02-P08: single-comp faces, no ring, sidecars empty
(0-byte xyz + log line) -- the step ring is a P01-S1-only feature.

P01 vs author (same numpy ruler, .xyz finals):
- Bl1: recipe 8.70 / 35.29% / 41.59% -> veto-off 0.81 / 66.67% / 100%
  -> 213: 224pts, med 0.67 / 97.32% (rev 0.64 / 100%). BAR MET.
- Bl0: before 0.52 / 100% -> 213: 207pts, med 0.50 / 100%. UNCHANGED.
- xcheck freshBl1 vs authorBl0: med 5.02 / 0% (lanes still distinct).
- sidecar ring (331 walked) vs before-Bl1 (92): med 0.50 / 100% -- the old
  ring file sits entirely on the sidecar loop; nothing lost, nothing added.
- jumps: freshBl1 0 over 10mm (endgap 9.5); freshBl0 0 (endgap 4.1).

Pictures (eye check done, both lanes overlay author; rim/ring cleanly split):
- artifacts/pota213/p213_P01_bl1_vs_author.png (Bl1 vs author side+top,
  rim-vs-sidecar side+top)
- artifacts/pota213/p213_P01_bl0_vs_author.png (Bl0 vs author side+top)
Fresh files: artifacts/pota213/Pot_A_Piece_01_Breakline_{0,1}.xyz/.pcd +
Pot_A_Piece_01_Breakline_1_stepring.xyz (.pcd on Spartan pipe). NO reseat
run (scope ends at re-extract+score per ticket). Ready for lead review.

### 213 gate + rule stated BEFORE building (worker, 2026-10-21)

**VETO GATE (ORIG-free, Pot-A geometry): keep-all.** `FACE_ALIGN_VETO = 2.0`
(align in [-1,1], so nothing is dropped). P01-S1 expectation: kept 1139 /
dropped 0 (recipe 0.5 gave kept 345 / dropped 794 and shattered the rim to
8 fragments, largest kept 113 < 214 author pts). Justification, Pot-A
calibrated: the centroid-radial alignment does not separate lip faces on
Pot-A -- any threshold near 0.5 that drops anything shatters the true rim
(rim dots span the veto band), while veto-off input is already a clean
2-group at 5mm (808 rim + 331 wall-base step ring; rim walks 214/214
contiguous, rev 100%, med 0.81). So the principled Pot-A gate keeps the
whole bag (1139/0) and separation moves downstream to shape -- strictly
INSIDE one face's bag (175 stands: S0 single-comp lane untouched, no
pooling across faces). Same centroid observable as 154, degenerate-pass
threshold; no ORIG constant, no ORIG geometry in the gate.

**SEPARATION RULE (per-surface, mesh-observable, ORIG-free).** After the
walk-input assembly (`boundaryCloud_Improved`, 5mm union-find, largest-
first), score each input component in cylindrical coords about that
piece's pipeline axis (`Dataset/Axes/Pot_A_Piece_XX_Axis.xyz`, 6-number
pipeline product -- no ORIG): r_med, r_std, h_span, count.
- RING (wall-base step, sidecar, never Bl): 20 <= r_med <= 35 mm AND
  r_std < 2.0 mm AND h_span < 4.0 mm AND 50 <= count <= 500.
  P01 calibration (ticket axis [-55.47,-133.90,62.45] dir
  [0.228,0.332,0.915]): ring 92-pt loop r_med 26.3 / r_std 0.73 /
  h_span 1.8 -> passes all; author rim 214 r_med 54.1 / r_std 7.15 /
  h_span 14.6 -> fails all three (margins: 28mm med, 10x std, 8x span).
- RIM (Bl file): union of all NON-ring components (normally one: P01-S1
  808), walked by the unchanged 212 walker; full B-spline pipeline
  downstream sees rim only, so no rim-ring chord.
- Fallback (logged, never silent): axis missing -> largest-first, no
  shape split; all-ring bag -> largest component emitted as Bl AND flagged
  `[LOOP-SELECT] FALLBACK` for the eye.
- Provenance per face: `[LOOP-SELECT]` log line + component table
  (count / r_med / r_std / h_span / verdict), main
  `Pot_A_Piece_XX_Breakline_{0,1}.*` = rim, sidecar
  `Pot_A_Piece_XX_Breakline_{0,1}_stepring.*` = ring (walked ring pts;
  empty + log line when absent). Minimal change: veto constant 1 line +
  caller-only split in `getInitialBoundary...` (walker untouched).

