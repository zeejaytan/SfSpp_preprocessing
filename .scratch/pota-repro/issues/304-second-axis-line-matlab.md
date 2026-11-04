# 304: Why our axes lack the reference's second line — run the authors' own MATLAB on Piece 08's own surfaces

**What to build:** a decision, with evidence, between the two explanations ticket 303 left open for
Pot A Piece 08's missing reference axis line. Then, only if the first one holds, the smallest fix
that makes our own estimator propose a comparable line and re-seats Pot A **8/8, 15/15 using our
axes alone**.

The two explanations, stated so they can be told apart:

1. **Port divergence.** The released `Axes/Pot_A_Piece_08_Axis.xyz` was produced from these same
   `Surfaces/*.xyz` by the authors' MATLAB, and our Python port loses the line that MATLAB keeps
   (subsample/`step`, the two refine stages, dedup at 10 deg, the `cost < cost(1) * 1.1` cut, the
   stale-cost sort). Fixable.
2. **Different input.** The released file was made from surfaces or an estimator that is not in
   `SfSpp_preprocessing/AxisExtraction/`. Then no change to `sfs_axes` can recover it, and the
   finding is about the reference, not about us.

The test is the authors' own code, not a reimplementation: `AxisExtraction/run_potsac.m`, run on
Piece 08's shipped surfaces, dumping **every candidate at every stage**, not only the winner.

**Answers:** E1

**Blocked by:** none. Ticket 303 is landed (merged 6ab14c4); its evidence is the starting point.

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** large 8

**Hand-over:** Claude — needs Spartan compute (MATLAB refuses the login-node licence), the corpus,
and the assembler for the end-to-end check.

**What ticket 303 already established (do not re-derive; verify only if you intend to contradict
it):**
- Pot A's corrected axes seat **7/8, 13/15** against the released axes' **8/8, 15/15**, on 5/5
  replays. The lost piece is **Piece 08**, and it is grossly wrong, not slightly off:
  **167.08 deg / 379.5 mm** from truth, while every other piece moves ≤0.4 deg / ≤2 mm against the
  control. Matched with the counter's own bar (0.35 rad, 50 mm — `class/data_structure.cpp:966`).
- It is a **singleton in the assembly graph, not a mis-join**: the Piece 02-08 pair reaches
  inlier 18 / area 2 in the failing arm against inlier 37 / area 15.5 in the 8/8 arm.
- **No re-ranking seats it**: oracle line order, first-line-only, our best line alone, post-refine
  cost re-sort, the paper's dedup, patch contiguity — all 7/8.
- **What does seat it**: our three lines plus the released file's **second** line → 8/8 and 15/15,
  two replays (job 34336399, run 20261104-2010_78dc9ee_t303-missing-axis). That arm is DIAGNOSTIC
  ONLY and must never ship: it reads the reference.
- Our full candidate set (100 candidates) never comes within **20.73 deg** of that line. Our three
  written lines sit **63.57 / 43.64 / 20.78 deg** from it.
- `AxisExtraction/read_surfaces_nurbs.m` is NOT a different input path: it reads the same
  `Surfaces/Pot_*_Piece_*_Surface_{0,1}.xyz` and `extract_axis_nurbs.m` calls the same
  `run_potsac`. Do not spend a stage on "the NURBS variant".

**Stage A — MATLAB, all stages dumped (the decisive measurement).**
Run `AxisExtraction/run_potsac.m` (and `run_potsac` on the `(C0, C1)` 6-column surfaces exactly as
`extract_axis_nurbs.m` does) on `Pot_A_Piece_08_Surface_0.xyz` / `_Surface_1.xyz` on a compute
node. Dump, per stage: the candidate directions after `compute_axis_of_symmetry`, after the
stage-1 refine, the stage-1 Huber costs, what the 10 deg dedup removes, what the
`cost < cost(1) * 1.1` cut removes, the stage-2 (all-points) refined axes and their costs, and the
final order. Also run it on **Pot_A_Piece_07** (3 reference lines) and **Pot_A_Piece_01** (1) as
controls that already work. Report, for every dumped axis: angle to released line 0 and line 1 of
Piece 08, and angle to our port's top axis.

**Stage B — the same table from our port.** `sfs_axes/potsac.py` with the settings the corpus run
used (`step=10`), dumping the same per-stage rows. The difference table is the evidence; a
difference in ONE stage is a fix, a difference in the candidate pool at stage 0 is not.

