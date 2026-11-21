# 09: Write each surface point once (position rule, not six floats)

**What to build:** A short code ticket on branch `09-write-each-surface-point-once` (worktree `C:/PR/worktrees/sfs/09`) that removes the duplicate-row defect at its source in `mesh_processing_headless.cpp`, proves the removal with a unit test and two real mesh cells, and records the consequence without re-running Part A. Three parts:

1. **Stop re-writing rows that are already in the surface.** `finishImprovedSurface` appends every row of `segmentedSurfacePointCloud` to the surface it just built, including the rows it already holds; measured on the exported walls, 45.8-48.1 % of our rows are exact 6-float repeats (Ticket 08). Append only rows not already present, count the skipped ones, and report the count in the existing `[DEDUPE-27]` line so the change is visible in every future run.
2. **Settle the TICKET-27 rule on position, and keep it.** Its adjacent-equality test looks at x/y/z only. **Keep that rule** - do not extend it to the six floats. Measured (first run of this ticket, 2026-11-21): the same position reaches a surface twice with a normal that differs in one float32 ulp, because the two code paths compute the normal differently; the exporter prints 8 significant digits, so the two rows are the same row in the only artefact anyone reads, and a six-value rule keeps both. Make the de-duplication keep one row per position, deterministically. Leave the switch **off** by default and say why.
3. **Prove both, and do not let the geometry move.** Unit test that reproduces the defect on the old behaviour and not on the new one; two real cells (`Pot_J_Piece_12`, whose duplicates are known, and `Pot_D_Piece_03`, which has appended rows that are *not* duplicates and must survive) showing zero repeated positions in the written PLY, `in == out`, `PLY rows == in`, the largest normal difference among the skipped pairs (no material normal may be dropped), and the unique-position set unchanged against the program's own run-to-run spread.

