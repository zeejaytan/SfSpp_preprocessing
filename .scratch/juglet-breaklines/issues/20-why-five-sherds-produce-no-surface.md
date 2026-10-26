# 20: Why five of the nine Juglet sherds produce no surface at all

**What to build:** the mechanism, piece by piece, for the five Juglet sherds that
the rebuilt preprocessing cannot turn into a surface — and the smallest change that
would restore them, costed but not implemented. Not a fix, and not a re-run for a
better number: a diagnosis that a conservator can follow and that says plainly
whether this is the method, the measurement, or the material.

**Answers:** U19 (the vessel-level claim) and E1 (its preprocessing half)

**Blocked by:** none

**Status:** ready-for-human
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 20-why-five-sherds-produce-no-surface, in /c/PR/worktrees/sfs/20

## What is already established (lead-verified, job 33834939)

Run `20261027-0055_d8af9d2_p07-juglet-stage1`, job **33834939** (sapphire,
COMPLETED 0:0, 5 min 18 s), commit `d8af9d2`, nine meshes from
`/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet/Piece0N.obj`.
Every number below was read by the lead out of the run directory, not out of a
worker report:

| piece | mesh verts | after 0.6 mm downsample | normal neighbours | clusters | outcome |
|---|---|---|---|---|---|
| 1 | 24294 | 14546 | 14 | 22 | surfaces written |
| 2 | 2568 | 1031 | 5 | 0 | nothing |
| 3 | 3495 | 1467 | — | 2 (169, 99) | fused by the merge to 1, nothing |
| 4 | 3651 | 1530 | — | 2 (242, 51) | surfaces written |
| 5 | 6212 | 3021 | — | 1 (679) | nothing |
| 6 | 5126 | 2351 | — | 2 | surfaces written |
| 7 | 8421 | 4254 | — | 5 | surfaces written |
| 8 | 4479 | 1988 | — | 2 (224, 196) | fused by the merge to 1, nothing |
| 9 | 2095 | 787 | — | 0 | nothing |

Sources: `out/juglet_pieces.tsv`, `out/juglet_attempts.tsv`,
`out/logs/Juglet_Piece_*.attempt-default.log`, `out/classify.tsv`.

Four facts that narrow it down:

1. **The clustering floor is not the reason.** `mesh_processing_headless.cpp:2559`
   sets `minCluster = 50`; `:2136` makes it `max(minCluster, max(30, Npts/500))`.
   Clusters of 99 and 169 points survive elsewhere in the same run, so a
   1031-point cloud yielding zero clusters is not a floor effect.
2. **The three "smoothness retries" were a no-op — the threshold was never wired to
   the code that runs.** With the paper chain on (default,
   `mesh_processing_headless.cpp:2568-2570`), segmentation goes to
   `growPaper234(cloud, normals, dynMinCluster, paperNB, paperTheta, paperKappa)`
   at `:2142`; `smoothnessAngleThreshold` is used only by the PCL region-growing
   branch at `:2156`. So pieces 3 and 8 give **identical** results at 3.0, 3.5 and
   4.5 deg (18.2686 % and 21.1268 % to four decimals, same cluster counts). The
   question "does loosening the smoothness help" has therefore not been tested at
   all.
3. **The merge fuses the only two clusters on pieces 3 and 8.**
   `[PAPER-234] appendix-A merge: rhoD=1.0000 rhoN=0.9500 rhoC=0.1000 rhoInN=0.7500
   rhoInC=0.2500 k1=10 k2=30`, then `pass 1: merge 99 into 169` / `merge 196 into
   224`, `pass 1 done: 1 clusters`, `Warning: Could not achieve 2 clusters after 1
   iterations. Final cluster count: 1`. Note `k2=30` against clusters of 99-224
   points.
4. **After that, the pipeline fails silently.** It looks for
   `Temp/Temp/Juglet/tmpSurfaceCluster_Improved_0.ply` and `_1.ply` and prints
   `Warning: Source file not found`, writes no surface, and the mesh stage still
   exits 0, so the piece is reported ABSENT rather than failed.

And one more, which matters for the whole Juglet plan: **the interior/exterior
classifier is blind on this material.** Pieces 1 and 6 read
`interior_frac=0.0000` on *both* faces, piece 7 reads 0.0000/0.3878, and only
piece 4 gives it evidence (0.0826/0.9412); on Pot A all eight pieces are decisive
(e.g. 0.9685/0.0000). Where it has no evidence it still emits a decision
(`swapped`), which the downstream code cannot tell apart from a decision it
made with evidence.

