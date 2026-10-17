# 68: Split-then-select repair — one loop, the inner one

**What to deliver:** C Bl_0 files holding a single inner-lip loop each — gate + E2E recovery.

**Answers:** E1

**Blocked by:** 67 (doubled-loop bound: C01 run2 152 + run3 211 each ~5.5mm off ORIG + cross-mouth spur run1 29; C04 outer loop 134 + 48-pt fold-back + 9-pt nub; C03 single arc fails via neighbours; C02 same disease + finder axle miss; guilty stage getPointsInSequence greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm; screening-only) + 66 (ordering-null ×3 stands) + 21 (RegionGrowing split precedent: SFS-T21 normal-sign split).

**Status:** results-in — SPLIT-SELECT measured NULL (jumps→0 on both arms, gate flat, E2E 0/3+0/3 ×3 bit-identical both arms; no in-file loop sits on the shipped contour — content disease confirmed, category 1 stands)

**Starting position:** split each C Bl_0 at >5mm gaps into one-loop components, drop spurs/fold-backs, select the inner loop via Surface standoff probe (predicted: Bl_0 ≈ ORIG counts already in file as run sizes; jumps→0 with no reorder; fresh-vs-shipped med ~5.6→~1-2mm). Fresh-only scratch copies; bundle references pota67/pota66/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. C02 axle still finder-side (orthogonal, per 66).

**Rules:** land ONLY with Bl_0 ≈ ORIG counts AND jumps→0 AND fresh-vs-shipped ~1-2mm AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [x] Split-then-select arms, one variable each
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

