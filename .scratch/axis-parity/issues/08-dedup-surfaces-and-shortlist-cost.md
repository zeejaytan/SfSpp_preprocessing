# 08: Deduplicate our own surfaces, then find why the true axis basin ranks 29-128 and rework the shortlist and cost

**What to build:** A research ticket in three linked parts, all prototyped on Spartan only (ZERO tracked edits in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`; export a clean `-p1` unified `impl_t08.diff` over commit `325a0a8`, the head of branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`; `git apply --ignore-whitespace --check` must pass):

1. **Prove and remove the upstream duplicate-point defect.** Our `MeshPreprocessingHeadless` surfaces carry 45.8-48.1 % exact-duplicate coordinates (Authors' clouds carry none) and 4.0-4.6x their point count; every mean cost therefore double-weights almost half of every wall. Quantify it over the whole corpus, name where the writer emits a point twice, and rerun the Part A benchmark with exact duplicates removed in memory (the corpus itself is never edited).
2. **Check the Authors'-surface losses.** State whether removing duplicates (a) leaves the Authors' surface Part A numbers exactly unchanged, as it must if they carry no exact duplicates, and (b) removes the own-vs-Authors gap on the pieces that lose; and report whether the Ticket 07 F1-induced Authors'-surface Pot J regression (J07's 6.60 deg line pushed out, Authors' Pot J K3 8 -> 7) survives the reworked selector.
3. **Attack the deeper cause: why the true-axis basin costs out at rank 29-128 of 116-131 basins.** Diagnose the rank mechanically (60-most-drawn cut / seed cost / 15 deg dedup shadowing / refinement / `keep_lines`), then pre-register at most two scale-free shortlist-and-cost fixes tied to the measured mechanism. Part A gates them; only a passing fix runs the E2E.

**Answers:** E1
**Blocked by:** None (Ticket 07 resolved at `1a19c9a`, Reading `pot-j-own-surface-not-fixed-offline`; Ticket 03 unmerged at `325a0a8`)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-21) (2026-11-21)
**Branch:** 08-dedup-surfaces-and-shortlist-cost, in /c/PR/worktrees/sfs/08
**Worker:** dsh one-shot subagent w08-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek - hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-08/accept.py` staged before dispatch

---

## 0. What is already established (read Ticket 07's write-back first; do not re-derive)

Sources: `.scratch/axis-parity/issues/07-pot-j-own-surface-axes.md` (on branch `07-pot-j-own-surface-axes` at `1a19c9a`, which is NOT in this worktree's base - read it with `git show 1a19c9a:.scratch/axis-parity/issues/07-pot-j-own-surface-axes.md`), the Ticket 07 run `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1628_46d7e2d_t07-potj-own`, and the artifacts `C:/PR/artifacts/axis-parity-07/` (`axes07_diag.tsv`, `rank2_diag.tsv`, `partA_table.tsv`, `rows/rows_*.json`, `axes07_summary.json`, `render07_diag.png`).

- **Surfaces are not the cause of the Pot J loss, but they are defective.** Our Pot J walls carry 124 980 / 27 223 (J01), 9 121 / 2 545 (J12), 43 101 / 12 509 (J07) points against the Authors', 45.8-48.1 % of them exact duplicates, whilst the bounding boxes agree to 0.1-1 mm and normals agree at median 1.0-2.5 deg (p90 3.9-8.8 deg, flip fraction 0) on every stem except J01 (20.70 mm p90 neighbour gap, 10.4 % of normals > 60 deg off, p90 61.7 deg).
- **The pool is not the cause.** A seed within 10 deg of the reference exists on 11/11 Pot J stems on both surface sets (`pool_best_deg` 1.85-7.33 own, 2.11-9.88 Authors').
- **The selector discards it after the pool.** Ticket 07 measured the cost rank of the nearest-to-GT basin among ALL basins: J01 own 128/129/129 of 131 (A1/B2/P), J05 own 109/101/99 of 130, J06 own 29/65/68 of 127, J08 own 97/105/102 of 116, J12 own 71/75/75 of 117 and 110/110/110 of 112 on the Authors' surfaces. Ticket 07 also named three distinct discard routes: (i) `joint._candidates` keeps only the 60 most-drawn basins and `ARM_REFINE_K = 8` refines only the 8 cheapest, so the true seed is never a candidate; (ii) refinement can throw a good seed away (J12 own: a 17.86 deg seed is in the post-dedup top-8 of B2/P, and both arms return 59-68 deg); (iii) `merge_lines` offered only the shipped arm's secondaries, so J07 own's 0.52 deg thickness line at rank 1 was never merged.
- **Ticket 07's carried fix F1 (symmetric merge, `sfs_axes/t07/fixes.py`) is the only offline win so far:** own K3 127 -> 129/141, own Pot J K3 7 -> 8/11, J07 own 13.28 -> 0.52 deg, J01 own 82.81 -> 62.09 deg. Its honest cost: on the Authors' surfaces F1 pushes J07's 6.60 deg line out (now 27.17/19.23) and Authors' Pot J K3 goes 8 -> 7 (the global Authors' bars do not move). F2 was inert.
- **Ticket 07 failed Part A on exactly one bar: own `Pot_J_Piece_12` best-of-3 = 63.51 deg against <= 30 deg.** The 17.86 deg seed is inside the cheap eight but is itself cost rank 71-75, the three rank-0 lines are all >= 10 deg apart so the three merge slots fill before any secondary is offered, and the 63.51 that enters is a P secondary. Reaching J12 needs the cost/shortlist itself, not another merge rule.
- **The duplicate probe in Ticket 07 was a decision probe, not a benchmark:** `in_short8` was identical raw vs deduped on 29 of 30 rows, and `PREREG07.md` said duplication is "a data defect, not the cause". That probe did not rebuild the pools, did not re-rank after deduplication, and did not rerun the Part A benchmark. This ticket does all three.
- **Staging (do this first, it is how Ticket 07 was run):** copy `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1628_46d7e2d_t07-potj-own/work/impl_t07` to `<run>/work/impl_t08`; that tree is the Ticket 03 code at `2e951d9`/write-back `325a0a8` with `C:/PR/artifacts/axis-parity-07/impl_t07.diff` already applied (it holds `sfs_axes/t07/fixes.py` and `tests/test_t07_fixes.py`), and it is the base every pass below starts from. Re-derive it if you prefer (`work/impl_t03` in `runs/20261121-1319_2e951d9_t03-ship` + `git apply -p1`), and confirm your base reproduces the numbers below before changing anything. Harness template: `<t07 run>/work/t07pkg/t07_parta.py` and `work/t03_lib.py` (points `SFS_IMPL` at `work/impl_t03` by default - point it at `impl_t08`).
- **Base reproduction (must hold):** the Ticket 03 code at `325a0a8` + `impl_t07.diff` reproduces Authors' 110/141 K1, 128/141 K3, median 2.7054 deg, Pot A `d_gt_to_est` 2.4733 mm, Pot G 7/7 K=1; own 116/141 K1, 127/141 K3, own Pot J K3 7/11 (8/11 with F1), J12 68.07 (63.51 with F1).
- **Dead ends already closed:** `.scratch/axis-parity/spec.md` §4 (unnormalised Cao alone, pure normal LM alone, single-sherd slab thickness, 5 deg bounded NM / raw A2, 2-DoF pivot-locked, 4-DoF c_in/c_ref, naive multiplicative reweighting, serial Arm D). Do NOT retest them.

## 1. Phase 0 - the upstream duplicate defect (measure, attribute, do not edit the corpus)

1. **Corpus scan, read-only.** For every own-surface piece available (`Pot A..J` under the ten `own_surfaces` directories recorded in `20261120-1430_9e0fe6a_t02-cost-landscape/work/run.json`; the 9 `def_3x` Juglet pieces under `20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom`; and the 141 Authors' `Surfaces/*.xyz` pieces), per wall, report in `axes08_dedup.tsv`: `stem, surfaces, wall, n_rows, n_unique_xyz, dup_frac_xyz, n_unique_full6, dup_frac_full6, n_xyz_dup_normal_diff, nn_med_mm, nn_p90_mm` with the header exactly as listed.
   - Deduplication rule: exact bitwise equality, no epsilon. Key is the full 6-vector (x, y, z, nx, ny, nz), first occurrence kept, order preserved, deterministic. Also count and report the case "same xyz, different normal" separately: if it exists at all, do NOT silently collapse it - name it as a second defect and report its count per wall.
   - Lead has already measured one file: `Pot_J_Piece_12.S0` 4 279 rows / 2 351 unique (45.06 % duplicate; 1 928 unique rows occur twice, 423 once), `S1` 4 842 / 2 590 (46.51 %), and full-row duplicates equal xyz duplicates in both - i.e. the duplicate rows are identical including the normal. Reproduce that number before trusting the scan.
2. **Attribute the defect to the writer.** Find where `MeshPreprocessingHeadless` writes the surface PLY (the files say `comment PCL generated`, `element vertex N`, 7 float properties including `curvature`). Name the file and line where a point is emitted twice - e.g. once per incident triangle, both sides of a sheet, or two sampling loops - and state whether removing the duplicate changes the surface at all (it cannot: the row is identical). Record this as an **upstream defect** with the exact location; this ticket does not fix the generator (prototype-only, tracked files untouched) but the write-back must name the follow-up code ticket it needs.
3. **Report the residual density.** After dedup our walls are still denser than the Authors' (J12 own ~4 941 against 2 545). Report the post-dedup point-count and nn-spacing ratio per pot; if the cost still double-weights because of residual sampling density rather than exact rows, say so in the mechanism statement - do not silently normalise by point count.

## 2. Phase 1 - dedup + Part A rerun (questions 1 and 2)

Rebuild the own-surface pools from the deduplicated walls (do NOT reuse `out/cache_own`: RANSAC basin draws depend on the point multiset). Run the Part A benchmark (141 GT pieces, both surface sets, same metrics as Ticket 07: K1 = 10 deg, best-of-3, median rank-0 angle, `d_gt_to_est`, `d_est_to_gt`, per-pot table) for these passes:

| pass | selector | surfaces |
|---|---|---|
| `base` | Ticket 03 tri + `impl_t07.diff` (control; must reproduce the Ticket 07 `base` numbers) | both |
| `dedup` | same, duplicates removed in memory | both (Authors' is a null control) |
| `fix1+dedup` | carried F1 (symmetric merge) + dedup | both |
| `candidate(s)+dedup` | Phase 3 fix(es) + dedup | both |

- **Null control (hard stop):** the Authors' walls carry no exact duplicates, so `dedup` must return byte-identical walls for them and the Authors' Part A numbers must equal `base` exactly, piece by piece. If they do not, stop with `Reading: blocked: missing-or-failed-control` and report the first differing piece. Do not "explain" a differing Authors' number as noise.
- **Question 2 - Authors'-surface losses.** In the write-back give the Authors'-surface failure list before and after (every piece outside 10 deg at rank 0 / best-of-3, with its angle), and answer: (a) did dedup leave the Authors' surface results exactly unchanged (the null control)? (b) did the own-vs-Authors per-piece gap close on the five failing own Pot J stems (J01, J05, J06, J08, J12) and on the three largest non-Pot-J gaps (D27, D29, E28, I26)? (c) is the F1-induced Authors' Pot J regression (J07 6.60 deg lost, Authors' Pot J K3 8 -> 7) still there with `fix1+dedup`, and is it gone with the reworked selector? State plainly which of these is true; do not answer "the losses are unchanged" without the per-piece list.
- Report which own pieces move, with their before/after angles, not just the totals. A total that stays at 116/141 can hide a swap in both directions.

## 3. Phase 2 - why the true basin ranks 29-128 (the deeper diagnosis)

Use the cached raw pools from `base` and `dedup` (rebuild if only the deduped pool exists) and the same GT metric. For every failing stem - own J01, J05, J06, J08, J12; Authors' J01, J08, J12; D27, D29, E28, I26 on each surface that fails - write one row per stem x surface x arm (A1, B2, P) into `axes08_rank.tsv` with header exactly:

`stem, surfaces, arm, n_basins, true_draw_rank, true_in_top60, true_cost_rank_all, true_cost_rank_top60, true_in_short8_after15deg, shadow_ddeg, shadow_cost_ratio, cost_true, cost_min, cost_ratio, refined_true_deg, refined_true_cost, refined_true_cost_rank, top1_deg`

Definitions that must be used:
- `true_*` always refers to the pool basin whose direction is nearest to GT (`pool_best_deg`), not to a refined line.
- `true_draw_rank`: 1-based rank of that basin under `np.argsort(-sizes)` (the `joint._candidates` cut).
- `true_in_top60`: whether it survives `_candidates`.
- `true_cost_rank_all` / `true_cost_rank_top60`: its cost rank among all basins / among the 60, per arm, BEFORE the 15 deg dedup.
- `true_in_short8_after15deg`: whether it is one of the eight seeds `_select` actually refines (this applies `_dedup` at `ARM_DEDUP_DEG = 15 deg` first).
- `shadow_ddeg`, `shadow_cost_ratio`: the nearest cheaper basin within 15 deg and its cost / true cost. A non-empty `shadow_ddeg < 15` means the 15 deg dedup discards the true seed in favour of a cheaper decoy - a different mechanism from a high cost rank.
- `refined_true_deg`, `refined_true_cost`, `refined_true_cost_rank`: refine the TRUE seed with that arm's refiner (`_bounded` + `refine_fn`), score it, and rank its refined cost against the arm's refined top-8. This separates "the cost is wrong" from "the seed's cost is not predictive of its refinement".
- `top1_deg`: angle of the arm's rank-0 answer to GT.

Then **look at the cost landscape**, not just the ranks: for at least four failing stems (`Pot_J_Piece_12` own, `Pot_J_Piece_01` own, `Pot_J_Piece_08` own, `Pot_J_Piece_12` Authors') render `render08_cost.png` with two panels per stem: (a) the arm cost along a 1-D angular sweep from the true direction to the top-1 direction (0-30 deg, fixed foot from the true line), and (b) the same sweep evaluated after a bounded refinement from each sweep angle. Mark the true angle, the top-1 angle and the shortlist cut. If the true basin is not a local minimum of the cost, that is the primary finding - say it in one sentence and cite the panel. Also render `render08_diag.png` (points, GT axis, top-1 seed and its refinement, true seed and its refinement) for the same four stems and inspect both before writing the mechanism.

**Mechanism statement (choose one, with the per-stem numbers):**
- **(C1) Cost objective wrong** - the true direction is not a local minimum of the arm cost (or its refined cost stays above the false lines' refined cost); ranking better cannot fix it.
- **(C2) Seed cost not predictive** - the true seed is expensive but its refinement is cheap and would win if refined; the shortlist's rank-on-seed rule is the defect.
- **(C3) 15 deg dedup shadowing** - the true seed is dropped in favour of a cheaper basin within 15 deg, so it never reaches refinement.
- **(C4) 60-most-drawn cut** - the true basin is outside the 60 most-drawn basins.
- **(C5) Something else** - say exactly what (e.g. the basin representative is a poor line for a wide basin; the foot point is wrong; one wall dominates).

**Phase 2 stop rule:** if the mechanism cannot be put in one of C1-C5 with per-stem evidence on both surface sets, finish with `Reading: rank-cause-not-isolated`, run NO fix and NO E2E.

## 4. Phase 3 - at most two pre-registered shortlist/cost fixes

Write `<run>/work/PREREG08.md` BEFORE submitting any Part A pass that contains a fix. It must contain: the mechanism, each fix's exact rule, why it follows from that mechanism, the expected effect, the falsification condition, and the untouched constants. Copy it to the run directory at creation (the Ticket 07 lesson: do not "pre-date" a document that was only copied later).

Rules for every fix:
- Scale-free: no per-pot, per-piece or object-size constant, and no GT or reference axis inside the selector. Fixed algorithm counts (basins, seeds, lines) are allowed if stated in PREREG; do not tune them per pot or after seeing a piece's result.
- Prototype namespace only: `sfs_axes/t08/__init__.py`, `sfs_axes/t08/<name>.py`, `tests/test_t08_*.py`; installed over the base tree, never editing a shipped module. `impl_t08.diff` over `325a0a8` must be additive.
- At most two fixes, picked from the C-bucket the evidence supports. Candidates (not endorsements; pick only what the evidence points to):
  - **S1 (C2): refine-then-rank.** Refine every seed that survives the 60-most-drawn cut (or a fixed, stated subset larger than 8), score the refinements, and let the existing 15 deg dedup / `keep_lines` decide. Tests whether the seed's cost is simply not predictive.
  - **S2 (C3): shadow-aware dedup.** When two seeds are within `ARM_DEDUP_DEG`, keep the cheaper AND the seed whose bounded refinement is cheaper (or keep the pair through to refinement) instead of discarding the shadowed one outright.
  - **S3 (C4): coverage shortlist.** Replace the "60 most-drawn, then 8 cheapest" rule with a stated coverage rule over the same pool (e.g. farthest-point in direction from the cheapest seed), fixed before running.
  - **S4 (C1): cost rework.** Only if the sweeps show the objective itself is wrong: a principled reweighting (e.g. per-unique-point weighting after dedup, an explicit truncation/inlier fraction, or evaluating the cost on both walls with a stated combination) - not a board of tuned weights. State the physical meaning of every term.
- A fix that only moves J12 while breaking another pot is not a pass; report the full per-pot table.

## 5. Phase 4 - Part A gate, then E2E (same own-code chain as Ticket 03 Pass 3 / Ticket 07 Phase 3)

**Part A gate (offline, 141 GT pieces, both surface sets).** Only a configuration that passes ALL of these may run E2E:
- Authors': K1 `>= 110/141`, K3 `>= 128/141`, median rank-0 `<= 2.7054 deg`, Pot A `d_gt_to_est <= 2.4733 mm`, Pot G `7/7` at `K = 1`, `SignAxisGuard 0/18` rank-0 and `0` worst-case.
- Own: K1 `>= 116/141`, K3 `>= 127/141`, **own Pot J K3 `>= 8/11`** (up from 7/11 base; F1 already reaches 8), **own `Pot_J_Piece_12` best-of-3 `<= 30 deg`** (the bar that failed at 63.51).
- No pot below its Ticket 07 `base` K1/K3 on the same surface set. Report every pot, both surfaces, every pass.
- If dedup alone changes own numbers, say so before any fix: dedup is a variable, not a fix.

**E2E (only if Part A passes).** Stage A first: `Pot J`, `Pot G`, `Pot H`, `Pot D`, `Pot E`, 2 repeats each (`MOR1/2` Authors'-axes control + `K3R1/2` ours), then the native-3x `def_3x` Juglet (4 repeats; report every repeat). Gate: **Pot J `>= 8/11, >= 16/21` in BOTH repeats**; `G 7/7 10/10`; `H 11/11 17/17`; `D >= 23/28 >= 55/69`; `E >= 29/31 >= 57/62`. Stage B (only if A passes): `Pot A, B, C, F, I`, 2 repeats, floors as in Ticket 03. Axes for `Pot A..J` are extracted from OUR deduplicated surfaces; the assembler reads our breaklines only; no Authors' breakline enters the K3 arms. Juglet axes in native 3x units (no `/3.0` on written files).
- **Best-of-N rule:** report the best attempt with how many attempts reached it; never present the median of repeats as the result.
- If Stage A passes but Stage B misses a floor, report the exact pot/repeat and do not call it a pass.

## 6. Harness traps already hit (Tickets 02/05/06/03/07)

`AX_MO` (`<P>_MOR1/2`) is the Authors' released `Axes/` control, `AX_318` (`<P>_K3R1/2`) is ours. `score58` lacks `--scale`; Piece 7 angles come from its `per_edge` deg column. Export `RUN_DIR` with `sbatch --export=ALL`. Collect `sacct -X` once from the login node into `out/sacct_all.txt`. `corpus_md5` helpers import by name; verify `CORPUS-UNCHANGED` is genuinely computed (a harness import error once printed a false CHANGED). `joint.select_joint_lines` calls `merge_lines(..., include_shipped_secondaries=True)` (`sfs_axes/joint.py:249`), so any replacement must accept that keyword. The tora env has no pytest: call the t08 test functions from a small runner on a compute node, as `t07_run_tests.py` did. The own-surface PLY loader is `load_wall` in `scripts/run_benchmark_172.py` (PCLPLY, reads the first 6 floats of each vertex row). Spartan run dir `runs/<YYYYMMDD-HHMM>_<git7>_t08-dedup-shortlist/`; one `runs/index.tsv` row per job with blank `verdict`/`human_note`.

## 7. Deliverables (`C:/PR/artifacts/axis-parity-08/`, fetch, then LOOK at the renders)

`axes08_dedup.tsv` (per piece x wall; 163 own pieces x 2 walls + 141 Authors' x 2 + 9 Juglet x 2), `axes08_rank.tsv` (per stem x surface x arm, header above), `axes08_summary.json` (non-empty `jobs` from `sacct -X`, `phase0`, `phase1`, `phase2` mechanism, `partA` table, `e2e` table when run), `gate08.tsv` (header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`), `render08_cost.png`, `render08_diag.png`, `PREREG08.md` (when Phase 3 runs), `impl_t08.diff` (when Phase 3 runs), `sacct_all.txt`, and `render08_e2e.png` + `score/acc_pot*.tsv` + `score/juglet/` when Phase 4 runs.

The write-back must carry the three answers explicitly: (1) the dedup delta with the per-pot table; (2) the Authors'-surface answer with the per-piece failure list; (3) the mechanism bucket with the rank table, plus what the fix did and whether it passed Part A. Numbers quoted bare, no rounding that hides a moved piece.

## 8. Git

Work only in your ticket worktree/branch; write the results into this ticket; commit with `Worker: DeepSeek` and push the branch. Do NOT merge, push `main`, run `ticket_close.sh`, change `**Status:**`, or edit `structure-from-sherds-pp/`, `docs/`, `intent/`, or other tickets. No background watcher left running. Finish with `**End state:** ready` and one bare `Reading:` line.

## Readings (pick one verbatim)

- `dedup-suffices-e2e-passes` - dedup (+carried F1) alone passes Part A and Stage A/B, Pot J >= 8/11, >= 16/21 in both repeats.
- `dedup-and-shortlist-e2e-passes` - the reworked shortlist/cost passes Part A and Stage A/B, Pot J >= 8/11, >= 16/21 in both repeats.
- `dedup-and-shortlist-offline-misses-e2e` - Part A passes but Phase 4 misses a floor; give the exact pot/repeat.
- `shortlist-mechanism-not-fixed` - mechanism named, no fix passes Part A, no E2E.
- `rank-cause-not-isolated` - Phase 2 could not name the mechanism, no fix, no E2E.
- `blocked: missing-or-failed-control` - input, null control or `CORPUS-UNCHANGED` failure.

## Out of scope

Editing tracked files (the upstream generator fix is a follow-up code ticket, not this one); merging Tickets 03/07; C++ assembler (Ticket 04); `K` capping on base fragments; Juglet repeat spread; any per-pot/per-piece tuning; changing the corpus.

## Acceptance

- [ ] `axes08_dedup.tsv` covers every own-surface piece x 2 walls + the Authors' 141 x 2 + 9 Juglet, with the exact duplicate and "same xyz, different normal" counts, and the writer's file:line is named.
- [ ] The Authors' dedup is a byte-identical no-op and the Authors' Part A numbers equal `base` piece by piece; otherwise `blocked: missing-or-failed-control`.
- [ ] `axes08_rank.tsv` covers every failing stem x surface x arm with the header above and separating rank-all / rank-top60 / shadow / refined-true; the mechanism is one of C1-C5 supported by both renders.
- [ ] If Phase 3 ran: `PREREG08.md` written before the first fixed pass, `impl_t08.diff` applies cleanly over `325a0a8`, t08 unit tests pass on a Spartan compute node (record job id).
- [ ] `sacct -X COMPLETED 0:0` for every counted job, `CORPUS-UNCHANGED`, `runs/index.tsv` rows appended.
- [ ] Deliverables fetched, both renders inspected, no watcher left, `**End state:** ready` and one bare `Reading:`.

---

## Results (worker w08-axis-parity / DeepSeek, 2026-11-21)

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-2002_9884175_t08-dedup-shortlist`
(worktree HEAD `9884175`, base `325a0a8` + `impl_t07.diff` as `work/impl_t08`; corpus never edited).
Artifacts: `C:/PR/artifacts/axis-parity-08/`.

| job | id | state | elapsed | what |
|---|---|---|---|---|
| t08-scan | 35471270 | COMPLETED 0:0 | 00:00:46 | phase 0 corpus scan, writer attribution, density |
| t08-partsA | 35471377 | COMPLETED 0:0 | 00:37:47 | 600 pools + Part A passes base / dedup / fix1dedup + gate table |
| t08-ctl | 35471521 | COMPLETED 0:0 | 00:00:07 | Authors' null control, scored on the 141 pot pieces |
| t08-rank | 35471647 | COMPLETED 0:0 | 00:18:59 | phase 2 rank tables (raw + dedup) and renders |
| t08-refcost | 35472535 | COMPLETED 0:0 | 00:14:10 | refined true seed vs refined rank-0 |
| t08-gates2 | 35472793 | COMPLETED 0:0 | 00:09:29 | shortlist gate ablation + (r,z) collapse |
| t08-render2 | 35472813 | COMPLETED 0:0 | 00:14:55 | re-render with the unsigned-angle x axis |
| t08-screen | 35472977 | COMPLETED 0:0 | 00:24:20 | per-wall cost-combination screen |

Four attempts failed and are kept in the ledger: 35472454 (sbatch options after the script path, so
`/work/t08_render.py` not found), 35472490 (render, TIMEOUT at 10 min with a 1-cpu request),
35472491 (6-vector into `direction_angle_deg`), 35472826 (`KeyError` in my screening print). None of
them produced a number used below. `CORPUS-UNCHANGED` was re-proved on 907 files before/after every
counted job; `sacct_all.txt` holds the twelve rows.

### Answer 1 - the duplicate defect, where it is written, and the dedup delta

Coverage: 596 walls = 296 own (148 pieces x 2) + 282 Authors' (141 x 2) + 18 Juglet (9 x 2).
The ticket's "163" is the Authors' corpus tree (326 files = 163 pieces); our own `geom` directories
hold 148 pieces, so the own scan is 148 x 2, and 141 of them carry GT axes.

Reproduction first: **Pot_J_Piece_12 own S0 4279 rows / 2351 unique (45.06 %), S1 4842 / 2590
(46.51 %)**, full-row duplicates equal xyz duplicates - exactly the lead's number.

| set | walls | rows | unique 6-vectors | dup frac | same xyz, diff normal |
|---|---|---|---|---|---|
| own | 296 | 8 711 828 | 4 503 780 | 0.4830 | 0 |
| Authors' | 282 | 2 511 886 | 2 511 886 | 0.0000 | 0 |
| Juglet | 18 | 591 299 | 334 371 | 0.4345 | 0 |

**Structure:** on 144 of the 148 own pieces (both surfaces) the duplicate block is one contiguous
**suffix**: the file is a fully unique prefix followed by a second copy of rows already in it
(`tail_start == n_unique_full6`, `tail_rows_not_in_head == 0`; e.g. Pot_A_Piece_01 own S0 66 763 rows,
33 988 unique, 32 775 trailing rows all already present). Eight own walls deviate (8 of 296): 1-7 stray boundary
rows on Pot_C_Piece_01.S1 (5), Pot_C_Piece_02.S0 (7), Pot_D_Piece_04.S0 (1), Pot_D_Piece_08.S1 (4),
Pot_E_Piece_18.S0 (1), Pot_H_Piece_01.S1 (1), and two real exceptions where the second copy is not a
pure suffix - Pot_D_Piece_03.S0 (103 177 rows / 53 134 unique, `tail_start` 51 434, 1 700 trailing
rows not in the head) and Pot_J_Piece_01.S1 (79 624 / 42 128, `tail_start` 39 760, 2 368 not in the
head). The Juglet geometry shows the same defect on 18 of 18 walls, with both Juglet_Piece_1 walls
deviating the same way (S0 80 440 / 53 933, `tail_start` 30 483, 23 450 not in the head; S1 113 199 /
72 648, 29 779 not in the head).

**Writer:** the suffix second copy is `finishImprovedSurface`'s unconditional re-append of the whole
`segmentedSurfacePointCloud` - `mesh_processing_headless.cpp:1568-1578`, the `push_back` at
**`mesh_processing_headless.cpp:1577`** - fed by the per-mesh-point admission loop at
`mesh_processing_headless.cpp:3237-3257` (`push_back` at :3245 for `angleDiff > 140`, at :3257 for
`angleDiff < 40`). A point admitted at :3245 whose xyz equals its row in
`segmentedSurfacePointCloud` is therefore written twice with the identical 6-vector. The existing
TICKET 27 dedup block (`mesh_processing_headless.cpp:1584-1621`, logs `[DEDUPE-27]`) assigns its
result only when `g_dedupeOn27` is set and **is off by default**, and it compares xyz only. Export
path: `savePLYFile` at :6014-6015, copied to `<stem>_Surface_0/1.ply` and converted at :6788-6802.
Removing the duplicate cannot change the surface - the row is bitwise identical. **Follow-up code
ticket needed:** delete the re-append at :1577 (or make the admission loop skip points already in
`segmentedSurfacePointCloud`) and turn the DEDUPE-27 comparison into the full 6-vector.

**Residual density** (after dedup, `axes08_density.tsv`): own walls are still 1.23-1.83x the Authors'
count (median count ratio A 1.79 B 1.79 C 1.75 D 1.57 E 1.79 F 1.23 G 1.83 H 1.81 I 1.68 J 1.52) with
nn ratio 0.73-0.78 (own median nn 0.2626-0.3132 mm, Authors' 0.3524-0.4258). The mean cost still
weights own walls ~1.5x per unit area after dedup - the mean is point-weighted - but this is residual
sampling density, not the exact-row defect, and it was not normalised away (report, not silence).

**Part A delta (dedup is a variable, not a fix).** Passes: base (raw walls/pools), dedup (dedup walls
and rebuilt pools), fix1+dedup (Ticket 07 F1). Authors' is the null control.

| pass | surface | K1 | K3 | median rank-0 | Pot A d med/max | Pot G K=1 | Pot J K1/K3 |
|---|---|---|---|---|---|---|---|
| base | Authors' | 110 | 128 | 2.7054 | 2.4733 / 14.8373 | 7/7 | 4/8 |
| dedup | Authors' | 110 | 128 | 2.7054 | 2.4733 / 14.8373 | 7/7 | 4/8 |
| fix1+dedup | Authors' | 110 | 128 | 2.7054 | 2.4733 / 14.8373 | 7/7 | 4/7 |
| base | own | 116 | 127 | 2.5631 | - | - | 5/7 |
| dedup | own | 111 | 123 | 2.7400 | - | - | 5/6 |
| fix1+dedup | own | 111 | 123 | 2.7400 | - | - | 5/7 |

Per pot (K1/K3 of n):

| pot | A 8 | B 9 | C 4 | D 28 | E 31 | F 5 | G 7 | H 11 | I 27 | J 11 |
|---|---|---|---|---|---|---|---|---|---|---|
| Authors' base | 8/8 | 9/9 | 4/4 | 20/22 | 21/29 | 5/5 | 7/7 | 9/10 | 23/26 | 4/8 |
| Authors' dedup | 8/8 | 9/9 | 4/4 | 20/22 | 21/29 | 5/5 | 7/7 | 9/10 | 23/26 | 4/8 |
| Authors' fix1+dedup | 8/8 | 9/9 | 4/4 | 20/23 | 21/29 | 5/5 | 7/7 | 9/10 | 23/26 | 4/7 |
| own base | 8/8 | 8/9 | 4/4 | 22/23 | 23/27 | 4/4 | 7/7 | 10/11 | 25/27 | 5/7 |
| own dedup | 8/8 | 8/9 | 4/4 | 19/21 | 22/28 | 4/4 | 7/7 | 11/11 | 23/25 | 5/6 |
| own fix1+dedup | 8/8 | 8/8 | 4/4 | 19/20 | 22/29 | 4/4 | 7/7 | 11/11 | 23/25 | 5/7 |

Own pieces the dedup moved (rank-0 / best-of-3, before -> after):
**newly failing rank-0 (6):** Pot_D_Piece_18 15.8/15.8, Pot_D_Piece_23 87.2/5.6,
Pot_D_Piece_24 87.5/14.7, Pot_E_Piece_24 27.7/19.7, Pot_I_Piece_22 10.7/10.7,
Pot_I_Piece_26 88.7/1.8; **recovered rank-0 (1):** Pot_H_Piece_04 15.0/1.6 -> pass.
Newly failing best-of-3 (7): the same six plus Pot_D_Piece_25 60.5/11.1 and Pot_J_Piece_05
23.5/23.5; recovered at best-of-3: Pot_D_Piece_21 38.7/15.0, Pot_E_Piece_26 82.3/12.5,
Pot_E_Piece_28 11.3/11.3. So dedup is not neutral on our surfaces either: it costs 5 K1 / 4 K3.

### Answer 2 - the Authors'-surface losses

**(a) Yes, dedup left the Authors' surfaces exactly unchanged.** In memory the rule is exact bitwise
equality on the full 6-vector: every one of the 141 Authors' walls is returned byte-identical
(`pools08_control.json`), 141/141 draw pools are bitwise identical to the raw ones (15473 -> 15954
basins on our own surfaces, +3.1 %, but 0 changed on theirs), and Part A equals base **piece by piece
on every bar** - 110/141 K1, 128/141 K3, median 2.7054, Pot A 2.4733/14.8373, Pot G 7/7, per-pot
table above, the 31 rank-0 and 13 best-of-3 failures identical file by file. (The first pools log line
reads `NULL-CONTROL-FAILED` only because that script counted the 9 Juglet stems - whose walls come from
our own `def_3x` geometry and do carry duplicates - into the Authors' numerator; `t08_control.py`
scores the control on the 141 pot pieces only and logs `NULL-CONTROL-OK 141/141 walls byte-identical,
141/141 pools bitwise identical`.)

**(b) The own-vs-Authors' gap closed on none of the diagnosed pieces.** rank-0 / best-of-3, own vs
Authors' on the same stem, base -> dedup -> fix1+dedup:

| stem | own base | own dedup | own fix1+dedup | Authors' (all passes) |
|---|---|---|---|---|
| J01 | 82.81/82.81 | 89.02/41.33 | 89.02/84.45 | 89.14/24.30 |
| J05 | 21.42/3.01 | 23.45/23.45 | 23.45/23.45 | 20.60/2.83 |
| J06 | 53.42/5.69 | 51.58/5.89 | 51.58/5.89 | 47.92/5.31 |
| J08 | 58.65/58.65 | 59.95/59.95 | 59.95/59.95 | 59.85/59.85 |
| J12 | 81.43/68.07 | 81.59/66.60 | 81.59/68.63 | 28.28/28.28 |
| D27 | 68.20/47.95 | 69.50/57.89 | 69.50/20.90 | 28.10/11.08 |
| D29 | 78.01/78.01 | 77.84/62.73 | 77.84/68.75 | 76.73/42.60 |
| E28 | 11.28/11.28 | 18.62/4.03 | 18.62/4.03 | 10.93/3.60 |
| I26 | 9.03/9.03 | 88.75/1.76 | 88.75/1.76 | 87.55/4.03 |

J12 is the clearest: 81.59 deg against the Authors' 28.28 on the same piece, so the defect is not the
surface. On J01 and D29 the best-of-3 gap **widened** (24.30 -> 41.33, 42.60 -> 62.73) and it never
narrowed to within 10 deg on any of the nine.

**(c) The F1-induced Authors' Pot J regression is still there and is not removed by anything in this
ticket.** With fix1+dedup the Authors' Pot J K3 goes 8 -> 7: Pot_J_Piece_07 authors 27.17/6.60 becomes
a failure (6.60 deg pushed out) while Pot_D_Piece_21 authors 60.93/14.44 -> 60.93/8.41 recovers, so the
global Authors' bars do not move (110/128/2.7054). No reworked selector was adopted (answer 3), so
there is nothing that removes it; the mechanism below explains why a shortlist change could not.

Authors' failure list before and after (identical in base and dedup, rank-0 / best-of-3):
Pot_D_Piece_17 17.92/1.20, D20 11.50/11.50, D21 60.93/14.44, D24 53.03/8.41, D25 70.81/12.89,
D26 89.50/70.44, D27 28.10/11.08, D29 76.73/42.60, E03 10.44/2.90, E09 21.94/3.68, E14 20.51/9.82,
E23 14.30/3.24, E25 15.03/12.68, E26 36.00/9.18, E27 66.38/2.87, E28 10.93/3.60, E30 13.23/13.23,
E31 62.40/5.35, H04 10.03/10.03, H11 28.67/2.04, I22 15.18/6.56, I25 80.17/22.08, I26 87.55/4.03,
I27 63.46/3.42, J01 89.14/24.30, J05 20.60/2.83, J06 47.92/5.31, J07 27.17/6.60, J08 59.85/59.85,
J11 10.96/3.40, J12 28.28/28.28 (with fix1+dedup J07 leaves this list at 27.17/19.23 and D21 joins it).

### Answer 3 - the mechanism: C1, the cost objective, not the shortlist

Rank table `axes08_rank.tsv` = 54 rows (9 stems x 2 surfaces x A1/B2/P), dedup pools, 18-column header
as specified. Summary on the P arm (18 stem-surfaces):

- the pool basin nearest GT is a genuine **2.22-9.88 deg** seed everywhere (J01 authors 2.74);
- its **seed** cost ratio is 1.00-9.18 (16 of 18 at or below 5.62);
- it is **outside the 60-most-drawn cut on 4 of 18**: J01 own 96th of 125 basins, J01 authors 85th of
  131, J12 own 85th of 116, J12 authors 106th of 112;
- a cheaper basin within 15 deg shadows it on **17 of 18** (shadow_ddeg 10.2-19.0, shadow_cost_ratio
  0.23-0.997; D29 authors' nearest cheaper basin is 61.8 deg away);
- it survives the 15 deg dedup into the refine-8 on only **3 of 18** (D27 own, D29 authors, I26 own)
  and on those three its **refined cost ranks 3, 5, 3** - it still loses.

**Refinement does not rescue it**: refining the nearest-GT seed is cheaper than refining the sold
rank-0 line on 7 of 18 stem-surfaces but *more expensive* on 11 of 18 (ratio 0.44-2.83, median 1.09);
where it wins it wins by less than the shortlist's own spread, and on I26 authors (12.0 deg @ 0.0412 vs
sold 87.8 deg @ 0.0907) the selector does not even pick the cheaper refined line. Refinement walks
away from truth on the hard pieces: J08 own 8.71 -> 65.66 deg @ 0.1421, J08 authors 4.62 -> 63.21
@ 0.1173, J12 authors 2.11 -> 72.68, J06 own 7.33 -> 30.58, J01 own 8.64 -> 21.51.

**Renders (both inspected).** `render08_cost.png`, two panels per stem: the true direction is a
shallow *local* minimum of the profile cost (J12 own 0.075 mm near 4 deg; J01 own 0.33 mm near 6 deg;
J12 authors 0.74 mm near 2 deg) but the shortlisted false lines are 2-7x cheaper (J12 own 0.057-0.10 mm
at 42-85 deg; J01 own 0.24-0.34 mm at 20-90 deg; J12 authors 0.07-0.12 mm at 32-90 deg; J08 own
0.13-0.19 mm at 28-90 deg against 0.62-0.66 mm at its own 8.7 deg seed); the refined panel shows the
true seed's refinement sliding into the cheap false basin rather than descending to it.
`render08_diag.png`: the GT axis lies on the piece while the sold rank-0 refinement is 60-90 deg away.

**Gate ablation** (`gates08_dedup.tsv`; variant `full` reproduces the shipped P-arm top1 to worst
|ddeg| 0.000048 over 18 rows, so the ablation is the shipped pipeline with one knob moved):

| variant | rank-0 <= 30 deg | truth shortlisted | truth refined |
|---|---|---|---|
| full (60 basins, 15 deg, refine 8) | 9/18 | 14/18 | 4/18 |
| allcand (C4 relaxed, all basins) | 8/18 | **18/18** | 2/18 |
| nodedup (C3 relaxed, 0 deg) | 9/18 | 14/18 | 1/18 |
| k30 (refine 30 distinct) | 8/18 | 14/18 | **8/18** |
| both | 9/18 | **18/18** | 1/18 |

The 60-cut is real (C4 excludes the truth on J01/J12) and the 15 deg shadow is real (C3 drops it on
15 of 18), yet admitting the truth to the shortlist and even refining it never makes it rank first.

**Cost-rework screen** (`screen08_dedup.json`, per-wall combination instead of the mean over walls):
max(wall0, wall1) 9/18 - it fixes D27 authors 23.17 -> 5.58 deg but breaks J05 authors 2.83 -> 26.33
and J06 authors 1.72 -> 5.14; mean + |wall0 - wall1| 7/18. No rule recovers J01, J08 or J12 at all.

**Shape of the false solution** (`collapse08_dedup.tsv`): at the sold rank-0 line the walls' radii have
std_r 4.37-11.91 mm about a mean_r 10.58-44.67 mm - a wide, nearly featureless band that a short
meridian fits at 0.06-0.24 mm - while the GT direction itself costs 0.427-1.167 mm. The objective does
what it says: it finds a surface of revolution, and a sherd patch admits many of them.

**Bucket: C1.** The true direction is a local minimum, but its *refined* cost stays above the false
lines' refined cost on 11 of 18 stem-surfaces on both surface sets, and the ablation shows that
ranking better cannot fix it (18/18 admitted, no extra recovery).

**What I did about it: no fix was pre-registered and no fixed pass was run.** Every Phase 3 candidate
was screened before Part A and each failed on its own evidence: S1 (refine-then-rank) is already the
shipped rule (the P arm refines the 8 cheapest and re-ranks on the refined cost; `k30` refines 8/18
of the truths and still ranks a false line first); S2 (shadow-aware dedup) - removing the shadow
altogether (`nodedup`) drops truth refinement to 1/18; S3 (coverage shortlist) - full coverage
(`allcand`) admits 18/18 and recovers nothing; S4 (cost rework) - the per-wall combination screen
moves recoveries around without adding any, and hitting the real cause needs a pottery-form prior or
per-object curvature normalisation, both outside this ticket's "scale-free, no per-pot or object-size
constant" rule. With the fix space empty, `PREREG08.md` was deliberately not written and
`impl_t08.diff` does not exist: writing a pre-registration for a fix the evidence had already
falsified would have been the Ticket 07 mistake in reverse.

**Part A could not have passed anyway** (dedup + any fix must beat these): own K1 111/141 against
>=116, own K3 123/141 against >=127, own Pot J K3 6/11 (fix1+dedup 7/11) against >=8/11, own
Pot_J_Piece_12 best-of-3 66.60 deg (fix1+dedup 68.63) against <=30. Authors' has zero slack and dedup
leaves it exactly at base. So Phase 4 E2E was not run - no stage A, no stage B, no assembler job, no
`score/` directory, no `render08_e2e.png`.

### Deliverables (fetched to `C:/PR/artifacts/axis-parity-08/`)

`axes08_dedup.tsv` (596 walls, exact 11-column header), `axes08_rank.tsv` (54 rows, exact 18-column
header), `axes08_summary.json` (12 sacct rows, phase0/phase1/phase2/partA, e2e null),
`axes08_attr.tsv`, `axes08_density.tsv`, `axes08_scan.json`, `gate08.tsv` (270 rows, exact
7-column tab header), `partA08.json`, `render08_cost.png`, `render08_diag.png`, `mechanism08.txt`,
`sacct_all.txt`, `gates08_dedup.tsv`, `collapse08_dedup.tsv`, `screen08_dedup.json`,
`refcost08_dedup.json`, `rows/rows_{base,dedup,fix1dedup}.json`, and `work/` (all scripts).
No `PREREG08.md`, no `impl_t08.diff`, no `score/`: Phase 3 and Phase 4 did not run.

No tracked file was edited anywhere: `git status` in the worktree shows this ticket only, and both
render files and every artifact come from the run directory. `CORPUS-UNCHANGED` on 907 files for every
counted job, `runs/index.tsv` has one row per job with blank `verdict`/`human_note`, no watcher or
background process is left running.

**End state:** ready
Reading: shortlist-mechanism-not-fixed