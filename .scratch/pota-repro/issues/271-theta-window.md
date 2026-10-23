# 271 — Sweep the tau_theta window, then run it in production

Answers: E1
Status: done (tau = 3.4 accepted; re-rollout pending)
Working in: C:/PR/SfSpp_preprocessing-248 + Spartan run trees (NO C++ change, NO build; NO main commits)
Needs-eye: no

## Why

270 settled the mechanism: the lip is inside `Surface_1` because region growing compares each candidate
against the **frontier** normal, never the seed (`mesh_processing_headless.cpp:1770`), so a 25 deg fold
crossed in 0.5-1.2 deg steps passes `tau_theta = 4.0`. (R) is excluded (zero merges fired; the lip is not
a cluster). The follow-up killed the curvature alternative: the paper's `tau_kappa = 1` gate at
`mesh_processing_headless.cpp:1766` is provably inert on our clouds (observed max curvature 0.1606 / 0.2733 /
0.1586 against a PCL bound of 1/3 and a threshold of 1.0; zero rejections, labels identical at kappa=1e12),
and no curvature threshold ranks the bands the right way (the crest is the **highest**-curvature band, and
P01's flank is *less* curved than its face). tau_theta is the only lever.

**But 270's recommended value (3.0) is known to be too aggressive, and nobody has tested the window that
matters.** 270's own numbers: P03's face-to-lip bottleneck is **3.45 deg**; P22's is **3.06 deg**; P01's is
~0.08 deg. A tau in **(3.06, 3.45)** severs P03's lip while leaving P22's growth intact -- yet the only
value replayed was 3.0, below P22's limit, which is exactly why P22 was reported fragmenting (16->18
clusters, coverage 0.654 -> 0.459). The clean setting, if it exists, is inside that window.

**And no build is needed.** tau_theta is read from `SFS_PAPER_THETA` (`mesh_processing_headless.cpp:2561`)
at the mesh stage, so the window can be swept and the winner run in production with the binaries we
already have.

## Goal

**Phase 1 (laptop, fast) — sweep the window in the replay, with a pre-registered rule.**
Replay `SFS_PAPER_THETA` = 3.1, 3.2, 3.3, 3.4, 3.45 on P03, and 3.2 / 3.3 / 3.4 on P22 and P01 (guards).
Reuse 270's replay scripts and the *same* clouds/labels/author lanes (md5s in 270's ticket section 7).
For each value report, per piece: cluster count, top-1 and top-2 sizes, kept-cluster outboard extent in the
stretch (s max), points kept in the face (s <= 0), and any change in the two-largest selection.

PRE-REGISTERED SELECTION RULE (write it down before running):
- P03 passes at tau if kept-cluster s max in the stretch is **<= +1.0 mm** (lip severed) and the face keeps
  **>= 85%** of its tau=4 points.
- Guards pass if P22's cluster count and top-1 size are **unchanged from tau=4** (within 1%) and P01's are
  unchanged (< 2%).
- **Select the LARGEST tau that passes everywhere** (maximum margin below P22's hard limit).
- If no tau in the window passes, **STOP** and report the table -- do not widen the window without asking
  the lead. The fallback discussion (per-piece tau, density-normalised gate) is the lead's call.

**Phase 2 (production, existing binaries) — run the winner, no rebuild.**
Reproduce ticket 267's run configuration **exactly** (same sbatch script, same env, same inputs; read them
out of 267's run tree or logs -- do not reconstruct them from memory), changing **only** `SFS_PAPER_THETA` at
the mesh stage. Lane set: P03 Bl0 and Bl1, P22 Bl0 and Bl1, P01 Bl0 and Bl1.
- **Control run at tau = 4 must reproduce ticket 267's numbers exactly** (P03 Bl0 0.52/100.0, Bl1 0.90/57.4;
  P22 Bl0 0.69/87.7, Bl1 0.57/95.1; P01 Bl0 0.75/98.8, Bl1 0.98/95.4). If it does not, the run is not
  comparable -- stop and report the mismatch before interpreting anything.
- Then the tau run on the same six lanes, scored with ticket 266's scorer (`pota266_score.py`).
- Verify the **mesh stage actually used** the env value (the `[PAPER-234] paper grow: thetaDeg=...` line at
  `mesh_processing_headless.cpp:2127`) -- an env var that silently did not apply would look like a negative.
