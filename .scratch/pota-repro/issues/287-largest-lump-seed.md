# 287 — Start the walk in the largest lump, not nearest the middle

Status: results-in
Answers: E1
Working in: C:/PR/worktrees/sfs/287 (one C++ change in the edge stage; laptop worktree, Spartan run dir for the build and the gate)
Needs-eye: no

## Why this ticket exists

Conservator's decision, 2026-10-24: **seed the one full walk on the largest lump** (option 1 of
three; option 2 was to land the parked 275 selector, option 3 to hold). The reasoning is in tickets
273 and 275 and is restated here so this ticket stands alone.

The walk that ships today starts at the dot nearest the **centre of the whole bag**. On a bag that
has split into lumps (the boundary set fragments at cracks, holes and scan discontinuities), the
centre can land in a debris lump tens of millimetres from the rim. The walk then traces that lump,
the 12 mm stop rule ends it correctly, and the lane becomes a 2–5 cm stub.

Measured, ticket 275 census of 5 mm lumps: Pot C 01 Bl0 986 dots in 4 lumps (716 / 114 / 79 / 77),
seed lands in the 77 one, 54.20 mm from the largest; C01 Bl1 1090 in 2 (825 / 265), 49.36 mm;
J01 Bl0 832 in 4 (580 / 127 / 75 / 50), seed in the 127, 36.72 mm; J01 Bl1 883 in 2 (600 / 283),
32.47 mm; B01 Bl1 1150 in 2 (752 / 398), seed in the 398. In the whole ten-lane set these four (plus
B01 Bl1) are the ONLY multi-lump bags — every other lane, including all ten in tickets 271/273, is a
single lump, where this change is a no-op by construction.

The debris lumps carry **zero** author dots within 2 mm; the largest lump carries all of them
(ticket 275, census table). That is what makes the seed — not the stop rule, not the detector — the
thing to fix.

Tickets 279, 281 and 283 killed the three competing explanations for these lanes: the authors'
surfaces do contain the base (279), Pot H 02's stall is growth and Pot H 10's is a cluster we never
kept (281), and the merge's refusal is principled (283). **Pot C 01 and Pot J 01 are known-defective
inputs in the INTERIOR surface only (ticket 285, project AGENTS.md)** — so on those two pieces the
exterior lanes (Bl1) are the evidence and the interior lanes (Bl0) are a bonus, never a proof.

## The change

One file: `C:/PR/SfSpp_preprocessing/edgeline_extraction_headless.cpp`, in
`getPointsInSequence_Vote247`. No new environment switch, no new default, nothing read at runtime
beyond what is read today.

- Components are already computed at `:584-601` with `COMP_GAP_MM` (default 5.0) and the largest is
  already tracked (`biggest` / `biggestSize`, `:585`, `:599`) — it is used today only by the
  non-full-walk branch's print at `:626`.
- The seed is chosen at `:627-636`: centroid over every dot with `!used[i]`, then the dot nearest
  that centroid.
- **Change:** take the centroid and the seed over the dots whose `comp[i] == biggest` (still requiring
  `!used[i]`). Nothing else moves — the heading guard, the 12 mm stop rule, the vote-order host and
  the 1.9 mm resample are untouched.
- When `ncomp == 1` this selects the same centroid and the same dot: identical input, identical
  arithmetic, so a single-lump lane must stay byte-identical in position. Prove it, do not assume it.
- When `SFS_FULL_WALK=0` the keep-only-largest-component path has already marked every other lump
  `used`, so the set is the largest lump with or without this change: also a no-op. Say so in the
  log comment, do not "fix" that branch.
- Print one line, e.g. `[SEED-287] ncomp=<k> biggest=<id> size=<m>/<n> seed=<x y z>`, so the log
  shows which lump was chosen. The `[STOP-267] BEGIN` line already prints the seed under the diag
  flag; do not duplicate it when the flag is on.

## What must not be done

- Do NOT land the parked 275 selector. It stays parked at
  `C:/PR/SfSpp_preprocessing/.scratch/pota-repro/patches/275-walk-selector.patch` and this change is
  meant to make it unnecessary. If this ticket's gate fails, say so and stop — do not switch to the
  selector as a fallback in the same run.
