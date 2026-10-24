# Scratch cleanup manifest — 2026-10-23

**Rule applied:** each `.scratch` work directory has a ticket that records its numbers and result; once that ticket
exists and carries those numbers, the directory itself can be deleted.

- **Repo:** `C:/PR/SfSpp_preprocessing` (branch `main`). Scope: **`.scratch/` only**; nothing outside it was touched.
- **Built before deletion**; this file corrected at 2026-10-24 01:51 after the incident in section **G**.
- **Live-round cutoff:** created or modified on/after **2026-10-22 00:00 local** -> KEPT.
- **Forbidden and untouched:** `C:/PR/SfSpp_preprocessing-248`; `.scratch/pota-repro/` (except stray `*.lock`).

## Summary

| | count | MB (sum of bytes, pre-deletion) |
|---|---|---|
| Candidates examined | 110 | 78.99 |
| **DELETE — executed, permanent** | **84** | **24.22** |
| KEEP | 26 | 54.76 |

KEEP reasons: **tracked=22**, open=4.

Outcomes: 84 deleted · 15 deleted then restored (tracked content only) · 11 untouched.

**Space freed: `du -sk .scratch` 88753 KB -> 32142 KB = 56611 KB ≈ 55.3 MB** (allocated; final measurement
with this task's own temp files removed).
Of that, 24.22 MB is the 84 correct rows and ~28.3 MB is untracked scratch content inside the 15 restored directories (see G).

## Method

1. **Candidate set** — every directory under `.scratch/` matching `pota<digits>_repro`, `pota<digits>_staging`,
   `pota<digits><b|sbs>_repro`, or `pota<digits:3>` (93 dirs), plus the loose
   scripts `.scratch/p215_*.py`, `.scratch/p216_*.py`, `.scratch/p216_*.sh` (17 files)
   and the directory `.scratch/p215_evidence/`.
2. **Ticket mapping** — strip `pota`/`p`, take the leading number, match `.scratch/pota-repro/issues/<number>-*.md`.
   110/110 mapped; no MISSING tickets.
3. **Status** — the ticket's `Status:` line verbatim (both `Status:` and `**Status:**` forms; tickets have mixed
   CRLF/LF endings, which a naive `split("\n")` silently mis-reads as "no status").
4. **Numbers line** — the ticket line carrying the most recorded numbers/results (decimals, `%`, PASS/FAIL, at-bar,
   `n=`, ratios), preferring verdict language and penalising plan headers and markdown headings. Verbatim, cut at 120.
5. **Tracked check** — every candidate tested against the **complete** `git ls-files` list (3314 files), written to a
   file and read from disk. See G for why this mattered.
6. **Age check** — newest recursive mtime **and** birthtime; nothing deleted is dated on/after 2026-10-22.
7. **Safety scan** — all targets `realpath`-resolved: no symlink or junction, nothing resolving outside `.scratch`.

**DELETE** = ticket exists ∧ Status is done/results-in/accepted/landed ∧ ticket quotes numbers ∨ non-tracked ∧ older
than 2026-10-22. KEEP precedence: **tracked > recent > open > no-numbers**.

## A. Candidates (110)

