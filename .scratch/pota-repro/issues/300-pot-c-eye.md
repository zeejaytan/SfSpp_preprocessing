# Ticket 300 - stage the reassembled Pot C (ours vs the authors'), and say whether C 01's gap cost a seat

Status: in-progress
Working in: chat on Thinkbook16 (2026-10-26)
Branch: 300-pot-c-eye, in /c/PR/worktrees/sfs/300
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("Pot C seated with C01 gap? can you stage the reassembled pot on visual-qa? ours vs authors")

## Why

Pot C came out 4/4 sherds and 5/5 joins in BOTH arms of ticket 298 - the pot looked perfect. But
Pot C's four scored pieces include **Pot C 01**, the sherd whose interior surface carries a scan gap
(project AGENTS.md "Corpus caveats", ticket 285): the pipeline reads that gap as a second broken edge
the sherd does not have. The assembler reads `Breakline_0`, which is the boundary of the INTERIOR
surface - exactly the defective one. A pot-level 4/4 does not certify that piece, and the conservator
wants to see the reassembly with his own eye, ours beside the authors'.

## Facts already established (do not re-derive)

- Assembler `/opt/sfs-pristine` (upstream `9195c016` + INFRA shim), binary md5
  `0fd8d707ceb3f9cffd08d8951c43ccda`, beam k=5 b=3; identical in both arms of ticket 298.
- Preprocessing commit `d1f1a4c`; runs (Spartan, `/data/gpfs/projects/punim2657/SfSpp/runs/`):
  `20261026-0126_d1f1a4c_p298-Pot_C-oursd` and `...-Pot_C-authb`. Both read
  "Sherd accuracy : 4 / 4 (100 %)" then "Sherd accuracy : 5 / 5 (100 %)" (the second line is JOINTS,
  not sherds - the assembler prints the same label twice).
- Each `out/Result/` holds `1. Acc.txt`, `T_0to_0.txt ... T_3to_3.txt` (one transform per staged
  piece, i.e. 4 pieces) and four `*_Edgeline_*.xyz`. 67 KB per arm - the geometry is NOT there.
- Corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/` holds
  `Mesh/Pot_C_Piece_0N_Mesh_DS.obj` (only the DS mesh exists for Pot C), `Axes/Pot_C_Piece_0N_Axis.xyz`,
  `Breaklines/`, `Surfaces/` and `Ground Truth/Pot_C_Piece_<n>_T.txt` (NO zero padding in GT names).
  The Pot C bundle holds six pieces; the assembly used four - establish WHICH four from the block
  arrays in the shim and/or `out/links.tsv` / `out/selector.txt`, before transforming anything.

## What to do

**Phase 1 - rebuild both reassemblies.** For each arm, apply each piece's `T_ito_i.txt` to that
piece's `Mesh_DS.obj` and combine the four pieces into ONE OBJ per arm. State the transform
convention you assumed and prove it: a piece seated correctly must land with its breakline touching
its neighbours' (measure, do not eyeball - e.g. nearest-neighbour distance between adjacent pieces'
surfaces on the joins the GT graph says exist). If the convention is inverted and the pot flies
apart, say so and fix it before staging.

**Phase 2 - did C 01 cost a seat?** Identify C 01's index in each arm, and report for it: rotation
error (deg) and translation error (mm) of its seated pose against `Ground Truth/Pot_C_Piece_1_T.txt`,
how that compares with the other three pieces, and whether its seated position differs between the
two arms. Then answer the conservator's question directly: on the geometry, is the gap visible as a
seam or a doubled edge, and does it move that piece relative to its neighbours?

**Phase 3 - stage it in visual-qa.** Per `C:/PR/docs/agents/visual-qa.md`: geometry stays in the
method's own `artifacts/` (`C:/PR/SfSpp_preprocessing/artifacts/pota300/`), only small previews are
staged; write a desc in `C:/PR/visual-qa/viewer/pairs/`, run `visual-qa/viewer/stage_pair.py`
(authoring a desc by hand instead of fixing what it refuses is not allowed), check the viewer is
serving and run the `check_*.py` gates in `visual-qa/`. Read `C:/PR/visual-qa/AGENTS.md` first.
Two pairs:
- `pota300_potC_arms`: left = authors' bundle reassembly, right = ours, locked overlay, camera set
  so the four sherds' seams and C 01's own surface are both legible at this scale.
- `pota300_potC_c01`: `single:` - C 01 alone from our arm, close enough to see the scan gap in its
  interior surface.
Report the desc path, the pair ids, and the gate output.

**Phase 4 - the record.** Small previews stay staged; the full OBJs stay in `artifacts/pota300/`
(gitignored). If any geometry step runs longer than a minute on the laptop, it belongs in a Spartan
job in a run directory (run.json + submit.sbatch + logs/ + out/ + an index row with verdict and
human_note EMPTY), not on the laptop.

## Constraints

- **No algorithm, threshold or assembler change;** no re-run of the campaign. This is staging and
  measurement of geometry that already exists.
- Heavy work on Spartan compute nodes; the laptop may fetch the four DS meshes (2-4 MB each) and run
  the transforms only if it stays trivial - otherwise job it.
- Never `build.sh --target nurbs` (it compiles the pre-247 duplicate).
- Do not touch `C:/PR/worktrees/sfs/299` if it exists; tickets that touch the same repo run one after
  another and this one reports and stops.
- Write results into this ticket; commit on your branch only; leave Status at in-progress.

## Acceptance

1. Both reassembled OBJs exist under `artifacts/pota300/`, with the four pieces named per arm and
   the transform convention proved by a measured join distance.
2. C 01's seated pose compared with GT (rotation deg + translation mm) and against its three
   neighbours, in both arms.
3. A direct answer to "did the gap cost a seat", in one sentence, with the measurement behind it.
4. Two pairs staged in visual-qa, desc path and pair ids reported, gates run and their output quoted.
5. What the conservator must look for, written as a line he can act on - not a description of the
   script.

## Needs-eye

Visual-qa pair `pota300_potC_arms` (ours against the authors', same four pieces) and
`pota300_potC_c01` (C 01 alone): does the reassembly look right, and is the scan gap visible as a
seam where it should not be?
