# Bend-aware boundary: sharp turns are not edges

GOAL: THE EDGE-FINDER STOPS FIRING WHERE THE SHERD BENDS.

**Answers:** E1

**Blocked by:** 163 (substrate = PCL BoundaryEstimation on cleanSamples sheets; C01 false loop = sheet edge past the loop) + user diagnosis 2026-10-19 + 155 (code sites).

**Status:** results-in

**User's diagnosis (verbatim):** the only reason BoundaryEstimation marks that as edge is the mesh takes a sharp turn at that junction; the code assumes a sherd is relatively flat without much bend, but this piece has bend. Fix: BoundaryEstimation must not mark anything that has points in 360-degree space -- only mark the true edge.

I.e. the angular-gap test confuses a sharp bend (neighbours present all round in 3D but folded, piling into half the tangent plane because the normal estimate tilts) with a true sheet end (neighbours genuinely missing on one side). The corrected rule fires only when points are truly absent through a 360-degree check that survives bending -- e.g. gap test in 3D rather than the tilted tangent plane, normal-consistency of neighbours, or a bend-compensated threshold.

**What to deliver:** (a) CONFIRM: measure bend (dihedral/curvature/normal-spread) at the C01 false-loop sites vs true-rim sites vs Pot A sites -- is the false loop at a sharp turn? (b) FIX: bend-aware boundary rule in the worktree variant; run both pots; 98-gate both. Bar: Pot A cure kept AND C01 false loop gone with rim kept (at-or-better-than fresh 5.61/22.9). (c) If bend does not own the false loop, negative with the measurements.

**Starting position:** 163 Comments (substrate, code sites, staged inputs); 155 Comments (worktree + build); 160/162 Comments (labels, gate scripts). New scratch pota164_repro/; renders artifacts/pota164/.

**Rules:** same-binary ORIG control alongside or void; worktree-local build only, restore byte-identical after; COMMIT NOTHING; tickets 39-163 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] bend measurements false vs true vs Pot A
- [ ] bend-aware rule built + both pots run + gated -- NOT BUILT (bend does not own the false loop; rule (c) negative path, same entailment as 162/163)
- [x] Verdict + render paths
## Comments (worker, 2026-10-20 -- CLEAN NEGATIVE, analysis-only, nothing built)

VERDICT: bend does not own the C01 false loop. The false loop sits on FLATTER sheet than the true rim (tilt 24.6 vs 29.0 deg, surface-variation 0.098 vs 0.130), the tilted-plane artefact the diagnosis predicts is ~zero on both (gapM-gapP med 0.15 vs 0.43 deg), and the user's 360-degree picture is INVERTED: the FACE is the one surrounded in 3D (surround-3D 0.494 vs 0.365, AUC(near>far)=0.05), the rim is the one-sided one. Bend-compensating the projection plane (PCA plane instead of mesh normal) SEPARATES WORSE (AUC 0.70 vs 0.83 at R=8, 0.85 vs 0.87 at R=12). Pot A directions flip vs C01, so no single bend rule can serve both pots. Per rule (c) reporting as negative with measurements and plots; no variant built, both-pots run omitted by entailment (nothing gate-passing to run), worktree untouched.

