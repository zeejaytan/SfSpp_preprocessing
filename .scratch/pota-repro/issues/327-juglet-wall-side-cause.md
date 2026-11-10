# Ticket 327 — Bind why three Juglet pieces draw the crack line on the outer wall, and prove the cure direction

**Status:** in-progress
**Working in:** C:/PR/worktrees/sfs/327-juglet-wall-side-cause
**Branch:** 327-juglet-wall-side-cause
**Answers:** E1
**Depends on:** none (326's bar-1 diagnosis is input; it lives in the 326 worktree)
**Blocks:** 328 (the cure)
**Worker:** dsh-subagent (glm-5.3)
**Budget:** medium (4 failed acceptance runs; waiting costs none)

> **In one line.** The interior/exterior breakline defect was fixed in the edgeline processing itself
> (tickets 175→182→296: split the dots by parent surface, walk each face, file both slots — interior in
> slot 0 *by construction*, proved 8/8 + 15/15 on a pot). That fixed code regenerated the Juglet bundle on
> 2026-11-03 — and pieces 2, 6 and 9 still carry the **exterior** wall in Surface_0/Breakline_0, so five of
> nine touching joins present breakline normals facing the wrong way and the assembler rejects them at
> correspondence time. Bind which rule in the shipped chain decides the face→slot filing, why it inverts on
> exactly 2/6/9, and prove by a diagnostic swap **on copies** that correcting the slot flips the five
> failing joins' normals positive.

## What is already known (lead-verified 2026-11-10; do not re-derive, reproduce)

**(a) The wall-side split.** Mean radius of each Surface cloud about the piece's own GT axis
(`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` applied with the piece's GT transform; lead script
`C:/PR/worktrees/sfs/325/.scratch/pota-repro/t325/wall_side_check.py` over `artifacts/pota325/juggeom`):

| piece | S0 r_mean (mm) | S1 r_mean (mm) | Surface_0 is |
|---|---|---|---|
| 2 | 5.94 | 5.33 | **outer** |
| 6 | 7.35 | 6.28 | **outer** |
| 9 | 3.74 | 3.36 | **outer** |
| 1,3,4,5,7,8 | — | — | inner |

**(b) The consequence at the assembler** (ticket 326 bar 1; job 34671027, run
`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1844_6925cb0_t326-diag`, GTPAIR lines): every
**same-wall** touching pair passes the normal-sign test (1-8 +0.97, 1-4 +0.79, 2-9 +0.99, 3-5 +0.99); every
**cross-wall** pair fails (1-2 −0.90, 1-9 −0.94, 2-5 −0.99, 7-9 −0.67, 6-7 +0.11 with 6/16 negative).
18/18 edges explained. The failing gaps equal wall thickness (0.36-2.91 mm): the two lines are the two rims
of one crack.

**(c) The fix line (this is the fix the conservator means — the edgeline processing).**
- **175** (2026-10-20, results-in): user direction "split the dots and let the walk do two walks, one for
  outer, one for inner". Separation by **parent-surface labels** (per-triangle wall label: triangle-normal
  vs mesh-frame radial; fold joins inner). Lead ruling: the **true-face (interior) walk goes in slot 0**
  (assembler opens slot 0 only; slot 0 is interior by design). Note for context: 175's own filing was a
  scratch proof ("installed nowhere"); its stage accounting found the estimator's Surface_0-exclusive
  product is 96% outer-wall.
- **182** (2026-10-20, DONE): the double-walk mechanism traced on the post-176 edgeline.
- **210** (done): Bl0/Bl1 swapped to the author convention on P02-P08.
- **238** (done): "restore working root-edge source to main" — the pristine line was reworked around here.
- **296** (done, merged `0050313` 2026-10-25): **"the interior slot is by construction, not a per-piece
  swap"** (`d19e437`); proved on its pot — interior slot 8/8, both arms seat 8/8 and join 15/15.
- Background (superseded era): the 2026-10-17/18 diagnosis of the same symptom on pots (80: cause bound to
  the size-descending sort in `mesh_processing_headless.cpp:218/:1680`; 81: per-pot slot-exchange surgery)
  was a data-level stopgap before the construction fix landed.
- Open history wrinkle to pin: `e962159` "Split-walk cure on pristine line" (2026-10-21) is **NOT an
  ancestor of fab76f5**, yet 296 (Oct 25) IS. Say what the shipped line at fab76f5 actually carries.

**(d) The regen ran the fixed code.** The Juglet bundle was regenerated 2026-11-03 by the t66 run
(`20261103-1332_fab76f5_t66-admitsign-default`, ticket 66-potc-reorder) at fab76f5, **with 296's
by-construction interior rule in the pipe** — and 3/9 pieces still came out exterior-in-slot-0. So this is
not "the cure never reached the Juglet"; the rule, proven on a pot, **inverts on the Juglet's geometry**
(33 mm vessel; the two walls sit 0.36-2.91 mm apart at the measured gaps). The same one-wall symptom was
also diagnosed on the old (pre-2026-10-31) Juglet bundle in September.

