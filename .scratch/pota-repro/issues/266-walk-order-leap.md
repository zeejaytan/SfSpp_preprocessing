# Ticket 266: the walk's 122.8 mm leap — instrument it, then test one ordering rule

**Answers:** E1

**Blocked by:** none. 265 LANDED df178ca (analysis only, no tracked source touched, 248 worktree source still == 263+264 patches).

**Status:** results-in
**Working in:**

- [x] Instrument FIRST (no source change): dump the FULL_WALK chain on the unfiltered 1121-dot P03-Bl1 bag with per-step gap, locate the 122.846/124.59 mm leap, classify it as MID-WALK DEPARTURE vs FINAL CLOSURE step — **CLOSURE** (see Comments)
- [x] Report the dots immediately before/after the leap, the local spacing distribution, and how many candidates the K=50 heading-guarded search had at that step — 0 fresh, exhaustive-NN path
- [x] Render the walk as ONE PNG: polyline coloured by step index, leap segment marked, plus a zoom at the leap — artifacts/pota266_walk_order_P03_Bl1.png (+ _1121 variant)
- [x] THEN one rule — **NOT BUILT: the ticket's STOP CONDITION fired** (the leap is the walk's terminal closure step). No source change, so no rebuild and no new md5.
- [x] Same job ran the guard set at bar (P03-Bl0, P22 both lanes, P01 both lanes, two gate rungs); no segfault; all untouched lanes reproduce 263/264 to the decimal
- [x] Evidence in ticket Comments + Status results-in

## Goal

265 proved the P03-Bl1 bag is ONE folded sheet on the EXTERIOR face, that the 76 dots the 264 3 mm gate drops are genuine rim on the author's line, and that the 1045-dot component's chain ORDER leaps 122.846 mm straight across the loop (visible as a straight chord in panels a/b of C:/PR/SfSpp_preprocessing-248/artifacts/pota265_strands_P03_Bl1.png). Ordering, not filtering and not separation, is the open question. Answer it with an instrument and one rule.

## Boundary

