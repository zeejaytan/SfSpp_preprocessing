# 47 — rebuild the nine Juglet input clouds with the corpus converter

## What to build

The Juglet stops being the exception. Its nine input clouds become **corpus-conforming samples**,
produced by the same converter, the same switches and the same freeze discipline as the 143 released
pieces: `cc_mesh_to_pcd.sh` (README step 1 — CloudCompare samples up to 1 000 000 points on the mesh
faces, octree normals at 0.5, MST orientation, SOR noise filter; ASCII PCD with normals). The new clouds
are installed at the canonical `Dataset/Point/Juglet/` on Spartan — where every ticket branch and every
run stages its inputs from — so the whole workspace uses the same files, not a copy inside a run
directory. The 2026-09-25 vertex dumps they replace are **archived with a manifest, not deleted
silently**.

Why: `docs/notes/2026-10-31-juglet-cloud-provenance.md` — those dumps carry 2 094-24 294 points where
the corpus carries ~840 000-1 000 000, and the first measurement that read the input's own layout
(ticket 45's fold radius) was wrong by exactly that factor. This ticket touches **no pipeline source**.

**Answers:** U19

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

**Worker:** unassigned

## The method, exactly

- Input meshes: `$CANON/Dataset/Mesh/Juglet/Juglet_Piece_N_Mesh.obj` — the **mm** meshes. The raw
  `Dataset/Juglet/PieceNN.obj` scans are inches (x50.8); never feed those.
- Command per piece, on a compute node via `sbatch` (the script loads GCC/11.3.0 OpenMPI/4.1.4
  CloudCompare/2.12.4 itself, offscreen Qt):
  `bash cc_mesh_to_pcd.sh -i <mesh> -o <staging dir>` — defaults only (1 000 000 points, medium SOR).
- Output naming must land exactly `Juglet_Piece_N_Point.pcd` — the name every stager and gate greps for.
- **Frame gate before install:** `-GLOBAL_SHIFT AUTO` must have shifted nothing (Juglet coordinates
  ~700 mm; Pot A at ~1e4 was left unshifted). Verify the first rows of each cloud against the mesh's
  own vertices and against the `Dataset/Juglet_GT` frame. A shifted cloud seats nothing downstream.
- Density gate: point count in the corpus range (the script itself refuses < 10 000; expect
  ~1 000 000 sampled, SOR keeping roughly 84 % as on Pot A 01: 1 000 088 -> 843 433); normals present
  in the header.
- **Freeze the draw:** the sampler is unseeded — one draw per piece, md5 + point count + `_cc.log`
  recorded in a `MANIFEST_JUGLET_CC.tsv` beside the clouds (the `MANIFEST_released.tsv` style). A
  rebuild is a different cloud and a corpus change, never a silent refresh.
- Install at `$CANON/Dataset/Point/Juglet/`; archive the nine vertex dumps to
  `/data/gpfs/projects/punim2657/SfSpp/attic/<dated dir>/` with a manifest-path-size list (rule 13:
  nothing is deleted without a record — moved with one, proved by reading it back).

## Known gaps in the converter — recorded here, NOT fixed in this ticket

`MAX_REMOVAL_PERCENT` is declared but never enforced, and the draw is unseeded (three Pot A 01 draws
spread 843 433 / 843 282 / 843 252, ticket 289). The corpus converter stays byte-frozen; changing it
is a separate decision with its own ticket.

## Acceptance

- [ ] 9 of 9 clouds produced by `cc_mesh_to_pcd.sh` unmodified, defaults only; `_cc.log` beside each.
- [ ] Frame gate recorded per piece: first rows vs mesh vertices vs GT frame; no global shift applied.
- [ ] `MANIFEST_JUGLET_CC.tsv` (piece / points / md5 / cc-log / date / command) committed beside the
      record note; the draw is frozen.
- [ ] Vertex dumps archived with manifest; nothing else under `Dataset/` changed (mesh + axes md5s
      unchanged, recorded before/after).
- [ ] Before/after figure for at least J2 — shipped vertex dump vs corpus cloud over the mesh outline,
      counts and pts/mm^2 in the caption — staged for the conservator's eye before any number is quoted.
- [ ] Run dir under `SfSpp/runs/` with `run.json`, index row appended (verdict left empty), poll and
      final `sacct` recorded in this ticket.
- [ ] The lead re-verifies the frame gate and the manifest itself, then updates the AGENTS.md caveat and
      the provenance note with the regeneration date.

**Needs-eye:** the before/after cloud figure (J2 minimum).

## Comments
