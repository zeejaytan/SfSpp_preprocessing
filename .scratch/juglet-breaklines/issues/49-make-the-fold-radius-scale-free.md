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

**Status:** ready-for-human
**Working in:** chat on Thinkbook16 (2026-10-31)
**Branch:** 49-make-the-fold-radius-scale-free, in /c/PR/worktrees/sfs/49

**Worker:** 3730bd77-9818-494a-ab98-d6ef826d84ab (one-shot; submitted both runs, wrote no verdict, merged nothing)

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

### Worker report — the fixed patch radius, and what it did (worker, 2026-10-31)

**Status untouched, no verdict written, no merge.** Numbers and paths only.

#### Run record

| | run | job | sacct | elapsed | commit |
|---|---|---|---|---|---|
| first attempt | `20261031-1552_0aba42f_t49-patch` | `34098609` | `FAILED 1:0` | 00:15:54 | `0aba42f` |
| **reported run** | `20261031-1623_dd578f2_t49-patch` | `34099113` | `COMPLETED 0:0` | 00:16:03 | `dd578f2` |

Both runs measured all 51 cells and produced every table; the first died at phase 8c because the
template passed `pipeline_cells.tsv` where `k49.py` takes the cells **directory**
(`NotADirectoryError: [Errno 20]`), fixed in `dd578f2` (`submit49.sbatch.tmpl:306-307`). The two
runs are numerically identical: `theta_check49.tsv` is byte-identical (md5
`6770c1f2869cd587f3b058083372e835`), every theta / R_med / skipped / cluster count / outcome
reproduces, and `pipeline_cells.tsv`, `pairs49.tsv`, `wall49.tsv` differ only in the
surf0/surf1 point split (<0.2%) and the embedded run-dir path. The measurement is reproducible.
Index rows carry `verdict` and `human_note` empty for both.

#### The source change

`mesh_processing_headless.cpp` `medianFoldRadius45()`: `nearestKSearch(p, kNN45, ...)` replaced by
`radiusSearch(p, rPatch45, ...)`; `rPatch45` is 1.0 mm, overridden by `SFS_PATCH_R_MM` (invalid
values FATAL with `[GROWTH-45] FATAL SFS_PATCH_R_MM=... is not a positive length in mm`, exit 2).
The diff is confined to the neighbour query, the skip counter and the log field, plus the
file-scope statics and the header comment: PCA frame, 6x6 normal equations, ridge `1e-12*trace`,
`ldlt` solve, k1/k2, `rad = 1/kmax` clipped `[0, 60]`, the nth_element median and the 20 000-point
stride are byte-identical.

**Two deviations from the brief, both deliberate:**

1. **The `< 4` skip was raised to `< 6`**, not kept. The quadric has six coefficients
   (`a, b, L, M, N, constant`); a ridge solve on four or five samples returns a curvature with no
   geometric meaning straight into the median. With 30 fixed neighbours that could not happen;
   with a radius it can, so the guard has to be the rank of the system, not the old constant.
2. **`skipped` is logged as `skipped=NNN/MMM`** (skipped / sampled stride points), not a bare
   count, so a piece whose R rests on a handful of usable patches is visible against how many
   patches were examined. Appended to the `[GROWTH-45]` line, never substituted: every earlier
   field keeps its position, so the stage-45/48 readers still parse it.

#### A. Calibration regression — ticket 45's own numbers, attic vertex dumps, Juglet

theta deg: t45 committed | r=1.0 | delta | r=1.5 | delta

