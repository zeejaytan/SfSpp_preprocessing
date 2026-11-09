# Ticket 322 — Generalise the axis finder: one method that also works on the Juglet

**Status:** resolved — 2026-11-10 (lead-verified; research only, nothing wired into the shipped path)
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

### Worker (cursor_code), 2026-11-10 — checkpoint 1: Q4, the Juglet's answer key

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes`
(`work/` = working-tree copy of `sfs_axes/` + the probes, `out/jugkey/`, `logs/jugkey*.log`).
Compute: holder job `34619050` (8 CPU, sapphire, spartan-bm206, `srun --overlap`); a 32-CPU holder
`34618986` is queued for the 172-piece benchmark. Probes (laptop copies):
`.scratch/pota-repro/t322/juglet_key.py`, `juglet_key2.py`.

**Q4 answer: `Juglet_GT` is right; `Dataset/Axes/Juglet` is wrong on most pieces, and it was never an
authors' reference.**

1. **Provenance.** `Dataset/Axes/Juglet/*` is our own MATLAB PotSAC output from 2026-09-16
   (`run_juglet_preprocessing.sbatch` Step 3 `matlab -batch run_juglet_axes`, staged by
   `run_ticket04_juglet.sh:5-6` "found in Juglet_Dataset_20260916/SfS_pp/Axes/"), run on the vertex-dump
   clouds. The Juglet is not in the paper's release; there are no "authors' juglet axes". The two
   `Dataset/Axes/Juglet` copies (`/data/gpfs/projects/punim2657/Dataset/...` and `.../sfs_preprocessing/Dataset/...`)
   are md5-identical.
2. **A third, independent witness.** `TORA/dataset/juglet_gt.hdf5` holds the nine pieces *assembled*, with
   the same vertex count and order as the scan-pose meshes `Dataset/Mesh/Juglet/Juglet_Piece_0N_Mesh.obj`.
   A similarity Procrustes on corresponding vertices fits every piece at **0.0001 mm RMS** (scale
   0.0141423 for all nine, i.e. 70.71 mm per hdf5 unit). That is each piece's true pose with no fitting choice.
3. **`Juglet_GT` agrees with it exactly.** Applied as `X_world = R·X + t` (the `T` convention), the nine
   `Juglet_GT` transforms equal the Procrustes poses up to one global motion to **0.000-0.002 deg** on all
   nine pieces. The inverse convention disagrees by 6.8-136.7 deg. Contact check in that pose: the 10
   touching neighbour pairs close to 0.011-0.030 mm; **8 of the 18 pairs in `Juglet_simple_graph.txt` do
   not touch at all in the true assembly** (1-5 3.3 mm, 1-6 3.6, 3-7 13.9, 4-5 4.9, 4-6 7.7, 5-9 18.0,
   6-8 0.62, 7-8 13.9, 8-9 18.8) — the E2E's "/18 joins" denominator carries 8 joins that cannot be made.
4. **One axis for the whole vessel**, fitted to all nine assembled pieces at once (60 000 area-weighted face
   samples, distance-invariant normal residual, Huber; `out/jugkey/key_report.json`): robust slice circles
   across it put the body centres (13 slices, z -25..+14 mm) within **0.11-0.87 mm** of the line; the
   body-only fit is **1.20 deg / 0.38 mm** from the whole-vessel fit, the neck-only fit 2.30 deg / 0.83 mm.
   The neck slices with the handle sit 4.0-5.1 mm off (handle points; trimmed circle residual 2-2.8 mm).
   Leave-one-piece-out: <= 0.8 deg except dropping piece 1 (neck, shoulder and handle zone, 39% of the
   clay; the base is piece 7, which reaches the axis, r_min 0.2 mm): 7.7 deg. **The vessel is small: max radius 16.3 mm (diameter ~33 mm), height ~60 mm** — not "half the
   pots": the pots run at 75-150 mm radius, so this object is 5-10x tighter.
5. **The key.** That axis mapped back into each piece's scan frame (`out/jugkey/key/Juglet_Piece_N_Axis.xyz`).
   The lane surfaces the axis finder reads (`outU_jug/geom/*.S0/.S1`) are in that same frame (S0 to mesh
   median 0.19-0.43 mm). With `Juglet_GT` the key maps to one world line for all nine pieces (spread
   0.00 deg) — the 321 inconsistency is entirely the axis file.
6. **Released (`Axes/Juglet`) vs key, direction deg / offset mm at the piece centroid:** p1 1.5/0.4,
   p2 **87.8**/15.9, p3 **31.8**/7.3, p4 10.7/2.5, p5 **44.5**/8.9, p6 13.3/3.0, p7 24.1/3.1 (line 2: 11.1/1.3),
   p8 12.8/2.8, p9 **73.3**/16.0. Within 10 deg: **1 of 9**. The 321 "20-81 deg" table used the `a`
   convention (no rotation); under the correct `R·a` the released lines still spread 4.7-82.0 deg, because
   they are wrong, not because the transforms are.
7. **axes320 vs key** (rank 0 ... rank 5, deg): p1 1.5, p2 14.1 (rank1 5.9), p3 18.5 (rank2 0.8), p4 2.1,
   p5 2.7, p6 12.7 (rank4 8.7), p7 6.3, p8 17.4 (rank4 6.5), p9 31.8 (best 31.8). **Rank 0 4/9, best-of-3
   6/9, best-of-6 8/9 within 10 deg.** Previously reported against the broken file as 0/9 rank 0, 5/9 K<=3.
8. **How sharp is the key per piece?** Starting at the key and refining the normalised cost on the piece's
   own two walls, the piece's own nearest surface-of-revolution optimum sits **1.5, 11.9, 25.4, 4.1, 2.7,
   2.1, 6.1, 25.3, 51.9 deg** from the vessel axis (p1..p9). On p3, p8 and p9 the piece's own data prefer a
   line 25-52 deg away (worse-wall cost at key 0.035/0.039/0.079 vs at the local optimum 0.022/0.020/0.023):
   on a handmade 1.8-mm-walled vessel a small sherd is not a precise surface of revolution about the
   vessel's axis. A per-piece score on those three is about the input, not the method.

Render: [juglet_key_vs_released_axes320.png](SfSpp_preprocessing/artifacts/pota322/renders/juglet_key_vs_released_axes320.png)
— panel 1 the assembled vessel with its one axis and the slice centres; panels 2-10 each piece square-on to
its key (green), the released line (red dashed), axes320 rank 0 (blue).

Claim type: for the Juglet's 0/9 axis column and the "inconsistent key" — **(c) the reference was wrong**
(our own Sept MATLAB output scored as if it were a reference). `Juglet_GT` stands.

### Worker, checkpoint 2: the fast loop and the first finding about the objective

- **Fast loop built.** `t322/dump_basins.py` reproduces `run_potsac_union`'s normalised pool exactly
  (10 seeds x 1000 Pottmann draws, 10-deg clustering), refines the 60 largest basins of every piece and
  stores scale-free features + the error against the reference for each. All 172 pieces in **85 s** on 8
  CPUs (holder 34619050) -> `out/basins_all.json` (laptop copy `artifacts/pota322/basins_all.json`).
  `t322/rank_rules.py` scores any ranking rule on it offline in seconds. Reference: pots = min(released
  lines, Ground Truth Axes line 0) (the 318/319 definition); Juglet = the key above.
- **Before column (axes320 files, same scorer):** pots rank-0 **107/163**, best-of-3 **133/163**,
  best-of-6 **137/163** (lead's 106/132 reproduced within one piece). Juglet against the key: **4 / 6 / 8 of 9**.
  The raw basin pool holds a line within 10 deg on **163/163** pots.
- **The current objective is not minimised at the true axis.** Starting LM on the distance-invariant
  normal cost *at the reference axis itself* moves it a median **6.4 deg**, >10 deg on **70/163** pot
  pieces, >20 deg on **52/163**; at the reference the worse-wall cost is often 2-20x higher than at the
  line it drifts to (Pot H 06: 0.070 vs 0.003, 82 deg away). Refining the pool's basins the same way
  drops the pool's coverage from 163 to 108. So no ranking on that cost can be right without priors —
  which is what the 25 mm / 250 mm / diag-65 / diag-140 / mean_ax gates in `potsac.py` have been doing.
  This is the structural answer to "why does every new object need a new gate".
- Next: `t322/profile_probe.py` tests a positional objective (profile thickness: about the true axis each
  wall collapses to a curve in the (r, z) plane).

### Worker, checkpoint 3: Q2 measured, the absolute-mm audit, and the profile objective

**Q2 — what is structurally different, measured** (`basins_all.json`, features at the reference axis;
r = distance of the wall points from the axis, L = piece bounding-box diagonal; lane surfaces):

| pot | n | L mm (med) | r_med mm (min-max) | r/L (med) | mean abs(n.a) (min-max) | Pottmann s2/s3 (med) |
|---|---|---|---|---|---|---|
| A | 8 | 125 | 79.5 (34.0-85.4) | 0.63 | 0.74 (0.51-0.96) | 4.4 |
| B | 9 | 113 | 71.8 (35.1-107.1) | 0.73 | 0.68 (0.34-0.88) | 7.4 |
| C | 6 | 130 | 43.0 (7.6-58.3) | 0.29 | 0.45 (0.26-0.95) | 2.9 |
| D | 32 | 116 | 65.7 (3.8-97.4) | 0.48 | 0.38 (0.10-0.97) | 5.0 |
| E | 34 | 100 | 56.1 (20.5-81.0) | 0.49 | 0.31 (0.09-0.93) | 4.5 |
| F | 7 | 55 | 42.6 (18.4-46.1) | 0.66 | 0.58 (0.36-0.88) | 4.2 |
| G | 7 | 79 | 39.8 (21.9-44.2) | 0.44 | 0.63 (0.59-0.71) | 4.5 |
| H | 11 | 102 | 45.8 (15.9-68.6) | 0.39 | 0.92 (0.06-0.98) | 11.8 |
| I | 30 | 112 | 56.6 (7.7-80.1) | 0.50 | 0.29 (0.16-0.97) | 4.6 |
| J | 19 | 61 | 27.9 (6.5-57.5) | 0.38 | 0.79 (0.22-0.94) | 3.2 |
| **Juglet** | 9 | **34** | **15.7 (11.3-16.5)** | **0.47** | 0.20 (0.15-0.67) | **1.9** |

- **In units of its own size the Juglet is an ordinary sherd set**: r/L 0.47, inside the pots' 0.29-0.73.
  What is different is (i) **absolute millimetres** — every piece's wall sits 11-16 mm from the axis,
  where the pots' medians are 28-80 mm — and (ii) **identifiability**: Pottmann's reduced 3x3 system has
  its second-smallest singular value only 1.9x the smallest (pots 2.9-11.8x). That ratio is ~1 for a
  sphere (every line through the centre is an axis) and large for a cone or a cylinder; the Juglet's
  globular body is the nearest thing in the corpus to a sphere, so its patches pin the axis direction
  least of all objects. Pieces: p7 is the base (the axis passes through it, r_min 0.2 mm); p1 is neck +
  shoulder + handle root (the handle is not a surface of revolution — it is what the robust trim has to
  discard); p2-p6, p8, p9 are globular body wall (r 14-18 mm; slice radius 14.3-16.3 mm over the 34 mm
  of body height, i.e. a near-spherical belly — principal curvatures not measured per piece).
- Pot shapes: H is the shallow dish (mean abs(n.a) 0.92 — normals almost parallel to the axis); C, D,
  E, I are mostly near-cylindrical walls (0.29-0.45); A, B, F, G, J mixed / conical (0.58-0.79).
- Not done, recorded as remaining: the per-piece cylinder vs cone vs free-profile residual table. The
  profile-thickness objective below is the free-profile fit and subsumes it for the ranking question.

**Absolute-millimetre thresholds in the current code — each asks a different question on a 33-mm vessel:**

| where | constant | what it means on the pots | what it does on the Juglet |
|---|---|---|---|
| `normalized.py:20` `DEFAULT_CLEARANCE_MM` | 25 mm min axis-to-centroid distance, `worst_wall_normalized_cost` penalty `1000*(25-d)^2` (`:200-203`), cylinder branch `potsac.py:531,557`, cone branch `:576,593` | "a wall is at least a few cm from its axis" | **excludes the true axis of every non-base piece** (r 11-16 mm) — the real axis is penalised as a "centroid-slicing decoy" |
| `potsac.py:171` `MAX_CLEARANCE_MM` | 250 mm | "no vessel wider than 50 cm" | irrelevant |
| `normalized.py:204` | penalty beyond 200 mm | same, as a soft term | irrelevant |
| `is_base_fragment` `normalized.py:125-171` | `d_c < 25`, `r_base_thresh = 25`, `z_extent >= 15` mm | "the base disk is ~5 cm across and 1.5 cm tall" | a 33-mm vessel's whole body is "near the axis"; the 15-mm z-extent is half the vessel |
| `potsac.py:482` Regime 1 | `w_dc <= 15.5` mm, `diag <= 65` mm, `min_hcw <= 38` (raw Cao Huber, units of mm) | — | **this is the switch that sends the Juglet down a separate branch**: a small-object patch keyed on size |
| `potsac.py:497,501` | `dcs >= 16`, `d_ref <= 22` mm | — | Juglet-branch internals |
| `potsac.py:516-520` `r_prior` | knee 30/40 mm, `diag >= 140`, `d > 120` mm | "an axis 3-12 cm from the sherd" | a 15-mm axis pays the knee penalty |
| `potsac.py:525` `max_drift` | `diag >= 140` mm | "big sherd => allow 25 deg LM drift" | never fires |
| `potsac.py:575,590-591` wall-skewer veto | `diag > 65` mm | Pot E skewers | never fires |
| `potsac.py:593-594` cone / dish windows | `d_ref` 25-110 mm, 35-115 mm | "cone/dish axis 3-11 cm away" | true axis outside both windows |

Draw-count gates (`sz >= 20, 50, 100, 1500, 4000, 6000`) are not mm but depend on the pool size, and the
normalised-cost gates (`cw <= 0.0065 / 0.0085 / 0.0092 / 0.0095`, `mean_ax` windows) are dimensionless
but were each set to separate named pieces. **Scale-free replacement:** no distance constant at all in the
ranking; the score is the profile thickness below, compared only between candidates of the same piece, so
its unit cancels. Where a distance must be judged it is judged against the piece's own size L
(the Nelder-Mead position step is 0.1 L).

**The profile-thickness objective (`t322/profile_probe.py`).** About the true axis every wall maps, in
the (r, z) plane, onto one curve — whatever the shape (cylinder, cone, dish, globular body, base). For an
axis v: map each wall to (r, z); for every point take its 24 nearest neighbours in that plane and the
smallest principal standard deviation of the neighbourhood (how far the local profile is from a curve);
the wall's cost is the mean of the best 80% (the trim discards non-revolved parts: handles, chips,
mis-segmented rim); the piece's cost is the mean of the two walls. It is position-based (mm on the
piece's own points), so it does not depend on normal estimates, and it has no lever arm.

