## Results

Read-only, 2026-10-24. Run directory (all scripts and outputs quoted below live here):

    /data/gpfs/projects/punim2657/SfSpp/runs/20261024-1417_dc869d4_p279-basefaces/

Nothing in this ticket ran a pipeline, built anything, or touched a C++ file. Every number below is a
cell of a file in that directory.

### Phase 0 — reachability of every reference lane (STOP condition not fired)

`phase0_reachability.tsv` — 326 rows, one per (piece, lane), columns documented in `p279_p0.py`.
Distance from each reference dot to their own Surface_0 and Surface_1, in mm:

| measure (per lane) | p50 | p90 | max |
|---|---|---|---|
| median best distance | 0.270 | 0.301 | 0.346 |
| p90 best distance | 0.523 | 0.579 | 0.729 |
| max best distance | 0.868 | 1.141 | 1.745 |

326/326 lanes have median best distance <= 1 mm, 258/326 have max best distance <= 1 mm, and no lane has
a median above 2 mm. The lane-to-surface assignment is unanimous: **all 163 lane-0 references are closest
to Surface_0 and all 163 lane-1 references to Surface_1**, so their lane numbering matches ours.

Pot C 03, the piece the stop condition was pre-registered for: Breakline_0 has 191 dots at median
0.2586 / p90 0.4633 / max 0.9298 mm from Surface_0 against 20.07 mm from Surface_1; Breakline_1 has 120
dots at median 0.2760 / p90 0.6003 / max 0.9928 mm from Surface_1 against 9.975 mm from Surface_0.
**It is within 1 mm of their own surface — Phase 1 proceeds.**

### Phase 1 — which surfaces are a complete base disc

The rule (fixed before looking at the counts, `p279_p1.py`, one row per surface in `phase1_scan.tsv`):
a surface counts as a complete base disc when

- `nsel` >= 360 — points with |n . axis| > 0.95, where 360 = 36 azimuth bins x 10 points, i.e. the
  smallest region that can satisfy the bin rule at all;
- `bins10` == 36 — all 36 bins hold >= 10 such points (the region wraps the axis);
- `l3l1` <= 0.02 — PCA thickness over length, i.e. a face, not a lump (l3/l1 without sqrt);
- `edge_cv` <= 0.15 — sd/mean of the per-bin 95th-percentile radius, i.e. a closed, near-circular
  outer edge;
- `ax_spread` <= 0.30 * r50 — the region occupies a thin slab along the axis.

| threshold | pieces flagged |
|---|---|
| edge_cv 0.10 | 3 |
| **edge_cv 0.15 (chosen)** | **3** |
| edge_cv 0.25 | 4 (+ Pot B 01 S1, edge_cv 0.169) |
| edge_cv 0.35 | 5 (+ Pot B 01 S0 0.301, Pot D 03 S0 0.316) |
| nsel 150 / 300 / 600 | 3 / 3 / 3 — no effect |
| l3l1 0.01 / 0.05 | 3 / 3 — no effect |

122 of the 326 surfaces have >= 30 axis-normal points and 74 reach `nsel` >= 360, so the flag is not
vacuous. The three flagged pieces are **Pot A 01, Pot C 03, Pot J 03**; the two loose-threshold additions
are flat plate faces whose outline is not circular, not discs.

| Pot | flagged by us | paper actual | paper detected |
|---|---|---|---|
| A | 1 | 1 | 0 |
| B | 0 | 1 | 1 |
| C | 1 | 1 | 1 |
| D | 0 | 3 | 6 |
| E | 0 | 4 | 7 |
| F | 0 | 3 | 3 |
| G | 0 | 4 | 4 |
| H | 0 | 5 | 6 |
| I | 0 | 3 | 6 |
| J | 1 | 1 | 3 |
| **total** | **3** | **26** | **37** |

We are not in excess — we are 23 short, and the deficit has three named causes, none of them a base face
missing from their surfaces:

