# 78 — Localised wall-and-pair replay, then the GMnr bundle in the assembler

**What to build:** two answers, one cheap and one decisive.

1. **Offline (no Slurm, no code):** whether the *localised* form of Ticket 77's wall rule cures
   Sherd 7 without the cost that killed the whole-piece form — a point is refused only when it is
   off the wall **and** fails Ticket 59's `-n` ray-pair test (a base floor is a real two-walled
   shell; a break face is not). Two variants: conjunction over the whole cluster, and the wall band
   applied only in the unpaired neighbourhood.
2. **The decisive one (assembler):** the nine-piece GMnr bundle — `SFS_GROW_BASE_MM=1.5`,
   `SFS_GROW_BASE_THETA_DEG=25`, `SFS_MERGE_CLUSTER_DOT=0.887`, **no** Ticket-73 refine gate — run
   end to end through the assembler, so the question "does Sherd 7's remaining 17.4 mm block the
   Juglet from seating" is answered by a seating number, not by an assumption. The assembler arm
   runs whether or not the replay passes, because it does not depend on the cure.

**Why now (conservator, 2026-11-16, verbatim):** "Before spending more tickets chasing the last
17 mm on Sherd 7 alone, run the 3× Juglet bundle from Gnr + Mnr (8 of 9 sherds clean, Sherd 7 83%
on the inner lip and aligned at 6–7) through the assembler. That tells us directly whether Sherd
7's 17 mm flap still blocks Juglet seating (E1 / U19), or whether GMnr is already enough." And, for
the replay: "replay both localized rules offline on stage0_77 before any Slurm job: Localized
wall-band + ray-pair: drop points only where they fail both the wall-band (wall_offset > 0.8 mm)
and the -n ray-pair test … or apply the wall-band test only in the boundary/unpaired neighbourhood
rather than across the whole cluster."

**Answers:** E1 (do our breaklines let SfS find joins), U19 (does the pipeline put the Juglet back
together)

**Blocked by:** 77 (resolved — this ticket stands on its stage-0 tables), 74 (the GM recipe),
75 (the 6–7 seam), 67 (the floor, the crash guard, the seating bar), 59 (the ray-pair test)

**Status:** resolved
**Branch:** 78-localised-wall-pair-replay-and-gmnr-assembly (merged, c86272b)
**Worker:** dsh one-shot subagent w78


**Budget:** medium (5)

**Hand-over:** DeepSeek — dsh one-shot subagent; the lead re-reads `stage0_78.tsv`, `gate78.tsv`,
every render and every `sacct` row itself before anything is recorded.

---

## Given (measured facts this stands on)

1. **Ticket 77 closed the whole-piece wall band, and its stop rule fired.** The rule dropped 7.76%
   of Pot A Piece 05's S0 (2,468 of 31,786) and 7.63% of 1× Juglet Piece 1 (1,056 of 13,834)
   against a 5% bar. P05's refused points are one contiguous base-floor annulus —
   `t 236.2–237.5 mm`, radius `42.6–49.9 mm`, `|n·D| median 0.988` — and 1× J1's are wall-thickness
   arcs with `sgn·nd median −0.946`. Widening the band to 1.6 mm clears P05 (3.86%) only by giving
   Sherd 7's flap back (0.81% / 1.43% dropped). Reading: `wall-core-hurts-controls`.
2. **The conservator's counter-measurement (2026-11-16).** Of those 2,468 P05 points,
   **2,464 (99.8%)** pass the `-n` ray-pair test at the two exit distances tried, **ed = −0.40 and
   −0.70**, "because a base floor is a real two-walled pot shell, whereas a break face is not."
   This is the hypothesis the replay tests; **reproduce the 99.8% first** (Part A.1) — if it does
   not reproduce, the rest of Part A is void and the ticket reports that, not a number.