- Do not re-mesh. The mesh stage draws 30 unseeded random ray-cast points
  (`mesh_processing_headless.cpp:1526-1527`), so surfaces differ run to run; reuse the frozen sheets
  and record their md5s. A re-mesh would confound the comparison with a new draw.
- Do not build with `build.sh --target nurbs` — it compiles the pre-247 duplicate at
  `original_nurbs_preprocessing/edgeline_extraction_headless.cpp` (ticket 282). Build the live root
  project; record source md5 and binary md5.
- No threshold may be retuned, and `thetaDeg` stays at 3.4. One change, one gate.

## Pre-registered acceptance (write this down before running)

Two builds on the SAME frozen sheets: **BEFORE** = main HEAD built as it stands; **AFTER** = this
ticket's branch. Same env otherwise (`POT_NAME`, edge stage only, defaults elsewhere). Scorer: the
same one used by tickets 266/271/275 (`pota266_score.py`: median distance to the nearest author dot,
coverage = share of our dots within 2 mm, jumps = consecutive step over 10 mm) — plus **author-side
coverage** (share of the author's dots within 2 mm of ours), which is mandatory here because a short
line lying on the author's line scores 100 otherwise.

1. **Guards must be byte-identical in position** (six single-lump lanes): Pot D 03 Bl0
   `216 / 0.354 / 100.00`, Bl1 `339 / 0.523 / 99.12`; Pot D 22 Bl0 `131 / 0.668 / 87.79`,
   Bl1 `143 / 0.552 / 96.50`; Pot D 01 Bl0 `334 / 0.621 / 99.40`, Bl1 `346 / 1.011 / 95.66`.
   Required: n equal, `max|dxyz| = 0.000000` pointwise, score row identical. Pot H 02 and H 10
   (four lanes) are also single-lump and must be identical: `152/0.582/100.00`, `138/0.864/73.19`,
   `98/0.661/100.00`, `92/0.641/72.83`.
2. **The three intact exterior lanes must reach the bar** (median ≤ 2.0 mm, coverage ≥ 90, zero
   jumps): Pot C 01 Bl1, Pot J 01 Bl1, Pot B 01 Bl1. What the parked selector measured on them, for
   scale — C01 Bl1 `226 / 0.527 / 100.00` (author-side 99.57), J01 Bl1 `184 / 0.596 / 100.00`
   (100.00), B01 Bl1 `307 / 0.661 / 97.39`. Accept as n ± 3, median ± 0.10 mm, coverage ≥ 90, jumps
   0. A different starting dot on the same closed loop rotates the export, so positions need not
   match the selector's to the dot — report how far the chosen start sits from the selector's, and
   show the loop is the same one (overlay or the author-side coverage figure).
3. **Interior lanes on the two defective pieces improve but do not count** (Pot C 01 Bl0, Pot J 01
   Bl0 — ticket 285). Report them; never quote them as proof.
4. **No lane may leave the bar.** Pot D 22 Bl0 is already below (87.79) and must not fall further by
   more than 1.0. Any other lane dropping below its bar fails the gate outright.
5. Report the lump census with the new seed choice on all five multi-lump bags: which lump was
   chosen, its size, and its distance from the largest — the mechanism must show as "seed moved into
   the largest lump", not as a score that happened to improve.

## If it passes

Leave the change uncommitted in the worktree with the ticket updated; the lead reviews the numbers,
commits, and then cuts the sequel ticket to delete the `SFS_FULL_WALK` split (the largest-component
plus clock-sort arm), which this change makes unreachable in purpose. Do not delete that arm here —
one change per gate.

## If it fails

Stop, report the exact lane and the failing number, and do not retune `stopR267`, `COMP_GAP_MM` or
`thetaDeg` to rescue it. A failure means the seed is not the whole story on that lane, which is a
finding, not a setback.

## Record

Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
`run.json`, `submit.sbatch`, `logs/`, `out/`, and one appended row in `runs/index.tsv`
(`verdict` and `human_note` left empty for the lead; appended, jobid 33746239). Binary md5s, source
md5s and sheet md5s, the table and the two closed blockers are in `run.json`.

## Results

Ran on the reduced gate the lead authorised: before/after on the 8 lanes whose stage trees still
exist, no mesh, no retune. Run directory
`/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed/` (jobs 33746239 seed,
33746280 H02 fix-up, 33746344 authors'-sheets probe, 33746350 and 33746383 selector comparison; all
COMPLETED 0:0). The change is uncommitted in the worktree; the diff is
`.scratch/pota-repro/patches/287-largest-lump-seed.patch` (37 lines, md5 0562edf4aab59d4ed371babf0ce4fa66,
17 insertions / 3 deletions).

**Builds.** BEFORE: source md5 `8264da3647d048e67d983edfe810b59d` (3725 lines, no `SEED-287` string),
binary md5 `62ddd28f4476e9cdf5b27cf0ee01c2f0` — identical to the p280 binary, so the edge source really
did not change between `d1b61cb` and `edf679c`. AFTER: source md5 `f0dbfe7032d90a04412d15bd1699a703`
(3739 lines, one `SEED-287` string), binary md5 `a28d10afab2b50bbe750d599ee2b7214`. Both built from
`git archive edf679c` in apptainer (`pcl_191_nurbs.sif`, 312520704 bytes) with
`cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` and
`make -j8 EdgeLineExtractionHeadless`; compiler `/usr/bin/c++`, `CMAKE_CXX_FLAGS` empty; the exact
compile command is in `logs/compile_cmd_before.txt` and `logs/compile_cmd_after.txt`. No mesh ran, and
every sheet's md5 was unchanged before and after (in `run.json`).

### The table

`n`, median (mm), coverage ours→author, coverage author→ours, jumps, max step (mm). Bar = median
≤ 2.0 mm and coverage ≥ 90 and zero jumps.

| lane | arm | n | median | cov ours→author | cov author→ours | jumps | max step | bar |
|---|---|---|---|---|---|---|---|---|
| H02 Bl0 | before | 152 | 0.582 | 100.00 | 100.00 | 0 | 3.569 | PASS |
| H02 Bl0 | after | 152 | 0.582 | 100.00 | 100.00 | 0 | 3.569 | PASS |
| H02 Bl1 | before | 138 | 0.867 | 73.19 | 74.45 | 0 | 3.736 | below |
| H02 Bl1 | after | 138 | 0.867 | 73.19 | 74.45 | 0 | 3.736 | below |
| H10 Bl0 | before | 98 | 0.664 | 100.00 | 100.00 | 0 | 3.633 | PASS |
| H10 Bl0 | after | 98 | 0.664 | 100.00 | 100.00 | 0 | 3.633 | PASS |
| H10 Bl1 | before | 92 | 0.642 | 72.83 | 77.27 | 0 | 4.571 | below |
| H10 Bl1 | after | 92 | 0.642 | 72.83 | 77.27 | 0 | 4.571 | below |
| C01 Bl0 | before | 25 | 51.620 | 0.00 | 0.00 | 0 | 5.637 | below |
| C01 Bl0 | after | 207 | 0.682 | 98.55 | 98.58 | 0 | 4.460 | PASS |
| C01 Bl1 | before | 81 | 41.055 | 0.00 | 0.00 | 0 | 4.551 | below |
| C01 Bl1 | after | 226 | 0.575 | 100.00 | 99.57 | 0 | 5.028 | PASS |
| J01 Bl0 | before | 47 | 29.268 | 0.00 | 0.00 | 0 | 5.632 | below |
| J01 Bl0 | after | 170 | 0.582 | 100.00 | 100.00 | 0 | 4.224 | PASS |
| J01 Bl1 | before | 82 | 23.306 | 0.00 | 0.00 | 0 | 4.654 | below |
| J01 Bl1 | after | 184 | 0.601 | 100.00 | 99.47 | 0 | 4.031 | PASS |

Against the ticket's own guard rows: H02 Bl0 152/0.582/100.00 and H10 Bl0 98/0.661 reproduce (mine
98/0.664); H02 Bl1 138/0.864 (mine 0.867), H10 Bl1 92/0.641 (mine 0.642). `n` and both coverage
figures reproduce exactly; the three medians differ by 0.001–0.003 mm, which is the author-dot copy
the scorer reads, not the code. Against the parked-selector bars: C01 Bl1 226/0.527/100.00 (99.57) →
mine 226/0.575/100.00/99.57, median +0.048 inside the ±0.10 tolerance, and J01 Bl1 184/0.596/100.00
(100.00) → mine 184/0.601/100.00/99.47, +0.005.

