# Sampled-dot overlay — paint the walker's input bag on the sherd

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** (1) Our 343-dot unordered input cloud (the walker's input for C01 S0) painted on the C01 mesh, colour-coded by visit order (walk sequence position), with the file-order start dot marked. (2) A verdict on whether the author's bundle contains their raw pre-walk dot bag; if yes, paint it the same way beside ours; if no, say exactly what the author's bundle holds instead (ordered loops only? surface samples?) with file paths.

**Answers:** E1

**Blocked by:** 99 (input cloud identified) + 100 (mesh overlay recipe) + 101 (hotspot map)

**Status:** results-in

**Starting position:** C01 S0 boundary input (343-pt per edgeline_stage.log) + mesh + ORIG Bl_0. Login-node numpy/matplotlib only — no Slurm, no E2E, no gate. New scratch pota102_repro/; renders under laptop artifacts/pota102/.

**Rules:** read-only (zero ORIG points, bundles md5-guarded); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); author-side hunt is evidence-only listing (paths + counts), no copying of author data into new files beyond the render.

- [ ] Our input dots on mesh, visit-order coloured, start marked
- [ ] Author raw-bag verdict (paths + counts or absence with evidence)

## Comments (worker, 2026-10-19)

REPLAY EXACT — all pipe checkpoints hit in login-node numpy (no Slurm):
S0 rows=11165 -> SOR(MeanK=50, std=9) kept 11165/removed 0 -> spacing 1.07761 r_b=6.46568
-> PCL-1.9.1 BoundaryEstimation float32 port 364 (zero max-gap margins within 1e-3 of 0.6pi,
so the set is robust) -> K=1 map onto unclustered.ply (2342 verts) 364, float64/float32 maps
identical, no near-tie nearest -> ROR 343 kept / 21 removed -> walk K=34 greedy 93/343
(cov 0.271137 < 0.40 fires SFS-T13) -> final 237 pushes, 4 jumps at seq-pos
(92,93) (132,133) (170,171) (223,224).

Two pipe-faithful details that a naive port gets wrong (both verified against
PCL 1.9.1 sources + edgeline_stage.log line 21 "343 kept / 21 removed of 364"):
(1) ROR dense branch keeps iff the 7th-nearest d2 <= r2 (nearestKSearch k=min+1=7),
i.e. keep count>=7, NOT keep count>=6. Naive >=6 keeps 348.
(2) Walk visited-set is coordinate-keyed (tobytes of float32 triple), matching C++
pointExistsInCLoud float-== semantics: the 343-bag holds only 236 distinct coords
(107 dup slots); t==1 double-taps idx1 which duplicates idx0, hence 237 pushes.
Global-scan break on all-masked (C++ best<0) also required.
Dead end logged: ASCII-PCD %.8g round-trip of the SOR output is lossless (maxdx=0),
values already coarse — not the 343/348 difference.

Deliverable (1): artifacts/pota102/p102_dots_overlay.png — C01 mesh (11875 verts)
+ our 343 dots in local frame (dot-to-mesh standoff med 0.68mm max 1.70mm),
viridis by walk seq-pos 0..236 (dup slots share their coord's pos), start
(input idx 0 = seq 0, [55.69,41.01,436.28]) red star + zoom panel. End dot (seq 236)
at [-11.91,62.32,406.89].
Scratch: /data/gpfs/projects/punim2657/pota102_repro/ (p102_replay.py 6c46d6f1,
p102_render.py 9be45518, p102_walk.npz 4405411d input/visit/seq/greedy_n/jumps,
p102_numbers.txt, p102_boundary364.npy, p102_improved364.npy). COMMIT NOTHING done.

Deliverable (2) author raw-bag verdict: ABSENT. Author bundle
prep/pota39_C/Dataset/ holds per piece only: Breaklines/ ordered loops
(Piece_01 Bl_0 402x6 xyz+ply+pcd, Bl_1 92x6), Point/ dense clouds (~50MB pcd each),
Surfaces/, Mesh/, Axes/ (empty). No unordered pre-walk boundary bag, no walk-input
or intermediate files (Temp/Temp_edge keeps last piece only). Note author's Bl_0 is
402 long vs our walk's 237 — ordered loop, not the 343-bag.