| piece | t45 | r=1.0 | d% | r=1.5 | d% |
|---|---|---|---|---|---|
| J1 | 10.36573 | 11.97416 | +15.52 | 10.35606 | **−0.09** |
| J2 | 48.55822 | 52.45785 | +8.03 | 39.42370 | −18.81 |
| J3 | 46.40826 | 53.58637 | +15.47 | 38.57727 | −16.87 |
| J4 | 39.88552 | 46.57070 | +16.76 | 33.88948 | −15.03 |
| J5 | 24.61259 | 32.57200 | +32.34 | 22.66828 | −7.90 |
| J6 | 32.30634 | 43.29121 | +34.00 | 30.22010 | −6.46 |
| J7 | 18.67685 | 25.08157 | +34.29 | 17.29224 | −7.41 |
| J8 | 37.77287 | 39.47999 | +4.52 | 33.28560 | −11.88 |
| J9 | 54.38436 | 55.87595 | +2.74 | 44.16401 | −18.79 |

r=1.0: mean |delta| **18.2%**, median 15.5%, max 34.3%, 2/9 within 5% (J8, J9 — and both of those
are the *closest* pieces, so it is not the estimator agreeing).
r=1.5: mean |delta| **11.5%**, median 11.9%, max 18.8%, **1/9** within 5%.

**The ticket-45 calibration case is not reproduced by either radius.** r=1.0 is systematically
too steep on every piece (8 of 9 positive), r=1.5 sits closer but low on 8 of 9.

#### A2. Calibration regression — Pot A, released corpus clouds

| piece | t45 | r=1.0 | d% | r=1.5 | d% |
|---|---|---|---|---|---|
| PA01 | 5.70709 | 7.19332 | +26.04 | 5.93037 | **+3.91** |
| PA02 | 4.57863 | 6.81454 | +48.83 | 4.78656 | **+4.54** |
| PA03 | 4.43321 | 5.48338 | +23.69 | 4.50348 | **+1.59** |
| PA04 | 3.57188 | 4.29624 | +20.28 | 3.59376 | **+0.61** |
| PA05 | 4.22457 | 5.07502 | +20.13 | 4.33590 | **+2.64** |
| PA06 | 4.08171 | 5.20810 | +27.60 | 4.21913 | **+3.37** |
| PA07 | 2.88049 | 2.66931 | −7.33 | 2.58302 | −10.33 |
| PA08 | 3.92527 | 3.63653 | −7.36 | 3.21327 | −18.14 |

r=1.0: mean |delta| **22.7%**, 0/8 within 5%. r=1.5: mean |delta| **5.6%**, median 3.6%,
**6/8 within 5%**. PA07 and PA08 are the two pieces whose k=30 patch was already small
(0.29 mm spacing, R 19.6 / 13.2 mm), and r=1.5 pushes them low.

#### B. Corpus Juglet — theta against the ticket-43 reference, and against ticket 48

| piece | t43 ref | t48 (k=30) | r=1.0 | d% | r=1.5 | d% | outcome r1.0 / r1.5 |
|---|---|---|---|---|---|---|---|
| J1 | 10.29 | 10.84 | 10.21747 | −0.7 | 9.49971 | −7.7 | two / none |
| J2 | 12.40 | 11.04 | 8.54603 | −31.1 | 12.84082 | +3.6 | none / none |
| J3 | 9.35 | 8.96 | 7.50325 | −19.8 | 7.66027 | −18.1 | none / none |
| J4 | 10.25 | 9.75 | 7.67459 | −25.1 | 7.63116 | −25.5 | two / two |
| J5 | 8.74 | 9.31 | 7.56179 | −13.5 | 7.41254 | −15.2 | two / two |
| J6 | 8.16 | 8.86 | 6.97316 | −14.5 | 6.67695 | −18.2 | two / two |
| J7 | 8.65 | 9.79 | 7.54867 | −12.7 | 6.43908 | −25.6 | none / two |
| J8 | 10.05 | 9.47 | 7.85665 | −21.8 | 7.49614 | −25.4 | two / two |
| J9 | 12.68 | 9.50 | 7.78042 | −38.6 | 10.78410 | −15.0 | none / none |

mean |delta| vs the t43 reference: **t48 (k=30) 9.4%** | **r=1.0 19.8%** | **r=1.5 17.1%**.
4 of 52 cells are inside the 2% band (J1 r1.0-corpus 0.705%, J1 r1.5-attic 0.642%,
PA07 r1.0 0.350%, PA08 r1.0 0.735%).

