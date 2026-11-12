# Ticket 331 — juglet_large: build the vessel at 3x and run the whole chain

**Status:** results-in
**Working in:** C:/PR/worktrees/sfs/331-juglet-large
**Branch:** 331-juglet-large
**Answers:** S1
**Depends on:** 328 (merged to main 2026-11-12, commit `3ec34bd` — the wall side is cured, all nine joins face the same way)
**Blocks:** 332 (the assembly run on this input; not written yet)
**Worker:** d4b5fdfa-000b-4cbd-bf46-53d36196cdb1 (dsh one-shot subagent, dsh-opencode-go/deepseek-v4.1-flash; dispatched 2026-11-12 02:05 by the lead)
**Budget:** large (8 failed acceptance runs; waiting on Slurm costs none)

> **In one line.** The conservator's proposal (2026-11-11): the Juglet fails because its break edges are
> physically shorter than the matcher's window, so enlarge the source mesh 3x, call the new input
> `juglet_large`, and run the whole sampling / meshing / edgeline chain on it. This ticket builds that
> input and runs the chain. It does **not** run the assembler; 332 does, on these outputs.

## Why this is the right shape of test (read before starting)

The matcher recognises a join by walking along two edgelines and requiring a stretch of at least 7 dots
(`structure-from-sherds-pp class/feature_matching.cpp:294`, the LCS run-length floor). Dot spacing is a
fixed 1.9 mm (`edgeline_extraction_headless.cpp:574`, `RESAMPLE_D_MM`), so that window is about 12.6 mm of
real edge. On the curred Juglet four of the nine touching pairs never produce a candidate at all because
the matched run is 1-4 dots (ticket 329 bar 2, job 34725192: 1-2, 2-5, 2-9, 7-9), and the authors' own rule
excludes pieces under 50 points — nine-tenths of a 9 cm perimeter
(`papers/text/sfspp-2502.13986v1.md:329`). The vessel's 59/32/44/31/43/45/54/40/22 dots are below that.

Enlarging the mesh 3x raises the dot count ~3x while the spacing stays 1.9 mm, so the 7-dot window becomes
4.2 mm **of the original vessel** — the quantity that is currently binding.

It also makes every millimetre and area gate 3x stricter relative to the vessel (1.5 mm agreement becomes
0.5 mm at the original scale; 50 mm2 overlap becomes 5.6 mm2; 20 mm merge becomes 6.7 mm). That is the cost
side of the trade and it is why part C measures the matched stretch, not the seat count, before anything
is submitted to the queue.

## What is already known — numbers to reproduce, not re-derive

- Source meshes: `/data/gpfs/projects/punim2657/Dataset/Juglet/Piece01.obj` .. `Piece09.obj` (the nine
  real sherds; this is the "source obj file" the conservator means). Never write into that directory.
- Answer key: `Dataset/Juglet_GT/` holds `Juglet_Piece_<i>_T.txt` (9 rigid transforms into the assembled
  vessel frame) and `Juglet_Piece_<i>_Axis.xyz` (point + direction; **the last 6 numbers of the file are
  point xyz then direction xyz**), plus `Juglet_simple_graph.txt` (the touching pairs) and
  `README-axes.md`.
- Today's dot counts, pieces 1..9: **59, 32, 44, 31, 43, 45, 54, 40, 22** (ticket 68 Part C, job 34268623,
  run `runs/20261103-1546_6761aed_t68-densify2x`). Expect ~3x these at 3x scale.
- The chain's shipped defaults are still the sparse ones: `sphereRadius 1.8`
  (`edgeline_extraction_headless.cpp:485`) and `RESAMPLE_D_MM 1.9` (:574). Ticket 69's densification
  switches (`SFS_SPHERE_RADIUS_MM`, `SFS_RESAMPLE_D_MM`) exist and are **default off**; leave them off.
  This ticket tests size, not density; if the switches are also turned on the two effects are confounded
  and the result answers neither question.
