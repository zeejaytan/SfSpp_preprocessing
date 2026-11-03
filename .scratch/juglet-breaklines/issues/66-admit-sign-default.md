# 66 — Make SFS_ADMIT_SIGN the default everywhere, prove no regression on other pots, and draw J1's edgeline

**What to build:** three things, in this order. (1) Flip the admit-sign filter in
`mesh_processing_headless.cpp` from default-off to default-ON: unset `SFS_ADMIT_SIGN` means ON,
and `SFS_ADMIT_SIGN=0` (or `off`/`false`) is the documented escape hatch. (2) Prove the flip is
inert arithmetic-wise (new-binary unset arm == t65 treatment, new-binary =0 arm == t65 control,
on S0/S1 md5 over all nine Juglet) and that it does not regress the non-Juglet corpus (Pot A
8 pieces + Pot C Piece_01, judged on the mesh stage). (3) Run the full J1 preprocessing chain
with the new default all the way to the edgeline stage and render the drawn edgeline as pictures.
**Reading adopted:** the conservator's "J01" (m06199) is read as **Juglet_Piece_1** — the piece
whose boundary spills onto the far face. State this reading in every read-out so a wrong guess is
corrected cheaply.

**Answers:** U19, E1

**Blocked by:** 65 (the flag, the filter, and the t65 C/T arms this stands on)

**Status:** in-progress
**Working in:** worktree 66, worker via cursor_code (lead dispatch) (2026-11-03)
**Branch:** 66-admit-sign-default, in /c/PR/worktrees/sfs/66
**Worker:** (unset)

## Spec

### Part A — the default flip (code)

1. `mesh_processing_headless.cpp`: flag `g_admitSign65 = false` at :249; env parse at
   :4724-4725 currently reads unset/empty/"0" as OFF. Change to: **default true**; the values
   "0", "off", "false" (case-insensitive) and empty string mean OFF; anything else means ON.
   No other behaviour changes.
2. Add ONE startup log line, `[ADMIT-SIGN-66] default=on|off admit_sign=<0|1>`, emitted once
   per piece run, so any run's log proves which default the binary carried. Keep the existing
   per-surface `[ADMIT-SIGN-65]` line unchanged.
3. Do NOT touch the filter logic itself (:1525-1562) or the append order (:1564-1575).

### Part B — proof the flip changed only the default (Juglet, 9 pieces)

4. One new run, one new binary built from the flipped commit. Two arms, same binary, recipe
   worness 0.7 + `SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0` (row 12 + row 13):
   - **arm U**: `SFS_ADMIT_SIGN` unset (new default => ON)
   - **arm Z**: `SFS_ADMIT_SIGN=0` (escape hatch => OFF)
5. Acceptance (hard): per piece, arm-U S0/S1 md5 == t65 outT md5, arm-Z S0/S1 md5 == t65 outC
   md5 (t65 run `20261103-0709_a47d478_t65-admitsign`, geom at `outT/geom`/`outC/geom`).
   Any md5 mismatch is a finding, not a tolerance.
6. Runner: generalise `stage65/run_cell55.sh` minimally (it is hard-coded POT_NAME=Juglet) into
   a `run_cell66.sh` that takes POT_NAME + pot-specific mesh/point/axis roots as env; keep the
   stager (`stage_synth_p40.sh`), the corpus md5 gate, the `[PAPER-234]`/`[WORNESS-54]`
   log-line requirements, and the export-then-delete-stage-tree behaviour identical.

### Part C — non-Juglet regression (Pot A 8 pieces + Pot C Piece_01)

7. Corpus: Pot_A Piece_01..08 from Dataset Point/Mesh + Dataset Axes (Pot A meshes come from
   CORP per `stage_synth_p40.sh`); Pot_C Piece_01 from Dataset Point/Mesh + CORP axis
   (`original_samples/SfS_pp/Axes/Pot_C_Piece_01_Axis.xyz`). Defaults = the SHIPPED Pot A
   defaults recorded in t41 run.json (`SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0
   SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0`, no worness, no radius
   mode) so the admit-sign switch is the ONLY difference. Arms U and Z exactly as Part B.
8. Judged on the MESH stage only: (a) surfaces per piece must stay 2/2 in both arms; (b) S0/S1
   point counts per arm and the `[ADMIT-SIGN-65]` dropped counts from the logs; (c) S0/S1 md5
   equal between arms wherever dropped == 0 (expected on clean clay: J2-J9 zero drops in t65;
   Pot A flip rate 0.18-1.70%). **Bl0/Bl1 dot counts are NOT regression evidence** — the edge
   stage is non-deterministic (b56: same arm re-run reads 28 vs 58 dots on J1); record them but
   judge nothing on them.
9. Regression = any piece where the filter dropped points AND the surface count changed OR the
   kept-surface md5 differs from arm Z for a reason other than the drop. Name the piece.

### Part D — J1 edgeline pictures (the conservator's deliverable)

10. Arm U of Part B IS the fresh full J1 chain (mesh stage + Breakline stage). Export J1's
    Bl0/Bl1 as in t65 and render: Bl dots over the shaded mesh, with the t59 label rim
    (`runs/20261102-1144_638504b_t59-breakstop-stage0/out/labels/Juglet_Piece_1.npz`, label 2
    = fracture rim) drawn as the true-edge reference. Two figures minimum: before (t65 outC J1
    Bl0) vs after (arm-U J1 Bl0), same camera.
11. Score with the frozen ruler `check_separation.py` from the t57 run (blind stretch, farS0,
    f2r/r2f, ring coverage) on arm-U J1 and report next to the t65 outT numbers. Reuse
    `stage65/t65_plot.py` framing (S0 fold midpoints, t59 label colours).

### Honesty notes (carry into the read-out)

12. The filter is a **symptom cure on J1**: it deletes admitted points whose nearest
    growth-cluster point sits across a thin wall. The mechanism cure is radius mode (ledger
    row 13). On clean pots it should be inert — that is what Part C proves or refutes.
13. A worn lip may cap how well any edgeline can follow the true break (U19, withdrawn 13.8mm
    figure, direct sphere fits J1 7.67mm @ 3mm ball). If arm-U J1 edgeline still misses the rim
    on part of the ring, that is a property of the surface, not a failure of this ticket.

### Deliverables / acceptance

- Flipped default + escape hatch merged; FIXES-LEDGER row 14 ("SFS_ADMIT_SIGN default-on,
  conservator 2026-11-03") + runbook note.
- Part B md5 table (18 rows) all equal; Part C table (9 pieces x 2 arms) with drop counts.
- J1 before/after edgeline figures in `SfSpp_preprocessing/artifacts/66/`, linked as
  workspace-relative Markdown in the read-out.
- `runs/index.tsv` row + run.json per the runs convention; every sbatch polled and its sacct
  State/ExitCode recorded.
