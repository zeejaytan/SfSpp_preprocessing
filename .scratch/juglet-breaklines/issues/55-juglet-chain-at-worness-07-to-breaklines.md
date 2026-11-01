# 55 — Juglet chain at WORNESS=0.7 down to breaklines, every edgeline rendered for the eye

**What to build:** all nine Juglet pieces go through the SHIPPED preprocessing chain at the
conservator's recommended dial `SFS_WORNESS=0.7` — mesh stage (two surfaces per piece) then the
edge-line stage — and every piece's edgelines are rendered as pictures ON its mesh for the
conservator to read with his own eyes. This is e2e step 4 of 5
(`../structure-from-sherds-pp/docs/e2e-obj-to-reassembly.md`): **the run stops before
assembly**. Nothing is scored and no seating claim is made. The pictures are the deliverable
(the conservator asked for them by name, 2026-11-01). The shipped stage they exercise is
the FIXED one: Breakline_0 comes from the **interior** wall (ticket 04, resolved 2026-09-28:
per-sherd surface_classify vote + exchange wiring, 15/15 with patch rims per ticket 14),
the specified noise filter runs (ticket 05, 2026-09-30) and resampling is equidistant
(ticket 06, 2026-09-30). Still open from the spec is only edge-line **ordering / vote
direction** (ticket 03, characterized-but-unfixed) — the pictures are the honest per-sherd
read of this fixed stage at the recommended dial.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** None (54 merged as 0724e5d; the dial exists on main and 0.7 is the
recommended value, ledger row 12)

**Status:** resolved 2026-11-01 — 9/9 Juglet pieces through the shipped chain at WORNESS=0.7 to breaklines, pictures delivered for the eye; lead verification below
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 55-juglet-chain-at-worness-07-to-breaklines, in /c/PR/worktrees/sfs/55

**Worker:** dsh-t55-worker (subagent of the lead session; never the lead itself)

**Needs-eye:** `SfSpp_preprocessing/artifacts/20261101-2004_05be12c_t55-worness07-breaklines/out/png/Juglet_Piece_{1..9}.png` — one picture
per sherd, on-mesh edgeline overlay; image-only bundle, deliberately NOT staged into
visual-qa manifests

## Spec — one job, no source change

Instruments only, pushed under `.scratch/juglet-breaklines/stage55/` (copy the stage54
`.gitattributes` CRLF guard). Precedents to copy, not reinvent:

- `.scratch/juglet-breaklines/stage54/instruments/run_cell54.sh` — staging + corpus-manifest
  gate (pass 1: md5 AND kept_points vs `MANIFEST_JUGLET_CC.tsv`) + mesh-stage invocation +
  log-line extraction. The env probe and the D/X/W arms are NOT needed (one arm only).
- `.scratch/juglet-breaklines/stage54/instruments/submit54.sbatch.tmpl` — job scaffolding:
  corpus md5 before/after, build from `git archive` of the PUSHED commit, geom_record /
  geom_delete with a named kept-list, index row appended with verdict/human_note empty,
  trap list (CRLF, set -u, no xargs -d, grep -a, PLY header varies).
- `.scratch/pota-repro/298/jobs/p298_prep.sbatch` — the edge-stage invocation and the
  out/geom deliverable bundle.
- `.scratch/pota-repro/289/a289.py` — the on-mesh overlay renderer (matplotlib Agg 3D,
  read_pcd/read_xyz, chunked nn).

Spartan facts: `CANON=/data/gpfs/projects/punim2657/sfs_preprocessing`, `DS=$CANON/Dataset`,
`CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`,
`SIF=$CANON/pcl_191_nurbs.sif`,
`APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`,
`PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`,
`RUNS=/data/gpfs/projects/punim2657/SfSpp/runs`, `IDX=$RUNS/index.tsv`.
Inputs: mesh `$DS/Mesh/Juglet/Juglet_Piece_{1..9}_Mesh.obj`, cloud
`$DS/Point/Juglet/Juglet_Piece_{1..9}_Point.pcd`, axis
`$DS/Axes/Juglet/Juglet_Piece_{1..9}_Axis.xyz`. Run dir
`$RUNS/<YYYYMMDD-HHMM>_<git7>_t55-worness07-breaklines/`.

Per piece (the whole loop inside the job):

1. stage (STAGER pattern of stage54: `stage_synth_p40.sh` signature
   `ST POT PIECE AXIS CLOUD KIND`);
2. mesh stage, from the staged tree:
   `(cd $ST && $APT exec --bind /data:/data $SIF env POT_NAME=Juglet
   SFS_AXIS_FILE=$ST/Dataset/Axes/${P}_Axis.xyz SFS_STATUS_FILE=... SFS_WORNESS=0.7 $MESH)`;
   REQUIRED log lines per piece: `[PAPER-234] classify: face0` (ticket 277 gate) and
   `[WORNESS-54] piece= ... theta=` — a piece missing either is a FAILED cell, not a skip;
