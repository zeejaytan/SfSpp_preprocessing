# Spec — Pot A reproduction (preprocessing side)

**Answers:** E1

**Prior work searched:** GitHub "SfSpp_preprocessing DominicoRyu", "Structure-from-Sherds SfS++ 2502.13986"; papers/text/sfspp-2502.13986v1.md. Found: https://github.com/DominicoRyu/SfSpp_preprocessing (pin d5ee6865) — or: nothing else found.

**Status:** spec for slicing; tickets 01–06 below slice the work

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

## Done when

- Gate 15/15 + E2E 8/8 + 15/15 on Pot A with fresh chain, ORIG arm alongside.
- E1 updated with date: box checked, amended, or claim retracted.
