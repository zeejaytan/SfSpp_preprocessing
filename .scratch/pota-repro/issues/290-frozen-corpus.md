# 290 — the frozen input corpus, and one piece run from it

Status: done (accepted as DROP-IN, Bl1 draw limit disclosed)
Answers: E1
Working in: C:/PR/worktrees/sfs/290

## Why this ticket exists

Every score this project has ever quoted rests on an input point cloud that was DERIVED at run time by
`C:/PR/SfSpp_preprocessing/cc_mesh_to_pcd.sh`: CloudCompare `-SAMPLE_MESH POINTS 1000000` on the OBJ,
then SOR medium (6 neighbours, 1.0 sigma), then normals (radius 0.5, orient k 6). That sampler is
UNSEEDED — three draws of `Pot_A_Piece_01_Mesh.obj` gave 843,433 / 843,282 / 843,252 points — so the
clouds that produced the 4.0-era scores cannot be regenerated (ticket 284 Phase 0 blocked for this
reason, and the survivors were two pieces out of 148).

On 2026-10-24 the authors' Google Drive release was downloaded and checked (`release_check.sh`, md5s in
the corpus manifest). `Point.zip` (2,663,152,436 B, md5 dce0bd8c499350991859e245f468b097) holds **143**
`.pcd` files laid out `Point/Pot_<X>/<Piece>_Point.pcd` — exactly the pipeline's expected filename
(`data_path.h:55-62`, read at `mesh_processing_headless.cpp:2502-2508`) — each **binary**, 28 B/point,
`FIELDS normal_x normal_y normal_z x y z _`, ~1,000,000 points, and in the SAME world frame as our own
derived clouds (Pot C 01: theirs x -37.01..76.71, y -46.30..69.77, z 375.46..490.77; ours -36.94..76.72,
-46.29..69.76, 375.48..490.61 — agreement ~0.15 mm). `Mesh.zip` (143 `.obj`) is the same mesh set we
already hold: **143 of 143** shared names have identical vertex and face counts (counted from `v ` / `f `
lines inside the zip member, not from the Meshlab comment header, which only 126 carry).

Coverage measured against the 148 pieces in `runs/20261024-1851_ee5f4dc_p284-rescore/phase0-table.tsv`
(the scored corpus): **143 covered, 5 not** — `Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`,
`Pot_I_Piece_30`, `Pot_J_Piece_12`. No released cloud is unused.

Conservator's decision (2026-10-24): adopt the 143 released clouds and derive only the 5 missing.

## What the lead has already done (do not redo)

- Extracted `Point.zip` into `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/`
  (143 files, 3.8 GB, per pot A8 B9 C4 D29 E31 F6 G7 H11 I27 J11). The input folder is NOT a git
  repository and is never copied into a worktree; a RUN stages its own copy under `runs/<id>/stage/`.
- Integrity: 143/143 parse, `DATA binary`, point counts 999,810–1,000,172 (sum 143,000,040), zero bad
  headers; per-file md5/points/bytes in `Point/MANIFEST_released.tsv` (144 lines incl. header).
- Derived the 5 missing clouds with the same script on `sapphire` (job 33748457,
  `/data/gpfs/projects/punim2657/Temp/pcd_derive5/`); they land as `Point/<Pot>/<Piece>_Point.pcd` and
  their manifest is `Temp/pcd_derive5/manifest_derived.tsv`.

## Work

### Phase 1 — verify the corpus is complete and readable

1. Confirm 148 files: the 143 from the release plus the 5 derived, and that each scored piece of the
   148 has exactly one `<Piece>_Point.pcd` under `Point/<Pot>/`.
2. The 5 derived files are **ascii** with `FIELDS x y z normal_x normal_y normal_z` while the 143 are
   **binary** with normals first. Both are legal PCD and the pipeline reads with
   `pcl::io::loadPCDFile<pcl::PointXYZ>` (`mesh_processing_headless.cpp:577`), which selects by field
   NAME. Prove it rather than assume it (Phase 2 does this).
3. Record for each of the 5 the source mesh md5 and the point count, and note in the corpus manifest
   that those 5 carry ONE unseeded CloudCompare draw each (the 143 do not: their bytes are frozen).

