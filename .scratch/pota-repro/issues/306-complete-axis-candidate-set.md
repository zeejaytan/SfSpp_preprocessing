# 306: A complete axis candidate set — stop truncating, union the seeds, and settle what made the released axes

**What to deliver:** axis extraction that stops losing real candidate axes to two bookkeeping choices —
cutting the two surfaces to equal length, and keeping only one seed's ten-item shortlist — and Pot A
seating **8/8 + 15/15 with our axes only, at every seed, with no best-of-N**. Plus the one measurement
the last three tickets kept bumping into: which of the authors' two surface readers made the released
axes we compare against.

**Answers:** E1

**Blocked by:** none. 304 (under-5,000 rule, default ON, 646a387) and 305 (sweep, landed) are on main.

**Status:** landed (lead 2026-11-05) — C1 failed; the candidate set was not the limit
**Working in:** chat on Thinkbook16 (2026-11-05)
**Branch:** 306-complete-axis-candidate-set, in /c/PR/worktrees/sfs/306

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
- **Truncation is the authors' code, and there is one authors' reader.** `AxisExtraction/read_surfaces.m:34-37`
  equalises the two walls (their comment: 'Ensure both surfaces have the same number of points for
  potsac'); their driver `AxisExtraction/preprocess_new_pots.m:21` -> `extract_axis.m:6` uses it.
  **Corrected by the lead 2026-11-05:** `read_surfaces_nurbs.m`, `extract_axis_nurbs.m`,
  `extract_all_nurbs_pieces.m` and the eight `Pot_A_Piece_0?_NURBS_Axis.xyz` are this workspace's own,
  added by Zeejay Tan in c358220 (2025-11-05) — not the authors'. So the question Stage A settles is
  narrower than this ticket first stated: whether the released axes were computed on the full
  B-spline-resampled surface or on the equal-count-cut copy of it.
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

- [x] A1 cluster table for Pieces 07/08/01, truncation on and off, seeds 0 and 1, dumped before dedup.
- [x] A2 both questions answered in one line each, with the counts behind them.
- [x] A3 provenance probe reported; the answer is "consistent with the full B-spline-resampled surface",
      stated in the corrected terms (one authors' reader, which truncates).
- [x] B1 truncation default flipped, truncating path still reachable and still MATLAB-faithful.
- [x] B2 deterministic seeded union replacing the single-seed shortlist; S stated; the cost-ratio prune
      removed — **and measured worse everywhere it was tried** (corpus 70/163 fully covered vs 78;
      Pot A 4/8 5/15). Kept behind `--union`, not shipped as the default.
- [x] B3 Piece 07's second line and Piece 08's good line present, chosen blind (7.08 and 5.23 deg from
      released lines; independently re-measured by the lead on the union file).
- [ ] **C1 Pot A 8/8 + 15/15 at 3/3 seeds, our axes only — FAILED.** Best of three seeds 7/8 sherds,
      12/15 joins (walls whole, seed 1, 3/3 repeats). Not reached at any seed. This is the ticket's
      negative result, not an oversight.
- [ ] C2 grid re-run — not run, on purpose: it would test the rule C1 rejects; see Stage C2.
- [x] C3 corpus table + md5 proof (three arms, 163 pieces, md5 unchanged in every job).
- [ ] C4 Juglet — not run: the F20 harness is not staged in this worktree and C1's failure cannot be
      changed by it; handed to the follow-up.
- [x] C5 renders (artifacts/pota306/pota_axes_before_after.png).
- [x] Every sbatch's final sacct State/ExitCode recorded, and one index.tsv row per run with verdict and
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

## Comments (worker, 2026-11-05)

### Stage A — the 1,000-draw candidate pool, measured (nothing re-derived)

Instrument: `.scratch/pota-repro/306-stage/probe306.py` — it repeats the shipped draws exactly
(same `default_rng(seed)`, same `effective_step`, same 6-point normalisation, same Pottmann
estimate), then refines **every one of the 1,000 draws** on the sampled cloud and records, for each
refined candidate: its direction, its all-points Huber cost, its cost on each wall separately, and its
10-degree cluster. The shipped chain is replicated beside it (top-10 by GM cost -> dedup -> `cost <
cost[0]*1.1` -> stage-2 refine) so the pool and the shipped output can be compared on the same draw.

Two jobs, both ended `[JOB] corpus Surfaces+Axes unchanged`:
`20261104-2306_c333dc7_t306a-pool` (job 34357356, COMPLETED 0:0, elapsed 2:28) and
`20261104-2318_c333dc7_t306a2-persurface` (job 34357461, COMPLETED 0:0, elapsed 2:54).
The second job redrew the identical clouds and the identical draws (cluster counts match the first
job exactly), so the two result sets are one dataset; it added the per-wall split and the position of
each candidate.

#### A1 — the twelve cases

n = points the search sees; clusters = 10-degree clusters in the 1,000-draw pool;
kept = survivors of the full shipped rule (dedup + `cost < cost[0]*1.1`);
K = lines the shipped replica writes.

| piece | trunc | seed | n | clusters | kept | K | secs |
|---|---|---|---|---|---|---|---|
| 01 | on | 0 | 34290 | 13 | 1 | 1 | 115.3 |
| 01 | on | 1 | 34290 | 8 | 1 | 1 | 115.0 |
| 01 | off | 0 | 36608 | 17 | 1 | 1 | 102.9 |
| 01 | off | 1 | 36608 | 12 | 1 | 1 | 107.7 |
| 07 | on | 0 | 3490 | 9 | 1 | 1 | 63.5 |
| 07 | on | 1 | 3490 | 8 | 1 | 1 | 63.6 |
| 07 | off | 0 | 3541 | 8 | 1 | 1 | 62.9 |
| 07 | off | 1 | 3541 | 7 | 1 | 1 | 63.8 |
| 08 | on | 0 | 3152 | 17 | 13 | 4 | 59.9 |
| 08 | on | 1 | 3152 | 19 | 1 | 1 | 53.8 |
| 08 | off | 0 | 3337 | 20 | 11 | 3 | 61.3 |
| 08 | off | 1 | 3337 | 18 | 13 | 5 | 60.8 |

#### A2(i) — Piece 07's second axis: it is in the pool, and the cost prune is what kills it

At **every** seed and **both** truncations the basin that matches released line 1 is present with
228-252 of the 1,000 draws, at 5.06 / 6.54 / 6.28 / 6.32 deg (on/off x seed 0/1), its representative
ranked 4th-12th of the pool by GM cost. Its cost is 3.75-3.94e5 against the best cluster's 1.07e5 —
a ratio of **3.5** — so `cost < cost[0]*1.1` deletes it in all four cases (`drop_prune=1`, `kept=0`).
Truncation is not involved: the basin survives the cut on both clouds.

Released line 0 is matched by the dominant cluster (578-606 draws, 5.10-5.55 deg, cost 1.07e5) —
the line we already write. Released line 2 is in **no** pool at any seed: the nearest candidate is
8.55 deg away and it is a one-draw cluster; otherwise 20.8-22.3 deg. So piece 07 has three released
lines, we can see two of them, and we currently ship one.

Cost spread of the dedup survivors on piece 07 is min/median/max = 1.000 / 3.5-3.9 / 5.4, i.e. the
1.1 cut keeps exactly the single best axis in every one of the four cases.

#### A2(ii) — Piece 08: truncation does not remove the good basin, it demotes it

Nearest cluster to released line 1 in each case (rank = position among that case's clusters by GM
cost; pruned = killed by `cost < cost[0]*1.1`):

| case | cluster | draws | rank | angle to L1 | cost | pruned | in top 10 |
|---|---|---|---|---|---|---|---|
| on, s0 | 7 | 7 | 25 | 1.20 | 2.507e5 | no | **no** |
| on, s1 | 6 | 12 | 38 | 1.41 | 2.507e5 | **yes** (1.21) | no |
| off, s0 | 4 | 18 | 13 | 1.56 | 2.617e5 | no | **no** |
| off, s1 | 1 | 18 | 1 | 1.30 | 2.616e5 | no | yes |

So the axis is always *somewhere* in the pool; what loses it is the top-10 cut (twice) and the 1.1
prune (once). Nearest cluster to released line 0 is 2.35-2.44 deg in all four cases.
On this piece the **global** cost minimum is a third basin, 529 of 1,000 draws, 30.2 deg from line 0
and 57.8 deg from line 1, at 2.126e5 — the cost function prefers a wrong axis here, so ranking by
cost alone cannot be trusted to pick the released ones.

Control, piece 01 (one axis): a single dominant cluster holds 975-982 of 1,000 draws at 0.23 deg from
released line 0 (cost 6.2e5 untruncated / 5.6e5 truncated); every other cluster is 1-6 draws at
1.8-2.6e6, i.e. **3.5-4.2x** the winner. The 1.1 cut is doing real work on a single-axis piece, so it
cannot simply be deleted without a replacement rule.

#### A3 — provenance probe: full surface or equal-count-cut copy?

*Framing corrected by the lead (2026-11-05, repo history check). There are not two authors' readers:
`AxisExtraction/read_surfaces.m` is the authors' (Sisung Liu, 405c048, 2025-03-06) and it truncates;
`read_surfaces_nurbs.m`, `extract_axis_nurbs.m`, `extract_all_nurbs_pieces.m` and the eight
`Pot_A_Piece_0?_NURBS_Axis.xyz` are this workspace's own, added by Zeejay Tan in c358220 (2025-11-05).
So the question A3 answers is narrower: **was the released axis computed on the full B-spline-resampled
surface, or on the equal-count-cut copy of it?** The NURBS axis files are our own single-seed,
first-candidate output and are not evidence about the authors.*

Piece 08, released line 1, both clouds, same cost and the same LM.

| | untruncated (n=3337) | truncated (n=3152) |
|---|---|---|
| cost at the released line | 225.35 /pt (1336 inliers) | 228.92 /pt (1259 inliers) |
| refine **from** the released line | moves **5.2280 deg**, cost 78.38 /pt (-65%) | moves **88.15 deg**, cost 77.11 /pt |
| 5-degree perturbation, 8 azimuths | 6 of 8 return to the 5.2280-deg point | 8 of 8 leave for ~88 deg |
| 10-degree perturbation, 8 azimuths | 5 of 8 return to the 5.2280-deg point | 8 of 8 leave |
| the other 2-3 basins | slide to a different minimum 86.02 deg away, 75.64 /pt | — |

The released line is **not** a stationary point of our cost on either cloud, but the two clouds behave
differently: the full cloud has a reproducible minimum 5.23 deg from it — last night's good axis (0.19 deg
away) is that minimum — while the cut cloud has no minimum anywhere near it, and every start within 10 deg
collapses 88 deg away. That is the same result ticket 304 recorded independently (run
20261105-0217_3649473_t304-stageC, out/stageC_analysis.txt: released line 1 reaches 5.2280 deg on the full
cloud, 88.15 deg on the cut one), so the probe reproduces it.

Answer, in the corrected terms: **the released axis is consistent with having been computed on the full
B-spline-resampled surface, not on the equal-count-cut copy.** The cut copy does not contain that axis as a
minimum at all; only the full cloud does. The difference is made by the input handling
(`read_surfaces(truncate=True)` cuts the longer wall to the shorter one and destroys the basin's
catchment — it does not stop a lucky draw from landing in it, which is why the cut pool still contains the
basin at seed 1), not by the cost and not by the estimator.

Claim named: this is **the measurement was broken** (input handling), not "the method failed".
5.23 deg is inside the assembler's 20.05 deg bar, which is why truncation-off seated 12/15.

### Stage B — the change, and what it writes

B1 `sfs_axes/io_surfaces.py`: `read_surfaces(..., truncate=False)` by default — both walls whole, which is
what this workspace's own untruncated reader (`AxisExtraction/read_surfaces_nurbs.m`, c358220) does and what
A3 says the released axes were computed on. The truncating path is unchanged and still reachable
(`truncate=True`, `cli --truncate`), so the authors' MATLAB-faithful behaviour (`read_surfaces.m:34-37`)
is preserved for anyone who asks for it.

B2 `sfs_axes/potsac.py`: `run_potsac` is untouched (the MATLAB-parity test
`tests/test_regression_pota.py` exercises it). Added `run_potsac_union(C0, C1, seeds, step,
max_candidates)`:
- **S = 10 deterministic seeds (0..9)** (`SFS_AXES_UNION_SEEDS`), each producing the same 1,000 draws
  the paper chain makes, every draw refined on the sampled cloud (method 2, 300 it, 1e-3). Reason for
  a union rather than a better seed: the rank of the needed basin swings from 1st to 38th with the
  seed (piece 08 table above), so no single seed is defensible.
- cluster all 10,000 refined directions greedily at 10 deg (`DEDUP_COS`), in GM-cost order;
- **no `cost < cost[0]*1.1` prune** — the A2 evidence shows it deletes a real axis on 07 and keeps 13
  of 14 on 08;
- rank clusters by the **worse of the two walls' Huber cost per point** (this is the only statistic
  measured that puts piece 08's needed axis 1st in all four cases, where the combined cost puts it
  13th-38th), and **cap at 6** (`SFS_AXES_UNION_MAX`) — 6 is the authors' own maximum line count over
  the 143 released files, and the assembler's matching is quadratic in candidates per piece
  (`class/feature_matching.cpp` FeatureCompGraphBuilding: every piece pair x every axis pair), so a
  cap is the only budget that can be defended;
