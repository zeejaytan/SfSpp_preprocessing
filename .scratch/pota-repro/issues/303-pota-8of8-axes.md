# 303: Why corrected Pot A axes seat 7/8 — diagnose, then a blind fix that seats 8/8

**What to build:** with the ticket-302 axis chain (MATLAB-faithful per-point cost), Pot A assembles 8/8 pieces and 15/15 joins from the released axis files but only 7/8 and 13/15 from our own. Find which piece and which axis line cause the loss, trace it to the paper or code, and change the axis chain so that **our own axes, chosen without looking at the released files, seat Pot A 8/8 and 15/15**, and do so repeatably.

**Answers:** E1

**Blocked by:** 302 (landed 2026-11-04, merge 3d55af5)

**Status:** landed (lead 2026-11-04) — diagnosis complete, **no blind fix exists**; Pot A Piece 08 needs a reference axis line our estimator never proposes (closest approach 20.73 deg over 100 candidates). Follow-up: ticket 304.
**Working in:** chat on Thinkbook16 (2026-11-04)
**Branch:** 303-pota-8of8-axes, in /c/PR/worktrees/sfs/303

**Worker:** sfs303

**Budget:** large 8

**Hand-over:** Claude — needs Spartan assembler runs (apptainer SIF), the corpus, and judgement about whether a seat change sits outside run-to-run spread; one session runs the chain.

## What the lead already established (2026-11-04, read from run 20261103-1620_01bff01_t302-e2e; re-check, do not take on trust)

