# 27: how much of a Pot A sherd is in no region, and counting distinct dots instead of copies

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 27-unclaimed-on-pot-a-and-distinct-dots, in /c/PR/worktrees/sfs/27

Two measurements the ladder left behind, both small, both needed before any repair is written. **Report
evidence; do not decide whether anything is a defect.**

## Where these come from

Ticket 25 merged as `0ae8449` and its reading is in
`.scratch/juglet-breaklines/issues/25-dump-the-geometry-at-every-step.md`. Two facts from it are
unfinished business:

1. **The region growing leaves most of every Juglet sherd in no region** — 1 199 of 1 467 points on piece 3,
   2 342 of 3 021 on piece 5, 3 455 of 4 254 on piece 7, all 1 031 on piece 2. **Nobody has measured a
   Pot A sherd the same way.** Until that number exists, "78-82 % unclaimed" is a property of one vessel,
   not a defect, and a repair aimed at it would be tuned against a property.
2. **`finishImprovedSurface` de-duplicates and then throws the result away** (`mesh_processing_headless.cpp:1163`,
   the block at `:1188-1213`). The built-and-unused cloud is why written surfaces carry 1.2-1.45x more
   vertices than distinct positions (piece 5 chain off 1 845 / 1 022; piece 7 defaults 1 012 / 609 and
   829 / 566; Pot A 01 66 759 / 33 985). Anything counted per dot — edgeline dots above all — is an upper
   bound until that is fixed.

## Part A — measure the unclaimed fraction on Pot A

Run today's defaults on ten pieces and report, per piece, from the rung-2 and rung-5 sidecars that ticket 25
already writes (`SFS_DUMP_STAGE=<dir>` with `SFS_DUMP_PIECES=<piece>` arms them; an unset switch writes
nothing):

- **Pot A:** `Pot_A_Piece_01`, `_02`, `_07`, `_08` (four pieces, the same pot the pair statistics have used).
- **Juglet:** `Juglet_Piece_1`, `_4`, `_6`, `_7` (the four that write a surface), plus `Juglet_Piece_2` and
  `_9` (the two that do not) — six pieces, so the same instrument is applied to both vessels.

Report per piece: points entering the segmentation (rung 2), the region sizes, `points_in_no_cluster` and
what fraction of the cloud that is, and at rung 5 how many points ended on each written surface (and how
many of those are distinct positions). **The Pot A number is the deliverable**; the Juglet rows are there so
the two can be read side by side, not as a re-run of ticket 25.

## Part B — make the de-duplication real, behind a switch

`finishImprovedSurface` (`mesh_processing_headless.cpp:1163`) appends the whole region cloud to the admitted
set at `:1172-1185`, which re-adds the admitted points and is where the copies come from. It then builds
`improvedSurfacePointCloudNoDuplicates` at `:1189-1212` and **never assigns it back**; the loop also stops at
`size() - 1`, so the last sorted point would be dropped if it were used.

- Add `SFS_DEDUPE=off|on`, **default `off`, and off must reproduce today exactly.** With `on`, assign the
  de-duplicated cloud back to `improvedSurfacePointCloud` and cover the final element.
- Equality is exact float comparison against the same source cloud, which is why the existing comparator is
  adequate; do not substitute a tolerance without saying so.
- The switch must be printed once per call: `[DEDUPE-27] surface=0 mode=on in=1845 out=1022`.

### The invariant that makes this safe

With `on`, **the set of distinct positions on each surface must be identical to the set the `off` arm
produces** — same points, each once. The repair may only stop repeating points; if it adds or removes one,
that is a behaviour change and it must be reported as one.

## Arms and cells

Three arms, ten pieces (the ones in part A), one job if it fits and two at most:

- **A** defaults, `SFS_DEDUPE` unset, `SFS_DUMP_STAGE` unset — the pre-change reference for the defaults proof;
- **A2** the same binary again, unset — the run-to-run control the unseeded ray casts make necessary;
- **B** `SFS_DEDUPE=on`.

Part A needs the dump armed, part B does not; run part A as its own arm (`SFS_DUMP_STAGE` set, `SFS_DEDUPE`
unset) so its numbers are today's behaviour.

## Evidence to return

1. Per piece: points in, region sizes, points in no cluster and the fraction, on **both** pots.
2. Per piece, rung 5: points on each surface and distinct positions, off against on.
3. The defaults proof: with the switch unset, written surfaces identical to the pre-change binary (compare
   the **sorted six-column point set**, not md5 — an uninitialised curvature column makes md5 differ), and
   the A-against-A2 spread stated in the same units.
