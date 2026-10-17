# 52: Content-side strength — what each point says, not where it sits

**What to deliver:** honest edge strengths toward author scale — or the measured reason content cannot close the gap.

**Answers:** E1

**Blocked by:** 46-fingerprinting (R4: we write curvature ~0.05 where ORIG writes 1.0; one optimizer path reads the slot as thickness; H4 column-7 open) + 49 (R3 resample rejected — matcher keys off raw sampling/curvature columns; R1 done via T42) + 50 (sequence exhausted — gap is STRENGTH).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the honest 2-1 match exists (size9/inlier16) but scores 2-5× below the beam frontier; ORIG brings five edges at sizes 8-19/inliers 30-78. Open content questions: (a) curvature-slot semantics — what does ORIG's ~1.0 vs our ~0.05 do inside the LCS/matcher? (b) column-7: thickness or curvature — which reader, what effect? (c) per-point weight the matcher actually keys off (49 proved raw sampling matters). ORIG evidence-only (44-asterisk rule); zero ORIG points in any fix.

**Rules:** land ONLY with honest edge-strength lift toward ORIG scale AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + B gate 15/15; gate-clean (GT-placed strict must not regress); render (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Slot-semantics arms, one variable each
- [ ] Strength lift or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: no strength lift — measured why-not. Column-7 is dead (R4 killed, H4 answered); the live content path is normals→computed-thickness→Cond4, and smoothing it destroys the one honest edge. Honest 2-1 stays size9/inlier16 1-edge vs ORIG's five 2-1 edges sizes 8-19/inliers 30-78 measured in my own same-run controls.**

**Wire trace (assembler @ bffefb6, read-only): the file's 7th column never enters the pipeline.**
- `BreakLine::ReadPCDFileWithInfo` (`class/data_structure.cpp`) parses exactly 6 values per row (`x y z nx ny nz`); the curvature column is left in the stream buffer and discarded. Correction to 46-F1: raw ORIG col7 is NOT 1.0 — it is constant `1.905766e-42` (=0x550) in all shipped B Breaklines (A-orig identical except odd single 0/1 rows); fresh col7 is real curvature 0.001–1.0. Either way, dead on load.
- The "thickness slot" (`feature_[6]`) is live but file-independent: `CalculateFeatureAxisless` (`class/filter.cpp:187`) fills axis-0 row 6 via `GetThickness()` — point-to-outer-surface distance along the breakline normal, computed from OUR `sur_out_` + per-point normals — and later axes inherit that row. LCS `Cond4` (`feature_matching.cpp:277,389`) gates run agreement on quantized thickness (`|dQ3|<=4*Q_size[3]`, Q_size[3] fixed 0.2 in graph building).
- So R4 ("write 1.0 vs 0.05") cannot move anything; the content lever is normals/surfaces via GetThickness, not the column.

**Arms (base = T50 honest-lip bundle, 187-pt p2 Bl0; ZERO ORIG points; 17/18 files byte-identical to T50 in each arm, one file differs):**
- COL7: p2 Bl0 col7 → ORIG bit-pattern `1.905766e-42` (coords+normals identical). Gate: 592 strict, 15/15, 1-2 19/19 — carries T50 exactly.
- NORM: p2 Bl0 normals → ±1 box-smooth along run, renormalized (mean cos 0.967, min 0.08 at the segment-joint kink; coords+col7 identical). Gate: 589 strict, 15/15, 1-2 18/19 (one strict inlier lost — gate stays green).
- Renders `SfSpp_preprocessing/artifacts/pota52/t52_lip_check_*.png` (md5-identical pair 7aad3bc3): lip rows ride the p1 mating arc, continuous with patch — T50 eye-check carries (xyz-identical, proven by col md5).

**E2E ×3 per arm** (cure-potA @ bffefb6, BASE-env, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserted in-script, now with `|| exit 1` hardening; all sacct COMPLETED 0:0, ~13–16 min each):
| jobs | arm | B fresh | p2 | controls (same runs) |
|---|---|---|---|---|
| 33242373/74/75 | COL7 | 4/9+2/15 ×3 identical, seated {1,3,4,7}, forest 86 | 2-1 size9/inlier16/score 0.825671 ×3, bit-identical to T50 (score+axisang to 6 decimals) | B ORIG 9/9+15/15, A ORIG + A fresh 8/8+15/15 ×3 |
| 33242376/77/78 | NORM | 4/9+2/15 ×3 identical, seated {1,3,4,7}, forest 84 | 2-1 ABSENT 3/3; best honest 8-2 size9/inlier26 (vs T50 size11/inlier22) | all green ×3 |

**Slot-semantics findings.**
(1) Column-7: changing all 187 values to the ORIG constant moved NOTHING — not LCS edges, not scores (0.825671 both), not forest (86), not tallies. Dead column proven at runtime, confirming the wire trace. R4 REJECTED; H4 CLOSED.
(2) Normals are live content: ±1 smoothing killed the honest 2-1 edge 3/3 while leaving every non-p2 edge bit-identical — the matcher keys off per-point normals through the GetThickness→Cond4 path (consistent with 49-R3: it keys off raw sampling). The tested direction is destructive-only.
(3) Honest-vs-ORIG scale, same-binary evidence (my B_orig controls): ORIG 2-1 = FIVE edges (size19/inlier34, size11/38, size15/30, size10/36, size8/78); honest = ONE edge size9/inlier16. Max honest run anywhere stays size10-11/inlier ≤26 vs the 45–65 beam frontier — p2 starves deterministically 6/6.

**Procedural note:** first submission batch (jobs 33241805–10) went COMPLETED 0:0 in ~4 s — void, no data: my stage copy hardcoded the container-side `/workspace/pota50_run_` RUNDIR while the host used `pota52_run_*_` (cmake log path missing; the inherited script swallows container failure without `set -e`). Fixed the RUNDIR split, added `|| exit 1` to the four arm invocations in MY stage copies only, removed the 6 stale run dirs, resubmitted as 33242373–78. Assembler clone untouched (asserts verify bffefb6 + P22FIX/C2-0.436 + k=5/b=3 every run). Tickets 49/50/51, p47/p49 flaggers untouched (read-only).

**Successor:** content-side point levers are now exhausted in the constructive direction (sequence exhausted by 50, sampling by 49-R3, column-7 dead, normal-smoothing destructive). Remaining seats for p2 live beam-side (rerouting around the 45–65 frontier) or surface-side (better `sur_out_` → better GetThickness — 45/50 territory, not revisited here).
