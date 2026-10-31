# 49 — make the fold radius scale-free, then re-derive k

## What to build

Ticket 48 proved the curvature law `theta = 3.3573 x S / R_fold` does not transfer from the clouds it
was calibrated on to the corpus clouds, and located the cause: **the fold radius is not
spacing-invariant.** `medianFoldRadius45()` takes the `k = 30` nearest neighbours, which is not a fixed
physical patch — it is a patch whose radius is proportional to the point spacing. At the ticket-45
calibration spacing that patch measured 0.63-1.04 mm across the nine Juglet pieces; on the corpus
clouds it measures 0.36-0.97 mm, a ratio down to 0.58x. Comparing curvature over patches that change
size with the input is what produced `R ~ S^0.22` and `theta ~ S^0.78` (ticket 48, "Why the prediction
failed"), and it is why a single constant could not carry the law between the two inputs.

This ticket makes the measurement **scale-free**: measure the fold radius over a fixed *physical*
diameter instead of a fixed *number* of neighbours, then re-derive the constant k on the corpus clouds
and test the resulting law on both vessels.

**Answers:** U19

**Blocked by:** 48 (the diagnosis this ticket acts on) — resolved.

**Status:** ready-for-agent

**Worker:** unassigned

## The change

1. **Fixed-diameter neighbourhood.** In `medianFoldRadius45()` (`mesh_processing_headless.cpp:1098`,
   neighbour search at `:1117`), replace `nearestKSearch(p, kNN45, ...)` with `radiusSearch(p, R_PATCH_MM,
   ...)`, keeping the rest of the estimator byte-for-byte (PCA tangent frame, bivariate quadric by least
   squares, ridge `1e-12 * trace`, larger principal curvature, radius `1/kmax` clipped to
   `[0, RHO_CAP_MM = 60]`, median over the deterministic 20 000-point stride). The estimator's arithmetic
   must not change — only which points it sees.
2. **`R_PATCH_MM` is a measured choice, not a taste.** The ticket-45 calibration used `k = 30` at
   spacings of 0.202-0.341 mm, i.e. patches of radius 0.63-1.04 mm (table in ticket 48's close-out). The
   candidate values to test are **1.0 mm** (the calibration's own patch size, nearest round number) and
   **1.5 mm** (a larger patch that averages more surface, less sensitive to a single fold). The ticket
   must report both and say which the evidence prefers — not pick one silently.
3. **Degenerate-neighbour guard.** A radius search on a sparse cloud can return too few points for a
   6-parameter quadric fit. Keep the existing `< 4` skip, and **log the count of skipped points** per
   piece (`[GROWTH-45] skipped=...`) so a piece whose R rests on a handful of usable patches is visible
   in the record rather than silently averaged.
4. **Re-derive k on the corpus clouds.** With R scale-free, k is no longer a calibration constant carried
   from another input — it must be fitted again. Do it the ticket-43 way: on the pieces where a genuine
   wall pair exists (ticket 44's six Juglet wall pairs and Pot A's eight), fit k so that the grown pair
   is the wall's two faces. Report the fitted k with its spread and n, and **state whether the same k
   serves both vessels** — if Pot A and the Juglet want different k, that is the finding, not a nuisance.

## The test

Two runs, both source-identical apart from the change above:

1. **Corpus clouds (the failing case).** Nine Juglet cells + eight Pot A control, `SFS_GROWTH_FORMULA=1`.
   The bar: every piece grows two surfaces, and the grown pair is the **wall's two faces** — separation
   comparable to the measured wall thickness (J2 2.693, J3 2.452, J5 2.900, J7 3.263, J9 2.595 mm;
   ticket 44's pairs sat 0.38-0.63 mm across, which is two layers of ONE face, not a wall).
2. **The calibration clouds (the regression case).** The ticket-45 arm must still reproduce its own
   numbers — the change must not silently move the case that already worked. Report the theta and
   outcome per piece against ticket 45's table.

If the fixed-diameter radius makes the pair separate to wall scale on the corpus clouds **and** keeps the
calibration case intact, the law becomes portable and ticket 45's default flip can be reconsidered. If it
does not, report where it lands and stop — as in ticket 48, that is the measurement speaking.

## Honesty lines this ticket carries

- **The 0.2-0.3 mm pair is the thing under test.** Tickets 44 and 46 both grew pairs that sit ~0.2-0.3 mm
  apart against a 2.4-3.3 mm wall. Neither ticket's bar could see that, because both were scoring the
  *angle*, not the *pair*. This ticket scores the pair.
- **A larger patch is not automatically better.** A 1.5 mm patch spans a real fold less faithfully than a
  1.0 mm one; the two candidates exist to expose that trade, not to be averaged.
- **k re-fitted on the same pieces that are then scored is a fit, not a test.** Report the fit and the
  score separately, and say plainly that the seating question (ticket 07) is untouched by both.

## Acceptance

- [ ] `radiusSearch` replaces `nearestKSearch` in `medianFoldRadius45()`; the estimator's arithmetic is
      otherwise unchanged (diff shows only the neighbour query, the skip counter and the new log field).
- [ ] `R_PATCH_MM` tested at 1.0 and 1.5 mm, both reported with per-piece R, theta, outcome and pair
      separation; the preference stated with its evidence.
- [ ] Skipped-point counts logged per piece; no piece silently rests on a handful of patches.
- [ ] k re-derived with its spread and n, per vessel and pooled; the same-k question answered explicitly.
- [ ] Corpus-cloud run: 9 Juglet + 8 Pot A, `SFS_GROWTH_FORMULA=1`, every piece's outcome and pair
      separation recorded against its measured wall thickness.
- [ ] Calibration-cloud regression: ticket-45's numbers reproduced or the drift quantified.
- [ ] `run.json` and index rows for every job (verdicts left empty), poll + final `sacct` recorded.
- [ ] Worker reports numbers and paths; the lead runs its own hidden acceptance check before close.

**Needs-eye:** a 3x3 grown-surface panel on the corpus clouds, and the same for the calibration clouds,
so the two can be compared side by side.

## Comments
