# Ticket 298 - assemble all ten pots with our own input, and with the authors' input

Status: ready-for-agent
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("let's test all pots with our own input, and see if output match author's")
Working in: unassigned
Branch: 298-assemble-all-pots

## Why

Ticket 296 proved the seating chain on ONE pot (Pot A, 8 pieces) with both arms at 8/8
sherds and 15/15 joins. Pot A saturates, so it cannot rank two preprocessing bundles. The
conservator now wants the same question asked at corpus scale: for every pot, assemble once
with OUR preprocessing (our Surfaces + our Breakline_0) and once with the AUTHORS' corpus
bundle, on identical meshes, axes, assembler and settings, and see whether the output
matches the authors'.

This is the join-level question behind intent question E1. It is the first test in this
project whose unit is a POT rather than a lane, and its numbers (sherds seated, joins
recovered) are the ones a conservator can act on.

## What exists (verified by the lead on 2026-10-26, re-verify in Phase 0)

- Corpus /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/:
  Mesh/ 164 files (A8 B9 C7 D32 E34 F7 G7 H11 I30 J19), Axes/ 163, Surfaces/ 326 (= 163 x 2),
  Breaklines/ 326, Ground Truth/ holds Pot_A..Pot_J_simple_graph.txt for ALL TEN pots plus
  per-piece Pot_X_Piece_N_T.txt transforms (Pot_D has 28 of 29; H and J have all).
- Our own bundles DO NOT EXIST for any pot except Pot A (a single 296 prep tree). Runs carry
  only 10 Surface_0.xyz files and no Breakline_0.pcd. SfSpp/bundles/ holds only README.txt.
  So the "ours" arm must be REGENERATED for every pot: CloudCompare sample from the surviving
  OBJ (cc_mesh_to_pcd.sh), then mesh stage, then edge stage.
- For pots C..J only the DOWNSAMPLED mesh survives (_Mesh_DS.obj); Pot A and Pot B have plain
  full-resolution OBJ. Both arms of a pot must use the same mesh, so the comparison is fair,
  but absolute numbers for C..J are not comparable with the paper's full-resolution table.
- The assembler is pinned at /opt/sfs-pristine (upstream 9195c016) with the INFRA shim
  hpc/tools/main_pristine_batch.cpp in C:/PR/structure-from-sherds-pp; ticket 296 proved it
  runs headless and scores. Config is COMPILE-TIME: class/data_path.h, selected by #define
  POT_X, with SHARD_NUMBER and arrays file_path[] (Breakline_0 per piece), surface_in[]/
  surface_out[], axis_path[], obj_path[], gt_graph_path[]. path = "/Dataset/" + data_type
  and data_type = "SfS_pp/" (class/data_path.h:39-46), so the bundle root is a single
  string that a bind mount at /Dataset/SfS_pp can point at either arm.
- Not every pot block carries gt_graph_path: the POT_D block (class/data_path.h:1993,
  SHARD_NUMBER 29) has none, so a POT_D build has nothing to score against. Phase 0 must
  list which of the ten blocks do and do not.
- Piece counts do not match the corpus for every pot (Pot D: 32 meshes vs SHARD_NUMBER 29;
  Pot E: 34 meshes vs a 31-piece block). Phase 0 decides the authoritative piece list per pot
  (the AXES set is 163, one per piece) and reports every mismatch rather than guessing.

## Phase 0 - inventory, no compute (do this first, report before spending GPU/CPU hours)

Write out/inventory.tsv with one row per pot (A..J) and these columns:

1. block #define name and the line of its #ifdef in class/data_path.h;
2. SHARD_NUMBER in that block;
3. whether the block declares gt_graph_path, and whether that file exists in the corpus;
4. the block's own piece list (basename of each file_path[] entry) and its count;
5. the corpus piece list from Axes/ (or Surfaces/) for the same pot, and its count;
6. set difference block-vs-corpus in both directions, named piece by piece;
7. mesh availability per piece: plain .obj or _Mesh_DS.obj only;
8. whether the three arrays a pot needs (axis_path, obj_path, gt_graph_path) are populated.

Then state, in two sentences, which pots can be run AS-IS and which need wiring.

