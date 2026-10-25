# Ticket 298 - assemble all ten pots with our own input, and with the authors' input

Status: in-progress
Working in: chat on Thinkbook16 (2026-10-26)
Branch: 298-assemble-all-pots, in /c/PR/worktrees/sfs/298
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("let's test all pots with our own input, and see if output match author's")

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

## Phase 0 - result (2026-10-26): inventory complete, nothing submitted yet

### Where these facts come from

- The header was extracted from the container, not read off a laptop copy:
  `/opt/sfs-pristine/class/data_path.h` -> `298-stage/data_path.pinned.h`, 257070 B,
  md5 `a244382311cb5d81f8bbf4ba4d823b47`, 6288 non-blank lines, inside
  `sfs_main/sfs_pristine_assembly.sif` (upstream 9195c0167e2077a564bd7c91156063252feeb506).
- **The line numbers in the What-exists section above came from a DIFFERENT header.**
  `C:/PR/structure-from-sherds-pp/class/data_path.h` is 6948 lines and carries a
  `POT_A_ORIG` block the pinned tree never had; the pinned file is 6607 lines. Every line
  cite below is the pinned one.
- Per-piece availability: `presence_scan.sh` run in the corpus (a copy sits in
  `.scratch/pota-repro/298/`). Block arrays: parsed out of the pinned header.
  Machine-readable result: **`.scratch/pota-repro/298/inventory.tsv`** (20 columns,
  one row per pot, tab separated, with the column definitions in its leading comment).

### Inventory (one row per pot; "none" = empty set)

| pot | block #define line | SHARD | active | corpus pieces | block - corpus | corpus - block | mesh | gt_graph_path | GT T for active slots | GT graph shape |
|-----|--------------------|-------|--------|---------------|----------------|----------------|------|---------------|------------------------|----------------|
| A | 1379 `#define POT_A` | 8 | 8 | 8 | none | none | plain `_Mesh.obj` | yes, exists | 8 / 8 | 8x8, 30 nz |
| B | 1478 | 9 | 9 | 9 | none | none | plain `_Mesh.obj` | yes, exists | 9 / 9 | 9x9, 30 nz |
| C | 1584 | 4 | 4 | 6 | none | 05, 06 | `_Mesh_DS.obj` | yes, exists | 4 / 4 | 4x4, 10 nz |
| D | 1650 | 29 | 29 | 32 | none | 30, 31, 32 | `_Mesh_DS.obj` | yes, exists | 28 / 29 (22) | 29x29, 138 nz |
| E | 1917 | 31 | 31 | 34 | none | 32, 33, 34 | `_Mesh_DS.obj` | yes, exists | 31 / 31 | 31x31, 124 nz |
| F | 2201 | 7 | 7 | 7 | none | none | `_Mesh_DS.obj` | yes, exists | 6 / 7 (07) | 7x7, 18 nz |
| G | 2292 | 7 | 7 | 7 | none | none | `_Mesh_DS.obj` | yes, exists | 7 / 7 | 7x7, 20 nz |
| H | 2382 | 11 | 11 | 11 | none | none | `_Mesh_DS.obj` | yes, exists | 11 / 11 | 11x11, 34 nz |
| I | 2504 | 30 | 30 | 30 | none | none | `_Mesh_DS.obj` | yes, exists | 27 / 30 (28, 29, 30) | 30x30, 130 nz |
| J | 2779 | **19** | **11** | 19 | none | 09 (slot off), 13-19 | `_Mesh_DS.obj` | yes, exists | 10 / 11 (09; 12 never read) | **11 rows x 12 cols**, 42 nz |

Active slots total **147** (A8 B9 C4 D29 E31 F7 G7 H11 I30 J11); declared slots 155.

### Which pots run as-is, which need wiring

**All ten run AS-IS**: every block declares `file_path[]`, `obj_path[]`, `axis_path[]`,
`surface_in[]`, `surface_out[]`, `gt_T_path[]` and `gt_graph_path[1]`, and for all 147 active
slots the axis, both surfaces, `Breakline_0` and a released point cloud are present in the corpus,
so no block needs a line filled in and no piece needs a derived cloud. **What needs wiring is only
the compile-time selector** (the pinned header ships `#define POT_A` at line 9 and the other nine
commented at lines 10-19) **and the bundle root**, which is `path = "/Dataset/" + data_type` with
`data_type = "SfS_pp/"` (pinned lines 32 and 35) and is therefore chosen by what the job mounts at
`/Dataset/SfS_pp` -- no source edit at all.

### Defects and mismatches, each with its evidence

1. **The ticket's POT_D claim is false on the pinned tree.** The POT_D block (line 1650) does
   declare `string gt_graph_path[1];` and sets it to `Ground Truth/Pot_D_simple_graph.txt`,
   which exists (10 lines, 29x29). No pot needs edit (b) from Phase 2.
2. **POT_J is inconsistent in the authors' own release.** `#define SHARD_NUMBER 19` at 2779 but
   the arrays hold 12 entries; `shard_on_off` is `TTTTTTTTFTTT` (index 8 = Piece 09 false);
   its graph has **11 lines but 12 values per line**, with the 12th column carrying 2 nonzeros.
   The shim sizes the matrix from the number of LINES (11) and reads 11 values per line, then reads
   `Pot_J_Piece_1..11_T.txt`; so **slot 11 (J12) is active but has no GT edge and is never given a
   GT transform**, and slot 8 (J09) is off.