Run on the same pool (`out/profile_probe.json`, all 172 pieces):

| | normal cost (current objective) | profile thickness |
|---|---|---|
| refine from the reference axis: median drift, pots | 6.4 deg | **1.5 deg** |
| ... drift > 10 deg, pots | 70 / 163 | **9 / 163** |
| ... drift <= 5 deg, pots | — | 143 / 163 |
| pool ranked by it, rank 0 within 10 deg, pots | 107 (axes320 with all its gates) | **114** (no gates) |
| same, Juglet vs key | 4 / 9 | **6 / 9** |

Per pot rank 0 (profile, no refinement / axes320): A 7/6, B 5/5, C 4/4, D 22/23, E 27/23, F 3/4,
**G 3/7**, H 10/10, I 22/18, J 11/7, Juglet 6/4. The G and F losses are not the objective's: on G 05/06/07,
F 05/06 and B 09 the reference axis is **cheaper** than every pool entry, but the pool's entries had all been
refined on the normal cost onto that cost's optimum 10-22 deg away. So the fix is to refine on the profile
cost too — run as `t322/profile_rank.py` (pool -> profile score -> 15-deg dedup -> Nelder-Mead on the
profile cost for the top 8 -> re-rank), in progress at the time of writing (`logs/profile_rank.log`).

### Worker — answers to Q1 and Q3 (Q2 and Q4 above; Q5 with the table)

**Q1. Regime gap or broken reference?** Both, in that order of size, and a third thing on the E2E.
- **(c) the reference was wrong** — the dominant cause of the "0/9" and "20-81 deg" story.
  `Dataset/Axes/Juglet` is our own Sept MATLAB output, 1 of 9 within 10 deg of the mesh-derived key
  (checkpoint 1). Against the key, axes320 is 4/9 rank 0, 6/9 best-of-3, 8/9 best-of-6 — not 0/9.
- **(a) the method failed, by construction, on the rest.** The finder's gates are absolute millimetres
  (table in checkpoint 3): the 25-mm clearance penalises the Juglet's true axis on every non-base piece,
  so the Juglet only gets candidates at all through the size-keyed "Regime 1" branch
  (`potsac.py:482`, `diag <= 65 mm`). Underneath the gates, the objective itself is not minimised at
  the true axis on 70 of 163 pot pieces (drift > 10 deg from the reference) — the gates exist to
  compensate for that, and they do not transfer to a 5-10x smaller object.
- **(b) the measurement is partly broken on the E2E:** 8 of the 18 joins in `Juglet_simple_graph.txt`
  are between pieces that do not touch in the true assembly (0.6-18.8 mm apart), so "/18" carries 8
  joins nobody can make; the honest join denominator is 10 (as ticket 07 already said).
- **Input ceiling:** on p2, p3, p8 the piece's own surfaces prefer a line 12-25 deg from the vessel axis
  under both objectives (normal cost 11.9 / 25.4 / 25.3 deg; profile cost 13.1 / 5.0 / 3.3 deg from the
  key when refined from it, but the pool's cheapest basin is 11.9 / 25.3 / 16.2 deg away). A handmade
  1.8-mm wall 15 mm from its axis is not a precise surface of revolution over a 30-mm sherd.
  Ceiling expected: 6/9 at rank 0; p2/p3/p8 are input-limited, not method misses.

**Q3. One formulation.**
- **Objective:** profile thickness (`sfs_axes/profile.py`): map each wall to (r, z) about the line;
  cost = trimmed mean (best 80%) of each point's local thickness (smallest principal std of its 24
  nearest neighbours in that plane); piece cost = mean over the two walls. *Why:* the defining property
  of a surface of revolution is that its meridian sections coincide — every shape a sherd can come from
  (cylinder, cone, dish, globular belly, base) collapses to a curve about its axis and to a 2-D smear
  about any other line. It uses positions, not estimated normals, and has no lever arm.
- **Parametrisation:** a line = unit direction + foot point nearest the piece centroid; refinement
  moves two direction tilts and two foot shifts, the shifts in units of 0.1 x the piece's own
  bounding-box diagonal L (so the search is the same shape on a 30-mm and a 300-mm sherd).
- **Robustifier:** the 80% trim. *Why:* a sherd carries non-revolved material (handle roots, chipped
  edges, segmentation spill onto the break face); a trimmed mean drops the worst fifth without any
  threshold in millimetres. The 20% is a fraction of the sherd, not a size.
- **Candidates:** unchanged — the union of Pottmann 6-point basins over 10 seeds (the pool already
  holds a line within 10 deg on 163/163 pot pieces). Each basin enters as its raw representative and its
  normal-cost refinement; both are scored.
- **Ranking:** ascending profile cost -> 15-deg dedup -> refine the best 8 on the profile cost
  (Nelder-Mead) -> re-score -> 15-deg dedup -> write up to 6. No shape classes, no branch on size, no
  base exception, no clearance window, no prior on radius: the base disk, the cone, the dish and the
  globular belly are all the same test.
- **Refusal test:** none that withholds an axis — the assembler needs a line per piece. Ambiguity is
  carried by the candidate list instead: where two distinct axes explain the piece almost equally (the
  near-spherical Juglet belly, Pottmann s2/s3 ~1.9), both are written and the assembler's geometry
  decides. The ratio cost(2nd distinct)/cost(1st) is reported per piece as the identifiability number.
- **Why this is not a new patch:** it deletes every millimetre constant from the ranking (the only
  length that appears is 0.1 L, a step size for the search, and the trim fraction 0.8 / neighbourhood
  k = 24 are counts); it is one path for every object; and it was chosen because its minimum sits at the
  reference axis (median drift 1.5 deg on the pots, 9/163 > 10 deg) — a property measured on the pots,
  before looking at what it does to the Juglet ranking.

### Worker, checkpoint 4 (partial): the profile ranking end to end, first 48 pieces

`t322/profile_rank.py` running in holder 34619050 (`logs/profile_rank.log`, ~3 pieces/min, all 172 due
~05:00). First 48 pieces (A, B, C, part of D), within 10 deg: **profile ranking rank-0 42, best-of-3 47,
best-of-6 47; axes320 36 / 40 / 40.** Gains at rank 0: A 08, B 02, B 06, B 08, B 09, C 04, C 05, D 21,
D 24. Losses at rank 0: **A 06 (35.0 vs 6.8 deg), C 06 (23.9 vs 3.0), D 32 (86.0 vs 2.2)** — to be checked
against best-of-3 before any claim about Pot A's end-to-end floor (Pot A is the pot that collapsed in 319
when one rank-0 moved).

### Worker, checkpoint 5: implementation drafted (working tree, not committed) and axes322 submitted

Implemented because the partial offline table (48 pieces: rank-0 42 vs 36, best-of-3 47 vs 40) already
supported it; to be reverted if the full table does not.

- **New `sfs_axes/profile.py`:** `wall_thickness`, `profile_cost`, `refine_axis_profile` (Nelder-Mead,
  shift step 0.1 x piece diagonal), `stride` — the objective of checkpoint 3, byte-for-byte the procedure
  `t322/profile_rank.py` benchmarks.
- **`sfs_axes/potsac.py`:** the normalised branch of `run_potsac_union` keeps its pool (10 seeds x 1000
  Pottmann draws, 10-deg clustering) and now ends in one call, `_rank_by_profile`. **Deleted** (old lines
  472-649): Regime 1 (`w_dc <= 15.5`, `diag <= 65`), `r_prior` (knees 30/40 mm, 120 mm), the cylindrical
  branch (25-250 mm clearance, `mean_ax <= 0.50`, 8/25-deg drift, `diag >= 140`), the conical/dish/flat
  branch (25-110 mm, 35-115 mm, `cw` windows, `sz >= 6000`), the base-disk exception and its wall-skewer
  veto (`diag > 65`, `sz < 4000`, `cw > 0.0065`), and the cone-promotion rule. `MAX_CLEARANCE_MM` removed.
  New constants are counts only: `PROFILE_BASINS 60`, `PROFILE_NREF 12000`, `PROFILE_NORMAL_ITERS 60`,
  `PROFILE_REFINE_K 8`, `PROFILE_DEDUP_DEG 15`. The paper chain (`run_potsac`) and the non-normalised
  union path are untouched; `normalized.py` is untouched (its 25-mm helpers are now used only by tests
  and `is_base_sherd`).
