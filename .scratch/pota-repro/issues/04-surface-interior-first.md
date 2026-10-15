# 04: Surface interior-first fix

**What to build:** the mesh surface split guarantees interior-first ordering (largest-two + classification), so fresh pieces 2–8 stop landing ~3mm high with flipped normals.

**Answers:** E1

**Blocked by:** 02-swap-test (needs the swap verdict to pick the mechanism).

**Status:** results-in — interior-first verified p1/p3-8, p2 guard-kept (designed); E1 write-back still to do

**Working in:** `%TEMP%\t04verify\` (48 xyz + `t04compare.py`; outside repo, kept for re-run)

- [x] Spike: state chosen mechanism (fork `ticket04_interior_first.cpp` + `surface_classify.cpp` direction, or refutation with measurement)
- [x] Fix in fork; ORIG arm rides along; fresh-vs-ORIG per-piece medians reported (target p2–8 ≈0.5mm, normals −Z on S0)
- [x] No-regression: piece 1 unchanged-or-better; density note (3.3× denser fresh) dispositioned

## Comments (worker pota-interior-fixer, 2026-10-15)

**Verdict: interior-first VERIFIED on p1 (control) and p3–8. Piece 2 guard-kept by design (documented exception, predicted Sept 28). No source edits made — the fix (Sept commits 4513f00/054a697/48cca80) was re-verified against current HEAD.**

### Spike: chosen mechanism (confirms ticket-02 H1, no refutation)
- Labels derive purely from cluster-size rank (`mesh_processing_headless.cpp:1680` sort desc, `:1704` merge, `:1755-1769` clusters[0]→Cluster1/[1]→Cluster2, `:1798-1799` tmp ply, `:2073-2087` Surface xyz) — no classification on that path (`:1733` flips all normals globally only).
- Fix hooks the **edgeline stage, not the mesh assignment**: `edgeline_extraction_headless.cpp:3665-3693` (SFS-T04) runs the paper IV-B1 ray-vs-axis vote (`surface_classify.{h,cpp}`, eps 5mm) on the two written Surface files using `Dataset/Axes/<piece>_Axis.xyz`, and exchanges them in `Temp/Data` iff Surface_1 wins — so Breakline_0 traces the interior wall. Rationale (Sept, kept): mesh stage stays byte-identical, one removable file, exchange verified post-write by byte-cmp. Largest-two selection itself matches the paper; the missing classification was the defect.
- Freshness proof (no rebuild needed): no pipeline-source commits after the Sept-30 12:58 binary build (`git log --since="2026-09-30 13:00" -- original_nurbs_preprocessing/` empty); the verified Oct-01 `diag_t04_pota` run used that binary (guard lines present, `mergeClusters pass` lines present). SFS-T04 log: p1 KEEP (820 vs 225), p2 guard-REJECT (ratio 0.015<0.10, margin 1.44<2.0 — 171-pt scrap vs 11k-pt wall), p3–8 EXCHANGE (margins 4.3–32).

### Numbers (laptop-only, at GT; fixed=Temp/Data post-exchange, ORIG=authors' samples, metric=ticket-02 style median NN + offset + normal cos)

| piece | straight S0-S0 med (mm) | straight S1-S1 med (mm) | normal sign | fixed S0 med nz |
|---|---|---|---|---|
| 1 (control) | 0.30 | 0.30 | agree (+1.000, 100%) | −0.993 |
| 2 (guard-kept) | 3.47 (dz +2.35) | 3.35 | oppose (−0.996) | +0.652 |
| 3 | 0.30 | 0.29 | agree (+1.000, 100%) | −0.758 |
| 4 | 0.31 | 0.30 | agree (+1.000, 100%) | −0.755 |
| 5 | 0.30 | 0.31 | agree (+1.000, 100%) | −0.752 |
| 6 | 0.30 | 0.30 | agree (+1.000, 100%) | −0.697 |
| 7 | 0.30 | 0.30 | agree (+1.000, 100%) | −0.924 |
| 8 | 0.31 | 0.30 | agree (+1.000, 100%) | −0.682 |

- Straight offsets 0.00 mm on all axes wherever med ≈0.3. Exchange audit re-run laptop-side on fetched files: p1/p2 fixed==historic same-side, p3–8 fixed S0==historic S1 and vice versa — matches the SFS-T04 log exactly.
- Controls: p1 crossed S1-S0 7.18 mm oppose (metric discriminates); p2 crossed S0-S1 0.40 mm agree (+0.999) — proves p2's fixed S0 IS the authors' S1, i.e. guard kept historic (swapped) order as designed. p2's fixed S1 is the 171-pt scrap vs ORIG's 13455-pt wall (mixed cos 73%), which is why the guard exists.
- **p1 unchanged-or-better: 0.30/0.30, identical to the unfixed 0.30 (p1 KEPT, correctly — it was already right).**
- **Density dispositioned, no action:** the 3.3× figure is the *untouched*-mesh run (p1 64661 vs ORIG 19463). The *fork*-mesh run samples differently (p1 6970, p2 S0 11263 vs 12178, p7 7904 vs 1745 — comparable-or-sparser; fork mesh tolerance/persist from earlier tickets, out of scope). Untouched-fresh vs fork-fixed same-wall medians are 0.56–0.72 mm (sampling, not shift), while wall-identity discrimination is 0.3 vs 3.5–7 mm — the verdict is not density-driven.

No geometry was moved and nothing was rendered (comparison-only; same basis as ticket 02).