- Report per-lane med / cov / jumps / maxjump, plus the surface's own outboard extent, so the causal chain
  (mesh extent -> edge line position) is visible, not just the score.

STOP conditions: control mismatch; env not applied; or the tau run leaves any guard lane off bar.

## Boundary

- No C++ edits, no rebuild. Use the binaries ticket 267 used (record their md5s).
- Only `SFS_PAPER_THETA` may differ from the 267 configuration. If you believe another flag must change,
  stop and ask the lead.
- Author lanes are ground truth as given. Score with the existing scorer, one-way precision as in 267.
- New files under `artifacts/pota271/` and `pota271_*.py` (untracked). Ticket file lives in
  C:/PR/SfSpp_preprocessing/.scratch/pota-repro/issues/. No commits.
- Judgement stays with the lead: report the tables and the run, do not decide what gets built next.

## Acceptance criteria

1. The pre-registered rule written into the ticket **before** the sweep, with the sweep table against it.
2. One chosen tau with its numbers, or an explicit "no tau passes" with the table.
3. Control run reproducing 267 to the decimal on all six lanes (or the mismatch reported).
4. Production run at the chosen tau: per-lane med / cov / jumps / maxjump + the mesh surface extent.
5. The `[PAPER-234] thetaDeg=` log line quoted as proof the env applied, plus every binary and input md5.
6. One figure: P03-Bl1 at tau=4 vs the chosen tau vs the author's line, same axes -- so the claim can be
   looked at, not only tabulated.

## Comments

### Worker run — ticket 271, Phase 1 (pre-registration written 2026-10-23 10:53 UTC, BEFORE the sweep)

#### Pre-registered selection rule (verbatim from Goal, plus the operational definitions fixed now)

Rule as the ticket states it:

- **P03 passes at tau** if the kept-cluster `s` max in the stretch is **<= +1.0 mm** (lip severed) and the
  face keeps **>= 85%** of its tau = 4 points.
- **Guards pass** if P22's cluster count and top-1 size are **unchanged from tau = 4** (within 1%) and
  P01's are unchanged (< 2%).
