# 211 - P01 fresh-Bl1 is an interior loop, not the second rim (209 follow-up)

Status: done
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20): find out why the Piece 1 trace differs. Lead analysis
(same day, laptop, fetched 208 files): our P01-Bl1 (92 pts, arclen 213mm) is
NOT a short second rim -- it is a small closed loop (~40mm across, centroid
[30.6,-6.9,410.7]) sitting in the INTERIOR of the P01 face, 27.6mm (med)
from the author's Bl1 and 28.3mm from the author's Bl0, 0/92 pts within 2mm
of either. It hugs the mesh (prox med 0.13/max 0.28), so it traces a real
surface feature -- just not a fracture rim. Meanwhile our Bl0 (207) and the
author's Bl1 (214) trace the outer rim together (red/blue in the pictures).
So our loop picker (largest-two boundary clusters) ranked this interior loop
above the true second rim face. Pictures: artifacts/pota209/p211_P01_loops.png
(loops-only, decisive) + p211_P01_bl1.png (on-mesh). Script: p210_check_p08.py
(coverage) + p211_p01_bl1.py.

## Boundary
Read-only diagnosis. Spartan inputs: 208 pipe tree pota208_pipe
(edgeline_stage.log P01 section, P01 surface dirs), bundle v0 P01 files.
Do NOT rebuild the pipe, do NOT modify v0, do NOT touch 210's v1 bundle or
its running seating job (different paths -- stay out of pota210_bundle_v1
and pota208_e2e run dirs), the live main checkout, or the 2 pre-E2E stashes.
Touch NO tracked file except this ticket. COMMIT NOTHING (lead commits).

## Constraints
Answer three ordered suspects: (1) WHAT interior feature the orange loop
circles -- mesh hole in P01's face? sharp interior ridge (wheelThrowing)?
normal-estimation artifact picked up by BoundaryEstimation? Check the P01
mesh around centroid [30.6,-6.9,410.7] r~25mm. (2) WHY the walk seeded and
closed there instead of the second rim face -- seed-point choice, loop
ranking (largest-two), early termination? Cite edge-log lines. (3) WHERE the
true second rim face went in our output -- unfound boundary cluster, merged
into Bl0, or filtered? Compare against author Bl1 (214 pts) point by point.
Standing submit sign-off covers any probe jobs; held allocation for iterative
checks, sbatch only for long unattended runs with laptop-side poll.

## Acceptance
Named mechanism with evidence: the interior feature identified (with a
picture circling it on the mesh), the picker failure cited to code/log
lines, and the fate of the true second rim stated. Fix PROPOSED, not applied
(separate ticket on acceptance). A picture suffices per standing decision.

## Required evidence
Comments: feature identification + picture paths + log/code cites + true-rim
fate + proposed fix. Final report: same, self-contained.

## Lead verdict (2026-10-20)
ACCEPT. Worker numbers independently rechecked on laptop (92 pts, 2 jumps >10mm max 36.2, end gap 27.2 -- exact match); 5 stage pictures on disk; only this ticket touched, nothing committed by worker. Correction accepted: no largest-two ranking in the walker (my brief phrasing wrong; largest-two is the mesh-splitting stage). Fix NOT applied -- separate ticket on user nod.

## Comments (worker, 2026-10-20 -- read-only diagnosis, COMMIT NOTHING)

**Mechanism in one line:** P01 fresh-Bl1 (92 pts) is the sharp circular wall-base
junction step of the P01 sherd (r~=26mm full circle, NOT a fracture rim). The
208 pristine walker seeded on that circle's dense boundary points and stalled
there (287 of 1139 boundary pts consumed, rest dead iterations), so the true
second rim (author-Bl1 lane, ~28mm away) was never walked. No picker ranked
anything -- Bl1 IS the whole Surface_1 output; the rim gate is advisory-only.

**(1) WHAT feature.** Full-circle step/ledge at the wall-base transition:
cylindrical coords about the P01 vessel axis
(Dataset/Axes/Pot_A_Piece_01_Axis.xyz: pt [-55.47,-133.90,62.45], dir
[0.228,0.332,0.915]): ring r med 26.25 std 0.71 (min 24.90 max 27.38), height
along axis med 380.55 std 0.42 (span 1.8mm), unique angular coverage 355.2 deg
(largest gap 4.8 deg), walk-order sweep 472 deg (overlaps itself ~112 deg).
Mesh (h,r) profile: wall descends to (h~380, r~26) then kinks into the base;
the ring sits exactly on that kink (picture p211_worker_feature.png left).
NOT a mesh hole: 0 boundary edges in the 100k-vert/200k-face mesh (watertight).
NOT a normal-estimation phantom: the mesh profile itself turns there and the
ring conforms (r-std 0.71mm, mesh-prox med 0.13/max 0.28 per 209 numbers).
Ring point normals ~axial (e.g. Bl1 xyz head: n~(0.36,0.60,0.71),
n.axis~=0.93) = locally horizontal tread: the sharp upper edge of the step.
Related input dots: 2243/56341 (3.98%) of the Surface_1 input cloud within
2mm of the ring, forming the same circle on the input surface
(picture p211_worker_s1_input.png). Open side note (not needed for verdict):
pipe-root Pot_A_Piece_01_Surface_{0,1} (207/92 lines, values ~0-145/~30-40)
are per-breakline-point files of unknown quantity -- correlated against
r/h/theta/arclength, no match; left as an open question.

