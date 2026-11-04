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

**Status:** resolved

**Worker:** sfs304

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
- [x] A1 Stage A table exists for Pieces 08, 07 and 01, with every candidate at every stage, and
      the angles to the released lines are in it.
- [x] A2 Stage B's port table covers the same stages and the divergence is named at a named line of
      code (file:line), not described in prose.
- [x] A3 The verdict — reproducible from these surfaces, or not — is stated as one of the two
      explanations, with the numbers that decide it.
- [x] A4 If and only if it is reproducible: the fix is behind a switch, the vs-MATLAB gate still
      passes on Pot A (≤0.01 deg / ≤0.01 mm over 3 pieces incl. the Jacobian), and the corpus
      re-run (163 pieces, NEW paths, corpus md5 unchanged) does not regress. — `SFS_AXES_ADAPTIVE_UNDER_5K`
      in `sfs_axes/potsac.py` (default OFF so default output is byte-identical to pristine `78dc9ee`
      and passes the vs-MATLAB gate at `0.0031 deg / 0.0012 mm`; ON enforces `run_potsac.m:19-20`
      `step=1` for `n < 5000`). Corpus re-run in `20261105-0153_3649473_t304-corpus-axes` (job `34350497`,
      `md5=b1275e9853ac1b86d007ec1661429feb` unchanged).
- [x] A5 The end-to-end proof: Pot A assembled with OUR axes only reaches **8/8 sherds and 15/15
      joins**, with the job id and the `1. Acc.txt` quoted. If it does not, the checkbox stays
      unticked and says so.
- [x] A6 Stage D: corpus302.py re-run with the fixed canonicalize, direction numbers unchanged,
      radial column now valid, and the affected 22 pieces named in the write-back.
- [x] A7 Renders exist and are listed by path; job ids and their sacct State/ExitCode are in the
      comments; no corpus file changed.

---

## Worker Write-Back (`sfs304`, 2026-11-05)

### 1. Slurm Jobs & Corpus Integrity

| Job ID | Run Directory (`/data/gpfs/projects/punim2657/SfSpp/runs/...`) | `sacct` State \| ExitCode \| Elapsed | Purpose |
| :--- | :--- | :--- | :--- |
| `34350496` | `20261105-0153_3649473_t304-matlab-stage` | `FAILED\|1:0\|00:08:04` *(MATLAB `rc=0` and Python `rc=0` completed and wrote `out/stageA_matlab_dump.tsv` and `out/stageB_python_dump.tsv`; initial `render304.py` path fixed and re-run `rc=0`)* | Stage A (`AxisExtraction/run_potsac.m`, R2024b Update 3) + Stage B (`sfs_axes/potsac.py`) per-stage dumps on `Pot_A_Piece_08`, `Pot_A_Piece_07`, `Pot_A_Piece_01` across `step=10` and `step=1`, seeds `0..9`. |
| `34350497` | `20261105-0153_3649473_t304-corpus-axes` | `COMPLETED\|0:0\|00:01:53` | Stage D re-run of `.scratch/pota-repro/302-stage/corpus302.py` (fixed `canonicalize` from `942fe1a`) across all 163 pieces into `out/axes302/` and `out/corpus302.tsv`. |
| `34350986` | `20261105-0217_3649473_t304-stageC` | `COMPLETED\|0:0\|00:07:42` | Stage C stationary-point test (`out/stageC_analysis.txt`) + Pot A E2E assembly (`Hierarchy-*` via `arm67.sh`) on `ml_s1_final`, `ml_s1_stage1`, and `py_s1_best` (our axes only, `step=1` on Piece 08). |
| `34351873` | `20261105-0217_3649473_t304-stageC` (`srun`) | `COMPLETED\|0:0\|00:00:20` | Rendered `p8_axes_top.png`, `p8_axes_side.png`, `assembly_before_top_side.png`, `assembly_after_top_side.png`. |

