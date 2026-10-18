# Void map — where the bag has no dots, and which input step owns each gap

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 118 (presplit shatters the cleaned bag too: 35 islands; bag lacks chainable structure at honest stepping) + 110 (same on filtered bag) + 112 (REFUSAL at bridges) + 111 (lip not globally under-sampled, but gap tail max 12.43mm) + 103 (cleaned bag, gate 4.68)

**Status:** results-in

**What to deliver:** map every structural break. Take 118's 35 presplit components on the 103 cleaned bag: seat each component's end dots on ORIG Bl_0, list the ORIG index ranges with ZERO bag coverage (true voids — no dots at honest stepping range), and for each void read the mesh context: segmentation label (Surface_0/1?), boundary-test distance, fold/constriction proximity (99's (38,191)/(39,401)?), scan-border proximity, local mesh edge fineness. Then name an OWNER per void: which input step failed to produce dots there (segmentation cut it away? boundary test blind? ROR deleted? snap dragged off? mesh too coarse?). Distinguish VOID (no dots where the true arc passes) from EATEN-BRIDGE (dots present but consumed — 112's pattern) per break. Success bar: every one of the 35 breaks classified (void vs eaten, void extents in ORIG indices, owner named with file+line) AND at least one void-owning step with a stated one-variable fix direction. If all breaks turn out eaten-bridges with zero true voids, say so — that kills the structural story and re-points at the walker.

**Starting position:** pota103/110/112/118_repro/ (cleaned bag, presplit components, stall freezes, checkpoints), C01 fragment mesh + segmentation outputs. Login-node numpy only — no Slurm, no E2E. New scratch pota119_repro/; render under laptop artifacts/pota119/ (ORIG arc coloured by coverage: dotted vs void spans, owners labelled).