## The hypotheses, each with its own check

Work them in this order and mark each **supported** or **refuted** by evidence, not
by reading.

**H1 — normals.** Normal estimation degrades with density ("ADAPTIVE CGAL Using 20
neighbors for 85136 points" on Pot A piece 01, "5 neighbors for 1031 points" on
Juglet piece 2). With 5 neighbours a normal is close to noise, and the paper chain
tests normals at 3.4 deg. *Check:* sweep `SFS_PAPER_NB` (10 → 30 → 50) and
`SFS_PAPER_THETA` (3.4 → 5 → 8 → 12) on pieces 2, 9 and 5, one env-var variant per
run directory, and record cluster counts and sizes at each; then re-run pieces 3
and 8 at whatever setting works and see whether the two-cluster split survives.

**H2 — the merge is too eager on small clusters.** *Check:* for one fusing piece
(3 or 8) and one non-fusing piece (4 or 7), record the merge's own criterion values
against the thresholds (`rhoD=1.00`, `rhoN=0.95`, `k1=10`, `k2=30`) — which
criterion fires and by how much. Read Appendix A of the paper at the pinned text
(`C:/PR/papers/text/`) for what `rho_D`, `rho_N`, `rho_C` are, and say whether
applying them to 99-224-point clusters is inside their intended regime.

**H3 — one wall written off as two.** A sherd whose two visible walls genuinely are
one sheet (or where only one wall was scanned) will always end with one cluster, and
the code has no branch that reports it as an honest one-wall result. *Check:*
measure the mesh directly for pieces 2, 3, 5, 8, 9 — wall thickness in mm, number
of sheets found by a 2-3 mm ray/normal probe, and whether the two clusters found on
3 and 8 are geometrically two parallel sheets apart or one sheet split in two.
Answer from the mesh, not from the pipeline.

**H4 — the interior test needs evidence it cannot get.** *Check:* read the code that
produces `interior_frac` (`mesh_processing_headless.cpp:~1960-2050`) and identify
the quantity and threshold that makes both faces read 0.0000; then state what the
Juglet surfaces lack (point count? curvature? interior-facing dots?) and whether
"no evidence" could be reported instead of a silent size-order decision.

## Acceptance

1. For each of H1-H4: the artefact that bears on it, the measured values, and the exact
   log or file lines. **Do not write the verdict** — the lead marks supported or refuted;
   a worker reports evidence, never a judgement.
2. For each of the five silent pieces, the exact stage where it is lost (0 clusters
   / 1 cluster / fused to 1 / missing file) and the log line that shows it.
3. A sweep table: piece × (NB, theta) → cluster count and sizes, with the run
   directory named for every row.
4. The merge criterion that fires, its computed value against its threshold, for one
   fusing and one non-fusing piece.
5. **Renders** of the two clusters for piece 3 before the merge and of the same for
   Pot A piece 07, saved as pictures the conservator can look at, with a one-line
   caption each — geometry work is rendered before it is reported.
6. What would restore surfaces, costed (env change vs source change vs new stage),
   not implemented.
7. No tracked source changed (`git diff --stat main..<branch>` must show only this
   ticket), the frozen corpus md5 unchanged, geometry deleted with a counted record,
   ticket and `Status:` updated.

## What this cannot settle

Whether the Juglet reassembly would work even if every sherd produced a surface —
that is stage 2 of ticket 07, and it is paused. Nothing here is about Pot A, Pot D
or Pot H.

## Comments

**Worker evidence, 2026-10-27 — no verdicts; the lead marks H1–H4.** Full report with every
number, path and source line: `.scratch/juglet-breaklines/stage20/REPORT.md` (commit `64144c4`);
renders and captions: `.scratch/juglet-breaklines/stage20/renders/`; instruments:
`.scratch/juglet-breaklines/stage20/instruments/`.

Two completed jobs carry every number used here: **33836128** (53-variant sweep, COMPLETED 0:0
2 m 04 s, run `20261027-0136_ea1f11a_p20-sweep`) and **33836433** (density arm + analysis +
renders, COMPLETED 0:0 3 m 10 s, run `20261027-0148_f3896e4_p20-arm`). Three failures:
33836033 (my harness: stager restored 0644 from a `git archive`, exit 126 — nothing ran),
33836171 and 33836302 (my analysis instrument: `normal_x` against `nx`, then `clusters[0]` on a
zero-cluster piece). No number here comes from a failed job. Budget: 5 of 6 jobs used.

### Where each silent piece is lost (acceptance 2)

