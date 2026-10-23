Status: done

# Ticket 240: bisect edge-source change that broke P03-Bl0

Answers: E1 — the piece-3 Bl0 walk regression 0.70/99.1 -> 2.43/45.5.
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

## Comments (worker, 2026-10-22 -- bisect COMPLETE, NO edge hunk flips: mesh-verdict)

**Verdict: NO single edge hunk (and no combination relevant to 239) reproduces the flip. The e962159..885f433 edge diff is a proven binary no-op; the flip carrier is upstream (mesh stage). Mesh-verdict per brief.**

**STEP 1 -- hunk list (git diff e962159..885f433 -- edgeline_extraction_headless.cpp: +124/-0, 4 hunks, ALL inside inactive #ifdef guards):**
- H1 ARM-B radius (~L780-792): #ifdef POTA218_ARM_B adaptive 3x-spacing/clamp-1.5-8mm vs #else fixed 4mm.
- H2 ARM-A/C kd-tree setup (~L817-823): #if defined(A)||defined(C) neighbor-field decls only.
- H3 ARM-A surround (~L836-893) + ARM-C normal gate (~L894-920) vs #else plain push-through.
- H4 diagnostic per-face boundary_Sx save (triple-guarded) + arm stdout (single-guarded).
- No-flag logic identical to e962159 by reading (238 already verified); proven at binary level below.

**STEP 2 -- variants (fresh Spartan clone sfs-bisect-240 @ 6479260 = origin/main both sides, no divergence; single build job, same node):**
- V0 = e962159 source (21fbb6b5), no flags (the 214 control).
- VA/VB/VC = 885f433 source (89ab05b1) + -DPOTA218_ARM_A/B/C respectively (each arm alone-first; other arms' code preprocessor-inert = absent).
- VALL = 885f433 source, no flags (= 239 config). V0R = V0 binary re-run (determinism check).
- P03 trees staged 6x from pota239_paper_P03 (mesh held constant); same Point.pcd as 214 (md5 4927bd33 both sides).

**Binary md5s (build 33648714 sacct COMPLETED 0:0, spartan-bm175):**
- V0 = dc472b0e87c934b6c487ff8637209864 == VALL == 239 reference dc472b0e BYTE-IDENTICAL. The 124-line diff compiles to zero bytes.
- VA = 75bc3809 / VB = ad513838 / VC = 822f4b1d -- all three EXACTLY 218's arm md5s (reproduced).

**Per-variant P03-Bl0 vs author (209 ruler, trace 33648725 COMPLETED 0:0; 214 ref 0.70/99.1 AGREE, 239 ref 2.43/45.5 MIXED 1x20.8mm):**
- V0: 275pts 2.43/45.45 1x20.8mm MIXED (= 239 EXACTLY). VALL: identical. V0R: identical (deterministic).
- VA: 261pts 2.28/47.1 1x18.6mm (still face-cutting). VB: 444pts 15.43/31.3, 3 jumps (catastrophic, same direction as P16). VC: 29pts 8.12/37.9 (lane collapsed, same as P16).
- No arm removes the cut; no arm approaches 0.70/99.1. Active-arm combos not run: 239 used no flags, and no-flag VALL already reproduces the degraded lane exactly, so code combinations cannot explain the 214->239 delta.
- Bl1: V0/VALL/V0R 348pts 0.86/95.4 (= 239); VA 332pts 0.96/96.1; VB 1118pts 18.58/22.4; VC 144pts 30.39/19.4.

**Mesh-verdict evidence:** V0-good-source on 239's tree gives the degraded lane, bit-deterministically; sampled PCD inputs bit-identical to 214's; therefore the flip entered via mesh-stage outputs (paper-splitter surfaces from the 237 merge, SFS_PAPER_CHAIN=1 in 239's mesh_P03.log vs old splitter in 214). 214's mesh-stage files are gone (no pota214_P03 tree survives) so the mesh-side diff could not be diffed here -- follow-up: re-run 214-mesh vs paper-mesh on the same PCD and compare Temp/Data surfaces. No lane render: no flipping variant exists (239 precedent: headless, no render path; 214's p214_P03_overlay.png is the clean reference).

**Spartan leftovers (all mine, sibling-safe):** sfs-bisect-240/ (clone @6479260, 5 build dirs, build240/trace240 sbatches + logs), pota240_P03_{V0,VA,VB,VC,VALL,V0R}/, score240_{V0,VA,VB,VC,VALL,V0R}/ + ev240_* + pota240_evidence.tgz. Main checkout, 214/218/237/238/239 dirs: untouched. Laptop: this ticket + artifacts/pota240/ev240_* (6 gate CSVs, 6 score logs, bin md5s, build + trace logs). No main commits.
## Lead verdict (2026-10-22)
ACCEPT mesh-verdict. R6: both jobs COMPLETED; evidence on disk; V0==VALL==dc472b0e byte-identical (diff compiles to zero bytes -- all hunks in inactive ifdefs); V0 reproduces 239 EXACTLY (2.43/45.45, 20.8mm jump); inputs md5-identical to 214's. No edge hunk flips; VB catastrophic/VC collapsed (218 arms worse, stay off). Flip entered via mesh-stage outputs. Follow-up 241: rebuild 214-era mesh, compare surfaces.

## Required evidence to report
Hunk list from the diff; per-variant table (hunk, md5, Bl0 med/cov, cut yes/no); the flipping variant's lane render; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35 via send_message. Your parent agent id is session-1ca83938-6e86-4736-bb84-2f4e58807e35.
