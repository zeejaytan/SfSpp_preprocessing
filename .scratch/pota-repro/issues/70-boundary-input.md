# 70: Boundary-detection input — move the cloud onto the lip

**What to deliver:** boundary cloud sitting on the shipped lip — gate recovery (+ E2E on landing).

**Answers:** E1

**Blocked by:** 69 (walk-level guards only re-tile: GUARD 4 runs→2, stays ~4-6mm off, gate regresses 2-4:14 vs 16; SPLIT destructive n=18; RADIUS 2.0 degenerates 9175 pts coverage 0.03 / 4.0 worse than BASE; all arms deterministic 16/16 STABLE; BASE byte-identical to p39; jobs 33281127/33281711/33282098/33282622 COMPLETED; NO E2E per Rules) + 67 (enabler PCL BoundaryEstimation r=4mm admitting both lip faces).

**Status:** results-in — no arm reaches the bar (M4 collapses the doubling but the surviving loop stays ~3.8mm off; radius selects loop count, not placement); no E2E per Rules

**Starting position:** the ~5-6mm offset is already in the boundary-estimator output. Next variables: radius multiplier/clamp around the estimator, or pre-walk cloud selection (which points get offered to detection). Fresh-only scratch prep copies; bundle references pota69/pota39 C bundles (read-only). C03 green control must stay seated. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** diagnosis with login-node screening first; E2E only to confirm a mechanism (and only when jumps→0 AND gate recovery AND ~1-2mm all hold); controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [x] Boundary-input arms, one variable each
- [x] Gate (+ E2E if bar met) or measured why-not
- [x] Job IDs + sacct states (or explicit screening-only)

**Comments (worker, 2026-10-17, measured why-not — bar not met, no E2E, COMMIT NOTHING):**
- Vehicle: pota70_repro/src = copy of pota69_repro/src + env-gated POTA70 patch only (POTA70_MULT / POTA70_CLAMP_HI around `clamp(spacing*6,[1,15])`, POTA70_NOIMPROVE skips the unclustered snap; all default off). Each arm sets exactly one variable. Nothing else touched; 39/69 lanes read-only; no commits.
- Jobs (sacct-direct, all COMPLETED 0:0): build 33283715 (BIN-POTA70-OK); edge 33283716 (BASE/M4/M8/CLAMP5/NOIMPROVE + bundles); repeat 33283920 (rep1+rep2 all arms).
- Baseline control: BASE Bl_0 byte-identical to p69 bundle 4/4 (cmp) — same-binary reproduction.
- Fresh-vs-shipped at GT (full-contour NN median): BASE 5.61/6.07/0.95/5.48 (C01/C02/C03/C04); M4 3.75/5.86/1.01/5.15; M8 5.43/6.08/0.96/5.47; CLAMP5 5.65/5.93/1.02/5.48 (C01 n=511 exploded); NOIMPROVE 5.23/6.11/1.28/5.50. C03 green control seated ~1mm in every arm. No arm reaches ~1-2mm.
- Gate (gate68.py metric, strict inliers per GT edge 1-2/1-3/1-4/2-3/2-4; jumps>5mm p1-p4): BASE jumps 3,3,1,2 / 0,1,4,0,16; M4 jumps 1,1,1,2 / 0,2,1,0,14; M8 1,3,1,2 / 1,3,1,0,17; CLAMP5 3,3,1,2 / 0,6,4,0,19 (1-3 ticks on doubled n=511 content, jumps unchanged — not recovery); NOIMPROVE 1,3,1,2 / 0,1,0,0,19. Jumps never →0; no gate recovery.
- Eye-check (pota70_repro/C01_BASE|M4|M8|CLAMP5|NOIMPROVE.png, C04_BASE.png; C01_BASE/M4 inspected): BASE = 4 concatenated runs (doubled parallel loops); M4 = single 244-pt loop + 16-pt nub still riding off ORIG. Smaller radius collapses the doubling, not the offset.
- Determinism: 40/40 STABLE (5 arms x 4 pieces x rep1+rep2) = x3 per arm with the original run.
- Verdict: bar (jumps→0 AND gate recovery AND ~1-2mm) not met in any arm, so no E2E per Rules (controls N/A without E2E, per 69 precedent). Mechanism refinement: radius selects loop COUNT (M4 402->260 pts, 4 runs->2) but not loop PLACEMENT (survivor still ~3.8mm off); NOIMPROVE null exonerates the unclustered snap. Next variable is which FACE survives (inner/outer selection rule) or detection-input density, not radius magnitude or the snap.
- Renders: /data/gpfs/projects/punim2657/pota70_repro/C01_*.png + C04_BASE.png; copies C01_BASE/M4.png in SfSpp_preprocessing/artifacts/pota70/ (local-only, uncommitted).
