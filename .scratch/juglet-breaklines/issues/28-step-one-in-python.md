# 28: step 1 replicated in Python — why does piece 2 grow nothing, and which figure is wrong

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 28-step-one-in-python, in /c/PR/worktrees/sfs/28

Piece 2 is the plainest failure on the vessel: 1 031 points go into the region growing and **every region it
grows is discarded** — the rung-2 sidecar reads `"clusters": []`, `points_in_no_cluster: 1031`, with the
parameters the run actually used (`theta 3.4, kappa 1.0, nb 10, floor_applied 50`), and the 21 retries repeat
it identically. Nobody has ever seen the regions that were thrown away, so nobody can say whether growth dies
at the first hop or grows forty-point patches just under the floor. That number decides the repair, and it is
cheap to get.

**This ticket changes no production code.** It is a Python replica of the growth step plus a figure grid, run
against geometry that already exists on disk.

## The paper's step, verbatim

`C:/PR/papers/text/sfspp-2502.13986v1.md:151`: "we use the region growing algorithm [35]. This algorithm
starts from the point with the minimum curvature and expands by combining the $n_b=10$ neighboring points that
have a curvature value of less than $\tau_\kappa$ and a normal angle less than $\tau_\theta$ with the point's
normal. We set the values of $\tau_\theta$=4 and $\tau_\kappa$=1 ...", and `:155`: "Finally, we select the two
largest clusters, representing the inner and outer surfaces."

**The constants we run are the authors' own, not our inventions** — `minCluster = 50` and `noOfNeighbours = 10`
are at `original_nurbs_preprocessing/.../mesh_processing_headless.cpp:2200` in the September tree
(`artifacts/old-vs-new/old.cpp:2200`), the dynamic floor `max(minCluster, max(30, Npts/500))` at its `:1733`,
and the 0.6 mm radius downsampler is their `downsamplePointCloud(inputPcdFile, 0.6F)`. So the tuning space is
**the figures inside their method**: `tau_theta` (4 in the paper, 3.4 in our default since ticket 271), `nb`
(10), `tau_kappa` (1), the floor (50), and the density the growth sees.

## The replica, and how it is proved correct before it is believed

Write it in Python (numpy + scipy is enough; PCL is not required) and **calibrate it against the C++ before
any conclusion is drawn from it**:

- Read the rung-1 dumps ticket 25 kept. They carry points, normals and the parameters:
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0337_d69f76f_t25-dump-grid2/out/dump/{B,E}/Juglet_Piece_{2,3,5,7}/r1_downsampled.ply`
  (arm **B** = today's defaults, 0.6 mm; arm **E** = paper chain off at **native** density). Each is ASCII PLY
  with `x y z nx ny nz cluster_id reason`, so the replica consumes exactly the points and normals the C++ did.
- Replicate `growPaper234` (`mesh_processing_headless.cpp:2940`, called at `:3438`; one pass, seeds visited
  flattest-curvature-first, a claimed seed skipped, a neighbour joins only if its normal is within `theta` of the
  **current front point's** normal and its curvature is under `kappa`, `nb` neighbours examined, then the floor).
- **The calibration gate:** with `theta=3.4`, `nb=10`, `kappa=1`, `floor=50`, on arm B, the replica must return
  exactly `[169, 99]` for piece 3, `[679]` for piece 5 and `[326, 263, 77, 68, 65]` for piece 7, in the same
  order of size. If it does not, the replica is wrong: report the mismatch and **stop** — nothing downstream
  from an uncalibrated replica is evidence.

## What to measure, once it is calibrated

1. **The answer for piece 2.** Every region grown, with its size, in order, **before the floor is applied**; the
   number of expansion steps the largest reached; and for the growth that stopped, the distribution of the
   neighbour tests that failed (angle over `theta` versus curvature over `kappa`). State whether the largest
   region was 1, 5, 20 or 40 points — that is the number that decides the repair.
2. **The figure grid**, same replica, 16 cells: `theta` in {3.4, 4.0} x cloud in {B (0.6 mm), E (native)} x
   floor in {50, none}, on pieces 2, 3, 5, 7. For each cell report the region sizes before and after the floor,
   and how many regions of at least 50 points survive.
3. **The Pot A control.** No rung-1 dump exists for Pot A, so produce one: a single pipeline run with
   `SFS_DUMP_STAGE` armed for `Pot_A_Piece_07` only (one piece, today's defaults). Then run the same replica and
   the same 16-cell grid on it. Pot A is the case the method is known to work on, so it is the reference for
   what a healthy growth looks like: report its region sizes before and after the floor.
4. **Which figure, if any, gives piece 2 two regions of at least 50 points,** and what that same figure does to
   pieces 3, 5, 7 and Pot A 07. Report the effect; do not choose.

## Evidence to return

1. The calibration result, piece by piece, against the three lists quoted above, with the replica's own output.
2. Piece 2: the full region-size list before the floor, the expansion depth reached, and the failed-test counts.
3. The 16-cell grid table for the Juglet, plus the Pot A table, each row naming theta, cloud, floor, region
   sizes and surviving count.
4. The replica source, committed under `.scratch/juglet-breaklines/stage28/`, and the run directory name.
5. The Pot A 07 dump's run id, sacct State/ExitCode, and the rung-1 file's point count and md5.
6. The paper lines you relied on, quoted with file and line number.
7. Job ids with sacct State and ExitCode; corpus md5 before and after; `/opt/sfs-pristine` recorded ABSENT if
   absent.
8. Index rows appended with `verdict` and `human_note` **empty** (six tab-separated fields).

## Constraints

- **Compute nodes only** for anything that produces a number; the replica is cheap and still does not run on
  the laptop or the login node. At most TWO jobs (one pipeline run for the Pot A dump, one for the replica grid).
- Do **not** modify `mesh_processing_headless.cpp` or any other production file: this ticket is read-only on the
  pipeline. If you believe a code change is needed to answer a question, stop and ask instead.
- Two other tickets may be running at the same time; only write inside your own worktree, your own run
  directories, and append to `index.tsv` with a single command, then read the file back to confirm six fields.
- Corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` and `/opt/sfs-pristine` are read-only;
  md5 before and after.