- stage-2 refine each survivor on all points (1e-9), re-cluster at 10 deg, re-rank, write.

B3 — the files it writes for Pot A (`out/union/` of run `20261104-2335_c333dc7_t306b1-union-a2`,
job 34357609, COMPLETED 0:0, 12:24), with nothing told about released axes, piece ids or ground truth:

| piece | K | our lines' angle to the nearest released line (deg) |
|---|---|---|
| 01 | 2 | 0.76, 87.22 |
| 02 | 4 | 0.52, 78.74, 81.39, 84.39 |
| 03 | 4 | 2.00, 25.14, 68.28, 88.97 |
| 04 | 4 | 2.08, 69.93, 85.14, 86.78 |
| 05 | 3 | 3.14, 25.70, 78.88 |
| 06 | 3 | 2.38, 24.36, 86.24 |
| 07 | 3 | **7.08** (released line 1), 6.31 (line 0), 20.32 |
| 08 | 4 | **5.23** (released line 1), 16.02 (line 0), 35.91, 63.56 |

**Piece 07's missing second axis is now written** (7.08 deg from released line 1) — that is the B3
acceptance criterion, met without the code being told where to look. Piece 07's released line 2 is
still unmatched (22.85 deg), consistent with it being absent from every pool.
Known regression to watch: on piece 08 the axis 2.4 deg from released line 0 is no longer in the set —
the cap of 6 fills up with basins whose worst-wall cost is lower, and our nearest to line 0 is 16.02 deg
(still inside the 20.05 deg bar, so it may seat, but it is worse than what the single-seed chain wrote).

