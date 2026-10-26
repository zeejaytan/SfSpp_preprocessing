# 21: Did the pipeline regress since late September, or was the old 7-of-9 a different bundle?

**What to build:** the comparison that separates two things a number cannot tell
apart — our code changed and lost surfaces, or the older "7 of 9 produced" was
measured on a different bundle/stage and was never comparable. This is the
measurement-call versus method-call question, and it decides how the Juglet result
is described.

**Answers:** U19

**Blocked by:** none

**Status:** in-progress — evidence recorded (job 33836038, 2026-10-27), reading and verdict left to the lead
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 21-did-we-regress-or-was-the-old-bundle-different, in /c/PR/worktrees/sfs/21

## What is already established

- Today's code (commit `d8af9d2`, job **33834939**, run
  `20261027-0055_d8af9d2_p07-juglet-stage1`) produces Surfaces for **4 of 9**
  Juglet sherds: pieces 1, 4, 6, 7. Pieces 2 and 9 give 0 clusters, piece 5 gives 1,
  pieces 3 and 8 give 2 and the merge fuses them to 1.
- The older claim is at
  `C:/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/issues/07-end-to-end-acceptance.md:17-20`:
  "0 of 5 scorable touching pairs pass, 5 touching pairs unmeasurable (**pieces 3
  and 9 produce no surfaces** — single cluster after 30 loosened retries — and skip
  loudly)", from the 2026-09-30 run. That implies the other **7 of 9** did produce
  surfaces, and it names a different pair of absent pieces (3 and 9) than today's
  (2, 3, 5, 8, 9).
- That bundle is **gone**: the 2026-10-24 attic sweep carved the three
  `Juglet_Dataset_*` trees out whole and deleted the geometry; only
  `checkout-bucketc-20261024-record.tar.gz` survives, holding `SfS_pp/Ground Truth/`.
  Its last full write was 2026-09-25 14:37-14:40, three days BEFORE the
  interior/exterior classifier (ticket 04, commit `4513f00`, 2026-09-28; its parent
  is `f27c5e5`).
- Code commits available as replay targets, verified in this clone:
  `a41a91e` (last commit before 2026-09-26, the code that wrote the old bundle) and
  `28e470b` (2026-09-30, the code that produced the "7 of 9 / 0 of 5" reading).
- The nine input meshes are still on disk:
  `/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet/Piece01..09.obj`,
  vertex counts 24294, 2568, 3495, 3651, 6212, 5126, 8421, 4479, 2095.

## The two checks

**A — replay the same nine meshes through the older code.** Build the mesh stage from
`28e470b` first (that is the code behind the "7 of 9" reading), and only if it cannot
build or run, from `a41a91e`. Reconstruct the stage invocation by reading that
commit's own `main()` and `data_path.h` — **not** today's `submit.sbatch`, which
carries the axis gate (ticket 277) and the paper chain (ticket 234) that did not exist
then. Run the nine meshes and report, per piece: point count into clustering, cluster
count and sizes, and whether surfaces were written.

**B — were the inputs the same?** Record the md5 of the nine `Piece0N.obj` today.
Then search for any record of what the old bundle was built from: the repo history
under `.scratch/juglet-breaklines/`, any `run.json` or `index.tsv` row naming the old
bundle, and the attic `checkout-bucketc-20261024-INDEX.txt` / record tarball listing.
If no md5 record survives, say **unknown** — do not infer identity from file names.

## Acceptance

1. A per-piece table, old commit vs today: surfaces produced, cluster count and sizes,
   points into clustering — with the run directory named for each row.
2. The per-piece comparison, plus for each of the three candidate readings — **(1)
   regression** (the older code produces more surfaces from byte-identical inputs),
   **(2) comparison artefact** (the old number came from different inputs or a different
   stage), **(3) not determined** — the evidence that would establish it, quoted. **Do
   not write the verdict**: the lead records it; a worker reports evidence, never a
   judgement.
3. The input-identity question answered with md5s, or explicitly recorded as unknown
   after the search.
4. If the older code cannot build or run, the exact failure (command, error text) and
   what it would take — do not port fixes forward, do not modify the old tree to make
   it work, and do not fall back to today's code.
