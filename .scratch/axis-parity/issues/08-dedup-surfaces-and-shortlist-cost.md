# 08: Deduplicate our own surfaces, then find why the true axis basin ranks 29-128 and rework the shortlist and cost

**What to build:** A research ticket in three linked parts, all prototyped on Spartan only (ZERO tracked edits in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`; export a clean `-p1` unified `impl_t08.diff` over commit `325a0a8`, the head of branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`; `git apply --ignore-whitespace --check` must pass):

1. **Prove and remove the upstream duplicate-point defect.** Our `MeshPreprocessingHeadless` surfaces carry 45.8-48.1 % exact-duplicate coordinates (Authors' clouds carry none) and 4.0-4.6x their point count; every mean cost therefore double-weights almost half of every wall. Quantify it over the whole corpus, name where the writer emits a point twice, and rerun the Part A benchmark with exact duplicates removed in memory (the corpus itself is never edited).
2. **Check the Authors'-surface losses.** State whether removing duplicates (a) leaves the Authors' surface Part A numbers exactly unchanged, as it must if they carry no exact duplicates, and (b) removes the own-vs-Authors gap on the pieces that lose; and report whether the Ticket 07 F1-induced Authors'-surface Pot J regression (J07's 6.60 deg line pushed out, Authors' Pot J K3 8 -> 7) survives the reworked selector.
3. **Attack the deeper cause: why the true-axis basin costs out at rank 29-128 of 116-131 basins.** Diagnose the rank mechanically (60-most-drawn cut / seed cost / 15 deg dedup shadowing / refinement / `keep_lines`), then pre-register at most two scale-free shortlist-and-cost fixes tied to the measured mechanism. Part A gates them; only a passing fix runs the E2E.

**Answers:** E1
**Blocked by:** None (Ticket 07 resolved at `1a19c9a`, Reading `pot-j-own-surface-not-fixed-offline`; Ticket 03 unmerged at `325a0a8`)
**Status:** ready-for-agent
**Branch:** set by `ticket_start.sh`
**Worker:** unassigned
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
