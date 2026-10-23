# 267 — Close the walk at the weld: stop when nothing is nearby

Answers: E1
Status: ready
Working in: C:/PR/SfSpp_preprocessing-248 (worktree only; NO main commits)
Needs-eye: no

## Why

Ticket 266 settled what the P03-Bl1 failure is. The walk is clean (median step 0.604 mm, p99 1.630 mm, exactly one step >10 mm), and the rim loop is already welded shut when the trouble starts: the walk's rim end sits 0.761 mm from its own start. But one genuine rim dot was stepped over back at 55.9% of the walk, so at the last step the fresh-candidate list is empty — and the chain does not stop. It falls back to "nearest remaining dot anywhere" (edgeline_extraction_headless.cpp:897-900), fetches that dot 124.590 mm away, and the implicit wrap then closes 124.773 mm back to the start. Leap + wrap = 249.36 mm = 27.8% of the 896.873 mm loop. That chord is what the resample and the score see (med 3.18, cov 41.9).

So: the spike is caused by the walk FAILING TO STOP, not by which dot the ordering picked. The ordering fault is upstream and only explains why one dot was left over at all.

## Goal

Three things, in this order. Do not write the rule before both instruments are reported.

### Instrument 1 — is the author's Bl1 lane a partial arc?

The lead saw, in C:/PR/SfSpp_preprocessing-248/artifacts/pota266_walk_order_P03_Bl1_1121.png, that our loop's outline reaches visibly beyond the author's compact 343-dot line (Y up to ~85, Z down to ~440). Settle whether that is expected or a second defect:

- author lane: its own closed length, and the distance from its last point to its first (is it a closed loop or an open arc?);
- our loop: 896.873 mm;
- read the scorer that produces `med` and `cov` for the pota lanes and state exactly how `cov` is computed (which direction, what tolerance, is coverage of author by us, us by author, or symmetric);
- a verdict, one line, with the numbers behind it: partial arc (expected) or second fault.

If instrument 1 says coverage is capped by a geometry mismatch that closing the loop cannot fix, STOP and report — do not chase a score.

### Instrument 2 — how big is a legitimate bridge?

A terminal stop rule is only safe if it never severs a bag that genuinely has separate pieces. P22-Bl1 currently passes at 0.57 / 95.1 with the full walk, and its bag is not one single-component blob. So measure, on the guard lanes (P03-Bl0, P03-Bl1, P22-Bl0, P22-Bl1, P01-Bl0, P01-Bl1):

- at each chain step, the distance to the nearest fresh (untaken) dot within the K=50 window, and whether that K-list is empty;
- how many steps would fire a "no fresh candidate" stop at each of R = 1.5, 2, 3, 5, 8, 12, 20, 40 mm, and how many dots each R would leave unvisited per lane.

Report the table. Choose R from it, not from taste: the smallest R that fires ZERO times on every lane where the walk currently reaches the bar, and fires exactly once on P03-Bl1.

### Rule (only if instruments allow)

Terminal stop: when the fresh-candidate set is empty at the current step, END the chain — no exhaustive fallback, no implicit far jump. Report also the variant that keeps the leftover dot: insert it at its nearest chain position instead of appending at the end (this is the "ordering fault" fix; do it only if the plain stop already scores well, and report both).

## Boundary

- C:/PR/SfSpp_preprocessing-248 worktree only. One blob patch to `edgeline_extraction_headless.cpp`. No commits to main, no commits in the worktree either — leave the diff in the tree and report its md5 plus +N/-M.
- One build is unavoidable (this is code, not a knob): use the same build sbatch the 264 worker used in that worktree. Report the new binary's md5 and its blob.
- Do not touch mesh code, axis files, or Pot A/C/D lanes that already landed.

## Constraints

