# 51 — cap the growth angle by the measured cheapest crossing

## Why

The curvature formula (`theta = k * S/R_fold`, k = 3.3573, ticket 43/45) sets the growth
angle from the WALL's fold radius. But growth fails when theta exceeds the CHEAPEST
smooth bridge between the two wall faces — and that bridge is not always the wall:

- Juglet Piece 1 is a complete 360-degree rim (largest angular gap 0.2 deg). Its binding
  bridge is the intact lip (roll radius ~2.6 mm), tighter than the wall fold (5.93 mm).
  Any k above R_wall/R_lip ~ 2.3 glues at the lip; k = 3.36 overshoots: formula gives
  10.2 deg, the real threshold is 6.5-7.0 deg (threshold sweep 20261031-2145).
- Worn break edges are also smooth bridges cheaper than the formula assumes.

Measured evidence (run 20261031-2007_158ddc6_t50-edge, edge50.tsv): the graph-model
cheapest crossing (Kruskal, k=10 NN, curvature < 1.0, angle where the largest component
first reaches 60% of eligible points) predicted the real pipeline thresholds closely:
J1 7.0 vs real 6.5-7.0; PA08 4.3 vs real 4.0-4.5; Pot A PA01-06 8.1-10.0 vs real 8.1-9.9.

So: measure the crossing on the piece's OWN growth cloud, at runtime, and cap theta.

## Change

In `mesh_processing_headless.cpp`, in the formula path (where medianFoldRadius45 runs,
the `[GROWTH-45]` block near :4745), add a measured cap:

1. Build the k-nearest-neighbour graph on `downsampledCloudWithNormals` (k = 11,
   same KdTreeFLANN already used). For each directed edge, the angle between the two
   point normals, in degrees. Edges eligible only when BOTH curvatures < 1.0
   (same kappa as growth).
2. Kruskal union-find over edges sorted by ascending angle. Track the size of the
   largest component. `thetaCross51` = the edge angle at which the largest component
   first reaches 60% of the points that have at least one eligible edge.
3. Cap: when `SFS_GROWTH_CAP` is set to `1` (default: off — do not change default
   behaviour), `paperTheta = min(paperTheta, 0.9 * thetaCross51)`.
4. Log one line: `[GROWTH-51] crossing=<deg> capped=<0|1> theta=<deg>` right after
   the existing `[GROWTH-45]` line. If fewer than 1000 points have eligible edges,
   log `crossing=none` and do not cap.

Constraints:
- The change is confined to the formula path (env-gated by SFS_GROWTH_FORMULA=1
  AND SFS_GROWTH_CAP=1). Default behaviour byte-identical when either env is unset.
- No new library dependencies. Use the existing Eigen/std containers.
- Complexity: ~1.1M edges, sort + union-find is milliseconds. Do not slow the
  measurable path otherwise.

## Run

One run, 17 pieces (Juglet 1-9, Pot A 01-08), corpus clouds (MANIFEST_JUGLET_CC.tsv
gate as in ticket 48), TWO arms per piece in ONE job:

- arm C (cap): SFS_GROWTH_FORMULA=1, SFS_GROWTH_CAP=1
- arm U (uncapped control): SFS_GROWTH_FORMULA=1 (identical to ticket 48 run)

Per cell record: piece, arm, rc, theta used ([GROWTH-51] line), crossing, outcome
([STATUS-23]), cluster sizes, surface point counts. After the run, score PAIR QUALITY
with `runs/20261031-2046_158ddc6_t50-theta45/paircheck45.py` (med_nn, med_across,
med_angle). Genuine pair bar: med_across < 0.05 mm and med_nn within 30% of the known
wall thickness (Juglet walls 2.0-3.3 mm, Pot A 3.6-8.3 mm).

## Predictions (falsifiable)

- J1 arm C: crossing ~7 deg, theta capped 10.2 -> ~6.3, outcome two, genuine pair.
- J1 arm U: theta 10.2, outcome none (glued) — same as ticket 48.
- Pot A arm C: crossing 8-10 deg > formula 4.4-8.1, capped=0, identical to arm U.
- Juglet J2-J9 arm C: capped where crossing < formula; two faces where ticket 48
  gave none or garbage.