| piece | clusters printed | lost at | printout |
|---|---|---|---|
| 2 | 0 | growth | `Number of clusters is equal to 0`, 21 identical retries, `notfound=2` |
| 9 | 0 | growth | same |
| 5 | 1 (679) | `if (clusters.size() > 1)` at `:2200` is skipped; `:2316` builds cluster 0 and `break;`s | `Final cluster count: 1`, `notfound=2` |
| 3 | 2 (169, 99) | the appendix-A merge | `pass 1: merge 99 into 169`, `pass 1 done: 1 clusters`, `notfound=2` |
| 8 | 2 (224, 196) at the shipped defaults | the appendix-A merge | stage-1 run's table; my replay of that PLY fires the same criterion |

A sherd reaches a NURBS surface only if two clusters survive the merge: only then is
`pcl::io::savePLYFile(...tmpSurfaceCluster_Improved_0.ply/_1.ply)` reached (`:2289-2291`), and
otherwise `:2600-2612` prints two `Warning: Source file not found`.

### H1 — normals and density

`SFS_PAPER_NB` never reaches the normal estimation: all 13 piece-2 cells, 6 piece-3, 12 piece-5,
3 piece-8 and 12 piece-9 cells share one segmentation-input md5 (`A_segmentation_input.tsv`,
`distinct_md5_over_variants=1`), and every log prints `Using 5 neighbors for N points
(density-aware)` for the Juglet and `8` for Pot A 07 — the adaptive rule at
`mesh_processing_headless.cpp:420` (`max(5, min(20, N/1000))`) sits at its floor for all nine.
How much the estimate depends on neighbourhood size (`D_normal_density.tsv`, 5-NN against 20-NN
PCA normal at the same point): median 5.5°–13.0° across pieces, p90 22°–39°; the two
growth-starved pieces are the worst (piece 2 median 11.14°, piece 9 12.97°, 14.7 % of piece-9
normals above 30°) and the control is the best (`Pot_A_Piece_07` 0.88°). The density arm
(`arm_table.tsv`, target 19000 against `-1`) moves these clouds by ≤4 points
(2: 2564/2565, 3: 3490/3486, 5: 6211/6208, 8: 4478/4478, 9: 2094/2090) and changes no outcome:
because at target 19000 the band is `Bounds=[15200-22800]` and the clouds are 2.1k–6.2k points,
so `[DOWNSAMPLING RESULT] ... Result=2565 points` on piece 2 — the restore path and the raw cloud
are the same clouds.

### H2 — the merge on 99–224-point clusters

Appendix A (`C:/PR/papers/text/sfspp-2502.13986v1.md:464-479`): `k1=10`, `k2=30`,
`rho_d=1.0` mm, `rho_n=0.95`, `rho_c=0.1`, `rho_in,n=0.75`, `rho_in,c=0.25`, and "at least
three boundary point pairs must be detected". Measured on the pipeline's own PLYs
(`B_merge_criteria.tsv`): piece 3 (169/99) has **5** boundary pairs, min pair distance
**0.520166 mm** against 1.0, dot **0.970041** against 0.95, dCurv **0.000217** against 0.1,
internal dot **0.971461** against 0.75 — every criterion clear at once. Piece 8 (224/196): 4
pairs, 0.51495 mm, dot 0.961161, dCurv 0.010478, internal 0.782891/0.00693 — same. The
non-fusing comparison that *does* produce surfaces, `Pot_A_Piece_07`, fuses only (120, 71)
(7 pairs, dot 0.997768, internal 0.978151) and leaves every other pair at `too-few-pairs`; the
pair that comes closest to fusing without doing so is piece 7's (403, 263), stopped at
`rhoInN` 0.409647 against 0.75. One disagreement is recorded: my replay grows 244/51 on piece 4
where the pipeline prints 242/51, and there the replay fires and the pipeline does not.

### H3 — measured on the mesh

`C_mesh.tsv` (800 rays per piece, my own Möller–Trumbore intersector): pieces 2, 3, 4, 5, 7, 8, 9
are watertight two-sheet shells with median wall **2.09–2.90 mm**, 34–80 % of rays in the 1–3 mm
band, and every ray but a handful crossing at least two sheets; `Pot_A_Piece_07` is an open shell
(median 4.06 mm, 0.93 % in 1–3 mm). `B_two_clusters.tsv` pre-merge: on pieces 3 and 8 the two
clusters' mean normals point the **same** way (+0.741637 and +0.717114) and their nearest points
are **0.52 mm** apart; on `Pot_A_Piece_07` they are **antiparallel** (−0.998866) and 3.30 mm
apart. The code has no honest one-wall branch: with one cluster `:2316-2339` throws the cloud
away and breaks, and the only trace is the printed warning at `:2392-2396`.