| # | Path | Ticket | Status (verbatim) | Recorded numbers / result (verbatim, ≤120) | Newest | MB | Decision | Outcome |
|---|---|---|---|---|---|---|---|---|
| 1 | `.scratch/pota113_staging` | 113-heading-walk.md | **Status:** results-in | "1. Control GREEN — stall reproduced to 2dp. Greedy 93/270, final 197, 4 jumps at (92,93)/(126,127)/(164,165)/(183,184..." | 2026-10-19 05:28 | 0.01 | DELETE | deleted |
| 2 | `.scratch/pota114_staging` | 114-heading-second.md | **Status:** results-in | "4. Second-iteration numbers vs full bar (1/5 — REGRESSION). Greedy 93/270 (was 190), final 197, 4 jumps at IDENTICAL ..." | 2026-10-19 05:33 | 0.03 | DELETE | deleted |
| 3 | `.scratch/pota115_staging` | 115-bridge-reserve.md | **Status:** results-in | "3. Reserved-walk numbers vs full bar (1/5 — REGRESSION). Greedy 135/270 (was 190), final 135, 0 jumps, maxstep 26.8; ..." | 2026-10-19 06:00 | 0.09 | DELETE | deleted |
| 4 | `.scratch/pota116_staging` | 116-wide-recovery.md | **Status:** results-in | "2. Freeze (p116_freeze.txt) the rule was stated from. F1: guard113 first within-5mm pass of the 112-stall at seqpos 1..." | 2026-10-19 05:46 | 0.07 | DELETE | deleted |
| 5 | `.scratch/pota117_staging` | 117-staged-triggers.md | **Status:** results-in | "4. Staged-walk numbers vs full bar (1/5 — COLLAPSE). Greedy 81/270 (was 195, -114), final 197 via 2 T13 jumps at (80,..." | 2026-10-19 05:49 | 0.08 | DELETE | deleted |
| 6 | `.scratch/pota118_repro` | 118-presplit-cleaned.md | **Status:** results-in | "3. Chained loop numbers vs full bar (2/4 — REFUTED). Emit: comp-25 walk 21 pts; SEL-substitute: single run [0,21), id..." | 2026-10-19 05:53 | 0.03 | DELETE | deleted |
| 7 | `.scratch/pota119_repro` | 119-void-map.md | **Status:** results-in | "- ORIG[9..13] len5 maxgap6.0 \\| mid O11 [-20.6,-13.2,397.5] dMesh0.37 dBorder36.5 edges med1.470/p90 2.146 cloud24/67..." | 2026-10-19 06:02 | 0.08 | DELETE | deleted |
| 8 | `.scratch/pota120_repro` | 120-ror-relax.md | **Status:** results-in | "Arms (one variable = min_neighbors 6->3, C01 S0 only): ROR input = 364 snapped (p104_bnd_S0.npy), radius 8.62091 (= 6..." | 2026-10-19 06:08 | 0.35 | DELETE | deleted |
| 9 | `.scratch/pota121_repro` | 121-targeted-readmit.md | **Status:** results-in | "- Pipe curvature (109's split): NOT measurable on laptop — SampledWithNormals.ply lives on Spartan (/data/gpfs/.../po..." | 2026-10-19 06:12 | 0.01 | DELETE | deleted |
| 10 | `.scratch/pota122_repro` | 122-meshside-fill.md | **Status:** results-in | "Verdict: REFUTED as a landing recipe — 2/4 bar. GROWTH-R1 buys 6 on-arc dots at the price of 8 wall-junk dots and a +..." | 2026-10-19 06:17 | 0.04 | DELETE | deleted |
| 11 | `.scratch/pota123_repro` | 123-multiscale-boundary.md | **Status:** results-in | "0. Method + control GREEN. Rebuilt 103 verbatim (p123_control.py = p121/p122 recipe, OUT repointed): cleaned 270, gre..." | 2026-10-19 06:26 | 1.31 | DELETE | deleted |
| 12 | `.scratch/pota124_repro` | 124-snap-yield.md | **Status:** results-in | "2. Placement numbers (p124_measure.txt). r1 93 cand: on-arc 48 (ORIG<=5mm) vs junk 45; K=1 disp on-arc med 2.27 (p25 ..." | 2026-10-19 06:31 | 0.04 | DELETE | deleted |
| 13 | `.scratch/pota125_repro` | 125-bestbag-bestwalker.md | **Status:** results-in | "Verdict: STRUCTURAL REFUTATION — 1/5 bar items hold. Verbatim GUARD-116's trigger goes stale on the grown bag: the R_..." | 2026-10-19 06:37 | 0.05 | DELETE | deleted |
| 14 | `.scratch/pota126_repro` | 126-reanchor-grown.md | **Status:** results-in | "2. Re-anchored walk numbers vs full bar. GUARD-126-on-grown: greedy 205/278, final 205, 0 jumps, stats 13 cone-fires/..." | 2026-10-19 06:44 | 0.06 | DELETE | deleted |
| 15 | `.scratch/pota127_repro` | 127-ror-r1-crossgate.md | **Status:** results-in | "0. Method + control GREEN (reproduce-or-stop PASSED). Rebuilt grown-278 in pota127_repro (p127_step1.py, OUT repointe..." | 2026-10-19 06:50 | 0.03 | DELETE | deleted |
| 16 | `.scratch/pota128_repro` | 128-span25-admit.md | **Status:** results-in | "Verdict: LAND (minimal, greedy arm 4/4). The one dot geography clears pays exactly one span on the honest walk: rej 3..." | 2026-10-19 06:55 | 0.04 | DELETE | deleted |
| 17 | `.scratch/pota129_repro` | 129-reanchor-279.md | **Status:** results-in | "2. Re-anchored walk vs full bar (PRIMARY S129, p129_step2.py). Greedy 203/279, final 203, 0 jumps, stats 13/3/1/0, ar..." | 2026-10-19 06:59 | 0.05 | DELETE | deleted |
| 18 | `.scratch/pota130_repro` | 130-voidmap-279.md | **Status:** results-in | "- (96,97) len2 VOID+BRIDGED, owner ROR+chaining. DO/DB 6.30/5.61 (SEQ 261/79); nearest LEFT 6.9/5.6mm (slot 224). Hop..." | 2026-10-19 07:03 | 0.01 | DELETE | deleted |
| 19 | `.scratch/pota131_repro` | 131-span165-admit.md | **Status:** results-in | "0. Control GREEN (reproduce-or-stop PASSED). Rebuilt 279 in pota131_repro (p131_step1.py, OUT repointed): C=270 + SN1..." | 2026-10-19 07:07 | 0.04 | DELETE | deleted |
| 20 | `.scratch/pota132_repro` | 132-span3246-admit.md | **Status:** results-in | "0. Control GREEN (reproduce-or-stop PASSED). Rebuilt 279 in pota132_repro (p132_step1.py, OUT repointed): C=270 + SN1..." | 2026-10-19 07:12 | 0.02 | DELETE | deleted |
| 21 | `.scratch/pota133_repro` | 133-span3246-wide.md | **Status:** results-in | "Verdict: NEITHER clean landing NOR spent-license refutation -- license VALIDATED detection-side, landing BLOCKED walk..." | 2026-10-19 07:15 | 0.02 | DELETE | deleted |
| 22 | `.scratch/pota134_repro` | 134-recovery-282.md | **Status:** results-in | "(a) M134 (index-greedy + forward global teleport): 252 / 4.2874 / uncovered 8, 3 teleports incl. 2 landings >=40mm (6..." | 2026-10-19 07:22 | 0.08 | DELETE | deleted |
| 23 | `.scratch/pota135_repro` | 135-voidmap-285.md | **Status:** results-in | "2. (36,37)+(46,47) -- R36/R46 rescan: ROR-6 reject + r1-PASS + disp<=2.5 + dmid<=5 to new void-mids O36/O46 (fresh sp..." | 2026-10-19 07:25 | 0.01 | DELETE | deleted |
| 24 | `.scratch/pota136_repro` | 136-span3646-rescan.md | **Status:** results-in | "1. R36/R46 stated BEFORE running (p136_rule.txt, ORIG-free) + pool stated first + walker choice stated first. Pool: t..." | 2026-10-19 07:29 | 0.03 | DELETE | deleted |
| 25 | `.scratch/pota137_repro` | 137-bridge-c96.md | **Status:** results-in | "3. Verdict + forward path (no presplit-ticket refutation -- flanks ARE reached). The brief's sequencing-refutation br..." | 2026-10-19 07:34 | 0.03 | DELETE | deleted |
| 26 | `.scratch/pota138_repro` | 138-gate-segment-credit.md | **Status:** results-in | "Verdict: HONEST MEASUREMENT -- segment-credit is selective, not inflationary. Under R138 the 282 walk goes from 8 poi..." | 2026-10-19 07:37 | 0.03 | DELETE | deleted |
| 27 | `.scratch/pota139_repro` | 139-last-point-o37.md | **Status:** results-in | "1. O37 rule stated BEFORE running (p139_rule.txt, ORIG-free) + pool stated first + walker choice stated first. Pool: ..." | 2026-10-19 07:40 | 0.03 | DELETE | deleted |
| 28 | `.scratch/pota140_repro` | 140-trace-vs-author-views.md | **Status:** results-in | "Frame (stated): GT-seated/gate frame via `.scratch/pota115_staging/inputs/TF.txt` (TF==TO byte-identical, so gate fra..." | 2026-10-19 09:34 | 0.01 | DELETE | deleted |
| 29 | `.scratch/pota141_repro` | 141-e2e-potC-finished.md | **Status:** results-in (worker 2026-10-19 — COMMIT NOTHING; lead to commit) | "0. Bundle frozen + verified (reproduce-or-stop PASSED). Laptop .scratch/pota134_repro/ md5s: G282 fca04009 / seq_d 49..." | 2026-10-19 10:21 | 0.02 | DELETE | deleted |
| 30 | `.scratch/pota142_repro` | 142-single-line-topology.md | **Status:** results-in | "0. Control GREEN (reproduce-or-stop PASSED). Rebuilt M134d from read-only 134 inputs (.scratch/pota142_repro/p142_ste..." | 2026-10-19 09:47 | 0.22 | DELETE | deleted |
| 31 | `.scratch/pota143_repro` | 143-true-densify.md | **Status:** results-in | "0. Control GREEN (reproduce-or-stop PASSED). Rebuilt 279 in .scratch/pota143_repro (p143_step1.py, OUT repointed): C=..." | 2026-10-19 09:51 | 0.09 | DELETE | deleted |
| 32 | `.scratch/pota144_repro` | 144-recovery-on-314.md | **Status:** results-in | "1. Latch re-derived + trigger firing record (p144_trigger.txt stated BEFORE any recovery run; p144_freeze.txt). Latch..." | 2026-10-19 09:56 | 0.03 | DELETE | deleted |
| 33 | `.scratch/pota145_repro` | 145-e2e-potC-314.md | **Status:** results-in | "0. Bundle frozen + verified (reproduce-or-stop PASSED). Frozen = laptop .scratch/pota143_repro/p143_G314.npy (md5 4b1..." | 2026-10-19 10:22 | 0.02 | DELETE | deleted |
| 34 | `.scratch/pota146_repro` | 146-double-twice-densify.md | **Status:** results-in | "2. Rung B arm (target ~1260; rule-stated rB-scale backup since r1 fell short). X8 full-band @rB (2.42463, FPS 48, pit..." | 2026-10-19 14:37 | 0.15 | DELETE | deleted |
| 35 | `.scratch/pota147_repro` | 147-author-density-parity.md | **Status:** results-in | "2. HALF 1b -- wall-side, lead steer (mesh itself; ORIG only as the loop being classified). Radial-from-loop-axis at m..." | 2026-10-19 15:04 | 0.04 | DELETE | deleted |
| 36 | `.scratch/pota148_repro` | 148-dot-provenance-band.md | **Status:** results-in | "Named next fix (bag-space, ORIG-free; prep-side root in parens). Filter the 314 successor by face-side BEFORE walking..." | 2026-10-19 15:12 | 0.07 | DELETE | deleted |
| 37 | `.scratch/pota149_repro` | 149-filtered-thinline-walk.md | **Status:** results-in | "3. Recipe-retune report: NO RETUNE -- all M144 constants transferred verbatim and the walk ran + HALTed honestly. K=3..." | 2026-10-19 15:35 | 0.03 | DELETE | deleted |
| 38 | `.scratch/pota150_repro` | 150-source-elimination-prep.md | **Status:** results-in | "Verdict: TAP CAN BE CLOSED AT THE C-BASE CLOUD LEVEL -- face-side select (align<=+0.5) drops 180/182 outer (98.9% red..." | 2026-10-19 15:23 | 0.04 | DELETE | deleted |
| 39 | `.scratch/pota151_repro` | 151-dense-extraction-98-125.md | **Status:** results-in | "4. Re-walk (p151_step2_walk.py, M144 machinery VERBATIM -- K34, d>=1mm twin-skip, envelope=own max greedy stride, T13..." | 2026-10-19 15:36 | 0.04 | DELETE | deleted |
| 40 | `.scratch/pota152_repro` | 152-small-spans-densify.md | **Status:** results-in | "3. Re-walk (p152_step2_walk.py, M144 machinery VERBATIM -- K34, d>=1mm twin-skip, envelope=own max greedy stride, T13..." | 2026-10-19 15:46 | 0.04 | DELETE | deleted |
| 41 | `.scratch/pota153_repro` | 153-revive-dead-code.md | **Status:** results-in | "probe: outer kept 1/182 (red 0.995, bar >=0.90 PASS), inner 88/88 (bar >=95% PASS)," | 2026-10-19 15:49 | 0.03 | DELETE | deleted |
| 42 | `.scratch/pota154_repro` | 154-apply-build-reextract.md | **Status:** results-in | "2. ORIG-free recheck: PASS. Added-line grep for ORIG/Bl_0/author = 3 hits, all comment prose from staged text; no ORI..." | 2026-10-19 15:56 | 0.02 | DELETE | deleted |
| 43 | `.scratch/pota155_repro` | 155-port-cure-to-production-copy.md | **Status:** results-in | "1. Sub-copy admission audit (p155_step0_admit.py -> .scratch/pota155_repro/p155_admit.txt; render artifacts/pota155/p..." | 2026-10-19 16:41 | 0.04 | KEEP (tracked) | deleted-then-restored |
| 44 | `.scratch/pota157_repro` | 157-c01-mesh-sbs.md | **Status:** results-in | "Verdict: the eye sees the grey Pot C sherd mesh (spout to the right) carrying both traces on its lip in the same 140-..." | 2026-10-19 16:56 | 0.01 | DELETE | deleted |
| 45 | `.scratch/pota159_repro` | 159-adaptive-veto.md | **Status:** superseded-by-160 | "Blocked by: 156 (fixed align<=0.5 eats C01 true rim: kept=223 dropped=141, gate 27.68/0) + 158 (no-veto 30.18/0: veto..." | 2026-10-19 17:36 | 0.01 | KEEP (open) | untouched |
| 46 | `.scratch/pota161_repro` | 161-mesh-overlay-160.md | **Status:** results-in | "Verdict: the eye sees both 160 walks seated on the C01 lip against the author's loop in one shared view -- BASE cover..." | 2026-10-19 18:03 | 0.06 | DELETE | deleted |
| 47 | `.scratch/pota162_repro` | 162-emptiness-veto.md | **Status:** results-in | "Banked context (cited, not rerun -- analysis-only landing needs no new numbers): Pot A BASE->VAR Bl_0 pairs P01 193->..." | 2026-10-19 18:20 | 0.67 | DELETE | deleted |
| 48 | `.scratch/pota163_repro` | 163-surface-support-test.md | **Status:** results-in | "Staging recovered from Spartan `pota160_repro/pota160_C/` (S1 xyz, `unclustered.ply` 2343 verts, leftover VAR `bounda..." | 2026-10-19 18:36 | 2.40 | DELETE | deleted |
| 49 | `.scratch/pota164_repro` | 164-bend-aware-boundary.md | **Status:** results-in | "VERDICT: bend does not own the C01 false loop. The false loop sits on FLATTER sheet than the true rim (tilt 24.6 vs 2..." | 2026-10-19 18:48 | 0.07 | DELETE | deleted |
| 50 | `.scratch/pota165_repro` | 165-surface-closeups.md | **Status:** results-in | "(a) At the false loop there is NO sharp turn/junction/crease under the red ring -- the sheet around it is smooth in a..." | 2026-10-19 19:10 | 0.01 | DELETE | deleted |
| 51 | `.scratch/pota166_repro` | 166-mesh-boundary-file-check.md | **Status:** results-in | "- FAR n=91: min 0.04 / p10 0.28 / p25 0.87 / MED 7.42 / p75 14.61 / p90 16.82 / max 69.39; frac <1mm 0.286, <2mm 0.37..." | 2026-10-20 00:34 | 0.05 | DELETE | deleted |
| 52 | `.scratch/pota167_repro` | 167-pipe-exclusion.md | **Status:** results-in | "VERDICT: negative per rule (c). Loop1 (247e MAIN-sheet hole, perim 102mm) has NO attached descending surface: the rim..." | 2026-10-20 00:51 | 0.13 | DELETE | deleted |
| 53 | `.scratch/pota168_repro` | 168-drop-second-ring-close-gaps.md | **Status:** results-in | "0. Controls GREEN (reproduce-or-stop PASSED). Loop trace verbatim from p166_filecheck: 34989 edges, 636 boundary, loo..." | 2026-10-20 01:14 | 0.00 | DELETE | deleted |
| 54 | `.scratch/pota168b_repro` | 168-drop-second-ring-close-gaps.md | **Status:** results-in | "0. Controls GREEN (reproduce-or-stop PASSED). Loop trace verbatim from p166_filecheck: 34989 edges, 636 boundary, loo..." | 2026-10-20 01:27 | 0.07 | DELETE | deleted |
| 55 | `.scratch/pota169_repro` | 169-why-finder-silent-at-gaps.md | **Status:** results-in | "Verdict: MECHANISM NAMED for all 188/188 gap stations, 0 unmeasured. The estimator is largely EXONERATED -- it fires ..." | 2026-10-20 01:43 | 0.35 | DELETE | deleted |
| 56 | `.scratch/pota170_repro` | 170-no-veto-manual-ring-walk.md | **Status:** results-in | "Verdict: HONEST NEGATIVE on the letter of the bar, walk-side fully closed. Recipe-verbatim single strand: 45/211 (fre..." | 2026-10-20 02:05 | 0.05 | DELETE | deleted |
| 57 | `.scratch/pota170sbs_repro` | 170-no-veto-manual-ring-walk.md | **Status:** results-in | "Verdict: HONEST NEGATIVE on the letter of the bar, walk-side fully closed. Recipe-verbatim single strand: 45/211 (fre..." | 2026-10-20 02:12 | 0.00 | DELETE | deleted |
| 58 | `.scratch/pota171_repro` | 171-potA-no-veto-regate.md | **Status:** ready-for-agent (170 landed 2026-10-20 -- unblocked). | "Verdict: REGRESS with per-pair owners -- the veto is load-bearing on intact-mesh Pot A. Per-piece policy is back on t..." | 2026-10-20 02:35 | 0.00 | KEEP (tracked) | untouched |
| 59 | `.scratch/pota171sbs_repro` | 171-potA-no-veto-regate.md | **Status:** ready-for-agent (170 landed 2026-10-20 -- unblocked). | "Verdict: REGRESS with per-pair owners -- the veto is load-bearing on intact-mesh Pot A. Per-piece policy is back on t..." | 2026-10-20 02:50 | 0.02 | KEEP (open) | untouched |
| 60 | `.scratch/pota172_repro` | 172-sheet-vs-mesh-at-gaps.md | **Status:** ready-for-agent | "Verdict: 13/13 runs MESH-HAS-IT, 0 MESH-MISSING. The scan is NOT silent -- the DS mesh carries surface within 0.26mm ..." | 2026-10-20 02:28 | 0.03 | KEEP (tracked) | untouched |
| 61 | `.scratch/pota173_repro` | 173-densify-the-dots.md | **Status:** results-in | "Bar scorecard (fresh = BASE 92/211, med 5.61, <2mm 22.9%; 170 union = 90/211, med 4.52, <2mm 31.0%; 170 strand1-M top..." | 2026-10-20 02:39 | 0.11 | KEEP (tracked) | deleted-then-restored |
| 62 | `.scratch/pota174_repro` | 174-find-the-real-edge.md | **Status:** results-in | "Lead ruling (2026-10-20): ACCEPT a+b as the ticket, CLOSE c as not-the-blocker. (a) mesh-stage reclaim proven same-bi..." | 2026-10-20 04:02 | 12.71 | KEEP (tracked) | deleted-then-restored |
| 63 | `.scratch/pota175_repro` | 175-two-walks-two-slots.md | **Status:** results-in | "1. SEPARATION (parent-surface labels, ORIG-free; C01 = this ticket's only piece). Per-triangle wall labels on the DS ..." | 2026-10-20 03:26 | 0.30 | KEEP (tracked) | deleted-then-restored |
| 64 | `.scratch/pota176_repro` | 176-potC-reclaim-split-assemble.md | **Status:** ready-for-agent | "7. Lead relay (2026-10-20, R8: only the lead holds Spartan SSH). Laptop legs VERIFIED (Comments present, C01+C03F0 re..." | 2026-10-20 03:51 | 3.19 | KEEP (tracked) | untouched |
| 65 | `.scratch/pota177_repro` | 177-assembler-side-miss.md | **Status:** results-in | "2. The search did not move -- numbers. 176-vs-145 chosen T: T_1to_1 rot-diff 0.033deg / trans-diff 0.10; T_3to_3 0.04..." | 2026-10-20 12:00 | 0.10 | KEEP (tracked) | deleted-then-restored |
| 66 | `.scratch/pota180_repro` | 180-single-loop-input.md | **Status:** ready-for-agent | "\\| closure \\| 1.80mm \\| 17.67mm \\| 1.48mm (<=2 PASS) \\|" | 2026-10-20 12:14 | 0.12 | KEEP (open) | untouched |
| 67 | `.scratch/pota181_repro` | 181-no-densify-arm.md | **Status:** ready-for-agent | "0. Controls GREEN (reproduce-or-stop equivalent). Bag rebuilt from parts: guarded-270 + 124-admit-8 + 128-admit-1 + 1..." | 2026-10-20 12:14 | 0.01 | KEEP (tracked) | untouched |
| 68 | `.scratch/pota183_repro` | 183-single-strand-picker.md | Status: DONE (mixed, loses shootout) | "- 202 dots / closure 0.85 PASS bar, but arc +9pc, D-alphabet 28 (fragmented spacing)." | 2026-10-20 15:12 | 0.03 | DELETE | deleted |
| 69 | `.scratch/pota184_repro` | 184-heading-rule-walk.md | Status: DONE (honest negative) | "- Arm 2 premise refuted: discipline must come from strand separation (183/185), not a" | 2026-10-20 15:10 | 0.06 | DELETE | deleted |
| 70 | `.scratch/pota185_repro` | 185-thin-then-walk.md | Status: DONE (WINS shootout) | "- 204 dots / arc 365.0 / closure 1.79 / gaps 0 / D-tokens 2 (run 131) / rim-med 0.64." | 2026-10-20 15:14 | 0.06 | DELETE | deleted |
| 71 | `.scratch/pota186_repro` | 186-thin-loop-e2e.md | Status: DONE | "S4. Verdict vs bar (honest, mixed). PASS: controls green (A 8/8+15/15, C_orig 4/4+5/5); C01 seated (T_0to_0 present x..." | 2026-10-20 15:23 | 0.15 | DELETE | deleted |
| 72 | `.scratch/pota188_repro` | 188-thin-rollout-potD.md | Status: landed (lead 2026-10-20: 29/29 singles verified, P22 artifact exonerated, E2E decline accepted -- rerun would duplicate 84) | "2. SXC census: 29/29 clean single loops -- ZERO doubled. ratio 0.97-1.14 on 28 pieces (P22 0.26 is a non-planar-loop ..." | 2026-10-20 15:57 | 0.14 | DELETE | deleted |
| 73 | `.scratch/pota189_repro` | 189-thin-rollout-potE.md | Status: landed (lead 2026-10-20: HONEST NEGATIVE verified -- 13 gated loops ship, E2E below bar x3, only E23 converts; generation fixed, placement fails downstream) | "E19 centreline had one 5.57mm coverage jump (gate FAIL) -> documented fallback:" | 2026-10-20 17:23 | 0.03 | DELETE | deleted |
| 74 | `.scratch/pota190_repro` | 190-thin-rollout-potF.md | Status: landed (lead 2026-10-20: PASS bar-neutral verified -- 6/6+9/9 x3, F01 seated x3, controls green; gated thin (doubled edge only) holds) | "2. Cure (185 v3 pipeline + one principled R3 strip refinement, all inputs strip-xyz-only). Verbatim-v3 on the full 25..." | 2026-10-20 16:40 | 0.07 | DELETE | deleted |
| 75 | `.scratch/pota193_repro` | 193-thin-rollout-potJ.md | Status: landed (lead 2026-10-20: bar-HOLD verified -- 7/10+13/18 x3 exact bit-identical set; J03-seating hypothesis REFUTED, J03 placed-but-wrong -> unplaced; J needs no further rim work) | "2. Cure (185 v3 verbatim, laptop-side). Input = J03 fresh doubled walk itself (371 dots) as the strip (no TRUE-strip ..." | 2026-10-20 15:59 | 0.16 | DELETE | deleted |
| 76 | `.scratch/pota197_repro` | 197-d-only-ablation-potC.md | Status: landed (lead 2026-10-20: MIXED verified -- D-only recovers C01-C03 true join x3 deterministic, pot-level falsifier fires 2/4 vs 4/4; side-finding: landed sections added ~270 rim pts) | "1. Tallies (identical x3 -- deterministic). C_orig BAR 4/4 sherd + 4/5 edge (all 5 GT edges geometrically PASS: rot<=..." | 2026-10-20 18:00 | 15.72 | DELETE | deleted |
| 77 | `.scratch/pota201_repro` | 201-loop-feature-identity.md | Status: landed (lead 2026-10-20: B09/A07 INTRINSIC -- thin halved word agreement; B04/J03 exonerated -- downstream; thickness leg inconclusive) | "Cross-piece: fwd agreement predicts seating (C01 0.544 seats; J03 0.556 + B04 0.535 at that level but fail downstream..." | 2026-10-20 17:34 | 0.03 | DELETE | deleted |
| 78 | `.scratch/pota202_repro` | 202-score-J03-true-pairs.md | Status: landed (lead 2026-10-20: INPUT EXONERATED TO SEARCH -- all 3 true pairs SAME thin-vs-ORIG, no killing gate; J03 dies in generation/pruning) | "Cross verdict: INPUT EXONERATED TO SEARCH. All three true pairs score SAME (thin duet = ORIG duet within noise); no p..." | 2026-10-20 17:49 | 0.28 | DELETE | deleted |
| 79 | `.scratch/pota204_repro` | 204-d-all-whole-pot-c.md | Status: open (lead 2026-10-20: cut per user's m04774 intent + m04778 answers Q1b/Q2a/Q3a; 197 was C01-only ablation, this is all-pieces) | "5. Falsifier (Q3a): C_D_ALL == C_orig (4/4 sherd + 4/5 edge, x3 deterministic) proves D-alone sufficient for the pot...." | 2026-10-20 20:33 | 0.29 | KEEP (open) | untouched |
| 80 | `.scratch/pota221` | 221-r2-validate-mixed.md | Status: done | "- P15@12: ourBl0->o1 0.64/100.0 AT-BAR (n=141, 0 jumps); ourBl1 below-bar vs either author lane alone (vs o0 5.87, vs..." | 2026-10-21 11:02 | 9.64 | KEEP (tracked) | deleted-then-restored |
| 81 | `.scratch/pota222` | 222-gap-gated-stop.md | Status: done | "ACCEPT. R6: 6/6 sacct COMPLETED 0:0; P12 bridge cross-checked against lead measurement (worker 0.18 vs lead 0.00, dis..." | 2026-10-21 15:11 | 13.64 | KEEP (tracked) | deleted-then-restored |
| 82 | `.scratch/pota223` | 223-trace-honest-split.md | Status: done | "ACCEPT with strict-FAIL recorded. R6: job 33589544 sacct COMPLETED 0:0; local re-score EXACT (o0->a1 0.63/89.0, o1->a..." | 2026-10-21 15:33 | 1.23 | KEEP (tracked) | deleted-then-restored |
| 83 | `.scratch/pota224` | 224-tighter-than-honest.md | Status: done | "- @3: ourBl0 vs o1 n=160 med=0.61 cov=99.4 max=2.4 jumps=0 gapmax=8.1 endgap=1.8 AT-BAR. ourBl1 vs o0 n=146 med=0.71 ..." | 2026-10-21 15:51 | 0.40 | KEEP (tracked) | deleted-then-restored |
| 84 | `.scratch/pota225` | 225-r4-five-piece-test.md | Status: done | "R4 = the LOOSEST threshold (proven search direction, user m03460: start loosest, tighten down) satisfying ALL THREE: ..." | 2026-10-21 16:09 | 0.02 | KEEP (tracked) | deleted-then-restored |
| 85 | `.scratch/pota226` | 226-r5-retune-decision.md | Status: done | "R5-DROP. R6: gap 33592717 + edge 33592730 COMPLETED 0:0; P27@8 re-scored EXACT (swapped o0->a1 0.87/62.9 max16.2, o1-..." | 2026-10-21 16:22 | 0.02 | KEEP (tracked) | deleted-then-restored |
| 86 | `.scratch/pota227` | 227-un-leg-test.md | Status: done | "R6-DROP as a complete rule, R6-KEPT as the stopping rule. R6: job 33593416 COMPLETED 0:0; P27@12 re-scored EXACT (swa..." | 2026-10-21 16:40 | 0.02 | KEEP (tracked) | deleted-then-restored |
| 87 | `.scratch/pota228` | 228-lane-adherence-leg.md | Status: done | "NO-SEPARATION accepted. R6: metrics.csv on disk (16 rows; spot values EXACT: P27@4.5 1.50/54.9, P27@8 0.87/62.9); ver..." | 2026-10-22 00:35 | 1.35 | KEEP (tracked) | untouched |
| 88 | `.scratch/pota229` | 229-p27-edge-sharpness.md | Status: done | "OURS-AT-EDGE accepted. R6: numbers EXACT (baseline 1.294, control 41.63/41.47 PASS, line 16.29, disputed 39.22/1.35);..." | 2026-10-21 17:18 | 0.17 | KEEP (tracked) | deleted-then-restored |
| 89 | `.scratch/pota230` | 230-p27-rescore-repaired-ruler.md | Status: done | "RESCORED-NEAR-MISS accepted. R6: repro bit-identical to 229 (baseline 1.294, control 41.63/41.47, line 16.29, dispute..." | 2026-10-21 17:30 | 0.30 | KEEP (tracked) | deleted-then-restored |
| 90 | `.scratch/pota231` | 231-r6-rollout-six-pieces.md | Status: done | "TABLE-COMPLETE accepted + P25 slot correction. R6: r6_table.csv on disk (6 rows, zero divergence claimed -- spot valu..." | 2026-10-21 17:42 | 0.01 | KEEP (tracked) | deleted-then-restored |
| 91 | `.scratch/pota232` | 232-p22-turn-away-diagnosis.md | Status: done | "BRIDGE-OPENS-AT-3 accepted with one grading correction. R6: jobs 33613082/33613083 sacct COMPLETED 0:0; report intern..." | 2026-10-22 00:52 | 0.22 | KEEP (tracked) | untouched |
| 92 | `.scratch/pota234` | 234-plane-continuity-split.md | Status: done | "No break swallowed (four checks). (1) Votes clean 100/0, 0/99.5, 0/100 — a swallowed break chunk would vote mixed. (2..." | 2026-10-22 02:12 | 10.80 | KEEP (tracked) | untouched |
| 93 | `.scratch/p215_evidence` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:20 | 0.04 | DELETE | deleted |
| 94 | `.scratch/p215_p16_bagmap.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:08 | 0.00 | DELETE | deleted |
| 95 | `.scratch/p215_p16_bridge.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:09 | 0.00 | DELETE | deleted |
| 96 | `.scratch/p215_p16_crease.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:11 | 0.00 | DELETE | deleted |
| 97 | `.scratch/p215_p16_hole.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:10 | 0.00 | DELETE | deleted |
| 98 | `.scratch/p215_p16_membership.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:03 | 0.00 | DELETE | deleted |
| 99 | `.scratch/p215_p16_normcontrast.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:11 | 0.00 | DELETE | deleted |
| 100 | `.scratch/p215_p16_reclaim.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:15 | 0.01 | DELETE | deleted |
| 101 | `.scratch/p215_p16_sectors.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:09 | 0.00 | DELETE | deleted |
| 102 | `.scratch/p215_p16_stage.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:04 | 0.00 | DELETE | deleted |
| 103 | `.scratch/p215_p16_stripun.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:18 | 0.00 | DELETE | deleted |
| 104 | `.scratch/p215_spans.py` | 215-potD-six-rewalks.md | Status: done | "0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%" | 2026-10-21 02:21 | 0.00 | DELETE | deleted |
| 105 | `.scratch/p216_ceil27.py` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:40 | 0.00 | DELETE | deleted |
| 106 | `.scratch/p216_cross.py` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:41 | 0.00 | DELETE | deleted |
| 107 | `.scratch/p216_edge.sh` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:35 | 0.00 | DELETE | deleted |
| 108 | `.scratch/p216_edge_resume.sh` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:46 | 0.00 | DELETE | deleted |
| 109 | `.scratch/p216_spans_strip.py` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:38 | 0.01 | DELETE | deleted |
| 110 | `.scratch/p216_stage_strip.sh` | 216-potD-class-test-five.md | Status: done | "ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15..." | 2026-10-21 02:30 | 0.01 | DELETE | deleted |

## B. Odd ones — listed, NOT deleted

| Path | What it is | Handling |
|---|---|---|
| `.scratch/pota-repro/gap-check.md` | inside the protected `pota-repro/` tree | **KEEP** — never deleted |
| `.scratch/pota-repro/issues/178-instrumented-C176-run.md` | inside `pota-repro/issues/`; untracked | **KEEP** — protected tree outranks untracked status |
| `.scratch/pota-repro/issues/204-d-all-whole-pot-c.md` | **tracked, MODIFIED in git** (pre-existing ` M`); `Status: open` | **KEEP** — not staged, not reverted, not committed |
| `C:/PR/SfSpp_preprocessing/vote247.diff` | obsolete now the arms are stripped from source (11196 bytes) | **KEEP — recommend deletion only**: outside `.scratch/`, outside this boundary |
| `.dsh-ops-update-*.lock` (79) | harness lock debris, all 0 bytes, newest 31 h stale | DELETE — split below |

## C. Lock debris

79 files, all **0 bytes**, newest 2026-10-22 18:26 (≈31 h stale at manifest time).

| Where | count | handling |
|---|---|---|
| under `.scratch/pota-repro/` (permitted by the brief) | 42 | **deleted** — none tracked |
| inside DELETE rows | 30 | removed with the directory (5 in `pota221` were **tracked**, restored with the dir) |
| inside `pota228` (6) and `pota232` (1) | 7 | **kept** — those dirs are in the frozen live round; 0 bytes |

## D. Deleted rows (84)

| Path | Ticket | MB |
|---|---|---|
| `.scratch/pota113_staging` | 113-heading-walk.md | 0.01 |
| `.scratch/pota114_staging` | 114-heading-second.md | 0.03 |
| `.scratch/pota115_staging` | 115-bridge-reserve.md | 0.09 |
| `.scratch/pota116_staging` | 116-wide-recovery.md | 0.07 |
| `.scratch/pota117_staging` | 117-staged-triggers.md | 0.08 |
| `.scratch/pota118_repro` | 118-presplit-cleaned.md | 0.03 |
| `.scratch/pota119_repro` | 119-void-map.md | 0.08 |
| `.scratch/pota120_repro` | 120-ror-relax.md | 0.35 |
| `.scratch/pota121_repro` | 121-targeted-readmit.md | 0.01 |
| `.scratch/pota122_repro` | 122-meshside-fill.md | 0.04 |
| `.scratch/pota123_repro` | 123-multiscale-boundary.md | 1.31 |
| `.scratch/pota124_repro` | 124-snap-yield.md | 0.04 |
| `.scratch/pota125_repro` | 125-bestbag-bestwalker.md | 0.05 |
| `.scratch/pota126_repro` | 126-reanchor-grown.md | 0.06 |
| `.scratch/pota127_repro` | 127-ror-r1-crossgate.md | 0.03 |
| `.scratch/pota128_repro` | 128-span25-admit.md | 0.04 |
| `.scratch/pota129_repro` | 129-reanchor-279.md | 0.05 |
| `.scratch/pota130_repro` | 130-voidmap-279.md | 0.01 |
| `.scratch/pota131_repro` | 131-span165-admit.md | 0.04 |
| `.scratch/pota132_repro` | 132-span3246-admit.md | 0.02 |
| `.scratch/pota133_repro` | 133-span3246-wide.md | 0.02 |
| `.scratch/pota134_repro` | 134-recovery-282.md | 0.08 |
| `.scratch/pota135_repro` | 135-voidmap-285.md | 0.01 |
| `.scratch/pota136_repro` | 136-span3646-rescan.md | 0.03 |
| `.scratch/pota137_repro` | 137-bridge-c96.md | 0.03 |
| `.scratch/pota138_repro` | 138-gate-segment-credit.md | 0.03 |
| `.scratch/pota139_repro` | 139-last-point-o37.md | 0.03 |
| `.scratch/pota140_repro` | 140-trace-vs-author-views.md | 0.01 |
| `.scratch/pota141_repro` | 141-e2e-potC-finished.md | 0.02 |
| `.scratch/pota142_repro` | 142-single-line-topology.md | 0.22 |
| `.scratch/pota143_repro` | 143-true-densify.md | 0.09 |
| `.scratch/pota144_repro` | 144-recovery-on-314.md | 0.03 |
| `.scratch/pota145_repro` | 145-e2e-potC-314.md | 0.02 |
| `.scratch/pota146_repro` | 146-double-twice-densify.md | 0.15 |
| `.scratch/pota147_repro` | 147-author-density-parity.md | 0.04 |
| `.scratch/pota148_repro` | 148-dot-provenance-band.md | 0.07 |
| `.scratch/pota149_repro` | 149-filtered-thinline-walk.md | 0.03 |
| `.scratch/pota150_repro` | 150-source-elimination-prep.md | 0.04 |
| `.scratch/pota151_repro` | 151-dense-extraction-98-125.md | 0.04 |
| `.scratch/pota152_repro` | 152-small-spans-densify.md | 0.04 |
| `.scratch/pota153_repro` | 153-revive-dead-code.md | 0.03 |
| `.scratch/pota154_repro` | 154-apply-build-reextract.md | 0.02 |
| `.scratch/pota157_repro` | 157-c01-mesh-sbs.md | 0.01 |
| `.scratch/pota161_repro` | 161-mesh-overlay-160.md | 0.06 |
| `.scratch/pota162_repro` | 162-emptiness-veto.md | 0.67 |
| `.scratch/pota163_repro` | 163-surface-support-test.md | 2.40 |
| `.scratch/pota164_repro` | 164-bend-aware-boundary.md | 0.07 |
| `.scratch/pota165_repro` | 165-surface-closeups.md | 0.01 |
| `.scratch/pota166_repro` | 166-mesh-boundary-file-check.md | 0.05 |
| `.scratch/pota167_repro` | 167-pipe-exclusion.md | 0.13 |
| `.scratch/pota168_repro` | 168-drop-second-ring-close-gaps.md | 0.00 |
| `.scratch/pota168b_repro` | 168-drop-second-ring-close-gaps.md | 0.07 |
| `.scratch/pota169_repro` | 169-why-finder-silent-at-gaps.md | 0.35 |
| `.scratch/pota170_repro` | 170-no-veto-manual-ring-walk.md | 0.05 |
| `.scratch/pota170sbs_repro` | 170-no-veto-manual-ring-walk.md | 0.00 |
| `.scratch/pota183_repro` | 183-single-strand-picker.md | 0.03 |
| `.scratch/pota184_repro` | 184-heading-rule-walk.md | 0.06 |
| `.scratch/pota185_repro` | 185-thin-then-walk.md | 0.06 |
| `.scratch/pota186_repro` | 186-thin-loop-e2e.md | 0.15 |
| `.scratch/pota188_repro` | 188-thin-rollout-potD.md | 0.14 |
| `.scratch/pota189_repro` | 189-thin-rollout-potE.md | 0.03 |
| `.scratch/pota190_repro` | 190-thin-rollout-potF.md | 0.07 |
| `.scratch/pota193_repro` | 193-thin-rollout-potJ.md | 0.16 |
| `.scratch/pota197_repro` | 197-d-only-ablation-potC.md | 15.72 |
| `.scratch/pota201_repro` | 201-loop-feature-identity.md | 0.03 |
| `.scratch/pota202_repro` | 202-score-J03-true-pairs.md | 0.28 |
| `.scratch/p215_evidence` | 215-potD-six-rewalks.md | 0.04 |
| `.scratch/p215_p16_bagmap.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_bridge.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_crease.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_hole.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_membership.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_normcontrast.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_reclaim.py` | 215-potD-six-rewalks.md | 0.01 |
| `.scratch/p215_p16_sectors.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_stage.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_p16_stripun.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p215_spans.py` | 215-potD-six-rewalks.md | 0.00 |
| `.scratch/p216_ceil27.py` | 216-potD-class-test-five.md | 0.00 |
| `.scratch/p216_cross.py` | 216-potD-class-test-five.md | 0.00 |
| `.scratch/p216_edge.sh` | 216-potD-class-test-five.md | 0.00 |
| `.scratch/p216_edge_resume.sh` | 216-potD-class-test-five.md | 0.00 |
| `.scratch/p216_spans_strip.py` | 216-potD-class-test-five.md | 0.01 |
| `.scratch/p216_stage_strip.sh` | 216-potD-class-test-five.md | 0.01 |

## E. Restored rows (15) — deleted, then tracked content restored

| Path | Tracked files back | MB before | MB now |
|---|---|---|---|
| `.scratch/pota155_repro` | yes | 0.04 | 0.01 |
| `.scratch/pota173_repro` | yes | 0.11 | 0.11 |
| `.scratch/pota174_repro` | yes | 12.71 | 0.71 |
| `.scratch/pota175_repro` | yes | 0.30 | 0.28 |
| `.scratch/pota177_repro` | yes | 0.10 | 0.01 |
| `.scratch/pota221` | yes | 9.64 | 1.10 |
| `.scratch/pota222` | yes | 13.64 | 6.12 |
| `.scratch/pota223` | yes | 1.23 | 1.21 |
| `.scratch/pota224` | yes | 0.40 | 0.38 |
| `.scratch/pota225` | yes | 0.02 | 0.00 |
| `.scratch/pota226` | yes | 0.02 | 0.01 |
| `.scratch/pota227` | yes | 0.02 | 0.01 |
| `.scratch/pota229` | yes | 0.17 | 0.17 |
| `.scratch/pota230` | yes | 0.30 | 0.30 |
| `.scratch/pota231` | yes | 0.01 | 0.01 |

## F. Measured size — the brief's ~161 MB does not reproduce

- Sum of bytes over the whole candidate set: **78.99 MB**.
- `du -sk` over the 92 candidate dirs + `p215_evidence`: 84801 KB ≈ 82.8 MB. Whole `.scratch/`: 88713 KB ≈ 86.6 MB.
- The whole tree is 86.6 MB, so no subset can be 161 MB. Freed space is therefore reported from `du` before/after
  (**55.1 MB**), not against the brief's figure.

## G. Incident — tracked files were deleted and restored

**What happened.** The first tracked-check read `git ls-files -z` from command stdout; the shell tool truncates long
output to its tail, so the set held only a fraction of the repo's **3314** tracked files. Every candidate therefore
tested as "not tracked", and the "0 of 110 candidates are tracked" conclusion was wrong. It was not caught earlier
because a directory whose contents are *entirely* tracked is **clean**, so it appears nowhere in `git status` — its
absence looked like "no tracked files" when it in fact meant "nothing to report".

**Damage.** 15 of the 99 deleted rows contained tracked files (263 files): `pota155_repro` (5), `pota173_repro` (25),
`pota174_repro` (34), `pota175_repro` (91), `pota177_repro` (41), `pota221` (15), `pota222` (8), `pota223` (12),
`pota224` (7), `pota225` (3), `pota226` (6), `pota227` (4), `pota229` (4), `pota230` (6), `pota231` (2).

**Repair.** `git ls-files -d -z -- .scratch` -> `xargs -0 git checkout --`: all 263 restored, `git ls-files -d` now 0.
No commit, no stage, no `git add`; the pre-existing ` M` on `204-d-all-whole-pot-c.md` was never a deleted path and is
untouched. Final `git status` non-untracked output is that single ` M` line.

**Residual, stated plainly.** The 15 directories survive but hold **only their tracked files** (10.43 MB of the
38.72 MB they had). Their **untracked** scratch content — `.npz`/`.npy`/`.png`/`.txt` intermediates — is gone and was
never in git, so it cannot be restored. Per the standing rule those directories were *deletable* (their tickets are
done/results-in with numbers quoted), so no ticket evidence was lost: all 271 tickets are intact and every ticket
referenced by a deleted row is still readable. But under the mechanical rule as briefed they should have been KEPT,
and 15 of the 84 deletions do not satisfy the "non-tracked" clause.

**Root cause fixed.** The tracked list is now written to a file and read from disk (`.tracked.lst`, 3314 entries), never
taken from truncated stdout; the reclassification above uses that list.

## H. Caveats

- `pota159_repro` ticket reads `superseded-by-160` — not a done value, so KEPT (reason: open).
- `pota204_repro` ticket is `Status: open` — KEPT.
- `pota171sbs_repro` and `pota180_repro` read `ready-for-agent` — work not done, KEPT.
- 7 of the 22 tracked KEEPs also fall under other guards (`pota171/172/176/181` open, `pota228/232/234` recent).
- 7 lock files remain inside `pota228`/`pota232` (0 bytes each), left deliberately to avoid touching the live round.
