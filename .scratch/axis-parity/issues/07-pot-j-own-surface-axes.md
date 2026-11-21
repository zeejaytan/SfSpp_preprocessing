# 07: Why do Pot J's axes lose on our own surfaces, and can one scale-free fix close it?

**What to build:** A diagnosis first, then at most two pre-registered fixes, all prototyped on Spartan only (ZERO tracked edits in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`; export a clean `-p1` unified `impl_t07.diff` over commit `325a0a8`, the head of branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`, which already contains the shipped tri selector in `sfs_axes/meridian.py` and `sfs_axes/joint.py`; check `git apply --ignore-whitespace --check`). Goal: make the own-code E2E chain reach Pot J `>= 8/11, >= 16/21` (the Authors-axes control floor) without dropping any other pot below its floor.

**Answers:** E1
**Blocked by:** None (Ticket 03 executed at `325a0a8`, `Reading: tri-shipped-own-e2e-differs`, unmerged)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-21)
**Branch:** 07-pot-j-own-surface-axes, in /c/PR/worktrees/sfs/07
**Worker:** dsh one-shot subagent w07-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check staged separately by lead

---

## 1. What is already established (read Ticket 03 write-back first; do not re-derive)

Source: `.scratch/axis-parity/issues/03-ship-joint-axis-and-e2e-own-surfaces-gate.md` (on branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`; read with `git show 325a0a8:<path>`), Ticket 06 Comments (on `main`), Ticket 03 Spartan run dirs under `/data/gpfs/projects/punim2657/SfSpp/runs/*t03*` (`out/axes03_tri` = axes from Authors' surfaces, `out/axes03_own` = axes from our own `MeshPreprocessingHeadless` surfaces, `runs/20261121-1600_2e951d9_t03-jctl` = the Pot J control).

- Own-code E2E with the tri selector: 9 of 10 pots meet their floor. **Pot J: `8/11 5/21` and `7/11 4/21`** vs floor `8/11 16/21`; the control (same breaklines, Authors' released axes) holds `8/11 16/21`.
- Same chain with axes extracted from the **Authors' surfaces**: Pot J `8/11 15/21` and `8/11 16/21`. So breaklines, assembler and selector code are not the cause; the axes extracted from our surfaces for Pot J are.
- Per-piece rank-0 angle, ours vs Authors' surface: `Pot_J_Piece_12` `81.4°` vs `28.3°`, `Pot_J_Piece_06` `53.4°` vs `47.9°`, `Pot_J_Piece_07` `13.3°` vs `27.2°`, `Pot_J_Piece_01` `82.8°` vs `89.1°`. Offline Pot J `K3` is `8/11` on Authors' surfaces and `7/11` on ours. Only 4 (Authors') / 5 (ours) of 11 Pot J stems reach rank-0 under `10°`.
- Dead ends already closed (do NOT retest): see `.scratch/axis-parity/spec.md` §4; `K` capping on base fragments is out of scope; `dual_k2` and plain `axes335` are known (Pot J own-surface numbers for them are in Ticket 05/03 outputs and may be used as references).

## 2. Phase 1 — Diagnosis (read-only, no new selector; Spartan compute nodes only)

For all 11 Pot J stems plus the 3 other pots' worst own-vs-Authors gaps (list them from `axes03_audit.json`), on both surface sets, using cached pools if they exist:

1. **Surface comparison:** point count, bounding size, point density (mm between nearest neighbours), normal quality (angle between our normal and the Authors' normal at nearest point, median/90th percentile), and whether the sherd's rim/edge band is trimmed differently. Report per stem in a TSV.
2. **Arm attribution:** for each stem and surface, rank-0 and best-of-`K` angle for `A1`, `B2`, `P`, and the merged `tri`; and whether a candidate within `10°` of GT exists in the seed pool at all (M1) or was lost in refinement/dedup (M2) or lost in ranking (M3). Same taxonomy as Ticket 01 (`.scratch/axis-parity/issues/01-diagnose-14-losses-and-own-surfaces-audit.md`).
3. **Name the cause in one of these buckets (pick, with the numbers):** (a) our normals are noisier or flipped on Pot J so `A1`/`B2` are misled; (b) our surfaces are trimmed/denser/thinner so the position-only `P` arm degrades; (c) pool seeds miss the true basin on our surfaces; (d) something else — say what.
4. Look at it: render at least 4 Pot J stems (GT, Authors' axes, ours on both surfaces) with the sherd points, as `render07_diag.png`, before writing the cause.

**Phase 1 stop rule:** if the cause cannot be put in a bucket with per-stem evidence, finish with `Reading: pot-j-cause-not-isolated` and run NO Phase 2.

## 3. Phase 2 — At most two pre-registered fixes (only if Phase 1 isolates a cause)

Write the fixes into `<run>/work/PREREG07.md` BEFORE running them: each must be scale-free (no per-pot, per-piece or object-size constant), tied to the named bucket, and implemented in `sfs_axes/t07/` plus `tests/test_t07_*.py` (prototype namespace, not shipped). Candidates by bucket (pick only what the evidence points to, max 2):
- (a) normal-quality-weighted or robustly re-estimated normals for `A1`/`B2` residuals (e.g. a local-PCA normal consistency weight), or dropping `A1`/`B2` rank-0 priority when their normal-consistency score is poor and promoting `P`;
- (b) matching the surface preprocessing that the position-only arm expects (e.g. the sampling/stride the `P` arm uses), only if the audit shows a density/trim difference;
- (c) enlarging or diversifying the seed pool by a scale-free rule.

**Part A bars (offline, on `141` GT pieces, both surface sets; Authors' surface numbers must not drop below Ticket 06/03):** Authors `110/141 K1`, `128/141 K3`, median `<= 2.7054°`, `Pot A d_gt_to_est <= 2.4733 mm`, `Pot G 7/7 K=1`, `SignAxisGuard 0/18` rank-0 and `0` worst-case; own surfaces `K1 >= 116/141`, `K3 >= 127/141`, **own `Pot J K3 >= 8/11`** (up from `7/11`), own `Pot_J_Piece_12` best-of-`K <= 30°`. If neither fix passes, finish with `Reading: pot-j-own-surface-not-fixed-offline` (no E2E).

## 4. Phase 3 — E2E (only if a fix passes Part A), same own-code chain as Ticket 03 Pass 3

Stage A first: `Pot J`, `Pot G`, `Pot H`, `Pot D`, `Pot E`, 2 repeats each (`MOR1/2` control + `K3R1/2` ours), then the native-3x `def_3x` Juglet (4 repeats; report every repeat). Gate: Pot J `>= 8/11, >= 16/21` in BOTH repeats; `G 7/7 10/10`; `H 11/11 17/17`; `D >= 23/28 >= 55/69`; `E >= 29/31 >= 57/62`. Stage B (only if A passes): `Pot A, B, C, F, I`, 2 repeats, floors as in Ticket 03. Axes for Pot A..J are extracted from OUR surfaces; the assembler reads our breaklines only; no Authors' breakline enters the K3 arms. Juglet axes in native 3x units (no `/3.0` on written files).

## 5. Harness traps already hit (Tickets 02/05/06/03)

`AX_MO` (`<P>_MOR1/2`) is the Authors' released `Axes/` control, `AX_318` (`<P>_K3R1/2`) is ours. `score58` lacks `--scale`; Piece 7 angles come from its `per_edge` deg column. Export `RUN_DIR` with `sbatch --export=ALL`. Collect `sacct -X` once from the login node into `out/sacct_all.txt`. `corpus_md5` helpers import by name; verify `CORPUS-UNCHANGED` is genuinely computed (a harness import error once printed a false CHANGED). Submit with `--export=ALL`, poll every `sbatch` with `scripts/slurm_poll.sh`, record final `sacct` State/ExitCode. Spartan run dir `runs/<YYYYMMDD-HHMM>_<git7>_t07-potj-own/`; one `runs/index.tsv` row per job with blank `verdict`/`human_note`.

## 6. Deliverables (`C:/PR/artifacts/axis-parity-07/`, fetch, then LOOK at the renders)

`axes07_diag.tsv` (per stem per surface: surface stats, arm angles, M-bucket), `axes07_summary.json` (non-empty `jobs` list from `sacct -X`, cause bucket, per-piece before/after, Part A table, Phase 3 per-repeat table), `gate07.tsv` (header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`), `render07_diag.png`, `PREREG07.md` (when Phase 2 runs), `impl_t07.diff` (when Phase 2 runs), and `render07_e2e.png` + `score/acc_pot*.tsv` + `score/juglet/` when Phase 3 runs.

## 7. Git

Work only in your ticket worktree/branch; write the results into this ticket; commit with `Worker: DeepSeek` and push the branch. Do NOT merge, push `main`, run `ticket_close.sh`, change `**Status:**`, or edit `structure-from-sherds-pp/`, `docs/`, `intent/`, or other tickets. No background watcher left running. Finish with `**End state:** ready` and one bare `Reading:` line.

## Readings (pick one verbatim)

- `pot-j-own-surface-fixed-e2e-passes` — Part A bars pass and Phase 3 clears Pot J in both repeats and every other gated pot.
- `pot-j-own-surface-fixed-offline-misses-e2e` — Part A passes but Phase 3 misses a floor; give exact pot/repeat.
- `pot-j-own-surface-not-fixed-offline` — cause isolated, no fix passes Part A, no E2E.
- `pot-j-cause-not-isolated` — Phase 1 could not name the cause.
- `blocked: missing-or-failed-control` — input, control or `CORPUS-UNCHANGED` failure.

## Out of scope

Editing tracked files; merging Ticket 03; C++ assembler (Ticket 04); `K` capping on base fragments; Juglet repeat spread.

## Acceptance

- [ ] Phase 1 table covers all 11 Pot J stems on both surfaces with a named cause bucket, or `pot-j-cause-not-isolated`.
- [ ] If Phase 2 ran: `PREREG07.md` written before results, `impl_t07.diff` applies cleanly over `325a0a8`, unit tests pass on a Spartan node (record job id).
- [ ] `sacct -X COMPLETED 0:0` for every counted job, `CORPUS-UNCHANGED`, `runs/index.tsv` rows appended.
- [ ] Deliverables fetched, renders inspected, no watcher left, `**End state:** ready` and bare `Reading:`.

## 8. Write-back — Ticket 07 (worker, DeepSeek)

### Phase 1 — the cause is the selector's seed shortlist, not the surfaces

Read-only diagnosis, job **35467409** (`t07-diag`, COMPLETED 0:0), 15 stems x 2 surface sets,
log `CORPUS-UNCHANGED`. 11 Pot J stems plus the three largest non-J own-vs-Authors gaps from
Ticket 03's `axes03_audit.json` (Pot D 27, Pot D 29, Pot E 28, Pot I 26 — the three pots, four
stems). Table: `artifacts/axis-parity-07/axes07_diag.tsv`; render `render07_diag.png`.

**Surfaces (bucket (a) and (b) are ruled out).** Our Pot J surfaces carry 4.0-4.6x the Authors'
points (J01 124 980 vs 27 223; J12 9 121 vs 2 545; J07 43 101 vs 12 509) with bounding boxes
identical to 0.1-1 mm, nearest-neighbour median 0.30-0.38 mm vs the Authors' 0.22-0.39 mm, and
45.8-48.1 % exact-duplicate coordinates (the Authors' clouds have none). Their normals agree
with the Authors' normals at the nearest point: median 1.0-2.5 deg on every row, p90 3.9-8.8 deg,
flip fraction 0 — **except Pot J 01**, whose own cloud has a 20.70 mm p90 neighbour gap (a hole,
`cover_1mm` 0.728) and 10.4 % of normals more than 60 deg from the Authors' (p90 61.7 deg).
So one stem has a genuine normal defect; the other ten do not.

**The pool holds the answer on 11/11 Pot J stems on both surface sets** — a seed within 10 deg of
ground truth exists (`pool_best_deg` 1.85-7.33 own, 2.11-9.88 Authors'), so bucket (c), "pool
seeds miss the true basin", is ruled out too. What fails is everything after the pool:

| stem | surface | pool best | A1 rank-0 | B2 rank-0 | P rank-0 | tri rank-0 | tri best-of-3 |
|---|---|---|---|---|---|---|---|
| J01 | Authors' | 2.74 | 89.14 | 85.18 | 88.92 | 89.14 | 24.30 |
| J01 | ours | 7.33 | 82.81 | 88.01 | 85.34 | 82.81 | 82.81 |
| J12 | Authors' | 2.11 | 28.28 | 72.77 | 69.27 | 28.28 | 28.28 |
| J12 | ours | 3.00 | 81.43 | 72.44 | 67.97 | 81.43 | 68.07 |
| J07 | Authors' | 5.43 | 27.17 | 19.23 | 20.42 | 27.17 | 6.60 |
| J07 | ours | 6.02 | 13.28 | 18.02 | 15.86 | 13.28 | 13.28 |
| J06 | Authors' | 9.88 | 47.92 | 5.31 | 1.72 | 47.92 | 5.31 |
| J06 | ours | 4.47 | 53.42 | 5.69 | 8.24 | 53.42 | 5.69 |
| J05 | Authors' | 6.41 | 20.60 | 26.68 | 2.83 | 20.60 | 2.83 |
| J05 | ours | 4.63 | 21.42 | 3.01 | 24.81 | 21.42 | 3.01 |
| J08 | Authors' | 4.62 | 59.85 | 60.35 | 61.51 | 59.85 | 59.85 |
| J08 | ours | 6.41 | 58.65 | 60.43 | 66.94 | 58.65 | 58.65 |
(The remaining rows are in the TSV; J02/J03/J04/J10/J11 are inside 10 deg best-of-3 on both
sets, and J11 own is the one own stem whose rank-0 already passes, at 2.58 deg.)

**Where the seed is lost — measured over ALL basins, not the shortlist (job 35467588,
`t07-rank2`, COMPLETED 0:0, 16 s).** For each stem and surface the cost rank of the
nearest-to-GT seed among every basin in the cached pool, per arm:

| stem/surface | basins | A1 rank / best of 8 | B2 rank / best of 8 | P rank / best of 8 |
|---|---|---|---|---|
| J01 ours | 131 | 128 / 55.89 | 129 / 29.47 | 129 / 33.19 |
| J01 Authors' | 131 | 120 / 7.98 | 126 / — | 124 / — |
| J05 ours | 130 | 109 / 21.12 | 101 / 28.64 | 99 / 28.64 |
| J06 ours | 127 | 29 / 15.50 | 65 / 28.20 | 68 / — |
| J08 ours | 116 | 97 / 58.36 | 105 / 20.67 | 102 / — |
| J12 ours | 117 | 71 / 22.44 | 75 / 17.86 | 75 / — |
| J12 Authors' | 112 | 110 / 28.11 | 110 / 30.58 | 110 / — |
| J07 ours | 123 | 6 / 8.86 | 8 / 8.86 | 8 / 8.86 |
| D27 ours | 74 | 30 / 19.54 | 34 / — | 34 / — |

**Cause bucket: (d) something else — the selector pipeline discards a true-axis seed that the
pool does contain, in three distinct ways.** (i) The shipped shortlist keeps only the 60
most-drawn basins (`joint._candidates`, `order = np.argsort(-sizes)[:60]`) and refines only the
8 cheapest (`ARM_REFINE_K = 8`), so on J01/J05/J06/J08/J12 own the true seed is never a candidate
at all (cost rank 29-128 of 116-131). (ii) Even when it is inside the cheap eight it can be
thrown away by refinement: on J12 own a 17.86 deg seed is in the post-dedup top-8 of B2 and P,
and both arms return 59-68 deg lines from it. (iii) `merge_lines` offers the secondaries of the
SHIPPED arm only, so J07 own keeps its 0.52 deg thickness line at rank 1 and the merge never sees
it (tri 13.28, above the 10 deg bar). Buckets (a) normals and (b) surface trimming/density are
ruled out for all stems but J01; (c) pool coverage is ruled out for all 11.

Exact-duplicate removal was tested and does NOT change the decision (`in_short8` identical raw vs
deduped on 29 of 30 rows), so the duplicate points are a real data defect but not this cause.

`render07_diag.png` (1113x2703, looked at): 8 panels, J01/J06/J07/J12 x (Authors' | ours) — grey
surface, black dashed GT axis, blue Authors' releases, red our tri lines — plus three normal-angle
histograms. It confirms the table: J12 and J01 own axes sit far off, J06/J07 close.

### Phase 2 — two pre-registered fixes, and what they did

`PREREG07.md` was written locally at **16:43:33** on 2026-11-21, before any Part A pass existed
(the first Part A job was submitted 16:47:56 and its first pass started 17:33:50). It contains no
Part A number. It was copied into `<run>/work/PREREG07.md` only at 18:31 (with its original
mtime), i.e. **during** the Part A job — the honest statement is that the document's content
predates the results, not that it sat in the run directory the whole time.

Both fixes remove a discard rule and add no constant, no per-pot/per-piece/object-size term:

1. **F1 — `joint.merge_lines` → `merge_secondaries_symmetric`.** The shipped merge keeps the three
   rank-0 lines (normal, thickness, shipped) and then offers only the SHIPPED arm's remaining
   lines. F1 offers every arm's remaining lines, rank-major (rank 1 of A1, B2, P, then rank 2 …),
   under the same `JOINT_DEDUP_DEG = 10` test and the same `JOINT_KMAX = 3` cap; the normal
   rank-0 stays first and unconditional, so nothing that already worked can move.
2. **F2 — `joint._select` → `_select_keep_seed`.** Each shortlisted seed is kept as a candidate
   beside its already-computed refinement (same 15 deg dedup, same `keep_lines(1.2x, kmax 3)`,
   same cap, same `orient_base_axis`). Scoped to A1 and B2; the shipped P hypothesis
   (`select_union_lines`) is the frozen Ticket 03 control and is untouched.

Files: `sfs_axes/t07/__init__.py`, `sfs_axes/t07/fixes.py` (`FIXES = ("fix1", "fix2")`,
`apply()` -> `base`/`fix1`/`fix2`/`pair`, `ValueError` otherwise), `tests/test_t07_fixes.py`
(10 tests over synthetic lines: merge order, the 10 deg boundary away from it, the cap, an empty
arm, the seed-beside-refinement cases, and the shipped call signature).
`impl_t07.diff` = 3 files, **+372 lines, 0 deletions**, 387 diff lines;
`git apply --ignore-whitespace --check` against a pristine copy of `325a0a8` prints **APPLY-OK**.

**Unit tests ran on a Spartan compute node**: job **35469798** (`t07-tests`, 1 cpu, partition
sapphire) COMPLETED `0:0`, log `[tests] 10/10 passed`, `tests exit=0`. The tora env has no
pytest, so the tests are plain functions and `work/t07_run_tests.py` calls each one (that is why
the first attempt printed `No module named pytest`).

### Part A — the bars, and the one that fails (job 35469782)

141 GT pieces per surface set, Juglet stems excluded from every 141-denominator bar.

| pass | Authors' K1 | K3 | median | Pot A d med | Pot G K1 | own K1 | K3 | own Pot J K3 | own J12 best-of-3 |
|---|---|---|---|---|---|---|---|---|---|
| base (control) | 110/141 | 128/141 | 2.7054 | 2.4733 | 7/7 | 116/141 | 127/141 | 7/11 | 68.07 |
| fix1 | 110/141 | 128/141 | 2.7054 | 2.4733 | 7/7 | 116/141 | **129/141** | **8/11** | 63.51 |
| fix2 | 110/141 | 128/141 | 2.7054 | 2.4733 | 7/7 | 116/141 | 127/141 | 7/11 | 68.07 |
| pair | 110/141 | 128/141 | 2.7054 | 2.4733 | 7/7 | 116/141 | **129/141** | **8/11** | 63.51 |
| bar | >=110 | >=128 | <=2.7054 | <=2.4733 | 7/7 | >=116 | >=127 | >=8 | <=30 |

Base reproduces Ticket 03 exactly, so the control holds (raw 150-stem counts 117/136 Authors',
123/135 own, the 110/128 being the JUG-excluded subset). **Part A fails on one bar only: own
`Pot_J_Piece_12` best-of-3 is 63.51 deg against the required <= 30 deg.** `[partA] pair
own=False authors=True -> PART-A-FAIL`.

Own Pot J best-of-3, base -> pair (degrees):

| piece | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 82.81 | 7.42 | 1.88 | 3.07 | 3.01 | 5.69 | 13.28 | 58.65 | 7.88 | 2.58 | 68.07 |
| pair | 62.09 | 7.42 | 1.88 | 3.07 | 3.01 | 5.69 | **0.52** | 58.65 | 7.88 | 2.58 | 63.51 |

F1 does exactly what it was pre-registered to do: J07 own now carries its 0.52 deg thickness line
(shift 3.5 % of the piece diagonal, so directionally and positionally sound) and Pot J K3 goes
7/11 -> 8/11, with own K3 127 -> 129/141 and no own K1 loss. It also lifts J01 own 82.81 -> 62.09
(another arm's secondary, still far off). **Honest cost, same mechanism, opposite luck: on the
Authors' surfaces F1 pushes J07's 6.60 deg line out (27.17/19.23 now) so the Authors' Pot J K3 goes
8 -> 7 there; the global Authors' bars are unchanged (110/141, 128/141) because that swap is inside
their 128.** With pair the Authors' J07 lands at 17.03.

**F2 alone changed nothing, and the mechanism is worth recording:** `merge_lines` only reads each
arm's rank-0, and a kept seed never outranks its own refinement inside `keep_lines` (the refinement
has the lower cost), so a seed can only matter if a merge actually reads a rank >= 1 slot. Fix2 is
therefore inert without Fix1 and contributes nothing to pair either.

**Why J12 stays at 63.51, and what that rules out.** The 17.86 deg seed is inside the cheap eight
of B2 and P, but it is a seed: its own cost ranks 71-75 of 117 basins, and the three rank-0 lines
(A1 81.43, B2 72.44, P 67.97) are all >= 10 deg apart, so the three merge slots are full before any
secondary is offered — the 63.51 that does enter is a P secondary. Reaching <= 30 deg on J12 needs
either a cheaper true-axis basin (rank 29-128 on J01/J05/J06/J08/J12 own — i.e. the 60-most-drawn
shortlist and the cost functions themselves) or dropping a rank-0 line. Neither is one of the two
pre-registered fixes, and the pre-registration forbids a third fix, so **none was attempted**.

### Decision

The pre-registered rule: Part A passes only if **pair** meets every own-surface bar and neither
base nor pair drops below the Authors' bars. Pair fails the J12 bar, so **Part A does not pass and
Phase 3 was not run** (no E2E job submitted, no Pot J E2E claim made). Nothing was relaxed after
the fact; fix1's own-surface win (Pot J K3 8/11) is reported as an offline, partial result only.

### Jobs (sacct -X, all recorded in `out/sacct_all.txt` and `runs/index.tsv`)

| job | name | state | exit | elapsed | what |
|---|---|---|---|---|---|
| 35467409 | t07-diag | COMPLETED | 0:0 | 00:02:05 | Phase 1, 15 stems x 2 surfaces |
| 35467565 | t07-rank | COMPLETED | 0:0 | 00:00:47 | shortlist rank probe |
| 35467588 | t07-rank2 | COMPLETED | 0:0 | 00:00:16 | cost rank over ALL basins |
| 35467837 | t07-passa | FAILED | 1:0 | 00:00:02 | first attempt, `T07_RUN: parameter null or not set` |
| 35468255 | t07-passa | COMPLETED | 0:0 | 00:50:01 | base+fix2 ran; fix1/pair died on a TypeError |
| 35469781 | t07-passa | CANCELLED by 18130 | 0:0 | 00:00:00 | cancelled while PENDING, resubmitted |
| 35469782 | t07-passa | COMPLETED | 0:0 | 00:49:57 | the four counted passes + Part A |
| 35469798 | t07-tests | COMPLETED | 0:0 | 00:00:03 | 10/10 unit tests on a compute node |

Both failures are mine and are recorded rather than hidden: (1) `sbatch --export=ALL` does not
create `T07_RUN`, so the script aborted under `set -u`; (2) F1 was written without the
`include_shipped_secondaries` keyword that `joint.select_joint_lines` passes at
`sfs_axes/joint.py:249`, so every fix1/pair piece raised `TypeError`. After the fix, job 35469782
re-ran all four passes — the per-piece resume check keys on `<stem>.json`, which `t07_pass1.py`
never writes, so base and fix2 re-ran too; their numbers came out identical to job 35468255's
(`CORPUS-UNCHANGED`, 907 files, on both md5 checks), which re-confirms determinism.

### Deliverables (`C:/PR/artifacts/axis-parity-07/`)

`axes07_diag.tsv`, `render07_diag.png` (looked at), `PREREG07.md`, `impl_t07.diff`,
`axes07_summary.json` (8-job sacct list, Phase 1 per-stem table, Part A block), `gate07.tsv`
(52 rows: 44 Part A bar rows + 8 job rows), `partA_table.tsv`, `sacct_all.txt`, and the four
`rows_<fix>.json` evidence files under `rows/`, logs under `logs/`.

### Worktree state

Tracked change in this branch: **this ticket file only**. The prototype lives in the worktree as
untracked files — `sfs_axes/t07/__init__.py`, `sfs_axes/t07/fixes.py`, `tests/test_t07_fixes.py` —
deliberately not committed (the ticket's Git rule; `impl_t07.diff` is the deliverable that carries
them). Nothing under `SfSpp_preprocessing/`, `structure-from-sherds-pp/`, `docs/`, `intent/` or any
other ticket was touched.

**End state:** ready

Reading: pot-j-own-surface-not-fixed-offline