**Stage C — decide.**
- **If MATLAB finds the line** (within 5 deg, and within 20.73 deg of the released second line):
  report the divergence and fix the port behind a switch, defaulting to whatever keeps the
  vs-MATLAB gate exact. Then the real target: **Pot A E2E with our own axes must reach 8/8 and
  15/15** — that is the only proof the fix works, and it must be produced WITHOUT reading the
  reference axes anywhere in the selection path.
- **If MATLAB does not find it**: say so plainly, record that the reference line is not reproducible
  from the shipped surfaces, make no change to `sfs_axes`, and leave the ticket's fix checkbox
  unticked with "NOT MET" written in — the same honesty ticket 303 was closed under.

**Stage D — the 302 instrument fix and its re-run (independent of A-C; do this even if nothing else
lands).** `canonicalize()` in the 302 stage scripts used to negate the whole `[dir; pos]` vector, so
**22 of the 163** written `out/axes302` files carry an anchor reflected through the origin
(Pot_A_07 725 mm off; Pot_B_03/04/05/09, Pot_D_26, Pot_E_03/06/27/29, Pot_H_05/06,
Pot_I_07/09/10/17/19/21/22, Pot_J_09/10/11). It is fixed on main (942fe1a). Re-run
`corpus302.py` into NEW paths with the fixed instrument, and report: (a) the direction numbers,
which must NOT move (median 6.81 deg, 44.2 % within 5 deg) — if they do, the fix changed something
it should not have; (b) the radial column, which is only now valid; (c) the same
generation for the Juglet lane if `juglet302.py` shares the write path (`grep canonicalize`).

**Rules**
- `bash /c/PR/scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/304-*.md`
  first. Status must still read `ready-for-agent` when you run it.
- SSH from this session is `/c/Windows/System32/OpenSSH/ssh.exe spartan` — git-bash's `ssh` cannot
  authenticate. Quote the whole remote command in single quotes or the remote `$R` expands
  locally.
- Runs go to `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
  `run.json`, `submit.sbatch`, `logs/`, `out/`, and a row appended to `runs/index.tsv` with the
  verdict columns left empty.
- MATLAB runs on a compute node, never the login node. Every `sbatch` gets a poll
  (`scripts/slurm_poll.sh <JOBID>`) and its final `sacct` State/ExitCode in the ticket.
- The reference axes and the ground truth may be read ONLY to score and to diagnose. Nothing in
  the shipped selection path may touch them — that is the difference between a fix and a cheat.
- No corpus file changes; md5 the `Surfaces` and `Axes` trees before and after.
- Renders to `/c/PR/SfSpp_preprocessing/artifacts/pota304/`: Piece 08's surface with the released
  two lines and our three lines drawn in distinct colours (the one picture the conservator needs),
  plus before/after assembly renders for any E2E claim.
- Comments-only ticket edits. Commit nothing; the lead lands it.
- Budget: 8 failed acceptance checks, then stop and report.

**Acceptance**
- [ ] A1 Stage A table exists for Pieces 08, 07 and 01, with every candidate at every stage, and
      the angles to the released lines are in it.
- [ ] A2 Stage B's port table covers the same stages and the divergence is named at a named line of
      code (file:line), not described in prose.
- [ ] A3 The verdict — reproducible from these surfaces, or not — is stated as one of the two
      explanations, with the numbers that decide it.
- [ ] A4 If and only if it is reproducible: the fix is behind a switch, the vs-MATLAB gate still
      passes on Pot A (≤0.01 deg / ≤0.01 mm over 3 pieces incl. the Jacobian), and the corpus
      re-run (163 pieces, NEW paths, corpus md5 unchanged) does not regress.
- [ ] A5 The end-to-end proof: Pot A assembled with OUR axes only reaches **8/8 sherds and 15/15
      joins**, with the job id and the `1. Acc.txt` quoted. If it does not, the checkbox stays
      unticked and says so.
- [ ] A6 Stage D: corpus302.py re-run with the fixed canonicalize, direction numbers unchanged,
      radial column now valid, and the affected 22 pieces named in the write-back.
- [ ] A7 Renders exist and are listed by path; job ids and their sacct State/ExitCode are in the
      comments; no corpus file changed.