- **Tests** (run on the compute node, holder 34619050, TORA env, the file's own `__main__` runner — the env
  has no pytest): all 13 existing `tests/test_normalized.py` pass on the new ranker, including the five
  union-path shape tests written for the old branches (conical shoulder, flared bowl, 8-mm "miniature",
  shallow dish, 200-mm base disk with its 2-deg bar). Added `test_profile_ranking_is_scale_free`: one
  synthetic globular belly at 0.2x, 1x and 5x — rank 0 within 5 deg at every scale and the 0.2x / 5x axes
  within 1 deg of each other: **PASS**. `tests/test_regression_pota.py` cannot run under the plain runner
  (one test needs pytest's `monkeypatch`); it covers the paper chain only, which is unchanged.
- **Production set submitted:** `axes322` = the new code through the unchanged 318/320 writer
  (`run_benchmark_172.py`), job **34619465** (24 CPU, sapphire), output
  `runs/20261110-0415_d628fc0_t322-axes/out/axes322`, code md5s in `out/axes322_code.md5`.
  Next: score it with `dump_basins.py --before out/axes322` (same scorer as the before column), confirm it
  equals the offline `profile_rank` table, then the pot end-to-end.

### Worker — synthetic tests: what they cover and how to re-run them

Re-run (compute node; the TORA env has no pytest, so use the file's own runner):
```
cd <tree with the working-tree sfs_axes/ and tests/>
srun --jobid=<holder> --overlap -n 1 -c 2 /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 tests/test_normalized.py
```
Result 2026-11-10 (copy at `runs/20261110-0415_d628fc0_t322-axes/impl/`): **14/14 PASS** (13 pre-existing +
the new one; the new one was also run on its own -> `PASS scale`). Use `-n 1`: with `-c 2` alone in an
8-CPU holder srun starts four copies.

What goes through the new ranker (`run_potsac_union(..., normalized=True)`, 3 seeds, noise-free patches):
| test | synthetic sherd | bar |
|---|---|---|
| `test_conical_shoulder_retains_true_axis_at_rank_0` | 45-deg cone, r 55/51 mm, 60-deg arc | rank 0 < 5 deg |
| `test_flared_conical_bowl_promotes_cone_at_rank_0` | 38-deg bowl, r 38/34 mm, 70-deg arc | rank 0 < 5 deg |
| `test_tight_radius_miniature_regime` | cylinder r 8/6 mm, 20 mm tall, 120-deg arc | rank 0 < 5 deg |
| `test_shallow_dish_regime` | 75-deg dish, r 60/56 mm, mean abs(n.a) > 0.925 | rank 0 < 5 deg |
| `test_large_base_fragment_not_vetoed` | 200-mm flat base disk with upturned foot ring | rank 0 < 2 deg |
| `test_profile_ranking_is_scale_free` (new) | globular belly r(z)=16-0.02z^2, 1.8-mm wall, 80-deg arc, at 0.2x / 1x / 5x | rank 0 < 5 deg at each scale; 0.2x vs 5x axes < 1 deg apart |

The other 8 tests exercise `normalized.py` helpers (residual, Jacobian, sign invariance, LM convergence,
the 25-mm clearance penalty, the base classifier) — unchanged code, still green. Each of the five shape
tests was written for one branch of the old ranker; all five pass on the single profile rule, which is the
point. `tests/test_regression_pota.py` (paper chain, untouched) needs pytest's `monkeypatch` and was not run.

### Worker — checkpoint 6: axes322 scored; decision: keep the splice, run the pot end-to-end

**axes322** = the working-tree `sfs_axes` (profile-thickness ranking) on all 172 pieces: Slurm **34619465**,
sacct `COMPLETED 0:0`, elapsed 00:04:12, 181 files (163 pot pieces + 9 Juglet + 9 alt-named). Output
`runs/20261110-0415_d628fc0_t322-axes/out/axes322/`. Scored with the same reference as every table above
(pots: min over released lines and Ground Truth line 0; Juglet: mesh-derived key), script
`.scratch/pota-repro/t322/score_set.py`, raw output `out/score_320_vs_322.txt`.
verified: `score_set.py out/jugkey axes320=... axes322=...` -> pots 107/133/137 vs 135/146/151.

Pieces whose axis lands within 10 deg of the reference, axes320 (before) -> axes322 (after):
| pot | n | rank 0 | best of 3 | best of 6 |
|---|---|---|---|---|
| A | 8 | 6 -> 6 | 6 -> 8 | 6 -> 8 |
| B | 9 | 5 -> 9 | 6 -> 9 | 6 -> 9 |
| C | 6 | 4 -> 5 | 5 -> 6 | 5 -> 6 |
| D | 32 | 23 -> 27 | 26 -> 29 | 28 -> 30 |
| E | 34 | 23 -> 32 | 33 -> 33 | 33 -> 33 |
| F | 7 | 4 -> 6 | **7 -> 6** | **7 -> 6** |
| G | 7 | 7 -> 7 | 7 -> 7 | 7 -> 7 |
| H | 11 | **10 -> 9** | 10 -> 11 | 10 -> 11 |
| I | 30 | 18 -> 25 | 24 -> 27 | 25 -> 28 |
| J | 19 | 7 -> 9 | 9 -> 10 | 10 -> 13 |
| **pots** | **163** | **107 -> 135** | **133 -> 146** | **137 -> 151** |
| Juglet | 9 | 4 -> 6 | 6 -> 8 | 8 -> 8 |

The assembler is fed the top 3 lines, so best-of-3 is the column that reaches the end-to-end. Pieces that
**lose** at best-of-3 (before -> after, deg): D29 4.99 -> 10.95, D32 2.19 -> 85.34, E29 9.87 -> 10.73,
F06 2.01 -> 14.70, I20 6.75 -> 21.58, J08 6.88 -> 12.62, J19 6.19 -> 33.48 (7 pieces). Pieces that **gain**
at best-of-3: A07, A08, B02, B06, B09, C05, D21, D23, D25, D27, D30, E34, H11, I17, I24, I27, I30, J04, J07, J10
(20 pot pieces; per-pot deltas add up to the table). Juglet at best-of-3: gains 6, 8, 9, loses 2 (5.9 -> 13.2). Rank-0 losses: A06 6.8 -> 35.0 (its best-of-3 still 3.9), C06 3.0 -> 23.9 (1.2), D32, F06, H08 1.2 -> 18.5
(1.6), E29, J08, J19, Juglet 7 6.3 -> 47.9 (2.6). Worst rank 0 after: J17 88.0, J13 86.8, J19 86.7,
D32 86.0, I29 71.0, D26 69.1, E14 50.3, Juglet 7 47.9, H11 45.2, J18 45.1, J16 37.2, A06 35.0.
D29 is the piece whose released axis file is itself defective (ticket 301), so its reference is half-suspect;
D32 has only two basins after the 15-deg dedup and both are wrong.

**Decision: keep the splice.** It is better on the pots, not only on the Juglet: +28 pieces at rank 0, +13 at
best-of-3, +14 at best-of-6, and no pot falls at best-of-3 except **Pot F (7 -> 6, piece 06)** — reported,
not absorbed; the end-to-end below decides whether it costs F a seat. Axes322 reproduces the offline
`profile_rank` partial table piece for piece where they overlap (A06 35.0, C06 23.9, D32 86.0).

### Worker — checkpoint 7: pot end-to-end on axes322 submitted (10 jobs, 2 repeats each, K=3)

Each run is the ticket 319 run of that pot with only these edits (verified by `diff` on Pot F): axes dir ->
`runs/20261110-0415_d628fc0_t322-axes/out/axes322`; the authors' `_MO` control arm dropped (on record in 319);
24 CPUs / 96G instead of 48 / 160G (two arms instead of four); job name. Same lanes, NAMED, NP, FLOOR=50,
staging (`stage305.py`), assembler SIF, scorers and corpus md5 gate. Generator:
`.scratch/pota-repro/t322/make_e2e_runs.sh` (also writes `run.json` and the `runs/index.tsv` row).
The code that built axes322 is the working tree as it stands: verified: md5 of laptop `sfs_axes/potsac.py`
`0b0cf42f...`, `profile.py` `91662c33...`, `normalized.py` `444a0ae1...` -> identical to `out/axes322_code.md5`.

| pot | run | job | floor to hold (from the ticket) |
|---|---|---|---|
| A | `20261110-0420_d628fc0_t322-potA` | 34619671 | 8/8 sherds, 15/15 edges |
| B | `..._t322-potB` | 34619672 | 9/9, 15/15 |
| C | `..._t322-potC` | 34619673 | 4/4, 5/5 |
| D | `..._t322-potD` | 34619674 | 23-25/28 |
| E | `..._t322-potE` | 34619676 | >= 30/31 |
| F | `..._t322-potF` | 34619677 | 5/5 (watch: F06 best-of-3 2.0 -> 14.7 deg) |
| G | `..._t322-potG` | 34619678 | 7/7, 10/10 |
| H | `..._t322-potH` | 34619679 | 11/11, 17/17 |
| I | `..._t322-potI` | 34619680 | 25/26 |
| J | `..._t322-potJ` | 34619681 | 8/11 |

All ten PENDING (Priority) at submission. Results go in `<run>/score/acc.tsv`; sacct State/ExitCode to be
recorded when they finish. Holder 34619050 cancelled (no longer needed). The axes run itself now has
`run.json` and an index row (`20261110-0415_d628fc0_t322-axes`, job 34619465).

### Worker — checkpoint 8: the Pot F 06 regression, diagnosed

**The candidate pool did not change; only the ranking moved.** The union pool is the same code and the same
draws as before (the splice replaced only what happens after `_cluster_union`). In `basins_all.json` piece F06
has 126 basins; basin 7 (297 draws) has a raw representative 2.0 deg from the reference — the very line
axes320 shipped at rank 0. Its normal-cost refinement drifts to 10.6 deg, like most of the other basins (the
whole cluster of normal-refined lines sits at 10.6 deg).

Probe on a compute node (job 34619756, `t322/f06_probe.py`, output `out/f06_probe.txt`; L = 46.4 mm,
walls 1106 / 1571 points):
| line | error vs reference | profile cost (mm) | angle to shipped rank 0 |
|---|---|---|---|
| shipped rank 0 (axes322) | 14.7 deg | 0.0231 | — |
| the reference itself | 0 | 0.0298 | — |
| profile optimum refined from the reference | 1.5 deg | 0.0282 | 13.2 deg |
| profile optimum refined from basin 7 raw (2.0 deg) | 1.3 deg | 0.0288 | 15.9 deg |
| profile optimum refined from basin 1 normal-refined (10.6 deg) | 6.6 deg | 0.0300 | 21.1 deg |
| profile optimum refined from basin 12 raw (12.9 deg) | 14.0 deg | 0.0276 | 0.7 deg |

Two separate things went wrong, and only one of them can be fixed by the ranker:
1. **Rank 0 — the objective, not the search.** The true basin's own optimum is 22-25% *dearer* than the
   line 13-16 deg away. Physically the piece is a short band of a wide vessel: radius 35-50 mm about the
   reference axis (median 44 / 48 mm), only 20-26 mm tall, so tilting the axis by ~14 deg smears its (r, z)
   profile less than the wall's own unevenness does. No ranking rule built on this cost puts the true axis
   first here. Corpus-wide this "objective prefers a wrong line" class is 16 of the 18 best-of-3 misses
   (D26, D29, D32, F06, I20, I25, I28, J08, J11, J12, J13, J14, J16, J17, J19, Juglet 2); the other two
   (E29, J18) are search misses where the true optimum is cheaper but was not reached.
   verified: `profile_probe.json` truth_refined_cost vs `profile_rank.json` ranked[0].s, per piece.
2. **Best-of-3 — a dedup artefact.** Refined, basin 7's raw line reaches 1.3 deg at 0.0288; it is 15.9 deg
   from the winner, survives the final 15-deg dedup and would be the second line written, rank 1 (the next distinct line costs
   0.0365). It was never refined: the *pre-refinement* 15-deg dedup compares an unrefined representative
   (cost 0.0814) with already-refined neighbours (0.0343), and basin 7's raw line is **12.5 deg** from them
   (verified: angle(raw basin 7, ref basin 16) from `basins_all.json` -> 12.5), so it is discarded as a
   duplicate before it is ever polished.

**One principled adjustment, declared before it is run:** the ranker's dedup radius 15 deg -> **10 deg**,
both places. Reason, independent of F: 10 deg is what this pipeline already calls "the same axis" — the
union clusters its draws into 10-deg basins (`_cluster_union`, `DEDUP_COS`) on the paper's own duplicate
rule (paper:175, "axes within 10 deg"); the 15 deg in `PROFILE_DEDUP_DEG` was my choice and was never
measured. It is not an F constant (no piece, pot or size enters it) and it is the only variant run.
**Acceptance, fixed now:** pots best-of-3 >= 146 overall, no pot below its axes322 best-of-3, Pot F
best-of-3 = 7, Juglet best-of-3 = 8. If any fails, 15 deg stays and F06 is recorded as an accepted
single-piece cost (reason: item 1 above). No second variant either way.

### Worker — FINAL READ-OUT for review (supersedes nothing above; consolidates it)

**Q1 (final).** Three claims, in order of size. (c) **The reference was wrong:** `Dataset/Axes/Juglet` is our
own September MATLAB output and is within 10 deg of the mesh-derived key on 1 of 9 pieces (checkpoint 1).
(a) **The method failed by construction** on the rest: its gates were millimetre windows sized on pots
(checkpoint 3 audit), and under the gates its normal cost is not minimised at the true axis (>10 deg drift
on 70 of 163 pot pieces). (b) **The Juglet end-to-end measurement is partly broken:** 8 of its 18 graph
joins are between pieces that do not touch; the honest denominator is 10. Predicted Juglet ceiling: 6 of 9
at rank 0, with p2 / p3 / p8 input-limited. Result on axes322: 6 of 9 at rank 0, but a different 6 —
p8 now passes (3.1 deg) and p7, the base, fails at rank 0 (47.9 deg) while its second line is at 2.6 deg.
Best-of-3 is 8 of 9; the miss is p2 (13.2 deg), one of the three predicted input-limited pieces.

**Q2 (final).** Measured in checkpoint 3: the Juglet sits inside the pots' range on every scale-free
feature (piece size relative to its distance from the axis, r/L 0.47 against 0.29-0.73) and outside it
only in absolute millimetres (median radius 15.7 mm against 28-80) and in how sphere-like the surface is
(Pottmann s2/s3 1.9 against 2.9-11.8 — a near-spherical belly lets more than one axis fit). **Not done:**
the per-piece cylinder / cone / free-profile residual table the question asked for. The profile objective
made that classification unnecessary for the ranking, but the table itself was not produced.

**Q3 (final)** stands as written in "answers to Q1 and Q3", with one correction found in checkpoint 8:
the 15-deg dedup radius in the ranker was not a measured choice (variant 10 deg under test, job 34619792,
acceptance fixed in checkpoint 8).

**Q5.** The prediction for the pots was the offline `profile_rank` table — first 48 pieces written in
checkpoint 4 before any implementation (rank 0 42 vs 36, best-of-3 47 vs 40). The full offline table
finished at the same time as axes322 was scored, so it is not a prediction for the other 124 pieces. The
implementation reproduced it piece for piece where they overlap: 146 pot pieces at best-of-3 both
offline and in axes322. The end-to-end prediction is that every pot holds its floor, except that Pot F
may lose a seat through piece 06. That is unmeasured: the ten jobs are queued.

**Axis before/after (all 172 pieces):** the table in checkpoint 6 is final for the shipped code (15-deg
dedup). Pots: rank 0 107 -> 135, best-of-3 133 -> 146, best-of-6 137 -> 151 of 163. Juglet: 4/6/8 -> 6/8/8.
Worst ten at rank 0 after: J17 88.0, J13 86.8, J19 86.7, D32 86.0, I29 71.0, D26 69.1, E14 50.3, Juglet 7 47.9,
H11 45.2, J18 45.1.

#### The code, reviewable from here

**New module `sfs_axes/profile.py` (80 lines, numpy / scipy only)** — the profile-thickness objective.
*What it is:* a cost for a candidate axis line that is low when both walls of the sherd are surfaces of
revolution about that line. Every wall point maps to (r, z): r is its distance from the line, z its
position along it. About the true axis the wall becomes one curve, the vessel profile; about any other
line it becomes a 2-D smear. The cost is how thick that smear is, in the piece's own millimetres.
*Interface* (axis lines are `vt` = 6-vector, direction then foot point; walls are (6, m) arrays of
xyz + normal, of which only the xyz is read):
| name | signature | returns |
|---|---|---|
| `PROFILE_K` = 24 | constant | neighbours per point in the (r, z) plane |
| `PROFILE_KEEP` = 0.8 | constant | fraction of points kept (best 80%) — the robustifier |
| `PROFILE_POINTS` = 2500 | constant | stride target per wall (cost evaluation budget) |
| `stride(X, n=2500)` | (6, m) -> (6, <= n) | deterministic every-k-th subsample |
| `wall_thickness(vt, X, k, keep)` | -> float mm | per point: smallest principal std of its k nearest (r, z) neighbours; trimmed mean |
| `profile_cost(vt, walls)` | -> float mm | mean of `wall_thickness` over the walls |
| `refine_axis_profile(vt, walls, centre, size, maxfev=400)` | -> (vt, cost) | Nelder-Mead over 4 parameters: 2 direction tilts, 2 foot-point shifts in units of 0.1 x `size` (the piece's bounding-box diagonal); xatol 1e-4, fatol 1e-5 |
*When it runs:* only inside `run_potsac_union(..., normalized=True)` — the default pool path behind
`--union` (and `run_benchmark_172.py`), through `potsac._rank_by_profile`. It is never called on the paper
chain (`--paper-chain` / CLI default calls `run_potsac`), nor on the non-normalised union path.
*What it replaced:* the ranking that followed the pool in `run_potsac_union` — Regime 1 (`diag <= 65 mm`),
the radius prior, the cylindrical / cone / dish / flat branches with their 25-250 mm clearance windows, the
base-disk exception and its wall-skewer veto, cone promotion (old `potsac.py` 472-649, about 180 lines, and
`MAX_CLEARANCE_MM`). The pool itself (10 seeds x 1000 Pottmann draws, 10-deg basins) is unchanged.

**`sfs_axes/potsac.py`:** new `_distinct_lines(lines, tol_deg)` (greedy angular dedup, first wins) and
`_rank_by_profile(reps, sizes, C0, C1, C, max_candidates, verbose)`: the 60 most-drawn basins
(`PROFILE_BASINS`) each enter twice, as raw representative and after `refine_axis_normalized` (60 iterations,
<= 12,000 points) -> sort by `profile_cost` -> 15-deg distinct -> best 8 (`PROFILE_REFINE_K`) refined with
`refine_axis_profile` -> sort -> 15-deg distinct -> first `max_candidates` (6) written. Imports trimmed to what
is used. After axes322 was built one docstring line of `run_potsac_union` was corrected (it still said
"worst-wall cost first"); comment-only, md5 now `e8578d40...` (axes322 was built from `0b0cf42f...`).
**`tests/test_normalized.py`:** `test_profile_ranking_is_scale_free` added (coverage table above).

**Paper chain unaffected — checked, not assumed** (job 34619756): committed `potsac.py` (md5 `79abd164...`)
against the working tree (`0b0cf42f...`), `python -m sfs_axes.cli extract-pot-a --paper-chain --seed 0` on
Pot A 1-8 and Pot F 1-7: all 15 runs in `mode=paper-chain`, **15 of 15 axis files byte-identical**
(`diff -r` empty; `pc/diff.txt` 0 bytes). Statically, nothing `run_potsac` reads was touched (the only removed
name, `MAX_CLEARANCE_MM`, had no other reader). sacct shows the job `FAILED 141:0`: that is a SIGPIPE from the
last diagnostic line (`md5sum ... | head -3` under `pipefail`), after every step had returned rc=0.

#### What is still unproven — plainly

- **The pots' end-to-end seating under axes322 is unmeasured.** The ten jobs (34619671-34619681) were all
  PENDING (Priority) when this was written. Until their `score/acc.tsv` are read, nothing here says the
  pots keep their floors; the axis table is evidence about axes, not about seating.
- **The Juglet end-to-end was not re-run** on axes322. Its axis numbers are against the mesh-derived key;
  whether 6/8/8 turns into more seated joins (out of the honest 10) is not known.
- **Pot F 06** loses its true axis at rank 0 and best-of-3; whether that costs Pot F a seat is not known
  (above), and whether the 10-deg dedup recovers it at best-of-3 is job 34619792, not yet read.
- The Q2 cylinder / cone / free-profile residual table was not produced.
- `tests/test_regression_pota.py` was not run (the cluster env has no pytest); the paper-chain identity
  check above covers the same code path on 15 pieces.

Status at end of turn: t322-potA / B / C (34619671 / 72 / 73) RUNNING (started within the last 5 minutes);
D-J and the dedup-10 variant (34619792) PENDING (Priority). Small job 34619756: sacct `FAILED 141:0`
(the SIGPIPE above; f06 probe rc=0, all four paper-chain runs rc=0).

### Worker — checkpoint 9: partial pot end-to-end (5 of 10), the Pot G regression, the 10-deg verdict

**End-to-end on axes322, K=3, two repeats** (each run's `score/acc.tsv`; all `CORPUS-UNCHANGED`):
| pot | job | sacct | repeat 1 sherds / joins | repeat 2 | floor | verdict |
|---|---|---|---|---|---|---|
| A | 34619671 | COMPLETED 0:0 (15:21) | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | holds |
| B | 34619672 | COMPLETED 0:0 (11:48) | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | holds |
| C | 34619673 | COMPLETED 0:0 (4:29) | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | holds |
| F | 34619677 | COMPLETED 0:0 (2:34) | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | holds — F06's 14.7-deg rank 0 cost no join |
| G | 34619678 | COMPLETED 0:0 (4:26) | 7/7, **4/10** | 6/7, **5/10** | 7/7, 10/10 | **REGRESSED, 5-6 joins lost** |
Outstanding: D 34619674, E 34619676, H 34619679, I 34619680, J 34619681 — RUNNING at time of writing.
verified: `cat <run>/score/acc.tsv` for A, B, C, F, G -> rows above; `sacct -X` -> states above.

**The 10-deg dedup variant (job 34619792, COMPLETED 0:0, `out/profile_rank_dedup10.json`) is rejected
by the rule fixed in checkpoint 8.** Pots best-of-3 146 -> 148 and Pot F 6 -> 7 (F06 gets a 3.0-deg second
line), Juglet stays 8 — but **Pot C falls 6 -> 5** (C06 best-of-3 1.1 -> 13.6 deg), and "no pot below its
axes322 best-of-3" was a condition. 15 deg stays; **F06 is recorded as an accepted single-piece cost**
(reason in checkpoint 8: the true basin is 22-25% dearer under the profile cost on this short wide band),
and the end-to-end shows it costs Pot F nothing.

#### Pot G: what moved

- **Not a line-cap artefact.** axes322 writes 5, 6, 4, 6, 5, 5, 4 lines for pieces 1-7 (axes320: 6 each);
  K=3 uses 3 on every piece in both sets.
- **The first lines did not get worse — they got better.** Error vs the reference, rank 0, axes320 ->
  axes322: G01 1.0 -> 0.3, G02 2.0 -> 0.5, G03 2.0 -> **8.0**, G04 6.5 -> 3.5, G05 6.0 -> 0.9, G06 7.9 -> 0.9,
  G07 4.9 -> 0.7 deg. New vs old first line: 0.9, 2.3, 10.1, 9.9, 6.8, 7.0, 5.4 deg apart, same direction
  sign on all seven (dot +0.985 to +1.000). Only G03 moved by more than the 10-deg bar, and it is still
  within it.
- **It is the second and third lines.** They are wholly different from axes320's (e.g. G02 45.3 / 20.6 deg
  against 26.0 / 52.5; G05 16.9 / 51.7 against 33.6 / 49.3), and their profile cost is 1.32-3.27x the
  first line's — never near-equal.
- **How the assembler used them** (inferred, not logged: each piece's three lines pushed through its
  final `T_i`, and for every graph join the pair of lines that coincides in the assembled pot). In 319
  (axes320, 10/10) nine of ten joins coincide on **line 0 / line 0** (the tenth, 5-7, on line 2 / line 2 at
  5.4 deg, 7 mm), so the pot is seated on one common axis. In 322 the pot splits into two groups seated
  ~150 deg apart: {2, 5} against {1, 3, 4, 6, 7}. Joins inside a group pass (1-3, 4-7, 2-5); every join
  across the groups fails at 140-154 deg (2-3, 2-6, 4-5, 5-7). The failing joins coincide on a non-first
  line on at least one side: repeat 1 2-3 on L1/L2, 4-5 on L1/L1, 5-7 on L2/L0, 2-6 on L0/L2; repeat 2
  2-3 L1/L1, 2-6 L0/L2, 3-6 L2/L1. The two repeats of the same bytes give different results (4 vs 5 joins;
  the 319 repeats were identical), so the search was close to a tipping point.
- **Answer to "is the old first line still in the new top 3":** the old first line is effectively the
  new first line on five pieces (within 7 deg), 9.9 deg away on G04 and 10.1 deg on G03. Nothing good was lost from
  the slots; what changed is which *wrong* lines fill slots 2 and 3, and the assembler found a
  self-consistent wrong configuration through them — the ticket 306 finding ("one extra candidate line
  on one piece moves the global search into a different, self-consistent, wrongly-joined configuration").

**Diagnostic submitted to separate the two causes** (changed inputs, not a repeat): job **34620128**,
run `20261110-0446_d628fc0_t322-potG-diag`, arms **G_K1** = axes322 line 0 only and **G_MX** = axes322
line 0 + axes320 lines 1-2, two repeats each. If both reach 10/10, the new first lines are fine and the
new extra lines caused the loss; if G_K1 fails, the first lines (G03 at 8.0 deg) matter too.

#### Proposed change — written before implementing, conditional on the diagnostic

Not a tie-break: on Pot G the competing lines are not near-equal (1.32x and up), so a near-equality rule
would not touch them. The principled reading is the identifiability one already in Q3 ("ambiguity is
carried by the candidate list"): **a second or third line is written only when the piece's own surfaces
cannot tell it apart from the first.** Candidate: keep line k >= 1 only if its profile cost is within the
first line's *measurement noise* — the spread of the first line's cost when the same wall is re-strided
at different phases — so the tolerance comes from the piece, not from a constant. Measured so far
(offline, `profile_rank.json`): the lines that rescue a piece at best-of-3 cost 1.01-1.16x the first on
9 of 13 rescues (H11, D27, E14, J07, A06, D18, Juglet 7, H08, C06), but 1.50 (A07), 1.94 (I27), 2.49
(Juglet 3) and 4.27 (I29) on the other four; Pot G's extra lines cost 1.32-3.27x. **So any cut that
removes G's lines also removes up to four rescues, one of them a Juglet piece** — the Juglet would fall
8 -> 7 at best-of-3 unless the noise measure separates them. Acceptance, fixed now: pots best-of-3 >= 146
and no pot below its axes322 count, Juglet best-of-3 8, and Pot G 10/10 joins end to end in both
repeats; otherwise the change is not made and Pot G is reported as a regression of this ticket.

Status at end of turn: D, E, H, I, J RUNNING (13-17 min elapsed); Pot G diagnostic 34620128 PENDING.
No code changed this turn; the proposal above waits on the diagnostic.

### Worker — checkpoint 10: DECISION — (c) the profile ranker is reverted in the working tree

**1. The Pot G cause, in one line.** The first lines barely moved (new vs old first line 0.9-10.1 deg
apart; error vs reference better on 6 of 7, G03 2.0 -> 8.0 deg), but **the second and third lines changed on
all seven pieces** (e.g. G02 now 45.3 / 20.6 deg from the reference instead of 26.0 / 52.5; G05 16.9 / 51.7
instead of 33.6 / 49.3), and the assembler joined **pieces 2 and 5 to the rest through those non-first
lines**: in both repeats every join between {2, 5} and the rest fails — 2-3, 2-6, 4-5, 5-7 at 141-154 deg in
repeat 1 and 79-107 deg in repeat 2 — costing 5-6 of 10 joins. ("Through non-first lines" is inferred from
the final poses: the failing joins coincide on L1 or L2 of at least one side; the assembler does not log it.)

**2. The 10-deg dedup variant: FAIL.** Rule registered in checkpoint 8 before the run: pots best-of-3
>= 146, no pot below its axes322 best-of-3, Pot F best-of-3 = 7, Juglet best-of-3 = 8. Result (job
34619792, COMPLETED 0:0): pots 148, Pot F 7, Juglet 8 — but **Pot C 6 -> 5** (C06 1.1 -> 13.6 deg). Fails on
the second condition. Not adopted.

**3. Recommendation: (c) — revert the ranker; keep only the profile objective, dormant and tested.**
Why not (b): the only principled rule I could state for Pot G — write a second or third line only when
the piece cannot tell it apart from the first (profile cost within a factor 1 + tau of the first line) —
**fails its own pre-registered acceptance offline at every tau** (0.10 to 1.00, `profile_rank.json`):
the Juglet always falls 8 -> 7 at best-of-3 (piece 3's rescuing line costs 2.49x), and Pot A or Pot I
always falls below its axes322 count (A07's rescue at 1.50x, I27 at 1.94x, I29 at 4.27x). The rescues
need tolerances of 1.5-4.3x; Pot G's harmful lines start at 1.32x. No cut, constant or per-piece, removes
G's lines and keeps those rescues; picking tau to fit between them would be a Pot-G constant. A
diversity or tie-break term does not apply either: G's competing lines are not near-equal.
Why not (a): the ticket's constraint is that the ten pots keep their floors and that a regression is
reported, not absorbed, and the standing instruction is not to leave the tree where the pots regress.
Pot G loses 5-6 joins end to end on two repeats; the axis-level gains do not license that.
What (c) keeps and loses: it loses the corpus axis gains (pots best-of-3 146 -> 133, rank 0 135 -> 107;
Juglet 8 -> 6 best-of-3) and leaves the old ranker's millimetre and size constants in place — the ticket's
goal of one scale-free ranking is **not met**. It keeps every pot at its 319/320 floor (axes320 is the set
those floors were measured on).

**What is in the working tree now**
- `sfs_axes/potsac.py`: **reverted to the committed version** (`git checkout`; md5 after LF normalisation
  `79abd164...`, the committed file). The splice is saved as `.scratch/pota-repro/t322/profile_ranker.patch`
  (`git apply` re-applies it; reverse-apply checked clean before the revert).
- `sfs_axes/profile.py`: kept, **not called by any production path** — the objective whose minimum sits at
  the reference axis (median drift 1.5 deg vs the normal cost's 6.4 deg, 163 pot pieces). It is the part that
  is unambiguously better as a measurement; what is not yet solved is how to rank the *extra* lines without
  breaking the assembler's search.
- `tests/test_normalized.py`: the ranker test is replaced by
  `test_profile_objective_is_minimal_at_true_axis_at_any_scale` (globular belly at 0.2x / 1x / 5x: the
  true axis is cheaper than an 8-deg tilt, and refinement from the tilt returns within 2 deg). Test run on
  the reverted tree: job **34620277** (submitted; result to be recorded).
- The sections above that describe the splice ("checkpoint 5", "FINAL READ-OUT — the code") describe the
  patch, not the tree.

**Still running and still informative:** D, E, H, I, J end-to-end on axes322 and the Pot G diagnostic
34620128 (K1 / MX arms). They do not change this decision unless they show the pots *better* than their
floors on axes322 *and* G_K1 seats 10/10 — that would argue for a follow-up that writes fewer extra lines,
which needs its own ticket and its own acceptance rule, not a constant chosen here.

**Tests on the reverted tree: job 34620277, COMPLETED 0:0 — 14/14 PASS** (13 pre-existing on the committed
`potsac.py`, md5 `79abd164...`, plus `test_profile_objective_is_minimal_at_true_axis_at_any_scale`).
verified: `logs/tests-34620277.out` -> "all 14 tests passed", rc=0. (`profile.py` md5 differs from the
earlier `91662c33...` only by CRLF line endings; verified: `diff --strip-trailing-cr impl/.../profile.py
impl_revert/.../profile.py` -> identical.)
Status at end of turn: D, E, H, I, J RUNNING; Pot G diagnostic 34620128 PENDING (estimated start 05:39).

### Worker — checkpoint 11: revert NOT finalised; hybrid test pre-registered (written before any run)

The lead asked for a hybrid test before the revert is final, because the end-to-end picture now has
A, B, C, F and H at their floors and G the only clear regression.

**The idea and my judgement of it.** The first line answers "what is the axis"; lines 2-K answer "which
other hypotheses should the assembler try". Those are different questions, and Pot G shows the old set
answered the second one in a way the assembler could live with (319: 10/10 with old lines 2-3 that are
themselves 26-55 deg off). So the split is defensible *as a test*. Its weakness, stated now: ordering
lines 2-K by the old ranker keeps the old ranker — every millimetre window and the size-keyed branch —
in the shipped path for those slots. If the hybrid passes it is a working stop-gap, not the ticket's
scale-free method. The alternative I would defend instead, "profile cost with a minimum separation",
is already measured not to help: Pot G's harmful new lines are 16.9-51.8 deg from line 1, so no
separation threshold below 16 deg removes them, and the 10-deg filter made G's extra lines *closer*
(G06 got a 7.7-deg second line).

**The hybrid, exactly** (`t322/build_hybrid.py`): per piece, line 1 = axes322's first line; then axes320's
lines in their own order, dropping any within 10 deg of a line already kept (the union's own duplicate
rule, `DEDUP_COS`); cap 6. Lines copied as text, byte for byte. Output `out/axes_hyb`.

**Acceptance — all must hold, or it does not ship:**
1. pots best-of-3 >= 146 (same scorer as every table above);
2. no pot below its axes322 best-of-3 count;
3. Pot F best-of-3 = 7 and Juglet best-of-3 = 8;
4. Pot G end-to-end back to 7/7 sherds and 10/10 joins on at least one of two repeats.
Prediction, written now: condition 3 fails. The hybrid's best-of-3 can only use line 1 from axes322 and
lines 2-3 from axes320; F06's axes322 line 1 is 14.7 deg off and axes320's lines 2-3 are 22.7 / 21.3 deg
off, so F06 fails and Pot F is 6, not 7 (axes322 is 6 too; Pot F was 7 only under axes320, whose first
line was the 2.0-deg one). Likewise the Juglet: it reached 8 under axes322 partly through second lines
(Juglet 7's 2.6-deg rescue is axes322's line 2), which the hybrid replaces. If condition 3 is read
literally the hybrid fails before the end-to-end; I run it anyway because the lead asked for the table
and the G / D end-to-end, and because a failing condition 3 with a passing condition 4 is itself
informative.

**End-to-end jobs for the hybrid: two only** — Pot G and Pot D, two repeats each, K=3. Pot G's top-3 under
the hybrid is expected to be byte-identical to the "MX" arm of the queued diagnostic 34620128 (axes322
line 1 + axes320 lines 2-3), because axes320's lines 2-3 on G are all > 10 deg from the new line 1; if that
holds, MX *is* the hybrid G test and no second G job is submitted (same bytes would prove nothing new).

### Worker — checkpoint 12: Pot G diagnostic in, hybrid fails its pre-registered rule, running end-to-end table

**Pot G diagnostic (job 34620128, COMPLETED 0:0, 3:43, CORPUS-UNCHANGED, run
`20261110-0446_d628fc0_t322-potG-diag`):**
| arm | what each piece gets | repeat 1 | repeat 2 |
|---|---|---|---|
| G_K1 | axes322 line 1 only | 7/7, **10/10** | 7/7, **10/10** |
| G_MX | axes322 line 1 + axes320 lines 2-3 | 7/7, **10/10** | 7/7, **10/10** |
| (axes322 K=3, job 34619678) | axes322 lines 1-3 | 7/7, 4/10 | 6/7, 5/10 |
**So the new first lines are right and sufficient on Pot G; the join loss comes entirely from axes322's
new second and third lines.** This confirms checkpoint 10's cause line on four more assembler runs.

**Hybrid (pre-registered in checkpoint 11): FAILS — does not ship.** Built by job 34620424 (COMPLETED
0:0; 181 files; 139 old lines dropped as within 10 deg of a kept line), scored with the same scorer,
`out/score_320_322_hyb.txt`. Pieces within 10 deg of the reference:
| pot | n | axes320 r0 / b3 / b6 | axes322 r0 / b3 / b6 | hybrid r0 / b3 / b6 |
|---|---|---|---|---|
| A | 8 | 6 / 6 / 6 | 6 / 8 / 8 | 6 / **7** / 7 |
| B | 9 | 5 / 6 / 6 | 9 / 9 / 9 | 9 / 9 / 9 |
| C | 6 | 4 / 5 / 5 | 5 / 6 / 6 | 5 / 6 / 6 |
| D | 32 | 23 / 26 / 28 | 27 / 29 / 30 | 27 / 29 / 30 |
| E | 34 | 23 / 33 / 33 | 32 / 33 / 33 | 32 / 33 / 34 |
| F | 7 | 4 / 7 / 7 | 6 / 6 / 6 | 6 / 7 / 7 |
| G | 7 | 7 / 7 / 7 | 7 / 7 / 7 | 7 / 7 / 7 |
| H | 11 | 10 / 10 / 10 | 9 / 11 / 11 | 9 / **10** / 10 |
| I | 30 | 18 / 24 / 25 | 25 / 27 / 28 | 25 / **26** / 27 |
| J | 19 | 7 / 9 / 10 | 9 / 10 / 13 | 9 / 10 / 11 |
| **pots** | 163 | 107 / 133 / 137 | 135 / 146 / 151 | 135 / **144** / 148 |
| Juglet | 9 | 4 / 6 / 8 | 6 / 8 / 8 | 6 / **7** / 9 |
Against the four conditions: (1) pots best-of-3 >= 146 — **144, fail**; (2) no pot below axes322 —
**A 8 -> 7, H 11 -> 10, I 27 -> 26, fail**; (3) Pot F 7 and Juglet 8 — F **7, pass** (my prediction was
wrong: the hybrid keeps axes320's 2.0-deg first line as F06's second line, because it is 14.7 deg from the
new first line and survives the 10-deg dedup), Juglet **7, fail** (Juglet 7's 2.6-deg rescue was an axes322
line and is replaced); (4) Pot G end-to-end — the hybrid's G top-3 is byte-identical to the diagnostic's
G_MX arm on 6 of 7 pieces (`cmp`; G03 differs: the hybrid keeps G03's old first line, 10.1 deg from the new
one, as line 2), and G_MX seated 10/10 twice — effectively a pass, but not on the exact bytes.
Three of four conditions fail on the axis table alone.

**Hybrid end-to-end jobs.** Pot D was submitted (job 34620425, run `20261110-0500_d628fc0_t322hyb-potD`,
dependent on the build) and **cancelled by me after 50 s** (`CANCELLED+`) once the axis table showed the
hybrid cannot ship: a 3-hour, 24-CPU assembly of a set that fails its own acceptance rule would only
delay D/E/I in a congested queue. Pot G was not submitted (see condition 4: the G_MX arm already
covers 6 of its 7 files). The run directory and its index row stay as the record.

**Running end-to-end table, axes322, K=3** (all `CORPUS-UNCHANGED` where finished):
| pot | job | sacct | repeat 1 | repeat 2 | floor | verdict |
|---|---|---|---|---|---|---|
| A | 34619671 | COMPLETED 0:0 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | holds |
| B | 34619672 | COMPLETED 0:0 | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | holds |
| C | 34619673 | COMPLETED 0:0 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | holds |
| D | 34619674 | RUNNING (29 min) | | | 23-25/28, 55-60/69 | pending |
| E | 34619676 | RUNNING (28 min) | | | 29-31/31, 57-62/62 | pending |
| F | 34619677 | COMPLETED 0:0 | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | holds |
| G | 34619678 | COMPLETED 0:0 | 7/7, 4/10 | 6/7, 5/10 | 7/7, 10/10 | **regressed** |
| H | 34619679 | COMPLETED 0:0 | 11/11, 17/17 | 9/11, 13/17 | 11/11, 17/17 | holds on repeat 1 |
| I | 34619680 | RUNNING (26 min) | | | 25/26, 59/62 | pending |
| J | 34619681 | COMPLETED 0:0 (22:51) | 8/11, 16/21 | 8/11, 16/21 | 8/11, 16/21 | holds |

**Pot H's 9/11 repeat is assembler nondeterminism, not the axis change.** Both repeats ran the same job
on byte-identical staged inputs (same axes322 top-3, same lanes) and got 11/11 + 17/17 and 9/11 + 13/17;
different results from identical inputs can only come from the assembler. Precedent: ticket 318 (job
34537402) ran the authors' axes on Pot H twice in one job and got 5/11 + 7/17, then 8/11 + 9/17; ticket
319 found the same on E (30/31 vs 31/31) and D (25/28 vs 24/28) from byte-identical inputs. (Correction to
the hand-over wording: the 5/11-then-8/11 split is ticket 318's, not 319's — in 319 the authors' H arm
came out identical twice, 8/11 + 9/17; 319's own text says "real, but not on H".) Under the repeat rule a
pot holds if a repeat reaches its floor, so H holds.

**Where the decision stands.** The working tree stays reverted (committed `potsac.py`; the ranker is
`t322/profile_ranker.patch`, one `git apply` away) while D, E, I are outstanding — the safe default for the
pots. Neither tested way of keeping the profile ranker passes its pre-registered rule (10-deg dedup:
checkpoint 10; hybrid: above). What the diagnostic adds is a specific, testable follow-up rather than a
tweak: on Pot G the profile ranker's *first* line is enough (K1 10/10 twice) and its extra lines are what
break the search. Note for whoever takes it: axes322's first line alone scores rank-0 135/163, above
axes320's best-of-3 (133/163), so "one profile line, plus extra lines only where the piece is genuinely
ambiguous" is the shape to test — with its own ticket, its own acceptance rule fixed before the run, and
all ten pots end to end, not a constant picked here.

### Worker — checkpoint 13: PRE-REGISTERED (before submission) — does the profile ranker seat every pot at K=1?

**Question.** Given ONE line per piece — axes322's first line, the profile-thickness estimate — does the
assembler seat every pot? If yes, the estimator generalises and the open problem is a separate one:
which extra lines to give the assembler (candidate-set selection).

**Design.** Ten jobs, one per pot, each derived mechanically from that pot's `t322-pot<X>` run (itself the
ticket 319 run with the axes swapped): same lanes, NAMED, NP, FLOOR, staging, SIF, scorers, md5 gate;
only change `head -n 3` -> `head -n 1` (arm labels `<X>_K1R1`, `<X>_K1R2`). Two repeats. Axes:
`runs/20261110-0415_d628fc0_t322-axes/out/axes322` (unchanged since checkpoint 6).

**Floors** (the ticket's evidence table): A 8/8 + 15/15; B 9/9 + 15/15; C 4/4 + 5/5; D 23-25/28 + 55-60/69;
E 29-31/31 + 57-62/62; F 5/5 + 7/7; G 7/7 + 10/10; H 11/11 + 17/17; I 25/26 + 59/62; J 8/11 + 16/21.
A pot reaches its floor if at least one repeat is at or above the floor's lower end on both sherds and
joins (the repeat rule, because the assembler is nondeterministic — checkpoint 12).

**Pass:** at least 9 of the 10 pots reach their floors. **Fail:** three or more pots below floor, or Pot G
below 7/7 + 10/10. Exactly two pots below floor (with G at floor) is neither — recorded as inconclusive,
named pot by pot. No re-run, no second variant, no constant changed in response to the result.

**K=1 jobs submitted** (all ten in one batch, then submission stopped; all PENDING at submission):
| pot | run | job |
|---|---|---|
| A | `20261110-0506_d628fc0_t322k1-potA` | 34620557 |
| B | `..._t322k1-potB` | 34620558 |
| C | `..._t322k1-potC` | 34620559 |
| D | `..._t322k1-potD` | 34620560 |
| E | `..._t322k1-potE` | 34620561 |
| F | `..._t322k1-potF` | 34620562 |
| G | `..._t322k1-potG` | 34620563 |
| H | `..._t322k1-potH` | 34620564 |
| I | `..._t322k1-potI` | 34620565 |
| J | `..._t322k1-potJ` | 34620566 |
Generator `t322/make_e2e_k1.sh` (writes run.json and the index row). verified: `diff` of the Pot G submit
script against `t322-potG`'s -> only the job name, comments, `head -n 1`, `axes_k1` and the `_K1` arm labels.

---

## WRITE-UP FOR THE LEAD (checkpoint 14 — supersedes "FINAL READ-OUT" above, which described the reverted splice)

### The answers

**Q1 — regime gap or broken reference?** Both, plus a partly broken measurement.
(c) *The reference was wrong*: `Dataset/Axes/Juglet` is our own September MATLAB output, within 10 deg of the
mesh-derived key on 1 of 9 pieces; the key comes from the meshes and the TORA assembled vertices (0.0001-mm
Procrustes, checkpoint 1) and `Juglet_GT` agrees with it. (a) *The method failed by construction*: the
shipped ranker's gates are millimetre windows sized on pots (25-mm clearance, 65-mm "Regime 1" diagonal,
radius knees) and its underlying normal cost is not minimised at the true axis (refined from the reference
it drifts > 10 deg on 70 of 163 pot pieces). (b) *The Juglet end-to-end measurement is partly broken*: 8 of its
18 graph joins are between pieces that do not touch; the honest denominator is 10. Against the right key the
old axes are 4 / 6 / 8 of 9 (rank 0 / best-of-3 / best-of-6), not 0.

**Q2 — what is structurally different, measured.** On every scale-free feature the Juglet sits inside the
pots' range (e.g. piece size over distance to the axis, r/L 0.47 against 0.29-0.73); it differs in absolute
millimetres (median radius 15.7 mm against the pots' 28-80) and in being near-spherical (Pottmann s2/s3 1.9
against 2.9-11.8, so more than one axis fits a piece). Piece 1 is the neck / shoulder / handle zone, piece 7
the base. **Not done:** the per-piece cylinder / cone / free-profile residual table.

**Q3 — one formulation.** Profile thickness (`sfs_axes/profile.py`): about the true axis every wall maps in
(r, z) onto one curve, for any vessel shape; the cost is the trimmed (best 80%) mean local thickness of that
curve, k = 24 neighbours, mean of the two walls; Nelder-Mead over two tilts and two foot shifts in units of
0.1 x the piece's own diagonal. No millimetre constant, no shape class. Refined from the reference it moves a
median 1.5 deg (> 10 deg on 9 of 163) against 6.4 deg (70 of 163) for the shipped cost. **As an estimator of
the first line it is better** (rank 0 135 against 107 of 163 pot pieces; Juglet 6 against 4). **As a ranker of
lines 2-3 it is not safe**: on Pot G its extra lines lead the assembler into a wrong configuration
(diagnostic below). The refusal / ambiguity test proposed in Q3 (write extra lines only where the piece is
ambiguous) was tested as a cost-ratio gate and fails its acceptance rule at every threshold (checkpoint 10).

**Q4 — the Juglet's answer key.** Accepted by the lead in checkpoint 1: `Juglet_GT` is right; the released
`Axes/Juglet` is wrong on 8 of 9 pieces. Key files `out/jugkey/key/`.

**Q5 — predict, then run.** Predicted before implementing (checkpoint 4, first 48 pieces): rank 0 42 vs 36,
best-of-3 47 vs 40; the implementation reproduced the offline table piece for piece. Predicted for the
Juglet: rank-0 ceiling 6/9 with p2 / p3 / p8 input-limited; result 6/9 (a different six — p8 passes, p7 the
base fails at rank 0). Predicted for the end-to-end: every pot holds except possibly F (piece 06). Result:
F held; **G regressed** — not predicted. Predicted for the hybrid: fails on F; it passed on F and failed on
the Juglet, A, H, I (prediction wrong in its reason, right that it fails).

### The three axis tables (172 pieces; within 10 deg of the reference; same scorer throughout)
| pot | n | axes320 (shipped) r0 / b3 / b6 | axes322 (profile ranker) | hybrid |
|---|---|---|---|---|
| A | 8 | 6 / 6 / 6 | 6 / 8 / 8 | 6 / 7 / 7 |
| B | 9 | 5 / 6 / 6 | 9 / 9 / 9 | 9 / 9 / 9 |
| C | 6 | 4 / 5 / 5 | 5 / 6 / 6 | 5 / 6 / 6 |
| D | 32 | 23 / 26 / 28 | 27 / 29 / 30 | 27 / 29 / 30 |
| E | 34 | 23 / 33 / 33 | 32 / 33 / 33 | 32 / 33 / 34 |
| F | 7 | 4 / 7 / 7 | 6 / 6 / 6 | 6 / 7 / 7 |
| G | 7 | 7 / 7 / 7 | 7 / 7 / 7 | 7 / 7 / 7 |
| H | 11 | 10 / 10 / 10 | 9 / 11 / 11 | 9 / 10 / 10 |
| I | 30 | 18 / 24 / 25 | 25 / 27 / 28 | 25 / 26 / 27 |
| J | 19 | 7 / 9 / 10 | 9 / 10 / 13 | 9 / 10 / 11 |
| **pots** | **163** | **107 / 133 / 137** | **135 / 146 / 151** | **135 / 144 / 148** |
| Juglet | 9 | 4 / 6 / 8 | 6 / 8 / 8 | 6 / 7 / 9 |
Worst rank 0 on axes322: J17 88.0, J13 86.8, J19 86.7, D32 86.0, I29 71.0, D26 69.1, E14 50.3, Juglet 7 47.9,
H11 45.2, J18 45.1 deg. Source: `out/score_320_322_hyb.txt` (job 34620424).

### End-to-end, axes322 at K=3 (two repeats; corpus unchanged in every finished job)
| pot | job | sacct | repeat 1 | repeat 2 | floor | verdict |
|---|---|---|---|---|---|---|
| A | 34619671 | COMPLETED 0:0 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | holds |
| B | 34619672 | COMPLETED 0:0 | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | holds |
| C | 34619673 | COMPLETED 0:0 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | holds |
| D | 34619674 | RUNNING | | | 23-25/28, 55-60/69 | pending |
| E | 34619676 | RUNNING | | | 29-31/31, 57-62/62 | pending |
| F | 34619677 | COMPLETED 0:0 | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | holds |
| G | 34619678 | COMPLETED 0:0 | 7/7, 4/10 | 6/7, 5/10 | 7/7, 10/10 | **regressed** |
| H | 34619679 | COMPLETED 0:0 | 11/11, 17/17 | 9/11, 13/17 | 11/11, 17/17 | holds (repeat 1) |
| I | 34619680 | RUNNING | | | 25/26, 59/62 | pending |
| J | 34619681 | COMPLETED 0:0 | 8/11, 16/21 | 8/11, 16/21 | 8/11, 16/21 | holds |
Hybrid Pot D 34620425: cancelled by me after 50 s (`CANCELLED+`) once the hybrid had failed its axis-table
conditions. K=1 jobs 34620557-34620566: pending (checkpoint 13).

### The Pot G diagnostic (job 34620128, COMPLETED 0:0)
| arm | lines per piece | repeat 1 | repeat 2 |
|---|---|---|---|
| axes322 K=3 (job 34619678) | profile lines 1-3 | 7/7, 4/10 | 6/7, 5/10 |
| G_K1 | profile line 1 only | 7/7, **10/10** | 7/7, **10/10** |
| G_MX | profile line 1 + old lines 2-3 | 7/7, **10/10** | 7/7, **10/10** |
Cause: the profile ranker's first lines are right (error vs the reference 0.3-8.0 deg, better than the old on
6 of 7); its second and third lines differ on all seven pieces, and with them the assembler seats {2, 5} as a
separate group 79-154 deg off the rest (every join between the groups fails, in both repeats).

### Single-piece costs, named
- **Pot F 06** — axes322 rank 0 14.7 deg (axes320: 2.0). The profile cost itself prefers the wrong line (the
  true basin's optimum is 22-25% dearer on this short, wide band: radius 44-48 mm, 20-26 mm tall); the 2.0-deg
  line was in the pool and lost a duplicate filter it never reached refinement for. **End-to-end cost: none**
  (Pot F 5/5 + 7/7 twice). Accepted.
- **Pot H** — 9/11 + 13/17 on repeat 2 against 11/11 + 17/17 on repeat 1 from byte-identical inputs in the
  same job: assembler nondeterminism, not the axis change (precedent: ticket 318 authors' arm on H, 5/11 then
  8/11, job 34537402; ticket 319 on E and D). At the axis level H loses one rank 0 (H08 1.2 -> 18.5 deg, its
  second line 1.6 deg) and gains H11 at best-of-3.

### What is proven / what is not
Proven (each with the job named above):
- The Juglet's released axes were the broken reference; the mesh-derived key is right (Q4).
- The profile cost is a better axis estimator than the shipped one on the pots: first-line accuracy 135 vs
  107 of 163, its minimum near the reference (median 1.5 vs 6.4 deg drift).
- On Pot G, its first line alone seats 10/10 twice; its extra lines cost 5-6 joins.
- The paper chain (`--paper-chain`, the CLI default) is unaffected: 15 of 15 files byte-identical, Pots A + F.
- Under axes322 at K=3, A, B, C, F, H, J keep their floors.
Not proven:
- **That the profile estimator seats every pot** — the K=1 experiment (checkpoint 13) is queued, unmeasured.
- D, E, I under axes322 at K=3 — running.
- **Anything about the Juglet end-to-end**: never re-run on axes322 or at K=1.
- A rule for which extra lines to write. Two were tested and failed (10-deg dedup, cost-ratio gate); the hybrid
  failed. Candidate-set selection is open.
- The Q2 shape-residual table.

### State of the working tree (nothing committed, nothing pushed)
- `sfs_axes/potsac.py`, `cli.py` and every other tracked file under `sfs_axes/`: **byte-identical to HEAD
  `d628fc0`** (`git diff --stat HEAD -- sfs_axes` empty). HEAD's `sfs_axes/` is identical to `97dad1e`
  (ticket 320, `git diff --stat 97dad1e d628fc0 -- sfs_axes` empty), the commit the axes320 set is recorded
  under; axes320 equals axes318 on 180 of 181 files (only `Pot_A_Piece_01` differs, `cmp`), so the files
  behind ticket 319's B-J floors and ticket 320's Pot A floor are what this code is recorded as producing.
  I did not regenerate axes320 from HEAD in this ticket, so "this code reproduces those bytes" rests on the
  320 record, not on a run here.
- **What the default path does:** the CLI default is the paper chain (`run_potsac`), unchanged and checked
  byte-identical on 15 pieces (job 34619756). The `--union` path (`run_potsac_union`, which builds the
  benchmark sets) is the committed ranker — the same code as axes320. **Shipped behaviour has not changed.**
- New, untracked: `sfs_axes/profile.py` — the profile-thickness estimator, **not wired into any path**
  (nothing in `sfs_axes/` imports it; its docstring says so). Only `tests/test_normalized.py` imports it.
- `tests/test_normalized.py`: one test added, `test_profile_objective_is_minimal_at_true_axis_at_any_scale`
  (14 of 14 pass on this tree, job 34620277).
- `.scratch/pota-repro/t322/`: the fast loop and every script used here, plus `profile_ranker.patch` (the
  reverted ranker; `git apply` re-applies it).

### Recommendation
**Land the tree as it is: the default unchanged, `profile.py` kept as the documented, tested, unwired
estimator.** Reason: no tested way of using it as the ranker passes its pre-registered rule (Pot G breaks at
K=3; the 10-deg dedup, the cost gate and the hybrid each fail), while the shipped code is the one every floor
was measured on. Then let the K=1 experiment decide what comes next:
- **If it passes** (>= 9 of 10 pots at floor, G at 7/7 + 10/10): the estimator generalises. Open a follow-up
  ticket for candidate-set selection, starting from "profile line 1, extra lines only where the piece is
  demonstrably ambiguous", with its own acceptance rule and all ten pots plus the Juglet end to end. Shipping
  K=1 itself would be `profile_ranker.patch` with `max_candidates=1` — a change to the assembler's input that
  needs its own decision, not this ticket's.
- **If it fails**: the estimator is better at the axis level but not sufficient for the assembler on its own,
  and the shipped ranker stays until a candidate-set rule is found.

Status at end of turn: K=1 A and B RUNNING, C RUNNING or just started, D-J PENDING; axes322 K=3 D, E, I RUNNING
(32-35 min). `sfs_axes/profile.py` gained one docstring line after the test run ("Not called by run_potsac or
run_potsac_union"); comment-only.

---

## Where this leaves the method

### (a) The tables

**Axis level** — pieces whose axis lands within 10 deg of the reference (rank 0 / best-of-3 / best-of-6;
same scorer for all three sets; `out/score_320_322_hyb.txt`, job 34620424):
| pot | n | axes320 (shipped ranker) | axes322 (profile ranker) | hybrid (profile line 1 + old lines) |
|---|---|---|---|---|
| A | 8 | 6 / 6 / 6 | 6 / 8 / 8 | 6 / 7 / 7 |
| B | 9 | 5 / 6 / 6 | 9 / 9 / 9 | 9 / 9 / 9 |
| C | 6 | 4 / 5 / 5 | 5 / 6 / 6 | 5 / 6 / 6 |
| D | 32 | 23 / 26 / 28 | 27 / 29 / 30 | 27 / 29 / 30 |
| E | 34 | 23 / 33 / 33 | 32 / 33 / 33 | 32 / 33 / 34 |
| F | 7 | 4 / 7 / 7 | 6 / 6 / 6 | 6 / 7 / 7 |
| G | 7 | 7 / 7 / 7 | 7 / 7 / 7 | 7 / 7 / 7 |
| H | 11 | 10 / 10 / 10 | 9 / 11 / 11 | 9 / 10 / 10 |
| I | 30 | 18 / 24 / 25 | 25 / 27 / 28 | 25 / 26 / 27 |
| J | 19 | 7 / 9 / 10 | 9 / 10 / 13 | 9 / 10 / 11 |
| **pots** | **163** | **107 / 133 / 137** | **135 / 146 / 151** | **135 / 144 / 148** |
| Juglet | 9 | 4 / 6 / 8 | 6 / 8 / 8 | 6 / 7 / 9 |

**End-to-end** — sherds seated / joins made, two repeats each, axes322 at K=3 and at K=1 (corpus unchanged
in every finished job; each run's `score/acc.tsv`):
| pot | floor | K=3 job | K=3 repeat 1 / repeat 2 | K=1 job | K=1 repeat 1 / repeat 2 |
|---|---|---|---|---|---|
| A | 8/8, 15/15 | 34619671 | 8/8 15/15 / 8/8 15/15 | 34620557 | **8/8 9/15 / 8/8 9/15** |
| B | 9/9, 15/15 | 34619672 | 9/9 15/15 / 9/9 15/15 | 34620558 | 9/9 15/15 / 9/9 15/15 |
| C | 4/4, 5/5 | 34619673 | 4/4 5/5 / 4/4 5/5 | 34620559 | 4/4 5/5 / 4/4 5/5 |
| D | 23-25/28, 55-60/69 | 34619674 | RUNNING | 34620560 | RUNNING |
| E | 29-31/31, 57-62/62 | 34619676 | RUNNING | 34620561 | RUNNING |
| F | 5/5, 7/7 | 34619677 | 5/5 7/7 / 5/5 7/7 | 34620562 | 5/5 7/7 / 5/5 7/7 |
| G | 7/7, 10/10 | 34619678 | **7/7 4/10 / 6/7 5/10** | 34620563 | 7/7 10/10 / 7/7 10/10 |
| H | 11/11, 17/17 | 34619679 | 11/11 17/17 / 9/11 13/17 | 34620564 | **9/11 11/17 / 9/11 11/17** |
| I | 25/26, 59/62 | 34619680 | RUNNING | 34620565 | RUNNING |
| J | 8/11, 16/21 | 34619681 | 8/11 16/21 / 8/11 16/21 | 34620566 | **6/11 5/21 / 6/11 8/21** |
All finished jobs COMPLETED 0:0 (sacct). **K=1 verdict against checkpoint 13's rule: FAIL** — three pots
below floor (A joins 9/15, H 9/11 + 11/17, J 6/11 + 5-8/21), which meets the "three or more" fail
condition whatever D, E, I show. K=3 on axes322: A, B, C, F, H, J at floor, G below; D, E, I outstanding.

### (b) What is now proven about the method, in one line each
- **Axis level:** the profile-thickness estimator finds a better axis than the shipped ranker — the first
  line is right on 135 of 163 pot pieces against 107, and on 6 of 9 Juglet pieces against 4.
- **End-to-end level:** no single candidate set built from it holds every pot — three lines per piece hold
  A and H but lose Pot G's joins (10 -> 4-5), one line per piece holds G but loses Pot A's joins (15 -> 9),
  Pot H (11/11 -> 9/11) and Pot J (8/11 -> 6/11). **The loss is in how the set of lines handed to the
  assembler is built, not in the axis estimate**, and neither a better single line nor a better fixed set
  fixed both ends.

### (c) What is NOT proven
- That any axis set built from the profile estimator keeps all ten floors. Three were measured end to end
  (K=3, K=1, and the hybrid's Pot G arm) and none did; Pots D, E, I are still outstanding on both.
- Anything about the Juglet end to end: it was never re-assembled on the new axes.
- A rule for which extra lines to give the assembler. Tested and rejected: 10-deg dedup, cost-ratio gate,
  hybrid ordering, one line only.
- That the committed code reproduces axes320 byte for byte (the code is identical to the commit it is
  recorded under; the set was not regenerated in this ticket).
- The Q2 per-piece cylinder / cone / free-profile residual table (not produced).

**The Juglet, in one sentence:** we are claiming **the reference was wrong** — the "true" axis file we had
been marking the Juglet against was our own earlier computer output, not the vessel's real axis, and when
the real axis is read off the reassembled vessel the old axes turn out to be right on 4 of 9 pieces (6 of 9
within the top three) rather than 0 of 9. Two smaller things sit underneath: the old method's millimetre
gates do misfit a vessel this small (a method weakness), and 8 of the 18 joins the Juglet was scored on are
between pieces that never touch (a measurement fault).

### (d) State of the working tree (nothing committed, nothing pushed)
| file | state | what it means |
|---|---|---|
| `sfs_axes/potsac.py`, `cli.py`, every other tracked file in `sfs_axes/` | **unchanged from HEAD `d628fc0`** | the shipped ranker; `git diff HEAD -- sfs_axes` is empty; HEAD's `sfs_axes/` equals `97dad1e`, the ticket 320 commit that axes320 is recorded under |
| `sfs_axes/profile.py` | **new, untracked, LF** | the profile-thickness estimator. **Not wired into any shipped path**: nothing in `sfs_axes/` imports it, neither `run_potsac` (paper chain, CLI default) nor `run_potsac_union` (`--union`) calls it; its docstring says so. Only the test below imports it |
| `tests/test_normalized.py` | **+31 lines, 0 deleted, LF as in HEAD** | adds `test_profile_objective_is_minimal_at_true_axis_at_any_scale`; 14 of 14 tests pass on this tree (job 34620277). Line endings restored this turn: `git -c core.autocrlf=false diff --stat` -> 31 insertions, 0 deletions |
| `.scratch/pota-repro/issues/322-...md` | appended (LF) | this ticket |
| `.scratch/pota-repro/t322/` | new, untracked | the fast loop and every script used here; `profile_ranker.patch` is the reverted profile ranker (`git apply` re-applies it) |
**The default path is the code that produced the ticket 319 / 320 numbers**: the CLI default (paper chain)
was checked byte-identical on 15 pieces (job 34619756); the `--union` path is HEAD's, identical by git to
the axes320 commit. Shipped behaviour has not changed.

### (e) Recommendation, in a form the next ticket can act on
1. **Land:** `sfs_axes/profile.py` (unwired) and the one test, as the documented estimator. Do not land
   `profile_ranker.patch`. The default stays the shipped ranker.
2. **Next ticket — "candidate set for the assembler", one question:** given the profile estimator's first
   line, which extra lines (if any) does each piece need so that A, H and J keep their joins (they need more
   than one line) without giving Pot G's assembler the alternatives it misuses (it needs exactly one)?
   Starting evidence, all in this ticket: the per-join line inference on Pot G (checkpoint 9), the G
   diagnostic (G_K1 and G_MX both 10/10), the K=1 losses on A / H / J, and the rescue list with cost ratios
   (checkpoint 10: rescues need 1.01-4.27x, G's harmful lines start at 1.32x, so a cost gate alone cannot
   separate them). First measurement to make: for A, H, J at K=1, which joins are lost and which second line
   (old or new) restores them, read from the assembled poses as in checkpoint 9.
3. **Acceptance for that ticket, fixed before it runs:** all ten pots at floor on at least one of two repeats
   at the chosen K, Pots D / E / I included, plus a Juglet end-to-end against the 10 real joins; no constant
   keyed on pot, piece or size.
4. **Record now:** Pot F 06 (rank 0 14.7 deg, no seating cost) and the Pot H repeat spread (assembler
   nondeterminism) as named single-piece costs; the Juglet reference correction in the corpus caveats of
   `AGENTS.md` if the lead agrees it belongs there.
## Follow-up (lead, 2026-11-10): the K=1 sweep finished, and the key is now saved with the ground truth

**The six outstanding K=1 jobs finished; the verdict is unchanged and now complete.** Pots D, E and I
(jobs 34620560 / 34620561 / 34620565, all COMPLETED 0:0):

| pot | floor | K=1 repeat 1 | K=1 repeat 2 | verdict |
|---|---|---|---|---|
| D | 23-25/28, 55-60/69 | 24/28 58/69 | 24/28 58/69 | at floor |
| E | 29-31/31, 57-62/62 | 26/31 44/62 | 28/31 51/62 | **below** |
| I | 25/26, 59/62 | 25/26 59/62 | 25/26 59/62 | at floor |

So the K=1 sweep ends **4 pots below floor** — A (joins 9/15), E (26-28/31, 44-51/62), H (9/11 11/17),
J (6/11 5-8/21) — against the 3 the pre-registered rule required to fail. Six pots hold at floor
(B, C, D, F, G, I). The three-line (K=3) arms for D, E and I were still RUNNING at 2h48m when this note
was written; they are not needed for either verdict and can be read from
`runs/20261110-0420_d628fc0_t322-pot<D|E|I>/score/acc.tsv` when they finish.

**The Juglet key is now where the ground truth lives.** The nine `Juglet_Piece_N_Axis.xyz` files from
`out/jugkey/key` were copied into `Dataset/Juglet_GT/` beside the nine `Juglet_Piece_N_T.txt` matrices,
in **both** Dataset copies (`/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset` and
`/data/gpfs/projects/punim2657/Dataset`), md5 identical between them. `README-axes.md` there records the
provenance, the format and the three caveats (33 mm vessel, 8 of 18 joins never touch, 9/9 unattainable);
a `README-not-a-reference.md` was dropped in `Dataset/Axes/Juglet/` so the old folder cannot be mistaken
for a reference again, and the project `AGENTS.md` now carries the same warning under its corpus caveats.

Read back after the copy: 9 axis files in each folder, `Juglet_Piece_1_Axis.xyz` md5
`e0f70a34288ea8f80fdd659908912961` in both, first line
`183.903911286378 148.464809059142 -134.053282670196 0.345475597391 0.356039490652 0.868264068532`.