Method (laptop-side, 162/163 staged data, no new jobs): C01 = 364 c0 veto-site dots, labels by 160/162 ORIG-overlay (TS-mapped, NEAR<2mm n=86 / FAR>5mm n=91 -- counts reproduce 160 exactly). Pot A = 16 veto_align CSVs, labels by distance to renders-verified VAR clean walks (6 two-face surfaces carry both labels, same six as 162/163: P01c1, P02c2, P03c4, P05c8, P08c14/c15). Dense sheets + mesh normals: C01S0_STAGED.xyz (163 inputs), Pot A NURBS_Dataset ProperSegmentation Surfaces (surface mapping re-verified per file by proximity, med 0.25-0.3mm frame match per 163). Features per veto dot on dense-surface ball R=8/12mm, all rigid-invariant and mesh-observable: tilt = angle(mesh normal, PCA plane normal); incoh = 1-|mean neighbour normal|; maxnp = max pairwise neighbour-normal angle; svar = PCA surface variation; gapM = PCL-replica maxgap on mesh-normal plane (163's score); gapP = same on PCA plane (bend-compensated); artefact = gapM-gapP; sur3 = 1-|mean neighbour direction| (3D one-sidedness).

Numbers (C01 S0, R=8; R=12 same picture):
- tilt: NEAR 29.0 vs FAR 24.6 deg, AUC(near>far)=0.64 -- rim MORE tilted (flaring break, cf. 160 both-align-modes). WRONG WAY for the diagnosis.
- svar: NEAR 0.130 vs FAR 0.098, AUC=0.68 (R=12: 0.86) -- rim MORE curved. WRONG WAY.
- incoh: 0.30 vs 0.44, AUC=0.53 -- coin flip. maxnp ~179 deg both (normals contain near-antipodal pairs everywhere; saturated, useless).
- artefact: NEAR 0.43 vs FAR 0.15 deg, AUC=0.55 (R=12: -2.2 vs +1.3, AUC=0.32) -- no tilted-plane artefact exists at either site.
- gapP separates WORSE than gapM (AUC 0.70 vs 0.83) -- bend compensation destroys signal, the opposite of the proposed fix.
- sur3: NEAR 0.365 vs FAR 0.494, AUC=0.05 (R=12: 0.015) -- the face is surrounded in 3D, the rim is one-sided. The diagnosis describes the two sites backwards.
- Formal one-cutoff bar on C01 (rim-kept>=95% AND face-drop>=90%): every feature fails with huge margins (best face-drop at rim-safe cutoff 0-3% for tilt-low/svar-low/artefact either direction); only sur3-low at R=12 reaches 91.2% -- and its direction (keep the LESS-surrounded) is exactly what Pot A inverts (below), so the two-pot bar is unpassable.

Pot A flips (R=8, per-surface): tilt face>rim on P01c1 (12.9 vs 2.4, AUC=0.13), P02c2 (6.7 vs 2.8), P05c8 (15.7 vs 5.2) -- INCONSISTENT with C01 (rim>face there); P08c14/c15 both sides highly tilted (21-31 deg, flaring lip). artefact AUCs straddle: 0.72/0.52/0.38/0.70/0.77/0.24 -- no consistent direction. sur3 AUCs 0.56/0.42/0.77/0.90/0.63/0.71 -- rim often MORE surrounded in 3D (backwards again, cf. 162 density). Same entailment as 162/163: per-pot cutoffs/directions would need pot identity, which is not mesh-observable (bar explicitly one cutoff both pots).

Mechanism note: PCL BoundaryEstimation is not firing on a bend here -- C01's false dots are interior false positives on flat sheet (163: face gap SHRINKS with radius = interior signature), while the true rim's own tilt/curvature comes from the flaring break. The user's junction-bend picture does not match where the false loop actually sits (inner flat wall, see spatial render).

Banked context (cited, not rerun -- analysis-only landing needs no new numbers): Pot A BASE->VAR pairs P01 193->191 ... P08 61->16 (160); C01 gate BASE 5.61/22.9% vs VAR 5.96/1.3% (160).

Renders (eye-checked: axes/legends live, both loops visible):
- artifacts/pota164/C164_C01_bend.png -- tilt/svar/artefact/sur3 NEAR vs FAR histograms (rim more bent, artefact~0, face more surrounded)
- artifacts/pota164/C164_PotA_bend.png -- per-surface tilt/artefact medians (direction flips vs C01)
- artifacts/pota164/C164_C01_spatial.png -- tilt-coloured dots + NEAR/FAR vs ORIG overlay (inner false loop = FAR, high tilt sits on the rim curve)
Scripts: .scratch/pota164_repro/p164_bend.py, p164_bar.py, p164_plots.py (+c01_bend.npz, pota_bend.npz).

Discipline: COMMIT NOTHING (no commits; 39-163 untouched -- this ticket Comments-only); relay worktree never entered, no build, still byte-identical by non-contact; no Slurm submitted -- sacct has nothing to record (same as 162/163); same-binary ORIG control N/A (no variant run to void).