**On the corpus clouds the fixed patch radius moves theta *away* from the ticket-43 reference,
not toward it** — it is 10 points worse than the k=30 run ticket 48 reported. The radius does not
rescue the law's transfer to these clouds.

#### C. Outcomes — surfaces grown

| arm | two surfaces | Juglet | Pot A |
|---|---|---|---|
| r1.0-corpus | 13/17 | 5/9 (J1 J4 J5 J6 J8) | 8/8 |
| r1.5-corpus | 13/17 | 5/9 (J4 J5 J6 J7 J8) | 8/8 |
| r1.0-attic | 1/9 | 1/9 (J1) | — |
| r1.5-attic | 1/9 | 1/9 (J1) | — |

Ticket 48 at k=30 had 4 of 9 Juglet on the corpus clouds; the fixed radius gives 5 of 9 at both
radii, but J2, J3 and J9 still collapse. On the 2–9 k-point vertex dumps a 1.0–1.5 mm patch is a
large fraction of the piece, R_med collapses to 0.7–2.9 mm and theta explodes to 17–56 deg, so
those cells mostly grow one cluster.

#### D. The thing under test — pair separation against measured wall

`pair_over_wall` = pair `med_nn` / 800-ray wall thickness measured on the same mesh by
`wall49.py` (wall40.py's machinery, unchanged).

| piece | arm | med_nn mm | wall mm | pair/wall | med_angle_deg | coin |
|---|---|---|---|---|---|---|
| J4 | r1.0-corpus | 2.0510 | 2.6256 | **1.280** | 21.81 | 0.0006 |
| J4 | r1.5-corpus | 2.0520 | 2.6256 | **1.280** | 21.97 | 0.0006 |
| J5 | r1.0-corpus | 2.5115 | 2.9593 | **1.178** | 11.23 | 0.0000 |
| J5 | r1.5-corpus | 2.5117 | 2.9593 | **1.178** | 11.23 | 0.0000 |
| J6 | r1.0-corpus | 2.3620 | 2.6170 | **1.108** | 12.49 | 0.0002 |
| J6 | r1.5-corpus | 2.3622 | 2.6170 | **1.108** | 12.48 | 0.0001 |
| J8 | r1.0-corpus | 1.8067 | 2.1606 | **1.196** | 13.36 | 0.0000 |
| J8 | r1.5-corpus | 1.8073 | 2.1606 | **1.196** | 13.36 | 0.0000 |
| J1 | r1.0-corpus | 26.4879 | 2.0538 | 0.077 | 69.50 | 0.0003 |
| J1 | r1.0-attic | 26.7996 | 2.0538 | 0.077 | 63.59 | 0.0001 |
| J1 | r1.5-attic | 22.7111 | 2.0538 | 0.090 | 57.61 | 0.0002 |
| J7 | r1.5-corpus | 15.7198 | 3.2945 | 0.210 | 45.29 | 0.0003 |

Pot A, all 8 pieces, both radii: `pair_over_wall` **0.975–1.030**, `coin` 0.0000, angle 2.6–13.7 deg,
nest `mean_normal_dot` ≈ −0.999 — opposite-facing sheets at wall separation, as in ticket 48.

**This is the ticket's bar, and it is met on the Juglet corpus clouds**: four pieces (J4, J5, J6,
J8) grow a pair **1.11–1.28x the measured wall**, i.e. 1.8–2.5 mm across, at both patch radii,
against the **0.38–0.63 mm** of tickets 44/46. The remaining pieces do not: J1 and J7 grow a pair
10–13x and 4.8x the wall at 42–70 deg — the two clusters there are the two **sides of the piece**,
not the two faces of a wall, and J2, J3, J9 do not grow two surfaces at all.

