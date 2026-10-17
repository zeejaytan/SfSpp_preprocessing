# 66: True C point-reorder repair — re-walk, not re-label

**What to deliver:** C Bl_0 point orders without teleports — E2E above zero.

**Answers:** E1

**Blocked by:** 65 (Arm-S header-regroup PROVEN no-op: same points+order, teleports 3/3/1/2 intact, E2E 0/3+0/3 ×3 bit-identical; headers invisible to binary via `is_seg_rim_` false path; jobs 33276193/33276355/33276356 COMPLETED) + 64 (teleports ≤113mm on all 4 C pieces; C02 axle 59° miss secondary) + 27 (T24-pattern: the Pot A cure re-walked/skipped at the walk level).

**Status:** results-in — TRUE reorder does NOT repair (jumps→0 achieved, gate no recovery, E2E 0/3+0/3 ×3 bit-identical; CONTENT binds, not order — category 1 stands, mechanism refined)

**Starting position:** the leaps live in POINT ORDER, not labels. True repair re-walks each C Bl_0 the way the ticket-27 cure did for A: nearest-neighbour continuation along the walk, splitting decorative appends (T14-family) from the true loop, emitting reordered points + fresh contiguity headers. Bundle reference: pota65 repaired bundle + pota39 C bundle (read-only); C02 axle-mode still open (measure walk-caused vs finder-caused). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with consecutive-jump count → 0 in emitted order AND gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Re-walk arms on C Bl_0, one variable each
- [x] C02 axle-mode verdict
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17 — COMMIT NOTHING; lead to commit)

**Verdict: the TRUE point-reorder repair is measured and does NOT land — jumps→0 achieved on all 4 pieces, but gate shows zero recovery and E2E seats 0/3+0/3 ×3 bit-identical with all controls green. The binding cause is rim CONTENT (fresh contours sit ~5mm off the shipped contour on C01/C02/C04), not point ORDER. Category 1 (method genuinely failed on these rims) stands with the mechanism refined: order was a co-symptom, never the cause on C. Ticket's own landing bar (gate recovery + E2E above 0) is NOT met — reported as measured why-not per the ticket's alternative.**

