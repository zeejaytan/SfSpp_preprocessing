# Stage 34 — `SFS_NORMAL_CARRY=nearest` (ticket 34): what ran and what it measured

Ticket: `.scratch/juglet-breaklines/issues/34-carry-the-nearest-normal.md` (branch `34-carry-the-nearest-normal`).
The one switch: `SFS_NORMAL_CARRY=mean|nearest`, default `mean`, effective only when `SFS_NORMAL_SOURCE=input`.
`nearest` gives every sampled point the unit normal of its nearest source point verbatim — no averaging ball,
no MST, the source sign kept; a point with no usable source normal is counted and filled from the pipeline's
own PCA estimate, never silently.

## Jobs

| job | run directory | slurm id | sacct | cells |
|----|----|----|----|----|
| 1 | `20261027-1046_4099ee3_t34-nearest-carry` | 33876722 | COMPLETED 00:04:59 | 70 of 70 wrote cell.tsv |
| 2 | `20261027-2159_bb3f67d_t34-mean-baseline` | 33876941 | COMPLETED 00:02:26 | 14 of 14 wrote cell.tsv |

Both under `/data/gpfs/projects/punim2657/SfSpp/runs/`. Each appended its index row with `verdict` and
`human_note` **empty** (`20261027-1046_4099ee3_t34-nearest-carry 33876722 4099ee3… t34-nearest-carry <TAB><TAB>`).