- The wall side is cured (328): the interior face is filed by measured curvature, and the exported line's
  normals are re-derived against the wall it sits on. All nine touching pairs face the same way
  (dot_med_d3 +0.786..+0.997). Use main, not a branch.

## Part A — build the input (no queue time)

1. Create `/data/gpfs/projects/punim2657/Dataset/Juglet_large/` and write, **derived, never edited from
   the original**: `Piece01.obj` .. `Piece09.obj` with every vertex coordinate multiplied by **3.0**
   about the vessel's own origin, faces and vertex count unchanged. Record the md5 of each source obj and
   of each written obj in `scale_census.tsv`.
2. Write the scaled answer key in the same directory: `Juglet_Piece_<i>_T.txt` with the translation column
   multiplied by 3.0 and the rotation block unchanged (this is the only correct scaling of a rigid
   transform; verify by checking that the scaled transform maps the scaled piece onto the scaled vessel
   with the same residual as the original), and `Juglet_Piece_<i>_Axis.xyz` with the point multiplied by
   3.0 and the direction **unchanged**. Copy `Juglet_simple_graph.txt` unchanged.
3. Prove the scale is uniform and no axis was left unscaled: report, per piece, the bounding-box diagonal
   ratio written/source (must be 3.000 +/- 0.001) and the axis point / axis direction norms before and
   after.

## Part B — run the chain (queue time, small)

Run the standard preprocessing chain on `Juglet_large` — sampling, mesh, edgeline extraction and axes —
with the shipped defaults, in a run directory `runs/<YYYYMMDD-HHMM>_<git7>_t331-large`. Use the same
entry point and container the current main branch uses for the Juglet lane (read `hpc/` for the submit
scripts; do not invent a second path).

Report:
- **Dot counts per piece**, against today's 59/32/44/31/43/45/54/40/22. Acceptance: every piece above 50
  and the nine counts within 2.7-3.3x of the originals.
- **Axis sanity at 3x**: each piece's axis direction against the GT axis direction — the angles must match
  today's within 1 degree (scaling is a similarity; a change means the axis stage is size-dependent and
  that is a finding in its own right).
- **The matched stretch per touching pair, measured geometrically under the GT transform** (this is the
  number this ticket exists for): for each of the nine touching pairs, take the two breaklines, apply the
  GT transforms so both sit in the vessel frame, and measure the longest contiguous stretch where the two
  lines are within **1.5 mm** of each other. Report it in **mm and in dots**. Report the same two numbers
  for the unscaled Juglet, recomputed the same way, as the control.
  Acceptance: **at least 7 of 9 pairs reach a 12.6 mm matched stretch** (>= 7 dots at 1.9 mm). If they do
  not, say so plainly — that falsifies the seam-length explanation before any assembly run is spent.

## Part C — stop and hand over

Do not submit an assembly run. Part B's numbers decide whether 332 is worth the queue. Record everything
in the ticket Comments and end with your end state.

## Must not

- Write into `Dataset/Juglet/`, `Dataset/Juglet_GT/` or any existing corpus directory. The new input is a
  new directory; the originals are read-only inputs.
- Change any constant in the code. No `SFS_SPHERE_RADIUS_MM`, no `SFS_RESAMPLE_D_MM`, no edits to
  `RESAMPLE_D_MM` or `sphereRadius`. The point is that only the object's size changes.
- Touch the ten pots, or re-run any pot lane.
- Commit or push. The lead verifies from artefacts and lands.

## Deliverables

- `scale_census.tsv`, the run directory with logs and `out/`, the dot-count table, the axis-angle table,
  and the matched-stretch table with its control — in the ticket Comments, with the exact paths.

## Comments (worker, 2026-11-12)

### Part A — `Dataset/Juglet_large/` built and verified (done)

