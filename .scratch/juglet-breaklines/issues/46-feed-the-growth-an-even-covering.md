# 46 — feed the growth an even covering, and the formula's angle with it

## What to build

One diagnostic grid (stage46) that runs the shipped pipeline **unchanged in source** — with ticket 45's
curvature default switched on — on an **even covering of each Juglet piece's own shipped mesh at the
spacing the run already resolves**, instead of the released vertex-set cloud. Nine Juglet cells, and the
eight Pot A pieces on their released ~1 000 000-point clouds as the unchanged control.

**This is not the paper's method, and every number from it says so.** The paper's resampling step
(§IV-B1, quoted in ticket 06) resamples the **breakline** to 1.9 mm; it says nothing about resampling the
surface cloud. Feeding an even covering is therefore *our* addition, made to test one mechanism, and it is
labelled "even covering" in every table, figure, filename and sentence. Ticket 16 (paper-compliance audit)
must be told before any of these numbers is compared with the paper's.

### Why this run, in one line

Ticket 45 measured that the angle the pipeline computes is wrong by exactly the factor by which its input
cloud under-reads the fold radius: on all 17 pieces `theta_delivered / theta_reference` equals
`R_even / R_shipped` to a mean of **0.7 %** (max 1.1 %, Pearson **0.9999** on the log ratios; Juglet
under-read 2.1-4.9x, Pot A 1.09-1.38x). So the estimator is faithful and the *covering* is what is wrong.

### Where the covering comes from

- Juglet input cloud: `Dataset/Point/<Pot>/<Piece>_Point.pcd`. Ticket 38's sampler proof established that
  this **is the mesh's vertex set** (piece 2: **2 565** points against **6 259** for an even covering at the
  same spacing; 0.232 against 3.94 points/mm^2), i.e. thin triangles and holes, not sparse millimetres.
- Even covering: sample the same shipped mesh (`Dataset/Mesh/<Pot>/<Piece>_Mesh.obj`) at that piece's
  resolved spacing with the ticket-38 sampler (`stage38/instruments/mesh38.py`, `sample_at`, analytic
  normals). **No subdivision**: level x1 only, so every sampled point lies on the shipped mesh.
- Pot A: nothing staged, nothing sampled — its released clouds already work.
- The sample spacing `S` per piece is the ticket-43 `spacing_req` value, which is what `[SPACING-22]`
  already resolves to (verified to 5 dp in ticket 45's `[GROWTH-45]` lines): J1 0.338049, J2 0.210898,
  J3 0.215278, J4 0.215618, J5 0.238566, J6 0.223696, J7 0.257993, J8 0.221611, J9 0.203461 mm.

### Predictions, written before the run

| # | prediction | falsified if |
|---|---|---|
| P1 | `[GROWTH-45]` theta lands within **2 %** of the ticket-43 reference on 9 of 9 | any piece off by more than 5 % |
| P2 | J2 and J9 — silent at every angle so far — grow **two** surfaces | either still `none` or `one` |
| P3 | J3-J8 keep the ticket-44 wall pairs (med_along 1.86-2.81 mm, med_across 0.38-0.63, angle 13-19 deg, coincidence ~0) | a pair becomes two same-facing sheets |
| P4 | Pot A unchanged: 8 of 8 two surfaces, counts within 2 % of ticket 45's control arm | any Pot A piece moves |

Either falsifier is informative and must be recorded as such: **theta lands but surfaces do not** ->
coverage is necessary and not sufficient, and the next limiter is the growth itself; **theta does not
land** -> the vertex set is not the only difference between the two clouds and the sampler's normals are
suspect — stop and say so rather than tuning.

### Evidence this rests on (cite, do not re-litigate)

- Ticket 45 run `20261030-2128_f4a3559_t45-default` (job 34054302): the theta/radius identity above;
  `out/theta_check.tsv` within_0.30 = 2 of 17; 8 of 9 Juglet pieces `status_outcome=none`.
- Ticket 38 run `20261028-0414_2a34d86_t38-resolution` (job 33892259): at the same spacing but an even
  covering, `Juglet_Piece_2` gives 8 clusters and two surfaces **4 155 / 3 979** points, `Juglet_Piece_9`
  **2 229 / 3 512**; and the shipped cloud is the vertex set.
- Tickets 39/40: with those dense coverings, `SFS_REASSIGN_MODE=own` (the default since ticket 41) stops
  the two faces sharing points (0 shared, mean normals -0.9994 / -0.9999).
- Ticket 45's k-sweep rules out neighbourhood size as the cause: J2 R = 0.60 / 0.78 / 1.04 / 1.17 mm at
  k = 10 / 30 / 60 / 120, never the calibration's 3.24.

## Prove-out

Reuse stage45's machinery (branch `45-adopt-the-curvature-formula-as-the-default-growth-angle`, tip
`fe33e44`): `run_cell45.sh` already carries the run cloud in one variable (`RUN_CLOUD`, one stager call at
about line 104), so stage46 changes the staging, not the pipeline.