**Successor:** forward-cone guard at the walk level (67's durable fix); roll wherever doubled loops recur.

## Comments (worker, 2026-10-17 — COMMIT NOTHING; lead to commit)

**Verdict: split-then-select is measured NULL — jumps→0 achieved on both arms, but gate shows zero recovery and E2E seats 0/3+0/3 ×3 bit-identical on BOTH arms with all controls green in the same runs. The ticket's predicted observable (fresh-vs-shipped med ~5.6→~1-2mm) is REFUTED: GT-seated evidence shows no in-file loop sits on the shipped contour for C01/C02/C04 — neither the radius-inner loop nor the count-matching loop. The binding cause is rim CONTENT (both fresh loops straddle ~5.5mm off shipped; the true lip was never traced), not ORDER (65/66) and not SELECTION (this ticket). Category 1 stands. Landing bar conjunctively failed (counts/jumps met, ~1-2mm + gate + E2E not met) — reported as measured why-not per the ticket's alternative.**

**0. Preliminaries (read-only bundle refs; NEW work dir only).** Fresh = `/data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_C/SfS_pp` (copied once to `pota68_repro/prep/pota68_work_C` for screening, then to the two arm bundles; reference bundle itself untouched). ORIG = `sfs_main/original_samples/SfS_pp` (evidence-only distances + gray render backdrops — zero ORIG points in any fix; all selected Bl_0 md5s/counts differ from ORIG). Work dir NEW `/data/gpfs/projects/punim2657/pota68_repro/` (probes `probe_standoff.py`/`probe2_radii.py`/`probe3_gtseat.py`, builder `build_arms.py`, gate `gate68.py` = byte-copy of proven `gate66.py`, renders, `run_pota68_stage_AC.sbatch` = p66 vehicle + 5th arm). 39/40/65/66/67 lanes untouched (md5 guards on A-fresh + both C arms pass in every job). No source edits anywhere — SingleOverlapTest@100 / RP / CheckGraph-150 NOT relaxed (not even touched).

**1. Surface-standoff probe (fresh-only; the mandated selector).** Per-run median NN distance to Surface_0 / Surface_1 (piece-local frame, valid): C01 run0(frag10) 1.28/56.5, run1(spur29) 24.2/50.3 (floats 24mm off ALL surfaces — aerial debris, dropped), run2(152) 1.79/37.6, run3(211) 2.34/62.9 — both loops hug S0, weak separation, agrees with radius-inner = run2 (axR 43.2 vs 54.6, C01 axis dirpass-good 0.06°). C02 (axis garbage, r meaningless): all runs hug S0 ~0.7-0.8, S1 ~6 — selection among equals. C04: run0(134) the only full loop. C03 (axis EMPTY → PCA fallback, fresh-only): run1(127) pcaR 45.8 ≈ ORIG-scale, run0(40) appendage.

**2. GT-seated evidence (ORIG allowed as evidence; seating convention validated — C03 fresh seats onto ORIG at 0.73/1.04mm, so the ~5.5mm elsewhere is SHAPE, not frame).** Run→ORIG medians (<2mm share): C01 run2 5.45mm/29% vs run3 5.76/23% — radius-match and count-match point at DIFFERENT loops and NEITHER is on-contour; C02 all runs 5.95-6.13mm/0%; C04 run0 5.47/0% (only the 9-pt nub on-ORIG at 0.78/100%); C03 run0 0.73/100%, run1 1.04/83% (rotation-only piece). ORIG→freshFULL: C01 2.53/44%, C02 5.95/0%, C03 1.04/83%, C04 5.32/8%.

**3. Arms (fresh-only derivation, full rows kept, zero points altered, single-segment `# 1 N 0` headers, axes byte-identical).** S-INNER: C01 run2[39,191)/C02 run3[100,267)/C03 rotate([40,167)+[0,40))/C04 run0[0,134) → counts 152/167/167/134. S-COUNT (one variable flipped): C01 run3[191,402), rest same → 211/167/167/134. Jumps>5: [] on all 8 files, maxlink ≤2.26, no reorder (each run internally file-ordered; C03 rotation closes at 1.91). Count bar vs ORIG (211/221/191/131): only C04 meets it — the counts-of-shipped-loops simply are not in the files (except C04's outer loop).

**4. Gate: NO recovery (fresh baseline reproduces T64 exactly: 0/1/4/0/16 — probe validated).** Strict p39 rule at GT seating: S-INNER 0/1/0/0/16, S-COUNT 0/0/2/0/16 vs ORIG scale 34/72/40/73/55. The 4→0/2 movement on edge 1-4 is point-removal noise (fewer points, fewer inliers), not recovery. Selection-null mirrors 66's reorder-null.

**5. E2E ×3 same-binary (cure-potA @ bffefb6, k=5/b=3, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK 5× per job, all jobs sacct COMPLETED 0:0, polled directly):**

| job | A_orig | A_fresh | C_orig | C_inner | C_count |
|---|---|---|---|---|---|
| 33279876 | 8/8+15/15 (70) | 8/8+15/15 (119) | 4/4+5/5 (40) | 0/3+0/3 (8) | 0/3+0/3 (8) |
| 33279902 | 8/8+15/15 (70) | 8/8+15/15 (119) | 4/4+5/5 (40) | 0/3+0/3 (8) | 0/3+0/3 (7) |
| 33279903 | 8/8+15/15 (70) | 8/8+15/15 (120) | 4/4+5/5 (40) | 0/3+0/3 (8) | 0/3+0/3 (6) |

(pruned counts in brackets; forest 142 both C arms R1.) Bit-identical tallies ×3 (deterministic binary): vehicle + A-fresh + C ORIG controls all green in the same runs. C arms hold T_0,T_1,T_3 only — P3 still unplaced (refusal path unchanged). Spur removal shrinks pruned 20-21 (T66) → 6-8 but converts zero.

**6. Renders (all eye-checked; `artifacts/pota68/`).** `C01_runs.png` / `C04_runs.png` (run splits before selection); `Csel_inner_vs_ORIG.png` (selected loops @GT vs gray shipped: C01 red covers only part of the ring, C02 partial + offset, C03 on-contour, C04 parallel-offset — the why-not seen directly); `Csel_seating_R1.png` (seated tangle flung off GT, P3 missing). Scripts `render_runs.py` / `render_selected.py` / `render_seating.py`.

**7. Jobs (sacct State/ExitCode, polled directly, never slurm_poll.sh).** 33279876 / 33279902 / 33279903 COMPLETED 0:0 (11-14 min each, 5 arms). RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota68_run_{33279876,33279902,33279903}/`; fetch tgz `pota68_fetch.tgz` in each (R1 used for seating render). Spartan leftovers: `pota68_repro/` + 3 `pota68_run_*` dirs only.

**Successor proposal for lead:** the C rims need CONTENT regeneration (re-trace the true lip at the walk level with 67's forward-cone guard + one-loop-per-component emission), not re-sorting or sub-selecting — this ticket exhausts the in-file options (order: 65/66 null; selection: 68 null on both natural choices). C03 (on-contour, rotation-only) is the clean control proving the vehicle + controls are green. E/I/J forests should check GT-seated fresh-vs-shipped contour distance FIRST; if ~5mm-scale with doubled counts, skip order/selection repairs and go straight to walk-level re-extraction.
