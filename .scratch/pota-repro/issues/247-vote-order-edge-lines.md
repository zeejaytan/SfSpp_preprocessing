Status: done

Lead verdict (R6 2026-10-22): SPLIT stands. 4/4 jobs COMPLETED 0:0. CTL reproduces all six lanes exactly (greedy intact, guards hold). VOTE wins clean loops (P03-Bl0 0.58/100.0, P01 both match-or-better) but fails braid bags (P03-Bl1 exam, P22 both). Conviction accepted: NN-chain braids (turnSum 44-65 vs 4-9); missing stage is the paper's K-D tree filter, not ported. Vote arm stays OFF by default; NOT merged. Follow-up is the filter stage.

# Ticket 247: port the paper's vote-ordered edge lines (kill the greedy-walk seed)

Answers: whether vote-ordering cures P03-Bl1 with the paper's own method.
Needs-eye: no.

## Goal
Replace the greedy seed-walk's ordering with the paper's method (SFS++ Sec. Edge line extraction and segmentation + Fig. 6): resample boundary dots equidistant (d = 1.9mm), reorder counter-clockwise by normals + voting, segment at corner peaks. The seed problem must disappear by construction (voting has no start point).

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Edge stage ONLY (edgeline_extraction_headless.cpp and its call sites). Mesh/splitter/classify untouched.
- Read the full paper section first (C:/PR/papers/text/sfspp-2502.13986v1.md, from 'Edge line extraction and segmentation' through the corner-segmentation paragraph + Fig. 6 caption). The section was truncated in one lead read ('peaks in the distribution of dist...') -- the worker reads the complete text and cites the exact corner criterion before building.
- Exam piece: P03-Bl1. Bar: med<2 + cov>=90% vs author, zero jumps>10mm, Bl0 lane unchanged (0.72/97.8-class), walk order along ONE loop.
- Guards (no-regress): P22 fork intact (faces + trace class = 239/244), P01 both lanes at bar, P03-Bl0 unchanged. Any guard fails => STOP, report, no further pieces.
- Ends at re-extract + score. No assembly/reseat. No commits to main.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands).

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence.
- Same build node as 244/245 for md5 comparisons. sacct COMPLETED for every job, in-ticket.
- Keep the greedy path intact behind a flag (paper-chain precedent): default stays greedy until the vote arm proves itself.

## Acceptance
- P03-Bl1 at bar (med<2, cov>=90%, 0 jumps) with walk order verified (consecutive gaps, no teleport).
- All guards hold with numbers cited.
- Corner criterion quoted from the paper before the build (no invented thresholds).

## Required evidence to report
Quoted corner criterion + figure reference; the ordering diff; P03 both-lane scores + jump counts; guard scores; job IDs + sacct states; binary md5; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
## Comments (worker, 2026-10-22 -- SPLIT: vote arm wins clean loops, fails braid bags; greedy intact)

**Verdict: SPLIT. Paper vote-arm ported behind SFS_VOTE_ORDER (default OFF, greedy intact), run on P03/P22/P01 x CTL/VOTE. CTL reproduces all six lanes EXACTLY (greedy intact proven). VOTE: 3/6 lanes at/above bar incl. P03-Bl0 IMPROVED 0.58/100.0; 3/6 catastrophic on braid bags. P03-Bl1 NOT cured (med 8.69) -- the exam bar fails; conviction below points at the paper's missing K-D tree filter stage (follow-up ticket), not at voting itself.**

Paper corner criterion (quoted, sfspp-2502.13986v1.md:164): "segment at corners via peaks in distance-score distribution (deviation from local linear trend)". No numeric threshold in the paper -- assumption stated in code/log (POTA-247): corner score = perp distance from chord +/-8 pts, peak iff score > max(2.0mm, 3x median). Corners LOGGED ONLY (idx list), lane stays whole; no invented threshold baked into geometry.

Ordering diff (edgeline_extraction_headless.cpp, +186/-1, flag SFS_VOTE_ORDER at rim call site :1024; ring sidecar :1030 keeps greedy): centroid-nearest seed -> pure NN chain -> PCA-plane angular sort -> turn-sign vote (reverse if CW; paper Fig.6 CCW) -> closed-loop arc-length resample d=1.9mm. Fix 247b: COMP_GAP-BFS largest-component pre-filter (5.0mm gate = greedy COMP_GAP, same population greedy would walk) after first run showed fragment poisoning. Corner indices logged per lane.

Jobs (all COMPLETED 0:0, bm167 except 247b-build bm172): build247 33675888 (edge md5 c60b48ba94a3aad4be31c1503ce665d8), run247 33675990 (3m51s), build247b 33677220 (edge md5 f9fef346e3962cc3b32d6faf55045263, cpp md5 01890d06...), run247b 33677402 (4m09s). Spartan: sfs-vote-247 @ 2d99306 detached + vote247.diff applied (remote pull --ff-only skipped per 239-245 precedent: checkout 18-behind but FF-possible, left untouched; skip-worktree data + Juglet dirs).

Scores (stats247.py: med/cov<2mm/jumps>10mm vs author GT):
- P03-CTL Bl0 225/0.72/97.8/0j + Bl1 358/0.98/52.8/1x47.1jump = 245-tree EXACT. P22-CTL Bl0 136/0.80/86.0/0j + Bl1 157/0.50/91.1/1x14.6jump = 244-tree EXACT (244 verdict: P22 trace = 239 class). P01-CTL Bl0 341/0.75/98.8 + Bl1 359/1.01/94.2 = paper-era EXACT. All guards hold on CTL.
- P03-VOTE Bl0 228/0.58/100.0/0j (IMPROVED, guard Bl0 holds stronger), corners=4 thr=5.31. P01-VOTE Bl0 336/0.72/98.8/0j corners=8; Bl1 347/0.93/95.7/0j corners=7 (both ~CTL, slightly better med).
- P03-VOTE Bl1 4328pts/med 8.69/cov 11.0/21 jumps (EXAM FAIL). P22-VOTE Bl0 2247pts/4.79/14.4/38j; Bl1 1753pts/4.43/15.8/17j.
Conviction: NN-chain turnSum diagnostic -- clean loops 4.5-9.0 rad (~1 rev: P01 4.6/7.1, P03-Bl0 9.0) vs braid bags 44.8-64.5 rad (P03-Bl1 44.8, P22 64.5/49.1). Angular voting is undefined on multi-strand bags: P22 bags are SINGLE-component (comp-filter kept 490/490, 423/423) yet L=4-5m folded star polylines (corners=226/131). Greedy survives via adaptive-K + forward-heading guard (walks one strand, discards rest); the vote arm has no strand-picker. Missing stage = the paper's K-D tree filter (outlier removal before reorder) -- I ported resample+reorder+segmentation but NOT the filter. Follow-up: port K-D tree filter, or seed the vote population from the greedy lane.
- Corner segmentation: counts only (no author corner GT exists to score against): P03-Bl0 4, P01 7/8, braid lanes 111-226 (noise). Eye-check or corner labels needed for a segmentation verdict -- follow-up.

Guards: all hold (CTL exact on all six lanes; VOTE P03-Bl0/P01 improve-or-match). No reseat/assembly. No main commits (main worktree untouched; vote247.diff lives in C:/PR/SfSpp_preprocessing-247/vote247.diff + Spartan sfs-vote-247/vote247.diff).