3. export surfaces `$ST/Temp/Data/Juglet/${P}_Surface_{0,1}.{ply,xyz}` (either ext) to
   `out/geom/${P}.S0/.S1`;
4. edge stage (p298 pattern): `rm -rf $ST/Dataset/Breaklines/Juglet` then
   `(cd $ST && $APT exec --bind /data:/data $SIF env POT_NAME=Juglet $EDGE)`, export
   `$ST/Dataset/Breaklines/Juglet/${P}_Breakline_{0,1}.pcd` to `out/geom/${P}.Bl0/.Bl1`;
5. count the stage, then delete it (counted record; the out/geom bundle IS kept — it is the
   input the future assembly ticket will consume).

Build BOTH binaries from the pushed commit: `make -j MeshPreprocessingHeadless
EdgeLineExtractionHeadless`; record both md5s. Corpus gate identical to t54 pass 1; corpus
md5 before/after must be empty-diff. No `SFS_*` other than the three named; the t54 unset
list carries over.

Renderer (new `render55.py`, TORA python, Agg backend): one PNG per piece at
`out/png/${P}.png` — mesh vertices as a light-grey 3D scatter, Breakline_0 dots in one
bright colour and Breakline_1 in another (legend must say Bl0 is the lane assembly
consumes), TWO panels (two azimuth/elevation choices so the traced rim is visible
edge-on in at least one), title carrying piece name, theta used, Bl0/Bl1 point counts;
equal-aspect axes labelled in mm (the meshes are in mm). A picture whose view hides the rim
fails this ticket even if every number is green.

## Acceptance

- [x] One run of record on the shared root, run.json facts in out/run-meta.txt (runid,
      jobid, commit, tag, rc), index row appended by the job with verdict/human_note empty,
      corpus md5 unchanged before/after, `sacct` State/ExitCode recorded in the ticket.
- [x] 9/9 pieces with classify line + WORNESS line + S0/S1 + Bl0/Bl1 exported; per-piece
      table (piece, capped theta, surf0/surf1 points, bl0/bl1 points, rc) in out/ and in the
      ticket write-back. A FAILED cell is reported as FAILED — never dropped.
- [x] 9/9 PNGs rendered per the spec above; fetched to
      `SfSpp_preprocessing/artifacts/<runid>/` on the laptop together with the per-piece
      table, run-meta and the slurm out/err; the Needs-eye line above resolves on disk.
- [x] No assembly, no scorer, no corpus write, no source change; stages deleted with the
      counted record; the branch carries instruments + ticket write-back only.
- [x] Worker reports facts only (numbers, paths, failures); the verdict is the lead's.

## Lead verification (2026-11-01)

- verified: worker table vs out/pieces55.tsv on the laptop -> identical 9 rows, all
  status ok, mesh_rc=0 edge_rc=0, classify+worness markers yes on 9/9.
- verified: branch 55-juglet-chain-at-worness-07-to-breaklines is based on the corrected
  caveat commit 6d89d75; the write-back carries no stale larger-surface claim.
- verified: binary identity -- MeshPreprocessingHeadless md5 736ff95c976486d17f7c00b3af402040
  equals the t54 binary of record; EdgeLineExtractionHeadless cbf747dc3172fe0bbd188822df14092a.
- verified: on-mesh geometry (lead-run out/nncheck55.py on Spartan: cKDTree lane-to-mesh-vertex
  NN distance, mm) -- 8/9 pieces, both lanes hug the mesh: median 0.15-0.30, p90 <= 0.36,
  max <= 1.02. **Exception J1 Bl0: 10 of 28 dots, one consecutive run, sit 3.3-5.2 mm off
  the mesh** (region x 26-34, y -16..-6, z -505..-502 -- ~13% of the sherd's 38 mm extent),
  visible in the picture as the lane leaving the sherd. The PNG plots the real Bl0
  coordinates, so this is pipeline data, not a render defect; B-spline projection bowing
  off a sparse region is the likely seat, unproven here.
- caveat: the mesh stage is not deterministic (30 unseeded ray-cast points,
  mesh_processing_headless.cpp:1526-1527; run-to-run spread up to 0.867 mm measured on
  Pot H 02), so the J1 departure may move between runs -- a single-run number is not a
  stable measurement of it.
- verified: 9/9 PNGs on disk at the Needs-eye path (1485x704, two panels); lane pixel
  presence per render55.tsv. The qualitative on-rim read stays with the conservator
  (vision bridge 503 for worker and lead alike).
- Verdict: run of record stands, deliverable accepted. Carry-forward finding: J1 Bl0's
  off-surface segment -- Bl0 is the lane the assembler reads, so the future assembly
  ticket inherits it.

## Results (worker write-back, 2026-11-01)

**Run of record:** '20261101-2004_05be12c_t55-worness07-breaklines', job **34165367**,
**sacct COMPLETED 0:0, elapsed 00:04:00** (host spartan-bm157), commit '05be12c'
(instruments 'c8da315' + gate fixes '05be12c'/'8700ee2'), branch pushed. First submit
34165338 FAILED in 3 s at the instruments md5 gate: the laptop render passed /data/...
as python argv and MSYS rewrote it into the bash-win32 install prefix, baking
'C:/Users/hermi/...' into --output/RUN=; fixed by rendering on Spartan + commit
'8700ee2' (MSYS2_ARG_CONV_EXCL render, C: gate, full 7-file instrument tar), resubmitted.
Both events are in sacct history; run.json carries prior_attempt_jobid.

- **Corpus gate 9/9 ok** -- cloud md5 AND kept_points match MANIFEST_JUGLET_CC.tsv
  per piece (840,666-841,413 pts); job log line 179: 'frozen inputs unchanged (empty
  corpus diff)'. No *_covering.pcd anywhere under the corpus Point trees.
