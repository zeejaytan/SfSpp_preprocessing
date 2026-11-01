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

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 55-juglet-chain-at-worness-07-to-breaklines, in /c/PR/worktrees/sfs/55

**Worker:** dsh-t55-worker (subagent of the lead session; never the lead itself)

**Needs-eye:** `SfSpp_preprocessing/artifacts/<runid>/Juglet_Piece_{1..9}.png` — one picture
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

- [ ] One run of record on the shared root, run.json facts in out/run-meta.txt (runid,
      jobid, commit, tag, rc), index row appended by the job with verdict/human_note empty,
      corpus md5 unchanged before/after, `sacct` State/ExitCode recorded in the ticket.
- [ ] 9/9 pieces with classify line + WORNESS line + S0/S1 + Bl0/Bl1 exported; per-piece
      table (piece, capped theta, surf0/surf1 points, bl0/bl1 points, rc) in out/ and in the
      ticket write-back. A FAILED cell is reported as FAILED — never dropped.
- [ ] 9/9 PNGs rendered per the spec above; fetched to
      `SfSpp_preprocessing/artifacts/<runid>/` on the laptop together with the per-piece
      table, run-meta and the slurm out/err; the Needs-eye line above resolves on disk.
- [ ] No assembly, no scorer, no corpus write, no source change; stages deleted with the
      counted record; the branch carries instruments + ticket write-back only.
- [ ] Worker reports facts only (numbers, paths, failures); the verdict is the lead's.

## Out of scope

- Any assembly run or seating claim (step 5; a later ticket).
- Any change to edgeline_extraction_headless.cpp / mesh_processing_headless.cpp — the
  spec.md rebuild is mostly DONE (interior surface 04, filter 05, resampling 06, all
  resolved 2026-09-28/30); only ordering / vote direction (ticket 03) remains open, and
  it is separate work. This ticket records the shipped stage's behaviour, it does not
  change it.
- The J8 spacing question, corpus changes, Pot A arms (t54 already proved the dial inert
  there).
