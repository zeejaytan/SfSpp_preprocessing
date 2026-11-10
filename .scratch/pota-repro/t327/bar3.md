

### Bar 3 — the pre-2026-10-31 bundle: what still exists, and what it said

**What still exists.** The pre-1031 Juglet runs are nine directories under
`/data/gpfs/projects/punim2657/SfSpp/runs/`: `20261027-0055_d8af9d2_p07-juglet-stage1`,
`20261027-0227_4cbb2b2_juglet-two-walls`, `20261027-0300_4cbb2b2_juglet-raw-vs-improved`,
`20261027-0320_0c28ae2_juglet-armgrid22`, `20261027-0331/0336_d4f2187_juglet-armgrid22(-rep2)`,
`20261027-0551_81d76c2_juglet-2x2`, `20261027-0659_cc9c6d9_t30-arm4-control-jug3p4`,
`20261029-0017_bdbd8b8_t41-juglet`, `20261029-0444_835fc1c_t42-juglet`. Per-piece **geometry** survives in
two of them only: `20261027-0659_cc9c6d9_t30-arm4-control-jug3p4/out/arms/t30-arm4-control-jug3p4/Juglet/Juglet_Piece_N/{surfaces,breaklines,logs}`
and `20261029-0017_bdbd8b8_t41-juglet/out/cells-pipeline/Juglet_Piece_N_armA..D/surfaces`. Everything else
was culled to counts and logs (`GEOMETRY_DELETED.txt`, `geometry_counts.tsv`); `t42-juglet` keeps only a
`packed-20261103.tar.gz` + MANIFEST, `juglet-two-walls` only `two_walls.tsv`/`NOTES.md`. The **old input
clouds** are archived at `SfSpp/attic/20261031-juglet-vertex-dumps`, so the pre-1031 clouds exist but the
per-piece surface exports mostly do not.

**What the surviving two say** (my own script `.scratch/pota-repro/t327/census327_old.py`, output
`artifacts/pota327/census_bar3_old.json`, same GT-axis instrument as bar 1; frame confirmed the same way —
centroids 2.8-15.0 mm off the GT line, z spans in −551..−476):

| bundle | piece | r_mean S0 | r_mean S1 | Surface_0 | note |
|---|---|---|---|---|---|
| t30 (2026-10-27) | 1 | 11.349 | 13.510 | inner | mesh log: both faces inFrac 0.0000, decided by size |
| t30 | 4 | 17.369 | 15.299 | **outer** | |
| t30 | 6 | 16.459 | 17.025 | inner | |
| t30 | 7 | 14.454 | 11.128 | **outer** | |
| t41 armA (2026-10-29) | 1 | 10.054 | 12.927 | inner | |
| t41 | 4 | 16.221 | 15.299 | **outer** | |
| t41 | 5 | 10.647 | 15.143 | inner | |
| t41 | 6 | 16.386 | 17.063 | inner | |
| t41 | 7 | 13.703 | 9.114 | **outer** | |
| t41 | 8 | 14.273 | 15.272 | inner | |

- **Pre-1031 the inverted set was {4, 7}; piece 6 was filed correctly then; pieces 2 and 9 could not be
  asked at all** — on the vertex-dump clouds the pipeline produced **zero** surfaces for them
  (`t41` `status_raw.tsv`: P2 "no temp surface; final clusters=0 sizes=none" after 21 merge passes, P9
  clusters=0; `t30`: P2 1031 pts / P9 787 pts, both clusters=0, and P3/P5/P8 collapsed to one cluster).
- So the misfiling set **moved** with the 2026-10-31 cloud regen and the chain change: {4,7} → {2,6,9}. That is
  a bundle-to-bundle comparison, not a controlled cloud-only A/B (old bundles also run a different commit and
  recipe), so it locates the change in time; it does not attribute it.
- The old runs already staged the **same axis file family** the t66 run used — `t41` `inputs.md5` REAL-AXIS
  `6066ab7374d91292403662fa1870f494` for `sfs_preprocessing/Dataset/Axes/Juglet/Juglet_Piece_2_Axis.xyz`,
  byte-identical to t66's P2 row — so the wrong-side axis on pieces 2 and 9 is not new.
- The old mesh logs show the same unguarded vote degenerating: `t30` P6 `face0 n=365 frac=0.0822 / face1
  n=213 frac=0.2207 -> satA=196 satB=382 -> swapped`, and P1/P4 with **both** faces at `frac=0.0000`, where
  the decision falls to the size term alone (P4: `satA=51 satB=242`). P1 also prints
  `Normals flipped: true` — the flip path of bar 2 was already in play on the old clouds.