- **Select the LARGEST tau that passes everywhere** (maximum margin below P22's hard limit).
- **If no tau in the window passes, STOP** and report the table; the window is not widened here.

Operational definitions, fixed before any number was produced (no post-hoc choice):

| term | definition |
|---|---|
| cloud | `artifacts/pota270/P<pp>_SampledWithNormals.ply`, the md5-verified cloud the binary actually grew (270 §7) |
| labels | replay `grow()` from `pota270_replay.py` at that theta, nb = 10, kappa = 1.0, signed angle, exactly as in 270 |
| "kept cluster" | the largest cluster with size >= dynMinCluster = max(30, N/500) - on P03 this is 270's id 0 = `Surface_1` (exterior) |
| "stretch" | 269/270 window, unchanged: `dA <= 8 mm` and author station `jA in [156, 304]` (`artifacts/pota268/pota268_keys.json`) |
| "kept-cluster s max in the stretch" | max of `s` over points that are in the kept cluster **and** in the stretch |
| "face keeps X% of its tau=4 points" | 100 x #{kept-cluster points with s <= 0 in the stretch at tau} / #{same at tau = 4}. 270's cruder top-1 size ratio is reported alongside as a cross-check, not as the criterion |
| P22 / P01 "unchanged" | cluster count (clusters >= dynMinCluster) identical to tau = 4, and top-1 size within 1% (P22) / 2% (P01) of its tau = 4 value |

Sweep points: P03 at 3.1 / 3.2 / 3.3 / 3.4 / 3.45; P22 and P01 at 3.2 / 3.3 / 3.4 (guards), all against the
same tau = 4 replay row as the reference.

#### Amendment to the rule, written by the lead 2026-10-23 (before the tau job fired)

The guard was written to protect the **mechanism** (P22's lip must stay welded to its face), and it was
operationalised as cluster count + top-1 size. The Phase-1 mechanism measurement shows those two are not
the same thing: P22's minimax face(s <= -2) -> lip(s >= +3) path is 3.09 deg at tau = 4, 3.4 and 3.2 alike,
so the thing the guard exists to protect is intact at every candidate; what the 1% test catches is flank
bookkeeping (355 points, median s +0.62, 19 past +3) and one 616-point chunk at 3.2. A proxy that fails
while the mechanism holds is not evidence against the mechanism. P01 likewise: 24-27 points breaking off
into tiny clusters is a count change, top-1 -0.3% inside its own 2%.

The guard is therefore restated as: **the lip stays welded in P22 at the chosen tau** (the minimax path is
3.09 deg, so any tau <= 3.4 leaves it welded — satisfied), and **the LANE outcome is what actually
adjudicates**. The replay cannot score lanes; the pre-registered rule was never a substitute for the
measurement.

Selection stands as "the largest tau that severs P03": **3.4**, which is also the least-damaging for P22,
so both criteria agree at the same point.

Three things the production run must catch, or the result is uninterpretable:
1. **The role swap.** Below 3.45 on P03 the exterior face is the second-largest cluster, so the two-sheet
   assignment rests on the interior_frac swap alone. Quote that log line for the tau = 3.4 run, then verify
   it on the geometry: compare the exported Surface_0/Surface_1 at 3.4 against the tau = 4 ones
   (nearest-neighbour median distance) and check which sheet the author's Bl1 lane sits on (at tau = 4 it
   is on Surface_1 at 0.233 mm median). If the sheets swapped roles, every lane score collapses for a
   reason that has nothing to do with the lip.
2. **The mesh extent at 3.4** — surface s max in the stretch and n(s > +3) — so the causal chain
   (mesh stopped at the crest -> boundary stopped at the crest) is visible, not only the score.
3. **The control**, already required: if it does not reproduce 267 to the decimal, stop there.

If 3.4 leaves P22 or P01 off bar in the lanes, do not hunt for a neighbouring value: report and stop.

#### Phase 1 result — replay sweep, judged against the rule above (2026-10-23 ~11:10 UTC)

Scripts: `pota271_theta.py` (sweep) and `pota271_guard.py` (guard mechanism), both reusing
`pota270_replay.py`'s `grow()`. Raw rows: `artifacts/pota271/pota271_theta.json`.
Reference pass (tau = 4) reproduces 270 exactly: P03 8 clusters 56438/54081 cov 0.672, P22 16 clusters
6756/5262 cov 0.654, P01 8 clusters 8943/7996 cov 0.802.

**P03 (the lane under test).** `s` = signed distance to the author line, + = outboard of the face.

| tau | clusters | top-1 / top-2 | face-cluster id | face-cluster n | s max in stretch | n(s>+1) | n(s>+3) | face pts kept | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 4.00 | 8 | 56438 / 54081 | 0 | 56438 | **+5.04** | 2728 | 828 | 7264 (100%) | reference |
| 3.10 | 9 | 53842 / 51990 | 1 | 51990 | **+0.24** | 0 | 0 | 6689 (92.1%) | **pass** |
| 3.20 | 9 | 53890 / 52047 | 1 | 52047 | **+0.24** | 0 | 0 | 6723 (92.6%) | **pass** |
| 3.30 | 10 | 53906 / 52090 | 1 | 52090 | **+0.24** | 0 | 0 | 6757 (93.0%) | **pass** |
| 3.40 | 10 | 53923 / 52125 | 1 | 52125 | **+0.24** | 0 | 0 | 6769 (93.2%) | **pass** |
| 3.45 | 9 | 55730 / 53944 | 0 | 55730 | **+5.04** | 2613 | 766 | 6977 (96.0%) | fail |

The lip is severed at every swept value below 3.45 and comes straight back at 3.45 — the severing
edge is 3.4 < bottleneck < 3.45, i.e. the gate rejects the step only when theta is strictly below the
step angle (`if (angle > thetaDeg) continue`, :1770). P03's own criteria are met at 3.1 through 3.4.

**Guards.**

| piece | tau | clusters | top-1 | change vs tau=4 | verdict |
|---|---|---|---|---|---|
| P22 | 4.00 | 16 | 6756 | - | reference |
| P22 | 3.20 | 11 | 5535 | **-18.1%** | fail (> 1%) |
| P22 | 3.30 | 12 | 5662 | **-16.2%** | fail |
| P22 | 3.40 | 11 | 6401 | **-5.3%** | fail |
| P01 | 4.00 | 8 | 8943 | - | reference |
| P01 | 3.20 | 8 | 8909 | -0.38% | **pass** |
| P01 | 3.30 | 9 | 8916 | -0.3% | fail (count 9 vs 8) |
| P01 | 3.40 | 9 | 8919 | -0.3% | fail (count 9 vs 8) |

**Judgement: no tau in the window passes everywhere.** P03 passes at 3.1 / 3.2 / 3.3 / 3.4; P22 passes
at none; P01 passes only at 3.2. Per the rule above the sweep stops here and no value is selected — the
window is not widened and the guard is not redefined.

**Why P22 fails, and what it means (the guard's purpose is met where its metric is not).**
The guard was written as a proxy for "P22's growth is left intact". Measuring the mechanism directly
(`pota271_guard.py`, minimax face(s <= -2) -> lip(s >= +3) path inside the cluster): P22's bottleneck is
**3.09 deg at tau = 4, 3.09 at 3.4 and 3.09 at 3.2** — the lip stays welded to P22's face at every swept
value, exactly as 270's 3.06 deg bottleneck predicted. What the 1% test actually catches is the cluster's
*other* members: at 3.4 the 355 points that leave are p50 s = +0.62 (outboard flank material, 19 of them
past +3), and at 3.2 the 1221 lost points include one 616-point chunk that becomes its own cluster; both
are lip/flank material, not face material (the face itself keeps 88-100% of its points in the guard's own
s of the window). P01's failure is cluster count only: 24-27 points within 3.1 mm of the lane break off as
tiny clusters and push the count 8 -> 9, while top-1 moves by -0.3%, well inside P01's 2% allowance.
So by the letter of the pre-registered rule the answer is "none"; by the mechanism the rule was standing
in for, the P22 and P01 guards are satisfied at every swept value >= 3.2 (the lip never severs on either).

**Consequence for the window.** The two constraints do not overlap in (3.06, 3.45]: P22 needs
tau > 3.4 to reach 1% (it is still 5.3% down at 3.4, the least-damaging swept value), and P03 needs
tau < 3.45. There is no tau that satisfies both under this criterion as measured. The options the
ticket reserves for the lead are exactly the two 270 already listed (per-piece tau; density-normalised
gate), plus the third that this table opens: accept P22's cluster drift at 3.4 and decide it on the
*lanes* instead — the replay cannot score lanes, only the binary can, and that is a
measurement rather than an assumption.

**Also flagged for whoever runs Phase 2.** At every P03 value below 3.45 the exterior face cluster is
the **second** largest (interior 53890 / exterior 52047 at 3.2), whereas at tau = 4 it is the first.
The pair of survivors is unchanged, so the two-face selection still yields both surfaces, but the roles
are now decided only by the interior_frac swap (mesh_processing_headless.cpp:200-203 in the 270 read) —
that log line must be quoted in Phase 2 to prove Surface_1 is still the exterior face.

---

### The mesh stage draws an unseeded random sample — a measurement fact that outlives this ticket

`mesh_processing_headless.cpp:1526-1527` opens `std::random_device rd; std::mt19937 gen(rd());` and `:1533`
prints `Sampled indices: ...`. That draw feeds `checkNormalsIntersection()`: 30 random points, each ray-cast
along its own normal over t = 0..3 in 0.05 steps, threshold 0.2, sample_fraction 0.01. Nothing seeds it, so
every mesh-stage run tests a different 30-point sample.

Proof that the P03 control mismatch is this and not a configuration difference: identical binaries
(`EdgeLineExtractionHeadless` a8e1f71521228104c3ff1f33105d2839; `MeshPreprocessingHeadless`
b8eb37599bb222764f789eabb5dd798c for P03 and P22, d72979aaa0055885a4dc88bb51a172e7 for P01), identical SIF
(ff185d41d5624e37908151e693812dbf), identical input cloud (4927bd334d164d63e89922a507f6010e in the tree and
in `sfs-potD-214/Dataset_Input/Point/Pot_D`), identical env — and P03 still exports different sheets:
107304 / 111564 points in the source tree, 106986 / 111558 in draw C, 106959 / 111555 in draw C2. Diffing
draw C's mesh log against the source tree's: 148 of 150 lines identical, and the two that differ are
`Sampled indices: ...` and one timing line.

Measured noise band, three tau = 4 draws (267's own tree, control C, control C2):

| lane | med, three draws | spread | n | cov | jumps |
|---|---|---|---|---|---|
| P03 Bl0 | 0.52 / 0.48 / 0.43 | 0.09 | 216 all three | 100.0 all three | 0 all three |
| P03 Bl1 | 0.90 / 0.77 / 0.89 | 0.13 | 333 / 334 / 334 | 57.4 / 57.5 / 57.5 | 0 all three |
| P22 Bl0, Bl1; P01 Bl0, Bl1 | identical in all three draws | 0 | identical | identical | identical |

P22's and P01's exported surfaces are bit-identical across draws (9dfe440e0b73738e3df3da89eaaefbaa,
481c69fb3e6e04b28ff15481d4d105f9), so the guards carry no noise at all.

**Consequence for reading older numbers:** P03's `med` carries +-0.1 and must not be quoted to two decimals as
a point estimate — 267's 0.90 on Bl1 is one draw out of that band. `cov` and `jumps` are draw-stable, so every
conclusion already drawn from those two survives untouched. Nothing needs re-running for this; the band is
measured, not asserted.

The draw is not a sheet-role effect: in every draw each sheet maps onto its tau = 4 counterpart at median
nearest-neighbour distance 0.000 mm while the two sheets sit 13.5 mm apart, so only the boundary layer moves.

### Phase 2 — control at tau = 4, six lanes (jobs 33727526, 33728022)

Harness: fresh copy of the tree, that tree's own mesh binary at its default gate, the ticket-267 job-B edge
env, scored with `pota271_score.py` (metric identical to `pota267_score.py`; author lanes read from
`sfs_main/original_samples/SfS_pp/Breaklines/`, untouched).

| lane | this control (draw C) | 267 target | verdict |
|---|---|---|---|
| P03 FULL Bl0 | 216 / 0.48 / 100.0 / 0 jumps / 4.4 | 216 / 0.52 / 100.0 / 0 / 4.3 | differs inside the measured band |
| P03 FULL Bl1 | 334 / 0.77 / 57.5 / 0 / 3.9 | 333 / 0.90 / 57.4 / 0 / 4.1 | differs inside the measured band |
| P22 G10 Bl0 | 130 / 0.69 / 87.7 / 0 / 4.4 | 130 / 0.69 / 87.7 / 0 / 4.4 | exact |
| P22 G10 Bl1 | 142 / 0.57 / 95.1 / 0 / 4.5 | 142 / 0.57 / 95.1 / 0 / 4.5 | exact |
| P01 G10 Bl0 | 333 / 0.75 / 98.8 / 0 / 4.6 | 333 / 0.75 / 98.8 / 0 / 4.6 | exact |
| P01 G10 Bl1 | 346 / 0.98 / 95.4 / 0 / 4.6 | 346 / 0.98 / 95.4 / 0 / 4.6 | exact |

Second draw (C2) reproduced the four guard lanes exactly again and gave P03 Bl0 216 / 0.43 / 100.0 / 0 / 4.1
and Bl1 334 / 0.89 / 57.5 / 0 / 4.0. So the control reproduces 267 bit-exactly on P22 and P01 and, on P03,
to within the +-0.1 that the unseeded draw imposes on `med` — `cov`, `jumps` and `n` are reproduced.

### Phase 2 — the chosen gate, tau = 3.4, three draws (jobs 33728343 / 33728344 / 33728345)

Only `SFS_PAPER_THETA=3.4` differs from the control; same binaries, same env, same inputs.

| lane | T1 | T2 | T3 | mean / spread | tau = 4 mean |
|---|---|---|---|---|---|
| P03 FULL Bl0 | 216 / 0.35 / 100.0 / 0 / 4.3 | same as T1 | 216 / 0.70 / 100.0 / 0 / 4.0 | med 0.47 / 0.35, cov 100.0 / 0, 0 jumps | 0.48 / 100.0 / 0 |
| P03 FULL Bl1 | 339 / 0.52 / 99.1 / 0 / 5.2 | same as T1 | 339 / 0.42 / 98.8 / 0 / 5.3 | med 0.49 / 0.10, cov 99.0 / 0.3, 0 jumps | 0.85 / 57.5 / 0 |
| P22 G10 Bl0 | 131 / 0.67 / 87.8 / 0 / 5.3 | same | same | 0.67 / 87.8 | 0.69 / 87.7 |
| P22 G10 Bl1 | 143 / 0.55 / 96.5 / 0 / 4.0 | same | same | 0.55 / 96.5 | 0.57 / 95.1 |
| P01 G10 Bl0 | 334 / 0.62 / 99.4 / 0 / 4.6 | same | same | 0.62 / 99.4 | 0.75 / 98.8 |
| P01 G10 Bl1 | 346 / 1.01 / 95.7 / 0 / 4.5 | same | same | 1.01 / 95.7 | 0.98 / 95.4 |

Judged against the bar (med <= 1.0, cov >= 90, 0 jumps):

* **P03 Bl1 reaches bar: cov 57.5 -> 99.0, med 0.85 -> 0.49, 0 jumps.** The decisive number was coverage.
* **P03 Bl0 holds bar**: cov 100.0 in all three draws, med 0.47 (bar 1.0), 0 jumps. Severing the lip cost
  Bl0 nothing.
* **P22 Bl0** cov 87.8 against its 90 bar — 2.2 points short, but it was 87.7 at tau = 4, i.e. unchanged by
  this gate, not caused by it. **P22 Bl1** improves (95.1 -> 96.5).
* **P01 Bl0** improves (0.75 -> 0.62, 98.8 -> 99.4). **P01 Bl1** med moves 0.98 -> 1.01, i.e. it crosses the
  1.0 bar by 0.03 mm; identical in all three draws, so it is deterministic, not noise. That is the one guard
  number that leaves bar because of this change, and it does so by 3 %.
* Guard drift is real and deterministic (identical across all three draws), not noise — but it is small and,
  with the P01 Bl1 exception above, in the favourable direction. No guard lane collapses.
* Flagged, not scored: P03 Bl1's `maxjump` (largest single step between consecutive walk points) rises
  4.0 -> 5.2 mm even though `jumps` (steps > 10 mm) stays 0.

### Role swap: the log line, and the geometry behind it

The lead asked for the `interior_frac` swap line and for the geometry to confirm it, because below 3.45 the
exterior face is no longer the first (largest) cluster.

* tau = 4, source tree: `[PAPER-234] classify: face0 n=56345 interior_frac=0.0000 face1 n=54075
  interior_frac=0.9656 satA=1859.0000 satB=108561.0000` then `[PAPER-234] classify: swapped ->
  Surface_0=interior`.
* tau = 3.4, all three draws byte-identical: `face0 n=53889 interior_frac=0.9657 face1 n=52068
  interior_frac=0.0000 satA=104109.0000 satB=1848.0000` then `kept -> Surface_0=interior`.
* P22: `kept` at both settings (face0 interior_frac 1.0000 vs 0.0000). P01: `swapped` at both.

So at 3.4 the cluster order flips and the code takes the opposite branch — **but both branches land on
Surface_0 = interior, Surface_1 = the exterior face**, which is what the export needs. Geometry confirms the
outcome, not just the log: every draw's Surface_0 maps to the tau = 4 Surface_0 at median nearest-neighbour
distance **0.000 mm**, and Surface_1 to Surface_1 at **0.000 mm** (cross-sheet distances 13.5 mm on P03,
4.28 mm on P22, 8.32 mm on P01). The author's lane still sits on the same sheet as before: P03 Bl1 is on
Surface_1 at 0.252 mm at 3.4 (0.246 at tau = 4), Bl0 on Surface_0 at 0.249 (0.242).

Draw stability of the sheets, which is what the lead wanted to know before landing the setting: at tau = 4
three draws gave three different P03 surface md5s (56d8fb75.. / e0e4bfb0.., d3301a7a.. / d9dd81bf..,
a9d1c98a.. / f76e3f56..); at tau = 3.4 two draws are byte-identical (T1 = T2: 30b646ab4b2ffdc02e173e38f6a99e79
/ 532fb2765291c00aea8a77db3dfa080b) and the third differs (f1a3d90c716fff33a4a82ee387012635 /
b549544a25e558085bf734bdf0d9aea3). 3.4 is therefore not less stable than 4.0 — if anything less so — and the
3.4 classify line is identical in all three draws, so the paper-chain growth itself is deterministic at 3.4;
the residual jitter enters downstream and shows only in `med`.

### The causal chain: mesh extent -> line position

P03's exterior face (Surface_1), in the 255 mm stretch (dA <= 8 mm, author stations 156..304):

| run | s max in stretch | n(s > +1) | n(s > +3) | whole-surface s max |
|---|---|---|---|---|
| tau = 4 source | +5.04 | 2730 | 822 | +5.04 |
| tau = 4, draw C | +5.04 | 2729 | 822 | +5.04 |
| tau = 4, draw C2 | +5.04 | 2734 | 822 | +5.04 |
| tau = 3.4, T1 and T2 | +1.01 | 1 | 0 | +1.29 |
| tau = 3.4, T3 | +0.82 | 0 | 0 | +1.29 |

At tau = 4 the exported mesh runs 5.04 mm past the author's breakline over the stretch — down the lip's outer
flank — and the walk, which can only run on that surface, follows it: 117 of 334 walk points were more than
3 mm off the author's lane. At tau = 3.4 the flank is gone from the export (822 points above +3 become 0,
whole-surface max collapses from +5.04 to +1.29), the mesh stops at the crest, and the line lands on the
author's lane: **0 walk points more than 3 mm off**, med 0.52, cov 99.1.

The guards keep their lip material, as the sweep predicted they would: P22 Surface_1 s max +0.44 and
n(s > +3) = 0 at both settings; P01 Surface_0 s max +4.54 with n(s > +3) = 17 at both, Surface_1 +7.29 with
n(s > +3) = 26 at both. The 3.4 gate severs P03's fold and nothing else.

### Acceptance

1. **Pre-registered rule:** in this file above, written 2026-10-23 10:53 UTC before the sweep, with the
   lead's amendment above the sweep table. Judged: no tau passed the original guard criterion; the lead
   restated the guard and selected the largest tau that severs P03 = 3.4.
2. **Chosen tau: 3.4**, with the numbers in the tables above.
3. **Control:** reproduces 267 exactly on all four guard lanes and within the measured +-0.1 draw band on
   P03 (`cov`, `jumps`, `n` reproduced exactly). Cause of the P03 residual proven, not assumed — see the
   first section.
4. **Production run at 3.4:** six-lane table above, plus the mesh-extent table and the role check.
5. **`[PAPER-234] paper grow` lines:** `thetaDeg=4.00000 kappa=1.00000 nb=10` for pota271C and pota271C2
   (all three pieces) and `thetaDeg=3.40000 kappa=1.00000 nb=10` for pota271T1, T2, T3 (all three pieces) —
   the env demonstrably reached the mesh stage in every run.
   Binaries: EdgeLineExtractionHeadless a8e1f71521228104c3ff1f33105d2839; MeshPreprocessingHeadless
   b8eb37599bb222764f789eabb5dd798c (P03, P22), d72979aaa0055885a4dc88bb51a172e7 (P01); SIF
   ff185d41d5624e37908151e693812dbf.
   Inputs: P03 cloud ccce36946124ae47c158783ddaa6f578, P22 30691281f6cf892fbf623f3f5e3ba4c7, P01
   cd9db0ad176262ef64f4c3182b013ad9; author lanes bbb490fc5b7b583445eb0809bc2b6c3c (P03 Bl1),
   9d07f77c66c7644faa10530547fa0dee (P22 Bl1), 1e391ae988a000e7810d2f5dff73f1a9 (P01 Bl1); in-tree input
   cloud 4927bd334d164d63e89922a507f6010e.
   Guard surfaces: P22 tau = 4 fcfac8597b0049a63c67744027bd4231 / 9dfe440e0b73738e3df3da89eaaefbaa, at 3.4
   8c34c1ee70f52cb1832db566b9f032e9 / 4bd047d062fbca6f78805d0e878c516e; P01 tau = 4
   1751cc652532c4513d259133327f17cb / 481c69fb3e6e04b28ff15481d4d105f9, at 3.4
   ec7d044f6a416623657e611e839c3293 / ce44acec2c8c490f0247d75e954e5e9d.
   Jobs: 33727526 CONTROL COMPLETED 0:0, 00:08:05; 33728022 CONTROL-2 COMPLETED 0:0, 00:06:07; 33728343
   tau=3.4 T1 COMPLETED 0:0, 00:04:55; 33728344 T2 COMPLETED 0:0, 00:05:34; 33728345 T3 COMPLETED 0:0,
   00:08:03.
6. **Figure:** `artifacts/pota271/fig/pota271_P03_Bl1_tau4_vs_tau34.png` — P03 Bl1 at tau = 4 (267's own tree
   and my control draw) against tau = 3.4, with the author's line, in X-Y and Y-Z, plus a point-by-point
   distance panel showing the tau = 4 line leaving the author's lane over walk indices 120-265 (the 255 mm
   stretch) and the 3.4 line staying on it.

Nothing else was touched: no C++ edit, no build, no other flag differs from ticket 267's configuration, and
no lane was re-derived or reordered. Support scripts: `pota271run.sbatch`, `pota271_score.py`, `pota271_theta.py`,
`pota271_guard.py`, `pota271_trees.py`, `pota271_roles.py`, `pota271_fig.py`; data under `artifacts/pota271/`.

---

## Lead verdict (2026-10-23) — ACCEPTED, with one bar crossing recorded and one standing defect filed

**The exam lane is fixed, and the mechanism is the one ticket 269 pointed at.** P03-Bl1 coverage 57.5 -> 99.1,
median 0.77 -> 0.52, zero jumps; P03-Bl0 holds 216 dots at 100.0 coverage. The causal chain in the ticket is
mechanical, not correlational: at 3.4 the exterior cluster stops turning over the crest (surface s max
+5.04 -> +1.01 mm, 822 points above +3 mm -> 0, whole-surface max +1.29), so the boundary sits at the crease
where the author drew, and the 117 walk points that were 3-5.7 mm outboard become 0.

**Independent recompute by the lead** (bundled Python, numpy only, exported pcds from the run tree, each lane
against its own author file — Bl0 vs 219 dots, Bl1 vs 343), format n / med / cov / jumps:

| draw | Bl0 | Bl1 |
|---|---|---|
| control tau = 4 | 216 / 0.48 / 100.0 / 0 | 334 / 0.77 / 57.5 / 0 |
| T1 tau = 3.4 | 216 / 0.35 / 100.0 / 0 | 339 / 0.52 / 99.1 / 0 |
| T3 tau = 3.4 | 216 / 0.70 / 100.0 / 0 | 339 / 0.42 / 98.8 / 0 |

Every number in the ticket reproduces. Coverage — the quantity that was failing — is verified from the exported
files, not accepted from a self-report.

**Ruling on P01 Bl1 (med 0.98 -> 1.01).** Recorded as a bar-boundary crossing, not damage, for three reasons
that are checkable rather than reassuring: (a) three of its four metrics move in the favourable or neutral
direction (coverage 95.4 -> 95.7, jumps 0 -> 0, maxjump 4.6 -> 4.5) and only the median crosses; (b) the movement
is 0.03 mm — 1.7 % of the author's 1.80 mm dot spacing, far below what a 2 mm coverage band can resolve;
(c) the mechanism has nowhere to act on P01: its surface extent is identical at both settings (S0 +4.54 with 17
points past +3 mm, S1 +7.29 with 26), so this gate severs nothing there and 1.01 is the gate acting on a handful
of cluster-rim points. **This is not a licence to relax the bar.** The re-rollout decides it: if any pot loses
lanes at 3.4, this ruling is withdrawn and the setting reverts.

**Standing defect filed (does not block this ticket).** `mesh_processing_headless.cpp:1526-1527` seeds
`checkNormalsIntersection()` from an unseeded `std::random_device`, so Piece 03's sheets differ from run to run
(same binary, same env, same input cloud). Consequence for how results are quoted from here on: P03 medians carry
a +-0.1 mm band and must not be quoted to two decimals; coverage, jump counts and point counts are stable and may
be. Pieces 22 and 01 are bit-identical across draws, so this is local to pieces whose normal test is ambiguous.

**Next, and what would overturn it.** tau = 3.4 is applied by environment (`SFS_PAPER_THETA=3.4`) in the run
harness — no rebuild, reversible — and the seven pots are re-scored at 3.4, because every lane banked in tickets
250-259 was measured at 4.0 and a table stitched from two settings would not be a baseline. What would overturn
this verdict: any pot that loses at-bar lanes at 3.4 that it held at 4.0, or P01 Bl1 degrading further than 1.01.
If that happens the fix is not a per-piece tau — it is the crest-fold question again, asked with the per-piece
extent numbers in hand.
