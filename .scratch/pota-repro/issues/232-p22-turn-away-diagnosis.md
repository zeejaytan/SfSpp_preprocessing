# Ticket 232: P22 turn-away diagnosis (split-plan check + divergence point)

Status: done

## Lead verdict (2026-10-22)
BRIDGE-OPENS-AT-3 accepted with one grading correction. R6: jobs 33613082/33613083 sacct COMPLETED 0:0; report internally consistent (turn dot coords -> walk-order distances -> fork angles -> ladder table cohere); evidence dirs on disk. CORRECTION: @3 (symmin 0.837, UN ~29%) still fails R6 (TOUCHING + UN) -- it is NOT a selectable stop; what opens at 3 is the FORK touch specifically (fork zone S1-only, 0 S0 dots; frac<2mm 13.4%->1.1%). The user's break-further rule is vindicated in direction; the usable fix is bridge-cutting/keep-list at ~3-class tightness, not selecting @3. Also: the walk EXECUTED the 81.3deg turn (user's 70-80 eye-witness confirmed to the decimal) and stopped at boundary exhaustion, riding a stronger crease (45.8->52deg) than the rim -- starvation, not a turn limit. Mechanism: tab-top bridge joins the faces ~6mm above the lane end; tab far side never filed. Only this ticket touched among tracked.
Answers: none (Pot D bridge class; feeds the R6-rule 4th-leg hole + bridge-class record)

## Goal
Two ordered questions on Pot D Piece 22, whose 221-kept lanes are stubs (o0 med 3.37/cov 32.5, o1 med 2.70/47.2, slot-corrected; zoom: C:/PR/SfSpp_preprocessing/.scratch/pota228/p228_P22_zoom_ours.png):
1. SPLIT-PLAN CHECK: is the author's line cut right on the edge of our 2 surface planes? (i.e. the split is correct and only the walk failed). Method: the 229 sharpness instrument (baseline/line/control triple, ticket 229 Comments) applied to author-lane dots vs the S0/S1 ladder faces (221 thr_* dirs on Spartan) + dense ORIG cloud. Verdict SPLIT-OK (author on-edge) or SPLIT-OFF (author mid-surface).
2. TURN-AWAY POINT: the exact dot where our trace leaves the author line (first our-dot >2mm from either author lane that never returns), its coordinates, and what is special about that point -- test in order: (a) S0-S1 bridge touch there (symmin gap ~0 at that spot, 222 method); (b) segmentation cluster boundary (segmentationStats.txt, 220/221 method); (c) boundary-bag hole (no input dots within r); (d) sharpness collapse (229 instrument at that dot). ONE named feature with a measurement, not a list.