5. No tracked source changed (`git diff --stat main..<branch>` shows only this
   ticket), frozen corpus md5 unchanged, geometry deleted with a counted record, index
   rows appended with `verdict` and `human_note` empty, ticket and `Status:` updated.

## Boundaries

- Build the old commit in a private tree inside its own run directory; never build in,
  or dirty, the canonical checkout `/data/gpfs/projects/punim2657/sfs_preprocessing`.
- Env-var and build-target choices only. No source edits, in any commit, at any age.
- Runs on compute nodes only. A scoring or probing step over a bundle runs there too —
  the previous ticket's Pot A gate probe was run on the laptop, which breaks the
  standing rule; do not repeat that.

## What this cannot settle

**Why** the surfaces are lost — that is ticket 20. And whether the Juglet would
reassemble if every sherd produced a surface — stage 2 of ticket 07, paused.

## Worker evidence — job 33836038, 2026-10-27

Evidence only. The reading of it, and any word for the outcome, is the lead's.

**Run:** `20261027-0129_28e470b_p21-replay-old-bundle`, `sacct` `State=COMPLETED ExitCode=0:0`, node spartan-bm173, elapsed 00:03:54.
Index row appended, verdict and human_note empty (TAB stands for the tab character):
`20261027-0129_28e470b_p21-replay-old-bundle\t33836038\t28e470b41753b2ca9633678a719b2e224ec9c0b1\tp21-replay-old-bundle\t\t`

### What each arm was, and where it was built

Two arms, each `git -C <canonical checkout> archive <commit>` unpacked into a private tree inside the
run directory (`build/{old,new}/src`, both removed at the end of the job after the binaries were
copied to `bin/`), then plain cmake + make inside `$CANON/pcl_191_nurbs.sif`. Both builds
exit 0; nothing was edited at either commit. Record: `out/source.md5`.

| arm | commit | file built | md5 | lines |
|---|---|---|---|---|
| old | `28e470b` | `original_nurbs_preprocessing/mesh_processing_headless.cpp` | `70c44d9b0575df0b4e7ee7311ae47144` | 2269 |
| new | `d8af9d2` | `mesh_processing_headless.cpp` | `07a1333a7e009198d71612c12d2e776b` | 2632 |

`data_path.h` is byte-identical at both commits (`e6184c9d9dc30cb7a8ccf012ac1f1b4f`, 104 lines). The
binaries kept as evidence: `bin/MeshPreprocessingHeadless_28e470b` md5
`26af0694aefec5155da00db95d0c87e8`, `bin/MeshPreprocessingHeadless_d8af9d2` md5
`91b75eeadcf02009064f5f18218e0882`.

The old arm's bytes are the **post-patch** bytes, so the September patch step is not repeated:
`git apply --check` of `juglet_mesh_diag`, `juglet_mesh_filter`, `juglet_mesh_thresholds`,
`juglet_edgeline_sphereradii`, `juglet_edgeline_spheremin`, `juglet_edgeline_nowriteconvert` all
reverse-apply cleanly (forward fails); the archived file carries `Single-file filter` ×1,
`Segmentation thresholds` ×1, `GROW-DIAG` ×2 — the markers
`run_juglet_preprocessing.sbatch:140-145` verifies after patching. The new arm carries
`PAPER-234` ×12, `RESTORE-244` ×1, `SFS_AXIS_FILE` ×6.

### How each arm was invoked

Old arm, reconstructed from that commit's own `main()`
(`original_nurbs_preprocessing/mesh_processing_headless.cpp:2095-2269`: `argc>=4` sets the
single-file filter and pot/piece ids at :2102-2104, applied at :2155) and from the tracked
`run_juglet_preprocessing.sbatch:156-180` — not from today's `submit.sbatch`. One fresh
process per piece, only that piece's PCD visible under `Dataset/Point/Juglet/`, its own
`Temp/Temp/Juglet/tmpSurfaceCluster_Improved_*.ply` removed first, `NURBS_OUTPUT_BASE` unset:

```
apptainer exec --bind /data:/data $CANON/pcl_191_nurbs.sif \
  env POT_NAME=Juglet SFS_SMOOTHNESS_DEG=<4.5 pieces 1-8, 12 piece 9> \
  bin/MeshPreprocessingHeadless_28e470b Juglet_Piece_<p>_Point A <p>
```

