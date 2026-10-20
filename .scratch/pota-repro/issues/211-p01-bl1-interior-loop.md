# 211 - P01 fresh-Bl1 is an interior loop, not the second rim (209 follow-up)

Status: ready-for-agent
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

## Comments (worker)