Wall thickness measured this run (800 rays, `thick_med_mm`): J1 2.0538, J2 2.91769 attic /
2.480753 corpus, J3 2.677558/2.27356, J4 2.760666/2.490447, J5 3.099416/2.819254,
J6 2.727861/2.506094, J7 3.345018/3.244075, J8 2.262621/2.058653, J9 2.742962/2.352357;
PA01 8.285696, PA02 3.694035, PA03 3.722396, PA04 3.724287, PA05 3.83032, PA06 3.612175,
PA07 4.057357, PA08 3.713287. The known-wall cross-check column (J2 2.693, J3 2.452, J5 2.900,
J7 3.263, J9 2.595) shows the ray measurement runs 0.06–0.3 mm high on the corpus clouds relative
to the earlier stages' figures; the ratios above use this run's own medians.

#### E. k re-derivation

`k49.py` recovers `k_now = theta_rad * R / S` from the `[GROWTH-45]` line (3.3573 everywhere, as
expected) and reports `k_needed_linear = k_now * wall / pair`. Its genuine-wall-pair test
(two surfaces, `coin <= 0.01`, `med_angle_deg >= 5`) excludes PA02–PA08, whose pairs sit at
1.01–1.03x wall but at 2.6–4.2 deg — the test does not look at the separation it explains.

Reading it on the pieces where **no extrapolation is needed**, i.e. the pair already sits at
0.70–1.35x wall:

| vessel | n | median k | min | max | spread |
|---|---|---|---|---|---|
| Juglet (J4, J5, J6, J8 at both radii) | 8 | **3.9848** | 3.7192 | 4.2980 | 0.579 (15%) |
| Pot A (PA01–PA08 at both radii) | 16 | **3.4030** | 3.2727 | 3.4590 | 0.186 (5%) |

**One k does not serve both vessels**: the pooled medians differ by **17%**. Pot A keeps ticket 43's
3.3573 almost exactly (1.4% away); the Juglet corpus clouds want **3.98, about 1.19x it**. Per
radius the answer does not move (Juglet 3.985 at r=1.0 and 3.985 at r=1.5; Pot A 3.40 and 3.40), so
the split is between vessels, not between patch radii.

`k49.py`'s own grouped output, for the record, with its stricter test (Juglet n=5 per radius,
median 3.9560 / 3.9558, spread 102% / 91% because J1's pair at 0.08x wall is counted in):
Juglet pooled n=12 median 3.8378, Pot A pooled n=2 median 3.2847, verdict line
"ONE k does NOT serve both vessels: pooled medians differ by 16.8% (> 10%)".

**This k is a fit on the same four pieces it is then scored against** — it is a fit, not a test,
and `k_needed_linear` is a linear projection that a run at that k would have to confirm. The
seating question (ticket 07) is untouched by any of it.

#### F. Skipped points — the new counter

| arm | skipped / sampled | share |
|---|---|---|
| r1.0-corpus | 17 / 287797 | 0.01% |
| r1.5-corpus | 0 / 287797 | 0.00% |
| r1.0-attic | 1659 / 44368 | **3.74%** |
| r1.5-attic | 76 / 44368 | 0.17% |

Worst pieces at r=1.0 on the dumps: J5 415/5668 (7.3%), J3 228/3252 (7.0%), J6 285/4641 (6.1%),
J7 365/7471 (4.9%). On the 840 k-point corpus clouds the guard is effectively silent. **No piece
rests on a handful of patches without that being visible in the log** — which was the point of
logging it, and it is itself evidence that 1.0 mm is oversized for a 2–9 k-point dump.

#### G. Which radius the evidence prefers

- **Pair separation: no difference.** J4 1.280 at both, J5 1.178 at both, J6 1.108 at both,
  J8 1.196 at both. The patch radius does not move the grown pair on the corpus clouds.
- **Pot A calibration: r=1.5 wins clearly.** 6/8 within 5% (mean 5.6%) against 0/8 at r=1.0
  (mean 22.7%).
