# 28: step 1 replicated in Python — why does piece 2 grow nothing, and which figure is wrong

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** ready-for-agent

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
