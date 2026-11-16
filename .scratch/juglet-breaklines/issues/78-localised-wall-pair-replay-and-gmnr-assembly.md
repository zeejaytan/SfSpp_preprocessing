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

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** 78-localised-wall-pair-replay-and-gmnr-assembly, in /c/PR/worktrees/sfs/78
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