- Delete no geometry until its numbers are in the table; then delete the pipeline run's stage geometry with a
  counted record and **keep the rung-1 dumps the replica needs**, saying so.
- Check the CRLF of every script before submitting.
- No write to `intent/`, no merge, no close, and **no verdict** — report measurements, the lead decides.

## What this cannot settle

A Python replica is not the shipped binary: it can agree with it on four pieces and still differ in a corner
nobody exercised. It says why growth produces what it produces and which figure moves the result; it does not
say whether a tuned figure is the right repair, and it says nothing about merging, the 3 mm window, or
reassembly.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

**Piece 2 is not stuck at a step: the growth splits its 1 031 points into 661 pieces averaging 1.6 points, and
the biggest is 36 — the floor of 50 is missed by a factor of 1.4, not by one hop. Every refusal that matters is
the normal-angle test (4 703 rejections against 0 curvature rejections), and the paper's own 4° buys 41 points,
not 50.**

The arm-B grid row for each piece, as the replica printed it (θ 3.4, κ 1.0, n_b 10, floor 50):

| piece | points in | regions grown | regions per point | largest | largest share of the cloud | largest depth | angle rejections | angle rejections per point | regions ≥ 50 |
|---|---|---|---|---|---|---|---|---|---|
| Juglet 2 | 1 031 | 661 | 0.64 | **36** | 3.5 % | 8 | 4 703 | 4.56 | **0** |
| Juglet 3 | 1 467 | 825 | 0.56 | 169 | 11.5 % | 16 | 6 189 | 4.22 | 2 |
| Juglet 5 | 3 021 | 1 467 | 0.49 | 679 | 22.5 % | 56 | 11 969 | 3.96 | 1 |
| Juglet 7 | 4 254 | 1 951 | 0.46 | 326 | 7.7 % | 24 | 16 823 | 3.95 | 5 |
| Pot A 07 | 8 598 | 1 276 | 0.15 | 3 093 | 36.0 % | 37 | 11 508 | 1.34 | 8 |

### What the growth actually does

It claims **every** point — the 661 regions of piece 2 sum to exactly 1 031, and `growth_floor_independent=True`
on every piece in the calibration log. A region that ends under the floor is dropped, but its points were
already marked claimed when they were admitted (`mesh_processing_headless.cpp` `growPaper234`: `pclaimed[sd] = 1`
at the seed and `pclaimed[cand] = 1` on each admission; the floor test `if (preg.size() >= minClusterSize)` sits
after the walk). So a seed that turns out to be a poor start burns its patch for the rest of the pass: there is
no second attempt and no unclaimed point left to re-seed. That is why the cloud comes out partitioned into
thousands of crumbs rather than split into a few regions.

Fragmentation is not a Juglet property. Pot A 07 fragments too — 1 276 pieces for 8 598 points, hundreds of them
of one or two points. What separates the vessels is the **largest** piece: Pot A has one of 3 093 to build on, and
the Juglet's best sherd reaches 679.

### The curvature gate can never fire