New arm, today's invocation (`20261027-0055/submit.sbatch:113-115`), no argv, with the axis each
piece carried into that run:

```
apptainer exec --bind /data:/data $CANON/pcl_191_nurbs.sif \
  env POT_NAME=Juglet SFS_AXIS_FILE=<20261027-0055/out/boot/Juglet_Piece_<p>_boot_Axis.xyz> \
  bin/MeshPreprocessingHeadless_d8af9d2
```

### 1. Check A — per piece, old vs today

`out/table_old_vs_today.tsv` carries all fifteen fields including surface md5s; `out/logs/`
holds 27 run logs; `stage/` still holds the produced surfaces. Sizes are the old arm's
`Cluster i : n` lines and the new arm's equivalents.

| piece | old: pcd → clustering | clusters first/final | sizes | S0 / S1 lines | today: pcd → clustering | clusters first/final | sizes | S0 / S1 lines |
|---|---|---|---|---|---|---|---|---|
| 1 | 24294 → 11291 | 4 / 4c-1i | 7138,506,58,50 | 11031 / 1788 | 24294 → 14546 | 22 / 18c-1i | 3489,626,411,… ,50 (18) | 3580 / 12092 |
| 2 | 2565 → 2565 | 0 / 4c-2i | 94,82,80,58 | 434 / 339 | 2565 → 1031 | 0 / — | — | 0 / 0 |
| 3 | 3493 → 3493 | 2 / 2c-1i | 350,143 | 1228 / 591 | 3493 → 1467 | 2 / — | 169,99 | 0 / 0 |
| 4 | 3651 → 3651 | 2 / 2c-1i | 384,121 | 1390 / 651 | 3651 → 1530 | 2 / 2c-1i | 242,51 | 182 / 732 |
| 5 | 6211 → 6211 | 3 / 3c-1i | 1002,62,58 | 2585 / 317 | 6211 → 3021 | 1 / — | 679 | 0 / 0 |
| 6 | 5126 → 5126 | 3 / 3c-1i | 773,92,78 | 2264 / 498 | 5126 → 2351 | 2 / 2c-1i | 365,213 | 608 / 1016 |
| 7 | 8421 → 8407 | 11 / 11c-1i | 1702,399,…,50 (11) | 4212 / 1972 | 8421 → 4254 | 5 / 4c-1i | 326,263,77,68,65 | 1012 / 829 |
| 8 | 4479 → 4479 | 6 / 6c-1i | 341,251,65,62,53,52 | 1387 / 960 | 4479 → 1988 | 2 / — | 224,196 | 0 / 0 |
| 9 | 2094 → 2094 | 2 / 2c-1i | 1657,265 | 3347 / 913 | 2094 → 787 | 0 / — | — | 0 / 0 |

Same nine PCD files, same nine meshes, same machine family, both arms in one job. The old arm
wrote both surfaces for nine of nine pieces (`missing_src` 0 on every row); the new arm wrote
them for pieces 1, 4, 6, 7 and for none of 2, 3, 5, 8, 9 (`missing_src` 2 on each).

The new arm is a control that lands where the recorded today-run lands, from a different node,
a separately built binary and fresh stage dirs: same four pieces, and piece 1's
`14546` clustering points, 22 clusters, `4 clusters after 1 iterations`… are run
`20261027-0055`'s own numbers.

### 2. The three readings, and what would establish each

