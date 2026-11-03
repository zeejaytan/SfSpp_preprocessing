# 67 — Juglet edgelines in the assembler: scaled floor, crash guard, and a real reassembly

**What to build:** the Juglet (9 pieces) assembled by SfS++ from our current edgelines, with
the assembler made safe for it: (1) an honest replacement for the 50-dot floor that admits
short Juglet breaks without admitting noise, (2) the empty-candidate SIGSEGV fixed so no arm
dies before scoring, (3) a measured attack on the wrong-attitude poses t58 exposed (I60:
pieces near-touching but 138-163 deg from the correct relative orientation), and (4) rendered
assemblies scored against the Juglet GT. Continues ticket 58 (resolved, cure undecided) under
the conservator's order of 2026-11-03: "we need juglet edgeline to work in assembler as other
pots, and get juglet reassembled".

**Why now (2026-11-03, conservator):** "it throw away the edgeline less than 50 points which
is most of juglet edgelines. this is continue the investigation for ticket 58".

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** none (t66 merged d1d0123 supplies the lanes; t58's run of record is read-only)

**Status:** ready-for-human (floor not binding; axis files 2/5/9 vs GT is the open input question; crash guard proven)
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 67-juglet-assembly-scaled-floor, in /c/PR/worktrees/sfs/67
**Worker:** (unset)

## Spec

### Given (measured facts this stands on)

- The gate: `structure-from-sherds-pp/main.cpp:86-90` and its batch twin
  `hpc/tools/main_pristine_batch.cpp:86` drop any piece whose Bl0 lane has < 50 dots.
  The paper states 50 only as a corpus-exclusion rule for pot-scale breaks
  (`papers/text/sfspp-2502.13986v1.md:329`); it removes 8 of 9 pieces of pot J, the same
  8 of 9 it removes from ours. The floor is length-bound: at the paper's d = 1.9 mm a
  43 mm break cannot hold 50 dots (t58 Table 3).
- Current lanes (t66 arm U, the merged recipe: worness 0.7 + radius 1.0 + admit-sign on):
  Bl0 dots J1..J9 = 59/32/44/31/43/45/54/40/22. Only J1 (59) and J7 (54) clear 50.
  Better preprocessing does NOT clear the floor -- loop length does (43-100 mm).
- t58 findings (run of record `runs/20261101-1913_d8f716f_t58-floor-density-panel`):
  - floor 10: all 9 active, 21 LCS candidates, one non-GT merge (2,4), 0 seated, exit 0.
  - floor 45/50: 1-3 active, 0 candidates, SIGSEGV 139 at
    `class/ranking_system.cpp:727` (`ext_state_[0]` on an empty vector; ext_state_ only
    appended at :720 when a non-empty graph exists).
  - I60 (old lanes resampled to 60 dots, floor 50): 63 candidates, 7 pieces saved, but
    0 seated -- chamfers 458-475 mm; three GT pairs physically near-touching (5.9-11.0 mm,
    14-21 contact points) while facing 138-163 deg away. A MATCHING/attitude failure,
    not a seating failure.
  - Pot A control at floor 10: 8/8 seated, 15/15 joins -- the floor edit alone is inert
    on a working corpus.
  - `MINIMUM_NUMBER 6` (LCS window) is NOT binding on these lanes (min 22 dots).
  - A second hidden floor: `reconstruction.cpp:72` `if (numberOfPoints < 10) return;` in
    AxisAlignment returns WITHOUT setting R_out/t_out -- not fired yet (min 22), but a
    short-lane arm must watch it.
  - LCS matcher needed ~45+ honest inliers on Pot A short lanes (ticket 45 lesson).
- Staging recipe that worked in t58 (reuse it): Breaklines/ = Bl0 lanes; Surfaces/ = S0/S1
  converted to bare 6-number .xyz (`class/data_structure.cpp:781-843` cannot parse PLY
  headers); Mesh/Axes/Ground Truth from `Dataset/{Mesh/Juglet, Axes/Juglet, Juglet_GT}`;
  Pot A bundle hardlinked. Seating bar: chamfer < 7.07% of the 65 mm reference = 4.596 mm;
  strict edge bar 5 deg / 10 mm.

### Task

1. **Crash guard (code, built in the run area, merge proposal at close).** In the batch
   shim (`hpc/tools/main_pristine_batch.cpp` path), guard the empty-candidate case at
   `ranking_system.cpp:727` (and any sibling `[0]` on `ext_state_`): when no candidate
   pairs exist, print a one-line "no candidates" result and exit 0 with empty outputs,
   instead of SIGSEGV. Record binary md5 + the diff. The canonical
   `structure-from-sherds-pp` sources stay untouched during the run; if the guard proves,
   the lead decides the merge as a separate commit.
2. **Scaled-floor experiment.** Arms (same binary family as t58, one sed-style literal
   change each, md5 + diff recorded): F20 (floor 20: all 9 t66 lanes active), F30, and
   SCL (a scale-aware floor = 50 x Juglet/PotA reference extent = 50 x 65/194 ~ 17, use 17).
   Lanes = the t66 arm-U Bl0 lanes (current merged recipe). Also rerun F50 (shipped) as the
   baseline-with-guard (expect "no candidates", exit 0 now).
3. **Attitude attack.** Whichever arm shows the most graph growth: instrument per GT-adjacent
   pair the LCS candidate list (pair, LCS length, inliers if extractable) and the relative
   pose the matcher proposes vs the GT relative pose (rotation error deg, translation mm).
   Name where the attitude error enters (candidate scoring? pruning? StateManager merge?
   axis alignment?). Do NOT tune by trial -- locate the stage, measure it, report.
4. **Control.** Pot A on the same guard binary at the shipped floor 50: must reproduce
   8/8 and 15/15.
5. **Write `## Results`**: arm x piece x seated/chamfer table, GT-edge pass table, attitude
   table, renders (workspace-relative under `SfSpp_preprocessing/artifacts/67/`), best-of-N
   stated (assembly path carries no RNG, so N=1 per arm -- say so), every sbatch polled and
   sacct recorded.

### Acceptance

- Every claim carries file:line or a measured number from a named run dir.
- Experimental binaries: md5 + diff recorded; canonical assembler untouched during the run.
- Renders for every seating claim; the Juglet assembly however it comes out -- a negative
  result with located cause is acceptable, a silent one is not.
- Budget: <= 5 Slurm jobs, <= 24 h wall.
- Worker measures; the lead verifies and merges; the conservator judges the assembly.

**Edges:** t58 run of record read-only; t66 run read-only; shares the Dataset/ trees
read-only.

## Results

Worker measurements, not yet verified by the lead. Run of record:
`/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly` (`run.json`,
`submit.sbatch` = job 1, `submit_b.sbatch` = job 2, `instruments/`, `logs/`, `out/`, `score/`, `trees/stage_manifest.txt`).
Harvest: `SfSpp_preprocessing/artifacts/67/` (`harvest_t67.tar.gz` md5 `69c6577413a9c3c8ebd4a6978bdae801`, extracted beside it).
Scripts: `.scratch/juglet-breaklines/stage67/` on this branch; resume notes in its `STATUS.md`.

**Headline.** The Juglet still does not go back together: 0 of 9 pieces seated in every arm. **The floor was not
the binding constraint.** At floors 30, 20 and 17 every piece that clears the floor is matched, and the outcome is
byte-identical across the three: one join, pieces (2,6), which is not a ground-truth join. The crash is fixed: at
the shipped floor of 50 the guarded batch exits 0 with `T67-NO-CANDIDATES` where t58 crashed with SIGSEGV 139.
The located cause has two parts.
(a) For 9 of the 18 true joins the matcher never proposes the pair at all. Every one of those 9 involves piece 2, 5
or 9, and for every true join involving those pieces the released axis files disagree with the ground-truth pose
by 46-86° (folded). So either those axis files or the Juglet ground truth is wrong for 2, 5 and 9. This run cannot
say which (claim 3, the reference is wrong, is open).
(b) For the other 9 true joins the matcher does propose the pair, but from 6-11-dot matched runs (Pot A: up to 35).
The ICP fitted to those short runs puts the two pieces at least 59.6° from the true relative orientation (median
of the best per pair: 116°). The pruning axis gate then rejects them (claim 1, the method fails on short breaks).

### Slurm

| job | what | sacct State / ExitCode | elapsed | MaxRSS |
|---|---|---|---|---|
| 34264796 | job 1: guard + floors F50G/F30/F20/SCL17 + Pot A control PACTL | COMPLETED 0:0 | 00:03:50 | 6873484K |
| 34265479 | job 2: attitude instrument, A20 (Juglet floor 20) + APA (Pot A floor 50) | COMPLETED 0:0 | 00:04:38 | 1345060K |

Both were polled with `scripts/slurm_poll.sh` from Git Bash over OpenSSH. The poller hung after two polls on job 1
(a stuck ssh) and was stopped; both final states were read with `sacct -j <id> -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS`.
Budget used: 2 of 5 jobs, 8m28s of 24 h.

**Best-of-N.** The assembly path has no RNG, so every arm is N=1. Supporting evidence: F30, F20, SCL17 and the
instrumented A20 write byte-identical `T_1to_1.txt` (md5 prefix `f0f8a0e7d0da`) and `T_5to_5.txt` (`5b710150e052`).

### Binaries (experimental, never merged; built in `$RUN/work/`)

The shipped shim `sfs_main/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp` is `fb26e8ab49e9c00f7e8d02de44f6eea5`.
The guarded base `work/shim/G.cpp` is `056dfb914d7f067244a87d200ecb9863`. Its diff is `logs/diff_guard.txt`: two
4-line inserts. The first, after `cout << "Total number pruned : "` (shipped :216), handles an empty pruned list:
it prints `T67-NO-CANDIDATES` and returns 0 before `StateManager` is constructed, whose `Initialize` reads
`ext_state_[0]` at `class/ranking_system.cpp:727`. The second, after `manager.BuildStep();` (:222), handles an empty
`out_state_`. The guard does not cover a non-empty list whose root graph is still empty; that would still reach
:727, and it did not occur here. The instrumented base `work/shim/GA.cpp` is `bc2f2aed832e8513c32970e4cc664c07`
(`logs/diff_attitude.txt`). Each arm seds only the floor literal (`logs/diff_<ARM>.txt`).

| arm | floor | source md5 | binary md5 | exit | candidates / after pruning | own Acc.txt |
|---|---|---|---|---|---|---|
| F50G | 50 | `056dfb91...` (G) | `5a5d83b325c41ab6131af3fa3483ce6f` | 0 | 1 / 0, `T67-NO-CANDIDATES` | none |
| F30 | 30 | `cd650478935cc1d1f2845c03d453a5f1` | `dccb00289b979a5a5615e277b6e1d9da` | 0 | 23 / 1 | 0/8, 0/13 |
| F20 | 20 | `90b5091bd4e191e411c618e50b10de14` | `320aa5a073cbe2c05c93ea426a78b90e` | 0 | 23 / 1 | 0/9, 0/18 |
| SCL17 | 17 | `a48ab78fe270b8f225ff039833ee504a` | `7eb92f2406d0c9abf0c46e00a832ba2f` | 0 | 23 / 1 | 0/9, 0/18 |
| PACTL | 50, Pot A | `056dfb91...` (G) | `d4323adc90a9a181eaf2cb54620822dc` | 0 | 124 / 70 | **8/8, 15/15** |
| A20 | 20, instrumented | GA + floor 20 | `53586a992d1a68d3f04dcdeef27ca633` | 0 | 23 / 1 | 0/9, 0/18 |
| APA | 50, Pot A, instrumented | `bc2f2aed...` (GA) | `bc67e19fafa491dbb29f22ea7827c2be` | 0 | 124 / 70 | 8/8, 15/15 |

At floor 50 only J1 (59 dots) and J7 (54) are active; at 30, J9 (22) drops out; at 20 and 17 all 9 are in (the
shortest lane is 22). Staging was t58's recipe on the t66 arm-U lanes (`trees/stage_manifest.txt`; e.g. J9 Bl0 md5
`cbaadf7d86c81c1cd1c783e28a171fe3`, 22 dots). Pot A was hardlinked (link count 3). The staged Juglet meshes are
byte-identical to t58's harvested meshes (9/9 md5 match).

