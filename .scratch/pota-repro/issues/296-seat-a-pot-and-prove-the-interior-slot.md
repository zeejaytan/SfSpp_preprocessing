# 296 - Seat a pot's pieces, and prove the interior edge is the one we feed

**Answers:** E1
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-25)
**Branch:** 296-seat-a-pot-and-prove-the-interior-slot, in /c/PR/worktrees/sfs/296
**Created:** 2026-10-25

## Why

The extraction corpus is settled at 283 of 291 valid lanes at bar (FIXES-LEDGER sections P/R), but the
assembler consumes exactly ONE breakline per piece -- the _0 file -- and never reads _1 (verified 2026-10-25:
class/data_path.h names one Breakline_0 path per sherd; Breakline_1 appears nowhere in class/ or the build).
Everything downstream of the edge stage therefore depends on the interior lines only, and **no seating run has
happened since the strip (538357c + 67ff3d7) and the theta 3.4 change**. The known-good seating result
(Pot A 8/8 sherds, 15/15 joins, 2026-10-20) predates both and must be re-established, not quoted.

## Goal

Two arms on identical meshes and axes, Pot A (8 pieces), scored against the ground-truth join graph:

- **Arm CEILING** -- the authors' own Breakline_0 files.
- **Arm TEST** -- our Breakline_0 files, shipped defaults, current main.

Report seated sherds and joins for each arm and the drift between them. The ceiling arm exists to separate
"our extraction" from "the assembler or its paths": if the ceiling does not reach the reference result, the
harness is at fault and the test arm means nothing.

## Phase 0 -- prove the interior slot (do this first and report it)

The conservator's point: the slot is not a per-piece decision, it is done in preprocessing. Prove it, do not
assume it.

1. Cite the mechanism in the code at the commit in use: classifyAndOrderPaper234 sets Surface_0 to the
   interior face (mesh_processing_headless.cpp), and the writer names Surface_0 -> Breakline_0
   (edgeline_extraction_headless.cpp, the rename block). Give file:line for both.
2. For each of the 8 Pot A pieces in the staged bundle, measure which of our two surfaces is the physical
   interior -- concavity test, mean(n . r) with r pointing away from the axis, report the number per piece --
   and confirm Breakline_0 rides that surface (median distance of its points to it).
3. Confirm the classify step actually ran per piece: the [PAPER-234] classify line in the mesh log and the
   axis file staged. Without SFS_AXIS_FILE the step silently keeps size order (ticket 277); that is the only
   mechanism by which the slot can be wrong.

Verdict line: "8/8 our Breakline_0 rides the interior face" or the exception named with numbers.

## Phase 1 -- the seating run

- Assembler: the structure-from-sherds-pp repo (Spartan canonical checkout sfs_main/sfspreproc-docker;
  misleading name -- it is the ASSEMBLY code). Read that repo's AGENTS.md and hpc/README.md before starting;
  the documented loop is push, pull_and_sbatch, job_status, fetch_artifacts.
- Pot A is the object: 8 pieces, full-resolution meshes, the authors' axes, and a ground-truth graph
  (data_path.h references Ground Truth/Pot_A_simple_graph.txt).
- Scored numbers to report per arm: sherds seated out of 8, joins correct out of 15, plus the run's own
  totals. Reference on this object with the authors' lines: 8/8 and 15/15.
- If a swap appears to be needed to get a result, STOP and report: by the Phase 0 argument a swap is a bug
  signal now, not a step (FIXES-LEDGER section R).

## Constraints

- No source edits in either repo, no parameter sweep, no new threshold. This ticket measures.
- Never "build.sh --target nurbs" in SfSpp_preprocessing (it compiles the pre-247 duplicate at
  original_nurbs_preprocessing/); build from a pushed commit with git archive + cmake as tickets 288/294 did.
- One run directory per run under /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/
  with run.json + submit.sbatch + logs/ + out/, and an index row (verdict and human_note left EMPTY for the
  lead). Delete staged geometry at the end and say what you deleted.
- No worktrees on Spartan, no copies of either tree, no edits in the canonical checkout.
- Do not touch C:/PR/worktrees/... (none is in use) and do not write to any other clone.

## Acceptance

1. Phase 0 verdict with per-piece numbers and the two code citations.
2. Phase 1 both arms with seated sherds / joins and the reference beside them, each with its runid and jobid.
3. Every input path plus md5 recorded (mesh, axis, breakline per piece per arm).
4. An honest statement of what the result does and does not settle -- in particular, that Pot A is 8 pieces of
   one pot, so it is a readiness check, not a corpus result.