- **Cells 9/9 ok, cells_rc=0** -- every piece has '[PAPER-234] classify: face0' and
  '[WORNESS-54] piece= ... theta='; mesh_rc=0, edge_rc=0; no FAILED cell.

| piece | capped theta deg | surf0 pts | surf1 pts | Bl0 dots | Bl1 dots |
|---|---|---|---|---|---|
| Juglet_Piece_1 | 6.43 | 13,850 | 15,173 | 28 | 64 |
| Juglet_Piece_2 | 12.87 | 1,390 | 1,296 | 32 | 31 |
| Juglet_Piece_3 | 11.93 | 2,063 | 2,189 | 38 | 41 |
| Juglet_Piece_4 | 17.13 | 2,033 | 2,255 | 32 | 35 |
| Juglet_Piece_5 | 13.54 | 4,066 | 5,302 | 47 | 51 |
| Juglet_Piece_6 | 16.82 | 3,870 | 3,944 | 46 | 45 |
| Juglet_Piece_7 | 10.50 | 5,703 | 7,282 | 54 | 58 |
| Juglet_Piece_8 | 15.46 | 2,770 | 2,933 | 41 | 41 |
| Juglet_Piece_9 | 14.21 | 1,051 | 1,219 | 23 | 24 |

(Full 12-col table: out/pieces55.tsv, fetched copy in artifacts.)

- **Deliverables:** 9/9 PNGs (out/png/Juglet_Piece_{1..9}.png, 1485x704, two panels)
  and the 36-file out/geom/ bundle ({P}.{S0,S1,Bl0,Bl1}, the assembly-consumable
  export) -- geom kept, every stage tree deleted with counts
  (GEOMETRY_DELETED.txt: before 0 / after 0 outside keeps, kept 36).
  Binaries from the pushed commit: MeshPreprocessingHeadless
  '736ff95c976486d17f7c00b3af402040', EdgeLineExtractionHeadless
  'cbf747dc3172fe0bbd188822df14092a' (out/binaries.md5).
- **Index row appended** with verdict/human_note EMPTY (lead's to write).
- **Artifacts on laptop** at SfSpp_preprocessing/artifacts/20261101-2004_05be12c_t55-worness07-breaklines/
  (fetch tar md5 'f425564e88bc24ff2c4b0c9ea8e5983e', verified after extraction):
  out/{pieces55.tsv,run-meta.txt,render55.tsv,corpus_gate.tsv,corpus_covering_sweep.txt,geometry_counts.tsv,GEOMETRY_DELETED.txt,binaries.md5,files.md5,cells55.log,render55.log,inputs.diff,versions.txt,png/Juglet_Piece_1..9.png}
  + logs/{slurm-34165367.out,slurm-34165367.err,build.log,fetch.log} + submit.sbatch.
- **Worker-side picture check (quantitative, not the eye):** every PNG contains both
  lanes -- red (Bl0) 468-791 px and blue (Bl1) 632-1,075 px, mesh 2.8-6.5% of frame.
  The qualitative on-rim read is the conservator's (modlens vision bridge was 503 both
  tries); pictures linked in Needs-eye resolve on disk.
- Acceptance items 1-4 are met by the facts above; the branch carries instruments +
  this write-back only, nothing merged to main, no assembly/scorer/corpus write/source
  change.

## Out of scope

- Any assembly run or seating claim (step 5; a later ticket).
- Any change to edgeline_extraction_headless.cpp / mesh_processing_headless.cpp — the
  spec.md rebuild is mostly DONE (interior surface 04, filter 05, resampling 06, all
  resolved 2026-09-28/30); only ordering / vote direction (ticket 03) remains open, and
  it is separate work. This ticket records the shipped stage's behaviour, it does not
  change it.
- The J8 spacing question, corpus changes, Pot A arms (t54 already proved the dial inert
  there).
