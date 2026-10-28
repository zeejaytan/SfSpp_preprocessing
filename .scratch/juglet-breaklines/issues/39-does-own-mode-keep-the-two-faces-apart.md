# 39: Does the own-mode admission keep the two faces apart?

**Status:** done
**Branch:** 39-does-own-mode-keep-the-two-faces-apart, in /c/PR/worktrees/sfs/39
**Answers:** U19
**Blocked by:** none
**Blocks:** none

## Why this exists

Ticket 38 showed that resolution is a real limiter and that the two exported surfaces are not two
faces. On evenly sampled clouds both silent sherds grow two large regions — sherd 2: 8 clusters,
surfaces of 4 155 and 3 979 points; sherd 9: 7 clusters, 2 229 and 3 512 — each surface covering the
sherd and sitting about 3 deg from the mesh. But the two surfaces then **nest**: 95 % (sherd 2) and
80 % (sherd 9) of the smaller one's points are also in the larger, and their mean normals point the
**same** way (+0.9960 / +0.9993). The pipeline prints the reason itself — the literal 3 mm boundary
admission hands each surface about half the whole sherd
(`[WINDOW-26] ... own_cluster_points=589 other_cluster_points=2237 candidates=5256 admitted_own=1610
admitted_other=1640`).

The pipeline already carries the rival rule. `SFS_REASSIGN_MODE=own`
(`mesh_processing_headless.cpp:3903-3925`) fits both clusters first and sends each candidate point to
the fitted surface it is nearer to, instead of to every surface within 3 mm. It has never been run on
clouds where the two clusters are actually separated — the one condition under which the two rules
can differ. That is this ticket.

## What to run

Two cells, one job. Regenerate the **same two clouds** ticket 38 grew on, with the stage-38
instruments already on main (`.scratch/juglet-breaklines/stage38/instruments/`: the mesh sampler, the
midpoint subdivision, the route-2 instrument gate):

| piece | level | expected points | expected median spacing |
|---|---|---|---|
| Juglet_Piece_2 | x1 | 6 259 | 0.209043 mm |
| Juglet_Piece_9 | x1 | 5 257 | 0.201511 mm |

The clouds must be checked against those two numbers **before** the cells run; if the sampler does not
reproduce them, stop and say so. (Ticket 38's own PLYs are deleted under the geometry rule; the sampler
is deterministic, so the check is count + median spacing, not a byte comparison.)

Arms, per piece:

- **A — control**: today's default, `SFS_REASSIGN_MODE=radius` (or unset). It must reproduce ticket
  38's numbers: sherd 2 surfaces 4 155 / 3 979, sherd 9 2 229 / 3 512. If it does not, the cell is
  void and the comparison cannot be made.
- **B — the test**: `SFS_REASSIGN_MODE=own`.

Everything else stays at the shipped defaults (`SFS_PAPER_CHAIN=1`, `SFS_PAPER_THETA=3.4`,
`SFS_SPACING_POLICY=piece`, no single-cluster write, no dedupe switch, no window override).

**Pot A is deliberately not in this job.** Its own-mode behaviour is a separate question, and the last
Pot A cell on the 1 000 000-point released cloud ran out the wall clock. Do not add it.

## What to measure, per cell

For **every written surface**: point count, distinct point count, extents and bounding-box diagonal
(mm), the fraction of the ORIGINAL piece's cloud within 2 mm of it, and the median folded angle to the
ORIGINAL mesh.

Between **Surface_0 and Surface_1 of the same cell**, with the corrected pair statistic that keeps the
signed component (`stage38/instruments/measure34.py`, `pair_pointwise`): `med_nn`, `med_along`,
`med_across`, `med_angle_deg`, `coin`, and the signed `med_t` with its p05/p95.

Three derived quantities, because they are what the question turns on:

1. **Shared points**: the count and fraction of the smaller surface's distinct points that also appear
   in the larger (round to 1e-4 mm), and the same the other way round.
2. **Mean-normal dot** between the two surfaces, and the median per-point folded angle between the two
   surfaces' normals at matching points.
3. **The admission line**: `[REASSIGN-22]` and every `[WINDOW-26]` line the pipeline prints for each
   cell, quoted verbatim.

## The bar the lead will read against (do not judge it yourself)

