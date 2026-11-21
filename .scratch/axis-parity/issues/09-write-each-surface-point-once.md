# 09: Write each surface point once, and make the de-duplication compare the whole point

**What to build:** A short code ticket on branch `09-write-each-surface-point-once` (worktree `C:/PR/worktrees/sfs/09`) that removes the duplicate-row defect at its source in `mesh_processing_headless.cpp`, proves the removal with a unit test and two real mesh cells, and records the consequence without re-running Part A. Three parts:

1. **Stop re-writing rows that are already in the surface.** `finishImprovedSurface` appends every row of `segmentedSurfacePointCloud` to the surface it just built, including the rows it already holds; measured on the exported walls, 45.8-48.1 % of our rows are exact 6-float repeats (Ticket 08). Append only rows not already present, count the skipped ones, and report the count in the existing `[DEDUPE-27]` line so the change is visible in every future run.
2. **Make the TICKET-27 de-duplication compare the whole point, not x/y/z.** Its sort key and its adjacent-equality test both look at coordinates only, so switching it on can silently delete a point whose normal differs. Extend both to the full 6-vector. Leave the switch **off** by default and say why.
3. **Prove both, and do not let the geometry move.** Unit test that reproduces the defect on the old behaviour and not on the new one; two real cells (`Pot_J_Piece_12`, whose duplicates are known, and `Pot_D_Piece_03`, which has appended rows that are *not* duplicates and must survive) showing zero duplicate 6-tuples in the written PLY, `in == out`, `PLY rows == in`, and the unique-position set unchanged against the program's own run-to-run spread.

