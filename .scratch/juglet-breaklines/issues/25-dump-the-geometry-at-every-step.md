# 25: dump the geometry at every step, with the cluster label on each point

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** 26 (ticket 24 merged as f3760fa; 26 edits the same file and the rungs it dumps)
**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-10-27)

A ticket on the **instrument**, not on the method. It adds a per-step dump behind one switch whose
default writes nothing extra, so that any later repair can be checked at the rung it acts on and a
failure can be located instead of argued about. **Report evidence; do not declare a winner.**

## Why a dump of the mesh is not enough — the label is the measurement

What the pipeline writes today, from `mesh_processing_headless.cpp` on main (grep over
`savePLYFile|savePCD|cloudForSpline`):

- `:553` `<piece>_SampledWithNormals.ply` — the last artefact before clustering;
- `:883` `cloudForSpline.pcd` — the points sampled for the spline fit;
- `:2540-2541`, `:2588` `tmpSurfaceCluster_Improved_{0,1}.ply` — the final pair;
- `:2656` `<piece>_unclustered.ply`.

**Between the cloud going in and the two surfaces coming out there is nothing on disk.** Every question
argued this week is a question about *which points belong to which region* — did the growth find two
walls, did the merge fuse them, did the 3 mm reassignment swallow one. A picture of a raw cloud at each
step would show the same grey cloud at each step, because none of these steps moves the points; they
only relabel them.

So each dump must carry a **per-point cluster id** (and the normal, so the same file also shows whether
the normals were usable at all). Then one render coloured by id answers the question at a glance, and
one PLY parser answers it as a table.

## The rungs to write

One file per rung per piece, ASCII PLY with two extra scalar columns (`cluster` int, `reason` uchar),
plus a `.json` sidecar. Same point set for rungs 2-5, so they can be diffed point by point.

1. `r1_downsampled` — the cloud entering clustering, after the density step, with normals, and the
   sidecar naming the sampling policy and the spacing actually used.
2. `r2_clusters_premerge` — that cloud with the cluster id from the growing step, `-1` for points
   never claimed, and the sidecar carrying the cluster sizes and the floor actually applied
   (`dynMinCluster`), not the configured `minCluster`.
3. `r3_after_merge` — relabelled after `mergePaper234`, with every merge written into the sidecar:
   which cluster into which, the pair count, and the criteria values that fired.
4. `r4_after_reassign` — after the boundary reassignment, with a per-point reason code: admitted to
   cluster 0 / admitted to cluster 1 / rejected-distance / rejected-normal, and the **radius actually
   used** in the sidecar. This is the rung that decided the Juglet question and it leaves no trace
   today.
5. `r5_write` — which points reached `Surface_0`, which `Surface_1`, which neither, plus the write
   gate's decision (pair / single / none).

Naming: `dump/<piece>/r<N>_<name>.ply` + `.json`. ASCII, so an instrument can read it without a PCL
dependency — a binary PCD already killed one of our coverage scripts.

**Colour is the reading, so the colour has to be stable.** Cluster id 0 is always the same colour, id 1
always the next, `-1` (never claimed) always grey, and that mapping is identical in every panel, every
rung and every piece. If colours were assigned per panel, a merge and a renumbering would look the same
and the ladder would be unreadable. At rung 4 the cluster colour stays primary — a point keeps the
colour of the region it ended up in — with rejected points drawn as small grey dots, so the swallowing
is visible as colour 1's points turning into colour 0's, and the reason code read from the sidecar
rather than from the picture.

## Cost guard (this is the part that can sink the run)

Geometry is what makes this project's archives 97 % payload, and the last three jobs each deleted
664 MB to 3.3 GB of stage geometry. A ladder over 9 pieces x 4 arms would be tens of GB.

- `SFS_DUMP_STAGE=<dir>` — **unset writes nothing at all** (see acceptance 1).
- `SFS_DUMP_PIECES=<name,name,...>` — only the pieces named are dumped. Two are enough: one that still
  reaches two clusters (`Juglet_Piece_3`) and one that reaches none (`Juglet_Piece_2`).
- Each rung holds that cloud's own point count (2 000-25 000) with two extra columns: a few MB, not a
  mesh.

## What each rung must be checked against

A ladder with no expectation is a photo album. The sidecar prints a measured-vs-expected line per rung:

- **r2** — are there two or more regions whose mean normals are opposite (dot <= -0.9) and whose nearest
  cross distance is >= 1.5 mm? (the wall-pair test applied to raw regions, not to fitted surfaces)
- **r3** — did the count change, which merge fired, with its criteria values?
- **r4** — how many points that belonged to the second region at r3 were admitted into the first at r4,
  and through which window?
- **r5** — how many points reached a surface, and did the piece get one or two?

Print these as `out/ladder.tsv`, one row per (piece, rung): the expectation, the measured values, and
pass/fail.

## Arms

No new method arms. The ladder is measured inside arms that already exist:

- **A** today's defaults, `SFS_DUMP_STAGE` unset — the defaults proof.
- **B** today's defaults + dumping, pieces 3 and 2.
- **C** the same dump with `SFS_DOWNSAMPLE_TARGET=-1` (native cloud), same two pieces, so the ladder
  can be read at both densities.

## Constraints

- With the switch unset, output must be byte-for-byte what it is today. That is acceptance 1.
- No change to any threshold, tolerance, growth rule, merge rule, reassignment rule or write rule.
- Compute nodes only. Corpus and `/opt/sfs-pristine` read-only, md5 before and after.
- At most four jobs. Each polled laptop-side; final `sacct` State/ExitCode recorded in the run directory.
- Keep the ladder dumps (they are the deliverable); delete the rest of the stage geometry with a counted
  record in `out/GEOMETRY_DELETED.txt`.
- One appended `index.tsv` row with **verdict and human_note left EMPTY**.

## Acceptance criteria

1. **Defaults proof:** with `SFS_DUMP_STAGE` unset, every written surface md5 is identical to the
   pre-change binary's, and no `dump/` directory is created.
2. Rungs 1-5 exist for the named pieces; each is a readable PLY carrying that step's point count; each
   sidecar names the radius, floor and merge values **actually used**.
3. `out/ladder.tsv` has one row per (piece, rung) with expectation, measured values and pass/fail —
   evidence only.
4. **One figure per dumped piece: a strip of panels r2 | r3 | r4 | r5, coloured by cluster id.** The
   camera, the scale and the colour-to-cluster-id mapping are **identical in every panel and for every
   piece**, so a region can be followed from rung to rung and a merge reads as one colour swallowing
   another rather than as a recolour. Each panel carries a scale bar, and one shared legend lists each
   colour with its cluster size at that rung. The scale must resolve the wall gap (this material's gaps
   are 0.75-3.43 mm). **Return the path, do not attach the image.**
5. No tracked source changed except `mesh_processing_headless.cpp`.
6. Corpus and `/opt/sfs-pristine` md5 before/after identical.
7. Geometry deleted with a counted record; ladder dumps kept, their paths reported.

## What this cannot settle

- It shows where a decision changed, not whether the decision was right. A merge of two regions is
  **correct** when they are one wall and wrong when they are two, and the ladder alone cannot tell the
  difference — that test is the dot and the cross distance above.
- The wall gap is known from the mesh, so a label that looks wrong against a flat picture may still be
  right against the surface.
- Two pieces and one spacing policy is a sample of the ladder, not a survey of it.