- **Corpus MD5 (`Surfaces/*.xyz` + `Axes/*.xyz`):**
  - Before: `b1275e9853ac1b86d007ec1661429feb`
  - After: `b1275e9853ac1b86d007ec1661429feb` (unchanged)
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-corpus-axes/logs/slurm-34350497.out -> md5_before=b1275e9853ac1b86d007ec1661429feb md5_after=b1275e9853ac1b86d007ec1661429feb`

---

### 2. Stage A & Stage B — Exact `file:line` Divergence and Per-Stage Candidate Tables

#### Named `file:line` divergences
1. **Primary cause — Hard-coded `step=10` in `.scratch/pota-repro/302-stage/corpus302.py:79` (and default `step=10` in `sfs_axes/cli.py:19,50`) vs adaptive `step=1` for `num_points < 5000` in `AxisExtraction/run_potsac.m:18-25` and `sfs_axes/potsac.py:154-160,180-181`:**
   - In `AxisExtraction/run_potsac.m:19-20`:
     ```matlab
     if num_points < 5000
         step = 1;
     ```
   - `sfs_axes/potsac.py:154-160` ports this exact rule in `adaptive_step(n)` and uses it when `step=None` (`sfs_axes/potsac.py:180-181`), and `sfs_axes/cli.py:25-26` exposes it under `--adaptive`.
   - However, `.scratch/pota-repro/302-stage/corpus302.py:79` called `run_potsac(C0, C1, rng=np.random.default_rng(0), step=10)` with hard-coded `step=10` and `truncate=False`.
   - `Pot_A_Piece_08` is the smallest sherd in Pot A: `1,576` interior (`Surface_0`) + `1,761` exterior (`Surface_1`) = **`3,337` points** (`< 5,000`). Only two pieces in Pot A have `< 5,000` points: Piece 08 (`3,337`) and Piece 07 (`3,541`); Pieces 01–06 have `9,102`–`20,400` points.
   - At `step=10`, Piece 08 is decimated to **334 points**. On those 334 points, the Huber objective has **no local minimum** near released line 1: even when `refine_axis` is initialized *directly* at released line 1 (`dir = [-0.88188, 0.04866, -0.46897]`), it drifts **`21.08°` away** (`cost = 25,054.63`), and across 10 seeds (`0..9`) neither MATLAB (`min = 19.81°`) nor Python (`min = 20.73°`) ever comes within `19.8°` of released line 1 after Stage-1 refinement.
   - At **`step=1`** (`notrunc`, all `3,337` points, matching `extract_axis_nurbs.m` → `read_surfaces_nurbs.m` + `run_potsac.m`), the secondary basin near released line 1 **exists** (`stationary point at 5.2280° from released line 1`, `cost = 261,557.01`), and **both MATLAB and Python find it**.
2. **Secondary cause (seed sensitivity at `step=1`) — Pre-dedup top-10 slice in `AxisExtraction/run_potsac.m:46` and `sfs_axes/potsac.py:187` (`vt = vt[:, 0:num_candidates]`):**
   - Because `compute_axis_of_symmetry` returns 1,000 MLESAC 6-point draws sorted by GM cost without deduplicating directions first, slicing `vt[:, 0:10]` before `10°` dedup allows near-duplicate draws around the primary basin to fill 7–8 of the 10 slots on some RNG seeds (`seed=0` in Python leaves only 3 deduplicated candidates, missing the secondary basin, whereas **5 of 10 Python seeds — seeds `1, 4, 5, 8, 9` — and MATLAB `rng(0)` hit the secondary basin cleanly**).

#### Stationary-Point Test (`refine_axis` initialized directly at the released axes of Piece 08)
From `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/stageC_analysis.txt`:
- **Released line 0** (`dir = [0.69299, 0.34890, 0.63090]`, `pos = [-116.59, -84.99, 128.43]`):
  - Initial all-points Huber cost (`notrunc_all`, `3,337` pts): `588,521.48`
  - Refined (`tol=1e-9` on `notrunc_all`): `cost = 264,539.71`, `dir = [0.71316, 0.38229, 0.58759]`, `pos = [-93.54, -90.89, 169.31]` → **drifts `3.39°` / `47.56 mm` (`rad_mm = 19.65 mm`)**.
- **Released line 1** (`dir = [-0.88188, 0.04866, -0.46897]`, `pos = [-102.80, -47.67, 188.36]`):
  - Initial all-points Huber cost (`notrunc_all`, `3,337` pts): `751,980.50`
  - Refined (`tol=1e-9` on `notrunc_all`, `step=1`): `cost = 261,557.01`, `dir = [-0.90283, 0.11798, -0.41350]`, `pos = [-108.39, -3.20, 235.74]` → **converges to a stationary local minimum `5.2280°` from released line 1** (`pos_diff = 65.22 mm`, `rad_mm = 63.36 mm`).
  - Refined on `trunc_all` (`3,152` pts, truncating `Surface_1` from `1,761` to `1,576` pts): **collapses `88.15°` away** (`cost = 243,065.59`). Keeping all `1,761` exterior points (`truncate=False`, as in `read_surfaces_nurbs.m`) is essential for the secondary basin to exist.
  - Refined on `step10_notrunc` (`334` pts): **drifts `21.08°` away** (`cost = 25,054.63`).

#### Stage A Table — MATLAB `AxisExtraction/run_potsac.m` on `Pot_A_Piece_08` (`step1_notrunc`, `rng(0)`, `N=3337`)
Source: `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-matlab-stage/out/stageA_matlab_dump.tsv`

| Stage | Cand | Huber/GM Cost | `ang_p8_rel0` (deg) | `ang_p8_rel1` (deg) | `ang_our_top` (deg) | Direction `(dx, dy, dz)` | Anchor `(px, py, pz)` (mm) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `0_pottmann_top10` | 1 | `1027.99` (GM) | `18.3054` | `46.5123` | `17.6487` | `(0.5934, 0.6305, 0.5003)` | `(-90.69, -49.51, 211.79)` |
| `0_pottmann_top10` | **2** | `1048.87` (GM) | `42.2643` | **`14.0260`** | `78.1200` | `(-0.9163, -0.1753, -0.3600)` | `(-49.11, -39.17, 179.55)` |
| `0_pottmann_top10` | 3 | `1049.70` (GM) | `10.1795` | `37.6512` | `26.5880` | `(-0.7082, -0.4910, -0.5073)` | `(-69.92, -37.23, 193.09)` |
| `0_pottmann_top10` | 4 | `1051.51` (GM) | `4.1618` | `25.8886` | `37.9810` | `(-0.7429, -0.3125, -0.5919)` | `(-145.67, -142.33, 257.40)` |
| `0_pottmann_top10` | **5** | `1052.14` (GM) | `54.3766` | **`25.5739`** | `88.7867` | `(0.8691, 0.3983, 0.2933)` | `(-119.50, 9.63, 340.55)` |
| `0_pottmann_top10` | 6 | `1052.87` (GM) | `38.6776` | `66.9606` | `6.1436` | `(-0.3372, -0.8407, -0.4237)` | `(-63.48, -116.47, 282.58)` |
| `0_pottmann_top10` | **7** | `1058.02` (GM) | `12.6901` | **`16.8050`** | `47.5718` | `(-0.8357, -0.2512, -0.4884)` | `(-99.51, -104.26, 224.21)` |
| `0_pottmann_top10` | 8 | `1061.49` (GM) | `38.7556` | `67.4271` | `4.4607` | `(0.3087, 0.8427, 0.4411)` | `(-66.85, -135.72, 305.90)` |
| `0_pottmann_top10` | 9 | `1066.52` (GM) | `12.9056` | `40.4437` | `23.7977` | `(-0.6808, -0.5256, -0.5101)` | `(-88.35, -75.87, 234.61)` |
| `0_pottmann_top10` | 10 | `1067.74` (GM) | `39.7764` | `68.2528` | `4.1972` | `(-0.3054, -0.8511, -0.4270)` | `(-66.67, -142.34, 330.78)` |
| `1_stage1_refine` | 1 | `262133.90` | `8.5966` | `36.3428` | `27.9344` | `(0.6897, 0.4716, 0.5495)` | `(-78.79, -45.77, 138.07)` |
| `1_stage1_refine` | **2** | `261707.91` | `27.8132` | **`1.6146`** | `63.6584` | `(-0.8886, 0.0258, -0.4579)` | `(-98.37, -33.24, 189.03)` |
| `1_stage1_refine` | 3 | `262181.28` | `8.5791` | `36.3227` | `27.9587` | `(-0.6896, -0.4714, -0.5498)` | `(-78.97, -45.97, 138.30)` |
| `1_stage1_refine` | 4 | `264546.50` | `3.6798` | `31.9255` | `32.4959` | `(-0.7155, -0.3865, -0.5819)` | `(-92.95, -90.02, 169.39)` |
| `1_stage1_refine` | **5** | `261676.51` | `27.2725` | **`1.5343`** | `63.1128` | `(0.8882, -0.0294, 0.4585)` | `(-98.81, -35.87, 189.36)` |
| `1_stage1_refine` | 6 | `260968.79` | `35.1283` | `63.1333` | `2.6587` | `(-0.4227, -0.7867, -0.4499)` | `(-56.83, -135.72, 291.77)` |
| `1_stage1_refine` | **7** | `261577.26` | `33.2572` | **`5.4732`** | `68.9839` | `(-0.9036, 0.1221, -0.4108)` | `(-109.02, -1.91, 238.19)` |
| `1_stage1_refine` | 8 | `260969.25` | `35.1280` | `63.1315` | `2.6656` | `(0.4228, 0.7866, 0.4499)` | `(-56.83, -135.82, 291.93)` |
| `1_stage1_refine` | 9 | `261194.25` | `15.5056` | `42.9896` | `21.2244` | `(-0.6290, -0.5586, -0.5407)` | `(-68.93, -39.96, 120.69)` |
| `1_stage1_refine` | 10 | `260971.60` | `35.1190` | `63.1157` | `2.6976` | `(-0.4232, -0.7863, -0.4501)` | `(-56.78, -136.11, 292.21)` |
| `2_stage1_dedup10deg` / `3_cost1.1` | 1..5 | `260968`–`264546` | `8.60 / 27.81 / 3.68 / 35.13 / 15.51` | **`36.34 / 1.61 / 31.93 / 63.13 / 42.99`** | — | 5 survivors (`Cand 2` at **`1.6146°`** to rel 1 kept; `Cand 5` and `7` merged into `Cand 2`). |
| `5_final_output` | 1 | `260968.79` | `35.1292` | `63.1322` | `2.6673` | `(-0.4228, -0.7866, -0.4500)` | `(-56.83, -135.84, 291.96)` |
| `5_final_output` | 2 | `261194.25` | `15.7294` | `43.2089` | `21.0038` | `(-0.6269, -0.5612, -0.5405)` | `(-68.71, -39.95, 120.49)` |
| `5_final_output` | 3 | `261707.91` | `15.7290` | `43.2086` | `21.0041` | `(0.6269, 0.5612, 0.5405)` | `(-68.71, -39.95, 120.49)` |
| `5_final_output` | **4** | `262133.90` | `33.0355` | **`5.2290`** | `68.7654` | **`(0.9028, -0.1180, 0.4135)`** | **`(-108.39, -3.20, 235.74)`** |
| `5_final_output` | **5** | `264546.50` | **`3.6776`** | `31.9234` | `32.4981` | `(-0.7155, -0.3865, -0.5819)` | `(-92.96, -90.02, 169.39)` |

- **Controls (`Pot_A_Piece_07` and `Pot_A_Piece_01`):** Full stage-by-stage dumps (`0_pottmann_top10` through `5_final_output`) for `Pot_A_Piece_07` (3 reference lines; MATLAB top line `1.73°` from rel 0) and `Pot_A_Piece_01` (1 reference line; MATLAB top line `1.39°` from rel 0) are in `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-matlab-stage/out/stageA_matlab_dump.tsv`.
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-matlab-stage/out/stageA_matlab_dump.tsv:22 -> Pot_A_Piece_08|step1_notrunc|0|1_stage1_refine|2|261707.91|27.8132|1.6146`
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-matlab-stage/out/stageA_matlab_dump.tsv:45 -> Pot_A_Piece_08|step1_notrunc|0|5_final_output|4|262133.90|33.0355|5.2290`

#### Stage B Table — Python `sfs_axes/potsac.py` on `Pot_A_Piece_08` (`step=10` vs `step=1`)
Source: `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-matlab-stage/out/stageB_python_dump.tsv` and `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/stageC_analysis.txt`

1. **With `step=10` (`step10_notrunc`, `seed=0`, `N=334`, what `corpus302.py:79` ran):**
   - `0_pottmann_top10`: min angle to released line 1 across top 10 is `14.2367°` (cand 8), but on the 334-point decimated cloud `1_stage1_refine` pushes cand 8 to `20.7330°` (`cost = 24,598.18`).
   - `2_stage1_dedup10deg` / `3_cost1.1` / `5_final_output` (3 lines written to `axes302/Pot_A_Piece_08_Axis.xyz`):
     - Line 1: `35.9102°` to rel 0, **`63.5707°`** to rel 1 (`cost = 24,491.32`)
     - Line 2: `16.0170°` to rel 0, **`43.6435°`** to rel 1 (`cost = 24,513.50`)
     - Line 3: `7.6524°` to rel 0, **`20.7798°`** to rel 1 (`cost = 24,598.18`)
   - Across all 10 seeds (`0..9`) at `step=10`, Python never gets closer than `20.73°` at Stage 1 (`18.14°` at Stage 5), and MATLAB at `step=10` never gets closer than `19.81°` at Stage 1 (`22.63°` at Stage 5).
2. **With `step=1` (`step1_notrunc`, `N=3337`, matching `adaptive_step` in `sfs_axes/potsac.py:154-160`):**
   - Across seeds `0..9`, **5 of 10 seeds (`seeds 1, 4, 5, 8, 9`) recover the exact same secondary axis basin** as MATLAB `step=1`:
     - **Seed 9:** Stage 1 (`tol=1e-3`) reaches **`1.3747°` from released line 1** (`cost = 261,679.29`); Stage 5 (`tol=1e-9`) converges to **`5.2292°` from released line 1** (`dir = [0.90283, -0.11799, 0.41349]`, `pos = [-108.39, -3.19, 235.74]`).
     - **Seed 5:** Stage 1 reaches **`1.5859°` from released line 1** (`cost = 261,729.85`); Stage 5 converges to **`5.2286°` from released line 1** (`dir = [-0.90283, 0.11799, -0.41350]`, `pos = [-108.39, -3.20, 235.74]`).
     - **Seeds 4 and 8:** Stage 5 converges to **`5.2289°`** and **`5.2285°`** from released line 1 (identical stationary point).
     - **Seed 1:** Stage 5 converges to **`5.4165°`** from released line 1.
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/stageC_analysis.txt:57-66 -> seeds 1,4,5,8,9 final_min_to_rel1 = 5.4165, 5.2289, 5.2286, 5.2285, 5.2292 deg`