**Answers:** E1
**Blocked by:** None (Ticket 08 resolved at `0c1ba1d`, Reading `shortlist-mechanism-not-fixed`)
**Status:** resolved
**Branch:** 09-write-each-surface-point-once, in /c/PR/worktrees/sfs/09
**Worker:** dsh one-shot subagent w09-surface-dedup
**Budget:** medium 5
**Hand-over:** DeepSeek - hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` staged before dispatch

---

## 0. What is established (read this, do not re-derive)

**The defect, measured.** Every surface our `MeshPreprocessingHeadless` writes carries rows that repeat earlier rows exactly (x, y, z and all three normal components). Ticket 08 scanned 296 own walls: 288 have the shape "unique prefix, then a second copy of part of it", 140 pieces have both walls affected and 8 pieces one wall. `Pot_J_Piece_12.S0` = 4 279 rows / 2 351 distinct, of which 1 928 are repeats; `.S1` = 4 842 / 2 590 (2 252 repeats). The Authors' 282 walls carry 2 511 886 rows and **zero** exact duplicates. Same-xyz-different-normal rows: **zero in the exported text**, which is the only place the count matters; in memory the appended twin's normal differs by one float32 ulp (measured on this ticket's first run - see §7.14).

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

**W1. Append only what is not already there, at the position.** Replace the unconditional copy at :1567-1578 with: for each row of `segmentedSurfacePointCloud`, append it only if no row already in `improvedSurfacePointCloud` has the same **x, y and z**. Equality is **exact bit equality of the three coordinates** (no epsilon — the walls are dense, median nearest-neighbour 0.26-0.31 mm, and a tolerance would delete real points). On a match, the destination row stays exactly as it is, **its normal included**, and the row is counted as skipped: the two normals are the same normal to within one float32 ulp (this ticket's §7.14), and the file prints eight digits, so keeping both writes the same row twice. Existing rows keep their positions and order; appended rows keep the order they have in `segmentedSurfacePointCloud`. Use a hash set built once over the destination positions; the surfaces hold up to ~100 k rows, so an O(n) pass is expected. Do not reorder the destination.

**W2. Report the skip.** Keep the existing `[DEDUPE-27] surface=<i> mode=<on|off> in=<n> out=<m>` fields byte-compatible, append `dups_skipped=<k> appended=<a> normal_maxdiff=<d>` at the end, and add one more field `improved_rows=<p>` before `appended` so the write-back can prove where the rows came from. `normal_maxdiff` is the largest absolute difference, over all skipped pairs, between the skipped row's normal and the kept row's normal, any component: it is the guard that no material normal is being dropped, and it must be reported for every future run. `in=` must count the rows **after** the skip (so `in = out` once nothing is duplicated, and the stage27 invariant "PLY count == in" keeps holding). `dups_skipped` counts rows *not appended* because they were already present. Do not change the line's prefix or the field order of the existing four fields — stage27's instruments grep them.

**W3. The de-duplication switch keeps one row per position.** The x/y/z rule at :1598 is the right rule and stays (W1's reason: a same-position row's normal differs by one ulp, and the file prints eight digits). What changes is only that the rule must be applied **deterministically**: order the rows by x, y, z with the three normal words as the tie-break (so the outcome does not depend on the order the cloud arrives in) and keep exactly one row per position. Do not extend the key to the six floats: that is the first run's mistake, recorded in §7.14. Keep `SFS_DEDUPE` **off** by default: with W1 in place there is nothing left to remove, and switching it on would only sort and reorder the cloud for no gain. Do not remove the switch (Ticket 27's instruments and arms use it).

**W4. Nothing else moves.** No change to the admit-sign filter, the region-growing, the projection, the sampling, the exporter, or the unbuilt root `*.cpp` copies. No change to any other file except (a) the .cpp, (b) one new header if you choose the extract-and-test route, (c) `CMakeLists.txt` for the test target, (d) the ticket. State in the write-back the full diffstat and a file:line map of every change.

## 2. Phase 2 - the unit test (red first, then green)

There is no C++ test target in this repo (`tests/` holds Python only). Add one, built by CMake and run on a compute node: `add_executable(SurfaceDedupeTest tests/test_surface_dedupe.cpp)` plus the target in `all_targets`; the test must exercise **the shipped code path**, not a copy of it (extract the append-skip and the one-row-per-position de-duplication into a small header-only template over a point type with `x,y,z,normal_x,normal_y,normal_z` — no PCL needed by the test — and call it from both the monolith and the test). It must print one `CASE <name> PASS|FAIL` line per case and exit non-zero on any failure, and be shown **red on the old behaviour** (a flag or a compile-time switch that restores the unconditional append) before it is green on the shipped one. Cases:

- **U1 duplicate suffix:** destination A, source = a tail whose rows are all already in A → append adds nothing, returns `dups_skipped == |source|`, destination byte-identical to A.
- **U2 new rows survive:** source has k rows not in A and m rows in A → exactly k appended, in source order, `dups_skipped == m`.
- **U3 same position, one-ulp normal:** a source row with A's xyz and a normal one float32 ulp off is **skipped** (destination unchanged, `dups_skipped == 1`, `normal_maxdiff` equal to that ulp), and the de-duplication keeps one row for that position, with A's six values.
- **U4 idempotence and order:** appending twice adds nothing the second time; the destination order after a mixed append equals "A then the missing rows in source order".
- **U5 position de-duplication:** a cloud with an exact repeat, a same-position one-ulp-normal pair and a unique row yields exactly 2 rows, in the same deterministic order whichever order the rows are offered in; the legacy path (unconditional append) yields 4 (this is the red case, and it fails only on the append).

Record the test's output at `out/UNIT.txt` in the run directory, including the red run.

## 3. Phase 3 - real cells (two pieces, five arms)

One Slurm job, compute node, container build. Build **two** binaries from the same tree: `OLD` = the parent commit (before Phase 1), `NEW` = the ticket commit. Run cells with the t305 staging and the stage27 cell runner:

| arm | binary | piece | what it proves |
|---|---|---|---|
| A | OLD | Pot_J_Piece_12 | the defect is present in the artefact (`n_dup6 > 0`) |
| A2 | OLD (byte copy, not rebuild) | Pot_J_Piece_12 | the defect is structural, not a draw |
| B | NEW | Pot_J_Piece_12 | no repeated position, `in == out`, `PLY rows == in`, `dups_skipped > 0`, `normal_maxdiff` at ulp scale |
| C | OLD | Pot_D_Piece_03 | the piece whose appended rows are *not* all duplicates: 1 700 of 103 177 tail rows are new |
| D | NEW | Pot_D_Piece_03 | those new rows still arrive (`appended_rows > 0`), no repeated position |

`Pot_D_Piece_03.S0` is 103 177 rows / 53 134 distinct with `tail_start=51 434` and 1 700 tail rows not in the head (Ticket 08's scan, `axes08_scan.json`) — it is the piece that fails if the fix over-reaches into "drop the append". Expect the rebuilt counts to differ from those numbers (see the draw trap); gate on the invariants, not the counts. Note for the write-back: `Pot_J_Piece_12`'s duplicate count 1 928 equals the largest cluster size in its `[STATUS-23]` line (`sizes=1928,2252,269,122,112,58`); say whether the appended cloud is that cluster (the log's `appended=` will show it).

Report `axes09_cells.tsv` with header exactly:

```
piece	wall	arm	improved_rows	appended_rows	dups_skipped	in	out	ply_rows	n_dup6	n_distinct_pos	verdict
```

(tab-separated) and `axes09_seteq.tsv` with header exactly

```
piece	wall	arm_a	arm_b	positions_a	positions_b	equal	nn_med_mm	nn_p90_mm
```

`n_dup6` = number of rows in the exported PLY whose 6 floats occur earlier in the same file. `n_distinct_pos` = number of distinct xyz. Computed by a checked-in-run script, not by eye (reuse `dedupe27.py surfaces`; extend it locally if needed and keep the extension in `work/`, not in the repo).

**Gates (all must hold, or the Reading changes):**

- **G1** J12 arms A and A2: `n_dup6 > 0` on both written walls of both arms.
- **G2** J12 arm B: `n_dup6 == 0`, `in == out`, `ply_rows == in`, `dups_skipped > 0` (at least one wall), `appended_rows >= 0`, `in == improved_rows + appended_rows`.
- **G3** D03 arms C/D: arm C `n_dup6 > 0`; arm D `n_dup6 == 0`, `appended_rows > 0` (the new tail rows still arrive).
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

`C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` checks: both repos clean and on the right branch; only the allowed files changed; `Worker: DeepSeek` trailer; `End state:` present and one Reading from the four; the two TSVs with the exact headers and the required arms; G1-G4 recomputed from the TSVs (J12 A/A2 duplicate counts > 0, J12 B zero duplicates with `in == out` and `ply_rows == in` and `dups_skipped > 0`, D03 C duplicates > 0 and D zero with `appended_rows > 0`); `UNIT.txt` containing a FAIL line for the old path and PASS lines for U1-U5; the `before`/`after` log lines for J12.S0 with the expected field names; the consequence sentence for the 111/123 numbers; `CORPUS-UNCHANGED`; the jobs and `sacct` lines; the figure present and non-trivial; nothing written under `C:/PR/SfSpp_preprocessing/Dataset` or the corpus.

---

## 7. Write-back (2026-11-21)

### 7.1 What changed

Branch `09-write-each-surface-point-once`, HEAD `ae7c750` (parent `8d7cc60`), pushed. Four files, nothing else:

```
 CMakeLists.txt                |  10 +-
 mesh_processing_headless.cpp  |  95 ++++++-----------
 surface_dedupe.h              | 168 ++++++++++++++++++++++++++++++++
 tests/test_surface_dedupe.cpp | 220 ++++++++++++++++++++++++++++++++++++++++
 4 files changed, 430 insertions(+), 63 deletions(-)
```

File:line map (numbers on `ae7c750`):

- `surface_dedupe.h:16-21` includes; `:26-31` the `SURFACE_DEDUPE_LEGACY` switch (the red-test flag; no shipped target defines it); `:41-50` `Key6` (six `uint32_t` words) and `:52-66` `Key6Hash`; `:68-74` `key6()` (memcpy of `{x,y,z,normal_x,normal_y,normal_z}`); `:77-82` `samePoint6`; `:84-89` `samePosition3` (the pre-ticket x/y/z test, used only by the legacy path); `:97-106` `lessPoint6` (lexicographic on the six words, a strict total order); `:111-138` `appendNewPoints`; `:143-164` `dedupeExact6`.
- `mesh_processing_headless.cpp:43` `#include "surface_dedupe.h"`; `:231-237` the deleted `myclass2`/`myobject2` block replaced by a comment, `g_dedupeOn27` at `:237`; `:1565-1570` the append (measure `improvedRows09`, copy the destination, `appendNewPoints`, measure `appended09`, swap back); `:1572-1573` width/height; `:1580-1591` `dedupeExact6` and the unchanged gated swap; `:1592-1597` the `[DEDUPE-27]` line; `:6434-6437` `SFS_DEDUPE` parsing, default off.
- `CMakeLists.txt:50` `add_executable(SurfaceDedupeTest tests/test_surface_dedupe.cpp)`; `:53-54` `SurfaceDedupeTestLegacy` with `target_compile_definitions(... PRIVATE SURFACE_DEDUPE_LEGACY=1)`; `:57` both targets in `all_targets`.
- `tests/test_surface_dedupe.cpp:1-220` U1-U5 over a plain 6-float POD, no PCL; `CASE U<n> PASS|FAIL` per case, a `[SURFACE-DEDUPE-09]` summary, exit 1 on any failure.

