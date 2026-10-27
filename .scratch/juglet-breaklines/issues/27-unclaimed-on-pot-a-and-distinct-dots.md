# 27: how much of a Pot A sherd is in no region, and counting distinct dots instead of copies

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** ready-for-agent

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
