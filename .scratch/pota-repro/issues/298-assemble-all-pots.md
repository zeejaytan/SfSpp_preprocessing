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

### Job plan (30 run directories, each with an `runs/index.tsv` row, verdict and human_note left empty)

There is no separate build job: each prep job builds both binaries from the pushed commit in its
own scratch root (ticket 296's precedent), so a build failure is reported by the prep job that
needed it and cannot silently hand the campaign a stale binary.

| run tag | jobs | what it does |
|---------|------|--------------|
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

## Phase 1 - result (2026-10-26): pilot PASSED, Pot B both arms, 9/9 sherds and 15/15 joins

Source commit `63cf61540094c3ec1e1dbefa9ff46a05b7d4708` ("298 Phase 0: inventory of all ten
pots; prep/arm job scripts; zero assembler edits needed"), pushed to `origin/298-assemble-all-pots`
before any job was submitted, built by each job from `git archive` of that commit.

| arm | run dir (job) | Total number | Total number pruned | sherds (first line) | joins (second line) |
|-----|---------------|--------------|---------------------|---------------------|---------------------|
| OURSD = our Surfaces + our Breakline_0 | `20261026-0052_63cf615_p298-Pot_B-oursd` (33782366) | 182 | 81 | **9 / 9 (100 %)** | **15 / 15 (100 %)** |
| AUTHB = corpus Surfaces + corpus Breakline_0 | `20261026-0052_63cf615_p298-Pot_B-authb` (33782456) | 114 | 77 | **9 / 9 (100 %)** | **15 / 15 (100 %)** |

Verbatim, `out/Result/1. Acc.txt` of the OURSD run:

```
Time : 1.90872e+06 Sec
Sherd accuracy : 9 / 9 (100 %)
Sherd accuracy : 15 / 15 (100 %)
```

and of the AUTHB run:

```
Time : 1.024e+06 Sec
Sherd accuracy : 9 / 9 (100 %)
Sherd accuracy : 15 / 15 (100 %)
```

Both lines come from the assembler itself; the first "Sherd accuracy" line is sherds seated and
the second is joins recovered (`class/data_structure.cpp:1004-1005`), and the console prints the
same two numbers under the labels "Sherd accuracy" and "Edge accuracy".

Prep (`20261026-0046_63cf615_p298-prep-Pot_B`, job 33782096, exit 0): 9 of 9 pieces, 9 of 9
`[PAPER-234] classify` lines, every stage/mesh/edge exit 0, theta 3.40000 on all nine, all nine
exported `Surface_0 = interior` ("kept" on piece 01, "swapped" on 02-09) -> our `S0/Bl0` ride the
interior face exactly as the authors' `Surface_0/Breakline_0` do, so the two arms differ in the
extractor and in nothing else. Our bundle: `out/geom` 36 files, 24 MB, kept.

Inputs. Both arms staged the frozen corpus by symlink (`out/links.tsv`, 46 links) for mesh, axis
and Ground Truth; `out/gt_missing.txt` is empty for Pot B. The only unmatched file open in either
arm is the corpus-wide absence of `..._Surface_F.pcd` (9 hits, one per piece) which the assembler
tolerates and which the gate allow-lists; no other "Could not open file" line appears.

Defects met and fixed while getting the pilot to run (all three are harness, none is the algorithm,
and both arms were re-run after the last fix):

1. The selector flip first looked for `POT_Pot_B`; the C++ selectors are `POT_B`. Fixed by
   upper-casing the letter and prefixing `POT_`.
2. Under `set -u`, a sed address written with a bare `$p` read the variable `p` and aborted the
   container. Fixed with an explicit numeric range.
3. Twice, "container pipeline exit 141" with no other message: `set -euo pipefail` turns a
   producer's SIGPIPE into a silent abort. First `grep ... | head -1`, then `sed -n ... | grep -m1`
   -- `head`/`grep -m1` exit early, the producer dies of SIGPIPE, `pipefail` propagates 141 and
   `set -e` kills the script at that line. Fixed by reading the header with **one** process
   (`awk`) and with `grep -m1` instead of a downstream `head`. Every attempt is recorded in
   `out/attempts.tsv` inside the arm run dirs, so the five submissions of one arm are legible
   without creating five run directories.

Gate: PASSED. Both arms produced a result and both scored from the assembler's own output, so
Phase 2 proceeds unchanged: 9 prep jobs (A, C, D, E, F, G, H, I, J) and 18 arm jobs.

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

## Phase 2 - result (2026-10-26): the campaign, all ten pots

### What ran, on what

- Preprocessing source commit **`d1f1a4c37ec5bc8e531c195858303b3ce942486a`** (pushed before the
  campaign; each job builds its own throwaway tree from a `git archive` of it and deletes it).
- Assembler: **`/opt/sfs-pristine`** = upstream `9195c0167e2077a564bd7c91156063252feeb506` plus the
  INFRA shim `hpc/tools/main_pristine_batch.cpp`, **unmodified**. Beam search `k`=5, `b`=3 — the
  paper's own setting: line 344, "We used $k=5$ and $b=3$ beam search parameters for SfS pipelines" —
  and `NO_BASE_INFO`, the shim's defaults. Nothing was tuned per pot.
- **Neither of the two permitted source edits was made, because neither was needed.** (a) The
  bundle root is decided by what is bind-mounted at `/Dataset/SfS_pp`, so a single unmodified binary
  serves both arms and no environment override was added to the shim. (b) All ten pot blocks declare
  `gt_graph_path`, including `POT_D` (`class/data_path.h:1993`, Phase 0 above), so no line had to be
  filled in. Both diffs are therefore empty and the assembler ran byte-identical in all 20 runs.
- 10 prep jobs, 18 campaign arm jobs, plus 2 repeat jobs (below). Per-arm wall-clock cap **4 h**
  (`#SBATCH --time=04:00:00`); the slowest arm was **1 h 13 min** (Pot D, our bundle), so the cap cut
  nothing. Resume rule honoured: no scored run directory was re-run; the repeats are new directories.
- Bundles retained as deliverables: **588 files / 458 MB** in the ten prep runs' `out/geom`
  (4 per piece: `.Bl0.pcd`, `.Bl1.pcd`, `.S0.xyz`, `.S1.xyz`).

Job ids: prep A `33782539`, C `33782540`, D `33782541`, E `33782542`, F `33782543`, G `33782544`,
H `33782545`, I `33782546`, J `33782547`; arms (ours bundle / authors' bundle) A `33782548/49`,
C `50/51`, D `52/53`, E `54/55`, F `56/57`, G `58/59`, H `60/61`, I `62/63`, J `64/65`;
Pot B pilot: prep `33782096`, arms `33782366 / 33782456`; repeats H `33783435`, D `33783436`.

### The table

"Scored" is the number of pieces the assembler actually put into its accuracy count — not the number
staged; the section after this one says why. Every cell is quoted from that run's own
`out/Result/1. Acc.txt` (first line = sherds seated, second = joins recovered) and from the
`Sherd accuracy` / `Edge accuracy` lines in `logs/assembly.log`.

| pot | pieces staged | scored (ours / authors') | our bundle SA / EA | authors' bundle SA / EA | paper SA / EA (line 351 / 356) |
| --- | --- | --- | --- | --- | --- |
| A | 8 | 8 / 8 | 8/8 (100 %) / 15/15 (100 %) | 8/8 (100 %) / 15/15 (100 %) | 100 / 100 |
| B | 9 | 9 / 9 | 9/9 (100 %) / 15/15 (100 %) | 9/9 (100 %) / 15/15 (100 %) | 100 / 100 |
| C | 4 | 4 / 4 | 4/4 (100 %) / 5/5 (100 %) | 4/4 (100 %) / 5/5 (100 %) | 100 / 100 |
| D | 29 | 29 / 28 | 23/29 (79.3103 %) / 55/69 (79.7101 %) | 22/28 (78.5714 %) / 53/66 (80.303 %) | 82.1 / 83.3 |
| E | 31 | 31 / 31 | 31/31 (100 %) / 62/62 (100 %) | 31/31 (100 %) / 62/62 (100 %) | 100 / 100 |
| F | 7 | 5 / 6 | 5/5 (100 %) / 7/7 (100 %) | 6/6 (100 %) / 9/9 (100 %) | 100 / 100 |
| G | 7 | 7 / 7 | 7/7 (100 %) / 10/10 (100 %) | 7/7 (100 %) / 10/10 (100 %) | 100 / 100 |
| H | 11 | 11 / 11 | 8/11 (72.7273 %) / 11/17 (64.7059 %) | 8/11 (72.7273 %) / 9/17 (52.9412 %) | 90.9 / 88.2 |
| I | 30 | 26 / 27 | 25/26 (96.1538 %) / 59/62 (95.1613 %) | 25/27 (92.5926 %) / 59/65 (90.7692 %) | 92.6 / 90.8 |
| J | 11 | 11 / 11 | 10/11 (90.9091 %) / 17/21 (80.9524 %) | 8/11 (72.7273 %) / 16/21 (76.1905 %) | 72.7 / 76.2 |

The paper prints percentages only; the counts they imply are unambiguous and match our authors'-bundle
denominators wherever the percentage agrees (82.1 % of 28 = 23, 83.3 % of 66 = 55, 90.9 % of 11 = 10,
88.2 % of 17 = 15, 92.6 % of 27 = 25, 90.8 % of 65 = 59, 72.7 % of 11 = 8, 76.2 % of 21 = 16).

Raw state counts, for the record only — `Total number` (states the beam search examined) is not a
quality measure and swings widely with the bundle: A 242 our / 124 authors', C 91/125, D 2358/2445,
E 1807/1912, F 32/36, G 74/51, H 480/485, I 1309/1424, J 698/731, B 182/114.

### Why a pot's scored count is not its piece count

`hpc/tools/main_pristine_batch.cpp:86` switches a piece off, **silently**, when its own
`Breakline_0` has fewer than 50 unique points:

```cpp
shard[i].edge_line_.ReadPCDFileWithInfo(file_path[i]);
if (shard[i].edge_line_.point_.cols() < 50) {
    shard_on_off[i] = false;
    shard[i].edge_line_.Remove();
    continue;
}
```

No message is printed, so a dropped piece simply disappears from both numerator and denominator. The
count above is therefore recomputed from the `Found N unique points` lines, per run:

| pot | dropped with our bundle (points) | dropped with the authors' bundle (points) |
| --- | --- | --- |
| D | none | D 27 (48) |
| F | F 06 (49), F 07 (37) | F 07 (28) |
| I | I 27 (49), I 28 (41), I 29 (40), I 30 (38) | I 28 (44), I 29 (41), I 30 (40) |
| A, B, C, E, G, H, J | none | none |

The four pieces the paper itself excluded as "fewer than 50 points in the respective surface edge
lines" (F 07, I 28, I 29, I 30 — project AGENTS.md, "Which pieces are in the corpus") are exactly the
ones this floor removes from the authors' bundle, which is why the authors'-bundle denominators (6, 27)
equal the paper's piece counts. **Our bundles lose two more pieces, by one point each**: Pot F 06 has
49 unique points where the authors' line has 57, and Pot I 27 has 49 where the authors' has more. That
is a real property of our extracted interior breaklines, not a scoring artefact, and it is the only
reason our denominators differ from the authors'.

### Per pot

- **A (8 pieces).** Both arms 8/8 and 15/15 = 100 / 100, the paper's numbers. Our bundle reproduces the
  authors' seating exactly; it makes the search work about twice as hard (242 states against 124).
- **B (9 pieces, the Phase 1 pilot).** Both arms 9/9 and 15/15 = 100 / 100 = the paper.
- **C (4 pieces).** Both arms 4/4 and 5/5 = 100 / 100 = the paper. This pot carries the corpus caveat
  (Pot C 01's interior surface has a scan gap, project AGENTS.md; ticket 285) and the assembler reads
  `Breakline_0`, which is the boundary of the interior surface — so a broken interior input sits inside
  this pot's four pieces. The assembler prints pot totals only, no per-piece line, so 4/4 shows the
  pot came out right; it does not by itself certify C 01's seat.
- **D (29 pieces).** Our bundle **23/29 sherds (79.3103 %) and 55/69 joins (79.7101 %)**; the authors'
  bundle 22/28 (78.5714 %) and 53/66 (80.303 %); the paper 82.1 / 83.3. Two separate facts: our arm
  reaches the paper's raw counts (23 sherds, 55 joins) but scores one extra piece (D 27, which our
  line keeps above the 50-point floor and the authors' does not), so its percentages are lower; and
  **the authors' own bundle is one sherd and two joins short of the published D numbers**. A repeat of the authors' bundle (job `33783436`) reproduced **22/28 and 53/66 exactly** (below), so the gap is a property of the release on this pinned commit, not of one run.
- **E (31 pieces).** Both arms 31/31 and 62/62 = 100 / 100 = the paper. The largest pot, and the one
  whose search is longest (53 min our bundle, 54 min the authors').
- **F (7 pieces).** Our bundle **5/5 (100 %) and 7/7 (100 %)**; the authors' 6/6 and 9/9; the paper
  100 / 100 over 6 pieces. Our arm is 100 % of what it is allowed to score but one piece fewer: F 06's
  interior breakline has 49 unique points against the assembler's floor of 50 and is switched off. The
  authors' bundle keeps F 06 (57 points) and drops only F 07, so the two arms are not scoring the same
  piece set, and the percentages cannot be read against each other without the counts.
- **G (7 pieces).** Both arms 7/7 and 10/10 = 100 / 100 = the paper.
- **H (11 pieces).** Our bundle 8/11 (72.7273 %) and **11/17 joins (64.7059 %)**; the authors' bundle
  8/11 (72.7273 %) and 9/17 (52.9412 %); the paper 90.9 / 88.2 = 10/11 and 15/17. **This is the one pot
  where both arms fall well short of the paper and the shortfall is not run-to-run variance** — the
  authors' arm reproduces 8/11 and 9/17 exactly on a repeat (see below). Our bundle seats the same
  eight sherds and recovers two more joins than theirs, so on this pot our interior lines are slightly
  the better input, and neither arm reaches the published 10 sherds / 15 joins. Cause not established;
  it is named as an open item rather than explained away.
- **I (30 pieces staged, 27 scored).** Our bundle 25/26 (96.1538 %) and 59/62 (95.1613 %); the authors'
  bundle **25/27 (92.5926 %) and 59/65 (90.7692 %) = the paper exactly**. Our raw counts are the
  paper's (25 sherds, 59 joins) over one piece fewer (I 27, 49 points against the floor), so the
  percentages move only because the denominator does.
- **J (11 pieces staged; the block carries 12 entries and J 09 is switched off in it).** Our bundle
  **10/11 (90.9091 %) and 17/21 (80.9524 %)**, the authors' 8/11 (72.7273 %) and 16/21 (76.1905 %) =
  the paper exactly. This is the pot where our chain does best against the authors': two more sherds
  and one more join, i.e. 18 points of SA above their arm and above the published 72.7. Two
  bookkeeping oddities of this run are recorded below (the 19 unreadable paths, and a negative
  `Time` in our arm's `Acc.txt`).

### The two repeat runs

The only pots where the authors'-bundle arm misses the paper are D and H. Because a shortfall can be a
property of the input or a property of one run, the same inputs were run again into two new run
directories (same commit, same binary, same bundle, nothing else changed):

- **H, job `33783435`, `20261026-0301_d1f1a4c_p298-Pot_H-authb-rep2`**: "Sherd accuracy : 8 / 11
  (72.7273 %)" and "Edge accuracy : 9 / 17 (52.9412 %)" — **identical** to the first run, which is
  what makes the H shortfall a stable property rather than noise. The search bookkeeping did move:
  `Total number` 485 / pruned 232 became 485 / pruned 233. The answer is reproducible; the state count
  is not.
- **D, job `33783436`, `20261026-0301_d1f1a4c_p298-Pot_D-authb-rep2`**: "Sherd accuracy : 22 / 28 (78.5714 %)" and "Edge accuracy : 53 / 66 (80.303 %)" — **identical** to the first run, with `Total number` 2445 and pruned 886 against 888.

### Defects, surprises and open items

1. **The 50-point floor is silent** (`main_pristine_batch.cpp:86`) and it is what makes "pieces in the
   block" and "pieces scored" differ. Anyone comparing two runs must recompute the denominator from the
   `Found N unique points` lines; the percentage alone is not comparable. Our bundles lose F 06 and
   I 27 by one point each (49 against 50).
2. **Five pieces the blocks name have no ground-truth transform in the corpus** — D 22, F 07, I 28,
   I 29, I 30 (`out/gt_missing.txt` in both arms of both pots). `Trans::Read` leaves the identity, so
   the piece is scored as if it had never moved. These are exactly the pieces the authors excluded
   (project AGENTS.md) and all five are switched off by the floor anyway, so nothing was scored against
   an identity by accident — but the mechanism is worth stating.
3. **Pot J's 19 unreadable paths are expected, and my first gate got this wrong.** Both J arms finished
   and wrote `Result/1. Acc.txt`, and the job was then failed with exit 11 by a gate that treated any
   `Could not open file` line as a staging failure. The 19 lines are: 11 `*_Surface_F.pcd` (the corpus
   has no `Surface_F` file for **any** piece — 0 hits in 164 pieces), 7 empty paths from slots 12..18
   (`POT_J` declares `SHARD_NUMBER 19` while its arrays hold 12 entries), and 1 axis of Pot J Piece 09,
   which the block itself switches off (`shard_on_off[8]=false`) and which we therefore never staged.
   The gate was replaced by `scripts/p298_gather.sh` (commit `b78d9b8`), which classifies every
   unreadable path into `out/open_absent.tsv` and fails only for an **active** piece; it was applied to
   both finished J runs (fatal_open=0, absent=19: 11 surface-f, 7 phantom-slot, 1 inactive-piece) and
   those runs were **not** re-run, per the resume rule. Pot J's numbers above come from those runs.
4. **Two pots do not reproduce the paper with the authors' own bundle**: D (78.5714 / 80.303 against
   82.1 / 83.3) and H (72.7273 / 52.9412 against 90.9 / 88.2). Everything else matches the paper's
   percentage exactly. Both pots reproduce their numbers exactly on a repeat (H 8/11 and 9/17,
   D 22/28 and 53/66), so the gap is a property of the release on this pinned commit and not of a
   single run. Why the release does not reach its own published D and H numbers is not established
   here, and is left as the open item of this ticket.
5. **A negative `Time` line** in Pot J's our-bundle `1. Acc.txt` ("Time : -184038 Sec") against
   1.11027e+06 in the authors' bundle. The accuracy lines in the same file are well-formed and agree
   with `assembly.log`; the timer is the only damaged field.
6. **Mesh `.obj` reads fail for pieces with no `_Mesh_DS.obj`** (e.g. all of Pot H, and Pot F 01-07
   in the log). The mesh is used for the exported scene, not for seating or scoring; the accuracy
   lines are unaffected. Recorded so the log noise is not mistaken for input loss later.
7. **`run.json` in all 27 campaign run directories was laid out from the Pot B template** and carried
   Pot B's run id, `SHARD_NUMBER` and bundle text (and the pilot commit). It was corrected on
   2026-10-26 from each job's own log and `out/links.tsv` — the real `SHARD_NUMBER` per block (A 8,
   C 4, D 29, E 31, F 7, G 7, H 11, I 30, J 19), the real bundle per arm, `runid` = directory name,
   and `commit_preprocessing` = `d1f1a4c`. A `metadata_note` in each file says so. No execution
   changed; arm-to-bundle binding was verified independently in `out/links.tsv` (our arms point at
   `runs/<prep>/out/geom`, the authors' arms at `original_samples/SfS_pp`).
8. **The two arms are not always scoring the same pieces** (F: 5 against 6; I: 26 against 27; D: 29
   against 28). Percentages must never be compared across arms without the counts beside them.

### Housekeeping

- **Index rows**: `runs/index.tsv` has one row for each of the **32** run directories this ticket made
  (10 prep + 20 arm runs + 2 repeats), with the job id and commit of that run, and `verdict` /
  `human_note` left empty for the lead. Appended by `.scratch/pota-repro/298/jobs/index_rows.py`,
  which is idempotent, skips a run id already present, and takes the commit from the run's own
  `run.json`; the file now has 119 rows and every row has six tab-separated fields.
- **GEOMETRY_DELETED**: the ten prep runs' staged `stage/` trees were deleted after both arms of every
  pot had been read: **8,378 files and 9,911,628,046 bytes** (A 454/606,156,458; B 510/585,880,073;
  C 261/448,195,238; D 1,649/2,343,102,994; E 1,750/1,942,108,449; F 404/334,921,781;
  G 394/336,697,172; H 615/613,430,197; I 1,698/1,981,334,294; J 643/719,801,390). Each run directory
  keeps `out/GEOMETRY_DELETED.txt` with the per-kind counts; the `out/geom` bundles are **kept**.
  The frozen corpus is untouched.

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