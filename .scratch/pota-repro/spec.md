# Spec — Pot A reproduction (preprocessing side)

**Answers:** E1

**Prior work searched:** GitHub "SfSpp_preprocessing DominicoRyu", "Structure-from-Sherds SfS++ 2502.13986"; papers/text/sfspp-2502.13986v1.md. Found: https://github.com/DominicoRyu/SfSpp_preprocessing (pin d5ee6865) — or: nothing else found.

**Status:** spec for slicing; tickets 01–06 slice the preprocessing fix; tickets 07–10 (added 2026-10-15) slice the pristine-only axis verdict — author's code + paper only, fork blocked.

## Problem statement

The untouched preprocessing chain cannot reproduce the authors' Pot A input as released. Three breaks, each with a known fix direction (evidence round Oct 2026, tasks 1–3):

1. Fresh surfaces pieces 2–8 sit +1.8–3.5mm in Z vs ORIG — enters at mesh surface segmentation (interior/exterior swap suspected).
2. Fresh edge files lack the `#` segment header block — pristine assembly loads 0/8.
3. MATLAB axis chain cannot run as released — full Python rebuild planned (`sfs_axes/`).

Success bar (interview converged): Gate 15/15 + end-to-end 8/8 + 15/15 at k=5/b=3, Table V Pot A. Pot A first, then expand.

## Scope decisions (binding)

1. Fixes land in forks with pristine controls pinned at `archive_2025_sfs_modified_src@d5ee6865` on both sides (version-skew warning: laptop copies already carry header support).
2. Two lanes per ticket: gate lane (must move a scored number) or compliance lane (no-regression proof + stated reason).
3. Research spike first in every ticket; work stops if the spike says harmless.
4. Authors' ORIG arm rides along in every comparison.
5. This feature does not specify assembly-side work; assembly gaps live in `structure-from-sherds-pp`.

## Tickets