**First run, superseded by §7.14** (kept as the record of what the six-value wording produced; the numbers below are that run's). W1-W4 are in as worded: bit-exact equality of all six values in the append (no epsilon), destination order untouched, appended rows in source order, one hash set built over the destination; the switch stays off with the reason in the comment at `:1575-1579`; the exporter, admit-sign filter, region-growing, sampling and the unbuilt root `*.cpp` copies are untouched. One deliberate deviation: W2 words the tail `dups_skipped=<k> appended=<a>`, the line prints `appended=` before `dups_skipped=`. The four legacy fields keep their place, so `dedupe27.py` still parses it.

### 7.2 The instrument line, before and after (Pot_J_Piece_12.S0)

```
before (arm A, 8d7cc60): [DEDUPE-27] surface=0 mode=off in=4222 out=2310
after  (arm B, ae7c750): [DEDUPE-27] surface=0 mode=off in=2376 out=2376 improved_rows=2310 appended=66 dups_skipped=1846
```

`in=` counts after the skip, so the stage27 invariant "PLY rows == in" holds: 2376 == 2376. The old `in - out` = 4222 - 2310 = 1912 is exactly what the append was offered: `appended_rows` 66 + `dups_skipped` 1846 = 1912.

### 7.3 Cells (out/axes09_cells.tsv, tab-separated)

```
piece	wall	arm	improved_rows	appended_rows	dups_skipped	in	out	ply_rows	n_dup6	n_distinct_pos	verdict
Pot_D_Piece_03	0	C	-1	-1	-1	100200	51569	100200	48631	51569	defect-present
Pot_D_Piece_03	0	D	49642	3114	47095	52756	52756	52756	1208	51548	FAIL(n_dup6=1208)
Pot_D_Piece_03	1	C	-1	-1	-1	102975	52906	102975	50069	52906	defect-present
Pot_D_Piece_03	1	D	52911	858	49211	53769	53769	53769	858	52911	FAIL(n_dup6=858)
Pot_J_Piece_12	0	A	-1	-1	-1	4222	2310	4222	1912	2310	defect-present
Pot_J_Piece_12	0	A2	-1	-1	-1	4222	2310	4222	1912	2310	defect-present
Pot_J_Piece_12	0	B	2310	66	1846	2376	2376	2376	66	2310	FAIL(n_dup6=66)
Pot_J_Piece_12	1	A	-1	-1	-1	4842	2590	4842	2252	2590	defect-present
Pot_J_Piece_12	1	A2	-1	-1	-1	4842	2590	4842	2252	2590	defect-present
Pot_J_Piece_12	1	B	2590	52	2200	2642	2642	2642	52	2590	FAIL(n_dup6=52)
```

`-1` on the three routing columns of arms A/A2/C is NA, not a measured zero: the pre-change binary prints none of them. **`appended_rows` is the log's `appended=` and nothing else: rows the append actually wrote.** `dups_skipped` is what it refused, so `appended_rows + dups_skipped` is what the segmented cloud offered (J12.S0 1912, J12.S1 2252, D03.S0 50209, D03.S1 50069). The arithmetic gate holds on every B/D row: `in == improved_rows + appended_rows` (2376 = 2310 + 66; 52756 = 49642 + 3114). (This table was regenerated on 2026-11-22 with the unified column; the earlier revision of this section had `appended_rows` = offered and a second `appended_missing` column holding the appended count - one count under two names, which is what the fix below removes. The PLY row counts, `n_dup6` and the verdicts are unchanged.)

### 7.4 Positions (out/axes09_seteq.tsv, tab-separated)

```
piece	wall	arm_a	arm_b	positions_a	positions_b	equal	nn_med_mm	nn_p90_mm
Pot_J_Piece_12	0	A	A2	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A	A2	2590	2590	yes	0.0	0.0
Pot_J_Piece_12	0	A	B	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A	B	2590	2590	yes	0.0	0.0
Pot_J_Piece_12	0	A2	B	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A2	B	2590	2590	yes	0.0	0.0
Pot_D_Piece_03	0	C	D	51569	51548	no	0.0	0.0
Pot_D_Piece_03	1	C	D	52906	52911	no	0.0	0.0
```

### 7.5 Gates

- **G1 PASS.** J12 arms A and A2: `n_dup6` = 1912 (S0) and 2252 (S1) on both arms, both walls.
- **G2 FAIL on one clause.** Arm B: `n_dup6` = 66 (S0) and 52 (S1), not 0. `in == out` (2376, 2642), `ply_rows == in` (2376, 2642), `dups_skipped` > 0 on both walls (1846, 2200), `appended_rows` 66 and 52 (>= 0), arithmetic gate holds (`2376 = 2310 + 66`, `2642 = 2590 + 52`). Cause measured in 7.7, not a leftover unconditional append.
- **G3 FAIL on one clause.** Arm C: `n_dup6` = 48631 (S0), 50069 (S1) > 0 as required. Arm D: `appended_rows` > 0 (3114, 858) as required, but `n_dup6` = 1208 (S0) and 858 (S1), not 0.
- **G4 PASS.** `seteq` A vs A2: 2310/2310 and 2590/2590 positions, equal, `nn_med_mm` 0.000000, `nn_p90_mm` 0.000000. A vs B: same, 0.000000/0.000000. Bar = 2 x 0.000000 + 0.01 = 0.010000, so 0.000000 <= 0.010000 on both walls. On D03 the C vs D sets differ by 56 and 35 positions (0.1 % of ~51.5 k) — the draw spread of §0, not a shape change; the two J12 arms happened to draw identical clouds.
- **G5 PASS.** Red exit 1 with `cases=5 pass=0 fail=5`, green exit 0 with `cases=5 pass=5 fail=0`, `out/UNIT.txt` present (7.6).

### 7.6 Unit test (out/UNIT.txt, both binaries built from `ae7c750`)

```
RED run:   SurfaceDedupeTestLegacy (cmake -DSURFACE_DEDUPE_LEGACY=1, pre-ticket behaviour) exit=1
[SURFACE-DEDUPE-09] build=SURFACE_DEDUPE_LEGACY=1 (old behaviour: append everything, compare x/y/z)
CASE U1 FAIL
INFO U1 offered=4 appended=4 skipped=0 rows=8 unchanged=no
CASE U3 FAIL
INFO U3 append_skipped=0 append_rows=5 dedupe_in=2 dedupe_out=1 (want 0,5 and 2,2)
CASE U5 FAIL
INFO U5 rows=4 distinct=2 want=3 a_kept=no normal_pair_kept=no unique_kept=no deterministic=yes
[SURFACE-DEDUPE-09] cases=5 pass=0 fail=5
GREEN run: SurfaceDedupeTest       (shipped code path, no define)                      exit=0
[SURFACE-DEDUPE-09] build=shipped (append only new rows, compare all six values)
CASE U1 PASS
INFO U1 offered=4 appended=0 skipped=4 rows=4 unchanged=yes
CASE U2 PASS
INFO U2 offered=4 appended=2 skipped=2 rows=6 order_kept=yes
CASE U3 PASS
INFO U3 append_skipped=0 append_rows=5 dedupe_in=2 dedupe_out=2 (want 0,5 and 2,2)
CASE U4 PASS
INFO U4 second_skipped=3 rows=6 unchanged=yes prefix_then_offered=yes
CASE U5 PASS
INFO U5 rows=4 distinct=3 want=3 a_kept=yes normal_pair_kept=yes unique_kept=yes deterministic=yes order=[(10.0,0.0,0.0|0.0,0.0,1.0) (10.0,0.0,0.0|0.0,0.0,-1.0) (11.0,0.0,0.0|0.0,0.0,1.0)]
[SURFACE-DEDUPE-09] cases=5 pass=5 fail=0
```

U1 and U2 are the append (A holds, source offered), U3 the same-position different-normal row kept by both paths, U4 idempotence and "A then the missing rows in source order", U5 the W3 red case (the x/y/z rule yields 2 rows where the 6-value rule yields 3).

### 7.7 Why G2 and G3 failed on the first run, measured: the residual is a 1-ulp normal twin, not a second append (this section is what prompted the amendment, §7.14)

The append is bit-exact, and the cloud it produces holds **zero** exact 6-float duplicates. That is not inferred from the log, it is printed from the cloud itself (throwaway instrumentation, jobs 35477246/35477289, branch `09-diag` at `66f1194`, deleted after use; the ticket branch never carried it):

```
[DIAG09-APPEND] dest_before=2310  src=1912 appended=66  skipped=1846 appended_with_same_position=66
[DIAG09] finish surface=0 rows=2376 exact_dups=0
[DIAG09] prewrite improved1_rows=2376 improved1_dups=0 cluster1_rows=2376 cluster1_dups=0 flip=false
[DIAG09-APPEND] dest_before=49909 src=50209 appended=2800 skipped=47409 appended_with_same_position=1217
[DIAG09] finish surface=0 rows=52709 exact_dups=0
```

Every appended row on J12 has a destination row at **exactly the same position** (66 of 66, 52 of 52). The six floats differ in one word, by one bit:

```
[DIAG09-POS] dest_row=498 a0=4107617c a1=418e600d a2=43e918d5 a3=bde287a5 a4=bf46f31f a5=3f1e98ff
                        b0=4107617c b1=418e600d b2=43e918d5 b3=bde287a4 b4=bf46f31f b5=3f1e98ff
```

`a3`/`b3` is `normal_x`: -0.11061028391122818 against -0.11061027646064758, one float32 ulp (7.45e-9) apart. The other five words are bit-identical, on every one of the 8+8 printed pairs (J12 and D03 alike; the differing word is always `normal_x`). So W1 as worded — exact bit equality of all six values — **must** append these rows: they are not duplicates, they are the same position with a normal that differs in its last bit, which is the very case W3/U3 require to survive.

The file-level duplicate appears one step later: `savePLYFile(..., false)` at `mesh_processing_headless.cpp:5985` writes ASCII at **8 significant digits** (trailing zeros trimmed), and at |n| ~ 0.1 the 8-digit grid (1e-8) is coarser than the ulp (7.45e-9), so both values print as `-0.11061028`. Two distinct floats, one line of text — and `n_dup6`, defined on the exported PLY, counts the second line as a repeat of the first.

Counted both ways: after W1, J12.S0 exports 2376 rows of which 66 (2.8 %) are this class; D03.S0 52756 rows of which 1208 (2.3 %) are; D03.S1 53769 of which 858 — and on S1 `appended_rows` = 858 = the twin count, i.e. every appended row on that wall is a near-copy, while S0's 3114 appended rows contain ~1900 genuinely new positions (which is what G3's `appended_rows > 0` protects and they do arrive).