Arms of job 1 — AO `908a750` (pre-change binary, no switches), A `4099ee3` (this commit's binary, no switches),
A2 (A again), B `SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest`, C = B + `SFS_SINGLE_CLUSTER=write`.
Pieces: Juglet 1, 2, 3, 5, 7, 9 and Pot A 01–08. Shipped floor and merge everywhere; no ceiling ladder.
Arm M of job 2 — `SFS_NORMAL_SOURCE=input` with `SFS_NORMAL_CARRY` **unset** (the default `mean`), on the same 14 pieces.

## The decisive measurement — median folded angle of the carried normals to the mesh

`carried34.tsv`, identical at rung `r1_downsampled` and `r2_clusters_premerge` in all 140 rows.

| piece | A (pipeline) | A2 | mean carry (ticket 33 arm B, reproduced by arm M) | **nearest carry (B = C)** |
|----|----|----|----|----|
| Juglet 1 | 2.364556 | 2.364556 | 1.646342 | **0.402294** |
| Juglet 2 | 8.100984 | 8.100984 | 9.441063 | **1.402148** |
| Juglet 3 | 6.106812 | 6.106812 | 7.034291 | **1.168996** |
| Juglet 5 | 4.002534 | 4.002534 | 4.490551 | **0.889034** |
| Juglet 7 | 3.392134 | 3.392134 | 3.866934 | **0.848680** |
| Juglet 9 | 9.011419 | 9.011419 | 9.952567 | **1.541745** |
| Pot A 01 | 1.030409 | 1.030409 | 0.797698 | **0.594607** |
| Pot A 02 | 0.995141 | 0.995141 | 0.792184 | **0.578226** |
| Pot A 03 | 0.748103 | 0.748103 | 0.653303 | **0.520739** |
| Pot A 04 | 0.644423 | 0.644423 | 0.562790 | **0.455450** |
| Pot A 05 | 0.721578 | 0.721578 | 0.608528 | **0.482448** |
| Pot A 06 | 0.743750 | 0.743750 | 0.614159 | **0.475136** |
| Pot A 07 | 0.712556 | 0.712556 | 0.694484 | **0.538747** |
| Pot A 08 | 0.889239 | 0.889239 | 0.894819 | **0.610801** |

AO = A = A2 in every row: no run-to-run spread on this instrument. Nearest carry lands at **0.40–1.54 deg on
the Juglet**, inside the 0.41–1.64 deg band the input clouds themselves carry (ticket 32), against 8.10 (pipeline)
and 9.44 (mean carry) on piece 2. On Pot A it is 0.455–0.611 against 0.644–1.030.

## What arm M adds: the mean path is unchanged, bit-for-bit

Arm M is the default carry run through **this commit's binary**, and it reproduces ticket 33's arm B exactly:

* carried fold-to-mesh: 9.441063 / 7.034291 / 4.490551 / 3.866934 / 9.952567 on Juglet 2, 3, 5, 7, 9 and
  0.694484 on Pot A 07 — every one equal to ticket 33's printed number to all six decimals (delta +0.000000);
* the pair statistic: Juglet 5 `2.944130 / 9.693411` (ticket 33: 2.944 / 9.693), Juglet 7
  `4.188686 / 12.366719` (ticket 33: 4.189 / 12.367), Pot A across 0.236419–0.265588 (ticket 33: 0.236–0.266).

So the new switch's default path is the old path, measured on two independent instruments rather than asserted.

## Criterion 3 — "nearest proven nearest"

`missing=0` and `carried=npts` on **all 14 pieces in both B and C**, at every call into the normal stage
(164 `[NORMAL-33]` lines — 3 calls per piece on twelve of the pieces, 23 on the two largest Pot A pieces):
none with a missing point, none with `carried != npts`. Example (arm B, Juglet 2):

```
[NORMAL-33] piece=Juglet_Piece_2 call=0 source=input carry=nearest npts=1031 carried=1031 nearest=1031 missing=0 median_dev_to_pca_deg=7.10507 missing_fill=pca mst=not_applied carry_radius_mm=0.60000 source_n=2565
```

The second half of the criterion — *deviation from the pipeline's PCA larger than in mean mode on the folding
pieces* — is only partly met, and the in-run comparison (mean from arm M, nearest from job 1 arm B) says so:

| piece | mean (arm M) | nearest (arm B) | nearest − mean |
|----|----|----|----|
| Juglet 1 | 1.62660 | 2.35025 | **+0.72365** |
| Juglet 2 | 7.73226 | 7.10507 | −0.62719 |
| Juglet 3 | 5.73999 | 5.57039 | −0.16960 |
| Juglet 5 | 4.03482 | 3.69164 | −0.34318 |
| Juglet 7 | 3.58219 | 3.17382 | −0.40837 |
| Juglet 9 | 7.64315 | 8.12052 | **+0.47737** |
| Pot A 01–06 | 0.26942–0.45103 | 0.35117–0.63476 | **+0.0818 … +0.2268** |
| Pot A 07 | 0.46406 | 0.46371 | −0.00035 |
| Pot A 08 | 0.58631 | 0.57702 | −0.00929 |

Larger on 7 pieces (Juglet 1, Juglet 9, Pot A 01–06), smaller on the four folding Juglet pieces 2, 3, 5, 7 and
on Pot A 08. The reading: the PCA estimate is the thing that is wrong on those four pieces (8.10, 6.11, 4.00,
3.39 deg from the mesh), and the averaging ball is dragged by the fold in the same direction as PCA, so the
mean stays *closer* to a bad reference than a copied source normal does. The criterion's first instrument —
the folded angle to the mesh — is the one that decides, and there the carry is inside the input's own band.

## Segmentation, arm by arm (cells34.tsv; every cell exit=0, meas_exit=0)

| piece | AO / A / A2 | B / C |
|----|----|----|
| Juglet 1 | 22 pre → 18 post, two surfaces 3580 / 12092 | 18 → 15, two surfaces 1422 / 8147 |
| Juglet 2 | **0 clusters, 21 retries, nothing written** | **0 clusters, 21 retries, nothing written** |
| Juglet 3 | 2 → 1 (268), nothing written | 1 → 1 (316), nothing written; **C writes it: 797 pts** |
| Juglet 5 | 1 → 1 (679), nothing written | 2 → 2 (65, 652), two surfaces 250 / 1620 |
| Juglet 7 | 5 → 4 (403, 263, 68, 65), two 1012 / 829 | 9 → 5 (295, 445, 225, 73, 71), two 1049 / 1197 |
| Juglet 9 | **0 clusters, 21 retries** | **0 clusters, 21 retries** |
| Pot A 01–08 | two surfaces 8 of 8 in every arm | two surfaces 8 of 8 in every arm |

Juglet 2 and 9 produce **no cluster at all** in any arm, so `SFS_SINGLE_CLUSTER=write` had nothing to write on
either; the switch does bite on Juglet 3 (one cluster, 797-point surface, 2 mm coverage 0.974520, folded angle
0.894747 deg) and on Juglet 5 (two clusters where the pipeline keeps one).

### Every merge line (68 events across 38 of the 70 cells)

Extracted from each cell's `logs/mesh.log` (`[PAPER-234] pass N: merge <size> into <size>`; the notation below is
`p<pass>:<into>+<merged>`); AO, A and A2 are identical, as are B and C.