---

## Phase 0 -- result: the interior slot holds on 8 of 8 (measured 2026-10-25, commit `3d5d537`)

### (1) The mechanism, at the commit in use

`mesh_processing_headless.cpp:1990` defines `classifyAndOrderPaper234(...)`; it is called at `:2178`, i.e.
after the two faces have been merged and sorted by size (`:2174-2178`), so the order it produces is the order
the rest of the file sees.

- `:1995-1996` -- `const char* axPath = std::getenv("SFS_AXIS_FILE"); if (!axPath || !*axPath) { std::cout <<
  "[PAPER-234] classify: no SFS_AXIS_FILE, keep size order"; return; }`. Without the variable the step is a
  no-op and Surface_0 is whatever the size sort left first -- the one mechanism by which the slot can be wrong
  (ticket 277).
- `:2007-2023` -- per cluster it counts the points whose offset from the axis has a positive component along
  the point normal (`if (v.dot(nn) > 0.0f) ++inN;`), giving `inFrac`, and scores
  `satA = inFrac[0]*n0 + (1.0 - inFrac[1])*n1` against `satB`.
- `:2027-2031` -- if `satB > satA` it swaps the two clusters and prints `classify: swapped ->
  Surface_0=interior`; otherwise `:2033` prints `classify: kept -> Surface_0=interior`. Both branches end with
  **Surface_0 = interior face**.
- `edgeline_extraction_headless.cpp:3517-3525` -- the writer takes `currentFileName` (for example
  `Pot_A_Piece_01_Surface_0`), finds `"Surface_0"` and replaces it with `"Breakline_0"` (`_Surface_1` ->
  `_Breakline_1` in the else branch); `:3531` builds `datasetBreaklinesFolder + breaklineFileName + ".pcd"` and
  `:3536` `writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline)` writes it.

So the `_0` in a breakline filename is not a label: it is the same cluster the mesh stage called `Surface_0`,
and that cluster is the interior by construction. The rename is a string substitution over the surface the
line was extracted from -- there is no per-piece choice anywhere in the chain, which is the conservator's point.

### (2) Per piece, measured on our own staged bundle

Instrument: ticket 295's `p295_q1.pair_stats`, copied unchanged into the run (`scripts/p295_q1.py`, md5
`981b5bd6bcf88d5bcb970070b8574080`; `scripts/p295_lib.py`, md5 `e4e1c70db99de8e1063f698cff1f224b`) and driven
by `scripts/p296_interior.py` (md5 `a3a4eb2740c5c244d99e50e7b04584b5`). `m` = mean(n_hat . r_hat) with r_hat
pointing away from the axis, so **interior is m < 0**; `r50` = median radius (consistency check only);
`d_ridden` = median distance from the line's points to the surface it rides, `margin` = |d(S0) - d(S1)|.
Pre-registered abstains: |normal_dm| < 0.10 concavity not discriminative, |radial_dr| < 1.0 mm radius not
discriminative, margin < 0.50 mm ride not attributable, line ON surface when d <= 2.0 mm.

```
piece                m(S0)    m(S1)   normal_dm  r50(S0) r50(S1) radial_dr  s(S0)  s(S1)  interior  Bl0_ride d_ridden margin  on  rides_int
Pot_A_Piece_01     -0.120   +0.344    +0.464   38.18   43.37     +5.19 -0.930 -0.968    S0/S0  S0    0.237  4.765   1  YES
Pot_A_Piece_02     -0.614   +0.647    +1.261   82.47   84.73     +2.26 -0.990 -0.989    S0/S0  S0    0.254  3.136   1  YES
Pot_A_Piece_03     -0.611   +0.637    +1.248   78.60   80.76     +2.16 -0.989 -0.989    S0/S0  S0    0.216  3.189   1  YES
Pot_A_Piece_04     -0.613   +0.637    +1.250   78.01   80.24     +2.23 -0.992 -0.991    S0/S0  S0    0.211  3.279   1  YES
Pot_A_Piece_05     -0.605   +0.635    +1.240   79.53   82.13     +2.59 -0.988 -0.990    S0/S0  S0    0.233  3.377   1  YES
Pot_A_Piece_06     -0.694   +0.711    +1.404   83.82   86.46     +2.64 -0.984 -0.980    S0/S0  S0    0.251  2.927   1  YES
Pot_A_Piece_07     -0.850   +0.853    +1.703   32.32   35.56     +3.24 -0.987 -0.989    S0/S0  S0    0.171  3.529   1  YES
Pot_A_Piece_08     -0.480   +0.510    +0.990   55.49   57.09     +1.59 -0.980 -0.981    S0/S0  S0    0.241  3.134   1  YES
  concavity discriminative on 8/8; Surface_0 interior on 8 of those, Surface_1 on 0
  both criteria discriminative on 8; they name the same face on 8
  Breakline_0 rides the interior face, on its surface (<= 2.0 mm) with margin >= 0.50 mm: 8/8
```