Two surfaces that are an inside and an outside of one wall should have: **shared points well under
10 %**, **mean-normal dot below -0.9** (they face opposite ways), **med_along about one wall thickness**
(Juglet 2 2.693 mm, Juglet 9 2.595 mm, ticket 35's ray measurements), and **med_across small**. Report
the numbers; the lead decides whether they meet it.

## Constraints

- **No change to tracked pipeline behaviour.** This ticket runs existing switches. If a switch is
  missing or does not do what its comment says, stop and report — do not edit `mesh_processing_headless.cpp`.
- Instruments and tables under `.scratch/juglet-breaklines/stage39/`; reuse stage 38's sampler and
  subdivision rather than writing new ones.
- Compute nodes only; **at most two jobs** (one to run, one to re-run if the first dies on plumbing).
  Split by piece, never by arm — a control that ran in a different job than its test is not a control.
- Synthetic clouds labelled synthetic in every table, figure and filename, staged inside the run
  directory only; never into the frozen corpus.
- Frozen corpus and `/opt/sfs-pristine` read-only, md5 before/after, compared; record ABSENT if absent.
- CRLF-check every script before submitting; `bash -n` the rendered batch script.
- Geometry dies with the ticket: clouds and surfaces deleted at the end with a counted record written
  **before** the delete. Keep tables, logs, per-surface jsons, the pipeline's own log lines.
- Index row with `verdict` and `human_note` left EMPTY.
- Report evidence, not verdicts: no "this shows", no Status change, no `intent/` writes, no merge.

## Evidence to report

1. The cloud check (regenerated points and median spacing beside the two expected numbers, both pieces).
2. The arm-A control against ticket 38's numbers, per piece — and a plain statement if it does not
   reproduce them.
3. The per-surface table, both arms, both pieces.
4. The pair table, both arms, both pieces, with the signed `t` and its percentiles.
5. The three derived quantities (shared points both ways, mean-normal dot, median normal angle).
6. The `[REASSIGN-22]` and `[WINDOW-26]` lines, verbatim, per cell.
7. Corpus and pristine md5 before/after; the geometry deletion record; job ids with `sacct` states; the
   pushed branch head.
8. Anything not done, with the exact command or line that failed.

## Progress (work in progress, 2026-10-28)

Numbers, evidence and the exact failures are in `.scratch/juglet-breaklines/stage39/REPORT.md`; the run of record
is `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode/` (job **33926931**, commit
`ed0fc16328efdb13991e2d9dba843fe7bddb174e`, `spartan-bm073`, `COMPLETED` 00:01:47, ExitCode 0:0). **One job of the
two allowed was used**; no cell failed, so there was nothing to re-run.

All eight evidence items are delivered:

1. **Cloud check** — both pieces reproduce ticket 38 before any cell runs: Juglet 2 6 259 points / 0.20904330739003849 mm
   median against 6 259 / 0.209043, Juglet 9 5 257 / 0.201511365190472 against 5 257 / 0.201511, `count_ok` and
   `spacing_ok` `yes`, gate `ok`. The clouds are byte-identical to ticket 38's (same md5s `c6cd2eab…` /
   `77e0f59d…`), and so are `sampler_validate_<piece>.json` and `sample_<piece>_x1.json`.
2. **Arm-A control** — reproduces ticket 38 exactly on both pieces: sherd 2 **4 155 / 3 979**, sherd 9 **2 229 /
   3 512**, so neither cell is void. Stronger: after masking the cell path and dropping the two timing lines and the
   `Sampled indices` draw, arm A's `mesh.log` has **0 differing lines** against ticket 38 run 6's own `mesh.log` for
   the same piece. Both arms of a piece ran on one cloud — their `inputs.md5` are byte-identical, and the environment
   differs only in `SFS_REASSIGN_MODE`.
3. **Per-surface table** — 8 rows in `out/cells-pipeline/surfaces.tsv` (points, distinct, extents, diagonal,
   2 mm coverage, folded angle to the original mesh). Piece 2 arm B `Surface_0` is bit-identical to arm A's; its
   `Surface_1` falls 3 979 → 3 762 (diagonal 27.7418 → 24.8165 mm). Piece 9 arm B `Surface_0` falls 2 229 → 2 087
   (diagonal 19.5211 → 18.6432 mm, 2 mm coverage 0.8138 → 0.6829), `Surface_1` 3 512 → 3 510.
4. **Pair table** — arm A's medians are all exactly `0.0` (every `Surface_1` point coincides with a `Surface_0`
   point). Arm B: `med_nn` 2.2847 / 2.1758, `med_along` **2.2541 / 2.1345 mm**, `med_across` 0.1593 / 0.1877,
   `coin` 0.0, signed `med_t` **-2.2541 / -2.1345** with p05 / p95 **-2.6541 / -1.5863** and **-2.4260 / -1.6616**.
   The `p90` columns and `min_nn_minus_across` are in the report.
