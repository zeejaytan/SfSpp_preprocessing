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
| 06 | Gate + E2E re-run with pristine controls | gate | issues/06-gate-e2e-rerun.md |
| 07 | Pristine PotSAC map (paper §IV-B2 → author files) | compliance | issues/07-pristine-potsac-map.md |
| 08 | Pristine axle failure repro (no fork in the loop) | gate | issues/08-pristine-axle-repro.md |
| 09 | Pristine axle repair (smallest fix that finds the shipped axles) | gate | issues/09-pristine-axle-repair.md |
| 10 | Axle generalisation (held-out pieces, then pots B–J) | gate | issues/10-axle-generalise.md |

## Pristine-only axis path (added 2026-10-15, binding on tickets 07–10)

Tickets 05's verdict is quarantined: it compared fork code against fork (NURBS) references, so it says nothing about whether the *author's* path is fixable. Tickets 07–10 re-derive from scratch.

- **Allowed sources:** the paper text (`papers/text/sfspp-2502.13986v1.md`), the pristine checkout (`sfs_main/archive_2025_sfs_modified_src @ 9195c01`, upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865`), Pot A data (`sfs_main/original_samples/SfS_pp/Pot_A_*`, 8 sherds / 15 ground-truth edges per `class/data_path.h:1610–1707`), and the shipped Pot A assembly inputs as the answer key.
- **Blocked sources (reading them fails review):** `SfSpp_preprocessing` fork code (`edgeline_extraction*.cpp`, `mesh_processing_headless.cpp`, `sfs_axes/`), `.scratch/pota-repro/notes/task3-axes-plan.md`, issues/05 numbers and verdict. Tickets 01–04 per-pot census counts remain usable as data facts.
- **Target:** an axle finder that works on pots with no reference axles (Juglet and later scans). Success bar per ticket; final bar: direction ≤5°, position ≤2mm vs shipped Pot A axles on held-out pieces, then Gate 15/15 + E2E 8/8 + 15/15 at k=5/b=3.

## Done when

- Gate 15/15 + E2E 8/8 + 15/15 on Pot A with fresh chain, ORIG arm alongside.
- E1 updated with date: box checked, amended, or claim retracted.