## Boundary
Spartan read-only + compute on existing faces/clouds; may re-run edge ONLY on transplanted faces (223 pattern) if the walk must be re-observed -- no segmenter changes, no new thresholds. Do not touch: main worktree, cure branches, .scratch/pota228 renders (read them, don't overwrite), any ticket but this one.

## Constraints
Q1 before Q2 (if SPLIT-OFF, Q2's premise changes -- report that instead of forcing Q2). Slot-verify before grading (231 amendment: P25 gate-table misread). Numbers with coordinates, not adjectives.

## Acceptance criteria
- [ ] Q1 verdict SPLIT-OK / SPLIT-OFF with the sharpness triple + control
- [ ] Q2: divergence dot index + coordinates + the ONE special feature measured
- [ ] One picture with the turn marked (gold author, blue ours-on, black ours-off, red ring on the turn dot)
- [ ] Verdict line: TURN-AT-<feature> / SPLIT-OFF / NEED-<named thing>

## Required evidence to report
Sacct COMPLETED for any Slurm; face/cloud md5s or paths; the triple numbers; the turn coordinates + feature measurement; PNG path. Self-contained report in ticket Comments; leave Status for the lead.
## Comments (worker 232, 2026-10-21/22. NO main commit; NO branch; job-free -- no Slurm, no sacct; Spartan read-only + login-node-free local compute on fetched copies; .scratch/pota232/ + artifacts/pota232/ new, this ticket only)

### Verdict: TURN-AT-S1-UN-BOUNDARY (SPLIT-OK; walk starved past the corner, not a walk bug at the corner)

### Slot-verify FIRST (231 amendment -- premise mismatch flagged)
- Slot matrix vs author (n: our b0=40, b1=53; auth o0=133, o1=162; cov = share <2mm): b0->o0 4.90/17.5, b0->o1 3.61/32.5; b1->o0 4.95/22.6, b1->o1 3.37/39.6. Straight (b0->o0,b1->o1) med-sum 8.27 vs swapped 8.56 -- straight wins by 0.29; both our lanes sit nearer o1.
- 221's per-lane numbers reproduced EXACT (b0->o1 3.61/32.5, b1->o1 3.37/39.6). Ticket premise (o0 3.37/32.5, o1 2.70/47.2) NOT reproduced -- 2.70/47.2 appears nowhere in my matrix; closest is b1->o1 3.37/39.6 + b0->o1 3.61/32.5. Graded against my matrix, not the premise.

### Q1 SPLIT-OK (229 instrument, pre-registered line)
- Instrument S(p) = deg(acos(|mean unit normal|)) over dense-cloud pts within r=2mm (229 Comments verbatim). Dense cloud sfs-potD-214/Dataset_Input/Point/Pot_D/Pot_D_Piece_22_Point.pcd (180966 pts with normals, md5 1bc7359e2b5a10401eb98cfc96d0dd43, fetched to artifacts/pota232/).
- Baseline (600 sampled cloud pts >6mm from any lane dot): med 3.98. Decision line = baseline+15 = 18.98.
- Control (b1 idx35-46 on-rim stretch, 12 dots + 12 unique nearest author dots): ours med 33.44, author med 33.58 -- both >> line. Control PASSES, instrument not blind.
- Author lines: o0 med 26.43 (78.2% of 133 dots >= line), o1 med 35.76 (90.1% of 162 >= line). Both author lanes read crease at control level -- the author's line sits ON the edge of our surface planes. SPLIT-OK; the split is correct, only the walk failed. (Ours for reference: b0 35.63, b1 35.13 -- also crease: the stubs ride real edges.)

### Q2 turn-away dot: our b1 idx48 at [-4.15, 18.58, 439.21]
- Walk-ordered dist-to-either-author-lane for b1 (53 dots): idx46 0.2, idx47 1.27 (last on-rim), idx48 2.78, idx49 4.31, idx50 5.93, idx51 7.03, idx52 7.91 -- idx48 is the first >2mm dot that never returns (49-52 all stay off, lane ends at 52). Affinity while on-rim: o1 (idx35-47 all nearer o1, d 0.2-1.3).
- Context: b0 (40 dots) leaves the rim twice (idx1-13 east jump, idx17-30 excursion peaking 7.8 at [22.01,3.90,431.59]) but RETURNS both times (idx31-39 all <1.0, ends on-rim) -- bridge-zone wandering, no permanent turn. The permanent turn-away is b1-only.

### Ordered tests at the turn (ticket order a-d + steering refocus)
- (a) S0-S1 bridge touch AT the spot: NO. P22@12 symmin = 0.00, but the touching pairs are at [-7.69, 18.44, 448.19] (9.65mm from turn) and [35.83, 17.52, 447.56] (40.86mm) -- tab-top region, not at the dot. (Faces: thr_12 S0 c5d8bc4104931373e65ac04c01904f47 10796 pts / S1 4a9d5c327f86062bfa794e48a5aac31 14262 pts; P25 thr_12 files md5-identical = known poisoned copies, P22 originals valid.)
- (b) Segmentation cluster boundary: YES -- THE feature. Turn dot: dS1 0.66mm, dS0 4.72mm, dUN(nearest unclustered dot) 0.04mm -- the turn dot coincides with an unfiled dot exactly at S1's filed edge. Along the author's continuation, the filed S1 boundary ends at the corner: boundary within 1.8mm of o1 up to idx134 ([-0.53, 20.41, 437.56]), then 3.5mm at idx135, 5.1 at 136, growing to 13.3 at idx148. Past the corner only UN dots are filed.
- (c) Boundary-bag hole: NO. 493 dense-cloud dots within 2mm of turn (2550 around the 5 excursion dots); 1175 S1 + 548 S0 dots within 10mm. Input and faces both exist there.
- (d) Sharpness collapse at the dot: NO -- opposite. S(turn) = 45.8deg (above control 33.4), rising along the excursion to 52.0 at lane end. The walk left the rim riding a crease stronger than the rim itself.
- Steering refocus (70-80deg sharp turn at BLUE line): measured 81.3deg turn at b1[47] (w=1; 87.3 at w=2; author corner 98.2 at o1 idx130, 3.7mm away) -- the walk EXECUTED the sharp turn and walked 5 more dots, so no angle-limit stop. Boundary-bag gap at corner: NO (S1 206-pt filed bag, max nearest-neighbour spacing 1.03mm global / 0.84 near corner; dense, duplicates aside). Stop = boundary exhaustion: lane end b1[52] [-9.72, 20.95, 442.9] with filed boundary dots to ~1.3mm past it ([-10.41, 21.05, 443.99], [-10.88, 21.56, 443.93]) then nothing -- walked the boundary to its end. Mechanism: splitter starved the walker (tab-top S0-S1 bridge at [-7.69, 18.44, 448.19] joins the faces ~6mm above the lane end; tab's far side never filed into S1's boundary) -- fix belongs to the splitter (keep-list/bridge-cutting), not the walk.

### Fork addendum (user eye-witness refinement 2: rim-vs-break fork, 67 face-hop family; ticket-69 heading-guard as alternative fix)
- Both continuations exhibited. Rim (author o1 through/after corner): o1[130] [-1.25,15.73,440.67] -> o1[134] [-0.53,20.41,437.56] (rim-through dir [+0.72,+4.68,-3.11]) -> o1[138] [-2.44,24.04,443.18] (tab-up dir [-1.91,+3.63,+5.62]). Break (our b1): fork b1[47] [-2.77,18.05,438.19] -> b1[52] [-9.72,20.95,442.90] (break dir [-5.57,+2.37,+3.69]).
- Angles: walk's kink AT the fork (arrival b1[46]->[47] vs departure [47]->[48]) = 81.3deg single-step (87.3 w=2) -- the user's 70-80deg. Break vs rim tab-up = 35.9deg over 5 dots, separating 2.78mm -> 7.91mm from o1. Rim's own corner = 98.2deg at o1[130]. Arrival vs rim-through = 57.8deg (walk paralleled the rim ~1mm off, converging).
- Membership (S1/S0/UN @12 nearest-dist per dot): rim continuation o1[133..140] all nearest S1 (dS1 0.06-0.30, dS0 ~5.4, dBnd 1.8 -> 9.4); break b1[48..52] all inside S1's filed envelope (dS1 0.38-0.67, dS0 4.7-5.4, dBnd 0.14-0.68, dUN 0.04-0.45). Rim dots AND break dots SHARE the S1 splitter cluster.
- No fork in the walker's input: 17 filed-boundary dots within 4mm of fork form ONE line (PCA var 0.98/0.02/0.00, uniform hist [3,4,2,2,2,4]) -- single boundary line runs rim -> corner -> break edge; no branch toward the tab was filed. Whole-bag walk (S1 bag=206, 1 comp, no ring, K=20) followed the only line it had.
- Decision (steering rule): SHARED-CLUSTER => SPLIT-FAILURE. The splitter filed break-edge + face into S1 (tab-top S0-S1 bridge at [-7.69,18.44,448.19] joins the faces ~6mm above the lane end; tab far side never filed into S1's boundary). Fix = splitter-side (keep-list / bridge-cutting family). Walk heading-guard (ticket-69 line) would NOT cure: at the 81deg kink a heading guard can only STOP the walk (no filed boundary up-tab to redirect onto) -- it converts a wrong-branch lane into a shorter stub, same below-bar coverage. Different-faces (walk-failure) REFUTED by the membership table.
### Below-floor ladder addendum (user verdict: NOT-face-hop-but-BRIDGE; 224 pattern, fresh dir sfs-fix-232, 221 binaries byte-identical)
- Jobs (sacct COMPLETED 0:0): mesh+edge P22 single-piece @3 = 33613082 (10s, 11 clusters), @2 = 33613083 (12s, 28 clusters). Binaries md5-verified in both job logs (Mesh 9a0386f54b0ecc70605f9f26371a789e, Edge dc472b0e87c934b6c487ff8637209864). Input cloud md5 1bc7359e2b5a10401eb98cfc96d0dd43 == fetched P22_Point.pcd. Trees landed as pota224_edgeP22_3/_2 (sbatch TREE name kept 224 prefix; content is P22 @3/@2 -- naming wart only). No code changed, no other paths touched.
- Touch-IS-fork check (@12 walked faces): 1522 S0 dots <2mm from S1 (face-wide background), but 15 contact mids within 5mm of the turn dot, nearest zero-gap mid [-2.70,16.14,442.97] 4.71mm from turn (fork b1[47] 4.91mm). Contact reaches the fork zone: CONFIRMED (within ~3 dots of sampling).
- Gap-vs-angle (filed Surface_0 <-> Surface_1, numpy-chunked both-directions on Spartan):

| stage | clusters | top2% | S0 | S1 | UN | symmin | p1 | p50 | frac<2mm | fork-zone (<5mm turn) contact |
|---|---|---|---|---|---|---|---|---|---|---|
| @12 | -- | -- | 10796 | 14262 | -- | 0.000 | -- | ~3.7 | 13.40% | 15 mids, nearest 4.71mm |
| @8 (231 cite) | -- | -- | -- | -- | -- | 0.00 | -- | -- | -- | -- |
| @4.5 (231 cite) | -- | -- | -- | -- | -- | 0.17 | -- | -- | -- | -- |
| @3 | 11 | 43.6 | 10004 | 11278 | 8855 | 0.837 | 1.97 | 3.98 | 1.10% | ZERO (0 S0 dots in zone; 85 S1 dots: S1 owns fork alone) |
| @2 | 28 | 14.1 | 6353 | 2282 | 12078 | 0.000 | 0.00 | 18.66 | 9.92% | ZERO at fork (both faces absent); the 0.000 pair sits 29mm away at [18.8,15.39,421.79] -- new fragmentation contact, not the fork bridge |

- Verdict: BRIDGE-OPENS-AT-3. The fork touch opens at threshold 3 (min 0.84, p1 1.97, fork zone single-face S1). @2 re-touches to 0.00 elsewhere while the faces shatter (S1 11278->2282, top2 14.1%, UN 65.7%, fork zone unfiled by either face) -- P12-NONE-class persistence-by-fragmentation, not a usable opening. Splitter fix direction stands: keep-list/bridge-cutting at ~3-class tightness separates the tab faces; going tighter destroys them.
### Picture (eye-checked by worker)
- .scratch/pota232/p232_P22_turn.png -- full + corner zoom, gold author / blue ours-on-rim / black ours-off-rim / red ring on b1 idx48. Lane-only overlay (no Pot D P22 mesh on laptop; .wt-217 absent -- stated, 228-P27 pattern).

### Paths & provenance
- Spartan (read-only, untouched): pota221_ladder/thr_{12,14,10}/ (S0/S1/UN sizes logged), pota221_edgeP22_12/ (edge_12.log: S0 bag=117/comps 111-5-1/K=11, S1 bag=206/comps 1/K=20, whole-bag walks, cuts @77/110/111/116 and @121/191; faces Transplanted? No -- native edge run, md5s above), Temp/Temp_edge/Pot_D/boundary.pcd (206-pt S1 filed bag) + Segments/{1,2}.xyz (walk-ordered).
- Fetched (md5-verified where dual-checked): artifacts/pota232/ (cloud 10.7MB, S0/S1 @12/@14/@10, UN @12/@14/@10, boundary, segs). Scripts: .scratch/pota232/{slot_div,coords,q1q2,q2b,q2c,q2d,final_nums,render232}.py.
- No Slurm submitted (all compute local numpy/scipy on fetched copies) -- no sacct to report.

