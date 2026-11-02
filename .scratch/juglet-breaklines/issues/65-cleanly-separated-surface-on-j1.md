# 65 — Get a cleanly separated surface on J1

**What to build:** the reason J1's growth does not separate cleanly along its break edge, and —
only if a cause can be proved — the smallest default-off change that makes it. "Clean" is defined
by the frozen scorer (`check_separation.py`), not by eye: Surface_0 must be one sheet that stops
at the break, so that the gap between the two surfaces is small **and** the boundary follows the
rim **all the way round**. J1 is the only one of the nine Juglet pieces that fails either half.
Diagnosis first; a null result is a valid ending and must be stated as one.

**Answers:** U19, E1

**Blocked by:** 63 (its instrumented walk is the instrument for stage 2a), 62 (its radius-1.0 cell
is the best baseline we have)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03); stage 1 analysed, stage 2 not yet run in the pipeline
**Branch:** 65-cleanly-separated-surface-on-j1, in /c/PR/worktrees/sfs/65
**Worker:** worker 3 (Cursor session, 2026-11-03 ~07:00), after workers 1-2 were reaped by the harness

## Spec

### Given (measured facts this stands on)

1. **The ruler is frozen.** `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py`
   (read its docstring, lines 1-60, before anything else). Four numbers matter here and their
   definitions may not be re-invented:
   - **blind stretch** (deg): largest angular gap in Surface_0's boundary-fire dots around the
     break-edge ring. Degrees only — the "717 fold points" figure elsewhere is derived, never a
     measurement.
   - **far-skin share** (`farS0`): share of Surface_0's fold midpoints whose points sit on the far
     side of the wall (median offset < -0.8 mm along the mesh normal). Low is good.
   - **reverse coverage** (`f2r_le1` / `r2f_le1`): the two directions of "is the boundary where
     the rim is". `f2r_le1` = fold midpoints within 1 mm of a boundary point; `r2f_le1` = rim
     midpoints with a boundary point within 1 mm; `ring_cov_deg5` = degrees of the ring that have
     any boundary point at all.
   - **genuine pair**: median NN S1->S0 between 70-105 % of the piece's wall thickness AND median
     perpendicular residual <= 0.05 mm. This only says two surfaces sit a wall apart. **On J1 it is
     true and still wrong** — do not treat it as success.

2. **J1 today, best configuration known** (radius 1.0 mm, `SFS_NORMAL_MODE=radius
   SFS_NORMAL_RADIUS_MM=1.0`, worness 0.7; cell F of `runs/20261103-0035_ca520fe_t62-normalfix-s2`,
   tables in `work/lead-fast/frontier/{label_edge,reverse,union_edge}.tsv`):
   blind 68.38 deg (worst of nine; the other eight are 5.51-18.64), farS0 0.6729 (worst of nine;
   others 0.6923-0.8824), `f2r_le1` 0.6665 (others 0.9448-1.0), `r2f_le1` 0.4211 (others
   0.4578-0.6267), **ring coverage 250 of 360 deg** (others 315-360) — i.e. 110 deg of J1's rim has
   no boundary point anywhere near it. Median boundary-to-rim distance 0.46 mm, but 26 % of fold
   midpoints are more than 2 mm off and the worst is 6.12 mm. The count-mode baseline (t55,
   `runs/20261101-2004_05be12c_t55-worness07-breaklines`) reads blind 85.49, farS0 0.8624,
   `f2r_le1` 0.449, worst 8.545 mm, coverage 360 deg (a long jagged boundary that reaches every
   sector).

3. **What the radius fix did and did not do.** It removed the orientation flip (J1 flipped 41.63 %
   -> 0.2 %, ticket 62) and halved the median boundary error (1.274 -> 0.460 mm), and it made the
   boundary *shorter and more local* — which is why coverage fell 360 -> 250 deg. So the fault is
   no longer normals; it is **which points the growth claims**.

4. **J1's remaining defect is not wall bridging or orientation.** Those are measured and clean at
   radius 1.0 (t62/t63). The two things still wrong are geometric: the boundary sits off the break
   by a few millimetres on a third of the rim, and a third of the rim is missing from the boundary
   altogether.