### Identity (before vs after, point by point)

| lane | n before | n after | max&#124;dxyz&#124; |
|---|---|---|---|
| H02 Bl0 | 152 | 152 | 0.000000 |
| H02 Bl1 | 138 | 138 | 0.000000 |
| H10 Bl0 | 98 | 98 | 0.000000 |
| H10 Bl1 | 92 | 92 | 0.000000 |
| C01 Bl0 | 25 | 207 | differs |
| C01 Bl1 | 81 | 226 | differs |
| J01 Bl0 | 47 | 170 | differs |
| J01 Bl1 | 82 | 184 | differs |

The four single-lump lanes are **byte-identical in position**, and their walk chains report the same
step counts and max jumps before and after (462/1.96007, 484/1.78839, 374/1.54641, 298/4.95857). The
four differing lanes are exactly the four multi-lump bags, as designed.

### The mechanism, from the logs

`[SEED-287]` after the change, and the lump census the old seed used (from ticket 275's
`[WALK-275]` lines):

| lane | lumps (5 mm) | chosen lump | seed | old seed's lump | old seed's distance from the largest |
|---|---|---|---|---|---|
| C01 Bl0 | 716/114/79/77 (4) | 716 | -5.85638 -27.3575 403.765 | 77 | 54.20 mm |
| C01 Bl1 | 825/265 (2) | 825 | -12.6057 -29.6216 404.988 | 265 | 49.36 mm |
| J01 Bl0 | 580/127/75/50 (4) | 580 | 55.1673 10.7026 472.957 | 127 | 36.72 mm |
| J01 Bl1 | 600/283 (2) | 600 | 57.7673 17.4733 474.449 | 283 | 32.47 mm |
| B01 Bl1 | 752/398 (2) | not run — no sheets | — | 398 | — |

