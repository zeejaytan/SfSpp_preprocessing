# Edge-only boundary — stop the boundary test admitting mid-face dots

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** a screening test of the user's two-fix program, fix 1: run the PCL empty-sector boundary test on each segmented surface cloud ALONE (Surface_0 interior, Surface_1 exterior) instead of on the merged/full cloud, and count mid-face admissions on C01. Prediction (registered before running): per-surface testing admits ~zero interior-wall dots (no neighbouring pass to confuse the sector test), while the merged-cloud run reproduces the 343-bag incl. the circled inboard row. If confirmed, write the exact implementation recipe (which call moves inside which loop, file + line).

**Answers:** E1

**Blocked by:** 102 (bag + replay + mesh) + 103 (removal rule + verdict)

**Status:** results-in

**Starting position:** /data/gpfs/projects/punim2657/pota102_repro/ + p103_repro/; staged surface clouds from the pipe intermediates. Login-node numpy/PCL-faithful only — no Slurm, no E2E. New scratch pota104_repro/; renders under laptop artifacts/pota104/.

**Rules:** read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one variable (per-surface vs merged input cloud).

- [ ] Per-surface boundary run vs merged run (admission counts, mid-face dots)
- [ ] Gate of resulting bag vs ORIG (does edge-only input chain cleaner)
- [ ] Implementation recipe if confirmed (file + line + moved call)

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: prediction REFUTED on both halves — per-surface testing does not yield an edge-only bag, and the merged run does not reproduce the 343-bag. The boundary test is not where the circled row enters: ROW40 is 0/40 in the per-surface boundary set and enters one stage later at the K=1 improve snap. No implementation recipe (nothing confirmed); redirect evidence below.**

**0. Method (login-node numpy only; zero ORIG points copied; ORIG Bl_0 gate-evidence only; COMMIT NOTHING).** Pipe-faithful replay of SOR (MeanK=50, std=9) + PCL-1.9.1 empty-sector test (float32 port ex 102: atan2f, FLT_MIN init, wrap, strict > 0.6pi) + adaptive radius + K=1 improve onto unclustered.ply + ROR dense rule + greedy K=34 / SFS-T13 walk, in two arms. Arm P (per-surface): S0 alone, S1 alone. Arm M (merged): concat S0+S1 raw -> SOR -> adaptive radius -> boundary, split admitted by origin; S0-origin set through the SAME downstream (improve, ROR r=8.62091, walk K=34) so the boundary input is the only delta (primary); pipe-exact merged variant (own r_o, own K) secondary. Mid-face rule pre-registered: ROW40 = 40 unique coords with 102 visit in [93,132] (the circled inboard row). New scratch /data/gpfs/projects/punim2657/pota104_repro/ (p104_run.py, p104_followup.py, p104_render.py, .npy/.npz, p104_numbers.txt, p104_compare.png). Laptop mirror artifacts/pota104/ (scripts + numbers + PNG, eye-checked). No Slurm, no E2E.

**1. Controls green (arm P reproduces the pipe exactly).** S0 SOR 11165 kept/0 removed; r_b 6.46568; S0 boundary 364; ROR 343 kept/21 removed; walk greedy 93/343, 237 pushes, 4 jumps at (92,93) (132,133) (170,171) (223,224); loop gate med 5.79 <2mm 24.9% (= 103 baseline to 2dp). S1 boundary 109 (log line 1226), ROR 109/0.

**2. Admission counts (rows; rounded-6 uniques in brackets: S0-alone 364 [338], merged S0-origin 473 [439] — near-tie dups).** Merged boundary 557 = 473 S0-origin + 84 S1-origin, vs per-surface 364 + 109 = 473. So merging admits a net +109 S0 points (109 merged-only minus 8 lost) while LOSING 25 S1 lip points (109 -> 84). Merged-only S0 admissions vs ORIG lip (GT-seated): n=109, med 6.72mm, max 51.28mm, 63.3% >5mm — genuinely mid-face/off-lip. Merging makes mid-face admission worse, not the cause of the 343-bag.

**3. ROW40 (the circled row) per arm.** S0-alone boundary: 0/40. Merged S0-origin boundary: 0/40. Per-surface final bag: 40/40. Merged final bag: 34/40. So NEITHER boundary test admits the row — prediction half 1 fails at the bag level (the level the walker sees). Entry point (follow-up): ROW40 are 40/40 exact vertices of unclustered.ply (nearest-vertex distance 0.000), sitting med 2.10mm (90% <3mm, max 5.74) from the nearest S0-alone lip boundary point — the K=1 improve snap (edgeline_extraction_headless.cpp:951-972, kdtree.nearestKSearch K=1 loop) drags the inboard row vertices into the bag. Fix-1 target (boundary input cloud) is upstream of the actual entry; the firewall belongs at the improve map (fix-2 territory, not implemented here).

**4. Gate vs ORIG Bl_0 (n=211; 103 recipe: GT-seat each, fresh->ORIG nearest, jumps = consecutive gaps >5mm).** Per-surf walk-loop (237): med 5.79, <2mm 24.9%, 45 jumps. Merged-fixed loop (235): med 4.69, <2mm 31.1%, 22 jumps — flattering but degenerate: greedy covers 235/462 (50.9%), the >=40% bar suppresses the second chance, 227 bag points never visited; the "better" median is a stalled half-walk, not a cleaner lip trace. Merged pipe-exact (K=45, 295): med 5.67, 26.8%, 36 jumps. Bag-level (unordered) gates are ~identical: per-surf 5.80/22.2% vs merged 5.83/24.0% — the bags sit in the same place; only walk behaviour differs. Edge-only input does not chain cleaner.

**5. Renders + paths.** artifacts/pota104/p104_compare.png eye-checked: (local) S0-alone vs merged S0-origin boundary + ROW40 X | per-surf vs merged walk loops | (GT-seated) ORIG green + both loops — merged hugs ORIG on the intact arc but never traces the top. Spartan: pota104_repro/{p104_run.py, p104_followup.py, p104_render.py, p104_bnd_{S0,S1,M}.npy, p104_bnd_M_origin.npy, p104_walk.npz, p104_row_snap.npy, p104_numbers.txt, p104_compare.png, p104_run.log}. 39-103 lanes read-only; no prep/assembly sources touched; COMMIT NOTHING done.