1. **A base sherd is not a complete disc.** A sherd holding a 40-degree arc of the base cannot fill 36
   azimuth bins; the flag asks for a closed ring, which only a piece carrying the whole base can pass.
   The paper counts *sherds that contain base material*; this rule counts *surfaces that are an entire
   base face* — different predicates on the same corpus.
2. **Their 26 is a classifier label, not geometry.** TABLE III's own row reads 37 detected against 26
   actual with 14 false negatives, and the text attributes the detector to prior work [9], an
   assembly-stage classifier. Reproducing it from surface geometry was never on offer.
3. **Corpus.** Our 163 pieces minus the <50-point removals the paper lists (1 C, 2 D, 4 E, 2 F, 3 I,
   8 J = 20) is 143, exactly TABLE III's "# sherds" total, so the comparison is on the same set.

### Phase 2 — the decisive question, per base piece

Their per-surface measurements for the three flagged pieces (`phase1_scan.tsv`). `r` is the radius
about that piece's axis; `axial span` is the extent along it; `axlo_frac` is where the region sits in
the piece's own axial span:

| piece | surface | n | nsel | frac | r5 / r50 / r95 | axial span | axlo_frac | edge_cv | l3l1 |
|---|---|---|---|---|---|---|---|---|---|
| Pot A 01 | S0 | 19463 | 18376 | 0.944 | 11.756 / 37.369 / 53.287 | 4.382 | 0.389 | 0.0799 | 0.0025 |
| Pot A 01 | S1 | 17145 | 7746 | 0.452 | 33.124 / 43.287 / 54.812 | 6.902 | 0.572 | 0.0729 | 0.0050 |
| Pot C 03 | S0 | 14590 | 7461 | 0.511 | 7.520 / 23.988 / 33.353 | 1.074 | 0.194 | 0.0814 | 0.0029 |
| Pot C 03 | S1 | 8150 | 5447 | 0.668 | 6.427 / 20.430 / 28.343 | 1.358 | 0.073 | 0.0836 | 0.0028 |
| Pot J 03 | S0 | 13330 | 7297 | 0.547 | 7.247 / 22.998 / 32.453 | 0.813 | 0.852 | 0.0573 | 0.0009 |
| Pot J 03 | S1 | 8455 | 6059 | 0.717 | 6.641 / 20.999 / 33.338 | 3.489 | 0.937 | 0.0718 | 0.0030 |

**Is the base inside their Surface_0, Surface_1 or neither?** In all three pieces it is *inside one of
the two* — the whole surface is the base face, not a region embedded in a bigger surface. Pot C 03 and
Pot J 03 each hold two discs a few mm apart (S0 axial 1.074 vs S1 1.358, and 0.813 vs 3.489), the two
faces of one flat sherd; Pot A 01 is the same situation with a wider dish. Which of the two faces is the
pot's underside cannot be decided from the two surface files alone, and nothing below depends on it.

