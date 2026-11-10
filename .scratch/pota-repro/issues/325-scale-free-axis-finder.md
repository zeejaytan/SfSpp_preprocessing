# Ticket 325 — Make the axis finder scale-free, so a 33 mm vessel is not judged by pot-sized millimetres

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-10)
**Branch:** 325-scale-free-axis-finder, in /c/PR/worktrees/sfs/325
**Answers:** E1
**Depends on:** 324 (the shipped rule and the byte-identical reference set), 322 (the Juglet answer key)
**Blocks:** none
**Worker:** session-e263b1ef-20fc-409f-9451-d643d578b11f (dsh one-shot subagent, qoder-global/dfmodel; dispatched 2026-11-10 by the lead; resumed from the rate-limited worker's worktree)
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

## Comments (lead, 2026-11-10)

**Why the lead is writing here.** Both dispatched workers died before reporting: `ea7da6de-bca6-4a5d-8530-9b63d7adaa09` (glm-5.3, stopped ~15:00) and `e263b1ef-20fc-409f-9451-d643d578b11f` (qoder-global/dfmodel, failed 15:58 — provider quota). Neither wrote a closing message, so this ticket has no worker report. The conservator's instruction is to continue without redoing finished work, so the lead is finishing the remaining bars and records them here, labelled as lead measurements. Nothing already produced is re-run: the worktree, the identity run 34648716, the measure run 34647797 and the two workers' submit scaffolding are reused as they stand.
Scratch-writer check (AGENTS.md rule 12) run 16:47 with `--quiet-for-hours 1`: every remaining sign is one of the two dead workers' files (newest 15:53:53, `t325/tmpl/potJ.sbatch`); no live writer.

### Bar 5 pre-registration (written before submitting, as the ticket requires)

Claim type: *the method's output is usable*, purely geometric — no reference answer is involved, so this cannot be a reference-is-wrong result.

- **Arms, K = 3 lines per piece, FLOOR = 20, NP = 9, two repeats each:**
  - `O` — `Dataset/Axes/Juglet` (our own September output, the shipped baseline);
  - `K3` — this ticket's axes, `runs/20261110-1450_22151d0_t325-axes/out/axes325`, top 3 lines per piece;
  - `GT` — `Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` used directly (the oracle control).
- **Success** = on **both** repeats, at least **1 of the 18 breakline joins seated** and at least **2 of the 9 pieces placed**. Partial success is reported per repeat, never averaged.
- **What each outcome will mean.** `K3` succeeds and `GT` succeeds: the axes are good enough to seat a 33 mm vessel. `K3` fails and `GT` fails: the blocker is downstream of the axis finder (breaklines or the assembler's scale), not this ticket's gates — reported as such, not patched around. `K3` fails while `GT` succeeds: the axis finder is the blocker, and the axis-error table says which pieces.
- **Baseline to beat, recorded before the run:** job 34623404 (`20261110-0740_d628fc0_t323-juglet`, axes323) scored **0/9 pieces and 0/18 edges on all four arms** — `score/acc.tsv`: F20O_r1 0/9 0/18, F20K3_r1 0/9 0/18, F20O_r2 0/9 0/18, F20K3_r2 0/9 0/18.

### Bar 2 — byte identity on the ten pots: PASS

Job **34648716** `t325-axes325` COMPLETED 0:0 in 00:04:16, run
`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes/out/axes325`.

- ours 181 files, reference 172 files: **IDENTICAL 172, DIFFER 0, MISSING 0**. The nine extra ours-only
  files are `Pot_JUGLET_Piece_01..09_Axis.xyz` — the Juglet, which is not in the 172-piece pot set.
- `for f in $A/*_Axis.xyz; do b=$(basename $f); cmp -s $f $R/$b; done` with
  A=`.../20261110-0740_d628fc0_t323-axes/out/axes323`, R=the axes325 out directory.
- The first attempt reported `MISSING-IN-REF` for every file: the submit script carried the reference
  path with the month typo `2026`**`10`**`10` instead of `20261110`. That was a path bug in the copied
  sbatch, not a code finding; fixed and re-run. Attempt-1 logs are kept under `logs/`.

### Bar 1 — audit table and grep proof

Measured on 485 rows (172 shipped axes323, 141 GT axes, 163 released axes, 9 Juglet GT) by
`artifacts/pota325/gate_stats.tsv` + `.scratch/pota-repro/t325/audit_margins.py`.

| old constant (file:line before) | what it did | dimensionless replacement (file:line now) | pot-side margin |
|---|---|---|---|
| `DEFAULT_CLEARANCE_MM = 25.0` normalized.py:20 | floor on centroid distance | removed; floor is now `u_clr = r_q01/r_mean >= 0.05` (`CLEARANCE_FLOOR_FRAC`, normalized.py:44) | min 0.0769 (Pot J 18) → **1.54x**; median 0.665 |
| `is_base_fragment` first test `d_c >= 25` normalized.py:138 | rejects base test far from the piece | removed; a far line now fails on the *count* of near points | n/a (count test) |
| `r_base_thresh = 25.0` normalized.py:125 | near-axis band for base points | `r < 0.75 * r_mean` of the same piece (normalized.py:197) | 20 base pieces, unchanged verdicts |
| azimuth span `160 deg` normalized.py:168 | base must wrap the axis | kept — an angle, not a length | unchanged |
| axial extent `15.0 mm` normalized.py:171 | base must carry depth | `z_extent >= 0.05 * D` (bbox diagonal, normalized.py:221) | base pieces min z_frac **0.0801** → 1.60x; median 0.153 |
| `1000*(25 - d_c)^2` normalized.py:200-202 | clearance penalty | `1000*(0.05 - u_clr)^2` on non-base pieces (normalized.py:258) | bites only when u_clr < 0.05, i.e. below every released wall |
| `d_c > 200`, `0.001*(d_c-200)^2` normalized.py:203-205 | far-decoy penalty | `v = r_mean/D > 2.5`, `10*(v-2.5)^2` (normalized.py:260) | released max v **2.0094** → 1.24x; one axes323 row at 2.5914 (0.96x) does not flip a decision — byte identity is the proof |
| `MAX_CLEARANCE_MM = 250`, r_prior knee 30/40, falloff 120, `valid_cone` 25-110, `valid_dish` 35-115 (potsac.py:176, 526-533, 542, 568, 587-588, 604-606) | the non-profile union regimes | rewritten to the same ratios (potsac.py:176-186, 500-523, 535-606) | **dead code on the live path**: `UNION_RANKER` defaults to `"profile"` (potsac.py:177) and `run_benchmark_172.py:73` calls `run_potsac_union(..., normalized=True)`, so only the profile ranker runs. Stated so nobody reads byte identity as validating these lines. |

Grep proof: every remaining `mm`/`_MM` hit in `sfs_axes/*.py` is prose (normalized.py:172, potsac.py:179,
profile.py:13, select.py:17). No code line in `sfs_axes/` carries a millimetre constant. `git diff --stat`:
normalized.py, potsac.py, tests/test_normalized.py. The paper chain (`run_potsac`,
`scripts/run_benchmark_172.py`) is untouched.

### Bar 3 — Juglet admissibility: PASS

Frame check first, because it decides whether the test means anything: the GT axis files are per piece, and
carrying each through its own `Juglet_Piece_N_T.txt` (`X_world = R*X + t`) collapses the nine onto one world
line — **0.002 deg direction spread, 0.000 mm line offset**. So an axis file and its piece are in the same
frame, and r, u_clr, z_frac are rigid-motion invariant. The test stands.

Per piece, from `.scratch/pota-repro/t325/diagnose_base.py` (implements the exact t325 bytes, md5
`1ee0f916c1282ee3c0de359e5e72b809`; job 34659026 COMPLETED 0:0): `u_clr` = 0.493, 0.890, 0.875, 0.835,
0.545, 0.846, **0.143**, 0.778, 0.898 for pieces 1-9 — all nine pass the floor (0.05) and the ceiling
(v <= 2.5), on all three axis sources (GT, axes325, axes323).

Base verdict: **only piece 7** is classified a base (near 3334 points, axial normals 0.903, azimuth span
358.0 deg, z_extent 0.494 of D). That is correct — piece 7 is the base (r_min to the true axis 0.14 mm).
No piece is called a base by a wall axis.

Control on the authors' own released axes, same shipped function, 163 pieces: 26 base verdicts (16%),
1-3 per pot. That is the physically expected rate, so the rule is not over-triggering at pot scale.

### Bar 4 — Juglet axis quality: FAIL

`.scratch/pota-repro/t325/score_axis_quality.py`, rank 0 = first line of each file. Direction error against
`Dataset/Juglet_GT`: **0.92, 13.16, 28.39, 3.44, 3.72, 1.84, 132.08, 3.05, 4.56 deg** (pieces 1-9).

- **6 of 9 within 10 deg** (bar asks 7), **8 of 9 within 30 deg** (bar asks 9). Piece 7 — the base, and the
  only piece that reaches the axis — is **132 deg out** (48 deg as a line).
- axes325 and axes323 are byte-identical files, so this is the baseline unchanged: the rewrite moved no
  Juglet axis. Most files hold one line (pieces 5 and 7 hold two, piece 9 three), so rank 0 and best-of-3
  are the same number here.

### Bar 5 — Juglet end to end: FAIL on the joins, PASS on the pieces

Job **34659057** `t325-juglet` COMPLETED 0:0 in 00:03:22, run `.../runs/20261110-1640_22151d0_t325-juglet`.
Six arms, two repeats each, 3 lines per piece, FLOOR 20, NP 9:

| arm | pieces | joins |
|---|---|---|
| GT_r1 (oracle axes) | **2/9** | 0/18 |
| GT_r2 | **2/9** | 0/18 |
| K3_r1 (this ticket) | 0/9 | 0/18 |
| K3_r2 | 0/9 | 0/18 |
| O_r1 (September axes) | 0/9 | 0/18 |
| O_r2 | 0/9 | 0/18 |

The control arm really carries the key: the staged `Axes/` files are md5-identical to `Dataset/Juglet_GT`
(e0f70a34...), the O arm to `Dataset/Axes/Juglet` (e0ba64c4...), the K3 arm to axes325 (2c6a6432... piece 1).

**Per the pre-registration, K3 fails and GT fails**, so the blocker is downstream of the axis finder:
the breaklines or the assembler's scale on a 33 mm vessel. That is the outcome the ticket anticipated in
writing (acceptance 5) and it is not patched around here.

What the control run actually did, measured rather than assumed: the eight placed OBJs sit at the input
poses. Placed bounding box **39.73 x 38.04 x 77.54 mm at (40.6, -4.5, -513.2)** against the input clouds'
38.63 x 37.02 x 77.41 at (40.3, -4.5, -513.2); piece 7's placed OBJ 22.89 x 27.05 x 26.09 at
(37.5, -6.4, -536.8) against its input 22.56 x 26.79 x 25.89 at (37.4, -6.5, -536.7). The assembler moved
nothing it was given: with the true axes it still returns the pieces as captured, 2/9 and 0/18.
(For comparison the same pipeline on Pot A seats 8/8 and 15/15, so this is not the assembler being broken
in general — it is the 33 mm scale.)

### Bar 6 — ten-pot assembly: PASS on every pot's stated number

**Attempt 1**, jobs **34659575-34659584**: all ten `FAILED` `6:0` within a minute of starting, with
`could not extract data_path.h`. The copied t323 template's shim extracts that header from a path that only
exists in the t323 run. Each run directory keeps `RUN-FAILED.txt` naming its jobid, rc and reason. This is a
template path bug, not a code finding; the shim was fixed (no axis code touched) and the batch resubmitted.

**Attempt 2**, jobs **34669184-34669193** (`t325-potA`..`t325-potJ`), all ten `COMPLETED` `0:0`
(00:01:03-00:52:19), run `.../runs/20261110-0552_22151d0_t325-pot<A..J>`, 4 arms each
(`MOR1`/`MOR2` = the authors' released axes, control; `K3R1`/`K3R2` = this ticket's chain),
`score/acc.tsv` written 18:46-20:08.

| pot | bar (acceptance 6) | K3 r1 | K3 r2 | authors' axes r1 / r2 | verdict |
|---|---|---|---|---|---|
| A | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 / 8/8 15/15 | PASS |
| B | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 / 9/9 15/15 | PASS |
| C | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 / 4/4 5/5 | PASS |
| D | >=23/28 >=55/69 | 26/28 63/69 | 25/28 60/69 | 23/28 55/69 / 23/28 55/69 | PASS |
| E | >=29/31 >=57/62 | 30/31 57/62 | 31/31 62/62 | 31/31 62/62 / 31/31 62/62 | PASS |
| F | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 / 5/5 7/7 | PASS |
| G | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 / 7/7 10/10 | PASS |
| H | 11/11 17/17 | 11/11 17/17 | 11/11 17/17 | 8/11 9/17 / 8/11 9/17 | PASS |
| I | >=25/26 >=59/62 | 25/26 59/62 | 25/26 59/62 | 25/26 59/62 / 25/26 59/62 | PASS |
| J | >=8/11 >=16/21 | 8/11 16/21 | 8/11 16/21 | 8/11 16/21 / 8/11 16/21 | PASS |

Against the t323 reference (`.../20261110-0740_d628fc0_t323-pot<A..J>/score/acc.tsv`) every pot matches
except three cells, all still above their bar: **D** K3 r2 26/28 63/69 -> 25/28 60/69; **E** K3 r1
31/31 62/62 -> 30/31 57/62; **H** authors'-axes r1 10/11 10/17 -> 8/11 9/17. Byte identity in bar 2 makes
this a confirmation, so a difference cannot come from the rewrite: it is the assembler's own
non-determinism on identical inputs, the phenomenon already recorded on Pot E (30/31 and 31/31 from
byte-identical inputs). The bar's H number, 11/11 17/17, is this chain's; the authors'-axes control is
8/11 9/17 on both repeats here and was 10/11 and 8/11 at t323 — that arm is weak at H either way, and it is
not the chain under test.

Corpus: `logs/corpus_inputs_before.md5` and `..._after.md5` are byte-identical in all ten run directories
(48, 54, 24, 173, 186, 41, 42, 66, 177, 71 input files per pot).

### Bar 7 — corpus: unchanged

`Dataset/` top level unchanged; the only entries newer than 2026-11-10 00:00 are `Juglet_GT/` and
`Dataset/Axes/Juglet` from tickets 322/324 (07:23, before this ticket's first job). Nothing under
`sfs_main/original_samples/SfS_pp` is newer than 2026-11-10 00:00.

### Bar 8 — renders

`C:/PR/worktrees/sfs/325/artifacts/pota325/renders/juglet-axes-and-assembly.png` — A the nine pieces at
their true pose (41 x 37 x 65 mm: body, neck, handle), B the assembler given the true axes (the capture
arrangement, 2/9 0/18), C down the vessel axis, D piece 7 with the true axis and the finder's.

### Lead verdict (2026-11-10, written after the ten pots landed)

Bars 1, 2, 3, 6 and 7 pass; bars 4 and 5 fail, and the failure is the informative part.

- **The rewrite is output-neutral.** `axes325` is byte-identical to `axes323` on all 172 pot pieces, and the
  nine Juglet files it wrote are identical to the ones the old code wrote. So on this evidence the millimetre
  gates were **not** what limited the Juglet's axes: the same lines come out of both versions.
- **Bar 4** (6 of 9 within 10 deg; piece 7, the base, 132 deg out — 48 deg as a line) is therefore the shipped
  finder's behaviour at 33 mm, not a regression introduced here and not something this ticket fixed.
- **Bar 5**: the oracle-axes control also seats 2/9 pieces and 0/18 joins, and the assembler returns the
  pieces at their input poses. Given the true axes it still cannot join the vessel, so the blocker on this
  object is downstream of the axis finder — which is what tickets 327/328 then found in the breakline filing
  (three pieces filed exterior-side, and line normals that flip sign inside one line).
- **Not merged to main yet.** The scale-free change is safe by bar 2, but bar 5 has to be re-measured after
  ticket 328 changes the breaklines; merging before that would record a Fail that a later run may not
  reproduce.
