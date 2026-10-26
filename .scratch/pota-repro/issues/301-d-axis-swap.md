# Ticket 301 - swap one Pot D piece's axis for the direction its reference pose implies, and see which artefact is the defect

Status: results-in
Working in: chat on Thinkbook16 (2026-10-26)
Branch: 301-d-axis-swap, in /c/PR/worktrees/sfs/301
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("Write the D axis-swap ticket and run it (5 short single-pot jobs)")

## Why

Ticket 299 established that the authors' released bundle does not reproduce their own paper on Pot D
(22/28 sherds and 53/66 joins against the printed 23/28 and 55/66, while our bundle reaches 23/29 and
55/69), and named a cause: on the five pieces that fail in every arm and every replay - 18, 25, 26, 28,
29 - the released axis file is inconsistent with the released reference pose, by 10.0 to 74.7 deg, while
on B, E and G (47 pieces, the pots that reproduce 100 %) nothing exceeds 13.7 deg.

That is a correlation with two holes in it, both stated in 299 itself: Pot D 21 is a 24.0-71.0 deg
outlier that nevertheless seats at 1.50 deg / 5.35 mm, and Pot D 20 at 11.3 deg seats while Pot D 28 at
10.0 deg fails grossly at 164.43 deg / 754.87 mm. So "the axis is inconsistent with the pose" is a risk
factor, not a demonstrated cause, and it cannot say WHICH of the two artefacts is wrong - the axis file,
the reference pose, or neither.

This ticket reads off the only thing that separates them: give one piece at a time the axis its own
reference pose implies, and see whether it then seats. It is an input-only swap, so the assembler, its
image, the meshes, the breaklines and the tolerances are identical to the run that failed.

## Facts already established (do not re-derive)

- Assembler `/opt/sfs-pristine` (upstream `9195c016` + INFRA shim, binary md5
  `0fd8d707ceb3f9cffd08d8951c43ccda`, beam k=5 b=3), image
  `/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif`, preprocessing commit `d1f1a4c`.
  Identical in every arm of ticket 298.
- Corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/` holds
  `Axes/Pot_D_Piece_NN_Axis.xyz`, `Mesh/Pot_D_Piece_NN_Mesh_DS.obj`, `Surfaces/Pot_D_Piece_NN_Surface_0/1.xyz`,
  `Breaklines/Pot_D_Piece_NN_Breakline_0/1.pcd` (two-digit piece numbers) and
  `Ground Truth/Pot_D_Piece_<n>_T.txt` (**no** zero padding in the GT names).
- The assembler's own bar: `class/data_structure.cpp:927` rad_threshold = 0.35 (20.05 deg),
  t_threshold = 50.0 mm; the transform comparison is `isSimilarTrans`, `class/data_structure.cpp:661-680`.
  "Seated" below means within those two numbers of the reference transform.
- Ticket 299 §3 (`C:/PR/SfSpp_preprocessing/.scratch/pota-repro/issues/299-dh-why.md:192`) holds the
  per-piece authors'-breakline table with every failing piece's rotation and translation error; §6
  (`:310`) holds the axis-deviation measurement **and the pot axis it used**; §8 (`:353`) the named
  cause; §10 (`:402`) the nondeterminism. Read them; do not recompute what is tabulated.
- The 298 harness for an authors'-breakline arm is
  `C:/PR/SfSpp_preprocessing/.scratch/pota-repro/298/p296-submit.sbatch` (100 lines). `ARM=ceiling`
  needs **no** prepare run - it takes the breaklines straight from the corpus - so a run here depends on
  nothing but the corpus. Everything the assembler reads is staged in
  `dataset/SfS_pp/{Breaklines,Mesh,Axes,Surfaces,Ground Truth,Result}`.
- 299 §10: identical `out/inputs.md5` between replays, yet the screen pruned 886 pairs in one Pot D run
  and 888 in its replay, and poses moved tens of degrees. A single draw can therefore differ from another
  for no reason we control - which is why every swap run below rides with its own control run.

## What to do

**Phase 0 - the swap, on a copy.** Establish from the loader how the axis file is read (which vector the
assembler actually uses, and whether the file carries more than one candidate direction), and reconstruct
the pot axis exactly as 299 §6 did, reusing that code and citing it. For a piece with reference rotation
`R_GT`, the direction its pose implies is `R_GT^T . a_world`, with `a_world` the pot axis in the vessel
frame. An axis is a line, so compare directions as the angle minimised over the two signs, and keep the
rest of the file's content intact. Write the swapped file into the run's `dataset/SfS_pp/Axes/` as a
**real file**, with provenance (md5 of the corpus original, md5 of the staged file, `a_world`, the
`R_GT` path) recorded in `run.json`. A symlink will not do: `link_into()` in the harness refuses to
replace a real file for a reason.

**Phase 1 - five pots, each with its own control.** For each of pieces 18, 25, 26, 28, 29, one job
assembles Pot D twice: `ctrl` with the corpus axis untouched, `swap` with only that one piece's axis
replaced. Authors' breaklines in both arms (`ARM=ceiling`), so the sole difference between the two arms
of a job is that one file. Ten run directories, five jobs, each with `run.json`, `submit.sbatch`,
`logs/` and `out/`, plus one `index.tsv` row per run with `verdict` and `human_note` **empty**.

**Phase 2 - read it.** For each pair: did `ctrl` reproduce 299's outcome for that piece? Then did
`swap` seat, and at what pose? Report, for every run, each staged piece's rotation and translation error
against its reference transform, and the pot's printed sherd and join counts.

**Phase 3 - say which artefact is the defect.** For each piece, one of:

- (a) swap seats, pose within the bar of the reference -> the released axis file is inconsistent with the
  released pose, and the pose is what the pipeline reproduces: **the axis file is the defect**.
- (b) swap seats, but at a pose outside the bar of the reference -> **the reference pose** for that piece
  is not the seat the method finds; the "inconsistency" 299 measured is not diagnostic of the axis file.
- (c) swap fails again, in the same gross way -> the axis is not the whole story; the cause is upstream of
  the piece's initial frame (breakline, surface, or the screen), and say which evidence points where.
- (d) not determined, with the reason (control did not reproduce; two runs of the same bundle disagreed;
  the swap could not be proved to land).

## Acceptance criteria

- [x] Ten run directories, five jobs, each with `run.json`, `submit.sbatch`, `logs/` and `out/`; one
      `index.tsv` row per run, `verdict` and `human_note` empty.
- [x] For every `swap` run, proof the swap landed: the angle between the staged axis direction and
      `a_world` rotated by the piece's staged pose is ~0 - report the number; more than 1 deg means the
      file was not written where the loader reads it.
- [x] Every `ctrl` run compared with 299's recorded outcome for that piece, and any disagreement stated
      plainly (that is evidence about the screen, not about the axis).
- [x] For each of the five pieces: seated or not, the rotation and translation error against the reference
      transform, the assembler's rule cited by `file:line`, and the verdict (a)-(d) with its evidence.
- [x] Pot-level sherd and join counts for all ten runs, and whether any NON-target piece changed its fate
      (the screen is global, so it can).
- [x] The frozen corpus provably untouched: md5 of each `Axes/Pot_D_Piece_NN_Axis.xyz` before and after,
      unchanged, and no write outside the run directories.
- [x] No change to the assembler, its image, the tolerances, the meshes, the breaklines or any tracked
      source file.
- [x] Geometry produced by the runs deleted before the ticket closes, with a counted record of what was
      removed and what was kept (the record, not the payload - workspace `AGENTS.md`, rule 13).
- [x] Ticket updated with the tables and section numbers, `Status:` moved, board rebuilt.

## What this cannot settle

It cannot show which of the two artefacts is *right* in any absolute sense - the only reference is the
authors' own pose file, which is itself one of the suspects; it can only show which one the pipeline can
seat against. It cannot fix 299 §10's nondeterminism: one paired control bounds the question per piece,
not the distribution, so a single draw that seats is a lead, not a rate. And it says nothing about Pot H,
whose pieces flip between replays of byte-identical input - different question, its own ticket.

## Result

**Answered for four of the five pieces; the fifth is void.** On **18** and **29**, replacing one
number in one axis file - its direction, keeping the axis point and the rest of the file byte for
byte - makes the piece seat inside the assembler's bar: 18 goes 153.04 deg / 799.13 mm -> 0.34 deg /
3.32 mm, 29 goes 87.40 / 420.98 -> 3.10 / 25.28. Nothing else in the run changed but that file, so on
those two pieces **the released axis file is the defect**, and the released reference pose is the seat
the pipeline reproduces: verdict **(a)**.

On **26** and **28** the swap changes the failure and does not clear it - 26: 163.42 deg -> 145.12 deg
and 438 mm -> 837 mm; 28: 163.78 -> 170.58 deg and 596 mm -> 668 mm - gross in the same way as before.
The direction is therefore not the whole story on those two and the cause lies upstream of the piece's
initial frame: verdict **(c)**.

On **25** nothing is determined. Its control does not reproduce 299 (it seats at 3.14 deg / 19.48 mm
where 299 recorded 108.76 / 441.74), and in five runs of byte-identical input piece 25 seats or fails
grossly **with its own axis untouched** - so its pair is void and its seat is not decided by its axis:
verdict **(d)**.

No piece took verdict (b): nothing seated outside the bar.

| piece | ctrl, best incident edge | swap, best incident edge | bar (20.05 deg / 50 mm) | verdict |
|---|---|---|---|---|
| 18 | 153.04 deg / 799.13 mm (13-18) | 0.34 / 3.32 (10-18) | ctrl fails, swap seats | **(a)** axis file |
| 25 | 3.14 / 19.48 (15-25), **seated** | 71.70 / 283.59 (25-29) | ctrl seats, swap fails | **(d)** void |
| 26 | 163.42 / 438.49 (13-26) | 145.12 / 837.29 (13-26) | both fail, gross | **(c)** upstream |
| 28 | 163.78 / 596.45 (14-28) | 170.58 / 667.77 (03-28) | both fail, gross | **(c)** upstream |
| 29 | 87.40 / 420.98 (07-29) | 3.10 / 25.28 (07-29) | ctrl fails, swap seats | **(a)** axis file |

### 1. Ten runs, five jobs

| piece | job | sacct State / ExitCode | arms | elapsed |
|---|---|---|---|---|
| 18 | 33813900 | COMPLETED / 0:0 | ctrl, swap, both arm exit 0 | 01:08:42 |
| 25 | 33813901 | COMPLETED / 0:0 | ctrl, swap, both arm exit 0 | 01:29:40 |
| 26 | 33813902 | COMPLETED / 0:0 | ctrl, swap, both arm exit 0 | 01:32:10 |
| 28 | 33813903 | COMPLETED / 0:0 | ctrl, swap, both arm exit 0 | 01:33:28 |
| 29 | 33813904 | COMPLETED / 0:0 | ctrl, swap, both arm exit 0 | 01:47:26 |

The ten run directories are `/data/gpfs/projects/punim2657/SfSpp/runs/20261026-1611_6da734d_p301-d<NN>-{ctrl,swap}`
(commit `6da734dd861093af6b1084d6f2763ba4c14c094a`), each with `run.json`, `submit.sbatch`,
`source.txt`, `logs/`, `out/`, and one `runs/index.tsv` row with `verdict` and
`human_note` empty. The harness is `.scratch/pota-repro/301/` on branch `301-d-axis-swap`; the
job builds it from the pushed commit through `C:/PR/scripts/run_from_commit.sh`, so no run read the
working tree. Authors' breaklines in both arms, corpus staged by symlink (`scripts/p301-arm.sh`),
assembler and image identical to ticket 298's (shim md5 `fb26e8ab49e9c00f7e8d02de44f6eea5`, image md5
`63a532b9732f84e59e7b1349065f1323`; `out/selector.txt` = POT_D, SHARD_NUMBER 29, header md5 after
flip `7d770d15927949a6d72e97d63887e582`). The only difference between the two arms of a job is
`dataset/SfS_pp/Axes/Pot_D_Piece_<NN>_Axis.xyz`.

### 2. The swap landed

#### Swap landed: what the staged file says when read back

| run | piece | corpus md5 | staged md5 | real file | staged vs planted (deg) | R_GT.d_staged vs a_world (deg) | moved from corpus (deg) |
|---|---|---|---|---|---|---|---|
| `d18-swap` | 18 | `f4a896ca76aaac5bbe39adf9769e601b` | `27ffb3be4d19626f99d8c387833898de` | yes | 0.00e+00 | 4.88e-05 | 36.32 |
| `d25-swap` | 25 | `83e8fab1963ec59d0fffec5ddc0cbaa7` | `4e966972529dd035e07b0d6979cc316c` | yes | 0.00e+00 | 8.53e-05 | 37.83 |
| `d26-swap` | 26 | `74833b60bf29c1308d64fba38ef0055d` | `e4fe7baec5f68f4fbc927e655b4f7442` | yes | 0.00e+00, 0.00e+00 | 5.86e-05, 5.86e-05 | 74.66, 71.96 |
| `d28-swap` | 28 | `e1b3fbd3b1e22582da17b391f5b53c67` | `c644053adc3e174f5723123ca3c68666` | yes | 0.00e+00, 0.00e+00 | 1.08e-05, 1.08e-05 | 27.77, 9.96 |
| `d29-swap` | 29 | `e54a5c015b2e14df9c1bd8177a109739` | `c8324083e4005d1000e05f8995a466d3` | yes | 0.00e+00, 0.00e+00 | 2.36e-05, 2.36e-05 | 75.34, 54.56 |

Read back with the loader's own parse (`class/data_structure.cpp:142`, whitespace doubles, six per
line): every staged file is a real file, staged direction against the planted one is `0.00e+00` deg on
every line, `R_GT . d_staged` against `a_world` is between 1.08e-05 and 8.53e-05 deg, and the file
moved 9.96 to 75.34 deg away from the corpus direction. All four numbers are far under the 1 deg that
would mean the file was written where the loader does not read it.

### 3. Did the controls reproduce 299?

| piece | 299's failed edge (deg / mm) | this ctrl, same edge | difference |
|---|---|---|---|
| 18 | 08-18 153.12 / 554.76 | 153.07 / 554.59 | -0.05 deg, -0.17 mm |
| 18 | 13-18 153.16 / 799.83 | 153.04 / 799.13 | -0.12 deg, -0.70 mm |
| 25 | 15-25 108.76 / 441.74 | **3.14 / 19.48, seated** | **disagrees** |
| 26 | 13-26 163.42 / 438.49 | 163.42 / 438.49 | 0.00 / 0.00 |
| 28 | 12-28 164.43 / 659.71 | 164.43 / 659.59 | 0.00 deg, -0.12 mm |
| 29 | 07-29 87.52 / 426.23 | 87.40 / 420.98 | -0.12 deg, -5.25 mm |

Four of the five reproduce to 0.12 deg. Only 25's control disagrees, and it disagrees by seating where
299 recorded a 108.76 deg miss - that is evidence about the screen, not about the axis, and per the
ticket it makes 25's pair void rather than good news.

**A defect in 299's own table, stated rather than papered over.** 299 §3's per-piece column quotes
translations that its failed-edge list does not support: 18 `895.62` where its edge says 554.76, 26
`974.37` vs 821.32, 28 `754.87` vs 659.71, 29 `462.95` vs 519.59. Its degrees agree with the
edge list in every case. Every comparison in this ticket is against the edge list, which reproduces.

**Five controls, one input, five outcomes.** The md5 of `out/inputs.md5` is
`c7169123bd0be4f4ee630a6991f89551` in all five ctrls and the md5 of `out/axes_seen_in_container.md5`
is `636aef01e8bdb91820e35c3101382a55` in all five (203 staged entries each, `Total number : 2445` in
all five) - and still: pruned 888 / 890 / 892 / 896 / 890, sherds 22 / 23 / 22 / 23 / 22, joins 53 / 55 /
53 / 55 / 53. 299 §10 saw this between two replays (886 against 888); five replays here show it at the
level of a single piece, which is what makes 25 unscorable rather than a failure of the swap.

### 4. The five pieces, evidence by piece

**18 - verdict (a).** In the control all three incident edges miss at 153 deg (10-18 153.23 / 198.14,
13-18 153.04 / 799.13, 08-18 153.07 / 554.59). With the pose-implied direction alone all three seat
(0.34 / 3.32, 0.49 / 2.74, 0.95 / 4.96). A one-file change moves the piece by the whole size of the
failure, so the released direction, not the released pose, is what the pipeline cannot seat.

**29 - verdict (a).** 07-29 goes 87.40 / 420.98 -> 3.10 / 25.28; 25-29 stays out (104.56 / 561.29),
which is why the pot gains one join (54 of 66) and not four. Same reading as 18.

**26 - verdict (c).** The swap helps by 18 deg on every incident edge (13-26 163.42 -> 145.12, 03-26
163.54 -> 145.63, 16-26 164.68 -> 146.66) and still misses by 7x the rotation bar and 10-17x the
translation bar: gross in the same way. Its axis **point** sits 47.6 and 161.5 mm off the reconstructed
pot axis line while the good pieces sit 4-24 mm off, and `AxisAlignment` builds the piece's frame from
that point as well as the direction (`class/reconstruction.cpp:66-123`), so a direction-only swap
cannot move it the whole way. What is left to look at is the point column in the same file, the
breakline, or the surface that sets the frame - this ticket does not separate those three.

**28 - verdict (c).** The swap does not help at all (14-28 163.78 -> 170.97, 03-28 164.40 -> 170.58,
12-28 164.43 -> 170.77): the failure moves with the piece's own frame, not with the direction. Its axis
point sits 190.2 and 38.9 mm off the pot axis line. Same three suspects as 26.

**25 - verdict (d).** The control seats (15-25 3.14 / 19.48, 24-25 3.70 / 24.37) where 299 recorded
108.76 deg, and piece 25 also seats in `d28-ctrl` (3.20 / 21.2), `d26-swap` (3.16 / 19.6) and
`d28-swap` (3.23 / 21.9) with its own corpus axis untouched, while failing in `d18-ctrl` (108.49),
`d26-ctrl` (107.48), `d29-ctrl` (108.49), `d18-swap` (157.37) and `d29-swap` (104.56). Its own
swap fails too (71.70 / 283.59). So the pair cannot decide anything, and the axis of 25 is demonstrably
not what decides whether it seats.

### 5. Pot-level counts, all ten runs

#### Pot-level counts, all ten runs

| run | role | hypotheses | pruned | sherds seated | joins seated | pieces off | pieces not seated |
|---|---|---|---|---|---|---|---|
| `d18-ctrl` | ctrl | 2445 | 888 | 22/28 (78.5714%) | 53/66 (80.303%) | 27 | 18,22,25,26,28,29 |
| `d18-swap` | swap | 2451 | 885 | 23/28 (82.1429%) | 56/66 (84.848%) | 27 | 22,25,26,28,29 |
| `d25-ctrl` | ctrl | 2445 | 890 | 23/28 (82.1429%) | 55/66 (83.333%) | 27 | 18,22,26,28,29 |
| `d25-swap` | swap | 2482 | 912 | 22/28 (78.5714%) | 53/66 (80.303%) | 27 | 18,22,25,26,28,29 |
| `d26-ctrl` | ctrl | 2445 | 892 | 22/28 (78.5714%) | 53/66 (80.303%) | 27 | 18,22,25,26,28,29 |
| `d26-swap` | swap | 2461 | 901 | 23/28 (82.1429%) | 55/66 (83.333%) | 27 | 18,22,26,28,29 |
| `d28-ctrl` | ctrl | 2445 | 896 | 23/28 (82.1429%) | 55/66 (83.333%) | 27 | 18,22,26,28,29 |
| `d28-swap` | swap | 2427 | 891 | 23/28 (82.1429%) | 55/66 (83.333%) | 27 | 18,22,26,28,29 |
| `d29-ctrl` | ctrl | 2445 | 890 | 22/28 (78.5714%) | 53/66 (80.303%) | 27 | 18,22,25,26,28,29 |
| `d29-swap` | swap | 2557 | 913 | 23/28 (82.1429%) | 54/66 (81.818%) | 27 | 18,22,25,26,28 |


### 6. Did any non-target piece change fate?

One did, and not because of the swap that was applied: piece 25 seats in `d26-swap` and `d28-swap`
(whose swapped piece is 26 and 28) and fails in `d18-swap` and `d29-swap`, with its own axis
untouched in all four - that is the nondeterminism of §3, not an effect of one piece's axis on another.
Every other piece 1-21, 23, 24 sits at 0.2-2.3 deg / 0.6-13.3 mm in all ten arms (§7). Piece 22 is off
in all ten (isolated ground-truth node, unscorable) and 27 is off in all ten (its `Breakline_0` has 48
points, under the assembler's 50-point floor). The screen itself moves: hypotheses 2427-2557, pruned pairs
885-913 across the ten runs.

### 7. Every staged piece, all ten runs

#### Every staged piece, best incident ground-truth edge (deg / mm), all runs

Cell = the piece's best incident edge against its reference transform; * = within the bar (seated). 'off' = the assembler dropped the piece before assignment. Rows are the whole shard, not only the five targets, because the screen is global.

| piece | 18c | 18s | 25c | 25s | 26c | 26s | 28c | 28s | 29c | 29s |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.32 / 3.1* | 0.32 / 3.0* | 0.31 / 2.9* | 0.34 / 3.3* | 0.32 / 2.9* | 0.33 / 3.2* | 0.32 / 2.9* | 0.31 / 2.8* | 0.32 / 3.1* | 0.31 / 3.0* |
| 2 | 0.49 / 4.7* | 0.58 / 4.9* | 0.46 / 3.4* | 0.44 / 4.4* | 0.30 / 3.1* | 0.48 / 4.5* | 0.34 / 3.7* | 0.41 / 4.0* | 0.49 / 4.7* | 0.49 / 3.7* |
| 3 | 0.83 / 7.8* | 0.75 / 7.3* | 0.91 / 9.4* | 0.84 / 7.8* | 0.81 / 7.4* | 0.83 / 8.0* | 0.77 / 7.4* | 0.84 / 8.1* | 0.83 / 7.8* | 0.92 / 8.7* |
| 4 | 0.58 / 5.1* | 0.59 / 5.5* | 0.59 / 5.2* | 0.59 / 5.2* | 0.62 / 5.6* | 0.59 / 5.1* | 0.62 / 5.4* | 0.59 / 5.3* | 0.58 / 5.1* | 0.57 / 4.8* |
| 5 | 0.32 / 3.1* | 0.32 / 3.0* | 0.31 / 2.9* | 0.34 / 3.3* | 0.32 / 2.9* | 0.33 / 3.2* | 0.32 / 2.9* | 0.31 / 2.8* | 0.32 / 3.1* | 0.31 / 3.0* |
| 6 | 0.43 / 1.8* | 0.37 / 1.3* | 0.35 / 1.4* | 0.41 / 1.7* | 0.46 / 2.1* | 0.40 / 1.5* | 0.40 / 1.6* | 0.43 / 1.6* | 0.43 / 1.8* | 0.43 / 1.4* |
| 7 | 0.76 / 5.5* | 0.76 / 5.8* | 0.89 / 6.3* | 0.75 / 5.5* | 1.07 / 7.4* | 0.83 / 6.0* | 1.07 / 7.5* | 1.09 / 7.6* | 0.76 / 5.5* | 0.85 / 5.9* |
| 8 | 0.59 / 4.5* | 0.64 / 3.8* | 0.53 / 4.2* | 0.54 / 4.3* | 0.62 / 4.9* | 0.54 / 4.4* | 0.58 / 4.5* | 0.50 / 4.1* | 0.59 / 4.5* | 0.50 / 4.0* |
| 9 | 0.65 / 2.9* | 0.60 / 2.5* | 0.68 / 4.0* | 0.66 / 3.0* | 0.68 / 3.2* | 0.64 / 2.9* | 0.65 / 3.0* | 0.68 / 3.2* | 0.65 / 2.9* | 0.60 / 3.4* |
| 10 | 0.21 / 1.6* | 0.22 / 1.6* | 0.26 / 1.7* | 0.16 / 2.0* | 0.11 / 2.0* | 0.20 / 1.8* | 0.26 / 1.9* | 0.26 / 2.2* | 0.21 / 1.6* | 0.28 / 1.7* |
| 11 | 0.64 / 2.2* | 0.53 / 2.3* | 0.65 / 2.5* | 0.66 / 3.0* | 0.60 / 2.1* | 0.61 / 2.6* | 0.65 / 3.0* | 0.67 / 2.4* | 0.64 / 2.2* | 0.60 / 2.5* |
| 12 | 0.96 / 9.4* | 1.06 / 10.4* | 0.91 / 9.4* | 0.98 / 9.7* | 0.94 / 9.2* | 0.99 / 9.5* | 0.98 / 9.6* | 0.97 / 9.9* | 0.96 / 9.4* | 0.93 / 9.5* |
| 13 | 0.21 / 1.6* | 0.22 / 1.6* | 0.25 / 0.6* | 0.16 / 2.0* | 0.11 / 2.0* | 0.20 / 1.8* | 0.26 / 1.9* | 0.26 / 2.2* | 0.21 / 1.6* | 0.27 / 0.8* |
| 14 | 0.96 / 2.9* | 0.45 / 3.2* | 0.42 / 2.7* | 1.04 / 6.8* | 1.06 / 4.1* | 0.96 / 6.3* | 0.89 / 5.8* | 0.46 / 3.0* | 0.96 / 2.9* | 0.40 / 2.9* |
| 15 | 0.75 / 3.4* | 0.93 / 4.3* | 0.91 / 3.7* | 0.87 / 4.0* | 1.07 / 4.1* | 0.89 / 3.8* | 0.87 / 3.2* | 0.94 / 3.3* | 0.75 / 3.4* | 0.86 / 3.9* |
| 16 | 0.99 / 6.5* | 0.45 / 3.2* | 0.42 / 2.7* | 1.04 / 6.8* | 1.10 / 7.3* | 0.96 / 6.3* | 0.89 / 5.8* | 0.46 / 3.0* | 0.99 / 6.5* | 0.40 / 2.9* |
| 17 | 1.59 / 11.9* | 1.53 / 12.1* | 1.44 / 11.1* | 1.77 / 13.3* | 1.23 / 10.1* | 1.34 / 10.6* | 1.47 / 11.4* | 1.36 / 10.8* | 1.59 / 11.9* | 1.45 / 11.3* |
| 18 | 153.04 / 799.1 | 0.34 / 3.3* | 48.95 / 180.0 | 148.08 / 546.2 | 153.10 / 554.9 | 121.89 / 771.4 | 49.02 / 414.8 | 141.90 / 402.1 | 153.04 / 799.1 | 153.04 / 799.0 |
| 19 | 0.28 / 0.6* | 0.54 / 3.8* | 0.25 / 0.6* | 0.25 / 0.9* | 0.22 / 0.8* | 0.34 / 0.8* | 0.38 / 0.9* | 0.33 / 1.7* | 0.28 / 0.6* | 0.27 / 0.8* |
| 20 | 0.59 / 4.3* | 0.58 / 4.9* | 0.63 / 4.2* | 0.66 / 4.5* | 0.30 / 3.1* | 0.64 / 4.4* | 0.34 / 3.7* | 0.41 / 4.0* | 0.59 / 4.3* | 0.65 / 4.4* |
| 21 | 1.24 / 8.4* | 1.27 / 8.6* | 1.39 / 9.4* | 1.28 / 8.3* | 1.23 / 10.1* | 1.34 / 10.6* | 1.36 / 9.3* | 1.36 / 10.8* | 1.24 / 8.4* | 1.45 / 11.3* |
| 22 | - | - | - | - | - | - | - | - | - | - |
| 23 | 0.43 / 1.8* | 0.37 / 1.3* | 0.35 / 1.4* | 0.41 / 1.7* | 0.46 / 2.1* | 0.40 / 1.5* | 0.40 / 1.6* | 0.43 / 1.6* | 0.43 / 1.8* | 0.43 / 1.4* |
| 24 | 2.24 / 11.5* | 2.29 / 11.3* | 2.11 / 10.6* | 2.27 / 11.6* | 1.58 / 10.7* | 2.03 / 10.0* | 2.09 / 12.0* | 2.14 / 12.7* | 2.24 / 11.5* | 1.91 / 9.2* |
| 25 | 108.49 / 440.6 | 157.37 / 764.7 | 3.14 / 19.5* | 71.70 / 283.6 | 107.48 / 519.8 | 3.16 / 19.6* | 3.20 / 21.2* | 3.23 / 21.9* | 108.49 / 440.6 | 104.56 / 561.3 |
| 26 | 163.10 / 440.6 | 162.83 / 440.3 | 143.37 / 956.4 | 163.05 / 441.2 | 163.42 / 438.5 | 145.12 / 837.3 | 143.51 / 956.8 | 124.97 / 814.4 | 163.10 / 440.6 | 162.67 / 433.7 |
| 27 | off | off | off | off | off | off | off | off | off | off |
| 28 | 163.69 / 597.1 | 171.91 / 627.3 | 175.40 / 819.7 | 163.66 / 596.3 | 163.65 / 596.4 | 117.18 / 593.6 | 163.78 / 596.5 | 170.58 / 667.8 | 163.69 / 597.1 | 175.45 / 820.3 |
| 29 | 87.40 / 421.0 | 154.00 / 551.6 | 126.53 / 688.4 | 71.70 / 283.6 | 87.52 / 426.2 | 82.58 / 480.8 | 82.33 / 478.6 | 114.57 / 348.2 | 87.40 / 421.0 | 3.10 / 25.3* |


### 8. The frozen corpus, untouched

| piece | md5 in the corpus, before and after every run | Phase 0 baseline |
|---|---|---|
| 18 | `f4a896ca76aaac5bbe39adf9769e601b` | same |
| 25 | `83e8fab1963ec59d0fffec5ddc0cbaa7` | same |
| 26 | `74833b60bf29c1308d64fba38ef0055d` | same |
| 28 | `e1b3fbd3b1e22582da17b391f5b53c67` | same |
| 29 | `e54a5c015b2e14df9c1bd8177a109739` | same |

Each arm md5'd all 32 `Axes/Pot_D_Piece_*_Axis.xyz` before and after itself and wrote the three files
`out/corpus_axes_md5_before.txt`, `_after.txt` and `corpus_unchanged.txt`; all ten report the
32 files unchanged, and the five targets were re-checked once more after the deletion. Nothing was
written outside the ten run directories except `runs/index.tsv` (ten rows) and a scratch copy of the
cleanup script in `/tmp`. No source file, mesh, breakline, surface, tolerance or assembler input was
touched: the harness recorded md5s of itself and of its assembler inputs in every run
(`out/harness_md5.txt`, `out/assembler_inputs.md5`) and they are the same in all ten.

### 9. What was deleted, and what was kept

Before closing, the geometry was removed with a counted record per run (workspace `AGENTS.md` rule 13),
by `.scratch/pota-repro/301/p301_cleanup.sh` (commit `529cc09`). Each run carries its own
`out/cleanup-record.txt`.

| run | dataset/ removed | edgelines removed | kept |
|---|---|---|---|
| `d18-ctrl` | 57 files, 203 symlinks, 322211 B | 28 files, 241343 B | 28 transforms, 7646 B |
| `d18-swap` | 58 files, 202 symlinks, 320485 B | 28 files, 239592 B | 28 transforms |
| `d25-ctrl` | 57 files, 203 symlinks, 320779 B | 28 files, 239911 B | 28 transforms |
| `d25-swap` | 58 files, 202 symlinks, 320367 B | 28 files, 239503 B | 28 transforms |
| `d26-ctrl` | 57 files, 203 symlinks, 320423 B | 28 files, 239556 B | 28 transforms |
| `d26-swap` | 58 files, 202 symlinks, 323170 B | 28 files, 242188 B | 28 transforms |
| `d28-ctrl` | 57 files, 203 symlinks, 320705 B | 28 files, 239849 B | 28 transforms |
| `d28-swap` | 58 files, 202 symlinks, 324414 B | 28 files, 243428 B | 28 transforms |
| `d29-ctrl` | 57 files, 203 symlinks, 322211 B | 28 files, 241342 B | 28 transforms |
| `d29-swap` | 58 files, 202 symlinks, 322287 B | 28 files, 241297 B | 28 transforms |

`dataset/` held everything the arm staged for the assembler (the corpus files as symlinks, the one
swapped axis as a real file - which is why a swap run shows one file more and one symlink fewer - and the
pot graph); `out/Result/*.xyz` were the 28 staged edgelines. Kept on purpose, because it is what every
number above is computed from: the 28 transforms `out/Result/T_<i>to_<j>.txt`, `run.json`,
`submit.sbatch`, `source.txt`, `logs/`, `out/summary.txt`, `out/inputs.md5`,
`out/swap_provenance.json`, the corpus md5 triples, `out/arm_exit.txt` and the swapped file itself as
`out/staged_axis.final.xyz`. The ten directories went from ~1.3 MB each to 381-396 KB each.

### 10. What this adds to "What this cannot settle"

The per-piece answer is not a rate. One paired control bounds one draw per piece, and piece 25 shows what
that costs: its own control and its own swap are both void, so its row says nothing either way. On 18 and
29 the swap is decisive because the control reproduced 299 and the only changed input was that file. On
26 and 28 the axis is excluded as the *sole* cause, not as a contributor - some of the failure is the
misalignment and some of it sits upstream of the piece's frame, and this ticket does not apportion them.
Nothing here says the released pose is right; verdict (b) never occurred, and no piece was found seating
outside the bar against a correct pose. Pot H is untouched.

## Comments

- **2026-10-26 - the first submission failed and was thrown away, not patched over.** Jobs
  33813784-88 (run directories `20261026-1609_c46227d_p301-d*-{ctrl,swap}`) all died in two minutes with
  `bash: /p301run/scripts/p301_inside.sh: No such file or directory` and arm exit 12: the harness md5'd
  itself into the run directory's log but never copied the scripts there, and the container binds the run
  directory at `/p301run`, not the job's temporary checkout. Commit `6da734d` stages the five harness
  files into `$RUN/scripts` and exits 16 if the inner script is still missing. The ten directories held
  no assembly (no `out/Result`, no `out/summary.txt`), so they were not results: they and their ten
  `index.tsv` rows were removed, and the run ids in §1 are the resubmission.
- **299 §3's per-piece translations are wrong against its own edge list** (§3 above); no number in this
  ticket uses them, and the comparison was made on the edge list, which reproduces to 0.12 deg on four of
  the five pieces.
- **The five controls are themselves a measurement** of the screen's nondeterminism (§3): one
  `out/inputs.md5`, five different prunings, and piece 25 seating in two of them and missing by 108 deg in
  the other three.
- Reduction and tables: `.scratch/pota-repro/301/p301_report.py --markdown`; its output is
  `.scratch/pota-repro/301/results/p301-tables.md` (pot counts, the 28-piece matrix, per-piece edge blocks,
  the swap-landed table) and `results/p301-ten-runs.json` is the machine-readable form. Every incident
  edge behind §4 is in that file.
- The acceptance boxes above are ticked by the worker against the evidence in §1-§10; the review and the
  close are the coordinating session's.