**How the branch is built, because the two rules meet here.** `scripts/ticket_start.sh` always cuts the ticket
branch from `origin/main`, and main deliberately does **not** carry ticket 45's unmerged formula. So: open the
ticket with the script as usual, then in the worktree run
`git merge --no-ff fe33e44 -m "..."` — that brings the formula default, its `[GROWTH-45]` line, the medians
and stage45's instruments into this branch, and **main still sees neither**. Do not merge branch 45 into main
and do not rebase: the adopt-or-drop decision belongs to this run's result. Record the merge commit in the
ticket, and diff against `fe33e44` (not main) when proving the source is untouched.

## Deliver

1. **Covering gate**, per Juglet piece: shipped points, even-covering points, ratio, achieved spacing vs
   `S` (within 1 %), maximum distance of a sampled point from the mesh (**<= 1e-3 mm**), cloud md5, and the
   line "no subdivision used".
2. **Per piece**, 9 Juglet + 8 Pot A: `[SPACING-22]` S (must be unchanged), `[GROWTH-45]` theta, cluster
   count, `status_outcome`, both surface point counts, pipeline rc.
3. **`theta_check.tsv`** against the committed reference (J1 10.29, J2 12.40, J3 9.35, J4 10.25, J5 8.74,
   J6 8.16, J7 8.65, J8 10.05, J9 12.68; PA01 4.36, PA02 3.30, PA03 3.76, PA04 2.92, PA05 3.50, PA06 3.17,
   PA07 2.66, PA08 3.61), with both the absolute delta and the percentage, and a pass at 2 %.
4. **Pair table** for every cell that grows two surfaces: med_nn, med_along, med_across, folded angle,
   coincidence (the `measure34` / `pairs33` columns already in stage45's instruments).
5. **Two pictures for the eye**, workspace-relative links: (a) piece 2's released cloud and its even
   covering drawn over the same mesh at a scale that shows the thin triangles — the covering before and
   after; (b) a 3x3 panel of the grown surfaces against the mesh, one per Juglet piece.
6. Bookkeeping: corpus and inputs md5 unchanged before and after (0-byte diff), instruments md5 gated, one
   index row appended with `verdict` / `human_note` left EMPTY, `run.json`, poll and final `sacct`
   recorded in the ticket.
7. Geometry dies with the ticket: the staged coverings and surfaces are deleted at close with the census
   written before the delete.

## What must not be claimed

- Not a scan, not new data, not more resolution: the same mesh, resampled evenly at the same spacing.
  Ticket 38's standing question ("may a synthetic cloud stand in for a scan in any recorded number?") is
  **not answered here**; this run dodges it by adding coverage, not detail — say exactly that.
- No comparison of absolute surface counts with the paper, and none with Pot A's 15/15 seating bar.
- No per-piece angle tuning: `SFS_PAPER_THETA` stays unset in all 17 cells.

## Answers

- Answers: U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

## Blocked by

- branch 45 (`fe33e44`): the formula default is implemented and unmerged on purpose — adopt or drop it on
  this run's result, not on its own. Carried in by a merge into this ticket's branch (see Prove-out), never
  into main.

**Status:** in-progress
**Working in:** lead session C:/PR (SFS++ theta work, 2026-10-30) (2026-10-31)
**Branch:** 46-feed-the-growth-an-even-covering, in /c/PR/worktrees/sfs/46
**Needs-eye:** after the run — the covering figure and the 3x3 surface panel go to the conservator

## Acceptance

- [ ] Source untouched: `git diff fe33e44...HEAD` shows changes only under `.scratch/juglet-breaklines/stage46/**`
      and the ticket file; `git log --oneline origin/main..HEAD` shows branch 45's two commits plus one merge
      and nothing else; `mesh_processing_headless.cpp` md5 equals branch 45's.
- [ ] Builds clean with stage45's `build_bin` (apptainer cmake), same commit.
- [ ] Covering gate passes on 9 of 9 Juglet pieces (spacing within 1 %, sampled points <= 1e-3 mm from the mesh,
      point ratio recorded against the shipped cloud).
- [ ] 17 of 17 cells run with `SFS_PAPER_THETA` unset and `SFS_GROWTH_MODE` unset; `[SPACING-22]` S equals the
      pre-run value on every piece.
- [ ] `theta_check.tsv`: 9 of 9 Juglet within 2 % of the reference, per-piece delta and percentage reported;
      Pot A reported beside it (the 1.09-1.38x under-read is expected to persist there and is not a failure).
- [ ] Outcome class and surface counts per piece; pair table for every two-surface cell.
- [ ] Pot A 8 of 8 two surfaces, counts within 2 % of run `20261030-2128_f4a3559_t45-default` arm F.
- [ ] Corpus and inputs md5 unchanged; instruments md5 gated before phase 4.
- [ ] `run.json`, index row appended (verdict/human_note left for the lead), poll and final `sacct` in the ticket.
- [ ] Worker reports numbers and paths; the lead runs its own acceptance check (hidden before hand-over),
      verifies, then decides whether adopting ticket 45 plus this covering step is the ship.