## Phase 1 - harness and pilot on ONE pot (Pot B, 9 pieces, plain meshes)

Goal: prove the whole chain end to end on our own input before spending the campaign.

1. Regenerate OUR bundle for Pot B from the surviving OBJ meshes: for each piece, sample the
   cloud exactly as the preprocessing repo's cc_mesh_to_pcd.sh does, run the mesh stage with
   SFS_AXIS_FILE set (the stage now exits 42 without it -- ticket 277), then the edge stage.
   Use the shipped defaults; no sweeps; the binary must be built from a pushed commit with
   git archive (NEVER 'build.sh --target nurbs': it compiles the pre-247 duplicate).
2. Stage the authors' bundle for Pot B from the corpus (Surfaces/, Breaklines/, Ground Truth/,
   Axes/, Mesh/) with symlinks.
3. Run the assembler twice on identical meshes/axes/settings: arm OURSD with our Surfaces +
   our Breakline_0, arm AUTHB with the corpus Surfaces + corpus Breakline_0. Same binary,
   same seed-visible settings, same wall-clock cap. Only the bundle root differs.
4. Score both arms from the assembler's own output: sherds seated (the FIRST 'Sherd accuracy'
   line) and joins recovered (the SECOND one -- the assembler prints the same string twice,
   data_structure.cpp:1004-1005). Quote both lines verbatim in the ticket.
5. GATE: the AUTHB arm must run and score without error, and OURSD must run and score. Do not
   invent a numeric bar; report what each arm produced. If the chain fails anywhere -- missing
   file, unreadable config, crash, empty result -- STOP and report the exact error; do not
   patch the algorithm to make a number appear.

## Phase 2 - the campaign, all ten pots (only after the Phase 1 gate passes)

For every pot A..J, both arms, in the same form as the pilot. Requirements:

- one run directory per arm per pot under SfSpp/runs/, plus one index.tsv row each;
- a per-pot wall-clock cap (state it) and a resume rule: a pot already scored is not re-run;
- report every pot even if it fails, with the failure's first error line;
- our bundles for all ten pots are KEPT (they cannot be regenerated byte-identically: the
  sampling and the mesh stage are unseeded -- ticket 284's lesson); staged CEILING trees and
  any intermediate clouds are deleted with a counted GEOMETRY_DELETED record;
- no source edits beyond: (a) an environment override of the bundle root in the INFRA shim
  (hpc/tools/main_pristine_batch.cpp) so one binary can serve both arms, and (b) filling in a
  missing gt_graph_path line for a pot block. Both are INFRA changes and must be listed in the
  ticket with their diff. No algorithm, threshold, weight or ordering change anywhere.

## Deliverable

One table, one row per pot: pot | pieces | our arm sherds/joins | authors' arm sherds/joins |
the paper's published numbers for that pot (quote the table verbatim from
C:/PR/papers/text/sfspp-2502.13986v1.md with line numbers), plus a short paragraph per pot
saying whether our input matched the authors' output, and where it fell short if it did not.

## Constraints

- Do not score against Pot C 03 Breakhine_1 (struck by the conservator, ticket 295) and do not
  present Pot J 09's lane as a reference (his ruling). Neither affects assembly, which reads
  Breakline_0 only -- but do not resurrect them in any table.
- Pot C 01 is a KNOWN-DEFECTIVE input (scan gap; project AGENTS.md, "Corpus caveats"): if Pot C
  misbehaves, say so and name the gap as the first suspect.
- The assembler is pinned: upstream 9195c016 + the INFRA shim. Do not upgrade, patch or
  re-derive it.
- Heavy work on Spartan compute nodes only; laptop for reading logs and staging.
- Write results into this ticket; leave Status at in-progress for the lead. Lead commits.

## Acceptance

1. Phase 0 inventory complete, every mismatch named, and the runnable-vs-needs-wiring split stated.
2. Phase 1 pilot: both arms scored on Pot B, both score lines quoted verbatim, and the binary's
   source commit named.
3. Phase 2: a row for every one of the ten pots, with the paper's own numbers beside ours.
4. Every staged tree accounted for; our ten bundles retained; run directories and index rows present.
5. Any defect found is stated with its evidence, not smoothed over.