Numbers worth reading off it: the concavity gap |normal_dm| is 0.46 mm to 1.70 mm on every piece, a factor of
4.6 to 17 above the 0.10 abstain line, and Surface_0 is the negative one on all 8; the radius agrees on 8/8
(interior smaller by 1.59 to 5.19 mm); our Breakline_0 sits 0.17-0.25 mm off Surface_0 and 2.9-4.8 mm off
Surface_1, so the ride is not marginal on any piece. Column `s` (mutual offset) is reported but not used:
ticket 295 measured that both faces' normals point away from each other, so its sign does not name the pot's
inside.

Control, same instrument, the authors' own lines against the authors' own surfaces (`out/q0_summary.txt`, second
block): 8/8, Surface_0 interior on 8 of 8, their Breakline_0 on their Surface_0 at 0.21-0.33 mm. The
instrument therefore reads a known-good bundle the same way it reads ours.

### (3) The classify step ran, on every piece

`SFS_AXIS_FILE` was set to the staged copy of the released axis for each piece (mesh stage only -- the edge
stage runs at the shipped defaults with no SFS_ variable). All 8 mesh logs carry the `[PAPER-234] classify`
line, i.e. the guard at `:1996` did not fire:

```
piece  face0 n / interior_frac   face1 n / interior_frac   decision   theta
01     32775 / 0.9685            27551 / 0.0000             kept       3.40000
02     22543 / 0.0000            20628 / 1.0000             swapped    3.40000
03     21172 / 0.0000            19382 / 1.0000             swapped    3.40000
04     17374 / 0.0000            15932 / 1.0000             swapped    3.40000
05     16570 / 0.0000            15256 / 1.0000             swapped    3.40000
06     11984 / 0.0000            10739 / 1.0000             swapped    3.40000
07      3093 / 0.0000             2850 / 1.0000             swapped    3.40000
08      2832 / 0.0000             2611 / 1.0000             swapped    3.40000
```

On pieces 02-08 the size order had the exterior first and `classifyAndOrderPaper234` swapped it -- the step is
doing work, not passing through. Piece 01 is the reverse (interior already first, kept). Theta is 3.40000 on
all 8, the shipped default, from the same line of the mesh log.

**Verdict: 8/8 our Breakline_0 rides the interior face.**

## Phase 1 -- result: both arms seat 8 of 8 and join 15 of 15

| arm | runid | jobid | sherds | joins | assembler candidates | kept after pruning |
|-----|-------|-------|--------|-------|----------------------|--------------------|
| reference on this object, authors' lines (ticket Goal) | -- | -- | 8/8 | 15/15 | -- | -- |
| CEILING -- the authors' own Breakline_0 | `20261025-2234_3d5d537_p296-ceiling` | 33780523 | **8 / 8 (100%)** | **15 / 15 (100%)** | 124 | 70 |
| TEST -- our Breakline_0, shipped defaults | `20261025-2234_3d5d537_p296-test` | 33780524 | **8 / 8 (100%)** | **15 / 15 (100%)** | 227 | 69 |

Drift between the arms: **0 sherds, 0 joins**. The ceiling arm reached the reference result, so the assembler
and its paths are not at fault and the test arm is readable. No swap was needed or made, and no runaway
per-piece intervention appeared.

The numbers are the assembler's own, printed from `class/data_structure.cpp:985` (sherd) and `:987` (edge) and
also written to `Result/1. Acc.txt`. Note that `:1004-1005` writes **both** lines with the label "Sherd
accuracy", so the second line of Acc.txt is the joins number; do not read it as a second sherd score. The
`Total number` lines are `main.cpp:212` and `:218` -- candidate pairs `LCS_out` before and after pairwise
pruning, not sherds.

Both arms are the same pinned assembler: `/opt/sfs-pristine` in
`/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif` (upstream `9195c0167e2077a564bd7c91156063252feeb506`),
built out-of-source in the job with the batch shim `hpc/tools/main_pristine_batch.cpp` from
`sfs_main/sfspreproc-docker`; the binary is identical in both arms, md5 `0fd8d707ceb3f9cffd08d8951c43ccda`.

