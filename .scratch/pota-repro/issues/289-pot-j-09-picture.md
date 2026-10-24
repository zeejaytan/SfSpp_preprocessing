# 289 — Pot J 09: show the surface, our edge line and the authors' edge line

Status: done -- (S)/(S) recorded; the extent test is unrun
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
mesh survives for this piece, and the cloud ticket 259 scored was sampled from that same mesh - so regenerating from it is the right route, the new cloud is not coarser, only a different draw (corrected at results time: this line earlier said 'coarser', which is wrong);
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

## Results

Measured 2026-10-24 on the shipped binary. Run directory
`/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2151_8e1e514_p289-p09/` (runid
`20261024-2151_8e1e514_p289-p09`); index row jobid 33747056 with `verdict` and `human_note` left empty
for the lead. Every number below is from that run directory; nothing is quoted from memory.

### Phase 0 — inventory

| item | md5 | size / n |
|---|---|---|
| `.../original_samples_backup/SfS_pp/Mesh/Pot_J_Piece_09_Mesh_DS.obj` | `810009272d4ff937876b52fa5d781fcf` | 1,317,317 B |
| `.../SfS_pp/Axes/Pot_J_Piece_09_Axis.xyz` | `5ef4dd54995c95410ea143da29b85b0d` | 108 B |
| `.../SfS_pp/Breaklines/Pot_J_Piece_09_Breakline_0.pcd` | `ac745d3a07936a856170e1f4ce9ab2e4` | 74 pts |
| `.../SfS_pp/Breaklines/Pot_J_Piece_09_Breakline_1.pcd` | `485b7c19544b4a2b754d278d845e8773` | 69 pts |

Ticket 260's md5s and point counts confirmed, no correction needed. The `original_samples` tree holds
byte-identical copies of both lanes (5,860 / 5,402 B), so the reference used here is not the only copy.

Only the DS mesh survives for this piece. The cloud ticket 259 scored was sampled from this same mesh
and that file is gone, so regenerating from the mesh is the only route. No seed exists for
CloudCompare's mesh sampler (measured on Pot A 01: 843,433 / 843,282 / 843,252 points over three
draws), so the cloud is a new draw. That is why two draws were run and the spread reported, rather
than a caveat alone.

### Phase 1 — run on the shipped binary

- **edge binary reused, not rebuilt**:
  `/data/gpfs/projects/punim2657/sfs-vote-248/p288-build-33746506/src/build/edge-release/EdgeLineExtractionHeadless`,
  md5 `a28d10afab2b50bbe750d599ee2b7214` — the shipped commit-`8e1e514` binary, its md5 checked
  against this ticket before it was used.
- **mesh stage had to be built**: no `MeshPreprocessingHeadless` from `8e1e514` existed on the
  cluster, so it was built from `git archive 8e1e514` unmodified — binary md5
  `0171f471d0558d2676df7c4b113c1e9d`, kept at `$RUN/bin/` and reused by draw 2. Edge source md5 (LF)
  `f0dbfe7032d90a04412d15bd1699a703`, 3739 lines, `SEED-287` count 1.
- **`SFS_AXIS_FILE` was set and read.** Draw 1:
  `[PAPER-234] classify: face0 n=4003 interior_frac=0.0000 face1 n=2853 interior_frac=1.0000 satA=0.0000 satB=6856.0000`
  then `[PAPER-234] classify: swapped -> Surface_0=interior`. Draw 2: `face0 n=4015 … face1 n=2829 …
  satB=6844.0000` then `swapped -> Surface_0=interior`. The stage ran at the shipped defaults:
  `[PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10`, `[SPLITTER-234] ... paper=PAPER-CHAIN`.
- **clouds**: draw 1 841,020 pts, md5 `8de35d14b8605bce21d03f58e79a6935`; draw 2 840,854 pts, md5
  `97ececff8f869f42cb5a5773db856f11`. No global shift; bbox draw 1 X 2.72–44.33, Y −0.71–45.43,
  Z 449.66–485.22.
- **sheets**: draw 1 `Surface_0 beadeee6f056dda18bcf1d534e6634b6` / `Surface_1
  d644a68702cb718a7832811845c74077` (7,214 / 9,192 rows); draw 2 `76761f186ff13cf2c4eb2679a30ab7cb` /
  `df4e8e0538866d6d053c8e7099b02871`. The partition itself is re-drawn per sample, so the surfaces
  behind the two draws are not identical either.
- **one lump per lane, both draws**: `[SEED-287] ncomp=1 biggest=0 size=279/279 seed=30.2315 13.7781
  472.785` (Bl0) and `... size=309/309 seed=30.9025 14.0478 475.193` (Bl1) — so ticket 287's
  largest-lump seed changes nothing on this piece.