4. With `on`: for every written surface, zero duplicate positions **and** the distinct position set equal to
   the `off` arm's distinct set. Name any surface where it is not.
5. Pot A pair statistics (through / across / coincidence, the corrected ruler from ticket 26) off against on,
   so we can see the pair is unchanged.
6. Our own `Breakline_0` dot counts, off against on, per piece — the number E1 asks about.
7. The `[DEDUPE-27]` lines, verbatim, for one piece showing in/out on both surfaces.
8. Corpus md5 before and after (identical), `/opt/sfs-pristine` recorded ABSENT not created, geometry deleted
   with a counted record, index rows appended with `verdict` and `human_note` **empty**.

## Acceptance criteria

1. `SFS_DEDUPE` unset produces written surfaces whose distinct and total point sets both match the
   pre-change binary; the A/A2 spread is stated.
2. `SFS_DEDUPE=on` produces no surface with duplicate positions.
3. With `on`, every surface's distinct position set equals the `off` arm's; any exception named.
4. Pot A pair statistics unchanged by the switch (same through/across to the precision reported).
5. Part A reports the unclaimed fraction for four Pot A pieces and six Juglet pieces from the sidecars, with
   the fraction computed, not estimated.
6. Edgeline dot counts reported per piece, off against on.
7. No change to any file other than `mesh_processing_headless.cpp` and `.scratch/juglet-breaklines/stage27/`.
8. Ticket updated with what was done, Status moved, evidence committed and pushed.

## Constraints

- **Compute nodes only.** Nothing measured on the laptop or the login node — a re-score of a bundle belongs on
  a node, and an earlier ticket breached this. At most three jobs.