The stored curvature is PCA surface variation, λ₀/(λ₀+λ₁+λ₂), which cannot exceed 1/3. The paper's τ_κ = 1 sits
above that ceiling, so `if (pnormals->points[cand].curvature >= kappaThresh) continue;` rejected **nothing** in
any of the 36 cells (`fail_curv = 0` throughout, piece 2's maximum curvature 0.178). The angle test is the only
gate that ever decides anything, and on this material it decides everything.

### The paper's figure does not rescue piece 2, and it costs elsewhere

Moving 3.4° → 4.0° (the paper's own τ_θ, `C:/PR/papers/text/sfspp-2502.13986v1.md:151`) takes piece 2's largest
region from 36 to 41 — still under the floor — while thinning the surviving regions on piece 7 from 5 to 3 and on
Pot A from 8 to 6. So the figure the paper prints is neither enough for the Juglet nor free for the pot that
works. This is the direct answer to "check against the paper and tune the figure": 4° is not the number for this
material, and the reason it is not is measurable — the Juglet's neighbours disagree about the surface normal
4.7 times per point where Pot A's disagree 1.3 times.

### Two corrections to what I said earlier

1. **My ticket-25 reading said the growth "leaves 78-82 % of each sherd unclaimed".** That was the fraction of
   points in *surviving* regions. The growth claims every point; it is the floor, not the walk, that discards.
   The 78-82 % figure stands as "the share of the sherd that ends up on no surviving region", and must not be
   restated as "the growth never reached those points".
2. **The E column of the grid is not a reproduction of the pipeline's chain-off arm.** `SFS_PAPER_CHAIN=0` takes
   the `else` branch at `mesh_processing_headless.cpp:3443-3455` and runs `pcl::RegionGrowing`, not
   `growPaper234`; the card is on `if (paperChain)` at `:3435`. The replica's E cells are its own growth on the
   native cloud, which is a different experiment from the E dumps of ticket 25. Nothing downstream should read
   the E column as "what the pipeline did at native density".

### Is this why the pot works and the vessel does not?

Partly, and this is the honest weight. The three differences that move in the same direction are: the angle
rejection rate (4.7 vs 1.3 per point), the size of the largest region (3.5-22 % of the sherd vs 36 %), and the
fact that the paper's constant was fixed for a density we do not have. But **Pot A would still work if it were
smaller**, because it only needs one region of 50 out of 8 598 points — 0.6 % of the cloud — while piece 2 needs
4.8 % of its cloud in one piece, and its best is 3.5 %. The failure is a race between the normals and the size,
and this ticket measures the first half of that race and not the second.

### What this changes

The next measurement is not a repair. It is the **distribution of neighbour-pair normal angles** on each piece
(and on Pot A as the control): if the Juglet's core is tight with a heavy tail, a θ between 4° and 8° exists that
would let the growth cross between crumbs without fusing Pot A's walls; if the whole distribution is shifted, no
single θ is right for both vessels and the normals must be repaired before any figure means anything. That is one
cheap replica job and it turns "tune the figure" from a guess into a number.

What must **not** be done on this evidence: lowering or removing the floor. Piece 2 would then produce its
36-point patch, and ticket 23 already measured what a 21-32 point single surface is worth — 28-42 % of the cloud,
a corner patch, not a wall.

### verified: the command or file:line behind each load-bearing claim

- `ssh spartan; grep -h "[CAL]" .../20261027-1539_5227f8f_t28-replica-grid/logs/calibration.log` → piece 3
  `sizes_before` starts `[169, 99, 17, 10, …]`, `surv_ge_50=[169,99]` **MATCH**; piece 2 `[36, 15, 12, 12, 11,
  9, 9, 8, 7, 7, 7, 6, 6, 6, 5, 5, 5, 5, 4×21, 3×33, 2×88, 1×501]`, `surv_ge_50=[]`, `growth_floor_independent=True`.
- `awk` over `out/cells/cells28.tsv` → the five arm-B θ3.4 rows in the table above (npts, regions, largest, depth,
  failA); `fail_curv` is 0 in all 36 rows.
- `git diff --stat main...HEAD` on the branch → 8 files, 894 insertions; `mesh_processing_headless.cpp` is not
  among them, so the pipeline is untouched.
- `sed -n '2940,2995p' mesh_processing_headless.cpp` → seeds sorted by ascending curvature, `pclaimed[sd] = 1`
  at the seed, `pclaimed[cand] = 1` on admission, angle test against the current front point, floor test after
  the walk.
- `sed -n '3425,3460p' mesh_processing_headless.cpp` → `if (paperChain) { growPaper234 … } else if (planeRule) …
  else { pcl::RegionGrowing … }` — the chain-off path is PCL's region growing.
- `python3 -c` on `…/20261027-1537_5227f8f_t28-pota07-dump/out/dump/Pot_A_Piece_07/r2_clusters_premerge.json`
  → `clusters: [3093, 2850, 203, 170, 144, 120, 73, 71]`, `paper_chain: True`, `npts: 8598`; the replica's
  Pot A `sizes_before` reads `[3093, 2850, 203, 170, **134**, 120, 73, 71, …]` — seven of eight identical, one
  region ten points short, cause not established.
- `grep t28 …/runs/index.tsv` → both rows six fields, `verdict` and `human_note` empty.
- `cat out/corpus_before.txt | md5sum` vs after → identical, 1 803 rows; `/opt/sfs-pristine` recorded ABSENT.

### What this does not settle

The replica is not the shipped binary: it agrees with it exactly on three pieces and to one region of ten points
on a fourth, which is strong, but a corner nobody exercised could still differ. Nothing here was measured on
merging, the 3 mm admission window, or reassembly. And it says nothing about the other five sherds — only pieces
2, 3, 5 and 7 were replicated.