**0. Preliminaries (read-only; no other tickets' files touched).** Fresh bundle = `/data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_C/SfS_pp` (p39, read-only); Arm-S bundle = `/data/gpfs/projects/punim2657/pota65_repro/prep/pota65_bundle_C_S` (reference only). Work in NEW dir `/data/gpfs/projects/punim2657/pota66_repro/` (repair script `repair_bl0.py`, gate probe `gate66.py`, renders, `run_pota66_stage_AC.sbatch` = clone of the proven p65 vehicle script). TRUE ORIG = `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` (NOT `pota39_C/Dataset/` — that dir's breaklines are byte-identical to the fresh bundle including jumps, i.e. staged pipe copies, not the shipped control; T64's ORIG-0 readings came from `original_samples`).

**1. Re-walk arms (fresh-ONLY derivation; zero ORIG points in any fix — all repaired md5s differ from ORIG).**
- Stitch analysis on fresh sets alone: every file splits at its >5mm jumps into internally-clean runs; endpoint-adjacency (≤1.9mm links) yields a UNIQUE Hamiltonian chain per piece — C01 runs(1-10,11-39,40-191,192-402)→order run1,run3,run2,run0; C02 runs(1-20,21-37,38-100,101-267)→same pattern; C03 runs(1-40,41-167)→rotation run1,run0. Pure run permutation: no point altered, full rows (xyz+normals) kept intact.
- C04 append split (T27-pattern): runs R0 rows1-134 (file-order clean, max 2.26mm, count 134 ≈ ORIG 131) vs spur R1 rows135-182 + R2 rows183-191 (each walks clean alone, no clean attach to R0 under 6mm; greedy full-set walk strands 1×28.3mm jump). True loop = R0; spur split off. Render confirms spur doubling back on the loop's right side.
- Fresh headers rewritten single-segment `# 1 N 0` (flag 0 = same `is_seg_rim_`-false binary path as before; order is the only variable; axes md5-identical to fresh).
- Jump counts before→after: C01 3→0 (max 105.0→1.9mm), C02 3→0 (112.7→1.9), C03 1→0 (14.2→1.9), C04 2→0 (48.2→2.26). Set-preservation verified (sorted-row subset equality vs fresh).

**2. C02 axle-mode verdict: FINDER-caused, orthogonal to the walk (persists by construction).** Axes carried over byte-identical (md5-verified); the rim re-walk cannot touch finder inputs (finder consumes surfaces, not Bl_0 order). C02-involved gate edges unchanged by reorder (1-2: 0, 2-3: 0, 2-4: 16 — identical to fresh). T65's 61.0°/42.5° miss therefore stands unaddressed and is NOT walk-caused. Secondary defect regardless: good-axle pieces C01 (0.06°) / C04 (1.28°) seat 0 too; and C02's own contour sits ~6mm off shipped (191/221 ORIG points >5mm from fresh), so no axle alone could seat it. C03 axis still EMPTY (refused, still off).

**3. Gate: NO recovery (probe validated — my FRESH-baseline reproduces T64 exactly: 0/1/4/0/16).** Strict p39 rule (d<2mm & |n·n|>0.85, dedup, Bl_0 only) at GT seating, per edge (fresh vs ORIG per T64: 1-2: 0/34; 1-3: 1/72; 1-4: 4/40; 2-3: 0/73; 2-4: 16/55): REPAIRED gives 0/1/2/0/16. Edge 1-4 drops 4→2 (the cut C04 spur had carried 2 inliers). Cause measured: fresh CONTOURS are offset from shipped — fresh→ORIG medians C01 5.6mm / C02 6.1 / C04 5.5 (centroid alignment makes it worse: shapes differ, not frames); only C03 sits on-contour (~1mm) yet its edges still fail via the other sides. A 2mm gate cannot pass on 5mm-offset content at any order. Do NOT relax SingleOverlapTest@100 / RP / CheckGraph-150 (unchanged).

**4. E2E ×3 same-binary (cure-potA @ bffefb6, k=5/b=3, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK 4× per job, all jobs sacct COMPLETED 0:0, polled directly):**

| job | A_orig | A_fresh | C_orig | C_fixed (forest/pruned) |
|---|---|---|---|---|
| 33277750 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (350/20) |
| 33278681 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (350/20) |
| 33278682 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (350/21) |

Bit-identical tallies ×3 (deterministic binary): vehicle + A-fresh + C ORIG controls all green in the same runs. C_fixed T holds T_0,T_1,T_3 only — P3 still unplaced (refusal path unchanged). Repair moves forest 307→350 / pruned 7-8→20-21 (more hypotheses survive) but converts zero of them.

**5. Renders (all eye-checked).** `artifacts/pota66/repaired_C.png` (4 repaired rims, 0 jumps, rim scale resolved: C03 clean arc, C04 clean loop, C02 loop with doubled region, C01 402-pt winding with crossings but continuously ordered); `artifacts/pota66/cmp_C{01,03,04}.png` (fresh-vs-shipped: same loop region, extra windings/spur); `artifacts/pota66/pota66_seating_C_fixed_R1.png` (script `artifacts/pota66/p66_render.py`, fetch `artifacts/pota66/R1/`): left = C_fixed E2E seating, scattered tangle, seated centroids 37-78mm off GT (C01 63.5, C02 36.9, C04 78.0); right = same reordered rims at GT, roughly ring-coherent but splayed (content offset seen directly).

**6. Jobs (sacct State/ExitCode, polled directly).** 33277750 / 33278681 / 33278682 COMPLETED 0:0 (13-15 min each). RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota66_run_{33277750,33278681,33278682}/`; fetch tgz `pota66_fetch.tgz` in R1 (R2/R3 same tallies, no fetch pulled). Spartan leftovers: `pota66_repro/` only (repair bundle + scripts + sbatch; 39/40/65 lanes untouched).

**Successor proposal for lead:** the C fix must move rim CONTENT back onto the shipped contour (~5mm systematic offset on C01/C02/C04 — wrong lip edge / wrong contour height family, upstream of the walk in the prep chain), not re-sort points. C03 (on-contour, 1 jump) is the cleanest test of order-only repair and it still fails via its neighbours — corroborates content-binds. Suggest a prep-stage diagnosis ticket (which extraction step puts the C contour 5mm off: lip-face choice, resampling, or piece frame) before any further assembly-side work on C. E/I/J forests (same suspected disease) should check content-offset FIRST (fresh-vs-shipped contour distance) before any reorder attempt — ticket 66's negative result says reorder alone will not move them either.

**Successor:** roll the re-walk wherever teleports recur (E/I/J forests dwarf ORIG — same disease suspected).