### Phase 2 — one piece, end to end, from the frozen cloud

Pick `Pot_J_Piece_09` (its original cloud is gone, its mesh survives as
`Mesh/Pot_J_Piece_09_Mesh_DS.obj`, and ticket 289 has the reference numbers to compare against).

1. Run the mesh stage at the shipped default (theta 3.4, `SFS_AXIS_FILE` set — quote the
   `[PAPER-234] classify:` line; a run without that line is void, ticket 277) with `Dataset/Point/<pot>`
   and `Dataset/Mesh/<pot>` pointing at the frozen corpus. Try a SYMLINK first and report whether the
   stage reads through it; fall back to a copy only if it does not, and say which was used.
2. Run the edge stage with the shipped binary (`a28d10afab2b50bbe750d599ee2b7214` or whatever `git
   archive` of main HEAD builds — record the md5 and the source md5; NEVER `build.sh --target nurbs`,
   ticket 282).
3. Score both lanes against the same author breaklines and report n / median / coverage ours->author /
   coverage author->ours / jumps / max step, alongside ticket 289's numbers (Bl0 78–79 dots, median
   1.04–1.20 mm, cov 70.9–75.6; Bl1 84–86 dots, median 1.98–2.12, cov 48.8–51.2) so it is visible whether
   the frozen cloud reproduces that piece.
4. State plainly whether the released cloud is DROP-IN (the pipeline reads it and lands in the same
   place as our own derived cloud did).

### Phase 3 — leave the record

- Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
  `run.json`, `submit.sbatch`, `logs/`, `out/`, and one appended `runs/index.tsv` row (leave `verdict`
  and `human_note` empty — the lead fills them).
