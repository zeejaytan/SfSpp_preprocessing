# 15: Where in the mesh stage does Surface_0 lose 2mm of edge?

**Answers:** E1

**Blocked by:** nothing — measurement with small diagnostic code changes

**Status:** ready-for-agent

**Needs-eye:** none — tables of numbers, no geometry claim. A render enters
only if the inset needs judging by eye.

## Established coming in (measured, not assumed)

Piece 2's chain, same reference (169 pts), same 2mm threshold:

| stage | n | ref within 2mm |
|---|---|---|
| mesh input (Point.pcd) | 60,000 | 96.4% |
| SampledWithNormals (post-downsample) | 8,977 | **100%**, med 0.49 |
| Surface_0 (post-split+fit) | 11,263 | **82.2%**, med 1.26 |
| unclustered | 1,428 | 100%, med 0.53 |
| Surface_1 | 171 | 10%, med 45 |

Downsampling exonerated (96→100%). The loss (100% → 82%, scattered
2.0–2.8mm misses, not a missing region; stored normals fine at 0.993) sits
inside surface construction, which is three sub-stages:

1. **RegionGrowing split** — the fracture strip lands in unclustered (which
   covers 100% including 18% covered NOWHERE else). The split assigns the
   edge strip away from both walls. By itself this explains the shortfall
   IF the fit faithfully follows its input cluster.
2. **Random 10k sample** (`improveSurfaceBoundaryByFittingBSplineSurface`:
   `rs.setSample(10000)`, UNSEEDED) — a different 10k points every run.
   Prime suspect for the run-to-run variation (pieces 2, 5, 6 differing
   byte-wise between identical-input runs). Never quantified.
3. **NURBS fit** (order 3, 8 iterations, mesh 128) + resample to 11,263 —
   smoothing a ragged fracture edge insets it. Never measured against its
   input cluster.

(1) is proven as a contributor (the strip is in unclustered — there is no
other place for it to have gone). (2) and (3) are unseparated because the
raw region clusters are never saved: only fitted `Surface_0/1.ply` survive,
so split-loss vs fit-inset cannot be told apart from disk.

## What to do (in order — each step cheap, each gates the next)

1. **Seed test (no code change): run the mesh stage twice, diff Surface_0.**
   If S0 differs run-to-run, (2) contributes and every gate number in this
   chain needs an error bar. If identical, the sampler is effectively stable
   and (2) is out. One holder run, `cmp` verdict.
2. **Save the raw clusters (diagnostic code change, ~10 lines):** write
   `cloudWithNormals_Cluster1/2` BEFORE `improveSurfaceBoundary...` runs,
   alongside the fitted outputs. Then measure raw-cluster vs fitted-surface
   rim coverage on piece 2:
   - raw covers, fitted does not → the FIT insets the edge (3). Fix lives
     in fit parameters or robust fitting.
   - raw already lacks it → the SPLIT lost it (1). Fix lives in split
     thresholds or in routing unclustered points to the rim source.
3. **Do not** retune smoothness/curvature blindly: ticket 12 showed the
   default is optimal and both directions hurt or crash. Any split change
   is judged by the per-stage coverage table + gate from 11/15, never by
   cluster counts alone.

## Acceptance criteria

- [ ] Mesh stage run twice; Surface_0 diff reported (seed question settled)
- [ ] Raw pre-fit clusters saved and measured: split-loss vs fit-inset
      attributed with numbers, not argued
- [ ] The 2mm shortfall attributed to ONE of split / sample / fit, with the
      measurement that rules out the other two
- [ ] Ticket 14 pointed at the attributed sub-stage (it currently says
      boundary estimation, which ticket 13 named before this refinement)
- [ ] Authors' arm in every comparison (ticket 11's rule)

## Note

Ticket 12's Euclidean-tolerance theory is dead (wrong stage — recorded in
12). Ticket 11's radius sweep is unaffected (different stage, still valid).
The `// 2cm` comment discrepancy at `mesh_processing_headless.cpp:658` is
still open and still worth fixing as hygiene when this area is touched, but
it is NOT the cause and must not be presented as one.