**So the second source is not rows duplicating inside the improved cloud** (measured 0, above): it is the append's bit-exact rule at `mesh_processing_headless.cpp:1567-1570` admitting a same-position row whose single normal word is one ulp off, plus the 8-digit ASCII export at `mesh_processing_headless.cpp:5985` collapsing the pair into one line. Neither is reachable from W1-W4 without overreaching: an epsilon in the append is forbidden by W1 ("no epsilon ... a tolerance would delete real points"), and the exporter is out of scope by W4.

**The gate and the unit-test case are in direct tension.** U3 (line 59) requires a source row with A's xyz and a different normal to be **appended**, and W1 fixes presence as bit equality of all six values; G2 (line 96) requires the exported file to carry no repeated 6-tuple. Both can hold only if no row's six values differ from its position twin by less than the export's printing resolution. On these two pieces they do: 66, 52, 1208 and 858 of them. So `n_dup6 == 0` is not reachable under W1/W3/U3 on this corpus, and the residual is reported rather than removed by quietly relaxing the rule.

### 7.8 Two things in §0 that this run contradicts

- **"Same-xyz-different-normal rows: zero everywhere."** That is a statement about the text. In the float cloud J12.S0 holds 66 same-position rows whose normal differs by exactly one ulp (1217 on D03.S0 in the second draw); Ticket 08's scan cannot see them because the 8-digit text is identical. They are real distinct rows under the 6-float definition the ticket adopts, and they are the whole of the residual above.
- **Line 77's cluster question — no.** On J12.S0 the append source held 1912 rows against clusters `sizes=1928,2252,269,122,112,58`: surface 1's source is exactly the 2252 cluster, surface 0's is 16 rows short of the 1928 one (`t72::trimBreakFace72` at `:5913` runs before the fit). The November 1928 was the duplicate count of a different draw, so the equality noted in §3 was a coincidence of that draw, not the cluster identity.

