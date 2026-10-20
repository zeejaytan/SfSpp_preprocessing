# 195 - Thin-then-walk as default: non-regression on clean Pot D

Status: landed (lead 2026-10-20: REGRESSION verified -- D_195 10-11/27+8-11/66 x3 vs 84 bar 21-22/27+47-49/66, controls green, deterministic Total 4970; blanket thin-then-walk rejected for clean singles, third pot after B and A)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Same as 194 for Pot B: prove the full default chain HARMLESS on Pot D's clean single rims (29/29 per 188). Force-apply densify -> split -> thin+walk, bundle, E2E x3 vs 84's bar (22/27+49/66 lineage, cite exact 84 tallies).

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143 pre-step): measure dot spacing per D loop; if coarser than ~1.8mm, true mesh-sampled densify (ladder to saturation); midpoint interpolation FORBIDDEN (111/146). If already ~1.8mm, record numbers, close vacuous per loop.
1. Split (175 pre-step, read 175-two-walks-two-slots.md first): apply the 175 split-by-parent-surface rule to each clean single -- mesh-observable features only, no ORIG. Expect one face cloud each; two faces = new evidence, report it.
2. Thin: 185 v3 on each face cloud (P22 handled per 188's ruler-artifact note). Gate: closure <=2.0, single wrap, rim-truth med check-only (~0.51-0.86 per 188).
3. Falsifier (own in advance): any loop whose rim-truth worsens by >0.5mm vs unthinned input is REFUSED, not bundled.
4. Bundle: ONLY thinned Bl_0 slots changed (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (this carries every Pot A-diagnosis change: preprocessing T13/T21/T23/T24/T27 + assembler P22FIX/P22FIX2 + C2-restore per ticket 38 -- verify HEAD before building); same-binary ORIG control must reproduce its bar (84's ORIG arm) or the run is VOID. Upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier + byte-proofs + E2E x3 vs 84 + verdict.

## Required evidence
Ticket Comments + final output: loop gates, refused loops if any, md5s, job IDs, per-run tallies, verdict.

## Comments (worker 2026-10-20, E2E x3 complete)

### Verdict: REGRESSION -- the thin-then-walk default is HARMFUL on Pot D clean singles
The full chain ran end to end, controls are green, and the thinned bundle assembles far worse than the 84 bar on all three runs. Plainly: smoothing + uniform resampling kept every loop within ~1 mm of the rim, yet the assembler could no longer find the joins -- about two-thirds of the sherds 84 seated dropped out, reproducibly.

### E2E x3 vs 84 bar (jobs 33486437 / 33486440 / 33486442, all sacct COMPLETED 0:0)
Vehicle pinned: cure-potA @ bffefb6 clean. Same-binary ORIG control (D_orig arm) reproduces 84's ORIG arm, so no run is VOID.

| arm | Total (x3) | pruned (x3) | sherd /27or28 | edge /66 |
| D_195 run 1 (440) | 4970 | 893 | 10/27 | 11/66 |
| D_195 run 2 (437) | 4970 | 876 | 11/27 | 10/66 |
| D_195 run 3 (442) | 4970 | 859 | 11/27 | 8/66 |
| 84 bar (199/200/201) | 4586 | 913/914/904 | 22/21/22 | 49/47/49 |
| D_orig control (my x3) | 2445 | 890/887/889 | 23/23/22 /28 | 55/55/53 /66 |

84 bar exact: Total 4586 x3; pruned 913/914/904; sherd 22/21/22; edge 49/47/49. 84 same-vehicle ORIG: 23/23/22 + 55/55/53. Controls green x3: A_orig 8/8+15/15 exact, A_fresh 8/8+15/15 exact, D_orig matches 84 ORIG within run wobble. Build asserts green in all 12 arm logs (LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK, 3/3 per arm). Total 4970 is binary-identical x3 (deterministic pipeline); only seating wobbles +-1.

### Which pieces dropped (GT-identity recompute, 0.35 rad / 50 mm, global-frame aligned; binary Acc is authoritative, this names pieces)
Method validated on D_orig: 23/28 = Acc exactly. D_195 seated: run1 8 [D01,D02,D05,D07,D13,D19,D20,D27], run2 7 [D01,D02,D05,D07,D19,D20,D27], run3 6 [D01,D02,D05,D07,D10,D20]. Core survivors all 3 runs: D01,D02,D05,D07,D20. 84 seated but unseated in ALL THREE thinned runs (13 pieces): D04,D06,D08,D09,D11,D12,D14,D15,D16,D17,D21,D23,D24. Intermittent: D10 (1/3), D13 (1/3), D19 (2/3), D27 (2/3). The misses are far off (flipped/scattered, ang ~2-3 rad), not near-threshold -- stable under looser (0.5/100) thresholds. (Binary Acc counts ~3 more sherds than my strict recompute; scorer-threshold territory, verdict unchanged.)

### Chain legs (all gates held; the harm is in the thin step, not the plumbing)
- Step 0 densify: all 29 SXC Bl_0 loops already at 1.88-1.92 mm median spacing -- VACUOUS, no interpolation (p195_spacing.py, artifacts/pota195/).
- Step 1 split: face clouds inner+fold per 175 rule; large pieces 87-100% kept. Audit: excluded dots sit on the same loop (SAME-FACE); on small pieces wall labels scatter randomly along it (lip-label noise, no second face) -- new evidence, reported not pooled.
- Step 2 thin (185 v3): 27/29 kept, deltas -0.17..+0.24 mm rim-truth. REFUSED 3: D01 (loop gate -- all 6 seeds closure >2.0, best 6.83; the 240-pt cap does not scale to B01-size 574 mm loops), D22 (falsifier +4.927 -- polar binning collapses a non-star-shaped small loop; render confirms the walk chords across the C), D28 (falsifier +0.546, just over the 0.5 bar). Render eye-checked: artifacts/pota195/p195_face_thin.png.
- Bundle: BUILD DONE, veto ABSENT-OK; 26 thinned Bl_0 slots changed, D01/D22/D28 byte-identical (D01 md5 a9e364... both sides); diff -rq = 26 files, all Bl_0; 84-SXC base untouched ALL-OK. Manifests: pota195_D_195_BL_md5.txt, pota195_D_195_bun_md5.txt in /data/gpfs/projects/punim2657/pota195_repro/.
- Mechanism read: rim-truth preserved yet seating collapses 22->~11 and edges 49->~10, while Total hypotheses ROSE (4970 vs 4586). The loops are in the right place but no longer matchable: smoothing + uniform resample erases the fine breakline detail the matcher relies on. This is claim-type 1 (the method genuinely fails on this material), not a broken ruler: the ruler (rim-truth) reads fine and the failure replicates 3/3 with green controls. Supporting context: sibling186's doubled-strip thin SEATED (defect removal helps); sibling 194's Pot B full-loop thins independently collapsed the same way (B_194 2/9+1/15 vs 93's 6/9+5/15 -- sibling's result to confirm, mine stands alone).
- Implication for the default: thin-then-walk as a blanket default is rejected for clean singles. Its proven use stays defect-driven (doubling, B01-scale loops per 185's note). The 240-pt cap and polar-binning collapse on small/non-star-shaped loops are separate v3 limits worth fixing regardless.

### Paths
Spartan work: /data/gpfs/projects/punim2657/pota195_repro/ (p195_spacing.py, p195_split.py/.txt, p195_audit.py, p195_thinface.py/.txt, p195_build.py/.txt, p195_identities.py, p195_align.py, run_pota195_stage_AD.sbatch). Bundle: .../prep/pota84_bundle_D_SXC + D_195 overlay (26 .pcd). Runs: /data/gpfs/projects/punim2657/sfs_main/pota195_run_{33486437,33486440,33486442}/. Laptop mirror: C:/PR/SfSpp_preprocessing/artifacts/pota195/ (spacing/split/audit/thin/build scripts+logs, render). COMMITTED NOTHING (worker).

## Final output
REGRESSION, replicated 3/3 (jobs 33486437/33486440/33486442, COMPLETED 0:0): D_195 sherd 10-11/27 + edge 8-11/66 vs 84 bar 21-22/27 + 47-49/66. Controls green (A arms exact; D_orig 22-23/28 + 53-55/66 = 84 ORIG). 13 pieces 84 seated never seat thinned (D04,D06,D08,D09,D11,D12,D14,D15,D16,D17,D21,D23,D24); only D01,D02,D05,D07,D20 survive all 3 runs. Chain gates all held (3 refusals: D01 gate, D22/D28 falsifier); bundle byte-proven (26 Bl_0 only). Thin-then-walk as a blanket default is rejected for clean singles; keep it defect-driven.

## Lead verification (2026-10-20)
Worker tallies accepted: D_orig control reproduces 84 ORIG within wobble (23\/23\/22+55\/55\/53 vs 84 22\/21\/22+49\/47\/49), A arms exact, Total binary-identical 4970 x3. Lead-side sacct re-check not possible from this session (no Spartan key here); acceptance rests on in-ticket controls + build asserts + corroboration by landed siblings 194 (B) and 196 (A) with the same signature. Ledger F: third pot confirming DEFAULT REJECTED.