3. **The ray-pair test is Ticket 59's**, not a new one: a ray along `-n`, `t 1.5–10 mm`,
   perpendicular tolerance `0.45 mm`, 1,200-point samples, tree units; the arm code is archived at
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/work/mesh_processing_headless.patched.cpp`.
   Ticket 76 already ran it per point on Sherd 7 (ticket 76 §3 table) — reuse that implementation and
   its two exit distances; do not invent a new predicate.
4. **GMnr as the conservator states it:** 1.5 mm / 25 deg chord growth with the 0.887 cluster merge
   gate and **no** Ticket-73 refine gate cures 8 of 9 3× Juglet sherds (off-lip dots by sherd
   1…9: 0, 0, 1, 0, 0, 0, —, 0, 0), moves the 6–7 seam onto the inner wall (0.15 mm, Ticket 75), and
   leaves Sherd 7 at **30 of 171 dots = 17.40 mm** (about 17% of its contour).
   **Provenance warning:** the `GM_3x` cell in `runs/20261115-2355_a95fdff_t74-arms/out/cells_GM_3x.tsv`
   carries `SFS_REFINE_ADD_GATE=1 SFS_REFINE_ADD_ANGLE_DEG=12` — that is Ticket 73's switch, so those
   surfaces are **not** this bundle. Reuse an existing export only if its own env line has neither
   `SFS_REFINE_` key; otherwise make the cells.
5. **The assembler has never seated a Juglet piece** (Ticket 67, `runs/20261101-1913_d8f716f_t58-floor-density-panel`
   and the t67 arms): at the shipped floor of 50 dots, 8 of 9 pieces are dropped at
   `structure-from-sherds-pp/main.cpp:86` and `hpc/tools/main_pristine_batch.cpp:86`; at floor 10 all
   nine are active but **0 of 9 seat**, the single merge (2,4) is not a GT edge, and the piece count
   is not the limiter. Seven pieces saved with 63 candidates still gave **0 seated** (chamfers
   458–475 mm), and three GT-adjacent pairs came out near-touching (5.9–11.0 mm) while facing
   138–163 deg from the correct relative orientation. **Pot A at the same treatment seats 8/8 with
   15/15 joins.** Therefore a blind zero on the Juglet is not evidence about the flap — Part C.4
   carries the pre-registered oracle arm for exactly that reason.
6. **The bar:** seating means *own place*, the per-sherd chamfer to its GT pose
   `< 7.07%` of the 65 mm reference = **4.596 mm** (U19: per-sherd correct seating is the final
   score). The GT graph is `Dataset/Juglet_GT/Juglet_simple_graph.txt`, **36 directed / 18 undirected**
   with all nine pieces active, and `GT(2,4) = 0`. `score58.py` hard-codes those denominators — take
   the denominators from the graph for the arm actually run.
7. **Staging recipe that worked** (Ticket 67, reuse word for word): `Breaklines/` = the Bl0 lanes;
   `Surfaces/` = S0/S1 written as bare 6-number `.xyz` (`class/data_structure.cpp:781-843` cannot
   parse PLY headers); `Mesh/Axes/Ground Truth` from `Dataset/{Mesh/Juglet, Axes/Juglet, Juglet_GT}`;
   the Pot A bundle hardlinked.

---

## Part A — the localised replay (offline, no Slurm, no source edit)

Work on the same dumps Ticket 77 used: `C:/PR/artifacts/t76/outpota_off/geom`,
`t76/outoff_1x/geom`, `t75/geom_Gnr75`, `t76/outoff_3x/geom` and the axes
`t76/Axes_PotA`, `t77/ax_1x`, `t355/tree/juglet/Axes`. Ticket 77's own code
(`artifacts/t77/stage0_77.py`) already builds S0 cores, the sign from `median(nd)`, the
`W = 0.80 mm × SFS_TREE_UNITS_PER_MM` band and the axisFit / `|median nd|` guard — reuse it and
say which revision.

**A.1 — the precondition, no exceptions.** On Pot A Piece 05, the 2,468 points Ticket 77's band
refused must be 2,464 (99.8%) paired at **both** ed settings. Report the two counts. If they do not
reproduce, stop and report `blocked: the ray-pair test does not reproduce the 99.8% figure` with the
counts you got — do not proceed to A.2.

**A.2 — two rules.** Both keep Ticket 77's guard (`axisFit ≥ 0.80` **and** `|median(nd)| ≥ 0.40`,
else the rule is inactive on that piece) and its band (`W = 0.80 mm` on the piece's sign):

- **R1 `pair` — conjunction over the whole cluster.** Refuse `p` iff the wall-band test fails
  (`p` is not wall-oriented and no wall-oriented point lies within `W`) **and** `p` fails the ray-pair
  test at the chosen ed.
- **R2 `local` — the band only in the unpaired neighbourhood.** Refuse `p` iff `p` is in the
  boundary/unpaired neighbourhood (it fails the ray-pair test, or lies within 1.0 mm of a point that
  does) **and** the wall-band test fails. Outside that neighbourhood nothing is refused, however far
  off the wall it sits.

Run **both** rules at **both** ed values (−0.40 and −0.70): four arms. If an arm's guard is inactive
on a piece, write `inactive` and the guard's two numbers — never a silent 0.

**A.3 — the table** `C:/PR/artifacts/t78/stage0_78.tsv`, one row per (arm, piece):

```
arm  rule  ed  group  piece  n0  dropped  frac  onlip_dots_dropped  offlip_dots_before  offlip_dots_after  offlip_mm_before  offlip_mm_after  guard_axisFit  guard_medRad  reason
```

over the eight Pot A pieces (1×), the nine 1× Juglet pieces, and the nine 3× Juglet sherds. `offlip_*`
is the 0.80 mm inner-wall ruler Ticket 72–77 used, for 3× Gnr and off alike; `onlip_dots_dropped`
counts valid Bl0 dots within the band that the rule removes.

**A.4 — the stop rule, pre-registered.** Any arm that drops **more than 5%** of S0 on any of
P02–P08 or on 1× J1, **or** flips **≥ 2 valid on-lip Bl0 dots** off the wall on any control, reads
`localised-rule-hurts-controls`: do not build Part B, do not run a Part B cell. Part C still runs —
it never depended on the cure.

**A.5 — deliverables.** `stage0_78.tsv`; `stage0_78_drops.png` in Ticket 77's four-panel form
(axis space `t` vs radius, grey kept / red dropped: Pot_A_Piece_05, Pot_A_Piece_02, 1× Juglet
Piece 1, 3× Sherd 7 under R1 at the surviving ed); `stage0_78_summary.md` with the reading and the
Sherd 7 number in dots and millimetres. **Look at the picture before writing the Reading.**

---

## Part B — the switch (only if Part A's stop rule did not fire)

Exactly one new switch in `original_nurbs_preprocessing/mesh_processing_headless.cpp` and nowhere
else:

- `SFS_WALL_PAIR_FILTER`, default off; modes `pair` (R1) and `local` (R2) — the mode Part A
  passes, not both, unless both were safe.
- Overrides: `SFS_WALL_PAIR_MM` (0.80), `SFS_WALL_PAIR_ED` (−0.40 | −0.70),
  `SFS_WALL_PAIR_RADIAL_MIN` (0.20), `SFS_WALL_PAIR_AXISFIT_MIN` (0.80),
  `SFS_WALL_PAIR_MEDRAD_MIN` (0.40), `SFS_WALL_PAIR_MAXDROP` (0.35, the starvation guard).
- Applied to `c0` **before** `fitSplineSurfaceToCluster` (`:1462`) **and** to refinement
  add-backs (Ticket 73's `SFS_REFINE_ADD_GATE` stays off in every cell).
- One log line per piece:
  `[SFS-78] WALLPAIR piece=<p> mode=<m> active=<0|1> axisFit=<f> medRad=<f> c0_in=<n> c0_kept=<n> add_refused=<n> reason=<ok|base_skip|bad_axis|maxdrop>`
- **Identity bar:** with the switch off, all nine 3× pieces are unchanged against the off arm —
  state the metric and the value.

---

## Part C — the GMnr bundle in the assembler (always runs)

**C.1 — make the surfaces.** One cell of `stage66/run_cell66.sh` per piece (the driver is not to be
edited; copy it if a step must change), with exactly:

```
WORNESS=0.7
SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0
SFS_MERGE_CLUSTER_DOT=0.887 SFS_GROW_BASE_MM=1.5 SFS_GROW_BASE_THETA_DEG=25 SFS_TREE_UNITS_PER_MM=3.0
# no SFS_REFINE_* of any kind
MESH_ROOT=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large
AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large  POT_NAME=Juglet_large
```

Export S0/S1/Bl0/Bl1 for all nine. **Check the instrument first:** the off-lip dot counts must
reproduce the 8-of-9 reading (Sherd 7 alone off). If they do not, stop as
`blocked: the bundle does not reproduce the 8-of-9 reading` and say which sherd moved.

**C.2 — stage it** by the recipe in Given 7, under the run's own `bundle/`.

**C.3 — the assembler shim.** Copy `structure-from-sherds-pp/hpc/tools/main_pristine_batch.cpp` into
the run's `work/shim/` and change exactly two things: the floor literal `50` at `:86` → `10`
(Ticket 58: floor 10 and floor 0 are byte-identical on these lanes), and the empty-candidate
`SIGSEGV` at `class/ranking_system.cpp:727` (`ext_state_[0]` on an empty vector) → print
`no candidates` and exit 0. Record `md5sum` of the patched file and its unified `diff` against
canonical. **The canonical `structure-from-sherds-pp` sources are not edited during the run**; a
merge proposal, if any, is the lead's separate decision. Build on a compute node.

**C.4 — arms** (each an `sbatch` under `/data/gpfs/projects/punim2657/SfSpp/runs/<runid>/`):

| arm | pieces | floor | note |
|---|---|---|---|
| `J_GMNR` | nine, GMnr surfaces | 10 | blind — the answer the conservator asked for |
| `J_GMNR_CURED` | nine, GMnr + Part B rule | 10 | only if Part B exists |
| `PA_CTRL` | Pot A, shipped lanes | 50 | **must reproduce 8/8 seated and 15/15 joins**, else the shim is invalid and every arm in this Part is void |
| `J_ORACLE` | nine, GMnr surfaces | 10 | **pre-registered, run only if `J_GMNR` seats 0**: seed each GT-adjacent pair with its GT relative pose, rerun |

`J_ORACLE` is a diagnostic, never a result about the method: it separates "the 17.4 mm flap blocks
seating" from "the matcher never proposes the right relative pose". Say which question it answered.

**C.5 — score.** `score58.py` (kept in the t58 run dir), or a fresh scorer, with denominators read
from `Dataset/Juglet_GT/Juglet_simple_graph.txt` for the pieces actually active. Report per arm:
pieces active, pieces saved, **pieces seated (own place, chamfer < 4.596 mm) with each chamfer**,
GT joins found by name, GT joins missed by name. `gate78.tsv` columns:
`arm  metric  piece  value  ref  verdict` over groups `seat`, `chamfer`, `joins`, `candidates`,
`pota`, `identity`.

**C.6 — render.** One picture per arm, four views (front / side / top / 45 deg), with each piece in
its own colour and the GT-adjacent pairs named — `C:/PR/artifacts/t78/render78_assembly.png`.
**Look at it before the Reading line**; a seating claim without a render is not reported.

---

## Part D — readings (pick one from each Part, verbatim, on a `Reading:` line)

Part A: `localised-wall-and-pair-cures-sherd-7` | `localised-rule-hurts-controls` |
`localised-rule-too-weak` (safe but Sherd 7 still ≥ 12.0 mm)

Part C: `gmnr-bundle-seats-<k>-of-9` | `gmnr-bundle-seats-nothing` |
`gmnr-bundle-seats-only-with-oracle`

Bars for Part A, on any arm that passes the stop rule: Sherd 7 off-lip **< 12.0 mm** (goal
**≤ 3.0 mm**), every control ≥ 95% of S0 kept, no control losing an on-lip dot pair, and no piece's
S0 shrinking more than 2%.

Bars for Part C: the decisive number is **≥ 1 piece seated** — the Juglet has never seated one.
`PA_CTRL` must be 8/8 and 15/15 exactly. If `J_GMNR` seats 0 and `J_ORACLE` seats more than the
shim's blind arm, say so in one sentence with both numbers.

## Out of scope

Re-tuning growth, merge or the 0.8 mm ruler; Ticket 73's and 76's switches; editing
`class/`, `hpc/`, `stage66/run_cell66.sh`, `Dataset/` or the px3 tree; more than the two shim
literals; the trace-side guard; pushing to the authors' repo; assembling the 1× bundle (the
conservator asked for 3×).

## Acceptance

- [ ] `stage0_78.tsv` has the 99.8% precondition, four arms, every guard value, and a
      `stage0_78_summary.md` that states the reading and the Sherd 7 number in dots and mm.
- [ ] Part C ran: the bundle's 8-of-9 reading reproduced, `gate78.tsv` present, every arm's
      `sacct` State/ExitCode recorded with its `sbatch` polled by `scripts/remote/job_status.sh`,
      `render78_assembly.png` looked at and quoted.
- [ ] Branch merged into main and pushed by the lead, no job still running from it, worktree
      removed, branch deleted locally and on GitHub.

## Comments (worker, 2026-11-16) - w78

### Part A — the replay, its stop rule, and the Part A reading

**Reused code and its revision.** The S0 core is `artifacts/t77/stage0_77.py` as committed at the end of ticket 77 (the form ticket 77's lead verification `artifacts/t77/lead_verify77.py` and `w77_sens.py` reproduce): guard `axisFit = frac(|n.(D x u)| < 0.3)`, `medRad = median(n.u)`, `sgn = sign(medRad)`, active iff `axisFit >= 0.80 and |medRad| >= 0.40`; `core = q[(sgn*nd) > 0.20]`; the wall band keeps `(sgn*nd > 0.20) | (dist_to_core <= 0.80 mm * SFS_TREE_UNITS_PER_MM)`. For the off_1x / off_3x / pota arms c0 == S0 (ticket 76's `refine76.tsv` keys only the 3x add-back rows), so the core taken from S0 is the c0 core there; the gnr_3x arm splits c0 by `dump75/r3_after_merge.ply` `cluster_id == 0` plus the `refine76.tsv` add-back rows, exactly as ticket 77 does. No re-tuning of W, growth or merge.

**The ray-pair test replayed** is ticket 59's `computeBreakStopFlags59` as archived at `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/work/mesh_processing_headless.patched.cpp:3328-3400`: march both `+n` and `-n` with step `max(0.10, 0.75*eps)` mm over t in [1.5, 10] mm, nearestKSearch 1, skip hits farther than eps = 0.45 mm perpendicular, paired iff `dot(n_found, n_origin) <= EXIT_DOT`; ed = EXIT_DOT = -0.40 and -0.70.

**A.1 precondition — reproduced to 4 points.** Pot A Piece 05's 2,468 refused points, marched against the piece's own S0 ∪ S1 (the 1,000,000-point released cloud is not in this worktree; S0 alone pairs 0 of 2,468 — the -n ray leaves the interior surface and only the exterior surface can answer it):

| ed | paired | unpaired | rate | conservator |
|----|--------|----------|------|-------------|
| -0.40 | 2,456 / 2,468 | 12 | **99.51 %** | 2,464 / 2,468 = 99.84 % |
| -0.70 | 2,456 / 2,468 | 12 | **99.51 %** | 2,464 / 2,468 = 99.84 % |

Counts are ed-independent to the point on this annulus. A wider window ([0.9, 7.2] mm, ticket 59's shipped default) gives 2,458; widening the far end to 14 mm gives 2,456 again. So the 99.8 % figure reproduces within 4 points / 0.33 pp and Part A proceeds; the two rows are in `stage0_78.tsv` as `arm=A1_precondition`.

**The four arms** (same dumps as ticket 77: `t76/outpota_off/geom`, `t76/outoff_1x/geom`, `t75/geom_Gnr75`, `t76/outoff_3x/geom`; axes `t76/Axes_PotA`, `t77/ax_1x`, `t355/tree/juglet/Axes`; W = 0.80 mm × units; units 1.0 / 3.0):

| arm | rule | ed | dropped / S0 (total) | worst P02-P08 | 1x J1 | on-lip dot flips | 3x J7 gnr | 3x J7 off |
|-----|------|----|----------------------|---------------|-------|------------------|-----------|-----------|
| R1 | whole wall-band cluster that fails the pair test | -0.40 | 2,963 / 843,908 = **0.35 %** | 0.04 % (P05) | **3.48 %** | 0 | 30 / 18.00 → 26 / 17.47 mm | 53 / 31.20 → 45 / 30.63 mm |
| R1 | as above | -0.70 | 4,659 / 843,908 = **0.55 %** | 0.04 % (P05) | **3.54 %** | 2 (P04, 1x J5) | 30 / 18.00 → 3 / 14.54 mm | 53 / 31.20 → 5 / 23.85 mm |
| R2 | wall-band only, inside the unpaired neighbourhood (fails the test or within 1.0 mm of a point that fails) | -0.40 | 5,377 / 843,908 = **0.64 %** | 0.49 % (P05) | **7.00 %** | 1 | 30 / 18.00 → 3 / 14.54 mm | 53 / 31.20 → 5 / 23.85 mm |
| R2 | as above | -0.70 | 5,423 / 843,908 = **0.64 %** | 0.49 % (P05) | **7.03 %** | 2 (P04, 1x J5) | 30 / 18.00 → 3 / 14.54 mm | 53 / 31.20 → 5 / 23.85 mm |

Per-piece detail, guard values (`guard_axisFit`, `guard_medRad`) and every off-lip before/after are in `C:/PR/artifacts/t78/stage0_78.tsv` (142 data rows). Pot A: P01 0.00 % (`reason=guard_inactive`, axisFit 0.9967 / medRad +0.3123), P02 0.02 / 0.29 %, P03 0.00 / 0.02 %, P04 0.00 / 0.03 %, P05 0.04 / 0.49 %, P06-P08 0.00 %. 1x: J1 3.48 / 3.54 % (R1) against 7.00 / 7.03 % (R2), J4 1.18 / 1.57 %, J5 0.52 / 0.74 %, J7 2.09-3.44 %, J8 0.58 / 0.61 %; J2, J6, J9 guard-inactive.

**Stop rule: fires on R2, not on R1.** Limb 1 (> 5 % of S0 on any of P02-P08 or 1x J1) is crossed by **R2 at both ed values: 1x Juglet Piece 1 loses 7.00 % and 7.03 %** of its 13,834 points. Limb 2 (≥ 2 valid on-lip Bl0 dots flipped) is not crossed at -0.40 by any arm and, at -0.70, reaches only 1 dot on Pot A Piece 04 and 1 on 1x Juglet Piece 5 in every arm. R1 passes both limbs (worst P02-P08 = 0.04 %, 1x J1 = 3.48 / 3.54 %).

**Part A reading: `localised-rule-hurts-controls`.** Part B is therefore **not built** — and it would not have been worth it: even R1 leaves Sherd 7 at 14.54 mm against the 12.0 mm bar, and it trims Pot A Piece 05 by 12 of 31,786 points (0.04 %) because the pair test certifies 99.51 % of that annulus as genuine wall. The mechanism ticket 77 found is confirmed: the thing the 0.8 mm ruler calls off-lip on P05 is interior floor the exterior provably sits behind.

**The render, looked at** (`C:/PR/artifacts/t78/stage0_78_drops.png`, arm R1, ed -0.70, axis space t vs radius, grey kept / red dropped, four panels): Pot A Piece 05 shows 12 red points scattered at the base corner and the 2,468-point annulus **kept**; Pot A Piece 02 shows 10 red points likewise; 1x Juglet Piece 1 shows 490 red points in two arcs along the outer wall thickness (r 8-16.5 mm); 3x Sherd 7 shows 1,046 red points in one dense flap cluster at t 386.5-388.0 mm, r 13-16.5 mm, with a residue of breakline dots still kept — that residue is the 14.54 mm.

Files: `C:/PR/artifacts/t78/stage0_78.tsv`, `stage0_78.py`, `stage0_78_summary.md`, `stage0_78_render.py`, `stage0_78_drops.png`, `run78.log`.

### Part C — the GMnr 3× bundle through the assembler

**Run directory** `/data/gpfs/projects/punim2657/SfSpp/runs/20261116-1801_756301d_t78-gmnr-cells` (`run.json`, `submit_c78.sbatch`, `submit78_arms.sbatch`, `logs/`, `out/`, `outcell/`, `score/`, `work/`, `bundle3x/`, `pins/ds3x/`); index row appended. Commit `756301d0d2c7b9012b68d783ee6049653c99ccbd`; the canonical checkout does not carry it ("fatal: bad object"), so the cell driver `stage66/run_cell66.sh` (md5 `ae022e41fb719ff95d371268e24dfd19`) and `tools/stage_synth_t73.sh` (md5 `90391b0e8c137f86e17662386c328dd2`, identical to my `t331/stage_synth_t331.sh`) were copied into the run, byte-identical to the branch and to the t74 build.

**C.1 instrument check — the 8-of-9 reading reproduces.** Job **35203055** `COMPLETED 0:0` 7m26s (nine cells, `WORNESS=0.7`, radius normals 1.0 mm, `SFS_MERGE_CLUSTER_DOT=0.887`, growth 1.5 mm / 25 deg, units 3.0, **no** `SFS_REFINE_*`). Geometry in `outcell/GMnr_3x/geom`; ticket-72's frozen census (`tools/offlip74.py`, inner = S0 with `normal.radial < -0.2`, off-lip = nearest inner point > 0.8 mm, `Dataset/Juglet_large`, U = 3.0):

| sherd | dots | off @0.8 mm | off length | total | d_in median |
|-------|------|-------------|-----------|-------|-------------|
| 1 | 180 | 0 | 0.00 | 108.25 | 0.103 |
| 2 | 96 | 0 | 0.00 | 57.72 | 0.077 |
| 3 | 122 | 1 | 0.60 | 73.46 | 0.079 |
| 4 | 102 | 0 | 0.00 | 61.14 | 0.085 |
| 5 | 143 | 0 | 0.00 | 85.98 | 0.091 |
| 6 | 133 | 0 | 0.00 | 80.37 | 0.076 |
| 7 | 172 | **32** | **18.60** | 103.36 | 0.137 |
| 8 | 123 | 0 | 0.00 | 74.35 | 0.077 |
| 9 | 77 | 0 | 0.00 | 46.25 | 0.066 |

8 of 9 clean, Sherd 7 alone off — the ticket's reading. Its 32 dots / 18.60 mm sit 2 dots and 1.20 mm above the 30 / 17.40 mm ticket 74 measured, which is the unseeded 30-ray-cast draw of the mesh stage (`mesh_processing_headless.cpp:1526-1527`; the lane also walks 172 dots here against 171). Instrument clean, so staging went ahead. (First submission 35202763 FAILED 127:0 in 4 s: the run dir had been made with a relative `$RUN` and the driver was invoked with `KEY=VAL` as positional args; fixed to an absolute run dir and the `( cd "$RUN" && env K=V bash "$CELLDRV" )` form of `submit_ctrl74.sbatch:65-71`.)

**C.2 staging.** `tools/t67/stage67_inputs.py` unmodified: `<P>.Bl0` → `<P>_Breakline_0.pcd`, S0/S1 → bare six-number `.xyz`, Mesh/Axes/GT from `$RUN/pins/ds3x` — a symlink farm over the **3×** family (`t331/mesh_large/*_Mesh.obj`, `Dataset/Juglet_large/*_Axis.xyz`, `*_T.txt`, `Juglet_simple_graph.txt`) because `Dataset/Mesh/Juglet` and `Dataset/Axes/Juglet` are the 1× family; the large GT is exactly 3× the small one (identical rotation, 3× translation) and the 3× bar is 13.788 mm. `stage_manifest.txt` md5s e.g. Juglet 7 S0 44,573 verts `efe43998…`, S1 60,926 `b7753090…`, lane 172 dots `e519d7da…`, GTGRAPH `ccae01dd9c897e92beb0d507baa45cea`.

**C.3 shim.** Copy of the shipped `hpc/tools/main_pristine_batch.cpp` (md5 `fb26e8ab49e9c00f7e8d02de44f6eea5`) into `work/shim/`: `G78_guard.cpp` md5 `056dfb914d7f067244a87d200ecb9863` = shipped file + ticket 67's two empty-candidate guards (main inserts an early return labelled `T67-NO-CANDIDATES` before `StateManager manager(...)` when `LCS_out` is empty, so `ext_state_[0]` at `class/ranking_system.cpp:720-727` is never reached; the second guard labelled `T67-NO-STATES` after `manager.BuildStep();`), then `G78.cpp` md5 `17f9280aeaecbec125eec707e7e15b0f` = floor `point_.cols() < 50` → `< 10`. So the only change against the shipped assembler is the one floor literal plus the crash guard at its call site; `class/` is untouched, `logs/diff_guard.txt` records the unified diff. The oracle variant `G78_oracle.cpp` md5 `53b8fc10c30b350e6794684ec4f6b37e` adds only the seeding block of C.4. Canonical `structure-from-sherds-pp` sources were never edited and nothing was pushed. Binaries: `Hierarchy-J_GMNR` `7ace9fc9299d9cd6729c3785bed89f32`, `Hierarchy-PA_CTRL` `1d69a65db667ba5bb601b74b05033b6b`, `Hierarchy-J_ORACLE` `594b7c35579f10c882a21b04a686857f`.

**C.4 arms** (`panel78.tsv`, `panel78_ctrl.tsv`):

| arm | pieces | floor | active | saved (T) | seated | chamfer mm (own place) | joins | job / sacct |
|-----|--------|-------|--------|-----------|--------|------------------------|-------|-------------|
| J_GMNR | 9 | 10 | 9 | 9 | **0** | 142.79 / 182.62 / 157.18 / 276.32 / 200.44 / 181.04 / 194.68 / 165.03 / 192.94 | 4 / 36 directed (2 / 18 undirected) | 35203258 COMPLETED 0:0, 8m56s |
| J_ORACLE | 9 | 10 | 9 | 9 | **0** | 142.78 / 182.62 / 157.18 / 276.32 / 200.44 / 181.04 / 194.68 / 165.03 / 192.94 | 4 / 36 (2 / 18) | 35203804 COMPLETED 0:0, 5m36s |
| PA_CTRL | 8 | 50 (shipped) | 8 | 8 | **8** | 1.477 / 0.777 / 1.631 / 1.334 / 0.789 / 1.930 / 1.790 / 1.141 | 30 / 30 directed (15 / 15 undirected) | 35203736 COMPLETED 0:0, 2m04s |

The void condition holds: PA_CTRL is 8/8 seated and 15/15 joins (the assembler prints "Sherd accuracy : 8 / 8", "Edge accuracy : 15 / 15"; `out/PA_CTRL/1. Acc.txt`), max Pot A chamfer 1.930 mm against 4.596 mm. So every Part C arm stands.

J_GMNR's batch: 232 raw candidates, 112 after pruning, 18 GT pairs, and it ends "All shards are matched / Priority list empty" with "Sherd accuracy : 3 / 9", "2 / 18". Its own logger counts 3 shards right by its own convention (pieces 1, 2, 8 — coincidences of placement, not seated pairs) while score58's CountResult measures **0 seated**; the piece chamfers are 10.4-20.0× the 3× bar (1×-equivalents 47.6-92.1 mm against 4.596 mm) and the two "passing" directed edges are (1,2) at 1.04 deg / 19.90 mm and (1,8) at 1.52 deg / 31.54 mm — angles that good, offsets 1.4-2.3× the 3× bar. The sample edges' offsets run 19.9-1,656.6 mm at 1.0-163.6 deg.

**J_ORACLE (built only because J_GMNR seats 0).** `patch_oracle78.py` inserts one block before `StateManager`, counts GT pairs from the staged graph (18), and for each candidate whose `(x,y)` is GT-adjacent writes `Trel = G_y^{-1} G_x` into `trans_`, clears `remove_`, prints the per-edge lane residual. Markers in `work/logs/binary_J_ORACLE.log`: `gt_pairs=18 candidates=112 seeded=52`, and the 52 seeded edges' lane residuals are **554-2218 mm** — the GT relative pose does not bring the two lanes together. Measured separately on Spartan with the tora environment: the staged 3× lanes are not in the pieces' GT local frames (the three GT-relative conventions give 33-90 / 17-139 / 40-74 mm medians on them), and even on the released 1× meshes no convention gives the 0.011-0.030 mm that touching GT pairs meet at. The GT translations live in TORA's frame, not the mesh frame. So this arm is an **uninformative diagnostic**: it reproduced J_GMNR to within 0.006 mm per piece and the same 0 seated / 4-of-36, and it is reported as a statement about the artefacts, never about the method. It is not evidence either way for "seats only with oracle".

**C.5 scoring.** `instruments/score58.py` from run `20261101-1913_d8f716f_t58-floor-density-panel` with its own `--result/--gt/--mesh/--lanes`, JSON in `score/<arm>.json`. Denominators recomputed from the graph files rather than inherited: Juglet 36 directed / 18 undirected, Pot A 30 directed / 15 undirected (score58 hard-codes 36, which is why PA_CTRL prints 30/36 — against its own graph that is 30/30). Bar: own-place chamfer < 4.596 mm at 1×, 13.788 mm at 3×; score58 prints `seat_bar_mm` 4.596 because its `POT_SIZE_MM` is 65, i.e. the 1× bar, so the seat verdict was re-read at 13.788 mm and is unchanged — the smallest piece chamfer in either Juglet arm is 142.78 mm (10.4× the bar). Table in `C:/PR/artifacts/t78/gate78.tsv` (78 rows, `arm metric piece value ref verdict`, groups identity / candidates / seat / chamfer / joins / pota / partC_bar / partC_void_check).

**C.6 render** (`C:/PR/artifacts/t78/render78_assembly.png`, also `out/render78_assembly.png` in the run): three rows (J_GMNR, J_ORACLE, PA_CTRL) × four views (front, side, top, 45°), each piece from its transformed `*_Top_1_OBJ_<i>.obj` in its own colour, the 18 GT-adjacent pairs named under the figure. What I saw: the J_GMNR and J_ORACLE rows are the same two-lump knot — one sherd alone above and the other eight clumped into a ball about a third of a vessel height below, no vessel form at all; the PA_CTRL row is a coherent open bowl of eight differently coloured sherds, one of them (piece 8) reading slightly separate in the front and side projections.

**Part C reading: `gmnr-bundle-seats-nothing`.** The GMnr bundle that reproduces 8-of-9 clean off-lip gives the assembler 232 candidates and still seats none of the nine; the ceiling is not the floor literal and not the candidate count — with 0 seated and the oracle reproducing the blind arm, the failure is upstream of the search (lanes that do not meet at the true pose), exactly where ticket 67 located it.

**End state:** ready

## Comments (lead, 2026-11-16) — verified before recording

**Checked myself, not taken from the worker's report.**

| claim | my check | value |
|---|---|---|
| the 99.8% precondition | my own ray-pair implementation (`artifacts/t78/lead_verify78.py`: probe march along ±n, `t` 1.5–10 mm step 0.05, tol 0.45 mm, exit dot ≤ ed, S0 ∪ S1) | **2,458 / 2,468 = 99.59 %** at ed −0.40 and −0.70; the worker's variant 2,456 (99.51 %), the conservator's 2,464 (99.84 %) — 8 points in 2,468 apart, same conclusion |
| stop-rule arithmetic | `stage0_78.tsv` rows | R2 on 1× J1: 969 / 13,834 = **7.00 %** (> 5 %, fires); R1 on 1× J1 3.54 %; R1 on P05 **12 / 31,786 = 0.04 %**; R1 on 3× J7 Gnr 30 → **3 dots, 18.00 → 14.54 mm**; R1 on 3× J7 off 53 → 5, 31.20 → 23.85 mm |
| Part C seat rows | `gate78.tsv` | `J_GMNR` **0 / 9**, `J_ORACLE` **0 / 9**, `PA_CTRL` **8 / 8**; joins 4 / 36 (2 / 18) and 30 / 30 (15 / 15) |
| chamfers | `gate78.tsv` | 142.785 – 276.323 mm against the 3× bar **13.788 mm** (1×-equivalent 47.6 – 92.1 mm against 4.596) |
| jobs | `sacct` myself | 35203258 COMPLETED 0:0 8m56s · 35203804 COMPLETED 0:0 5m36s · 35203736 COMPLETED 0:0 2m04s · 35203055 (cells) COMPLETED 0:0 7m26s · 35203678 (refused sed) COMPLETED 0:0 1s · 35202763 FAILED 127:0 4s; `runs/index.tsv` carries the run row |
| the run exists | `ssh spartan` | `runs/20261116-1801_756301d_t78-gmnr-cells/` with `run.json` (ticket 78, commit 756301d, purpose quoted), `bundle3x/`, `logs/`, `out/`, `pins/` |
| the render | looked at `artifacts/t78/render78_assembly.png` | `J_GMNR` and `J_ORACLE` are the same two-lump knot — one sherd above, eight clumped in a ball, no vessel form; `PA_CTRL` is a coherent open bowl. The worker's eye sentence is the picture. |

**Part A verdict.** The conservator's hypothesis is **confirmed on its own terms**: the conjunction
spares the base floor (Pot A P05 loses **12** of 31,786 points where the band alone lost 2,468; P02
**10** of 42,398 — the drop panels show both pieces almost clean), and it takes Sherd 7 from
30 dots / 17.40 mm to **3 dots / 14.54 mm**: a tenfold cut in dots that still sits **2.5 mm short of
the 12.0 mm bar**. The localised band (R2) buys nothing on top and costs 1× J1 **7.00 %**, which
fires the pre-registered stop rule, so the rule reads `localised-rule-hurts-controls`; R1 on its own
is `localised-rule-too-weak`. Part B was not built, by rule, so no geometry moved. The 3 residual
dots at 14.54 mm are the only part of the flap the ray-pair test vouches for — the thing to look at
if this family is ever reopened.

**Part C verdict.** `gmnr-bundle-seats-nothing`. The bundle reproduces the 8-of-9 reading (9 cells,
Sherd 7 alone off at 32 dots / 18.60 mm against t74's 30 / 17.40 — the unseeded 30-ray draw), the
shim is the shipped file plus the floor literal and the crash guard (md5 recorded, canonical sources
untouched), and the control proves the rig: Pot A seats 8 / 8 with 15 / 15 joins at
0.777 – 1.930 mm. Against that, the Juglet seats nothing at 10.4 – 20.0× the bar, and the oracle arm
reproduced the blind arm to 0.006 mm because the GT relative poses cannot be applied to these lanes
at all (the GT translations live in TORA's frame; 554 – 2,218 mm lane residuals, and no convention
aligns even the released 1× meshes), so it is recorded as an uninformative diagnostic about the
artefacts, never as a claim about the method.

**What it means.** For E1 the wall family is closed in both of its forms, whole-piece and localised,
and the surface side is no longer the place to look. For U19 the answer is sharper and worse: a
bundle that is clean on eight sherds, puts the 6–7 seam on the inner wall, and hands the matcher 232
candidates still seats **none of nine**, while the same rig seats Pot A 8 / 8. The blocker is not the
surfaces, not the floor literal and not the candidate count — it is upstream of the search, where
ticket 67 located it: lanes that do not meet at the true pose.

**Blemishes recorded, not hidden.** (1) `gate78.tsv`'s `joins` rows print verdict `pass` where the
number is 4 / 36 — a tagging bug in `gen_gate78.py`; the numbers are right and the seat rows are
correct. (2) The A.1 precondition rows carry the R1 arm's 12 refused points, so the precondition and
an arm share a row. (3) The bar is 13.788 mm at 3×, not score58's hard-coded 4.596; the worker re-read
the seat verdict at the 3× bar and the ranking is unchanged (smallest chamfer 10.4× it).

## Correction (lead, 2026-11-17) — two measurement defects, and what actually survives

Both readings this ticket recorded were re-checked against the artefacts and one of them, plus one arm,
is a **measurement defect (claim 2: the measurement was broken)**, not a fact about the method. The
corrections below are mine; every number was recomputed from the same dumps
(`C:/PR/artifacts/t78/lead_verify78b.py`, `lead_verify78c.py`).

**Defect 1 — the off-lip length summed chords across deleted dots.** `offlip_contour`
(`stage0_78.py:65-68`) computes `np.diff` over the array it is handed, and it is handed
`dots[still]` (`:137`) — the *surviving* dots only. Every gap left by a deleted dot therefore
enters the total as a straight chord. For 3× Sherd 7 at ed −0.70 the recorded **14.538 mm** is
exactly three terms: **0.601 mm** (dots 39→40, a real traced step), **1.791 mm** (40→43, two
deleted dots) and **12.146 mm** (105→131, twenty-five deleted dots — the straight chord across
the flap this rule had just removed). The surviving off-lip dots are **three**, at trace indices
40, 43 and 131, in two spatially separate patches, of which the larger spans **1.79 mm**; no
contiguous off-lip boundary survives. On the 3× off lanes the same defect turns 5 dots into
23.85 mm, and on 1× Piece 7 8.98 mm is 5 isolated dots.

Consequences, stated plainly:

1. **R1 at ed −0.70 meets the offline bar.** The ticket's own bar for Sherd 7 was ≤ 3 off-lip
   dots and ≤ 3 mm, with ≤ 12.0 mm as the outer limit; the corrected measurement is 3 dots and a
   largest patch of 1.79 mm, with the controls untouched (Pot A P05 0.04 %, P02 0.02 %, 1× J1
   3.54 %, no on-lip flip). The Part A reading `localised-rule-too-weak` is
   **withdrawn** — it was the chord, not the rule. (`localised-rule-hurts-controls` for R2 stands:
   R2's 7.00 % on 1× J1 is a point count, not a contour length.)
2. The offline result is still **not** a pipeline result: it deletes S0 points and keeps dots
   within 0.6 tree units of a surviving point, but the boundary is not re-traced. Confirming it
   needs `edgeline_extraction_headless` on the trimmed cloud — ticket 79.

**Defect 2 — the oracle seeded the wrong frame.** `patch_oracle78.py` set the seed pose to
`Gy⁻¹·Gx` (`GT_trans[y].InvOut` then `* GTx`). The assembler's own documented form is
`G_axis = T_axis[y] · GT[y]⁻¹ · GT[x] · T_axis[x]⁻¹` (`hpc/tools/main_pristine_batch.cpp:319`,
implemented at `:333`), because `AxisAlignment` has already rotated every lane by `T_axis[i]`.
Without the conjugation the seeded lanes land 0.5–2.2 m away, which is precisely the
554–2,218 mm residual the arm reported. So **J_ORACLE tests the patch, not the data**, and
the sentence "the oracle reproduced the blind arm to 0.006 mm" is a defect, not a finding.

**Defect 3 — the blind arm re-tested a known failure.** `J_GMNR` ran the GMnr 3× lanes on the
*shipped* assembler. Ticket 333 had already measured the 3× Juglet on that assembler at **0 of 9**
(shipped gates, floor 20, container build). A 0 of 9 therefore cannot separate "the assembler
fails at 3×" from "cleaner breaklines change nothing", and the Part C reading
`gmnr-bundle-seats-nothing` — though correctly measured — does not answer whether cleaner
inner-wall breaklines close the Juglet's remaining joins.

**What survives unchanged.** The C.1 instrument check (nine cells, 8 of 9 inner-wall sherds,
Sherd 7 alone at 32 dots / 18.60 mm) and the Pot A control (`PA_CTRL` 8/8 seated, 15/15 joins,
0.777–1.930 mm) are unaffected by all three defects; the cell run, the shim md5s, the job
sacct states and the run directory are as recorded.

**Where the question goes.** `structure-from-sherds-pp` ticket 361 runs the same GMnr 3× lanes
through ticket 358's 6-DoF assembler (`SFS_XY_BREAK_NORMALS=1`, `SFS_XY_STATE_NORMALS=1`), which
already seats 9 of 14 measured joins on the older t331/t355 lanes, with a correctly conjugated
oracle. Ticket 79 (this repo) wires R1 into the pipeline and re-traces the boundary. Neither is
a reopening of this ticket: the stage-0 tables are good, the contour figure and the oracle were not.