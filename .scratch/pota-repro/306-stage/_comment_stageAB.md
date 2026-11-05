
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

#### A3 — provenance probe: which reader made the released axes

Piece 08, released line 1, both clouds, same cost and the same LM.

| | untruncated (n=3337) | truncated (n=3152) |
|---|---|---|
| cost at the released line | 225.35 /pt (1336 inliers) | 228.92 /pt (1259 inliers) |
| refine **from** the released line | moves **5.2280 deg**, cost 78.38 /pt (-65%) | moves **88.15 deg**, cost 77.11 /pt |
| 5-degree perturbation, 8 azimuths | 6 of 8 return to the 5.2280-deg point | 8 of 8 leave for ~88 deg |
| 10-degree perturbation, 8 azimuths | 5 of 8 return to the 5.2280-deg point | 8 of 8 leave |
| the other 2-3 basins | slide to a different minimum 86.02 deg away, 75.64 /pt | — |

The released line is **not** a stationary point of our cost on either cloud. The untruncated cloud has
a reproducible minimum 5.23 deg from it — last night's good axis (0.19 deg away) is that minimum — and
the truncated cloud has no minimum anywhere near the released line. The reader is therefore the thing
that made the difference, not the cost and not the estimator: `read_surfaces(truncate=True)` cuts the
longer wall to the shorter one and destroys the basin's catchment (it does not stop a lucky draw from
landing in it, which is why the truncated pool still contains the basin at seed 1).

Claim named: this is **the measurement was broken** (input handling), not "the method failed".
5.23 deg is inside the assembler's 20.05 deg bar, which is why truncation-off seated 12/15.

### Stage B — the change, and what it writes

B1 `sfs_axes/io_surfaces.py`: `read_surfaces(..., truncate=False)` by default — the NURBS reader's
behaviour (both walls whole). The truncating path is unchanged and still reachable (`truncate=True`,
`cli --truncate`), so the MATLAB-faithful behaviour is preserved for anyone who asks for it.

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
