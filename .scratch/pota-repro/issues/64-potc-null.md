# 64: Pot C null diagnosis — why zero, when A scores full marks

**What to deliver:** the measured reason Pot C fresh seats 0/3+0/3 while the same chain scores 8/8+15/15 on A — prep, search, or material.

**Answers:** E1

**Blocked by:** 61 (C: ORIG 4/4+5/5 ×3 green; fresh flagged 0/3+0/3 ×3, forest 307 pruned 7–8; seated [] ×3; P3 UNPLACED; 5 GT edges off 360–730mm; ceiling 0) + 39 (C unflagged baseline also 0/3+0/3 — flagging is NOT the cause on C) + 41 (B-diagnosis pattern: kill-site per true edge) + census (C per-pot counts in ticket 01).

**Status:** results-in — DIAGNOSED (prep rims: Bl0 ordering teleports on all 4 C pieces kill every GT edge; search/vehicle/reference/measurement exonerated; screening-only, no new jobs)

**Starting position:** C is the extreme case: same vehicle, same chain, A perfect, C null. Candidate causes: (a) PREP — C rims fail the gate or C axles wrong (check: gate per-edge strict on C fresh rims; axle errors vs shipped); (b) SEARCH — true edges die in filtering (forest 307 vs ORIG's?; pruned only 7–8 — where do the 5 GT edges die: RP, pairwise, beam?); (c) MATERIAL — C03 ingest-off (denominator already excludes it); small pot (3 scored pieces?) so one kill = total zero; P3 UNPLACED (refusal — why?). Bundle reference: pota39 C bundle + pota61 C flagged bundle (read-only); C census counts in issues/01. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** diagnosis FIRST (login-node screening per T53 precedent; E2E only to confirm a mechanism); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 for any E2E claim.

- [x] Gate + axle check on C fresh (prep verdict per piece)
- [x] Kill-site per GT edge (where each true edge dies, with numbers)
- [x] P3-unplaced reason (refusal statistics)
- [x] Verdict: prep / search / material — with the single binding cause if one exists
- [x] Job IDs + sacct states (or explicit screening-only)

## Comments (worker, 2026-10-17, COMMIT NOTHING — screening-only, no new jobs)

**Verdict: category 1 — the method genuinely failed (fresh preprocessing rims), same family as Pot B (ticket 41). Fresh C Bl_0 polylines carry mid-run ordering teleports on all 4 pieces (up to 113mm; ORIG ≤4mm), collapsing every GT edge at the gate (fresh 0,1,4,0,16 vs ORIG 34–73) and killing 2 of 5 edges at SingleOverlapTest@100 (areas 128 and 1714 vs ORIG 0–4). The small pot (3 scored pieces) amplifies the rim defect to a total zero, but is NOT the cause. Search, vehicle, reference and our measurement are exonerated with numbers. C02's axle miss (59°) is a secondary prep defect, not the binding cause (the two good-axle pieces seat 0 anyway). Flagging is NOT the cause (1 strict flag on the refused piece only; unflagged arms score identically 0/3).**

**0. Method notes.** Assembly loads ONLY Breakline_0 per piece (P41 §0) — all probes use Bl_0. Overlap numbers are the faithful numpy port of OverlapCheck_3d P41 validated on Pot B (MakeCorWOTree+DetectIntersection+SortRegion, region<10/centroid<5 rules, threshold 100). Gate is the p39 A→B strict rule (d<2mm & |n·n|>0.85, dedup) at GT seating. No source edits anywhere; no new Spartan jobs; 39/61 lanes read-only; original flaggers untouched.

**1. Gate + axle per piece (prep verdicts).**
- Teleports (consecutive jumps >5mm, mid-run; fresh vs ORIG Bl_0): C01 3 (max 105.0mm: 56.8/65.5/105.0) vs 0; C02 3 (max 112.7: 5.8/112.7/68.6) vs 0; C03 1 (14.2) vs 0; C04 2 (48.2/6.6) vs 0. Fresh Bl_1 clean (0 mid-run); ORIG Bl_0/Bl_1 clean (max ≤4.2, boundary jumps only). Same ordering defect as B (8/9 Bl_0) and A-p3/p4/p5.
- Gate per GT edge at GT seating (Bl_0, fresh vs ORIG): 1-2: 0/34; 1-3: 1/72; 1-4: 4/40; 2-3: 0/73; 2-4: 16/55. Fresh collapses everywhere (matches 39's full-rim gate 3/5 with 1-2=0). ORIG passes all 5 by 34–73.
- Axles (authoritative P10/P18 records, not recomputed): C01 ADMITTED (1.204/0.380) dirpass PASS (0.06°) — GOOD; C02 ADMITTED (1.414/0.281) dirpass FAIL (59.17°; p39 run 42.52°) — BAD (count/landscape-miss family, healthy support, wrong mode); C03 REFUSED (1.619/0.159, cost>1.40 AND share<0.22) chain-skipped — OFF; C04 ADMITTED (1.215/0.367) dirpass PASS (1.28°) — GOOD. C05/C06 pass but outside vehicle blocks (not piped).
- Per-piece prep verdict: C01 good axle + corrupt rims; C02 bad axle + corrupt rims; C03 refused + corrupt rims; C04 good axle + corrupt rims. Rims condemn all 4; axle condemns C02 additionally.

**2. Kill-site per GT edge (graph: 1-2,1-3,1-4,2-3,2-4; C03 = piece 3, 2 edges).**
- Overlap at GT seating Bl_0 (fresh kill?/area vs ORIG area): 1-2 PASS/0 vs 2; 1-3 KILL/128 vs 0; 1-4 KILL/1714 vs 4; 2-3 PASS/0 vs 4; 2-4 PASS/4 vs 0. Fresh kills 2/5; ORIG kills 0/5 (areas 0–4).
- (1,3): dead three ways — upstream refusal (C03 off) + overlap kill (128, 1.3× gate) + gate 1/72.
- (2,3): upstream refusal + gate 0/73 (overlap would pass, never reached — starvation).
- (1,2): gate 0/34 (zero rim support → pairwise/RP starvation; overlap passes at GT so the terminal gate is NOT the killer — dies upstream) + C02 axle miss compounds.
- (1,4): gate 4/40 (weak) + overlap kill 1714 (17× gate) — terminal-gate kill.
- (2,4): gate 16/55 (weakest pass) + overlap passes (4) → dies in beam filtering (forest 307→8, wrong graphs win); E2E error 370mm/3.06rad + C02 axle miss compounds.
- Forest/prune (binary logs): fresh 307/8 (61 R1; 39 unflagged 307/7, 307/9) vs ORIG 125/40. Fresh keeps 2.6%, ORIG 32%. E2E wrong-edge errors (recompute, all flung, no near-misses): (1,2) 726mm/3.07rad, (1,3) 676/2.66, (1,4) 600/2.47, (2,3) 654/2.91, (2,4) 370/3.06 — the 360–730mm of the starting position.
- Renders (both eye-checked): `artifacts/pota64_C/pota64_c01_teleports.png` (fresh C01 Bl_0 at GT crisscrossed by 3 red teleport chords 57/66/105mm vs ORIG clean loop — the defect seen directly); `artifacts/pota61/pota61_seating_C_C1.png` re-verified (gray GT ring coherent, red fresh flung, P1/P2/P4 MISS, P3 UNPLACED).

**3. P3-unplaced reason.** T_fresh holds T_0,T_1,T_3 — T_2 (C03) never written: refused piece carries an empty axle file → shard_on_off=false → never placed → binary excludes it from the denom (0/3, not 0/4; recompute on the n=4 universe scores 0/4+0/5). Refusal stats (P18 C): C03 cost 1.619/share 0.159 — H-type low-support family. Strictly a false refusal (P10: C03 dirpass PASS 0.60°, one of 18's 3/117), but harmless: C03's rims are corrupt (gate 1/72, overlap kill 128), so it could not seat anyway. Refusal auto-exclusion works as designed.

**4. Three-category verdict: (1) genuinely-failed method.** Deciding number: **2 of 5 GT-true edges exceed SingleOverlapTest@100 at GT seating on fresh rims (128, 1714) vs 0 of 5 on ORIG rims (0–4) — same poses, same code, same threshold — and the other 3 edges carry gate support 0/34, 0/73, 16/55 vs ORIG 34–73.** Exonerated: search (ORIG 4/4+5/5 ×3 same binary, all gates passable), vehicle (cure-potA @ bffefb6 ORIG-valid green ×3), reference (GT+graph seat ORIG fine), our measurement (port validated on B; Bl_0-only semantics verified in source; ORIG recompute = binary exactly), flagging (scored pieces carry ZERO flags, layout-match 0/8; 39 unflagged 0/3 ×2 = 61 flagged 0/3 ×3). Material (3 scored pieces) amplifies but does not cause. NOT claimed: per-site RP/CheckGraph/profile-veto splits (need P26DIAG-pattern instrumentation, barred here by the screening-only mandate — same limitation as P41).

**5. Jobs (sacct State/ExitCode, all COMPLETED 0:0, polled directly — screening-only, none cut by me).** Flag 33266319 (C, 7s); 61 stages 33266388 (fresh 307/8→0/3+0/3, ORIG 125/40→4/4+5/5), 33266454, 33266456 (same tallies ×3); 39 unflagged stages 33200136, 33200139 (fresh 307/7, 307/9→0/3+0/3 ×2). Laptop probes: `artifacts/pota64_C/p64_render.py` + PNG; fetch extract `artifacts/pota61/fetch_C_R1/` (tgz pre-existing). Spartan leftovers: none (read-only; no scratch written).

**Successor proposal for lead:** rim-content fix ticket (Bl_0 ordering repair C01/C02/C04+C03, C02 axle-mode, same fix family as P41's B successor), then gate + E2E rerun; optional P26DIAG-pattern instrumentation on C first for measured RP/CheckGraph/profile splits. Do NOT relax SingleOverlapTest@100, RP axis/score gates, or CheckGraph-150 — ORIG proves all gates passable. Ceiling for C under any search-only change: 0 (nothing to attribute; rims bind every edge).

**Starting position:** C is the extreme case: same vehicle, same chain, A perfect, C null. Candidate causes: (a) PREP — C rims fail the gate or C axles wrong (check: gate per-edge strict on C fresh rims; axle errors vs shipped); (b) SEARCH — true edges die in filtering (forest 307 vs ORIG's?; pruned only 7–8 — where do the 5 GT edges die: RP, pairwise, beam?); (c) MATERIAL — C03 ingest-off (denominator already excludes it); small pot (3 scored pieces?) so one kill = total zero; P3 UNPLACED (refusal — why?). Bundle reference: pota39 C bundle + pota61 C flagged bundle (read-only); C census counts in issues/01. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** diagnosis FIRST (login-node screening per T53 precedent; E2E only to confirm a mechanism); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 for any E2E claim.

- [ ] Gate + axle check on C fresh (prep verdict per piece)
- [ ] Kill-site per GT edge (where each true edge dies, with numbers)
- [ ] P3-unplaced reason (refusal statistics)
- [ ] Verdict: prep / search / material — with the single binding cause if one exists
- [ ] Job IDs + sacct states (or explicit screening-only)

**Successor:** remedy ticket per verdict (C is small — the fix may be one kill-site).
