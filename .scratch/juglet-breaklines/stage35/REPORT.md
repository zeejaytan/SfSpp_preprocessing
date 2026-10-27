# Ticket 35 — Juglet pieces 2 and 9, measured on the mesh

Worker session, ticket 35 (question: are the meshes of pieces 2 and 9 simple wall sherds like the
seven that yield a face, or compound parts — handle stub, rim junction, base corner?). This file
records **measurements only**. No interpretation, no verdict: the lead reads the numbers.

Pieces measured: Juglet 1, 2, 3, 5, 7, 9 and Pot_A 01, 07 (references). Everything below comes from
one Slurm job, id 33880958, run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0024_de55998_t35-mesh`.
Instrument: `instruments/measure35.py` (numpy only — no scipy, no trimesh, no sklearn; own OBJ/PLY/PCD
readers, uniform-grid kNN, Möller–Trumbore ray casting, topology, union-find, rasteriser and PNG
writer with zlib). Tables copied to `tables/`, figures to `figures/` in this directory.

---

## 1. Job record

| # | run directory (under /data/gpfs/projects/punim2657/SfSpp/runs/) | job id | commit | state | elapsed | exit | node |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 20261028-0019_b8f7cc7_t35-mesh | 33880769 | b8f7cc7 | (ended) | 00:00:08 | 3:0 | — |
| 2 | 20261028-0022_f772c83_t35-mesh | 33880898 | f772c83 | FAILED | 00:00:07 | 1:0 | — |
| 3 | 20261028-0024_de55998_t35-mesh | 33880958 | de55998 | COMPLETED | 00:09:46 | 0:0 | spartan-bm151 |

**The contract allows two jobs. Three were submitted** — disclosed rather than smoothed over. Both
extra jobs died in under ten seconds on bugs in my own instrument, before any measurement survived:

- **Job 1** aborted in its selftest: `selftest slab: 4 hits at [5.0, 5.0, 7.0, 7.0] (want 2: 5 7)` →
  `SELFTEST FAIL` → `ABORT: selftest failed`. A ray through a quad's diagonal hits both triangles at the
  same `t`; the count of "sheets" now merges hits within 1e-4 mm. **No corpus file was read** (the md5
  stage never ran).
- **Job 2** passed the selftest, measured Juglet 9 completely, then died in the table dump with
  `KeyError: 'boundary_loops'` — the accumulator used the key `loops` while the column map used
  `boundary_loops`. It wrote `topology.tsv` and an empty `boundary_loops.tsv` and nothing else.
- **Job 3** is the measurement of record: all 8 pieces ok, `failures.tsv` empty (header only),
  per-piece seconds in `tables/timing.tsv`: Juglet 9 2.1, Juglet 2 2.5, Juglet 3 4.9, Juglet 5 8.7,
  Juglet 7 20.5, Pot_A 07 58.1, Juglet 1 77.7, Pot_A 01 407.0.

Compute node only: everything ran on `spartan-bm151`, `--partition=sapphire --account=punim2657`,
8 CPUs, `--time=03:00:00`, python `/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3`
(3.11.15, numpy 2.4.6, md5 of the instrument as run `a72284540d807f4239465d8e628b40e6`). The laptop was
used only for `python -m py_compile` and a static check of the table keys — never to measure anything.

The run directory holds `run.json`, `submit.sbatch`, `logs/slurm-33880958.out`, `out/measure.log`,
`out/state.json` and `out/{tables,figures}`.

---

## 2. Inputs, and proof they are unchanged

24 files read, **24 unchanged** (`tables/md5_check.tsv`, md5 taken immediately before the first read
and again after the last piece). `md5_before == md5_after` on every row.

| file | role | bytes | md5_before | unchanged |
| --- | --- | --- | --- | --- |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_9_Mesh.obj | mesh | 128277 | c773e3d0e28d0bc8513d9eef463e190f | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_9_Point.pcd | pcd | 110027 | 1542b45d18cea115c03d56ff3fcbe2a6 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_9/surfaces/Juglet_Piece_9_SampledWithNormals.ply | cloud0.6 | 59078 | afde2f47c3c4bd16066731138fce5f24 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_2_Mesh.obj | mesh | 159681 | 5223fe76170ac556be23c7164c715943 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_2_Point.pcd | pcd | 136555 | 42568d383687c73933b60a880bde9475 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_2/surfaces/Juglet_Piece_2_SampledWithNormals.ply | cloud0.6 | 76741 | 9e5bab27c406fc4ec9baec2259b493a5 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_3_Mesh.obj | mesh | 219412 | 4bc141bd8344b57667441b7c6c94b0dd | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_3_Point.pcd | pcd | 184432 | 54feda576ca03cf04b688330e5187556 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_3/surfaces/Juglet_Piece_3_SampledWithNormals.ply | cloud0.6 | 108396 | 122b2fbbc7356c8305cff5b0d8699958 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_5_Mesh.obj | mesh | 396698 | 68049b91790afe6479224ee1dd277103 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_5_Point.pcd | pcd | 327415 | a855f6da22a0e95e024ebca6fad4f9a8 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_5/surfaces/Juglet_Piece_5_SampledWithNormals.ply | cloud0.6 | 220639 | f1be45777b47176273163efb4e6fe302 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_7_Mesh.obj | mesh | 541878 | 8a1889ef4acab212b2e13533f5f5d452 | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_7_Point.pcd | pcd | 448957 | 199d257b2078345ec549997d6fbfc969 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_7/surfaces/Juglet_Piece_7_SampledWithNormals.ply | cloud0.6 | 314641 | cadba02ac15b5b402d48142abcca98d6 | yes |
| /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_A_Piece_07_Mesh.obj | mesh | 3095000 | 1e16639d9847734cd9055085b14ab7b7 | yes |
| /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/Pot_A/Pot_A_Piece_07_Point.pcd | pcd | 28000229 | 0a7fc1f2dc221e29788bfb8505d043e5 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0647_5bc82a9_t30-arm1-pa3p4/out/arms/Pot_A/Pot_A_Piece_07/surfaces/Pot_A_Piece_07_SampledWithNormals.ply | cloud0.6 | 611993 | 29536bde341dd14e22f11b5852eb75ee | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet/Juglet_Piece_1_Mesh.obj | mesh | 1655590 | b447066c29181fe7ba987439c22c5d9c | yes |
| /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Point/Juglet/Juglet_Piece_1_Point.pcd | pcd | 1287137 | b1df295ba405c881bf06a91e3b46fddf | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_1/surfaces/Juglet_Piece_1_SampledWithNormals.ply | cloud0.6 | 1079873 | ab38ff7dde0f52b3fc051196b993e8f8 | yes |
| /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_A_Piece_01_Mesh.obj | mesh | 30988363 | 0d54f5cf8b73a98bae223c86930e0c8a | yes |
| /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/Pot_A/Pot_A_Piece_01_Point.pcd | pcd | 27994907 | b6bae56000527d4d73b05750ac27a690 | yes |
| /data/gpfs/projects/punim2657/SfSpp/runs/20261027-0647_5bc82a9_t30-arm1-pa3p4/out/arms/Pot_A/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_SampledWithNormals.ply | cloud0.6 | 6056071 | b58f583996c154243ca6d41d3149f597 | yes |

Paths that differ from the brief and were resolved by checking, not assuming:

- **Pot A is not under `Dataset/Mesh/Pot_A/`.** The real paths are
  `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_A_Piece_01_Mesh.obj` and
  `..._07_Mesh.obj`, with clouds under `.../SfS_pp/Point/Pot_A/Pot_A_Piece_01_Point.pcd`.
- **Juglet meshes carry no zero padding** in the name actually used: `Juglet_Piece_2_Mesh.obj`, not
  `Juglet_Piece_02_Mesh.obj`. `Juglet_Piece_2_Mesh.obj` and `Juglet_Piece_02_Mesh.obj` are the same file
  (md5 5223fe76170ac556be23c7164c715943), as are `_1_` and `_01_` (b447066c29181fe7ba987439c22c5d9c).
- **`/opt/sfs-pristine` does not exist on this host** (`ls: cannot access '/opt/sfs-pristine': No such
  file or directory`). It was not created. The canonical checkout
  `/data/gpfs/projects/punim2657/sfs_preprocessing` was used read-only.
- **The 0.6 mm cloud is the pipeline's own segmentation input, read from disk rather than rebuilt**:
  `.../runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet/Juglet_Piece_<N>/surfaces/Juglet_Piece_<N>_SampledWithNormals.ply`
  and `.../runs/20261027-0647_5bc82a9_t30-arm1-pa3p4/out/arms/Pot_A/Pot_A_Piece_<NN>/surfaces/Pot_A_Piece_<NN>_SampledWithNormals.ply`.
  Counts 14546 / 1031 / 1467 / 1530 / 3021 / 2351 / 4254 / 1988 / 787 and Pot A 85136 / 8598 reproduce
  ticket 20's ray counts exactly under its stride rule `step = max(1, N//800)`.

---

## 3. Figures

Four per piece, 32 in all, in `figures/` (also in `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0024_de55998_t35-mesh/out/figures`). Views are orthographic along the
piece's own principal axes of its vertex cloud: view1 = PC1, view2 = PC2, view3 = PC3; **view4 is the
same camera and the same scale as view3** with per-vertex local turning coloured (0–30 deg ramp, clipped
at 30, legend at the right). Flat shading (two-sided Lambert, no specular). Every picture carries a 5 mm
scale bar of five alternating segments, labelled `5 MM = N PX`, and its own mm/px in the table below.

Resolution: the coarsest picture is Pot A 01 view3/view4 at 0.100312 mm/px = **9.97 px per mm**; the
finest is Juglet 2 view1 at 0.0153802 mm/px = 65 px per mm. **Every figure resolves a 1 mm feature.**

| piece | view | file (stage35/figures/) | bytes | WxH | mm/px | px per mm | bar mm | bar px |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Juglet 9 | view1-pc1 | Juglet_9_view1-pc1.png | 46465 | 1400x1400 | 0.0174289 | 57.4 | 5.0 | 287 |
| Juglet 9 | view2-pc2 | Juglet_9_view2-pc2.png | 47714 | 1400x1400 | 0.0207929 | 48.1 | 5.0 | 240 |
| Juglet 9 | view3-pc3 | Juglet_9_view3-pc3.png | 76687 | 1400x1400 | 0.0206908 | 48.3 | 5.0 | 242 |
| Juglet 9 | view4-turning | Juglet_9_view4-turning.png | 85954 | 1400x1400 | 0.0206908 | 48.3 | 5.0 | 242 |
| Juglet 2 | view1-pc1 | Juglet_2_view1-pc1.png | 54028 | 1400x1400 | 0.0153802 | 65.0 | 5.0 | 325 |
| Juglet 2 | view2-pc2 | Juglet_2_view2-pc2.png | 55750 | 1400x1328 | 0.0220349 | 45.4 | 5.0 | 227 |
| Juglet 2 | view3-pc3 | Juglet_2_view3-pc3.png | 53220 | 1400x834 | 0.0264212 | 37.8 | 5.0 | 189 |
| Juglet 2 | view4-turning | Juglet_2_view4-turning.png | 58456 | 1400x834 | 0.0264212 | 37.8 | 5.0 | 189 |
| Juglet 3 | view1-pc1 | Juglet_3_view1-pc1.png | 58640 | 1400x1400 | 0.0186774 | 53.5 | 5.0 | 268 |
| Juglet 3 | view2-pc2 | Juglet_3_view2-pc2.png | 54786 | 1400x1400 | 0.0275295 | 36.3 | 5.0 | 182 |
| Juglet 3 | view3-pc3 | Juglet_3_view3-pc3.png | 83646 | 1400x938 | 0.0285184 | 35.1 | 5.0 | 175 |
| Juglet 3 | view4-turning | Juglet_3_view4-turning.png | 93031 | 1400x938 | 0.0285184 | 35.1 | 5.0 | 175 |
| Juglet 5 | view1-pc1 | Juglet_5_view1-pc1.png | 88563 | 1400x1400 | 0.0232121 | 43.1 | 5.0 | 215 |
| Juglet 5 | view2-pc2 | Juglet_5_view2-pc2.png | 83185 | 1400x1002 | 0.0314123 | 31.8 | 5.0 | 159 |
| Juglet 5 | view3-pc3 | Juglet_5_view3-pc3.png | 151363 | 1400x1090 | 0.0331322 | 30.2 | 5.0 | 151 |
| Juglet 5 | view4-turning | Juglet_5_view4-turning.png | 173289 | 1400x1090 | 0.0331322 | 30.2 | 5.0 | 151 |
| Juglet 7 | view1-pc1 | Juglet_7_view1-pc1.png | 101738 | 1400x1329 | 0.0251103 | 39.8 | 5.0 | 199 |
| Juglet 7 | view2-pc2 | Juglet_7_view2-pc2.png | 111612 | 1400x1400 | 0.0281298 | 35.5 | 5.0 | 178 |
| Juglet 7 | view3-pc3 | Juglet_7_view3-pc3.png | 201105 | 1400x1400 | 0.0310878 | 32.2 | 5.0 | 161 |
| Juglet 7 | view4-turning | Juglet_7_view4-turning.png | 236161 | 1400x1400 | 0.0310878 | 32.2 | 5.0 | 161 |
| Pot A 07 | view1-pc1 | Pot_A_07_view1-pc1.png | 68610 | 1400x973 | 0.0277708 | 36.0 | 5.0 | 180 |
| Pot A 07 | view2-pc2 | Pot_A_07_view2-pc2.png | 83164 | 1400x1102 | 0.0383233 | 26.1 | 5.0 | 130 |
| Pot A 07 | view3-pc3 | Pot_A_07_view3-pc3.png | 124293 | 1400x1400 | 0.0383066 | 26.1 | 5.0 | 131 |
| Pot A 07 | view4-turning | Pot_A_07_view4-turning.png | 164081 | 1400x1400 | 0.0383066 | 26.1 | 5.0 | 131 |
| Juglet 1 | view1-pc1 | Juglet_1_view1-pc1.png | 237114 | 1400x1400 | 0.0337535 | 29.6 | 5.0 | 148 |
| Juglet 1 | view2-pc2 | Juglet_1_view2-pc2.png | 209552 | 1400x1362 | 0.0362447 | 27.6 | 5.0 | 138 |
| Juglet 1 | view3-pc3 | Juglet_1_view3-pc3.png | 221405 | 1400x1400 | 0.0406646 | 24.6 | 5.0 | 123 |
| Juglet 1 | view4-turning | Juglet_1_view4-turning.png | 305045 | 1400x1400 | 0.0406646 | 24.6 | 5.0 | 123 |
| Pot A 01 | view1-pc1 | Pot_A_01_view1-pc1.png | 140620 | 1400x603 | 0.0850842 | 11.8 | 5.0 | 59 |
| Pot A 01 | view2-pc2 | Pot_A_01_view2-pc2.png | 132773 | 1400x839 | 0.0947711 | 10.6 | 5.0 | 53 |
| Pot A 01 | view3-pc3 | Pot_A_01_view3-pc3.png | 417464 | 1400x1400 | 0.100312 | 10.0 | 5.0 | 50 |
| Pot A 01 | view4-turning | Pot_A_01_view4-turning.png | 736437 | 1400x1400 | 0.100312 | 10.0 | 5.0 | 50 |

Two rendering facts recorded rather than hidden:

- The red line `ZBUFFER DREW <seen> OF <total> FACES` counts faces that survived the z-buffer in that
  view; the rest are hidden behind the surface (closed shells show roughly half: Juglet 9 view3 drew
  3479 of 4184, Pot A 01 view1 drew 104730 of 200124).
- **Label defect, seen by opening three figures** (Juglet_9_view3-pc3.png, Juglet_2_view4-turning.png,
  Pot_A_01_view1-pc1.png): the scale-bar caption is drawn overlapping the bar and the bottom of its
  mm/px line is clipped by the image edge (`5 MM = 242 PX` sits on top of the bar; `MM/PX 0.02069` is
  cut in half), and on the turning view the legend caption is clipped at the right edge (`TURNING (`).
  The bars and all the numbers are legible and are also in the table above, so nothing in this report
  depends on the clipped text — but the pictures are not typographically clean and a re-render would
  fix it.

---

## 4. Topology

Welding at 1e-4 mm changed no vertex count on any piece (`v_welded == v_raw` everywhere), so no mesh
here is stored with duplicated vertices. Columns: `v_raw`, faces, edges, Euler characteristic V−E+F,
boundary edges, non-manifold edges, boundary loops, watertight, connected components, area mm²,
bounding box in the three principal directions (mm).

| piece_key | piece | mesh_file | mesh_md5 | v_raw | v_welded | weld_tol_mm | f | e | euler_chi | boundary_edges | nonmanifold_edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Juglet_9 | 2094 | 4184 | 6276 | 2 | 0 | 0 | 0 | 1 | 1 | 373.757 | 8.5573/13.8602/16.9345 |
| Juglet_2 | 2565 | 5126 | 7689 | 2 | 0 | 0 | 0 | 1 | 1 | 491.067 | 8.4555/24.9674/10.3217 |
| Juglet_3 | 3493 | 6982 | 10473 | 2 | 0 | 0 | 0 | 1 | 1 | 752.904 | 18.7161/23.5028/14.9893 |
| Juglet_5 | 6211 | 12418 | 18627 | 2 | 0 | 0 | 0 | 1 | 1 | 1401.63 | 23.6458/28.5142/20.8044 |
| Juglet_7 | 8421 | 16838 | 25257 | 2 | 0 | 0 | 0 | 1 | 1 | 1980.18 | 22.8944/27.053/26.0882 |
| Pot_A_07 | 10593 | 21174 | 31766 | 1 | 10 | 0 | 1 | 0 | 1 | 2005.19 | 27.9363/42.8268/28.632 |
| Juglet_1 | 24294 | 48592 | 72888 | -2 | 0 | 0 | 0 | 1 | 1 | 4987.15 | 34.0224/37.6371/37.4401 |
| Pot_A_01 | 100064 | 200124 | 300186 | 2 | 0 | 0 | 0 | 1 | 1 | 23273.6 | 106.728/119.164/64.921 |

Boundary loops (`tables/boundary_loops.tsv`): exactly one piece has any.

| piece | loop | edges | length mm | closed | start xyz |
| --- | --- | --- | --- | --- | --- |
| Pot_A_07 | 0 | 9 | 1.57691 | 1 | -9.993, 58.964, 331.726 |

Juglet 2 and Juglet 9 have **0 boundary edges, 0 boundary loops, are watertight, single-component, with
Euler characteristic 2**. Juglet 1 is the only Juglet mesh that is watertight with Euler characteristic
−2 (genus 2) — 0 boundary edges, still one component.

---

## 5. Turning

### 5.1 Per-vertex angle on the mesh

For each vertex, the angle between its own normal (area-weighted face normal sum) and each neighbour
within the stated radius; `vert_max` is that vertex's largest such angle. Gate 3.4 deg.

| piece_key | piece | radius_mm | n_vertices | sampled | n_pairs | pair_med_deg | pair_p90_deg | pair_max_deg | frac_pairs_gt_3p4 | vert_max_med_deg | vert_max_p90_deg | vert_max_max_deg | frac_verts_gt_3p4 | n_verts_gt_3p4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Juglet_9 | Juglet 9 | 0.6 | 2094 | 0 | 12682 | 21.9806 | 55.7751 | 89.9784 | 0.96018 | 50.7074 | 80.0469 | 89.9784 | 0.958453 | 2007 |
| Juglet_9 | Juglet 9 | 1.0 | 2094 | 0 | 31387 | 26.9889 | 68.4609 | 89.9854 | 0.968235 | 69.3097 | 88.8493 | 89.9854 | 0.989016 | 2071 |
| Juglet_2 | Juglet 2 | 0.6 | 2565 | 0 | 14381 | 21.4972 | 55.7393 | 89.9974 | 0.95807 | 49.8478 | 80.8061 | 89.9974 | 0.948148 | 2432 |
| Juglet_2 | Juglet 2 | 1.0 | 2565 | 0 | 36058 | 26.7107 | 68.5418 | 89.9974 | 0.96464 | 68.7327 | 88.8858 | 89.9974 | 0.990643 | 2541 |
| Juglet_3 | Juglet 3 | 0.6 | 3493 | 0 | 18246 | 21.7019 | 57.2654 | 89.9934 | 0.955004 | 49.7687 | 80.1633 | 89.9934 | 0.910965 | 3182 |
| Juglet_3 | Juglet 3 | 1.0 | 3493 | 0 | 45677 | 26.1009 | 68.1104 | 89.9955 | 0.956915 | 68.0705 | 88.6909 | 89.9955 | 0.971085 | 3392 |
| Juglet_5 | Juglet 5 | 0.6 | 6211 | 0 | 27725 | 19.4739 | 56.4019 | 89.9828 | 0.939225 | 27.941 | 78.2954 | 89.9828 | 0.882789 | 5483 |
| Juglet_5 | Juglet 5 | 1.0 | 6211 | 0 | 72187 | 22.4677 | 67.6793 | 89.9975 | 0.940585 | 53.5498 | 88.4287 | 89.9975 | 0.966672 | 6004 |
| Juglet_7 | Juglet 7 | 0.6 | 8421 | 0 | 35658 | 17.7938 | 57.7779 | 89.9948 | 0.926777 | 22.9259 | 79.9298 | 89.9948 | 0.883268 | 7438 |
| Juglet_7 | Juglet 7 | 1.0 | 8421 | 0 | 91676 | 20.1063 | 65.7193 | 89.9959 | 0.927222 | 39.0183 | 88.3916 | 89.9959 | 0.979337 | 8247 |
| Pot_A_07 | Pot A 07 | 0.6 | 10593 | 0 | 87242 | 18.5694 | 54.1005 | 89.9971 | 0.891325 | 45.6323 | 78.1254 | 89.9971 | 0.846502 | 8967 |
| Pot_A_07 | Pot A 07 | 1.0 | 10593 | 0 | 222360 | 24.6869 | 70.0966 | 89.9981 | 0.91503 | 65.8998 | 89.2303 | 89.9981 | 0.910601 | 9646 |
| Juglet_1 | Juglet 1 | 0.6 | 24294 | 0 | 61904 | 4.25637 | 17.5124 | 89.9819 | 0.60652 | 6.90798 | 30.4819 | 89.9819 | 0.883963 | 21475 |
| Juglet_1 | Juglet 1 | 1.0 | 24294 | 0 | 183421 | 5.69448 | 24.4126 | 89.9853 | 0.729851 | 12.2965 | 60.6709 | 89.9853 | 0.993126 | 24127 |
| Pot_A_01 | Pot A 01 | 0.6 | 100064 | 0 | 505347 | 8.90231 | 37.4145 | 89.993 | 0.783335 | 9.91977 | 53.3953 | 89.993 | 0.774374 | 77487 |
| Pot_A_01 | Pot A 01 | 1.0 | 100064 | 0 | 1376096 | 11.6825 | 49.7461 | 89.9996 | 0.828927 | 18.5265 | 74.9716 | 89.9996 | 0.884644 | 88521 |

### 5.2 The largest connected set a 3.4 deg neighbour rule can hold, on the shipped 0.6 mm cloud

Ticket 33/34 carry method: each cloud point takes the unit normal of the nearest point of the scan's own
PCD, sign preserved, no averaging. Ticket 28's replica is reproduced exactly as its `grow()` behaves: one
pass, seeds in ascending curvature, a claimed seed skipped, breadth-first, the reference normal is that of
the front point (not the seed), the 10 nearest neighbours of the front point tested in distance order, a
candidate joins iff `curvature < 1.0` and `angle <= 3.4 deg`, floor applied to finished regions only.
`k_nn` follows ticket 28's `max(10, min(50, npts/300))` (10 for the small clouds, 50 for Pot A 01). Two
curvature sources are run per cell: `recomputed` = ticket 28's `|lambda_min| / trace(cov)`, and
`ply-column` = the curvature already stored in the pipeline PLY. `sym` columns are the transitive closure
of the same 3.4 deg rule over the same 10 neighbours.

| piece | cloud pts | normals | curvature | k_nn | theta | kappa | nb | greedy regions | greedy largest | greedy top 6 | sym components | sym largest | largest share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Juglet 9 | 787 | pca | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 541 | 17 | 17;13;12;8;7;7 | 543 | 17 | 0.021601 |
| Juglet 9 | 787 | pca | ply-column | 11 | 3.4 | 1.0 | 10 | 543 | 17 | 17;13;11;8;7;7 | 543 | 17 | 0.021601 |
| Juglet 9 | 787 | carry | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 574 | 33 | 33;14;11;7;7;7 | 581 | 22 | 0.0279543 |
| Juglet 9 | 787 | carry | ply-column | 11 | 3.4 | 1.0 | 10 | 577 | 33 | 33;14;11;7;7;7 | 581 | 22 | 0.0279543 |
| Juglet 2 | 1031 | pca | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 660 | 36 | 36;15;12;12;11;9 | 661 | 36 | 0.0349176 |
| Juglet 2 | 1031 | pca | ply-column | 11 | 3.4 | 1.0 | 10 | 663 | 36 | 36;15;12;12;11;9 | 661 | 36 | 0.0349176 |
| Juglet 2 | 1031 | carry | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 709 | 39 | 39;31;16;14;10;9 | 710 | 39 | 0.0378274 |
| Juglet 2 | 1031 | carry | ply-column | 11 | 3.4 | 1.0 | 10 | 711 | 39 | 39;31;16;14;10;10 | 710 | 39 | 0.0378274 |
| Juglet 3 | 1467 | pca | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 828 | 268 | 268;17;10;10;9;8 | 828 | 169 | 0.115201 |
| Juglet 3 | 1467 | pca | ply-column | 11 | 3.4 | 1.0 | 10 | 829 | 169 | 169;99;17;10;10;9 | 828 | 169 | 0.115201 |
| Juglet 3 | 1467 | carry | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 878 | 316 | 316;17;15;8;7;7 | 885 | 306 | 0.208589 |
| Juglet 3 | 1467 | carry | ply-column | 11 | 3.4 | 1.0 | 10 | 880 | 316 | 316;17;15;8;7;7 | 885 | 306 | 0.208589 |
| Juglet 5 | 3021 | pca | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 1467 | 679 | 679;42;27;13;12;11 | 1474 | 678 | 0.224429 |
| Juglet 5 | 3021 | pca | ply-column | 11 | 3.4 | 1.0 | 10 | 1472 | 679 | 679;42;27;13;12;11 | 1474 | 678 | 0.224429 |
| Juglet 5 | 3021 | carry | recomputed(k=10) | 11 | 3.4 | 1.0 | 10 | 1562 | 652 | 652;65;36;34;19;18 | 1559 | 652 | 0.215823 |
| Juglet 5 | 3021 | carry | ply-column | 11 | 3.4 | 1.0 | 10 | 1564 | 652 | 652;65;36;34;19;18 | 1559 | 652 | 0.215823 |
| Juglet 7 | 4254 | pca | recomputed(k=14) | 15 | 3.4 | 1.0 | 10 | 1949 | 326 | 326;263;77;68;65;44 | 1961 | 328 | 0.0771039 |
| Juglet 7 | 4254 | pca | ply-column | 15 | 3.4 | 1.0 | 10 | 1955 | 326 | 326;263;77;68;65;44 | 1961 | 328 | 0.0771039 |
| Juglet 7 | 4254 | carry | recomputed(k=14) | 15 | 3.4 | 1.0 | 10 | 2022 | 258 | 258;193;137;101;88;86 | 2037 | 259 | 0.0608839 |
| Juglet 7 | 4254 | carry | ply-column | 15 | 3.4 | 1.0 | 10 | 2021 | 359 | 359;214;137;88;86;81 | 2037 | 259 | 0.0608839 |
| Pot A 07 | 8598 | pca | recomputed(k=28) | 29 | 3.4 | 1.0 | 10 | 1276 | 3093 | 3093;2850;203;170;134;120 | 1275 | 3097 | 0.3602 |
| Pot A 07 | 8598 | pca | ply-column | 29 | 3.4 | 1.0 | 10 | 1277 | 3093 | 3093;2850;203;170;134;120 | 1275 | 3097 | 0.3602 |
| Pot A 07 | 8598 | carry | recomputed(k=28) | 29 | 3.4 | 1.0 | 10 | 1032 | 3185 | 3185;2961;312;244;143;125 | 1036 | 3185 | 0.370435 |
| Pot A 07 | 8598 | carry | ply-column | 29 | 3.4 | 1.0 | 10 | 1033 | 3185 | 3185;2961;312;244;143;125 | 1036 | 3185 | 0.370435 |
| Juglet 1 | 14546 | pca | recomputed(k=48) | 49 | 3.4 | 1.0 | 10 | 4036 | 3489 | 3489;626;411;349;274;164 | 4041 | 3486 | 0.239654 |
| Juglet 1 | 14546 | pca | ply-column | 49 | 3.4 | 1.0 | 10 | 4036 | 3489 | 3489;626;411;349;274;164 | 4041 | 3486 | 0.239654 |
| Juglet 1 | 14546 | carry | recomputed(k=48) | 49 | 3.4 | 1.0 | 10 | 4865 | 3340 | 3340;354;177;158;146;136 | 4863 | 3304 | 0.227141 |
| Juglet 1 | 14546 | carry | ply-column | 49 | 3.4 | 1.0 | 10 | 4859 | 3343 | 3343;354;177;158;146;136 | 4863 | 3304 | 0.227141 |
| Pot A 01 | 85136 | pca | recomputed(k=50) | 51 | 3.4 | 1.0 | 10 | 6883 | 32775 | 32775;27551;3803;3375;815;730 | 6891 | 32776 | 0.384984 |
| Pot A 01 | 85136 | pca | ply-column | 51 | 3.4 | 1.0 | 10 | 6877 | 32775 | 32775;27551;3803;3375;815;730 | 6891 | 32776 | 0.384984 |
| Pot A 01 | 85136 | carry | recomputed(k=50) | 51 | 3.4 | 1.0 | 10 | 6831 | 32206 | 32206;28179;3743;3401;891;757 | 6850 | 32205 | 0.378277 |
| Pot A 01 | 85136 | carry | ply-column | 51 | 3.4 | 1.0 | 10 | 6843 | 32206 | 32206;28179;3743;3401;891;757 | 6850 | 32205 | 0.378277 |

---

## 6. Thickness and sheets (ticket 20's 800-ray method, unchanged)

Rays start at sampled cloud points offset 1e-3 mm along their normal and travel inward (−n); the wall
thickness is the first positive hit beyond 0.15 mm; `step = max(1, N//800)`.

| piece | cloud pts | rays | rays with a hit | median mm | p10 mm | p90 mm | frac 1-3 mm | hits/ray median | hits/ray max | rays >=2 sheets | rays >2 sheets | frac >2 | max merged | rays >=3 merged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Juglet 9 | 787 | 787 | 785 | 2.59484 | 2.06616 | 8.18262 | 0.613811 | 2 | 8 | 783 | 32 | 0.0406607 | 8 | 30 |
| Juglet 2 | 1031 | 1031 | 1028 | 2.69305 | 2.13945 | 6.75069 | 0.598249 | 2 | 10 | 1027 | 44 | 0.042677 | 10 | 42 |
| Juglet 3 | 1467 | 1467 | 1467 | 2.4516 | 1.85722 | 7.13893 | 0.67054 | 2 | 9 | 1460 | 59 | 0.0402181 | 8 | 50 |
| Juglet 5 | 3021 | 1007 | 1006 | 2.8998 | 2.31574 | 6.51743 | 0.541294 | 2 | 9 | 1005 | 44 | 0.0436941 | 6 | 40 |
| Juglet 7 | 4254 | 851 | 851 | 3.26316 | 2.32523 | 5.78525 | 0.338824 | 2 | 8 | 847 | 42 | 0.0493537 | 8 | 39 |
| Pot A 07 | 8598 | 860 | 860 | 4.05609 | 3.50109 | 11.9737 | 0.00930233 | 2 | 2 | 860 | 0 | 0 | 2 | 0 |
| Juglet 1 | 14546 | 809 | 808 | 2.35376 | 1.66574 | 18.0882 | 0.584718 | 2 | 10 | 606 | 329 | 0.406675 | 10 | 323 |
| Pot A 01 | 85136 | 804 | 804 | 8.2857 | 5.40824 | 21.0378 | 0 | 2 | 6 | 804 | 80 | 0.0995025 | 6 | 80 |

`hits` are raw triangle hits, so a ray through a quad's diagonal counts twice; the `merged` columns merge
hits within 1e-4 mm, which is what "sheets" means. `frac 1-3 mm` is the fraction of rays with a thickness
in [1, 3] mm.

---

## 7. Instrument checks against numbers already on record

`tables/instrument_checks.tsv`: **64 rows, 61 identical, 3 differ.** Every ticket-20 number listed below
reproduces to the digit against `20261027-0148_f3896e4_p20-arm/out/C_mesh.tsv`:

- **Juglet 9** — v 2094, f 4184, area 373.757, rays 787, thickness median 2.59484, p10 2.06616,
  **p90 8.18262**, frac 1–3 mm 0.613811, **max sheets 8**, rays with ≥2 sheets 783.
- **Juglet 2** — v 2565, f 5126, area 491.067, rays 1031, median 2.69305, p10 2.13945, p90 6.75069,
  frac 0.598249, max sheets 10, ≥2 sheets 1027.
- Juglet 3, 5, 7 and Pot_A_07 likewise (vertices, faces, area, rays, median, p10, p90, frac, max sheets,
  ≥2 sheets — all identical).

The two numbers this ticket names are therefore reproduced exactly: **piece 9 p90 = 8.18262 mm, max
sheet count 8**.

The three differences, with the reason each one is not an instrument error:

| check | recorded | measured | why |
| --- | --- | --- | --- |
| ticket 20 `v_raw` for Pot_A_07 | 63522 | 10593 | ticket 20's reader counted the mesh's `vt` rows as vertices. The OBJ has 10593 `v` lines, 21174 faces, and `grep "^v " \| sort -u` gives 10593 distinct vertex lines. |
| ticket 28 greedy largest, **piece 3** | 169 | 268 | measured with curvature **recomputed** at k=11. With the curvature **column of the pipeline PLY** the same cell gives **169** — the recorded number. |
| ticket 28 greedy largest, **piece 9** | 16 | 17 | off by one point, both curvature sources, both normal sets. Not explained. |

Ticket 28's replica is otherwise reproduced to the number, on the `ply-column` curvature:

| piece | ticket 28 arm B (theta 3.4, kappa 1.0, nb 10, floor 50) | this instrument, pca normals + ply-column curvature |
| --- | --- | --- |
| Juglet 2 | 36 | **36** (top 6: 36;15;12;12;11;9) |
| Juglet 3 | [169, 99] | **169;99**;17;10;10;9 |
| Juglet 5 | [679] | **679**;42;27;13;12;11 |
| Juglet 7 | [326, 263, 77, 68, 65] | **326;263;77;68;65**;44 |
| Juglet 9 | 16 | 17 |

So ticket 28's 36 for piece 2 stands, and its 16 for piece 9 is 17 here.
---

## 8. `index.tsv` rows appended

Three rows, one per job, appended to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` with
`printf '%s\\t%s\\t%s\\t%s\\t\\t\\n'`, i.e. **six tab-separated fields with verdict and human_note
left empty**. Verified with `cat -A` (each row ends `^I^I$` — two empty trailing fields) and
`awk -F'\t' '{print NF}'` → `6` on all three. The file had 306 rows when I started and 311 now.

```
20261028-0019_b8f7cc7_t35-mesh	33880769	b8f7cc733def196f1674095274e828456f366779	t35-mesh		
20261028-0022_f772c83_t35-mesh	33880898	f772c835ec2274092a42f627856a5f34ff08d7ba	t35-mesh		
20261028-0024_de55998_t35-mesh	33880958	de55998077a24324ef9a5cce01408ea193eef269	t35-mesh		
```

---

## 9. Git

Branch `35-what-are-sherds-2-and-9`, worktree `C:/PR/worktrees/sfs/35`. Commits on this ticket:

```
847db11 Ticket 35-what-are-sherds-2-and-9: job 3 tables and 32 figures
de55998 Ticket 35-what-are-sherds-2-and-9: table key map matched to the accumulator
f772c83 Ticket 35-what-are-sherds-2-and-9: merge edge-duplicate ray hits; slab selftest off the quad diagonal
b8f7cc7 Ticket 35-what-are-sherds-2-and-9: numpy-only mesh measurement instrument
```

`git diff --stat main...HEAD` (before the report commit): **48 files changed, 1367 insertions(+),
2 deletions(-)** — 32 PNG, 11 TSV, `instruments/measure35.py`, `instruments/submit35.sbatch`,
`run35.json`, `.gitignore` (2 lines: `__pycache__/`, `*.pyc`) and the ticket's own claim line.
Every path outside `.scratch/juglet-breaklines/stage35/` — one file, the claim ticket_start.sh made:

```
.scratch/juglet-breaklines/issues/35-what-are-sherds-2-and-9.md
```

No tracked source change of any kind, no pipeline C++ change, no build. The branch is pushed; nothing was
merged, no ticket `Status:` line was touched, nothing was written to `intent/`, `docs/` or `AGENTS.md`.
Three pushes used `--force-with-lease` on my own branch to strip a `__pycache__/*.pyc` that py_compile
had staged; the pre-existing `main` history was never rewritten.

---

## 10. What I could not do, and what is imperfect

1. **Three jobs instead of the two allowed** (section 1). Both extra jobs died in under ten seconds on my
   own instrument bugs; job 1 read no corpus file, job 2 wrote no usable table.
2. **`/opt/sfs-pristine` does not exist here.** Recorded, not created. The canonical checkout was used
   read-only instead.
3. **`scipy`, `trimesh` and `sklearn` are not installed** in the system python3
   (`ModuleNotFoundError: No module named 'scipy'` / `'trimesh'`). Nothing was installed; the instrument
   carries its own kNN, ray casting, topology and PNG writer (numpy only).
4. **The figure caption clipping** described in section 3. Not fixed: a fix costs another job, and the
   numbers it hides are in `tables/figures.tsv`.
5. **Ticket 28's 16 for piece 9 is 17 here** (both curvature sources, both normal sets). Not explained.
   Ticket 28's other four pieces reproduce to the number.
6. **The run's `out/` directory is pruned after 90 days**, so the tables and figures are copied into this
   stage directory and committed; `out/measure.log` is gitignored (`*.log`, rule at `.gitignore:54`) and
   a copy sits at `tables/measure.log`.
7. **No interaction with the pipeline itself.** The 0.6 mm cloud was read from a surviving t30 run rather
   than rebuilt, so no apptainer image and no C++ build was involved; the job could not fail on a build,
   but it also does not prove the t30 PLYs are byte-identical to a fresh pipeline run (they are ticket 20's
   own input, and its ray counts reproduce exactly).

---

## 11. Deletion record

Written **before** the deletions it describes, with counts and bytes.

| what | files | bytes | per-extension breakdown | when |
| --- | --- | --- | --- | --- |
| `stage35/instruments/__pycache__/` (local, from `python -m py_compile`) | 1 | 93278 | `.pyc` 1 / 93278 B | deleted after this line was written |
| `stage35/tables/_md_cache.json` (my scratch cache while assembling this report) | 1 | 17955 | `.json` 1 / 17955 B | deleted after this line was written |

Deleted earlier, **without** a prior record — disclosed rather than back-dated:

| what | contents | why nothing was lost |
| --- | --- | --- |
| `/tmp/t35-stage-XXXX` on spartan (submission staging) | 4 files: measure35.py 51361 B, submit35.sbatch 1333 B, run35.json 2162 B, .gitignore 19 B | byte-for-byte `git archive de55998 -- .scratch/juglet-breaklines/stage35`; reproducible from the pushed commit |
| `/tmp/t35-build-XXXX` on spartan (the sbatch's own build root) | the same 4 files | same |

No corpus file, no run directory, no existing worktree file and no other ticket's data was deleted. Nothing
under `original_samples`, `sfs_preprocessing` or any `runs/*` directory was removed or rewritten.

---

## 12. What was kept

49 files, 4,885,439 bytes in `.scratch/juglet-breaklines/stage35/` (counted after the two deletions in
section 11):

| extension | files | bytes |
| --- | --- | --- |
| `.png` | 32 | 4,755,951 |
| `.py` | 1 | 51,361 |
| `.tsv` | 11 | 24,931 |
| `.md` | 1 | 33,912 |
| `.json` | 1 | 2,162 |
| `.sbatch` | 1 | 1,333 |
| `.log` (gitignored) | 1 | 15,770 |
| none (`.gitignore`) | 1 | 19 |

- `instruments/measure35.py` — the whole instrument, 1069 lines, numpy only.
- `instruments/submit35.sbatch` — the exact batch script job 3 ran.
- `run35.json` — parameters, input paths and md5s, thresholds (theta 3.4, kappa 1.0, nb 10, floor 50,
  800 rays, weld 1e-4 mm, render width 1400 px).
- `tables/*.tsv` — topology, boundary loops, turning (mesh), turning (cloud growth), thickness, carry,
  figures manifest, md5 check, instrument checks, timing, failures.
- `figures/*.png` — 32 renders.
- `REPORT.md` — this file.

For the run's own log: `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0024_de55998_t35-mesh/out/measure.log` (15,770 B) and
`/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0024_de55998_t35-mesh/logs/slurm-33880958.out`.