### 7.9 Consequence for the recorded numbers

Own Part A becomes the **111/123** of Ticket 08 when surfaces are next regenerated; **nothing is re-measured here**. Concretely, a future own run writes 2376 rows where this piece used to write 4222 (S0) and 2642 where it used to write 4842 (S1), so every point-based cost on our walls drops to its distinct-row value and the de-duplicated numbers Ticket 08 measured in memory become the numbers any new run produces. Shape is unchanged: the position set of arm B equals arm A's exactly (7.4), and the 66 residual rows sit on positions the wall already has. The 111/123 claim is Ticket 08's and rests on its own Part A re-run; this ticket only makes the writer agree with it.

### 7.10 Corpus

`[JOB] CORPUS-UNCHANGED` — `logs/corpus_inputs_before.md5` and `logs/corpus_inputs_after.md5` (Point, Mesh, Axes, Breakline_0/1, Surfaces Surface_0/1.xyz for both pieces) diff clean (`logs/corpus_inputs.diff` empty). Nothing was written under the corpus or under `C:/PR/SfSpp_preprocessing/Dataset`; all staging is symlink-in, deleted per cell by `run_cell27.sh`.

### 7.11 Figure

`out/render09_rows.png`, 135160 B, two panels (Pot_J_Piece_12, Pot_D_Piece_03), per written wall a bar pair "PLY rows / distinct positions" for the old and the new arm with the counts printed, log y. It shows row multiplicity, not geometry: no render of the surface is in it, and it does not show the 1-ulp normals of 7.7 (the file cannot).

### 7.12 Jobs, sacct, run directory, index

```
35475379  t09-dedup  sapphire  FAILED     1:0  00:00:03  2026-11-21T22:27:31   script bug (local var expanded under set -u), nothing ran
35475519  t09-dedup  sapphire  FAILED     1:0  00:23:42  2026-11-21T22:54:56   the job itself: build x2, unit test x2, 5 cells, analysis; exit 1 because the analyzer exits 1 on a failing gate
35477246  t09diag    sapphire  COMPLETED  0:0  00:01:24  2026-11-21T23:12:26   diagnostic: build 66f1194 + J12 cell (7.7)
35477289  t09diag2   sapphire  COMPLETED  0:0  00:07:56  2026-11-21T23:22:45   diagnostic: D03 cell with the same binary
```

Run of record: `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1121_ae7c750_t09-surface-dedup/` (`logs/ work/ out/ cells/ pins/ build/ instrsrc/`), `out/sacct_final.txt` holds the final states — `out/sacct_all.txt` was written while 35475519 was still RUNNING, so it shows RUNNING. Diagnostic run: `runs/20261121-1210_66f1194_t09-diag/`. `runs/index.tsv` row appended by the job: `20261121-1121_ae7c750_t09-surface-dedup  35475519  ae7c750  t09-dedup` (verdict and human_note left empty for the coordinator).

### 7.13 What is still owed

- An own-surface regeneration ticket: the walls now change rows, and the 111/123 becomes what future runs must match.
- The E1 edgeline re-measure is already answered by Ticket 27 ("a storage fix, not a counting fix") and is not re-opened here.
- G2/G3's `n_dup6 == 0` was unreachable with a six-value rule (§7.14). With W1/W3 as amended (position) it is reachable, and the re-run met it (§7.15: G2 and G3 both PASS). The staged checker `C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` needs no change: its gates already count `n_dup6`, which is now the same set as the repeated positions.

### 7.14 Coordinator's amendment after the first run (2026-11-21 23:35) - position, not six floats

The first run (branch `09`, `ae7c750`, Reading `writer-fixed-second-duplicate-found`) built the append exactly as W1 first worded it - bit-exact on all six floats - and the append is sound: every row it refused was already there (`dups_skipped` 1 846 / 2 200 on `Pot_J_Piece_12`), and the finished cloud holds zero exact six-value duplicates (`[DIAG09] finish rows=2376 exact_dups=0`, `in == out == 2376`). Yet the exported PLY still shows 66 repeats on S0 and 52 on S1 (`Pot_D_Piece_03`: 1 208 and 858). The cause is measured, not guessed: each appended row has a destination row at exactly the same position whose normal differs in **one word by one float32 ulp** (8 of 8 printed pairs; e.g. `normal_x` hex `bde287a5` vs `bde287a4`, -0.11061028391122818 vs -0.11061027646064758, 7.45e-9; the other five words identical). `savePLYFile(..., false)` (:5985) writes ASCII at 8 significant digits, so both rows print `-0.11061028`: at the precision of the only artefact anyone reads they are the same row, twice.

So the ticket is amended where it was wrong, and the code change is the **position** rule the shipped TICKET-27 block already used:

- **W1** skips on bit-identical x, y, z and keeps the destination row (its normal included), instead of comparing six floats.
- **W2** prints `normal_maxdiff=`, the largest normal component difference among the skipped pairs, so no material normal can be dropped silently (expected at most one ulp; anything larger is a finding, not a rounding).
- **W3** keeps the shipped x/y/z comparison and only makes it deterministic (one row per position, order-independent); the six-value extension is withdrawn.
- **U3** becomes the skip-with-one-ulp-normal case and **U5** the position de-duplication; the red case is the unconditional append, which is the defect itself.
- The five cells, the tables and the gates are unchanged. The re-run must show `n_dup6 == 0` on the new arms with `in == out`, `PLY rows == in`, `dups_skipped > 0` and `normal_maxdiff` at ulp scale; `accept.py` needs no change.

The first run's numbers stay in §7.1-§7.12 as the record of what the six-value wording produced; the write-back must add this section's replacement numbers beside them and set Reading `writer-writes-each-point-once` only if the re-run meets the gates.