### Score — both draws beside ticket 259

Bar = median ≤ 2.0 mm **and** coverage ≥ 90 (`score275.lane`: coverage is the share of one ring's dots
within 2 mm of the other).

| lane | draw | n | median mm | cover ours→auth | auth→ours | jumps | max step | len ours / author | ratio | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| Bl0 | 1 (picture) | 78 | 1.204 | 75.64 | 81.08 | 0 | 4.60 | 143.20 / 133.74 | 1.07x | below |
| Bl0 | 2 | 79 | 1.041 | 70.89 | 75.68 | 0 | 4.29 | 144.69 / — | — | below |
| Bl1 | 1 (picture) | 84 | 1.980 | 51.19 | 65.22 | 0 | 3.92 | 153.32 / 125.28 | 1.22x | below |
| Bl1 | 2 | 86 | 2.122 | 48.84 | 63.77 | 0 | 2.63 | 155.63 / — | — | below |
| *Bl0, ticket 259* | — | 95 | 2.53 | 32.6 | 39.2 | 0 | — | 172.3 / 131.9 | 1.31x | below |
| *Bl1, ticket 259* | — | 95 | 2.41 | 40.0 | 52.2 | 1 (14.4 mm) | — | 181.8 / 123.5 | 1.47x | below |

Bl0 improves in every column (median 2.53 → 1.20, coverage 32.6 → 75.6, length ratio 1.31 → 1.07).
Bl1 improves in median (2.41 → 1.98), coverage (40.0 → 51.2), the 14.4 mm jump is gone and its length
ratio falls 1.47 → 1.22, but its median sits exactly on the 2.0 mm bar and its coverage is still far
short of 90. Both lanes remain below bar: this piece is a diagnosis, not a pass.

The lead re-scored the exports independently and reproduced the table (Bl0 ours→auth 1.200 / 24.4% of
our dots beyond 2 mm; Bl1 1.959 / 48.8%; auth→ours Bl0 1.148 / 18.9%, Bl1 1.269 / 34.8%, max
9.164 mm), so the numbers are not a single-script artefact.

### The draw spread — the error bar for any comparison against 259

| lane | n | point-set max mm | point-set mean mm | median moves | coverage moves |
|---|---|---|---|---|---|
| Bl0 | 78 vs 79 | 3.148 / 3.001 | 0.767 / 0.776 | 0.163 mm | 4.75 pts |
| Bl1 | 84 vs 86 | 1.147 / 1.881 | 0.462 / 0.487 | 0.142 mm | 2.35 pts |

(point-set distance computed both ways, draw 1 → draw 2 and back.) A pointwise `max|dxyz|` between the
two exported lines is not defined: n differs, so the two exports are not the same dots.

Read against that spread, the moves from 259 are one to two orders of magnitude larger than the
sampling noise (median 1.3 mm vs 0.16 mm; coverage 30–40 points vs 5). **The four shipped fixes did
change this piece.** That conclusion rests on one piece and two lanes.

### Phase 2 — the pictures

| file | px | bytes | md5 |
|---|---|---|---|
| `C:/PR/SfSpp_preprocessing/artifacts/pota289/png/p289_J09_Bl0.png` | 2300x520 | 437,812 | `e5b13d1cbcd6441fd6bb105275b113bb` |
| `C:/PR/SfSpp_preprocessing/artifacts/pota289/png/p289_J09_Bl1.png` | 2300x520 | 423,300 | `bb1f01b027aaa70ec72de1bcbe91c0d8` |