- **The corpus is read-only**: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` and
  `/opt/sfs-pristine` (record it ABSENT; do not create it). md5 before and after.
- Run directories follow the convention; check the `CRLF` of every script before submitting (two grids have
  already died with `set: pipefail: invalid option name`).
- Delete the stage geometry with a counted record; keep the logs, the sidecars, the tables and any figure.
- If a change outside `mesh_processing_headless.cpp` turns out to be needed, **stop and report**.
- Do not write to `intent/`, do not merge, do not close the ticket, and do not give a verdict.

## What this cannot settle

Part A says what fraction of a sherd is unclaimed on both vessels; it does not say whether high unclaimed is
good or bad. Part B makes the dot count honest; it does not say whether our Breakline_0 follows the right
edge — only how many dots it has once copies are removed. Neither part touches reassembly.

## Worker result — 2026-10-27, job 33860966

Run of record `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1534_df523dd_p27-dedupe-grid`, commit
`df523dd`, pre-change `16ba55d`, arms OLD / A (defaults) / A2 (same binary again) / P (defaults +
`SFS_DUMP_STAGE`) / B (`SFS_DEDUPE=on`), 50 mesh cells + 32 edgeline cells in one job. Tables in
`.scratch/juglet-breaklines/stage27/evidence/`, instruments documented in `stage27/README.md`.
Status left at `in-progress`: acceptance is the lead's, and item 6 below was not obtained.

### Part A — what the sidecars say (arm P, today's defaults)

`points_in_no_cluster` and the region sizes are verbatim from `r2_clusters_premerge.json`; the surface
columns are `r5_write.json`. Fraction = `points_in_no_cluster / npts`, computed not estimated.

| piece | points in | regions | region sizes | in no region | fraction | Surface_0 pts/distinct | Surface_1 pts/distinct |
|---|---|---|---|---|---|---|---|
| Pot_A_Piece_01 | 85136 | 12 | 32775 27551 3803 3375 815 730 697 570 379 285 203 173 | 13780 | 0.1619 | 66760 / 33985 | 57283 / 29732 |
| Pot_A_Piece_02 | 49528 | 5 | 22543 20628 751 221 211 | 5174 | 0.1045 | 42198 / 21570 | 46332 / 23789 |
| Pot_A_Piece_07 | 8598 | 8 | 3093 2850 203 170 144 120 73 71 | 1874 | 0.2180 | 6066 / 3216 | 6437 / 3344 |
| Pot_A_Piece_08 | 7682 | 5 | 2832 2611 265 194 90 | 1690 | 0.2200 | 5528 / 2917 | 6097 / 3265 |
| Juglet_Piece_1 | 14546 | 22 | 3489 626 411 349 274 164 151 143 133 106 103 102 86 84 81 80 64 58 57 53 53 50 | 7829 | 0.5382 | 3580 / 2954 | 12092 / 8627 |
| Juglet_Piece_2 | 1031 | 0 | — (21 retries, no region) | 1031 | 1.0000 | no surface | no surface |
| Juglet_Piece_4 | 1530 | 2 | 242 51 | 1237 | 0.8085 | 182 / 131 | 732 / 732 |
| Juglet_Piece_6 | 2351 | 2 | 365 213 | 1773 | 0.7541 | 608 / 395 | 1016 / 651 |
| Juglet_Piece_7 | 4254 | 5 | 326 263 77 68 65 | 3455 | 0.8122 | 1012 / 609 | 829 / 566 |
| Juglet_Piece_9 | 787 | 0 | — (21 retries, no region) | 787 | 1.0000 | no surface | no surface |

Same run, the rung-5 assignment: `points_on_surface_0 / points_on_surface_1 / points_on_neither` =
33985 / 29732 / 21419 (A 01), 21570 / 23789 / 4169 (A 02), 3216 / 3344 / 2038 (A 07), 2917 / 3265 / 1500
(A 08), 2954 / 5826 / 5766 (J 1), 131 / 680 / 719 (J 4), 395 / 471 / 1485 (J 6), 609 / 413 / 3232 (J 7),
1031 / — / 1031 (J 2), 787 / — / 787 (J 9). On J 1, J 6 and J 7 the written Surface_1 carries **more
distinct positions than the segmentation assigned to it** (8627 v 5826, 651 v 471, 566 v 413) because
`finishImprovedSurface` also copies the other surface and appends the whole segmentation cloud.

### Part B — copies in the written surfaces, off against on

`n_ply` and distinct positions from `surfaces27.tsv` (`np.unique` on xyz). Every `on` surface has
`duplicates = 0`, ratio 1.000.

| piece | surface | off pts | off distinct | off dup | off ratio | on pts = on distinct |
|---|---|---|---|---|---|---|
| Pot_A_Piece_01 | 0 / 1 | 66761 / 57293 | 33986 / 29742 | 32775 / 27551 | 1.964 / 1.926 | 33989 / 29749 |
| Pot_A_Piece_02 | 0 / 1 | 42203 / 46327 | 21575 / 23784 | 20628 / 22543 | 1.956 / 1.948 | 21570 / 23786 |
| Pot_A_Piece_07 | 0 / 1 | 6066 / 6437 | 3216 / 3344 | 2850 / 3093 | 1.886 / 1.925 | 3216 / 3344 |
| Pot_A_Piece_08 | 0 / 1 | 5528 / 6097 | 2917 / 3265 | 2611 / 2832 | 1.895 / 1.867 | 2917 / 3265 |
| Juglet_Piece_1 | 0 / 1 | 3580 / 12092 | 2954 / 8627 | 626 / 3465 | 1.212 / 1.402 | 2954 / 8627 |
| Juglet_Piece_4 | 0 / 1 | 182 / 732 | 131 / 732 | 51 / 0 | 1.389 / 1.000 | 131 / 732 |
| Juglet_Piece_6 | 0 / 1 | 608 / 1016 | 395 / 651 | 213 / 365 | 1.539 / 1.561 | 395 / 651 |
| Juglet_Piece_7 | 0 / 1 | 1012 / 829 | 609 / 566 | 403 / 263 | 1.662 / 1.465 | 609 / 566 |

**Within-run chain (exact, every cell):** for the three off arms `n_ply == [DEDUPE-27] in=` and for the
`on` arm `n_ply == out=`; the counts agree to the point.

```
off (A, Pot_A_Piece_01): [DEDUPE-27] surface=0 mode=off in=66761 out=33986
                         [DEDUPE-27] surface=1 mode=off in=57293 out=29742
on  (B, Pot_A_Piece_01): [DEDUPE-27] surface=0 mode=on in=66764 out=33989
                         [DEDUPE-27] surface=1 mode=on in=57300 out=29749