**(1) the older code writes more surfaces from byte-identical inputs.** Established by the two
things this job did together: the inputs are the same bytes (below), and the two commits differ
only in the downsample call. Quoted, old arm
`original_nurbs_preprocessing/mesh_processing_headless.cpp:569`:
`std::string downsamplePointCloud(std::string inputPcdFile, float samplingRadius = 0.6F)`
— targetSamples defaults to 10000, band 8000-12000, so a cloud under 8000 points survives whole;
today's call site `mesh_processing_headless.cpp:2535`
`downsamplePointCloud(inputFilePath, 0.6F, dsTarget244)` with `dsTarget244` defaulting to 0
(:572 `// Default 0 = restored density`) takes the fixed-radius path at :603-608
(`// POTA-244 RESTORE (targetSamples == 0)`), introduced by `93c33bc` 2026-10-22
"Ticket 245: merge density restore to main". The log lines that show it:
old `out/logs/old_pass1_p3.log:10` `[DEBUG getNormalsOnSurface] Starting function. Input points: 3493`
against new `out/logs/new_pass1_p3.log`
`[DOWNSAMPLING RESTORE-244] Fixed radius=0.60000, input=3493 points, Result=1467 points` and
`[DEBUG getNormalsOnSurface] Starting function. Input points: 1467`. Every new-arm piece shows
0.38-0.60× of the staged cloud reaching clustering (2565→1031, 2094→787, …); every old-arm
piece shows 1.00× except piece 1 (24294→11291, inside the 8000-12000 band).

**(2) the older number came from other inputs or another stage.** Established by showing the
staged clouds differ from what the old run read, or that the "7 of 9" figure was not the mesh
stage's output. Neither holds for the clouds — see the md5 identity in item 3. What the search
*did* turn up is that the surviving September-era log is not this binary's log:
`attic/checkout-bucketc-20261024-record.tar.gz` member
`sfs_preprocessing/diag_t04_juglet/mesh_stage.log` records one process for all nine pieces,
piece 3 `3` clusters and piece 9 `4` — both followed by
`Warning: Source file not found: Temp/Temp/Juglet/tmpSurfaceCluster_Improved_0.ply` — i.e. the
7-of-9 shape, while the 28e470b replay gives piece 3 `2` clusters (350/143) and piece 9
`2` (1657/265) and writes both surfaces for each. Its percentages match the replay to four
digits on pieces 1, 5, 6, 7 (67.7 / 17.13 / 16.88 / 24.99) but not on 3, 4, 8, 9 (37.3066 /
13.0721 / 13.1726 / 14.5315 against 14.13 / 13.84 / 13.22 / 91.79). So that log is a close
relative of the replay, not the same build. The 09-30 reading in
`issues/17-stale-temp-surface-inheritance.md:73-100` ("9 Surface_0 files: 7 genuine + 2 absent",
pieces 3 and 9 "MISSING surfaces", "30 iterations still yield one cluster each") is likewise not
reproduced by the commit ticket 21 names as its code (28e470b): there, pieces 3 and 9 produce
two clusters each and write both surfaces. Two differences that could carry it: this replay used
the tracked smoothness table (4.5, piece 9 = 12) and did not run the 30-retry sweep, whose grid
is not recorded; and no run.json or index row survives from that build, so its bytes are
unestablished.

**(3) not determined.** Would be the answer if the old arm had failed to build or run, or if the
staged clouds could not be tied to what the old run read. Neither happened; the old commit builds
and runs unmodified, and the clouds regenerate byte-identically.

### 3. The input-identity question

The stage consumes the cloud, not the mesh named in the brief: it derives
`<stem>_Mesh.obj` from the PCD stem and reads
`Dataset/Mesh/Juglet/Juglet_Piece_<N>_Mesh.obj`, which Step 0 copies from the two-digit
`Juglet_Piece_<NN>_Mesh.obj` (byte-identical pairs, mtime 2026-09-16 17:33:44).

- **The nine `Piece0N.obj` the brief names** (`Dataset/Juglet/`, mtime 2026-05-29 16:19) md5
  today: `d0d872d6d810d3ebde5e9f32021487e0`, `a3e47cf5c04ec0c08f460a919fba6af3`, `e01f2fedd2fd2cc221fa13fdc4a39494`,
  `bb7f07b5cdb2829a1b9f8ce4cb912091`, `41f7f875cb15cd751f7f80a104fd8cfa`, `f4ff2150b161979fe63c00979535de10`,
  `bc408a3208ed27c216c92059e4887b13`, `6ab8c73bbe9167cc0e5b9d39219302ee`, `0e241a434bf8c4ef76eca03b8e4c5aea`.
- **The clouds the stage actually ate** — all nine `Dataset/Point/Juglet/Juglet_Piece_<N>_Point.pcd`
  carry `mtime == ctime == 2026-09-25 14:35:50` (0.689-0.871 s apart), two minutes before the old
  bundle's last full write at 14:37-14:40, and `ctime == mtime` means nothing rewrote, renamed or
  re-chmoded them afterwards.