**(e) Slot semantics** (2026-10-17): slot 0 means interior *by convention*
(`Surface_0 -> Breakline_0`, `convert_intermediate_breaklines.py:45`); the assembler reads only slot 0.
"Interior" names the slot, not necessarily the content — which is exactly the defect.

## What to deliver (stop on the first bar that fails and report it)

1. **Nine-piece census, evidence class ≥ ticket 80's.** Re-derive the wall side independently (your own
   script under `.scratch/pota-repro/t327/`, not a copy of the lead's): per piece, mean radius of S0 and S1
   about the GT axis **and** per-wall loop point count / sampling density. Confirm the split is exactly
   2/6/9-outer, and record per-wall densities for the mechanism test in bar 2.
2. **The filing rule + why it inverts.** In the shipped chain at fab76f5 (read the t66 run's
   `submit.sbatch` / stage scripts / logs to see what ran): name **file:line** where the face→slot filing
   is decided (the "interior by construction" of 296 — parent-surface label? walk order? radial sign?), and
   why it inverts on exactly 2/6/9. Test the rule's inputs per piece (e.g. the radial/frame quantity it
   thresholds, evaluated on each Juglet piece) and show the quantity flips sides on 2/6/9 while holding on
   the six. Also pin the e962159-vs-238 history wrinkle from (c).
3. **The old bundle.** If a pre-2026-10-31 Juglet bundle still exists on Spartan, census it the same way —
   were 2/6/9 flipped then too? If it is gone, record that it is gone (nothing is deleted).
4. **Causality proof on COPIES.** Copy the three offending pieces' inputs under your run dir, swap S0↔S1 +
   Bl_0↔Bl_1 on the copies only, run the 326 pair harness
   (`C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp`, read-only reference; do not
   modify it) at GT on copies + the untouched six, and report dot_med_d3 per touching pair.
   **Bar: all five formerly-failing pairs ≥ +0.7 median; strict-gate inliers > 0 on each.**
5. **Renders.** Per swapped piece, before/after (outer-wall line vs inner-wall line, coloured) into
   `SfSpp_preprocessing/artifacts/pota327/renders/`, as workspace-relative Markdown links in your
   write-back. Eye-check them; the conservator reads pictures.

## Must not

- **No corpus writes.** Diagnostic copies live under your run dir only; the t66 bundle, `Dataset/`,
  `original_samples/` are read-only (list them before/after and paste the listings).
- **No fix in this ticket.** The swap-on-copies is diagnostic; designing or landing the cure is ticket 328.
- **No ORIG/GT points into anything.** GT transforms and axes are the oracle, evidence-only.
- **Never `git worktree add/remove`.** Work only in the pre-created worktree the dispatcher named.
- **No commits, no pushes.** Write-back goes into the ticket's `## Comments (worker, <date>)` section and
  your final-turn output. End with exactly one line:
  `**End state:** ready|waiting: <job ids>|blocked: <reason>|incomplete: <what>`.
- Poll `sacct` directly (never `slurm_poll.sh`); never idle-poll a PENDING job — end the turn `waiting:`.
- Spartan compute only; runs under
  `spartan:/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t327<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`.

## Inputs

- t66 Juglet bundle: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`
  (9x Surface_0/Surface_1 PLY + Breakline_0 PCD) — plus the run's `submit.sbatch`/stage logs for bar 2.
- GT: `/data/gpfs/projects/punim2657/Dataset/Juglet_GT/` (9 T matrices + `Juglet_Piece_N_Axis.xyz`;
  axis .xyz = point+direction, **last 6 numbers, direction = last 3**). Second copy under
  `sfs_preprocessing/Dataset`.
- Lead's measurement (reference, laptop): `C:/PR/worktrees/sfs/325/.scratch/pota-repro/t325/wall_side_check.py`
  over `C:/PR/worktrees/sfs/325/artifacts/pota325/juggeom/`.
- 326 pair harness (reference, laptop): `C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp`
  + `hpc/scripts/diag326.sh`; its run dir above shows the wiring.
- Touching pairs per the scorer's `Juglet_simple_graph.txt`: 1-2, 1-4, 1-8, 1-9, 2-5, 2-9, 3-5, 6-7, 7-9
  (3-7 is in the graph at 14.19 mm and does not touch; 6-9 is not in the graph).
- Fix-line tickets to read: `.scratch/pota-repro/issues/175-two-walks-two-slots.md`,
  `182-trace-new-edgeline-double-walk.md`, `210-swap-reseat-fresh.md`, `238-restore-good-edge-source.md`,
  `296-seat-a-pot-and-prove-the-interior-slot.md`; background `80-float-cause.md`, `81-swap-cure.md`.