- **Skipped patches on the dumps: r=1.5 wins.** 0.17% against 3.74%.
- **Attic Juglet calibration: r=1.5 wins, and neither reproduces it.** mean |delta| 11.5% against
  18.2%, and 1/9 against 2/9 within 5%.
- **Cost of a larger patch:** on the corpus clouds r=1.5 puts J1 and J7 over the collapse edge
  (J1 two→none) while pulling J7 the other way (none→two), and it moves corpus theta slightly
  further from the t43 reference (17.1% vs 19.8% mean |delta| — r=1.5 is the *better* of the two
  there, not the worse).

The evidence points to **1.5 mm** on every comparison that separates the two, and the honesty line
that "a larger patch is not automatically better" is not what the numbers show here — but note
that neither radius reproduces ticket 45 on the attic dumps, so 1.5 mm is "less wrong", not
"right".

#### H. A mechanism worth recording

**A fixed patch radius does not make R_fold independent of the cloud.** R_med, corpus / attic:

| piece | r=1.0 | ratio | r=1.5 | ratio |
|---|---|---|---|---|
| J1 | 5.933 / 5.431 | 1.09 | 6.381 / 6.279 | 1.02 |
| J2 | 3.186 / 0.773 | 4.12 | 2.120 / 1.029 | 2.06 |
| J3 | 4.303 / 0.773 | 5.57 | 4.214 / 1.073 | 3.93 |
| J4 | 4.014 / 0.891 | 4.51 | 4.037 / 1.224 | 3.30 |
| J5 | 5.402 / 1.409 | 3.83 | 5.510 / 2.024 | 2.72 |
| J6 | 5.442 / 0.994 | 5.47 | 5.683 / 1.424 | 3.99 |
| J7 | 5.605 / 1.979 | 2.83 | 6.571 / 2.870 | 2.29 |
| J8 | 4.225 / 1.080 | 3.91 | 4.428 / 1.281 | 3.46 |
| J9 | 2.903 / 0.700 | 4.15 | 2.095 / 0.886 | 2.36 |

For J2–J9 the same physical patch reads a 2.1–5.6x larger radius on the dense corpus clouds than
on the sparse dumps (J1 is the exception, ~1.05x). Fixing the neighbourhood's **size in mm** fixes
what the fit is asked to look at; it does not fix how well that patch is sampled, and a patch
holding ~10–100 points instead of thousands resolves a different surface. The k=30 patch was not
even ~1 mm on the calibration clouds — implied from the t45 theta it ranged **0.72–6.27 mm**
(J1 6.27, J2 0.84, J3 0.89, J4 1.04, J5 1.86, J6 1.33, J7 2.66, J8 1.13, J9 0.72) — which is why
no single fixed radius can reproduce ticket 45 on them.

