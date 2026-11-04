# 306: A complete axis candidate set — stop truncating, union the seeds, and settle what made the released axes

**What to deliver:** axis extraction that stops losing real candidate axes to two bookkeeping choices —
cutting the two surfaces to equal length, and keeping only one seed's ten-item shortlist — and Pot A
seating **8/8 + 15/15 with our axes only, at every seed, with no best-of-N**. Plus the one measurement
the last three tickets kept bumping into: which of the authors' two surface readers made the released
axes we compare against.

**Answers:** E1

**Blocked by:** none. 304 (under-5,000 rule, default ON, 646a387) and 305 (sweep, landed) are on main.

**Status:** ready-for-agent

**Worker:** sfs306

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the assembler SIF, the t66 lane recipe and the corpus; MATLAB
only if Stage A's provenance probe needs it.

## Why this ticket exists (measured; do not re-derive)

- **Pot A Piece 08, truncation on vs off.** The sherd is two surfaces: 1,576 and 1,761 points.
  `sfs_axes/read_surfaces(truncate=True)` (the shipped default) cuts the longer one to 1,576, so the
  search sees 3,152 points; with truncation off it sees the whole 3,337. Run
  20261105-0455_9c5eec2_t305-axes-stage0c, out/notrunc: at **truncation off, step=1, seed 1 only**, the
  good axis appears (line 4; 0.19 deg from the stationary point at 5.2280 deg from the authors' released
  line 1). Seeds 0 and 2 do not propose it (nearest 38.28 and 33.56 deg). With truncation on it is absent
  at every seed tried.
- **The assembler agrees.** Run 20261105-0420_9c5eec2_t305-e2e-a-s1: the truncation-off arm seats
  **7/8 + 12/15 at seed 1** and **6/8 + 10/15 at seeds 0 and 2**; every truncation-on arm is 6/8 + 10/15.
  So the axis and the seating move together — this is not a scoring artefact.