3. **Five GT transforms inside active blocks do not exist**: `Pot_D_Piece_22_T.txt`,
   `Pot_F_Piece_7_T.txt`, `Pot_I_Piece_28_T.txt`, `Pot_I_Piece_29_T.txt`,
   `Pot_I_Piece_30_T.txt` (plus `Pot_J_Piece_9_T.txt` for the switched-off slot). Consequence
   measured in the pinned source, not guessed: `Trans::Read` (`class/data_structure.cpp:633`)
   leaves `T_` as the identity when the stream fails to open, and the shim's GT loop
   (`hpc/tools/main_pristine_batch.cpp:112-145`) calls `GT_trans[j].Read(gt_T_path[j])` for every
   `j < num_raw` regardless of `shard_on_off`. Those pieces are **assembled and then scored
   against an identity reference**. This is the released state; it is recorded, not repaired.
4. **Block piece sets are the authors' evaluation sets, and three of them include pieces the paper
   says were excluded**: F07 is in POT_F, I28-I30 in POT_I, J12 in POT_J, while the paper's Table V
   headers say F(6), I(27), J(11). Assembly therefore runs on 147 pieces, the paper's columns cover
   143. Both facts stay in the deliverable table.
5. **16 corpus pieces are outside the active blocks** -- C05, C06, D30-D32, E32-E34, J09 (released,
   but its slot is switched off), J13-J19. Fifteen of them (all but J09) have **no released point
   cloud**, so `scripts/stage_piece.sh` would refuse them ("Refusing to derive one"); J09 has a
   cloud and surfaces but no GT transform. None is staged.
6. **Pot C 07 exists as a mesh only** -- no axis, no surfaces, no breakline, no GT transform, no
   block slot. It is not a piece of this campaign. (Corpus counts in the ticket: Mesh 164, Axes 163
   -- the missing axis is exactly this one.)
7. **Every block names `Surfaces/Pot_X_Piece_NN_Surface_F.pcd` and the corpus contains none**
   (0 files match `_Surface_F`). Ticket 296 established `LoadSurface` tolerates the absence, so
   the "Could not open file" gate keeps its allow-list for `_Surface_F.pcd` and nothing else.
8. **Line 13 is `// #define POT_E` with a space** where the other eight are `//#define POT_X`.
   The selector flip must accept both spellings and must be token-anchored (`POT_A` must not match
   `POT_A_B_C`, `POT_A_B_F_G_H`, `POT_A_B_C_D_E`, `POT_All` at lines 20-26).
9. **Pot A and Pot B are plain meshes; C-J are the authors' downsampled `_Mesh_DS.obj` only.**
   Both arms of a pot use the same mesh file, so every comparison is fair internally, but C-J
   absolute numbers are not comparable with a full-resolution table and the ticket must say so in
   the deliverable.

### Three plan changes forced by Phase 0

1. **No INFRA edit is needed for the arm.** The bundle root is decided by the bind mount at
   `/Dataset/SfS_pp` (recipe already used by 296), so permitted edit (a) is not made; and no block
   lacks `gt_graph_path`, so permitted edit (b) is not made either. **The assembler source is
   untouched.** The per-pot selector is applied to a throwaway 13 MB copy of the pinned tree inside
   the job's `/tmp` (`cp -a /opt/sfs-pristine /tmp/sfx`; only `main.cpp` includes
   `class/data_path.h`, so every other object is pot-independent), never to `/opt/sfs-pristine`,
   which is mounted read-only.
2. **Pot B's cloud is not re-sampled with CloudCompare.** All nine Pot B pieces have the authors'
   *released* cloud in `Point/Pot_B/`, so the OUR arm feeds our mesh+edge chain the SAME cloud the
   authors used. That is a tighter control than a re-derived cloud (input identical, algorithm the
   only difference) and it removes the unseeded sampler from the comparison. No block piece in any
   pot needs a derived cloud, so `cc_mesh_to_pcd.sh` is not used at all.
3. **Cap and resume rule, stated before the campaign**: `--time=04:00:00` per arm job (Pot A's
   8-piece arm took ~3 min wall including a 1m48s in-container build; the largest pot has 31
   pieces, ~4x the seating work, so 4 h is ~50x headroom), and a run directory whose
   `out/Result/*Acc.txt` already carries two accuracy lines is **scored and never re-run**.

### Job plan (31 run directories, each with an `runs/index.tsv` row, verdict and human_note left empty)

| run tag | jobs | what it does |
|---------|------|--------------|
| `p298-build` | 1 | builds `MeshPreprocessingHeadless` + `EdgeLineExtractionHeadless` from the pushed commit (git archive), records the commit and both binary md5s |
| `p298-prep-POT_X` | 10 | per piece: `stage_piece.sh` (authors' released cloud, symlinked) -> mesh stage with `SFS_AXIS_FILE` (must print the `[PAPER-234] classify` line) -> edge stage; exports `out/geom/<Piece>.{S0,S1,Bl0,Bl1}` = OUR bundle |
| `p298-POT_X-oursd`, `p298-POT_X-authb` | 20 | assembler, one pot per job, arm = what is mounted at `/Dataset/SfS_pp` |

The two arm jobs of a pot are submitted with `--dependency=afterok:<prep job>`; the 20 arm jobs run
two at a time.

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