### Seating (arm x piece; scorer `score58.py`, bar 7.07% of 65 mm = 4.596 mm)

| arm | pieces with a saved T | piece: chamfer mm | seated | GT edges passing (5°/10 mm) |
|---|---|---|---|---|
| F50G | none | — | 0/2 active | none testable (active set {1,7}; GT(1,7) = 0, so its denominator is 0) |
| F30 / F20 / SCL17 / A20 | 2, 6 | 2: 19.69; 6: 21.52 | 0 | 0 (their only join, (2,6), is not a GT edge: `Juglet_simple_graph.txt` row 2 = `1 0 0 0 1 0 0 0 1`) |
| PACTL / APA (control) | 1-8 | (t58 PA10 0.96-2.36) | own Acc.txt 8/8 | own Acc.txt 15/15 |

The `score58.py` JSON prints 36 directed / 18 undirected for every arm. That is right only for all-9 arms; the
correct denominators are F50G 0 / 0 and F30 26 / 13 (8 active; matches its Acc.txt 0/13).

Renders, for the eye check:
[F20_assembly.png](SfSpp_preprocessing/artifacts/67/render/F20_assembly.png),
[F20_perpiece.png](SfSpp_preprocessing/artifacts/67/render/F20_perpiece.png): pieces 2 and 6 sit 20 mm away from
home and turned to a different attitude (piece 2's arc stands upright where the reference lies flat). The F30,
SCL17 and A20 transforms are identical, so one render covers all four.
[PACTL_assembly.png](SfSpp_preprocessing/artifacts/67/render/PACTL_assembly.png),
[PACTL_perpiece.png](SfSpp_preprocessing/artifacts/67/render/PACTL_perpiece.png): the assembler result and the
reference panels match.

### Attitude attack: per GT pair (A20; `out/A20/T67_gtpairs.tsv`, `out/A20/T67_candidates.tsv`)

How it was measured: `patch_attitude67.py` replays `PairwisePruning`'s first loop verbatim
(`class/feature_matching.cpp:1637-1707`: `Icp`, trans update, axis angle, `OverlapCheck_3d(...,50.0)`) on a copy of
the candidate list, before the real pruning runs. The replay agrees with the real pruning: its gates leave exactly
idx 10 (2,6), which is the real survivor (`T67_survivors.tsv`). Pose error uses `CountResult`'s convention
(`class/data_structure.cpp:1001-1009`, `T_i^-1 T_j`). Calibration: on Pot A the right candidates read 1.0-5.9° /
1.4-6.4 mm at the lane centroid (APA idx 1, 10, 23, 31), so the convention holds. "GT axis" is the angle between
the two pieces' released axes when posed at the GT pose, folded to 0-90° the way the gate at :1667 folds it. On
Pot A's single-axis pieces it reads ≤4.5° or ≥177.4°, i.e. ≤4.5° folded; its multi-axis pieces 7 and 8 read
19-122° on axis 0, so the measure is only clean for single-axis pieces (all Juglet pieces except J7). "Contacts" is
the number of moving-lane dots within 2 mm of the fixed lane at the GT pose. On Pot A the GT pairs read 7-50; the
median distance is not used, because both loops run far apart away from the shared break.

| GT pair | GT axis, folded ° | contacts at GT pose | candidates | best candidate: dots matched, inliers, ICP score, axis fold °, rot err °, centroid err mm | dies at |
|---|---|---|---|---|---|
| 1-2 | 86.4 | 5 | 0 | — | no LCS |
| 1-4 | 9.5 | 12 | 1 | 7, 0, 11, 30.0, 166.3, 30.7 | axis gate :1715 |
| 1-5 | 45.9 | 0 | 0 | — | no LCS |
| 1-6 | 12.5 | 0 | 1 | 11, 0, 11, 52.9, 116.1, 20.1 | axis gate |
| 1-8 | 11.3 | 19 | 3 | 6, 12, 0.70, 58.1, 113.7, 27.6 (others 63.0°/74.4° fold) | axis gate |
| 1-9 | 73.5 | 0 | 0 | — | no LCS |
| 2-5 | 47.7 | 0 | 0 | — | no LCS |
| 2-9 | 63.7 | 5 | 0 | — | no LCS |
| 3-5 | 66.8 | 5 | 1 | 7, 0, 11, 82.2, 59.6, 5.4 | axis gate |
| 3-7 | 10.4 | 0 | 1 | 8, 4, 11, 32.4, 108.6, 16.5 | axis gate |
| 4-5 | 55.0 | 0 | 0 | — | no LCS |
| 4-6 | 17.1 | 0 | 1 | 7, 0, 11, 72.8, 136.9, 25.7 | axis gate |
| 5-9 | 58.2 | 0 | 0 | — | no LCS |
| 6-7 | 11.2 | 16 | 1 | 8, 0, 11, 88.9, 141.1, 30.6 | axis gate |
| 6-8 | 9.8 | 0 | 1 | 7, 8, 0.49, 76.8, 86.6, 45.7 | axis gate |
| 7-8 | 15.6 | 0 | 2 | 10, 0, 11, 14.2, 167.5, 30.1 | score gate :1726 (lowest score 11 > 1.5) |
| 7-9 | 58.6 | 3 | 0 | — | no LCS |
| 8-9 | 72.6 | 0 | 0 | — | no LCS |

Tally: 9 GT pairs form no candidate, 8 die at the axis gate and 1 at the score gate; none reaches the graph. The
best rotation error of any candidate on a GT pair is 59.6° (3-5); everything else is 86.6-171.9°.

**Where the attitude error enters, by stage:**

1. **Candidate formation (`FeatureComp`, `feature_matching.cpp:1453-1493`).** This splits cleanly by piece.
   - The 8 GT pairs among {1,3,4,6,7,8} all read GT axis ≤17.1°, and all 8 formed candidates.
   - The 10 GT pairs that involve 2, 5 or 9 all read 45.9-86.4°, and only 1 of them, (3,5), formed a candidate.
   - The features are measured relative to each piece's axis after it is aligned to z (shim `:176-200`,
     `CalculateFeatureAxisless`). An axis file that disagrees with the true pose makes the two edgelines'
     features disagree, so no LCS forms.
   - This is the Pot D 18/29 pattern (ticket 301: an axis file that contradicts the piece's pose) in a third form.
     Either `Dataset/Axes/Juglet/Juglet_Piece_{2,5,9}_Axis.xyz` or the Juglet GT (derived in ticket 01) is wrong
     for those pieces. This run does not separate the two.
2. **Matched-run length, then ICP (`PairwisePruning` → `Icp`, `feature_matching.cpp:1650`;
   `reconstruction.cpp:1113ff`, seeded from the LCS by `UsePreCorres` at :1181).**
   - Juglet runs are 6-11 dots (mean 8.2) on GT pairs, against Pot A's 12.3 mean and 35 max. At about 1.8 mm per
     dot that is 11-20 mm of break edge.
   - 16 of 23 Juglet candidates end with score 11, ICP's rejection value: fewer than 6 correspondences at
     `reconstruction.cpp:1198-1200`, not converged at :1283, or inliers under `MINIMUM_NUMBER` 6 at :1304 via
     :727/:763. Their inliers are 0-4. The 7 that converge have 6-12 inliers (Pot A GT candidates: 18-100).
   - Every converged or rejected pose on a GT pair is 59.6-171.9° from the truth. Pot A has 18 GT-edge candidates
     under 10°.
   - So the wrong attitude is produced here, by ICP on short seeds, and the axis gate at :1715 (folded angle
     > 0.436 rad = 25°) is what removes it. Neither the StateManager merge nor `AxisAlignment` is where it enters.
3. **Contact at the true pose.** Of the 18 GT pairs, 10 have **no** lane dot within 2 mm of the partner's lane at
   the GT pose, and the best has 19 of 40 (1-8). Pot A's GT pairs read 7-50. So even at the right pose our
   interior lanes often do not run along each other. Two readings fit: the lanes do not trace the shared break,
   or the derived Juglet GT is loose. This is recorded as a measurement, not a verdict.

**Why the wrong pair (2,6) beat every GT pair.**
- It is candidate idx 10: 7 dots matched, 8 inliers, ICP score 0.54, folded axis angle 4.49°.
- Of the 23 candidates, 7 pass the score gate (≤1.5: idx 0, 2, 5, 8, 10, 18, 20) and 5 pass the axis gate
  (≤25°: idx 9, 10, 13 and 21, at 13.4°, 4.5°, 24.6° and 14.2°).
- Their intersection is idx 10 alone, and the overlap gate (:1729) passes it.
- At the GT pose the axes of 2 and 6 are 85.2° apart (`gt_axis_unfold_deg`), yet ICP's axis-consistency term
  (`reconstruction.cpp:1228-1234`) brought them parallel. So the pose that "looks" axis-consistent is consistent
  only with piece 2's suspect axis file, not with the GT.
- It won by being the only candidate the gates could not reject. Nothing scored it above a GT pair.

### What this means for the work

- The floor change is inert here. Lowering 50 to 30, 20 or 17 admits the short breaks, and the outcome does not
  move.
- The crash guard is a clean, one-place change and Pot A reproduces 8/8 and 15/15 on it. It is a merge candidate
  for the lead, as a separate commit.
- The next question is an input question before it is a method question: are the Juglet axis files for pieces 2,
  5 and 9 (or their GT) right? If they are wrong, the fix is a corpus fix, done the ticket-301 way, by
  substitution in the run dir only.
- After that, the short-break matching (6-11-dot seeds producing 60-170° attitudes) is the method limit the
  conservator would be deciding on. It is not tuned here, per the spec.


### Lead verification (2026-11-03)

- verified: axis-vs-GT split, independent of the worker's instrument -> I transformed each piece's axis direction
  (6th-field vector of Dataset/Axes/Juglet/Juglet_Piece_N_Axis.xyz) by its GT pose
  (Dataset/Juglet_GT/Juglet_Piece_N_T.txt, row-major R|t) and computed folded pairwise angles in the assembled
  frame: piece medians to the other eight are P1 23.1, P2 77.2, P3 29.3, P4 25.0, P5 55.0, P6 17.1, P7 23.1,
  P8 15.6, P9 63.5 deg -- pieces 2, 5, 9 stick out exactly as claimed, and my per-pair values match the
  instrument's gt_axis columns exactly (1-2 86.4, 1-5 45.9, 2-5 47.7, 3-7 10.4, 6-7 11.2, 7-8 15.6, 8-9 72.6).
- verified: out/F20/1.\ Acc.txt reads 0 / 9 and 0 / 18; only T_1to_1.txt and T_5to_5.txt exist (pieces 2, 6);
  out/PACTL/1.\ Acc.txt reads 8 / 8 (100 %) and 15 / 15 (100 %) with eight T files -> control reproduces on the
  guarded binary.
- verified: guard fired -> run log logs/binary_F50G.log prints "T67-NO-CANDIDATES pruned LCS list empty;
  StateManager skipped; exit 0"; out/F50G is empty (0 files) as expected.
- verified: renders exist on the laptop (artifacts/67/render/{F20,PACTL}_{assembly,perpiece}.png) and the F20
  chamfer figures 19.69 / 21.52 mm sit in score/F20.json.
- note: my first collinearity check on the axis POINTS was inconclusive (I misread the 6-field format as
  point-to-point); the direction-vector check above is the correct one and confirms the claim.
