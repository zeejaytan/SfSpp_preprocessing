# Make the input seat: author-vs-ours C01 bundle diff

GOAL: THE UNTOUCHED ASSEMBLER SEATS C01 -- BY CHANGING ONLY THE INPUT.

**Answers:** E1

**Blocked by:** 177 (C01 dies upstream of scoring; C_176 generates 40 total vs C_orig 125 -- the input difference already shows at generation), 176 (439-dot TRUE walk, staged bundle), 145 (CSXC rims + author G0).

**Status:** ready-for-agent

**User ruling (2026-10-20):** the assembler SFS++ is proven and is NOT touched. Only the input changes to match. 178 (instrumented assembler run) stopped for this reason.

**Standing evidence (do not re-derive):** author rims seat 4/4+5/5 in the same vehicle; our 439-dot rim (med 0.95 vs author) generates only 40 hypotheses vs author's 125. Same geometry, different generation -- the difference is IN THE INPUT FILES.

**What to deliver (laptop-side, no Spartan, no assembler changes):** (1) Field-by-field diff of the installed bundle inputs for C01-Bl_0: author G0/CSXC version vs our 439-dot TRUE-walk version -- headers, flags, counts, ordering, spacing uniformity, normals/curvature channels, slot arrangement, every field the assembler reads. (2) Name the input feature(s) that differ AND plausibly gate LCS generation (feature_matching.cpp:1473 inputs: quantized D/H/Theta, curvature -- which input fields feed them?). (3) Propose the preprocessing-side change that makes our input match the author's on that feature, with a numeric prediction (e.g. reformat X -> generated count moves 40 toward 125). STOP at the proposal; the bundle rebuild + E2E is a follow-up.

**Bar:** the differing input feature named with side-by-side numbers, the preprocessing change specified, prediction numeric. No assembler source touched, no instrumented assembler build.

**Rules:** dataset read-only; tickets 39-178 read-only (178 superseded by this ruling); edit this ticket's Comments section ONLY; COMMIT NOTHING.

- [x] Author-vs-ours C01 input diff
- [x] Gating feature named with numbers
- [x] Preprocessing-side change + prediction
## Comments (worker, 2026-10-20 -- INPUT DIFF, no E2E, no assembler touch; COMMIT NOTHING)

**Status: results-in. Gating feature named with side-by-side numbers + preprocessing change + numeric prediction below. Assembler checkout never entered (not even read); vehicle/builds used as read-only numbers from 145 s1 / 176 s7 / 177 s6 only.**

**0. Inputs compared (all laptop-side, dataset + tickets 39-178 read-only, zero bytes modified).** Author side: (i) author ORIG C01-Bl_0 = artifacts/pota26/pota26_fetch/rims_orig/Pot_C_Piece_01_Breakline_0.pcd (211 pts; the ORIG family that seats 4/4+5/5 per 145 s1: C_orig 125 total / 40 pruned); (ii) GT_C poses + P145_C_orig.txt (125/40) / P145_C_FIN.txt (45/8) from .scratch/pota177_repro/fetch145/ (145 fetch tgzs); (iii) 177 s6 lead check: C_176 40 total / 8 pruned, survivors exact. Ours side: (i) installed 176 C01-Bl_0 reconstructed from staged .scratch/pota176_repro/p176_build.py + 176 s7 lead patches (inverse-T mesh frame, G0 author-normal donor, 13 segs rescaled 402->439, xyz = p176_C01_TRUE_walk.npy 439 dots md5 5f902355dd99a4fe35885bf596193733) -- the installed file itself is Spartan-side (no SSH from this worker); xyz/channel numbers below are laptop-side exact. (ii) CSXC FIN C01-Bl_0 (rims_CSXC, 310 pts, 45/8) as second ours-regime control; fresh C01-Bl_0 (.scratch/pota176_repro/inputs/, 402 pts) as donor baseline.

**1. Field-by-field C01-Bl_0 diff (author ORIG vs ours-176-installed; FIN/CSXC as control).**