Built 2026-11-12, run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large/`,
builder `tools/build_large.py` (local copy `.scratch/pota-repro/t331/build_large.py`), log `logs/partA_build_large.log`.

**Deviation to declare: the source is `Dataset/Mesh/Juglet/Juglet_Piece_0N_Mesh.obj`, not
`Dataset/Juglet/Piece0N.obj`.** The ticket names the latter, but that file is the raw Blender export in file
units (bbox diagonal 1.241, 24294 verts but 24296 quads, not mm) and it is not what the chain reads:
`cc_mesh_to_pcd.sh`, the corpus manifest and `data_path.h` all take
`Dataset/Mesh/Juglet/Juglet_Piece_0N_Mesh.obj` (the mm scan-pose mesh, 24294 verts / 48592 tris, bbox
diagonal 63.054 mm). Scaling the raw export would have produced a 3x copy in file units that no stage of this
chain can consume. Both are measured and recorded in the census: `src_md5` (the mesh actually scaled),
`raw_md5` (the Blender export, provenance only) and `ratio_vs_raw` = 152.38155042578364 identically on all
nine.

Contents of `/data/gpfs/projects/punim2657/Dataset/Juglet_large/` (4.1 MB): `Piece01.obj` … `Piece09.obj`,
`Juglet_Piece_<i>_T.txt` (translation x3, rotation unchanged), `Juglet_Piece_<i>_Axis.xyz` (point x3,
direction unchanged), `Juglet_simple_graph.txt` (byte-identical copy), `scale_census.tsv`,
`scale_checks.json`.

- **Scaling law**: x' = 3x about the coordinate origin, T' = (R, 3t). Verified `R(3p)+3t == 3(Rp+t)` on every
  piece: max residual **4.547473508864641e-13 mm**.
- **Uniformity**: bbox diagonal ratio written/source = **3.0000000000** on all nine
  (2.999999999999998–3.000000000000002); vertex/face counts unchanged (24294/48592, 2565/5126, 3493/6982,
  3651/7298, 6211/12418, 5126/10248, 8421/16838, 4479/8954, 2094/4184); every non-`v` line byte-identical
  (`cmp` passes for all nine); the CRLF endings are preserved.
- **Axes**: point norms exactly x3 (e.g. 271.7218 → 815.1654, 529.2786 → 1587.8358 …), direction norms
  1.0 → 1.0 with the direction components unchanged; graph md5 `ccae01dd9c897e92beb0d507baa45cea` both sides.
- **Pairwise minimum distance under the key, scale 1 → 3** (x3.000000 on every pair, so key and meshes move
  together): touching 1-2 0.013813, 1-4 0.026865, 1-8 0.020019, 1-9 0.030007, 2-5 0.017219, 2-9 0.018789,
  3-5 0.014594, 6-7 0.010805, 7-9 0.012924 mm — all under 0.031 mm, the same nine touching pairs the AGENTS
  note records at 0.011–0.030 mm; non-touching 1-5 3.325, 1-6 3.638, 3-7 13.851, 4-5 4.864, 4-6 7.682,
  5-9 17.987, 6-8 0.617, 7-8 13.871, 8-9 18.846 mm. The nine/nine split is thus re-derived here rather than
  assumed.

### Part B — submitted

- Job **34874502** (`t331L`, sapphire, 1 node / 8 cpus / 64G / 2h), submitted 2026-11-12 15:36 local from
  `runs/20261112-0218_b1e1580_t331-large`; `submit.sbatch` md5 `8288d2232ecb55321f83aa279ae41edf`.
- Build: `git -C /data/gpfs/projects/punim2657/sfs_preprocessing archive b1e1580 | tar -x` (source md5s in
  `pins/src.md5`: mesh_processing_headless.cpp `8eab296c…`, edgeline_extraction_headless.cpp
  `ca177a1d…`, cc_mesh_to_pcd.sh `860fb2fd…`, run_cell66.sh `ae022e41…`), built in
  `pcl_191_nurbs.sif`; the ticket-328 markers are present (1 × `T328-LINENORMALS`, 5 ×
  `PAPER-234] t328:`).
- **No source edit and no constant change.** The one adapted file is `tools/stage_synth_t331.sh`
  (md5 `90391b0e…`, derived from the b1e1580 stager `9bb59676…` with exactly one line changed: the mesh
  root honours `MESH_ROOT`, default unchanged) so the 3x meshes can be staged as a corpus; the diff is
  `tools/stage_t331.diff` and the job refuses to continue unless it is exactly one line.
- Three cells over the same nine pieces, both binaries from b1e1580: `large_jug` (pot `Juglet_large`,
  3x meshes sampled here, key `Dataset/Juglet_large`, normal radius 1.0 mm = the shipped stage66 recipe),
  `ctl_jug` (pot `Juglet`, corpus cloud/mesh, key `Dataset/Juglet_GT`, the same 1.0 mm) and
  `large_rad3` (**diagnostic only**, 3x meshes with the scale-equivalent normal neighbourhood 3.0 mm — not
  the shipped recipe, reported separately).
- Sampling: the repo's `cc_mesh_to_pcd.sh -m 1000000 -f` on the nine 3x meshes into `cloud_mesh/`
  (per-piece kept_points/md5 in `pins/MANIFEST_JUGLET_LARGE.tsv`) — the corpus converter, not a second path.
- Corpus is read-only here: `Dataset/Juglet_large` md5s are taken before and after, and
  `Dataset/{Juglet,Juglet_GT,Point/Juglet,Mesh/Juglet}` md5s are re-listed after the run
  (`pins/*_after.md5`).

Status: running at the time of this comment; the next comment carries sacct State/ExitCode and the numbers.

### Part B — the nine cells and the matched stretch (interim; axes stage was still running)

Job **34874502** (`t331L`) is still in its 2h wall at the time of this comment. All three cells finished with
rc=0 (9/9 pieces each, every row `ok` with all markers): `large_jug` (3x, normal radius 1.0 mm = shipped
recipe), `ctl_jug` (unscaled control, same build, same 1.0 mm), `large_rad3` (diagnostic, 3.0 mm).
Rows: `outlarge_jug/pieces66.tsv`, `outctl_jug/pieces66.tsv`, `outlarge_rad3/pieces66.tsv`.

**Dot counts, Breakline_0** (the matcher's line; Breakline_1 in the next comment):

| piece | ticket ref (t68) | control, this build | 3x @ 1.0 mm | 3x @ 3.0 mm | 3x / ticket | 3x / control |
|---|---|---|---|---|---|---|
| 1 | 59 | 28 | 185 | 183 | 3.136 | 6.607 |
| 2 | 32 | 31 | 96 | 95 | 3.000 | 3.097 |
| 3 | 44 | 38 | 125 | 123 | 2.841 | 3.289 |
| 4 | 31 | 32 | 102 | 102 | 3.290 | 3.188 |
| 5 | 43 | 47 | 150 | 153 | 3.488 | 3.191 |
| 6 | 45 | 45 | 141 | 141 | 3.133 | 3.133 |
| 7 | 54 | 54 | 174 | 170 | 3.222 | 3.222 |
| 8 | 40 | 41 | 126 | 126 | 3.150 | 3.073 |
| 9 | 22 | 24 | 77 | 86 | 3.500 | 3.208 |

- All nine 3x pieces are **> 50 dots** (77–185), so the authors' 50-point floor is cleared on every piece.
- Against the ticket's reference column, **7 of 9** sit inside 2.7–3.3; pieces 5 (3.488) and 9 (3.500) are above
  the window, i.e. the 3x arm carries *more* dots than 3x there, not fewer.
- Against the **same-build control measured in this run**, 8 of 9 sit inside the window (2.841–3.289); piece 1 is
  outside only because its control came out at **28** where the ticket's reference and the 2026-11-10 t328 run
  both read **59**. The control's own numbers differ from the reference on pieces 1, 3, 5, 8, 9 — the mesh stage
  draws 30 random ray-cast points from an unseeded generator (mesh_processing_headless.cpp:1526), which *could*
  make the exported line, and with it the dot count, run-dependent. **The repeat disproved that on this build:**
  the follow-up job `34875510` (chained `--dependency=afterany:34874502`) re-ran the control into `outctl2/`
  and reproduced 28,31,38,32,47,45,54,41,24 exactly, so the gap to the reference column is not run-to-run noise
  here — see the final comment below.
- **Dot spacing is unchanged by the scaling**: median step between consecutive dots is **1.800 mm on both arms**
  (`out/stretch/dot_order.tsv`), so the matcher's 7-dot window still means 12.6 mm of the line it is looking at.

**Matched stretch, the nine touching pairs** (both lines in vessel frame under the answer key; longest
contiguous run of dots within tolerance of the other line's polyline; `out/stretch/stretch.tsv`). `1.5 mm` is
the ticket's bar in the arm's own frame; `4.5 mm` on the 3x arm is the same physical tolerance expressed on the
scaled model:

| pair | control @1.5 mm (dots / mm) | 3x @1.5 mm (dots / mm) | 3x @4.5 mm (dots / mm) |
|---|---|---|---|
| 1-2 | 6 / 9.00 | 8 / 12.60 | 47 / 82.80 |
| 1-4 | 0 / 0.00 | 13 / 21.60 | 21 / 36.00 |
| 1-8 | 0 / 0.00 | 16 / 27.00 | 64 / 113.41 |
| 1-9 | 1 / 0.00 | 0 / 0.00 | 24 / 41.40 |
| 2-5 | 1 / 0.00 | 1 / 0.00 | 5 / 7.20 |
| 2-9 | 5 / 7.20 | 13 / 21.60 | 18 / 30.60 |
| 3-5 | 6 / 10.98 | 12 / 22.84 | 19 / 32.40 |
| 6-7 | 18 / 30.60 | 44 / 77.40 | 51 / 90.00 |
| 7-9 | 6 / 9.00 | 16 / 27.00 | 19 / 32.40 |

- Control, 1.5 mm: **1 of 9** pairs reaches 7 dots / 12.6 mm (only 6-7); four pairs (1-4, 1-8, 2-5, 1-9) read 0–1
  dots. That is the known failure the ticket asked the control to reproduce.
- 3x arm, 1.5 mm: **7 of 9** reach both 7 dots and 12.6 mm — the acceptance bar, met exactly. The two that do not
  are **1-9** (0 dots) and **2-5** (1 dot).
- 3x arm, 4.5 mm (same physical tolerance): **8 of 9**; only **2-5** fails, and it fails at 5 dots / 7.20 mm —
  the same pair is the weakest in the control (1 dot / 0.00 mm), so it is a hard pair on its own terms, not a
  scaling artefact.
- Non-touching pairs at 1.5 mm: **0 dots on every one of the nine in both arms** (control shows a single 1-dot
  blip on 6-8), so the scaling created no false join (`out/stretch/stretch.tsv`, rows `nontouching`).

### Part B — final: both jobs ended, the control repeated, the axes, and the four acceptance items

**Jobs.** `34874502` (`t331L`) — sacct `COMPLETED`, `ExitCode 0:0`, `Elapsed 00:41:52` against a
`Timelimit 02:00:00` (`MaxRSS 3924496K`, `AllocCPUS 8`); `logs/job_status.log` reads `job 34874502 exit 0`;
all three cells rc=0 with 9/9 pieces each and every row `ok`; steps A–J all ran. **The 2h wall was enough** —
the 3x piece-1 mesh stage cost 455.77 s (`improveSurfaceBoundaryByFittingBSplineSurface`,
`mesh_processing_headless.cpp:2384`, loops all ~840k sampled points through
`fit.inverseMapping(..., im_max_steps=100, im_accuracy=1e-5)` at 2420–2446) but pieces 2–9 are much cheaper,
so the whole large cell took ~12 min, not the ~72 min extrapolated from piece 1. The follow-up `34875510`
(`t331A`, chained `--dependency=afterany:34874502`) — `COMPLETED 0:0`, `Elapsed 00:01:54` — re-ran the
control into `outctl2/`, found the axes stage already complete and skipped it, re-ran the stretch on both
controls and re-proved the corpus read-only.

**The control, measured twice on this one build** (the question the interim comment left open):

| Breakline_0 dots | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| `ctl_jug` | 28 | 31 | 38 | 32 | 47 | 45 | 54 | 41 | 24 |
| `ctl2` (repeat) | 28 | 31 | 38 | 32 | 47 | 45 | 54 | 41 | 24 |

Identical, and the two stretch runs emit identical `SUMMARY` lines, so **the control is reproducible on this
build** and the interim comment's unseeded-ray-cast explanation for the difference from the reference column
is not supported. The facts it has to explain: the ticket's column reads 59,32,44,31,43,45,54,40,22; the
2026-11-10 t328 run read 59,30,44,31,43,41,54,40,29 with **byte-identical binaries** (below); today reads
28,31,38,32,47,45,54,41,24 twice. Three sessions, three readings on six of nine pieces — I have not
established why and do not assert a cause. Consequence for item 1: **the ratio bar's denominator moves by up
to 2x on pieces 1,3,5,6,8,9**, so 3x/reference is not a stable test there; 3x/same-build-control is.

**Breakline_1** (the exterior line — not the line the matcher reads, recorded for completeness):
control 64,32,41,35,51,46,58,41,23 / 3x 206,106,131,114,162,146,185,133,78 /
3x@3.0 mm 207,106,132,113,163,144,185,133,77.

**Axis directions** (degrees, sign folded; `tools/axis_cmp_t331.py` → `out/axis_compare.tsv`, inputs
`axes_{ctl,large,rad3}/axes_summary_*.tsv` against `Dataset/Juglet_large` key directions):

| piece | ctl vs key | 3x vs key | 3x@3.0 vs key | 3x vs ctl | 3x@3.0 vs 3x |
|---|---|---|---|---|---|
| 1 | 1.073 | 1.113 | 0.932 | **0.062** | 0.180 |
| 2 | 13.165 | 8.795 | 3.856 | 19.812 | 5.069 |
| 3 | 28.412 | 8.613 | 9.806 | 29.427 | 1.487 |
| 4 | 3.577 | 4.753 | 8.432 | 1.234 | 4.215 |
| 5 | 2.703 | 5.550 | 5.533 | 2.890 | 0.226 |
| 6 | 1.637 | 2.325 | 5.141 | **0.765** | 3.418 |
| 7 | 3.948 | 3.099 | 3.460 | 1.444 | 2.394 |
| 8 | 3.030 | 3.019 | 3.486 | **0.476** | 0.849 |
| 9 | 3.808 | 6.045 | 8.760 | 5.486 | 2.718 |

3x-vs-control is **under 1 deg on 3 of 9** (pieces 1, 6, 8), under 3 deg on 6 of 9. On pieces 2 and 3 the
*control* is the arm far from the key (13.165 / 28.412 deg) while 3x (8.795 / 8.613) and 3x@3.0 (3.856 /
9.806) are closer; mean |vs key| is 6.82 deg (ctl), 4.81 (3x), 5.68 (3x@3.0). `rank0` equals `best` on all
nine in all arms; K differs between arms (control K=1 on pieces 2 and 3; 3x K=2 on 2 and 3 with a second
candidate 37.283 / 13.257 deg away; 3x@3.0 K=2–3), so part of the disagreement is candidate selection, not a
different answer from the same candidate.

**The four acceptance items, as measured.**

| # | item as written | result |
|---|---|---|
| 1 | every piece >50 dots **and** within 2.7–3.3x of 59/32/44/31/43/45/54/40/22 | >50: **MET** (77–185). Window: **7 of 9** — pieces 5 (3.488) and 9 (3.500) sit *above* it. Against the same-build control instead: **8 of 9** (2.841–3.289), piece 1 at 6.607 because its control is 28, not 59 |
| 2 | each scaled axis direction within 1 deg of unscaled | **NOT MET — 3 of 9** (pieces 1, 6, 8); six pieces differ by 1.2–29.4 deg (table above) |
| 3 | scale census bbox ratio 3.000 ± 0.001, with md5s | **MET** — 2.99999999999999–3.000000000000002 on all nine, `Dataset/Juglet_large/scale_census.tsv` (src/out md5, vertex and face counts equal, axis point- and direction-norm 1.0000000000) |
| 4 | ≥7 of the 9 touching pairs reach 12.6 mm matched stretch | **MET, exactly 7 of 9** at 1.5 mm (fail 1-9, 2-5); 8 of 9 at the scale-equivalent 4.5 mm (fail 2-5 only); control 1 of 9. Non-touching pairs: 0 dots in both arms (one 1-dot blip, control, pair 6-8). Dot spacing unchanged at 1.800 mm median on both arms |

**Provenance.** commit `b1e1580`, built by `git archive` of that commit only — no source edits; binaries
`MeshPreprocessingHeadless c521e82638cbf8865a01b89791817a7e`, `EdgeLineExtractionHeadless
a481f49ec5450adfa0de872fef7ed969`, both byte-identical to the 2026-11-10 t328 build's binaries. No constant
was changed: the one source-side deviation in this run is the stager's `MESH_ROOT` hunk already declared in
Part A. The 3x clouds were made with the repo's own `cc_mesh_to_pcd.sh -m 1000000 -f` (kept
840,419–841,576; `pins/MANIFEST_JUGLET_LARGE.tsv`), so the scaled corpus is built the same way as the
2026-10-31 Juglet rebuild.

**Read-only.** `pins/juglet_large.md5` == `_after` == `_after2` (`Juglet_large unchanged`); 20 GT files,
18 mesh files, 9 cloud files re-hashed unchanged after the jobs.

**Where it lives.** Run dir
`/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large/` (`run.json`,
`submit.sbatch`, `logs/`, `out/dotcounts.tsv`, `out/axis_compare.tsv`, `out/stretch/`, `out/stretch_ctl2/`,
`out/stretch/dot_order.tsv`, `axes_ctl/`, `axes_large/`, `axes_rad3/`, `cloud_mesh/`, `pins/`, `tools/`).
Scaled corpus `/data/gpfs/projects/punim2657/Dataset/Juglet_large/` (4.1 MB: 9 `Piece0N.obj`, 9
`Juglet_Piece_N_Axis.xyz`, 9 `Juglet_Piece_N_T.txt`, `Juglet_simple_graph.txt`, `scale_census.tsv`,
`scale_checks.json`).

**Not done, by contract.** No commit, no push, no branch or worktree change; the run index row is left for
the lead (verdict and human_note are human fields); the worker's local copies of the seven tools/scripts are
untracked in `.scratch/pota-repro/t331/` (68 KB, mirrors the run dir's `tools/`) and were deliberately not
committed.

**End state:** ready


## Lead verification (2026-11-12, lead)

**Verified independently from the run dir** `/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large/`
(every value below re-read or recomputed; my scripts are in `artifacts/`, not committed):

- **Jobs:** `34874502` t331L `COMPLETED 0:0` `00:41:52` (8 cpus); `34875510` t331A `COMPLETED 0:0` `00:01:54`.
- **Corpus:** piece-1 T translation `(281.684909, 236.451973, 353.370002)` -> `(845.054727, 709.355919, 1060.110006)`, exactly 3x, rotation rows bit-identical; piece-3 axis point `(3.957441336663, 227.428183075967, -118.727337732524)` -> `(11.872324009989, 682.284549227901, -356.182013197572)`, exactly 3x, direction `(-0.116579142656, 0.461215752670, 0.879596119243)` unchanged; `Juglet_simple_graph.txt` md5 `ccae01dd9c897e92beb0d507baa45cea` identical to the 1x copy (my own `md5sum`, not the worker's manifest).
- **Dots** (my parse of the PCD `POINTS` headers, not the worker's table): control `28/31/38/32/47/45/54/41/24`; 3x `185/96/125/102/150/141/174/126/77`; median dot step 1.800 mm in both arms.
- **Stretch** (my own recompute, `artifacts/t331_lead_verify_stretch.py`: GT transforms applied to each piece's Bl0, segment distance to the other polyline, longest contiguous run within 1.5 mm): 3x 1-2 = 8 dots, 1-8 = 16, 1-9 = 0; control 1-2 = 6, 1-8 = 0, 1-9 = 1. Matches `out/stretch/stretch.tsv`. 3x reaches 7/9 pairs at >=7 dots and >=12.6 mm (fails 1-9, 2-5), 8/9 at the scale-equivalent 4.5 mm (fails 2-5 only); non-touching pairs 0 dots.
- **Axis item 2:** `out/axis_compare.tsv` confirms 3x-vs-control under 1 deg on **3 of 9** (pieces 1 = 0.062, 6 = 0.765, 8 = 0.476); the other six differ 1.234-29.427 deg. **NOT MET**, as the worker reported. This does not block the ticket's purpose: the axis is not the binding gate (tickets 325/329/332).

**The control column is not the 1x baseline - corrected here.** The control cell does not reproduce ticket 332's 1x trees
(`20261112-0245_30b80ae_t332-dense-window12/work/gt/trees/base18/juglet`), which ran the same binaries:

| Breakline_0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 331 control | 28 | 31 | 38 | 32 | 47 | 45 | 54 | 41 | 24 |
| 332 base18 (1x) | 59 | 30 | 44 | 31 | 43 | 41 | 54 | 40 | 29 |

My polyline measurements locate the disagreement: on piece 1 the control's `Bl0` is **28 dots / 52.0 mm** while the same
piece's `Bl1` is **64 dots / 115.6 mm**, and 332's `Breakline_0` is **59 dots / 106.3 mm** - i.e. in the control the long
edge landed on the exterior line, which the assembler never reads. The other eight pieces agree within 12 %
(control `55.7/69.8/58.3/84.8/82.3/98.3/73.0/42.9` mm against 332's `54.9/81.0/56.3/78.5/74.6/96.5/72.0/53.6` mm).
So: the control is a usable *near* 1x reference on eight pieces, and **not** on piece 1. Consequences: the ticket's
`3x / reference column` ratios on pieces 1, 3, 5, 6, 8, 9 are not stable (the worker said this too), and **the ratio that
may be quoted is 3x against 332's 1x trees: 3.14 / 3.20 / 2.84 / 3.29 / 3.49 / 3.44 / 3.22 / 3.15 / 2.66** (last is
piece 9, below the ticket's 2.7 floor). The 1x baseline for every downstream claim is ticket 332's trees, not this
control column.

**Mesh provenance, checked and disposed of.** The control's own `stage.log` records `REAL-MESH .../mesh_large/Juglet_Piece_1_Mesh.obj`
(md5 `232c7f432cea387aef62412ae3ac3b1c`, the 3x mesh) with the 1x cloud and 1x axis - the stager's `MESH_ROOT` hunk
overrode the per-cell mesh. But the follow-up cell `outctl2` staged the corpus 1x mesh (`.../Dataset/Mesh/Juglet/...`,
md5 `b447066c29181fe7ba987439c22c5d9c`) and produced a **byte-identical surface** (S0 md5 `87295dcf7b8312b4af6d26513e02fca2`,
990,509 bytes, own `stages/.../Temp` - not a cache). The chain's surface/edge output does not depend on the mesh here,
so the mismatch is a provenance defect worth recording, not the cause of the piece-1 difference. **Cause of that
difference is not established**; I say so rather than assert one.

**Verdict.** The 3x side is established and independently reproduced: every piece carries 77-185 dots, the median dot
step is unchanged, seven of nine seams reach the matcher's 7-dot / 12.6 mm window at 1.5 mm (eight of nine at the
scale-equivalent 4.5 mm), and no non-touching pair produces a run. The control column is corrected above; item 2
(axes) is not met and is not load-bearing. **Part C (the assembler on this input) has not been run** - by the ticket's
own contract - and is the next experiment; note that at 3x the assembler's unmodified 1.5 mm agreement gate is
0.5 mm of the real vessel, so a 3x assembly run with shipped defaults tests something stricter than the 1x run did.

**End state:** results-in (3x input built and measured; control column corrected; assembler run pending a new ticket)