- **Geometry dies with its ticket** (conservator's rule, 2026-10-24): delete the run's derived point
  clouds, surfaces and staging copies when the ticket closes, keeping `run.json`, logs, the scorer,
  numbers and pictures; write `GEOMETRY_DELETED.txt` naming what went. The corpus itself is INPUT —
  never delete it.
- Write the result into this ticket (main clone, leave uncommitted; the lead commits) and paste the
  per-lane table into it.

## Constraints

- Do NOT modify `cc_mesh_to_pcd.sh`, the pipeline code, or any default/threshold.
- Do NOT re-run the corpus. One piece only.
- Do NOT touch `C:/PR/worktrees/sfs/275`, `/276`, `/287`, `/288`, `/289`.
- Do NOT delete anything outside your own run directory.
- The corpus at `sfs_main/original_samples/SfS_pp/Point/` is a shared INPUT: read-only for this ticket.

## Acceptance

1. 148/148 scored pieces have exactly one cloud; the 143 released md5s are unchanged from
   `MANIFEST_released.tsv`.
2. `Pot_J_Piece_09` runs end to end from the frozen cloud with the classify line present, and its
   numbers are reported next to ticket 289's.
3. A clear DROP-IN / NOT-DROP-IN verdict with the evidence it rests on.
4. Run directory + index row exist; the run's derived geometry is deleted and inventoried.

## Evidence to report

The 148-file inventory check, the classify line quoted verbatim, both lane rows versus 289, the
symlink-or-copy answer, the binary/source md5s, the run id and index row, and any deviation.

## Results

Status: results-in. Run directory `20261024-2328_d36a33e_p290-corpus`, commit
`d36a33e58bbbdcfa52daf41689ae902fa51266d1` (the worktree HEAD, already on origin/main). Nothing was
committed and no code, default or threshold was touched.

### Phase 1 — the corpus is complete and readable. PASS

The check is `inv290.py`; its output is kept as `out/inventory.txt`.

| Check | Result |
|---|---|
| Released clouds, 143 rows of `Point/MANIFEST_released.tsv` | md5 mismatch 0, point-count mismatch 0, byte-size mismatch 0 |
| Derived clouds, 5 rows of the derived manifest | all 5 present, md5 0 mismatch, source-mesh md5 0 mismatch |
| The scored corpus (`phase0-table.tsv`, 148 pieces) | 148 rows -> 148 pieces -> 148 files; missing 0, duplicated 0, unaccounted 0 |
| Per pot, after the five derived | A 8, B 9, C 4, D 29, E 31, F 7, G 7, H 11, I 30, J 12 = 148 |
| Encoding | 143 binary, 5 ascii |
| Field order | binary `FIELDS normal_x normal_y normal_z x y z _`; ascii `FIELDS x y z normal_x normal_y normal_z` |

The per-pot line in this ticket (A8 B9 C4 D29 E31 F6 G7 H11 I27 J11 = 143) describes the release and is
correct; the five derived files land one each on F, I (three) and J, giving the row above.

Phase 1 item 2 asked for the reading of the ASCII clouds to be **proved, not assumed**, and Phase 2 proves
only the binary one. So one of the five went through the mesh stage alone (job 33748700 — no edge stage, no
scoring): `Pot_I_Piece_28`, ascii, xyz first, 841,452 points, cloud md5 `149b624ef1c8c049a0f9ccd5c787050f`.

    MESH_EXIT=0
    Copied Point file: Pot_I_Piece_28_Point.pcd
    [PAPER-234] classify: face0 n=1306 interior_frac=0.0000 face1 n=953 interior_frac=1.0000 satA=0.0000 satB=2259.0000
    [PAPER-234] classify: swapped -> Surface_0=interior
    Pot_I_Piece_28_Surface_0.xyz rows=2577 md5 3c4b86bdadbd2df765b64b891259c6be
    Pot_I_Piece_28_Surface_1.xyz rows=3067 md5 010783aeb4d7864668add09b010ca257

The ASCII layout is read correctly and the axis classify runs on it. The other four carry the same header,
field list and writer (`cc_mesh_to_pcd.sh`) and are not individually tested — one piece of evidence, not five.

### Phase 2 — Pot J 09 end to end from the frozen cloud

Both binaries were built from `git archive d36a33e` inside the apptainer container (ticket 287/289 recipe,
`make -j8`); nothing was built with `build.sh --target nurbs`.

| Stage | Binary md5 | Source md5 (LF) | Lines |
|---|---|---|---|
| edge | `a28d10afab2b50bbe750d599ee2b7214` | `f0dbfe7032d90a04412d15bd1699a703` (SEED-287 count 1) | 3739 |
| mesh | `0171f471d0558d2676df7c4b113c1e9d` | `459dabe145056489829804292710b382` | 2618 |

The edge binary is the one tickets 287, 288 and 289 scored with, so the comparison below is on identical code.

**Symlinked or copied: the pipeline reads THROUGH a symlink, and the run used file-level symlinks.** Evidence
from a 25 s probe with `Dataset/Point` a DIRECTORY symlink to the whole corpus and `POT_NAME=Pot_A`:

    Copied Point file: Pot_A_Piece_01_Point.pcd
    Selected file: Dataset/Point/Pot_A/Pot_A_Piece_01_Point.pcd
    [DOWNSAMPLING RESTORE-244] Fixed radius=0.60000, input=999810 points, Result=85136 points
    Warning: Mesh file not found: Dataset/Mesh/Pot_A/Pot_A_Piece_01_Mesh.obj

Nothing about a symlink blocks the stage. The caveat is the scan: it is recursive with no pot filter, so a
whole-corpus directory symlink makes the stage walk all 148 pieces (one piece completed inside the 25 s
window). The real run therefore symlinked the one file, `Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd`.

The classify line, with `SFS_AXIS_FILE` set (a run without it is void):

    [PAPER-234] classify: face0 n=4089 interior_frac=0.0000 face1 n=2880 interior_frac=1.0000 satA=0.0000 satB=6969.0000
    [PAPER-234] classify: swapped -> Surface_0=interior
    [SPLITTER-234] rule=PCL-REGION-GROWING smoothDeg=4.50000 curv=1.50000 joinDeg=60.00000 distMM=2.00000 window=100 paper=PAPER-CHAIN theta=3.40000 kappa=1.00000 nb=10
    [PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10

The edge stage, both lanes, shipped defaults:

    [FULL-263] no-discard kept 276/276 (1 comps @ 5mm)
    [SEED-287] ncomp=1 biggest=0 size=276/276 seed=31.1847 15.6651 473.543
    [STOP-267] CHAIN-END step=274 of 276: nearest fresh dot 22.4362mm > R=12mm ; refusing it ; left=1 dots unvisited
    [FULL-263] chain=275 maxjump=2.69915mm
    [FULL-263] kept chain order n=275 (clock sort skipped)
    [FULL-263] no-discard kept 306/306 (1 comps @ 5mm)
    [SEED-287] ncomp=1 biggest=0 size=306/306 seed=31.0263 14.3209 474.594
    [FULL-263] chain=306 maxjump=9.62677mm
    [FULL-263] kept chain order n=306 (clock sort skipped)

`ncomp=1` on both lanes, so ticket 287's largest-lump seed is a no-op on this piece.

Lane table (project scorer, `score275.lane`; bar is median <= 2.0 mm and coverage >= 90; Pot J 09's
reference lines are ruled WRONG, so these rows are a drop-in comparison, not a bar tally):

| Lane | Source | n | median mm | cov ours->authors | cov authors->ours | jumps | max step mm | length mm |
|---|---|---|---|---|---|---|---|---|
| Bl0 | frozen cloud (290) | 79 | 1.079 | 70.89 | 75.68 | 0 | 4.999 | 145.40 |
| Bl0 | 289 derived, draw 1 | 78 | 1.204 | 75.64 | 81.08 | 0 | 4.596 | 143.20 |
| Bl0 | 289 derived, draw 2 | 79 | 1.041 | 70.89 | 75.68 | 0 | 4.291 | 144.69 |
| Bl0 | authors (reference) | 74 | — | — | — | — | — | 133.74 |
| Bl1 | frozen cloud (290) | 91 | 1.913 | 50.55 | 63.77 | 0 | 4.890 | 166.89 |
| Bl1 | 289 derived, draw 1 | 84 | 1.980 | 51.19 | 65.22 | 0 | 3.923 | 153.32 |
| Bl1 | 289 derived, draw 2 | 86 | 2.122 | 48.84 | 63.77 | 0 | 2.629 | 155.63 |
| Bl1 | authors (reference) | 69 | — | — | — | — | — | 125.28 |

Line-to-line distance between the frozen run and 289's draw 1: Bl0 max 2.2459 mm one way and 2.4494 the
other, mean 0.6604 / 0.6585; Bl1 max 1.6936 / 1.0259, mean 0.5696 / 0.5216.

**Verdict: the released cloud is DROP-IN — with one limit that must be carried forward.**

- Bl0 lands inside ticket 289's own two draws on all four columns: n 79 (draw 2 = 79), median 1.079
  (1.041–1.204), cov ours->authors 70.89 (inside 70.89–75.64, equal to draw 2), cov authors->ours 75.68
  (equal to draw 2).
- Bl1 is **not** inside on two columns: n 91 against 84–86, median 1.913 against 1.980–2.122, and the line is
  11.3–13.6 mm longer. Coverage is inside (50.55 between 48.84 and 51.19; 63.77 equal to draw 2).
- Mechanism, measured on Pot C 01 (AGENTS.md, 2026-10-24): the released cloud keeps the outliers that
  `cc_mesh_to_pcd.sh`'s statistical outlier removal takes out (840,835 points against 1,000,026 on that
  piece), so it is not more resolution — it is a different sample with a different rim population. That is
  consistent with what this run shows: fewer kept dots than 289 (276/306 against 279/309) but a longer
  exported line.
- Consequence for the plan: the frozen corpus is readable, reproducible at shipped defaults, and lands where
  our derived clouds landed within our own draw-to-draw spread on the interior lane. It is a REPLACEMENT
  input, not a byte-identical one, so every bar measured on derived clouds must be re-measured on it and
  must not be inherited piece by piece.

### Phase 3 — reproducibility of the frozen route, measured

Job 33748615 ran the mesh stage twice from the same frozen cloud and the edge stage twice from one identical
`Temp/Data`:

- The mesh stage is deterministic: both runs wrote the same sheets, `32360b58ab00691cab6fefb04ffe2c04`
  (Surface_0) and `f9f3846e40b426292e685db862e9fb46` (Surface_1), with the same classify line. Both differ
  from ticket 289's sheets because the splitter partitions the CLOUD, not the mesh (face0 n=4089 here
  against 4003 there).