| # | Title | Lane | File |
|---|---|---|---|
| 01 | Census close-out (Spartan ls + threshold overrides) | compliance | issues/01-census-closeout.md |
| 02 | Swap test (laptop-only cross-pair) | gate | issues/02-swap-test.md |
| 03 | Header writer fix (emit segment block) | gate | issues/03-header-writer-fix.md |
| 04 | Surface interior-first fix | gate | issues/04-surface-interior-first.md |
| 05 | sfs_axes Python port | gate | issues/05-sfs-axes-port.md |
| 06 | Gate + E2E re-run with pristine controls | gate (SHORTFALL: gate 15/15, E2E 4/8+3/15) | issues/06-gate-e2e-rerun.md |
| 07 | Pristine PotSAC map (paper §IV-B2 → author files) | compliance (results-in: refine_axis MISSING from pin) | issues/07-pristine-potsac-map.md |
| 08 | Pristine axle failure repro (no fork in the loop) | gate (results-in: NO — 0/8 yield an axle; loader missing + vote crashes on iter 1) | issues/08-pristine-axle-repro.md |
| 09 | Pristine axle repair (smallest fix that finds the shipped axles) | gate (KILL: 1/8 after R1+R2+R3; redesign needed) | issues/09-pristine-axle-repair.md |
| 12 | Reverse-engineered axle finder (fit 01–04, prove on sealed 05–08) | 2/8 (fit 2/4 + held-out 0/4; direction solved where fittable, ~2-3mm material floor; P06 + multi-axis open) | issues/12-axle-finder-redesign.md |
| 13 | Genuine piece-2 rim fix (last blocker to 8/8) | gate 15/15 patched (landed; E2E best 7/8+11/15 — blocker now search-side) | issues/13-piece2-rim-fix.md |
| 14 | Diagnose piece-6's direction miss (base? disjoint? vote poverty?) | landed: vote finds truth 1/6000, Huber refine destroys it — cost mismatch | issues/14-piece6-diagnosis.md |
| 15 | Align refine cost with selection cost (GM refine) | landed: (a) passes — refine-from-shipped 4/4, P06 8.19°→2.00°; 6/8 under bar | issues/15-gm-refine-align.md |
| 16 | Frozen re-validation on sealed 05/07/08 (+ near-tie selection if needed) | landed: (a)-baseline P05 pass, P07 count-miss, P08 direction-miss; (b) moves P08-sh2 but regresses P06 — NOT frozen | issues/16-sealed-revalidation.md |
| 10 | Generalise the frozen (a)-finder to pots B–J (frozen 2026-10-16; cross-pot only, Pot A held-out spent in 16) | landed: 117/155 (75%) dir-pass, H-family 1/11 new — per-family repairs next, not E2E | issues/10-axle-generalise.md |
| 17 | Diagnose the Pot H collapse (span floor? vote dilution? fragment type?) | landed: base-type + sub-floor support + dilution combined; refusal-gate proposal | issues/17-poth-diagnosis.md |
| 18 | Refusal gate for unidentifiable fragments + H base-cap renders | landed: ship cost>1.40 AND share<0.22 (H 11/11 refused, 97.4% specificity); H3 eye-confirmed by lead on all four renders | issues/18-refusal-gate.md |
| 19 | Pot A end-to-end assembly on admitted fragments (our rims + our axles) | landed: ORIG control 8/8+15/15 valid; fresh-ablated 7/8+11/15 (only p2 off ~103°); patched arm 7/8+7/15 (patch poison ×3); p2 is the last blocker | issues/19-admitted-e2e.md |
| 20 | Piece-2 endgame (exterior wall? beam preference?) | landed: swap seats p2 4/4 strict — search exonerated; our p2 wall lost downstream of byte-identical mesh (S1 = 171-pt scrap ~3mm off); fix NOT yet made | issues/20-piece2-endgame.md |
| 21 | Recover the p2 exterior-wall surface (pin extraction stage) | landed SHORTFALL: SFS-T21 wall split committed (gate 15/15, ORIG valid); E2E strict fails — beam's ~102° p2 attractor persists across stub/patch/full rims, drags pieces 1,6,7,8 as rigid block | issues/21-piece2-wall-recovery.md |
| 22 | Search-side: break the ~102° p2 false attractor (within-bundle swaps only) | strict 8/8 + 15/15 fresh | issues/22-beam-attractor.md |
| 23 | Landmine fixes: tmp_path multi-iteration wipe + mesh-stage nondeterminism | deterministic reruns, no silent loss | issues/23-pipeline-landmines.md |
| 11 | Ablate patch segments on p2–p5, re-run E2E (follows 06 shortfall) | gate (results-in: 11/15 gate, 7/7+11/11 placeable; patches load-bearing yet search-poison; p2 rim next) | issues/11-patch-ablation-e2e.md |

## Pristine-only axis path (added 2026-10-15, binding on tickets 07–10)

Tickets 05's verdict is quarantined: it compared fork code against fork (NURBS) references, so it says nothing about whether the *author's* path is fixable. Tickets 07–10 re-derive from scratch.

- **Allowed sources:** the paper text (`papers/text/sfspp-2502.13986v1.md`), the pristine checkout (`sfs_main/archive_2025_sfs_modified_src @ 9195c01`, upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865`), Pot A data (`sfs_main/original_samples/SfS_pp/Pot_A_*`, 8 sherds / 15 ground-truth edges per `class/data_path.h:1610–1707`), and the shipped Pot A assembly inputs as the answer key.
- **Blocked sources (reading them fails review):** `SfSpp_preprocessing` fork code (`edgeline_extraction*.cpp`, `mesh_processing_headless.cpp`, `sfs_axes/`), `.scratch/pota-repro/notes/task3-axes-plan.md`, issues/05 numbers and verdict. Tickets 01–04 per-pot census counts remain usable as data facts.
- **Target:** an axle finder that works on pots with no reference axles (Juglet and later scans). Success bar per ticket; final bar: direction ≤5° everywhere, position ≤2mm where the fragment spans enough shape (direction-strict, position-conditional — decided 2026-10-15: the P01/P04/P05 family proves a ~2-3mm material floor from handmade variation, recorded as floor not failure), then Gate 15/15 + E2E 8/8 + 15/15 at k=5/b=3.

## Done when

- Gate 15/15 + E2E 8/8 + 15/15 on Pot A with fresh chain, ORIG arm alongside.
- E1 updated with date: box checked, amended, or claim retracted.
