# 290 — the frozen input corpus, and one piece run from it

Status: ready-for-agent
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