- The edge stage gives identical **scores** every time: Bl0 79 / 1.079 / 70.89 / 75.68 / 0 / 4.999 / 145.40
  and Bl1 91 / 1.913 / 50.55 / 63.77 / 0 / 4.890 / 166.89 — the same rows as job 33748526.
- The exported **files** are not byte-identical (Bl0 `b9060d23…` against `5d0e2715…`; Bl1 `7d75caeb…`
  against `342a6cda…`). Job 33748661 found where: lane 0 A 5347 B 5426 bytes, identical 15-line headers, xyz
  bytewise equal in the same order, point sets equal after sorting, nearest-neighbour distance 0.000000 both
  ways — and the 7th column differing as a constant per file:

      A line 16: 40.8228 32.5596 475.389 0.359796 -0.501863 -0.786562 4.20319e+08
      B line 16: 40.8228 32.5596 475.389 0.359796 -0.501863 -0.786562 -4.18843e+09

  4.2e8 is not a curvature (values here are of order 1e-2, mm^-1): the exporter never assigns that field, so
  it prints stale heap content, and the two processes held different garbage — which is also why B's lines
  are one character longer (79 bytes = one per point).
- Rule for every later verification: compare the xyz columns or the scored numbers, never the md5 of an
  exported `*_Breakline_*.pcd`. Written to `out/curvature_column.txt`.

