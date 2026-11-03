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

**Status:** ready-for-human (merged d1d0123; default flipped, regression clean, figures delivered)
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

## Worker findings (2026-11-03)

Job **34262530**, run `20261103-1332_fab76f5_t66-admitsign-default` (commit fab76f5).
sacct: **COMPLETED, ExitCode 0:0, Elapsed 00:16:07**. All six cells rc=0; sep/sector/stage1/render rc=0;
frozen inputs unchanged; index row present (verdict left empty for the lead).

verified: `sacct -j 34262530 --format=JobID,State,ExitCode,Elapsed -P` → 34262530|COMPLETED|0:0|00:16:07.
verified: commit from `run.json`/index row `20261103-1332_fab76f5_t66-admitsign-default	34262530	fab76f5...`.

### Startup-line / escape hatch

`[ADMIT-SIGN-66] default=on admit_sign=1` in every arm-U mesh.log; `default=on admit_sign=0`
in every arm-Z mesh.log; [ADMIT-SIGN-65] per-surface lines present in U (18 jug / 16 pota / 2 potc),
absent in Z (0 everywhere). verified: grep of `pass{U,Z}_{pota,potc}.admit66.txt` / `admit65.txt`.

### Part B — Juglet S0/S1 md5 vs t65 (18 rows)

Arm U (unset = new default ON) vs t65 outT: **18 same, 0 DIFF** (job line `[JOB] Part B U_jug vs t65 T: 18 same, 0 DIFF of 18`).

| piece.surf | t66 U md5 = t65 outT md5 | verdict |
|---|---|---|
| Juglet_Piece_1.S0 | f90290f1748ab8bfc2b4903c1f7dae07 | same |
| Juglet_Piece_1.S1 | e902c5a4ad23810b560578b78e71188c | same |
| Juglet_Piece_2.S0 | b55f2370419698af910106406c0f4c5d | same |
| Juglet_Piece_2.S1 | 307e246d5dfe213b04728935c2e2892c | same |
| Juglet_Piece_3.S0 | 3e1bc4ae5eec948cec2b27292e4a4c59 | same |
| Juglet_Piece_3.S1 | ebd74d0a85845f65ef92eaef1b19e600 | same |
| Juglet_Piece_4.S0 | 9cb520d3bc098dfe96880aa3de5dc694 | same |
| Juglet_Piece_4.S1 | 0ff2a1eca5092840dfad30eef24bc0d1 | same |
| Juglet_Piece_5.S0 | ecca284bb82539833fdf3a2c434ee351 | same |
| Juglet_Piece_5.S1 | 89040689beea4b6d7a5b28a9100a98cb | same |
| Juglet_Piece_6.S0 | 130afed47c52b2916a592cd75f205b2e | same |
| Juglet_Piece_6.S1 | 6f91da15079d9df51bbe7359c7ea3f71 | same |
| Juglet_Piece_7.S0 | 317c93dd9ef147396c9641051f136dd9 | same |
| Juglet_Piece_7.S1 | b8bf1450d862560b7eaee88724275a04 | same |
| Juglet_Piece_8.S0 | f7498660b2b62ca9b14e6e06ad4060fd | same |
| Juglet_Piece_8.S1 | 4da2ea04be20791d50ad912554a314c3 | same |
| Juglet_Piece_9.S0 | 3d5f7b54e2bcafc42956657923648636 | same |
| Juglet_Piece_9.S1 | de3d86ef307a863195fb5cdff78c7f86 | same |

verified: md5sum of `t65/outT/geom/Juglet_Piece_1.S0`=f90290f1..., `.S1`=e902c5a4..., `Juglet_Piece_5.S0`=ecca284b... — match the table (out/geom on t65 side, outU_jug/geom on t66 side).

Arm Z (SFS_ADMIT_SIGN=0) vs t65 outC: **0 same, 18 DIFF** — see anomaly A1; every measured
quantity (sep table row values, sector summary, S0/S1 point counts) is identical to t65 outC.
Example rows (col2 = t66 Z, col3 = t65 outC): J1.S0 e04548e6... vs cdf24514...; J1.S1 654ca5b0...
vs 1e9a20f2...; J2.S0 0b4c64e2... vs ff31689... (full table at run `out/partB_Z_jug_vs_t65C.tsv`).
verified: md5sum `t65/outC/geom/Juglet_Piece_1.S0` = cdf24514a70a4184d635eb970f3df4f2, `.S1` =
1e9a20f2fa0c885fbe0e0ca2f3100da6 — match the table's t65 column.

U vs Z within t66: 0 same, 18 DIFF (same A1 cause).

### Anomaly A1 — md5 DIFFs are curvature-column-only; xyz+normals byte-identical

On t66-Z vs t65-outC `Juglet_Piece_1.S0` (13 062 lines, 13 027 vertices + header):
- diff of columns 1-6 (x y z nx ny nz), raw order: **0 differing lines** — same points, same order.
- Only column 7 (curvature) differs: t65C `3.0816738e-12` on 7 208 rows vs t66Z `-1.5497616e-26` on
  7 208 rows (27 `-nan` and 24 blank rows identical on both sides). Same on J1.S1 (19 838 sorted-diff
  lines, all curvature) and J2.S0 (675/676 rows: U `0` vs Z `2.8027385e-34`).
