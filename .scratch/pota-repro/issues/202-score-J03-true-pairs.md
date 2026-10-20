# 202 - Score J03\u2019s true pairs: thin vs ORIG duet (laptop leg)

Status: landed (lead 2026-10-20: INPUT EXONERATED TO SEARCH -- all 3 true pairs SAME thin-vs-ORIG, no killing gate; J03 dies in generation/pruning)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User decision (m04694, option 1). 201 exonerated J03\u2019s loop solo (words 0.556 = C01 level) yet J03 stays unseated (193). A join is a duet: the true edges (1,3),(3,6),(3,7) (92 \u00a74) need the mating rims (J01/J06/J07) to agree. Score, LAPTOP-SIDE, the true pairs with J03-thin vs J03-ORIG against the SAME neighbour loops. No E2E, assembler untouched (user freeze ruling stands).

## Legs (all laptop-side, numpy, read-only inputs; reuse .scratch/pota201_repro/ replication, cited source lines only)
1. Pair scores: replicate the assembler\u2019s pairwise match score (LCS + Cond1-4 incl. thickness, same cited lines as 201) for pairs (1,3),(3,6),(3,7) in two versions: neighbour-vs-J03-thin and neighbour-vs-J03-ORIG. Neighbour loops = the exact SXC bundle loops from 193 (J01/J06/J07 as seated in J_THIN). Report per-pair: score_thin, score_ORIG, delta, and rank of the true hypothesis among sampled wrong partners (same J03 vs 3+ wrong neighbours) in both versions.
2. Verdict per pair: SAME (thin duet scores like ORIG duet -- input fully exonerated, J03 is assembly-search) vs WORSE (thin duet scores worse despite matching solo words -- second input mechanism at pair level; name which gate kills it: LCS run, Cond4/thickness, veto).
3. Cross verdict: does pair scoring explain unseated-while-words-match? If all three pairs score SAME yet J03 unseats, the death is generation/pruning (beam never proposes or kills early) -- state this explicitly as the handoff to an assembly-search ticket.

## Boundary
Laptop only. Inputs read-only: 193 bundle loops (SXC + thin J03), ORIG loops, J meshes, pinned SFS++ source. Scripts + numbers under .scratch/pota202_repro/ + artifacts/pota202/ (untracked). Do NOT touch tracked files except this ticket. COMMIT NOTHING.

## Constraints
Same neighbour loops both versions -- the ONLY change is J03\u2019s loop (thin vs ORIG). Cite the matcher score source lines; no reimplementation from memory. No sbatch, no bundles, no E2E.

## Acceptance
Per-pair table (score_thin, score_ORIG, delta, true-vs-wrong rank both versions) + per-pair SAME/WORSE verdict with killing gate named + cross verdict (input-exonerated-to-search vs pair-level mechanism found).

## Required evidence
Comments: script paths, cited source lines, per-pair table, verdicts. Final output: same, self-contained.

## Comments (worker, 2026-10-20 -- LAPTOP ONLY; COMMIT NOTHING)

**Cross verdict: INPUT EXONERATED TO SEARCH. All three true pairs score SAME (thin duet = ORIG duet within noise); no pair-level gate kills the thin loop. J03's death (placed-but-wrong under doubled rim in 92, unplaced under thin rim in 193, despite solo words 0.556 = C01 level in 201) is generation/pruning -- the beam never proposes a surviving J03 hypothesis or kills it early. Handoff: this needs an assembly-search ticket (hypothesis inventory for J03 pairs in T_J_THIN vs T_J_orig), not rim work.**

**1. Inputs (read-only; same neighbours both versions, ONLY J03's loop changes).**
Neighbour loops = J_THIN bundle Bl_0 from 193's E2E fetch (`artifacts/pota193/pota193_fetch_33486061.tgz` -> extracted read-only to `.scratch/pota202_repro/pota193_fetch/rims_JTHIN/`): J01 md5 `c03fe021` n=201, J06 `b06ac589` n=130, J07 `c59cb413` n=113. J03-thin = bundle Bl_0 md5 `242bf342` n=178 (byte-identical to installed p193 loop `.scratch/pota193_repro/Pot_J_Piece_03_Breakline_0.p193.pcd`). J03-ORIG = `.scratch/pota193_repro/J03_ORIG_Bl0.pcd` md5 `e05f32c8` n=189 (201's auth loop). Meshes `temp_download/Mesh/Pot_J/Pot_J_Piece_0{1,3,6,7}_Mesh_DS.obj` (+02/04/05/08/10/11 for wrong partners). True edges (1,3),(3,6),(3,7) per 92 section 4.

