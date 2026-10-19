# Emptiness test: a true-edge dot has empty space beside it, a false-face dot does not

GOAL: A VETO FEATURE THAT SEES POSITION, NOT ANGLE.

**Answers:** E1

**Blocked by:** 160 (angle features exhausted: align modes straddle true/false on C01) + 158 (veto load-bearing) + user insight 2026-10-19.

**Status:** results-in

**User's idea (verbatim):** test the edge -- on the edge there would be no dot for miles. I.e. for each veto-candidate dot, examine its local neighbourhood: a dot on the true rim has empty half-space beside it (air beyond the edge), while a dot on the false face sits amid mesh/dots all around. Asymmetry of neighbours (e.g. fraction of an annulus/ball occupied, or largest empty angular sector) should separate rim from face where the normal-angle rule cannot.

**What to deliver:** (a) ANALYSIS: compute a neighbourhood-emptiness score for the 364 C01 veto-site dots + Pot A rim dots; overlay vs ORIG loops -- do true-rim dots score empty and false-face dots score surrounded on BOTH pots with one cutoff? (b) RULE (if it separates): emptiness-gated veto in the worktree variant, both pots run + 98-gated. Bar: Pot A cure kept (P02_0 ~97 etc.) AND C01 rim kept (gate at-or-better-than fresh 5.61/22.9). (c) If emptiness also straddles, report as negative with the plots.

**Starting position:** 155/156/158/160 Comments (code sites, worktree + build, staged inputs, gate scripts); 160 scratch (C01_BASE/C01_VAR, veto-site dots). New scratch pota162_repro/; renders artifacts/pota162/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-161 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] emptiness scores A + C01 (rim vs face overlay vs ORIG)
- [ ] (if separates) emptiness-gated veto built + both pots run + gated -- NOT BUILT (straddles; rule (c) negative path)
- [x] Verdict + render paths

## Comments (worker, 2026-10-20 -- clean NEGATIVE, analysis-only, nothing built)

VERDICT: emptiness straddles -- no neighbourhood score isolates the false face on both pots with one cutoff, and density separates BACKWARDS (rim dots are the dense ones). Per rule (c) reporting as negative with plots; no variant built, both-pots run omitted by entailment (nothing gate-passing to run), worktree untouched.

Method (laptop-side, 160's staged data, no new jobs): C01 veto-site cloud = C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv (364 dots, x/y/z pre-veto); labels by 160's ORIG-overlay method (TS-mapped, TO==TS md5-verified e6209ecb; NEAR<2mm n=86 / FAR>5mm n=91 -- counts reproduce 160 exactly). Pot A = PA_ADAPT veto_align CSVs, all 8 pieces/16 surfaces; labels by distance to that piece's renders-verified VAR clean walks (same extraction frame, no transform needed): 6 two-face surfaces carry both labels (P01c1, P02c2, P03c4, P05c8, P08c14/c15; n_rim=630, n_face=441); other 10 surfaces are single-face (FAR=0, veto had nothing to veto there). Scores (all rigid-invariant): ball counts r=2/3/5/8/12mm, largest-empty-sector R=6/12/20mm, annulus count/cover 3-8/5-12/8-20mm, PCA linearity.

Numbers (direction kills the idea, not just the cutoff):
- C01 ball8: rim med 8.0 vs face 6.0, AUC(rim>face)=0.81 -- rim DENSER (veto-the-sparse would keep the face). ball12 same direction (15.5 vs 11.0, AUC 0.75).
- C01 maxgap R=6/12: 188/172 vs 184/170 deg, AUC 0.50/0.52 -- coin flip. Both structures are 1D loops (~170 deg empty locally), not rim-vs-sheet.
- C01 annulus 8-20 cover: rim 0.19 vs face 0.31 -- direction FLIPS vs small scale (scale-fragile, no robust operating point).
- Pot A: rim med >= face med on ALL 6 two-face surfaces (ball5/8/12; e.g. P03c4 ball8 AUC 0.96 backwards, P01c1 ball8 AUC 0.60 backwards) -- same backwards direction as C01.
- One-cutoff bar test (rim-kept>=95% AND face-dropped>=90% simultaneously on C01 + all 6 Pot A surfaces): all 5 scores FAIL with huge negative margins (best face-drop at any rim-safe cutoff is 0-1% for density scores; gap20 keeps only 31-73% of rims).
- Mechanism (renders): the veto-site cloud is TWO PARALLEL LOOPS a wall-thickness apart, not rim-vs-sheet -- the user's "no dot for miles" half-space doesn't exist because the false loop runs alongside the rim. The rim loop is sampled denser (extractor walks it), so density anti-separates.

Banked context (cited, not rerun -- analysis-only landing needs no new numbers): Pot A BASE->VAR Bl_0 pairs P01 193->191, P02 727->79, P03 485->117, P04 242->101, P05 326->55, P06 144->105, P07 64->37, P08 61->16 (160); C01 gate BASE 5.61/22.9% vs VAR 5.96/1.3% (160).

Renders (eye-checked: axes/legends live, loops visible, no empty panels): artifacts/pota162/C162_C01_scores.png (ball8/maxgap histograms + density-vs-ORIG-distance), artifacts/pota162/C162_C01_spatial.png (gate-frame ball8 + ORIG Bl0/Bl1 overlay; dense dots sit ON the ORIG rim, sparse dots form the parallel false loop), artifacts/pota162/C162_PotA_scores.png (pooled + per-surface medians; CAUTION left panel mixes inter-surface density scales -- right panel carries the claim). Scripts: .scratch/pota162_repro/p162_emptiness.py, p162_sweep.py, p162_bar.py, p162_plots.py (+c01_scores.npz, pota_scores.npz, pota_twoface.npz; inputs unpacked under .scratch/pota162_repro/pota160_repro + sfs_main/).

Discipline: COMMIT NOTHING (no commits; 39-161 untouched; relay worktree sfs_cure_1c6a8f9 never entered, no build, still byte-identical by non-contact); no Slurm submitted -- sacct has nothing to record (analysis laptop-side on 160's staged CSVs/pcds fetched via one /tmp tarball, md5-verified TO==TS). Same-binary ORIG control N/A (no variant run to void).

Next (not claimed): position thinks in loops, not dots -- a loop-level feature (e.g. loop-to-loop pairing across the wall thickness, or the 160 radial probe r>=47.69 which hit 98.8%/11% but was knife-edge in adaptive form) is where a position-based veto could still live; dot-neighbourhood emptiness is exhausted.
