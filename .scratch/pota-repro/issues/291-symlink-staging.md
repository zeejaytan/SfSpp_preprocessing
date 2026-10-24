# 291 — Stage a run's inputs by symlink, not by copy

Status: ready-for-agent
Answers: E1
Working in: C:/PR/worktrees/sfs/291

## Why

The conservator's rule (2026-10-24): geometry must not grow on the system, and a run adds no
geometry of its own. Today every run copies its inputs into its own stage tree and, before the
released corpus existed, also derived a fresh cloud per piece:

- `SfSpp/runs/20261024-2151_8e1e514_p289-p09/submit.sbatch:51-55` — `mkdir -p $STAGE/Dataset/{Point,Mesh,Axes}/Pot_J`
  then `cp "$AUTHB/Mesh/Pot_J_Piece_09_Mesh_DS.obj" "$STAGE/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj"`
  and `cp "$AUTHB/Axes/Pot_J_Piece_09_Axis.xyz" ...`;
- `:63` then ran `cc_mesh_to_pcd.sh` to **derive** the cloud into `Dataset/Point/Pot_J/` (~50 MB ASCII);
- `:68` copies that cloud into `out/cloud.pcd` as well.

A piece therefore costs one mesh copy (1.3 MB) plus one 20-90 MB cloud per stage tree, and a full
corpus run would recreate about 5-6 GB that already exists once.

The corpus now exists, frozen and complete:

```
/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/
    Mesh/<Pot>/<Piece>_Mesh.obj | <Piece>_Mesh_DS.obj     164 pieces
    Point/<Pot>/<Piece>_Point.pcd                          148 (143 released + 5 derived)
    Axes/<Piece>_Axis.xyz                                  163
    Breaklines/, Surfaces/                                 the authors' own outputs
```

## The change

Add `scripts/stage_piece.sh` to this repo (the canonical checkout only fetches; the script is
called from a run's submit.sbatch).

```bash
scripts/stage_piece.sh <stage_dir> <Pot_X> <Piece_01> [<Piece_02> ...]
```

Contract:

1. `Dataset/Mesh/<Pot>/<Piece>_Mesh.obj` → **symlink** to `$CORPUS/Mesh/<Pot>/<Piece>_Mesh.obj`,
   or to `..._Mesh_DS.obj` when only the downsampled mesh exists. This is also how the `_DS`
   naming trap is absorbed: the pipeline builds `<Piece>_Mesh.obj` from the point file's stem
   (`mesh_processing_headless.cpp:2505-2511`), and a symlink carries the expected name for free.
2. `Dataset/Point/<Pot>/<Piece>_Point.pcd` → **symlink** to `$CORPUS/Point/<Pot>/<Piece>_Point.pcd`.
   Fail loudly if the cloud is missing (it must not silently derive one: derivation is unseeded).
3. `Dataset/Axes/<Piece>_Axis.xyz` → **copy** (7 KB; the mesh stage is given it by
   `SFS_AXIS_FILE`, and a copy keeps the run's provenance self-contained).
4. Real (writable) directories for the outputs: `Dataset/Breaklines/<Pot>`,
   `Dataset/Surfaces/<Pot>`, `Temp/Data/<Pot>`, `Temp/Temp_edge/<Pot>`. Nothing else is created.
5. Append to `$STAGE/inputs.md5`: `readlink -f` of each symlink, the target's md5, and its point
   count — `md5sum` follows symlinks, so this records what was actually read.
6. Refuse to replace an existing **regular** file with a symlink (a derived cloud must never be
   silently swapped), and refuse a stage directory inside the corpus.
7. Print one summary line: pieces staged, symlinks, bytes copied.

Then: the run's `submit.sbatch` calls the script instead of the `cp` + `cc_mesh_to_pcd.sh` block,
and `AGENTS.md` ("Runs, worktrees and the attic") gains one sentence: *inputs are staged by
symlink into the frozen corpus; a job copies no geometry.*

## Gate (pre-registered, written before any number is taken)

One job, one piece, two stage trees **from the same inputs**: A staged by `cp` (today's way),
B staged by symlink (new script). Both run the mesh stage (theta 3.4, `SFS_AXIS_FILE` set, the
`[PAPER-234] classify` line quoted) and the edge stage with the shipped binary.

1. **IDENTITY**: A and B export lane files identical point for point — `n` equal and
   `max|dxyz| = 0.000000`. Anything else fails the gate; the symlink is then not equivalent and
   the ticket stops.
2. **NO GEOMETRY IN THE STAGE**: in tree B, `find "$STAGE" -type f -size +1M` is empty, and
   `find "$STAGE" -type l | wc -l` is exactly 2 per piece. Report `du -sh` for both trees.
3. **PROVENANCE**: `inputs.md5` resolves each symlink to the corpus path and its md5 matches
   `Point/MANIFEST_released.tsv` (or `MANIFEST_derived.tsv` for the 5 derived pieces).
4. **SCORES**: report both lanes' n / median / coverage both ways / jumps for A and B; they must
   be equal, and reported for the record, not gated against older runs (the frozen cloud is the
   released one, so older numbers came from different draws).

Use **Pot J 09** (has a released cloud, and ticket 289's picture exists to compare against) and
**Pot H 02** as a second piece (multi-component bag, exercises the seed path).

## Constraints

- No change to pipeline code, defaults or thresholds; this is staging only.
- Do not derive any cloud in the gate run. If a cloud is missing, stop and report.
- Never `build.sh --target nurbs` (ticket 282: it compiles the pre-247 duplicate at
  `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`). Build the live root project.
- Write the ticket results into this file in the main clone; leave it uncommitted (the lead commits).
- Run directory under `SfSpp/runs/` + one `index.tsv` row with `verdict`/`human_note` left empty.
- The job deletes its own stage trees at the end (`GEOMETRY_DELETED.txt`), keeping `out/` and `logs/`.
- Do not touch `C:/PR/worktrees/sfs/290`.

## Results

(pending)
