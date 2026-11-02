# 60 — Why does the break-stop test call J1's growth "break-like"? Test the full-body hypothesis and the normal field

**What to build:** a **diagnosis**, not a fix. Three read-only measurements that together
decide between three candidate explanations for ticket 59's contradiction, plus one debug-only
dump of the growth's candidate pool so the contradiction can be counted rather than guessed.

**Why now (2026-11-02, conservator):** after ticket 59's read-out the conservator chose this
run: "let's do the run comparing J1's cloud normals to its mesh. i think it might be because it
is a piece contain full 360 degree body". The lead's quick shape check (axis frame, 5 deg
azimuth bins) supports the premise: **J1 covers 360.00 deg of azimuth with a 0 deg
largest gap** -- i.e. it is a ring fragment with a top and a bottom break edge (see H1), J7 also wraps (360 deg, 2 deg gap), J2 wraps 0.94 (13 deg gap) and J9 0.85
(27 deg), while J3-J6 and J8 cover only 0.24-0.42 (219-279 deg gaps). J1 is also ten times the
mesh of J2 (24 294 vs 2 565 vertices).

**Answers:** U19, E1

**Blocked by:** none (reads ticket 59's run dir and the corpus read-only)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 60-j1-full-body-diagnosis, in /c/PR/worktrees/sfs/60
**Worker:** unassigned

## Spec

### Given (measured, from ticket 59, commit 8862864)

- Armed in the growth loop, J1's pairing test reports `npts=19312 wall_like=1674 break_like=17638`
  (8.7 % wall-like); J2 reports `npts=1883 wall_like=1647` (87.5 %) on nearly the same
  wall-like COUNT. Armed J1 collapses (S0 13 850 -> 351, genuine pairs 8/9); the other eight
  move -1 to -9 %.
- Offline on the same piece, 89-98 % of J1's wall points pair, and the mesh labels call 62.5 %
  of J1's faces wall. So the live test rejects candidates the offline test would accept.
- The live test (worker patch, run-dir provenance `work/patch.diff`, +111/-0, base 638504bf):
  ray cast along the candidate point's normal, window `[0.9, 7.2]` mm, `eps_mm=0.45`,
  `exit_dot=-0.4`; a candidate is admitted only if it pairs.
- The pieces' own measured wall thickness varies 1.876-2.839 mm; J1 is 1.876 mm.

### The three explanations this run must separate

- **H1 (conservator) — shape, restated 2026-11-02 after the lead got it wrong.** The lead's
  first reading ("full 360 deg, therefore no break edge") is **wrong**; the conservator corrected
  it (m03836): "no, it does have a break boundary, a 360 degree full body means it's cylindrical,
  it STILL have break edge at top and bottom". J1 is a **ring fragment**: one piece wrapping the
  whole circumference, so it has no break edge *around* its side, but it has a break edge at the
  **top and another at the bottom**, each running all the way round. A growth that encircles
  ends with its frontier lying along those two annular edges, and an edge point cannot pair --
  its ray leaves the shell at a grazing angle instead of crossing clay -- so the bag goes
  edge-dominated and the stop fires everywhere: the 91 % break-like bag. What the dump must show
  if H1 is right: the candidates cluster along the two annular break edges, not uniformly over
  the surface. (Workspace precedent: the Juglet is 2/9 ring fragments by count and 54 % by mass,
  and TORA's lessons.md records "I ruled out a breakage pattern the target object actually has".)
- **H2 — normals.** J1's cloud normals (the t47 corpus clouds, 840 666-841 413 points) disagree
  with its mesh: sign flips, or normals estimated across an edge on a closed 360 deg shell. A
  flipped normal makes every ray shoot outward into air -> no pair.
- **H3 — bookkeeping.** `npts` counts candidate *evaluations* across growth iterations, not
  distinct points; if so, J1's 19 312 is ten times J2's 1 883 because the piece is bigger, and
  the wall-like count ~1.65 k on both pieces is the real (piece-independent) wall population.

Only one of them is ruled in by the numbers; the run must say which, and must not stop at
"all three are possible".

### Plan

**A — shape audit (read-only, all nine).** In each piece's own axis frame
(`Dataset/Axes/Juglet/<piece>_Axis.xyz`): cast rays from the axis line outward at 72 azimuths x
several heights, count how many azimuths hit the mesh — a sector piece returns one contiguous
arc, a full body returns hits all the way round. Report per piece: azimuth coverage, largest
hit-free arc, radial profile, and the width of the fold band (the band where the surface turns
through 180 deg between outer and inner sheet). One render: J1 vs J7 vs J3 in the axis frame,
coloured by hit/miss.

**B — normal field (read-only, all nine).** For each piece compare the cloud the pipeline
actually reads (`Dataset/Point/Juglet/<piece>_Point.pcd`) with its mesh
(`Dataset/Mesh/Juglet/<piece>_Mesh.obj`): nearest-triangle assignment, then report the angle
between cloud normal and face normal (median, p90), the **sign-flip rate** (angle > 90 deg), and
the fraction pointing into the shell vs out. J1 against the other eight in one table; one J1
render coloured by agreement.

**C — the candidate pool (one debug build, J1 only).** Rebuild the t59 patch with a
debug-only env switch (`SFS_BREAK59_DUMP=<path>`) that writes, per candidate evaluation:
point id + coordinates, its pairing result, the iteration index. Run **J1 only**, two cells in
one job: gate-closed (dump on) and armed (dump on). Then classify each dumped candidate by
(a) its stage-0 face label from ticket 59's `out/labels/Juglet_Piece_1.npz`, (b) its
geodesic distance to the nearest rim/fold band, (c) whether it is a repeat evaluation of the
same point. Reproduce the 19312 / 1674 figures from the dump; if you cannot, say so - that is a
result.

### Gate (written by the lead before hand-over; the lead will re-run these)
1. The arm dump must reproduce ticket 59's J1 counts exactly (19312 / 1674 / 17638) or the
   diagnosis is reported void with the difference shown.
2. The gate-closed J1 with the debug build must write an S0 byte-identical (md5) to ticket 59's
   control J1 S0 (`passA` in run 20261102-1144_638504b_t59-breakstop-stage0). If it does not,
   the dump changed the path and the run is void.
3. A and B run on **all nine**; J1 must appear beside the other eight in one table.
4. Every claim names its type: measurement, inference, or guess.

### Deliverables
- Tables in the run dir, PNGs copied to `SfSpp_preprocessing/artifacts/60/` (gitignored).
- A **Results** section in this ticket: numbered findings, each tagged to H1, H2 or H3, with the
  number that supports it; then one paragraph saying which hypothesis is ruled in and what
  would be needed to act on it. No verdict on whether to merge anything - that is the lead's.
- Jobs: every `sbatch` with its `sacct` State/ExitCode.

### Budget
Two sbatch jobs, one hour wall clock, no GPU. Heavy work on compute nodes only.

### Do not
- Change any tracked source file; commit or push nothing.
- Touch the shipped defaults or any `SFS_*` behaviour; the dump switch must be inert unless set.
- Delete or rewrite ticket 59's run dir (read-only input).