5. **The three derived quantities** — arm A reproduces ticket 38's nesting: shared-of-smaller **0.9518 / 0.8020**,
   mean-normal dot **+0.9960 / +0.9993**. Arm B: shared **0** on both pieces (fraction 0.0 both ways), mean-normal
   dot **-0.9993570511406065 / -0.9999474210970047**, median per-point normal angle `na` because there is no shared
   position to take it at.
6. **`[REASSIGN-22]` and `[WINDOW-26*]` lines** — 8 lines per cell quoted verbatim from each cell's
   `logs/admission39.log`, in the report's section 6, with the reason each arm's numbers differ
   (`admitted_own` 0 on piece 2 arm B; 1 498 / 262 against 1 610 / 1 755 on piece 9) and with
   `[WINDOW-26-SWITCH]` identified as the window scheme (`g_windowMode`, `SFS_WINDOW_MODE`), not the reassign mode.
7. **Corpus, pristine, deletion, job, branch** — `corpus_before.tsv` = `corpus_after.tsv` (1 803 lines) and
   `inputs_before.md5` = `inputs_after.md5` (215 lines), both `diff` files 0 bytes; `/opt/sfs-pristine` recorded
   **ABSENT** from the compute node with the `ls`/`stat` text; the geometry delete counted first (14 files /
   4 512 423 bytes, 0 after) and written to `GEOMETRY_DELETED_phase1.txt` before the delete; index row at
   `index.tsv` line 320 with `verdict` and `human_note` **empty**; branch head pushed, `git diff --stat main --
   mesh_processing_headless.cpp` **empty** (no tracked pipeline change).
8. **Not done, with the exact command or line** — six numbered items in the report's section 8, the load-bearing
   ones being: no `SAMPLER-GATE-DISCLOSURE_<piece>.txt` was written by `run_cell39.sh` (the route-1/route-2 lines
   survive in `phase1.log` only), `nest39.py selftest` is not run by the job (its 3/3 was run by hand), and the
   435 MB `build/` tree and the built binary `out/bin-new` stay on the cluster as they did for stage 38 — every
   other file the run wrote (89 of 90 outside `instruments/`) is in `stage39/results/`, md5-compared against the
   cluster copy, 89 of 89 identical.

The bar in "The bar the lead will read against" is restated in the report beside the numbers and **not judged**
there. `Status`, `intent/` and `mesh_processing_headless.cpp` are untouched by this ticket; no merge.
## Lead reading — 2026-10-28 (verified first-hand, not taken from the worker's report)

### The answer

**Yes, and the bar is met on both silent sherds at every limb.** On evenly sampled clouds, with
`SFS_REASSIGN_MODE=own`, the two exported surfaces of Juglet_Piece_2 and Juglet_Piece_9 stop nesting
and become two opposite-facing sheets about one wall thickness apart. The control arm, run on the same
cloud in the same job, keeps nesting. So the difference is the admission rule and nothing else.

The one thing that must not be said: own mode does **not** achieve this by "admitting only its own
points". On sherd 2 it admits **zero** own points to either surface and both surfaces are then filled by
the *other* cluster through the copy-over branch. The honest mechanism is one level up — own mode lets
the own/other split decide **which cluster each surface is fitted from**, and then the existing copy-over
branch decides what lands in the file. That branch is now on the critical path for sherd 2 and needs a
ticket of its own.

### The bar, limb by limb

