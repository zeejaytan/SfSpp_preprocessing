# 289 — Pot J 09: show the surface, our edge line and the authors' edge line

Status: ready-for-agent
Answers: none
Working in: C:/PR/worktrees/sfs/289

## Why

Ticket 259 found Pot J 09 is the **only whole-piece failure in the seven-pot rollout**: both lanes
miss, and unlike every other miss in the corpus ours is *longer* than the reference

| lane | n ours / author | length ours / author | median | coverage ours→author | reverse | jumps |
|---|---|---|---|---|---|---|
| P09 Bl0 | 95 / 74 | 172.3 / 131.9 mm (1.31x) | 2.53 mm | 32.6 | 39.2 | 0 |
| P09 Bl1 | 95 / 69 | 181.8 / 123.5 mm (1.47x) | 2.41 mm | 40.0 | 52.2 | 1 (idx 10, 14.4 mm) |

Ticket 260 then read the mesh and the bag and reported that **the boundary already follows the wrong
ring** (its own words: `onSurf == fresh`, median 0.00), i.e. the fault is upstream of the walk. That
reading was taken on the theta-4 pre-fix binary, and four things have shipped since (growth angle 3.4,
the 12 mm stop rule, the short-chain clamp, the largest-lump seed). The conservator has asked to see
the surface, our line and the authors' line for this piece.

## Goal

One picture set that lets the conservator see what goes wrong on Pot J 09, plus the numbers that say
whether it still misses on the **shipped** binary and where the excess length is made.

## Phases

**Phase 0 — inventory (no compute).** Record md5 and size for: the mesh
`sfs_main/original_samples_backup/SfS_pp/Mesh/Pot_J_Piece_09_Mesh_DS.obj`, its axis
`.../Axes/Pot_J_Piece_09_Axis.xyz`, and the authors' lanes
`.../Breaklines/Pot_J_Piece_09_Breakline_0.pcd` and `_1.pcd` (ticket 260 recorded these as
ac745d3a / 485b7c19, n = 74 / 69 — confirm or correct). Note that only the **DS (downsampled)**
mesh survives for this piece, so the cloud derived from it is coarser than the one ticket 259 scored;
say so plainly and do not present the new medians as a re-measurement of 259.

**Phase 1 — run the piece on the shipped binary.** Build nothing new: use the shipped edge binary
(commit 8e1e514, md5 `a28d10afab2b50bbe750d599ee2b7214`; if you must rebuild, build from
`git archive 8e1e514` per ticket 288, never `build.sh --target nurbs` per 282). Derive the input
cloud with `cc_mesh_to_pcd.sh` and record the cloud md5 (the CloudCompare sampler is unseeded, so the
cloud is a new draw and is not byte-reproducible). Run the mesh stage at the shipped defaults with
`SFS_AXIS_FILE` set and **quote the `[PAPER-234] classify` line** to prove the axis was read (the
trap in ticket 277: without it the stage silently keeps size order and swaps the lanes). Then the edge
stage at defaults, both lanes. Score both lanes with the project scorer against the authors' lanes and
set the numbers beside ticket 259's.

**Phase 2 — the picture the conservator asked for.** Per lane, 2300x520 px, four panels: 3D, X-Y,
X-Z, Y-Z, with Surface_0 (interior) blue, Surface_1 (exterior) orange, **our** exported line thick
green, the **authors'** line thick black, plus a zoom panel on the worst stretch, using the ticket-286
recipe (`artifacts/pota286/png/p286_H02_Bl1.png` is the reference for style and layout). Write the
PNGs to `C:/PR/SfSpp_preprocessing/artifacts/pota289/png/` and record their md5 and pixel size in the
ticket.

**Phase 3 — where the extra length is made.** Split our length excess into (a) what the pre-walk
boundary set already contained and (b) what the walk or the resample added: read
`Temp/Temp_edge/Pot_J/boundary.pcd` (the pre-walk boundary set) and `boundaryImproved.pcd` (the walk
input) beside the exported lane, and report for each: n, closed length, median/max distance to the
authors' line, and how much of each sits more than 2 mm from the authors' line. Then classify the
lane: **(K)** partition mismatch — the authors' line lies on a face we did not keep; **(S)** same face,
different contour; **(W)** the walk went wrong on a correct bag. Cite the measurements behind the
class; do not choose by eye alone, and do not propose a fix.

## Boundary

Diagnosis and pictures only. **No code change, no default, no threshold, no `SFS_*` retune, no new
build unless the shipped binary is missing.** Do not re-mesh beyond this one piece. Do not delete
anything outside your own run directory, and **do not run any sweep** — the conservator has said the
cleanup is not this session's work. Do not touch `C:/PR/worktrees/sfs/275` or `/276`.

## Record

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
`run.json`, `submit.sbatch`, `logs/`, `out/`, and one appended row in `runs/index.tsv` (verdict and
human_note left for the lead). Poll every `sbatch` from the laptop. Write results into this ticket in
the main clone and leave it uncommitted; the lead commits and appends the verdict.

## Acceptance

1. Four PNGs (two lanes x the panel set) exist at the path above, with md5 and size recorded, and each
   shows all three things the conservator asked for: the surface, our line, the authors' line.
2. The `[PAPER-234] classify` line is quoted, so the interior/exterior assignment is not assumed.
3. Both lanes are scored on the shipped binary, set beside ticket 259's numbers, with the DS-cloud
   caveat stated.
4. Phase 3 gives a (K)/(S)/(W) class per lane with the length-decomposition numbers behind it.
5. Nothing changed in the code, no default touched, no sweep run.
