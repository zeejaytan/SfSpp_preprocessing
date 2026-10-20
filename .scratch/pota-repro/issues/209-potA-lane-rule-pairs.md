# 209 - Pot A all pieces: lane-rule pairs (208 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins
Needs-eye: user witnesses the 8 staged pairs in the viewer before this closes.

## Goal
User request (2026-10-20): for every Pot A piece (8), stage the lane-rule pair
from 2026-10-17 -- OUR trace on OUR mesh beside AUTHOR trace on OUR mesh
(same mesh, so any difference is purely the trace). Our trace = the trace
actually seated in the 208 fresh arm (bundle v0); author trace = ORIG author
trace; mesh = 208 fresh mesh. Render recipe + conventions per ticket 203
(p199_render.py pattern, same mesh + same camera within a piece, mm units,
mesh-proximity check per loop, no substitution/faking, name any undrawable
piece in Comments). Then stage the 8 pairs in the visual-qa viewer per
docs/agents/visual-qa.md (via visual-qa-helper) and run its gates.

## Boundary
Inputs read-only: 208 bundle v0 breaklines (Spartan pota208_bundle_v0/SfS_pp;
see 208 Comments for paths), ORIG author traces (same source as 208's ORIG
arm), 208 fresh meshes (Spartan pota208_pipe/ Pot_A_Piece_*_Surface_*).
Fetch small samples only; render laptop-side under artifacts/pota209/
(untracked). Do NOT touch tracked files except this ticket. COMMIT NOTHING.
Verify Bl-slot identities from the bundle manifests (fresh Bl_0 vs author) --
do not assume slot contents from memory. Do not pop the 2 pre-E2E Spartan
stashes; do not disturb the live Spartan main checkout.

## Constraints
Bl0/Bl1 naming: resolve from files on disk (see Boundary), state the
resolution in Comments. If a trace or mesh is missing, stage the pieces that
exist and NAME the missing one -- no substitution. Read 203 + 208 Comments
first for exact paths and conventions. Standing submit sign-off covers any
needed Solute/queue work; batch per AGENTS.md (held allocation for iterative
checks, sbatch only for long unattended runs, laptop-side poll per sbatch).

## Acceptance
8 lane-rule pairs staged in the viewer, gates green (or failures named with
lines verbatim), each pair eye-checked by worker with a per-piece line: loop
point counts (ours vs author), mesh-proximity med/max per loop, and whether
the two traces coincide / sit offset / diverge (and where on the rim).
Needs-eye witnessed by user before close.

## Required evidence
Comments: viewer pair names/paths + source artifact per trace (md5 where
available) + Bl-slot resolution + proximity numbers + eye-check per pair +
any piece unstaged and why. Final report: same, self-contained, plus the
one-line answer the user asked for -- do our and author traces ride the same
rim on our mesh, or sit offset (mesh-shift evidence)?

## Comments (worker)