- Replication gate first: with your rule OFF, reproduce ticket 266's numbers exactly (VOTE / GATED / FULL identities in the ticket). If replication fails, stop.
- Input cloud is Temp/Temp_edge/Pot_D/boundaryImproved.pcd (1121 pts = 1045 + 76). boundary.pcd in that same folder is a DIFFERENT cloud that replays to maxjump 1.499 mm / L = 660.803 — a convincing wrong answer. Do not use it.
- Check `df -h` on the project filesystem before you build; it was near full during 263. Prune only your own trees.
- STOP conditions: replication fails; instrument 1 says the score is geometry-capped; the chosen R severs any guard lane; the rule helps P03-Bl1 but breaks a passing lane. Report the negative, do not shop for a threshold that makes P03 look good.
- Heavy work on Spartan compute nodes only. No laptop runs of the pipeline.

## Acceptance criteria

1. Instrument 1 answered with numbers and a one-line verdict.
2. Instrument 2 table delivered, R chosen by the stated rule with its justification.
3. With the rule ON: P03-Bl1 scored (med, cov, jumps, resampled n) and compared against the current 3.18 / 41.9 / 1 jump.
4. Guard lanes unchanged or better: P03-Bl0 0.52/100.0, P22-Bl0 0.69/87.7, P22-Bl1 0.57/95.1, P01-Bl0 0.75/98.8, P01-Bl1 0.98/95.4. Any regression is a fail, reported as such.
5. One PNG: the P03-Bl1 walk in order, rule ON, with the author's line in black, so the lead can see whether the spike is gone and whether the loop still lies on the rim.

## Required evidence to report

Ticket Comments with: job ids and states; binary md5s; the two instrument tables; the R decision; the before/after score table; the diff md5 and size; the PNG path; and one line naming what you would have to know to overturn your own verdict. Judgement (accept / re-cut / land) is the lead's — do not write a verdict into the ticket.

## Comments

### Worker run — ticket 267 (2026-10-23). Measurements only; no verdict (lead's call).

#### Patch, build, jobs

- Worktree `C:/PR/SfSpp_preprocessing-248` (detached at 4887348), Spartan mirror `/data/gpfs/projects/punim2657/sfs-vote-248`. Nothing committed in either repo.
- Patch: one blob, `edgeline_extraction_headless.cpp`, **558 insertions(+), 1 deletion(-), 3 hunks, 36837 bytes** of `git diff`. File md5 **e9028730c7100ae75249258cb6cd9959**, byte-identical on laptop and cluster. Normalized diff kept at `sfs-vote-248/pota267_rule.diff` (md5 9e7d6f5dbcfead372a96d6ae4618f9c4); it equals the laptop's `git diff` except the `index …` blob-hash line, because the two checkouts differ in `core.autocrlf` (file is CRLF, committed blob LF). On the cluster a raw `git diff` therefore reports 3978/3421 whole-file lines — read it with `git diff --ignore-cr-at-eol`.
- Flags: `SFS_STOP_NOFRESH=<mm>` (the rule; unset/0 = pre-267 behaviour, byte-identical) and `SFS_STOP_NOFRESH_DIAG=1` (read-only instrument). The test sits between the `if (best < 0) break;` guard and `cur = (size_t)best;`, i.e. before the exhaustive nearest-anywhere fallback, so a firing chain simply ends where it stands. Test variable: `dall` = distance from the current position to the nearest **fresh (unvisited) dot anywhere** in the bag.
- Job **33716250** `potD267-build` COMPLETED 1:12 → `build-267/EdgeLineExtractionHeadless` md5 **a8e1f71521228104c3ff1f33105d2839**, only the pre-existing `-Wold-style-cast` warnings. One build, as briefed. Compared against build-263 (2d435e9f6a2b6e78ede480b326861da5) and build-264 (f3a2bcf5cdd1e90744034eef599695ce).
- Job **33716251** `potD267a` COMPLETED 3:34 — rule OFF + DIAG, 8 lanes (P03 CTL/VOTE/GATED/FULL, P22 G10, P01 G10), trees `pota267_<P>_<ARM>`.
- Job **33717040** `potD267b` COMPLETED 0:35 — rule ON at R=12, 3 lanes (P03 FULL, P22 G10, P01 G10), trees `pota267R_<P>_<ARM>`, plus scores, dd profile and the PNG.
- `df -h` before the build: `/data/gpfs` 1.9 T, 88 % used, 235 G available.