**2. Method (verbatim 201 replication, no reimplementation from memory).** Script `.scratch/pota202_repro/p202_main.py` imports `p201_lib` (compute_features/quantize/longest_run/get_thickness). Cited lines, pinned source `structure-from-sherds-pp` (cure-potA vehicle lineage): `class/feature_matching.cpp:72-95` Quantization (Q=x-fmod(x,y)), `:215-320` LCS (Cond1-4 + windowsize + rim veto + Clustering-20), `:1479-1490` FeatureComp Q_size (0.15/0.15/0.15/0.2), `class/filter.cpp:77-113/50-75/116-160/161-226/228-265` feature pipeline + GetThickness, `class/data_structure.cpp:227-254` seg-flag parse, `main.cpp:108-114` NO_BASE_INFO. Score = longest Cond1-3 run (LCS) + Cond4-inclusive run (thickness, mesh-vert proxy -- same documented deviation as 201), max of fwd/rev orientations. Wrong partners: J03 (same variant) vs 6 wrong Bl_0 neighbours (J02/J04/J05/J08/J10/J11); rank = position of true pair among 7. Numbers: `.scratch/pota202_repro/p202_numbers.json`.

**3. Per-pair table (score_thin, score_ORIG, delta, rank both versions; n/m = loop lengths).**

| pair | version | LCS run (cov) | Cond4 run (cov) | rank /7 | cond4 rank /7 | wrong-partner LCS runs (J02/J04/J05/J08/J10/J11) |
|---|---|---|---|---|---|---|
| (1,3) | thin (178x201) | 13 (0.073) | 7 (0.039) | 6 | 4 | 19/21/21/18/19/10 |
| (1,3) | ORIG (189x201) | 15 (0.079) | 6 (0.032) | 6 | 4 | 18/25/21/17/19/14 |
| (3,6) | thin (178x130) | 20 (0.154) | 7 (0.054) | 3 | 4 | same wrongs as above |
| (3,6) | ORIG (189x130) | 22 (0.169) | 7 (0.054) | 2 | 4 | same wrongs as above |
| (3,7) | thin (178x113) | 18 (0.159) | 9 (0.080) | 5 | 1 | same wrongs as above |
| (3,7) | ORIG (189x113) | 18 (0.159) | 10 (0.088) | 4 | 3 | same wrongs as above |

Deltas (thin-ORIG): (1,3) run -2 / cond4 +1; (3,6) -2 / 0; (3,7) 0 / -1.

**4. Per-pair verdicts: SAME x3.** No gate kills the thin duet: LCS runs track ORIG within 2 (noise on runs of 13-22), Cond4 within 1, ranks move by at most 1 place. Veto: absent both versions (all seg flags 0 in every loop used; `is_seg_rim_=false` both -- `feature_matching.cpp:227-243` gate never arms). Base-skip (`feature_matching.cpp:1507-1512`): never fires either version -- all fresh/thin Bl_0 headers carry info_index=0, and although ORIG J03 carries info_index=2 (base), no neighbour is base, so the sane_base+base skip condition is unsatisfiable both ways (`main.cpp:108-114` NO_BASE_INFO clears it belt-and-braces).

**5. Why this exonerates the input (read carefully).** Even the ORIG true pairs rank mid-pack on whole-loop LCS (ranks 2-6/7, cond4 ranks 3-4/7) -- yet they seat in J_orig E2E (8/11+16/21, 193 section 4). So seating is decided downstream of whole-loop LCS (Clustering-20/no-overrange/geometric verification/beam), and the thin loop behaves identically to ORIG at every pair-level gate measured here. Pair scoring therefore cannot explain unseated-while-words-match. The death is generation/pruning: the beam never proposes a surviving J03 hypothesis from the thin duet (or kills it early) despite LCS runs (13-20, all > windowsize 6) that clear the hypothesis floor. Next step belongs to an assembly-search ticket: inventory J03-pair hypotheses in `T_J_THIN` vs `T_J_orig` (both in the 193 fetch tgz) and find where the true hypotheses go missing.

Caveats: whole-loop longest-run proxy (no Clustering-20, NoOverrange, or downstream geometric check -- relative thin-vs-ORIG comparison is apples-to-apples regardless); thickness via mesh-vert proxy (201's documented deviation; cond4 leg inconclusive as driver per 201, consistent here); wrong set is Bl_0 neighbours only.