### 7.15 Re-run after the amendment (2026-11-22) - the position rule

**What ran.** Commit `3658152` (parent `1ec845e`) in run directory `runs/20261121-1238_3658152_t09-surface-dedup/`. Job `35477684` `COMPLETED 0:0`, elapsed `00:20:52`, ended `2026-11-22T00:00:46`. A first submission of the same script, `35477665`, `FAILED 2:0` in two seconds because it fetched the repo before `3658152` had been pushed (`[JOB] FATAL rc=2 commit 3658152 not in .../sfs_preprocessing`); its record is kept as `RUN-FAILED-35477665.txt` in the run directory and in `out/sacct_attempts.txt`. Nothing ran in it - no build, no cell, no corpus write. The two commits of record are `8d7cc60` (OLD) and `3658152` (NEW). The analyzer was then corrected to one meaning per column - `appended_rows` is the log's `appended=`, the rows actually written, and the identity is `in == improved_rows + appended_rows`, with `appended_rows + dups_skipped` the offered set - and re-run offline against the same cells for both runs (`work/t09_analyze_v3.py`, md5 `289452fe909c86f43b1366ca186b35ec`). No geometry, PLY row count, `n_dup6` or gate changes: the tables lost the duplicate `appended_missing` column, and the first run's `out/` was regenerated the same way (its table keeps its 66 and 52 appended rows on J12 and 3114 and 858 on D03). The commit that carries this write-back also corrects three stale comments in `mesh_processing_headless.cpp` (:43, :231-233, :1571-1573); no statement in it changes behaviour, and the tables below come from `3658152`.