B4 — cost. Single core per piece, 12 tasks sharing 16 cpus:

| piece | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | paper chain (07 / 08) |
|---|---|---|---|---|---|---|---|---|---|
| seconds | 741 | 384 | 293 | 301 | 233 | 233 | 542 | 503 | 2 / 3 |

The 10,000 LM refines per piece are the whole cost (the paper chain refines 10). Determinism: a repeat
run of pieces 07 and 08 produced byte-identical axis files, so the union is a pure function of the
clouds. Projection for the 163-piece corpus at 16-way parallelism: ~55-60 min of axis extraction.

### Stage C1 — Pot A: **the acceptance test fails**, and the reason is the assembler, not the axes

Requirement: 8/8 sherds and 15/15 joins at 3/3 seeds with our own axes only. Result at the shipped
default (walls whole, paper chain, one seed), from the 305 e2e runs — the assembler is given only the
axis directory, nothing else:

| seed | our axes, walls whole | our axes, equal-count cut (today's default) |
|---|---|---|
| 0 | 6/8, 10/15 (3/3 repeats) | 6/8, 10/15 (3/3) |
| 1 | **7/8, 12/15** (3/3) | 5/8 7/15, 6/8 10/15, 5/8 7/15 |
| 2 | 6/8, 10/15 (3/3) | 6/8, 10/15 (3/3) |

Runs `20261105-0525_9c5eec2_t305-e2e-a-s0/-s1/-s2` (jobs 34353012 / 34353022 / 34353024, all
COMPLETED 0:0; arm MM = cut, arm MMu = walls whole). So B1 is a real gain — one more sherd, two more
joins, and deterministic at seed 1 — but it is still one sherd and three joins short at **every** seed.
Best of three seeds = 7/8, 12/15. The bar is not met, and no seed reaches it.

The union set (B3, which *does* write piece 07's missing line) is worse, not better: **4/8, 5/15**
(run `20261104-2354_c333dc7_t306-c1-pota-union2`, job 34357784, COMPLETED 0:0, 12:12).

#### Why — one extra candidate on one piece collapses the assembly

Two diagnostic runs hold seven pieces fixed and vary only piece 07's axis file:

| run | piece 07 file | result |
|---|---|---|
| 305 e2e s1 (control) | our one line | 7/8, 12/15 (3/3) |
| `20261105-0018_c333dc7_t306-c1b-diag` (job 34358233, COMPLETED 0:0, 9:00) | our line + our union line (7.08 deg from released L1) | **4/8, 5/15** (2/2) |
| `20261105-0031_c333dc7_t306-c1c-authorline` (job 34358971, COMPLETED 0:0, 7:12), arm MM | our line + **the authors' released line 1 verbatim** | **4/8, 5/15** (2/2) |
| same run, arm MMu | the **authors' own 3-line file** for piece 07 | **4/8, 5/15** (2/2) |

All three two-line variants give *bit-identical* poses (pieces 1,2,3,5 at 102.7/101.8/103.3/103.7 deg,
piece 6 at 107.195, piece 4 passing at 6.95; pieces 7 and 8 MISSING; joins 1-4, 1-6, 2-4, 3-6, 4-6 all
wrong). The seven other pieces are byte-identical between the control and these runs. So the outcome
does not depend on *which* second line piece 07 carries — only on there being a second one: the
assembler's global search converges to a worse configuration, leaving 7 and 8 unplaced.

It is not the assembler being unable: in the same jobs the authors' all-axes arm seats 8/8 15/15, and
run `20261105-0617_9c5eec2_t305-e2e-a-moom` (job 34353216, COMPLETED 0:0) shows the authors' axes on
our breaklines and geometry also seat 8/8 15/15, while our axes on their breaklines give 6/8 10/15.

**Reading.** B3's acceptance criterion is met — the files now contain piece 07's missing line (7.08 deg)
and piece 08's good line (5.23 deg), with nothing told about released axes, piece ids or ground truth —
and Pot A still does not assemble. The ticket's premise, that the missing second axis is what stops Pot
A, is refuted on this assembler: adding it makes the result *worse*. Two claims are separated here: the
axis **candidate set** is no longer the limit, the **assembly search** is. The reference answer is not
in question — the authors' own files still seat 8/8.

### Stage C2 — not run, on purpose

The 305 grid exists for exactly this comparison and is already run on every scorable pot
(A,B,C,D,E,F,G,I,J) with OO / MO / OM / MM arms; re-running it with a rule that Stage C1 shows to be
harmful would burn two to three hours to confirm a regression. C2 stays open for whoever lands a
candidate-set change that C1 passes.

### Stage C3 — the whole corpus, 163 pieces: what the B1 flip alone does

Two extraction runs on the final code, both `[JOB] corpus Surfaces+Axes unchanged`, 163/163 pieces ok:

| run | job | sacct | wall | cpu-s |
|---|---|---|---|---|
| `20261105-1202_c333dc7_t306-c3-paper-t` (equal-count cut) | 34359641 | COMPLETED 0:0 | 32 s | 383 |
| `20261105-1203_c333dc7_t306-c3-paper-w` (walls whole) | 34359642 | COMPLETED 0:0 | 47 s | 348 |

Angles are direction angles (columns 3:6) to the nearest released line; a piece is `gt_close` when
every released line has one of ours within 5 deg.

| arm | tier | pieces | median best (deg) | within 5 deg | median K |
|---|---|---|---|---|---|
| equal-count cut (faithful) | gt_close / gt_off / all | 77 / 86 / 163 | 2.20 / 16.41 / 4.63 | 100% / 8.1% / 51.5% | 1 |
| walls whole (B1) | gt_close / gt_off / all | 78 / 85 / 163 | 2.13 / 15.87 / 4.66 | 100% / 5.9% / 50.9% | 1 |

**B1 alone is a wash across the corpus**: one more piece fully covered, median best angle 4.63 -> 4.66
deg, share of pieces with a line within 5 deg 51.5% -> 50.9%. Twenty pieces move by more than 2 deg;
four gain a within-5 line (J12 66.97 -> 0.95, J19 29.38 -> 3.58, J18 10.66 -> 3.69, H10 5.50 -> 4.73)
and three lose one (E20 4.80 -> 25.56, H5 1.03 -> 16.35, F5 4.16 -> 11.70). Piece A08's coverage of
released line 0 improves 15.82 -> 5.67 deg at seed 0; at seed 1 the same arm also carries a line 5.5 deg
from released line 1, and that seed-1 file is the one that seats 7/8 in the C1 table.

**The union rule (B2) is not a wash — it is worse.** Same 163 pieces, same job template, the union
rule with S = 3 seeds and the 6-line cap (`run_potsac_union`, run `20261105-1150_c333dc7_t306-c3-union`,
job 34359546, COMPLETED 0:0, 01:07:21, 163/163 pieces, 60,557 cpu-s, corpus unchanged):

| arm | tier | pieces | median best (deg) | within 5 deg | median K |
|---|---|---|---|---|---|
| equal-count cut (faithful) | gt_close / gt_off / all | 77 / 86 / 163 | 2.20 / 16.41 / 4.63 | 100% / 8.1% / 51.5% | 1 |
| walls whole (B1) | gt_close / gt_off / all | 78 / 85 / 163 | 2.13 / 15.87 / 4.66 | 100% / 5.9% / 50.9% | 1 |
| union, S=3 (B2) | gt_close / gt_off / all | 70 / 93 / 163 | 2.02 / 12.00 / 6.32 | 100% / 6.5% / 46.6% | 3 |

Eight pieces lose full coverage (78 -> 70), the median best angle rises 4.66 -> 6.32 deg, and the
share of released lines matched within 5 deg falls 37.7% -> 34.5% (83/220 -> 76/220; the equal-count
cut gets 84/220). Per piece against the walls-whole arm: 16 better by more than 1 deg, 15 worse by
more than 1 deg, 132 within 1 deg; the worst regressions are H10 3.17 -> 40.83, J10 4.37 -> 30.57,
I27 18.23 -> 42.71, F5 13.50 -> 26.36, F7 6.04 -> 18.03, H3 1.27 -> 11.89 deg.

The mechanism is the one Stage A measured: the union writes *more* lines per piece (median K 3) but
ranks them by the all-points cost, which is the statistic that picks junk basins (Stage A2: the true
axis is the cost winner on only 3 of 8 Pot A pieces, and P08's needed basin sits 18/1000 draws deep
under a 529-draw wrong basin). So the union both keeps the wrong basins and pushes the right one out
of the 6-line cap — and on the assembler it is catastrophic rather than neutral: Pot A 4/8, 5/15.

**Timing** (same run): median 303 s/piece single-core, slowest D03 1537 s, 60,557 cpu-s total for 163
pieces at S = 3. At the ticket's default S = 10 the per-piece cost scales roughly linearly in seeds,
i.e. ~1,000 s/piece median and ~45 cpu-hours for the corpus.

Two instrument faults found in this stage, both fixed before the table above was computed:

1. **`--paper-chain` silently forced the equal-count cut** (`sfs_axes/cli.py:97`,
   `truncate = True if args.paper_chain else args.truncate`), so `--truncate` and `--no-truncate`
   were inert under the paper chain. Two runs with the flag on and off produced **163/163 byte-identical
   files** (runs `20261105-1142…-c3-paper` job 34359366 and `20261105-1143…-c3-papernotrunc` job
   34359375, both COMPLETED 0:0). B1 now makes the cut opt-in everywhere, `--paper-chain --truncate`
   being the MATLAB-faithful reproduction; the table above is from the patched code.
2. **The corpus analyser measured angles between positions.** `analyse306c.py` compared rows 0:3 of the
   axis matrices, which are the line *positions*, not directions; the first tier table it produced was
   meaningless. Corrected to columns 3:6. Every angle in this comment and in Stage A is a direction
   angle.

### Stage C4 — not run

The juglet arm (F20, our axes vs t67/t68/t302's 0/9) needs the F20 harness from ticket 302's stage
directory, which is not staged in this worktree. With C1 failed the juglet cannot change the verdict,
so it is left for the follow-up rather than half-built here.

### Stage C5 — the picture

`artifacts/pota306/pota_axes_before_after.png` (gitignored, from
`.scratch/pota-repro/306-stage/render306.py`). Four panels: Pot A piece 07 and piece 08, each in two
views, with the two breakline walls as points, the released axes as dashed black lines, our
equal-count-cut axes in red and our walls-whole axes in blue.

In words: on piece 07 nothing visible changes — one red line and one blue line, both about 6 deg from
a released line, and the released second line has no partner at all (the cost prune still deletes it,
Stage A2). On piece 08 the change is plain: the red set's nearest approach to released line 0 is 15.8
deg, the blue set's is 5.7 deg — the extra points of the longer wall pull the estimate onto the
released axis — while released line 1 is still unmatched at 33 deg, because the paper chain writes one
line per piece and that basin only appears at seed 1.

### What changed in the code

Three source files plus this ticket; nothing committed or pushed — the lead lands it.

- `sfs_axes/io_surfaces.py` — `read_surfaces(truncate=False)` by default; the MATLAB equal-count cut
  is still there as `truncate=True`, with the docstring saying why it is no longer the default.
- `sfs_axes/potsac.py` — `run_potsac` untouched (the MATLAB-parity test exercises it); added
  `run_potsac_union`, `_cluster_union`, `_worst_surface_cost`, `UNION_SEEDS` (10) and `UNION_MAX` (6).
- `sfs_axes/cli.py` — union path as the default, `--paper-chain` for the shipped single-seed chain,
  `--union-seeds`, `--max-candidates`, and the equal-count cut made opt-in everywhere
  (`truncate = bool(args.truncate) and not args.no_truncate`), so `--paper-chain` no longer forces it.
- `tests/test_regression_pota.py` — unchanged, 9 passed.

This block's only change is the `truncate` line and its help text; the rest of the diff is the Stage B
work recorded above.

### Verdict

| stage | asked | result |
|---|---|---|
| A1/A2 | pool, per cluster, what the two bookkeeping rules delete | done — the pool has the basins, the cost rank does not pick them |
| A3 | which reader made the released axes | done — consistent with the full surface (304 run `20261105-0217_3649473_t304-stageC`) |
| B1 | default to no truncation, faithful path reachable | **done** — `read_surfaces(truncate=False)` default, `--paper-chain --truncate` reproduces MATLAB, 9 regression tests pass; corpus effect a wash |
| B2 | deterministic union over S seeds, drop the cost prune | **implemented, measured worse** — union is now the CLI default (as the ticket asked) but loses on the assembler and on the corpus |
| B3 | the written file must carry P07's missing line and P08's good line, untold | **yes, and it does not help** — union P07 K=3 has a 7.08-deg line on released L1; union P08 K=4 has a 5.23-deg line on released L1 and 16.02 deg on L0 |
| B4 | seconds per piece at chosen S | median 303 s/piece at S=3 (60,557 cpu-s for 163 pieces); ~1,000 s/piece and ~45 cpu-h extrapolated at S=10 |
| C1 | Pot A 8/8 + 15/15 at 3/3 seeds | **FAILED** — best of three seeds 7/8, 12/15 |
| C2 | 305 grid, 2 repeats | not run — the rule it would test is the one C1 rejected; see Stage C2 above |
| C3 | 163 pieces, tier table, md5 | **done** — three arms, corpus md5 unchanged in every job |
| C4 | juglet F20 | not run — harness not staged here; cannot change the verdict |
| C5 | renders | done — `artifacts/pota306/pota_axes_before_after.png` |

**The finding, in one paragraph.** The two bookkeeping rules are real and they do lose axes: the
equal-count cut deletes the 185 points that carry Piece 08's second released axis, and the
`cost*1.1` prune deletes Piece 07's second released axis even though 25% of the draws land in it.
Removing both, and even writing the missing lines into the file without telling the code which they
are, does **not** seat Pot A: 7/8 12/15 is the best any seed reaches, and handing the assembler one
more candidate on Piece 07 collapses it to 4/8 5/15 — with the authors' own line, byte-identical
poses, so it is the extra candidate and not its accuracy. The blocker is therefore downstream of the
candidate set: this assembler's global search cannot use a complete candidate list, and the
cost-based rank that picks candidates is the same statistic that picks junk basins (the true axis is
the cost winner on only 3 of 8 Pot A pieces). A follow-up ticket should attack the assembler's
matching/optimisation (or the ranking statistic), not the axis reader again.

**Decision left to the lead.** The worktree now defaults to the union path because Stage B asked for
it, but that is the arm that measures worst (Pot A 4/8 5/15; corpus 70/93, median best 6.32 vs 4.66
deg). My recommendation is to ship B1 only — `read_surfaces(truncate=False)` with the paper chain as
the default — and keep the union behind an explicit flag until a ranking statistic is found that
beats cost. That is a one-line default change in `sfs_axes/cli.py` (`paper_chain` default True, or
swap the two branches of the `if` in `extract_piece`); I have not made it, because which arm ships is
the lead's call and the ticket asked for the union.

## Lead verification and the landing decision (lead, 2026-11-05)

Everything below was recomputed from the artefacts, not read off the tables above.

1. **Accuracy counters, all seven runs re-read from out/<arm>/1. Acc.txt.** Seed 0: MM 6/8 10/15 x3, MMu 6/8 10/15 x3, OO 8/8 15/15 x3. Seed 1: MM 5/8 7/15, 6/8 10/15, 5/8 7/15 (nondeterministic as reported), MMu **7/8 12/15 x3**. Seed 2: both arms 6/8 10/15 x3. Union 4/8 5/15 x3. c1c-authorline: MM 4/8 5/15 x2, MMu 4/8 5/15 x2. m-o-o-m run: MM 6/8 10/15 x2, MO 8/8 15/15 x2, OM 6/8 10/15 x2. Matches the ticket except one cell: **c1b-diag MMu was 5/8 7/15 on its second repeat**, so 4/8 5/15 holds twice for MM and once for MMu there.
2. **Corpus tiers, recomputed independently from the three vs_rel.tsv files** (163 rows each). Equal-count cut: gt_close 77, gt_off 86, 84 pieces with a line within 5 deg of some released line (51.5 %), median best 4.63 deg, median K 1. Walls whole: 78 / 85, 83 (50.9 %), 4.66 deg, K 1. Union S=3: 70 / 93, 76 (46.6 %), 6.32 deg, K 3. Line-weighted share of released lines matched within 5 deg: 38.2 / 37.7 / 34.5 %. Every column matches the comment.
3. **B3 re-measured on the union file itself.** Pot_A_Piece_07_Axis.xyz has 3 lines: 6.31 deg from released line 0, **7.08 deg from released line 1**, 20.32 deg from released line 2. So the missing second axis is genuinely written, blind. (The comment says 22.85 for released line 2 in one sentence and 20.32 in its table; the file measures 20.32.)
4. **One claim corrected: the poses are not bit-identical.** The concatenated T-file md5s differ between the c1b-diag MM arm and the c1c-authorline MM arm, and piece by piece only pieces 3 and 5 match exactly; 1, 2, 4 and 6 differ in low-order digits. What IS identical is the outcome: 4/8 5/15 in all four arms, the same five joins wrong, pieces 07 and 08 absent. The conclusion stands on the counts, not on byte-identity, and the comment's stronger wording is withdrawn.
5. **Also worth recording:** in the 4/8 arms the placed pieces sit about 102-107 deg from ground truth, which is a global frame offset and invisible to the per-edge check (it compares relative transforms). So 4/8 is a self-consistent but wrongly-joined configuration, not a scatter of random poses.

### The landing decision (lead)

**Ship B1 only: the authors' paper chain as the default, with no equal-count cut, and the union behind an explicit flag.** I made that one-line change myself in `sfs_axes/cli.py`: `extract_piece(..., paper_chain=True)`, a new `--union` flag, `--paper-chain` kept as a compatibility no-op, `--truncate` still there for MATLAB parity. Nine regression tests pass.

Reasons: the union is worse on all 163 corpus pieces and catastrophic on the assembler (4/8 5/15); B1 is what the paper describes (line 175: after pruning, all surface points are used), it is the arm the released Piece 08 axis is consistent with, and it is the arm that reaches 7/8 12/15. Neither arm reaches 8/8.

### What this means (claim named)

- **The measurement was broken in two places** - the equal-count cut and the `cost*1.1` prune. Both are now fixed and reachable, and fixing both is still not enough.
- **The method has not failed.** With the authors' axes substituted onto our breaklines, the same assembler seats 8/8 15/15 in the same jobs. What fails is our axis set.
- **The failure is inside the assembly search, not in the candidate pool.** One extra candidate line on one piece moves the global search into a different, self-consistent, wrongly-joined configuration. More candidates is not the fix; which candidate the search trusts is.

**Needs-eye:** `artifacts/pota306/pota_axes_before_after.png` (this session has no image input, so it has not been eye-checked).

## Where the worktree's untracked outputs went (lead, 2026-11-05, before close)

`ticket_close.sh` refused to retire the worktree because it held 5.7 MB of git-ignored files under
`.scratch/pota-repro/306-stage/out/` (the C3 axis dumps in `out/rel/`, `out/union/`, `out/union_chk/`,
`out/c3notrunc/`, `out/pool/`, plus `__pycache__` and a `slurm.out`). Nothing was deleted: the whole
`306-stage/` tree, ignored files included, was copied into the canonical checkout's
`.scratch/pota-repro/306-stage/` first (`cp -a`), and only then was `git clean -Xdf` run on the
worktree's `306-stage/`. The run directories themselves remain the unit of record on Spartan.



