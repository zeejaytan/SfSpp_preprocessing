# Ticket 300 - stage the reassembled Pot C (ours vs the authors'), and say whether C 01's gap cost a seat

Status: done (accepted: both arms rebuild the same four pieces and the transform convention is proved by a measured join test with a negative control; C 01's joins close to 0.035-0.100 mm at 0.44-0.63 deg / 2.55-4.35 mm, inside the assembler's own bar and no worse than its neighbours; the scan gap is real but sits >=36 mm inside the line that seats the piece, so it did not cost a seat. NEEDS-EYE OUTSTANDING: the conservator has not yet opened pota300_potC_arms / pota300_potC_c01, and the gate caveats stand as recorded in section 5 -- check_stage_pair.py exits 1 in its own Windows temp teardown, the two loader gates exit 1 on manifests that live in preview/retired/ and are absent from HEAD)
Working in: chat on Thinkbook16 (2026-10-26)
Branch: 300-pot-c-eye, in /c/PR/worktrees/sfs/300
Answers: E1
Created: 2026-10-26 by the coordinating session, on the conservator's instruction
("Pot C seated with C01 gap? can you stage the reassembled pot on visual-qa? ours vs authors")

## Why

Pot C came out 4/4 sherds and 5/5 joins in BOTH arms of ticket 298 - the pot looked perfect. But
Pot C's four scored pieces include **Pot C 01**, the sherd whose interior surface carries a scan gap
(project AGENTS.md "Corpus caveats", ticket 285): the pipeline reads that gap as a second broken edge
the sherd does not have. The assembler reads `Breakline_0`, which is the boundary of the INTERIOR
surface - exactly the defective one. A pot-level 4/4 does not certify that piece, and the conservator
wants to see the reassembly with his own eye, ours beside the authors'.

## Facts already established (do not re-derive)

- Assembler `/opt/sfs-pristine` (upstream `9195c016` + INFRA shim), binary md5
  `0fd8d707ceb3f9cffd08d8951c43ccda`, beam k=5 b=3; identical in both arms of ticket 298.
- Preprocessing commit `d1f1a4c`; runs (Spartan, `/data/gpfs/projects/punim2657/SfSpp/runs/`):
  `20261026-0126_d1f1a4c_p298-Pot_C-oursd` and `...-Pot_C-authb`. Both read
  "Sherd accuracy : 4 / 4 (100 %)" then "Sherd accuracy : 5 / 5 (100 %)" (the second line is JOINTS,
  not sherds - the assembler prints the same label twice).
- Each `out/Result/` holds `1. Acc.txt`, `T_0to_0.txt ... T_3to_3.txt` (one transform per staged
  piece, i.e. 4 pieces) and four `*_Edgeline_*.xyz`. 67 KB per arm - the geometry is NOT there.
- Corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/` holds
  `Mesh/Pot_C_Piece_0N_Mesh_DS.obj` (only the DS mesh exists for Pot C), `Axes/Pot_C_Piece_0N_Axis.xyz`,
  `Breaklines/`, `Surfaces/` and `Ground Truth/Pot_C_Piece_<n>_T.txt` (NO zero padding in GT names).
  The Pot C bundle holds six pieces; the assembly used four - establish WHICH four from the block
  arrays in the shim and/or `out/links.tsv` / `out/selector.txt`, before transforming anything.

## What to do

**Phase 1 - rebuild both reassemblies.** For each arm, apply each piece's `T_ito_i.txt` to that
piece's `Mesh_DS.obj` and combine the four pieces into ONE OBJ per arm. State the transform
convention you assumed and prove it: a piece seated correctly must land with its breakline touching
its neighbours' (measure, do not eyeball - e.g. nearest-neighbour distance between adjacent pieces'
surfaces on the joins the GT graph says exist). If the convention is inverted and the pot flies
apart, say so and fix it before staging.

**Phase 2 - did C 01 cost a seat?** Identify C 01's index in each arm, and report for it: rotation
error (deg) and translation error (mm) of its seated pose against `Ground Truth/Pot_C_Piece_1_T.txt`,
how that compares with the other three pieces, and whether its seated position differs between the
two arms. Then answer the conservator's question directly: on the geometry, is the gap visible as a
seam or a doubled edge, and does it move that piece relative to its neighbours?

**Phase 3 - stage it in visual-qa.** Per `C:/PR/docs/agents/visual-qa.md`: geometry stays in the
method's own `artifacts/` (`C:/PR/SfSpp_preprocessing/artifacts/pota300/`), only small previews are
staged; write a desc in `C:/PR/visual-qa/viewer/pairs/`, run `visual-qa/viewer/stage_pair.py`
(authoring a desc by hand instead of fixing what it refuses is not allowed), check the viewer is
serving and run the `check_*.py` gates in `visual-qa/`. Read `C:/PR/visual-qa/AGENTS.md` first.
Two pairs:
- `pota300_potC_arms`: left = authors' bundle reassembly, right = ours, locked overlay, camera set
  so the four sherds' seams and C 01's own surface are both legible at this scale.
- `pota300_potC_c01`: `single:` - C 01 alone from our arm, close enough to see the scan gap in its
  interior surface.
Report the desc path, the pair ids, and the gate output.

**Phase 4 - the record.** Small previews stay staged; the full OBJs stay in `artifacts/pota300/`
(gitignored). If any geometry step runs longer than a minute on the laptop, it belongs in a Spartan
job in a run directory (run.json + submit.sbatch + logs/ + out/ + an index row with verdict and
human_note EMPTY), not on the laptop.

## Constraints

- **No algorithm, threshold or assembler change;** no re-run of the campaign. This is staging and
  measurement of geometry that already exists.
- Heavy work on Spartan compute nodes; the laptop may fetch the four DS meshes (2-4 MB each) and run
  the transforms only if it stays trivial - otherwise job it.
- Never `build.sh --target nurbs` (it compiles the pre-247 duplicate).
- Do not touch `C:/PR/worktrees/sfs/299` if it exists; tickets that touch the same repo run one after
  another and this one reports and stops.
- Write results into this ticket; commit on your branch only; leave Status at in-progress.

## Acceptance

1. Both reassembled OBJs exist under `artifacts/pota300/`, with the four pieces named per arm and
   the transform convention proved by a measured join distance.
2. C 01's seated pose compared with GT (rotation deg + translation mm) and against its three
   neighbours, in both arms.
3. A direct answer to "did the gap cost a seat", in one sentence, with the measurement behind it.
4. Two pairs staged in visual-qa, desc path and pair ids reported, gates run and their output quoted.
5. What the conservator must look for, written as a line he can act on - not a description of the
   script.

## Result (2026-10-26)

All four phases done on the laptop; no step ran longer than about a minute, so no Spartan job and no run
directory were created. Numbers come from `.scratch/pota-repro/300/*.py` in this worktree; machine-readable
records are in `artifacts/pota300/geom/{measure,gap,gap_detail,pair_build,obj_export}.json`.

### 1. The four pieces, and the transform convention (measured, not assumed)

Both arms stage and seat **Pot C 01, 02, 03, 04** — `out/links.tsv` maps `Mesh/Pot_C_Piece_01..04_Mesh.obj`
to the corpus `Pot_C_Piece_0N_Mesh_DS.obj`, and `out/selector.txt` reads pot `Pot_C`, `SHARD_NUMBER 4`,
ifdef line 1584. C 05 and C 06 are in the bundle but not in the assembly; C 07 has a mesh only.

Convention: **`p_world = R p_local + t`** — the top three rows of `T_ito_i.txt` read as (R|t), applied to the
raw corpus mesh. Decided by the only thing that can decide it, using the authors' Ground Truth transforms as
the known-good reference and measuring the minimum vertex-to-vertex distance across each join:

| join | in GT graph | GT transforms | inverted reading R^T(p - t) |
|---|---|---|---|
| C01-C02 | yes | 0.0755 mm | 292.47 mm |
| C01-C03 | yes | 0.0454 mm | 523.95 mm |
| C01-C04 | yes | 0.1018 mm | 240.46 mm |
| C02-C03 | yes | 0.0574 mm | 709.02 mm |
| C02-C04 | yes | 0.0678 mm | 198.97 mm |
| C03-C04 | **no** | 12.105 mm | 551.87 mm |

The five joins the GT graph has close under 0.11 mm; the one pair it says does **not** join stays 12.1 mm apart,
so the test carries a negative control and passes it. The inverted reading throws every piece hundreds of mm
away. **The convention is not inverted; nothing was fixed.** Applied unchanged to both arms' stored transforms:

- authb: 0.0664 / 0.0353 / 0.0518 / 0.0563 / 0.0196 mm (non-join 10.5825)
- oursd: 0.0698 / 0.0694 / 0.0998 / 0.0347 / 0.0958 mm (non-join 10.6722)

Reassembled OBJs: `artifacts/pota300/geom/potC_oursd_assembled.obj` and `potC_authb_assembled.obj`
(4,688 KB each, four `g Pot_C_Piece_0N` groups, assembler world frame); re-read from disk they give the same
seam distances to 4 dp, so the export is faithful.

### 2. C 01's seated pose vs Ground Truth, and vs its neighbours

Two numbers are needed and they are not the same number, so both are given.

**(a) The assembler's own metric** — frame-free relative transform `E = T_rel · inv(GT_rel)`, i.e. what
`CountResult` compares, reported as quantities rather than a pass/fail at its tolerance of 0.35 rad
(20.05 deg) / 50 mm:

| join | oursd rot deg / trans mm | authb rot deg / trans mm |
|---|---|---|
| C01-C02 | 0.591 / 2.948 | 0.677 / 2.952 |
| C01-C03 | 0.634 / 2.548 | 0.862 / 3.886 |
| C01-C04 | 0.438 / 4.351 | 0.333 / 3.004 |
| C02-C03 | 0.467 / 2.853 | 0.778 / 4.494 |
| C02-C04 | 0.490 / 4.319 | 0.395 / 3.107 |

Every join in both arms is inside the assembler's tolerance by more than an order of magnitude. C 01's worst
join (C01-C04: 4.351 mm oursd / 3.004 mm authb) is the same size as its neighbours' worst (C02-C04:
4.319 / 3.107), so C 01 is **not** the outlier of the hand in either arm.

**(b) Whole-hand pose after ONE global rigid alignment per arm onto the GT assembly** (removes the frame
choice only; cannot change inter-piece geometry):

| piece | authb centroid shift / RMS mm | oursd centroid shift / RMS mm |
|---|---|---|
| C 01 | 1.057 / 1.131 | 0.941 / 1.005 |
| C 02 | 0.614 / 0.634 | 0.585 / 0.598 |
| C 03 | 0.765 / 0.841 | 0.759 / 0.795 |
| C 04 | 0.904 / 0.913 | 0.806 / 0.825 |
| hand RMS | 0.8457 | 0.7760 |

**Trap to keep:** the per-piece "frame-free" rotation of ~152-153.7 deg is the difference between the
assembler's axis frame and the GT vessel frame. It is not seating error and must never be quoted as one. The
sub-millimetre residuals above are the honest pose error.

**(c) Ours against the authors'**, after one global alignment between the two arms (1.366 deg / 0.341 mm):
raw centroid separation C 01 0.947, C 02 0.983, C 03 0.416, C 04 0.940 mm; expressed relative to C 01 —
C 02 0.139 deg / 0.723 mm, C 03 0.318 / 1.874, C 04 0.262 / 1.520. The two builds agree to 0.10 mm median
surface coincidence on the staged previews (p90 0.18).

### 3. The gap: where it is, measured for the first time (ticket 285's open question)

C 01 is the only one of the four that is not watertight: C 02, C 03, C 04 have **zero** boundary edges, C 01
has four closed rims.

| rim | vertices | perimeter mm | radius to axis mm | distance to our S0 / S1 |
|---|---|---|---|---|
| 1 | 274 | 116.82 | 63.8 - 74.3 (the wall's thickness) | 11.7 / 11.4 mm |
| 2 | 247 | 101.97 | 55.0 - 59.8 | **0.29** (p90 2.48) / 9.3 mm |
| 3 | 97 | 43.81 | ~95 | 47.6 / 41.0 mm |
| 4 | 18 | 5.15 | ~55 | - |

Rim 2 lies on our **Surface_0, the interior** sheet (0.29 mm), so it is a hole in the interior face; rim 1
spans the wall's thickness 11.35 mm away in centroid, i.e. the same missing region seen across the wall. That
is the scan gap, and it is on the flat of the sherd, not at its edge: **both interior lines stay clear of every
rim** — our `Bl0` (207 dots) is 36.1 / 40.3 / 71.3 / 36.4 mm from rims 1-4, the authors' `Breakline_0`
(211 dots) 36.2 / 40.2 / 71.5 / 36.1 mm. The `.pcd` header records our line's lump structure as five lumps
(1-31, 32-98, 99-109, 110-179, 180-212): the gap owns some of those dots, not the exported line's path.

### 4. Did the gap cost a seat

**No.** The interior line the assembler seats C 01 by runs the real break edge — 36.1 mm from the nearest gap
rim, where the authors' own line is 36.2 mm from it — and C 01's joins close to 0.035-0.100 mm with relative
pose error 0.44-0.63 deg / 2.55-4.35 mm, inside the assembler's 20.05 deg / 50 mm tolerance and no worse than
its neighbours'. The gap is real and it does hand the boundary detector four rims the sherd does not have, so a
Bl0-derived score on this piece still measures an input defect; what this ticket adds is that on this piece
the defect never reached the seat.

Weight: one hand, four pieces, one pot, one seating each. It settles C 01 for these two arms; it does not
speak for Pot C's other three released pieces, for Pot J 01, or for other pots, and the pot-level 4/4 stays a
pot-level score.

### 5. Staged in visual-qa

- **`pota300_potC_arms`** — left "Authors' lines (authb arm)", right "Our lines (oursd arm)", four pieces in
  the same colours on both sides (C 01 tan, C 02 teal, C 03 olive, C 04 purple), both in the GT vessel frame,
  z up.
- **`pota300_potC_c01`** — `single:` C 01 seated, light grey; magenta rings = the two large open rims (the
  interior-face hole and its far side), yellow rings = the two small ones, red = our `Bl0`, blue = the
  authors' `Breakline_0`.
- Descs: `C:/PR/visual-qa/viewer/pairs/pota300_potC_arms.json` and `..._potC_c01.json` (untracked, like the
  `pota209_*` and `pristine_pota_whole` descs). Manifests: `visual-qa/preview/manifest_pota300_potC_arms.json`
  and `..._c01.json`. Geometry (gitignored, in the method's own artifacts):
  `SfSpp_preprocessing/artifacts/visual-qa/pota300_potC_arms/{left_authors,right_ours}.ply` (127,936 faces
  each) and `.../pota300_potC_c01/c01_seated.ply` (48,410 faces) — no decimation, median edges 1.226 and
  1.043 mm.
- `stage_pair.py` output: `surface coincidence: median 0.10 mm, p90 0.18 mm` — under the 5.0 mm gate, so
  `frame_ok: true` and the overlay is live; the single look stages without overlay, as designed.
- Gates (`C:/PR/visual-qa/viewer/`): `check_annotations.py` **exit 0** — "all-hits OK: entry, exit, entry,
  exit in order / mouth-ray OK: interior floor hit with the floor out of nearest-vertex range / annotations OK:
  nearest-side hit, camera round-trip, log round-trip". `check_stage_pair.py` prints all 21 of its checks as
  passing (matched pair 0.00 mm, shifted 45.00 mm warns not refuses, unit scaling, scale-less refusal, empty
  mesh refusal, colour and guessed flags through decimation, drawing crop/refusals) and then exits 1 inside
  Windows temp-dir teardown — `PermissionError: [WinError 32] ... drawing.png` — a gate-side cleanup bug on
  its own fixtures; it never opens a pair desc. `check_loader.py` and `check_mesh_loader.py` exit 1 reading
  `preview/manifest.json` / `preview/manifest_a02.json`, which are in `preview/retired/` on this checkout:
  pre-existing, TORA/juglet bundles, nothing to do with Pot C.
- Page-side check (read-only): `view_juglet.manifest_loader` loads both bundles (127,936 + 127,936 and 48,410
  faces, all finite) and `registry()` lists both titles, so the pairs appear in the dropdown.
- Viewer serving: `python viewer/view_juglet.py --port 8080` from `C:/PR/visual-qa`, HTTP 200 on
  `http://localhost:8080/` (pid 40640 listening on 0.0.0.0:8080); log `.viewer_pota300.log`.

### 6. What the conservator should look for

**Open `pota300_potC_arms` first and check the seams where C 01 meets C 02, C 03 and C 04: they close in
both builds. Then open `pota300_potC_c01` and note that the magenta rings — the open rims on C 01's interior
face — sit on the flat of the sherd, at least 36 mm inside the red line that seats it: what you see at the
seam is the real break edge, not the gap.**

## Needs-eye

Visual-qa pair `pota300_potC_arms` (ours against the authors', same four pieces) and
`pota300_potC_c01` (C 01 alone): does the reassembly look right, and is the scan gap visible as a
seam where it should not be?