### Phase 4 — the record

- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2328_d36a33e_p290-corpus`: `run.json`
  (carrying a results block), `submit.sbatch`, `submit2–4.sbatch`, `logs/`, `out/`, `bin/`.
- One appended `runs/index.tsv` row: runid, jobid 33748526, the full commit, tag `p290-corpus`, verdict and
  human_note left EMPTY for the lead.
- Jobs: 33748526 (build, inventory, symlink probe, run, score) 2:55; 33748615 (reproducibility) 0:17;
  33748661 (byte diff) and 33748700 (ascii read test) about a minute each. All COMPLETED 0:0.
- **Geometry deleted**: `out/lane0.pcd`, `out/lane1.pcd`, `out/surface_0.xyz`, `out/surface_1.xyz`,
  `stage/`, `probe/`, `repeat/`, `cmp/`, `ascii/` and the node-local build tree — md5s in
  `out/geometry.md5`, statement in `out/GEOMETRY_DELETED.txt`. Kept: `run.json`, the sbatch files, the four
  scripts, `logs/`, `out/*.txt`, `out/*.md5`, `out/png/`, `bin/`. The corpus itself was not touched.
- Picture: `out/png/p290_J09.png`, 1150x520 px, 84,928 B, md5 `3577c62a134dd40e69810794973751c0`; laptop
  copy `C:/PR/SfSpp_preprocessing/artifacts/pota290/png/p290_J09.png` (with `inventory.txt`,
  `key_lines.txt`, `lane_table.txt` beside it). In the Bl0 panel the frozen (green) and derived (blue) rings
  coincide round the whole loop while the authors' black ring leaves it at the bottom-left and over the
  top-right notch; in the Bl1 panel the black ring leaves the silhouette on the right and crosses the
  interior, while green and blue lie on top of each other.

### Acceptance, item by item

1. 148/148 scored pieces have exactly one cloud, the 143 released md5s unchanged — **PASS** (0 mismatches on
   md5, point count and byte size).
2. Pot J 09 runs end to end from the frozen cloud with the classify line present, its numbers beside 289's —
   **PASS** (both lanes, table above, classify line quoted verbatim).
3. A clear DROP-IN / NOT-DROP-IN verdict with the evidence it rests on — **PASS**: DROP-IN, with Bl1's n and
   length outside our own draw spread stated as the limit.
4. Run directory and index row exist, the run's derived geometry deleted and inventoried — **PASS**.

### Deviations

1. **Four jobs, not one.** 33748615 and 33748661 answer whether the frozen route reproduces (the acceptance
   does not ask, but a corpus-wide run depends on it); 33748700 closes Phase 1 item 2 for the ASCII clouds.
   No code, default or threshold was touched in any of them.
2. The first determinism attempt was made INSIDE job 33748526 and failed for a staging reason worth
   recording: the repeat tree held only the mesh object and the two sheets, while the edge stage also reads
   the mesh stage's PLY companions in `Temp/Data` — so it reported
   `[pcl::PLYReader] Temp/Data/Pot_J/Pot_J_Piece_09_unclustered.ply:1: parse error: couldn't read the magic string`
   and `Cannot create a KDTree with an empty input cloud!`, and wrote no exports. Job 33748615 repeated it
   with a full copy of `Temp/Data`. The failed attempt is kept as `out/determinism.txt`.
3. Two 5 KB lane exports were kept for the length of job 33748661 in order to locate the byte difference, then
   deleted; what remains is the quoted pair of data lines in `out/curvature_column.txt`.
4. The picture is one 1150x520 two-panel PNG, not the 2300x520 five-panel layout of tickets 286 and 289: this
   ticket asks for a picture of a drop-in comparison (two of our lines plus the reference), not a per-lane
   diagnosis.
5. The ticket's Phase 1 item 2 also expected Phase 2 to prove the ASCII reading, which it does not (that
   piece's cloud is binary). Job 33748700 is the missing proof, on one of the five.

---

## Verdict (lead, 2026-10-25) — accepted as DROP-IN, with the one limit it discloses

1. **The corpus is real and the sampler leaves the loop.** `…/SfS_pp/Point/` holds 148 clouds — 143
   released (binary, about 1,000,000 points each) and 5 derived from the mesh (ASCII, about 841,000) —
   with `MANIFEST_released.tsv`, `MANIFEST_derived.tsv` and a README carrying the provenance. Run end to
   end from a frozen cloud, Pot J 09 reproduces across staging (ticket 291: `max|dxyz| 0.000000`, four
   runs); that repeatability is the property the corpus exists for.
2. **Pot J 09's numbers, recomputed here from `out/lane_table.txt` and `out/key_lines.txt`**: Bl0
   79 / 1.079 mm / cov 70.89 / reverse 75.68 / 0 jumps / max step 4.999 / length 145.40 mm; Bl1
   91 / 1.913 / 50.55 / 63.77 / 0 / 4.890 / 166.89. The mesh stage ran at theta 3.4 with the axis
   (`classify: face0 n=4089 interior_frac=0.0000 face1 n=2880 interior_frac=1.0000 satA=0.0000
   satB=6969.0000` → `swapped -> Surface_0=interior`), the walk kept one component (276/276), seeded on
   it (`[SEED-287] ncomp=1`), and the stop rule ended it at step 274 with 1 dot left.
3. **The limit, stated by the worker and upheld here.** Bl0's count and both coverages reproduce ticket
   289's second draw exactly (79 / 70.89 / 75.68), so that lane landed inside the old draw spread; Bl1
   does not — 91 dots and 166.89 mm against 289's 84-86 and 153.32 mm, outside it. It changes no
   decision: both lanes are below bar, and Pot J 09 is excluded from the bar tally altogether by the
   reference ruling in ticket 289. But the frozen cloud is a different draw, not a byte-equivalent
   replacement for the cloud that scored 2.53 mm.
4. **What this does not lift**: the 296-lane rollout still cannot be re-scored — those clouds were never
   kept and are gone (ticket 284, blocked). What changes is every run from now on: it starts from a
   fixed cloud, so a re-run repeats and a change can be attributed.
5. **Two records that carry as much weight as the numbers**: five of the 148 clouds are ours and belong
   to pieces the authors excluded (Pot F 07, I 28, I 29, I 30, J 12 — ledger section O), and the
   derived-cloud equivalence was measured rather than assumed (median 0.091 mm to the released surface,
   normals |dot| 0.999).
6. **Status**: done.