```
A/AO/A2  Juglet_Piece_1   p1:274+102  p1:164+64  p1:151+133  p2:376+53
A/AO/A2  Juglet_Piece_3   p1:169+99
A/AO/A2  Juglet_Piece_7   p1:326+77
A/AO/A2  Pot_A_Piece_01   p1:697+203
A/AO/A2  Pot_A_Piece_02   p1:751+211  p2:962+221
A/AO/A2  Pot_A_Piece_03   p1:829+100
A/AO/A2  Pot_A_Piece_07   p1:120+71
A/AO/A2  Pot_A_Piece_08   p1:194+90
B/C      Juglet_Piece_1   p1:177+51  p1:104+68  p1:103+51
B/C      Juglet_Piece_7   p1:258+101  p1:214+81  p1:137+88  p2:359+86
B/C      Pot_A_Piece_02   p1:125+120
B/C      Pot_A_Piece_04   p1:371+139  p1:164+139  p1:128+107
B/C      Pot_A_Piece_05   p1:311+118
B/C      Pot_A_Piece_06   p1:11047+149  p1:124+95
B/C      Pot_A_Piece_08   p1:189+82  p1:138+127
```

These reproduce ticket 33's shipped-default regions: piece 3 `[169, 99] → [268]`, piece 7
`[326, 263, 77, 68, 65] → [403, 263, 68, 65]`.

## The pair statistic (ticket 30's ruler: median step along Surface_0's own normal / across it / coincidence at 1 um)

Pot A, every arm — the standing bar (along 3.5–7.1 mm, across 0.13–0.27 mm, coincidence 0.0000) holds 8 of 8:

| piece | AO / A / A2 along / across | B / C along / across |
|----|----|----|
| 01 | 7.089350 / 0.270923 | 7.069705 / 0.266096 |
| 02 | 3.631529 / 0.251293 | 3.633153 / 0.247401 |
| 03 | 3.671245 / 0.244389 | 3.672217 / 0.242680 |
| 04 | 3.656681 / 0.237421 | 3.658825 / 0.235793 |
| 05 | 3.766851 / 0.250533 | 3.764524 / 0.249038 |
| 06 | 3.547105 / 0.256264 | 3.548322 / 0.253126 |
| 07 | 3.919588 / 0.248680 | 3.917081 / 0.248351 |
| 08 | 3.603650 / 0.250306 | 3.597655 / 0.253918 |

Coincidence 0.000000 in all 40 Pot A pairs. The one number outside the quoted upper edge is Pot A 01 in
AO/A/A2 at 0.270923 mm — 0.0009 mm over 0.27, and 0.266096 in B/C.

Juglet "pairs" (patches in different places, not real pairs) — across 4–12 mm as before:

