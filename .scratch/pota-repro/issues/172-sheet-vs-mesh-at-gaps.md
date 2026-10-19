# Sheet edge vs mesh boundary at the 13 gap stations

GOAL: SETTLE WHETHER THE MESH HAS SURFACE WHERE THE SHEET GOES SILENT.

**Answers:** E1

**Blocked by:** 169 (sheet shortfall 2.0-6.4mm at all 13 gap stations; sheet = 11165 cleaned samples, spacing 1.08mm), 168b (gap-station list + coverage plot artifacts/pota168b/).

**Status:** ready-for-agent

**User direction (2026-10-20):** the rendered mesh clearly shows surface at the gaps -- check the sheet against the mesh before claiming the scan is silent.

**What to deliver:** (a) At EACH of the 13 gap stations: distance from the nearest MESH boundary/triangles to the ORIG station vs the 169 sheet-sample distance -- per station verdict MESH-HAS-IT (mesh reaches <2mm where sheet stops short: re-sample fix viable) or MESH-MISSING (mesh also stops short: scan silence, honest). (b) Overlays eye-checkable in artifacts/pota172/ (sheet edge + mesh boundary + ORIG at gap stations). (c) If MESH-HAS-IT anywhere: name the stage that dropped the surface (cleanSamples sampling? piece segmentation clipping?) with file + line.

**Bar:** all 13 stations owned with numbers; sampling-drop stage named where applicable; renders eye-checked. No walk, no gate -- measurement only.

**Starting position:** 169 Comments (sheet numbers, repro scripts, gap ledger); 168b Comments (gap stations); 166 Comments (hole loop geometry, DS mesh path temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj). New scratch pota172_repro/; renders artifacts/pota172/.

**Rules:** dataset + mesh read-only; COMMIT NOTHING; tickets 39-171 read-only; Comments-only ticket edits; eye-check renders.

- [x] per-station mesh-vs-sheet distances + verdicts
- [x] stage that dropped the surface, named (where MESH-HAS-IT)
- [x] Verdict + render paths
\n## Comments (worker, 2026-10-20 -- laptop numpy only; COMMIT NOTHING)

**Verdict: 13/13 runs MESH-HAS-IT, 0 MESH-MISSING. The scan is NOT silent -- the DS mesh carries surface within 0.26mm of all 188 gap stations (med 0.021mm) where the sheet stops 0.76-5.20mm short. Re-sample fix viable at every gap.**

**0. Controls GREEN (reproduce-or-stop PASSED).** Mesh temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj 11875v/23114f asserted exact. Boundary census verbatim from p166: 636 boundary edges, loops [274,247,97,18] closed. Labels exact: NEAR 86 / MID 187 / FAR 91. Sheet KDTree reproduces p169_gapstations.csv bit-exact (max abs diff 0.000000 over 188 stations). T==TF gate frame throughout (R,t from Pot_C_Piece_1_T.txt). Point-to-triangle distances are exact Ericson-5.1.5 region logic, chunked over all 23114 faces (not a vertex proxy). No Slurm submitted -- sacct has nothing to record (precedent 162/163/168/169). Tickets 39-171 read-only; relay worktree never entered, no build, byte-identical by non-contact.

**1. Per-run mesh-vs-sheet (station -> nearest mesh TRIANGLE vs 169 sheet/fired; verdict line <2mm).**

| run | stations (n) | sheet min/med | mesh-surf min/med/max | mesh<2mm | verdict |
|-----|--------------|---------------|----------------------|----------|---------|
| R0 | 0..1 (2) | 2.70/2.78 | 0.020/0.047/0.075 | 2/2 | MESH-HAS-IT |
| R1 | 3..21 (19) | 2.26/2.97 | 0.002/0.024/0.163 | 19/19 | MESH-HAS-IT |
| R2 | 23..30 (8) | 2.61/2.91 | 0.001/0.008/0.037 | 8/8 | MESH-HAS-IT |
| R3 | 34..68 (35) | 1.51/2.79 | 0.001/0.027/0.262 | 35/35 | MESH-HAS-IT |
| R4 | 72..81 (10) | 2.05/3.14 | 0.002/0.029/0.131 | 10/10 | MESH-HAS-IT |
| R5 | 83..88 (6) | 2.05/2.62 | 0.002/0.013/0.055 | 6/6 | MESH-HAS-IT |
| R6 | 93..124 (32) | 0.76/3.32 | 0.000/0.029/0.227 | 32/32 | MESH-HAS-IT |
| R7 | 126..136 (11) | 2.25/2.76 | 0.000/0.008/0.085 | 11/11 | MESH-HAS-IT |
| R8 | 139..143 (5) | 2.24/3.06 | 0.001/0.005/0.044 | 5/5 | MESH-HAS-IT |
| R9 | 145..147 (3) | 2.15/2.47 | 0.001/0.001/0.048 | 3/3 | MESH-HAS-IT |
| R10 | 151..156 (6) | 2.09/3.15 | 0.001/0.020/0.087 | 6/6 | MESH-HAS-IT |
| R11 | 158..203 (46) | 1.59/3.67 | 0.000/0.015/0.155 | 46/46 | MESH-HAS-IT |
| R12 | 206..210 (5) | 2.90/3.48 | 0.002/0.008/0.140 | 5/5 | MESH-HAS-IT |

