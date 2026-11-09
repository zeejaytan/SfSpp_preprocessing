# Ticket 322 — Generalise the axis finder: one method that also works on the Juglet

**Status:** ready-for-agent
**Answers:** E1
**Depends on:** none (reads 319/320/321 for context)
**Blocks:** none
**Worker:** cursor_code (dispatched 2026-11-10, this ticket is the brief)
**Budget:** large

## The ask

The axis finder now works on the ten sample pots and fails on the Juglet. The conservator's
ruling (2026-11-10): **do not patch the Juglet case.** Make the axis method general — one
formulation, no per-object special cases — so that it works on the Juglet and on objects we
have not seen yet, while the ten pots keep the numbers they have today.

Read this whole ticket before touching code. Everything below is context we have already paid
for. The questions at the end are yours to answer; the design is yours to choose. What is not
negotiable is that the answer generalises.

## What the method is today (map of the ground)

Code: `C:/PR/SfSpp_preprocessing/sfs_axes/`

| module | what it holds |
|---|---|
| `potsac.py` | the RANSAC-style sampler over candidate axes, the two candidate pools (cylindrical branch, conical branch), the guards and the ranking; `run_potsac_union` is the entry point |
| `cao.py` | Cao / biaxial-Cao residual (per-point since ticket 302) and its Jacobian |
| `refine.py` | Levenberg-Marquardt port of the authors' `refine_axis.m` / `optimize_using_lm.m` |
| `normalized.py` | distance-invariant (radial-distance-normalised) axis error, refine and ranking (ticket 312) — corrects the lever-arm bias of the raw Cao residual |
| `plucker.py`, `pottmann.py` | Plücker line machinery and the Pottmann 6-point symmetric-axis solver (port of `compute_pottmann_axis.m`) — present in the tree, not on the current path |
| `hybrid.py` | ticket 68's label-free juglet estimator; **default OFF, marked "do not enable on the corpus"** — read its docstring before assuming it is a candidate |
| `cli.py` | `extract-pot-a`, `--union` (the general path, `:103`), `--paper-chain` (the authors' chain, default) |

Current behaviour, in one line: sample axes, keep the ones whose inlier support survives two
branches — a cylindrical branch (`DEFAULT_CLEARANCE_MM <= d_c <= 250`, `mean_ax <= 0.50`,
8° drift) and a conical branch (25–105 mm, `0.50 < mean_ax <= 0.925`, `cw <= 0.0095`,
25° drift) — rank by the worse wall's normalised cost, dedup at 15°, write the top 6. Everything
is behind `--union` + `SFS_AXES_CONVERGE_BEFORE_RANK=1`; the paper chain is untouched by it.

## The evidence we have (verified by the lead, from the runs' own `score/acc.tsv`)

**Ten sample pots assemble on our axes** (ticket 319, jobs `20261109-1426_...`, two repeats and
the authors'-axes control arm each; Pot A after ticket 320's repair):

| pot | sherds | joins |
|---|---|---|
| A | 8/8 | 15/15 |
| B | 9/9 | 15/15 |
| C | 4/4 | 5/5 |
| D | 23–25/28 | 55–60/69 |
| E | 29–31/31 | 57–62/62 |
| F | 5/5 | 7/7 |
| G | 7/7 | 10/10 |
| H | 11/11 | 17/17 (authors' axes: 8–9/11) |
| I | 25/26 | 59/62 |
| J | 8/11 | 16/21 |

**At the axis level** (172 pieces, one reference answer per piece = the nearer of the released
`Axes/` and `Ground Truth Axes/`): rank-0 correct within 10° on **106/163** corpus pieces,
best-of-3 on **132/163**. Five pieces carry no scoreable reference (Pot C 01 and J 01 interior
edgelines, J 09 and C 03 Bl1 unscored).

**The Juglet fails** (`runs/20261110-0320_41494d0_t320b-juglet`, job `34617857`, COMPLETED 0:0):
0/9 sherds and 0/18 joins in all four arms — the authors' released axes and our top-3, two
repeats each. Our per-piece direction/position errors: p1 152.5°/614 mm, p2 18.1°/145, p3 9.0°/68,
p4 109.9°/503, p5 23.5°/40, p6 15.9°/148, p7 21.2°/55, p8 154.0°/524, p9 105.3°/804. Four pieces
are within 25° but 40–148 mm out; five are 105–154° out. On a vessel of this size that is
scatter, not a near miss.

**And the Juglet's answer key contradicts itself.** Transform the released
`Dataset/Axes/Juglet` axes by the `Dataset/Juglet_GT` transforms and the nine world-frame axes
should coincide; they spread **20–81°** (per piece 29.8, 44.4, 26.7, 20.8, 81.2, 32.4, 62.0,
79.3, 57.5), under all three frame conventions tested. The same arithmetic on pots gives
Pot G 1.6°, Pot B 5.4°, Pot A 5.6°, Pot H 33°. So one of those two Juglet files is not what it
claims to be, and every Juglet number we have — ours and the 5/9 axis column — is scored against
a key we cannot trust. The authors' own axes place only 2 of 9 juglet pieces in the same job.

Useful physical context for the Juglet (recorded in the ticket 317 analysis; **re-derive rather
than trust**): nine pieces including base and handle, a vessel roughly half the diameter of the
pots, and — measured on the released axes — pieces lying 0.8–14.7 mm from the axis with
per-piece `mean |axis·normal|` between 0.12 and 0.57. Both numbers sit outside what the
cylindrical branch's guards assume (25 mm minimum clearance, `mean_ax <= 0.50`).

## The questions

Answer these in writing, in the ticket, before you change behaviour. Numbers, not adjectives.

1. **Is the Juglet failure a regime gap in the method, or a broken reference?** Name which claim
   you are making: (a) the method failed, (b) the measurement is broken, (c) the reference is
   wrong. Given the 20–81° split, this has to be settled first — otherwise an "improvement" on
   the Juglet may be fitting noise.
2. **What is structurally different about that object, measured?** Per piece: size, extent,
   distance of the piece from the true axis, the distribution of `normal·axis`, the residual of
   a cylinder fit vs a cone fit vs a general surface-of-revolution fit. Say what the pots have
   that the Juglet does not, and vice versa. (A pot shoulder is a cone; a juglet body is neither
   cylinder nor cone; a handle is not a surface of revolution at all. Which pieces are which?)
3. **What one formulation covers all of it?** State the objective, the parametrisation, the
   robustifier, the ranking rule and the refusal test. Justify each choice physically. If the
   answer is a family of nested models selected by an evidence criterion (support, residual,
   complexity) rather than a gate on `mean_ax`, say so and say why it is not just a new patch.
4. **What is the Juglet's true answer key, and how do you know?** Derive one frame for that
   object — from the meshes, or by reconciling `Axes/Juglet` with `Juglet_GT` — and state which
   file you concluded is wrong if either is.
5. **Predict before you run.** Write down what the ten pots and the Juglet should do under your
   formulation, then run and report the difference.

## Constraints

- **No per-object, per-pot or per-piece special cases.** No constants keyed on a pot name, a
  piece count, a file name, or a piece id. A threshold that encodes a geometric fact is fine;
  a threshold that exists because the Juglet needed it is a patch and will be rejected.
- **The ten pots keep their numbers** (floors above). Any regression is reported, not absorbed.
- **One code path.** If the paper chain's default has to change, argue it; do not fork behaviour
  into two methods that both claim to be the method.
- **Build a fast loop first.** An axis-only benchmark over all 172 pieces that runs in minutes
  (on a Spartan compute node), so you are not queueing assemblies to iterate. The end-to-end
  assembler run is the final proof, not the development loop.
- **Heavy work on Spartan compute nodes only** — never the laptop, never the login node.
  MATLAB is available on compute nodes; its licence refuses on the login node.
- **Look before reporting.** Any geometry claim comes with a render. The lead session cannot see
  images; the conservator can, so leave the renders in `artifacts/pota322/renders/`.
- **Do not commit.** Write results and code into the working tree and the ticket; the lead
  verifies and lands.

## Definition of done

- [ ] Written answers to questions 1–5, with numbers, in this ticket.
- [ ] A stated general formulation, with the physical reason for each term and each threshold.
- [ ] Implementation in one path, no per-object branches; the ten pots' behaviour accounted for.
- [ ] Axis benchmark before/after on all 172 pieces: rank-0, best-of-3, best-of-6, per pot, plus
      the worst ten pieces named.
- [ ] Ten-pot end-to-end: no regression below the floors; job IDs and `sacct` State/ExitCode in
      the Comments block.
- [ ] Juglet: a reconciled answer key, and a measured verdict against it; if it cannot be
      reconciled, the evidence for that and an explicit stop — not a number against a broken key.
- [ ] Renders for any geometry claim, in `artifacts/pota322/renders/`.

## Where things live

- Code and CLI: `C:/PR/SfSpp_preprocessing/sfs_axes/` (`--union` at `sfs_axes/cli.py:103`).
- Axis sets to compare: `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-1350_e556fc8_t318a-axes/out/axes318`
  and `.../out/axes320` (181 files each; `axes320` = `axes318` + the Pot A base-disk repair).
- References: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes` (pots),
  `.../Ground Truth Axes`, `.../Ground Truth` (piece transforms `Pot_X_Piece_N_T.txt`).
- Juglet: `/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Axes/Juglet` (released axes),
  `.../Dataset/Juglet_GT` (transforms), surfaces under `.../Dataset/Surfaces/Juglet`.
- Juglet lanes (breaklines/segmentation used by the E2E):
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`.
- Assembly harness: `/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif`; the
  ticket 319 runs are the template for submit scripts.
- Earlier tickets that carry the detail: 302 (per-point Cao), 310 (union pool), 315 (conical
  shoulder), 317 (distance-invariant fit), 320 (base disk), 321 (generalisability + Juglet E2E
  with the reference-inconsistency table).

## Comments