#### Replication gate: PASS — all 12 lanes reproduce ticket 266 to the decimal

| lane | n | med (mm) | cov (%) | jumps | maxjump (mm) |
|---|---|---|---|---|---|
| P03 CTL Bl0 | 225 | 0.72 | 97.8 | 0 | 7.8 |
| P03 CTL Bl1 | 358 | 0.98 | 52.8 | 1 | 47.1 |
| P03 VOTE Bl0 | 228 | 0.58 | 100.0 | 0 | 3.8 |
| P03 VOTE Bl1 | 4328 | 8.69 | 11.0 | 21 | 141.1 |
| P03 GATED Bl0 | 228 | 0.58 | 100.0 | 0 | 3.8 |
| P03 GATED Bl1 | 403 | 0.99 | 78.2 | 3 | 137.9 |
| P03 FULL Bl0 | 216 | 0.52 | 100.0 | 0 | 4.3 |
| P03 FULL Bl1 | 463 | 3.18 | 41.9 | 1 | 11.1 |
| P22 G10 Bl0 | 130 | 0.69 | 87.7 | 0 | 4.4 |
| P22 G10 Bl1 | 142 | 0.57 | 95.1 | 0 | 4.5 |
| P01 G10 Bl0 | 333 | 0.75 | 98.8 | 0 | 4.6 |
| P01 G10 Bl1 | 346 | 0.98 | 95.4 | 0 | 4.6 |

The exported pcds do **not** md5-match the 264/266 trees, and the difference is confined to the last four columns (`normal_x normal_y normal_z curvature`), which are recomputed per run: x/y/z agree per index to 0.000e+00 mm. First differing row — ours `-32.5351 -27.5049 476.015 -0.308235 -0.360745 -0.880258 2.34218e-26`, reference `-32.5351 -27.5049 476.015 -0.270902 -0.372872 -0.887456 4.63522e+12`; header lines 1–11 identical. Geometry replicated exactly, normals did not.

#### Instrument 1 — is the author's P03-Bl1 lane a partial arc, and what exactly does `cov` compute?

`cov` (scorer `pota266_score.py`, `lanescore`) is **one-way precision**: for each of *our* dots take the distance to its nearest *author* dot (`dd`), sort, then `med = dd[len//2]` and `cov = 100 * #{dd < 2 mm} / n`. It says "our dots lie on the author's line". It is **not** author coverage and **not** symmetric. Author-side coverage is the last column of the table below (computed here, not by the scorer).