**(2) WHY the walk lived and died there (pristine walker, no picker).** 208
binary = e2e-pristine source. getPointsInSequence
(e2e-pristine:edgeline_extraction_headless.cpp:533): seeds at
cloud->points[0] (L548, BoundaryEstimation file order -- arbitrary vs
geometry), greedy nearest-UNVISITED among K=50 (L553, L571-582); when all 50
nearest are visited nothing is pushed but the for counter (L550, bound =
cloud size) still advances => dead iterations, output shorter than input.
Log (pota208_pipe/edgeline_stage.log): Surface_1 boundaryCloud 1139 (L209)
-> Improved/Filtered/reload all 1139 -> cloud_sequenced 287 (L220, 25%
consumed) -> CompleteBreakline 92 (L242) -> 12 gap-segments
(9/17/7/9/7/21/6/5/5/4/10/4, L261-272) -> Saved PCD with 12 segments (L457).
Direction kept ("46 / CountClock Wise - Right", L240-241, no
Change_Sequence). Contrast Surface_0: 829 (L16) -> sequenced 628 (L27, 76%)
-> Bl0 207 (L49): same walker, seed luck on the main rim. Correction to the
ticket's "largest-two picker" phrasing: the pristine edgeline stage has NO
cross-loop ranking (single walk per surface; all segments concatenated:
12 segs 104 rows - 12 dropped = 92, cf. rows-1 push loop). The only
largest-two code (mesh_processing_headless.cpp:1710-1711) belongs to the
surface-splitting stage, not the walk. Rim gate is advisory: threshold
100*stdev/mean < 50 (e2e-pristine L2855); ALL P01 segs Not Rim (Surface_1:
58.9-138.4, L433-444; Surface_0: 72.6-126.0, L135-139) yet both files saved
unconditionally (writeBreaklinePCDWithSegments/savePLY/copy, L2890-2895;
atLeastOneSegIsRim only flips segment flags). Final xyz walk order shows 2
jumps >10mm (max 36.2 at idx 7,22) = 3 gap-groups (8/15/69), first-last gap
27.2mm -- even the interior loop did not close cleanly
(picture p211_worker_s1_walked.png; true rim blue, unwalked).

**(3) WHERE the true second rim went.** Never walked (not merged, not
filtered). The 852/1139 unvisited boundary pts (incl. the author-Bl1 lane,
med 28.33mm from our Bl1, 0/92 <2mm) never entered cloud_sequenced. Bl0 is
an independent pipeline (Surface_0) riding the OTHER lane (fB0==oB0 med
0.52, 100%<2mm; fB0-oB1 med 5.05, 0%<2mm -- P01 slots agree per 209 matrix).
Author-Bl1 lane (214 pts) has NO counterpart in our output.

**PROPOSED fix (not applied).** Port the already-landed POTA-154 split-walk
cure (main: components at 5mm, largest-first, forward cone cos>=0 + 6mm
gate, cuts, no dead iterations) to the pristine line OR minimal pristine
patch: (a) seed largest-first / multi-seed unvisited components, (b) restart
on stall instead of dead iterations so every boundary component is walked,
(c) keep two rim lanes per piece with a wall-thickness separation prior
(~3-8mm) so two loops on one face can't occupy both slots. Fix-ticket
acceptance: P01 Surface_1 Bl1 ~= author Bl1 (med <2mm, >=90% <2mm), Bl0
unchanged. Also decide: make PercentDev gate actually gate, or delete it
(currently decides nothing).

**Stage-marking pictures (same frame side+top, committed nowhere):**
- artifacts/pota209/p211_worker_s1_input.png -- Surface_1 input cloud (gray,
  1:7 subsample) + ring-related input dots red (<2mm of final ring, 2243) +
  final ring orange. Enters the chain as a dense flagged circle at the kink.
- artifacts/pota209/p211_worker_s1_walked.png -- final 92 split at >10mm
  jumps into 3 walk gap-groups (blue 8 / orange 15 / green 69) + author Bl1
  blue (the unwalked true rim, same frame). The walk's whole world.
- artifacts/pota209/p211_worker_feature.png -- (h,r) zoom (ring on the kink)
  + 3D mesh zoom (ring on mesh, author rim far below).
- artifacts/pota209/p211_worker_profile.png + p211_worker_ring.png -- full
  (h,r) context + radius/angle diagnostics (r const, h const, 472 deg sweep).
- Lead's decisive loops-only: artifacts/pota209/p211_P01_loops.png.
Missing stage (stated, not faked): per-piece Temp_edge boundary/sequenced
clouds were overwritten by P08 (Temp/Temp_edge/Pot_A/* is P08's; boundary
1139->287 evidenced by log L209/L220 only). Surviving P01 stage files:
Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz (56341 pts, fetched to
artifacts/pota209/src_pipe/, md5 n/a -- untracked pipe file) + bundle v0
breaklines/mesh (local src/). Scripts (untracked): p211_worker_feature.py,
p211_worker_ring.py, p211_worker_profile.py, p211_worker_final.py,
p211_worker_stages.py. No Slurm submitted; no tracked file touched except
this ticket; Status left ready-for-agent (lead flips).