**Where does the reference line sit?** (`a279_edge.py` -> `edge_check.txt`, `a279_rad.py` ->
`rad_check.txt`; `d_med` is the dot-to-surface distance, the last column the fraction of dots within
1 mm of the surface's own r95 radius):

| piece | lane -> surface | ndot | dot radius p5 / p50 / p95 | dot radius min-max | d_med / d_p90 / d_max | frac within 1 mm of r95 |
|---|---|---|---|---|---|---|
| Pot A 01 | 0 -> S0 | 208 | 46.00 / 53.17 / 70.64 | 44.75 - 74.38 | 0.281 / 0.574 / 1.049 | 0.024 |
| Pot A 01 | 1 -> S1 | 214 | 47.54 / 54.11 / 72.84 | 46.28 - 76.92 | 0.252 / 0.452 / 0.742 | 0.014 |
| Pot C 03 | 0 -> S0 | 191 | 35.95 / 44.51 / 55.78 | 35.32 - 56.15 | 0.259 / 0.463 / 0.930 | 0.073 |
| Pot C 03 | 1 -> S1 | 120 | 32.58 / 33.83 / 34.91 | 32.33 - 35.20 | 0.276 / 0.600 / 0.993 | 0.733 |
| Pot J 03 | 0 -> S0 | 189 | 32.79 / 39.53 / 56.22 | 31.28 - 56.53 | 0.264 / 0.520 / 0.747 | 0.201 |
| Pot J 03 | 1 -> S1 | 120 | 33.23 / 33.92 / 34.82 | 32.96 - 35.00 | 0.270 / 0.552 / 0.670 | 0.833 |

The two tea-pot disc lanes (Pot C 03 lane 1, Pot J 03 lane 1) ride **one radius** — the disc's outer rim,
2.9 and 2.0 mm wide in radius, with 73.3% and 83.3% of their dots within 1 mm of the surface's
95th-percentile radius. The wall lanes (Pot C 03 lane 0, Pot J 03 lane 0, both Pot A 01 lanes) spread over
20-30 mm of radius: they follow the sherd's ragged break edge, not any circle. So their edge line is the
*boundary* of the surface it belongs to in both cases — it is a rim only where the boundary is a rim.

**Pot C 03 worked in full** (`a279_c03_probe.py`): their S0 is 14590 points (r 10.56/33.64/52.05, axial
436.4/437.5/457.8, |n . axis| median 0.962), their S1 is 8150 points (r 7.89/25.05/33.17, axial
427.4/431.0/431.6, |n . axis| median 0.996). Distances from *our* 276 clusters into *their* two surfaces
(median / p90 / max, and the share within 1 mm):

| our cluster | n | -> their S0 | -> their S1 | reading |
|---|---|---|---|---|
| c0 interior bowl | 23446 | 0.300 / 0.472 / 0.921, 100% | 7.578 | their S0 IS our interior region |
| c1 exterior wall | 17245 | 5.992 / 8.083 / 10.472, 0% | 14.456 | our wall is in **neither** of their surfaces |
| c2 base band | 13265 | 5.805 | 0.295 / 0.463 / 0.832, 100% | **their S1 IS the base disc we drop** |
| c3-c7 debris (603/521/497/224/206) | 2051 | 2.649 - 3.468 | | in neither |

Their two surfaces on Pot C 03 are therefore *(interior bowl + inner wall)* and *(base disc)*. Ours are
*(interior bowl)* and *(exterior wall)*. Their S1 stops at radius ~33-34 mm, exactly where our
unclustered corner ring begins (34.09-36.65 mm, ticket 278). This is the answer the ticket was opened
for: **the base face is one of their two surfaces, and it is the very band we classify out.**

**Our side, the four meshed pieces** (`a279_our.py` -> `our_side.txt`, the ticket 276 Phase 3a dumps;
our clusters carry no per-point normals, so the normal is the PCA plane normal and `l3l1` is not
comparable to the table above). The dump legend is `surface 1` = kept, `0` = dropped — it is not a
slot number:

| piece | our clusters | complete-disc cluster by the Phase 1 rule | kept? |
|---|---|---|---|
| Pot C 03 | 8 | c2, 13265 pts: |n . axis| 1.000, 36/36 bins, edge_cv 0.025, l3l1 0.0044 | **no** (kept pair = c0 23446 + c1 17245) |
| Pot C 01 | 7 | none — c0 48961 pts has |n . axis| 0.127 and 18/36 bins | — |
| Pot H 02 | 12 | none — c0 17091 pts, |n . axis| 0.983 but only 13/36 bins, edge_cv 0.424 | — |
| Pot H 10 | 9 | none — c0 4484 pts fills 36/36 bins but edge_cv 0.459 (ragged outline, not a ring) | c0 is kept, yet it is not a disc |

So on our side the base is one of the two surfaces in **0 of 4** pieces, and the only complete base disc
in the set (Pot C 03's band) is the cluster we drop.

**Corpus-wide boundary test** (`a279_boundary.py` -> `boundary_test.tsv`, `boundary_summary.txt`).
For each reference dot: nearest surface point q, its neighbours within 2 mm, projected into q's tangent
plane using their surface normals, and the largest angular gap; boundary-like when the gap exceeds 100
degrees. All 326 matched (surface, lane) pairs:

| group | median gap p10 / p50 / p90 | lanes with median > 100 deg | mean share of dots > 100 deg |
|---|---|---|---|
| lane 0 -> Surface_0 | 155.9 / 164.9 / 173.7 | 163 / 163 | 91.7% |
| lane 1 -> Surface_1 | 159.0 / 167.6 / 175.6 | 163 / 163 | 91.6% |

Worst single lane 140.0 deg (Pot I 29, Surface_0, lane 0). The mismatched pairs read 183.4 deg and are
not a control — those dots are far from that surface. **Every reference breakline in the corpus is the
boundary curve of the surface it belongs to**, so their edge line comes from the surface boundary, with
no separate base rule and no line drawn on a region their surfaces do not contain.

### Phase 3 — verdict

**(i) Their surfaces contain the base.** The fix is in growth/merge, and the two-largest rule stands.

Three numbers carry it:

1. **0.295 mm, 100%** — on Pot C 03 their Surface_1 is our dropped band: 13265 of our points at 0.295 mm
   median, p90 0.463, max 0.832, all within 1 mm, while their Surface_0 is 5.805 mm away from it. The
   base face is not missing from their output; it is their second surface.
2. **0.276 mm at 73.3%** — their Breakline_1 rides that band's outer rim: median 0.276 mm from their S1,
   dot radii p5/p50/p95 32.58/33.83/34.91 mm, 73.3% of the 120 dots within 1 mm of the surface's own
   95th-percentile radius.
3. **326/326 lanes** — every reference line in the corpus is a surface boundary (median max angular gap
   164.9 / 167.6 deg), so the line always comes from a surface they kept, never from a base region their
   own selection excluded.

The paper has no base step to port: preprocessing is sample -> region grow (n_b 10, tau_theta 4,
tau_kappa 1) -> B-spline refine -> "we select the two largest clusters" (:147-168); the edge line is "the
interior surface point cloud boundary ... extracted using the point cloud boundary-estimation method from
the PCL library" resampled at 1.9 mm; the pipeline is named base-agnostic (abstract) and base information
is listed as future work (:460). TABLE III's base row counts an assembly-stage classifier inherited from
[9], not a preprocessing product.

**What this says about the fix** (not built, per the ticket): the selection rule is not the difference. On
Pot C 03 their second surface is the base disc (8150 pts) while ours is the exterior wall (17245 pts), and
that wall is in neither of their surfaces (5.992 mm from S0, 14.456 mm from S1) — so in their run the wall
either did not form a cluster or was smaller than the base disc, and the same two-largest rule then kept
the base. Ours is bigger than our base (17245 vs 13265), so the rule keeps the wall. Reaching their
pairing is a growth/merge problem: the base must stop being a separate cluster, or stop being the
third-largest one — which is exactly the re-entrant corner ticket 278 measured, 2.4872 mm between the band
and both kept faces with 0 of 1175 slab points within 1 mm of both sides.

**The one measurement that would overturn it:** a reference breakline that traces a base region which is
*not* one of its piece's two surfaces — dots neither within 1 mm of a surface nor on its boundary. That is
exactly the boundary test above, run over all 326 lanes, and it found none (the worst lane's median gap is
140.0 deg, still boundary-like). A single piece failing it — a line riding a base arc interior to a kept
surface, at a gap well under 100 deg — would move the verdict to (ii) and imply a base pass we have not
ported.