- 248 worktree C:/PR/SfSpp_preprocessing-248 (detached @4887348 + 263/264 patches, uncommitted) and its Spartan mirror /data/gpfs/projects/punim2657/sfs-vote-248. Edge stage ONLY (edgeline_extraction_headless.cpp and its call sites).
- NO main commits, no tracked source committed. New behaviour behind its own flag, default OFF.
- Do NOT enable SFS_GUIDED_FILTER on any lane — 265 proved it deletes genuine rim (76 dots on the author's line).
- Reuse the read/render helpers in the existing pota265_*.py scripts if useful.

## Constraints

- Spartan: git pull --ff-only, STOP on divergence. Same node class for md5 comparisons.
- Existing binaries to reuse UNCHANGED while only instrumenting: FULL walk md5 2d435e9f6a2b6e78ede480b326861da5, guided md5 f3a2bcf5cdd1e90744034eef599695ce. If md5 differs, STOP and report.
- Source change => rebuild on Spartan + record the new md5, and say which binary produced which lane.
- Replication gate: the untouched lanes must reproduce 263/264 to the decimal in the SAME job (P03 CTL 0.72/97.8 + 0.98/52.8/1j; VOTE 0.58/100 + 8.69/11.0/21j; GATED 0.58/100 + 0.99/78.2/3j; FULL 0.52/100 + 3.18/41.9/1j n=463; P22 FULL 0.69/87.7 and 0.57/95.1; P01 0.75/98.8 and 0.98/95.4).
- Judgement stays with lead — stage evidence and STOP. Do NOT tune the rule across many k values; one documented k, honest result. If the instrument shows the leap is the final closing step of a legitimately open curve, STOP and report that instead of building a rule.
- Disk was 84% in 265 — check df -h, prune only your own temp trees, keep evidence.

## Acceptance

- Instrument: leap index in the chain, its two endpoint coordinates, the gap, the previous/next 10 steps' gaps, local median spacing, and the MID-WALK vs CLOSURE classification — with the log lines that show it.
- PNG: whole walk coloured by step index (leap shown in a contrasting colour or marked), plus a zoom panel at the leap. Readable without the ticket.
- Rule: the chosen k and the mm threshold, why that k, and the fallback; per-lane scores before/after on P03-Bl1 (med/cov/jumps) against the 264 baseline 3.18/41.9/1j.
- Guards at bar-or-better (P03-Bl0 >=97%, P22 both lanes, P01 both lanes) and no segfault anywhere, in the same job.
- Honest verdict line: rule closes the leap and is worth keeping, or it does not and why.

## Lead verdict (R6, 2026-10-23)

Checked independently: ticket Comments, both walk-order PNGs (C:/PR/SfSpp_preprocessing-248/artifacts/pota266_walk_order_P03_Bl1_1121.png and ..._Bl1.png), and the ticket's claim that the 10/14/20/28 mm lanes are identical to gate-OFF FULL.

ACCEPTED — the leap is a FINAL CLOSURE step, not a mid-walk departure. STOP CONDITION correctly honoured; no ordering rule built, and the worker's reason is sound: a step-length guard fires at exactly the one step whose K=50 fresh-candidate list is empty, so its only fallbacks are 'keep' (no change) or 'stop the chain' (silently drops a genuine dot, i.e. a filter). Any k from ~2.5 to ~180 fires identically.

THE MECHANISM, which supersedes the braid framing:
- The walk itself is CLEAN: median step 0.604 mm, p99 1.630 mm, exactly one step >10 mm, and K=50 exhausted on exactly one step. There is no scribble and no strand-hopping in the chain.
- What breaks is the CLOSURE. The rim loop is already welded shut when the leap fires (|rim end before leap - walk start| = 0.761 mm). One genuine dot (1.208 mm off the author's line; 1.876 mm from a rim dot the walk passed at chain index 776 = 55.9% through) was deferred by greedy NN and is collected at the very end; the implicit wrap then closes 124.773 mm back to the start.
- Leap + wrap = 249.36 mm = 27.8% of the 896.873 mm closed loop. That is the structural defect the 1.9 mm resample and the score see.
- CONSEQUENCE: 'P03-Bl1 is a braid / two strands' is WRONG as a description of the walk. 265's own evidence already hinted at it (the 1045 set is one traversal, lag-distance monotone, no dip); 266 confirms it at chain level.

GATE SWEEP — pre-registered rule answered, the filter has NO job on this bag:
- Separability exists and is clean: the 1045 strand sits min 0.000 / med 0.369 / max 0.939 mm from the reference line; the 76-dot arc sits min 3.512 / med 6.645 / max 8.744 mm. Nothing overlaps.
- Kept counts across 3/4/5/6/8/10/14/20/28 mm: 1045/1059/1068/1078/1106/1121/1121/1121/1121. Every dropped dot is inside the 76-dot arc; no strand dot is ever dropped.
- Scores: 4.00/3.67/3.58/3.39/3.24 then 3.18 at 10 mm and all wider, identical to gate-OFF FULL. Coverage never leaves ~42.
- Rule (i) kept>=1115 is met only by inert rungs (>=10 mm, dropped 0); rule (ii) 'removes something genuinely off-surface' is met by NO rung. Count of genuinely off-surface dots in this bag: 0. The window between 'eats rim' (<=8 mm) and 'does nothing' (>=10 mm) is EMPTY — proven by count, not argued.
- STRUCTURAL: the gate lives inside getPointsInSequence_Vote247 (edgeline_extraction_headless.cpp:687-741); the CTL/greedy path never reads SFS_GUIDED_FILTER. CTL, CTLG3, CTLG8 are bit-identical in the same job (714/1115 sequenced; Bl0 0.72/97.8, Bl1 0.98/52.8/1j). So the filter cannot clean the production greedy path at all, whatever its setting. Recorded for the ledger.

PARKED: SFS_GUIDED_FILTER stays default-OFF and must not be re-enabled without new evidence from a bag that actually contains off-surface dots. Do not re-open the gate sweep on P03.

TRAP RECORDED for every follow-up: the walk reads Temp/Temp_edge/Pot_D/boundaryImproved.pcd (1121 pts, 1045+76). boundary.pcd in the same folder is a DIFFERENT cloud (1121 pts, ONE comp) that replays to maxjump 1.499 mm / L=660.803 — a convincing wrong answer.

OPEN OBSERVATION for the next ticket (not a conclusion): in the X-Z and Y-Z panels the walk's outline extends visibly beyond the author's breakline (author 343 dots, compact; our loop reaches Y ~85 and Z ~440). Whether that is expected (author's lane may be a partial arc) or a second defect capping coverage must be settled before any score improvement is claimed from closing the loop properly.

## Required evidence to report

Ticket Comments + results-in; PNG path (laptop and Spartan); leap table; per-lane score table before/after; job IDs + sacct State/ExitCode; binary + edge md5s; diff summary; self-contained completion message.
## Comments

### Step 1 — instrument the leap (job **33709589** `potD266b`, sacct **COMPLETED / 0:0 / 00:05:27**, node spartan-bm167)

**No source change**: the job reused the trusted binaries untouched — FULL `2d435e9f6a2b6e78ede480b326861da5`, guided `f3a2bcf5cdd1e90744034eef599695ce`; the job aborts with exit 9 if either md5 differs. `git diff` on tracked source is still just the 263+264 patch; nothing committed.

**The walk's input cloud** (this is where a follow-up can go wrong): the FULL/VOTE walk reads `Temp/Temp_edge/Pot_D/boundaryImproved.pcd` — n=1121, comps@5mm = **1045 + 76**. Proven by the log sequence `[EDGELINE DBG] boundaryCloud_Improved size=1121` → `cloud_filtered size=1121` → `[LOOP-SELECT] bag=1121 comps=2` → `[VOTE-247] comp-filter kept 1045/1045` → `[FULL-263] no-discard kept 1045/1045`. **`boundary.pcd` in the same folder is a different cloud** (also 1121 points but ONE 5 mm component — a single point bridges the gap) and replaying it yields maxjump 1.499 mm / L=660.803 mm, i.e. a convincing-looking wrong answer. The instrument therefore reads the bag the log names and cross-checks its replay against the logged maxjump and arclength before printing anything.

**Replay validity** — offline replica of the shipped chain (centroid-nearest seed, K=50, plain-NN pick, exhaustive fallback) reproduces the binaries to the decimal:

| set | chain | replay maxjump | logged | replay L | logged |
|---|---|---|---|---|---|
| 1121 bag (FULL lane) | 1121 | 124.590 mm | `[FULL-263] chain=1121 maxjump=124.59mm` | 896.873 mm | `[VOTE-247] resampled=472 (L=896.873mm)` |
| 1045 comp (G3 lane) | 1045 | 122.846 mm | `[FULL-263] chain=1045 maxjump=122.846mm` | 890.467 mm | `[VOTE-247] resampled=469 (L=890.467mm)` |

**The leap**

| field | 1121 bag | 1045 comp |
|---|---|---|
| leap step | **1117 of 1120 steps (99.7 % through the walk)** | **1041 of 1044 (99.7 %)** |
| gap | **124.590 mm** | **122.846 mm** |
| departure | [54.410, 49.518, 508.799] | [54.922, 47.941, 504.455] |
| landing | **[-35.333, -29.997, 474.946]** (identical in both) | same |
| local median spacing, 20 steps before | 0.671 mm → leap = **185.6×** | 0.683 mm |
| 10 steps before | 0.737, 0.722, 0.634, 0.620, 0.700, 0.457, 0.235, 0.959, 0.340, 0.483 mm | same order of magnitude |
| steps after the leap | **2, both 0.000 mm** (same coordinate repeated) | 2, both 0.000 mm |
| fresh (unused) candidates in the K=50 list at the leap step | **0** | **0** |
| pick source at the leap step | **exhaustive-NN fallback (source :897-900)** | same |
| landing → walk start / → chain end | 124.773 mm / 0.000 mm | 123.022 mm / 0.000 mm |
| implicit closure gap (chain end → chain start) | 124.773 mm | 123.022 mm |
| landing dot is a cluster of | **3 coincident coordinates** | 3 |

Whole-walk context: median step 0.604 mm, p99 1.630 mm, **exactly one step above 10 mm in the entire walk**, K=50 fully exhausted on exactly 1 step (the leap), fresh-in-K50 median 25.

**Where the landing dot actually sits** (the decisive measurement):

- 1.876 mm from another rim dot at **chain index 776 = 55.9 % through the walk** → the walk passes within ~1.9 mm of it in mid-rim and leaves it for last;
- **1.208 mm off the author's black breakline** → it is genuine rim, not a stray or a satellite;
- **|rim end before the leap − walk start| = 0.761 mm** → when the leap fires, the rim **loop is already welded shut**.

**Classification: FINAL CLOSURE STEP** (terminal collection of one deferred genuine dot), **not** a mid-walk departure. Evidence chain: the rim is closed at 0.761 mm → the leap is step 1117/1120 (99.7 %) → the only steps after it are two 0.000 mm repeats of its landing coordinate → the loop then closes back over the 124.773 mm wrap. Long-run cost: the leap (124.590) + the wrap (124.773) = **249.36 mm = 27.8 % of the 896.873 mm closed loop**, which is why the 1.9 mm resample of this bag scores med 3.18 mm / cov 41.9 %.

**STEP 2 NOT BUILT — the ticket's STOP CONDITION fired** ("if the instrument shows the leap is the final closing step of a legitimately open curve, STOP and report that instead of building a rule"). Recorded reasoning, so the decision is auditable rather than a matter of taste: a step-length rule would fire on exactly this one step, where the K=50 list contains **zero** fresh candidates; its only possible fallbacks are (a) *keep* — output unchanged, or (b) *stop the chain* — which silently drops that one dot and is a filter, not an ordering rule. Any k from ~2.5 to ~180 fires identically (the leap is 185.6× the local median and the largest non-leap step in the walk is 1.63 mm), so there is no k to justify from the data. If the lead wants the crossing chord gone, the operative lever is the **deferred leftover dot and the implicit wrap** (close the loop at the 0.761 mm rim weld and attach or absorb the leftover), which is a different ticket, not an ordering guard. Judgement stays with the lead.

### Gate sweep (SCOPE ADD 2) — same job, guided binary, FULL_WALK on, no rebuild

**The gate quantity is a property of the bag, not of the knob** (same reference loop at every lane: 4576 points from the largest 1045/1121 comp, `[GUIDED-264] ... (ref loop 4576 from largest 1045/1121)`), so it is measured once:

| population | n | min | p25 | median | p75 | max |
|---|---|---|---|---|---|---|
| 76-dot arc (genuine rim) | 76 | **3.512** | 4.385 | **6.645** | 7.753 | **8.744** |
| 1045-dot strand | 1045 | 0.000 | — | 0.369 | — | 0.939 |

Columns are distance to the reference line in mm. The strand's p99 is 0.911 and its max 0.939, so the gate can never separate the arc from junk by distance: the arc is 3.5–8.7 mm off the line and the strand is sub-millimetre on it.

**(A) Ladder on P03-Bl1** (kept/1121 from each lane's own `[GUIDED-264]` line; scores from `Dataset/Breaklines/Pot_D/Pot_D_Piece_03_Breakline_1.pcd`):

| SFS_GUIDED_DIST | kept/1121 | dropped | of the 76-dot arc kept | n | med | cov | jumps | maxjump |
|---|---|---|---|---|---|---|---|---|
| 3 (264 baseline) | 1045 | 76 | 0/76 | 460 | 4.00 | 42.2 % | 1 | 11.1 |
| 4 | 1059 | 62 | 14/76 | 460 | 3.67 | 42.0 % | 1 | 11.0 |
| 5 (264 baseline) | 1068 | 53 | 23/76 | 461 | 3.58 | 41.9 % | 1 | 11.5 |
| 6 | 1078 | 43 | 33/76 | 461 | 3.39 | 42.1 % | 1 | 11.1 |
| 8 (264 baseline) | 1106 | 15 | 61/76 | 461 | 3.24 | 42.3 % | 1 | 11.1 |
| **10** | **1121** | **0** | 76/76 | 463 | 3.18 | 41.9 % | 1 | 11.1 |
| 14 | 1121 | 0 | 76/76 | 463 | 3.18 | 41.9 % | 1 | 11.1 |
| 20 | 1121 | 0 | 76/76 | 463 | 3.18 | 41.9 % | 1 | 11.1 |
| 28 | 1121 | 0 | 76/76 | 463 | 3.18 | 41.9 % | 1 | 11.1 |
| gate OFF (= FULL) | 1121 | 0 | 76/76 | 463 | 3.18 | 41.9 % | 1 | 11.1 |

Every dropped dot is a member of the 76-dot arc (first dropped indices 902, 906, 907, 909 … — all inside the arc component); **no dot of the 1045-dot strand is dropped at any rung** (strand max gate distance 0.939 mm < 3 mm). The rungs trade genuine rim dots for nothing. The 1.2 mm-covered Bl0 is untouchable — `kept 714/714` at every rung, 0.52/100 % unchanged.

**(B) Against the pre-registered rule — no sweet spot exists on this bag.** (i) "keeps ≥ 1115 of 1121" is satisfied **only** by the inert rungs (≥ 10 mm, kept 1121, dropped 0); (ii) "still removes anything genuinely off the surface" is satisfied by **no** rung, because the only population the gate can remove is the genuine 3.512–8.744 mm arc. **Count of genuinely off-surface dots in this bag: 0.** The window between "eats rim" (≤ 8 mm, 15 of 76 arc dots gone, kept 1106 — also fails (i) by 9) and "does nothing" (≥ 10 mm) is empty. That is the real result the rule was written to catch, not a failed sweep: on P03-Bl1 the filter's job (cleaning strays) has no work to do, and any setting that does work is deleting rim.

**(C) Squiggle control — structurally impossible on that path, and that is the finding.** The gate lives *inside* `getPointsInSequence_Vote247` (`edgeline_extraction_headless.cpp:687-741`); the CTL/greedy path calls the other sequencer and never reads `SFS_GUIDED_FILTER`/`SFS_GUIDED_DIST`. Evidence from the same job: CTL, CTLG3 and CTLG8 are bit-identical — `cloud_sequenced (rim) size=714` / `size=1115`, scores Bl0 0.72/97.8 % (n=225) and Bl1 0.98/52.8 %/1j (n=358) in all three, and **no `[GUIDED-264]` line appears in any CTL lane**. So the greedy stray tail cannot be tested against the gate without a source change; per the instruction, reported and stopped — no hunting on other pots.

**(D) Clean-lane guards** at 10 mm (plateau edge) and 28 mm (the rule's literal answer), same job:

| lane | 10 mm | 28 mm | bar | verdict |
|---|---|---|---|---|
| P03-Bl0 | 216 / 0.52 / 100.0 % / 1.2 / 0j | identical | ≥ 97 % cov | **at bar** |
| P22-Bl0 | 130 / 0.69 / 87.7 % / 7.2 / 0j | identical | 0.69/87.7 | **at bar** |
| P22-Bl1 | 142 / 0.57 / 95.1 % / 4.7 / 0j | identical | 0.57/95.1 | **at bar** |
| P01-Bl0 | 333 / 0.75 / 98.8 % / 2.6 / 0j | identical | 0.75/98.8 | **at bar** |
| P01-Bl1 | 346 / 0.98 / 95.4 % / 3.2 / 0j | identical | 0.98/95.4 | **at bar** |

At both rungs the gate keeps everything on the clean lanes (`490/490`, `423/423` on P22; `435/435`, `427/427` on P01) — inert, so no lane can regress. No segfault in any of the 16 runs (all exit 0).

### Replication (same job) — every untouched lane reproduces 263/264 to the decimal

| lane | this job | ticket baseline | |
|---|---|---|---|
| P03 CTL Bl0 / Bl1 | 0.72/97.8 % (225) ; 0.98/52.8 %/1j (358) | 0.72/97.8 ; 0.98/52.8/1j | match |
| P03 VOTE Bl0 / Bl1 | 0.58/100 % (228) ; 8.69/11.0 %/21j (4328) | 0.58/100 ; 8.69/11.0/21j | match |
| P03 GATED Bl0 / Bl1 | 0.58/100 % (228) ; 0.99/78.2 %/3j (403) | 0.58/100 ; 0.99/78.2/3j | match |
| P03 FULL Bl0 / Bl1 | 0.52/100 % (216) ; 3.18/41.9 %/1j (463) | 0.52/100 ; 3.18/41.9/1j n=463 | match |
| P03 G3 / G5 / G8 (re-run fresh) | 4.00/42.2 % ; 3.58/41.9 % ; 3.24/42.3 % | 4.00/42.2 ; 3.58/41.9 ; 3.24/42.3 | match |
| P22 Bl0 / Bl1 | 0.69/87.7 % ; 0.57/95.1 % | 0.69/87.7 ; 0.57/95.1 | match |
| P01 Bl0 / Bl1 | 0.75/98.8 % ; 0.98/95.4 % | 0.75/98.8 ; 0.98/95.4 | match |

### Verdict lines

1. **The 122.846 / 124.590 mm step is the walk's terminal closure step, not a mid-walk departure** — the rim loop is already welded at 0.761 mm when it fires, and it exists only to collect one deferred genuine rim dot (1.876 mm off the rim at 56 % of the walk, 1.208 mm off the author's line) before the implicit 124.773 mm wrap back to the start. **No ordering rule was built**, per the ticket's STOP CONDITION, and none would help: a step-length guard fires exactly once, at the only step whose K=50 list has zero fresh candidates, so it can only keep the step or drop the dot.
2. **The gate has no usable window on P03-Bl1**: ≤ 8 mm removes genuine rim (76/62/53/43/15 dots, all from the 3.512–8.744 mm arc), ≥ 10 mm removes nothing at all. Genuine off-surface dots in this bag: **0**. The pre-registered rule is unsatisfiable here, and every clean lane is unchanged at both candidate rungs.

### Artifacts and provenance

- Figures (laptop): `C:/PR/SfSpp_preprocessing-248/artifacts/pota266_walk_order_P03_Bl1.png` (1045-dot comp, 122.846 mm; md5 `7e1cdf3d3daa0d8d3b8c64ccc7da89dc`, 311633 B) and `..._1121.png` (unfiltered bag, 124.590 mm; md5 `24f92345c6a72a45e344176e6f53ae0d`, 312768 B). Spartan: `/data/gpfs/projects/punim2657/sfs-vote-248/pota266/` with `leap.log`, `leap_summary.json`, `gate.log`, `gate_summary.json`.
- Figure legend: whole walk in visit order coloured by step index, leap in red, the implicit closure wrap in magenta dashed, walk start ○ / last rim dot ▢ / landing ★, per-step gap on a log axis, the 12 steps around the leap as bars, a zoom at the leap, and X-Z / Y-Z views against the author's breakline. The zoom's caption box slightly overlaps the chord — cosmetic only; every number in it is repeated in this comment.
- Job: **33709589** `potD266b`, sacct `COMPLETED 0:0 00:05:27 spartan-bm167`, 16 lanes + instrument + scoring in one submission (`potD266b-33709589.out`). Predecessor **33709330** `potD266a-leap` (`COMPLETED 0:0 00:01:05`, spartan-bm174) established the 10 mm/24 mm identity lanes (`kept 1121/1121`).
- Scripts (untracked, Spartan + laptop): `pota266_leap.py` md5 `84ee17891dd09060b7261da198dc99ef`, `pota266_gate.py` md5 `970740729ef66f591650ff7dc7bb1816`, `pota266_score.py` md5 `b43bc9e8016cc8223c946153f938a1ce`, `run266b.sbatch` md5 `fa04991c723418d6576d0cd03217ab6e`.
- No source diff, no rebuild, nothing committed. New temp trees, all owned by this ticket: `pota266_P03_G{3,4,5,6,8,10,14,20,28}`, `pota266_P03_CTL{,G3,G8}`, `pota266_P22_G{10,28}`, `pota266_P01_G{10,28}`.
- Instrument caveat: the offline reconstruction of the gate's reference loop is not bit-exact (turnSum 44.980 vs the binary's 44.805, L 8694.550 vs 8694.96 mm — 0.005 %), so the distances are cross-checked the strong way instead: replaying the gate at 3/4/5/6/8/10/14/20/28 mm reproduces the binary's own `kept` counts **exactly** at all nine rungs (1045/1059/1068/1078/1106/1121/1121/1121/1121), so the measured arc distances agree with the shipped gate to within one rung transition.
