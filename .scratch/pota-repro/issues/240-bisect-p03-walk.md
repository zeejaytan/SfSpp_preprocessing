Status: ready-for-agent

# Ticket 240: bisect edge-source change that broke P03-Bl0

Answers: E1 (P03-Bl0 walk regression 0.70/99.1 -> 2.43/45.5).
Needs-eye: no.

## Goal
Find which change in the edge code flipped P03-Bl0 from clean to face-cutting, by applying the changes one at a time. Last-known-good edge source: commit e962159 (file md5 21fbb6b5, the 212/213-cure source 214 used). Current: commit 885f433 (file md5 89ab05b1, the 218-ifdef source 239 uses). Same P03 inputs throughout (214 sampled PCDs, aggregate a05b1445 -- reused, not resampled).

## Boundary
- P03 ONLY. No other piece, no seating, no assembly.
- Hold the mesh constant (paper v3 mesh d72979aa, the 239 mesh) and vary ONLY edge-code hunks. If no single edge hunk reproduces the flip, report that (mesh becomes suspect) -- do not expand scope without lead say-so.
- Work in a fresh Spartan copy. No commits to main, no repo file changes outside the experiment copy. Laptop tree: ticket file only.

## Constraints
- STEP 1: diff the edge file e962159..885f433, list the hunks (functional changes, not whitespace). STEP 2: starting from the GOOD source, apply hunks ONE AT A TIME (cumulative ladder is acceptable only after testing each alone: alone-first, then cumulative to confirm).
- Each variant: rebuild edge binary in container, trace P03, score Bl0 vs author (med/cov, same ruler as 239). Record per-variant: hunk applied, binary md5, Bl0 med/cov, and whether the interior cut appears (render the lane on S0 for the flipping variant).
- If the flip needs a hunk COMBINATION (no single hunk does it), say so with the minimal combination.
- Spartan: fresh clone of origin/main, pull --ff-only; STOP and report on divergence.

## Acceptance
- The flipping hunk (or minimal combination, or mesh-verdict) identified with per-variant scores. Sacct COMPLETED for every build/trace job, binary md5s cited. No main commits.

## Required evidence to report
Hunk list from the diff; per-variant table (hunk, md5, Bl0 med/cov, cut yes/no); the flipping variant's lane render; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35 via send_message. Your parent agent id is session-1ca83938-6e86-4736-bb84-2f4e58807e35.