| piece / arm | along | across | coincidence |
|----|----|----|----|
| 1, A (and AO/A2) | 0.367769 | 4.198927 | 0.325174 |
| 7, A (and AO/A2) | 0.643408 | 4.295400 | 0.262967 |
| 1, B/C | 4.334815 | 12.705216 | 0.070087 |
| 5, B/C | 3.779366 | 11.044544 | 0.087037 |
| 7, B/C | 2.231944 | 7.901371 | 0.029240 |
| 1, M (mean) | 1.855852 | 11.714778 | 0.059300 |
| 5, M (mean) | 2.944130 | 9.693411 | 0.091084 |
| 7, M (mean) | 4.188686 | 12.366719 | 0.102273 |

The arm A piece 7 row (0.643408 / 4.295400) is ticket 33's own number, so the instrument is proven against the
earlier grid. Nearest carry moves the Juglet pair statistic in the right direction (piece 7 across 12.37 → 7.90)
but has not made a real pair out of any Juglet surface.

## Per surface (surfaces34.tsv: points / bbox diagonal mm / 2 mm coverage / folded angle deg)

Arm A and arm B, both surfaces where two exist:

| piece | A s0 | A s1 | B s0 | B s1 |
|----|----|----|----|----|
| Juglet 1 | 3580 / 39.650 / 0.274 / 1.775 | 12092 / 54.405 / 0.710 / 1.907 | 1422 / 30.297 / 0.160 / 0.257 | 8147 / 55.145 / 0.578 / 0.273 |
| Juglet 5 | — | — | 250 / 16.524 / 0.123 / 0.465 | 1620 / 39.375 / 0.461 / 0.414 |
| Juglet 7 | 1012 / 27.482 / 0.197 / 1.124 | 829 / 28.240 / 0.168 / 1.157 | 1049 / 31.973 / 0.204 / 0.509 | 1197 / 33.687 / 0.257 / 0.502 |
| Pot A 01 | 66764 / 164.648 / 0.434 / 0.734 | 57299 / 169.259 / 0.395 / 0.829 | 66262 / 164.670 / 0.435 / 0.480 | 58058 / 169.560 / 0.396 / 0.512 |
| Pot A 04 | 32683 / 111.175 / 0.482 / 0.566 | 35789 / 114.160 / 0.523 / 0.547 | 33062 / 111.372 / 0.483 / 0.424 | 36297 / 114.173 / 0.523 / 0.415 |
| Pot A 07 | 6066 / 53.981 / 0.486 / 0.566 | 6437 / 55.360 / 0.523 / 0.484 | 6215 / 53.425 / 0.483 / 0.477 | 6557 / 55.699 / 0.524 / 0.389 |

