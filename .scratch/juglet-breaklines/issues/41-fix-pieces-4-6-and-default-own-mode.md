# 41: fix the pieces-4/6 loss and make own mode the default

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-29)
**Branch:** 41-fix-pieces-4-6-and-default-own-mode, in /c/PR/worktrees/sfs/41
**Answers:** U19
**Blocked by:** none
**Blocks:** 07 (the Juglet end-to-end run, PAUSED)

## Why this exists

Ticket 40 measured the whole vessel for the first time and found two things. Own admission
(`SFS_REASSIGN_MODE=own`) separates both faces on 9 of 9 sherds on a uniform covering where the radius
admission nests on 8 of 9, and Pot A is untouched by it (8/8, shared 0, dot <= -0.9988). But the
ticket-37 adaptive-spacing default silently loses Juglet pieces 4 and 6: at the adaptive default they
grow ONE cluster and write no surface (both arms), while at the old fixed 0.6 mm they wrote pairs of
182/732 and 608/1016 points. The conservator chose (2026-10-29): fix that regression, then make own
mode the shipped default, verified in one grid over all nine sherds at real density.

Hypothesis to test, not assume: at the finer adaptive spacing the paper merge's fixed 1.0 mm
boundary-pair distance (`SFS_PAPER_RHOD`, default 1.0) reaches more neighbours per boundary point and
fuses the two regions into one - the same fusion seen on piece 3 at 0.6 mm ([169,99] -> [268], ticket
25). The candidate repair is to scale the merge thresholds by the spacing actually used, which is also
the standing "hardcoded metric must be adaptive" rule.

## Changes to the code (two, both with defaults proofs)

1. **Flip the admission default:** `SFS_REASSIGN_MODE` default "radius" -> "own" at the env read
   (mesh_processing_headless.cpp:3903-3905 area). Proof 1: with SFS_REASSIGN_MODE=radius explicitly
   set, the new binary reproduces the pre-change binary's Surface_0/Surface_1 point counts and the
   nest statistics on Juglet 1,5,7,8 and Pot A 07,08,01 within the run-to-run spread.
2. **Add `SFS_MERGE_SCALE=literal|spacing`** (default literal = today). In spacing mode every
   paper-merge threshold that is a length in mm (RHOD only - check that RHON/RHOC/RHOINN/RHOINC are
   dot/corvature terms and are NOT scaled) is multiplied by (S / 0.6) where S is the spacing the run
   actually used (the [SPACING-22] S). Print `[MERGE-41] piece=... scale=... rhod_raw=... rhod_eff=...`.
   Proof 2: with SFS_MERGE_SCALE=literal the merge behaves exactly as today (same cluster counts on
   pieces 1,5,7 and Pot A 07).

The merge-scale DEFAULT stays literal in this ticket. Whether it ships as spacing is the lead's
decision from this grid's evidence, recorded in the reading, not the worker's.

## The grid (at most 2 jobs, split by pot)

All cells on REAL RELEASED clouds, no synthetic, no SFS_DOWNSAMPLE_TARGET override. Pieces: all nine
Juglet + all eight Pot A. Arms:

- **A** today exactly: adaptive spacing, radius admission, literal merge (baseline; must reproduce
  ticket 40's g2/g3 numbers: J1 5497 shared; PA01 66764/57288; PA07 24636/26739).
- **B** own admission only (SFS_REASSIGN_MODE=own, literal merge) - the default-flip arm.
- **C** own + SFS_MERGE_SCALE=spacing - the repair candidate for pieces 4/6.
- **D** fixed 0.6 mm spacing + own admission (SFS_SPACING_POLICY=fixed) - the revert arm that must
  restore pieces 4 and 6 to two surfaces (182/732 and 608/1016 at the old defaults; with own
  admission the counts may move - report them beside the recorded ones).

## Measurements per cell

1. [SPACING-22] S and the downsampled point count; pre-merge cluster count and sizes (from the
   pipeline's own cluster print), post-merge count and sizes, [MERGE-41] line.
2. [STATUS-23] outcome and written surface point counts, extent, 2 mm coverage of the piece cloud,
   folded angle to the mesh.
3. Nest statistics (shared distinct points both ways, mean-normal dot) and the corrected pair
   statistic (med_nn, med_along, med_across, coincidence, signed t) per ticket 38's fixed instrument
   (stage38/instruments/measure34.py, the corrected pair_stats).
4. Wall thickness per piece (measure35.py) beside each pair statistic.
5. The pieces 4 and 6 story in full: at which rung do they lose the second region in arm A (pre-merge
   sizes vs post-merge), and what each of B/C/D does to them.
6. Switch proof table: which cells ran which switches (grep the env echoes).

## Constraints

- Only mesh_processing_headless.cpp + .scratch/juglet-breaklines/stage41/ may change; stop and report
  if anything else must.
- Compute nodes only; CRLF-check every script; the xargs/-n-2, unbound-variable under set -u, and
  brace-stripping traps are already paid for - name them in the scripts' headers.
- Corpus, /opt/sfs-pristine (record ABSENT, do not create) and the canonical checkout read-only, md5
  before/after.
- Geometry deleted with a counted record written BEFORE the delete; keep cell surface PLYs, logs and
  tables.

## Evidence to report

1. The two proofs (radius-reproduces-old and literal-merge-reproduces-old) with numbers.
2. The four-arm table over 17 pieces x 6 measurements.
3. The pieces 4/6 rung-by-rung account.
4. Pot A regression check: 8/8 two surfaces in every arm, pair statistics within the ticket-40 band.
5. Index rows appended with verdict and human_note EMPTY; corpus/input md5; deletion record; squeue
   clear.

Numbers already on record to prove the instrument against: ticket 40's g2 (A: J1 shared 5497, J5 34,
J7 336, J8 200; B: 532/0/10/0; J1 B along 1.815 across 0.528 coin 0.035) and g3 (PA01 66764/57288,
PA07 24636/26739, PA08 26774/29286; walls PA01 8.2857, PA07 4.0574); fixed-0.6 pieces 4/6 pairs
182/732 and 608/1016 (ticket 23 arm A).

## Progress

2026-10-29, worker 910df661 (runs 1 and 2 of 3 for this brief).

Run 1 - the four-arm grid, two jobs: 33946838 t41-juglet COMPLETED 0:0 05:55, 33946839 t41-pota
COMPLETED 0:0 14:04. Code: SFS_REASSIGN_MODE default flipped radius->own; SFS_MERGE_SCALE=literal|spacing
added (scales only rhoD by S/0.6, prints [MERGE-41]); binary from commit bdbd8b8.

Run 2 - the measurement rerun the lead ordered after review: run 1's nest/surface_pairs/surfaces tables
were HEADER-ONLY (two instrument defects: replica37.py never copied so every grow38/nest39 import died;
a stray ')' in jget() making every JSON lookup empty) and the pair quality of the restored pieces was
unmeasured. Fixed in 3730a0d/1f68ae7; job 33947960 FAILED 9:0 13:00 in its input gate (the :ARMS suffix
not stripped - dead plumbing, no compute); job 33948452 COMPLETED 0:0 48:05, 48 cells, all six tables
filled, 96 surface PLYs kept, per-cell measure JSONs.

Run dirs: 20261029-0017_bdbd8b8_t41-juglet, 20261029-0017_bdbd8b8_t41-pota, 20261029-0111_1f68ae7_t41-measure
(+ the failed 20261029-0045_3730a0d_t41-measure). Corpus unchanged in every run; /opt/sfs-pristine ABSENT;
geometry deletion records written before the deletes; index rows with empty verdict/human_note.

## Lead reading

2026-10-29. Every number below re-read by me from the run tables (pipeline_cells.tsv, merge41.tsv,
nest.tsv, surface_pairs.tsv, walls.tsv) and sacct - not taken from the worker's reports. The worker's
two instrument defects in run 1 (missing replica37.py import, stray ')' in jget) and its report's
"tables written per cell" claim that was not true are recorded above and cost one extra job.

### The one-line answer

The own-mode default is safe to ship and has shipped (proof 1: SFS_REASSIGN_MODE=radius reproduces the
old binary's counts within sampler spread; cluster sequences identical on all 17 pieces; Pot A pair
statistics unchanged to three decimals). The pieces-4/6 regression is NOT repaired by this ticket: the
merge is innocent (they reach the merge with ONE cluster already - retry=335 and 707 - so the loss
happens in the growth at fine spacing), the rhoD scaling changed nothing anywhere, and reverting to
fixed 0.6 mm restores two surfaces that are patches facing the same way, not two faces.

### Proof rows (verified)

Proof 1, arm A reproduces ticket 40 g2/g3 exactly: J1 10800/15780, J5 229/2317, J7 1753/1997;
PA01 66763/57289 (anchor 66763/57286), PA07 24636/26739 exact, PA08 26767/29273 (anchor 26774/29286),
all within the unseeded-sampler spread. Proof 2, arm B cluster sequences identical to arm A on every
piece (J1 13->7 sizes 4812,9032,752,373,338,205,59; PA07 11815,12888,2722,1059,1018,234,216).

### The pieces 4/6 rung-by-rung account

merge41.tsv: at the adaptive spacing pieces 4 and 6 arrive at the merge with n=1 (retry sizes 335 and
707); piece 3 likewise (289). At fixed 0.6 mm the same growth gives 2 regions (51+242 and 213+365).
So the loss is growth-side and spacing-driven - at ~0.21-0.26 mm steps the per-step normal turn falls
below the 3.4 deg gate, the growth stops being stopped by the broken edge, and one band wraps the
whole sherd (consistent with the ticket-30 curvature arithmetic). Arm C (rhoD scaled by S/0.6, factors
~0.35) changed no cluster count on any of the 17 pieces - the merge never had a second region to fuse.

Arm D (fixed 0.6 + own) restores two written surfaces: J4 120/674 and J6 514/930. But they are not
faces: J4 mean-normal dot +0.9785, pair med_across 6.16 mm (patches in different places facing the
SAME way); J6 dot +0.5813, across 8.25 mm. The old fixed-0.6 pairs (182/732, 608/1016 under radius)
were the same class of object - offset patches - which is why "they wrote pairs" was never evidence
of two faces.

### Own mode as the shipped default - what it does on real clouds

Juglet, arms A->B: J1 shared 5497 (dot +0.35) -> 532 (dot -0.914), pair along 1.815 / across 0.528 /
coin ~0 - the one genuine pair, reproduced exactly from ticket 40; J5 34->0 (dot -0.44, along 8.19 -
patches); J7 336->10 (dot +0.40, across 7.94 - patches); J8 200->0 (dot +0.76, across 6.63 - patches).
Pieces 2, 3, 4, 6, 9 write nothing in any arm at the adaptive default. Pot A: all 8 pieces shared 0
and dot -0.9988 to -0.9997 in ALL FOUR arms; pair statistics identical to three decimals (PA01
7.095/0.271, PA02 3.646/0.251); arm D's 4-5x thinner surfaces (fixed 0.6 downsampling) remain proper
opposite faces. The default flip costs nothing measured and removes the point-sharing everywhere.

### What I take from it

1. SFS_REASSIGN_MODE=own is now the shipped default, on evidence: no piece got worse, the point-
   sharing is gone, Pot A is untouched. SFS_MERGE_SCALE stays literal (it changed nothing; kept as an
   instrument for the day the merge is actually the lever).
2. The pieces-4/6 repair remains OPEN, and the mechanism is now located: the growth at fine spacing
   wraps the sherd into one band because the angle gate no longer stops at the edge. The repair is a
   spacing-relative or curvature-relative growth criterion (ticket 30's survivors), not the merge and
   not the admission.
3. Reverting to fixed 0.6 mm is NOT the repair: it restores surfaces that are same-facing patches and
   thins Pot A's clouds 4-5x for nothing.
4. Real-cloud tally under the new default: 1 genuine pair (J1), 3 patch pairs (J5/J7/J8), 5 silent
   (J2/J3/J4/J6/J9). Weight: one vessel, one pot.

### Where the jobs went wrong

Run 1's three measurement tables header-only (the two instrument defects above); one dead plumbing
submission in run 2 (the :ARMS gate); the worker's first report quoted J8-D from memory ("1 cluster")
where the table says clusters=2, outcome=none - corrected in its second report.

### verified:

- sacct: 33946838 / 33946839 COMPLETED 0:0 (05:55 / 14:04); 33947960 FAILED 9:0 13:00;
  33948452 COMPLETED 0:0 48:05.
- pipeline_cells.tsv (both pots, 4 arms x 17 pieces): counts as quoted; anchors hit (J1 10800/15780,
  PA07 24636/26739 exact; PA01/PA08 within 3/13 points of the anchors).
- merge41.tsv: J3/J4/J6 at adaptive arrive n=1 (289 / 335 / 707); at fixed 0.6 n=2 (268; 51+242;
  213+365); arm C changed no cluster count anywhere.
- nest.tsv (measurement run): J4 D shared 0 dot +0.978483694797915; J6 D shared 7 dot +0.5813134209709283;
  J1 A 5497/+0.347 -> B 532/-0.9139406842293344; J5 34/-0.48 -> 0/-0.44; J7 336/+0.51 -> 10/+0.40;
  J8 200/+0.85 -> 0/+0.76; Pot A 32 of 32 rows shared 0, dot -0.9988 to -0.9997.
- surface_pairs.tsv: J1 B med_nn 2.0146 / along 1.8152 / across 0.5282; J4 D along 0.586 / across
  6.158; J6 D along 2.281 / across 8.247; PA01 A 7.0952/7.0888/0.2709 and B/C/D identical to 4 dp;
  PA02 3.6462/3.6319/0.2513 across arms.
- walls.tsv populated (J1 D 2.353758 vs anchor 2.35376; J7 3.345018 vs 3.26316); 96 surface PLYs kept
  (find *.ply = 96).
- git: only mesh_processing_headless.cpp + stage41/ changed; corpus before==after in all four runs;
  /opt/sfs-pristine ABSENT x4; index rows present with empty verdict (filled by the lead at close).

### What this does not settle

- How to make the growth stop at the broken edge at fine spacing (the open repair; candidates from
  ticket 30: outcome-set threshold, curvature-space criterion).
- Whether the silent sherds 2/9 (fragmentation) share a mechanism with 3/4/6 (fusion) - likely
  different fixes.
- The synthetic-cloud acceptability question and the 7-of-9 last-resort bar, both standing.
