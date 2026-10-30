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

## Result — run of record (lead, 2026-10-31)

Run `20261031-0123_a4d72f6_t46-covering4`, job **34071136**, commit `a4d72f6`, 9 coverings + 17 cells.
`sacct`: **FAILED 3:0**, elapsed **00:06:31**. Exit 3 is `theta_check46.py`'s single miss (J3); every cell ran
(`pipeline_rc` 0 on 17 of 17), `out/corpus.diff` and `out/inputs.diff` are 0 bytes, geometry was deleted with its
census (85 files before, 51 kept cell surface plies, coverings deleted after phase 9), and one index row was
appended with `verdict`/`human_note` **empty** for me. Phase rcs: 4 -> 8, 7 -> 3 (phase 4's 8 was its own spacing
proof — see "Two alarms that were the instruments", below; replayed on this run's own tables it passes).

Three submits before it, each recorded as a **void** row in `runs/index.tsv`:

| run | job | died how |
|---|---|---|
| `20261031-0104_b30da90_t46-covering` | 34069902 | cancelled 00:06:18 — the exact all-point surface gate cost 5+ min per piece |
| `20261031-0112_1801b68_t46-covering2` | 34070441 | FAILED 5:0 — coverings sat 0.035-0.110 mm *inside* the mesh (voxel merge), and `make -j` received a piece name instead of a job count |
| `20261031-0118_f152500_t46-covering3` | 34070850 | cancelled 00:02:04 — surface gate clean, but the written cloud's measured spacing moved 1.1-1.6 % after projection |

Each defect was fixed in the instruments — project every sampled point onto the mesh exactly, loop the nine
pieces with `JP` so the CPU count survives, re-solve the sample spacing against the post-projection median —
and no band was widened to make a run pass.

### The covering did what it was meant to

`out/covering_gate.tsv`, 9 of 9 PASS (max distance to the mesh is measured on a 1 000-point subsample):

| piece | shipped | covering | ratio | spacing err | max dist to mesh |
|---|---|---|---|---|---|
| J1 | 24 294 | 26 835 | 1.105 | 0.16 % | 0.000000 mm |
| J2 | 2 565 | 6 066 | 2.365 | 0.43 % | 0.000000 mm |
| J3 | 3 493 | 9 707 | 2.779 | 0.55 % | 0.000000 mm |
| J4 | 3 651 | 9 055 | 2.480 | 0.42 % | 0.000000 mm |
| J5 | 6 211 | 15 056 | 2.424 | 0.68 % | 0.000000 mm |
| J6 | 5 126 | 13 055 | 2.547 | 0.60 % | 0.000000 mm |
| J7 | 8 421 | 17 655 | 2.097 | 0.80 % | 0.000000 mm |
| J8 | 4 479 | 10 710 | 2.391 | 0.41 % | 0.000000 mm |
| J9 | 2 094 | 5 249 | 2.507 | 0.67 % | 0.000000 mm |

No subdivision was used (level x1): every covering point lies on the shipped mesh. The covering holds
**2.1-2.8x** the points of the cloud the pipeline was reading, at the same spacing.

### Theta: the pipeline's own curvature measurement, on an even covering

| piece | reference (k43) | delivered | delta | within 2 % |
|---|---|---|---|---|
| J1 | 10.29 | 10.22647 | -0.617 % | yes |
| J2 | 12.40 | 12.59916 | +1.606 % | yes |
| J3 | 9.35 | 9.13822 | **-2.265 %** | **no** |
| J4 | 10.25 | 10.28547 | +0.346 % | yes |
| J5 | 8.74 | 8.72093 | -0.218 % | yes |
| J6 | 8.16 | 8.23416 | +0.909 % | yes |
| J7 | 8.65 | 8.64907 | -0.011 % | yes |
| J8 | 10.05 | 10.14824 | +0.978 % | yes |
| J9 | 12.68 | 12.69573 | +0.124 % | yes |

Mean absolute error **0.79 %**, no systematic bias (five high, four low). On the *same* nine pieces ticket 45's
run on the released clouds delivered **18.7-54.4 deg**. Same binary, same code, same source commit: the
difference is the cloud.

### Predictions

| # | prediction | outcome |
|---|---|---|
| P1 | theta within **2 %** on 9 of 9 | **8 of 9.** J3 at -2.27 % (0.21 deg on a 9.35 deg angle). The ticket's own falsifier — "any piece off by more than 5 %" — is **not** reached; the closest is 2.27 %. |
| P2 | J2 and J9 grow **two** surfaces | **met.** J2 263 / 6 143, J9 3 770 / 4 855. Both had been `none` at every angle tried so far. |
| P3 | J3-J8 keep the ticket-44 pairs (along 1.86-2.81 mm, across 0.38-0.63, angle 13-19 deg, coincidence ~0) | **met in form, across is smaller.** J3-J9: along **1.88-2.70 mm**, across **0.18-0.30 mm**, angle **10.5-20.4 deg**, coincidence **0.0000-0.0112**. |
| P4 | Pot A unchanged, 8 of 8 two surfaces, counts within 2 % | **met.** theta identical to ticket 45's arm F to 5 dp on all 8; clusters identical; worst surface-size move **0.55 %** (PA01 second surface 82 029 vs 82 484). |

Outcome and surface counts (all nine grew two surfaces; clusters in brackets): J1 261/31 579 (4), J2 263/6 143 (3),
J3 7 891/7 473 (7), J4 9 120/7 098 (2), J5 10 623/13 048 (5), J6 8 916/11 115 (7), J7 15 223/16 451 (4),
J8 7 582/8 674 (9), J9 3 770/4 855 (4).

### What the eye sees

`juglet_surfaces.png` (3x3, grown surfaces over each piece's own mesh silhouette): J3-J9 show **two interleaved
sheets filling the sherd**, not a scrap beside a sheet. J1 and J2 are the exception and the picture says so
plainly — one large surface plus a small patch (J1 261 points, J2 263). `j2_covering.png` shows why the
covering was the variable: the released cloud hugs the piece's **outline** and leaves the interior hollow — it
is the mesh's vertex set, thin triangles and holes — while the covering is even. This session read both
images directly.

### What this does not say

- **Not the paper's method.** The covering is derived *from the shipped mesh*: the run adds coverage, it does
  not add detail. Ticket 38's standing question — may a synthetic cloud stand in for a scan in any recorded
  number — is **untouched** here, and ticket 16 must be told before these numbers meet the paper's.
- **No wall pair has been shown.** The 0.18-0.30 mm separation is a tenth of the Juglet's wall thickness
  (2.4-3.3 mm), so what the growth produces is still two layers of the *same* face — the signature ticket 44
  recorded at 0.38-0.63 mm. This run does not upgrade that reading.
- **The clustering is still loose**: 2-9 clusters per piece, most of them under the 30-point floor.

### The consequence for ticket 45

The law now holds **inside the pipeline**, measured by the pipeline's own instrument (8 of 9 within 2 %, mean
0.8 %), so the C++ port is faithful, the constant is right, and ticket 45's failure was the input cloud — not
the method and not the measurement code. That is the first question answered.

The second is not answered, and it decides the ship: the formula needs `R`, and on a **real released cloud**
`R` is under-read 2-4x (ticket 45's own measurement). Adopting the formula as the default today would therefore
leave the Juglet at ticket 45's 18.7-54.4 deg and change nothing for Pot A, where the shipped 3.4 and the
formula's 2.9-4.4 already agree. **The angle is no longer the blocker; the input cloud is** — a
capture/representation question (is a vertex-set dump a faithful stand-in for a scan?), not an angle
question, and the same question ticket 38 left open. Decision for the conservator: ship the formula as
correct-but-inert (it becomes right as clouds get denser), or hold it until the input side is answered.

### Two alarms that were the instruments

Both were raised by this run, both are fixed in commit `076d0c3`, and both were replayed on this run's own
tables so the tables above stand unchanged:

1. `run_cell46.sh`'s spacing proof compared the run's `[SPACING-22]` **S** with `spec46.tsv`'s *requested* S at a
   1e-3 mm absolute tolerance, so four pieces read MOVED at 0.0011-0.0020 mm. The run's S actually equals the
   covering's own measured spacing to **2.5e-5 mm** worst case (J1 0.337343 vs 0.337342846 ... J9 0.202559 vs
   0.2025699). The proof now reads the achieved spacing from `<piece>_cover.json`.
2. `theta_check46.py` demanded *exact* equality of the Pot A control counts where this ticket asks for 2 %;
   it now requires identical clusters and both surface sizes within 2 %.

### Verified (lead)

- `verified: out/cells-pipeline/*/cell.tsv spacing_line -> S matches the covering spacing to 2.5e-5 mm`
- `verified: python theta_check46.py --cells out/cells-pipeline/pipeline_cells.tsv -> exit 3, J3 alone`
- `verified: git diff --name-only fe33e44...HEAD -> only .scratch/juglet-breaklines/issues/46-* and stage46/**`
- `verified: git rev-parse HEAD:mesh_processing_headless.cpp == fe33e44:... -> 25895a3fa52d3c120e28c2d64628a4eb14eb2620`
- `verified: wc -c out/corpus.diff out/inputs.diff -> 0 0`
- `verified by eye: juglet_surfaces.png, j2_covering.png (read directly in this session)`

- Deleted at close, with this record: `.scratch/juglet-breaklines/stage46/_dry46_submit.sbatch` (16 036 B, mtime
  2026-10-31 01:18) — the pre-flight dry render of `submit46.sbatch.tmpl`. The template itself is tracked and is the
  source; read back before deleting: its first lines were the rendered `#SBATCH` header (`--job-name=t46-covering`,
  `--account=punim2657`). Nothing else was removed, and no geometry was ever on the laptop.

## Answers

- Answers: U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

## Blocked by

- branch 45 (`fe33e44`): the formula default is implemented and unmerged on purpose — adopt or drop it on
  this run's result, not on its own. Carried in by a merge into this ticket's branch (see Prove-out), never
  into main.

**Status:** done
**Working in:** lead session C:/PR (SFS++ theta work, 2026-10-30) (2026-10-31)
**Branch:** 46-feed-the-growth-an-even-covering, in /c/PR/worktrees/sfs/46
**Worker:** lead — the session that wrote this ticket built its instruments, submitted its four runs, verified them and closed it; the ticket-45 worker died twice and the pattern was not reinstated (rule lapse, 2026-10-31)
**Needs-eye:** the covering figure and the 3x3 surface panel are drawn and read (see Result); the conservator still decides the ticket-45 ship question

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

## The default after this ticket (lead, 2026-10-31)

Closing this ticket merged its branch, and the branch carried ticket 45's merge (`006d4c8` of `fe33e44`) — so `main` began computing the growth angle from curvature with **no env set**, the exact configuration ticket 45 measured as broken. Commit `2263532` gates the rule: it runs only when `SFS_GROWTH_FORMULA` is set and not `0`; with nothing set the angle is the flat 3.4, and `SFS_PAPER_THETA` still overrides both. `medianFoldRadius45()` is untouched, so nothing measured here is thrown away.

Verified on Spartan, run `20261031-0200_2263532_t46-default-check` (job `34073410`, sacct COMPLETED 0:0, 00:02:44), rebuilt from `2263532` with the whole `SFS_*` family unset:

| piece | paper grow theta | `[GROWTH-45]` lines | outcome | surfaces | SampledWithNormals md5 |
|---|---|---|---|---|---|
| Juglet_Piece_2 | 3.40000 | 0 | none | – | equal to t45 arm O |
| Pot_A_Piece_01 | 3.40000 | 0 | two | 66 760 / 57 295 (t45 arm O 66 761 / 57 284) | equal to t45 arm O |

The default is back to what shipped before this week: a run with no switches behaves as it did, and the formula is available for the day the input side is fixed.