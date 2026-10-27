# 36: The adaptive spacing without the count scaling, on the honest normals

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 36-adaptive-spacing-with-the-honest-normals, in /c/PR/worktrees/sfs/36
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

The conservator's standing instruction since the start of the Juglet work: **a hard-coded metric like the
0.6 mm sampling step must be adaptive**, or the cloud on a small sherd is too sparse to mean anything.

That was built (ticket 22: `SFS_SPACING_POLICY=piece`, S = min(0.6, max(s0, diag/N))) but it is **OFF by
default**, and every arm run since — tickets 24, 29, 30, 32, 33, 34 — used the shipped literal 0.6 mm. So the
arithmetic quoted to him ("piece 2 turns 27-51 deg per 0.6 mm step") is arithmetic **at the fixed step**, and
he is right to refuse it.

What has already been measured, and must not be re-run:

- Ticket 22's grid (117 cells) DID include adaptive spacing with the counts **not** scaled — arms
  `C2_100`, `C2_200`, `C2_400` (SFS_SPACING_POLICY=piece, SFS_SPACING_SAMPLES=100/200/400, no
  SFS_COUNT_SCALE). Verified in
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0352_d4f2187_p22-analysis/out/measure_juglet.tsv`:
  **Juglet_Piece_2 and Juglet_Piece_9 are NA (no surface) in all thirteen arms**, including those three.
  The adaptive step did refine the clouds (piece 1 went 3580/12092 -> 10800/15780 in C2_200), and Pot A stayed
  8 of 8 two-surface with the bar met in C2_200 — the refinement itself is not what broke anything.
- BUT every one of those arms used the pipeline's **re-estimated** normals. The honest carry
  (`SFS_NORMAL_SOURCE=input`, `SFS_NORMAL_CARRY=nearest`) landed only in ticket 34, and it was never tried at
  adaptive spacing.

That combination — **adaptive spacing + honest normals + counts unscaled** — has never been run. It is the
configuration the conservator has been asking for, and this ticket tests it.

## Arms

Every arm prints its own `[SPACING-22]`, `[NORMAL-33]`, `[FLOOR-23]`/`[COUNT-22]` and `[STATUS-23]` lines.
No source change is needed: all five switches already exist on main (tickets 22, 23, 33, 34). If any of them
does not behave as documented, stop and report — do not patch the source.

| arm | spacing | counts | normals | write gate |
|---|---|---|---|---|
| **A** | today: fixed 0.6 mm | today (minCluster 50) | re-estimated (today) | pair only (today) |
| **A2** | repeat of A (determinism control) | | | |
| **B** | `SFS_SPACING_POLICY=piece` `SFS_SPACING_SAMPLES=200` | **unscaled** (leave `SFS_COUNT_SCALE` unset) | re-estimated | pair only |
| **C** | as B | unscaled | `SFS_NORMAL_SOURCE=input` `SFS_NORMAL_CARRY=nearest` | pair only |
| **D** | as C | unscaled | as C | `SFS_SINGLE_CLUSTER=write` |

Pieces: **Juglet 1, 2, 3, 5, 7, 9** and **Pot_A 01-08** = 14 pieces x 5 arms = **70 cells**.

## The deciding readings

1. **Piece 2 and piece 9 under arm B and arm D** — any surface at all, and if any, its point count, 2 mm
   coverage, extent in mm, and folded angle to the mesh. These are the two that have never produced a face.
2. **The sampling step actually used, per piece per arm** (`[SPACING-22] ... s0MM= ... S= ...`), beside the point
   count entering clustering. The refinement must be visible as a number, not assumed.
3. **Pot A 8 of 8 two-surface, bar met, in every arm.** If adaptive spacing breaks the sample pot, that decides
   against making it the default.
4. **Pieces 1, 3, 5, 7** — do their surfaces keep or improve against arm A's known counts (3580/12092, 268 single,
   679 single, 1012/829)?
5. **The normal fold-to-mesh** per piece under B (re-estimated at the finer spacing) against A and C — ticket 33
   found the averaging ball, not the source, drives this, so this cell shows whether refining alone improves it.

## Acceptance criteria

1. All 70 cells attempted; `mesh_exit` recorded for every one; every run directory has run.json, submit.sbatch,
   logs/ and out/.
2. Per-cell table with: arm, piece, S used, points into clustering, clusters at each retry, floor and its source,
   final cluster sizes, outcome, surface point counts, 2 mm coverage, extent, folded angle to mesh.
3. Pot A: 8 of 8 in every arm, with the pair statistics (along / across / coincidence) on the ticket-30 ruler.
4. Defaults unchanged: arm A with no switches must reproduce ticket 34's recorded numbers on the pieces that
   write surfaces (piece 1 1422/8147 under the honest-normals arm is NOT the control — the control is
   the shipped default: 3580/12092, 182/732, 608/1016, 1012/829).
5. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT.
6. Geometry deleted behind a counted record written before the delete; surfaces and logs kept for the lead.
7. Index rows appended, 6 fields, `verdict` and `human_note` EMPTY.

## Limits

Two jobs maximum, compute nodes only. CRLF-check every script; do not use `xargs -n 2` over a two-field list;
read binary PCD and varying-column PLY defensively.

## What this cannot settle

It cannot say what the right sampling step is in principle — only what this particular adaptive rule does at
N=200. It cannot rescue a sherd whose surface turns faster than any threshold the pot can tolerate; that is a
separate question. And a surface produced here is not yet a face: the along/across test still decides that.
