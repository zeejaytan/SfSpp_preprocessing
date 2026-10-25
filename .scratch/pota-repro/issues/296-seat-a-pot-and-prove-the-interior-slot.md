# 296 - Seat a pot's pieces, and prove the interior edge is the one we feed

**Answers:** E1
**Status:** ready-for-agent
**Working in:** unassigned
**Branch:** unassigned
**Created:** 2026-10-25

## Why

The extraction corpus is settled at 283 of 291 valid lanes at bar (FIXES-LEDGER sections P/R), but the
assembler consumes exactly ONE breakline per piece -- the _0 file -- and never reads _1 (verified 2026-10-25:
class/data_path.h names one Breakline_0 path per sherd; Breakline_1 appears nowhere in class/ or the build).
Everything downstream of the edge stage therefore depends on the interior lines only, and **no seating run has
happened since the strip (538357c + 67ff3d7) and the theta 3.4 change**. The known-good seating result
(Pot A 8/8 sherds, 15/15 joins, 2026-10-20) predates both and must be re-established, not quoted.

## Goal

Two arms on identical meshes and axes, Pot A (8 pieces), scored against the ground-truth join graph:

- **Arm CEILING** -- the authors' own Breakline_0 files.
- **Arm TEST** -- our Breakline_0 files, shipped defaults, current main.

Report seated sherds and joins for each arm and the drift between them. The ceiling arm exists to separate
"our extraction" from "the assembler or its paths": if the ceiling does not reach the reference result, the
harness is at fault and the test arm means nothing.

## Phase 0 -- prove the interior slot (do this first and report it)

The conservator's point: the slot is not a per-piece decision, it is done in preprocessing. Prove it, do not
assume it.

1. Cite the mechanism in the code at the commit in use: classifyAndOrderPaper234 sets Surface_0 to the
   interior face (mesh_processing_headless.cpp), and the writer names Surface_0 -> Breakline_0
   (edgeline_extraction_headless.cpp, the rename block). Give file:line for both.
2. For each of the 8 Pot A pieces in the staged bundle, measure which of our two surfaces is the physical
   interior -- concavity test, mean(n . r) with r pointing away from the axis, report the number per piece --
   and confirm Breakline_0 rides that surface (median distance of its points to it).
3. Confirm the classify step actually ran per piece: the [PAPER-234] classify line in the mesh log and the
   axis file staged. Without SFS_AXIS_FILE the step silently keeps size order (ticket 277); that is the only
   mechanism by which the slot can be wrong.

Verdict line: "8/8 our Breakline_0 rides the interior face" or the exception named with numbers.

## Phase 1 -- the seating run

- Assembler: the structure-from-sherds-pp repo (Spartan canonical checkout sfs_main/sfspreproc-docker;
  misleading name -- it is the ASSEMBLY code). Read that repo's AGENTS.md and hpc/README.md before starting;
  the documented loop is push, pull_and_sbatch, job_status, fetch_artifacts.
- Pot A is the object: 8 pieces, full-resolution meshes, the authors' axes, and a ground-truth graph
  (data_path.h references Ground Truth/Pot_A_simple_graph.txt).
- Scored numbers to report per arm: sherds seated out of 8, joins correct out of 15, plus the run's own
  totals. Reference on this object with the authors' lines: 8/8 and 15/15.
- If a swap appears to be needed to get a result, STOP and report: by the Phase 0 argument a swap is a bug
  signal now, not a step (FIXES-LEDGER section R).

## Constraints

- No source edits in either repo, no parameter sweep, no new threshold. This ticket measures.
- Never "build.sh --target nurbs" in SfSpp_preprocessing (it compiles the pre-247 duplicate at
  original_nurbs_preprocessing/); build from a pushed commit with git archive + cmake as tickets 288/294 did.
- One run directory per run under /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/
  with run.json + submit.sbatch + logs/ + out/, and an index row (verdict and human_note left EMPTY for the
  lead). Delete staged geometry at the end and say what you deleted.
- No worktrees on Spartan, no copies of either tree, no edits in the canonical checkout.
- Do not touch C:/PR/worktrees/... (none is in use) and do not write to any other clone.

## Acceptance

1. Phase 0 verdict with per-piece numbers and the two code citations.
2. Phase 1 both arms with seated sherds / joins and the reference beside them, each with its runid and jobid.
3. Every input path plus md5 recorded (mesh, axis, breakline per piece per arm).
4. An honest statement of what the result does and does not settle -- in particular, that Pot A is 8 pieces of
   one pot, so it is a readiness check, not a corpus result.
