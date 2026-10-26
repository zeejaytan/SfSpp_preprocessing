# 20: Why five of the nine Juglet sherds produce no surface at all

**What to build:** the mechanism, piece by piece, for the five Juglet sherds that
the rebuilt preprocessing cannot turn into a surface — and the smallest change that
would restore them, costed but not implemented. Not a fix, and not a re-run for a
better number: a diagnosis that a conservator can follow and that says plainly
whether this is the method, the measurement, or the material.

**Answers:** U19 (the vessel-level claim) and E1 (its preprocessing half)

**Blocked by:** none

**Status:** in-progress
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
