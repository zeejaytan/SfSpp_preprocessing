Status: done

# Ticket 241: mesh-stage bisection for P03-Bl0 flip

Answers: E1 — the piece-3 Bl0 walk regression; 240 cleared the edge code, the mesh stage stands.
Needs-eye: no.

## Goal
Find what differs in the mesh-stage OUTPUTS (faces S0/S1) between the 214 era (P03-Bl0 clean, 0.70/99.1) and now (2.43/45.5 with interior cut), on IDENTICAL inputs (214 sampled P03 Point.pcd, md5 4927bd33 -- verified same in 240; reuse, do not resample).

## Boundary
- P03 ONLY. No tracing beyond a single confirmation trace per mesh variant; no seating.
- 214-era mesh = the 212/213-cure mesh source. It lives on the pristine-splitwalk cure line (branch off b1ed4d1; 213 landed there). If the branch is gone from origin, STOP and report (do not reconstruct from memory).
- Current mesh = paper v3 (d72979aa, origin/main). Rebuild both in containers on the same node (note -march=native lesson from 239: same node or compare behavior, not md5).
- No commits to main. Laptop tree: ticket file only.

## Constraints
- Compare the S0 faces then vs now: extent, density, and specifically the cut region (around [28.9, -1.4, 501.8] where our Bl0 leaves the rim) and the top region the eye flagged. Measure: what exists in one S0 and not the other (holes? extra bleed? different boundary? different normals?).
- One confirmation trace per mesh variant with the SAME edge binary (dc472b0e) to close the loop: 214-mesh should trace clean-ish, paper-mesh should cut. If 214-mesh ALSO cuts, report that (inputs/edge interaction, not mesh).
- Spartan: fresh clones; pull --ff-only; STOP and report on divergence.

## Acceptance
- Named surface difference at/near the cut region (with numbers + render), confirmation traces both variants, jobs sacct COMPLETED, no main commits.

## Lead verdict (2026-10-22)
ACCEPT mesh-carries-flip. R6: jobs 33650346+33650610 COMPLETED; render eye-checked (dense OLD + rim-hugging lane vs sparse PAPER + cutting lane); OLD mesh bit-identical to 214 ref, PAPER to v3 ref; OLD-mesh trace clean 0.53/97.3, PAPER-mesh 2.43/45.5 exact. Named difference: paper splitter guts S0 to 6.3% density (106842->6693, cut-region 2391->129, clusters 7->61). Caveat recorded (P03-only context 52-pt delta, same verdict). Next: density-restore ticket.

## Required evidence to report
Both mesh sources (commit/branch) + binary notes; S0 then-vs-now comparison (numbers + render path); confirmation trace scores; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35 via send_message. Both mesh sources (commit/branch) + binary notes; S0 then-vs-now comparison (numbers + render path); confirmation trace scores; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35 via send_message. Your parent agent id is session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments (worker, 2026-10-22 -- BISECTION COMPLETE, mesh carries the flip)

**Verdict: the flip entered via the mesh stage. The paper splitter (237 merge) guts P03 S0 to 6.3% of its 214-era density and shatters the segmentation (7 -> 61 unclustered clusters); the same dc472b0e edge binary traces clean on 214-era mesh and cuts on paper mesh. Edge exonerated (240 already proved the edge diff a binary no-op); mesh convicted here.**

**Mesh sources (both verified in fresh clone sfs-mesh-241 @ 6479260 = laptop origin/main, no divergence):**
- OLD (214-era) = origin/pristine-splitwalk mesh (e962159 file md5 048904d01fc389cde429fa1ec43b4f1c) == live sfs-potD-214 source file md5. Branch exists on origin; no STOP needed.
- PAPER (current) = origin/main mesh (HEAD file md5 556ef97aacedddadd4df283ccff01d15).
- Live-checkout note: sfs_preprocessing main checkout behind (f4add97 vs 6479260) + documented skip-worktree live file; left untouched per 239/240 precedent, fresh clone used.