- Control GPA50 (released axes): 8/8, 15/15; 124 matches, 70 after pruning. Treatment GPA50N (our `out/axes302` axes): 7/8, 13/15; 118 matches, 59 after pruning. All 8 OBJs are written in both arms, so in GPA50N one piece is **placed wrong**, not dropped. Which piece has not been identified yet: read `out/GPA50N/T_*to_*.txt` against GT.
- **The assembler uses axis lines in two ways.** Matching loops over every line pair (`sfs_main/sfspreproc-docker/class/feature_matching.cpp:1461-1475`, `axis_x`/`axis_y`; the chosen pair's angle is used at :1665-1668). Root alignment to z and reconstruction read **line 0 only** (`class/ranking_system.cpp:957-958, 1033-1034, 1727-1731`; `class/reconstruction.cpp:156-157`).
- **Our line order differs from the released files on the two suspect pieces** (angle of each of our lines to released line 1): P06 = [24.36°, **2.38°**] (released file has one line); P08 = [35.91°, 16.02°, **7.74°**] (released has two). On P01 our single line is 0.8° from released. Per-seed angle to released (pota302.tsv): P6 24.4 every seed; P8 35.9 on 7/10 seeds and 16.0 on 3/10; P1-P5 0.6-3.2; P7 6.3.
- **How the order is set:** `run_potsac.m:39-45` computes the Huber cost on the 10% subsample after stage-1 refine; stage-2 refine on all points (:66-68) moves the axes, and the final sort (:82) reuses the **stale stage-1 cost**. The port copies this faithfully (`sfs_axes/potsac.py:116-125`). The paper (`papers/text/sfspp-2502.13986v1.md:175`) says all surface points are used for detailed refinement after pruning and the higher-cost axis is pruned; it does not say the cost is recomputed. A candidate deviation, not a proven one. Also open: `extract_axis_nurbs.m` / `read_surfaces_nurbs.m` suggest the released axes may come from NURBS surfaces, not the shipped Surface xyz (ticket 302's residual (a)).
- **Weight warning:** E1 records the released-axis control itself at 6/8 and 7/8 in other runs (density-restore run, "±2 mm wobble"). One 7/8 may be noise. Nothing below is a result until it is shown outside the replay spread.

## Stages

**A — Is 7/8 real?** Replay GPA50 and GPA50N, staged inputs byte-identical (md5 logged), at least **5 replays each** in one job. Report sherd/join counts per replay. If GPA50N reaches 8/8 in some replays and GPA50 drops in some, say so and give best-of-N plus counts (best-of-N rule, AGENTS.md).

**B — Which piece, which line.** Per replay, identify the misplaced piece(s) (T files vs GT: rotation deg, translation mm). Read the assembler logs for which axis-line pair the winning matches on that piece used (add logging in a shim copy only if needed; never edit the SIF or sfs_main).

**C — Single-variable arms** (only Axes/ differs from GPA50N; diff -rq proves it, as in 302's e2e script). All axes from `out/axes302`:
- **C1 oracle reorder** (diagnostic only, never shippable): put the line nearest the released line 1 first on every piece.
- **C2 first line only:** truncate every file to its first line.
- **C3 recompute cost after stage-2:** rank the survivors by the Huber cost on all points after the final refine (the candidate code-vs-paper fix). Runs with the port; the lead wants this one.
- **C4 (only if C1-C3 do not explain it):** NURBS-input axes via the authors' extract_axis_nurbs path, to test the provenance hypothesis.
Replay each arm at least 3 times.

**D — The fix.** Make the smallest **blind** change to `sfs_axes` that seats 8/8 and 15/15: it may use only the piece's own surfaces, never the released axes or GT. If it departs from `run_potsac.m`, cite the paper line that licenses it, and add a switch so the MATLAB-faithful behaviour can still be reproduced. Re-run the 302 MATLAB unit/regression checks wherever the change touches the code they cover. Then re-run the corpus axes (163 pieces, new paths, corpus md5 unchanged) and a Juglet E2E arm for collateral damage.

## Rules

Read `SfSpp_preprocessing/AGENTS.md` first (corpus caveats; runs layout; staging by symlink; unseeded mesh stage). Open the branch with `C:/PR/scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/303-pota-8of8-axes.md` (Status must still read ready-for-agent when you run it). **SSH from the laptop: use `/c/Windows/System32/OpenSSH/ssh.exe spartan`** — git-bash's `/usr/bin/ssh` cannot use the key ("Permission denied (publickey)"). Runs live under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with run.json and an index.tsv row (verdict columns empty). Start from 302's `.scratch/pota-repro/302-stage/submit302_e2e.sbatch` (guarded shim, arm67.sh, apptainer). Poll every sbatch with `sacct -j <id> --format=State,ExitCode` and record it. Released axes and GT may be read **only to score and diagnose**; the shipped selection rule must never read them. No corpus file changes. Renders: Pot A reassembly top+side for the best GPA50N-type arm before and after the fix, plus the misplaced piece (images go to `artifacts/pota303/`; the lead and conservator eye-check them). Comments-only ticket edits (`## Comments (worker, <date>)`); checkboxes and Status stay with the lead. Commit nothing.

- [x] A: replay spread for GPA50 and GPA50N (≥5 each), counts per replay, best-of-N — 5/5 each, 8/8 15/15 vs 7/8 13/15, deterministic (job 34328989)
- [x] B: misplaced piece(s) named with rotation/translation error and the axis-line pair used — Pot A Piece 08, 167.08 deg / 379.5 mm, **never joined at all** (singleton subgraph); 8/8 arm joins it to Piece 2 line 0 at axis angle 12.86 deg
- [x] C: arms C1-C3 ≥3 replays each, axes-only diffs proven — C1 7/8, C2 6/8 (worse), C2b 7/8, C3 7/8, paper-dedup 7/8, no-35.9-line 7/8, patch-gap 7/8. C4 not run: C1-C3 plus the perturbation ladder explain the loss, and C4 as written does not test a different input (see lead comment)
- [ ] D: blind fix in sfs_axes behind a switch, paper line cited; 8/8 and 15/15 — **NOT MET, and the checkbox stays unticked.** No blind change seats Piece 08. The only arms that reach 8/8 use the released file (one-hot, or our lines plus the released second line: job 34336399 miss_r1/miss_r2/pair_r1). Reported honestly rather than met by a fitted rule.
- [x] D: 302 checks and collateral — identity: default output byte-identical to pristine `78dc9ee` (8/8 Pot A files); corpus 163/163 axis files byte-identical, input md5 unchanged (job 34335728); Juglet 9/9 differ by 0.000e+00 (one line each, unreachable by a reorder)
- [x] Renders staged (4 PNGs, artifacts/pota303); 13 job IDs and their sacct states recorded
- [x] Branch merged and pushed by lead, worktree removed, branch deleted (lead)

## Comments (worker, 2026-11-04)

### A — the 7/8 is real and does not move between replays

Run `20261104-1606_78dc9ee_t303-pota-axes-r2` (job 34328989, COMPLETED, every arm rc=0), 22 arms in one job, staged trees byte-identical (md5s in the run's `logs/`). Each arm ~100-190 s, 8 cpus.

| arm | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|
| GPA50 (released axes) | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 |
| GPA50N (`out/axes302`) | 7/8 13/15 | 7/8 13/15 | 7/8 13/15 | 7/8 13/15 | 7/8 13/15 |

Both sides are deterministic, so no best-of-N is needed: **7/8 13/15 is a property of these axis files, not of the run.** The assembler's one random path (`ComputePotSACAxis`) is never called from `main_pristine_batch.cpp`, and `RefineAxis` is pinned single-threaded (`class/axis_estimation.cpp:250`).

### B — the misplaced piece is Pot A Piece 08, and it is never joined at all

Scored every arm's `out/<arm>/T_<k>to_<k>.txt` against `Ground Truth/Pot_A_Piece_<k+1>_T.txt` with the counter's own bar, 20.05° and 50 mm (`class/data_structure.cpp:966`, 0.35 rad / 50.0). The method reproduces the lead's table to the digit.

- GPA50N: Piece 08 **167.08° / 379.5 mm**; the other seven 0.68-2.78° / 10.5-17.1 mm.
- GPA50: Piece 08 1.64° / 12.8 mm.

The shim dumps (`work/logs/binary_<arm>.log`, the instrumented main in `work/shim/GA.cpp`) show the mechanism, and it is not a mis-join:

- failing arm: state 0 has **two** subgraphs — graph 0 root 1 (score 720) and graph 1 root 8 with **zero edges**. Piece 08 is a singleton, so it sits at whatever its own root alignment gives, and that is the 167° flip.
- 8/8 arm: one graph (root 2, score 790, nodes 1-8, 13 edges) and Piece 08 attaches by `fix 2 mov 8 ax_f 0 ax_m 0 ang 0.224432 score 0.397769` — Piece 2 line 0 against Piece 8 line 0, inlier 37, overlap area 15.5. In the failing arm the same pair only reaches inlier 18, area 2.

So the question is not "which wrong line won the match" — Piece 08 fails to win any match at all.

### C — the arms, and what they rule out

All arms change `Axes/` only (a `diff -rq` guard refuses anything else), 3 replays each:

| arm | result |
|---|---|
| C1 oracle reorder (nearest released line first) | 7/8 13/15 ×3 |
| C2 first line only, every piece | **6/8 10/15** ×3 (worse) |
| C2b Piece 08 truncated to our line 2 alone | 7/8 13/15 ×3 |
| C3 recompute the Huber cost after stage-2 (`SFS_AXES_POST_REFINE_COST`) | 7/8 13/15 ×3 |
| paper's dedup only (drop the `cost < cost[0]*1.1` cut) | 7/8 13/15 ×2, Piece 08 file **byte-identical** to `axes302` |
| Piece 08 without its 35.9° line (keep lines 0-1) | 7/8 13/15 ×2 |
| patch-contiguity reorder (`SFS_AXES_PATCH_GAP`, good line first) | 7/8 13/15 ×2 |

C4 (NURBS input) was not run: C1-C3 plus the extra arms below explain the loss, and the ticket makes C4 conditional.

**Why no re-ranking can fix it.** The estimator is internally consistent, so the ranking is a symptom:

- Four different blind costs over Piece 08's survivors — stale stage-1, all points after stage 2, each face alone, worst of the two faces — all put the **same** candidate first, and it is the 35.9° one; all four also leave every other piece's line 0 unchanged. The wrong axis really does fit the patch better (cost 23822 vs 25062 for the good one).
- A spherical mean over the seed sweep reproduces the shipped line to three decimals; refining again (tighter tolerance, more iterations, alternating faces) does not move it, and the inlier-only variant is worse (11.5° vs 10.8° from the true pot axis).
- The good axis **is** in the pool — it is the seven-degree candidate — and it carries the **highest** cost of the three survivors, so the stale-cost sort puts it last.
- Three independent ways of putting it first (C1, C2b, patch-contiguity) all still leave the pot at 7/8.

### What does move it — and what that proves

- **One-hot:** Piece 08's file replaced by the released one, the other seven still ours → **8/8 15/15**, twice. Piece 08's own axis set is the whole lever.
- Perturbation ladder on Piece 08 alone: 2 mm point shifts in any direction 7/8; direction −2° 7/8; **direction +2° 8/8**, three replays, and both sides of that boundary are deterministic. In the ground-truth frame our good line is 10.78° from the pot axis, the +2° nudge 9.06°, the −2° nudge 12.58° — but the released line 0 is 18.13° from the same truth and seats, so "closer to the true axis" is not the rule either.
- **The decisive arms (diagnostic only, use the released file, never shippable):** run `20261104-2010_78dc9ee_t303-missing-axis`, job 34336399, all rc=0.
  - our own three Piece 08 lines **plus the released file's second line** → **8/8 15/15**, twice (miss_r1 319 s, miss_r2 246 s);
  - our **one good line alone plus that second line** → **8/8 15/15** (pair_r1 241 s). So our good line is not poisoned and the three-line set is not the issue: what decides the join is that the piece carries an axis near the pot's true axis *and* a second one that only the reference has.

That last one is the mechanism: **the reference carries a second axis on Piece 08 that our estimator never proposes from the same surfaces.** Dumping the ten pre-prune candidates of Piece 08 over ten seeds — 100 candidate axes — the closest any of them gets to that reference line is **20.73°** (probe `pool10.py`; the closest to the reference's *first* line is 4.07°). So no seed, no sampling stride, no re-ranking, no cost repair and no refinement can recover it.

### D — the outcome, stated plainly

**No blind change in this ticket seats Pot A 8/8.** Every variant confined to the piece's own surfaces that could be justified from the paper — reorder, cost repair, dedup, refinement, truncation, patch contiguity — leaves 7/8 13/15. The one thing that works (a +2° nudge of one line) is an arbitrary direction, not a rule, and nothing in the piece's own surface tells you which way to nudge.

Which of the three claims this is: **not** "the method failed" and **not** "the measurement was broken". Every arm is a clean single-variable comparison, both controls are stable, and our own line 0 on Piece 08 is 7.1-7.6° from the reference's first line across all seeds. It is a **reference/input** difference: the released Piece 08 axis file carries an axis that our estimator cannot produce from the shipped `Surfaces/*.xyz`. That is consistent with ticket 302's residual (a) — `extract_axis_nurbs.m` / `read_surfaces_nurbs.m` in the authors' release suggest the released axes were fitted to NURBS surfaces, not to the point clouds we ship. **C4 is the experiment that would settle it**, and it is the one I did not run.

The switch `SFS_AXES_PATCH_GAP` is left in `sfs_axes/potsac.py` **at its default OFF**. It is blind, it is paper-consistent (top-10 candidates, prune by the 10° rule), and its collateral is measured: of 163 corpus pieces, 156 carry a single line and cannot be touched, and the other 7 (Pot A 08, Pot B 09, Pot D 24/27/30, Pot J 01/08) are pure permutations — worst direction change 0.000000°, worst perpendicular offset 0.000000 mm (run `20261104-2008_78dc9ee_t303-blast`, job 34336350, estimator run twice per piece, switch OFF then ON). It does **not** seat Pot A, so it is not offered as the fix; the lead may drop it.

### Closing checks

- **Identity:** the edited package at its default and the pristine `78dc9ee` package (`git archive 78dc9ee sfs_axes`) produce **byte-identical** Pot A axis sets, 8 of 8 files. The switch is a strict no-op at the default.
- **Corpus:** 163 of 163 axis files byte-identical to the ticket-302 corpus set, input corpus md5 before == after (`b1275e9853ac1b86d007ec1661429feb`). Run `20261104-1939_78dc9ee_t303-final`, job 34335728 COMPLETED. (My first reading of that job reported "0 files produced" — that was a path bug in the job's comparison loop, the files were in `out/corpus_new/axes302/`.)
- **Juglet:** all nine juglet pieces carry one axis line, so a reorder cannot reach them; regenerated with the switch OFF and ON, all nine files differ by 0.000e+00 and the gate numbers are identical (median 12.35°, worst 52.24-55.61°, reference t68 hybrid 12.31). The Juglet **E2E** arm cannot serve as this control: it scores 0/9 0/18 with both axis sets (ticket 302's F20O and F20N are both 0/9).
- **302 MATLAB checks:** not run as such — with the switch OFF the Python is byte-identical in output to the pristine package, which is stronger than a regression check. With the switch ON the estimator's candidate *values* are unchanged too (pure permutation, see the blast-radius run), so the MATLAB comparison still holds line for line.

### A defect found in a ticket-302 instrument (not in the package)

While checking identity I found that `corpus302.py`'s `canonicalize()` negates the whole six-vector when the direction's z is negative:

```python
def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt = -vt
```

The stored position is the foot point of the line, so negating it reflects the line to the other side of the piece's own frame origin. On Pot A this moves Piece 07's line **712.5 mm sideways** (direction identical to 1e-12); seven of eight Pot A pieces are unaffected because their line passes ~0 mm from the piece origin. Direction-based numbers, including the corpus gate's headline angle, are unaffected; anything using the stored position is not. The shipped package does not canonicalise (`cli.py` -> `write_axes`), so nothing in `sfs_axes` is affected — but the ticket-302 corpus set carries it. Suggest a follow-up rather than a change inside this ticket.

### Runs and renders

Runs (all under `/data/gpfs/projects/punim2657/SfSpp/runs/`): `20261104-1606_78dc9ee_t303-pota-axes-r2` 34328989; `...1753_..._t303-pert-p8-r2` 34333318; `...1813_..._t303-replay-basin2` 34334178; `...1812_..._t303-refine-variants` 34333691; `...1814_..._t303-seed-mean` 34333773; `...1822_..._t303-paper-dedup` 34334153; `...1859_..._t303-patch-gap2` 34334984; `...1926_..._t303-onehot2` 34335444; `...1939_..._t303-final` 34335728; `...1950_..._t303-renders5` 34335951; `...2002_..._t303-jug-axes2` 34336240; `...2008_..._t303-blast` 34336350; `...2010_..._t303-missing-axis` 34336399.

Renders in `C:/PR/SfSpp_preprocessing/artifacts/pota303/`: `assembly_before_top_side.png` (7/8 — the red Piece 08 lies flat across the middle of the pot's mouth) and `assembly_after_top_side.png` (8/8 — the same piece out at the rim, wall-aligned, filling a gap in the cloud), plus `p8_axes_top.png` and `p8_axes_side.png`, which draw our three candidate lines and the two released lines in separate colours over Piece 08's 3337-point patch. The OBJ files the assembler writes are the capture-frame poses every arm shares, so the pictures are drawn from `out/<arm>/T_<k>to_<k>.txt` applied to each piece's own surface cloud.

Worktree state: `C:/PR/worktrees/sfs/303` on branch `303-pota-8of8-axes`, HEAD `78dc9ee`, uncommitted: `sfs_axes/potsac.py` (the switch) and the `Worker:` line of this ticket. Nothing committed.

### What I could not do

- C4 (NURBS-input axes). It is the experiment the evidence now points at.
- No blind fix, because I found none that is a rule rather than a coincidence.

## Comments (lead, 2026-11-04 — landing and independent verification)

**Verified by the lead, not taken on trust.** Re-read every arm's `1. Acc.txt` on Spartan: job 34328989 → GPA50_r1..r5 all "Sherd accuracy : 8 / 8 (100 %)" + "15 / 15 (100 %)", GPA50N_r1..r5 all 7/8 13/15, C1_r1..r3 and C2b_r1..r3 and C3_r1..r3 all 7/8, C2_r1..r3 all 6/8 10/15; job 34336399 → miss_r1, miss_r2, pair_r1 all 8/8 15/15. Re-scored the per-piece transforms against `Ground Truth` with the counter's own 0.35 rad / 50 mm bar (`class/data_structure.cpp:966`): Piece 08 167.08 deg / 379.5 mm in GPA50N and 1.64 deg / 12.8 mm in GPA50, every other piece within 0.4 deg / 2 mm of the control. Verified the `canonicalize` arithmetic: our Piece 07 line 0 anchor is (-6.2, 12.7, -356.0), |p| = 356.3 mm, so `vt = -vt` moves it 2|p| = 712.6 mm — the reported 712.5 mm. Verified the package does not canonicalise (`sfs_axes/io_axes.py:21-29` `write_axes` only reorders to position-first and formats).

**A corpus-wide fact the lead measured here, which changes how the P8 result should be read.** Of the 163 released `Axes/*_Axis.xyz` files, 129 carry one line, 19 carry two, 11 carry three, 1 four, 2 five and 1 six — **34 of 163 (21%) are multi-line**. Ours: 135 one, 15 two, 11 three, 2 four. So a reference file carrying an axis our estimator does not propose is not a Pot A oddity; whether it costs a seat on other pots is untested and is the reason for the follow-up rather than a shrug.

**Correction to a premise in this ticket, made at landing.** `AxisExtraction/read_surfaces_nurbs.m` does **not** read a different dataset: it `readmatrix`s `Dataset/SfS_pp/Surfaces/Pot_*_Piece_*_Surface_{0,1}.xyz` — the same six-column files this pipeline reads — and calls the same `run_potsac`. So "C4 (NURBS input)" would not have tested a different input, and the missing axis is not explained by a NURBS-vs-cloud difference on that reading. The remaining explanation is that the released file was produced from *different surfaces* than the ones shipped, or by a *different estimator* than the one in this repo. Those two separate cleanly: run the authors' own MATLAB `run_potsac` on Piece 08's shipped `Surfaces/*.xyz`. If it produces the missing line, the gap is a divergence in our port and is fixable — which is exactly what the conservator asked for. If it does not, the reference file was not made from these surfaces.

**Decisions.**
1. Both switches stay in `sfs_axes/potsac.py`, default OFF, and each now carries a MEASURED line stating that it does not seat Piece 08, so neither can be mistaken for a fix (the ticket-302 lesson: a false docstring cost a whole ticket).
2. Checkbox D is **not** ticked. Nothing blind seats 8/8, and a fitted +2 deg nudge is a coincidence, not a rule.
3. `canonicalize()` in the three 302-stage instruments (`corpus302.py:30`, `gen302_unit_inputs.py:22`, `pota302.py:28`) is fixed in a separate commit, and ticket 302 records that the `out/axes302` files carry the reflected anchor on pieces whose line runs far from the origin. Direction numbers stand; position numbers from those files do not.
4. Follow-up ticket 304: MATLAB-vs-port on Piece 08, then (only if MATLAB reproduces the line) the port divergence.

**Renders** (4 PNGs in `artifacts/pota303/`) await the conservator's eye — the lead cannot view images in this session (model has no image input).
