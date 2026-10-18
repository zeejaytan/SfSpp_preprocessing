# Fused-content separation research (Pot C) — preprocessing-side fix

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** A preprocessing-side way to un-fuse Pot C's fused walk content. Stage 1 (must-have): characterize the fusion — how the author's C ORIG rims differ from our fresh C rims, which loops fused where, and where the branch points are. Stage 2: propose + implement a separation, gate it. Stage 3 (only if gate passes): E2E x3.

**Answers:** E1

**Blocked by:** 89 (regime: slot-corrected fresh near-author everywhere except fused C) + 68 (split-select measured NULL — read why before repeating it) + 79 (C02/C04 territory) + 85/87/88 (crest NULL, FLIP-BOUND, GATE-NAMED: third-loop geometry ruled out, matcher-side vetoed — the fix must be preprocessing-side) + 63 (C bar/ORIG)

**Status:** results-in

**Starting position:** Author C ORIG bundle + t39-pipe fresh C bundle (read-only first). Read tickets 68, 79, 85 Comments (what was tried, why NULL) before touching anything. New scratch pota97_repro/; renders under laptop artifacts/pota97/.

**Rules:** research-first (Stage 1 characterization is the deliverable even if separation fails — honest negative > forced cure); one variable per attempt; no E2E without a passing gate; E2E on cure-potA @ bffefb6 with asserts + C ORIG + A controls in the same runs; sacct-direct polling (never scripts/slurm_poll.sh); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3 for any E2E.