Overall over 188 stations: mesh-surf min 0.000 / med 0.021 / max 0.262; frac <1mm 1.000, <2mm 1.000, <5mm 1.000. Nearest mesh BOUNDARY segment sits 36.2-80.0mm away (med 53.7) at every station -- the stations are mid-sheet, the 4 boundary loops are nowhere near, and the surface under the stations is interior main-sheet triangulation (not flake/crumb, which live >=36mm from ORIG per 166/168). Full per-station table (station,run,sheet_d,mesh_surf_d,mesh_bnd_d,verdict): .scratch/pota172_repro/p172_gapstations.csv (188 rows).

**2. Drop stage NAMED: mesh-stage region-growing segmentation, NOT cleanSamples, NOT downsampling, NOT the estimator.** Chain with evidence at each link: (a) downsamplePointCloud (original_nurbs_preprocessing/mesh_processing.cpp:447, UniformSampling radius 0.6mm) EXONERATED -- rim points survive it: the staged unclustered.ply (2343 pts, downstream of the sampler) reaches min 0.07 / med 0.74 / max 1.66mm of all 188 gap stations, 188/188 <2mm, every run. A 0.6mm sampler cannot open a 2-6mm gap. (b) surfaceSegmentation (mesh_processing.cpp:1341, called from main :1738 with minCluster 50, neighbours 10, smoothnessAngleThreshold 4.5, curvatureThreshold 1.5; smoothness applied :1405, unclustered spill written :1607) -- NAMED DROP: PCL RegionGrowing with a 4.5-degree smoothness threshold stops at the rounded rim fold (normals turn fast across it, cf. 166 rim fold), leaving the 2-6mm rim strip unclustered. The near-rim unclustered points (the 188 station-nearest, all <2mm from ORIG) sit 1.1-5.3mm off the sheet (med 2.98) -- exactly the missing strip, sitting in the rejects pile. (c) cleanSamples (original_nurbs_preprocessing/edgeline_extraction_headless.cpp:2265, SOR MeanK 50 / std 9) EXONERATED -- removes 0/11165 (169). (d) BoundaryEstimation EXONERATED (169: fires bit-exactly at the truncated sheet edge). Honesty note: stage (b) is inferred from staged artifacts (DS mesh + Surface_0.xyz + unclustered.ply agree exactly), not from rerunning the C++ segmentation -- the numbers leave no other stage: rim present downstream of the sampler (unclustered), absent from Surface_0, untouched by cleanSamples.

**3. Renders (all 5 eye-checked: green mesh curve hugs ~0 while gray sheet rides 2-6mm; closeups show green ORIG stations on light-green triangulation beyond the gray sheet dots; overview shows the full ORIG rim riding mesh triangulation).** artifacts/pota172/p172_coverage.png | p172_runR11_46.png | p172_runR3_35.png | p172_runR6_32.png | p172_overview.png. Scratch .scratch/pota172_repro/ (p172_step0.py + p172_meshgap.npz + p172_gapstations.csv, p172_step1.py + p172_unclustered.npz, p172_step2_render.py + step txts).

**What would overturn this:** a Surface_0 re-segmentation (smoothness/curvature relaxed at the fold, or rim-aware region seeding) whose sheet reaches <2mm at the 188 stations -- the estimator would fire there by the verified 169 rule, and the mesh triangles already underneath (<=0.26mm) prove the surface exists to sample.

- [x] per-station mesh-vs-sheet distances + verdicts
- [x] stage that dropped the surface, named (where MESH-HAS-IT)
- [x] Verdict + render paths