| # | field | author ORIG | ours 176 | control FIN/CSXC |
|---|---|---|---|---|
| 1 | header (# nseg npts info) | 5 211 0 | 13 439 0 | 13 310 0 |
| 2 | segment flags | 5/5 flag 0: [1-30][31-97][98-108][109-176][177-211] | 13 segs rescaled 402->439, all flag 0 (exact bounds Spartan-side) | 13 segs, all flag 0 |
| 3 | PCD schema | VERSION/FIELDS/SIZE/TYPE/COUNT/WIDTH/HEIGHT/VIEWPOINT/POINTS/DATA ascii; FIELDS = x y z normal_x normal_y normal_z curvature | identical schema | identical |
| 4 | count | 211 | 439 (2.08x) | 310 |
| 5 | ordering | single ordered loop, 0 zero-steps, closure 1.80mm (~1 step, CLOSED) | walk order, 2 zero-length signed-zero steps, closure 17.67mm (OPEN) | 8 zero-steps (dup rows), closure 20.42mm |
| 6 | spacing | max 1.97 / med 1.80 / n>5mm 0 -- uniform | max 14.77 / med 1.36 / n>5mm 3 -- gappy | max 35.37 / med 3.15 / n>5mm 88 |
| 7 | arc length | 380.0mm single lap | 691.4mm (1.82x -- out-and-back doubling, cf. 176 s4b) | 1393.5mm |
| 8 | normals | unit exact (1.0000), smooth author field; installed-176 = G0 author donor (176 s7b) -> MATCHES author | matches author by donor | fresh-NN donor (differs; yet tally 45~=40, see s2) |
| 9 | curvature raw | constant 1.9058e-42 all 211 rows (also all 230 Bl_1 rows) | donor: fresh-family varying 0.002-0.34, or G0-constant if lead switched all 4 cols (Spartan-side) | varying 0.002-0.176, nuniq 169 |
| 10 | curvature @ quantum 0.2 | 211/211 in bin [0,0.2) | EITHER branch -> ~all in bin [0,0.2) (fresh donor 400/402; G0 439/439) | 310/310 in bin [0,0.2) |
| 11 | slots | slot 0 = Bl_0 (211); slot 1 = Bl_1 (230 pts, 7 segs, info 1, one flag-1 seg #202-219) | slot 0 = Bl_0 (439); Bl_1 untouched = fresh 92 pts / 4 segs / info 0 / all flag 0 | same as 176 (ONLY Bl_0 differs vs 98-SXC) |
| 12 | quantized-D alphabet, 0.15 bins (laptop proxy) | 3 distinct tokens (bins 11,12,13); top-2 = 109+100 of 210 steps; longest run 4 | 34 distinct tokens; top-3 = 40+33+30 of 438; longest run 2 | 74 distinct; longest run 4 |

Tallies: author 125 total / 40 pruned -> 4/4+5/5; FIN 45/8 -> 2/3+1/3; 176 40/8 -> 2/3+1/3 (177 s6: survivors exact, total off by 5).

**2. Gating feature (single): the ordered xyz polyline as an LCS token source -- uniform closed single loop (author) vs doubled gappy open walk (ours).** Side-by-side: author 211 pts / 380mm / closed (1.8) / 0 gaps / 3 D-tokens with 209/210 steps in two adjacent bins -> quantized D/H/Theta runs match everywhere -> 125 generated, 40 survive pruning, C01 among them (4/4+5/5). Ours 439 pts / 691mm / open (17.7) / 3 gaps>5 (max 14.8) / 34 D-tokens with longest run 2 -> token runs fragment at every gap and doubling -> 40 generated (-5 vs FIN, survivors exact), 8 survive, zero C01 placements reach scoring (177 mechanism stands). Ruled OUT numerically: curvature (row 10 -- every version collapses to one 0.2-quantum bin, so it cannot discriminate at the stated quantum); normals (row 8 -- FIN fresh-donor 45 vs 176 G0-donor 40, same band); schema/slots (identical). Segment-table shape (5 vs 13) held UNPROVEN -- FIN and 176 share 13 segs yet both sit at ~40-45, so segs do not explain the 125-vs-40 contrast; not part of the proposal. Caveat owned: the D-quantum/LCS mapping is a laptop-side proxy (assembler never opened per ruling); the tally contrast it predicts (rich vs starved generation) is vehicle-measured (125/40 vs 45/8 vs 40/8).

**3. Preprocessing-side change (no assembler touch) + numeric prediction.** Change (all in the walk->pcd writer, i.e. a p176_build.py successor staged like 176 s5, login-node numpy only, no binary rebuild): (a) de-double the TRUE walk to one strand (per-bin single-track rule; 175 s4 floor-proof family) -> arc 691->~380mm; (b) uniform arc-length resample at 1.80mm -> n~=211; (c) close the loop (closure <=2mm), drop zero-steps, zero gaps>5mm; (d) hold channels fixed (G0 normal donor, existing curvature donor) and hold the 13-seg rescale machinery (mechanics only). Net: our xyz becomes author-regime (211/uniform/closed/single) with our provenance. Prediction for the next C_176-class run: Total number 40 -> 100-125 band (author 125), pruned 8 -> 30-40 band (author 40), C01-involving pairs >=1 pruned survivor (177-P2 flips 0->=1), C01 seated (edge count 1/3->=2/3). Falsifier: Total stays ~40 -> the gate is NOT the D-alphabet (H/Theta or segment windows instead) and this proposal is refuted -- the number decides, no further input-side iteration without new evidence. STOP per ticket: bundle rebuild + E2E is the follow-up.

**4. Evidence.** Analysis scripts /tmp/p179_diff.py + /tmp/p179_dtok.py (outside repo, rerunnable; repo untouched -- dataset + tickets 39-178 read-only, COMMIT NOTHING, assembler repo never entered).


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