- **Truncation is the authors' code, and they have two readers.** `AxisExtraction/read_surfaces.m:34-37`
  equalises the two walls (their comment: 'Ensure both surfaces have the same number of points for
  potsac'); their driver `AxisExtraction/preprocess_new_pots.m:21` -> `extract_axis.m:6` uses it.
  `AxisExtraction/read_surfaces_nurbs.m` reads the same files and does **not** cut, and
  `extract_axis_nurbs.m:11` is its caller. POTA-05 (182d5e8) recorded, but never proved, that the
  released assembly axes come from the NURBS path — i.e. from the untruncated cloud. Stage A settles it.
- **Pot A Piece 07 is the other half.** Released file has 3 lines; ours has 1 under every setting tried
  (truncation on 5.91 deg, off 6.31 deg, from released line 0). At step=10 the 302 run wrote 2 lines on
  4 of 5 seeds — so a second candidate does exist at some strides and is being lost.
- **The shortlist can eat real candidates.** `sfs_axes/potsac.py:118-140` dedups at 10 deg
  (DEDUP_COS = 0.9848) and then prunes with `cost < cost[0] * 1.1`. The paper
  (papers/text/sfspp-2502.13986v1.md:175) describes the 10-deg duplicate removal and says nothing about
  a cost-ratio prune or about truncating the surfaces; both are implementation choices of the authors'
  code, not the method.
- **More lines is not automatically better.** The assembler tests **every** line pair as a hypothesis
  (`class/feature_matching.cpp:1461-1475` loops axis_x/axis_y; the pair's angle is used at :1665-1668 and
  rejected above 0.436 rad at :1715), so adding spurious lines adds wrong hypotheses. 303 found exactly
  that on Piece 08. Any completeness fix must be measured, not assumed.

## Stage A — the candidate landscape (no E2E; hours)

Dump what the search actually proposes, before dedup and before the cost prune, for Pot A pieces **07**
and **08** (piece **01** as a control), at truncation on and off, seeds 0 and 1: the 1,000 Pottmann draws,
each refined candidate's direction, its all-points cost, and its cluster at 10 deg.

A1. Per cluster: how many of the 1,000 draws landed in it, its mean cost, whether the 10-deg dedup keeps
    it, whether `cost < cost[0] * 1.1` keeps it, and (scoring only, never as input) its angle to the
    nearest released line.
A2. Answer in one line each: (i) does the search ever **propose** Piece 07's second axis, or does it never
    exist in the candidate pool; (ii) how many distinct clusters does Piece 08 have, and which are lost
    to truncation and which to the cost prune.
A3. **Provenance probe.** For Piece 08, on both clouds, evaluate the cost at the authors' released line 1
    and probe whether it is a local minimum (perturb ~5 deg in 8 directions, re-refine, report where each
    returns). If it is a minimum of the untruncated cost and not of the truncated one, the release came
    from the untruncated path — say so, with the numbers.

## Stage B — the fix (blind; only the piece's own surfaces may inform the choice)

B1. Default to **not truncating** the surfaces (the NURBS reader's behaviour); keep the truncating path
    reproducible behind the existing switch so 302/304's MATLAB parity stays available.
B2. Replace the single-seed shortlist with a **deterministic union**: run the search at S seeds (state S;
    default 10), union every surviving candidate, 10-deg dedup, and **drop the `cost*1.1` prune** or
    replace it with a margin that the paper supports. Order by cost.
B3. The written axis file must contain Piece 07's missing line and Piece 08's good line **without the
    code being told which they are**. No released axis, no ground truth, no piece-id special case.
B4. Report seconds per piece at the chosen S and the projected cost for the 163-piece corpus.

## Stage C — verification

C1. **Pot A seats 8/8 + 15/15 with our axes only, at 3 of 3 seeds**, no best-of-N. If 3/3 is not reached,
    the ticket has failed and that is the result.
C2. **No collateral damage**: re-run the 305 grid (OO and MM arms, authors' axes as control in the same
    job) on every scorable pot, 2 repeats (3 on the small pots). Report per pot as best-of-N with N, and
    name any pot that got worse.
C3. **Corpus**: 163 pieces to a new out/ path, corpus input md5 unchanged, and the median / percent-within-5
    table split by the released-axis tiers (gt_close / gt_off / no_gt).
C4. **Juglet**: the F20 arm with our axes, reported against t67/t68/t302's 0/9 with candidate counts and
    the gauge median.
C5. Renders before/after for the Pot A assembly, and for any pot whose count changes, at a view that
    resolves the join: artifacts/pota306/.

## Acceptance

- [ ] A1 cluster table for Pieces 07/08/01, truncation on and off, seeds 0 and 1, dumped before dedup.
- [ ] A2 both questions answered in one line each, with the counts behind them.
- [ ] A3 provenance probe reported; the reader that made the released axes named, or explicitly left open.
- [ ] B1 truncation default flipped, truncating path still reachable and still MATLAB-faithful.
- [ ] B2 deterministic seeded union replacing the single-seed shortlist; S stated; the cost-ratio prune
      removed or defended against the paper text.
- [ ] B3 Piece 07's second line and Piece 08's good line present, chosen blind.
- [ ] C1 Pot A 8/8 + 15/15 at 3/3 seeds, our axes only.
- [ ] C2 grid re-run: no pot worse than the 305 baseline, or the regression named.
- [ ] C3 corpus table + md5 proof. C4 Juglet. C5 renders.
- [ ] Every sbatch's final sacct State/ExitCode recorded, and one index.tsv row per run with verdict and
      human_note left empty.

## Rules

- Open the ticket with `scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/306-*.md`
  (Status must be ready-for-agent on origin when you run it).
- Spartan over `/c/Windows/System32/OpenSSH/ssh.exe spartan` (git-bash's own ssh cannot authenticate).
- Runs live at /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/ with run.json and an
  index.tsv row; poll with `sacct -j <id> --format=State,ExitCode` and record the final value.
- Build on the t305 E2E recipe (.scratch/pota-repro/305-stage/e2e305.sbatch) and the t305 axis recipe
  (.scratch/pota-repro/305-stage/axes305.sbatch); do not invent a new staging path.
- The corpus is read-only: no file under Dataset/SfS_pp may change (md5 before and after).
- Released axes and ground truth may be read to **score and diagnose**, never inside the shipped
  selection rule.
- Edit only the Comments section of this ticket; commit nothing. The lead lands it.
- Renders before/after before any geometry claim is reported.