Originals: `$RUN/out/png/` (same bytes, same md5). Each figure carries five panels — 3D, X-Y, X-Z,
Y-Z and a zoom on the worst stretch — with Surface_0 (interior) blue, Surface_1 (exterior) orange, our
line thick green (#00c000), the authors' thick black. The suptitle carries the lane numbers and the
line "DS-mesh cloud: a new draw, not a re-measure of 259".

**Bl0 (interior, blue sheet).** Our green ring runs on the sheet's outer edge; the authors' black ring
shadows it closely along the left and bottom, sitting some 3–4 mm inside it, and over the top-right
black runs up and over a notch while green cuts straight across. The worst stretch is 19.8 mm of arc
(our dots 20–31 of 78) at a median 3.80 mm and max 4.88 mm — and their own ring has a 12.6 mm stretch
with median 3.72 mm at the same place, so both lines wander there. Same loop, same kept face.

**Bl1 (exterior, orange sheet).** Left half: the two rings coincide. Right half: black leaves the rim
and runs across the middle of the sheet for 41.4 mm of arc (our dots 29–52 of 84), reaching 10.4 mm
from green at a median 7.29 mm. **That stretch is not a chord**: measured per-dot turning angles along
the authors' line, no run longer than 10 mm keeps a turning angle under 2° per step, so their contour
is smooth and only *looks* straight at panel scale. What it is, is a contour drawn inside our
surface's silhouette.

Neither lane jumps anything (ticket 259 had one 14.4 mm jump on Bl1), and the dots are evenly spaced
all the way round (mean 1.84 mm and 1.83 mm), i.e. a walked rim, not a stub.

### Phase 3 — where the extra length is made

Stage readings as dot sets, 2 mm threshold:

| stage | lane | n | median mm | max mm | % dots >2 mm | % of authors' ring covered | length |
|---|---|---|---|---|---|---|---|
| `boundary.pcd` (pre-walk bag) | Bl1 | 309 | 1.717 | 11.112 | 48.5 | 65.2 | n/a (dot set) |
| `boundaryImproved.pcd` (walk input) | Bl1 | 309 | 1.961 | 11.112 | 48.5 | 65.2 | n/a |
| `cloud_Filtered.pcd` | Bl1 | 309 | n/a | n/a | 48.5 | 0.0 | n/a (degenerate dots; distance columns unusable) |
| `cloudBreaklinePointsOnBSplineSurface.pcd` | Bl1 | 84 | 1.959 | 10.447 | 48.8 | 65.2 | 153.32 mm |
| exported | Bl0 | 78 | 1.200 | 4.876 | 24.4 | 81.1 | 143.20 mm |
| exported | Bl1 | 84 | 1.959 | 10.447 | 48.8 | 65.2 | 153.32 mm |

Decomposition:

- **Bl1**: authors 125.28 mm → ours 153.32 mm = **+28.04 mm**. Before any walking, the bag was already
  1.717 mm off with **48.5% of its dots beyond 2 mm**, covering only **65.2%** of the authors' ring. The
  export is 1.959 mm / 48.8% / 65.2%. The walk added 0.24 mm of median deviation and moved neither
  percentage — the disagreement was inherited.
- **Bl0**: authors 133.74 mm → ours 143.20 mm = **+9.46 mm**. Its pre-walk bag is not retained: the
  shared per-lane stage files hold whichever surface was written last (Bl1 here), so the before/after
  split exists for Bl1 only.

The bag's *length* is not quoted because the pre-walk bag is an unordered dot set — stepping it in file
order gives a nonsense 6,816 mm. Only n, median, max, % beyond 2 mm and % of the authors' ring covered
are meaningful there. The per-face bags (`boundary_S0.pcd` / `boundary_S1.pcd`) exist only under the
compile-time POTA-218 arm and are absent from the shipped binary; the analysis logs that absence rather
than substituting one.

### Class

Rule, fixed in the analysis script before the numbers were read: **(K)** the two rings ride different
kept faces, or the authors' ring is off every kept face; **(W)** a retained bag was on the authors' ring
(median ≤ 1.0 mm, ≤ 20% of dots beyond 2 mm) but the export is not; **(S)** a retained bag was already
off before any walk; bag not retained → (S) if the ring is complete and its deviations are interior,
(W) if the ring is cut short.

- **Bl0 → (S).** Both rings ride kept face S0 (ours 100% within 1 mm, theirs 97.3%), the ring is
  complete, 0 jumps, and all four of its >2 mm stretches are interior excursions (worst 19.8 mm of arc).
  **Caveat: the bag is not retained, so this class rests on the exported geometry alone.**
- **Bl1 → (S).** Both rings ride kept face S1 (ours 100%, theirs 100%), and the bag was already
  1.717 mm off with 48.5% of its dots beyond 2 mm before any walking. The walk is not the cause.

Nobody is off the kept surfaces (2.7% of their Bl0 dots and 0.0% elsewhere are more than 1 mm from
their face): every reference dot lies on a surface we kept, so this is not a **(K)** partition
mismatch.

### What this piece is not

- **Not a whole-piece miss any more.** Both lanes come out as complete rings of 78 and 84 dots over
  143 and 153 mm, evenly spaced, with no jump.
- **Not a walk failure.** The pre-walk bag already carried 48.5% of its dots beyond 2 mm and covered
  only 65.2% of their ring, at a median of 1.717 mm; the walk moved that by 0.24 mm of median and
  0.3 of a percentage point, so the disagreement is inherited, not produced by the walk.
- **Not a partition mismatch in the ticket-286 sense.** Every reference dot lies on a kept surface
  (97.3% / 100% within 1 mm).

**Running hypothesis (not a conclusion):** this is the same shape of disagreement filed on Pot H 02 in
ticket 286 — our line is the boundary of **our** surface, theirs is the boundary of **theirs**, and the
two surfaces have different extents. On Bl1 that difference is 41 mm of arc; on Bl0 it is a systematic
inset plus one notch. What would settle it is the same test ticket 286 used, applied across pieces:
how much of each reference ring falls inside our surface's silhouette.

### Deviations

1. **The mesh stage was built** (Phase 1 said "build nothing new"). No `MeshPreprocessingHeadless`
   from `8e1e514` existed anywhere on the cluster, and the only copy present is another worktree's at a
   different commit. It was built from an unmodified `git archive 8e1e514`; md5 above. The **edge**
   binary was not rebuilt.
2. **Four jobs, not one.** 33747056 (build + draw 1 + both lanes), 33747182 (draw 2 + comparison),
   33747530 and 33747540 (two 3-second re-runs of the analysis script). The re-runs fixed analysis
   defects only — a stage file the shipped binary never writes, and a missing `matplotlib` on the batch
   PATH — and reproduced draw 1's numbers exactly. All four COMPLETED 0:0.
3. **Two PNGs, not four.** Acceptance item 1 says "four PNGs (two lanes x the panel set)" while Phase 2
   asks for one 2300x520 figure per lane carrying 3D + X-Y + X-Z + Y-Z + a zoom. Both were satisfied in
   the Phase 2 shape: one file per lane, five panels, 2300x520.
4. **This file's own Phase 0 text was corrected** (the sentence that called the new cloud 'coarser').
   The cloud ticket 259 scored came from this same DS mesh; what differs is only the sampling draw.

### Acceptance, item by item

1. Pictures exist at the path above with md5 and pixel size recorded, each showing the surface, our
   line and the authors' line — met (two files, five panels each; deviation 3).
2. The `[PAPER-234] classify` line is quoted for both draws, so the interior/exterior assignment is
   demonstrated, not assumed — met.
3. Both lanes scored on the shipped binary and set beside ticket 259, with the draw caveat replaced by
   a measured two-draw spread — met.
4. A (K)/(S)/(W) class per lane with the decomposition numbers behind it — met: (S) / (S), Bl0 with the
   stated bag caveat.
5. No code, default, threshold or `SFS_*` change, no sweep, nothing deleted outside the run directory,
   worktrees 275/276 untouched, nothing committed — met.

### Record

- Run directory as above with `run.json` (jobs, both draws, classify line, PNG md5s, classes,
  `not_done`), `submit.sbatch`, `draw2.sbatch`, `rerun_a289.sbatch`, `a289.py`, `a289d.py`, `logs/`,
  `out/`, `bin/`.
- `runs/index.tsv` row: jobid 33747056; `verdict` and `human_note` left empty for the lead. The three
  later jobs are recorded in `run.json`, not in the index.
- This ticket: `Status: results-in`, left uncommitted in the main clone.

## Lead verdict (2026-10-24)

1. **Accepted.** I read both PNGs and re-scored the exports myself, independently of the ticket's script:
   ours→auth Bl0 1.200 mm / 24.4 % beyond 2 mm, Bl1 1.959 / 48.8; auth→ours Bl0 1.148 / 18.9,
   Bl1 1.269 / 34.8, max 9.164 mm. The table is not one script's artefact.
2. **The straight-chord reading is dead, and the ticket says so.** Their Bl1 contour has no run longer
   than 10 mm that keeps a turning angle under 2° per step, so the stretch that reads as a straight line
   across the face at panel scale is a smooth curve. What is true is narrower and more useful: they drew
   a contour inside our silhouette.
3. **Ring geometry measured by me, recorded here:** all four rings close at 1.80 mm — one dot spacing, so
   both are properly welded loops. Ours encloses 1010 mm2 (Bl1) and 802 (Bl0); theirs 769 and 724. Ours
   encircles 31 % and 11 % more area. That is the physical content of the 41 mm excursion: not a wander,
   a different boundary of a different surface.
4. **Class accepted: (S) / (S)**, with the Bl0 bag caveat stated rather than hidden. Pot J 09 leaves the
   whole-piece-miss column. It stays a MISS on the bar (75.6 % and 51.2 % against 90), and the ticket
   does not claim otherwise.
5. **What this does not establish:** nothing about the corpus; nothing about the walk, which is exonerated
   on this piece by the bag measurement rather than by argument; and nothing about which of the two
   contours is "right", which is a definition question the conservator's eye decides.
6. **The draw spread is now a method, not a caveat.** Where a piece's input cloud can no longer be
   reproduced, run two draws and quote the spread (here: median moves 0.163 / 0.142 mm, coverage 4.75 /
   2.35 points) instead of hedging in prose. That rule stands for every later re-score.

Status set to **done (S)/(S) recorded; the extent test is unrun.**