## Acceptance

- [x] Diff confined to mesh_processing_headless.cpp (formula path) + stage51/** + this ticket.
- [x] Default behaviour unchanged: SFS_GROWTH_CAP unset -> [GROWTH-45] path identical,
      no [GROWTH-51] line.
- [x] Run COMPLETED 0:0; 34 cells (17 pieces x 2 arms); corpus gate 9/9 (pcd_md5 AND
      kept_points vs MANIFEST_JUGLET_CC.tsv); corpus.diff/inputs.diff empty.
- [x] [GROWTH-51] line present in all 17 arm-C cells; crossing values within 1.5 deg of
      edge50.tsv glue60 where that table covers the piece (J1-9, PA01-04).
- [x] Arm-U cells reproduce ticket 48's theta_computed to 2 dp (same clouds, same code path).
- [x] Verdict table: per piece, arm C vs U outcome + pair quality, in the ticket write-back.

## Out of scope

- Changing the default growth angle or spacing (ticket 50's lane).
- Touching the merge pass, breaklines, or anything downstream of growth.

## Result — the cap works on every piece, and Pot A does not notice

Run `20261101-0210_863d4f8_t51-cap`, job `34132847`, COMPLETED 0:0 in 00:10:20, built from
`863d4f8`. 34 cells (17 pieces x arms C cap / U uncapped), `pipeline_rc` 0 on all 34, corpus
gate 17/17 (9 Juglet rows matched `MANIFEST_JUGLET_CC.tsv` on `pcd_md5` AND `kept_points`;
8 Pot A rows recorded as the control), `corpus.diff` and `inputs.diff` both 0 bytes,
`GEOMETRY_DELETED.txt` 58 files before / 58 after.

### The cap fires on the Juglet and only there

| piece | formula theta | crossing | capped theta | outcome C | outcome U (uncapped) |
|---|---|---|---|---|---|
| J1 | 10.84 | 6.645 | **5.980** | two 43,394 + 55,121 | two, but 421 + 84,190 — a junk second surface |
| J2 | 11.04 | 5.975 | **5.378** | two 24,176 + 20,926 | none (one cluster 31,541) |
| J3 | 8.96 | 6.492 | **5.843** | two 25,951 + 27,669 | two, but 881 + 36,390 |
| J4 | 9.75 | 8.072 | **7.265** | two 40,035 + 30,882 | none |
| J5 | 9.31 | 8.135 | **7.322** | two 31,634 + 39,591 | two, but 1,268 + 46,661 |
| J6 | 8.86 | 7.895 | **7.106** | two 34,651 + 34,228 | two, but 1,706 + 40,438 |
| J7 | 9.79 | 6.198 | **5.579** | two 40,004 + 51,334 | none |
| J8 | 9.47 | 8.534 | **7.681** | two 39,428 + 33,527 | none |
| J9 | 9.50 | 6.157 | **5.541** | two 27,299 + 34,658 | none |
| Pot A 01-08 | 2.88-5.71 | 4.378-9.869 | **unchanged** | two, 8/8 | two, 8/8 |

The cap fires on 9 of 9 Juglet pieces (reduction 1.8-5.7 deg) and 0 of 8 Pot A pieces: every
Pot A formula theta was already below 0.9 x its own crossing, which is the prediction and it
held. Pot A arm C vs arm U surface counts differ by 0-6 points on 8 of 8 pieces — the cap does
not disturb the pieces that already worked.

`[GROWTH-51]` printed in 17/17 arm-C cells and 0/17 arm-U cells, so the default path is
untouched. Arm U reproduces ticket 48's `theta_formula` to the printed precision on 17/17,
which is the control that the only thing changed between arms is the cap.

### Are the pairs genuine? Yes, on all nine — and this corrects a mistake of mine

Pair quality (`pairquality51.tsv`, arm C): med_nn 1.81-2.97 mm, med_across 0.003-0.013 mm,
med_angle 9.0-22.2 deg. Arm U's surviving second surfaces: med_nn 6.3-26.8 mm,
med_across 5.0-9.9 mm, med_angle 38.9-69.7 deg — 500-3000x worse across.

I first read the cross-section figure (`artifacts/t51-cap/t51_xsec.png`) as showing J4, J6,
J8 and J9 "dipping into each other", i.e. partly a split of one face. That reading was wrong.
Projecting a doubly-curved shell onto one global principal axis is not a wall cross-section: the
fold bends the section, so two correctly separated surfaces can appear to cross. The direct
measurement, B-to-A nearest-neighbour distance over every point of every piece:

| piece | median separation | as % of wall | points closer than 0.1 mm |
|---|---|---|---|
| J1 | 1.96 mm | 96% of 2.05 | 2.1% |
| J2 | 2.27 | 84% of 2.69 | 0.00% |
| J3 | 2.00 | 82% of 2.45 | 0.00% |
| J4 | 2.05 | 78% of 2.63 | 0.10% |
| J5 | 2.51 | 85% of 2.96 | 0.00% |
| J6 | 2.36 | 90% of 2.62 | 0.03% |
| J7 | 2.97 | 91% of 3.26 | 0.00% |
| J8 | 1.81 | 84% of 2.16 | 0.01% |
| J9 | 2.06 | 79% of 2.59 | 0.19% |

Every piece separates at 78-96% of its own measured wall thickness, with at most 2.1% of points
in contact. That is a wall pair, not a split face. Figure of record:
`artifacts/t51-cap/t51_wallsep.png` (per-piece separation histograms against the wall line),
rendered after the correction.

### What this does and does not settle

It settles that **the growth step now yields two wall surfaces on every Juglet sherd**, which
ticket 48 could not do (0 of 9 clean). It does **not** settle that the Juglet goes back
together: that is U19's seating score, and it still needs the end-to-end assembly run. The cap
also does not rescue the worn-edge story on its own — it replaces the guess about how worn an
edge is with a measurement of the piece in hand, which is why it transfers where the curvature
formula alone did not.

`SFS_GROWTH_CAP` is **default off**. Flipping it to default-on is a separate, one-line change
plus a confirming run, and is left to the conservator's decision.

### Verification (lead)

```
verified: accept51.py after 3 lead-side fixes -> ACCEPT51 PASS (A 19 files, B gate env-read
          default off, C [GROWTH-51] present, D py_compile 9 / bash -n 3, E 34 rows caps
          consistent, F crossings within 1.5 deg of edge50 glue60)
verified: thetas51.tsv rows 1-34 -> arm U theta == theta_formula on 17/17; arm C capped=1 on
          9/9 Juglet and capped=0 on 8/8 Pot A; pipeline_rc 0 on 34/34
verified: surfaces/*_Surface_0/1.ply, cKDTree B->A over 9 pieces -> med 1.81-2.97 mm,
          78-96% of wall40.py wall thickness, frac<0.1mm 0.00-2.1%
verified: run 20261101-0210_863d4f8_t51-cap/out/corpus.diff, inputs.diff -> 0 bytes each
verified: edge50.tsv vs arm-C crossing -> max |delta| 0.69 deg (PA04), inside the 1.5 deg bar
```

Three defects in my own acceptance check were fixed before it could pass: a Windows GBK decode
crash (fixed with `encoding="utf-8", errors="replace"`); check E reading the committed 24-row
REFERENCE table instead of the run's 34-row output (fixed by taking the run dir as `argv[2]`);
and a 1e-6 cap tolerance tighter than the 5-dp printing (relaxed to 2e-4). An acceptance check
that fails a correct implementation is itself the defect.

### Figures

- `artifacts/t51-cap/t51_wallsep.png` — per-piece separation histograms with the wall line; the
  evidence for the table above.
- `artifacts/t51-cap/t51_pairs.png` — surface 0 vs surface 1, face-on and edge-on, six pieces.
- `artifacts/t51-cap/t51_xsec.png` — along-the-wall vs across-the-wall sections. Read this one
  with the caveat above: it misled me once.

Status: done
Working in: chat on Thinkbook16 (2026-11-01)
Branch: 51-cap-the-growth-angle-by-the-measured-cheapest-crossing, in /c/PR/worktrees/sfs/51
Worker: 304e201f-d2cb-4251-92c5-b7519507d910 - built the C++ cap, the stage51 instruments and
        submitted the run; lead verified, wrote the verdict and corrected the pair-quality
        reading
