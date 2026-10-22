Status: ready-for-agent

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
