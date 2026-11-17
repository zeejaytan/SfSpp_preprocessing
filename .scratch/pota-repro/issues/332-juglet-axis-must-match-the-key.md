# 332: The Juglet's axis must come from our code — diagnose the piece that misses the key, and fix the cause

**What to build:** the axis stage produces all nine Juglet axes from **our own code**, matching
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` closely enough to be used instead of it, and the reason the
failing piece misses is **named with evidence** rather than inferred. This ticket diagnoses; it does not
re-run assembly. Today the chain is an oracle on the Juglet: the 3x cells read
`AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large`, and every one of those nine files is the
key (verified 2026-11-17: direction **0.000 deg** against `Juglet_GT`, offset ratio 1.000, on pieces 1, 5,
7, 9; only the file layout differs). The 1x cells read `Dataset/Axes/Juglet`, our own September MATLAB
output, which is right on 1 of 9 and **73.3 deg / 16.0 mm** off on piece 9 (ticket 322). So no lane in any
seating result so far used an axis our current code produced.

**Answers:** E1
**Blocked by:** None (can start immediately). If the mechanism turns out to be the size-keyed branch, this
ticket supplies the answer ticket 325 needs; it does not replace 325's whole-corpus rewrite.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek — check path: the lead re-reads the per-piece rank table against the key from a
fresh run, the pool-coverage dump for the failing piece, the per-term attribution table, and the 172-file
`cmp` count; **no assembly run, no seating number, so there is no hidden acceptance run to write**.

## What is already known (verified by the lead, 2026-11-17; do not re-derive as if new)

- **The key is right and the old released folder is wrong.** Ticket 322 established it from a third witness
  (`TORA/dataset/juglet_gt.hdf5`, 0.000-0.002 deg) and from the nine `Juglet_GT` transforms. Claim (3)
  ("the reference was wrong") is **closed**: the folder `Dataset/Axes/Juglet` was our own Sept MATLAB run,
  not an authors' reference.
- **Our finder against that key:** rank 0 within 10 deg on **4 of 9**, best-of-3 **6 of 9**, best-of-6
  **8 of 9**; piece 9 is **31.8 deg even at its best rank** (ticket 322, Q7). The one piece that no ranking
  on the current pool recovers is **piece 9**.
- **Three pieces' own walls prefer another line.** On p3, p8 and p9 the piece's own data prefer a line
  25-52 deg from the vessel axis (worse-wall cost at key 0.035 / 0.039 / 0.079 against 0.022 / 0.020 /
  0.023 at the local optimum). That is the input ceiling the ticket must test for, not assume away.
- **The finder is out of range on this object, not merely inaccurate.** Every Juglet piece sits below the
  finder's 25 mm clearance floor, so the wall-not-base gate is unsatisfiable; and the prior *prefers* axes
  further from the piece when every candidate is below its knee. The pot-scaled lengths are enumerated in
  ticket 325 with `file:line` (`AxisExtraction/sfs_axes/normalized.py:20` `DEFAULT_CLEARANCE_MM = 25.0`,
  `:138` inside `is_base_fragment`, `:183-202` the penalty; `potsac.py:176` `MAX_CLEARANCE_MM = 250`,
  `:526-533` `r_prior`, `:604-606` `valid_cone` 25-110 / `valid_dish` 35-115).
- **There is also a size-keyed branch.** `AxisExtraction/sfs_axes/potsac.py:482` "Regime 1" switches on
  `w_dc <= 15.5`, `diag <= 65`, `min_hcw <= 38` — ticket 322 calls it "the switch that sends the Juglet
  down a separate branch: a small-object patch keyed on size". **Which path the Juglet's axes actually come
  out of is an open question this ticket must settle before it explains anything.**

## Stages

**A — Baseline, rebuilt by us (must reproduce, else `blocked`).** Run the shipped axis path on the nine
**1x** Juglet pieces exactly as the last Juglet run did (`runs/20261110-0320_41494d0_t320b-juglet`, job
`34617857`; find its driver rather than inventing one) on a compute node, poll with
`scripts/remote/job_status.sh`, record final `sacct` State/ExitCode. Score every written line against
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`: **direction error in degrees and offset in mm at the piece
centroid, per piece, for rank 0..5**, plus which path produced it (Regime 1 vs the normalized union). It
must reproduce **4 / 6 / 8 of 9** within one piece of ticket 322's count and piece 9 near 31.8 deg. If it
does not, stop: the shipped path has moved since 322 and this ticket's premise is stale — report
`blocked: baseline does not reproduce` with the table.