## Numbers

### The inputs, per piece, per arm

`corpus` = `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`. All paths below exist under it;
staged copies live in each run's `out/inputs.md5` (57 rows: 8 mesh, 8 axis, 16 surfaces, 16 breaklines, 9
ground truth).

| piece | mesh `Mesh/Pot_A_Piece_NN_Mesh.obj` md5 / bytes (both arms) | axis `Axes/Pot_A_Piece_NN_Axis.xyz` md5 / bytes (both arms) | CEILING breakline `Breaklines/Pot_A_Piece_NN_Breakline_0.pcd` md5 / bytes | TEST breakline `p296-prep/out/geom/Pot_A_Piece_NN.Bl0.pcd` md5 / bytes |
|-------|------|------|------|------|
| 01 | `0d54f5cf8b73a98bae223c86930e0c8a` / 30,988,363 | `74086636b14717695cf12330c702bfca` / 107 | `5b0bc1975ab77fecd0b590cf642f96e8` / 16,369 | `f5c1a59054f77a54cf9d900695cdb6e0` / 13,762 |
| 02 | `985e4eb186ab1d1707ee70a292f763e0` / 17,164,343 | `c7edaa769cefbd0006d010239c6f5ace` / 107 | `6792660e274505dddc59d7e29dd356c7` / 14,982 | `31014721bb5a7afcf07f545a7ec24be7` / 10,997 |
| 03 | `40390e72e5940a13fba87e2ab2174f1e` / 12,602,227 | `4199c8b6c962c44abd44d216f83ff48d` / 109 | `395d3125e1f489a68b1ec84ef61cd3d8` / 13,661 | `d4bf74963be35fc1bb7d95603aadf7d3` / 10,124 |
| 04 | `3be349165928b40dc782529ad00f6437` / 10,214,186 | `e6d2b617bf303c7afe823a655603c146` / 108 | `46862ea02a9cf7beb5c27783d349774e` / 13,434 | `bdddaf3f3202e953198d167307d1c547` / 9,931 |
| 05 | `f7c8531e984ec8241ed1ef213db277f3` / 10,401,421 | `9bc89ee01d5b56ee9ebbd98d2a8be0c9` / 108 | `f5fdbca80c755be4316e6b0576e0e8da` / 12,718 | `da9aa390a1d1e04c1471463587791aec` / 9,547 |
| 06 | `ada13424d1dc25437bd7f4ab2f410091` / 8,865,427 | `97d9c450dc8acccc4f59c66ba813388a` / 108 | `3c5c4f8109776426236386477e59fad4` / 13,372 | `31c371f11ac63fc29440d62d15b538f6` / 8,800 |
| 07 | `1e16639d9847734cd9055085b14ab7b7` / 3,095,000 | `ab8edae4c50007a16433fbe940288209` / 320 | `55939132f37d63a22cfa021914ace0a6` / 5,724 | `a768d41b5f4a004c03f7cb524c79e31c` / 4,163 |
| 08 | `b07dbc7f4bbd0936a71b3f5607131ce8` / 3,045,744 | `8ddddecfd4d4ec7b3e49c9cbbbca7844` / 219 | `d578723c812d9c7192ff6bf2df6bcb16` / 5,533 | `c31f511938f8c45198f3ca4a5181e329` / 4,069 |

The two arms stage everything else from the same place: `Surfaces/Pot_A_Piece_NN_Surface_0.xyz`,
`_Surface_1.xyz`, `Breaklines/Pot_A_Piece_NN_Breakline_1.pcd` (inert -- never read), and
`Ground Truth/Pot_A_Piece_1..8_T.txt` + `Ground Truth/Pot_A_simple_graph.txt`. `Surface_F.pcd` is absent from
the corpus; `Geom::LoadSurface` tolerates it and the assembler prints `Could not open file ..._Surface_F.pcd`
once per piece in both arms.

### The code that produced the TEST arm

- commit `3d5d5379175d0731dffa1f0edb186a848093508e` of `zeejaytan/SfSpp_preprocessing`, archived by the job
  (`git archive $COMMIT | tar -x`), never a worktree, never a copy: `main` at the time of the run.
- binaries built inside `pcl_191_nurbs.sif` from that archive:
  `EdgeLineExtractionHeadless` md5 `cbf747dc3172fe0bbd188822df14092a`,
  `MeshPreprocessingHeadless` md5 `fb3fd055d30fb08ccce48dba7d49a879`.