The lump sizes match ticket 275's census to the dot. The walk now runs the largest lump and stops at
its far edge instead of stubbing in the debris lump: C01 Bl0 step 715 of 986 with 270 unvisited
(= 114+79+77, the other three lumps) and max jump 4.49 mm, where before it was step 153 of 986 with 832
unvisited and a 10.04 mm jump; C01 Bl1 step 824 of 1090 with 265 unvisited, max jump 1.71 mm (before:
step 264, 825 unvisited, 48.48 mm to the next dot).

### Same loop, different start dot

The ticket warned that a different start dot on the same closed loop rotates the export. Measured
against the parked selector's own exports in
`/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/out/` (that run holds two
arms per lane, `_247` = selector in the vote-247 host and `_full` = selector in the full walk):

- **C01 Bl1**: ours 226 points vs `_247` 226 points, point sets agree to 1.5383 mm (mean 0.4327) —
  the same loop, rotated: our seed (-15.602, -27.158, 402.709) vs theirs (51.443, 46.457, 435.781).
- **J01 Bl1**: ours 184 vs `_full` 184, ordered max 1.383180 mm, set max 1.4694 mm, mean 0.8258 —
  same loop, start dots 1.05 mm apart (6.944, 31.036, 513.769 vs 6.283, 31.403, 512.851). Against
  `_247` (184 points) the sets agree to 1.8029 mm.

In no case is the point count a coincidence of a different loop: the sets coincide to under 2 mm.

### The authors'-sheets probe: closed, it needs a mesh