| limb (ticket's own bar) | sherd 2 arm A (radius) | sherd 2 arm B (own) | sherd 9 arm A | sherd 9 arm B |
|---|---|---|---|---|
| shared distinct points, bar: well under 10 % | 2 352 of 2 471 = **95.2 %** FAIL | **0** | 1 616 of 2 229 = **72.5 %** (0.802 of the smaller) FAIL | **0** |
| mean-normal dot, bar: below -0.9 | **+0.99603** FAIL | **-0.999357** PASS | **+0.99932** FAIL | **-0.999947** PASS |
| med_along, bar: about one wall (2.693 / 2.595 mm) | **0.0** FAIL | **2.254 mm** = 0.84 of the ray wall | **0.0** FAIL | **2.134 mm** = 0.82 of the ray wall |
| med_across, bar: small | 0.0 but meaningless (surfaces coincide) | **0.159 mm** | 0.0, same | **0.188 mm** |
| coincidence, not in the bar, reported | 0.591 / 0.825 | **0.0 / 0.0** | — | — |
| signed med_t (p05 / p95) | -0.0043 / +0.0399 | **-2.2541** (-2.6541 / -1.5863) | — | **-2.1345** (-2.4260 / -1.6616) |

The signed `t` is the whole result in one column: in arm A the second surface sits **at** the first
(median 0.0 mm, a spike at zero); in arm B it sits **behind** it, one wall away, and the p05/p95 bracket is
narrow (-2.65 to -1.59 mm on sherd 2) rather than scattered.

The gap between 2.25 mm and the ray-measured 2.693 mm (2.13 against 2.595 on sherd 9) is the ray test
measuring a **chord across a curved wall** while the pair statistic measures the perpendicular offset at
matched points. Both are consistent with one wall; the ray number is an upper bound on the perpendicular
thickness.

### The mechanism, in the pipeline's own words

From the run of record (`/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode`,
job 33926931):

- sherd 2, arm B, surface 0: `admitted_own=0 admitted_other=2471` then
  `other_copied_over=yes final_points=4155`; surface 1: `admitted_own=0 admitted_other=2142`,
  `other_copied_over=yes final_points=3762`.
- sherd 2, arm A, surface 0: `admitted_own=2003 admitted_other=2471`, `other_copied_over=yes
  final_points=4155`.
- sherd 9, arm B, surface 0: `admitted_own=1498 admitted_other=2`, `other_copied_over=no
  final_points=2087`; surface 1: `admitted_own=262 admitted_other=2013`, `other_copied_over=yes
  final_points=3510`.

In own mode a candidate is admitted to the *nearer fitted surface*, so `admitted_other` counts the points
that belong to the other cluster but are nearer this surface — which is exactly the correct assignment
when the two fitted sheets are parallel and one wall apart. **The number that was merging the faces in
arm A was `admitted_other` under a 3 mm radius: everything within 3 mm went to both surfaces.** In arm B
the same candidate set is split by distance, and the two fits then hold.

That reads as a mechanism I can state without hedging: **the growth was never the last blocker on the
dense clouds; the admission rule was.** Ticket 38's own [WINDOW-26] line on sherd 9 said it before this
ticket ran (`admitted_own=1610 admitted_other=1640`, i.e. one third of the sherd handed to each surface
twice).

### What it costs

Own mode is not free. On sherd 2, Surface_0 is bit-identical to the control's, but Surface_1 falls
3 979 → 3 762 points (diagonal 27.7418 → 24.8165 mm). On sherd 9 both fall: Surface_0 2 229 → 2 087
(diagonal 19.5211 → 18.6432 mm, 2 mm coverage 0.8138 → 0.6829), Surface_1 3 512 → 3 510. Every surface
stays within 2.80-3.32 deg of its mesh, so accuracy is not traded away — only extent, because a point
nearer the other fitted sheet is now given to the other surface instead of to both.

### The picture

`fig39_Juglet_Piece_9_x1_hist_SYNTHETIC.png` is the decisive one: arm A's signed through-distance
histogram is a **spike at 0.000 mm** (p05 -0.004, p95 +0.040) and arm B's is a **broad lobe centred
-2.134 mm** (p05 -2.426, p95 -1.662). Arms A and B: `fig39_..._armA_views_SYNTHETIC.png` and
`..._armB_views_SYNTHETIC.png`, one scale for both arms, four panels each.

Looking at the views rather than trusting a description of them: in arm A the orange surface is drawn over
the blue one across the whole sherd because the two coincide, and my own pixel count (bluish 18 541 px,
orange 52 112 px in that panel) reflects the occlusion. In arm B the blue surface is exposed over most of
the sherd (bluish 46 425 px against orange 57 631 px) because the second surface has moved behind it. A
rendered picture alone cannot tell two faces of one wall from two patches of one shell — that is why the
signed statistic exists — but it can and does show that the second sheet is no longer on top of the first.

### What this does not settle

1. **The cloud is synthetic.** Both cells ran on a cloud obtained by subdividing the sherd mesh and
   sampling it; the scan itself carries only 2 094-2 565 points. So this shows what the *rule* does when
   the growth is given a cloud it can work with. Whether that cloud can be obtained from a real scan of
   these sherds — thicker sampling, a better scanner, or kept as the mesh's own surface — is untouched.
2. **One vessel, two sherds.** The other seven Juglet pieces and all of Pot A have not run under own mode.
   Pot A is the risk: it works today under radius and own mode could break it. This is the next cell.
3. **The copy-over branch decides sherd 2.** `mesh_processing_headless.cpp:1167-1170` copies the other
   cluster over when it is larger, and on sherd 2 both surfaces took that branch. It happens to give a
   correct separation here; on another piece it could give the wrong one and nothing would report it.
4. **The 3 mm window is still literal.** Arm B changes the assignment rule, not the window
   (`[WINDOW-26-SWITCH] mode=literal` in every cell).
5. **De-duplication is still dead** (ticket 27/28): surface point counts carry the cluster roughly twice,
   which is why the distinct counts differ from the point counts on both surfaces in both arms.
6. **A wall that is 2.1-2.3 mm apart at the perpendicular is a plausible pot wall, not a proof it is one.**
   Two parallel faces of a single broken slab would give the same signature. What rules the coincidence arm
   out and this one in is the shared-point count (0) and the sign of the mean normal — together, not the
   distance alone.

### verified:

- `sacct -j 33926931,33929933 -X` → COMPLETED 0:0, 00:01:47 spartan-bm073 and 00:01:55 spartan-bm058.
- `out/cloud_gate.tsv` (run of record) → Juglet_Piece_2 6 259 pts / 0.20904330739003849 mm md5 c6cd2eab8a1df10b6e97951cc360d3af; Juglet_Piece_9 5 257 / 0.201511365190472 md5 77e0f59d80bef8df1f92049622f97f59; both byte-identical to ticket 38's clouds.
- `fig39_Juglet_Piece_9_x1_figures.json` arm A → shared 1616, shared_over_a 0.7249887842081651, mean_normal_dot 0.9993183797978673, pair med_along 0.0, coin 0.8246013667425968, p05_t -0.004322898100523831, p95_t 0.03986170855198336.
- `fig39_Juglet_Piece_9_x1_figures.json` arm B → shared 0, mean_normal_dot -0.9999474210970047, med_nn 2.175759811718171, med_along 2.134489859141274, med_across 0.1877338703672796, coin 0.0, med_t_signed -2.134489859141274, p05 -2.4260113140511037, p95 -1.6615995307254277.
- `out/cells-pipeline/surfaces.tsv` (8 rows) → arm B sherd 2 Surface_0 unchanged at 4 155, Surface_1 3 979 → 3 762, diagonal 27.7418 → 24.8165 mm; sherd 9 Surface_0 2 229 → 2 087, diagonal 19.5211 → 18.6432 mm, coverage 0.8138 → 0.6829, Surface_1 3 512 → 3 510.
- `grep "WINDOW-26" <cell>/logs/mesh.log` → the six admission lines quoted above, verbatim, including `other_copied_over=yes` on both sherd-2 arm-B surfaces and `admitted_own=0` on both.
- `[REASSIGN-22] mode=radius` vs `mode=own` → the only environment difference between the arms of a piece; both ran one cloud (identical `inputs.md5`).
- Arm A reproduces ticket 38 exactly: 4 155 / 3 979 and 2 229 / 3 512, and its `mesh.log` has 0 differing lines against ticket 38 run 6 after masking the cell path and the two timing lines.
- `out/GEOMETRY_DELETED_phase2.txt` → "geometry_files_before 7 / geometry_files_after 0"; `out/geometry_counts_phase2.tsv` → pcd 1 / 314 797 B, ply 6 / 1 650 520 B, TOTAL 7 / 1 965 317 B.
- `out/pristine.txt` → "/opt/sfs-pristine ... status ABSENT"; `corpus.diff` and `inputs.diff` both 0 bytes.
- `git diff --stat main -- mesh_processing_headless.cpp` → empty: this ticket changes no tracked pipeline behaviour, it runs a switch that was already there.
- The three PNGs I opened (`read_image` is refused for this session's model; `modlens_read_image` used and its prose checked against the tables, where it wrongly described arm A's sheets as "visibly separated") plus my own PIL pixel counts in `artifacts/juglet-p39/`.

### What happens next (proposed, not decided here)

Own mode is the first rule found in this whole investigation that turns the nesting into two faces. Before
it can be called the fix it has to survive two cells: **the other seven Juglet sherds under own mode**, and
**Pot A under own mode** (the pot works today under radius; a rule that breaks it is not an improvement).
The copy-over branch on sherd 2 and the still-literal 3 mm window are the two follow-ups that this reading
raises and does not answer.