5. **The surface is genuinely worn there.** Median normal turn against a geodesic window on J1:
   9.07 deg at 2 mm, 20.76 at 5 mm, 38.48 at 10 mm — about **3.8 deg/mm sustained to 10 mm**
   (t59 stage-0 signals, `runs/20261102-1144_638504b_t59-breakstop-stage0/out/stage0_summary.json`).
   The other eight turn 23-52 deg inside 2 mm then flatten. Implied round-over radius ~**13.8 mm**
   against 3.4-4.7 mm on the other eight, on a 65 mm vessel whose own curvature is ~19 deg per
   10 mm. A worn lip is physically a diffuse edge: any method may be limited to placing the line
   to a few millimetres, and a worn lip also cannot mate tightly. **That limit is not assumed here
   — it must be measured, and distinguished from a boundary that simply stops too early.**

6. **Worness is not the lever.** Swept 0.30-0.90 (t57): no value cleans J1 while holding all nine;
   J1 farS0 stays 0.776-0.912 across 0.55-0.90, and 0.30-0.50 swaps the surface identities. Treat
   `SFS_WORNESS` as a control, not a candidate fix.

7. **Dot counts are not evidence.** The same count-mode arm scored 28 dots in the t55 run and 58 in
   the t57 repeat; the mesh split is deterministic (S0 md5 stable), the edge stage is not. Any
   gate that reads Bl0 counts must first say which run it came from; better, do not use them.

8. **The 50-dot floor is the authors' own exclusion rule**, not a bug to lower (t58,
   `papers/text/sfspp-2502.13986v1.md:329`). SFS++ excludes short-breakline pieces rather than
   seating them, so "make J1's breakline longer" is not a route to a seated J1.

9. **Pot A is the control**: 8 pieces, thick walls (2.5-4.0 mm), 9/9 genuine pairs, none of them
   wearing this problem. Any change must leave Pot A within the usual tolerance.

