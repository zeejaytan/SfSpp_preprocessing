# 36: The adaptive spacing without the count scaling, on the honest normals

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 36-adaptive-spacing-with-the-honest-normals, in /c/PR/worktrees/sfs/36
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

The conservator's standing instruction since the start of the Juglet work: **a hard-coded metric like the
0.6 mm sampling step must be adaptive**, or the cloud on a small sherd is too sparse to mean anything.

That was built (ticket 22: `SFS_SPACING_POLICY=piece`, S = min(0.6, max(s0, diag/N))) but it is **OFF by
default**, and every arm run since — tickets 24, 29, 30, 32, 33, 34 — used the shipped literal 0.6 mm. So the
arithmetic quoted to him ("piece 2 turns 27-51 deg per 0.6 mm step") is arithmetic **at the fixed step**, and
he is right to refuse it.

What has already been measured, and must not be re-run:

- Ticket 22's grid (117 cells) DID include adaptive spacing with the counts **not** scaled — arms
  `C2_100`, `C2_200`, `C2_400` (SFS_SPACING_POLICY=piece, SFS_SPACING_SAMPLES=100/200/400, no
  SFS_COUNT_SCALE). Verified in
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0352_d4f2187_p22-analysis/out/measure_juglet.tsv`:
  **Juglet_Piece_2 and Juglet_Piece_9 are NA (no surface) in all thirteen arms**, including those three.
  The adaptive step did refine the clouds (piece 1 went 3580/12092 -> 10800/15780 in C2_200), and Pot A stayed
  8 of 8 two-surface with the bar met in C2_200 — the refinement itself is not what broke anything.
- BUT every one of those arms used the pipeline's **re-estimated** normals. The honest carry
  (`SFS_NORMAL_SOURCE=input`, `SFS_NORMAL_CARRY=nearest`) landed only in ticket 34, and it was never tried at
  adaptive spacing.

That combination — **adaptive spacing + honest normals + counts unscaled** — has never been run. It is the
configuration the conservator has been asking for, and this ticket tests it.

## Arms

Every arm prints its own `[SPACING-22]`, `[NORMAL-33]`, `[FLOOR-23]`/`[COUNT-22]` and `[STATUS-23]` lines.
No source change is needed: all five switches already exist on main (tickets 22, 23, 33, 34). If any of them
does not behave as documented, stop and report — do not patch the source.

| arm | spacing | counts | normals | write gate |
|---|---|---|---|---|
| **A** | today: fixed 0.6 mm | today (minCluster 50) | re-estimated (today) | pair only (today) |
| **A2** | repeat of A (determinism control) | | | |
| **B** | `SFS_SPACING_POLICY=piece` `SFS_SPACING_SAMPLES=200` | **unscaled** (leave `SFS_COUNT_SCALE` unset) | re-estimated | pair only |
| **C** | as B | unscaled | `SFS_NORMAL_SOURCE=input` `SFS_NORMAL_CARRY=nearest` | pair only |
| **D** | as C | unscaled | as C | `SFS_SINGLE_CLUSTER=write` |

Pieces: **Juglet 1, 2, 3, 5, 7, 9** and **Pot_A 01-08** = 14 pieces x 5 arms = **70 cells**.

## The deciding readings

1. **Piece 2 and piece 9 under arm B and arm D** — any surface at all, and if any, its point count, 2 mm
   coverage, extent in mm, and folded angle to the mesh. These are the two that have never produced a face.
2. **The sampling step actually used, per piece per arm** (`[SPACING-22] ... s0MM= ... S= ...`), beside the point
   count entering clustering. The refinement must be visible as a number, not assumed.
3. **Pot A 8 of 8 two-surface, bar met, in every arm.** If adaptive spacing breaks the sample pot, that decides
   against making it the default.
4. **Pieces 1, 3, 5, 7** — do their surfaces keep or improve against arm A's known counts (3580/12092, 268 single,
   679 single, 1012/829)?
5. **The normal fold-to-mesh** per piece under B (re-estimated at the finer spacing) against A and C — ticket 33
   found the averaging ball, not the source, drives this, so this cell shows whether refining alone improves it.

## Acceptance criteria

1. All 70 cells attempted; `mesh_exit` recorded for every one; every run directory has run.json, submit.sbatch,
   logs/ and out/.
2. Per-cell table with: arm, piece, S used, points into clustering, clusters at each retry, floor and its source,
   final cluster sizes, outcome, surface point counts, 2 mm coverage, extent, folded angle to mesh.
3. Pot A: 8 of 8 in every arm, with the pair statistics (along / across / coincidence) on the ticket-30 ruler.
4. Defaults unchanged: arm A with no switches must reproduce ticket 34's recorded numbers on the pieces that
   write surfaces (piece 1 1422/8147 under the honest-normals arm is NOT the control — the control is
   the shipped default: 3580/12092, 182/732, 608/1016, 1012/829).
5. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT.
6. Geometry deleted behind a counted record written before the delete; surfaces and logs kept for the lead.
7. Index rows appended, 6 fields, `verdict` and `human_note` EMPTY.

## Limits

Two jobs maximum, compute nodes only. CRLF-check every script; do not use `xargs -n 2` over a two-field list;
read binary PCD and varying-column PLY defensively.

## What this cannot settle

It cannot say what the right sampling step is in principle — only what this particular adaptive rule does at
N=200. It cannot rescue a sherd whose surface turns faster than any threshold the pot can tolerate; that is a
separate question. And a surface produced here is not yet a face: the along/across test still decides that.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

### The question this answers

The conservator has asked since the start of the Juglet work for the fixed 0.6 mm sampling step to be made
adaptive: on a sherd 23-63 mm across, a 0.6 mm grid leaves too few points to mean anything. That switch was
built in ticket 22 and then left OFF, and every arm run since (24, 29, 30, 32, 33, 34) used the literal 0.6 mm.
This grid is the first to run adaptive spacing together with the scan's own normals and **unscaled** counts.

### What the spacing actually did

The rule is S = min(0.6, max(s0, diag/N)) with N = 200. Every Juglet piece resolves to its **native** spacing,
because the raw step the rule would give is finer than the mesh's own:

| piece | step used S (mm) | points into clustering, A -> B | change |
|---|---|---|---|
| Juglet 1 | 0.338049 | 14546 -> 23077 | +59 % |
| Juglet 2 | 0.210898 | 1031 -> 2397 | +132 % |
| Juglet 3 | 0.215277 | 1467 -> 3252 | +122 % |
| Juglet 5 | 0.238572 | 3021 -> 5668 | +88 % |
| Juglet 7 | 0.257988 | 4254 -> 7471 | +76 % |
| Juglet 9 | 0.203464 | 787 -> 1971 | +150 % |
| Pot A 01,02,03,05,06 | 0.6 (unchanged) | unchanged | 0 % |
| Pot A 04 / 07 / 08 | 0.581739 / 0.292881 / 0.270368 | 38901 -> 41296 / 8598 -> 34608 / 7682 -> 36097 | +6 % / +303 % / +370 % |

So the conservator's premise was correct and is now measured: the fixed step was discarding two thirds of the
samples on the two small sherds (2 and 9), and up to three quarters on Pot A 07 and 08.

### And sherds 2 and 9 still produce nothing

| arm | Juglet 2: points in / retries / clusters | Juglet 9: points in / retries / clusters |
|---|---|---|
| A (today) | 1031 / 21 / **0** | 787 / 21 / **0** |
| A2 (repeat) | 1031 / 21 / 0 | 787 / 21 / 0 |
| B (adaptive, today's normals) | 2397 / 21 / **0** | 1971 / 21 / **0** |
| C (adaptive + honest nearest normals) | 2399 / 21 / **0** | 1972 / 21 / **0** |
| D (C + write one region as one surface) | 2399 / 21 / **0** | 1972 / 21 / **0** |

The floor is 50 in every one of these cells and `floor_from` = 50, so nothing is being lost to the dynamic floor.
With 2.3-2.5x the points, at the sherd's own native spacing, with normals 0.4-1.6 deg from the mesh (see below),
the region growing still cannot assemble 50 connected points on either sherd.

**That refuses sparsity as the explanation.** It does not tell us what the explanation is; it removes the one
that has been assumed for several tickets.

### Pot A is untouched — adaptive spacing is safe for the sample

Eight of eight pieces give two surfaces in **A, A2, B, C and D**, and the pair statistics are within a few
thousandths of a millimetre of today's on every piece (arm C):
Pot_A_01 7.070 / 0.266, 02 3.633 / 0.247, 03 3.672 / 0.243, 04 3.659 / 0.231, 05 3.765 / 0.249,
06 3.548 / 0.253, 07 3.890 / 0.131, 08 3.590 / 0.135, coincidence 0.0000 in all eight.
Six of the eight keep the 0.6 mm step; the three that get finer (04, 07, 08) get **better** pairs (across
0.131 and 0.135 on 07 and 08 against 0.249 and 0.250). So the rule costs the sample nothing and helps it where
it bites.

### What it did to the sherds that do produce surfaces

| cell | today (A) | adaptive + honest normals (C) | adaptive + single write (D) |
|---|---|---|---|
| Juglet 1 | 3580 / 12092, cov 0.274 / 0.710 | 8026 / 13532, cov 0.537 / 0.585 | same as C |
| Juglet 3 | none (one region [268]) | none (one region [350]) | **one surface: 1223 pts, 18.5 x 22.0 x 13.9 mm, cov 0.929, fold 1.10 deg** |
| Juglet 5 | none (one region [679]) | 320 / 2178, cov 0.123 / 0.729 | same as C |
| Juglet 7 | 1012 / 829, cov 0.197 / 0.168 | 564 / 3219, cov 0.135 / 0.485 | same as C |

Normals to the mesh improve at the finer spacing even when re-estimated (B: 2.14 / 5.45 / 5.01 / 3.89 / 3.74 /
5.06 deg, against A's 2.36 / 8.10 / 6.11 / 4.00 / 3.39 / 9.01), and the honest carry at the finer spacing is the
best yet measured (C: 0.41 / 1.55 / 1.50 / 1.17 / 1.07 / 1.59 deg).

### The one regression to keep in view

Juglet 1's two surfaces **collapse onto each other** under adaptive spacing:
A along 0.368 / across 4.199 / coincidence 0.325; B 0.007 / 0.387 / 0.460; C and D 0.000 / 0.000 / 0.531.
That is one wall written twice, and it is the de-duplication defect of ticket 27 showing more strongly at a
finer spacing. It is not a new failure mode - J1's pair failed the genuine-pair test before this ticket too -
but the gain in coverage on J1 must not be reported as two faces.

### The two jobs, and why one is invalid

Job 1 (33880164) is **invalid** and stays in the record as invalid: arms B and C ran with empty switch strings,
because the variables were expanded inside an `export -f` function run through `xargs bash -c`, so every B and
C cell logged `policy=fixed S=0.6` and `normalSourceSet=no`. The worker found it, recorded it in
`NOTE-arms-B-and-C-ran-as-A.md`, fixed the quoting in `0a53dee` and added an in-job `ARMCHECK` gate that reads
each arm's own logs. Job 2 (33880555) passes that gate: B 14/14 cells with `policy=piece`, C 14/14 with
`normalSourceSet=yes`, D 14/14 with `singleCluster=write`. Only job 2's numbers are used above.

Also recorded: the worker's `compare36.py` reports unusable `sorted_identical` and `max_abs_diff` columns for
surface PLY files (2.5e24-scale differences where a direct parse gives identical sorted multisets). Its md5
column is sound, and the A-versus-A2 check was re-derived independently: `.ply` surfaces equal on J1, J7, A07
and A01 s1; A01 s0 differs by 2 points at 0.216 mm - consistent with ticket 34's finding that the mesh stage's
30 unseeded ray casts make surface files differ between two runs of one binary while the normals file stays
byte-identical.

### What I take from it

1. **Adaptive spacing should become the default.** It costs Pot A nothing (8 of 8, pairs unchanged or better),
   it more than doubles the samples on the small sherds, it improves the surfaces that exist, and it improves
   the normals. That is the conservator's rule, and this grid is the evidence it was missing.
2. **Its counts must stay unscaled.** The version that scaled minCluster and k1/k2 by (0.6/S)^2 (ticket 22 arm C)
   is what made coverage fall from 4 to 2; unscaled, the same rule is neutral-to-better.
3. **It does not rescue sherds 2 and 9, and density is now ruled out as their cause.** Two and a half times the
   points, native spacing, honest normals, floor 50 - still zero regions at 21 retries each.
4. **The silence of 2 and 9 now belongs to ticket 35** (what the two meshes actually are) and to the angle
   question the ladder raised: at 0.21 mm spacing, a surface folding over a 1 mm radius still turns ~12 deg per
   step against a 3.4 deg gate.

### verified: the command or file:line behind each load-bearing claim

- verified: `out/ARMCHECK.txt` in run 20261028-0013_0a53dee_t36-adaptive-spacing-r2 -> "B 14 14/14 0/0 0/0 ok",
  "C 14 14/14 14/14 0/0 ok", "D 14 14/14 14/14 14/14 ok"; A and A2 0/0 on all three.
- verified: `grep -h "SPACING-22" .../C/Juglet/Juglet_Piece_9/logs/*.log` -> "policy=piece diagMM=23.4967
  s0MM=0.203464 samples=200 rawMM=0.117483 S=0.203464".
- verified: `awk -F'\t' '$3 ~ /Piece_2$|Piece_9$/ {print $1,$3,$19,$20,$24}'` over `out/cells36.tsv` ->
  every arm "outcome=none", retries 21, npts 1031/787 (A, A2) and 2397/1971, 2399/1972 (B, C, D).
- verified: same table, arm D piece 3 row -> `npts 3253, retries 1, clusters_post_merge 1, sizes "350",
  outcome "one", floor 50, surf0_points 1223`.
- verified: `out/pairs30.tsv` arm C Pot_A rows -> along 3.548-7.075, across 0.131-0.266, coincidence 0.0000 on
  all eight pieces; arm A identical to two decimals.
- verified: same file, Juglet rows -> A J1 0.368 / 4.199 / 0.3252; C J1 0.000 / 0.000 / 0.5311; B J5
  5.187 / 10.270 / 0.0147; C J7 2.688 / 7.755 / 0.1162.
- verified: `out/inputs_before.md5` vs `out/inputs_after.md5` -> 222 lines each, cmp IDENTICAL;
  `corpus_before.txt` vs `corpus_after.txt` -> identical, 1803 lines; `out/pristine.txt` -> ABSENT.
- verified: `out/GEOMETRY_DELETED.txt` head -> "# deleted at 2026-10-27T13:18:36Z: 3831 files, 193057045 bytes";
  `GEOMETRY_KEPT.txt` -> "count 0".
- verified: `tail -2 runs/index.tsv | cat -A` -> rows 307 and 308, six fields, fields 5 and 6 empty.
- verified: `git diff --stat main...HEAD` -> 18 files, all under `.scratch/juglet-breaklines/`, nothing outside
  `stage36/` except the ticket file's four changed lines.
- verified: `sacct` -> 33880164 COMPLETED 0:0 00:03:26 spartan-bm076; 33880555 COMPLETED 0:0 00:03:59
  spartan-bm174.

### What this does not settle

- Why 2 and 9 grow nothing. Density is now excluded; the angle gate and the shape of the two meshes are the
  remaining suspects, and ticket 35 measures the second.
- Whether adaptive spacing at a finer N (400) or a different N changes anything for 2 and 9 - N=200 is the only
  value tested here.
- Whether J1's coincident pair is the de-duplication defect alone or the reassignment radius as well; the
  de-duplication repair is still queued.
- Whether making adaptive spacing the default is safe on the other nine pots. Only Pot A is in this grid.