| lane | slot | nAuth | nOurs | auth open (mm) | auth closed (mm) | auth last→first (mm) | ours closed (mm) | arclength cap at 2 mm (%) | measured cov (%) | author covered by us (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| P03 | 0 | 219 | 216 | 393.12 | 394.92 | 1.80 | 391.26 | 100.0 | 100.0 | 100.0 |
| P03 | 1 | 343 | 463 | 614.97 | 616.77 | 1.80 | 842.68 | 41.5 | 41.9 | 56.9 |
| P22 | 0 | 133 | 130 | 241.28 | 243.08 | 1.80 | 236.60 | 87.3 | 87.7 | 87.2 |
| P22 | 1 | 162 | 142 | 289.70 | 291.50 | 1.80 | 258.29 | 95.2 | 95.1 | 88.3 |
| P01 | 0 | 339 | 333 | 607.91 | 609.71 | 1.80 | 602.24 | 98.9 | 98.8 | 97.9 |
| P01 | 1 | 352 | 346 | 631.21 | 633.01 | 1.80 | 625.58 | 96.2 | 95.4 | 94.9 |

The cap column is the geometric ceiling `cov` could reach if every one of our dots sat on the author's line: 2 mm of tolerance divided by our own dot spacing along the loop.

**Verdict of instrument 1: the author's P03-Bl1 lane is a closed loop, not a partial arc, and no author-side stretch is missing** (last→first gap 1.80 mm = exactly one dot spacing, on all six lanes; closed length = open + 1.80 everywhere). The shortfall was ours: our P03-Bl1 loop measured 842.68 mm against the author's 616.77 mm (1.37×), inflated by the 249.36 mm leap+wrap chord, and the arclength cap on that inflated loop (41.5 %) matched the measured cov (41.9 %). So the score was capped by our own chord geometry — which is precisely what removing the weld addresses.

#### Instrument 2 — distance to the nearest fresh dot per chain step (rule OFF)

Two definitions are reported because the ticket asks about the K=50 window. `f50` = number of fresh dots among the 50 nearest neighbours; `f50 = 0` means the candidate window is empty (R-independent). `dall` = nearest fresh dot anywhere; `fires@R` counts steps with `dall > R`, and `left` is the number of dots still unvisited if the chain ended at the first such step.

| lane | bag | steps | min f50 | steps with f50 = 0 | fires @ R = 1.5 / 2 / 3 / 5 / 8 / 12 / 20 / 40 | left @ R=12 |
|---|---|---|---|---|---|---|
| P03 FULL Bl0 | 714 | 713 | 1 | 0 | 7 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 |
| P03 FULL Bl1 | 1121 | 1120 | 0 | **1** (i=1117) | 20 / 6 / 5 / 3 / 2 / 1 / 1 / 1 | **3** |
| P22 G10 Bl0 | 490 | 489 | 1 | 0 | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 |
| P22 G10 Bl1 | 423 | 422 | 1 | 0 | 14 / 9 / 6 / 0 / 0 / 0 / 0 / 0 | 0 |
| P01 G10 Bl0 | 435 | 434 | 1 | 0 | 240 / 122 / 14 / 0 / 0 / 0 / 0 / 0 | 0 |
| P01 G10 Bl1 | 427 | 426 | 1 | 0 | 242 / 139 / 14 / 0 / 0 / 0 / 0 / 0 | 0 |

(Where a slot is walked twice by the harness the figures are per walk; the two walks are identical. The P03 VOTE and GATED arms also empty the window on Bl1, at i = 347 / 1041 / 1044 — those arms already fold and are not at the bar.)

**R decision: R = 12 mm.**
- Every guard lane is fire-free from R = 5 mm up; its worst step is 4.69 mm (P01 Bl1), so 12 mm is 2.56× the worst passing-lane step.
- P03-Bl1 fires exactly once for any R in **[12, 124.59)** — the leap is 124.590 mm and there are further steps with `dall` in (8, 12] at i=338, so R must be ≥ 12 to keep the stop *exactly* once.
- The K-window definition (`f50 = 0`) would also fire exactly once on P03-Bl1 and never on a guard lane — but `min f50 = 1` on every guard lane means that test sits one dot away from stopping a passing lane, which is why the shipped rule uses an explicit distance margin instead.

#### Rule ON at R = 12 (job 33717040)

- `[STOP-267] CHAIN-END step=1117 of 1121: nearest fresh dot 124.59mm > R=12mm ; refusing it ; left=3 dots unvisited` (chain 1118 of 1121 dots).
- Before → after (n / med / cov / jumps / maxjump): **P03 FULL Bl1 463 / 3.18 / 41.9 / 1 / 11.1 → 333 / 0.90 / 57.4 / 0 / 4.1** (largest single step in the exported walk 47.8 → 5.67 mm).
- Guard lanes, rule ON, identical to rule OFF to the digit: P03 Bl0 216 / 0.52 / 100.0; P22 Bl0 130 / 0.69 / 87.7, Bl1 142 / 0.57 / 95.1; P01 Bl0 333 / 0.75 / 98.8, Bl1 346 / 0.98 / 95.4. No guard lane is severed, none regresses.
- PNG: `/data/gpfs/projects/punim2657/sfs-vote-248/pota267_P03_Bl1_rule12.png` (257 942 B), copy at `C:/PR/SfSpp_preprocessing-248/artifacts/pota267_P03_Bl1_rule12.png` — the walk in chain order, author's lane in black, implicit wrap dashed red. The 124.59 mm spike is gone and the loop closes; the picture also shows where the loop no longer lies on the black line (see next section).

#### Why P03-Bl1 is still not at the bar: a second fault that termination cannot reach

- Exported loop, rule ON: n = 333, closed length 601.69 mm (open 599.89 + 1.80 wrap) against the author's 616.77.
- **One contiguous off-line run** in chain order: exported indices 124–265 (142 dots, 255.6 mm of arclength = 42.6 % of the loop), distance to the author's lane mean 4.13 mm, max 5.67 mm (samples along it: 2.50 / 3.13 / 3.31 / 3.71 / 4.77 / 5.25 / 5.13 / 5.21 / 4.36 / 3.56 / 2.82).
- Mirrored on the author's side: 149 of 343 author dots are >2 mm from our loop, in one stretch, author indices 157–304 (148 dots, 266.4 mm, mean 4.18 mm, max 5.67 mm). Side split along our run: 47 dots on one side of the author's local normal, 95 on the other.
- So after the weld is closed the walk tracks a **parallel line about 4 mm away over 42.6 % of the loop**; the missing arclength (our loop is 15 mm shorter than the author's) matches the chord that the deviation cuts. This is dot selection/ordering along the rim — the walk chooses one of two nearby boundaries for a stretch — not termination.
- Bag composition (reconstructed from the rule-OFF per-step log): the Bl1 bag = 1044-dot main component + a 76-dot component at chain indices 338–413, centroid (17.9, 43.8, 578.2), extent 30.8 × 11.5 × 9.3 mm. The 255.6 mm off-line run brackets that component's neighbourhood, but the components are not themselves the explanation: only 76 of the 142 off-line dots belong to the small one.

#### The leftover-dot variant (reported, not implemented)

3 dots stay unvisited at R = 12 (the deferred landing cluster at [-35.333, -29.997, 474.946], which ticket 266 measured as 3 coincident coordinates). That cluster sits **1.876 mm** from chain dot #776 — 0.12 mm inside the 2 mm `cov` band — so inserting it at its nearest chain position instead of appending it would add ≤3 dots that are already covered, moving `cov` by at most ~0.9 pt and adding no arclength. On this lane it is a geometric no-op, and it needs a second build, so it was not built; the variant is reported because the ticket asks for it, and the measurement above is why it is not worth a build here.

#### Caveat on one log column

The `d50` field printed in the `[STOP-267] S` lines is **not** the nearest fresh dot inside the K=50 window: it is the last (i.e. farthest) fresh candidate in that neighbourhood, ≈ the K=50 radius (12–34 mm per lane). It is a defect in the diagnostic print only — the rule, the stop decision and every score come from `dall`, `f50` and the picked point, and `f50` is computed correctly. Wherever `f50 > 0` a fresh dot lies inside the window, so the nearest fresh dot in the window equals `dall`; where `f50 = 0` there is none. Not rebuilt to fix the print, to keep the build/binary md5 reported above unchanged.

#### What would overturn this

If the exported `x y z` of the rule-OFF runs are not per-index identical to the 264/266 trees after the EOL/format reconciliation (only the normal and curvature columns differed here), the replication gate would be void and every number above with it; equally, if the 255.6 mm off-line stretch turns out to be an artefact of the 1.9 mm resample rather than of the walk's dot choices, the second fault would move back into the termination question instead of dot selection.

## Lead verdict (R6, 2026-10-23)

Checked independently: this ticket's Comments, the diff in C:/PR/SfSpp_preprocessing-248 (edgeline_extraction_headless.cpp md5 e9028730c7100ae75249258cb6cd9959, +558/-1, flags SFS_STOP_NOFRESH / SFS_STOP_NOFRESH_DIAG at diff lines 292-298), the scorer definition (pota266_score.py:17-27 lanescore: cov is one-way, OUR dot -> nearest AUTHOR dot < 2 mm), and the rule-ON overlay C:/PR/SfSpp_preprocessing-248/artifacts/pota267_P03_Bl1_rule12.png.

ACCEPTED, and a strict improvement:

- Instrument 1 answered the question it was asked: the author's Bl1 lane is a CLOSED loop (last->first 1.80 mm = one dot spacing on all six lanes), so the 266 open observation is settled — the extra extent was OUR chord, not a partial author arc. The corroboration is worth recording: the arclength cap on our inflated loop was 41.5% and the measured cov was 41.9%.
- Instrument 2 chose R from data, not taste: every guard lane is fire-free from R = 5 mm up (worst step 4.69 mm, P01 Bl1), so R = 12 mm sits at 2.56x the largest legitimate gap, and P03-Bl1 fires exactly once for any R in [12, 124.59). The window-empty variant was correctly rejected for having no margin (min f50 = 1 on all five guard lanes).
- Rule ON: P03 Bl1 463 / med 3.18 / cov 41.9 / 1 jump / maxjump 11.1 -> 333 / 0.90 / 57.4 / 0 jumps / 5.7, largest exported step 47.8 -> 5.7 mm. Five guard lanes identical to the digit; nothing severed. Loop closes over 1.80 mm.
- Leftover-insert variant correctly NOT built: the 3 unvisited dots sit 1.876 mm from chain dot #776, inside the 2 mm band the rim already covers, so it is a geometric no-op (<= ~0.9 pt cov). Honest call; one-build constraint respected.

NOT AT BAR, and the reason is a SECOND fault that termination cannot reach: one contiguous 255.6 mm run (42.6% of the loop, exported idx 124-265, 142 dots) tracks a parallel line at mean 4.13 mm / max 5.67 mm from the author's lane, mirrored by a 266.4 mm author stretch at mean 4.18 mm; 149 of 343 author dots are >2 mm from our loop. Since 42.6% is exactly the share of our dots that are >2 mm, that run IS the whole miss population and no dot anywhere is farther than 5.67 mm: the loop and the author agree on ROUTE and differ by a consistent few-mm lateral offset. Own cross-check: our closed length 601.69 mm against the author's 616.77 mm, 15.1 mm short, is what a ~4 mm inward shift over 255 mm of a ~100 mm-radius loop produces, so the length figures and the offset figures agree rather than compete. The overlay supports it: the loop closes, tracks black round the ring, and rides inside the author's line over one stretch; the upper-right lobe is NOT an ours-only excursion — it cannot be, because every dot >2 mm lies in that one run whose max is 5.67 mm.

Consequence for the pota framing: P03-Bl1 is no longer a walk defect. It is now a boundary-POSITION defect of about 4 mm over 43% of the seam. Nothing in the walk family (strand selection, closure, stop rules) reaches it, and the park on the guided filter stands.

Next step is a diagnostic, not a fix: establish whether that 4 mm is in the extracted bag itself (upstream, edge/mesh stage, nothing the walk can do), or whether bag dots nearer the author's line exist and the walk declined them (ordering), or whether the author's line is simply off our surface there (reference). P03-Bl0 and every passing lane stay untouched.

Uncommitted as required: the diff is left in the 248 worktree, OFF by default, no commits in either repo.