- [ ] Stage 1: fusion characterization (author vs fresh C, branch points)
- [ ] Stage 2: separation proposal + implementation + gate
- [ ] Stage 3 (gate-gated): E2E x3 vs bar + controls green
- [ ] Job IDs + sacct states (if E2E run)

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: fusion characterized with branch points named (Stage 1 due); separation honestly NEGATIVE — branch-point-aware touch-split (new variable vs 68's gap split) leaves every C01 loop component >=3.28mm median off ORIG, so the gate (<2mm medians) fails and no E2E was run per Rules. The blocking evidence: the true lip was never traced for C01 (both slots miss by ~5.6mm / 46mm), and C02/C04 need no separation — they are clean SWAPS already routed by S24 (73/74, 2/3+1/3 with 17mm floor). Zero ORIG points; source bundles read-only md5-guarded; login-node screening only (no Slurm jobs); no commits.**

**0. Method (read-only characterization first; ORIG evidence-only distances, nothing copied).** Read 97 brief, then 68 + 79 + 85 Comments (ruled-out paths not repeated without a new variable), then 89 Comments (fused-C regime note), then the C bar (39: ORIG C 4/4+5/5 vs fresh 0/3+0/3; S24 state of the art 2/3+1/3 per 73/74). Fresh = pota39_bundle_C (t39 pipe); ORIG = sfs_main/original_samples. NEW work dir /data/gpfs/projects/punim2657/pota97_repro/ (p97_char.py, p97_sep.py, p97_render.py, 2 PNGs, md5 manifests). GT-seating convention = gate73.py verbatim (each bundle at its own GT T; validated by C03 seating 0.95/86.8 here). Source-breakline md5s recorded in p97_source_guard.md5 (C01-Bl0 e1e59cdf..., full list in work dir); sources untouched. Laptop mirror artifacts/pota97/ (p97_char.py, p97_sep.py, p97_render.py, p97_numbers.txt, 2 PNGs).

**1. Stage 1 — fusion characterization (GT-seated fresh-vs-ORIG, med mm / <2mm %).**
Counts fresh/ORIG Bl_0: C01 402/211, C02 267/221, C03 167/191, C04 191/131. Bl_1: C01 92/230, C02 203/313, C03 114/120, C04 115/146.
Swap table (file level, GT): C01 F0-O0 5.61/22.9, F0-O1 5.96/25.4, F1-O0 46.54/0, F1-O1 47.96/0 (FUSED/SHREDDED — both slots miss); C02 F0-O0 6.07/0, F0-O1 0.95/94.4, F1-O0 0.78/98.5, F1-O1 6.00/0 (clean SWAP); C03 F0-O0 0.95/86.8, F1-O1 0.89/90.4 (clean control); C04 F0-O0 5.48/5.8, F0-O1 0.75/91.1, F1-O0 0.73/93.0, F1-O1 5.64/0 (clean SWAP).
Bl_0 branch points (file order, jumps>5mm): C01 idx 10 (56.8mm), 39 (65.5), 191 (105.0) — runs [0,10)/[10,39,29-pt spur]/[39,191,152]/[191,402,211); C02 idx 20 (5.8), 37 (112.7), 100 (68.6) — runs [0,20)/[20,37)/[37,100,63)/[100,267,167); C03 idx 40 (14.2) only — runs [0,40,0.73/100%]/[40,167,1.04/82.7%]; C04 idx 134 (48.2), 182 (6.6) — runs [0,134,5.47/0%]/[134,182,48-pt 5.68/4.2%]/[182,191,9-pt nub 0.78/100%].
Fusion constrictions (non-consecutive pairs <2mm, branch candidates): C01 5: (0,190),(38,191),(39,401),(261,294),(261,295) — the two parallel loops touch at fold points adjacent to jumps 39/191; C02 3: (0,99),(36,100),(37,266); C03 1: (0,166) closure; C04 74 starting (0,133),(4,180),(5,178-181),(6,177) — the 48-pt [134,182) fold-back rides ON [0,134).
Per-run vs ORIG Bl_0 (GT): C01 [39,191) 5.45/28.9%, [191,402) 5.76/22.7%, spur [10,39) 27.21/0% — neither radius-match nor count-match loop sits on-contour (confirms 68 GT-seat); C02 all runs 5.95-6.13/0%; C04 [0,134) 5.47/0%. ORIG->freshFULL reverse: C01 2.53/43.6%, C02 5.95/0%, C03 1.04/83.2%, C04 5.32/8.4%.
Renders eye-checked: artifacts/pota97/C97_C01_fused_vs_ORIG.png (red fused walk crisscrossing gray ORIG ring, black chords at 10/39/191; right panel: touch-split comps each offset from ORIG) and C97_C0204_swap_vs_ORIG.png (red fresh Bl_0 tracking black ORIG Bl_1 on C02 with teleport chords, tightly on C04).

**2. Stage 2 — separation (ONE new variable vs 68: split at touch constrictions, not gaps).** C01 Bl_0 cut at jumps {10,39,191} PLUS all touch constrictions -> cuts (0,10,38,39,190,191,261,294,295,401,402), 6 components >=5pts. Fresh-only lip-face select (mean distance to Surface_0, zero ORIG input): comps (39,190) n=151 S0 1.77; (191,261) n=70 S0 2.09; (295,401) n=106 S0 3.13 (aerial spur); (261,294) n=33; (10,38) n=28 S0 23.84 (debris); (0,10) n=10 S0 1.21 (frag). Gate vs ORIG (evidence-only): (39,190) 5.48/29.1%, (191,261) 3.28/30.0%, (295,401) 34.38/20.8%, (261,294) 5.33/15.2%, (10,38) 28.08/0%, (0,10) 3.58/0% — ALL medians >2mm (best 3.28mm). Fresh-only rule picks the n=10 frag. GATE FAILS -> no variant bundle built (nothing to land), no E2E per Rules. Not a repeat of 68 (gap split + radius-inner/S-count select): different cut set (touch constrictions are the new variable), finer granularity, same NULL with mechanism — the loops themselves are off-lip, so no partition of the file can sit on-contour. Consistent with 71 ceilings (no face holds a full on-contour loop: C01 walk-input 39% partial arc max, C02/C04 0%).

**3. No E2E (gate-gated, correctly skipped).** Bar for reference: ORIG C 4/4+5/5 (39), S24 branch-route 2/3+1/3 x3 with 17.37mm floor (73/74). This ticket's separation does not meet its <2mm gate, so Stage 3 was not opened; no job IDs (screening-only per 64/69/70/71 precedent). Controls N/A without E2E.

**4. Spartan leftovers:** pota97_repro/ only (3 scripts + 2 PNGs + 2 md5 files). 39/68/73/74 lanes untouched (read-only; source md5s verified unchanged). No prep/assembly source touched; SingleOverlapTest@100 / RP / CheckGraph-150 untouched. COMMIT NOTHING.

**Successor proposal for lead:** (a) C02/C04 need no separation work — S24 already routes their clean swapped loops (this ticket's swap table is the cleanest statement of that: F0-O1 0.95/94.4 and 0.75/91.1); the open item there is the 17mm overlap-valley floor (74/76/77 family), not content. (b) C01 content regeneration is upstream of any file-level repair (walk input holds at most a 39-pt on-contour partial arc per 71/74 ceilings; touch-split confirms at component level) — next variable is mesh->sample resampling at the lip or boundary-detection input density per face, not walk/split/radius/face/smoothing (69/70/71/79/85 exhaust those). (c) Quote 2/3+1/3 WITH the 17.37mm single-axis-slide caveat per 74 if C is cited in the thesis.