**B — Is the true line even in the pool?** Per piece, the nearest basin in the candidate pool to the key:
report the angle, and whether a line within 1 / 5 / 10 deg exists at all. Reuse `t322/dump_basins.py`
(10 seeds x 1000 Pottmann draws, 10 deg clustering, 60 largest basins refined) or the equivalent; this is
the test that separates "the pool never offered it" from "we offered it and chose wrong". **Check the pool
on the 1x cloud the E2E itself uses, not only on the released surface xyz**, if the two differ.

**C — Attribution for every piece that misses at rank 0, and piece 9 first.** For that piece, a table of
each element's value **at the key** and **at the chosen winner**: the Regime-1 switch (`potsac.py:482`),
each gate that could reject it, the penalty (`normalized.py:183-202`), the `r_prior` knee
(`potsac.py:526-533`), the fit's drift from the true line, and the final ranking score. Name the one
element that costs the most, with numbers. Then state the claim: (1) the method fails, (2) the measurement
is broken, or (3) the reference is wrong — (3) is closed, so only (1), (2) or "input ceiling" is available,
and "input ceiling" needs stage B's dump to say the line is not in the pool at all.

**D — The smallest general fix, and only if C names one.** No constant keyed to the Juglet, no unit switch,
no "small object" flag (the conservator's 2026-11-10 ruling, ticket 322). If the mechanism is the size-keyed
Regime-1 switch or a pot-scaled length, make that element dimensionless in the piece's own size (bbox
diagonal, fitted radius or rms radius — say which, and why it is the right denominator for that term) and
show the pot margin it leaves. Then re-score the nine: **the bar is rank 0 within 10 deg on all nine**, and
whatever remains short must be explained by stage B (a piece whose pool holds nothing within 10 deg is an
input ceiling — report it as such with the dump, and do not force it). If C says a piece is a ceiling,
**stop at the diagnosis** rather than buying the bar with a constant.

**E — The pots must not move by a byte.** One writer run over the 172 pieces (`scripts/run_benchmark_172.py`,
the ticket-324 job as the template) and `cmp` every file against
`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323` (172 files, 251
lines). **Any differing file stops the ticket**: name the piece, the gate or score term that flipped, and
its pot-side margin. Do not nudge a threshold until it matches.

**F — Look at it.** Per piece, a render with the key, our rank-0 line and the winner drawn on the piece's
own cloud, at a view that resolves a 33 mm vessel, into
`SfSpp_preprocessing/artifacts/pota332/renders/` (gitignored). Look at it **before** writing the Reading;
a right angle on a line that is drawn off the piece is not a right axis.

## What would settle it (acceptance)

- [ ] A: the nine-piece rank table (rank 0..5, degrees and mm) against the key, from our own run, with job
      IDs and final `sacct` states, reproducing 322's 4/6/8 or declaring `blocked` with the table.
- [ ] B: per-piece nearest-pool-line table, saying which pieces have a line within 10 deg in the pool.
- [ ] C: the per-term attribution table for every rank-0 miss, with the failing element named and the claim
      labelled (method / measurement / input ceiling).
- [ ] D: either nine of nine within 10 deg at rank 0, or the per-piece proof that the pool does not contain
      it — with no object-specific constant added, and the byte-identity (E) still holding.
- [ ] E: 172 of 172 files identical by `cmp`, or the ticket stopped with the flipped term named.
- [ ] F: the renders, and one sentence saying what they show.
- [ ] No assembly run, no `Dataset/` write, no edit to the paper chain (`run_potsac`).
- [ ] Code tickets: branch merged into main and pushed, no job still running from it, worktree removed,
      branch deleted locally and on GitHub.

## Readings (pick one, verbatim, on a `Reading:` line)

`juglet-axis-matches-key-from-code` | `juglet-axis-mechanism-named-not-fixed` |
`juglet-axis-piece-has-no-basin` | `juglet-axis-fix-breaks-the-pots`

## Out of scope

Rerunning the assembly or any seating number; the 3x bundle's lane wiring (ticket 331/362); the wall-side
and breakline work (tickets 327/328/79); changing `Dataset/`; the paper's own chain (`AxisExtraction/run_potsac.m`);
ticket 325's whole-corpus rewrite beyond the one element this ticket proves; any constant, flag or branch
that exists because the object is small.