Lane D03 (before and after) exited `EDGE_EXIT=139`. The log reads the sheet, cleans 31179 → 31163
dots, vets the face boundary (497 kept) and then dies on

```
[pcl::PLYReader] Temp/Data/Pot_D/Pot_D_Piece_03_unclustered.ply:1: parse error: couldn't read the magic string
[pcl::PLYReader::read] problem parsing header!
```

`<piece>_unclustered.ply` is a **mesh-stage** product, and the authors' bundle does not ship one.
B01 is blocked twice over: its `cp` failed because the bundle has `Pot_B_Piece_01_Mesh.obj`
(24,314,852 bytes) and no `_DS` variant. Running the edge stage on the authors' own surfaces would
need a mesh, which this ticket and the lead both exclude — so it yields no identity evidence.

### What was lost, and what it costs

The Pot D and Pot B stage inputs were deleted on 2026-10-24 with a class-G (geometry) deletion of
2,468 `Surface_*.xyz` files from a scratch tree. They are recorded, not recoverable:
`/data/gpfs/projects/punim2657/SfSpp/attic/pota-wave1-deleted-manifest-20261024.tsv.gz`, e.g.
`pota240_P03_V0R/Dataset/Surfaces/Pot_D/Pot_D_Piece_03_Surface_0.xyz`, 356,285 bytes, sha256
`7dcf6e1acb013e6f0b8d671e9c0103c7af550a7558551dea7c25992ad0de1544`.

Consequence, plainly: **acceptance item 1 could only be measured on 4 of its 10 lanes** (Pot H, both
stamps, two pieces) and **item 2 on 2 of its 3** (Pot B 01 Bl1 untested, so the 307/0.661/97.39
reference is unverified). The Pot D lanes that motivated the ticket — D03 and D22, 216/339 and
131/143 dots — could not be rerun at all. Nothing here answers the Pot D question; it answers the
mechanism question on four bags and leaves Pot D's numbers as they stood.

### Verdict against the pre-registered items

1. **Single-lump lanes byte-identical** — holds on 4 of 10 lanes, all on Pot H: H02 Bl0/Bl1 and
   H10 Bl0/Bl1 at max|dxyz| = 0.000000 with equal n. The six Pot D lanes cannot be measured (no
   sheets); do not describe this as ten.
2. **Three intact exterior lanes reach the bar** — C01 Bl1 226/0.575/100.00/99.57 PASS, J01 Bl1
   184/0.601/100.00/99.47 PASS, both inside the n ± 3 and median ± 0.10 window, zero jumps, same loop
   shown above. B01 Bl1 **untested**.
3. **Interior lanes on the two defective pieces** — C01 Bl0 207/0.682/98.55/98.58 and J01 Bl0
   170/0.582/100.00/100.00, both improved and both PASS; per ticket 285 they are evidence about the
   input, not about the method, and are not quoted as proof.
4. **No lane may leave its bar** — no lane changed on a single-lump bag at all, and no lane that
   passed went below. D22 Bl0 (87.79) was not rerun, so its 1.0 allowance is untouched and unverified.
5. **Lump census on all five multi-lump bags** — given for four; the seed moved into the largest lump
   on every one (distance 0), from 54.20/49.36/36.72/32.47 mm away. B01 Bl1 has no sheets.

### Deviations from the brief

- **Six of ten lanes not run** (Pot D 03, 22, 01, Pot B 01) — their stage inputs were deleted
  2026-10-24; the lead's reduced gate authorised this.
- **First seed job (33746239) produced a bad H02/before lane**: the stage-tree copy ran before its
  parent directory existed, so the edge stage ran in the wrong working directory and logged a 2.6 ms
  no-op. Job 33746280 reran that one lane and re-scored all eight. No code, sheet or parameter changed
  between the two.
- **Authors'-sheets probe attempted and failed** (33746344) — authorised as optional by the lead, and
  closed: it needs a mesh.
- One extra line of output per run (`[SEED-287]`), and it is suppressed only when `SFS_DIAG_STOP267`
  is already printing the seed, as the ticket asked. No new environment switch, no runtime knob, no
  threshold touched.
