# Ticket 301 - swap one Pot D piece's axis for the direction its reference pose implies, and see which artefact is the defect

Status: ready-for-agent
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

- [ ] Ten run directories, five jobs, each with `run.json`, `submit.sbatch`, `logs/` and `out/`; one
      `index.tsv` row per run, `verdict` and `human_note` empty.
- [ ] For every `swap` run, proof the swap landed: the angle between the staged axis direction and
      `a_world` rotated by the piece's staged pose is ~0 - report the number; more than 1 deg means the
      file was not written where the loader reads it.
- [ ] Every `ctrl` run compared with 299's recorded outcome for that piece, and any disagreement stated
      plainly (that is evidence about the screen, not about the axis).
- [ ] For each of the five pieces: seated or not, the rotation and translation error against the reference
      transform, the assembler's rule cited by `file:line`, and the verdict (a)-(d) with its evidence.
- [ ] Pot-level sherd and join counts for all ten runs, and whether any NON-target piece changed its fate
      (the screen is global, so it can).
- [ ] The frozen corpus provably untouched: md5 of each `Axes/Pot_D_Piece_NN_Axis.xyz` before and after,
      unchanged, and no write outside the run directories.
- [ ] No change to the assembler, its image, the tolerances, the meshes, the breaklines or any tracked
      source file.
- [ ] Geometry produced by the runs deleted before the ticket closes, with a counted record of what was
      removed and what was kept (the record, not the payload - workspace `AGENTS.md`, rule 13).
- [ ] Ticket updated with the tables and section numbers, `Status:` moved, board rebuilt.

## What this cannot settle

It cannot show which of the two artefacts is *right* in any absolute sense - the only reference is the
authors' own pose file, which is itself one of the suspects; it can only show which one the pipeline can
seat against. It cannot fix 299 §10's nondeterminism: one paired control bounds the question per piece,
not the distribution, so a single draw that seats is a lead, not a rate. And it says nothing about Pot H,
whose pieces flip between replays of byte-identical input - different question, its own ticket.

## Comments