**Code as shipped (file:line on this commit).** `surface_dedupe.h:51` `Key3` (the three position words), `:61` `Key3Hash`, `:77` `key3()`, `:86` `samePosition3` (bit equality of x/y/z, no tolerance), `:93` `Key6` and `:124` `lessPoint6` (the deterministic order: x, y, z, then the three normal words), `:138` `normalComponentMaxDiff`, `:154-190` `appendNewPoints(dest, src, double* normalMaxDiffOut)` (an `unordered_map` over the destination's positions; a matched position is skipped and its normal difference accumulated, otherwise the row is appended), `:197-216` `dedupePositions` (sort with `lessPoint6`, keep the first row of each position run; the legacy build returns the rows unchanged, which is the pre-ticket behaviour). `mesh_processing_headless.cpp:43` the include; `:231-238` the comment that replaced the deleted `myclass2`/`myobject2` block, `g_dedupeOn27` at `:238`; `:1574-1580` the append; `:1582-1583` width/height; `:1592-1595` `dedupePositions`; `:1598-1603` the gated swap; `:1604-1610` the `[DEDUPE-27]` line in W2's order; `:6447-6450` `SFS_DEDUPE` parsing, default off. `tests/test_surface_dedupe.cpp` (247 lines) U1-U5. `CMakeLists.txt:50` `SurfaceDedupeTest`, `:53-54` `SurfaceDedupeTestLegacy` with `SURFACE_DEDUPE_LEGACY=1`, `:57` both in `all_targets`. Diffstat of the four code files against `8d7cc60`: 522 insertions, 63 deletions - `CMakeLists.txt` 10, `mesh_processing_headless.cpp` 108, `surface_dedupe.h` 220 new, `tests/test_surface_dedupe.cpp` 247 new.

**The instrument line, before and after (`Pot_J_Piece_12.S0`).**

```
A  [DEDUPE-27] surface=0 mode=off in=4222 out=2310
A2 [DEDUPE-27] surface=0 mode=off in=4222 out=2310
B  [DEDUPE-27] surface=0 mode=off in=2310 out=2310 improved_rows=2310 dups_skipped=1912 appended=0 normal_maxdiff=0.0000
```

`Pot_J_Piece_12.S1`: A and A2 `in=4842 out=2590`; B `in=2590 out=2590 improved_rows=2590 dups_skipped=2252 appended=0 normal_maxdiff=0.0000`. `Pot_D_Piece_03`: C `in=100160 out=51598` (S0) and `in=102979 out=52910` (S1); D `in=51576 out=51576 improved_rows=49931 dups_skipped=48564 appended=1645 normal_maxdiff=0.0000` (S0) and `in=52877 out=52877 improved_rows=52877 dups_skipped=50069 appended=0 normal_maxdiff=0.0000` (S1).

**Cells (`out/axes09_cells.tsv`, tab-separated).** `-1` is NA on the OLD arms: the pre-ticket binary prints no `improved_rows`/`appended`/`dups_skipped`, so those fields are not a measured zero.

```
Pot_D_Piece_03	0	C	-1	-1	-1	100160	51598	100160	48562	51598	defect-present
Pot_D_Piece_03	0	D	49931	1645	48564	51576	51576	51576	0	51576	PASS
Pot_D_Piece_03	1	C	-1	-1	-1	102979	52910	102979	50069	52910	defect-present
Pot_D_Piece_03	1	D	52877	0	50069	52877	52877	52877	0	52877	PASS
Pot_J_Piece_12	0	A	-1	-1	-1	4222	2310	4222	1912	2310	defect-present
Pot_J_Piece_12	0	A2	-1	-1	-1	4222	2310	4222	1912	2310	defect-present
Pot_J_Piece_12	0	B	2310	0	1912	2310	2310	2310	0	2310	PASS
Pot_J_Piece_12	1	A	-1	-1	-1	4842	2590	4842	2252	2590	defect-present
Pot_J_Piece_12	1	A2	-1	-1	-1	4842	2590	4842	2252	2590	defect-present
Pot_J_Piece_12	1	B	2590	0	2252	2590	2590	2590	0	2590	PASS
```

**Set equality (`out/axes09_seteq.tsv`).**

```
Pot_J_Piece_12	0	A	A2	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A	A2	2590	2590	yes	0.0	0.0
Pot_J_Piece_12	0	A	B	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A	B	2590	2590	yes	0.0	0.0
Pot_J_Piece_12	0	A2	B	2310	2310	yes	0.0	0.0
Pot_J_Piece_12	1	A2	B	2590	2590	yes	0.0	0.0
Pot_D_Piece_03	0	C	D	51598	51576	no	0.0	0.0
Pot_D_Piece_03	1	C	D	52910	52877	no	0.0	0.0
```

**Row identity, so the table can be checked without the log.** A written wall holds `improved_rows + appended_rows` rows: the fit's rows plus the rows the append actually wrote. The append refused `dups_skipped` rows at positions the surface already held, so the cloud offered `appended_rows + dups_skipped` rows in all. Worked: J12 B S0 `2310 = 2310 + 0` with 0 written and 1912 refused; J12 B S1 `2590 = 2590 + 0`, 2252 refused; D03 D S0 `51576 = 49931 + 1645`, 48564 refused; D03 D S1 `52877 = 52877 + 0`, 50069 refused. On J12 the offered count is independently measurable because the draw is deterministic: the old arm's `in - improved_rows` = 4222 - 2310 = 1912 and 4842 - 2590 = 2252, exactly `appended_rows + dups_skipped`, and the analyzer checks that on every J12 wall. D03's two arms are separate draws, so the offered-set identity is not exact there and is not gated on.

**Gates.** All five hold on these numbers.

- **G1 PASS** - J12 arms A and A2, both walls: `n_dup6` 1912 (A S0), 2252 (A S1), 1912 (A2 S0), 2252 (A2 S1); all `> 0`, and A and A2 are identical row for row.
- **G2 PASS** - J12 arm B, both walls: `n_dup6 == 0`; S0 `in=2310 out=2310 ply_rows=2310`, S1 `in=2590 out=2590 ply_rows=2590`; `dups_skipped` 1912 and 2252 `> 0`; `appended_rows` 0 and 0 (the fix wrote nothing, because every offered row was already there); `in == improved_rows + appended_rows` holds on both (2310 = 2310 + 0, 2590 = 2590 + 0) and `appended_rows + dups_skipped` = 1912 and 2252 is exactly what the old arm's `in - improved_rows` says was offered.
- **G3 PASS** - D03 old arm C: `n_dup6` 48562 (S0) and 50069 (S1), and its PLY carries 100160 / 102979 rows for 51598 / 52910 distinct positions. New arm D: `n_dup6 == 0` on both walls, `in == out == ply_rows` (51576, 52877), and `appended_rows = 1645 > 0` on S0 - the new tail rows still arrive.
- **G4 PASS** - J12 draw control, both walls: A vs A2 `nn_med = 0.000000`, A vs B `nn_med = 0.000000`, bar `2 x 0.000000 + 0.01 = 0.010000`; positions 2310/2310 and 2590/2590, `equal = yes` in all four rows.
- **G5 PASS** - `out/UNIT.txt`, red exit 1, green exit 0 (quoted below).

**`normal_maxdiff` reads 0.0000 on all four new-arm surfaces, and that is the format, not a measurement of zero.** The field prints at the stream's four decimals, so 0.0000 means "below 5e-5"; a material difference would have printed, e.g., 0.0100, and none did - which is the guard's purpose, since the row that is kept is the surface's own and the skipped one is the near-copy. It does **not** display the ulp. The ulp is shown where it can be: the unit test prints `INFO U3 ... normal_maxdiff=1.1920929e-07 ulp=1.1920929e-07`, and §7.7's diagnostic printed the hex words and found exactly one float32 ulp on every pair it examined. The field is left as it is (it catches material differences); a future run that wanted ulp resolution would print it scientific, and the comment at `mesh_processing_headless.cpp:1571-1573` says so.

**The clean control is J12, not D03.** On J12, A and A2 are the same binary byte for byte (proved with `cmp`), and their numbers are identical to each other and to the first run - 4222 rows / 2310 distinct (S0), 4842 / 2590 (S1) - while A's distinct positions and B's position set are equal with `nn_med = 0.000000`. So on J12 the fix removed exactly the 1912 and 2252 re-appended rows and moved no position. **D03's C and D are separate draws** (the mesh stage takes 30 unseeded ray-cast points): C wrote 100160 / 102979 rows with 51598 / 52910 distinct positions, D 51576 / 52877 positions - 22 and 33 positions apart, every one within 0.0 mm of the other set. That difference is a draw effect and is **not** attributable to the fix from this run; what D03 proves here is G3's `appended_rows > 0` (1645 on S0).

**D03's second wall adds nothing new:** D S1 has `appended_rows = 0` - every one of the 50069 rows offered on that wall was already at a position the surface held (`dups_skipped = 50069`). G3's "the new tail rows still arrive" therefore rests on S0's 1645, as it must; S1 contributes the "no repeated position, `in == out`" half.

**Unit test (`out/UNIT.txt`, built twice from `3658152`).** RED `SurfaceDedupeTestLegacy` (pre-ticket behaviour) **exit 1**:

```
CASE U3 FAIL / INFO U3 append_skipped=0 append_rows=5 unchanged=no normal_maxdiff=0 ulp=1.1920929e-07 dedupe_in=2 dedupe_out=2 kept_surface_row=no (want 1,4,yes,ulp,2,1,yes)
CASE U5 FAIL / INFO U5 rows=4 distinct=4 want=2 a_kept=no unique_kept=no order_independent=no
[SURFACE-DEDUPE-09] cases=5 pass=0 fail=5
```

GREEN `SurfaceDedupeTest` (shipped code path) **exit 0**:

```
CASE U1 PASS / INFO U1 offered=4 appended=0 skipped=4 rows=4 unchanged=yes normal_maxdiff=0
CASE U3 PASS / INFO U3 append_skipped=1 append_rows=4 unchanged=yes normal_maxdiff=1.1920929e-07 ulp=1.1920929e-07 dedupe_in=2 dedupe_out=1 kept_surface_row=yes
CASE U5 PASS / INFO U5 rows=4 distinct=2 want=2 a_kept=yes unique_kept=yes order_independent=yes order=[(10.0,0.0,0.0|0,0.0,1.0) (11.0,0.0,0.0|0,0.0,1.0)]
[SURFACE-DEDUPE-09] cases=5 pass=5 fail=0
```

**Corpus.** `[JOB] CORPUS-UNCHANGED` in `logs/slurm-35477684.out`; `logs/corpus_inputs.diff` is 0 bytes and `logs/corpus_inputs_before.md5` / `..._after.md5` both hold 14 lines (Point, Mesh, Axes, Breakline_0/1, Surface_0/1.xyz for both pieces). Nothing was written under the corpus or under `C:/PR/SfSpp_preprocessing/Dataset`. The pass is **proved by the empty diff and the 14-vs-14 manifests**, not by the summary: `out/axes09_summary.json` first said `CORPUS-CHECK-MISSING` because the job ran the analyzer (`submit.sbatch:192`) before it wrote the diff (`:196`) - the analyzer's path was already `logs/corpus_inputs.diff`. Fixed offline in `work/t09_analyze.py` (`corpus_check()` now falls back to the two manifests; `sacct_jobs()` now parses the pipe-separated `sacct -P` output, which the padded table's empty `Partition` columns and dashed header had shifted) and refreshed with `--json-only`; the geometry tables and the gates are untouched by that, the run's commit of record stays `3658152`, and `work/CHANGELOG_analyze09.txt` records both edits (patched analyzer md5 in `logs/analyze_patched.md5`). The summary now reads `diff_bytes 0, CORPUS-UNCHANGED`.