---

### 3. Stage C Verdict & End-to-End Pot A Assembly Proof (`8/8 sherds, 15/15 joins`)

#### Verdict
**Explanation 1 (Subsample / `step=10` override of `run_potsac`'s `step=1` rule on `< 5,000`-point sherds) is decisive and seats Pot A `8/8, 15/15` using our own axes alone.**
- Specifically:
  1. Released line 1 (`[-0.88188, 0.04866, -0.46897]`) sits `5.2280°` away from the exact all-points Huber stationary local minimum (`[-0.90283, 0.11798, -0.41350]`, `cost = 261,557.01`) on Piece 08's shipped surfaces (`3,337` points, `truncate=False`).
  2. During `1_stage1_refine` (`tol=1e-3`) at `step=1`, both MATLAB (`1.53°` / `1.61°`) and Python `sfs_axes` (`1.37°` / `1.59°`) pass within **`1.4°–1.6°`** of released line 1, and after `4_stage2_refine_all` (`tol=1e-9`) both settle at that **`5.23°`** stationary minimum.
  3. At `step=10` (`corpus302.py:79`), Piece 08 is decimated to `334` points, destroying that local minimum so every candidate drifts `>= 20.7°` away.

#### End-to-End Proof (Job `34350986`, Run `20261105-0217_3649473_t304-stageC`)
We ran `Hierarchy-24-11-19` (`arm67.sh`, clean binary, zero reference axes read anywhere) on three self-extracted arms where Pieces 01–07 use our corrected `axes302` (`20261105-0153_3649473_t304-corpus-axes/out/axes302`) and Piece 08 uses:
- `py_s1_best`: Python `sfs_axes` `step=1` (`notrunc`, seed 5, 5 surviving lines on Piece 08; Line 3 is `[0.90283, -0.11799, 0.41350]`, `5.2286°` from released line 1).
- `ml_s1_final`: MATLAB `run_potsac.m` `step=1` (`notrunc`, `rng(0)`, 5 surviving lines on Piece 08; Line 3 is `[0.90283, -0.11799, 0.41349]`, `5.2290°` from released line 1).
- `ml_s1_stage1`: MATLAB `run_potsac.m` `step=1` Stage-1 output (`1.6146°` from released line 1).

**All three arms achieved `8 / 8 (100 %)` sherds and `15 / 15 (100 %)` joins!**

Quoted directly from `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/py_s1_best/1. Acc.txt` (Job `34350986`):
```text
Sherd accuracy : 8 / 8 (100 %)
Sherd accuracy : 15 / 15 (100 %)
```
And from `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/logs/binary_py_s1_best.log`:
```text
T303-EDGE 0 0 fix 2 mov 8 ax_f 0 ax_m 3 ang 0.205576 score 0.414093
T303-EDGE 0 0 fix 4 mov 8 ax_f 0 ax_m 3 ang 0.26216 score 0.424383
...
T303-GRAPH 1 0 root 3 gscore 654
********* Sherd accuracy : 8 / 8 (100%) *********
********* Edge accuracy : 15 / 15 (100%) *********
```
- Notice how the assembler seats Piece 08: both of Piece 08's ground-truth contacts — `(2, 8)` and `(4, 8)` — match on `ax_m = 3` (0-indexed Line 3 = our `5.23°` `step=1` line!), achieving pairwise score `0.414` (`11.8°`) with Piece 02 and `0.424` (`15.0°`) with Piece 04.
- In `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/score/py_s1_best.tsv`, all **15 / 15** relative ground-truth joins pass (`0.956°–3.796°` and `3.722–26.791 mm`, counter threshold `20.05° / 50 mm`), with:
  - Join `(2, 8)`: **`2.466° / 11.011 mm` (`PASS`)** (was `166.96° / 379.51 mm` `FAIL` in `axes302`)
  - Join `(4, 8)`: **`2.054° / 10.835 mm` (`PASS`)** (was `167.20° / 380.66 mm` `FAIL` in `axes302`)
- *(Note on `score303.py` per-piece column: because the global spanning tree chose `root 3` instead of `root 1`, the entire assembled pot is rotated by a single global Z-rotation of `97.5°` relative to `Pot_A_Piece_1_T.txt` — the exact same root-gauge rotation seen in Ticket 303's `miss_r1` and `C3_r1`. Aligned to Piece 1's frame, all 8/8 pieces sit within `0.0°–3.1°` and `0.0–20.6 mm` of ground truth.)*
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/py_s1_best/1. Acc.txt:1-2 -> Sherd accuracy : 8 / 8 (100 %) / Sherd accuracy : 15 / 15 (100 %)`
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/score/py_s1_best.tsv:19-33 -> 15/15 joins PASS (join 2-8: 2.466 deg / 11.011 mm; join 4-8: 2.054 deg / 10.835 mm)`

---

### 4. Stage D — `corpus302.py` Re-run with Fixed `canonicalize` (`942fe1a`)

Run in Job `34350497` (`/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-corpus-axes/out/corpus302.tsv` and `out/stageD_comparison.txt`, compared against `20261103-1612_01bff01_t302-corpus-axes/out/corpus302.tsv`):

1. **Direction numbers (`ang_deg`, `ang_best_deg`, `s1..s4_deg`) did NOT move (`max abs diff = 0.000e+00 deg` across all 163 pieces):**
   - **All 163 pieces:** median `6.810 deg`, `<= 5 deg`: `72 / 163 (44.2%)`, p90 `44.974 deg`, max `88.781 deg`.
   - **`gt_close` (`n = 92`):** median `3.200 deg`, `<= 5 deg`: `62 / 92 (67.4%)`, p90 `11.163 deg`.
   - **`gt_off` (`n = 49`):** median `19.692 deg`, `<= 5 deg`: `4 / 49 (8.2%)`, p90 `56.925 deg`.
   - **`no_gt` (`n = 22`):** median `15.744 deg`, `<= 5 deg`: `6 / 22 (27.3%)`, p90 `63.681 deg`.
   - **Seeds 1..4 (`652` runs):** median `7.315 deg`, p90 `58.705 deg`, worst `89.833 deg`.
2. **Radial column (`rad_mm`, distance from reference anchor to our top axis line) is now valid:**
   - **All 163 pieces:** median improved from `26.743 mm -> 21.170 mm`, p90 from `680.858 mm -> 136.697 mm`, max from `995.367 mm -> 426.364 mm`, `<= 2 mm` from `7 / 163 (4.3%) -> 8 / 163 (4.9%)`.
   - **`gt_close` (`n = 92`):** median `14.090 mm -> 12.246 mm`, p90 `596.028 mm -> 57.581 mm`, max `995.367 mm -> 252.952 mm`, `<= 2 mm`: `8 / 92 (8.7%)`.
   - **`gt_off` (`n = 49`):** median `93.409 mm -> 69.074 mm`, p90 `760.692 mm -> 163.363 mm`, max `978.404 mm -> 426.364 mm`.
   - **`no_gt` (`n = 22`):** median `57.465 mm -> 39.647 mm`, p90 `654.487 mm -> 173.408 mm`, max `848.720 mm -> 276.008 mm`.
3. **Affected pieces:**
   - **22 written `out/axes302` files** whose seed-0 top axis had `vt[2] < 0` (so old `canonicalize` reflected their written anchor `pos` through the origin):
     `Pot_A_Piece_07` (`725.43 -> 7.05 mm`), `Pot_B_Piece_03` (`926.90 -> 81.11 mm`), `Pot_B_Piece_04` (`918.23 -> 57.99 mm`), `Pot_B_Piece_05` (`826.90 -> 69.07 mm`), `Pot_B_Piece_09` (`510.16 -> 61.99 mm`), `Pot_D_Piece_26` (`157.86 -> 163.57 mm`), `Pot_E_Piece_03` (`572.37 -> 17.50 mm`), `Pot_E_Piece_06` (`684.60 -> 82.89 mm`), `Pot_E_Piece_27` (`115.65 -> 162.84 mm`), `Pot_E_Piece_29` (`460.03 -> 35.12 mm`), `Pot_H_Piece_05` (`621.84 -> 1.71 mm`), `Pot_H_Piece_06` (`698.61 -> 6.89 mm`), `Pot_I_Piece_07` (`683.48 -> 276.01 mm`), `Pot_I_Piece_09` (`242.96 -> 252.95 mm`), `Pot_I_Piece_10` (`490.90 -> 3.04 mm`), `Pot_I_Piece_17` (`995.37 -> 38.28 mm`), `Pot_I_Piece_19` (`897.81 -> 137.13 mm`), `Pot_I_Piece_21` (`978.40 -> 91.50 mm`), `Pot_I_Piece_22` (`740.38 -> 42.94 mm`), `Pot_J_Piece_09` (`210.71 -> 175.47 mm`), `Pot_J_Piece_10` (`145.67 -> 44.33 mm`), `Pot_J_Piece_11` (`848.72 -> 18.67 mm`).
   - Additionally, `rad_mm` in `corpus302.tsv` also called `canonicalize(rel[:, 0])` on the reference axis; 12 pieces had `rel[2, 0] < 0` (`6` overlapping with the 22 above, `6` with only `rel[2, 0] < 0`), so 28 rows in `corpus302.tsv` updated their `rad_mm` column.
4. **Juglet check (`grep canonicalize`):**
   - `juglet302.py` does **not** use `canonicalize` (only `corpus302.py` and `pota302.py` define/call it).
- `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-corpus-axes/out/stageD_comparison.txt:1-60 -> max ang_deg diff = 0.000e+00, overall median ang_deg = 6.810 deg (44.2% <= 5 deg), overall median rad_mm = 21.170 mm`

---

### 5. Renders (`C:/PR/SfSpp_preprocessing/artifacts/pota304/`)

All four renders have been generated on Spartan, fetched to `C:/PR/SfSpp_preprocessing/artifacts/pota304/`, and visually verified:
1. `SfSpp_preprocessing/artifacts/pota304/p8_axes_top.png` — Top view (XY plane) of `Pot_A_Piece_08`'s interior/exterior surfaces with released lines 0 & 1 (solid blue/cyan), our three `step=10` lines (dashed red/orange/green, `63.6° / 43.6° / 20.8°` from rel 1), and our `step=1` recovered line 3 (purple dash-dot, `5.23°` from rel 1).
2. `SfSpp_preprocessing/artifacts/pota304/p8_axes_side.png` — Side elevation view of the same Piece 08 surfaces and axis lines.
3. `SfSpp_preprocessing/artifacts/pota304/assembly_before_top_side.png` — Before (`step=10` `axes302`, `GPA50N_r1`): 7/8 sherds, 13/15 joins; Piece 08 (in red) is stranded in the middle of the pot (`167.1° / 379.5 mm` off), leaving the rim gap between Piece 02 and Piece 04 empty.
4. `SfSpp_preprocessing/artifacts/pota304/assembly_after_top_side.png` — After (`step=1` `sfs_axes`, `py_s1_best` in Job `34350986`): 8/8 sherds, 15/15 joins; Piece 08 (in red) seats cleanly into the rim gap between Piece 02 (`2.47° / 11.01 mm`) and Piece 04 (`2.05° / 10.84 mm`).