- source md5s as built: `edgeline_extraction_headless.cpp` `f0dbfe7032d90a04412d15bd1699a703` (3739 lines),
  `mesh_processing_headless.cpp` `459dabe145056489829804292710b382` (2618 lines); `out/source.md5`.
- assembler: SIF md5 `63a532b9732f84e59e7b1349065f1323`, shim md5 `fb26e8ab49e9c00f7e8d02de44f6eea5`,
  built binary md5 `0fd8d707ceb3f9cffd08d8951c43ccda`.

### What was deleted at the end

Run P's `stage/` (582 MB: the 8 per-piece staging trees -- symlinks into the frozen corpus, the copied axis
files and the pipeline's Temp trees) and both arms' `dataset/` (242 MB and 121 MB: the staged /Dataset tree
plus the `Result/` the assembler wrote into it). What the assembler wrote is preserved as `out/Result/`
(`1. Acc.txt`, the `Top_1_Edgeline_*.xyz` files, `T_*to_*.txt`). Kept on purpose: run P's `out/geom/` (27 MB)
-- our 8 surfaces and 8 breakline pairs exactly as the TEST arm consumed them. The mesh stage draws unseeded
ray-cast points (`mesh_processing_headless.cpp:1526-1527`), so those files are not byte-reproducible and are the
only record of what the test arm was fed. Each run records its own deletion in `out/GEOMETRY_DELETED.txt`.
Nothing in the frozen corpus was copied, moved or written; the canonical checkouts were only read.

## Deviations

1. **First ceiling submission (33780064) died in 2 seconds**: `apptainer 1.3.3` has no `--mkdir`, and the
   script passed it. Bind targets are created automatically in this version, so the flag was dropped and the
   arm resubmitted. No parameter changed.
2. **Run P's job 33780063 did all the geometry and then crashed in the measurement's reporting step** --
   `summarise(prow, lrow, a.out)` at `p296_interior.py:116` passed the output path where the function expects the
   parsed options, so the summary text was never written (the per-piece TSVs had already been written). The
   call site was fixed and only the measurement re-run, as job 33780403 (12 s, exit 0), over the same
   `out/geom`. Instrument md5 `d6df97934c82a2b01344ee173c7c3ad6` -> `a3a4eb2740c5c244d99e50e7b04584b5`; no
   criterion, threshold or abstain line was touched.
3. **Ceiling job 33780374 produced 8/8 + 15/15 but exited 11**: the new fail-fast check I added after the
   `--mkdir` incident tripped on `Surfaces/Pot_A_Piece_NN_Surface_F.pcd`, which is absent from the corpus by
   design. The check was narrowed to ignore `_Surface_F.pcd` only, and the clean re-run is 33780523 (exit 0).
   That re-run reproduced 8/8, 15/15 and the binary md5 exactly -- a free reproducibility check, not a
   parameter change.
4. In each arm's `out/inputs.md5` the byte column for corpus rows is **the symlink's own size** (104 B = the
   length of the target path), not the file's. The md5 column is the target's content and matches the corpus
   file; true sizes are in the table above.
5. `run.json` is written by the submitting session, as the ledger requires; `verdict` and `human_note` in
   `index.tsv` are left EMPTY for the lead.
6. The comparison has no mesh-stage nondeterminism in it: both arms consume the same corpus meshes and the
   same preprocessed surfaces from run P, and differ only in the eight `_0` breaklines.

## Not measured

- **Our own surfaces are in neither arm.** Both arms load the corpus `Surfaces/`; the only difference between
  them is the breakline. This run tests the line we feed the assembler, not the surface extraction.
- **Breakline_1 is never read** -- staged inert in both arms, as `class/data_path.h` names only the `_0` path.
- **Pot A only**: 8 pieces of one pot, 15 joins. This is a readiness check that the pipeline still seats after
  the strip (`538357c` + `67ff3d7`) and the theta 3.4 change; it is not a corpus result and does not move the
  283/291 lane bar.
- **Both arms saturate.** 8/8 + 15/15 on both sides says the pipeline works and our line is good enough for
  this pot; it does not rank our extraction against the authors'. A pot where the two arms disagree is needed
  for that and none is measured here. Drift 0 is a floor result, not a ceiling on quality.
- **Geometry-level agreement is not measured**: the metric is the assembler's own sherd/edge accuracy against
  the ground-truth graph. The seated transforms (`Result/T_*to_*.txt`) were saved but no `part_acc` or chamfer
  distance was computed from them.
- **No comparison with the paper's per-pot scores**, and no claim about the other nine pots.
- Nothing was tuned: one run per arm, no sweep, no threshold, no source edit in either repo.