**Answers:** E1
**Blocked by:** None (Ticket 08 resolved at `0c1ba1d`, Reading `shortlist-mechanism-not-fixed`)
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek - hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` staged before dispatch

---

## 0. What is established (read this, do not re-derive)

**The defect, measured.** Every surface our `MeshPreprocessingHeadless` writes carries rows that repeat earlier rows exactly (x, y, z and all three normal components). Ticket 08 scanned 296 own walls: 288 have the shape "unique prefix, then a second copy of part of it", 140 pieces have both walls affected and 8 pieces one wall. `Pot_J_Piece_12.S0` = 4 279 rows / 2 351 distinct, of which 1 928 are repeats; `.S1` = 4 842 / 2 590 (2 252 repeats). The Authors' 282 walls carry 2 511 886 rows and **zero** exact duplicates. Same-xyz-different-normal rows: zero everywhere.

**Where it comes from.** `C:/PR/SfSpp_preprocessing/mesh_processing_headless.cpp`, `finishImprovedSurface` (:1518-1627):

- :1567-1578 iterates `segmentedSurfacePointCloud` and copies x/y/z/normal_x/y/z into `ptTmp`, `improvedSurfacePointCloud->points.push_back(ptTmp)` at :1577 — unconditionally, with no test whether the row is already in the surface.
- :1583-1623 is the TICKET-27 de-duplication block. It sorts a copy with `myobject2` (:1590), keeps a row only when the *next* sorted row differs in **x, y, z only** (:1598), keeps the last element (:1609), and assigns the de-duplicated cloud back only when `g_dedupeOn27` (:1617). `myobject2`/`myclass2` at :230-240 compare x then y then z; that sort call at :1590 is its only use in this file. The switch is a static bool at :245 (default false), set at :6463-6466 from `SFS_DEDUPE=on`.
- The line :1624-1626 `[DEDUPE-27] surface=<i> mode=on|off in=<n> out=<m>` is the instrument. With the switch unset the written PLY count must equal that run's `in=`; when on, `out=`. Ticket 27 built its instruments (`.scratch/juglet-breaklines/stage27/`) on that invariant — keep it working.
- Callers: :3329 (single-surface path) and :3698-3699 (two surfaces, indices 0 and 1).
- This is the Authors' original defect, not a fork regression: upstream `DominicoRyu/SfSpp_preprocessing` has the same unconditional append in `mesh_processing.cpp` (:763 and :819) and the same never-assigned de-duplication block at :825+. Our fork only added the switch. The unbuilt root `*.cpp` copies stay untouched.

**Why it matters and why it is not the whole story.** The rows are identical, so a wall's *shape* does not change; but every point-based cost double-weights almost half of every wall. That was the framing of Ticket 08, which de-duplicated in memory and re-ran Part A: own 116/141 K1, 127/141 K3 became **111/141 K1, 123/141 K3**, Authors' numbers **exactly unchanged** (141/141 walls and pools byte-identical null control). So the honest own-surface numbers are the de-duplicated ones, and a writer that emits each row once makes every future own run agree with them. It also explains a long-standing note in `intent/E1-do-our-breaklines-let-sfs-find-joins.md` (2026-10-27) that the de-duplication "is meant to remove duplicate points and does not", corrected the same day by Ticket 27 to "a storage fix, not a counting fix" — the edgeline writes each position once whatever the surface holds, so no dot count moves.

**The trap: the mesh stage is not deterministic.** 30 unseeded ray casts (`mesh_processing_headless.cpp:1940-1950`) make every mesh-stage run a different draw; `Pot_J_Piece_12`'s own log shows `retries=1`, so it is one of the pieces that re-draws. **No claim in this ticket may rest on comparing a rebuilt wall with the November files or with another run.** The claims that survive the spread are set-equality-by-construction (unit test) and the in-run invariants (duplicate count, `in == out`, `PLY rows == in`). Cross-run set distance is reported as a control against the same binary's own spread, never as an equality.

**Instruments that already exist and should be reused, not rewritten** (`.scratch/juglet-breaklines/stage27/`, on main):

- `run_cell27.sh` — one mesh cell: run, keep `surfaces/*.ply` + `*.xyz` + every `<piece>_*` file the stage left (the unclustered cloud included), grep the `[..-2x]` lines, delete the stage with per-extension file+byte counts.
- `submit_27.sbatch.tmpl` — greps `[DEDUPE-27]` into `out/dedupe27_lines.txt`.
- `dedupe27.py` — `surfaces` (rows vs distinct positions per wall), `seteq` (position-set equality and nn distance between two arms' sets), `selftest27.sh` (laptop self-test of the ruler).
- The **own-surface cell recipe** is the t305 lane `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-d3/submit.sbatch`: container `SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif`, `apptainer=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`, `PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`, `SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"`, `CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`, mesh `_Mesh_DS.obj` for pots C..J, both binaries built inside the container, corpus md5 before/after with a `diff` (`CORPUS-UNCHANGED`).

## 1. Phase 1 - the writer fix (the only code change)

**W1. Append only what is not already there.** Replace the unconditional copy at :1567-1578 with: for each row of `segmentedSurfacePointCloud`, append it only if no row already in `improvedSurfacePointCloud` has the same 6 floats. Equality is **exact bit equality of all six values** (no epsilon — the walls are dense, median nearest-neighbour 0.26-0.31 mm, and a tolerance would delete real points). Existing rows keep their positions and order; appended rows keep the order they have in `segmentedSurfacePointCloud`. Use a hash set built once over the destination rows; the surfaces hold up to ~100 k rows, so an O(n) pass is expected. Do not reorder the destination.

**W2. Report the skip.** Keep the existing `[DEDUPE-27] surface=<i> mode=<on|off> in=<n> out=<m>` fields byte-compatible, append `dups_skipped=<k> appended=<a>` at the end, and add one more field `improved_rows=<p>` before `appended` so the write-back can prove where the rows came from. `in=` must count the rows **after** the skip (so `in = out` once nothing is duplicated, and the stage27 invariant "PLY count == in" keeps holding). `dups_skipped` counts rows *not appended* because they were already present. Do not change the line's prefix or the field order of the existing four fields — stage27's instruments grep them.

**W3. The de-duplication switch compares the whole point.** Extend `myclass2`'s comparison (and therefore `myobject2`) to x, y, z, nx, ny, nz, and the adjacent-equality test at :1598 to the same six values. A row with the same position but a different normal is **not** a duplicate and must be kept by both paths. Keep `SFS_DEDUPE` **off** by default: with W1 in place there is nothing left to remove, and switching it on would only sort and reorder the cloud for no gain. Do not remove the switch (Ticket 27's instruments and arms use it).

**W4. Nothing else moves.** No change to the admit-sign filter, the region-growing, the projection, the sampling, the exporter, or the unbuilt root `*.cpp` copies. No change to any other file except (a) the .cpp, (b) one new header if you choose the extract-and-test route, (c) `CMakeLists.txt` for the test target, (d) the ticket. State in the write-back the full diffstat and a file:line map of every change.

## 2. Phase 2 - the unit test (red first, then green)

There is no C++ test target in this repo (`tests/` holds Python only). Add one, built by CMake and run on a compute node: `add_executable(SurfaceDedupeTest tests/test_surface_dedupe.cpp)` plus the target in `all_targets`; the test must exercise **the shipped code path**, not a copy of it (extract the append-skip and the 6-vector de-duplication into a small header-only template over a point type with `x,y,z,normal_x,normal_y,normal_z` — no PCL needed by the test — and call it from both the monolith and the test). It must print one `CASE <name> PASS|FAIL` line per case and exit non-zero on any failure, and be shown **red on the old behaviour** (a flag or a compile-time switch that restores the unconditional append) before it is green on the shipped one. Cases:

- **U1 duplicate suffix:** destination A, source = a tail whose rows are all already in A → append adds nothing, returns `dups_skipped == |source|`, destination byte-identical to A.
- **U2 new rows survive:** source has k rows not in A and m rows in A → exactly k appended, in source order, `dups_skipped == m`.
- **U3 same position, different normal:** a source row with A's xyz but a different normal is appended (both paths must keep it), and the 6-vector de-duplication keeps both rows.
- **U4 idempotence and order:** appending twice adds nothing the second time; the destination order after a mixed append equals "A then the missing rows in source order".
- **U5 6-vector de-duplication:** a cloud with an exact repeat, a same-xyz-different-normal pair and a unique row yields exactly 3 distinct rows in a deterministic order; the old xyz-only rule yields 2 (this is the W3 red case).

Record the test's output at `out/UNIT.txt` in the run directory, including the red run.

## 3. Phase 3 - real cells (two pieces, five arms)

One Slurm job, compute node, container build. Build **two** binaries from the same tree: `OLD` = the parent commit (before Phase 1), `NEW` = the ticket commit. Run cells with the t305 staging and the stage27 cell runner:

| arm | binary | piece | what it proves |
|---|---|---|---|
| A | OLD | Pot_J_Piece_12 | the defect is present in the artefact (`n_dup6 > 0`) |
| A2 | OLD (byte copy, not rebuild) | Pot_J_Piece_12 | the defect is structural, not a draw |
| B | NEW | Pot_J_Piece_12 | no duplicate 6-tuple, `in == out`, `PLY rows == in`, `dups_skipped > 0` |
| C | OLD | Pot_D_Piece_03 | the piece whose appended rows are *not* all duplicates: 1 700 of 103 177 tail rows are new |
| D | NEW | Pot_D_Piece_03 | those new rows still arrive (`appended_missing > 0`), no duplicate 6-tuple |

`Pot_D_Piece_03.S0` is 103 177 rows / 53 134 distinct with `tail_start=51 434` and 1 700 tail rows not in the head (Ticket 08's scan, `axes08_scan.json`) — it is the piece that fails if the fix over-reaches into "drop the append". Expect the rebuilt counts to differ from those numbers (see the draw trap); gate on the invariants, not the counts. Note for the write-back: `Pot_J_Piece_12`'s duplicate count 1 928 equals the largest cluster size in its `[STATUS-23]` line (`sizes=1928,2252,269,122,112,58`); say whether the appended cloud is that cluster (the log's `appended=` will show it).

Report `axes09_cells.tsv` with header exactly:

```
piece	wall	arm	improved_rows	appended_rows	appended_missing	dups_skipped	in	out	ply_rows	n_dup6	n_distinct_pos	verdict
```

(tab-separated) and `axes09_seteq.tsv` with header exactly

```
piece	wall	arm_a	arm_b	positions_a	positions_b	equal	nn_med_mm	nn_p90_mm
```

`n_dup6` = number of rows in the exported PLY whose 6 floats occur earlier in the same file. `n_distinct_pos` = number of distinct xyz. Computed by a checked-in-run script, not by eye (reuse `dedupe27.py surfaces`; extend it locally if needed and keep the extension in `work/`, not in the repo).

**Gates (all must hold, or the Reading changes):**

- **G1** J12 arms A and A2: `n_dup6 > 0` on both written walls of both arms.
- **G2** J12 arm B: `n_dup6 == 0`, `in == out`, `ply_rows == in`, `dups_skipped > 0` (at least one wall), `appended_missing >= 0`.
- **G3** D03 arms C/D: arm C `n_dup6 > 0`; arm D `n_dup6 == 0`, `appended_missing > 0` (the new tail rows still arrive).
- **G4** draw control: `seteq` A vs A2 and A vs B per wall; A vs B `nn_med_mm` must be no more than 2x A vs A2's (if it is more, say so and investigate — do not delete the row).
- **G5** unit test red on old behaviour and green on shipped code, `out/UNIT.txt` present.

Also record `runs/index.tsv` rows for the job, the `sacct` final State/ExitCode in the ticket, and the corpus md5 before/after diff.

**Figure.** `render09_rows.png` (one panel per piece): for each written wall, a bar pair "PLY rows / distinct positions" for arm A (or C) and arm B (or D), log scale if needed, with the counts printed on the bars. The claim is row multiplicity, not shape, so no geometry render is required — say that in the write-back and say what the figure does and does not show.

## 4. Phase 4 - write-back and record

Write into the ticket, in this order: what changed (diffstat + file:line map), the two log lines `before`/`after` for `Pot_J_Piece_12.S0`, the cell and seteq tables, the gates with values, the unit-test red/green output, the consequence for the recorded numbers (*own Part A becomes the 111/123 of Ticket 08 when surfaces are next regenerated; nothing is re-measured here*), the corpus check, the jobs and `sacct`, and what is still owed (an own-surface regeneration ticket; the E1 edgeline re-measure already answered by Ticket 27 as "storage, not counting"). Then `End state:` and exactly one `Reading:` line (singular, no bullet), from:

- `writer-writes-each-point-once` — W1-W4 in, G1-G5 hold, no second source of duplicates found.
- `writer-fixed-second-duplicate-found` — the fix is in but `in != out` or `n_dup6 > 0` on arm B/D because rows already duplicate inside the improved cloud; name the second source with file:line and do not hide it behind a log tweak.
- `writer-not-fixed` — the test cannot be made red then green, the build fails, or any gate fails for a reason other than a second source.
- `blocked` — container, corpus or cluster unavailable; say which.

Do **not** run Part A, do not regenerate any existing surface, do not edit the corpus, do not merge, push `main`, close the ticket or change `Status:`. Commit only Phase 1-2 files plus the ticket, with `Worker: DeepSeek` in the message body, on `09-write-each-surface-point-once`, and push the branch.

## 5. Commands (adapt, do not invent)

- Work is in `C:/PR/worktrees/sfs/09` on `09-write-each-surface-point-once`; the run is `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t09-surface-dedup/` with `logs/`, `work/`, `out/`.
- Build inside the container from a compute node, exactly as the lane does; keep `build.log` for both binaries.
- Every `sbatch` gets `scripts/slurm_poll.sh <JOBID>` and its final `sacct` State/ExitCode in the ticket. Heavy work never on the login node or the laptop.
- Fetch to the laptop only the small record: the two TSVs, `UNIT.txt`, the two logs' `[DEDUPE-27]`/cell lines, `sacct_all.txt`, `render09_rows.png` — into `C:/PR/artifacts/axis-parity-09/`.
- `ssh spartan` one-shot is the only way to the cluster from this session; no recursive `find`/`du` over `/data/gpfs`.

## 6. Acceptance (hidden, run by the lead)

`C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` checks: both repos clean and on the right branch; only the allowed files changed; `Worker: DeepSeek` trailer; `End state:` present and one Reading from the four; the two TSVs with the exact headers and the required arms; G1-G4 recomputed from the TSVs (J12 A/A2 duplicate counts > 0, J12 B zero duplicates with `in == out` and `ply_rows == in` and `dups_skipped > 0`, D03 C duplicates > 0 and D zero with `appended_missing > 0`); `UNIT.txt` containing a FAIL line for the old path and PASS lines for U1-U5; the `before`/`after` log lines for J12.S0 with the expected field names; the consequence sentence for the 111/123 numbers; `CORPUS-UNCHANGED`; the jobs and `sacct` lines; the figure present and non-trivial; nothing written under `C:/PR/SfSpp_preprocessing/Dataset` or the corpus.
