# 287 — Start the walk in the largest lump, not nearest the middle

Status: ready-for-agent
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
(`verdict` and `human_note` left empty for the lead). Binary md5s, source md5s and sheet md5s in
`run.json`.