(The full 140-row table is `out/surfaces34.tsv`; arm C equals arm B except Juglet 3's single surface and
Pot A 03's 43938-point Surface_1.) Every surface's folded angle falls under the nearest carry, and the
Pot A geometry — points, diagonal, coverage — is unchanged to within the sampler's own jitter.

## The defaults proof (criterion 2)

* `<piece>_SampledWithNormals.ply`, **28 comparisons** = 14 pieces × 2 pairings (AO vs A, and A vs A2):
  **28 byte-identical** (md5 equal), sorted point set identical, point counts equal, `max_abs_diff` 0.0.
  This is `out/defaults2.tsv`, check `surface`.
* segmented `[STATUS-23]`/`[RETRY-23]` lines, same 28 pairings: 19 identical line for line; the 9 that differ
  differ **only** in `surf0_points`/`surf1_points` (the random ray-cast surface sampler), never in
  `outcome`, `clusters`, `sizes`, `retries` or `floor` — Pot A 01 66760 vs 66764, 02 42199 vs 42207, etc.
* surface PLYs (not part of the criterion, and the reason the criterion is written the way it is): md5 differs
  in **all 40** pairs including A vs A2, i.e. two runs of one binary do not agree, as ticket 33 found.
* with every switch unset the `[NORMAL-33]` line is **not printed at all** (`lines34.tsv` has 82 rows in B and
  82 in C, zero in AO/A/A2), so the default output is unchanged at the line level too.

## Inputs, corpus and the pristine path (criterion 6)

* `inputs_before.md5` = `inputs_after.md5`: **221 rows, diff empty**, in both jobs (corpus clouds and meshes,
  the axis files, the boot axes, the SIF, all instruments, both binaries).
* `corpus_before.txt` = `corpus_after.txt`: **1803 rows, diff empty** (job 1; job 2 likewise).
* `/opt/sfs-pristine` recorded **ABSENT** from the compute node in both jobs (`out/pristine.txt`).

## What was deleted, and the record written first (criterion 7)

Job 1: `out/GEOMETRY_DELETED.txt` was written **before** the delete — per-cell `logs/geometry_counts.tsv`
records each stage directory and rung dump (path, ext, files, bytes) and each count is written by
`run_cell34.sh` before `rm -rf`; the file then records the build trees: **6288 files, 380 436 810 bytes**
deleted, 0 remaining. Job 2: **3153 files, 190 333 014 bytes**. `out/GEOMETRY_KEPT.txt` lists the cells whose
geometry was kept because measurement failed: **count 0** in both jobs.

Locally, the fetched surface PLYs, `mesh.log` files and both binaries were deleted after the tables were
extracted (`results/` holds 0 `.ply` and 0 `mesh.log`, 3.0 MB of tables); the surfaces themselves stay in the
run directories on Spartan. The unqualified counted record for that local fetch is the run's own
`GEOMETRY_DELETED.txt` / `geometry_counts.tsv` pair, written before its delete; the local copy was removed
after the fact and no separate pre-delete count was taken of it.

## Acceptance criteria, one line each

1. Switch exists, default `mean`, printed per cell (`run.json`, `cell.tsv` field 4, `[NORMAL-33] carry=`): **met**.
2. Defaults proof, switch unset: 28 sampled-PLY comparisons, 28 byte-identical, both pairings: **met**.
3. Nearest proven nearest: `missing=0`, `carried=npts` on 14/14 pieces — **met**; "deviation from PCA larger
   than mean on the folding pieces" — **not met on Juglet 2, 3, 5, 7** (larger on 1, 9 and Pot A 01–06), see the
   table above; the folded-angle-to-mesh instrument is met with 0.40–1.54 deg.
4. Every arm × piece cell reports exit, regions before/after, merge lines, surface measurements: **met**
   (`cells34.tsv` 23 fields per cell + the merge lines above + `surfaces34.tsv`).
5. Pot A 8/8 two surfaces in every arm, along 3.5–7.1, across 0.13–0.27, coincidence 0.0000: **met**, with one
   number 0.0009 mm over the quoted upper edge (Pot A 01 at 0.270923 in AO/A/A2).
6. Corpus and staged inputs md5 identical, pristine ABSENT: **met**.
7. Geometry deleted with the counted record written first: **met** in the run directories; the local fetch's
   record is reconstructed, not pre-written.
8. Index rows appended with verdict and human_note empty: **met**, both jobs.
9. No tracked file touched but `mesh_processing_headless.cpp` and `.scratch/juglet-breaklines/stage34/`;
   no verdict, no merge, no `intent/` write: **met** (see `git diff --stat` against `db48e9f`).

## What this does not settle

Juglet 2 and 9 produce **no cluster** even with normals that sit 1.40 and 1.54 deg from the mesh — the growth
step, not the normals, is what kills those two pieces at the shipped defaults, and `SFS_SINGLE_CLUSTER=write`
cannot write what the region growing never grows. Pieces 4, 6, 8 of the Juglet were not run. No seating claim is
made anywhere in this stage: the earlier normals arms (tickets 52/53) were destructive on seating, and this
ticket measures angles against the mesh only.