```

**Defaults reproduce the pre-change binary, and the run-to-run spread in the same units** (`seteq27.tsv`,
distinct-position sets, 16 surfaces per pair; `nn_max` is the largest nearest-neighbour distance between the
two sets): A/OLD 12 of 16 exactly equal, worst cell 18 positions only in one set and `nn_max` 0.666714 mm;
**A/A2 12 of 16 exactly equal, worst 18 positions and 0.761401 mm**; P/A 30 positions, 0.714881 mm; B/A 11
positions, 0.714881 mm; B/A2 21 positions, 0.761401 mm. Every unequal cell is Pot A 01 or 02 — the two
1 000 000-point clouds the unseeded ray casts move — while all eight Juglet surfaces and Pot A 07/08 are
**exactly** equal in every pair, so the A-vs-A2 figure is the bar a difference must beat, and against it the
`on` arm's distinct sets match the `off` arm's within the same 0-21 points.

### Pot A pair statistics, the corrected ruler (through along Surface_0's own normal, across it)

| piece | arm | n0 | n1 | med through | p90 through | max through | med across | p90 across | max across | coincidence at 1 µm |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | A off | 66761 | 57293 | 7.089063 | 9.944138 | 12.954713 | 0.270913 | 0.543787 | 4.474023 | 0.000000 |
| 01 | A2 off | 66763 | 57283 | 7.089063 | 9.943797 | 12.954713 | 0.270911 | 0.543634 | 4.474023 | 0.000000 |
| 01 | B on | 33989 | 29749 | 7.060942 | 10.041428 | 12.954713 | 0.276117 | 0.655563 | 4.474023 | 0.000000 |
| 02 | A off | 42203 | 46327 | 3.631630 | 4.458488 | 6.353303 | 0.251284 | 0.447085 | 3.722243 | 0.000000 |
| 02 | B on | 21570 | 23786 | 3.626575 | 4.472346 | 6.353303 | 0.255074 | 0.490298 | 3.722243 | 0.000000 |
| 07 | A off | 6066 | 6437 | 3.919588 | 4.297276 | 4.596343 | 0.248680 | 0.467674 | 3.556027 | 0.000000 |
| 07 | B on | 3216 | 3344 | 3.904660 | 4.292938 | 4.596343 | 0.253443 | 1.089373 | 3.556027 | 0.000000 |
| 08 | A off | 5528 | 6097 | 3.603650 | 3.816507 | 4.000407 | 0.250306 | 1.202003 | 2.891494 | 0.000000 |
| 08 | B on | 2917 | 3265 | 3.589088 | 3.814568 | 4.000407 | 0.263740 | 1.534700 | 2.891494 | 0.000000 |

All in mm; `med_nn` tracks `med through` to 0.014 mm at worst (01 off 7.095229 / on 7.067484).

### Item 6, our own Breakline_0 dots, was NOT obtained

All 32 edgeline cells (OLD/A/A2/B × the eight pieces that write a surface) exited **139 (SIGSEGV)** in 1-5 s
and wrote only `(none-written)` rows into `dots27.tsv`. Failing command and message, from
`out/cells/A/Pot_A/Pot_A_Piece_01/logs/edge.log`:

```
[pcl::PLYReader] Temp/Data/Pot_A/Pot_A_Piece_01_unclustered.ply:1: parse error: couldn't read the magic string
[pcl::PLYReader::read] problem parsing header!
[pcl::KdTreeFLANN::setInputCloud] Cannot create a KDTree with an empty input cloud!
instruments/run_edge27.sh: line 34: 161680 Segmentation fault (core dumped) "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$EDGEBIN"
```

Cause: the edgeline stage reads `Temp/Data/<pot>/<piece>_unclustered.ply` as well as the surfaces, and
`run_cell27.sh` kept only `Surface_{0,1}` and `_SampledWithNormals.ply` before deleting the staged tree, so
the file was absent. One-line fix for a future job (not submitted: the brief caps the grid at three jobs):
keep `${PIECE}_unclustered.ply` into `<cell>/surfaces/` in `run_cell27.sh` and copy it into
`$ES/Temp/Data/$POT/` in `run_edge27.sh`.

### Record

Corpus tree and md5 before/after identical (1 803 paths, 30 md5s, 228 922 and 3 982 bytes);
`opt-sfs-pristine` recorded **ABSENT**, not created; `[S27] geometry deleted: 1252 files, 1 610 428 132 bytes`
of staged trees, plus the 210 kept cell surfaces (130 `.ply` 151 883 930 bytes + 80 `.xyz` 62 987 058 bytes)
and the 50 rung dumps (56 516 653 bytes) deleted afterwards with a counted manifest in the run directory's
`out/GEOMETRY_DELETED_cells.txt`; logs, sidecar JSONs, tables and arm binaries kept. Index row appended with
`verdict` and `human_note` empty.
