# Ticket 325 — Make the axis finder scale-free, so a 33 mm vessel is not judged by pot-sized millimetres

**Status:** ready-for-agent
**Answers:** E1
**Depends on:** 324 (the shipped rule and the byte-identical reference set), 322 (the Juglet answer key)
**Blocks:** none
**Worker:** unassigned
**Budget:** large

> **In one line.** The axis finder's gates and its clearance prior are written in millimetres calibrated on
> pots whose walls stand 40-150 mm off their axis; the Juglet's true axis stands **3.5-15.3 mm** off the piece,
> so the gate that says "this is a wall, not a base" is *unsatisfiable* on all nine pieces and the prior
> actively pushes the ranking away from the truth. Make every length in that path a fraction of the piece's
> own size, prove the ten pots do not move by a byte, and then the Juglet is a real test instead of an
> out-of-range input.

## What is already known (verified by the lead, 2026-11-10; do not re-derive)

The shipped path finds the Juglet's axes but places nothing: **0/9 sherds, 0/18 joins** against
`Dataset/Juglet_GT` (ticket 323, arms F20K3; two repeats, identical). The 1.2x line rule of ticket 324 made
no difference there, and ticket 324's identity run proves the shipped code writes the same bytes as the
sets that produced that result.

**Measured now (this ticket's own starting evidence).** For each Juglet piece: the bounding-box diagonal of
its two breakline clouds, the orthogonal distance from its centroid to the *known-good* axis in
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`, and the largest point radius about that axis:

| piece | diag (mm) | centroid→true axis d_c (mm) | r_max (mm) |
|---|---|---|---|
| 1 | 62.68 | 3.50 | 20.81 |
| 2 | 27.87 | 14.56 | 17.75 |
| 3 | 32.31 | 14.60 | 18.13 |
| 4 | 31.31 | 14.90 | 17.75 |
| 5 | 41.35 | 13.11 | 18.14 |
| 6 | 38.75 | 13.85 | 17.83 |
| 7 | 43.56 | 4.53 | 16.66 |
| 8 | 33.93 | 13.90 | 17.96 |
| 9 | 23.06 | 15.27 | 17.17 |

All nine are **below the 25 mm floor** the finder applies to every candidate. For comparison, on 16 pot pieces
sampled from the ticket-305 lanes (Pots B and E, released axes): d_c = **40.1-104.6 mm** on a bbox diagonal of
84-179 mm — i.e. every pot wall sits four to eight times the Juglet's distance from its axis. (One pot piece,
`Pot_B_Piece_01`, sits at 2.1 mm — it is a **base** sherd, and the finder handles it by a different branch.)

**Where the absolute lengths are.** Every one of these is a hard number today:

- `sfs_axes/normalized.py:20` — `DEFAULT_CLEARANCE_MM = 25.0`, the floor.
- `sfs_axes/normalized.py:138` — `if d_c >= DEFAULT_CLEARANCE_MM: return False`, the first test inside
  `is_base_fragment`; the rest of that function is pot-scaled too: `r_base_thresh = 25.0` (:125),
  azimuth span 160 deg (:168), axial extent 15.0 mm (:171).
- `sfs_axes/normalized.py:183-202` — `worst_wall_normalized_cost(..., min_clearance_mm=DEFAULT_CLEARANCE_MM)`
  and, at :200-202, a penalty of `1000.0 * (min_clearance_mm - d_centroid)**2`. At the Juglet's true distance
  (13 mm) that term is about **1.4e5** — it dominates every other term in the score.
- `sfs_axes/potsac.py:176` — `MAX_CLEARANCE_MM = 250.0`, the ceiling.
- `sfs_axes/potsac.py:526-533` — `r_prior`: a knee at 30/40 mm, a falloff past 120 mm, and `0.01 * (knee - d)`
  below the knee. On a pot the true axis sits *past* the knee (40-105 mm), so this term is near zero; on the
  Juglet every candidate is below the knee, so the term rises monotonically with d_c and **prefers axes
  further from the piece** — the opposite of its purpose.
- `sfs_axes/potsac.py:542` and `:568` (cylindrical branch), `:587-588` (conical branch entry and
  `min_clearance_mm`), `:604-606` (`valid_cone` 25-110 mm, `valid_dish` 35-115 mm) — the same floor and
  ceiling, five more times.
- The tight path above them (`[POTSAC-UNION-NORMALIZED-TIGHT]`, `sfs_axes/potsac.py:~500-523`) needs the
  same audit; do not assume it is clean.

**The consequence to test, stated so it can be wrong:** on a 33 mm vessel the cylindrical gate cannot admit
the true axis, and the prior and the penalty push every kept candidate *outward*; so the Juglet's bad axes
are a scale defect in this layer, not a failure of the cost that ticket 322 fixed.

## The ask

Make the normalized union path **dimensionless in the piece's own size**, calibrated so that the ten pots make
exactly the same decisions as today, and then measure what that does to the Juglet. One scale, one rule, no
object-specific constants, and no exceptions for the Juglet or for base sherds.

Answer these, in this order:

1. **What is the right scale?** Candidates: the bbox diagonal, the current candidate's fitted radius, the
   rms radius of the piece about its own centroid, or the piece's overall size from the two clouds. State
   which one you chose and why it is the physically meaningful denominator for *each* of the terms above
   (they may not share one).
2. **What does each threshold mean on the pots?** For each absolute length, the fraction it becomes, and the
   margin it leaves on the 172 pieces (min and median of `d_c / scale`). A gate whose pot-side margin is
   barely above 1 is a gate that will flip; say so rather than tuning it.
3. **Does the same rule admit the Juglet's true axis?** Apply the rewritten gate to the nine key axes and
   report, per piece, `d_c / scale` and which test it fails, if any.
4. **What does the shipped finder produce then?** Rebuild the Juglet axes with the shipped path and score
   them against `Dataset/Juglet_GT` (direction error per piece, rank 0 and best-of-3).
5. **Does the Juglet assemble?** End to end, two repeats, with the key's own axes as a control arm.
6. **Is anything genuinely absolute?** The 15 mm axial extent, the 80-point minimum, the 160 deg span, and the
   `sz` draw-count thresholds are not obviously lengths. For each, either justify it against the noise scale
   (sensor resolution, breadline sampling) or convert it. Do not convert something because converting is
   easier — a rule that is about counting points is not a rule about millimetres.

## What would settle it (acceptance)

1. **Audit table** in the ticket: every absolute length in the normalized union path (file:line), what it is
   for, its dimensionless replacement, and the pot-side margin. Grep proof that no bare millimetre constant
   survives in a gate or a score on that path. The paper chain (`run_potsac`) is untouched.
2. **Byte identity on the ten pots.** One run of the shipped writer over the 172 pieces; `cmp` every file
   against `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323` (172 files,
   251 lines). **Any differing file stops the ticket**: report the piece, the gate or score term that
   flipped, and its margin. Do not nudge a threshold until it matches — that is fitting, and it would destroy
   the only independent check we have.
3. **Juglet admissibility**, from step 3 above: the true axis must pass the rewritten cylindrical gate on
   **all nine** pieces, and no piece may be classified as a base fragment by a wall axis. This is the
   mechanism test and it needs no assembly.
4. **Juglet axis quality**, from step 4: measure the shipped `axes323` baseline first and record it, then
   require **at least 7 of 9 within 10 deg at rank 0** and **all nine within 30 deg**. (Today's numbers are in
   ticket 323; re-measure rather than trusting this line.)
5. **Juglet end to end**, two repeats, best-of-N reported as best-of-N (never the median, and say how many
   attempts reached it): the new arms, **plus a control arm using `Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`
   directly**. That control is the point of this ticket's second half: if the *known-good* axes also seat
   nothing, the blocker is not the axes at all and the honest result is "the breaklines or the assembler's
   scale, not the axis finder" — report that, do not patch around it. Pre-register, before submitting, what
   you will call success (a purely geometric claim, e.g. ≥1 join seated and ≥2 pieces placed on both repeats).
6. **Ten-pot assembly unchanged**: A 8/8 15/15, B 9/9 15/15, C 4/4 5/5, D ≥ 23/28 ≥ 55/69, E ≥ 29/31 ≥ 57/62,
   F 5/5 7/7, G 7/7 10/10, H 11/11 17/17, I ≥ 25/26 ≥ 59/62, J ≥ 8/11 ≥ 16/21 — two repeats each, with job IDs
   and final `sacct` State/ExitCode in the ticket. (Byte identity in (2) makes this a confirmation, not a
   discovery; if it disagrees with (2), the run is telling you something and you must report it.)
7. **No corpus write.** `Dataset/` and `original_samples/` are inputs. List the corpus before and after.
8. **Renders** before/after for any geometry claim, into `SfSpp_preprocessing/artifacts/pota325/renders/`
   (gitignored), at a view that resolves a 30 mm vessel.

## What must not happen

- **Do not lower `DEFAULT_CLEARANCE_MM` globally.** 2 mm would admit every pot candidate and break (2).
- **No unit switch or "small object" flag.** A branch on object size is the per-object table this ticket
  exists to remove.
- **No assembler changes.** This ticket is about the axis finder's scale; if the control arm in (5) points at
  the assembler, that is a finding for the next ticket, not a licence to edit it here.
- **No millimetre constants justified by a pot.** If a number must stay absolute, justify it by the noise
  scale, not by "it worked on Pot D".

## Inputs and templates

- Shipped writer: `scripts/run_benchmark_172.py` (args `--cap 6 --seeds 10 --step 10`), CLI `sfs_axes/cli.py`.
- Reference set to match: `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323`.
- Ticket 324's identity run (the template for the writer job): `.../runs/20261110-1202_e94d8fb_t324-axes`.
- Juglet key + README: `/data/gpfs/projects/punim2657/Dataset/Juglet_GT/` (a second copy exists under
  `/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet_GT/`; keep them in step or use one).
- Juglet breaklines: `.../runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom` (9 pieces x S0/S1).
- Juglet E2E template: `.../runs/20261110-0320_41494d0_t320b-juglet/submit.sbatch` (SIF
  `sfs_main/sfs_pristine_assembly.sif`, `-DJUGLET_ORIG`, `juglet_orig_block.inc`, FLOOR=20, NP=9).
- Ten-pot E2E template: `.../runs/20261110-0740_d628fc0_t323-pot<X>/submit.sbatch`.
- Corpus caveats before scoring anything: `SfSpp_preprocessing/AGENTS.md` ("Corpus caveats").

## Constraints

- **Spartan compute nodes only** for the writer and every assembly job; the login node is for reading.
- **Two repeats** for any assembly; the assembler is not deterministic on identical input (Pot E gave
  30/31+57/62 and 31/31+62/62 from byte-identical staged inputs in one job).
- **One code path**, no per-object table, no Juglet special case.
- **No commits.** The lead reviews and commits; leave the tree with your changes in place and `git status`
  readable.
- Keep scripts, sbatch files and notes in `.scratch/pota-repro/t325/`; run directories go under the shared
  run root with the usual `<YYYYMMDD-HHMM>_<git7>_<tag>` name.

## Hand-over

Report: the audit table, the chosen scale and why, the byte-identity count (files compared / differing, with
the first differing file if any), the Juglet admissibility table, the Juglet axis errors per piece, the E2E
table for both arms and the control with job IDs and `sacct` states, the ten-pot confirmation, and the
renders. If byte identity fails, lead with that and stop.