**Consequence for the recorded numbers.** Own Part A becomes the **111/123** of Ticket 08 when surfaces are next regenerated; **nothing is re-measured here**. On `Pot_J_Piece_12` the writer now emits 2310 rows where it emitted 4222 (S0) and 2590 where it emitted 4842 (S1) - exactly the distinct-position counts Ticket 08 measured in memory - and it emits no row at a position the wall already had.

**Figure.** `out/render09_rows.png`, 132921 B, same layout as §7.11: per piece, per written wall, a solid bar for PLY rows and a hatched bar for distinct positions, old arm against new arm, counts printed, log y. On J12 the new pair is flush (2310/2310, 2590/2590) while the old pair is not (4222/2310, 4842/2590); on D03 the new pairs are flush too (51576/51576, 52877/52877). It shows row multiplicity, not shape, and it cannot show the one-ulp normals.

**Jobs and sacct** (`out/sacct_attempts.txt`):

```
35477665  t09-dedup  FAILED     2:0  00:00:02  2026-11-21T23:39:12   submission raced the push; nothing ran
35477684  t09-dedup  COMPLETED  0:0  00:20:52  2026-11-22T00:00:46   the run of record: build x2, unit test x2, 5 cells, analysis
```

Run of record `runs/20261121-1238_3658152_t09-surface-dedup/`; `runs/index.tsv` row appended by the job: `20261121-1238_3658152_t09-surface-dedup  35477684  3658152  t09-dedup` (verdict and human_note empty for the coordinator). The laptop record is `C:/PR/artifacts/axis-parity-09/` - this run's `axes09_cells.tsv`, `axes09_seteq.tsv`, `axes09_summary.json`, `UNIT.txt`, `dedupe27_lines.txt`, `sacct_all.txt`, `sacct_final.txt`, `render09_rows.png`; the first run's copies are kept beside them in `firstrun/`.

## Lead verification (2026-11-22, before recording)

Every number the write-back rests on was re-read by the coordinator at the source, not taken from the report:

- verified: `python C:/PR/artifacts/dsh-handover/axis-parity-09/accept.py` -> `ACCEPTANCE PASSED (reading=writer-writes-each-point-once)`, exit 0.
- verified: `C:/PR/artifacts/axis-parity-09/axes09_cells.tsv` recomputed row by row -> `in == improved_rows + appended_rows` on every new-arm row (J12 B S0 2310 = 2310 + 0; J12 B S1 2590 = 2590 + 0; D03 D S0 51576 = 49931 + 1645; D03 D S1 52877 = 52877 + 0), and `appended_rows + dups_skipped` = 1912 / 2252 / 50209 / 50069, which is what each wall offered.
- verified: `ssh spartan` grep of the run's `out/dedupe27_lines.txt` -> B S0 `in=2310 out=2310 improved_rows=2310 dups_skipped=1912 appended=0 normal_maxdiff=0.0000`, B S1 `in=2590 out=2590 improved_rows=2590 dups_skipped=2252 appended=0`; A and A2 identical `in=4222 out=2310` / `in=4842 out=2590`.
- verified: `C:/PR/artifacts/axis-parity-09/axes09_seteq.tsv` -> J12 A-A2, A-B and A2-B all `equal=yes`, `nn_med_mm=0.0`, positions 2310/2310 and 2590/2590: the fix changed no position on the piece whose draw reproduced.
- verified: `ssh spartan sacct -j 35477684 -X` -> `COMPLETED 0:0`, elapsed `00:20:52`; `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` -> row `20261121-1238_3658152_t09-surface-dedup  35477684  3658152  t09-dedup`, verdict and human_note empty.
- verified: `ssh spartan` on the run's `logs/slurm-35477684.out:80` -> `[JOB] CORPUS-UNCHANGED`; `logs/corpus_inputs.diff` 0 bytes; `corpus_inputs_before.md5` and `..._after.md5` 14 lines each.
- verified: `C:/PR/artifacts/axis-parity-09/UNIT.txt` -> red `exit=1` `cases=5 pass=0 fail=5`, green `exit=0` `cases=5 pass=5 fail=0`, with U3's `normal_maxdiff=1.1920929e-07 ulp=1.1920929e-07`.
- verified: code at `3658152` -> `surface_dedupe.h:155-190` `appendNewPoints` skips on `key3` (position), keeps the destination row and accumulates `normalMaxDiffOut`; `surface_dedupe.h:198-216` `dedupePositions` sorts by the six words and keeps the first row of each position; `mesh_processing_headless.cpp:1575` is the call and `:1602-1607` the log line that prints `dups_skipped` and `normal_maxdiff`.
- verified: `read` of `C:/PR/artifacts/axis-parity-09/render09_rows.png` (1890x896) -> J12 B and D03 D bar pairs flush at 2310/2310, 2590/2590, 51576/51576, 52877/52877; the old arms still gapped at 4222/2310, 4842/2590, 100160/51598, 102979/52910. The picture shows what the table says.
- checked and corrected by the coordinator during verification: (a) the staged checker's G2 identity had the wrong sign (`in == improved + appended - skipped`); the run's numbers satisfy `in == improved + appended`, and the checker now says so. (b) The column `appended_rows` had silently changed meaning between the first run's table (rows written, 66) and the re-run's (rows offered, 1912); it is now rows written in both tables, `appended_missing` is retired, and the first-run table in §7.3 was regenerated from its own cells to the same column set.

Not verified, and said so in the write-back: the D03 C-vs-D position difference (22 and 33 positions) has no same-draw control and is reported as a draw effect, not as evidence about the fix.

**End state:** ready
Reading: writer-writes-each-point-once