- **Byte identity, reproduced** (`out/pcd_identity.md5`): regenerating each cloud from the same
  single-digit mesh with the `ObjToPcd` built from the 28e470b archive gives byte-identical files
  for nine of nine — `b1df295ba405c881bf06a91e3b46fddf`, `42568d383687c73933b60a880bde9475`,
  `54feda576ca03cf04b688330e5187556`, `b9e273bba1b60c67d6eb3cc5bfb24471`, `a855f6da22a0e95e024ebca6fad4f9a8`,
  `1a5373ed49d21ddacdd25a4f4ca1d5e7`, `199d257b2078345ec549997d6fbfc969`, `3014b81049f5e63a889235183c7aec41`,
  `1542b45d18cea115c03d56ff3fcbe2a6`, at 24294 / 2565 / 3493 / 3651 / 6211 / 5126 / 8421 / 4479 /
  2094 points. `ObjToPcd` samples nothing and draws no random numbers, so equal input necessarily
  gives equal output; the equality is a check that the same mesh was being read.
- **No md5 record of the old bundle's own inputs survives**, and the ticket asked for that to be
  said explicitly: `index.tsv` has no September Juglet row (its only Juglet rows are the 2026-10-24
  sweep and `20261027-0055`); `grep -l Juglet */run.json` returns only today's runs; no
  `*/out/inputs.md5` names a Juglet file; the attic record tarball's 80 Juglet members are diag
  logs, text dumps and Ground Truth only; and the full-geometry tarball
  `checkout-bucketc-20261024.tar.gz` is gone (only its `.md5` file remains). So the old
  bundle's recorded input md5s are **unknown**; identity rests on the filesystem timestamps and
  the byte-identical regeneration above.

### 4. Determinism, per the identity-gate caveat

The mesh stage draws 30 random ray-cast points from an unseeded generator
(`mesh_processing_headless.cpp:1526-1527`), so the old arm ran twice. Pass 1 and pass 2 give
identical surface md5s, identical cluster counts and identical sizes on **8 of 9** pieces; piece
2 alone differs in content (`Surface_0` `d6c564c1e21ae1c62285c905d083c8a9` →
`5ab17ea88afe6f59f55e3007a2f23734`, `Surface_1` `4f83bc08fba6bbb1dcdb340416e13501` →
`a261f5f3c4e4e4a0dfa269f596d25872`) with its counts and line counts unchanged (4 clusters,
94/82/80/58; 434 / 339 lines). On this bundle the non-determinism showed up as content drift on
one piece, never as a change in which pieces produced surfaces.

### 5. Corpus, deletions, and what is not here

- Corpus unchanged: `out/inputs_before.md5` and `out/inputs_after.md5` hold the same 18 rows
  (nine clouds + nine meshes, with size and mtime), they diff clean, and
  `out/inputs_verdict.txt` reads `UNCHANGED`. The canonical checkout is still `1cdab4c`
  with the same 11 pre-existing modified files it had before this ticket (mtimes 2025-11 and
  earlier), no `Dataset/` entry among them, and no untracked files.
- Deleted: the two private build trees (`build/{old,new}/src`, 1.7 G) once the binaries were
  copied to `bin/`; and the read-only peek dir `.ticket21_peek/` I had made inside the
  canonical checkout to read the attic tarball (removed; `ls` now reports it absent). No corpus
  file was deleted, moved or rewritten.
- Kept: `stage/` (91 M — the produced surfaces, so the numbers in the table can be re-checked
  file by file), `bin/` (2.8 M), `out/` (tables, 27 logs, md5 records, `NOTES.md`).
- Second job of the two-job budget left unspent, because A and B are answered and **why** the
  surfaces are lost is ticket 20. The ready experiment, for whoever takes ticket 20: run the
  `d8af9d2` binary with `SFS_DOWNSAMPLE_TARGET=19000` (the pre-restore adaptive band,
  :2534-2535) and with `SFS_DOWNSAMPLE_TARGET=-1` (skip), on pieces 2, 3, 5, 8, 9, which separates
  the density restore from the ticket-234 paper chain.

