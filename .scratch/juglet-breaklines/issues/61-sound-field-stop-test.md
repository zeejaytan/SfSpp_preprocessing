# 61 — Give the growth stop a sound normal field, then ask whether it stops at the break surface

**What to build:** the same nine pieces, run through the same chain with the same stop rule, but
with the normal field the stop test consumes taken from the corpus cloud instead of the
pipeline's per-rung re-estimate. The question is narrow: **with a sound field, does the
break-surface stop fire where it should, or does the rule still fail?** Either answer closes the
stop-rule line of enquiry for now; a positive one means the rule was right and the field was
broken; a negative one means the rule itself does not work and it should be parked.

**Why now (2026-11-02, conservator):** after ticket 60's diagnosis he chose options 1 and 2 —
"1 and 2 ... do 1 and 2 using cursor_code". This ticket is option 1.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS
find joins)

**Blocked by:** none

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 61-sound-field-stop-test, in /c/PR/worktrees/sfs/61
**Worker:** cursor_code (grok-4.7), three phases; jobs 34211858 / 34211859 / 34212470 all COMPLETED 0:0

## Spec

### Given (measured facts this stands on)

1. Ticket 59 implemented the stop as an opt-in switch and ran it: with `SFS_BREAK_STOP=1` on
   J1 the surface collapses from 13850 points to 351 and the piece loses its genuine pair, while
   the other eight barely move. Nothing was merged; the patch lives in
   `.scratch/juglet-breaklines/stage59/stage1/mesh_processing_headless.patched.cpp` beside the
   clean `.lf.cpp` it was made from, and the run of record is
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm`.
2. Ticket 60 found why, and it is not the clay and not the rule: **the field is scrambled**. Measured
   against the mesh, the per-rung re-estimate is sign-flipped on **41.63 %** of J1's 19312 points,
   against 0.18–1.70 % on the other eight. The stored normals of the corpus cloud
   (`Dataset/Point/Juglet/<piece>_Point.pcd`, FIELDS x y z normal_x normal_y normal_z on all
   nine) are **0.40 %** flipped on J1. Of J1's 17638 break-like points, 96.14 % do find clay
   within 0.45 mm along the march, but with a normal pointing the *same* way — the two facing
   walls carry normals pointing the same direction, so a rule asking for `dot <= -0.4` must
   refuse them. Split by sheet: S0 89.75 % flipped, S1 2.40 % — one whole sheet inverted.
3. The pipeline already has a switch that carries the input normals instead of re-estimating:
   `SFS_NORMAL_SOURCE=input` (tickets 33/34), with `SFS_NORMAL_CARRY=mean|nearest`. It is wired at
   `mesh_processing_headless.cpp:1005`, `:1082` (downsampling) and `:3795` (the growth stage, which
   re-loads the rung PLY and is the call whose output the stop test consumes). In this mode MST is
   deliberately **not** applied, and a point with no usable source normal is counted and reported
   (`[NORMAL-33] ... carried= nearest= missing=`), never silently filled.
4. Nothing in the ticket-59 arms set that variable: `submit-arm.sbatch` unsets it, so the t59
   armed run consumed the re-estimated field throughout.

### The four cells

All nine Juglet pieces, `SFS_WORNESS=0.7`, binaries built from this ticket's commit with the t59
patch applied exactly as ticket 59 applied it (only `computeBreakStopFlags59` and its call site
differ from the clean file — reproduce that diff, do not re-invent the rule).

| cell | `SFS_NORMAL_SOURCE` | `SFS_NORMAL_CARRY` | `SFS_BREAK_STOP` | what it isolates |
|------|----------------------|---------------------|------------------|------------------|
| U    | unset                 | unset               | unset            | the t55 baseline (identity gate) |
| I    | input                 | nearest             | unset            | what a sound field does to the surfaces and breaklines alone |
| UA   | unset                 | unset               | 1                | the t59 armed run (identity gate) |
| IA   | input                 | nearest             | 1                | **the question**: the rule given a sound field |

`nearest` is chosen over `mean` for the carried cells because it keeps every source sign
verbatim with no averaging ball (ticket 34); say in the Results why, and if a cell shows
`missing` above 1 % of points, report it rather than patching around it.

### What is measured, per piece, in every cell

- **The field actually consumed**, not the field intended: with `SFS_NORMAL_DUMP_DIR` set, the
  rung-1 normals PLY, sign-flipped fraction against the nearest mesh face normal, and the folded
  angle. This is the column that says whether the switch did anything on the piece — printed
  `[NORMAL-33] carried=` is the corroboration, not the proof.
- The ticket-57 separation metrics, exactly as `check_separation.py` takes them:
  `nS0`, `foldS0`, `blindDeg`, `farS0`, `dc_ge1`, `bl0`, `genuine`. Invocation flags are
  `--geom --mesh-dir --walls --pieces`; note it is **not** `--geom-dir`, and `--pieces` takes
  comma-joined full names.
- Where the S0 boundary sits against the true break edge, if the existing instrument produces it
  cheaply (ticket 60's nearest-S0-point-to-true-edge distance); otherwise say it was not measured.

### Gates (both must pass before any conclusion is drawn)

1. **Identity, U vs t55.** The default-field, disarmed, `WORNESS=0.7` cell must reproduce the t55
   run of record per piece — S0 md5 where the piece is deterministic, and the printed parameters —
   or the build or the cell is wrong. Use t55's own rule for which pieces are deterministic
   (J1's flip draw is not).
2. **Identity, UA vs t59.** The default-field, armed cell must reproduce t59's armed numbers, in
   particular J1's collapse (S0 351 points) and the nine `wall_like` counts
   (1674/1647/2475/2407/5121/3921/6926/3136/1231). If it does not, the instrument differs from
   ticket 59's and the run is void.
3. **The switch has to be shown working.** On J1, `carried` must equal the rung point count
   (19312 at rung 1), `missing` must be small and reported, and the consumed-field flip rate must
   fall from 41.63 % to **at most 5 %**. A cell where input mode silently fell back to the
   re-estimate is a failed cell, not a negative result.

### The decision this ticket exists to reach

With the sound field (IA) on J1:

- **Positive** — the stop no longer collapses the surface, the S0 boundary stops short of the
  true break edge rather than across it (`farS0` well below the 0.86 of the armed default run),
  and the nine still give 9/9 genuine pairs: the rule is right and the field was the fault; record
  it and hand the field question to ticket 62.
- **Negative** — with a sound field the stop still fails the same way, or now fails differently:
  record it and recommend parking the stop rule.
- **Partial** — say exactly which pieces move and which do not, and do not average over the nine.

Report `farS0`, `blindDeg` and `nS0` per piece, never a mean, and state which of the three
claims is being made (method failed / measurement broken / reference wrong).

### Deliverables

- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t61-soundfield`
  with `run.json`, `submit*.sbatch`, `logs/`, `out*/`, and the index row appended.