So the arm-Z md5 mismatches (and the U-vs-Z DIFFs on pieces where the filter dropped nothing) are
confined to the near-zero curvature field; the geometry the downstream stages read is byte-identical.
verified: `diff <(tail -n +11 A|cut -d' ' -f1-6) <(tail -n +11 B|cut -d' ' -f1-6) | grep -c '^[<>]'` → 0;
`awk '{print $7}'|sort|uniq -c` tallies as above. (Why the ON arm reproduces t65T curvature exactly
while the OFF arm does not reproduce t65C is left to the lead.)

### Part C — Pot A (8) + Pot C Piece_01, mesh stage, shipped Pot A defaults

Surfaces 2/2 per piece in BOTH arms (8 S0 + 8 S1 pota, 1+1 potc per cell summary lines).
[ADMIT-SIGN-65] dropped counts in arm U: **0 on every surface of every piece** (all 16 pota lines +
2 potc lines read dropped=0; e.g. Pot_A_Piece_01 s0 admitted_in=33988 kept=33988 dropped=0,
Pot_C_Piece_01 s0 47022/47022/0). Arm Z logs carry no [ADMIT-SIGN-65] lines (filter off).

| piece | U S0 n | Z S0 n | U S1 n | Z S1 n | U drops | md5 U vs Z |
|---|---|---|---|---|---|---|
| Pot_A_Piece_01 | 66763 | 66759 | 57302 | 57286 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_02 | 42198 | 42201 | 46326 | 46327 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_03 | 39774 | 39773 | 43572 | 43573 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_04 | 32683 | 32686 | 35790 | 35790 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_05 | 31577 | 31575 | 34140 | 34139 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_06 | 22571 | 22562 | 24919 | 24920 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_07 | 6066 | 6066 | 6437 | 6437 | 0/0 | DIFF / DIFF |
| Pot_A_Piece_08 | 5528 | 5528 | 6097 | 6097 | 0/0 | DIFF / DIFF |
| Pot_C_Piece_01 | 91929 | 91964 | 105498 | 105516 | 0/0 | DIFF / DIFF |

verified: `grep -m1 'element vertex' out{U,Z}_{pota,potc}/geom/*.S?` headers (counts above);
`passU_pota.admit65.txt` / `passU_potc.admit65.txt` for drop counts.

Anomaly A2 (recorded, not judged): with dropped=0 in arm U, point counts still differ between arms
by up to 9 (Pot A) and 18-35 (Pot C S0/S1) — a difference the filter cannot have made; consistent
with the mesh stage's known unseeded sampling. The md5 DIFFs carry A1's curvature noise on top.

### J1 (Juglet_Piece_1) scores — arm U vs t65 outT

check_separation.py row (arm U `out/sep_U.tsv`; t65 `out/sep_T.tsv` — identical values):
nS0 12663, nS1 16672, blindDeg **58.19** (t65T 58.19), fireDots 384 (384), farS0 0.6575 (0.6575),
farPts5mm 0.8096, bl0 dots 59, bl1 64. Arm Z row identical to t65 sep_C (nS0 13027, blindDeg
68.38, fireDots 340, farS0 0.6729, lip 264). Sector summary (sector.log): U J1 blind 58.19
**f2r_le1 0.9185** r2f_le1 0.4049 r2f0_le1 0.7634 cov 280.0 cov0 275.0 — byte-identical to t65 T
line; Z identical to t65 C (blind 68.38 f2r_le1 0.6665 r2f_le1 0.4211 cov 250.0). Reference arms in
the same log: t55_count blind 85.49 f2r_le1 0.4490, t62F_r1.0 blind 68.38 f2r_le1 0.6665.
verified: grep `Juglet_Piece_1 ` of `out/sector.log` and of t65 `out/sector.log` (both shown above).

### Figures

`out/fig/j1_bl0_before.png` (t65 outC J1 Bl0), `j1_bl0_after.png` (arm-U J1 Bl0),
`j1_bl0_before_after.png`; render.log distance stats identical for both panels: dots 59, le1 59,
b12 0, gt2 0, med 0.336, max 0.933 (Bl0 dots over shaded mesh with t59 label rim).
Copied to `artifacts/66/` in the worktree (gitignored, not committed):
`SfSpp_preprocessing/artifacts/66/j1_bl0_before.png`, `.../j1_bl0_after.png`,
`.../j1_bl0_before_after.png`.

### Anomalies (summary)

- A1: Part B arm-Z md5 DIFFs (18/18) and all U-vs-Z DIFFs are confined to the curvature column
  (near-zero denormals); xyz+normals byte-identical, same point order. Arm U vs t65 outT is
  byte-identical md5 on all 18.
- A2: Pot A/C point counts differ slightly between arms despite dropped=0 (see table).
- No non-zero drops on Pot A or Pot C; no missing surfaces; no other anomalies found.