**Binaries (job 33650346 sacct COMPLETED 0:0, pinned spartan-bm175):**
- build-241OLD/MeshPreprocessingHeadless = de8effd08b9c9cbe1a4777bbc8840992 == 214 ref binary BYTE-IDENTICAL.
- build-241PAPER/MeshPreprocessingHeadless = d72979aaa0055885a4dc88bb51a172e7 == v3/239 ref BYTE-IDENTICAL.
- Edge binary reused for both traces: sfs-bisect-240/build-240V0/EdgeLineExtractionHeadless = dc472b0e87c934b6c487ff8637209864 == 239 ref (no rebuild needed, md5 re-verified in-run).

**Inputs (identical both variants, no resampling):** fresh P03 trees staged from canonical samples (Dataset_Input Point PCD md5 4927bd334d164d63e89922a507f6010e verified in-job + Mesh_DS.obj + Axis); OLD run `env POT_NAME` only (214 pattern), PAPER run full 239 env (SFS_PAPER_CHAIN=1 + RHO set + SINGLE_SHOT=1).

**S0 then-vs-now (rebuilt trees; REF = surviving 214/239 trees):**
- OLD S0 n=106842 vs REF214 S0 n=106894 (52 pts, 0.05%; bbox/z identical) -- rebuild reproduces 214 mesh. PAPER S0 n=6693 vs REF239 S0 n=6693 EXACT.
- S1: OLD 107267 vs REF214 107272; PAPER 10935 vs REF239 10935 EXACT.
- Extent is NOT the difference (bboxes match: x~[-28,48] y~[-14,89] z~[443,557] both). Density/holes are: cut-region [28.9,-1.4,501.8] occupancy n_lt10mm 2391 (OLD) -> 129 (PAPER), 18.5x; n_lt30mm 20679 -> 1228. Unclustered fragments 7 (OLD) -> 61 (PAPER).
- Top region: S0 z-range identical [443,557]; the loss is interior coverage, not a shifted boundary -- paper S0 is a sparse sieve over the same footprint (see render).

**Confirmation traces, same dc472b0e binary (job 33650610 COMPLETED 0:0, ran bm165 -- same-binary run, node only matters at build):**
- OLD-mesh Bl0: 225pts med 0.53 / cov 97.3%, 1 jump 10.7mm (CLEAN, no face cut). PAPER-mesh Bl0: 275pts 2.43/45.5, 1x20.8mm jump (= 240 V0/VALL EXACTLY, face-cutting).
- Bl1 controls: OLD 362pts 0.64/96.1; PAPER 348pts 0.86/95.4 (= 240 EXACT). S1 survives the paper sieve well enough to walk.
- Calibrator: surviving REF214 Bl0 under this scorer = 226pts 0.71/99.1 (matches 214 report 0.70/99.1: scorer valid). Rebuilt-OLD lane (225/0.53/97.3) is near- but not bit-clean vs 214 -- 52-pt S0 delta from P03-only tree context (214 ran 29 pieces/tree) and/or MST noise; same verdict (clean), approximate reproduction, stated not hidden.

**Render:** artifacts/pota241/p241_P03_S0_compare.png (top view: dense OLD S0 + rim-hugging cyan lane vs sparse red PAPER S0 + orange lane cutting interior off the blue author rim; cut star at (28.9,-1.4)); script render_p241.py; evidence .xyz/.pcd alongside.

**Spartan leftovers (all mine, sibling-safe):** sfs-mesh-241/ (clone @6479260, mesh_old_048904d0.cpp, build-241OLD/PAPER, build241/run241 sbatches + logs, stats241.py, bin241 md5s), pota241_P03_OLD/, pota241_P03_PAPER/ (trees + mesh/edge logs). 214/239/240 dirs untouched. Laptop: this ticket + artifacts/pota241/ (7 files). No main commits anywhere (git log HEAD still 6479260).

Completion sent to dispatch parent session-f43ebd6e-a4fd-4a68-ac04-ec71bfd81330 (ticket text names lead session-1ca83938; sent per live dispatch instruction).