10. **Instruments already on Spartan** (all verified present on 2026-11-03):
    - scorer: `runs/20261102-0450_05be12c_t57-sweep/check_separation.py`;
    - t59 region labels (wall/roll/fracture/anomaly per face) + true rim:
      `runs/20261102-1144_638504b_t59-breakstop-stage0/out/labels/<piece>.npz` (keys
      `V F labels core hit_dist hit_dot devs ball_radii lab_sens0 lab_sens1 vlab t_piece`;
      `labels` int8 0=wall 1=roll 2=fracture 3=anomaly; J1 = 35464/4276/4117/4735 over 48592
      faces; probe source `work/stage0_probe.py`);
    - t63 instrumented orientation walk: `runs/20261103-0211_249906a_t63-orientwalk/work/orient_walk.py`
      (through-wall MST edge count + flip share on the pipeline's own dumped points);
    - wall thickness: `runs/20261101-1613_83edd76_t54-worness-dial/out/wall40/<piece>_wall.json`;
    - t62 frontier probe kit (working imports, panels, tables):
      `runs/20261103-0035_ca520fe_t62-normalfix-s2/work/lead-fast/frontier/`
      (`t62_frontier.py` shows `sys.path.insert(...); import check_separation as cs`, and the arms
      list; `t62_labedge.py`, `t62_rev.py`, `t62_plot.py` are the three tables and the figure);
    - geometry bundles to read: `runs/.../t55.../out/geom` and
      `runs/20261103-0035_ca520fe_t62-normalfix-s2/outF/geom` (`<P>.{S0,S1,Bl0,Bl1}`);
    - meshes `/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet` (J1 md5
      b447066c29181fe7ba987439c22c5d9c);
    - the per-piece pipeline driver to adapt:
      `/c/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/stage55/instruments/run_cell55.sh`
      (stage -> mesh stage -> export -> edge stage) and the submitter beside it (`submit55.sh`,
      twelve laptop-side gates).

### Build

Work in this order. Each stage ends in a number you can be wrong about. **Do not skip stage 1 to
get to a fix**: three earlier attempts to fix J1 by knob died because the defect had not been
located.

**Stage 0 — reproduce and localise (no new pipeline run).** Re-run the scorer and the three
frontier tables for J1 against the frozen bundles, and confirm you reproduce the Given numbers
(j1 blind 68.38, farS0 0.6729, f2r 0.6665, r2f 0.4211, coverage 250). If you do not, stop and
report the discrepancy rather than proceeding on a number you cannot reproduce. Then localise: for
J1 only, bin the rim ring into 10-deg sectors and report, per sector, (i) the boundary-to-rim
distance distribution, (ii) whether a boundary point exists at all, (iii) the local wall thickness
and t59 label mix (wall/fracture/roll), (iv) the local normal-turn rate. **The deliverable is a
per-sector table plus one figure** showing the rim, the S0 boundary, and the sectors that fail,
from a viewpoint that resolves 1 mm (a bad viewpoint is a bad measurement: state the camera
placement and the in-plane scale). This alone answers "which part of J1 is broken" and it is
cheap.

**Stage 1 — characterise the boundary: what, physically, is the S0 boundary on J1?** In the worst
sectors, ask whether the boundary is (a) a genuine stop at the break, (b) a slice through the
sheet where the growth stopped claiming wall, or (c) an artefact of the split (the pixels near the
seam assigned to the other sheet). Test each with the existing labels: the boundary's own t59
label mix; whether points just outside the boundary are claimed by S1 (double-cover table,
`dc_ge1` is 0.1205 on J1 at t55 — check the radius-1.0 value); and whether the boundary follows a
smooth curve across the sheet rather than the rim. **Gate 1:** every failing sector is assigned
to (a), (b) or (c), with the measurement that decides it, and the split of failing rim across the
three. If some sectors are genuinely (a) — a worn, diffuse edge — say so and quantify the
irreducible error there.

**Stage 2 — test the candidate causes, cheapest first.** Only the causes stage 1 implicates.
Candidates, with the prediction each makes (a cause that makes no falsifiable prediction is not a
candidate):

- **2a — detachment / wall claim.** If the failure is (b) or (c), the growth is deciding the wall
  face belongs to the other sheet. Prediction: on J1, wall-labelled points adjacent to the
  boundary are claimed by S1 at a higher rate than on the other eight, and the failing sectors are
  the thin ones (J1's thinnest smooth wall is **1.463 mm** vs 1.585 J2 / 1.980 J7; ticket 63).
  Measure with the t63 walk and the labels. If this is the cause, the fix is a claim rule, not a
  threshold.
- **2b — the split/termination rule.** If the failure is (b), the sheet is being cut by the
  clustering's own termination, not by the geometry. Locate the code path that ends the growth and
  show which condition fires first on J1 and not on the other eight. Read the source before
  guessing: `mesh_processing_headless.cpp` (growth and merge from ~:4940 onward; worness ladder
  :4845-4910; surface export :4993-5030).
- **2c — the worn-edge regime.** This one already has a measured answer: worness 0.30-0.90 cleans
  nothing (t57). Re-run one point only if a new mechanism demands it; do not sweep again.
- **2d — something not on this list.** Allowed and welcome, provided it comes with its own
  falsifying test.

**Gate 2:** one named cause (or an explicit "no single cause found"), the prediction it made, and
whether the prediction held. A cause whose prediction fails is reported as refuted, not reframed.

**Stage 3 — the smallest change, default-off, measured on all nine plus Pot A.** Only if stage 2
produces a cause whose prediction held. Constraints: unset behaviour byte-identical; no default
change; no retuning of the frozen scorer's constants; the change is small enough to review in one
sitting. Measure with the same scorer on all nine Juglet and Pot A 8, against both baselines (t55
count-mode and t62 cell F radius 1.0).

**Gate 3 (the only definition of "cleanly separated" this ticket accepts):** J1 blind <= 20 deg,
`r2f_le1` >= 0.90 and ring coverage >= 340 deg, farS0 >= 0.85, worst boundary error <= 2 mm; the
other eight stay within 0.08 mm on median boundary error and hold 9/9 genuine pairs; Pot A shows
no harm. **If stage 3 cannot clear gate 3, say so plainly and record what J1's floor is** — the
measured irreducible error at the worn sectors — because that number is what the assembler
question actually needs.

### Report back (the worker's write-up)

Append a `## Results` section to this ticket: the per-sector table, the figure path, the cause
with its prediction and verdict, every job id with its `sacct` State/ExitCode, and **one short
plain-language paragraph** a conservator can read: what was wrong with J1, whether it is fixed,
and if not, how wrong the best result is in millimetres of misplacement on the pot. Name which
claim you are making — "the method fails on J1", "the measurement was broken", or "the reference
is wrong" — do not blur them. Add no `Status`/`Branch` edits, no commits, no merges;
`verdict`/`human_note` in `runs/index.tsv` stay empty for the lead.

### Gates and budget

- Corpus read-only; `inputs.diff` empty; the unset arm byte-identical.
- Every `sbatch` polled with `scripts/slurm_poll.sh <JOBID>`; final `sacct` State/ExitCode in the
  ticket.
- Budget: <= 6 jobs, <= 5 h wall total. Stage 0/1 need **no** new job — they read frozen outputs;
  say so before submitting anything.
- Heavy work on Spartan compute nodes, never the laptop or the login node; small scoring runs may
  share a held allocation (`scripts/gpu_session.sh`).

### Traps (paid for already)

- SSH from this laptop: `C:/Windows/System32/OpenSSH/ssh.exe spartan` (Git Bash `ssh` has no key);
  poll `sacct` directly.
- Spartan python: `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` (no pandas —
  aggregate in awk or fetch small TSVs to the laptop).
- sbatch files need Unix line endings (a DOS-ending sbatch was rejected once); `bash -n` and
  `py_compile` every script before it is submitted.
- Jobs must fetch the worktree commit before building; verify the commit hash in the job log
  against `git rev-parse HEAD`.
- A FAILED row in any TSV must carry the same field count as the header.
- `grep -a` on binary PLY/PCD; PLY header length varies — never parse it, record size+md5.
- Unset every `SFS_*` and `POT_NAME` between pieces.
- Single writer in `.scratch/`: run `python C:/PR/scripts/check_scratch_writer.py SfSpp_preprocessing`
  before editing, and only inside your own worktree.
- Do not re-tune the scorer's frozen constants, and do not compute "blind stretch times a density"
  to get a point count: the fold's angular density is far from uniform (36 ten-degree bins, mean
  78.4, sd 70.2, range 4-266).

### Out of scope

- Adopting radius 1.0 mm as a pipeline default (ticket 64 / the conservator's decision).
- Ticket 64's adaptive radius rule (built separately; this ticket must not depend on it).
- The full assembly run, and any judgement about whether J1 *should* seat.
- The edge stage's non-reproducibility (28 vs 58 dots): if it blocks a measurement, record it and
  route around it — fixing it is its own ticket.
- Changes to `check_separation.py` or the t55/t62 baselines.

## Worker log

### 2026-11-03 ~07:00 — worker 3: stage-1 read-out of worker 2's emulation (no new job)

Analysis only. Every number below was read in this session from
`runs/20261103-0515_aee7ba0_t65-j1-localise/out/` over ssh (`emul/sep_emul{55,F}.tsv`,
`emul/{emul55,emulF}/emul_counts.tsv`, `emul/stage1.log`, `emul/stage1/stage1_pieces.tsv`,
`emul/sector.log`, `stage2/admit_blocks.tsv`). No Slurm job was submitted; holder 34240339 was
not used. `check_scratch_writer.py` flagged worker 2's untracked stage65 scripts (newest 06:37,
before that worker was reaped); I edited only this ticket file.

**Stage 0 reproduces.** `sector.log` gives J1 at t62 cell F: blind 68.38°, f2r_le1 0.6665,
r2f_le1 0.4211, coverage 250°. These match Given 2. The t55 values also match: blind 85.49°,
f2r 0.4490, coverage 360°.

**What the emulation varies (read from `t65_emul.py`, `t65_admit.py`, `run_emul65.sh`).** Each
written surface file is the B-spline admission block (the first `n_adm` rows; `n_adm` is taken from
the `[WINDOW-26-FINAL]` line in `mesh.log`, using the other branch's count when
`other_copied_over=yes`) followed by the growth cluster. The emulation keeps every growth-cluster
row. It keeps an admitted row only if that row's normal agrees in sign (dot > 0) with the normal of
the nearest growth-cluster point of the same surface. Rows that appear in both blocks (distance 0)
fix the relative sign between the two blocks first. Bl0 and Bl1 are symlinked from the source run
unchanged. The two arms use the same rule on different source surfaces:
- **emulF** applies it to t62 cell F (normals with a 1.0 mm radius);
- **emul55** applies it to t55 (count-mode normals, where J1's orientation is 41.63 % flipped).

So the arms differ in source run, not in rule. On t55 the normal test cannot work, because the
normals it reads are the ones that are flipped.

**Nine-piece table from the frozen scorer** (`sep_emul*.tsv`; "S0 drop" is `adm_dropped` for
surface 0 from `emul_counts.tsv`):

| piece | arm | S0 drop / adm | blind ° | farS0 | dc_ge1 | med_nn mm | % wall | genuine |
|---|---|---|---|---|---|---|---|---|
| J1 | emul55 | 16 / 6901 | 45.89 | 0.8936 | 0.1198 | 1.892 | 83.6 | True |
| J1 | emulF | 364 / 5819 | 58.19 | 0.6575 | 0.0085 | 1.984 | 87.6 | True |
| J2 | emul55 | 0 / 724 | 18.14 | 0.8182 | 0.0129 | 2.281 | 96.2 | True |
| J2 | emulF | 0 / 735 | 18.64 | 0.8824 | 0.0029 | 2.282 | 96.2 | True |
| J3 | emul55 | 0 / 1081 | 22.06 | 0.7714 | 0.0027 | 2.030 | 94.3 | True |
| J3 | emulF | 0 / 1158 | 14.57 | 0.6923 | 0.0262 | 2.039 | 94.8 | True |
| J4 | emul55 | 0 / 1047 | 11.03 | 0.7059 | 0.0245 | 2.322 | 93.0 | True |
| J4 | emulF | 0 / 983 | 11.60 | 0.7941 | 0.0011 | 2.314 | 92.7 | True |
| J5 | emul55 | 0 / 2087 | 7.70 | 0.7544 | 0.0163 | 2.534 | 93.5 | True |
| J5 | emulF | 0 / 1998 | 7.57 | 0.7447 | 0.0000 | 2.570 | 94.8 | True |
| J6 | emul55 | 0 / 1957 | 11.94 | 0.8824 | 0.1388 | 2.388 | 96.6 | True |
| J6 | emulF | 0 / 1960 | 9.90 | 0.8333 | 0.0013 | 2.442 | 98.8 | True |
| J7 | emul55 | 0 / 2997 | 5.92 | 0.8039 | 0.0502 | 3.002 | 93.0 | True |
| J7 | emulF | 0 / 2969 | 5.51 | 0.7059 | 0.0365 | 3.013 | 93.4 | True |
| J8 | emul55 | 0 / 1431 | 11.93 | 0.6512 | 0.0556 | 1.910 | 93.0 | True |
| J8 | emulF | 0 / 1482 | 7.96 | 0.7429 | 0.0312 | 1.919 | 93.4 | True |
| J9 | emul55 | 0 / 541 | 12.32 | 0.7000 | 0.0777 | 2.142 | 94.9 | True |
| J9 | emulF | 0 / 553 | 13.10 | 0.8065 | 0.0691 | 2.137 | 94.7 | True |

The other eight are not just "barely moved": the rule drops **zero** points on either surface of
any of them, in both arms. Their emulated surfaces are therefore the same point sets as the
source, and the scorer reads the same values: `sector.log` shows emulF identical to t62F and
emul55 identical to t55 on J5-J9, and J2's emulF blind of 18.64 is the Given t62F value. The
differences between emul55 and emulF on rows J2-J9 are differences between t55 and t62F, not
effects of the rule. J1 is the only piece where the rule acts. Its S1 loses 23 points (emul55) and
62 points (emulF).

**J1 in detail** (`stage1_pieces.tsv`; `sector.log` for f2r, r2f and coverage). "Off-rim" means a
fold midpoint more than 2 mm from the Surface_0-side rim; it is split by the sheet it lies on.

| J1 arm | blind ° | f2r_le1 | r2f_le1 | cov ° | off-rim fold | on S1 sheet | on S0 sheet | on fracture | fold islands | rim misses | misses claimed by S0 / S1 only / nobody | a2 band S1-only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t55 | 85.49 | 0.449 | 0.442 | 360 | 0.545 | 0.523 | 0.017 | 0.005 | 22 comp, 0.161 | 0.296 | 0.876 / 0.041 / 0.083 | 0.003 |
| emul55 | 45.89 | 0.450 | 0.444 | 355 | 0.540 | 0.518 | 0.017 | 0.005 | 19 comp, 0.155 | 0.287 | 0.872 / 0.032 / 0.096 | 0.000 |
| t62F | 68.38 | 0.667 | 0.421 | 250 | 0.367 | 0.335 | 0.014 | 0.019 | 9 comp, 0.128 | 0.237 | 1.000 / 0 / 0 | 0.000 |
| emulF | 58.19 | 0.919 | 0.405 | 280 | 0.068 | 0.039 | 0.020 | 0.006 | 3 comp, 0.000 | 0.237 | 1.000 / 0 / 0 | 0.000 |

The best possible scores, taking J1's Surface_0-side rim itself as the boundary, are the same in
every arm: r2f_ceil 0.4426, coverage 360°, gap_ceil 5.05°. At the rim points the boundary misses,
the fracture face is 5.03 mm wide (median, t62F and emulF; 155 points). Where the boundary does
hit, it is 1.37 mm.

From `admit_blocks.tsv` (t62F): Surface_0's admission block (5,819 rows, copied from the other
branch) carries 373 points on the far face, 6.4 % of the block, and supplies 98.4 % of all of
Surface_0's far-face points. On the other eight pieces, Surface_0's admission block has at most
2.6 % of its points on the far face (J2 2.6 %, J3 1.8 %, J4-J9 0-0.5 %). Copying the other
branch's block is not unique to J1: `other_copied_over=yes` appears on one surface of every piece.

**Stage-1 verdict (gate 1), on the t62F baseline. Claim type: the method fails on J1, in two
separable ways. Neither the measurement nor the reference is implicated.**

1. **The off-rim boundary is a split artefact (class c), not a slice (b) and not a stop (a).**
   - 36.7 % of J1's fold sits more than 2 mm from the rim. Of that, 33.5 points are on the S1
     sheet, 1.4 on S0's own sheet and 1.9 on the fracture face. So about 91 % of the off-rim
     boundary is Surface_0 running onto the far face.
   - Dropping only the 364 admitted points whose normals disagree with the growth cluster cuts
     the off-rim share from 0.367 to 0.068 and the share on the S1 sheet from 0.335 to 0.039. It
     also raises f2r_le1 from 0.667 to 0.919, just under the other eight's t62F range of
     0.9448-1.0. The share of the fold in detached islands falls from 0.128 to 0.
   - The mechanism is localised to the B-spline admission block, not the growth cluster: the
     cluster has 6 far-face rows against the block's 373.
2. **The missing rim is S0 running past the rim onto a wide, worn break face (class a /
   diffuse edge). It is not S0 stopping short (b), and the seam is not handed to S1 (c).**
   - 23.7 % of the S0-side rim has no boundary within 1 mm. Every one of those rim edges is
     covered by S0 on both vertices: claimed by S0 1.000, S1 only 0, nobody 0.
   - The 2a test (wall vertices within 3 mm of the rim claimed by S1 and not S0) reads 0.000.
     **2a's prediction is refuted on J1.**
   - These misses sit where the break face is 5.0 mm wide, against 1.4 mm where the boundary
     hits. That is consistent with the ~13.8 mm round-over in Given 5.
   - The emulation leaves this part unchanged: rim misses stay at 0.237, blind still reads
     58.19°, r2f 0.405, coverage 280°.
   - Split of the failing rim: about 0 % (b), about 0 % (c, seam given to S1), and 100 % S0
     overrunning a wide break face. The irreducible error there is not yet quantified; the
     5.0 mm median break-face width is an upper bound on how far the line can be from the rim.

**Two cautions for the lead.**
- **On J1, emul55's blind of 45.89° is not an improvement.** It removed 16 of 13,850 Surface_0
  points (0.12 %). Every geometric column barely moved: off-rim 0.545 to 0.540, f2r 0.449 to 0.450,
  and 22 to 19 fold components. Yet blind fell 39.6°. Blind stretch on J1's jagged,
  many-island boundary is fragile at that scale, so a difference of tens of degrees there needs a
  geometric column beside it before it means anything. (This is the measurement's sensitivity,
  claim 2, not a broken scorer.)
- **Gate 3 as written cannot be met by any boundary, perfect or not.** J1's r2f ceiling is 0.4426:
  r2f counts rim midpoints on both sides of the break, and only the Surface_0-side rim can be
  within 1 mm. The other eight have ceilings of 0.56-0.87. So `r2f_le1 >= 0.90` is unreachable on
  every Juglet piece. Gate 3 needs restating against the ceiling, for example
  r2f_le1 / r2f_ceil, or r2f0_le1. Also, "farS0 … Low is good" (Given 1) conflicts with gate 3's
  "farS0 >= 0.85". I report the values and leave that to the lead.

**Stage-2 prediction this sets up (2d: an admission-side rule; untested in the pipeline).** A
default-off switch in `finishImprovedSurface` (`mesh_processing_headless.cpp:1510-1531`) applies
the emulated rule. It drops admitted points whose normal disagrees with the nearest growth-cluster
point, with the sign fixed by the duplicated rows. Run at radius 1.0, it should:
- leave S0 and S1 point-identical on J2-J9 (0 drops predicted on all 16 surfaces);
- on J1, drop about 364 S0 points, bring the off-rim fold to ≤ 0.08 and f2r_le1 to ≥ 0.90, and
  bring dc_ge1 to ≤ 0.01;
- **not** close the blind stretch or the coverage gap: blind about 55-60°, coverage about 280°, rim
  misses about 0.24, all at the 5 mm wide break face.

What would refute it:
- any drop on J2-J9;
- or, on J1, off-rim above 0.15 after the change.

The edge stage is not deterministic, so compare Bl0-derived columns against that piece's own
run-to-run spread. Pot A has not been emulated. Its admission blocks must be checked for drops
before a pipeline run. That check is cheap: `t65_admit.py` plus `t65_emul.py` on the Pot A
bundles. Nothing in this stage clears gate 3; on present evidence a fix to the admission block
would leave J1 with a sound off-rim boundary but a missing quarter of the rim on the worn lip.

### 2026-11-03 07:05 — lead verification and gate ruling

Every load-bearing number in the section above was re-read by the lead from the same tables
(`stage1_pieces.tsv`, `sep_emul{55,F}.tsv`, `admit_blocks.tsv`, `emul_counts.tsv`) and from
`t65_emul.py:46-54` (the rule and the duplicate-row sign fix are exactly as described).

verified: stage1_pieces.tsv J1 rows -> fold_off2 t62F 0.3673 / emulF 0.0678; fold_off2_s1 0.3348 -> 0.0394; fold_island_share 0.128 -> 0.0; rim0_miss 0.2366 unchanged; r2f_ceil 0.4426 in all four arms
verified: admit_blocks.tsv t62F J1 S0 -> adm_on_far 373, far_total 379, far_from_adm 0.9842, cl_n_far 6
verified: emul_counts.tsv -> adm_dropped 0 on all of J2-J9, both arms, both surfaces
verified: t65_emul.py:46-54 -> admitted rows kept iff sgn*dot(Na, Nc_nearest) > 0, sgn from duplicate rows

**Ruling on the two cautions (both accepted):**
- emul55's blind 45.89 deg is recorded as an artefact of blind's fragility on J1, not an
  improvement (16 of 13,850 points removed, every geometric column static, blind fell 39.6 deg).
  Blind is reported on J1 but gates nothing there.
- **Gate 3 is restated** (it was mis-authored: `r2f_le1 >= 0.90` exceeds J1's measured ceiling
  0.4426 on every arm, and `farS0 >= 0.85` contradicts Given 1's "low is good"):
  1. *Split-artefact half (gating):* fold_off2 <= 0.10 AND fold_off2_s1 <= 0.05 AND
     fold_island_share == 0 AND f2r_le1 >= 0.90, on all nine pieces, with J2-J9 unchanged.
  2. *Rim-following half (report-only, against ceilings):* r2f_le1 / r2f_ceil and ring_cov /
     cov_ceil. J1's residual rim0_miss ~0.24 where the break face is 5.03 mm wide is the worn-lip
     physical ceiling (Given 5); it is documented, not gated.
  3. farS0 is dropped from the gate (redundant with fold_off2_s1, which measures the spill directly).

**Stage-1 verdict is ACCEPTED as the ticket's stage-1 answer:** J1's boundary fails in two
separable ways — (i) a split artefact, the copied-other-branch admission block carrying 373
far-face points (98.4 % of S0's far-face points), cleared offline by the sign rule; and (ii) S0
overrunning the rim onto a 5.0 mm-wide worn break face, which no admission rule can clear
(rim0_miss unchanged in every arm). 2a is refuted on J1; 2c was refuted before (Given 5).

**Stage-2 outcome so far:** the 2d admission-side rule (emulated) meets restated gate half 1 on
J1 (0.0678 / 0.0394 / 0.0 / f2r 0.919) and is provably neutral on J2-J9 (zero drops). Stage 3 =
carry it into the pipeline as a default-off flag and re-run the real chain.
