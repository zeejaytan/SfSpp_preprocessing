# Pipe exclusion: a boundary loop with surface inside it is a pipe, not an edge

GOAL: THE FINDER STOPS REPORTING PIPES AS FRACTURE EDGES.

**Answers:** E1

**Blocked by:** 166 (loop1 = 247e hole in MAIN sheet, flake hovering beside it; FAR rings it; user agrees it is a pipe -- surface goes down along it) + 155 (code sites).

**Status:** results-in

**User's rule (verbatim):** it is a hole in the sense of a pipe -- there is still surface going down along that hole. Exclude the pipe as edge.

I.e. a true fracture edge is a boundary with AIR beyond it; a pipe rim is a boundary with SURFACE beyond it (the pipe walls descending inside the loop). The test for each boundary loop: does the loop enclose further surface (pipe -- exclude from edge candidacy) or open onto air (true edge -- keep)? Operationalize on the sheet cloud (depth of points inside the loop footprint below the rim plane, interior-point count, or equivalent) -- worker's choice with justification.

**What to deliver:** (a) CONFIRM pipe geometry: depth profile inside loop1 (surface descending how far? pipe walls present?). (b) RULE: pipe-exclusion in the worktree variant (BoundaryEstimation output filtered, or sheet pre-masked); run both pots; 98-gate both. Bar: Pot A cure kept (pairs ~= 155) AND C01 false loop gone with rim kept (at-or-better-than fresh 5.61/22.9). (c) If the loop interior holds no surface (not a pipe), negative with the depth numbers.

**Starting position:** 166 Comments (loops, flake, distances, scripts); 155 Comments (worktree + build); 160/162 Comments (labels, gate scripts). New scratch pota167_repro/; renders artifacts/pota167/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-166 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] pipe depth profile inside loop1 (surface descending? -- NO: through-hole, see Comments)
- [ ] pipe-exclusion rule built + both pots run + gated -- NOT BUILT (negative path, rule (c))
- [x] Verdict + render paths
## Comments (worker, 2026-10-20 -- NEGATIVE: loop1 is a through-hole, not a pipe; nothing built)

VERDICT: negative per rule (c). Loop1 (247e MAIN-sheet hole, perim 102mm) has NO attached descending surface: the rim neighborhood is flat, the nearest below-rim surface is a detached hovering flake (separate component, min gap 5.46mm), and the deep surface inside the footprint is the far wall seen through the hole (geodesically >=39 edges around the hole, not down it). Per the ticket's constraint ("build only if surface descends inside the loop"), no variant was built, both-pots run omitted by entailment, worktree never entered.

### Depth profile inside loop1 (gate frame, DS mesh temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj)

- Rim: 247 edges, all MAIN-sheet; centroid [22.95,54.54,36.39]; best-fit plane normal [-0.437,-0.895,-0.091], singvals [151.3,132.5,16.0] (planar); rim relief min -2.86 / p10 -1.28 / med +0.25 / p90 +1.16 / max +1.54; mean in-plane radius 12.75mm.
- MAIN verts inside loop footprint (point-in-polygon on rim plane): 274/11263; signed depth min -22.22 / p10 -20.36 / med -16.58 / p90 +0.51 / max +1.48. Radial: r[0,4) n=8 med -19.96; [4,8) n=42 med -19.14; [8,12) n=96 med -18.11; [12,20) n=128 med -0.21 (bimodal: rim-notch verts + deep far-wall window, nothing graded between).
- Rim-adjacent faces (244, the single ring touching loop1): centroid depths min -2.62 / p10 -1.23 / med +0.29 / p90 +1.28 / max +1.49 -- flat at rim-relief scale, NO funnel start. (A 102mm-perimeter pipe throat would dive its first ring; it does not.)
- Flake (separate 592v component, the 166 cover): 290/592 verts inside footprint, depths med -13.52 range [-17.64,-6.37]; flake overall med -12.51 range [-18.58,-5.86]; flake-to-rim min 5.46 / med 12.07mm -- hovering cover, detached, not walls.
- Attachment (BFS over main-mesh edges from the 247 rim verts): deep set (depth<-10, n=1243) reached at graph-dist min 39 / p10 43 / med 53 edges -- the deep surface is reached only by travelling around the hole, never down from it. A pipe would attach within a few edges.
- All 120 interior verts at rim level (|depth|<3) are rim-concavity verts (gap-to-rim max 0.56mm, zero non-rim) -- no sheet at rim level spans the hole. Clean through-opening.
- Under-hole column eye-check: cross-section slab shows outer sheet continuing smoothly past the rim on both sides, air below the rim, then flake + far-wall layers at -11..-22mm (see render).

### Corollary for the finder (why pipe-exclusion would not cure C01 even if built)

- A naive footprint-interior-count test WOULD fire (274 main + 290 flake verts inside) but on detached surface (far wall + hovering cover), not walls -- the connectivity-aware form of the user's rule correctly does NOT fire.
- And the target is not loop1 anyway: the false loop rings OUTSIDE the hole on intact sheet -- 90/91 FAR dots outside the footprint (med 3.21mm off-rim), only 1/91 inside. The extraction walk loop parallels the hole; it is not the hole boundary. Excluding loop1 from candidacy leaves the walk that makes the false loop untouched.
- Banked context (cited, not rerun -- negative landing needs no new numbers): 160 Pot A BASE->VAR Bl_0 pairs P01 193->191, P02 727->79, P03 485->117, P04 242->101, P05 326->55, P06 144->105, P07 64->37, P08 61->16; C01 BASE 5.61/22.9% vs VAR 5.96/1.3%.

### Renders (eye-checked)

- artifacts/pota167/p167_section.png -- left: cross-section slab |W|<2.5mm (U vs signed depth: rim X at ~0, outer sheet continuous past it, detached flake blue + far wall orange at -11..-22); right: top-down along rim normal (rim loop red, flake blue + interior orange inside, FAR red-x ring OUTSIDE the loop on surrounding sheet).

### Scripts + data

- .scratch/pota167_repro/p167_depth.py (loops/components/plane/footprint/depths), p167_section.py (renders + gaps), p167_attach.py (BFS attachment + notch check); .scratch/pota167_repro/p167_depth.npz.

### Discipline

- COMMIT NOTHING; tickets 39-166 untouched (read-only); relay worktree sfs_cure_1c6a8f9 never entered (byte-identical by non-contact); no Slurm submitted -- sacct has nothing to record (all laptop-side, system python numpy+scipy+matplotlib+PIL, no env change); same-binary ORIG control N/A (no variant run to void).
- LIMITATION: Spartan SSH key rejected server-side (publickey denied although client offers the key; user zhuojiat) -- the 166 open question (does the hole pre-date decimation / full-res mesh check) could not be run. DS-mesh connectivity verdict is unaffected: a 102mm-perimeter pipe throat survives any reasonable decimation (the 25mm flake did), and no attached wall stub exists at any scale.
- Heads-up for the lead: the pipe idea is exhausted in both forms (footprint-count fires on the wrong surface; connectivity-aware does not fire); the false loop is extra-hole sheet (162's two-parallel-loops picture holds -- the hole is the cause as a data gap attracting the extractor, but the loop to kill lives beside it, not on it).
