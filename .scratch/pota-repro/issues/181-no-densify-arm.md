# No-densify arm: pre-densify edgeline gated, then assembled

GOAL: TEST WHETHER THE DENSIFY STEP IS NEEDED AT ALL -- PRE-DENSIFY EDGELINE THROUGH THE SAME ASSEMBLY.

**Answers:** E1

**Blocked by:** 134 (M134d walk: 290/278u, gate 4.2488, uncovered 8 on the 282-bag = last pre-densify best), 145 (CSXC rims, GT_C, 98 bar), 176 (relay pattern: staged build + sbatch, lead relays), 180 (single-loop dense arm -- runs in parallel, neither waits; compare tallies).

**Status:** ready-for-agent

**User theory (2026-10-20):** roll back the densify change; check whether a good edgeline is still maintained; then assemble again.

**User ruling carries:** assembler NOT touched. Input only.

**What to deliver:** (1) Take the pre-densify C01 walk (M134d family on the 282-bag, no 143/146 densified dots): gate it vs author exactly as 176 s1 did (coverage/med/<2mm). State plainly whether the good edgeline is maintained without densify. (2) If gated good (within ~1mm of 176's 0.95 med): build the C bundle with ONLY C01-Bl_0 from this walk (others bit-identical to 176, md5 proof), stage build + sbatch in .scratch/pota181_repro/ for lead relay, x3 + same-binary ORIG control. (3) If gated bad: stop, own the numbers -- theory refuted, no E2E.

**Bar:** gate numbers side-by-side with 176 (0.95 med) + 179's input features (n, arc, closure, gaps, D-tokens) for the pre-densify walk; then either staged E2E or honest refutation. No re-tuning to chase the gate.

**Rules:** dataset read-only; relay worktree pattern only, production checkout never touched; COMMIT NOTHING; tickets 39-180 read-only; edit this ticket's Comments section ONLY; NO assembler changes.

- [ ] Pre-densify C01 walk gated vs author
- [ ] Verdict: maintained or refuted with numbers
- [ ] If maintained: bundle staged for relay (x3 + controls)

## Comments (worker, 2026-10-20 -- laptop numpy only; COMMIT NOTHING)

**Verdict: REFUTED -- the pre-densify edgeline is NOT maintained without densify. No E2E staged, no bundle built, per ticket falsifier rule.**

**0. Controls GREEN (reproduce-or-stop equivalent).** Bag rebuilt from parts: guarded-270 + 124-admit-8 + 128-admit-1 + 133-admit-3 = 282, rebuild-equals-stored True -- the 282-bag carries NO 143/146 densified dots. M134d seq loads seqlen=290 unique=278 (matches 134 file). Author reference via the 176-s1 recipe verbatim (C01 ORIG Bl_0 + Pot_C_Piece_1_T seated): maxdev 0.000000 vs 134's OG -- same frame, head-to-head is exact. Recomputed gate matches p134_walk_d.txt to all digits (290/4.2488/29.3%/98/25.8/99/8). D-token proxy validated on the author loop first: exact reproduction of 179 row 12 (3 tokens, bins 11/12/13, top-2 109+100 of 210, longest run 4, arc 378.2mm, closure 1.80mm). Zero ORIG points copied (ORIG = gate-evidence only); dataset read-only; tickets 39-180 untouched; nothing committed.

**1. Gate vs author, 176-s1 recipe (coverage/med/<2mm), side-by-side.**

| walk | n | med (walk->ORIG) | <2mm (walk-side) | ORIGcov (of 211) | gaps>5 | maxstep | uncovered |
|---|---|---|---|---|---|---|---|
| author ORIG (179) | 211 | -- | uniform 1.80 | 211/211 | 0 | 1.97 | 0 |
| 176 TRUE walk (s1) | 439 | 0.9492 | 92.0% | 211/211 | 3 | 14.8 | 0 |
| **M134d pre-densify (this ticket)** | **290 (278u)** | **4.2488** | **29.3%** | **99/211 (46.9%)** | **98** | **25.8** | **8** |

Gap to the bar: med +3.30mm over 176's 0.95 (bar allows ~1mm); ORIG-side coverage less than half the ring (99 vs 211). The 134-lane gate (4.2488<=4.3107) holds on its own terms, but the edgeline it certifies is 3.3mm off the reclaimed-rim line -- it beats the 133 probe, not the author.

**2. 179 input features for the M134d walk (as-sequenced 290 rows, bag frame -- all rigid-invariant).**

| input | n | arc | closure | gaps>5 | D-tokens (0.15 proxy) |
|---|---|---|---|---|---|
| author ORIG | 211 | 378.2mm | 1.80mm (closed) | 0 | 3 (bins 11,12,13; run 4) |
| 176 ours (179) | 439 | 691.4mm (1.82x doubled) | 17.67mm (open) | 3 | 34 (run 2) |
| **M134d pre-densify** | **290** | **1361.0mm** | **20.42mm (open)** | **98** | **73 (top-3 bins 14/33/20 with 15/14/13 steps; longest run 8)** |

Read: the pre-densify walk is 3.6x the author arc (retreat re-treads + 98 jumps, 2 steps over 25mm), closes 20mm open, and fragments the LCS token source into 73 bins -- strictly worse than the already-starved 176 input (34 tokens, 40 generated vs author's 125) on every 179 feature. Spacing med 3.50mm vs author 1.80mm; 1 zero-step (index re-tread coincidence).

**3. Decision.** Bar requires ~0.95-med-class edgeline to justify a bundle + 3x E2E relay. M134d is not in that class on any of the six head-to-head numbers, and its token alphabet (73) predicts generation at-or-below the 176 arm's 40 -- feeding it to the assembler would re-run a known-starved regime, not test the user theory. So: theory refuted for this walk family, no sbatch staged, .scratch/pota181_repro/ holds only the gate evidence (p181_gate.py + p181_gate.txt). The densify step (143/146 dots) stays load-bearing for C01: post-densify M144 filed 310 pts at med 3.97 with uncovered 0 (145), and the reclaimed-rim 439 walk holds 0.95 -- both built on dots the 282-bag does not have.

**4. Evidence.** Laptop .scratch/pota181_repro/p181_gate.py (rerunnable; repo + dataset + tickets 39-180 read-only) + p181_gate.txt (this section's numbers); render eye-checked: artifacts/pota134/p134_walk.png (recovery-290 chains the arc with long chords; DO panel: 8 uncovered spans). No relay worktree touched, no binaries built, COMMIT NOTHING done.