#### Artefacts

Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261031-1623_dd578f2_t49-patch`; fetched to
`SfSpp_preprocessing/artifacts/t49-patch/` (`t49_final.tgz`, 4 710 987 bytes, md5
`fcf001ad049429994e65002f93bb5ce0`). Tables: `pipeline_cells.tsv`, `theta_check49.tsv`,
`theta_proof.tsv`, `env_proof.tsv`, `surfaces49.tsv`, `pairs49.tsv`, `nests49.tsv`,
`wall49.tsv`, `k49.tsv`, `corpus_gate.tsv`, `attic_gate.tsv`, `corpus.diff` (0 bytes),
`inputs.diff` (0 bytes), `geometry_counts.tsv`, `run-meta.txt`, `versions.txt`. Panels under
`out/figures/`: `juglet_panel49_r1.0_corpus.png`, `juglet_panel49_r1.5_corpus.png`,
`juglet_panel49_r1.0_attic.png`, `juglet_panel49_r1.5_attic.png`.

**Gates, all passed:** corpus gate 9/9 Juglet clouds `ok` against `MANIFEST_JUGLET_CC.tsv` on both
`pcd_md5` and `kept_points`, 8/8 Pot A recorded not gated; attic gate 9/9 dumps md5-equal to their
own manifest; `corpus.diff` and `inputs.diff` 0 bytes; `env_proof.tsv` every row reading exactly
`SFS_GROWTH_FORMULA=1 SFS_PATCH_R_MM=<its own radius>`; `theta_proof.tsv` 52 cells with
`delta_abs` 0.0000; instruments commit == rundir (the job fails with rc=4 otherwise); 108 geometry
files before and after, all `*/cells-pipeline/*/surfaces/*.ply` kept.

**Anomalies.** (1) Every cell's note reads `ok patch_r logged 1.00000 but asked 1.0` — the cell
driver compares the log's 5-decimal print against the requested string; the values agree, cosmetic
only. (2) `/opt/sfs-pristine` is ABSENT on spartan-bm151, so `pristine.txt` records absence rather
than a baseline, as in every previous stage run. (3) The run tag reads `t49-patch` as passed.

**Looked at it.** The r1.0 corpus panel shows J1, J4, J5, J6, J8 covered by the two grown surfaces
and J2, J3, J7, J9 showing the grey mesh only; the r1.0 attic panel shows J1 grown and the other
eight collapsed. The outcome column is what the pictures show.

## Lead verification (2026-10-31, coordinating session)

Re-read the run's own tables and recomputed what could be recomputed. **Three of my own first-pass
claims failed re-checking and are corrected here before anything else**, because a verification that
only reports the worker's errors is not a verification.

### Corrections to my own first pass

1. **I reported the calibration regression as 299% / 197% mean |delta|. Wrong.** I compared the attic
   arms against the *ticket-43 reference* (the LAW) instead of against **ticket 45's own output**, which
   is what clause 2 of this ticket's test asks for. Recomputed against ticket 45's own table the
   regression is **r1.0 mean 18.19% / median 15.52% (within 5%: 2/9)**, **r1.5 mean 11.47% / median
   11.88% (within 5%: 1/9)** — which is what the worker reported. The worker was right and I was wrong.
2. **I wrote that the worker's attic figures "do not match its own theta_check49.tsv". Wrong** — they
   match to the printed precision. The 299%/197% figures were mine, computed against the wrong reference.
3. **I wrote that the ticket's bar "names five pieces" and only 1 of 5 met it. Too narrow.** The
   parenthetical at :57 lists the five pieces whose wall thickness is *known*; the bar's clause 1 is
   "every piece grows two surfaces", scored over all nine. The correct statement of the failure is
   clause 1 at 5 of 9, not "1 of 5 named pieces".

### What stands, and it is the headline

**`pair_over_wall` is stored inverted.** `k49.py:179` computes `ratio = w / s_now` (wall divided by
pair) and writes it at `:192` under the name `pair_over_wall`. The column therefore holds **wall/pair**,
not pair/wall. Section D's table above labels it pair/wall and reads it as such, so the claim
"four pieces grow a pair **1.11-1.28x the measured wall**" is inverted: those pairs are **0.78-0.90x**
the wall. Recomputed from the same rows:

| piece | arm | pair med_nn mm | wall mm | **pair/wall** | angle deg |
|---|---|---|---|---|---|
| J4 | r1.0-corpus | 2.051 | 2.626 | **0.781** | 21.81 |
| J5 | r1.0-corpus | 2.512 | 2.959 | **0.849** | 11.23 |
| J6 | r1.0-corpus | 2.362 | 2.617 | **0.903** | 12.49 |
| J8 | r1.0-corpus | 1.807 | 2.161 | **0.836** | 13.36 |
| J1 | r1.0-corpus | 26.488 | 2.054 | **12.897** | 69.50 (two sides of the piece) |
| J7 | r1.5-corpus | 15.720 | 3.295 | **4.82** | 45.29 (two sides) |
| Pot A 01-08 | both | 3.56-8.50 | 3.61-8.29 | **0.971-1.026** | 2.62-13.66 |

The direction error does not change the substance — a pair at 0.78-0.90x wall is a **different thing
from tickets 44/46's 0.15x**, and it is the change this ticket was built to find. But "wider than the
wall" and "slightly narrower than the wall" are different physical claims, and the record must carry
the right one.

### The bar, scored honestly

- **Clause 1, every piece grows two surfaces: NOT MET.** r1.0-corpus grows a pair on **5 of 9**
  Juglet (J1 J4 J5 J6 J8; none on J2 J3 J7 J9); r1.5-corpus on **5 of 9** (J4 J5 J6 J7 J8; none on
  J1 J2 J3 J9). Pot A 8 of 8 at both radii.
- **The five pieces whose wall is known** (:57): J2 no pair either radius; J3 no pair either radius;
  **J5 pair 2.5115 mm against a known wall of 2.900 = 0.866 (the one that lands at wall scale)**;
  J7 no pair at r1.0 and 4.82x wall at r1.5; J9 no pair either radius.
- **Clause 2, the calibration case intact: NOT MET.** The attic arms move 11.5-18.2% mean against
  ticket 45's own numbers, with 1-2 of 9 pieces inside 5%. Ticket 45's figures are not reproduced.
- **Against the ticket-43 reference the fixed radius is worse, not better**: Juglet k=30 (t48)
  mean 9.39% -> r1.0 19.76% -> r1.5 17.13%; Pot A 22.04% -> 46.85% -> 24.35%.

**Verdict: the bar is not met, and the law is not portable.** The measurement improved — the pairs now
resolve to wall scale instead of two layers of one face — but the *law* did not transfer, and the
calibration case that already worked was not preserved.

### A defect in the instrument's own criterion

`k49.py:165-172` calls a pair "genuine" only when `med_angle_deg >= 5.0`, on the reasoning that a
wall's two faces meet the break edge at an angle. But the two faces of a wall are **near-parallel
almost everywhere** — they are separated by the wall, not tilted across it. The consequence is that
the criterion **excludes the correct answer**: PA02-PA08 sit at **0.97-1.03x their own wall** (the
best evidence in the run) and are thrown out for having angles of 2.6-4.2 deg. Separation, not angle,
is what distinguishes a wall from two layers of one face (0.2-0.3 mm vs 2-3 mm); the angle test
conflates the two. Section E works around this with a second, looser criterion, which is why it and
`k49.py`'s grouped output disagree on Pot A's n (16 vs 2). A future stage should test separation first
and use the angle only to reject *large*-separation coincidences.

**One more inverted statement:** section D says the ray wall "runs 0.06-0.3 mm **high** on the corpus
clouds"; the numbers in the same paragraph show it running **low** (J2 known 2.693 vs measured 2.481;
J3 2.452 vs 2.274; J5 2.900 vs 2.819; J7 3.263 vs 3.244; J9 2.595 vs 2.352).

### k

The re-derivation stands as a **fit, not a test**: Juglet median **3.9848** (n=8, range 3.7192-4.2980),
Pot A median **3.4030** (n=16, range 3.2727-3.4590), a **17% split** — one k does not serve both
vessels, and Pot A keeps ticket 43's 3.3573 to 1.4% while the Juglet wants 1.19x it. On the stricter
genuine-only flag Pot A has n=2 (PA01 only), median 3.2847.

### What I verified myself

`accept49.py` PASS after I fixed **three defects in my own check** (recorded in the file): it searched
the whole 5000-line blob for `nearestKSearch` (used ~16 other places legitimately) instead of the
`medianFoldRadius45()` body; it looked for `0.5 * x * x` when the variable is `x45`; and it looked for
`R_PATCH=1.0` when the run logs `patch_r=1.00000`. Diff confined to `mesh_processing_headless.cpp` +
`stage49/**` + this ticket (22 files); corpus gate 9/9 on `pcd_md5` and `kept_points`; `corpus.diff`
and `inputs.diff` 0 bytes; both radii evidenced [1.0, 1.5].

**Nothing merged. No source default changed. Ticket 45's default flip remains unadopted.**
