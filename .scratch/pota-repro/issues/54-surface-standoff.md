# 54: Surface standoff — reshape the wall so it stands off the rim

**What to deliver:** a p2 Surface_1 that stands off the rim like ORIG — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 53 (our p2 S1 hugs rim ~0.5mm noisy → 66% valid thickness vs 97%, med shift 1.2mm > 0.8mm Cond4 gate; p1 fine; SURFNORM destructive; trim refuted; point levers EXHAUSTED) + 21 (T21 split precedent — RegionGrowing fusion class fix) + 50 (gap corridor sheet — no new material; reshape existing).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the wall EXISTS (8001 pts) but sits wrong: noisy contact with the rim where ORIG keeps a structured standoff. This is pipeline-side surface regeneration work, not point editing: candidates include RegionGrowing parameter/merge behaviour on B-p2 (cf. T21 cluster split), surface denoising/smoothing that preserves the rim (50 proved raw sampling is matcher signal — do NOT resample the rim), re-fitting S1 from the mesh with standoff. Render reference: artifacts/t53_p2_surfrim.png (ours crowds, ORIG stands off). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with valid-thickness recovery toward ORIG (97% valid, med ~2.9) AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Standoff measurement + reshape arms, one variable each
- [x] Thickness/strength/E2E lift or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: measured why-not — no lift. Surface smoothing cannot recover the standoff because the wall is not the defect: OUR p2 sheets sit ON ORIG's sheets (NN med 0.34mm both walls) while OUR rim runs mid-wall between them (~1.1mm off ORIG rim, bad thickness flags spread over the whole run, not the tail). The ticket's premise (reshape the wall) is refuted by composition evidence; the defect is rim-walk lateral position (T50 proved length/existence, position remains wrong). SMOOTH-class arms move validity and median in opposite directions with no ORIG-like joint point; the strongest smooth silences Cond4 vetoes but E2E 3/3 shows the honest 2-1 edge still absent with controls green.**

**Standoff measurement (T50-base bundle = honest-best start; ORIG evidence-only, zero ORIG points used):**
- Rim→S1 nearest: OURS med 0.64mm (67% < 1mm, hugging) vs ORIG med 2.87mm (13% < 1mm, structured standoff). Thickness: 124/187 (66%), med 1.73 vs 146/150 (97%), med 2.90 — reproduces T53 on the T50 base.
- Composition (native-frame NN, frames verified same via rim med 1.08): OUR-S1 ≈ ORIG-S0 (med 0.34, 87% within 1mm); OUR-S0 ≈ ORIG-S1 (med 0.34, 88% within 1mm). Labels swapped vs ORIG (known T04-exchange, T21 note c) but sheets well-registered — the wall sits RIGHT.
- Rim at GT seating: OUR→ORIG med 1.08, mean 1.28, mean-disp |mag| 0.77 (partly systematic); OUR rim threads BETWEEN the sheets (Bl0→S0 med 1.78 AND →S1 med 1.73) where ORIG rim grazes inner (0.26) and spans outer (2.90). Bad-thickness indices spread idx 1–186 (whole run), not the tail.
- Eye-checked render `SfSpp_preprocessing/artifacts/t54_anatomy.png`: ORIG rim rides the sheet edge; OUR rim cuts mid-sheet; GT-seated overlay shows shared bottom arc with the top loop cut across (per-index dist 2.5–4mm idx 0–20, ~0.5–2 noisy mid-run).
- T42base is a strict subset of the rewalked rim (revert-to-base meaningless: identity FALSE, T50 was a full rewalk, not base+append).

**Offline arm screening (OUR-side only, rim byte-identical throughout):**
- FLIP (p2 Bl0 normals → negated): REFUTED — valid 124→56/187, med 0.23 (rays hit inner graze). Not a global orientation fault.
- SWAP-label (read OUR-S0 as outer): REFUTED — valid 101/187 (54%), med 1.78. Neither sheet gives ORIG-like stats because the rim sits between them.
- SMOOTH (Laplacian kNN, rim untouched): MILD-5x0.3 → 111/187, med 1.69 (worse); MID-10x0.4 → 35/187, med 2.24, standoff-med 2.03; STRONG-20x0.5 → 14/187, med 3.37, Cond4-proxy 20.9% (≈ORIG 25.6%). Monotonic: smoothing shrinks the sheet away (validity collapses while survivor median rises) — no joint ORIG-like point exists. STRONG's proxy lift is the vacuous-invalid artifact T53 discredited (93% invalid pass Cond4 with no discrimination), so it went to E2E as a veto-silence probe, not a landing candidate.
- Gate: unchanged by construction (all Breakline content-hashes identical BASE vs STRONG, 057d4b00…; surfaces don't enter the gate probe).

**Arm STRONG E2E ×3** (cure-potA @ bffefb6 asserted, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserted, B-bundle-match asserted; all sacct COMPLETED 0:0):
| jobs | B fresh | controls (same runs) |
|---|---|---|
| 33244793 (18:16), 33256245 (12:38), 33256243 (~14:00) | 4/9 + 2/15 ×3 identical, seated {1,3,4,7}, VERBOSE pairs {1-3,1-4,3-7}, p2 ok_edges=0 — honest 2-1 edge ABSENT 3/3 | B ORIG 9/9+15/15, A ORIG + A fresh 8/8+15/15 ×3 |
- Veto-silence hypothesis REFUTED: removing false Cond4 vetoes does not admit the true edge — discrimination lives elsewhere (sequence/normals per T50), and the edge stays starved at max inlier 16 (non-admitted 2-x candidates only).
- Render `SfSpp_preprocessing/artifacts/t54_strong_check.png`: STRONG sheet keeps wall shape (no collapse), still threads the rim. Eye-checked.

**Successor:** the fault is rim-walk lateral position on B-p2 (walk rides mid-wall, cuts the top loop) — a rim-path ticket building on T50 (which settled length/existence): re-seat the Bl0 walk laterally toward the lip edge estimated from OUR surfaces alone (no ORIG points, no resampling of point spacing). Surface-side levers (smooth/swap/flip/trim/normals) are now all measured-dead. Work dir `/data/gpfs/projects/punim2657/pota54_repro/` (measure/discriminate/composition/rimshift/fliptest/smooth/render scripts, BASE + STRONG bundles + md5s, sbatch, 3 slurm outs); tickets 49/50/51/52/53 + p47/p49 flaggers untouched (read-only).

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