**Rules:** control reproduces 118-presplit first (35 comps, max 27, emit 21, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; classify-first, fix-direction second.

- [x] Presplit reproduced + every break seated on ORIG
- [x] Void-vs-eaten classification with extents + mesh context per void
- [x] Owner named per void (file+line) + fix direction
- [x] Verdict + coverage render

## Comments (119 worker, 2026-10-18, login-node numpy only, COMMIT NOTHING)

CONTROL GREEN (118-presplit reproduced to 2dp, `.scratch/pota119_repro/p119_run.py`): 35 comps, sizes=[27,24,22,17,16,16,15,15,12,11,8,8,7,7,6,6,6,5,5,5,4,4,4,3,3,2,2,2,2,1x6], comp-25 (n=24) walks 21, stall dots identical to 118. Bag = 103 cleaned 270 (`pota115_staging/inputs/p113_guarded.npz`); ORIG = Bl_0 211 (gate-evidence only, zero ORIG points copied).

FRAME NOTE: laptop `Temp/Data/Pot_A` is the WRONG frame (bag->cloud med 23.7mm; its Mesh.obj 100064 verts watertight vs 112's 11875-vert mesh). All mesh context below is Spartan `pota39_repro/prep/pota39_C/Temp/Data/Pot_C` (bag->cloud med 0.0000, Mesh.obj 11875 verts/23114 faces, unclustered.ply 2343 pts) via read-only login-node probe (`p119_probe.py`, /tmp cleaned after).

7 TRUE VOID SPANS (Dob>5mm, ORIG coverage 179/211). Per-void mesh context (local frame; dMesh = dist to mesh; dBorder = dist to nearest of 636 scan-border verts; edges = mesh edges within 10mm; cloud = unclustered.ply counts within 5/10mm; S0/S1 = Surface_0/1 dist):

- ORIG[9..13] len5 maxgap6.0 | mid O11 [-20.6,-13.2,397.5] dMesh0.37 dBorder36.5 edges med1.470/p90 2.146 cloud24/67 bag0 S0 2.69 S1 31.6 nearBag c5/c0 (5.5-7.6mm) stall18.0mm -> break00 VOID
- ORIG[25] maxgap5.7 | mid O25 [-27.7,5.4,383.7] dMesh0.44 dBorder45.2 edges med1.853/p90 3.095 cloud17/62 bag0 S0 3.45 nearBag c11/c6/c31 (5.7-7.7mm) stall6.8mm -> break02 VOID (stall dot dies ONE span before this void)
- ORIG[32..50] len19 maxgap6.8 | mid O41 [-29.9,27.9,385.9] dMesh0.66 dBorder46.2 edges med1.774/p90 2.784 cloud18/63 bag0 S0 3.09 nearest cluster_1 @1.7mm nearBag c4/c3/c0 (5.8-7.1mm) stall27.2mm -> break03 VOID. Swallows fold-99 feet ORIG 38 (Dob6.0) and 39 (Dob6.0): the fold feet are void, not the cause.
- ORIG[96..97] maxgap6.3 | mid O96 [38.9,60.0,422.1] dMesh0.51 dBorder57.0 edges med1.719/p90 2.813 cloud25/59 bag0 S0 0.76 nearBag c33/c5/c25 (6.3-8.1mm) stall94.7mm -> break16 VOID
- ORIG[160..161] maxgap5.8 | mid O160 [64.2,-24.8,404.1] dMesh0.66 dBorder78.3 edges med1.587/p90 2.454 cloud23/71 bag0 S0 2.97 nearBag c1/c21/c2 (5.8-7.0mm) stall96.2mm -> break27 VOID
- ORIG[164..165] maxgap5.3 | mid O164 [60.8,-30.0,400.8] dMesh0.60 dBorder78.3 edges med1.494/p90 2.291 cloud29/80 bag0 S0 4.42 nearBag c2/c3/c15 (5.3-5.7mm) stall94.2mm -> break28 VOID
- ORIG[173] maxgap5.6 | mid O173 [52.3,-38.5,390.7] dMesh0.08 dBorder79.7 edges med1.535/p90 2.788 cloud21/91 bag0 S0 5.04 nearBag c2/c16/c17 (5.6mm) stall88.8mm -> break29 VOID

BREAKS (median-ordered intervals tile the arc; each void assigned once by midpoint; `p119_voidmap.txt`): VOID=7 (breaks 00,02,03,16,27,28,29 with extents above), EATEN-BRIDGE=28 (no void midpoint in interval; threshold/walk cut on dotted arc). Wrap break34 comp25->comp6 EATEN (tail+head maxgap 2.7mm). 112-CONSISTENT: stall region ORIG[21..24] Dob=[0.5,1.4,3.2,5.0] covered -> the stall break itself (break01, EATEN) is 112's REFUSAL pattern; the walk died one span before true void [25].

OWNER (all 7 voids, one pattern): pre-filter cloud holds 17-29 pts within 5mm of every void mid, post-filter bag holds 0 within 5mm (nearest 5.3-6.9mm) -> points existed at segmentation input and were deleted downstream. Mesh rules OUT scan/mesh/snap causes: arc meshed (dMesh<=0.66), edges normal fineness (med 1.47-1.85 vs 112 stall 1.782), voids interior (dBorder 36-80mm, not scan border), S0 surface present <=5mm. Primary owner = ROR deletion: `original_nurbs_preprocessing/boundary_filter.cpp:10-33` (RadiusOutlierRemoval) called from `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:990-992`, `outlier_radius_mm=max(2,min(20,g_boundary_radius_mm*8/6))` (:986-989), `min_neighbors=6` (:991-993). Sparse lip-strip points with <6 neighbours inside the radius match the void signature (gap widths 5.3-6.8mm ~ outlier-radius scale). Residual ambiguity ROR-vs-boundary-radius-test (:904) stated, not hidden: both live in the same filter block; the fix rerun below separates them.

FIX DIRECTION (one variable): relax `min_neighbors` 6->3 in the headless ROR call for C01 only, rerun edgeline-to-bag, recount the 7 spans (predict shrink: cloud holds 17-29 pts/5mm at each void). Alternative second-chance: re-admit ROR rejects within 5mm of Surface_0 AND <=2x radius of a surviving dot, then re-presplit and recount 35->?. Classify-first held: no code changed.

VERDICT: structural story CONFIRMED and bounded — 7 true voids (incl. 19-span [32..50]) can never be walked at honest 5mm stepping, while 28/35 breaks are eaten-bridges (walker-side cuts on dotted arc, incl. 112's stall). 99's folds do not explain any void (feet 38/39 sit inside void [32..50]). Next: ROR-relax rerun, then re-seat.

Render: `artifacts/pota119/p119_voidmap.png` (PCA-2D: bag by comp, ORIG covered vs void, stall star, void labels). Scratch: `.scratch/pota119_repro/` (run/voidmap/context/probe/render scripts + txt + npz).
