# 02 — Probe the 20 author-excluded special-part meshes

**Answers:** E3
**Type:** task
**Blocked by:** None
**Status:** ready-for-agent
**Worker:** unassigned
**Hand-over:** DeepSeek (hidden acceptance check to be staged before dispatch)

## Question

What are the `20` special-part meshes excluded from the authors' released `Point/` benchmark (across Pots C, D, E, F, I, and J) on Spartan, and what does our un-modified pipeline (`cc_mesh_to_pcd.sh` -> `MeshPreprocessingHeadless` -> `sfs_axes`) do when fed them directly (cluster count, wall point counts, rendered 3D walls with `20 mm` scale bars, and candidate axes)?

## Related tickets

- Independent of [Census attached appendages in t09 and Juglet](issues/01-census-attached-appendages-in-t09-and-juglet.md); unblocks [Decide appendage guard location and scope](issues/04-decide-appendage-guard-location-and-scope.md).