### H4 — the interior test

`classifyAndOrderPaper234` (`:2004-2049`) counts, per face, the fraction of points whose normal
points toward the axis (`v.dot(nn) > 0` at `:2031`), then compares
`satA = inFrac[0]*n0 + (1-inFrac[1])*n1` with `satB = (1-inFrac[0])*n0 + inFrac[1]*n1` and swaps
on `satB > satA` (`:2041`). **There is no threshold and no third branch**: with both fractions
at 0.0000 the scores collapse to `satA = n1`, `satB = n0`, so the "interior" label is decided
by relative cluster size. That is the case for piece 1 (`interior_frac=0.0000` on both faces,
3489 and 626 points, `satA=626.0 satB=3489.0`) and for pieces 4 and 6 in their `axes` attempts.
The same evidence is axis-dependent: pieces 4, 6 and 7 each have two stage-1 attempts with
identical cluster sizes and different axes, and the fractions move — piece 6 from
`0.0822/0.2207` (boot axis) to `0.0000/0.0000` (axes), piece 7 from `0.1836/0.0000` to
`0.0000/0.3878`, piece 4 from `0.0000/0.0000` to `0.0826/0.9412`. The smallest margin measured
on a Juglet piece is 8 points out of 268 (piece 7 boot: 337 against 329; piece 3 in my replay:
138 against 130). Pieces 2, 5 and 9 never reach the test at all (`:2008`, fewer than two
clusters). Nothing in the code reports "no evidence".

### Renders (acceptance 5)

`.scratch/juglet-breaklines/stage20/renders/`: `Juglet_Piece_3.png` (118021 B) and
`Pot_A_Piece_07.png` (217871 B), plus the three theta-8 pieces; captions in `CAPTIONS.txt`.
Zoom scale **0.0414 mm/px** (31.06 mm across 750 px, 1 mm bar) on piece 3 and **0.0622 mm/px**
(46.65 mm, 1 mm bar) on Pot A 07 — a 1–3 mm separation is 24–72 px. On piece 3 the 169 and 99
point clusters lie on one arc side by side along z within one radial band (median s 2.492 against
3.298 mm, separation 0.805 mm, overlapping histograms); on Pot A 07 they are two parallel bands
(35.005 against 31.872 mm, separation 3.133 mm, disjoint).

### What would restore surfaces (acceptance 6, not implemented)

Costed in report §9: env only `SFS_PAPER_THETA=8` (piece 2 → 4 clusters, 9 → 2, 3 → 3, 5 → 6,
all with surfaces; ~2.3 s per piece, no rebuild; collateral on pieces 1, 4, 6, 7 and Pot A 07
**not measured**); env only `SFS_PAPER_CHAIN=0` (2 and 5 produce surfaces, 3, 8, 9 do not); a
source branch for the one-cluster case (`:2316-2339`, `:2600-2612`; one extra B-spline fit per
piece; needs a rebuilt binary — the container is fixed and each job builds the checkout);
removing the 21 identical retries (proved a no-op: `p3-sm3.0` and `p3-sm45.0` differ in exactly
one printed token, `smoothDeg=3.00000` against `45.00000`, and in nothing else); and a new stage
that decides interior/exterior from the mesh (`ray_hits`, ~1 s per piece) instead of the argmax.

### Accounting (acceptance 7)

No tracked source changed. Every staged input md5 unchanged in both completed runs
(`out/corpus_verdict.txt`: `yes (21 files)`): the 9 Juglet meshes and 9 clouds read from the
canonical checkout's `Dataset/{Mesh,Point}/Juglet/` (the frozen corpus has no Juglet entry) and
Pot A 07's mesh, cloud and axis from the frozen corpus; `corpus_md5_before.tsv` against
`corpus_md5_after.tsv` diff clean, rechecked on 2026-10-27. Geometry deleted with a counted record: sweep
832 files / 103619712 B, arm 140 files / 21217764 B, aborted job 300 files / 1378584 B. Index
rows for all five run directories with `verdict` and `human_note` empty. **One ledger wart:**
the aborted job 33836033 appended 50 per-variant rows before it died; the index is append-only,
so they stay and are declared void in `20261027-0131_bc58c3d_p20-sweep/out/VOID_VARIANT_ROWS.txt`.
