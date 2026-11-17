# 332: The Juglet's axis must come from our code — diagnose the piece that misses the key, and fix the cause

**What to build:** the axis stage produces all nine Juglet axes from **our own code**, matching
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` closely enough to be used instead of it, and the reason the
failing piece misses is **named with evidence** rather than inferred. This ticket diagnoses; it does not
re-run assembly. Today the chain is an oracle on the Juglet: the 3x cells read
`AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large`, and every one of those nine files is the
key (verified 2026-11-17: direction **0.000 deg** against `Juglet_GT`, offset ratio 1.000, on pieces 1, 5,
7, 9; only the file layout differs). The 1x cells read `Dataset/Axes/Juglet`, our own September MATLAB
output, which is right on 1 of 9 and **73.3 deg / 16.0 mm** off on piece 9 (ticket 322). So no lane in any
seating result so far used an axis our current code produced.

**Answers:** E1
**Blocked by:** None (can start immediately). If the mechanism turns out to be the size-keyed branch, this
ticket supplies the answer ticket 325 needs; it does not replace 325's whole-corpus rewrite.
**Status:** resolved
**Branch:** 332-juglet-axis-must-match-the-key, in /c/PR/worktrees/sfs/332
**Worker:** dsh one-shot subagent w332
**Budget:** medium 5
**Hand-over:** DeepSeek — check path: the lead re-reads the per-piece rank table against the key from a
fresh run, the pool-coverage dump for the failing piece, the per-term attribution table, and the 172-file
`cmp` count; **no assembly run, no seating number, so there is no hidden acceptance run to write**.

## What is already known (verified by the lead, 2026-11-17; do not re-derive as if new)

- **The key is right and the old released folder is wrong.** Ticket 322 established it from a third witness
  (`TORA/dataset/juglet_gt.hdf5`, 0.000-0.002 deg) and from the nine `Juglet_GT` transforms. Claim (3)
  ("the reference was wrong") is **closed**: the folder `Dataset/Axes/Juglet` was our own Sept MATLAB run,
  not an authors' reference.
- **Our finder against that key:** rank 0 within 10 deg on **4 of 9**, best-of-3 **6 of 9**, best-of-6
  **8 of 9**; piece 9 is **31.8 deg even at its best rank** (ticket 322, Q7). The one piece that no ranking
  on the current pool recovers is **piece 9**.
- **Three pieces' own walls prefer another line.** On p3, p8 and p9 the piece's own data prefer a line
  25-52 deg from the vessel axis (worse-wall cost at key 0.035 / 0.039 / 0.079 against 0.022 / 0.020 /
  0.023 at the local optimum). That is the input ceiling the ticket must test for, not assume away.
- **The finder is out of range on this object, not merely inaccurate.** Every Juglet piece sits below the
  finder's 25 mm clearance floor, so the wall-not-base gate is unsatisfiable; and the prior *prefers* axes
  further from the piece when every candidate is below its knee. The pot-scaled lengths are enumerated in
  ticket 325 with `file:line` (`AxisExtraction/sfs_axes/normalized.py:20` `DEFAULT_CLEARANCE_MM = 25.0`,
  `:138` inside `is_base_fragment`, `:183-202` the penalty; `potsac.py:176` `MAX_CLEARANCE_MM = 250`,
  `:526-533` `r_prior`, `:604-606` `valid_cone` 25-110 / `valid_dish` 35-115).
- **There is also a size-keyed branch.** `AxisExtraction/sfs_axes/potsac.py:482` "Regime 1" switches on
  `w_dc <= 15.5`, `diag <= 65`, `min_hcw <= 38` — ticket 322 calls it "the switch that sends the Juglet
  down a separate branch: a small-object patch keyed on size". **Which path the Juglet's axes actually come
  out of is an open question this ticket must settle before it explains anything.**

## The scale question (read first — this is where the pipeline stands today)

There is **no axis-generation step in the lane that seats the vessel**. `stage66/run_cell66.sh` takes
`AXIS_DIR` (default `$DS/Axes/$POT`, `run_cell66.sh:12`, `:44`) and passes `SFS_AXIS_FILE` into the mesh
stage (`:139-157`); it never runs the finder. On the **3x** lane `AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large`,
and that directory holds the **scaled answer key** — `Juglet_Piece_<i>_Axis.xyz` with the point multiplied by
3.0 and the direction unchanged, built by ticket 331 `tools/build_large.py` (verified: `head` of
`Juglet_large/Juglet_Piece_1_Axis.xyz` is `183.903911286378 148.464809059142 -134.053282670196 ...` against
`Juglet_GT`'s own numbers `183.90...` — the same line). `Juglet_large/` has **no `Point/` and no `Axes/`**.

So three facts this ticket must hold together:

1. **The axis is supplied, not generated, in every cell that has seated anything.** The 9-of-9 (ticket 362)
   is an oracle result on the axis stage, both at 3x (key x3) and at 1x (our Sept MATLAB folder, 1 of 9 right).
2. **The 3x lane is the one that assembles**, and its geometry is in tree units where **3 units = 1 mm**
   (`SFS_TREE_UNITS_PER_MM=3.0`; `Juglet_Piece_2_Mesh.obj` 84.93 units vs 28.31 mm). The 3x cloud exists, from
   ticket 331's own sampling: `runs/20261112-0218_b1e1580_t331-large/cloud_mesh/` (`cc_mesh_to_pcd.sh -m 1000000 -f`
   on the nine scaled meshes, manifest `pins/MANIFEST_JUGLET_LARGE.tsv`).
3. **The finder has no notion of the tree's units.** It reads a cloud and applies absolute-millimetre gates
   (the list in ticket 325). Fed the 3x cloud it would see a ~100 mm-diameter vessel whose wall sits 33-48 mm
   out: the 25 mm clearance floor becomes *satisfiable*, while the `r_prior` knee (30/40 mm) lands **inside**
   the wall radius and `MAX_CLEARANCE_MM = 250` is 2.5x the vessel. Fed the 1x corpus cloud it is the regime
   ticket 322 measured. **Neither run has been done, and the two are different questions.**

Therefore stage A and B run **twice**: once on the 1x corpus cloud (`Dataset/Point/Juglet/*.pcd`, what
preprocessing step 2 reads) and once on the **3x cloud the winning lane consumes**
(`runs/20261112-0218_b1e1580_t331-large/cloud_mesh/`). Report angles in degrees (scale-free, comparable
across the two) and offsets **in original-vessel millimetres** as well as in the input's own units, so the
two columns can be read side by side; say explicitly which scale the fix is proved at. If a code-generated
axis is to serve the 3x lane it must come out in the lane's units — either the finder runs on the 3x cloud
with the mm gates rescaled or made scale-free, or the axis is scaled on the way in the way ticket 331 scaled
the key (point x3, direction unchanged). **Say which, and why it is not a per-object constant.**

## Stages

**A — Baseline, rebuilt by us (must reproduce, else `blocked`).** Run the shipped axis path on the nine
**1x** Juglet pieces **and, separately, on the 3x cloud above (task A2)** exactly as the last Juglet run did (`runs/20261110-0320_41494d0_t320b-juglet`, job
`34617857`; find its driver rather than inventing one) on a compute node, poll with
`scripts/remote/job_status.sh`, record final `sacct` State/ExitCode. Score every written line against
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`: **direction error in degrees and offset in mm at the piece
centroid, per piece, for rank 0..5**, plus which path produced it (Regime 1 vs the normalized union). It
must reproduce **4 / 6 / 8 of 9** within one piece of ticket 322's count and piece 9 near 31.8 deg. If it
does not, stop: the shipped path has moved since 322 and this ticket's premise is stale — report
`blocked: baseline does not reproduce` with the table.

**B — Is the true line even in the pool?** Per piece, the nearest basin in the candidate pool to the key:
report the angle, and whether a line within 1 / 5 / 10 deg exists at all. Reuse `t322/dump_basins.py`
(10 seeds x 1000 Pottmann draws, 10 deg clustering, 60 largest basins refined) or the equivalent; this is
the test that separates "the pool never offered it" from "we offered it and chose wrong". **Check the pool
on the 1x cloud the E2E itself uses, not only on the released surface xyz**, if the two differ.

**C — Attribution for every piece that misses at rank 0, and piece 9 first.** For that piece, a table of
each element's value **at the key** and **at the chosen winner**: the Regime-1 switch (`potsac.py:482`),
each gate that could reject it, the penalty (`normalized.py:183-202`), the `r_prior` knee
(`potsac.py:526-533`), the fit's drift from the true line, and the final ranking score. Name the one
element that costs the most, with numbers. Then state the claim: (1) the method fails, (2) the measurement
is broken, or (3) the reference is wrong — (3) is closed, so only (1), (2) or "input ceiling" is available,
and "input ceiling" needs stage B's dump to say the line is not in the pool at all.

**D — The smallest general fix, and only if C names one.** No constant keyed to the Juglet, no unit switch,
no "small object" flag (the conservator's 2026-11-10 ruling, ticket 322). If the mechanism is the size-keyed
Regime-1 switch or a pot-scaled length, make that element dimensionless in the piece's own size (bbox
diagonal, fitted radius or rms radius — say which, and why it is the right denominator for that term) and
show the pot margin it leaves. Then re-score the nine: **the bar is rank 0 within 10 deg on all nine**, and
whatever remains short must be explained by stage B (a piece whose pool holds nothing within 10 deg is an
input ceiling — report it as such with the dump, and do not force it). If C says a piece is a ceiling,
**stop at the diagnosis** rather than buying the bar with a constant.

**E — The pots must not move by a byte.** One writer run over the 172 pieces (`scripts/run_benchmark_172.py`,
the ticket-324 job as the template) and `cmp` every file against
`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323` (172 files, 251
lines). **Any differing file stops the ticket**: name the piece, the gate or score term that flipped, and
its pot-side margin. Do not nudge a threshold until it matches.

**F — Look at it.** Per piece, a render with the key, our rank-0 line and the winner drawn on the piece's
own cloud, at a view that resolves a 33 mm vessel, into
`SfSpp_preprocessing/artifacts/pota332/renders/` (gitignored). Look at it **before** writing the Reading;
a right angle on a line that is drawn off the piece is not a right axis.

## What would settle it (acceptance)

- [ ] A: the nine-piece rank table (rank 0..5, degrees and mm) against the key, from our own run, with job
      IDs and final `sacct` states, reproducing 322's 4/6/8 or declaring `blocked` with the table.
- [ ] B: per-piece nearest-pool-line table, saying which pieces have a line within 10 deg in the pool.
- [ ] C: the per-term attribution table for every rank-0 miss, with the failing element named and the claim
      labelled (method / measurement / input ceiling).
- [ ] D: either nine of nine within 10 deg at rank 0, or the per-piece proof that the pool does not contain
      it — with no object-specific constant added, and the byte-identity (E) still holding.
- [ ] E: 172 of 172 files identical by `cmp`, or the ticket stopped with the flipped term named.
- [ ] F: the renders, and one sentence saying what they show.
- [ ] No assembly run, no `Dataset/` write, no edit to the paper chain (`run_potsac`).
- [ ] Code tickets: branch merged into main and pushed, no job still running from it, worktree removed,
      branch deleted locally and on GitHub.

## Readings (pick one, verbatim, on a `Reading:` line)

`juglet-axis-matches-key-from-code` | `juglet-axis-mechanism-named-not-fixed` |
`juglet-axis-piece-has-no-basin` | `juglet-axis-fix-breaks-the-pots`

## Out of scope

Rerunning the assembly or any seating number; the 3x bundle's lane wiring (ticket 331/362); the wall-side
and breakline work (tickets 327/328/79); changing `Dataset/`; the paper's own chain (`AxisExtraction/run_potsac.m`);
ticket 325's whole-corpus rewrite beyond the one element this ticket proves; any constant, flag or branch
that exists because the object is small.

## Comments (worker, 2026-11-17) - w332

### Where this ran

Branch `332-juglet-axis-must-match-the-key`, worktree `C:/PR/worktrees/sfs/332` at `5ec5bef`.
Run dir: `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-1155_5ec5bef_t332-axes` (`run.json`, `submit*.sbatch`,
`work/impl` = the laptop worktree code, md5-verified). Code is byte-identical to the shipped tree
(`scripts/run_benchmark_172.py ac53d347…`, `sfs_axes/potsac.py 89187944…`, `select.py 7df8d709…`,
`profile.py b1dcba31…`, `normalized.py 8cc382e6…`). Compute node only; every job below was submitted with
`sbatch` and polled with `scripts/remote/job_status.sh`; final `sacct` states are in the job table at the end.

The key is `Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` throughout. Error metric is ticket 322's
`ref_errors`: unsigned direction angle, and offset = distance between the two lines measured at the piece
centroid (mm, original vessel). `work/score_key.py`.

### Stage A — the baseline reproduces, and it reproduces *two different answers*

Both paths were re-run through the shipped writer on the nine 1x pieces, from the same staged code, and
both are **byte-identical to the sets already on disk**:

- pass N, `SFS_AXES_UNION_RANKER=normal` (the path that wrote `axes320` and therefore the axis input of the
  `t320b-juglet` seating run, job 34617857): `cmp` 9/9 identical to `runs/20261108-1350_e556fc8_t318a-axes/out/axes320`.
- pass P, shipped default (profile ranker + 1.2x keep rule): `cmp` 9/9 identical to
  `runs/20261110-0740_d628fc0_t323-axes/out/axes323`.

So the harness is not in question, and the ticket's 4/6/8-at-rank-0 / piece 9 at 31.8 deg reproduces exactly.
But it reproduces **on the old ranker only** — and the old ranker is what the seating run consumed:

**AX_N = normal ranker = axes320 (the seating input). deg / mm offset at centroid, ranks 0..5:**

| piece | r0 | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|---|
| 1 | 1.45 / 0.15 | 12.49 / 2.51 | 11.27 / 1.96 | 11.92 / 1.92 | 23.04 / 3.22 | 27.04 / 4.13 |
| 2 | 14.13 / 3.63 | 5.85 / 1.05 | 28.88 / 6.81 | 23.40 / 2.66 | 18.32 / 2.77 | 6.61 / 2.02 |
| 3 | 18.45 / 2.43 | 35.13 / 6.96 | 0.79 / 1.34 | 13.67 / 3.82 | 16.85 / 3.70 | 24.74 / 6.14 |
| 4 | 2.12 / 0.94 | 13.12 / 3.21 | 8.22 / 2.14 | 19.08 / 5.52 | 28.76 / 7.11 | 30.69 / 7.63 |
| 5 | 2.66 / 1.08 | 15.60 / 3.89 | 19.44 / 4.64 | 20.35 / 4.87 | 10.54 / 2.11 | 35.00 / 7.37 |
| 6 | 12.65 / 2.88 | 16.46 / 3.58 | 22.41 / 5.23 | 14.88 / 3.63 | 8.68 / 1.75 | 26.44 / 4.61 |
| 7 | 6.25 / 2.49 | 13.51 / 3.86 | 28.11 / 3.42 | 11.52 / 2.24 | 16.04 / 3.21 | 13.77 / 3.73 |
| 8 | 17.43 / 2.89 | 13.26 / 2.50 | 40.65 / 9.15 | 16.24 / 3.85 | 6.45 / 1.61 | 44.81 / 8.72 |
| 9 | 31.84 / 7.47 | 40.15 / 9.87 | 86.82 / 20.31 | 40.50 / 10.94 | 73.07 / 16.15 | 51.88 / 12.08 |

rank0 within 10 deg **4/9**, best-of-3 **6/9**, best-of-6 **8/9**, rank-0 mean 11.89 deg — ticket 322's numbers,
reproduced. Piece 9 is 31.84 deg at rank 0 and never better than 31.84 in six.

**AX_P = shipped default = axes323 (what our code produces today). deg / mm at rank 0:**

| piece | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| deg / mm | 0.92 / 0.16 | **13.16 / 2.91** | **28.39 / 3.56** | 3.44 / 1.19 | 3.72 / 0.87 | 1.84 / 1.00 | **47.92 / 8.22** | 3.05 / 0.43 | 4.56 / 3.17 |
| lines written | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 3 |

rank0 **6/9**, best-3 7/9, best-6 7/9, mean 11.89 deg. **The shipped path's failing pieces are 2, 3 and 7, and
piece 9 is not one of them** (4.56 deg). Piece 7's own second line is 2.56 deg / 0.55 mm; piece 3 has an
8.64-deg line available. The "piece 9 at 31.8 deg" premise is true of the ranker that fed the seating
run, not of the code we ship; both are reported above so the lead can use the right one.

### Stage A2 / B — the scale question (3x) and the pool

The 3x lane reads `AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large`, which is the **key scaled x3**
(direction unchanged), so ticket 362's 9-of-9 is an oracle on the axis stage, as the lead's section says.
Three runs answer whether the unit is the cause:

- **A1** — finder on the 1x corpus cloud (`Dataset/Point/Juglet/*.pcd`, the cloud the E2E actually uses):
  **7/9** at rank 0, mean 5.68; misses p7 13.61 deg / 2.63 mm, p9 12.25 / 4.82.
- **A2P** — finder on the 3x cloud (`runs/20261112-0218_b1e1580_t331-large/cloud_mesh`), constants untouched,
  answer read in tree units: **7/9** at rank 0, mean 6.90, best-of-3 8/9; misses p3 10.11 / 2.45 mm,
  p9 29.81 / 8.50 mm.
- **A2N** — the old normal ranker on the 3x cloud: **0/9** at rank 0, best-of-3 3/9, mean 41.89.

The Regime-1 switch (`potsac.py:493`, `w_dc <= 15.5 and min_hcw <= 38.0 and diag <= 65.0`) **fires on all nine
1x pieces** (diag 23.06-62.68 mm) and **cannot fire at 3x** (diag 70.5-189.1). It changes nothing, because on
the shipped default `run_potsac_union` returns at `potsac.py:478-481` before it is reached; and when the old
path is selected explicitly, its output at 3x is 0/9. **So the unit is not the cause and no rescaling of the
finder fixes it**: running on the 3x cloud is 7/9, running the old path at 3x is 0/9, the 1x key-scaled lane
works only because it is the answer key. The unit a generated axis would have to arrive in is the tree's
(`3 units = 1 mm`): the finder run on the 3x cloud already answers in tree units and needs no conversion;
a 1x answer would have to be multiplied by 3. Both routes exist; neither is 9/9, and neither is a constant.

**Stage B — the pool offers the key on every piece, in every setting.** `t322/dump_basins.py`, 10 seeds x
1000 Pottmann draws, 10-deg clustering, 60 largest basins refined:

| setting | basin representative within 10 deg of the key | after `refine_axis_normalized` |
|---|---|---|
| 1x geom walls | **9/9**, best basin 0.79-8.68 deg | p1 1.47, p4 4.13, p5 2.66, p6 2.08, p7 5.01 — **only 5/9** |
| 1x corpus cloud | **9/9**, 0.36-8.02 deg | p1 2.19 only — 1/9 |
| 3x cloud | **9/9**, 2.45-8.09 deg | p1 2.23 only — 1/9 |

On all nine pieces the largest basin's representative is already within 10 deg. The refined pool loses them:
refining the key itself under that same cost (`truth_local_deg`) moves it 11.91-51.91 deg on the four hard
pieces. **This is not an input ceiling: the line is in the pool, we destroyed it.** (Claim (3), reference
wrong, closed by 322 — not reopened.)

### Stage C — the per-term attribution (the failing element, with numbers)

Every absolute-millimetre term the ticket lists — the 25 mm clearance floor, the `1000*(25-d_c)^2` penalty
(`normalized.py:183-202`), the `r_prior` knee (`potsac.py:526-533`), `valid_cone`/`valid_dish` — lives on
branches the shipped default **never executes**: it returns at `potsac.py:478-481` when
`UNION_RANKER == "profile"`. On the shipped path the only terms are `profile_cost` (`profile.py:54-56`, k=24
trimmed k-NN width in the (r,z) plane) and the structure of `rank_by_profile` (`select.py:55-76`: sort by
cost, 15-deg dedup, refine only the **8 cheapest** by Nelder-Mead, re-sort, discard everything else).
The replica pool (same constants, own draw — it reproduces the writer's rank-0 for every 1x piece) says:

| piece / setting | rank 0 | the best line that is within 10 deg | why it lost |
|---|---|---|---|
| p2 / 1x geom | 13.16 deg, 2.91 mm, cost 0.0059 | 6.61 deg, raw, pre-refine **rank 64 of 120** | outside the 8 refined → discarded unrefined |
| p3 / 1x geom | 28.39 deg, 3.56 mm, cost 0.0176 | 8.64 deg survives at **order rank 3**, cost 0.0438 = 2.49x | refined, then out-priced |
| p7 / 1x geom | 47.92 deg, 8.22 mm, cost 0.0612 | **2.56 deg survives at order rank 2**, cost 0.0653 = **1.067x** | refined, kept as line 2, written second |
| p7 / 1x corpus | 13.61 deg, 2.63 mm, cost 0.1085 | 3.72 deg, pre-refine rank **79 of 120** | outside the 8 refined → discarded unrefined |
| p9 / 1x corpus | 12.25 deg, 4.82 mm, cost 0.0559 | 8.99 deg at order rank 3, cost 0.0706 = 1.26x | out-priced |
| p3 / 3x | 10.11 deg, 2.45 mm, cost 0.2235 | 6.06 deg at order rank 2, 0.2319 = 1.038x | out-priced, kept as line 2 |
| p9 / 3x | 29.81 deg, 8.50 mm, cost 0.1794 | 2.35 deg, pre-refine rank **100 of 120** | outside the 8 refined → discarded unrefined |

Where the two lines were both refined the deciding gap is **3.8-6.7%** (p7 1x geom, p3 3x, p9 1x corpus
26%), and on p3 1x geom the criterion prefers 28.39 deg to 8.64 deg by **2.5x**. The key itself, refined by the same Nelder-Mead, costs 0.0939/0.0064/0.0425/0.0341/0.0460/0.0498/0.0649/
0.0424/0.0509 (pieces 1..9, 1x geom) against winners of 0.0939/0.0059/0.0176/0.0342/0.0458/0.0492/0.0612/
0.0424/0.0412 — **indistinguishable at the 0.1-2% level while the lines differ by 3-48 deg**. On p2 and on
p9/3x the key, refined, lands 13.14 deg and 7.56 deg away: the cost's own minimum is not at the key.

**Why the term has no resolution here** (`work/probe_cost.py`, job 35236241). The two walls of a Juglet
fragment are **1.44-2.39 mm** apart in the (r,z) plane. At the shipped k=24 the median radius to the 24th
(r,z) neighbour at the key is **0.116-0.223 mm** — the neighbourhood is 7-15x smaller than the wall it is
meant to measure, so it measures the cloud's own sampling noise. The cost at the key grows like a sampled
arc, not like a flat bottom at the wall: 0.0644 (k=12) → 0.1062 (24) → 0.1547 (48) → 0.2010 (96) →
0.2444 (192) → 0.3041 (384), a x4.7 growth for x32 neighbours (`sqrt` scaling). The statistic's resolution
is an absolute point spacing; the signal it is asked to read scales with the piece's own extent — a 75-150 mm
pot fragment gives it 2-3x more lever arm, which is why ticket 322 measured only 1.5 deg of drift on the 172
pot pieces and 6.4 deg here.

For the old path (what fed the seating run) the attribution is different and equally specific: at
`potsac.py:508` a candidate is refined **only if `dcs[j] >= 16.0` or `sizes[j] >= 1500`**. The Juglet's basins
sit at `d_c` 13-15 mm (weighted mean `w_dc` 5.31-11.94 mm), so **no candidate is ever refined** and the
written line is an unrefined 6-point draw; the ranking score is `hcw * sqrt(c) / size^0.45` with
`hcw = _worst_surface_cost`, which carries `+1000*(25-d_c)^2` — on a piece 13-15 mm from the axis that term
is 1.0-1.4 x 10^5 and varies several-fold between candidates, i.e. **the absolute 25 mm floor decides the
Juglet's axis, by distance from the piece, not by agreement with the walls.** Piece 9's 31.84 deg is that.

**Claim: (1) method fails.** Not (2) measurement — the key is right and the clouds are fine; not (3)
reference — closed; not input ceiling — Stage B has the line in the pool on 9/9.

### Stage D — stopped at the diagnosis (per the ticket's own instruction)

No fix was shipped. The reason is in Stage C's numbers, not in a lack of effort: the ranking criterion does
not price truth above its neighbours. It is flat to 0.4-7% across 3-48 deg of angular error; its own minimum
refined from the key lands 6.1-13.1 deg away on the hard pieces; and its resolution (0.12-0.22 mm at k=24)
is an order of magnitude below the feature (1.44-2.39 mm) it must resolve. A constant, a tie-break rule, an
extra pool line or a bigger `refine_k` cannot repair a criterion whose signal is below its own noise — and
every one of them is the "nudge a threshold" the ticket forbids. Making the element dimensionless in the
piece's own size (the ticket's preferred shape) here means: choose k so the neighbourhood spans the wall the
piece actually has, and normalise the residual by the bbox diagonal — that is a different objective, which
would move the 172 pot files, and Stage E's control proves the harness is otherwise byte-exact, so the bar
would have to be re-earned there rather than assumed. Per the ticket: **STOP at the diagnosis rather than
buying the bar with a constant.**

### Stage E — the pots do not move

Job 35236085: the **unchanged** writer over all 172 pieces (`scripts/run_benchmark_172.py --pots ALL`) into
`out/axes_E_control`, then `cmp` every output against `runs/20261110-0740_d628fc0_t323-axes/out/axes323`:
**172 files, 172 same, 0 differ** (13 of them are the Juglet lines). The harness is byte-exact, so the run
above is a proven baseline for whoever picks the objective up. No fix was made, so there is no flipped term
to name — and no threshold was touched.

### Stage F — renders

Nine PNGs, `<run>/out/renders/Juglet_Piece_N.png`, copied into the worktree at `artifacts/pota332/renders/`
(gitignored) and to `C:/PR/artifacts/t332/renders/`:
the piece's own cloud in x-z and y-z, equal aspect, the key in black, our rank-0 line in red, our second line
where the writer wrote one, at a view that resolves the 33 mm vessel. Looked at before writing this section
(p2, p7, p9). **What they show: on p2 and p7 our line is visibly rotated against the key by 13 and 48 deg
while the piece is a few millimetres of wall — the fragment cannot tell the two apart by eye, which is the
criterion's problem in one picture.** The piece sits 10-16 mm off the drawn line, correctly: the axis of a
33 mm vessel passes inside it, not through a sherd.

### Job table (final `sacct` State / ExitCode)

| job | tag | state | exit | elapsed |
|---|---|---|---|---|
| 35235931 | t332a-axes | FAILED | 1:0 | 3s (scipy absent; resubmitted) |
| 35235990 | t332a-axes | FAILED | 1:0 | 1m04s (both passes COMPLETED; scoring step died on import path) |
| 35236020 | t332b-pool | COMPLETED | 0:0 | 2m02s |
| 35236051 | t332a2 | COMPLETED | 0:0 | 10m59s |
| 35236070 | t332c-pool | FAILED | 1:0 | 3s (worker arity bug; resubmitted) |
| 35236112 | t332c-pool | COMPLETED | 0:0 | 5m50s |
| 35236085 | t332e-ctrl | COMPLETED | 0:0 | 9m41s |
| 35236241 | probe | COMPLETED | 0:0 | 13s |
| 35236371 | t332f-render | COMPLETED | 0:0 | 8s (framing bug) |
| 35236427 | t332f-render | COMPLETED | 0:0 | 5s |

Artifacts: scores `out/score_*.txt`, pool dumps `out/basins_*.json` + `out/sel_*.json`, probe
`out/probe_cost.json`, renders `out/renders/`; local copies under `artifacts/t332/`. No assembly run, no
`Dataset/` write, no edit to `AxisExtraction/run_potsac.m`.

### What a conservator should take from this

Our code does not generate the Juglet's axis today — it picks one out of a pool of candidate lines, and the
picking is wrong because the number it picks with is a millimetre width measured over a neighbourhood smaller
than the wall: on a 33 mm vessel it cannot tell a line 2 deg from the key from one 48 deg away (they differ
by 6.7% in cost, and on one piece it prefers the 48-deg line by a factor 2.5). The consequence is physical: the measured
line offset at the piece centroid is 2.91 mm on p2 and 8.22 mm on p7 — the wall of this vessel is 1.4-2.4 mm
thick — so the axis we hand the assembler is displaced by one to four wall thicknesses on a 33 mm vessel.
On the 3x lane the same code is 7/9, not 9/9: the 9-of-9 comes from the scaled answer key, not the finder.

Reading: `juglet-axis-mechanism-named-not-fixed`

**End state:** ready

---

## Verdict (lead, 2026-11-17)

**Reading accepted — `juglet-axis-mechanism-named-not-fixed` — with the claim named: (1) the method fails, and
the measurement that says so is sound. The axis the assembler is fed is not generated by our code, it is drawn
from a pool by a score whose window is smaller than the wall it is supposed to find.**

### What I checked myself

- **The nine-piece table, recomputed from the delivered files** (`out/axes323/Juglet_Piece_N_Axis.xyz` against
  `Dataset/Juglet_GT/`, undirected angle from the first written line, my own code): 0.92, **13.16**, **28.39**,
  3.44, 3.72, 1.84, **47.92**, 3.05, 4.56 deg — piece for piece the worker's row, including which three fail.
  So rank-0 is **6 of 9** on the shipped path, and piece 9 (4.56 deg) is *not* the failure: the 31.84 deg that
  fed the seating run belongs to the old ranker, which the worker also reproduced (4/9, 6/9 best-3, 8/9 best-6).
- **The control that stops this being an artefact of my own run**: `cmp` of the worker's 172-pot output against
  `axes323`, run by me — **172 files, 172 identical, 0 differ, 0 missing**. The pots do not move, so what was
  measured is the Juglet's criterion and nothing else in the writer.
- **The physical mechanism, read off its own dump** (`probe_cost.json`): piece 1's wall is **2.007 mm**, piece 2's
  **2.328 mm**, and the k=24 neighbourhood the cost is computed over has radius **0.116 mm** and **0.175 mm** —
  a window a tenth of the wall it must span. The cost at the key then grows with k like a sampled arc
  (0.0644 at k=12 → 0.3041 at k=384 on piece 1) instead of flattening at the wall, which is what a width
  criterion is supposed to do. On piece 2 our 13-deg-wrong line costs **0.00595** against the key's **0.04594**:
  the criterion prefers it by 7.7x. That is the failure, in its own numbers.
- **The renders, looked at before writing this**: piece 7 shows the red rank-0 line vertical against a black key
  48 deg away, while the blue rank-1 line sits **2.6 deg** from the key — the right answer is in the pool and
  loses; piece 2 shows red 13.2 deg off black. The fragment looks the same either way, which is the point: the
  eye cannot catch this, only the key can.
- **Slurm**, my own `sacct -X`: 35235990 FAILED 1:0; 35236020, 35236051, 35236085, 35236112, 35236241, 35236427
  all COMPLETED 0:0. The one failure is the scoring step the worker names; no arm result depends on it.

### Where I do not repeat the worker's phrasing

The **deg** column is verified by construction. The **mm** column (2.91 on p2, 8.22 on p7) is a local offset
measured at the piece centroid; my own attempt to re-derive it as the distance from the key origin to our line
gives 40-98 mm, a different quantity, because the key's stored origin sits far from the fragment. The mm numbers
therefore stand as the worker's local measure and should be quoted with that word ("at the piece centroid"), not
as a displacement I re-measured.

### What it means

**The 9-of-9 seating was fed the answer key, and this is the size of that loan.** The 3x lane points
`AXIS_DIR` at `Dataset/Juglet_large`, which is the GT axis scaled by three; our own finder on the same 3x
cloud is **7 of 9** at rank 0 (p3 10.11 deg, p9 29.81 deg), on the 1x corpus cloud 7 of 9 (p7 13.61, p9 12.25),
and on the delivered 1x lane 6 of 9. So an end-to-end run on our own axes would be reading the breakline and
the axis error together, at an error of one to four wall thicknesses. **The units are not the cause** (the old
ranker at 3x is 0 of 9, the new one is 7 of 9 with constants untouched; the Regime-1 switch is unreachable on
the shipped path and cannot fire at 3x anyway), and **the pool is not the ceiling** — a representative within
10 deg of the key exists on 9 of 9 pieces in all three settings (0.36-8.68 deg). What throws it away is the
criterion plus the refine-only-the-eight-cheapest cut: the good line sits at pre-refine cost rank 64-100 of 120
on p2, p7 and p9/3x and is discarded before the refiner ever sees it.

**Nothing shipped, and that is the right end state for a diagnosis ticket.** `Dataset/` untouched, no threshold
moved, the 172-pot corpus byte-identical. The fix this names — a cost whose window scales with the wall it is
measuring (or that spans the two walls rather than one sampling neighbourhood), and a refinement cut that does
not pre-discard the interior of the pool — is not built, and on this evidence it should be a ticket of its own,
with the bar set on the delivered line (rank-0 within 10 deg on 9 of 9) and the 172-pot `cmp` as its
non-regression gate. Until then every Juglet assembly number carries the axis loan in it.