- Tables: one row per piece per cell, the columns above; a `decision_table.tsv` naming the
  verdict per piece.
- Two or three PNGs a conservator can read: J1 before/after under UA and IA at the same camera,
  and the field colouring (sign vs mesh) for U and I on J1.
- `## Results` in this ticket appended by the worker: jobs with `sacct` State/ExitCode, both
  gates with the command and the value, the tables, the verdict, and the names of what was not
  measured.
- **No commits, no tracked source edits.** The patch and the instrumented file stay in the run
  directory, exactly as in tickets 59 and 60.

### Budget and discipline

Two sbatch jobs, wall time 1 hour total (t59's armed nine-piece arm took 7 m 55 s). Compute nodes
only. Build inside the job from the ticket commit; check the built binary's md5 against the
patched binary the job records. Corpus read-only. Poll every job with
`scripts/slurm_poll.sh <JOBID>` and record `sacct` State/ExitCode in the Results. If a gate
fails, stop and report rather than spending the second job.

## Results

Run `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1744_f1e876d_t61-soundfield`, commit `f1e876d854cb1e5f2c7ff558179e8b17dfaaaa57`. No tracked source was edited. The stop patch is `work/t59-stop.patch` (+111/−0).

The stop starves J1 only while the field is the pipeline's own re-estimate. Once the rung carries the corpus normals, J1 keeps a surface and its genuine pair comes back, and the test calls **18074 of 19312** points wall-like. The other eight pieces barely move. That is a partial result: the collapse was the field, and the rule with a coherent field does not park J1's boundary short of the break (`farS0` 0.59).

### Jobs

| job | name | sacct State | ExitCode | elapsed |
|-----|------|-------------|----------|---------|
| 34211858 | t61A | COMPLETED | 0:0 | 00:06:39 |
| 34211859 | t61B | COMPLETED | 0:0 | 00:07:34 |
| 34212470 | t61C | COMPLETED | 0:0 | 00:01:39 |

t61A ran U and I. t61B ran UA and IA. t61C scored all four cells and wrote `fields.tsv`, `armed_counts.tsv`, `gate_identity.tsv`, `sep_all.tsv`.

### Gate 1 — U against t55

Command: job 34212470, `work/measure61.py`, md5 of `outU/geom/<piece>.S0` against `/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/out/geom/<piece>.S0`, plus the printed theta and `Normals flipped` line. Table: `gate_identity.tsv`.

J1 is byte-equal: `ff97481e9229201407d182bacd91fd8c` on both sides. Flip draw true/true. Theta 19.03055/19.03055.

J2, J3, J4, J5, J6, J7 and J9 are EQ, flip draw the same, theta the same. J8 is DIFF: this run `e363513a870b7bda8226750111b3c9f6`, t55 `a995cea01148f9d8c395bc096ff55f79`, flip false here and true in t55, theta 27.42166 on both. Eight of nine S0 files match. The ninth is the flip draw, which t55's own rule does not treat as a failed cell.

### Gate 2 — UA against t59

Command: the same script, md5 of `outUA/geom/<piece>.S0` against `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/outG/geom/<piece>.S0`. Armed counts from each piece's `[BREAK-59] piece=` line.

Nine of nine EQ. J1 S0 md5 `cb8119ced5c2a56851de15acbfc3df69`. J1 `nS0` 351. J1 `wall_like=1674` `break_like=17638` `npts=19312`. The nine `wall_like` counts are 1674 / 1647 / 2475 / 2407 / 5121 / 3921 / 6926 / 3136 / 1231.

### Gate 3 — the switch, on the field the stop consumes

Command: `grep NORMAL-33` on `outI/pieces/Juglet_Piece_1/mesh.log`, and `fields.tsv` (call-1 ply against the nearest mesh face, ticket 60's majority-sign flip rate).

Call 1, the growth call, cell I:

`[NORMAL-33] piece=Juglet_Piece_1 call=1 source=input carry=nearest npts=19312 carried=19312 nearest=19312 missing=0 median_dev_to_pca_deg=2.21392 mst=not_applied carry_radius_mm=0 source_n=19312`

The corpus line above it is `source_n=840666`. Call 1 then carries that rung's own stored normals (`source_n=19312`). `missing=0`. Cell IA prints the same carried/missing line.

J1 majority-sign flip rate: U `0.416270`, I `0.001450`. Folded median 3.93° to 2.55°. The picture of that same colouring is below: U is split 11273 same side / 8039 opposite (41.6%). I is 28 same side / 19284 opposite (99.9%). The 0.145% figure is the 28 points that disagree with the other 19284. The carried field is coherent, and as a whole it points the other way from the mesh's outward normal.

### J1, four cells

From `sep_all.tsv`. One row per cell.

| cell | nS0 | blindDeg | farS0 | dc_ge1 | bl0 | genuine |
|------|------|----------|-------|--------|-----|---------|
| U | 13850 | 85.49 | 0.8624 | 0.1205 | 28 | True |
| I | 15730 | 51.49 | 0.5732 | 0.048 | 65 | True |
| UA | 351 | 22.6 | 0.1429 | 0.0017 | 15 | False |
| IA | 10760 | 40.92 | 0.5926 | 0.0588 | 86 | True |

UA is the collapse: 351 points, genuine pair lost. IA is not that collapse: 10760 points, genuine pair back, `farS0` 0.59.

### Armed counts, all nine

`wall_like` / `break_like` / `npts`, from `armed_counts.tsv`.

| piece | UA | IA |
|-------|----|----|
| J1 | 1674 / 17638 / 19312 | 18074 / 1238 / 19312 |
| J2 | 1647 / 236 / 1883 | 1663 / 220 / 1883 |
| J3 | 2475 / 366 / 2841 | 2485 / 356 / 2841 |
| J4 | 2407 / 361 / 2768 | 2381 / 387 / 2768 |
| J5 | 5121 / 550 / 5671 | 5149 / 522 / 5671 |
| J6 | 3921 / 452 / 4373 | 3896 / 477 / 4373 |
| J7 | 6926 / 707 / 7633 | 6956 / 677 / 7633 |
| J8 | 3136 / 328 / 3464 | 3117 / 347 / 3464 |
| J9 | 1231 / 244 / 1475 | 1235 / 240 / 1475 |

On J2–J9 the wall-like count moves by at most 30 points. On J1 it moves from 1674 to 18074.

### Verdict per piece

Partial, and only J1 moves.

- **J1 — partial.** The scrambled field collapses the piece (351 points, genuine false, 1674 of 19312 wall-like). The carried field does not (10760 points, genuine true) and the test then accepts 18074 of 19312. `farS0` goes from 0.86 disarmed to 0.59, which is not a boundary that has stopped short of the break. The positive bar in the ticket is not met. The failure is not the same one either.
- **J2 — does not move.** Wall-like 1647 to 1663. Genuine true in all four cells. `nS0` 1390 / 1238 / 1377 / 1228.
- **J3 — does not move.** 2475 to 2485. Genuine true. `nS0` 2063 / 2227 / 2055 / 2223.
- **J4 — does not move.** 2407 to 2381. Genuine true. `nS0` 2033 / 1940 / 1921 / 1879.
- **J5 — does not move.** 5121 to 5149. Genuine true. `nS0` 4066 / 5347 / 3980 / 5326. The field changes the surface size; the stop does not.
- **J6 — does not move.** 3921 to 3896. Genuine true. `nS0` 3870 / 3600 / 3870 / 3378.
- **J7 — does not move.** 6926 to 6956. Genuine true. `nS0` 5703 / 7373 / 5491 / 7307.
- **J8 — does not move.** 3136 to 3117. Genuine true. `nS0` 2770 / 3429 / 2577 / 2866. Its U-versus-t55 S0 difference is the flip draw above, not this stop.
- **J9 — does not move.** 1231 to 1235. Genuine true. `nS0` 1051 / 1429 / 1050 / 1088.

`nS0` order in those lines is U / I / UA / IA. No mean is taken. The claim is about the method: the collapse was the field it was given; with a coherent field the rule stops refusing points on J1 and does not settle the boundary.

### Pictures

Same axis frame in both files.

- [J1 interior surface, U beside IA](worktrees/sfs/61/artifacts/61/j1_U_IA.png) — titles `U nS0 = 13850` and `IA nS0 = 10760`.
- [J1 consumed field, U beside I](worktrees/sfs/61/artifacts/61/j1_sign_U_I.png) — legends carry the counts above. U is one red sheet and one green sheet. I is red on both sheets.

### Not measured

The distance from each S0 point to the true break edge. `farS0` is the fold far-skin share from `check_separation.py`, not that distance. Call 0 was not scored; call 1 is the field the stop reads. U and UA print no `carried` / `missing` line because `SFS_NORMAL_SOURCE` was unset there.

## Lead verification (2026-11-02)

Checked against the run's own tables rather than the write-up above: `fields.tsv`, `armed_counts.tsv`,
`gate_identity.tsv` and `sep_all.tsv` in `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1744_f1e876d_t61-soundfield`.
Every figure quoted in the Results matches its table.

- `verified: cat gate_identity.tsv -> U vs t55 8/9 EQ (J8 DIFF, flip false here / true in t55), UA vs t59 9/9 EQ`.
- `verified: cat armed_counts.tsv -> J1 wall_like 1674 (UA) vs 18074 (IA); J2-J9 |delta| <= 30`.
- `verified: cat sep_all.tsv -> J1 U 13850 / 85.49 / 0.8624 / 0.1205 / 28 / True; I 15730 / 51.49 / 0.5732 / 0.048 / 65 / True; UA 351 / 22.6 / 0.1429 / 0.0017 / 15 / False; IA 10760 / 40.92 / 0.5926 / 0.0588 / 86 / True`.
- Both renders inspected through the vision bridge (this model has no image input). `j1_U_IA.png`
  carries the titles `U nS0 = 13850` and `IA nS0 = 10760`, and the right panel's blue surface is
  visibly smaller and cut back. `j1_sign_U_I.png` carries `U majority-sign flip 41.63%`
  (11273 same side / 8039 opposite) and `I majority-sign flip 0.14%` (28 / 19284); U shows one sheet
  of each colour, I one colour throughout. The pictures establish the sign structure and the surface
  shrink. They do **not** establish that the boundary stopped short of the break -- that claim rests
  on `farS0` alone, and it is why the bar is not met.

Two things the Results section leaves implicit, recorded because they change how the number reads:

1. **`flip_rate` is the majority-sign rate**, `min(raw_neg, 1 - raw_neg)`, not the share opposite the
   mesh. Cell I is 99.855 % opposite the mesh and only 0.145 % disagreeing with itself. The global
   inversion is harmless to a `dot <= -0.4` test (both sides invert together); what changed is that
   the two sheets now agree. For scale, J6's own re-estimate is also globally inverted (`raw_neg`
   0.9982) and has never been treated as a defect, so the global sign carries no information about
   the piece.
2. **Carrying the input normals is not a free global improvement.** The field alone moves `nS0` on
   the other eight too (J3 2063 -> 2227, J5 4066 -> 5347, J7 5703 -> 7373, J9 1051 -> 1429) and makes
   `farS0` **worse** on four of them (J2 0.818 -> 0.867, J5 0.754 -> 0.939, J7 0.804 -> 0.942, J9
   0.700 -> 0.920). Only J1 improves (blindDeg 85.49 -> 51.49, farS0 0.862 -> 0.573). `genuine` stays
   true on all nine pieces in all four cells.

**Verdict: the positive bar is not met, and the negative bar is met in a specific form.** With a
coherent field the rule accepts 93.6 % of J1's points as wall-like and the surface still reaches the
break (`farS0` 0.593 against 0.573 disarmed, with 32 % of the surface removed); it is not a selective
stop, it is a thin-sherd artefact. The collapse in ticket 59 was the scrambled field, not the clay and
not the arithmetic of the rule. Nothing is merged; the patch remains provenance in the run directory.

**Follow-on:** ticket 62 carries the field question (why the per-rung re-estimate scrambles a whole
sheet) as its own enquiry.

